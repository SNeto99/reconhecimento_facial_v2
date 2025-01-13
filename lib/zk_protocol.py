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
    CMD_ADD_FACE = 2100       # Adiciona face via foto
    CMD_INIT_CAMERA = 2200    # Inicializa câmera
    CMD_CAMERA_CONFIG = 2201  # Configura câmera
    CMD_FACE_DETECT = 2202    # Inicia detecção facial
    CMD_UPLOAD_PHOTO = 2203   # Upload de foto
    
    # Comandos de versão
    CMD_GET_VERSION = 1100      # Obtém versão do firmware
    CMD_GET_OS_VERSION = 1116   # Obtém versão do sistema operacional
    
    # Estados de registro
    STATE_ENROLL_SUCCESS = 0x01
    STATE_ENROLL_FAILED = 0x02
    STATE_ENROLL_PROGRESS = 0x03
    
    # Eventos em tempo real
    EF_ENROLLFINGER = 0x08      # Enrolled fingerprint
    EF_FPFTR = 0x100           # Fingerprint score
    EF_FACE = 0x200            # Face event
    EF_ENROLL_SUCCESS = 0x400   # Enrollment success
    EF_ENROLL_FAILED = 0x800    # Enrollment failed
    
    def __init__(self, ip, port=4370):
        self.ip = ip
        self.port = port
        self.socket = None
        self.session_id = 0
        self.reply_number = 0
        self.timeout = 5  # timeout em segundos
        
    def connect(self):
        """Estabelece conexão com o dispositivo"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
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
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
            
    def disconnect(self):
        """Fecha a conexão"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except:
            pass
            
    def send_command(self, command, data=b''):
        """Envia um comando para o dispositivo"""
        try:
            if not self.socket:
                print("[ZK-PROTO] Socket não está conectado")
                return None
                
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
            total_sent = 0
            while total_sent < len(packet):
                sent = self.socket.send(packet[total_sent:])
                if sent == 0:
                    raise RuntimeError("Conexão quebrada")
                total_sent += sent
            
            # Incrementa o número de resposta
            self.reply_number += 1
            
            # Recebe a resposta
            response = self.receive_reply()
            return response
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao enviar comando: {str(e)}")
            return None
            
    def disable_device(self):
        """Desabilita o dispositivo temporariamente"""
        try:
            print("[ZK-PROTO] Desabilitando dispositivo...")
            response = self.send_command(self.CMD_DISABLEDEVICE)
            return response and response.get('command') == self.CMD_ACK_OK
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao desabilitar dispositivo: {str(e)}")
            return False
            
    def enable_device(self):
        """Reabilita o dispositivo"""
        try:
            print("[ZK-PROTO] Reabilitando dispositivo...")
            response = self.send_command(self.CMD_ENABLEDEVICE)
            return response and response.get('command') == self.CMD_ACK_OK
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao reabilitar dispositivo: {str(e)}")
            return False
            
    def free_data(self):
        """Limpa o buffer do dispositivo"""
        try:
            print("[ZK-PROTO] Limpando buffer do dispositivo...")
            response = self.send_command(self.CMD_FREE_DATA)
            return response and response.get('command') == self.CMD_ACK_OK
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao limpar buffer: {str(e)}")
            return False
            
    def start_face_enrollment(self, user_id):
        """Inicia o processo de cadastro facial"""
        try:
            print(f"[ZK-PROTO] Iniciando cadastro facial para usuário {user_id}")
            
            # Desabilita o dispositivo primeiro
            if not self.disable_device():
                print("[ZK-PROTO] Falha ao desabilitar dispositivo")
                return False
                
            # Limpa o buffer do dispositivo
            if not self.free_data():
                print("[ZK-PROTO] Falha ao limpar buffer")
                self.enable_device()  # Tenta reabilitar antes de retornar
                return False
            
            # Cancela qualquer operação pendente
            self.cancel_operation()
            
            # Ativa a função facial
            data = b'FaceFunOn'
            response = self.send_command(self.CMD_FACE_FUNCTION, data)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao ativar função facial")
                self.enable_device()  # Tenta reabilitar antes de retornar
                return False
                
            # Prepara o dispositivo para receber dados
            response = self.send_command(self.CMD_PREPARE_DATA)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao preparar dispositivo")
                self.enable_device()  # Tenta reabilitar antes de retornar
                return False
                
            # Configura o modo de captura facial
            data = pack('<I', int(user_id))  # User ID (4 bytes)
            data += pack('<H', 50)           # Face ID (2 bytes)
            data += pack('<H', 12)           # Flag (2 bytes)
            data += pack('<H', 1)            # Enable realtime events
            
            # Envia o comando de início de cadastro
            response = self.send_command(self.CMD_STARTENROLL, data)
            
            if response and response.get('command') == self.CMD_ACK_OK:
                print("[ZK-PROTO] Cadastro iniciado com sucesso")
                return True
                
            print("[ZK-PROTO] Falha ao iniciar cadastro")
            self.enable_device()  # Tenta reabilitar antes de retornar
            return False
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro no cadastro: {str(e)}")
            self.enable_device()  # Tenta reabilitar em caso de erro
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
            if not self.socket:
                return None
                
            # Recebe o cabeçalho (8 bytes)
            header = self._recv_all(8)
            if not header or len(header) < 8:
                return None
                
            # Extrai o tamanho do payload
            payload_size = unpack('<I', header[4:8])[0]
            
            # Recebe o payload
            payload = self._recv_all(payload_size)
            if not payload or len(payload) < payload_size:
                return None
                
            # Extrai os campos do payload
            command = unpack('<H', payload[0:2])[0]
            checksum = unpack('<H', payload[2:4])[0]
            session_id = unpack('<H', payload[4:6])[0]
            reply_id = unpack('<H', payload[6:8])[0]
            
            # Verifica se é um evento em tempo real
            if command == 0x01f4:  # CMD_REG_EVENT
                event_code = session_id  # No caso de eventos, session_id contém o código do evento
                data = payload[8:] if len(payload) > 8 else b''
                return {
                    'command': command,
                    'event': event_code,
                    'data': data
                }
            
            # Resposta normal
            data = payload[8:] if len(payload) > 8 else b''
            return {
                'command': command,
                'session_id': session_id,
                'reply_id': reply_id,
                'data': data
            }
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao receber resposta: {str(e)}")
            return None
            
    def _recv_all(self, size):
        """Recebe todos os bytes solicitados"""
        try:
            data = bytearray()
            while len(data) < size:
                packet = self.socket.recv(size - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return data
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao receber dados: {str(e)}")
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

    def init_camera(self):
        """Inicializa a câmera do dispositivo"""
        try:
            print("[ZK-PROTO] Inicializando câmera...")
            
            # Envia comando de inicialização da câmera
            response = self.send_command(self.CMD_INIT_CAMERA)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao inicializar câmera")
                return False
                
            # Configura parâmetros da câmera
            data = pack('<I', 0x01)  # Modo de captura facial
            data += pack('<I', 0x02)  # Qualidade da imagem
            data += pack('<I', 480)   # Largura da resolução
            data += pack('<I', 640)   # Altura da resolução
            data += pack('<I', 30)    # FPS reduzido para maior estabilidade
            data += pack('<I', 0x01)  # Formato da imagem (1 = JPEG)
            
            response = self.send_command(self.CMD_CAMERA_CONFIG, data)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao configurar câmera")
                return False
                
            # Aguarda a câmera inicializar
            time.sleep(2)
                
            # Inicia detecção facial
            response = self.send_command(self.CMD_FACE_DETECT)
            if not response or response.get('command') != self.CMD_ACK_OK:
                print("[ZK-PROTO] Falha ao iniciar detecção facial")
                return False
                
            print("[ZK-PROTO] Câmera inicializada com sucesso")
            return True
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao inicializar câmera: {str(e)}")
            return False 

    def upload_face_photo(self, user_id, photo_data):
        """
        Faz upload de uma foto para um usuário
        :param user_id: ID do usuário
        :param photo_data: Bytes da imagem JPEG
        """
        try:
            print(f"[ZK-PROTO] Iniciando upload de foto para usuário {user_id}")
            
            # Desabilita o dispositivo primeiro
            self.disable_device()
            time.sleep(0.5)
            
            try:
                # Limpa qualquer dado pendente
                self.free_data()
                time.sleep(0.5)
                
                # Prepara o comando para upload de foto
                command_data = pack('<IIII', 
                    0x0B,               # Comando de face
                    int(user_id),       # ID do usuário
                    len(photo_data),    # Tamanho da foto
                    0x02                # Operação: upload de foto
                )
                
                # Envia o comando inicial
                response = self.send_command(self.CMD_UPLOAD_PHOTO, command_data)
                if not response or response.get('command') != self.CMD_ACK_OK:
                    print("[ZK-PROTO] Falha ao iniciar upload")
                    return False
                    
                # Envia os dados da foto em chunks
                chunk_size = 1024
                total_sent = 0
                while total_sent < len(photo_data):
                    chunk = photo_data[total_sent:total_sent + chunk_size]
                    chunk_data = pack('<I', len(chunk)) + chunk
                    response = self.send_command(self.CMD_DATA, chunk_data)
                    if not response or response.get('command') != self.CMD_ACK_OK:
                        print("[ZK-PROTO] Falha ao enviar chunk")
                        return False
                    total_sent += len(chunk)
                    print(f"[ZK-PROTO] Enviados {total_sent} de {len(photo_data)} bytes")
                    
                # Finaliza o upload
                finish_data = pack('<II', int(user_id), 0x01)  # 0x01 = finalizar upload
                response = self.send_command(self.CMD_UPLOAD_PHOTO, finish_data)
                if not response or response.get('command') != self.CMD_ACK_OK:
                    print("[ZK-PROTO] Falha ao finalizar upload")
                    return False
                    
                print("[ZK-PROTO] Upload de foto concluído com sucesso")
                return True
                
            finally:
                self.free_data()
                time.sleep(0.5)
                self.enable_device()
                time.sleep(0.5)
                
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao fazer upload da foto: {str(e)}")
            self.enable_device()
            return False

    def set_user(self, uid=None, name='', privilege=0, password='', group_id='', user_id='', card=0):
        """
        Cria ou atualiza um usuário pelo uid

        :param uid: ID único do usuário
        :param name: nome do usuário
        :param privilege: nível de privilégio (0=normal, 14=admin)
        :param password: senha do usuário
        :param group_id: ID do grupo
        :param user_id: ID alternativo do usuário
        :param card: número do cartão
        :return: bool
        """
        try:
            # Garante que temos um uid válido
            if uid is None:
                raise ValueError("UID não pode ser None")
                
            # Garante que temos um user_id válido
            if not user_id:
                user_id = str(uid)
                
            # Garante que o nome não está vazio
            if not name:
                name = f"User_{uid}"
                
            # Garante que o privilégio é válido (0 = normal, 14 = admin)
            if privilege not in [0, 14]:
                privilege = 0
                
            # Garante que group_id é uma string válida
            if not group_id:
                group_id = '0'
                
            # Prepara os dados do usuário
            name_bytes = name.encode('utf-8')
            password_bytes = password.encode('utf-8') if password else b''
            user_id_bytes = str(user_id).encode('utf-8')
            group_id_bytes = str(group_id).encode('utf-8')
            
            # Monta o comando
            data = pack('<H', uid)  # uid - 2 bytes
            data += pack('<B', privilege)  # privilege - 1 byte
            data += password_bytes.ljust(8, b'\x00')[:8]  # password - 8 bytes
            data += name_bytes.ljust(24, b'\x00')[:24]  # name - 24 bytes
            data += pack('<I', int(card))  # card - 4 bytes
            data += b'\x00'  # separator - 1 byte
            data += group_id_bytes.ljust(7, b'\x00')[:7]  # group_id - 7 bytes
            data += user_id_bytes.ljust(24, b'\x00')[:24]  # user_id - 24 bytes
            
            # Envia o comando
            response = self.send_command(self.CMD_USER_WRQ, data)
            
            if response and response.get('status'):
                print(f"[ZK-PROTO] Usuário {uid} cadastrado/atualizado com sucesso")
                return True
                
            print(f"[ZK-PROTO] Erro ao cadastrar/atualizar usuário {uid}")
            return False
            
        except Exception as e:
            print(f"[ZK-PROTO] Erro ao cadastrar/atualizar usuário: {str(e)}")
            return False 