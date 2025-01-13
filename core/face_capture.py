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
        self.current_user_id = None
        self.last_event = None
        self.face_score = 0
        self.face_detected = False
        self._connected = False
        
    def _ensure_connection(self):
        """Garante que existe uma conexão ativa"""
        if not self._connected:
            if self.protocol.connect():
                self._connected = True
                return True
            return False
        return True
        
    def _disconnect(self):
        """Desconecta do dispositivo"""
        if self._connected:
            self.protocol.disconnect()
            self._connected = False
        
    def start_enrollment(self, user_id):
        """Inicia o processo de cadastro facial"""
        try:
            print(f"Iniciando registro facial para usuário {user_id}")
            
            # Garante que temos uma conexão
            if not self._ensure_connection():
                raise Exception("Falha ao conectar ao dispositivo")
            
            # Desabilita o dispositivo temporariamente
            if not self.device.conn.disable_device():
                raise Exception("Falha ao desabilitar dispositivo")
                
            time.sleep(1)  # Aguarda a desabilitação
            
            try:
                # Reseta variáveis de estado
                self.current_user_id = user_id
                self.enrollment_status = False
                self.last_event = None
                self.face_score = 0
                self.face_detected = False
                
                # Inicia o registro usando o protocolo ZK
                if not self.protocol.start_face_enrollment(user_id):
                    raise Exception("Falha ao iniciar registro")
                
                self.enrollment_status = True
                return True
                
            except Exception as e:
                print(f"Erro durante o registro: {str(e)}")
                self._disconnect()  # Desconecta em caso de erro
                raise e
            
        except Exception as e:
            print(f"Erro no cadastro: {str(e)}")
            self.enrollment_status = False
            return False
            
        finally:
            # Reabilita o dispositivo
            time.sleep(1)  # Aguarda antes de reabilitar
            self.device.conn.enable_device()
            
    def check_enrollment_status(self):
        """Verifica o status do cadastro e processa eventos"""
        if not self.enrollment_status or not self.current_user_id:
            return False
            
        try:
            # Garante que temos uma conexão
            if not self._ensure_connection():
                raise Exception("Falha ao conectar ao dispositivo")
                
            # Verifica status usando o protocolo
            response = self.protocol.receive_reply()
            
            if not response:
                return False
                
            # Processa eventos em tempo real
            if response.get('command') == 0x01f4:  # CMD_REG_EVENT
                event = response.get('event')
                self.last_event = event
                
                if event == self.protocol.EF_FACE:
                    self.face_detected = True
                    return False
                elif event == self.protocol.EF_FPFTR:
                    self.face_score = int.from_bytes(response.get('data', b'\x00'), byteorder='little')
                    return False
                elif event == self.protocol.EF_ENROLL_SUCCESS:
                    print("Cadastro concluído com sucesso")
                    self.enrollment_status = False
                    self.current_user_id = None
                    self._disconnect()  # Desconecta após sucesso
                    return True
                elif event == self.protocol.EF_ENROLL_FAILED:
                    print("Falha no cadastro")
                    self.enrollment_status = False
                    self.current_user_id = None
                    self._disconnect()  # Desconecta após falha
                    return False
                    
            return False
            
        except Exception as e:
            print(f"Erro ao verificar status: {str(e)}")
            self._disconnect()  # Desconecta em caso de erro
            return False
            
    def cancel_enrollment(self):
        """Cancela o processo de cadastro"""
        try:
            if self.enrollment_status:
                # Garante que temos uma conexão
                if not self._ensure_connection():
                    raise Exception("Falha ao conectar ao dispositivo")
                    
                if self.protocol.cancel_operation():
                    print("Cadastro cancelado")
                    self.enrollment_status = False
                    self.current_user_id = None
                    return True
                    
            return True
            
        except Exception as e:
            print(f"Erro ao cancelar cadastro: {str(e)}")
            return False
            
        finally:
            self._disconnect()  # Sempre desconecta ao finalizar
            
    def get_enrollment_feedback(self):
        """Retorna feedback do processo de cadastro"""
        if not self.enrollment_status:
            return "Aguardando início do cadastro"
            
        if self.last_event == self.protocol.EF_FACE:
            return "Rosto detectado! Mantenha a posição..."
        elif self.last_event == self.protocol.EF_FPFTR:
            return f"Qualidade da captura: {self.face_score}%"
        elif self.last_event == self.protocol.EF_ENROLL_SUCCESS:
            return "Cadastro realizado com sucesso!"
        elif self.last_event == self.protocol.EF_ENROLL_FAILED:
            return "Falha no cadastro. Tente novamente."
            
        return "Posicione seu rosto na frente do dispositivo"