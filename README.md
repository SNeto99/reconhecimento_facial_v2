# Reconhecimento Facial com ZKTeco

Este projeto implementa uma interface Python para comunicação com dispositivos de reconhecimento facial da ZKTeco, utilizando as DLLs oficiais fornecidas pelo fabricante.

## Funcionalidades Implementadas

- Registro de faces
- Adição e remoção de usuários
- Consulta de usuários cadastrados
- Monitoramento de reconhecimento facial em tempo real

## Requisitos

- Windows (as DLLs são específicas para Windows)
- Python 3.6+
- Dispositivo de reconhecimento facial ZKTeco compatível

## Estrutura do Projeto

```
reconhecimento_facial_v2/
?
??? sdk/                      # Wrapper Python para as DLLs da ZKTeco
?   ??? __init__.py           # Facilita a importação dos módulos
?   ??? zk_hid_api.py         # Interface para ZKHIDLib.dll
?   ??? zk_camera_api.py      # Interface para ZKCameraLib.dll
?   ??? zk_face_registration.py # Funções de alto nível para registro facial
?
??? sdks_oficiais/            # SDKs oficiais da ZKTeco
?   ??? zkBio_SDK/            # SDK oficial utilizado como referência
?
??? main.py                   # Ponto de entrada principal da aplicação
??? demo_face_register.py     # Exemplo de uso do registro facial
??? README.md                 # Este arquivo
```

## Instalação

1. Coloque as DLLs oficiais da ZKTeco (`ZKHIDLib.dll` e `ZKCameraLib.dll`) no diretório `sdk/` 

2. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/reconhecimento_facial_v2.git
   cd reconhecimento_facial_v2
   ```

## Como Usar

### Exemplo de Registro de Face

Execute o script de demonstração:

```bash
python demo_face_register.py
```

Este script demonstra como:
- Conectar-se a um dispositivo ZKTeco
- Adicionar usuários
- Registrar faces
- Listar usuários cadastrados
- Excluir usuários
- Monitorar reconhecimentos em tempo real

### Integração com seu código

Para integrar a funcionalidade de registro facial em seu próprio código:

```python
from sdk.zk_face_registration import ZKFaceRegistration

# Inicializa o objeto de registro de face
face_reg = ZKFaceRegistration()

# Conecta ao dispositivo
if face_reg.connect():
    # Registra uma face
    success, result = face_reg.register_face(person_id="1001", name="João Silva")
    if success:
        print(f"Face registrada com sucesso!")
    else:
        print(f"Falha ao registrar face: {result}")

    # Desconecta do dispositivo
    face_reg.disconnect()
```

## Solução de Problemas

### DLL não encontrada

Se ocorrer o erro "DLL não encontrada", certifique-se de que:

1. As DLLs (`ZKHIDLib.dll` e `ZKCameraLib.dll`) estão no diretório `sdk/`
2. O diretório `sdk/` está no PATH do sistema ou no mesmo diretório onde o script está sendo executado

### Dispositivo não detectado

Se o dispositivo não for detectado:

1. Verifique se o dispositivo está conectado corretamente ao computador
2. Verifique se os drivers do dispositivo estão instalados
3. Tente reiniciar o dispositivo e o computador

## Desenvolvimento

Este projeto foi desenvolvido usando a biblioteca `ctypes` do Python para interagir com as DLLs nativas da ZKTeco. A estrutura do código foi projetada para fornecer uma interface Pythônica para as funcionalidades do SDK C#.

### Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias. 