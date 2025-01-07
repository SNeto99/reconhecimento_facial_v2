# -*- coding: utf-8 -*-
from zk import ZK, const
from tkinter import messagebox
import time
import socket
from struct import pack, unpack

# Configurações do dispositivo
ZK_IP = '192.168.50.201'
ZK_PORT = 4370

# Comandos específicos para face baseados no SDK
CMD_SET_FACE = 0x0182       # Comando para definir face
CMD_GET_FACE = 0x0183       # Comando para obter face
CMD_PREPARE_FACE = 0x0184   # Comando para preparar captura
CMD_FACE_INIT = 0x0185      # Comando para inicializar face

def testar_cadastro_facial(id_usuario, nome):
    try:
        print(f"Iniciando teste de cadastro facial para usuário {id_usuario}")
        
        # Inicializa conexão
        zk = ZK(ZK_IP, port=ZK_PORT, timeout=10)
        conn = zk.connect()
        
        if not conn:
            raise Exception("Não foi possível conectar ao dispositivo")
        
        # Desabilita o dispositivo antes das operações
        conn.disable_device()
        
        try:
            print("Conexão estabelecida com sucesso")
            
            # Primeiro cadastra o usuário básico usando o método existente
            print(f"Cadastrando usuário {nome}")
            conn.set_user(
                uid=int(id_usuario),
                name=nome,
                password='123456',
                group_id=const.USER_DEFAULT,
                user_id=str(id_usuario)
            )
            
            print("Usuário cadastrado com sucesso")
            print("Iniciando cadastro facial...")
            
            # Inicializa o módulo facial
            if not conn.init_face():
                raise Exception("Falha ao inicializar módulo facial")
            
            # Prepara para captura facial
            if not conn.prepare_face(id_usuario):
                raise Exception("Falha ao preparar captura facial")
            
            print("Por favor, posicione seu rosto na frente do dispositivo...")
            
            # Inicia a captura facial
            if not conn.set_face(id_usuario):
                raise Exception("Falha ao iniciar captura facial")
            
            # Aguarda a conclusão do cadastro (timeout de 20 segundos)
            timeout = time.time() + 20
            print("Aguardando captura facial...")
            
            while time.time() < timeout:
                # Verifica se o cadastro foi concluído
                if conn.get_face(id_usuario):
                    print("Cadastro facial concluído com sucesso!")
                    messagebox.showinfo("Sucesso", "Cadastro facial realizado com sucesso!")
                    return True
                    
                time.sleep(1)
                print(".", end="", flush=True)
                
            raise Exception("Tempo limite excedido para cadastro facial")
            
        finally:
            # Atualiza os dados e habilita o dispositivo
            print("Finalizando operação...")
            conn.refresh_data()
            conn.enable_device()
            conn.disconnect()
            print("Dispositivo desconectado")
            
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")
        messagebox.showerror("Erro", f"Erro durante o teste: {str(e)}")
        return False

def obter_dados_dispositivo():
    try:
        zk = ZK(ZK_IP, port=ZK_PORT, timeout=10)
        conn = zk.connect()
        users = conn.get_users()
        conn.disconnect()
        return users
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao dispositivo: {e}")
        return None

def obter_logs_dispositivo():
    try:
        zk = ZK(ZK_IP, port=ZK_PORT, timeout=10)
        conn = zk.connect()
        attendance = conn.get_attendance()
        conn.disconnect()
        return attendance
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao dispositivo: {e}")
        return None

def cadastrar_usuario_dispositivo(id_aluno, nome, senha):
    try:
        zk = ZK(ZK_IP, port=ZK_PORT, timeout=10)
        conn = zk.connect()
        
        # Convertendo id_aluno para inteiro
        id_aluno_int = int(id_aluno)
        
        conn.set_user(
            uid=id_aluno_int,
            name=nome,
            password=senha,
            group_id=const.USER_DEFAULT,
            user_id=str(id_aluno_int)
        )
        conn.enroll_user(uid=id_aluno_int, user_id=str(id_aluno_int))
        
        conn.disconnect()
    except ValueError:
        messagebox.showerror("Erro", "O ID do aluno deve ser um número válido")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")