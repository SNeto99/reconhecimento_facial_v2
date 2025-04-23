# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .user_form import UserForm
from core.face_device import FaceDevice
import time
from ui.settings_tab import SettingsTab

class MainWindow(tk.Tk):
    def __init__(self, device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Interface do Dispositivo ZKTeco")
        
        # Configura o tamanho fixo da janela
        self.geometry("680x750")
        
        # Inicializa o dispositivo
        self.device = device
        if not self.device:
            self.title(self.title() + " (Desconectado)")
        
        # Notebook para as abas (agora direto na janela principal)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        self.device_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.device_tab, text="Dispositivo")
        
        self.user_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="Usuários")
        
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="Logs")
        
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Configurações")
        
        self.create_device_tab()
        self.create_user_tab()
        self.create_log_tab()
        
        if self.device:
            self.refresh_device_info()
            self.refresh_user_list()
            self.refresh_log_list()
        else:
            self.load_local_users()
            self.load_local_logs()

        # Criar área scrollable para a aba de Configurações
        settings_canvas = tk.Canvas(self.settings_tab, borderwidth=0, highlightthickness=0)
        settings_scrollbar = ttk.Scrollbar(self.settings_tab, orient="vertical", command=settings_canvas.yview)
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        settings_scrollbar.pack(side="right", fill="y")
        settings_canvas.pack(side="left", fill="both", expand=True)
        # Adicionar o widget de configurações dentro do canvas e ajustar largura
        settings_widget = SettingsTab(settings_canvas)
        settings_canvas_window = settings_canvas.create_window((0, 0), window=settings_widget, anchor="nw")
        # Ajustar a região scrollable e largura do conteúdo sempre que necessário
        def _on_configure(event):
            # Ajusta o width do window interno para preencher toda a canvas
            settings_canvas.itemconfig(settings_canvas_window, width=event.width)
            # Atualiza região de scroll
            settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        # Handle resize of canvas
        settings_canvas.bind("<Configure>", _on_configure)
        # Handle mudanças no conteúdo
        settings_widget.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        
        # Funções para ativar/desativar scroll com a roda do mouse
        def _on_mousewheel(event):
            settings_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_scroll(event):
            settings_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            settings_canvas.bind_all("<Button-4>", lambda e: settings_canvas.yview_scroll(-1, "units"))
            settings_canvas.bind_all("<Button-5>", lambda e: settings_canvas.yview_scroll(1, "units"))

        def _unbind_scroll(event):
            settings_canvas.unbind_all("<MouseWheel>")
            settings_canvas.unbind_all("<Button-4>")
            settings_canvas.unbind_all("<Button-5>")

        # Vincula ao entrar/ sair do canvas de configurações
        settings_canvas.bind("<Enter>", _bind_scroll)
        settings_canvas.bind("<Leave>", _unbind_scroll)
        
    def create_device_tab(self):
        frame = ttk.Frame(self.device_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
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
            ttk.Label(info_frame, text=text).grid(row=i, column=0, sticky='e', padx=5, pady=3)
            value_label = ttk.Label(info_frame, text="---")
            value_label.grid(row=i, column=1, sticky='w', padx=5, pady=3)
            self.info_labels[key] = value_label
        
        # Botão para atualizar informações
        refresh_button = ttk.Button(frame, text="Atualizar Informações", command=self.refresh_device_info)
        refresh_button.pack(pady=10)
        
    def add_log(self, message):
        """Adiciona uma mensagem à área de log"""
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        else:
            print(message)
        
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
                from database import save_device_info
                device_id = save_device_info(info)
                self.add_log(f"Dispositivo salvo com id: {device_id}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter informações do dispositivo: {str(e)}")

    def create_user_tab(self):
        frame = ttk.Frame(self.user_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.add_user_button = ttk.Button(button_frame, text="Adicionar Usuário", command=self.open_user_form)
        self.add_user_button.pack(side=tk.LEFT, padx=5)
        
        self.user_refresh_button = ttk.Button(button_frame, text="Atualizar Lista", command=self.refresh_user_list)
        self.user_refresh_button.pack(side=tk.LEFT, padx=5)
        if not self.device:
            self.user_refresh_button.config(state="disabled")
        
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
        
        self.log_refresh_button = ttk.Button(button_frame, text="Atualizar Logs", command=self.refresh_log_list)
        self.log_refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttk.Button(button_frame, text="Limpar Logs", command=self.clear_logs)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        
        # Rótulo para exibir a contagem de logs
        self.log_count_label = ttk.Label(frame, text="Total de logs: 0")
        self.log_count_label.pack(fill=tk.X, padx=10, pady=5)
        
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
        """Atualiza a lista de usuários a partir do dispositivo, se conectado"""
        if not self.device:
            messagebox.showinfo("Atenção", "Por favor, conecte-se com o dispositivo para atualizar a lista de usuários.")
            return
        try:
            from database import init_db, synchronize_users, add_device
            init_db()
            device_info = self.device.get_device_info()
            current_device_id = add_device(device_info.get("mac"))
            device_users = self.device.get_users()
            local_users = synchronize_users(device_users, current_device_id)
            local_users = sorted(local_users, key=lambda u: u[0], reverse=True)
            for item in self.user_list.get_children():
                self.user_list.delete(item)
            for u in local_users:
                # u: [id, device_user_id, system_id, name, synced]
                self.user_list.insert("", "end", values=(u[1], u[3], "̲E̲d̲i̲t̲a̲r̲", "̲E̲x̲c̲l̲u̲i̲r̲"))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista de usuários: {str(e)}")
            
    def refresh_log_list(self):
        """Atualiza a lista de logs a partir do dispositivo, se conectado"""
        if not self.device:
            messagebox.showinfo("Atenção", "Por favor, conecte-se com o dispositivo para atualizar os logs.")
            return
        try:
            for item in self.log_list.get_children():
                self.log_list.delete(item)
            from database import get_all_users, synchronize_logs, add_device, get_event_map
            local_users = get_all_users()
            user_mapping = {u[1]: u[3] for u in local_users}
            event_map = get_event_map()
            device_info = self.device.get_device_info()
            current_device_id = add_device(device_info.get("mac"))
            device_logs = self.device.get_attendance_logs()
            # Insere o current_device_id em cada log para associá-los ao dispositivo
            for log in device_logs:
                log['device_id'] = current_device_id
            logs = synchronize_logs(device_logs)
            from datetime import datetime
            for log in logs:
                if not isinstance(log['timestamp'], datetime):
                    log['timestamp'] = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            logs_sorted = sorted(logs, key=lambda log: log['timestamp'], reverse=True)
            self.log_count_label.config(text=f"Total de logs: {len(logs_sorted)}")
            for log in logs_sorted:
                try:
                    status_code = int(log['status'])
                except:
                    status_code = log['status']
                event_name = event_map.get(status_code, log['status'])
                student_name = user_mapping.get(log['user_id'], log['user_id'])
                self.log_list.insert('', 'end', values=(log['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), student_name, event_name))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista de logs: {str(e)}")
        
    def on_mouse_move(self, event):
        """Altera o cursor quando passa sobre os botões de ação"""
        region = self.user_list.identify_region(event.x, event.y)
        column = self.user_list.identify_column(event.x)
        
        if region == "cell" and column in ("#3", "#4"):  # Colunas de Editar e Apagar
            self.user_list.config(cursor="hand2")
        else:
            self.user_list.config(cursor="")

    def disable_device_controls(self):
        """Desabilita os botões que interagem diretamente com o dispositivo."""
        try:
            if hasattr(self, 'add_user_button'):
                self.add_user_button.config(state='disabled')
            if hasattr(self, 'log_refresh_button'):
                self.log_refresh_button.config(state='disabled')
            if hasattr(self, 'clear_log_button'):
                self.clear_log_button.config(state='disabled')
        except Exception as e:
            print("Erro ao desabilitar os controles do dispositivo:", e)

    def enable_device_controls(self):
        """Habilita os botões que interagem diretamente com o dispositivo."""
        try:
            if hasattr(self, 'add_user_button'):
                self.add_user_button.config(state='normal')
            if hasattr(self, 'log_refresh_button'):
                self.log_refresh_button.config(state='normal')
            if hasattr(self, 'clear_log_button'):
                self.clear_log_button.config(state='normal')
        except Exception as e:
            print("Erro ao habilitar os controles do dispositivo:", e)

    def load_local_users(self):
        """Carrega usuários do banco de dados local e atualiza a lista"""
        try:
            from database import get_all_users
            local_users = get_all_users()
            local_users = sorted(local_users, key=lambda u: u[0], reverse=True)
            for item in self.user_list.get_children():
                self.user_list.delete(item)
            for u in local_users:
                self.user_list.insert("", "end", values=(u[1], u[3], "̲E̲d̲i̲t̲a̲r̲", "̲E̲x̲c̲l̲u̲i̲r̲"))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários locais: {str(e)}")

    def load_local_logs(self):
        """Carrega logs do banco de dados local e atualiza a lista"""
        try:
            from database import get_all_logs, get_all_users, get_event_map
            local_users = get_all_users()
            user_mapping = {u[1]: u[3] for u in local_users}
            event_map = get_event_map()
            logs = get_all_logs()
            from datetime import datetime
            for log in logs:
                if not isinstance(log['timestamp'], datetime):
                    log['timestamp'] = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            logs_sorted = sorted(logs, key=lambda log: log['timestamp'], reverse=True)
            self.log_count_label.config(text=f"Total de logs: {len(logs_sorted)}")
            for log in logs_sorted:
                try:
                    status_code = int(log['status'])
                except:
                    status_code = log['status']
                event_name = event_map.get(status_code, log['status'])
                student_name = user_mapping.get(log['user_id'], log['user_id'])
                self.log_list.insert('', 'end', values=(log['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), student_name, event_name))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar logs locais: {str(e)}")