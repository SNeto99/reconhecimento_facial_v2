#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemplo de uso da classe ZKConnection para comunicação com dispositivos ZKTeco via IP.
"""

import os
import sys
import json
import time
from pathlib import Path

# Adiciona o diretório raiz ao path
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
    print("==== Demonstração de Conexão ZKTeco via IP ====")
    
    # Configurações do dispositivo
    ip_address = "192.168.50.11"  # Endereço IP do seu dispositivo
    port = 4370                   # Porta padrão da ZKTeco
    timeout = 10                  # Timeout em segundos
    password = 0                  # Senha do dispositivo (normalmente 0)
    
    # Inicializa a conexão
    zk = ZKConnection(ip_address=ip_address, port=port, timeout=timeout, password=password, verbose=True)
    
    try:
        # Conecta ao dispositivo
        if not zk.connect():
            print("Falha ao conectar ao dispositivo. Verifique o endereço IP e a conexão de rede.")
            return
        
        print("\n=== Informações do Dispositivo ===")
        device_info = zk.get_device_info()
        
        if device_info:
            for key, value in device_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Menu de opções
        while True:
            print("\n==== Menu ====")
            print("1. Listar usuários")
            print("2. Adicionar usuário")
            print("3. Remover usuário")
            print("4. Monitorar reconhecimento (live capture)")
            print("5. Ver registros de presença")
            print("6. Reiniciar dispositivo")
            print("7. Cadastrar face de usuário")
            print("8. Diagnóstico de comandos faciais")
            print("9. Registro Facial Automático (Método Recomendado)")
            print("0. Sair")
            
            opcao = input("\nEscolha uma opção: ")
            
            if opcao == "1":
                # Listar usuários
                print("\n=== Usuários Cadastrados ===")
                users = zk.get_users()
                
                if users:
                    if len(users) == 0:
                        print("Não há usuários cadastrados.")
                    else:
                        for user in users:
                            print(f"ID: {user['user_id']}, Nome: {user['name']}, Privilégio: {user['privilege']}")
                else:
                    print("Falha ao obter lista de usuários.")
                    
            elif opcao == "2":
                # Adicionar usuário
                user_id = input("Digite o ID do usuário: ")
                name = input("Digite o nome do usuário: ")
                privilege = int(input("Digite o privilégio (0=Normal, 14=Admin): ") or "0")
                password = input("Digite a senha (ou deixe em branco): ")
                
                print("\nAdicionando usuário...")
                if zk.set_user(user_id=user_id, name=name, privilege=privilege, password=password):
                    print("Usuário adicionado com sucesso!")
                else:
                    print("Falha ao adicionar usuário.")
                    
            elif opcao == "3":
                # Remover usuário
                user_id = input("Digite o ID do usuário a ser removido: ")
                
                print("\nRemovendo usuário...")
                if zk.delete_user(user_id=user_id):
                    print("Usuário removido com sucesso!")
                else:
                    print("Falha ao remover usuário.")
                    
            elif opcao == "4":
                # Monitorar reconhecimento
                print("\nIniciando monitoramento de eventos...")
                print("Pressione Ctrl+C para cancelar.")
                
                try:
                    def event_callback(event):
                        print(f"Evento detectado: {event}")
                        
                    zk.live_capture(callback=event_callback, timeout=30)
                except KeyboardInterrupt:
                    print("\nMonitoramento interrompido.")
                    
            elif opcao == "5":
                # Ver registros de presença
                print("\n=== Registros de Presença ===")
                attendances = zk.get_attendance()
                
                if attendances:
                    if len(attendances) == 0:
                        print("Não há registros de presença.")
                    else:
                        for attendance in attendances:
                            print(f"ID: {attendance['user_id']}, Data/Hora: {attendance['timestamp']}, Status: {attendance['status']}")
                else:
                    print("Falha ao obter registros de presença.")
                    
            elif opcao == "6":
                # Reiniciar dispositivo
                if input("Tem certeza que deseja reiniciar o dispositivo? (s/N): ").lower() == 's':
                    print("\nReiniciando dispositivo...")
                    if zk.restart_device():
                        print("Dispositivo reiniciado com sucesso!")
                        print("Reconectando em 15 segundos...")
                        time.sleep(15)
                        zk.connect()
                    else:
                        print("Falha ao reiniciar dispositivo.")
                        
            elif opcao == "7":
                # Cadastrar face de usuário
                user_id = input("Digite o ID do usuário para cadastro facial: ")
                
                # Verificar se o usuário existe
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
                    print("Usuário não encontrado. É preciso criar o usuário primeiro.")
                    name = input("Digite o nome para o novo usuário: ")
                    if not zk.set_user(user_id=user_id, name=name):
                        print("Falha ao criar o usuário. Operação cancelada.")
                        continue
                    user_name = name
                
                print(f"\nIniciando o cadastro facial para o usuário: {user_id} ({user_name})")
                print("Posicione o rosto do usuário na frente do dispositivo.")
                print("O processo pode levar alguns segundos.")
                
                # Usa o novo método específico para registro facial
                if zk.enroll_face(user_id=user_id, name=user_name):
                    print("\nProcesso de cadastro facial iniciado com sucesso!")
                    print("Siga as instruções no dispositivo para completar o cadastro.")
                    
                    # Pergunta se o usuário deseja monitorar o processo
                    if input("\nDeseja monitorar eventos do dispositivo durante o cadastro? (s/N): ").lower() == 's':
                        print("\nMonitorando eventos... (Pressione Ctrl+C para cancelar)")
                        try:
                            def event_callback(event):
                                print(f"Evento detectado: {event}")
                                
                            zk.live_capture(callback=event_callback, timeout=60)
                        except KeyboardInterrupt:
                            print("\nMonitoramento interrompido pelo usuário.")
                else:
                    print("\nFalha ao iniciar o cadastro facial.")
                    
            elif opcao == "8":
                # Diagnóstico de comandos faciais
                print("\n=== Diagnóstico de Comandos Faciais ===")
                user_id = input("Digite o ID do usuário para o diagnóstico facial: ")
                
                # Verifica se o usuário existe
                users = zk.get_users()
                user_exists = False
                
                if users:
                    for user in users:
                        if user['user_id'] == user_id:
                            user_exists = True
                            break
                
                if not user_exists:
                    print("ATENÇÃO: Usuário não encontrado. O diagnóstico pode falhar.")
                    if input("Deseja continuar mesmo assim? (s/N): ").lower() != 's':
                        continue
                
                print("\nIniciando diagnóstico com diversos comandos...")
                print("Observe o comportamento do dispositivo durante o teste e anote qual comando ativou o registro facial.")
                
                results = zk.test_face_commands(user_id)
                
                print("\nDiagnóstico concluído.")
                print("Para cada comando que gerou uma resposta do dispositivo, anote o comportamento.")
                print("Isso ajudará a identificar o comando correto para o registro facial.")
                    
            elif opcao == "9":
                # Registro facial automático (método recomendado)
                print("\n=== Registro Facial Automático (Método Recomendado) ===")
                user_id = input("Digite o ID do usuário para o registro facial: ")
                
                # Verifica se o usuário existe
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
                    print("ATENÇÃO: Usuário não encontrado. Criando usuário...")
                    user_name = input("Digite o nome para o novo usuário: ")
                    if not zk.set_user(user_id=user_id, name=user_name):
                        print("Falha ao criar usuário. Operação cancelada.")
                        continue
                
                print("\nIniciando registro facial manual usando a sequência correta de comandos...")
                print("Posicione o rosto do usuário na frente do dispositivo.")
                print("O processo pode levar alguns segundos.")
                
                # Usa o método específico para registro facial manual com a sequência correta
                if zk.manual_face_enroll(user_id=user_id):
                    print("\nProcesso de registro facial manual iniciado com sucesso!")
                    print("Siga as instruções no dispositivo para completar o registro.")
                    
                    # Pergunta se o usuário deseja monitorar o processo
                    if input("\nDeseja monitorar eventos do dispositivo durante o registro? (s/N): ").lower() == 's':
                        print("\nMonitorando eventos... (Pressione Ctrl+C para cancelar)")
                        try:
                            def event_callback(event):
                                print(f"Evento detectado: {event}")
                                
                            zk.live_capture(callback=event_callback, timeout=60)
                        except KeyboardInterrupt:
                            print("\nMonitoramento interrompido pelo usuário.")
                else:
                    print("\nFalha ao iniciar o registro facial manual.")
                    
            elif opcao == "0":
                # Sair
                break
                
            else:
                print("Opção inválida!")
    
    finally:
        # Garante a desconexão mesmo em caso de erro
        print("\nDesconectando do dispositivo...")
        zk.disconnect()
        print("Desconectado.")

if __name__ == "__main__":
    main() 