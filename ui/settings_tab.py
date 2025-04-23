import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class SettingsTab(ttk.Frame):
    def __init__(self, parent, config=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_data = config or {}
        self.create_widgets()

    def create_widgets(self):
        # Frame para dados de login da API
        login_frame = ttk.LabelFrame(self, text="Credenciais da API", padding="10")
        login_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(login_frame, text="Login:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.login_entry = ttk.Entry(login_frame)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(login_frame, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')

        save_cred_button = ttk.Button(login_frame, text="Salvar Credenciais", command=self.save_credentials)
        save_cred_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Frame para sincronização com a API
        sync_frame = ttk.LabelFrame(self, text="Sincronização com API", padding="10")
        sync_frame.pack(fill=tk.X, padx=10, pady=5)

        self.sync_status = ttk.Label(sync_frame, text="Status: Desconectado")
        self.sync_status.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        sync_button = ttk.Button(sync_frame, text="Sincronizar com API", command=self.sync_with_api)
        sync_button.grid(row=0, column=1, padx=5, pady=5)

        # Frame para configuração do dispositivo
        device_frame = ttk.LabelFrame(self, text="Configuração do Dispositivo", padding="10")
        device_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(device_frame, text="IP Padrão do Dispositivo:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.default_ip_entry = ttk.Entry(device_frame)
        self.default_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        # Frame para sincronização automática
        interval_frame = ttk.LabelFrame(self, text="Sincronização Automática", padding="10")
        interval_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(interval_frame, text="Intervalo (minutos):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=1440, width=10)
        self.interval_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        # Frame para exportação de dados
        export_frame = ttk.LabelFrame(self, text="Exportação de Dados", padding="10")
        export_frame.pack(fill=tk.X, padx=10, pady=5)

        export_button = ttk.Button(export_frame, text="Exportar Dados", command=self.export_data)
        export_button.pack(padx=5, pady=5)

        # Configurar o weight para as colunas que usam grid
        for frame in [login_frame, device_frame, interval_frame]:
            frame.columnconfigure(1, weight=1)

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

        # Lógica para salvar as configurações (por exemplo, em um arquivo config.json) poderia ser inserida aqui
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")

    def sync_with_api(self):
        self.sync_status.config(text="Status: Sincronizando...")
        # Placeholder para sincronização com a API
        self.after(2000, lambda: self.sync_status.config(text="Status: Conectado"))

    def export_data(self):
        # Placeholder para exportação de dados
        messagebox.showinfo("Exportar Dados", "Dados exportados com sucesso!") 