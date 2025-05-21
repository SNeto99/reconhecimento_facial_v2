#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script espec�fico para registro facial no dispositivo ZKTeco.
Este script foca apenas no registro facial, garantindo uma nova conex�o com o dispositivo.
"""

import os
import sys
import time
from pathlib import Path

# Adiciona o diret�rio raiz ao path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importa a classe ZKConnection
try:
    from sdk.zk_connection import ZKConnection
except ImportError as e:
    print(f"Erro ao importar a classe ZKConnection: {e}")
    print(f"PATH atual: {sys.path}")
    sys.exit(1)

def main():
    print("==== Registro Facial ZKTeco ====")
    
    # Configura��es do dispositivo
    ip_address = "192.168.50.11"  # Endere�o IP do seu dispositivo
    port = 4370                   # Porta padr�o da ZKTeco
    timeout = 15                  # Timeout aumentado para 15 segundos
    password = 0                  # Senha do dispositivo (normalmente 0)
    
    # Inicializa a conex�o com novo objeto para garantir estado limpo
    print(f"\nEstabelecendo nova conex�o com {ip_address}:{port}...")
    zk = ZKConnection(ip_address=ip_address, port=port, timeout=timeout, password=password, verbose=True)
    
    try:
        # Conecta ao dispositivo
        for tentativa in range(3):
            print(f"Tentativa {tentativa+1} de conex�o...")
            if zk.connect():
                print("Conex�o estabelecida com sucesso!")
                break
            else:
                print("Falha na conex�o. Aguardando 3 segundos...")
                time.sleep(3)
                if tentativa == 2:  # �ltima tentativa
                    print("Todas as tentativas de conex�o falharam. Verifique a rede e o dispositivo.")
                    return
        
        # Breve confirma��o da conex�o
        print("\nObtendo informa��es do dispositivo...")
        device_info = zk.get_device_info()
        
        if device_info:
            print(f"Dispositivo conectado: {device_info.get('device_name', 'Desconhecido')}")
            print(f"Vers�o facial: {device_info.get('face_version', 'Desconhecida')}")
        
        # Solicita ID do usu�rio
        user_id = input("\nDigite o ID do usu�rio para o registro facial: ")
        
        # Verifica se o usu�rio existe
        print("\nVerificando se o usu�rio existe...")
        users = zk.get_users()
        user_exists = False
        user_name = ""
        
        if users:
            for user in users:
                if user['user_id'] == user_id:
                    user_exists = True
                    user_name = user['name']
                    break
        
        if not user_exists:
            print("\nUsu�rio n�o encontrado. Precisamos criar um novo usu�rio.")
            user_name = input("Digite o nome para o novo usu�rio: ")
            
            print(f"\nCriando usu�rio: {user_id} ({user_name})...")
            if not zk.set_user(user_id=user_id, name=user_name):
                print("Falha ao criar usu�rio. Opera��o cancelada.")
                return
            print("Usu�rio criado com sucesso!")
        else:
            print(f"\nUsu�rio encontrado: {user_id} ({user_name})")
        
        # Inicia o processo de registro facial
        print("\n" + "="*50)
        print("INICIANDO REGISTRO FACIAL")
        print("="*50)
        print("\nPrepare o usu�rio para ficar em frente � c�mera.")
        input("Pressione ENTER quando estiver pronto...")
        
        print("\nIniciando processo de registro facial...")
        if zk.manual_face_enroll(user_id=user_id):
            print("\nProcesso de registro facial iniciado com sucesso!")
            print("Por favor, verifique no dispositivo se a face foi registrada corretamente.")
            
            # Opcionalmente monitorar para verificar o registro
            if input("\nDeseja verificar o registro com verifica��o facial? (s/N): ").lower() == 's':
                print("\nIniciando verifica��o facial...")
                print("Pe�a ao usu�rio para olhar para a c�mera do dispositivo.")
                print("O dispositivo deve reconhecer a face automaticamente.")
                print("Monitorando eventos por 30 segundos... (Pressione Ctrl+C para cancelar)")
                
                try:
                    def event_callback(event):
                        if hasattr(event, 'user_id') and event.user_id == user_id:
                            print(f"\n? SUCESSO! Usu�rio {user_id} reconhecido!")
                        else:
                            print(f"Evento detectado: {event}")
                            
                    zk.live_capture(callback=event_callback, timeout=30)
                except KeyboardInterrupt:
                    print("\nMonitoramento interrompido pelo usu�rio.")
        else:
            print("\nFalha no processo de registro facial.")
            print("Sugest�es:")
            print("1. Verifique se o dispositivo est� funcionando corretamente")
            print("2. Verifique se a ilumina��o � adequada")
            print("3. Tente reiniciar o dispositivo f�sico")
            print("4. Verifique a conex�o de rede")
    
    finally:
        # Garante a desconex�o mesmo em caso de erro
        print("\nDesconectando do dispositivo...")
        zk.disconnect()
        print("Processo conclu�do.")

if __name__ == "__main__":
    main() 