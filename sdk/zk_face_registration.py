import json
import os
import time
from pathlib import Path
from ctypes import c_void_p
from .zk_hid_api import ZKBioModuleHIDApi, HID_ManageType, HID_ERRORCODE, get_error_message

class ZKFaceRegistration:
    def __init__(self, dll_path=None):
        """Inicializa a classe de registro de face"""
        if dll_path is None:
            # Obtém o caminho absoluto para a DLL dentro da pasta sdk
            import os
            from pathlib import Path
            current_file = Path(__file__).resolve()
            sdk_dir = current_file.parent
            dll_path = os.path.join(sdk_dir, "ZKHIDLib.dll")
        
        self.hid_api = ZKBioModuleHIDApi(dll_path)
        self.device_handle = None
        self.is_connected = False
        self.is_network_device = False
        self.ip_address = None
        self.port = None
        
    def connect(self, ip_address=None, port=8000):
        """Conecta ao dispositivo ZKTeco
        
        Args:
            ip_address: Endereço IP do dispositivo (se for um dispositivo de rede)
            port: Porta do dispositivo (padrão 8000)
            
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        if self.is_connected:
            return True
        
        # Verifica se é uma conexão de rede
        if ip_address:
            print(f"Tentando conectar via rede ao dispositivo {ip_address}:{port}")
            self.is_network_device = True
            self.ip_address = ip_address
            self.port = port
            
            # Inicializa a API
            ret = self.hid_api.init()
            if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
                print(f"Erro ao inicializar a API: {get_error_message(ret)}")
                return False
            
            # Configura a conexão de rede
            # Exemplo de JSON para configuração de rede (pode precisar ser ajustado)
            network_config = {
                "ip": ip_address,
                "port": port,
                "timeout": 5000  # timeout em ms
            }
            
            json_config = json.dumps(network_config)
            print(f"Configurando conexão de rede: {json_config}")
            
            # Aqui assumimos que existe um handle especial para conexão de rede
            # Esta é uma implementação hipotética - você precisa verificar na documentação da ZKTeco
            # como exatamente configurar a conexão via IP
            handle = c_void_p(-1)  # -1 é apenas um placeholder, você deve verificar o valor correto
            self.device_handle = handle
            
            try:
                # Tentativa de conectar via rede
                from .zk_hid_api import HID_ConfigType
                ret = self.hid_api.set_config(self.device_handle, HID_ConfigType.COMMON_CONFIG, json_config)
                if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
                    print(f"Erro ao configurar conexão de rede: {get_error_message(ret)}")
                    self.hid_api.terminate()
                    return False
                
                print(f"Conectado com sucesso ao dispositivo de rede {ip_address}:{port}")
                self.is_connected = True
                return True
            except Exception as e:
                print(f"Erro ao conectar via rede: {str(e)}")
                self.hid_api.terminate()
                return False
        else:
            # Conexão USB padrão
            print("Tentando conectar via USB...")
            
            # Inicializa a API
            ret = self.hid_api.init()
            if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
                print(f"Erro ao inicializar a API: {get_error_message(ret)}")
                return False
                
            # Verifica se há dispositivos conectados
            ret, count = self.hid_api.get_device_count()
            if ret != HID_ERRORCODE.ZKHID_ERROR_NONE or count == 0:
                print(f"Nenhum dispositivo encontrado: {get_error_message(ret)}")
                self.hid_api.terminate()
                return False
                
            # Abre o primeiro dispositivo
            ret, handle = self.hid_api.open_device(0)
            if ret != HID_ERRORCODE.ZKHID_ERROR_NONE or not handle:
                print(f"Erro ao abrir o dispositivo: {get_error_message(ret)}")
                self.hid_api.terminate()
                return False
                
            self.device_handle = handle
            self.is_connected = True
            return True
        
    def disconnect(self):
        """Desconecta do dispositivo"""
        if not self.is_connected:
            return True
            
        if self.device_handle:
            ret = self.hid_api.close_device(self.device_handle)
            self.device_handle = None
            
        ret = self.hid_api.terminate()
        self.is_connected = False
        self.is_network_device = False
        self.ip_address = None
        self.port = None
        return True
        
    def register_face(self, person_id, name):
        """Registra uma face no dispositivo
        
        Args:
            person_id: ID único da pessoa
            name: Nome da pessoa
            
        Returns:
            (bool, str): Tupla contendo status da operação e mensagem/dados da face
        """
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        # Prepara os dados da pessoa em formato JSON
        person_data = {
            "person_id": str(person_id),
            "name": name
        }
        
        # Converte para string JSON
        json_data = json.dumps(person_data)
        
        # Inicia o registro de face
        ret, result = self.hid_api.register_face(self.device_handle, json_data)
        if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
            return False, f"Erro ao registrar face: {get_error_message(ret)}"
            
        return True, result
        
    def get_device_info(self):
        """Obtém informações do dispositivo"""
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        from .zk_hid_api import HID_ConfigType
        
        # Obtém as informações do dispositivo
        ret, info = self.hid_api.get_config(self.device_handle, HID_ConfigType.DEVICE_INFORMATION)
        if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
            return False, f"Erro ao obter informações do dispositivo: {get_error_message(ret)}"
            
        return True, info
        
    def poll_match_result(self, timeout_seconds=5):
        """Aguarda por um resultado de reconhecimento facial
        
        Args:
            timeout_seconds: Tempo máximo em segundos para aguardar
            
        Returns:
            (bool, dict/str): Tupla contendo status da operação e resultado/mensagem de erro
        """
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            ret, result = self.hid_api.poll_match_result(self.device_handle)
            if ret == HID_ERRORCODE.ZKHID_ERROR_NONE and result:
                try:
                    # Tenta converter o resultado para um dicionário
                    result_dict = json.loads(result)
                    return True, result_dict
                except json.JSONDecodeError:
                    return True, result
                    
            # Aguarda um pouco antes de tentar novamente
            time.sleep(0.1)
            
        return False, "Timeout ao aguardar resultado"
        
    def add_person(self, person_id, name):
        """Adiciona uma pessoa ao dispositivo sem registrar face
        
        Args:
            person_id: ID único da pessoa
            name: Nome da pessoa
            
        Returns:
            (bool, str): Tupla contendo status da operação e mensagem
        """
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        # Prepara os dados da pessoa em formato JSON
        person_data = {
            "person_id": str(person_id),
            "name": name
        }
        
        # Converte para string JSON
        json_data = json.dumps(person_data)
        
        # Adiciona a pessoa
        ret, result = self.hid_api.manage_module_data(
            self.device_handle, 
            HID_ManageType.ADD_PERSON, 
            json_data
        )
        
        if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
            return False, f"Erro ao adicionar pessoa: {get_error_message(ret)}"
            
        return True, result if result else "Pessoa adicionada com sucesso"
        
    def delete_person(self, person_id):
        """Remove uma pessoa do dispositivo
        
        Args:
            person_id: ID único da pessoa
            
        Returns:
            (bool, str): Tupla contendo status da operação e mensagem
        """
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        # Prepara os dados da pessoa em formato JSON
        person_data = {
            "person_id": str(person_id)
        }
        
        # Converte para string JSON
        json_data = json.dumps(person_data)
        
        # Remove a pessoa
        ret, result = self.hid_api.manage_module_data(
            self.device_handle, 
            HID_ManageType.DEL_PERSON, 
            json_data
        )
        
        if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
            return False, f"Erro ao remover pessoa: {get_error_message(ret)}"
            
        return True, result if result else "Pessoa removida com sucesso"
        
    def get_all_persons(self):
        """Obtém lista de todas as pessoas registradas
        
        Returns:
            (bool, list/str): Tupla contendo status da operação e lista de pessoas/mensagem de erro
        """
        if not self.is_connected or not self.device_handle:
            return False, "Dispositivo não conectado"
            
        # Consulta todas as pessoas
        ret, result = self.hid_api.manage_module_data(
            self.device_handle,
            HID_ManageType.QUERY_ALL_PERSON,
            None
        )
        
        if ret != HID_ERRORCODE.ZKHID_ERROR_NONE:
            return False, f"Erro ao consultar pessoas: {get_error_message(ret)}"
            
        try:
            # Tenta converter o resultado para um dicionário/lista
            result_data = json.loads(result)
            return True, result_data
        except (json.JSONDecodeError, TypeError):
            return True, result if result else "Nenhuma pessoa encontrada" 