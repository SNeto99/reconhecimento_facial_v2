# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .user_form import UserForm
from core.face_device import FaceDevice
import time

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Interface do Dispositivo ZKTeco")
        
        # Configura o tamanho fixo da janela
        self.geometry("800x726")
        
        # Inicializa o dispositivo
        self.device = None
        
        # Notebook para as abas (agora direto na janela principal)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        self.device_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.device_tab, text="Dispositivo")
        
        self.user_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="Usuários")
        
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="Logs")
        
        self.create_device_tab()
        self.create_user_tab()
        self.create_log_tab()
        
        # Desabilita as abas até que haja conexão
        self.notebook.state(['disabled'])
        
    def create_device_tab(self):
        frame = ttk.Frame(self.device_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de conexão
        self.connection_frame = ttk.LabelFrame(frame, text="Conexão", padding="5")
        self.connection_frame.pack(fill=tk.X, pady=5)
        
        # Campos de conexão
        self.ip_label = ttk.Label(self.connection_frame, text="IP do Dispositivo:")
        self.ip_label.pack(side=tk.LEFT, padx=5)
        self.ip_entry = ttk.Entry(self.connection_frame)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.ip_entry.insert(0, "192.168.50.201")  # IP padrão
        
        # Porta
        self.port_label = ttk.Label(self.connection_frame, text="Porta:")
        self.port_label.pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(self.connection_frame, width=6)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.port_entry.insert(0, "4370")  # Porta padrão
        
        self.connect_button = ttk.Button(self.connection_frame, text="Conectar", command=self.connect_device)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(self.connection_frame, text="Desconectado")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Área de log
        self.log_frame = ttk.LabelFrame(frame, text="Log de Conexão", padding="5")
        self.log_frame.pack(fill=tk.X, pady=5)
        
        # Usando ScrolledText para ter barra de rolagem
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, width=70)
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Botão para limpar logs
        self.clear_log_button = ttk.Button(self.log_frame, text="Limpar Logs", command=self.clear_logs)
        self.clear_log_button.pack(pady=5)
        
        # Frame para informações do dispositivo
        info_label = ttk.Label(frame, text="Informações do Dispositivo", font=('Helvetica', 12, 'bold'))
        info_label.pack(pady=10)
        
        # Criando frame para informações em grid
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Labels para as informações
        self.info_labels = {}
        info_fields = [
            ("MAC", "Endereço MAC:"),
            ("firmware", "Versão do Firmware:"),
            ("platform", "Plataforma:"),
            ("serial", "Número de Série:"),
            ("face_algorithm", "Algoritmo Facial:"),
            ("users", "Total de Usuários:"),
            ("faces", "Total de Faces:"),
            ("records", "Total de Registros:"),
            ("device_name", "Nome do Dispositivo:")
        ]
        
        for i, (key, text) in enumerate(info_fields):
            # Label do campo
            ttk.Label(info_frame, text=text).grid(row=i, column=0, sticky='e', padx=5, pady=3)
            # Label do valor
            value_label = ttk.Label(info_frame, text="---")
            value_label.grid(row=i, column=1, sticky='w', padx=5, pady=3)
            self.info_labels[key] = value_label
        
        # Botão para atualizar informações
        refresh_button = ttk.Button(frame, text="Atualizar Informações", command=self.refresh_device_info)
        refresh_button.pack(pady=10)
        
    def add_log(self, message):
        """Adiciona uma mensagem à área de log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Limpa os logs do dispositivo"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todos os logs?"):
            try:
                if self.device.clear_attendance_logs():
                    messagebox.showinfo("Sucesso", "Logs limpos com sucesso!")
                    self.refresh_log_list()
                else:
                    messagebox.showerror("Erro", "Não foi possível limpar os logs.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs: {str(e)}")
                
    def connect_device(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        
        if not ip:
            messagebox.showerror("Erro", "Por favor, insira o IP do dispositivo.")
            return
            
        try:
            self.add_log(f"Tentando conectar ao dispositivo {ip}:{port}...")
            self.device = FaceDevice(ip, port)
            self.device.set_debug_callback(self.add_log)
            
            self.add_log("Inicializando SDKs...")
            if self.device.connect():
                self.status_label.config(text="Conectado")
                self.connect_button.config(text="Desconectar", command=self.disconnect_device)
                self.notebook.state(['!disabled'])
                self.add_log("Conectado com sucesso!")
                
                # Atualiza todas as informações
                self.refresh_device_info()
                self.refresh_user_list()
                self.refresh_log_list()
                
                messagebox.showinfo("Sucesso", "Conectado ao dispositivo com sucesso!")
            else:
                self.add_log("Falha na conexão com o dispositivo")
                messagebox.showerror("Erro", "Não foi possível conectar ao dispositivo.")
                
        except Exception as e:
            error_msg = str(e)
            self.add_log(f"Erro ao conectar: {error_msg}")
            messagebox.showerror("Erro", f"Erro ao conectar: {error_msg}")
            
    def disconnect_device(self):
        try:
            if self.device:
                self.add_log("Desconectando do dispositivo...")
                self.device.disconnect()
                self.status_label.config(text="Desconectado")
                self.connect_button.config(text="Conectar", command=self.connect_device)
                self.notebook.state(['disabled'])
                self.add_log("Desconectado com sucesso")
                
        except Exception as e:
            error_msg = str(e)
            self.add_log(f"Erro ao desconectar: {error_msg}")
            messagebox.showerror("Erro", f"Erro ao desconectar: {error_msg}")
            
    def refresh_device_info(self):
        """Atualiza as informações do dispositivo"""
        if not self.device:
            return
            
        try:
            # Obtém informações do dispositivo
            info = self.device.get_device_info()
            
            # Atualiza os labels com as informações
            if info:
                self.info_labels["MAC"].config(text=info.get("mac", "---"))
                self.info_labels["firmware"].config(text=info.get("firmware", "---"))
                self.info_labels["platform"].config(text=info.get("platform", "---"))
                self.info_labels["serial"].config(text=info.get("serial", "---"))
                self.info_labels["face_algorithm"].config(text=info.get("face_algorithm", "---"))
                self.info_labels["users"].config(text=str(info.get("users", "---")))
                self.info_labels["faces"].config(text=str(info.get("faces", "---")))
                self.info_labels["records"].config(text=str(info.get("records", "---")))
                self.info_labels["device_name"].config(text=info.get("device_name", "---"))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter informações do dispositivo: {str(e)}")

    def create_user_tab(self):
        frame = ttk.Frame(self.user_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.add_user_button = ttk.Button(button_frame, text="Adicionar Usuário", command=self.open_user_form)
        self.add_user_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Atualizar Lista", command=self.refresh_user_list)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Lista de usuários
        list_frame = ttk.LabelFrame(frame, text="Usuários Cadastrados", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Adiciona scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cria a tabela com colunas para botões separados
        self.user_list = ttk.Treeview(list_frame, columns=("ID", "Nome", "Editar", "Apagar"), show="headings",
                                     yscrollcommand=scrollbar.set)
        self.user_list.heading("ID", text="ID")
        self.user_list.heading("Nome", text="Nome")
        self.user_list.heading("Editar", text="")
        self.user_list.heading("Apagar", text="")
        
        # Configura larguras das colunas
        self.user_list.column("ID", width=100)
        self.user_list.column("Nome", width=200)
        self.user_list.column("Editar", width=80, anchor="center")
        self.user_list.column("Apagar", width=80, anchor="center")
        
        self.user_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.user_list.yview)
        
        # Bind do clique nos botões e eventos do mouse
        self.user_list.bind('<ButtonRelease-1>', self.handle_user_action)
        self.user_list.bind('<Motion>', self.on_mouse_move)

    def handle_user_action(self, event):
        """Manipula cliques nos botões de ação"""
        if not self.device:
            return
            
        region = self.user_list.identify_region(event.x, event.y)
        if region == "cell":
            column = self.user_list.identify_column(event.x)
            item = self.user_list.identify_row(event.y)
            
            if column == "#3":  # Coluna Editar
                user_id = self.user_list.item(item)['values'][0]
                self.edit_user(user_id)
            elif column == "#4":  # Coluna Apagar
                user_id = self.user_list.item(item)['values'][0]
                self.delete_user(user_id)

    def edit_user(self, user_id):
        """Abre formulário para editar usuário"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        try:
            # Obtém dados do usuário
            users = self.device.get_users()
            user = next((u for u in users if u['user_id'] == str(user_id)), None)
            
            if user:
                form = UserForm(self, self.device, user=user)
                self.wait_window(form)  # Espera a janela de edição fechar
                self.refresh_user_list()  # Atualiza a lista após o fechamento
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
                
        except Exception as e:
            self.refresh_user_list()  # Atualiza a lista mesmo em caso de erro

    def delete_user(self, user_id):
        """Deleta um usuário"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o usuário {user_id}?"):
            try:
                result = self.device.delete_user(user_id)
                # Atualiza a lista após um pequeno delay para garantir que a operação foi concluída
                self.after(500, self.refresh_user_list)
                if result:
                    messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")
            except Exception as e:
                # Atualiza a lista mesmo em caso de erro após um pequeno delay
                self.after(500, self.refresh_user_list)

    def create_log_tab(self):
        frame = ttk.Frame(self.log_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        refresh_button = ttk.Button(button_frame, text="Atualizar Logs", command=self.refresh_log_list)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Limpar Logs", command=self.clear_logs)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Lista de logs
        list_frame = ttk.LabelFrame(frame, text="Registros de Acesso", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Adiciona scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_list = ttk.Treeview(list_frame, columns=("Data", "Usuário", "Evento"), show="headings",
                                    yscrollcommand=scrollbar.set)
        self.log_list.heading("Data", text="Data/Hora")
        self.log_list.heading("Usuário", text="Usuário")
        self.log_list.heading("Evento", text="Evento")
        
        self.log_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_list.yview)
        
    def open_user_form(self):
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        UserForm(self, self.device)
        
    def refresh_user_list(self):
        """Atualiza a lista de usuários"""
        if not self.device:
            return
            
        try:
            # Limpa a lista atual
            for item in self.user_list.get_children():
                self.user_list.delete(item)
                
            # Obtém a lista de usuários
            users = self.device.get_users()
            
            # Adiciona os usuários à lista
            for user in users:
                # Insere o item com as tags apropriadas para cada coluna
                self.user_list.insert("", "end", values=(
                    user['user_id'],
                    user['name'],
                    "̲E̲d̲i̲t̲a̲r̲",  # Usando o caractere combinante U+0332 de forma contínua
                    "̲E̲x̲c̲l̲u̲i̲r̲"   # Usando o caractere combinante U+0332 de forma contínua
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista de usuários: {str(e)}")
            
    def refresh_log_list(self):
        """Atualiza a lista de logs"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        try:
            # Limpa a lista atual
            for item in self.log_list.get_children():
                self.log_list.delete(item)
                
            # Obtém e exibe os logs
            logs = self.device.get_attendance_logs()
            for log in logs:
                self.log_list.insert('', 'end', values=(
                    log['timestamp'].strftime('%d/%m/%Y %H:%M:%S'),
                    log['user_id'],
                    log['status']
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista de logs: {str(e)}")
        
    def iniciar_cadastro_facial(self, user_id):
        """
        Inicia o processo de cadastro facial para um usuário
        """
        try:
            # Desativa o dispositivo temporariamente
            self.face_device.disable_device()
            
            # Inicia o processo de cadastro
            if self.face_device.face_capture.start_enrollment(user_id):
                self.show_message(
                    "Cadastro Facial",
                    "Por favor, posicione seu rosto na frente do dispositivo.\n"
                    "Mantenha o rosto centralizado e aguarde a captura."
                )
                
                # Loop para verificar o status do cadastro
                attempts = 0
                while attempts < 30:  # 30 segundos de timeout
                    if self.face_device.face_capture.check_enrollment_status():
                        self.show_message("Sucesso", "Cadastro facial realizado com sucesso!")
                        return True
                    time.sleep(1)
                    attempts += 1
                    
                self.show_error("Erro", "Tempo excedido para cadastro facial")
                return False
                
        except Exception as e:
            self.show_error("Erro", f"Falha no cadastro facial: {str(e)}")
            return False
            
        finally:
            # Reativa o dispositivo
            self.face_device.enable_device()

    def on_mouse_move(self, event):
        """Altera o cursor quando passa sobre os botões de ação"""
        region = self.user_list.identify_region(event.x, event.y)
        column = self.user_list.identify_column(event.x)
        
        if region == "cell" and column in ("#3", "#4"):  # Colunas de Editar e Apagar
            self.user_list.config(cursor="hand2")
        else:
            self.user_list.config(cursor="")