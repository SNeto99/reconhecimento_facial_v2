import ctypes
from ctypes import c_int, c_int32, c_uint64, c_void_p, POINTER, byref, Structure, CFUNCTYPE

# Definição das estruturas
class UVCVedioData(Structure):
    _fields_ = [
        ("frame_index", c_int32),
        ("ori_length", c_int32),
        ("data_length", c_int32),
        ("data", c_void_p)
    ]

class UVCCustomData(Structure):
    _fields_ = [
        ("frame_index", c_uint64),
        ("width", c_int32),
        ("height", c_int32),
        ("customData", c_void_p)
    ]

# Definição dos callbacks
VIDEO_DATA_CALLBACK = CFUNCTYPE(None, c_void_p, UVCVedioData)
CUSTOM_DATA_CALLBACK = CFUNCTYPE(None, c_void_p, UVCCustomData)

class ZKBioModuleCameraApi:
    def __init__(self, dll_path=None):
        """Inicializa a API carregando a DLL"""
        # Definindo initialized como False logo no início
        self.initialized = False
        self.zkcamera_lib = None
        
        try:
            if dll_path:
                print(f"Tentando carregar DLL do caminho: {dll_path}")
                self.zkcamera_lib = ctypes.WinDLL(dll_path)
            else:
                print(f"Tentando carregar DLL do caminho padrão")
                self.zkcamera_lib = ctypes.WinDLL("ZKCameraLib.dll")
                
            # Configuração dos protótipos das funções
            self._setup_function_prototypes()
            self.initialized = True
            print(f"DLL da câmera carregada com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar a biblioteca ZKCameraLib.dll: {e}")
    
    def _setup_function_prototypes(self):
        """Configura os protótipos das funções da DLL"""
        if not self.zkcamera_lib:
            return
            
        # ZKCamera_Init
        self.zkcamera_lib.ZKCamera_Init.argtypes = []
        self.zkcamera_lib.ZKCamera_Init.restype = c_int
        
        # ZKCamera_Terminate
        self.zkcamera_lib.ZKCamera_Terminate.argtypes = []
        self.zkcamera_lib.ZKCamera_Terminate.restype = c_int
        
        # ZKCamera_GetDeviceCount
        self.zkcamera_lib.ZKCamera_GetDeviceCount.argtypes = []
        self.zkcamera_lib.ZKCamera_GetDeviceCount.restype = c_int
        
        # ZKCamera_GetDeviceType
        self.zkcamera_lib.ZKCamera_GetDeviceType.argtypes = [c_int]
        self.zkcamera_lib.ZKCamera_GetDeviceType.restype = c_int
        
        # ZKCamera_OpenDevice
        self.zkcamera_lib.ZKCamera_OpenDevice.argtypes = [c_int, c_int, c_int, c_int, POINTER(c_void_p)]
        self.zkcamera_lib.ZKCamera_OpenDevice.restype = c_int
        
        # ZKCamera_CloseDevice
        self.zkcamera_lib.ZKCamera_CloseDevice.argtypes = [c_void_p]
        self.zkcamera_lib.ZKCamera_CloseDevice.restype = c_int
        
        # ZKCamera_GetCapWidth
        self.zkcamera_lib.ZKCamera_GetCapWidth.argtypes = [c_void_p]
        self.zkcamera_lib.ZKCamera_GetCapWidth.restype = c_int
        
        # ZKCamera_GetCapHeight
        self.zkcamera_lib.ZKCamera_GetCapHeight.argtypes = [c_void_p]
        self.zkcamera_lib.ZKCamera_GetCapHeight.restype = c_int
        
        # ZKCamera_FreePointer
        self.zkcamera_lib.ZKCamera_FreePointer.argtypes = [c_void_p]
        self.zkcamera_lib.ZKCamera_FreePointer.restype = c_int
        
        # ZKCamera_SetDataCallback
        self.zkcamera_lib.ZKCamera_SetDataCallback.argtypes = [
            c_void_p,  # handle
            VIDEO_DATA_CALLBACK,  # videoDataCallback
            CUSTOM_DATA_CALLBACK,  # customDataCallback
            c_void_p   # userParam
        ]
        self.zkcamera_lib.ZKCamera_SetDataCallback.restype = c_int
    
    def init(self):
        """Inicializa a biblioteca de câmera"""
        if not self.initialized:
            return -1
        return self.zkcamera_lib.ZKCamera_Init()
    
    def terminate(self):
        """Finaliza a biblioteca de câmera"""
        if not self.initialized:
            return -1
        return self.zkcamera_lib.ZKCamera_Terminate()
    
    def get_device_count(self):
        """Obtém o número de dispositivos de câmera conectados"""
        if not self.initialized:
            return 0
        return self.zkcamera_lib.ZKCamera_GetDeviceCount()
    
    def get_device_type(self, index):
        """Obtém o tipo do dispositivo de câmera"""
        if not self.initialized:
            return -1
        return self.zkcamera_lib.ZKCamera_GetDeviceType(c_int(index))
    
    def open_device(self, index, width, height, fps):
        """Abre um dispositivo de câmera pelo índice"""
        if not self.initialized:
            return -1, None
            
        handle = c_void_p()
        ret = self.zkcamera_lib.ZKCamera_OpenDevice(
            c_int(index), c_int(width), c_int(height), c_int(fps), byref(handle)
        )
        if ret == 0:
            return ret, handle
        return ret, None
    
    def close_device(self, handle):
        """Fecha um dispositivo de câmera aberto"""
        if not self.initialized or not handle:
            return -1
            
        return self.zkcamera_lib.ZKCamera_CloseDevice(handle)
    
    def get_cap_width(self, handle):
        """Obtém a largura da captura"""
        if not self.initialized or not handle:
            return -1
            
        return self.zkcamera_lib.ZKCamera_GetCapWidth(handle)
    
    def get_cap_height(self, handle):
        """Obtém a altura da captura"""
        if not self.initialized or not handle:
            return -1
            
        return self.zkcamera_lib.ZKCamera_GetCapHeight(handle)
    
    def free_pointer(self, ptr):
        """Libera um ponteiro alocado pela biblioteca"""
        if not self.initialized or not ptr:
            return -1
            
        return self.zkcamera_lib.ZKCamera_FreePointer(ptr)
    
    def set_data_callback(self, handle, video_callback, custom_callback, user_param=None):
        """Define os callbacks para receber dados de vídeo e dados personalizados"""
        if not self.initialized or not handle:
            return -1
            
        # Não passamos None diretamente para a função C
        video_cb = video_callback if video_callback else VIDEO_DATA_CALLBACK(lambda *args: None)
        custom_cb = custom_callback if custom_callback else CUSTOM_DATA_CALLBACK(lambda *args: None)
        user_p = user_param if user_param else c_void_p()
        
        return self.zkcamera_lib.ZKCamera_SetDataCallback(handle, video_cb, custom_cb, user_p)

# Classe auxiliar para processar callbacks e converter para Python
class ZKCameraCallbackHelper:
    @staticmethod
    def video_data_to_bytes(video_data):
        """Converte os dados de vídeo para bytes Python"""
        if not video_data.data or video_data.data_length <= 0:
            return None
            
        # Cria um buffer Python a partir do ponteiro C
        buffer = ctypes.create_string_buffer(video_data.data_length)
        ctypes.memmove(buffer, video_data.data, video_data.data_length)
        
        # Retorna os bytes Python
        return bytes(buffer)
    
    @staticmethod
    def custom_data_to_bytes(custom_data):
        """Converte os dados personalizados para bytes Python"""
        if not custom_data.customData:
            return None
            
        # Precisamos saber o tamanho dos dados, que não está explícito na estrutura
        # Aqui assumimos um tamanho, mas isso pode precisar ser ajustado
        estimated_size = custom_data.width * custom_data.height * 4  # Estimativa para RGBA
        
        # Cria um buffer Python a partir do ponteiro C
        buffer = ctypes.create_string_buffer(estimated_size)
        ctypes.memmove(buffer, custom_data.customData, estimated_size)
        
        # Retorna os bytes Python
        return bytes(buffer) 