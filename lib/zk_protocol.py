from struct import pack, unpack
import socket
import time
from zk import const

class ZKProtocol:
    # Comandos básicos
    CMD_CONNECT = 0x03e8        # 1000 decimal
    CMD_EXIT = 0x03e9           # 1001 decimal
    CMD_ENABLEDEVICE = 0x03ea   # 1002 decimal
    CMD_DISABLEDEVICE = 0x03eb  # 1003 decimal
    
    # Comandos de registro
    CMD_STARTENROLL = 0x003d    # 61 decimal
    CMD_STARTVERIFY = 0x003c    # 60 decimal
    CMD_CANCELCAPTURE = 0x003e  # 62 decimal
    
    # Comandos de status
    CMD_ACK_OK = 0x07d0         # 2000 decimal
    CMD_ACK_ERROR = 0x07d1      # 2001 decimal
    CMD_STATE_RRQ = 0x0040      # 64 decimal
    
    # Comandos de face
    CMD_FACE_FUNCTION = 11      # Comando para funções faciais
    CMD_PREPARE_DATA = 1500     # Prepara para transmitir dados
    CMD_DATA = 1501            # Transmite pacote de dados
    CMD_FREE_DATA = 1502       # Limpa buffer do dispositivo
    
    # Comandos de versão
    CMD_GET_VERSION = 1100      # Obtém versão do firmware
    CMD_GET_OS_VERSION = 1116   # Obtém versão do sistema operacional
    
    # Estados de registro
    STATE_ENROLL_SUCCESS = 0x01
    STATE_ENROLL_FAILED = 0x02
    STATE_ENROLL_PROGRESS = 0x03
    
    def __init__(self, ip, port=4370):
        self.ip = ip
        self.port = port
        self.socket = None
        self.session_id = 0
        self.reply_number = 0
        
    def connect(self):
        """Estabelece conexão com o dispositivo"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            
            # Envia comando de conexão (CMD_CONNECT = 1000)
            response = self.send_command(self.CMD_CONNECT)
            
            if response and response.get('session_id'):
                self.session_id = response.get('session_id')
                print(f"[ZK-PROTO] Conectado com session_id: {self.session_id}")
                return True
                
            return False
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro de conexão: {str(e)}")
            return False
            
    def disconnect(self):
        """Fecha a conexão"""
        if self.socket:
            self.socket.close()
            
    def send_command(self, command, data=b''):
        """Envia um comando para o dispositivo"""
        try:
            # Monta o pacote
            payload = pack('<H', command)  # Command ID (2 bytes)
            payload += pack('<H', 0)       # Checksum (2 bytes, será calculado depois)
            payload += pack('<H', self.session_id)  # Session ID (2 bytes)
            payload += pack('<H', self.reply_number)  # Reply number (2 bytes)
            payload += data                # Data
            
            # Calcula checksum
            chksum = self.calculate_checksum(payload)
            
            # Substitui o checksum no payload
            payload = payload[:2] + pack('<H', chksum) + payload[4:]
            
            # Monta o pacote completo
            packet = pack('<I', 0x7d825050)  # Start token
            packet += pack('<I', len(payload))  # Payload size
            packet += payload
            
            # Envia o pacote
            self.socket.send(packet)
            
            # Incrementa o número de resposta
            self.reply_number += 1
            
            # Recebe a resposta
            response = self.receive_reply()
            return response
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao enviar comando: {str(e)}")
            return None
            
    def start_face_enrollment(self, user_id):
        """Inicia o processo de cadastro facial"""
        try:
            print(f"[ZK-PROTO] Iniciando cadastro facial para usuário {user_id}")
            
            # Cancela qualquer operação pendente
            self.cancel_operation()
            
            # Ativa a função facial
            data = b'FaceFunOn'
            response = self.send_command(self.CMD_FACE_FUNCTION, data)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao ativar função facial")
                return False
                
            # Prepara o dispositivo para receber dados
            response = self.send_command(self.CMD_PREPARE_DATA)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao preparar dispositivo")
                return False
                
            # Monta o comando para registro
            data = pack('<I', int(user_id))  # User ID (4 bytes)
            data += pack('<H', 50)           # Face ID (2 bytes)
            data += pack('<H', 12)           # Flag (2 bytes)
            
            # Envia o comando de início de cadastro
            response = self.send_command(self.CMD_STARTENROLL, data)
            
            if response and response.get('command') == self.CMD_ACK_OK:
                print("[ZK-PROTO] Cadastro iniciado com sucesso")
                return True
                
            print("[ZK-PROTO] Falha ao iniciar cadastro")
            return False
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro no cadastro: {str(e)}")
            return False
            
    def cancel_operation(self):
        """Cancela a operação atual"""
        try:
            print("[ZK-PROTO] Cancelando operação...")
            response = self.send_command(self.CMD_CANCELCAPTURE)
            return response and response.get('command') == self.CMD_ACK_OK
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao cancelar operação: {str(e)}")
            return False
            
    def get_state(self):
        """Obtém o estado atual do dispositivo"""
        try:
            response = self.send_command(self.CMD_STATE_RRQ)
            if response and response.get('command') == self.CMD_ACK_OK:
                # Extrai o estado dos dados da resposta
                state = unpack('<I', response.get('data', b'\x00\x00\x00\x00'))[0]
                return state
            return 0
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao obter estado: {str(e)}")
            return 0
            
    def calculate_checksum(self, payload):
        """Calcula o checksum do pacote"""
        chk_32b = 0
        
        # Garante que o payload tem tamanho par
        if len(payload) % 2:
            payload += b'\x00'
            
        # Calcula a soma de 16 bits
        for i in range(0, len(payload), 2):
            num_16b = payload[i] + (payload[i+1] << 8)
            chk_32b += num_16b
            
        # Adiciona os bytes superiores aos inferiores
        chk_32b = (chk_32b & 0xffff) + ((chk_32b >> 16) & 0xffff)
        
        # Retorna o complemento de 1
        return chk_32b ^ 0xFFFF
        
    def receive_reply(self):
        """Recebe e processa a resposta do dispositivo"""
        try:
            # Recebe o cabeçalho (8 bytes)
            header = self.socket.recv(8)
            if len(header) < 8:
                return None
                
            # Extrai o tamanho do payload
            payload_size = unpack('<I', header[4:8])[0]
            
            # Recebe o payload
            payload = self.socket.recv(payload_size)
            if len(payload) < payload_size:
                return None
                
            # Extrai os campos do payload
            command = unpack('<H', payload[0:2])[0]
            session_id = unpack('<H', payload[4:6])[0]
            reply_id = unpack('<H', payload[6:8])[0]
            data = payload[8:]
            
            return {
                'command': command,
                'session_id': session_id,
                'reply_id': reply_id,
                'data': data
            }
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao receber resposta: {str(e)}")
            return None 

    def get_firmware_version(self):
        """Obtém a versão do firmware do dispositivo"""
        try:
            response = self.send_command(self.CMD_GET_VERSION)
            if response and response.get('command') == self.CMD_ACK_OK:
                version = response.get('data', b'').decode('ascii', errors='ignore').strip('\x00')
                print(f"[ZK-PROTO] Versão do firmware: {version}")
                return version
            return None
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao obter versão: {str(e)}")
            return None 