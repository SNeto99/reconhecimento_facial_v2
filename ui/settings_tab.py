import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import get_config_value, set_config_value


class SettingsTab(ttk.Frame):
    def __init__(self, parent, config=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_data = config or {}
        self.create_widgets()

    def create_widgets(self):
        # Adicionado novo frame para conexão com o dispositivo
        connection_frame = ttk.LabelFrame(self, text="Conexão com o Dispositivo", padding="10")
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(connection_frame, text="IP do Dispositivo:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.device_ip_entry = ttk.Entry(connection_frame, width=20)
        self.device_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.device_ip_entry.insert(0, get_config_value("last_connected_ip", "192.168.50.201"))
        connect_button = ttk.Button(connection_frame, text="Conectar", command=self.connect_device_from_settings)
        connect_button.grid(row=0, column=2, padx=5, pady=5)

        # Frame para dados de login da API
        login_frame = ttk.LabelFrame(self, text="Credenciais da API", padding="10")
        login_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(login_frame, text="Login:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.login_entry = ttk.Entry(login_frame, width=20)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)
        self.login_entry.insert(0, get_config_value("login", ""))

        ttk.Label(login_frame, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(login_frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_entry.insert(0, get_config_value("password", ""))

        save_cred_button = ttk.Button(login_frame, text="Salvar Credenciais", command=self.save_credentials)
        save_cred_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Novo frame unificado para Sincronização
        sync_frame = ttk.LabelFrame(self, text="Sincronização", padding="10")
        sync_frame.pack(fill=tk.X, padx=10, pady=5)

        self.sync_status = ttk.Label(sync_frame, text="Status: Desconectado")
        self.sync_status.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        sync_button = ttk.Button(sync_frame, text="Sincronizar com API", command=self.sync_with_api)
        sync_button.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(sync_frame, text="Intervalo (minutos):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.interval_spinbox = ttk.Spinbox(sync_frame, from_=1, to=1440, width=10)
        self.interval_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky='we')

        sync_interval = get_config_value("sync_interval", "10")
        self.interval_spinbox.delete(0, tk.END)
        self.interval_spinbox.insert(0, sync_interval)

        save_sync_button = ttk.Button(sync_frame, text="Salvar Sincronização", command=self.save_sync_config)
        save_sync_button.grid(row=1, column=2, padx=5, pady=5)

        # Container para os formulários de Exportação e Gerenciamento de Eventos
        forms_container = ttk.Frame(self)
        forms_container.pack(fill=tk.X, padx=10, pady=5)

        # Formulário para Exportação de Dados
        export_frame = ttk.LabelFrame(forms_container, text="Exportação de Dados", padding="10")
        export_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        export_button = ttk.Button(export_frame, text="Exportar Dados", command=self.export_data)
        export_button.pack(padx=5, pady=5)

        # Formulário para Gerenciamento de Eventos
        events_frame = ttk.LabelFrame(forms_container, text="Gerenciar Eventos", padding="10")
        events_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0))
        events_button = ttk.Button(events_frame, text="Gerenciar Eventos", command=self.open_events_manager)
        events_button.pack(padx=5, pady=5)

        # Novo frame para exibir as Informações do Dispositivo
        device_info_frame = ttk.LabelFrame(self, text="Informações do Dispositivo", padding="10")
        device_info_frame.pack(fill=tk.X, padx=10, pady=5)
        # Permitir expansão da segunda coluna
        device_info_frame.columnconfigure(1, weight=1)
        info_mapping = [
            ("mac", "MAC"),
            ("firmware", "Firmware"),
            ("platform", "Plataforma"),
            ("serial", "Serial"),
            ("face_algorithm", "Algoritmo Facial"),
            ("users", "Usuários"),
            ("faces", "Faces"),
            ("records", "Registros"),
            ("device_name", "Nome do Dispositivo")
        ]
        self.device_info_labels = {}
        for i, (key, label_text) in enumerate(info_mapping):
            ttk.Label(device_info_frame, text=label_text+":").grid(row=i, column=0, padx=5, pady=2, sticky='w')
            lbl = ttk.Label(device_info_frame, text="---")
            lbl.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            self.device_info_labels[key] = lbl
        # Criar subframe para o botão para não misturar grid e pack no mesmo container
        button_frame = ttk.Frame(device_info_frame)
        button_frame.grid(row=len(info_mapping), column=0, columnspan=2, sticky='we', padx=5, pady=(20,20))
        # Expandir o frame do botão
        button_frame.columnconfigure(0, weight=1)
        update_info_button = ttk.Button(button_frame, text="Atualizar Informações", command=self.update_device_info)
        update_info_button.pack(side=tk.RIGHT, padx=5)
        # Preencher automaticamente as informações se já estiver conectado
        toplevel = self.winfo_toplevel()
        if hasattr(toplevel, 'device') and toplevel.device:
            self.update_device_info()

    def save_credentials(self):
        new_login = self.login_entry.get()
        new_password = self.password_entry.get()
        if not new_login or not new_password:
            messagebox.showerror("Erro", "Ambos os campos de credenciais são obrigatórios.")
            return

        # Confirmação de senha
        confirm = messagebox.askyesno("Confirmar", "Deseja alterar a senha?")
        if confirm:
            senha_repetida = simpledialog.askstring("Confirmação", "Digite a senha novamente:", show="*")
            if senha_repetida != new_password:
                messagebox.showerror("Erro", "As senhas não conferem.")
                return

        set_config_value("login", new_login)
        set_config_value("password", new_password)
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")

    def sync_with_api(self):
        self.sync_status.config(text="Status: Sincronizando...")
        # Placeholder para sincronização com a API
        self.after(2000, lambda: self.sync_status.config(text="Status: Conectado"))

    def export_data(self):
        # Placeholder para exportação de dados
        messagebox.showinfo("Exportar Dados", "Dados exportados com sucesso!")

    def connect_device_from_settings(self):
        ip = self.device_ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Erro", "Por favor, insira o IP do dispositivo.")
            return
        try:
            from core.face_device import FaceDevice
        except ImportError as e:
            messagebox.showerror("Erro", f"Importação falhou: {e}")
            return
        device = FaceDevice(ip)
        device.set_debug_callback(lambda msg: print(msg))
        loading_window = tk.Toplevel(self)
        loading_window.title("Conectando...")
        ttk.Label(loading_window, text="Conectando...").pack(padx=20, pady=20)
        loading_window.geometry("200x100")
        loading_window.transient(self)
        loading_window.grab_set()
        
        import threading
        def attempt_connection():
            result = device.connect()
            self.after(0, lambda: on_connection_result(result))
        def on_connection_result(result):
            loading_window.destroy()
            if result:
                messagebox.showinfo("Sucesso", "Conectado com sucesso ao dispositivo!")
                # Atualizar a janela principal
                toplevel = self.winfo_toplevel()
                toplevel.device = device
                toplevel.title("Interface do Dispositivo ZKTeco")
                if hasattr(toplevel, 'enable_device_controls'):
                    toplevel.enable_device_controls()
                else:
                    print("Função enable_device_controls não implementada")
                if hasattr(toplevel, 'refresh_device_info'):
                    toplevel.refresh_device_info()
                if hasattr(toplevel, 'refresh_user_list'):
                    toplevel.refresh_user_list()
                if hasattr(toplevel, 'refresh_log_list'):
                    toplevel.refresh_log_list()
                from database import set_config_value
                set_config_value("last_connected_ip", ip)
                self.update_device_info()
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao dispositivo.")
        threading.Thread(target=attempt_connection, daemon=True).start()

    def open_events_manager(self):
        from ui.events_manager import EventsManager
        EventsManager(self)

    def save_sync_config(self):
        sync_interval = self.interval_spinbox.get()
        set_config_value("sync_interval", sync_interval)
        messagebox.showinfo("Sucesso", "Configurações de sincronização salvas com sucesso!")

    def update_device_info(self):
        toplevel = self.winfo_toplevel()
        if not hasattr(toplevel, "device") or not toplevel.device:
            return
        try:
            info = toplevel.device.get_device_info()
            if info:
                for key, lbl in self.device_info_labels.items():
                    lbl.config(text=str(info.get(key, '---')))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter informações do dispositivo: {str(e)}") 