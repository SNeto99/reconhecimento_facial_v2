# -*- coding: utf-8 -*-
import json
import time
from lib import const
from lib.zk_protocol import ZKProtocol

class FaceCapture:
    def __init__(self, device):
        self.device = device
        self.enrollment_status = False
        self.protocol = ZKProtocol(ip=device.ip, port=device.port)
        self.current_user_id = None  # Armazena o ID do usuário atual
        
    def start_enrollment(self, user_id):
        """Inicia o processo de cadastro facial"""
        try:
            # Primeiro conecta ao protocolo
            if not self.protocol.connect():
                raise Exception("Falha ao conectar ao dispositivo")
            
            # Desabilita o dispositivo temporariamente
            self.device.conn.disable_device()
            
            try:
                print(f"Iniciando registro facial para usuário {user_id}")
                
                # Armazena o ID do usuário atual
                self.current_user_id = user_id
                
                # Inicia o registro usando o protocolo ZK
                if not self.protocol.start_face_enrollment(user_id):
                    raise Exception("Falha ao iniciar registro")
                
                self.enrollment_status = True
                return True
                
            except Exception as e:
                raise e
            
        except Exception as e:
            print(f"Erro no cadastro: {str(e)}")
            self.enrollment_status = False
            return False
            
        finally:
            # Reabilita o dispositivo
            self.device.conn.enable_device()
            # Desconecta o protocolo
            self.protocol.disconnect()
            
    def check_enrollment_status(self):
        """Verifica o status do cadastro"""
        if not self.enrollment_status or not self.current_user_id:
            return False
            
        try:
            # Primeiro conecta ao protocolo
            if not self.protocol.connect():
                raise Exception("Falha ao conectar ao dispositivo")
                
            try:
                # Verifica status usando o protocolo
                status = self.protocol.get_state()
                
                if status == self.protocol.STATE_ENROLL_SUCCESS:
                    print("Cadastro concluído com sucesso")
                    self.enrollment_status = False
                    self.current_user_id = None  # Limpa o ID do usuário
                    return True
                elif status == self.protocol.STATE_ENROLL_PROGRESS:
                    print("Cadastro em andamento...")
                    return False
                else:
                    print(f"Estado atual: {status}")
                    return False
                
            finally:
                self.protocol.disconnect()
            
        except Exception as e:
            print(f"Erro ao verificar status: {str(e)}")
            return False
            
    def cancel_enrollment(self):
        """Cancela o processo de cadastro"""
        try:
            if self.enrollment_status:
                # Primeiro conecta ao protocolo
                if not self.protocol.connect():
                    raise Exception("Falha ao conectar ao dispositivo")
                    
                try:
                    if self.protocol.cancel_operation():
                        print("Cadastro cancelado")
                        self.enrollment_status = False
                        self.current_user_id = None  # Limpa o ID do usuário
                        return True
                finally:
                    self.protocol.disconnect()
                    
            return True
            
        except Exception as e:
            print(f"Erro ao cancelar cadastro: {str(e)}")
            return False