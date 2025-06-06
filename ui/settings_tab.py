import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import font as tkfont
from database import get_config_value, set_config_value, get_connection
from core.api import buscar_cidades, buscar_escolas_cidade
import csv
import os
import zipfile
from datetime import datetime


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

        # Novo frame unificado para Sincronização
        # Padding ajustado para aproximar o conteúdo do título
        sync_frame = ttk.LabelFrame(self, text="Sincronização", padding=(10,2))
        sync_frame.pack(fill=tk.X, padx=10, pady=5)
        # Permite que a coluna 1 expanda, mantendo botão Salvar fixo à direita
        sync_frame.columnconfigure(1, weight=1)
        # Layout simples: sem expansão automática de colunas

        # Exibe data/hora da última sincronização ou estado inicial
        last_sync = get_config_value("last_sync", "")
        # Prepara prefixo e texto de data separadamente
        if last_sync:
            try:
                dt = datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
                date_text = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                date_text = last_sync
            prefix_text = "Última sincronização:"
        else:
            date_text = "Desconectado"
            prefix_text = "Status:"
        # Label de prefixo (fonte normal)
        self.sync_prefix = ttk.Label(sync_frame, text=prefix_text)
        self.sync_prefix.grid(row=0, column=0, padx=5, pady=(0,2), sticky='w')
        # Label de data (fonte normal, mesmo estilo do prefixo)
        self.sync_date = ttk.Label(sync_frame, text=date_text)
        self.sync_date.grid(row=0, column=1, padx=5, pady=(0,2), sticky='w')

        sync_button = ttk.Button(sync_frame, text="Sincronizar com API", command=self.sync_with_api)
        # Botão será reposicionado abaixo após configuração de intervalo

        ttk.Label(sync_frame, text="Intervalo (minutos):").grid(row=1, column=0, padx=(5,0), pady=(2,2), sticky='w')
        self.interval_spinbox = ttk.Spinbox(sync_frame, from_=1, to=1440, width=10)
        # Spinbox fixo à esquerda da coluna expansível
        self.interval_spinbox.grid(row=1, column=1, padx=(0,5), pady=(2,2), sticky='w')

        sync_interval = get_config_value("sync_interval", "10")
        self.interval_spinbox.delete(0, tk.END)
        self.interval_spinbox.insert(0, sync_interval)

        save_sync_button = ttk.Button(sync_frame, text="Salvar", command=self.save_sync_config)
        # Botão Salvar alinhado à direita da coluna 2
        save_sync_button.grid(row=1, column=2, padx=5, pady=(2,2), sticky='e')
        
        # Posiciona botão de sincronizar abaixo dos minutos, alinhado ao centro
        sync_button.grid(row=2, column=0, columnspan=3, padx=5, pady=(5,1), sticky='w')

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
        # Por fim, bloco de Configurar API (movido para baixo)
        api_frame = ttk.LabelFrame(self, text="Configurar API", padding="10")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        api_button = ttk.Button(api_frame, text="Configurar API", command=self.open_api_config_window)
        api_button.pack(padx=5, pady=5)

    def save_sync_config(self):
        sync_interval = self.interval_spinbox.get()
        set_config_value("sync_interval", sync_interval)
        messagebox.showinfo("Sucesso", "Configurações de sincronização salvas com sucesso!")

    def open_api_config_window(self):
        # Cria janela de configuração de API
        win = tk.Toplevel(self)
        win.title("Configurar API")
        win.geometry("800x650")
        win.resizable(True, True)
        # Inicializa mapas e seleção
        city_map = {}
        school_map = {}
        selected_school = {}

        # URL da API
        url_frame = ttk.LabelFrame(win, text="URL da API", padding="10")
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(url_frame, text="Base URL:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        api_url_entry = ttk.Entry(url_frame, width=40)
        api_url_entry.grid(row=0, column=1, padx=5, pady=5)
        api_url_entry.insert(0, get_config_value("api_url", os.getenv("API_URL", ""))
)

        # Credenciais da API
        cred_frame = ttk.LabelFrame(win, text="Credenciais da API", padding="10")
        cred_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(cred_frame, text="Login:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        login_entry = ttk.Entry(cred_frame, width=30)
        login_entry.grid(row=0, column=1, padx=5, pady=5)
        login_entry.insert(0, get_config_value("login", ""))
        ttk.Label(cred_frame, text="Senha:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        password_entry = ttk.Entry(cred_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        password_entry.insert(0, get_config_value("password", ""))

        # Seleção de Cidade
        city_frame = ttk.LabelFrame(win, text="Seleção de Cidade", padding="10")
        city_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(city_frame, text="Cidade:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        city_combobox = ttk.Combobox(city_frame, state="readonly", width=30)
        city_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # Botão para atualizar cidades após configurar a URL
        def refresh_cities():
            api_url = api_url_entry.get().strip()
            if not api_url:
                messagebox.showwarning("Aviso", "Configure a URL da API primeiro.", parent=win)
                return
            # Salva URL temporariamente para que buscar_cidades possa usá-la
            from database import set_config_value
            set_config_value("api_url", api_url)
            try:
                cidades = buscar_cidades()
                if not cidades:
                    messagebox.showinfo("Informação", "Nenhuma cidade encontrada. Verifique a URL da API.", parent=win)
                    return
                city_names = [c['nome'] for c in cidades]
                city_map.clear()
                city_map.update({c['nome']: c['id'] for c in cidades})
                city_combobox['values'] = city_names
                current_city = get_config_value("city_name", "")
                if current_city in city_names:
                    city_combobox.set(current_city)
                else:
                    city_combobox.set('')  # Limpa seleção atual se não for válida
                messagebox.showinfo("Sucesso", f"Lista de cidades atualizada: {len(cidades)} encontradas.", parent=win)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível buscar cidades: {e}", parent=win)
        
        refresh_cities_btn = ttk.Button(city_frame, text="Atualizar", command=refresh_cities)
        refresh_cities_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Tentativa inicial de carregar cidades se houver URL configurada
        
        api_url = get_config_value("api_url", os.getenv("API_URL", ""))
        
        if api_url:
            try:
                cidades = buscar_cidades()
                if cidades:
                    city_names = [c['nome'] for c in cidades]
                    city_map.update({c['nome']: c['id'] for c in cidades})
                    city_combobox['values'] = city_names
                    current_city = get_config_value("city_name", "")
                    if current_city in city_names:
                        city_combobox.set(current_city)
            except Exception:
                # Silenciosamente ignora erros na carga inicial
                pass
        
        # Seleção de Escola
        school_frame = ttk.LabelFrame(win, text="Seleção de Escola", padding="10")
        school_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(school_frame, text="Buscar Escola:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        school_search_entry = ttk.Entry(school_frame, width=30)
        school_search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_school_button = ttk.Button(school_frame, text="Buscar Escola", state="disabled")
        search_school_button.grid(row=0, column=2, padx=5, pady=5)
        # Listbox de resultados limpa e expansível
        school_frame.rowconfigure(1, weight=1)
        school_frame.columnconfigure(0, weight=1)
        school_frame.columnconfigure(1, weight=1)
        school_listbox = tk.Listbox(school_frame)
        school_listbox.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        scrollbar = ttk.Scrollbar(school_frame, orient="vertical", command=school_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky='ns', padx=5, pady=5)
        school_listbox.config(yscrollcommand=scrollbar.set)
        # Botão de seleção (não persiste ainda)
        link_school_button = ttk.Button(school_frame, text="Selecionar", state="disabled")
        link_school_button.grid(row=2, column=2, sticky='e', padx=5, pady=5)
        # Label de confirmação da escola selecionada (persistida)
        selected_label = ttk.Label(school_frame, text=f"Selecionada: {get_config_value('school_name','---')}")
        selected_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        # Habilita busca se já há cidade selecionada e ao escolher uma cidade
        if city_combobox.get():
            search_school_button.config(state="normal")
        # Habilita botão de busca ao selecionar qualquer nova cidade
        city_combobox.bind("<<ComboboxSelected>>", lambda e: search_school_button.config(state="normal"))

        def on_search_school():
            idcidade = city_map.get(city_combobox.get())
            if not idcidade:
                messagebox.showerror("Erro", "Selecione uma cidade válida primeiro.")
                return
            try:
                escolas = buscar_escolas_cidade(idcidade, school_search_entry.get().strip())
                school_listbox.delete(0, tk.END)
                school_map.clear()
                for e in escolas:
                    text = e['nome']
                    school_listbox.insert(tk.END, text)
                    school_map[text] = e
                link_school_button.config(state="normal")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar escolas: {e}")

        search_school_button.config(command=on_search_school)

        def on_select_school():
            sel = school_listbox.curselection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma escola.")
                return
            text = school_listbox.get(sel[0])
            e = school_map.get(text)
            # Atualiza label de confirmação e guarda na variável
            selected_label.config(text=f"Selecionada: {e['nome']}")
            selected_school.clear()
            selected_school.update(e)

        link_school_button.config(command=on_select_school)

        def on_save_close():
            # Persiste configuração de API
            set_config_value("api_url", api_url_entry.get().strip())
            set_config_value("login", login_entry.get().strip())
            set_config_value("password", password_entry.get().strip())
            # Persiste cidade e escola selecionadas
            if city_combobox.get():
                set_config_value("city_id", str(city_map[city_combobox.get()]))
                set_config_value("city_name", city_combobox.get())
            if selected_school:
                set_config_value("school_id", str(selected_school['id']))
                set_config_value("school_name", selected_school['nome'])
            win.destroy()

        save_button = ttk.Button(win, text="Salvar e Sair", command=on_save_close)
        save_button.pack(pady=10)

    def sync_with_api(self):
        """Inicia sincronização completa (pull+push) via API e atualiza o status."""
        self.sync_date.config(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Iniciando sincronização...")
        import threading
        def run_sync():
            try:
                # Obtém o dispositivo conectado no toplevel
                toplevel = self.winfo_toplevel()
                device = getattr(toplevel, 'device', None)
                if not device:
                    raise Exception('Dispositivo não conectado')
                from core.sync import sync_full
                sync_full(device)
                # Função para atualizar status e listas na UI
                def on_success():
                    self.sync_date.config(text=f"Sincronizado com sucesso em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                    # Atualiza informações do dispositivo e listas na janela principal
                    if hasattr(toplevel, 'refresh_device_info'):
                        toplevel.refresh_device_info()
                    # Atualiza listas na janela principal
                    if hasattr(toplevel, 'refresh_user_list'):
                        toplevel.refresh_user_list()
                    if hasattr(toplevel, 'refresh_log_list'):
                        toplevel.refresh_log_list()
                # Após sucesso, atualiza status com data/hora
                self.after(0, lambda: self.sync_date.config(text=f"Sincronizado com sucesso em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}") or on_success())
            except Exception as e:
                self.after(0, lambda ex=e: self.sync_date.config(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Erro: {ex}"))
        threading.Thread(target=run_sync, daemon=True).start()

    def export_data(self):
        """Exporta todos os dados do banco para arquivos CSV e compacta em um arquivo ZIP."""
        try:
            # Solicita ao usuário o local para salvar o arquivo ZIP
            filename = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("Arquivo ZIP", "*.zip")],
                initialfile=f"exportacao_dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )
            
            if not filename:  # Usuário cancelou a operação
                return
                
            # Cria um diretório temporário para os arquivos CSV
            temp_dir = os.path.join(os.path.dirname(filename), "temp_export")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Obtém conexão com o banco
            conn = get_connection()
            cursor = conn.cursor()
            
            # Lista de tabelas para exportar
            tables = [
                ("usuarios", "SELECT * FROM usuarios"),
                ("dispositivos", "SELECT * FROM dispositivos"),
                ("registros", "SELECT * FROM logs"),
                ("eventos", "SELECT * FROM eventos"),
                ("config", "SELECT * FROM config"),
                ("api_logs", "SELECT * FROM api_logs")
            ]
            
            # Exporta cada tabela para um arquivo CSV
            for table_name, query in tables:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    csv_file = os.path.join(temp_dir, f"{table_name}.csv")
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f, delimiter=';')
                        # Escreve o cabeçalho
                        writer.writerow([description[0] for description in cursor.description])
                        # Escreve os dados
                        writer.writerows(rows)
            
            conn.close()
            
            # Cria o arquivo ZIP com os CSVs
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(temp_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(temp_dir, file)
                        zipf.write(file_path, file)
            
            # Remove o diretório temporário
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
            # Tenta limpar o diretório temporário em caso de erro
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)

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