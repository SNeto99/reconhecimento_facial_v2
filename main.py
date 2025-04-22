# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Obtém o diretório raiz do projeto de forma absoluta
ROOT_DIR = Path(__file__).resolve().parent

# Adiciona o diretório raiz ao PYTHONPATH de forma absoluta
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Erro de importação: {e}")
    print(f"PYTHONPATH atual: {sys.path}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"ROOT_DIR: {ROOT_DIR}")
    sys.exit(1)

def setup_environment():
    """Configura o ambiente necessário para a aplicação"""
    # Adiciona o diretório do SDK ao PATH
    sdk_path = os.path.join(ROOT_DIR, 'sdk')
    if sdk_path not in sys.path:
        sys.path.append(sdk_path)
    
    # Verifica se as DLLs do SDK existem
    required_dlls = ['ZKCameraLib.dll', 'ZKHIDLib.dll']
    missing_dlls = []
    
    for dll in required_dlls:
        dll_path = os.path.join(sdk_path, dll)
        if not os.path.exists(dll_path):
            missing_dlls.append(dll)
    
    if missing_dlls:
        raise Exception(f"SDKs não encontrados: {', '.join(missing_dlls)}\nPasta esperada: {sdk_path}")

def main():
    try:
        setup_environment()
        from ui.connection_form import ConnectionForm
        app = ConnectionForm()
        app.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()