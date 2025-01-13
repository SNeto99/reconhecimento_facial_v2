# -*- coding: utf-8 -*-

# Constantes do SDK ZKBio
class ManageType:
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

class ConfigType:
    COMMON_CONFIG = 1
    CAPTURE_FILTER_CONFIG = 2
    MOTION_DETECT_CONFIG = 3
    PALM_CONFIG = 4
    DEVICE_INFORMATION = 5
    DEVICE_TIME = 6

class SnapShotType:
    SNAPSHOT_NIR = 0
    SNAPSHOT_VL = 1

# Códigos de erro do SDK
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

# Constantes originais do protocolo de rede
USHRT_MAX = 65535

CMD_DB_RRQ          = 7     # Read in some kind of data from the machine
CMD_USER_WRQ        = 8     # Upload the user information (from PC to terminal).
CMD_USERTEMP_RRQ    = 9     # Read some fingerprint template or some kind of data entirely
CMD_USERTEMP_WRQ    = 10    # Upload some fingerprint template
CMD_OPTIONS_RRQ     = 11    # Read in the machine some configuration parameter
CMD_OPTIONS_WRQ     = 12    # Set machines configuration parameter
CMD_ATTLOG_RRQ      = 13    # Read all attendance record
CMD_CLEAR_DATA      = 14    # clear Data
CMD_CLEAR_ATTLOG    = 15    # Clear attendance records
CMD_DELETE_USER     = 18    # Delete some user
CMD_DELETE_USERTEMP = 19    # Delete some fingerprint template
CMD_CLEAR_ADMIN     = 20    # Cancel the manager
CMD_USERGRP_RRQ     = 21    # Read the user grouping
CMD_USERGRP_WRQ     = 22    # Set users grouping
CMD_USERTZ_RRQ      = 23    # Read the user Time Zone set
CMD_USERTZ_WRQ      = 24    # Write the user Time Zone set
CMD_GRPTZ_RRQ       = 25    # Read the group Time Zone set
CMD_GRPTZ_WRQ       = 26    # Write the group Time Zone set
CMD_TZ_RRQ          = 27    # Read Time Zone set
CMD_TZ_WRQ          = 28    # Write the Time Zone
CMD_ULG_RRQ         = 29    # Read unlocks combination
CMD_ULG_WRQ         = 30    # write unlocks combination
CMD_UNLOCK          = 31    # unlock
CMD_CLEAR_ACC       = 32    # Restores Access Control set to the default condition.
CMD_CLEAR_OPLOG     = 33    # Delete attendance machines all attendance record.
CMD_OPLOG_RRQ       = 34    # Read manages the record
CMD_GET_FREE_SIZES  = 50    # Obtain machines condition, like user recording number and so on
CMD_ENABLE_CLOCK    = 57    # Ensure the machine to be at the normal work condition
CMD_STARTVERIFY     = 60    # Ensure the machine to be at the authentication condition
CMD_STARTENROLL     = 61    # Start to enroll some user, ensure the machine to be at the registration user condition
CMD_CANCELCAPTURE   = 62    # Make the machine to be at the waiting order status, please refers to the CMD_STARTENROLL description.
CMD_STATE_RRQ       = 64    # Gain the machine the condition
CMD_WRITE_LCD       = 66    # Write LCD
CMD_CLEAR_LCD       = 67    # Clear the LCD captions (clear screen).
CMD_GET_PINWIDTH    = 69    # Obtain the length of user’s serial number
CMD_SMS_WRQ         = 70    # Upload the short message.
CMD_SMS_RRQ         = 71    # Download the short message
CMD_DELETE_SMS      = 72    # Delete the short message
CMD_UDATA_WRQ       = 73    # Set user’s short message
CMD_DELETE_UDATA    = 74    # Delete user’s short message
CMD_DOORSTATE_RRQ   = 75    # Obtain the door condition
CMD_WRITE_MIFARE    = 76    # Write the Mifare card
CMD_EMPTY_MIFARE    = 78    # Clear the Mifare card

CMD_GET_TIME        = 201   # Obtain the machine time
CMD_SET_TIME        = 202   # Set machines time
CMD_REG_EVENT       = 500   # Register the event

CMD_CONNECT         = 1000  # Connections requests
CMD_EXIT            = 1001  # Disconnection requests
CMD_ENABLEDEVICE    = 1002  # Ensure the machine to be at the normal work condition
CMD_DISABLEDEVICE   = 1003  # Make the machine to be at the shut-down condition, generally demonstrates ‘in the work ...’on LCD
CMD_RESTART         = 1004  # Restart the machine.
CMD_POWEROFF        = 1005  # Shut-down power source
CMD_SLEEP           = 1006  # Ensure the machine to be at the idle state.
CMD_RESUME          = 1007  # Awakens the sleep machine (temporarily not to support)
CMD_CAPTUREFINGER   = 1009  # Captures fingerprints picture
CMD_TEST_TEMP       = 1011  # Test some fingerprint exists or does not
CMD_CAPTUREIMAGE    = 1012  # Capture the entire image
CMD_REFRESHDATA     = 1013  # Refresh the machine interior data
CMD_REFRESHOPTION   = 1014  # Refresh the configuration parameter
CMD_TESTVOICE       = 1017  # Play voice
CMD_GET_VERSION     = 1100  # Obtain the firmware edition
CMD_CHANGE_SPEED    = 1101  # Change transmission speed
CMD_AUTH            = 1102  # Connections authorizations
CMD_PREPARE_DATA    = 1500  # Prepares to transmit the data
CMD_DATA            = 1501  # Transmit a data packet
CMD_FREE_DATA       = 1502  # Clear machines opened buffer

CMD_ACK_OK          = 2000  # Return value for order perform successfully
CMD_ACK_ERROR       = 2001  # Return value for order perform failed
CMD_ACK_DATA        = 2002  # Return data
CMD_ACK_RETRY       = 2003  # * Regstered event occorred */
CMD_ACK_REPEAT      = 2004  # Not available
CMD_ACK_UNAUTH      = 2005  # Connection unauthorized

CMD_ACK_UNKNOWN     = 0xffff# Unkown order
CMD_ACK_ERROR_CMD   = 0xfffd# Order false
CMD_ACK_ERROR_INIT  = 0xfffc#/* Not Initializated */
CMD_ACK_ERROR_DATA  = 0xfffb# Not available

EF_ATTLOG           = 1     # Be real-time to verify successfully
EF_FINGER           = (1<<1)# be real–time to press fingerprint (be real time to return data type sign)
EF_ENROLLUSER       = (1<<2)# Be real-time to enroll user
EF_ENROLLFINGER     = (1<<3)# be real-time to enroll fingerprint
EF_BUTTON           = (1<<4)# be real-time to press button
EF_UNLOCK           = (1<<5)# be real-time to unlock
EF_VERIFY           = (1<<7)# be real-time to verify fingerprint
EF_FPFTR            = (1<<8)# be real-time capture fingerprint minutia
EF_ALARM            = (1<<9)# Alarm signal

USER_DEFAULT        = 0
USER_ENROLLER       = 2
USER_MANAGER        = 6
USER_ADMIN          = 14

FCT_ATTLOG          = 1
FCT_WORKCODE        = 8
FCT_FINGERTMP       = 2
FCT_OPLOG           = 4
FCT_USER            = 5
FCT_SMS             = 6
FCT_UDATA           = 7

MACHINE_PREPARE_DATA_1 = 20560 # 0x5050
MACHINE_PREPARE_DATA_2 = 32130 # 0x7282

# Comandos para cadastro facial
CMD_STARTENROLL = 61    # Comando para iniciar registro
CMD_STARTVERIFY = 60    # Comando para iniciar verificação
CMD_CANCELCAPTURE = 62  # Comando para cancelar captura
CMD_STATE_RRQ = 64      # Comando para obter estado

# Estados do dispositivo
STATE_READY = 0
STATE_FACE_ENROLLING = 1
STATE_FACE_ENROLLED = 2
STATE_FACE_VERIFYING = 3

# Constantes para o SDK de reconhecimento facial
SDK_SUCCESS = 1
SDK_FAILED = 0

# Tipos de eventos
EVENT_NONE = 0
EVENT_ALARM = 1
EVENT_DOOR_BELL = 2
EVENT_DOOR_OPEN = 3
EVENT_DOOR_CLOSED = 4
EVENT_INVALID_VERIFICATION = 5
EVENT_ALARM_CANCEL = 6
EVENT_FACE_ENROLLED = 7
EVENT_FACE_VERIFY_SUCCESS = 8
EVENT_FACE_VERIFY_FAILED = 9

# Estados do dispositivo
DEVICE_STATUS_CONNECTED = 1
DEVICE_STATUS_DISCONNECTED = 0
DEVICE_STATUS_ENROLLING = 2
DEVICE_STATUS_VERIFYING = 3

# Parâmetros de captura facial
FACE_DETECT_MIN_SIZE = 100
FACE_DETECT_MAX_SIZE = 300
FACE_QUALITY_THRESHOLD = 70
FACE_LIVENESS_THRESHOLD = 80

# Modos de verificação
VERIFY_MODE_FACE = 1
VERIFY_MODE_CARD = 2
VERIFY_MODE_PASSWORD = 3
VERIFY_MODE_FACE_AND_CARD = 4
VERIFY_MODE_FACE_OR_CARD = 5

# Códigos de erro
ERROR_NONE = 0
ERROR_FAILED = -1
ERROR_INVALID_PARAM = -2
ERROR_NOT_CONNECTED = -3
ERROR_TIMEOUT = -4
ERROR_NO_FACE_DETECTED = -5
ERROR_FACE_TOO_FAR = -6
ERROR_FACE_TOO_CLOSE = -7
ERROR_FACE_TOO_HIGH = -8
ERROR_FACE_TOO_LOW = -9
ERROR_FACE_TOO_RIGHT = -10
ERROR_FACE_TOO_LEFT = -11
ERROR_FACE_NOT_FRONTAL = -12
ERROR_MULTIPLE_FACES = -13
ERROR_FACE_POOR_QUALITY = -14
ERROR_FACE_NOT_ALIVE = -15

# Comandos para operações faciais
CMD_FACE_INIT = 0x0500        # Inicializar módulo facial
CMD_PREPARE_FACE = 0x0501     # Preparar para captura facial
CMD_SET_FACE = 0x0502         # Iniciar captura facial
CMD_GET_FACE = 0x0503         # Verificar status do cadastro facial
CMD_FACE_CANCEL = 0x0504      # Cancelar operação facial

# Status de resposta
CMD_ACK_OK = 0x7D0            # Comando executado com sucesso
CMD_ACK_ERROR = 0x7D5         # Erro na execução do comando

# Estados do dispositivo
STATE_FACE_ENROLLING = 1
STATE_FACE_ENROLLED = 2
STATE_FACE_VERIFYING = 3
STATE_READY = 0

# Comandos adicionais
CMD_STATE_RRQ = 64    # Obter estado do dispositivo
CMD_STARTVERIFY = 60  # Iniciar verificação

# Comandos para registro facial
CMD_START_ENROLL = 0x0140    # Comando StartEnrollEx
CMD_GET_ENROLL_STATUS = 0x0141  # Verificar status do registro
CMD_CANCEL_CAPTURE = 0x0142     # Cancelar operação

# Status do registro
ENROLL_SUCCESS = 0x01      # Registro concluído com sucesso
ENROLL_PROCESSING = 0x02   # Registro em andamento
ENROLL_FAILED = 0x03       # Falha no registro

# Comandos básicos
CMD_CONNECT = 1000
CMD_EXIT = 1001
CMD_ENABLEDEVICE = 1002
CMD_DISABLEDEVICE = 1003
CMD_RESTART = 1004
CMD_POWEROFF = 1005
CMD_SLEEP = 1006
CMD_RESUME = 1007
CMD_TEST_TEMP = 1011
CMD_TESTVOICE = 1017
CMD_VERSION = 1100
CMD_CHANGE_SPEED = 1101

# Comandos de dados
CMD_PREPARE_DATA = 1500
CMD_DATA = 1501
CMD_FREE_DATA = 1502
CMD_DATA_WRRQ = 1503
CMD_DATA_RDY = 1504

# Comandos de usuário
CMD_USERTEMP_RRQ = 9
CMD_USERTEMP_WRQ = 10
CMD_OPTIONS_RRQ = 11
CMD_OPTIONS_WRQ = 12
CMD_ATTLOG_RRQ = 13
CMD_CLEAR_DATA = 14
CMD_CLEAR_ATTLOG = 15
CMD_DELETE_USER = 18
CMD_DELETE_USERTEMP = 19
CMD_CLEAR_ADMIN = 20
CMD_SET_USER = 8

# Comandos de face
CMD_FACE_FUNCTION = 11
CMD_REG_EVENT = 500
CMD_FACE_DETECT = 2202
CMD_UPLOAD_PHOTO = 2203

# Constantes de usuário
USER_DEFAULT = 0
USER_ADMIN = 14

# Constantes de face
FACE_FUN_ON = b'FaceFunOn'
FACE_FUN_OFF = b'FaceFunOff'






