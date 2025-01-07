import os
from ctypes import *
from zk import ZK, const
from lib.base import ZK
from lib.const import *
from .face_capture import FaceCapture

class FaceDevice:
    def __init__(self, ip, port=4370):
        self.ip = ip
        self.port = port
        self.zk = None
        self.face_capture = None
        self.debug_callback = None
        self._initialize_sdk()
        
    def set_debug_callback(self, callback):
        """Define uma função de callback para logs de debug"""
        self.debug_callback = callback
        
    def _log(self, message):
        """Função interna para logging"""
        if self.debug_callback:
            self.debug_callback(message)
        print(message)
        
    def _initialize_sdk(self):
        """Inicializa as DLLs do SDK"""
        try:
            self._log("Inicializando conexão de rede...")
            self.zk = ZK(self.ip, port=self.port, timeout=10)
            
            # Removemos a parte de inicialização do SDK USB já que vamos usar rede
            self._log("Inicialização concluída")
            
            # Inicializa o módulo de captura facial
            self.face_capture = FaceCapture(self)
                
        except Exception as e:
            self._log(f"Erro durante inicialização: {str(e)}")
            raise
            
    def connect(self):
        """Conecta ao dispositivo"""
        try:
            self._log(f"Conectando ao dispositivo {self.ip}:{self.port}...")
            conn = self.zk.connect()
            if not conn:
                raise Exception("Não foi possível estabelecer conexão")
                
            self._log("Desabilitando dispositivo temporariamente...")
            conn.disable_device()
            
            # Obtém informações do firmware para testar a conexão
            firmware = conn.get_firmware_version()
            self._log(f"Versão do Firmware: {firmware}")
            
            self.conn = conn
            
            self._log("Reabilitando dispositivo...")
            conn.enable_device()
            
            self._log("Dispositivo conectado e pronto")
            return True
            
        except Exception as e:
            self._log(f"Erro durante a conexão: {str(e)}")
            return False
            
    def disconnect(self):
        """Desconecta do dispositivo"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self._log("Desabilitando dispositivo...")
                self.conn.disable_device()
                
                self._log("Desconectando da rede...")
                self.conn.disconnect()
                self._log("Desconectado da rede")
                
            if self.face_capture:
                self._log("Parando captura facial...")
                self.face_capture.cancel_enrollment()
                
            return True
            
        except Exception as e:
            self._log(f"Erro durante a desconexão: {str(e)}")
            return False
            
    def start_face_capture(self, user_id, video_callback=None, face_callback=None):
        """Inicia a captura da face para um usuário específico"""
        try:
            if not self.face_capture:
                raise Exception("Módulo de captura facial não inicializado")
                
            self._log(f"Iniciando captura facial para usuário {user_id}")
            
            # Inicia o processo de cadastro
            if not self.face_capture.start_enrollment(user_id):
                raise Exception("Falha ao iniciar processo de cadastro facial")
                
            return True
            
        except Exception as e:
            self._log(f"Erro ao iniciar captura facial: {str(e)}")
            return False
            
    def finish_face_capture(self):
        """Finaliza o processo de captura facial"""
        try:
            if not self.face_capture:
                raise Exception("Módulo de captura facial não inicializado")
                
            self._log("Finalizando captura facial...")
            
            # Para a captura
            self.face_capture.stop_capture()
            
            # Finaliza o processo de cadastro
            if not self.face_capture.finish_enrollment():
                raise Exception("Falha ao finalizar processo de cadastro facial")
                
            return True
            
        except Exception as e:
            self._log(f"Erro ao finalizar captura facial: {str(e)}")
            return False
            
    def get_users(self):
        """Obtém a lista de usuários cadastrados no dispositivo"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                raise Exception("Dispositivo não está conectado")
                
            self._log("Obtendo lista de usuários...")
            users = self.conn.get_users()
            
            user_list = []
            for user in users:
                user_info = {
                    'uid': user.uid,
                    'name': user.name,
                    'privilege': 'Admin' if user.privilege == const.USER_ADMIN else 'User',
                    'password': user.password,
                    'group_id': user.group_id,
                    'user_id': user.user_id
                }
                user_list.append(user_info)
                
            self._log(f"Encontrados {len(user_list)} usuários")
            return user_list
            
        except Exception as e:
            self._log(f"Erro ao obter usuários: {str(e)}")
            return []
            
    def get_attendance_logs(self):
        """Obtém os registros de presença do dispositivo"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                raise Exception("Dispositivo não está conectado")
                
            self._log("Obtendo registros de presença...")
            logs = self.conn.get_attendance()
            
            attendance_list = []
            for log in logs:
                log_info = {
                    'user_id': log.user_id,
                    'timestamp': log.timestamp,
                    'status': log.status,
                    'punch': log.punch,
                }
                attendance_list.append(log_info)
                
            self._log(f"Encontrados {len(attendance_list)} registros")
            return attendance_list
            
        except Exception as e:
            self._log(f"Erro ao obter registros: {str(e)}")
            return []
            
    def clear_attendance_logs(self):
        """Limpa os registros de presença do dispositivo"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                raise Exception("Dispositivo não está conectado")
                
            self._log("Limpando registros de presença...")
            self.conn.clear_attendance()
            self._log("Registros limpos com sucesso")
            return True
            
        except Exception as e:
            self._log(f"Erro ao limpar registros: {str(e)}")
            return False
            
    def get_device_info(self):
        """Obtém informações detalhadas do dispositivo"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                raise Exception("Dispositivo não está conectado")
                
            self._log("Obtendo informações do dispositivo...")
            
            # Obtém informações básicas
            info = {
                'firmware': self.conn.get_firmware_version(),
                'platform': self.conn.get_platform(),
                'serial': self.conn.get_serialnumber(),
                'mac': self.conn.get_mac(),
                'face_algorithm': self.conn.get_face_version(),
                'device_name': self.conn.get_device_name(),
            }
            
            # Obtém estatísticas
            self.conn.read_sizes()
            info.update({
                'users': self.conn.users,
                'faces': self.conn.faces,
                'records': self.conn.records
            })
            
            self._log("Informações do dispositivo obtidas com sucesso")
            return info
            
        except Exception as e:
            self._log(f"Erro ao obter informações do dispositivo: {str(e)}")
            return None

    def delete_user(self, user_id):
        """Deleta um usuário do dispositivo"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                raise Exception("Dispositivo não está conectado")
                
            self._log(f"Deletando usuário {user_id}...")
            if self.conn.delete_user(user_id=str(user_id)):
                self._log("Usuário deletado com sucesso")
                return True
            return False
            
        except Exception as e:
            self._log(f"Erro ao deletar usuário: {str(e)}")
            return False 