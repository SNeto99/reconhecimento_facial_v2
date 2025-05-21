#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemplo de uso do SDK de reconhecimento facial ZKTeco para registro de faces.
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

# Importa a classe de registro facial
try:
    from sdk.zk_face_registration import ZKFaceRegistration
except ImportError as e:
    print(f"Erro ao importar o módulo ZKFaceRegistration: {e}")
    print(f"PATH atual: {sys.path}")
    sys.exit(1)

def main():
    print("==== Demonstração de Registro de Face ZKTeco ====")
    
    # Caminho para as DLLs
    sdk_dir = os.path.join(ROOT_DIR, 'sdk')
    hid_dll_path = os.path.join(sdk_dir, 'ZKHIDLib.dll')
    
    # Verifica se as DLLs existem
    if not os.path.exists(hid_dll_path):
        print(f"ERRO: A DLL não foi encontrada em {hid_dll_path}")
        print("Por favor, coloque as DLLs ZKHIDLib.dll e ZKCameraLib.dll no diretório sdk/")
        return
    else:
        print(f"DLL encontrada em: {hid_dll_path}")
    
    # Inicializa o objeto de registro de face com o caminho explícito para a DLL
    face_reg = ZKFaceRegistration(hid_dll_path)
    
    # Configuração do dispositivo
    use_network = True  # Altere para False se quiser usar conexão USB
    ip_address = "192.168.50.11"  # Endereço IP do seu dispositivo
    port = 4370  # Porta do dispositivo (normalmente 8000)
    
    try:
        # Conecta ao dispositivo
        print("\nConectando ao dispositivo...")
        
        if use_network:
            print(f"Usando conexão de rede: {ip_address}:{port}")
            if not face_reg.connect(ip_address=ip_address, port=port):
                print("Falha ao conectar ao dispositivo. Verifique se o endereço IP está correto e se o dispositivo está acessível na rede.")
                return
        else:
            print("Usando conexão USB...")
            if not face_reg.connect():
                print("Falha ao conectar ao dispositivo. Verifique se ele está conectado corretamente via USB.")
                return
        
        print("Conectado com sucesso!")
        
        # Obtém informações do dispositivo
        print("\nObtendo informações do dispositivo...")
        success, device_info = face_reg.get_device_info()
        if success:
            if isinstance(device_info, str):
                try:
                    device_info = json.loads(device_info)
                    print(f"Informações do dispositivo:")
                    for key, value in device_info.items():
                        print(f"  {key}: {value}")
                except json.JSONDecodeError:
                    print(f"Informações do dispositivo: {device_info}")
            else:
                print(f"Informações do dispositivo: {device_info}")
        else:
            print(f"Falha ao obter informações do dispositivo: {device_info}")
        
        # Lista todas as pessoas cadastradas
        print("\nListando pessoas cadastradas...")
        success, persons = face_reg.get_all_persons()
        if success:
            if isinstance(persons, list):
                print(f"Pessoas cadastradas: {len(persons)}")
                for person in persons:
                    print(f"  ID: {person.get('person_id')}, Nome: {person.get('name')}")
            elif isinstance(persons, dict) and 'persons' in persons:
                person_list = persons.get('persons', [])
                print(f"Pessoas cadastradas: {len(person_list)}")
                for person in person_list:
                    print(f"  ID: {person.get('person_id')}, Nome: {person.get('name')}")
            else:
                print(f"Resultado da consulta: {persons}")
        else:
            print(f"Falha ao listar pessoas: {persons}")
        
        # Menu de opções
        while True:
            print("\n==== Menu ====")
            print("1. Adicionar pessoa")
            print("2. Registrar face")
            print("3. Listar pessoas")
            print("4. Excluir pessoa")
            print("5. Aguardar reconhecimento")
            print("0. Sair")
            
            opcao = input("\nEscolha uma opção: ")
            
            if opcao == "1":
                # Adicionar pessoa
                person_id = input("Digite o ID da pessoa: ")
                name = input("Digite o nome da pessoa: ")
                
                success, result = face_reg.add_person(person_id, name)
                if success:
                    print(f"Pessoa adicionada com sucesso: {result}")
                else:
                    print(f"Falha ao adicionar pessoa: {result}")
                    
            elif opcao == "2":
                # Registrar face
                person_id = input("Digite o ID da pessoa: ")
                name = input("Digite o nome da pessoa: ")
                
                print("\nAperte ENTER para iniciar o registro de face e posicione o rosto na câmera...")
                input()
                
                print("Registrando face... Por favor, mantenha o rosto posicionado na câmera.")
                success, result = face_reg.register_face(person_id, name)
                if success:
                    print(f"Face registrada com sucesso!")
                    # Se o resultado for uma string JSON, tenta formatá-lo
                    try:
                        result_dict = json.loads(result)
                        print(f"Detalhes: {json.dumps(result_dict, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"Resultado: {result}")
                else:
                    print(f"Falha ao registrar face: {result}")
                    
            elif opcao == "3":
                # Listar pessoas
                success, persons = face_reg.get_all_persons()
                if success:
                    if isinstance(persons, list):
                        print(f"Pessoas cadastradas: {len(persons)}")
                        for person in persons:
                            print(f"  ID: {person.get('person_id')}, Nome: {person.get('name')}")
                    elif isinstance(persons, dict) and 'persons' in persons:
                        person_list = persons.get('persons', [])
                        print(f"Pessoas cadastradas: {len(person_list)}")
                        for person in person_list:
                            print(f"  ID: {person.get('person_id')}, Nome: {person.get('name')}")
                    else:
                        print(f"Resultado da consulta: {persons}")
                else:
                    print(f"Falha ao listar pessoas: {persons}")
                    
            elif opcao == "4":
                # Excluir pessoa
                person_id = input("Digite o ID da pessoa a ser excluída: ")
                
                success, result = face_reg.delete_person(person_id)
                if success:
                    print(f"Pessoa excluída com sucesso: {result}")
                else:
                    print(f"Falha ao excluir pessoa: {result}")
                    
            elif opcao == "5":
                # Aguardar reconhecimento
                print("\nAguardando reconhecimento... (pressione Ctrl+C para cancelar)")
                try:
                    while True:
                        success, result = face_reg.poll_match_result(timeout_seconds=2)
                        if success and result:
                            print("\nReconhecimento detectado!")
                            if isinstance(result, dict):
                                print(f"Detalhes: {json.dumps(result, indent=2)}")
                            else:
                                print(f"Resultado: {result}")
                            
                            continuar = input("\nPressione ENTER para continuar aguardando ou 'q' para voltar ao menu: ")
                            if continuar.lower() == 'q':
                                break
                        time.sleep(0.1)  # Pequena pausa para não sobrecarregar a CPU
                except KeyboardInterrupt:
                    print("\nMonitoramento interrompido.")
                    
            elif opcao == "0":
                # Sair
                break
                
            else:
                print("Opção inválida!")
    
    finally:
        # Garante a desconexão mesmo em caso de erro
        print("\nDesconectando do dispositivo...")
        face_reg.disconnect()
        print("Desconectado.")

if __name__ == "__main__":
    main() 