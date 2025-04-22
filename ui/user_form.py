# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from struct import pack
from zk import const
import base64
import json
import time

class UserForm(tk.Toplevel):
    def __init__(self, parent, device, user=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("Editar Usuário" if user else "Cadastro de Usuário")
        self.geometry("400x700")  # Aumentei a altura para acomodar a foto
        self.device = device
        self.user = user
        self.parent = parent
        self.cadastro_realizado = False  # Flag para controlar se o usuário foi cadastrado
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        self.id_label = ttk.Label(main_frame, text="ID do Aluno:")
        self.id_label.pack(pady=5)
        self.id_entry = ttk.Entry(main_frame)
        self.id_entry.pack(pady=5)
        
        self.nome_label = ttk.Label(main_frame, text="Nome:")
        self.nome_label.pack(pady=5)
        self.nome_entry = ttk.Entry(main_frame)
        self.nome_entry.pack(pady=5)
        
        self.senha_label = ttk.Label(main_frame, text="Senha:")
        self.senha_label.pack(pady=5)
        self.senha_entry = ttk.Entry(main_frame, show="*")
        self.senha_entry.pack(pady=5)
        
        # Frame para os botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Se for edição, preenche os campos
        if self.user:
            self.id_entry.insert(0, self.user['user_id'])
            self.id_entry.config(state='disabled')  # ID não pode ser alterado
            self.nome_entry.insert(0, self.user['name'])
            if 'password' in self.user:
                self.senha_entry.insert(0, self.user['password'])
            
            self.cadastrar_button = ttk.Button(button_frame, text="Salvar Alterações", command=self.salvar_usuario)
            self.cadastrar_button.pack(side=tk.LEFT, padx=5)
        else:
            self.cadastrar_button = ttk.Button(button_frame, text="Cadastrar Usuário", command=self.cadastrar_usuario)
            self.cadastrar_button.pack(side=tk.LEFT, padx=5)
        
        self.cancelar_button = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        self.cancelar_button.pack(side=tk.LEFT, padx=5)
        
    def cadastrar_usuario(self):
        try:
            id_aluno = self.id_entry.get()
            nome = self.nome_entry.get()
            senha = self.senha_entry.get()
            
            if not id_aluno or not nome:
                messagebox.showerror("Erro", "Por favor, preencha ID e Nome do aluno.")
                return
                
            try:
                id_aluno = int(id_aluno)
            except ValueError:
                messagebox.showerror("Erro", "O ID do aluno deve ser um número inteiro.")
                return
                
            # Desabilita o dispositivo antes de fazer alterações
            self.device.conn.disable_device()
            time.sleep(0.5)  # Aguarda o dispositivo ser desabilitado
            
            try:
                # Limpa o buffer antes de cadastrar
                self.device.conn.free_data()
                time.sleep(0.5)  # Aguarda a limpeza do buffer
                
                # Cadastra o usuário básico
                self.device.conn.set_user(
                    uid=id_aluno, 
                    name=nome, 
                    password=senha if senha else '',  # Envia string vazia se não tiver senha
                    user_id=str(id_aluno),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                self.aluno_id = id_aluno
                self.cadastro_realizado = True
                
                messagebox.showinfo(
                    "Sucesso", 
                    "Usuário cadastrado com sucesso!\nDeseja iniciar a captura facial agora?"
                )
                
                # Desabilita campos
                self.id_entry.config(state='disabled')
                self.nome_entry.config(state='disabled')
                self.senha_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
            finally:
                # Sempre reabilita o dispositivo
                time.sleep(0.5)  # Aguarda antes de reabilitar
                self.device.conn.enable_device()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(e)}")
            
    def salvar_usuario(self):
        """Salva as alterações do usuário"""
        try:
            nome = self.nome_entry.get()
            senha = self.senha_entry.get()
            
            if not nome:
                messagebox.showerror("Erro", "Por favor, preencha o Nome do aluno.")
                return
                
            # Desabilita o dispositivo antes de fazer alterações
            self.device.conn.disable_device()
            time.sleep(0.5)  # Aguarda o dispositivo ser desabilitado
            
            try:
                # Limpa o buffer antes de atualizar
                self.device.conn.free_data()
                time.sleep(0.5)  # Aguarda a limpeza do buffer
                
                # Atualiza o usuário
                self.device.conn.set_user(
                    uid=int(self.user['user_id']), 
                    name=nome, 
                    password=senha if senha else '',  # Envia string vazia se não tiver senha
                    user_id=str(self.user['user_id']),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                
                # Desabilita os campos e o botão de salvar após a atualização
                self.nome_entry.config(state='disabled')
                self.senha_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
                self.parent.refresh_user_list()  # Atualiza a lista
                    
            finally:
                # Sempre reabilita o dispositivo
                time.sleep(0.5)  # Aguarda antes de reabilitar
                self.device.conn.enable_device()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")