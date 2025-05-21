import ctypes
from ctypes import c_int, c_char_p, c_byte, POINTER, byref, pointer, Structure, CFUNCTYPE, c_void_p

# Definição do callback para envio de arquivos
SEND_FILE_CALLBACK = CFUNCTYPE(None, c_void_p, c_int)

# Enumerações
class HID_ERRORCODE:
    ZKHID_ERROR_NONE = 0
    ZKHID_ERROR_OPEN = -1
    ZKHID_ERROR_NOTOPEN = -2
    ZKHID_ERROR_PARAMETER = -3
    ZKHID_ERROR_MEMORY = -4
    ZKHID_ERROR_NO_MEMORY = -5
    ZKHID_ERROR_SEND_CMD = -6
    ZKHID_ERROR_READ_TIMEOUT = -7
    ZKHID_ERROR_SET_CONFIG = -8
    ZKHID_ERROR_IO = -9
    ZKHID_ERROR_INVALID_FILE = -10
    ZKHID_ERROR_INVALID_HEADER = -11
    ZKHID_ERROR_CHECKSUM = -12
    ZKHID_ERROR_LOSS_PACKET = -13

class HID_ConfigType:
    COMMON_CONFIG = 1
    CAPTURE_FILTER_CONFIG = 2
    MOTION_DETECT_CONFIG = 3
    PALM_CONFIG = 4
    DEVICE_INFORMATION = 5
    DEVICE_TIME = 6

class HID_ManageType:
    ADD_PERSON = 1
    DEL_PERSON = 2
    CLEAR_PERSON = 3
    GET_PERSON = 4
    QUERY_ALL_PERSON = 5
    QUERY_STATISTICS = 6
    ADD_FACE = 7
    ADD_FACE_REG = 8
    DETECT_FACE_REG = 9
    REG_START = 10
    REG_END = 11
    DETECT_PALM_REG = 12
    ADD_PALM = 13
    ADD_PALM_REG = 14
    MERGE_PALM_REG = 15
    DEL_FACE_CACHEID = 16
    DEL_PALM_CACHEID = 17
    ATT_RECORD_COUNT = 18
    EXPORT_ATT_RECORD = 19
    CLEAR_ATT_RECORD = 20

class ZKBioModuleHIDApi:
    def __init__(self, dll_path=None):
        """Inicializa a API carregando a DLL"""
        # Definindo initialized como False logo no início
        self.initialized = False
        self.zkhid_lib = None
        
        try:
            if dll_path:
                print(f"Tentando carregar DLL do caminho: {dll_path}")
                self.zkhid_lib = ctypes.WinDLL(dll_path)
            else:
                print(f"Tentando carregar DLL do caminho padrão")
                self.zkhid_lib = ctypes.WinDLL("ZKHIDLib.dll")
                
            # Configuração dos protótipos das funções
            self._setup_function_prototypes()
            self.initialized = True
            print(f"DLL carregada com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar a biblioteca ZKHIDLib.dll: {e}")
    
    def _setup_function_prototypes(self):
        """Configura os protótipos das funções da DLL"""
        if not self.zkhid_lib:
            return
            
        # ZKHID_Init
        self.zkhid_lib.ZKHID_Init.argtypes = []
        self.zkhid_lib.ZKHID_Init.restype = c_int
        
        # ZKHID_Terminate
        self.zkhid_lib.ZKHID_Terminate.argtypes = []
        self.zkhid_lib.ZKHID_Terminate.restype = c_int
        
        # ZKHID_GetCount
        self.zkhid_lib.ZKHID_GetCount.argtypes = [POINTER(c_int)]
        self.zkhid_lib.ZKHID_GetCount.restype = c_int
        
        # ZKHID_Open
        self.zkhid_lib.ZKHID_Open.argtypes = [c_int, POINTER(c_void_p)]
        self.zkhid_lib.ZKHID_Open.restype = c_int
        
        # ZKHID_Close
        self.zkhid_lib.ZKHID_Close.argtypes = [c_void_p]
        self.zkhid_lib.ZKHID_Close.restype = c_int
        
        # ZKHID_GetConfig
        self.zkhid_lib.ZKHID_GetConfig.argtypes = [c_void_p, c_int, POINTER(c_byte), POINTER(c_int)]
        self.zkhid_lib.ZKHID_GetConfig.restype = c_int
        
        # ZKHID_SetConfig
        self.zkhid_lib.ZKHID_SetConfig.argtypes = [c_void_p, c_int, c_char_p]
        self.zkhid_lib.ZKHID_SetConfig.restype = c_int
        
        # ZKHID_RegisterFace
        self.zkhid_lib.ZKHID_RegisterFace.argtypes = [c_void_p, c_char_p, POINTER(c_byte), POINTER(c_int)]
        self.zkhid_lib.ZKHID_RegisterFace.restype = c_int
        
        # ZKHID_RegisterPalm
        self.zkhid_lib.ZKHID_RegisterPalm.argtypes = [c_void_p, c_char_p, POINTER(c_byte), POINTER(c_int)]
        self.zkhid_lib.ZKHID_RegisterPalm.restype = c_int
        
        # ZKHID_PollMatchResult
        self.zkhid_lib.ZKHID_PollMatchResult.argtypes = [c_void_p, POINTER(c_byte), POINTER(c_int)]
        self.zkhid_lib.ZKHID_PollMatchResult.restype = c_int
        
        # ZKHID_ManageModuleData
        self.zkhid_lib.ZKHID_ManageModuleData.argtypes = [c_void_p, c_int, c_char_p, POINTER(c_byte), POINTER(c_int)]
        self.zkhid_lib.ZKHID_ManageModuleData.restype = c_int
    
    def init(self):
        """Inicializa a biblioteca HID"""
        if not self.initialized:
            return HID_ERRORCODE.ZKHID_ERROR_OPEN
        return self.zkhid_lib.ZKHID_Init()
    
    def terminate(self):
        """Finaliza a biblioteca HID"""
        if not self.initialized:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN
        return self.zkhid_lib.ZKHID_Terminate()
    
    def get_device_count(self):
        """Obtém o número de dispositivos conectados"""
        if not self.initialized:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, 0
            
        count = c_int(0)
        ret = self.zkhid_lib.ZKHID_GetCount(byref(count))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE:
            return ret, count.value
        return ret, 0
    
    def open_device(self, index):
        """Abre um dispositivo pelo índice"""
        if not self.initialized:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, None
            
        handle = c_void_p()
        ret = self.zkhid_lib.ZKHID_Open(c_int(index), byref(handle))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE:
            return ret, handle
        return ret, None
    
    def close_device(self, handle):
        """Fecha um dispositivo aberto"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN
            
        return self.zkhid_lib.ZKHID_Close(handle)
    
    def get_config(self, handle, config_type):
        """Obtém configuração do dispositivo"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, None
            
        buffer_size = 2 * 1024  # 2KB de buffer
        buffer = (c_byte * buffer_size)()
        length = c_int(buffer_size)
        
        ret = self.zkhid_lib.ZKHID_GetConfig(handle, c_int(config_type), buffer, byref(length))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE:
            # Convertendo buffer para string
            config_data = bytes(buffer[:length.value]).decode('utf-8')
            return ret, config_data
        return ret, None
    
    def set_config(self, handle, config_type, json_data):
        """Define configuração do dispositivo"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN
            
        # Convertendo string para bytes
        json_bytes = json_data.encode('utf-8')
        
        return self.zkhid_lib.ZKHID_SetConfig(handle, c_int(config_type), c_char_p(json_bytes))
    
    def register_face(self, handle, json_data):
        """Registra uma face no dispositivo"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, None
            
        # Alocando buffer para receber os dados da face
        buffer_size = 20 * 1024  # 20KB de buffer
        buffer = (c_byte * buffer_size)()
        length = c_int(buffer_size)
        
        # Convertendo string para bytes
        json_bytes = json_data.encode('utf-8')
        
        ret = self.zkhid_lib.ZKHID_RegisterFace(handle, c_char_p(json_bytes), buffer, byref(length))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE:
            # Convertendo buffer para string
            face_data = bytes(buffer[:length.value]).decode('utf-8')
            return ret, face_data
        return ret, None
    
    def poll_match_result(self, handle):
        """Verifica resultados de reconhecimento"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, None
            
        buffer_size = 40 * 1024  # 40KB de buffer
        buffer = (c_byte * buffer_size)()
        length = c_int(buffer_size)
        
        ret = self.zkhid_lib.ZKHID_PollMatchResult(handle, buffer, byref(length))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE:
            # Convertendo buffer para string
            result_data = bytes(buffer[:length.value]).decode('utf-8')
            return ret, result_data
        return ret, None
    
    def manage_module_data(self, handle, manage_type, json_data):
        """Gerencia dados do módulo"""
        if not self.initialized or not handle:
            return HID_ERRORCODE.ZKHID_ERROR_NOTOPEN, None
            
        buffer_size = 40 * 1024  # 40KB de buffer
        buffer = (c_byte * buffer_size)()
        length = c_int(buffer_size)
        
        # Convertendo string para bytes
        json_bytes = json_data.encode('utf-8') if json_data else None
        json_char_p = c_char_p(json_bytes) if json_bytes else None
        
        ret = self.zkhid_lib.ZKHID_ManageModuleData(handle, c_int(manage_type), json_char_p, buffer, byref(length))
        if ret == HID_ERRORCODE.ZKHID_ERROR_NONE and length.value > 0:
            # Convertendo buffer para string
            result_data = bytes(buffer[:length.value]).decode('utf-8')
            return ret, result_data
        return ret, None

# Função de conveniência para obter os códigos de erro em formato de texto
def get_error_message(error_code):
    error_messages = {
        HID_ERRORCODE.ZKHID_ERROR_NONE: "Operação bem-sucedida",
        HID_ERRORCODE.ZKHID_ERROR_OPEN: "Erro ao abrir o dispositivo",
        HID_ERRORCODE.ZKHID_ERROR_NOTOPEN: "Dispositivo não aberto",
        HID_ERRORCODE.ZKHID_ERROR_PARAMETER: "Parâmetro inválido",
        HID_ERRORCODE.ZKHID_ERROR_MEMORY: "Erro de memória",
        HID_ERRORCODE.ZKHID_ERROR_NO_MEMORY: "Memória insuficiente",
        HID_ERRORCODE.ZKHID_ERROR_SEND_CMD: "Erro ao enviar comando",
        HID_ERRORCODE.ZKHID_ERROR_READ_TIMEOUT: "Timeout de leitura",
        HID_ERRORCODE.ZKHID_ERROR_SET_CONFIG: "Erro ao definir configuração",
        HID_ERRORCODE.ZKHID_ERROR_IO: "Erro de I/O",
        HID_ERRORCODE.ZKHID_ERROR_INVALID_FILE: "Arquivo inválido",
        HID_ERRORCODE.ZKHID_ERROR_INVALID_HEADER: "Cabeçalho inválido",
        HID_ERRORCODE.ZKHID_ERROR_CHECKSUM: "Erro de checksum",
        HID_ERRORCODE.ZKHID_ERROR_LOSS_PACKET: "Pacote perdido",
    }
    return error_messages.get(error_code, f"Erro desconhecido: {error_code}") 