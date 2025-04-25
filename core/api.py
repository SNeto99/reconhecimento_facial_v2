# -*- coding: utf-8 -*-
import json
import random
import urllib.request
import urllib.error
from database import get_config_value

# Simulação da API
def simular_busca_aluno(ra_nome):
    # Simula uma busca na API e retorna um ID de aluno
    # Em um cenário real, você faria uma requisição HTTP para sua API
    return random.randint(1000, 9999)

def buscar_cidades():
    """
    Busca a lista de cidades disponíveis na API.
    Espera um JSON com campo "cidades", opcionalmente "status".
    """
    api_url = get_config_value("api_url", "")
    if not api_url:
        raise Exception("URL da API não está configurada. Defina 'api_url' em config.")
    url = f"{api_url}/escolas/buscarCidades"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise Exception(f"Erro HTTP ao buscar cidades: {e.code} - {e.reason}")
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
    api_url = get_config_value("api_url", "")
    if not api_url:
        raise Exception("URL da API não está configurada. Defina 'api_url' em config.")
    # Constrói endpoint e payload
    url = f"{api_url}/escolas/buscarEscolas"
    payload = json.dumps({"idsme": idcidade, "nomebuscar": nomebuscar}).encode('utf-8')
    # Executa requisição POST
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            raw_bytes = resp.read()
    except urllib.error.HTTPError as e:
        raise Exception(f"Erro HTTP ao buscar escolas: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"Erro de rede ao buscar escolas: {e.reason}")
    except Exception as e:
        raise Exception(f"Erro inesperado ao buscar escolas: {e}")
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
    api_url = get_config_value("api_url", "")
    if not api_url:
        raise Exception("URL da API não está configurada. Defina 'api_url' em config.")
    url = f"{api_url}/alunos/buscarAluno"
    # Obtém o id da escola a partir da configuração
    idescola = get_config_value("school_id", "")
    # Monta payload com nomeBuscar e idescola
    payload = json.dumps({"nomeBuscar": nome, "idescola": idescola}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            raw_bytes = resp.read()
    except urllib.error.HTTPError as e:
        raise Exception(f"Erro HTTP ao buscar alunos: {e.code} - {e.reason}")
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