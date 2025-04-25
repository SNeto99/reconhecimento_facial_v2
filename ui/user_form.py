# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from struct import pack
from zk import const
import base64
import json
import time
from core.api import buscar_alunos
from database import add_device, insert_or_update_user

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
        
        # Campos adicionais RA, Série e Turma
        self.ra_label = ttk.Label(main_frame, text="RA do Aluno:")
        self.ra_label.pack(pady=5)
        self.ra_entry = ttk.Entry(main_frame)
        self.ra_entry.pack(pady=5)
        self.serie_label = ttk.Label(main_frame, text="Série:")
        self.serie_label.pack(pady=5)
        self.serie_entry = ttk.Entry(main_frame)
        self.serie_entry.pack(pady=5)
        self.turma_label = ttk.Label(main_frame, text="Turma:")
        self.turma_label.pack(pady=5)
        self.turma_entry = ttk.Entry(main_frame)
        self.turma_entry.pack(pady=5)
        
        # Busca de alunos da API
        self.api_id = None
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Aluno na API", padding="10")
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Nome API:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.api_search_entry = ttk.Entry(search_frame)
        self.api_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        search_btn = ttk.Button(search_frame, text="Buscar", command=self.search_api)
        search_btn.grid(row=0, column=2, padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        self.api_listbox = tk.Listbox(search_frame, height=5)
        self.api_listbox.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
        self.api_listbox.bind('<<ListboxSelect>>', self.select_api_student)
        search_frame.rowconfigure(1, weight=1)
        # Armazena resultados da busca
        self.api_results = []
        # Label de confirmação do aluno selecionado
        self.selected_label = ttk.Label(main_frame, text="Aluno Selecionado: ---")
        self.selected_label.pack(pady=5)
        
        # Frame para os botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Se for edição, preenche os campos
        if self.user:
            self.id_entry.insert(0, self.user['user_id'])
            self.id_entry.config(state='disabled')  # ID não pode ser alterado
            self.nome_entry.insert(0, self.user['name'])
            # Preenche campos adicionais ao editar
            self.ra_entry.insert(0, self.user.get('ra', ''))
            self.serie_entry.insert(0, self.user.get('serie', ''))
            self.turma_entry.insert(0, self.user.get('turma', ''))
            # Inicializa api_id e api_name com valores existentes
            self.api_id = self.user.get('system_id')
            self.api_name = self.user.get('api_name')
            
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
            ra = self.ra_entry.get()
            serie = self.serie_entry.get()
            turma = self.turma_entry.get()
            
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
                    password='',  # Envia string vazia se não tiver senha
                    user_id=str(id_aluno),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                self.aluno_id = id_aluno
                self.cadastro_realizado = True
                
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                
                # Desabilita campos
                self.id_entry.config(state='disabled')
                self.nome_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
                # Persiste vinculação com API no banco
                device_info = self.device.get_device_info()
                device_id = add_device(device_info.get('mac'))
                # Prepara valores para BD
                device_user_id = str(id_aluno)
                system_id = str(self.api_id) if self.api_id else device_user_id
                alias_name = self.nome_entry.get()
                api_name = self.api_name or alias_name
                # Usa campos adicionais
                insert_or_update_user(device_user_id, system_id, alias_name, api_name, ra, serie, turma, device_id)
                
                # Fecha o formulário após salvar
                self.destroy()
                
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
            ra = self.ra_entry.get()
            serie = self.serie_entry.get()
            turma = self.turma_entry.get()
            
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
                    password='',  # Envia string vazia se não tiver senha
                    user_id=str(self.user['user_id']),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                
                # Desabilita os campos e o botão de salvar após a atualização
                self.nome_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
                # Persiste vinculação com API no banco
                device_info = self.device.get_device_info()
                device_id = add_device(device_info.get('mac'))
                device_user_id = str(self.user['user_id'])
                system_id = str(self.api_id) if self.api_id else device_user_id
                alias_name = self.nome_entry.get()
                api_name = self.api_name or alias_name
                insert_or_update_user(device_user_id, system_id, alias_name, api_name, ra, serie, turma, device_id)
                
                self.parent.refresh_user_list()  # Atualiza a lista após o fechamento
                    
                # Fecha o formulário após salvar as alterações
                self.destroy()
                
            finally:
                # Sempre reabilita o dispositivo
                time.sleep(0.5)  # Aguarda antes de reabilitar
                self.device.conn.enable_device()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")

    def search_api(self):
        """Busca alunos na API e popula a listbox"""
        nome = self.api_search_entry.get().strip()
        try:
            results = buscar_alunos(nome)
            self.api_results = results
            self.api_listbox.delete(0, tk.END)
            for r in results:
                self.api_listbox.insert(tk.END, r['nome'])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar alunos: {e}")

    def select_api_student(self, event):
        """Seleciona aluno da API e preenche campos"""
        idx = self.api_listbox.curselection()
        if not idx:
            return
        student = self.api_results[idx[0]]
        # Preenche no form
        self.id_entry.delete(0, tk.END)
        # Sugere o menor ID disponível até 65535
        try:
            existing_ids = {int(u['user_id']) for u in self.device.get_users()}
            for i in range(1, 65536):
                if i not in existing_ids:
                    next_id = i
                    break
        except Exception:
            # Fallback para ID da API se válido
            api_id = int(student.get('id', 0))
            next_id = api_id if api_id <= 65535 else 1
        self.id_entry.insert(0, str(next_id))
        self.nome_entry.delete(0, tk.END)
        self.nome_entry.insert(0, student['nome'])
        # Preenche campos adicionais
        self.ra_entry.delete(0, tk.END)
        self.ra_entry.insert(0, student.get('ra', ''))
        self.serie_entry.delete(0, tk.END)
        self.serie_entry.insert(0, student.get('serie', ''))
        self.turma_entry.delete(0, tk.END)
        self.turma_entry.insert(0, student.get('turma', ''))
        # Atualiza label de confirmação
        self.selected_label.config(text=f"Aluno Selecionado: {student['nome']}")
        # Armazena para persistir
        self.api_id = student['id']
        self.api_name = student['nome']