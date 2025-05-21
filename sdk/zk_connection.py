import os
import sys
import json
import time
from pathlib import Path

# Obtém o diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent

# Adiciona a biblioteca pyzk ao PYTHONPATH
pyzk_lib_path = os.path.join(ROOT_DIR, 'sdks_oficiais', 'biblioteca pyzk')
if pyzk_lib_path not in sys.path:
    sys.path.insert(0, pyzk_lib_path)

try:
    from zk import ZK, const
except ImportError as e:
    print(f"Erro ao importar a biblioteca pyzk: {e}")
    print("Certifique-se de que a biblioteca pyzk está instalada e no PYTHONPATH")

class ZKConnection:
    """
    Classe para gerenciar a conexão com dispositivos ZKTeco usando a biblioteca pyzk.
    Esta classe fornece uma interface para conectar, desconectar e executar operações 
    comuns em dispositivos ZKTeco.
    """
    
    def __init__(self, ip_address='192.168.50.11', port=4370, timeout=10, password=0, verbose=False):
        """
        Inicializa a conexão com o dispositivo ZKTeco.
        
        Args:
            ip_address: Endereço IP do dispositivo
            port: Porta do dispositivo (normalmente 4370)
            timeout: Tempo limite em segundos para a conexão
            password: Senha do dispositivo (normalmente 0)
            verbose: Se True, exibe mensagens de debug
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.password = password
        self.verbose = verbose
        self.zk = ZK(ip_address, port=port, timeout=timeout, password=password, verbose=verbose)
        self.conn = None
        self.is_connected = False
        
    def connect(self):
        """
        Conecta ao dispositivo ZKTeco.
        
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário
        """
        if self.is_connected:
            return True
            
        try:
            print(f"Conectando ao dispositivo {self.ip_address}:{self.port}...")
            self.conn = self.zk.connect()
            self.is_connected = True
            print(f"Conectado com sucesso ao dispositivo {self.ip_address}")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao dispositivo: {e}")
            self.is_connected = False
            self.conn = None
            return False
            
    def disconnect(self):
        """
        Desconecta do dispositivo ZKTeco.
        
        Returns:
            bool: True se a desconexão foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            return True
            
        try:
            self.conn.disconnect()
            self.is_connected = False
            self.conn = None
            print(f"Desconectado do dispositivo {self.ip_address}")
            return True
        except Exception as e:
            print(f"Erro ao desconectar do dispositivo: {e}")
            return False
            
    def disable_device(self):
        """
        Desativa o dispositivo temporariamente para operações administrativas.
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            self.conn.disable_device()
            return True
        except Exception as e:
            print(f"Erro ao desativar o dispositivo: {e}")
            return False
            
    def enable_device(self):
        """
        Reativa o dispositivo após operações administrativas.
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            self.conn.enable_device()
            return True
        except Exception as e:
            print(f"Erro ao reativar o dispositivo: {e}")
            return False
            
    def get_device_info(self):
        """
        Obtém informações do dispositivo.
        
        Returns:
            dict: Dicionário com informações do dispositivo ou None em caso de erro
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return None
            
        try:
            info = {
                'firmware_version': self.conn.get_firmware_version(),
                'device_name': self.conn.get_device_name(),
                'serial_number': self.conn.get_serialnumber(),
                'mac_address': self.conn.get_mac(),
                'face_version': self.conn.get_face_version(),
                'platform': self.conn.get_platform(),
                'device_time': self.conn.get_time()
            }
            
            # Informações de rede (IP, máscara, gateway)
            try:
                network_info = self.conn.get_network_params()
                info.update(network_info)
            except:
                pass
                
            # Informações de capacidade
            try:
                self.conn.read_sizes()
                info.update({
                    'users': self.conn.users,
                    'fingers': self.conn.fingers,
                    'faces': self.conn.faces,
                    'records': self.conn.records,
                    'users_capacity': self.conn.users_cap,
                    'fingers_capacity': self.conn.fingers_cap,
                    'faces_capacity': self.conn.faces_cap
                })
            except:
                pass
                
            return info
        except Exception as e:
            print(f"Erro ao obter informações do dispositivo: {e}")
            return None
            
    def get_users(self):
        """
        Obtém a lista de usuários cadastrados no dispositivo.
        
        Returns:
            list: Lista de usuários ou None em caso de erro
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return None
            
        try:
            users_list = []
            users = self.conn.get_users()
            
            for user in users:
                user_data = {
                    'uid': user.uid,
                    'name': user.name,
                    'user_id': user.user_id,
                    'privilege': user.privilege,
                    'password': user.password,
                    'group_id': user.group_id,
                    'card': user.card
                }
                users_list.append(user_data)
                
            return users_list
        except Exception as e:
            print(f"Erro ao obter lista de usuários: {e}")
            return None
            
    def set_user(self, user_id, name, privilege=0, password='', group_id='', card=0):
        """
        Adiciona ou atualiza um usuário no dispositivo.
        
        Args:
            user_id: ID do usuário
            name: Nome do usuário
            privilege: Privilégio do usuário (0=Normal, 14=Admin)
            password: Senha do usuário
            group_id: ID do grupo
            card: Número do cartão
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            self.disable_device()
            self.conn.set_user(user_id=user_id, name=name, privilege=privilege, 
                          password=password, group_id=group_id, card=card)
            self.enable_device()
            return True
        except Exception as e:
            print(f"Erro ao adicionar/atualizar usuário: {e}")
            self.enable_device()
            return False
            
    def delete_user(self, user_id):
        """
        Remove um usuário do dispositivo.
        
        Args:
            user_id: ID do usuário a ser removido
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            self.disable_device()
            self.conn.delete_user(user_id=user_id)
            self.enable_device()
            return True
        except Exception as e:
            print(f"Erro ao remover usuário: {e}")
            self.enable_device()
            return False
            
    def activate_face_capture(self):
        """
        Ativa o modo de captura de faces no dispositivo.
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            # Verifica se o dispositivo tem suporte para faces
            face_version = self.conn.get_face_version()
            if face_version is not None and face_version > 0:
                print(f"Dispositivo suporta reconhecimento facial (versão {face_version})")
            else:
                print("Este dispositivo não parece suportar reconhecimento facial")
                if face_version is not None:
                    print(f"Versão do algoritmo facial retornada: {face_version}")
                return False
                
            # Tenta iniciar o modo de verificação no dispositivo
            try:
                print("Habilitando o dispositivo...")
                self.conn.enable_device()
                
                # Se tiver um método específico para ativar o modo de reconhecimento facial, use-o primeiro
                face_method_used = False
                
                if hasattr(self.conn, 'start_verify'):
                    try:
                        print("Tentando método start_verify...")
                        result = self.conn.start_verify()
                        print(f"Resultado de start_verify: {result}")
                        face_method_used = True
                    except Exception as e:
                        print(f"Erro ao usar método start_verify: {e}")
                
                if not face_method_used and hasattr(self.conn, 'start_identify'):
                    try:
                        print("Tentando método start_identify...")
                        result = self.conn.start_identify()
                        print(f"Resultado de start_identify: {result}")
                        face_method_used = True
                    except Exception as e:
                        print(f"Erro ao usar método start_identify: {e}")
                
                # Se nenhum método específico funcionou, use o comando de baixo nível
                if not face_method_used:
                    print("Usando comando de baixo nível CMD_STARTVERIFY...")
                    # CMD_STARTVERIFY = 60 é o comando para iniciar verificação
                    result = self._send_command(const.CMD_STARTVERIFY)
                    
                    if result and isinstance(result, dict) and result.get('status') == True:
                        print(f"Modo de verificação ativado: {result}")
                        return True
                    else:
                        print(f"Falha ao ativar modo de verificação: {result}")
                        
                        # Última tentativa: tentar método SDK específico da ZKTeco (se disponível)
                        if hasattr(self.conn, 'verify_user'):
                            try:
                                print("Tentando método verify_user como última alternativa...")
                                result = self.conn.verify_user()
                                print(f"Resultado de verify_user: {result}")
                                return True
                            except Exception as e:
                                print(f"Erro ao usar método verify_user: {e}")
                                return False
                        return False
                
                return True
            except Exception as e:
                print(f"Erro ao ativar modo de verificação: {e}")
                return False
        except Exception as e:
            print(f"Erro ao ativar captura facial: {e}")
            return False
            
    def _send_command(self, command, data=None):
        """
        Envia um comando direto para o dispositivo.
        
        Args:
            command: Código do comando a ser enviado
            data: Dados adicionais para o comando (opcional)
            
        Returns:
            Resultado do comando ou None em caso de erro
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return None
            
        try:
            # Mapeia os comandos conhecidos para melhor clareza
            command_names = {
                const.CMD_STARTVERIFY: "CMD_STARTVERIFY (60)",
                const.CMD_STARTENROLL: "CMD_STARTENROLL (61)",
                const.CMD_CANCELCAPTURE: "CMD_CANCELCAPTURE (62)",
                const.CMD_ACK_OK: "CMD_ACK_OK (2000)",
                const.CMD_ACK_ERROR: "CMD_ACK_ERROR (2001)",
                const.CMD_ACK_DATA: "CMD_ACK_DATA (2002)",
                const.CMD_ACK_RETRY: "CMD_ACK_RETRY (2003)",
                const.CMD_PREPARE_DATA: "CMD_PREPARE_DATA (2004)"
            }
            
            command_name = command_names.get(command, f"Comando desconhecido ({command})")
            print(f"Enviando comando: {command_name}")
            
            # Como a biblioteca pyzk não expõe diretamente todos os comandos,
            # precisamos usar uma solução alternativa
            if command in [const.CMD_STARTVERIFY, const.CMD_STARTENROLL, const.CMD_CANCELCAPTURE]:
                # Estes são comandos de alta prioridade para o dispositivo
                try:
                    # Tenta usar o método interno de envio de comando
                    if hasattr(self.conn, '_ZK__send_command'):
                        result = self.conn._ZK__send_command(command, data)
                        print(f"Comando {command_name} enviado com sucesso")
                        return {'status': True, 'code': 2000, 'result': result}
                    else:
                        # Tenta usar o método send_command se disponível
                        if hasattr(self.conn, 'send_command'):
                            result = self.conn.send_command(command, data)
                            print(f"Comando {command_name} enviado com sucesso")
                            return {'status': True, 'code': 2000, 'result': result}
                        else:
                            print(f"Método de envio de comando não encontrado")
                            return {'status': False, 'code': 2001, 'message': 'Método de envio não disponível'}
                except Exception as e:
                    print(f"Erro ao enviar comando {command_name}: {e}")
                    return {'status': False, 'code': 2001, 'message': str(e)}
            else:
                print(f"Comando {command_name} não implementado diretamente")
                print("Tentando enviar usando método genérico...")
                
                # Tenta enviar usando o método genérico
                try:
                    if hasattr(self.conn, '_ZK__send_command'):
                        result = self.conn._ZK__send_command(command, data)
                        return {'status': True, 'code': 2000, 'result': result}
                    else:
                        return {'status': False, 'code': 2001, 'message': 'Método de envio não disponível'}
                except Exception as e:
                    print(f"Erro ao enviar comando genérico: {e}")
                    return {'status': False, 'code': 2001, 'message': str(e)}
                
        except Exception as e:
            print(f"Erro ao preparar comando: {e}")
            return None
            
    def enroll_user_face(self, user_id, name=''):
        """
        Inicia o processo de registro de face para um usuário.
        
        Args:
            user_id: ID do usuário
            name: Nome do usuário (opcional)
            
        Returns:
            bool: True se a operação foi iniciada com sucesso, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            # Verifica se o dispositivo suporta faces
            face_version = self.conn.get_face_version()
            if not face_version or face_version <= 0:
                print("Este dispositivo não suporta reconhecimento facial")
                return False
            else:
                print(f"Versão do algoritmo facial: {face_version}")
                
            # Primeiro, registra o usuário básico se ainda não existir
            try:
                users = self.conn.get_users()
                user_exists = any(user.user_id == user_id for user in users)
                
                if not user_exists:
                    if not name:
                        print("Nome de usuário necessário para criar novo usuário")
                        return False
                        
                    print(f"Adicionando usuário {user_id} ({name})")
                    if not self.set_user(user_id=user_id, name=name):
                        print("Falha ao criar usuário básico")
                        return False
                    print("Usuário criado com sucesso")
                else:
                    print(f"Usuário {user_id} já existe no dispositivo")
            except Exception as e:
                print(f"Erro ao verificar/criar usuário: {e}")
                return False
                
            # Inicia o registro de face
            try:
                print(f"Iniciando registro de face para o usuário {user_id}")
                
                # Desativa o dispositivo para operações administrativas
                print("Desativando o dispositivo temporariamente...")
                self.conn.disable_device()
                
                # Tentativa 1: Usa o método enroll_user se disponível
                if hasattr(self.conn, 'enroll_user'):
                    print("Usando método enroll_user...")
                    try:
                        result = self.conn.enroll_user(user_id=user_id)
                        print(f"Resultado do enroll_user: {result}")
                        self.conn.enable_device()
                        return True
                    except Exception as e:
                        print(f"Erro ao usar enroll_user: {e}")
                        # Continue para a próxima tentativa
                
                # Tentativa 2: Tenta usar a função face_enroll_start da biblioteca
                if hasattr(self.conn, 'face_enroll_start'):
                    print("Usando método face_enroll_start...")
                    try:
                        result = self.conn.face_enroll_start(user_id=user_id)
                        print(f"Resultado do face_enroll_start: {result}")
                        self.conn.enable_device()
                        return True
                    except Exception as e:
                        print(f"Erro ao usar face_enroll_start: {e}")
                        # Continue para a próxima tentativa
                
                # Tentativa 3: Usar os comandos diretos
                print("Usando comandos diretos...")
                
                # CMD_STARTENROLL = 61 (0x3D) é o comando para iniciar registro
                try:
                    # Vamos tentar primeiro o comando genérico de registro
                    cmd_result = self._send_command(const.CMD_STARTENROLL)
                    print(f"Resultado do comando CMD_STARTENROLL: {cmd_result}")
                    
                    # Verifica se foi bem-sucedido antes de continuar
                    if cmd_result and isinstance(cmd_result, dict) and cmd_result.get('status') == True:
                        print("Comando de registro enviado com sucesso")
                        print("Aguardando registro facial no dispositivo...")
                        print("Por favor, siga as instruções no dispositivo para completar o registro")
                        
                        # Ativa o dispositivo após o comando
                        self.conn.enable_device()
                        return True
                    else:
                        print("Falha ao enviar comando de registro")
                except Exception as e:
                    print(f"Erro ao enviar comando direto: {e}")
                
                # Se chegou aqui, todas as tentativas falharam
                print("Todas as tentativas de iniciar o registro facial falharam")
                self.conn.enable_device()
                return False
                
            except Exception as e:
                print(f"Erro ao iniciar registro de face: {e}")
                # Garante que o dispositivo seja reativado
                try:
                    self.conn.enable_device()
                except:
                    pass
                return False
        except Exception as e:
            print(f"Erro no processo de registro de face: {e}")
            return False
            
    def live_capture(self, callback=None, timeout=10):
        """
        Inicia a captura de eventos em tempo real.
        
        Args:
            callback: Função de callback para processar os eventos
            timeout: Tempo limite em segundos (não utilizado diretamente)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            print("Iniciando captura em tempo real...")
            # Ativa o modo de captura de faces
            self.activate_face_capture()
            self.conn.enable_device()
            
            # Se não for fornecido um callback, usamos um padrão
            if not callback:
                def callback(event):
                    print(f"Evento: {event}")
                    
            # Inicia a contagem de tempo para o timeout
            start_time = time.time()
                    
            # A biblioteca pyzk já tem um método para live_capture
            # O parâmetro timeout não é utilizado diretamente aqui
            try:
                print("Aguardando eventos... (pressione Ctrl+C para cancelar)")
                for event in self.conn.live_capture():
                    if event:
                        # Processa o tipo de evento
                        if event.punch == 3:  # Punch 3 geralmente indica reconhecimento facial
                            print(f"Reconhecimento facial detectado para o usuário {event.user_id}")
                        elif event.punch == 0:  # Punch 0 geralmente indica entrada
                            print(f"Entrada registrada para o usuário {event.user_id}")
                            
                        # Chama o callback fornecido
                        if callback:
                            callback(event)
                    
                    # Verifica se já passou o tempo limite (precisamos implementar manualmente)
                    if timeout and (time.time() - start_time) > timeout:
                        print(f"Tempo limite de {timeout} segundos atingido.")
                        break
            except KeyboardInterrupt:
                print("\nCaptura interrompida pelo usuário.")
                
            return True
        except Exception as e:
            print(f"Erro na captura em tempo real: {e}")
            return False
            
    def restart_device(self):
        """
        Reinicia o dispositivo.
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
            
        try:
            self.conn.restart()
            self.is_connected = False
            self.conn = None
            return True
        except Exception as e:
            print(f"Erro ao reiniciar o dispositivo: {e}")
            return False
            
    def get_attendance(self):
        """
        Obtém os registros de presença do dispositivo.
        
        Returns:
            list: Lista de registros de presença ou None em caso de erro
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return None
            
        try:
            attendance_list = []
            attendances = self.conn.get_attendance()
            
            for attendance in attendances:
                attendance_data = {
                    'user_id': attendance.user_id,
                    'timestamp': str(attendance.timestamp),
                    'status': attendance.status,
                    'punch': attendance.punch,
                }
                attendance_list.append(attendance_data)
                
            return attendance_list
        except Exception as e:
            print(f"Erro ao obter registros de presença: {e}")
            return None
            
    def enroll_face(self, user_id, name=''):
        """
        Inicia o processo de registro facial para um usuário.
        Este método é específico para face, diferente do enroll_user que parece iniciar o registro de impressão digital.
        
        Args:
            user_id: ID do usuário
            name: Nome do usuário (opcional)
            
        Returns:
            bool: True se a operação foi iniciada com sucesso, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado. Tentando reconectar...")
            if not self.connect():
                print("Falha ao reconectar ao dispositivo.")
                return False
            print("Reconexão bem-sucedida!")
            
        try:
            # Garante uma conexão estável
            print("Verificando comunicação com o dispositivo...")
            device_info = self.get_device_info()
            if not device_info:
                print("Falha na comunicação com o dispositivo. Tentando reconectar...")
                self.disconnect()
                time.sleep(2)  # Pausa antes de reconectar
                if not self.connect():
                    print("Falha ao reconectar ao dispositivo.")
                    return False
                print("Reconexão bem-sucedida!")
                # Obtém as informações novamente
                device_info = self.get_device_info()
                if not device_info:
                    print("Falha persistente na comunicação com o dispositivo.")
                    return False
            
            # Verifica se o dispositivo suporta faces - baseando-se nas informações do dispositivo
            if device_info and 'face_version' in device_info and device_info['face_version'] > 0:
                print(f"Versão do algoritmo facial: {device_info['face_version']}")
            else:
                print("Este dispositivo parece não suportar reconhecimento facial")
                return False
                
            # Primeiro, registra o usuário básico se ainda não existir
            try:
                users = self.get_users()
                user_exists = False
                
                if users:
                    for user in users:
                        if user['user_id'] == user_id:
                            user_exists = True
                            break
                
                if not user_exists:
                    if not name:
                        print("Nome de usuário necessário para criar novo usuário")
                        return False
                        
                    print(f"Adicionando usuário {user_id} ({name})")
                    if not self.set_user(user_id=user_id, name=name):
                        print("Falha ao criar usuário básico")
                        return False
                    print("Usuário criado com sucesso")
                else:
                    print(f"Usuário {user_id} já existe no dispositivo")
            except Exception as e:
                print(f"Erro ao verificar/criar usuário: {e}")
                return False
                
            # Utiliza o novo método que implementa a sequência correta para registro facial
            # conforme encontrado no SDK oficial em C#
            print("Utilizando sequência correta de comandos para registro facial...")
            return self.manual_face_enroll(user_id)
                
        except Exception as e:
            print(f"Erro ao iniciar o registro facial: {e}")
            return False
            
    def _send_custom_command(self, command, data=None):
        """
        Envia um comando personalizado para o dispositivo.
        Este método é usado para comandos não documentados ou específicos.
        
        Args:
            command: Código do comando personalizado
            data: Dados adicionais para o comando
            
        Returns:
            dict: Resultado do comando ou None em caso de erro
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return None
            
        try:
            print(f"Enviando comando personalizado: {command}")
            
            # Usa a função interna de envio de comando da classe ZK
            if hasattr(self.conn, '_ZK__send_command'):
                result = self.conn._ZK__send_command(command, data)
                print(f"Comando personalizado enviado com sucesso")
                return {'status': True, 'code': 2000, 'result': result}
            elif hasattr(self.conn, 'send_command'):
                result = self.conn.send_command(command, data)
                print(f"Comando personalizado enviado com sucesso")
                return {'status': True, 'code': 2000, 'result': result}
            else:
                print(f"Método de envio de comando não encontrado")
                return {'status': False, 'code': 2001, 'message': 'Método de envio não disponível'}
        except Exception as e:
            print(f"Erro ao enviar comando personalizado: {e}")
            return {'status': False, 'code': 2001, 'message': str(e)}
            
    def test_face_commands(self, user_id):
        """
        Função de diagnóstico para testar diferentes comandos de face.
        Esta função tentará diversos comandos para determinar qual funciona para o registro facial.
        
        Args:
            user_id: ID do usuário para teste
            
        Returns:
            dict: Dicionário com resultados dos testes
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return {"status": False, "message": "Dispositivo não conectado"}
            
        results = {}
        
        try:
            # Verifica suporte a face
            face_version = self.conn.get_face_version()
            print(f"Versão da face: {face_version}")
            results["face_version"] = face_version
            
            # Informações do dispositivo para diagnóstico
            device_info = self.get_device_info()
            print(f"Informações do dispositivo: {device_info}")
            results["device_info"] = device_info
            
            # Converte user_id para string se for inteiro
            if isinstance(user_id, int):
                user_id_str = str(user_id)
            else:
                user_id_str = user_id
                
            # Prepara o dispositivo
            print("Desativando dispositivo para testes...")
            self.conn.disable_device()
            
            try:
                # 1. Tenta comandos padrão da pyzk
                methods = []
                if hasattr(self.conn, 'enroll_user'):
                    methods.append('enroll_user')
                if hasattr(self.conn, 'enroll_face'):
                    methods.append('enroll_face')
                if hasattr(self.conn, 'face_enroll_start'):
                    methods.append('face_enroll_start')
                
                print(f"Métodos disponíveis na biblioteca: {methods}")
                results["available_methods"] = methods
                
                # 2. Testa campos no objeto ZK que poderiam revelar comandos
                interesting_members = {}
                for attr in dir(self.conn):
                    if attr.startswith('CMD_') or 'FACE' in attr.upper() or 'ENROLL' in attr.upper():
                        value = getattr(self.conn, attr)
                        interesting_members[attr] = value
                        
                print(f"Membros relevantes: {interesting_members}")
                results["interesting_members"] = interesting_members
                
                # 3. Testa comandos específicos para face
                # Lista de comandos para testar
                test_commands = [
                    # Comandos padrão
                    (const.CMD_STARTENROLL, "CMD_STARTENROLL (61)"),
                    (const.CMD_STARTVERIFY, "CMD_STARTVERIFY (60)"),
                    
                    # Comandos não documentados para testes
                    (1100, "Custom Face Command 1100"),
                    (1101, "Custom Face Command 1101"),
                    (1102, "Custom Face Command 1102"),
                    
                    # CAPTUREFINGER (pode ser adaptado para face em alguns modelos)
                    (const.CMD_CAPTUREFINGER, "CMD_CAPTUREFINGER (1009)"),
                    
                    # Comandos específicos para face (valores hipotéticos)
                    (1200, "Possible Face Enroll 1200"),
                    (1201, "Possible Face Enroll 1201"),
                    (1202, "Possible Face Verify 1202")
                ]
                
                command_results = {}
                for cmd, name in test_commands:
                    try:
                        print(f"Testando comando {name}...")
                        
                        # Prepara dados para o comando (baseado no user_id)
                        command_data = user_id_str.encode().ljust(24, b'\x00')
                        
                        # Tenta enviar o comando
                        result = None
                        if cmd == const.CMD_STARTENROLL:
                            # Para CMD_STARTENROLL, tentar com flag=1 (para possível registro facial)
                            from struct import pack
                            command_data = pack('<24sbb', user_id_str.encode(), 0, 1)
                            
                        result = self._send_custom_command(cmd, command_data)
                        print(f"Resultado do comando {name}: {result}")
                        
                        # Armazena o resultado
                        command_results[name] = result
                        
                        # Espera um pouco para o dispositivo processar
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"Erro ao testar comando {name}: {e}")
                        command_results[name] = {"status": False, "error": str(e)}
                
                results["command_tests"] = command_results
                
                # 4. Tenta abordagens específicas para enroll_user
                # Em alguns casos, o template_id determina se é dedo ou face
                template_tests = {}
                try:
                    for temp_id in [0, 50, 100, 150, 200]:
                        try:
                            print(f"Testando enroll_user com temp_id={temp_id}...")
                            cmd_result = self.conn.enroll_user(uid=int(user_id), temp_id=temp_id, user_id=user_id_str)
                            template_tests[f"temp_id_{temp_id}"] = cmd_result
                            print(f"Resultado: {cmd_result}")
                            
                            # Espera um pouco para o dispositivo processar
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"Erro com temp_id={temp_id}: {e}")
                            template_tests[f"temp_id_{temp_id}"] = {"status": False, "error": str(e)}
                            
                    results["template_tests"] = template_tests
                except Exception as e:
                    print(f"Erro nos testes de template: {e}")
                    results["template_tests"] = {"status": False, "error": str(e)}
                
                # 5. Observa o comportamento do dispositivo após cada comando
                print("\nTestes concluídos. Observe o comportamento do dispositivo e anote qual comando ativou o registro facial.")
                print("Você pode então usar o comando específico que funcionou.")
                
            except Exception as e:
                print(f"Erro durante os testes: {e}")
                results["error"] = str(e)
            finally:
                print("Reativando dispositivo...")
                self.conn.enable_device()
                
            return results
            
        except Exception as e:
            print(f"Erro global no diagnóstico: {e}")
            return {"status": False, "error": str(e)}
            
    def _send_raw_packet(self, data):
        """
        Envia um pacote de dados bruto para o dispositivo.
        Esta é uma função de baixo nível para comunicação direta.
        
        Args:
            data: Dados a serem enviados
            
        Returns:
            dict: Resultado da operação
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return {'status': False, 'message': 'Dispositivo não conectado'}
            
        try:
            print(f"Enviando pacote bruto de {len(data)} bytes")
            
            if hasattr(self.conn, '_ZK__sock') and self.conn._ZK__sock:
                sock = self.conn._ZK__sock
                sock.send(data)
                
                # Tenta ler a resposta
                try:
                    response = sock.recv(1024)
                    print(f"Resposta recebida: {response}")
                    return {'status': True, 'response': response}
                except Exception as e:
                    print(f"Erro ao ler resposta: {e}")
                    return {'status': True, 'message': 'Comando enviado, mas erro ao ler resposta'}
            else:
                print("Socket não disponível")
                return {'status': False, 'message': 'Socket não disponível'}
                
        except Exception as e:
            print(f"Erro ao enviar pacote bruto: {e}")
            return {'status': False, 'message': str(e)}
            
    def manual_face_enroll(self, user_id):
        """
        Inicia o processo de registro facial para um usuário usando a sequência correta de comandos
        baseado no SDK oficial em C#.
        
        A sequência correta é:
        1. REG_START - Inicia o processo de registro
        2. DETECT_FACE_REG - Detecta a face para o registro
        3. ADD_FACE_REG - Adiciona a face detectada
        4. REG_END - Finaliza o processo de registro
        
        Args:
            user_id: ID do usuário para registro facial
            
        Returns:
            bool: True se a operação foi iniciada com sucesso, False caso contrário
        """
        if not self.is_connected or not self.conn:
            print("Dispositivo não conectado")
            return False
        
        # Variável para controlar se o dispositivo está desativado
        device_disabled = False
            
        try:
            # Verifica se o dispositivo suporta faces - baseando-se nas informações do dispositivo
            device_info = self.get_device_info()
            if device_info and 'face_version' in device_info and device_info['face_version'] > 0:
                print(f"Versão do algoritmo facial: {device_info['face_version']}")
            else:
                print("Este dispositivo parece não suportar reconhecimento facial")
                return False
            
            # Prepara o ID do usuário (pode ser necessário formatação específica)
            if isinstance(user_id, int):
                user_id_str = str(user_id)
            else:
                user_id_str = user_id
                
            print(f"Iniciando processo de registro facial para o usuário {user_id_str}")
            
            # Desativa o dispositivo para operações administrativas
            print("Desativando o dispositivo temporariamente...")
            try:
                self.conn.disable_device()
                device_disabled = True
                # Pausa para garantir que o dispositivo tenha tempo para processar
                time.sleep(1)
            except Exception as e:
                print(f"Aviso: Não foi possível desativar o dispositivo: {e}")
                print("Tentando continuar mesmo assim...")
            
            # 1. Inicia o processo de registro (REG_START)
            print("Passo 1: Iniciando processo de registro (REG_START)...")
            reg_start_data = user_id_str.encode().ljust(24, b'\x00')
            result_start = self._send_custom_command(10, reg_start_data)  # 10 = HID_ManageType.REG_START
            
            if not result_start or not isinstance(result_start, dict) or not result_start.get('status'):
                print(f"Falha ao iniciar o processo de registro: {result_start}")
                if device_disabled:
                    try:
                        self.conn.enable_device()
                    except:
                        pass
                return False
                
            print("Processo de registro iniciado com sucesso")
            print("Aguardando 3 segundos para processamento...")
            time.sleep(3)  # Pausa mais longa para garantir processamento
            
            # 2. Detecta a face para registro (DETECT_FACE_REG)
            print("Passo 2: Detectando face para registro (DETECT_FACE_REG)...")
            detect_data = user_id_str.encode().ljust(24, b'\x00')
            result_detect = self._send_custom_command(9, detect_data)  # 9 = HID_ManageType.DETECT_FACE_REG
            
            if not result_detect or not isinstance(result_detect, dict) or not result_detect.get('status'):
                print(f"Falha ao iniciar a detecção de face: {result_detect}")
                print("Tentando método alternativo...")
                
                # Método alternativo: Tentar com o comando 1201 que teve sucesso em diagnósticos anteriores
                print("Método alternativo: Tentando comando 1201 para registro facial...")
                try:
                    alt_data = user_id_str.encode().ljust(24, b'\x00')
                    alt_result = self._send_custom_command(1201, alt_data)
                    
                    if alt_result and isinstance(alt_result, dict) and alt_result.get('status'):
                        print("Comando alternativo enviado com sucesso")
                        print("Aguardando 5 segundos para ativação da câmera...")
                        time.sleep(5)
                    else:
                        print(f"Método alternativo também falhou: {alt_result}")
                        # Último recurso: tentar o comando 1100 que mostrou resultados no diagnóstico
                        print("Último recurso: Tentando comando 1100...")
                        final_result = self._send_custom_command(1100, alt_data)
                        
                        if not final_result or not isinstance(final_result, dict) or not final_result.get('status'):
                            print(f"Todos os métodos de ativação facial falharam")
                            if device_disabled:
                                try:
                                    self.conn.enable_device()
                                except:
                                    pass
                            return False
                        else:
                            print("Comando 1100 enviado com sucesso")
                except Exception as e:
                    print(f"Erro ao tentar método alternativo: {e}")
                    if device_disabled:
                        try:
                            self.conn.enable_device()
                        except:
                            pass
                    return False
            else:
                print("Detecção de face iniciada com sucesso. O dispositivo deve mostrar a interface da câmera.")
                
            print("Aguardando 5 segundos para ativação da câmera...")
            time.sleep(5)  # Pausa mais longa para ativação da câmera
            
            # Instrução para o usuário
            print("\nPor favor, posicione o rosto na frente da câmera do dispositivo.")
            print("Siga as instruções na tela do dispositivo.")
            print("Aguardando 10 segundos para captura facial...")
            
            # Pausa para permitir a captura do rosto pelo dispositivo
            time.sleep(10)
            
            # 3. Adiciona a face detectada (ADD_FACE_REG) - Este comando será chamado automaticamente pelo dispositivo
            print("\nO dispositivo deve prosseguir automaticamente com o registro da face.")
            print("Após a captura bem-sucedida, o dispositivo irá processar e armazenar a face.")
            print("Aguardando 5 segundos para processamento...")
            time.sleep(5)
            
            # 4. Finaliza o processo de registro (REG_END)
            print("\nFinalizando o processo de registro (REG_END)...")
            end_data = user_id_str.encode().ljust(24, b'\x00')
            result_end = self._send_custom_command(11, end_data)  # 11 = HID_ManageType.REG_END
            
            # Tenta uma segunda vez o comando REG_END se falhar
            if not result_end or not isinstance(result_end, dict) or not result_end.get('status'):
                print(f"Aviso: Primeira tentativa de finalizar o processo falhou: {result_end}")
                print("Tentando novamente em 2 segundos...")
                time.sleep(2)
                result_end = self._send_custom_command(11, end_data)
            
            # Reativa o dispositivo
            if device_disabled:
                try:
                    print("Reativando o dispositivo...")
                    self.conn.enable_device()
                except Exception as e:
                    print(f"Aviso: Não foi possível reativar o dispositivo: {e}")
            
            print("\nProcesso de registro facial concluído.")
            print("Por favor, verifique no dispositivo se o registro foi bem-sucedido.")
            return True
                
        except Exception as e:
            print(f"Erro durante o processo de registro facial: {e}")
            # Garante que o dispositivo seja reativado mesmo em caso de erro
            if device_disabled:
                try:
                    self.conn.enable_device()
                except:
                    pass
            return False 