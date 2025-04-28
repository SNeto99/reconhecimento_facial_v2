# -*- coding: utf-8 -*-
import json
import random
import urllib.request
import urllib.error
from database import get_config_value


def _api_request(path, payload=None):
    """
    Realiza requisição HTTP (GET se payload=None, POST se payload!=None) com headers padrão.
    """
    api_url = get_config_value("api_url", "")
    if not api_url:
        raise Exception("URL da API não configurada")
    url = f"{api_url}/{path}"
    school_id = get_config_value("school_id", "")
    mac_address = get_config_value("device_mac", "")
    headers = {"X-School-Id": school_id, "X-MAC-Address": mac_address}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        code = resp.getcode()
        if code not in (200, 201):
            raise Exception(f"Erro ao acessar {path}: HTTP {code}")
        return resp
    except urllib.error.HTTPError as e:
        raise Exception(f"Erro HTTP ao acessar {path}: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"Erro de rede ao acessar {path}: {e.reason}")

def buscar_cidades():
    """
    Busca a lista de cidades disponíveis na API.
    Espera um JSON com campo "cidades", opcionalmente "status".
    """
    resp = _api_request("escolas/buscarCidades")
    data = json.load(resp)
    # Converte resposta para lista de dicionários com keys 'id' e 'nome'
    raw = data.get("data", data.get("cidades", [])) or []
    cidades_list = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        # Obtém nome da cidade
        if "cidade" in item:
            nome = item.get("cidade")
        else:
            nome = item.get("nome")
        # Obtém id da cidade a partir de 'idsme', 'id' ou usa o nome
        id_val = item.get("idsme") or item.get("id") or nome
        if nome:
            cidades_list.append({"id": id_val, "nome": nome})
    return cidades_list

def buscar_escolas_cidade(idcidade, nomebuscar):
    """
    Busca escolas por cidade e nome na API.
    Body: {"idsme": idcidade, "nomebuscar": nomebuscar}, espera campo "escolas".
    """
    payload = json.dumps({"idsme": idcidade, "nomebuscar": nomebuscar}).encode('utf-8')
    resp = _api_request("escolas/buscarEscolas", payload)
    raw_bytes = resp.read()
    # Se não houver conteúdo, retorna lista vazia
    if not raw_bytes:
        return []
    # Decodifica JSON e extrai array de escolas
    try:
        data = json.loads(raw_bytes.decode('utf-8'))
    except Exception:
        return []
    if isinstance(data, dict):
        raw_list = data.get('data', data.get('escolas', [])) or []
    elif isinstance(data, list):
        raw_list = data
    else:
        return []
    schools = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        # Tenta obter id e nome conforme resposta
        id_val = item.get('id') or item.get('idescola') or item.get('id_escola') or item.get('nome')
        nome_val = item.get('nome') or item.get('escola') or item.get('nome_escola')
        if id_val is None:
            id_val = nome_val
        if nome_val:
            schools.append({'id': id_val, 'nome': nome_val})
    return schools

def buscar_alunos(nome):
    """
    Busca pessoas/alunos na API pelo nome.
    Body: {"nome": nome}. Resposta padrão: {"erro": bool, "data": [{"idpessoa": ..., "nome": ...}, ...]}
    """
    payload = json.dumps({"nomeBuscar": nome, "idescola": get_config_value("school_id", "")}).encode('utf-8')
    resp = _api_request("alunos/buscarAluno", payload)
    raw_bytes = resp.read()
    if not raw_bytes:
        return []
    # Decodifica JSON, pode ser lista ou dict
    try:
        parsed = json.loads(raw_bytes.decode('utf-8'))
    except Exception:
        return []
    # Se resposta é lista, usa diretamente; se dict, pega 'data'
    if isinstance(parsed, list):
        raw_list = parsed
    elif isinstance(parsed, dict):
        raw_list = parsed.get('data') or []
    else:
        return []
    students = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        id_val = item.get('idpessoa') or item.get('idPessoa') or item.get('id')
        nome_val = item.get('nome')
        if not nome_val:
            continue
        # Captura campos adicionais ra, serie e turma
        ra_val = item.get('ra', '')
        serie_val = item.get('serie', '')
        turma_val = item.get('turma', '')
        students.append({
            'id': id_val,
            'nome': nome_val,
            'ra': ra_val,
            'serie': serie_val,
            'turma': turma_val
        })
    return students

def enviar_dispositivo(device):
    """
    Envia as informações de um dispositivo para a API.
    """
    payload = json.dumps(device).encode("utf-8")
    _api_request("sincronizar/syncDispositivos", payload)

def enviar_usuario(user):
    """
    Envia as informações de um usuário para a API.
    """
    payload = json.dumps(user).encode("utf-8")
    _api_request("sincronizar/syncAlunos", payload)

def enviar_log(log):
    """
    Envia um registro de log para a API.
    """
    payload = json.dumps(log).encode("utf-8")
    _api_request("sincronizar/syncLogs", payload)

def enviar_dispositivos_batch(devices_list):
    """
    Envia lista de dispositivos para a API em batch.
    """
    payload = json.dumps(devices_list).encode("utf-8")
    _api_request("sincronizar/syncDispositivos", payload)

def enviar_usuarios_batch(users_list):
    """
    Envia lista de usuários para a API em batch.
    """
    payload = json.dumps(users_list).encode("utf-8")
    _api_request("sincronizar/syncAlunos", payload)

def enviar_logs_batch(logs_list):
    """
    Envia lista de logs para a API em batch.
    """
    payload = json.dumps(logs_list).encode("utf-8")
    _api_request("sincronizar/syncLogs", payload)