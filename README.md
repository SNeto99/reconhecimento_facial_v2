# Reconhecimento Facial com ZKTeco

Este projeto implementa uma interface Python para comunica��o com dispositivos de reconhecimento facial da ZKTeco, utilizando as DLLs oficiais fornecidas pelo fabricante.

## Funcionalidades Implementadas

- Registro de faces
- Adi��o e remo��o de usu�rios
- Consulta de usu�rios cadastrados
- Monitoramento de reconhecimento facial em tempo real

## Requisitos

- Windows (as DLLs s�o espec�ficas para Windows)
- Python 3.6+
- Dispositivo de reconhecimento facial ZKTeco compat�vel

## Estrutura do Projeto

```
reconhecimento_facial_v2/
?
??? sdk/                      # Wrapper Python para as DLLs da ZKTeco
?   ??? __init__.py           # Facilita a importa��o dos m�dulos
?   ??? zk_hid_api.py         # Interface para ZKHIDLib.dll
?   ??? zk_camera_api.py      # Interface para ZKCameraLib.dll
?   ??? zk_face_registration.py # Fun��es de alto n�vel para registro facial
?
??? sdks_oficiais/            # SDKs oficiais da ZKTeco
?   ??? zkBio_SDK/            # SDK oficial utilizado como refer�ncia
?
??? main.py                   # Ponto de entrada principal da aplica��o
??? demo_face_register.py     # Exemplo de uso do registro facial
??? README.md                 # Este arquivo
```

## Instala��o

1. Coloque as DLLs oficiais da ZKTeco (`ZKHIDLib.dll` e `ZKCameraLib.dll`) no diret�rio `sdk/` 

2. Clone o reposit�rio:
   ```
   git clone https://github.com/seu-usuario/reconhecimento_facial_v2.git
   cd reconhecimento_facial_v2
   ```

## Como Usar

### Exemplo de Registro de Face

Execute o script de demonstra��o:

```bash
python demo_face_register.py
```

Este script demonstra como:
- Conectar-se a um dispositivo ZKTeco
- Adicionar usu�rios
- Registrar faces
- Listar usu�rios cadastrados
- Excluir usu�rios
- Monitorar reconhecimentos em tempo real

### Integra��o com seu c�digo

Para integrar a funcionalidade de registro facial em seu pr�prio c�digo:

```python
from sdk.zk_face_registration import ZKFaceRegistration

# Inicializa o objeto de registro de face
face_reg = ZKFaceRegistration()

# Conecta ao dispositivo
if face_reg.connect():
    # Registra uma face
    success, result = face_reg.register_face(person_id="1001", name="Jo�o Silva")
    if success:
        print(f"Face registrada com sucesso!")
    else:
        print(f"Falha ao registrar face: {result}")

    # Desconecta do dispositivo
    face_reg.disconnect()
```

## Solu��o de Problemas

### DLL n�o encontrada

Se ocorrer o erro "DLL n�o encontrada", certifique-se de que:

1. As DLLs (`ZKHIDLib.dll` e `ZKCameraLib.dll`) est�o no diret�rio `sdk/`
2. O diret�rio `sdk/` est� no PATH do sistema ou no mesmo diret�rio onde o script est� sendo executado

### Dispositivo n�o detectado

Se o dispositivo n�o for detectado:

1. Verifique se o dispositivo est� conectado corretamente ao computador
2. Verifique se os drivers do dispositivo est�o instalados
3. Tente reiniciar o dispositivo e o computador

## Desenvolvimento

Este projeto foi desenvolvido usando a biblioteca `ctypes` do Python para interagir com as DLLs nativas da ZKTeco. A estrutura do c�digo foi projetada para fornecer uma interface Pyth�nica para as funcionalidades do SDK C#.

### Contribui��es

Contribui��es s�o bem-vindas! Sinta-se � vontade para abrir issues ou enviar pull requests com melhorias. 