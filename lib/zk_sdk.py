from ctypes import *
import os
import json
import struct
import time
from . import const  # Importa o módulo const do mesmo diretório
from .base import ZK
from .zk_protocol import ZKProtocol

class ZKSDK:
    def __init__(self):
        self.zk = None
        self.current_protocol = None  # Mantém referência ao protocolo atual
    
    def connect(self, ip, port=4370):
        """Conecta ao dispositivo"""
        try:
            self.zk = ZK(ip, port=port)
            return self.zk.connect()
        except Exception as e:
            print(f"Erro ao conectar: {str(e)}")
            return False
            
    def register_face(self, user_id, conn):
        """Inicia o registro facial"""
        try:
            print(f"\n[FACE-SDK] Iniciando registro facial para usuário {user_id}")
            
            # Desabilita o dispositivo temporariamente
            conn.disable_device()
            
            try:
                print("[FACE-SDK] Iniciando processo de registro facial...")
                
                # 1. Verifica se o dispositivo suporta face
                if not conn.verify_user():
                    raise Exception("Dispositivo não está pronto")
                
                # 2. Cria uma instância do protocolo ZK
                protocol = ZKProtocol(ip=conn.ip, port=conn.port)
                self.current_protocol = protocol
                
                # 3. Conecta ao protocolo
                if not protocol.connect():
                    raise Exception("Falha ao conectar ao protocolo")
                
                # 4. Inicia o registro facial
                if not protocol.start_face_enrollment(user_id):
                    raise Exception("Falha ao iniciar registro facial")
                
                print("[FACE-SDK] Registro facial iniciado com sucesso")
                return True
                
            except Exception as e:
                print(f"[FACE-SDK] Erro ao registrar face: {str(e)}")
                raise
                
            finally:
                # Reabilita o dispositivo
                conn.enable_device()
                
        except Exception as e:
            print(f"[FACE-SDK] Erro no registro facial: {str(e)}")
            try:
                if self.current_protocol:
                    self.current_protocol.cancel_operation()
                    self.current_protocol.disconnect()
                    self.current_protocol = None
            except:
                pass
            return False
            
    def cancel_enrollment(self):
        """Cancela o processo de cadastro atual"""
        try:
            if self.current_protocol:
                print("[FACE-SDK] Cancelando cadastro...")
                self.current_protocol.cancel_operation()
                self.current_protocol.disconnect()
                self.current_protocol = None
        except Exception as e:
            print(f"[FACE-SDK] Erro ao cancelar cadastro: {str(e)}")
            
    def delete_user(self, user_id):
        """Deleta um usuário do dispositivo"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.delete_user(user_id=str(user_id))
        except Exception as e:
            print(f"Erro ao deletar usuário: {str(e)}")
            return False
    
    def get_all_users(self):
        """Obtém lista de todos os usuários cadastrados"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.get_users()
        except Exception as e:
            print(f"Erro ao obter usuários: {str(e)}")
            return []
    
    def get_attendance_logs(self):
        """Obtém registros de presença"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.get_attendance()
        except Exception as e:
            print(f"Erro ao obter logs: {str(e)}")
            return []
    
    def clear_attendance_logs(self):
        """Limpa todos os registros de presença"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.clear_attendance()
        except Exception as e:
            print(f"Erro ao limpar logs: {str(e)}")
            return False
            
    def get_face_status(self, conn, user_id):
        """Verifica o status do cadastro facial
        
        Args:
            conn: Objeto de conexão com o dispositivo
            user_id (str): ID do usuário para verificar o status
            
        Returns:
            dict: Dicionário com o status do cadastro
        """
        try:
            if not conn:
                raise Exception("Conexão não estabelecida")
                
            # Verifica se o usuário foi registrado
            users = conn.get_users()
            for user in users:
                if user.uid == int(user_id):
                    if user.face:
                        print("[FACE-SDK] Cadastro facial concluído")
                        return {'status': 'success'}
            
            print("[FACE-SDK] Cadastro facial em andamento...")
            return {'status': 'in_progress'}
                
        except Exception as e:
            print(f"[FACE-SDK] Erro ao verificar status: {str(e)}")
            return None
            
    def cancel_operation(self):
        """Cancela a operação atual"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.cancel_capture()
        except Exception as e:
            print(f"Erro ao cancelar operação: {str(e)}")
            return False

    def refresh_data(self):
        """Atualiza dados do dispositivo (usuários e logs)"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            return self.zk.refresh_data()
        except Exception as e:
            print(f"Erro ao atualizar dados: {str(e)}")
            return False
            
    def disconnect(self):
        """Desconecta do dispositivo"""
        try:
            if self.zk:
                self.zk.disconnect()
                self.zk = None
            return True
        except Exception as e:
            print(f"Erro ao desconectar: {str(e)}")
            return False 

    def get_firmware_version(self):
        """Obtém a versão do firmware do dispositivo"""
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            # Cria uma instância do protocolo
            protocol = ZKProtocol(ip=self.zk.ip, port=self.zk.port)
            
            # Conecta ao protocolo
            if not protocol.connect():
                raise Exception("Falha ao conectar ao protocolo")
                
            try:
                # Obtém a versão
                version = protocol.get_firmware_version()
                if not version:
                    raise Exception("Falha ao obter versão")
                    
                return version
                
            finally:
                protocol.disconnect()
                
        except Exception as e:
            print(f"[FACE-SDK] Erro ao obter versão do firmware: {str(e)}")
            return None
            
    def upload_face_photo(self, user_id, photo_data):
        """
        Faz upload de uma foto para um usuário
        :param user_id: ID do usuário
        :param photo_data: Bytes da imagem JPEG
        """
        try:
            if not self.zk:
                raise Exception("Dispositivo não conectado")
                
            # Obtém a conexão
            conn = self.zk.connect()
            if not conn:
                raise Exception("Falha ao conectar ao dispositivo")
                
            try:
                # Desabilita o dispositivo
                conn.disable_device()
                time.sleep(0.5)
                
                # Prepara os dados para envio
                command_data = struct.pack('<IIII', 
                    0x0B,               # Comando de face (CMD_FACE_FUNCTION)
                    int(user_id),       # ID do usuário
                    len(photo_data),    # Tamanho da foto
                    0x02                # Operação: upload de foto
                )
                
                # Envia o comando inicial
                response = conn.send_command_raw(500, command_data)  # CMD_REG_EVENT = 500
                if not response:
                    raise Exception("Falha ao iniciar upload")
                    
                # Envia os dados da foto em chunks
                chunk_size = 1024
                total_sent = 0
                while total_sent < len(photo_data):
                    chunk = photo_data[total_sent:total_sent + chunk_size]
                    chunk_data = struct.pack('<I', len(chunk)) + chunk
                    response = conn.send_command_raw(1501, chunk_data)  # CMD_DATA = 1501
                    if not response:
                        raise Exception("Falha ao enviar chunk")
                    total_sent += len(chunk)
                    print(f"[FACE-SDK] Enviados {total_sent} de {len(photo_data)} bytes")
                    
                # Finaliza o upload
                finish_data = struct.pack('<II', int(user_id), 0x01)  # 0x01 = finalizar upload
                response = conn.send_command_raw(500, finish_data)  # CMD_REG_EVENT = 500
                if not response:
                    raise Exception("Falha ao finalizar upload")
                    
                print("[FACE-SDK] Upload de foto concluído com sucesso")
                return True
                
            finally:
                # Reabilita o dispositivo
                conn.enable_device()
                time.sleep(0.5)
                conn.disconnect()
                
        except Exception as e:
            print(f"[FACE-SDK] Erro ao fazer upload da foto: {str(e)}")
            return False 