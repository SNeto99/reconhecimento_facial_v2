# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .user_form import UserForm
from core.face_device import FaceDevice
import time
from ui.settings_tab import SettingsTab
from .user_detail import UserDetailForm
from tkcalendar import DateEntry
from database import get_config_value
from datetime import datetime

class MainWindow(tk.Tk):
    def __init__(self, device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Interface do Dispositivo ZKTeco")
        
        # Configura o tamanho fixo da janela
        self.geometry("1200x800")
        
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
        
        # Inicia agendamento de sincronização automática
        self.start_scheduler()
        
    def create_device_tab(self):
        frame = ttk.Frame(self.device_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome da escola em negrito no topo da página
        escola = get_config_value("school_name", "---")
        escola_label = ttk.Label(frame, text=escola, font=('Helvetica', 12, 'bold'))
        escola_label.pack(pady=(0,10))
        
        # Estatísticas Gerais para o administrador
        stats_frame = ttk.LabelFrame(frame, text="Estatísticas Gerais", padding="10")
        stats_frame.pack(fill=tk.X, padx=20, pady=(0,10))
        # Carrega dados de usuários e logs
        from database import get_connection, get_unsynced_logs
        conn_stats = get_connection()
        cur_stats = conn_stats.cursor()
        cur_stats.execute("SELECT COUNT(*) FROM usuarios")
        total_users = cur_stats.fetchone()[0]
        cur_stats.execute("SELECT COUNT(*) FROM logs")
        total_logs = cur_stats.fetchone()[0]
        conn_stats.close()
        unsynced = len(get_unsynced_logs())
        # Data da última sincronização (formatar para d/m/Y)
        last_sync_raw = get_config_value("last_sync", "Nunca")
        try:
            last_sync = datetime.strptime(last_sync_raw, "%Y-%m-%d %H:%M:%S").strftime('%d/%m/%Y %H:%M:%S')
        except:
            last_sync = last_sync_raw
        sync_interval = get_config_value("sync_interval", "Não definido")
        # Status de conexão do dispositivo com ícone colorido
        status_text = "Conectado" if self.device else "Desconectado"
        icon_color = "green" if self.device else "red"
        # Status do dispositivo com ícone e texto colados
        status_container = ttk.Frame(stats_frame)
        status_container.grid(row=0, column=0, sticky="w", padx=(5,0), pady=2, columnspan=2)
        ttk.Label(status_container, text="Status do dispositivo:").pack(side="left")
        tk.Label(status_container, text="●", fg=icon_color).pack(side="left", padx=(2,0))
        ttk.Label(status_container, text=status_text).pack(side="left", padx=(2,0))
        # Reordenação dos indicadores
        # 1: Última sincronização
        ttk.Label(stats_frame, text=f"Última sincronização: {last_sync}").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        # 2: Intervalo entre sincronizações
        ttk.Label(stats_frame, text=f"Intervalo entre sincronizações: {sync_interval} minutos").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        # 3: Espaço em branco (pula linha)
        ttk.Label(stats_frame, text="").grid(row=3, column=0, pady=2)
        # 4: Total de usuários
        ttk.Label(stats_frame, text=f"Total de usuários: {total_users}").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        # 5: Total de Registros
        ttk.Label(stats_frame, text=f"Total de Registros: {total_logs}").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        # 6: Registros não sincronizados
        ttk.Label(stats_frame, text=f"Registros não sincronizados: {unsynced}").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        # 7: Registros hoje
        conn_today = get_connection()
        cur_today = conn_today.cursor()
        cur_today.execute("SELECT COUNT(*) FROM logs WHERE date(timestamp)=date('now','localtime')")
        today_count = cur_today.fetchone()[0]
        conn_today.close()
        ttk.Label(stats_frame, text=f"Registros hoje: {today_count}").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        # Últimos 10 registros de acesso (JOIN para trazer nome e evento)
        last_frame = ttk.LabelFrame(frame, text="Últimos Registros", padding="10")
        last_frame.pack(fill=tk.X, padx=20, pady=(0,10))
        from database import get_connection
        conn_last = get_connection()
        cur_last = conn_last.cursor()
        cur_last.execute(
            """SELECT l.timestamp,
                              COALESCE(u.name, l.user_id) AS user_name,
                              u.ra AS ra,
                              u.serie AS serie,
                              u.turma AS turma,
                              COALESCE(e.nome, l.status) AS event_name
               FROM logs l
               LEFT JOIN usuarios u ON u.device_user_id = l.user_id
               LEFT JOIN eventos e ON e.codigo = l.status
               ORDER BY l.timestamp DESC
               LIMIT 5"""
        )
        rows_last = cur_last.fetchall()
        conn_last.close()
        # Cria Treeview para mostrar registros (inclui RA e Série-Turma)
        cols = ("Data", "Usuário", "RA", "Série-Turma", "Evento")
        tree = ttk.Treeview(last_frame, columns=cols, show="headings", height=5)
        for col in cols:
            tree.heading(col, text=col)
            # Centraliza RA, Série-Turma e Evento; restante alinhado à esquerda
            if col in ("RA", "Série-Turma", "Evento"):
                tree.column(col, anchor="center", stretch=True)
            else:
                tree.column(col, anchor="w", stretch=True)
        tree.pack(fill=tk.BOTH, expand=True)
        # Popula os registros
        for ts, user_name, ra, serie, turma, event_name in rows_last:
            try:
                from datetime import datetime
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                ts_disp = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                ts_disp = ts
            # Combina série e turma
            serie_turma = f"{serie}-{turma}" if serie or turma else ""
            tree.insert("", "end", values=(ts_disp, user_name, ra, serie_turma, event_name))
        
        # Botão para atualizar toda a página ao final da aba
        def _refresh_page():
            # Sincroniza logs do dispositivo para o banco antes de atualizar a view
            if self.device:
                from database import add_device, synchronize_logs
                device_info = self.device.get_device_info()
                device_id = add_device(device_info.get('mac'))
                logs = self.device.get_attendance_logs()
                for log in logs:
                    log['device_id'] = device_id
                synchronize_logs(logs)
            # Limpa todo o conteúdo da aba Dispositivo
            for w in self.device_tab.winfo_children():
                w.destroy()
            # Reconstrói a aba completamente
            self.create_device_tab()
            # Recarrega as abas de Usuários e Logs
            try:
                self.refresh_user_list()
                self.refresh_log_list()
            except:
                pass
        refresh_page_btn = ttk.Button(frame, text="Atualizar", command=_refresh_page)
        refresh_page_btn.pack(pady=(10,10))
        
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
        self.user_list = ttk.Treeview(list_frame, columns=("ID","Nome","RA","Série-Turma","Editar","Apagar"), show="headings", yscrollcommand=scrollbar.set)
        self.user_list.heading("ID", text="ID")
        self.user_list.heading("Nome", text="Nome")
        self.user_list.heading("RA", text="RA")
        self.user_list.heading("Série-Turma", text="Série-Turma")
        self.user_list.heading("Editar", text="")
        self.user_list.heading("Apagar", text="")
        
        # Configura larguras das colunas
        self.user_list.column("ID", width=60)
        self.user_list.column("Nome", width=150)
        self.user_list.column("RA", width=80, anchor="center")
        self.user_list.column("Série-Turma", width=120, anchor="center")
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
            
            if column == "#2":  # Coluna Nome
                user_id = self.user_list.item(item)['values'][0]
                self.open_user_detail(user_id)
            elif column == "#5":  # Coluna Editar
                user_id = self.user_list.item(item)['values'][0]
                self.edit_user(user_id)
            elif column == "#6":  # Coluna Apagar
                user_id = self.user_list.item(item)['values'][0]
                self.delete_user(user_id)

    def edit_user(self, user_id):
        """Abre formulário para editar usuário"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        try:
            # Obtém metadados do usuário no banco
            from database import add_device, get_connection
            device_info = self.device.get_device_info()
            current_device_id = add_device(device_info.get("mac"))
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT device_user_id, system_id, name, api_name, ra, serie, turma "
                "FROM usuarios WHERE device_user_id = ? AND device_id = ? AND active = 1",
                (str(user_id), current_device_id)
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                messagebox.showerror("Erro", "Usuário não encontrado no banco de dados.")
                return
            # Monta dicionário de dados para o formulário
            user = {
                'user_id': row[0],
                'system_id': row[1],
                'name': row[2],
                'api_name': row[3],
                'ra': row[4],
                'serie': row[5],
                'turma': row[6]
            }
            form = UserForm(self, self.device, user=user)
            self.wait_window(form)
            self.refresh_user_list()
        except Exception:
            self.refresh_user_list()

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
        
        # Filtro de data com seletor de calendário
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Data Início:").pack(side=tk.LEFT, padx=5)
        # Inicializa data com 30 dias atrás
        from datetime import date, timedelta
        today = date.today()
        self.start_date_entry = DateEntry(filter_frame, date_pattern='dd/MM/yyyy', width=12)
        self.start_date_entry.set_date(today - timedelta(days=30))
        self.start_date_entry.pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="Data Fim:").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = DateEntry(filter_frame, date_pattern='dd/MM/yyyy', width=12)
        self.end_date_entry.set_date(today)
        self.end_date_entry.pack(side=tk.LEFT)
        filter_btn = ttk.Button(filter_frame, text="Filtrar", command=self.refresh_log_list)
        filter_btn.pack(side=tk.LEFT, padx=5)
        clear_filter_btn = ttk.Button(filter_frame, text="Limpar Filtro", command=self.clear_date_filter)
        clear_filter_btn.pack(side=tk.LEFT, padx=5)
        
        # Rótulo para exibir a contagem de logs
        self.log_count_label = ttk.Label(frame, text="Total de logs: 0")
        self.log_count_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Lista de logs
        list_frame = ttk.LabelFrame(frame, text="Registros de Acesso", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Adiciona scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_list = ttk.Treeview(list_frame, columns=("Data","Usuário","Evento"), show="headings", yscrollcommand=scrollbar.set)
        self.log_list.heading("Data", text="Data/Hora")
        self.log_list.heading("Usuário", text="Usuário")
        self.log_list.heading("Evento", text="Evento")
        
        self.log_list.column("Data", width=150)
        self.log_list.column("Usuário", width=150)
        self.log_list.column("Evento", width=150)
        
        self.log_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_list.yview)
        
    def open_user_form(self):
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
            
        form = UserForm(self, self.device)
        # Aguarda o formulário fechar e então atualiza a lista automaticamente
        self.wait_window(form)
        self.refresh_user_list()
        
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
                ra = u[5] or ""
                serie_turma = f"{u[6]} - {u[7]}" if (u[6] or u[7]) else ""
                self.user_list.insert("", "end",
                    values=(u[1], u[3], ra, serie_turma, "̲E̲d̲i̲t̲a̲r̲", "̲E̲x̲c̲l̲u̲i̲r̲")
                )
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
            # Converte timestamps de string para datetime
            for log in logs:
                if isinstance(log['timestamp'], str):
                    try:
                        log['timestamp'] = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
                    except:
                        pass
            logs_sorted = sorted(logs, key=lambda log: log['timestamp'], reverse=True)
            # Filtro de datas
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
            if start_date and end_date:
                # Aplica filtro de intervalo nas datas
                filtered_logs = [log for log in logs_sorted if start_date <= log['timestamp'].date() <= end_date]
            else:
                filtered_logs = logs_sorted
            self.log_count_label.config(text=f"Total de logs: {len(filtered_logs)}")
            for log in filtered_logs:
                try:
                    status_code = int(log['status'])
                except:
                    status_code = log['status']
                student_name = user_mapping.get(log['user_id'], log['user_id'])
                event_name = event_map.get(status_code, log['status'])
                # Exibe data/hora no formato DD/MM/YYYY HH:MM:SS; trata strings caso não convertidos
                ts = log['timestamp']
                if hasattr(ts, 'strftime'):
                    ts_display = ts.strftime('%d/%m/%Y %H:%M:%S')
                else:
                    try:
                        dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                        ts_display = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        ts_display = ts
                self.log_list.insert('', 'end', values=(
                    ts_display,
                    student_name,
                    event_name
                ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista de logs: {str(e)}")
        
    def on_mouse_move(self, event):
        """Altera o cursor quando passa sobre os botões de ação"""
        region = self.user_list.identify_region(event.x, event.y)
        column = self.user_list.identify_column(event.x)
        
        if region == "cell" and column in ("#5", "#6"):  # Colunas de Editar e Apagar
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
                ra = u[5] or ""
                serie_turma = f"{u[6]}-{u[7]}" if (u[6] or u[7]) else ""
                self.user_list.insert("", "end",
                    values=(u[1], u[3], ra, serie_turma, "̲E̲d̲i̲t̲a̲r̲", "̲E̲x̲c̲l̲u̲i̲r̲")
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários locais: {str(e)}")

    def load_local_logs(self):
        """Carrega logs do banco de dados local e atualiza a lista"""
        try:
            from database import get_all_logs, get_all_users, get_event_map
            from datetime import datetime
            local_users = get_all_users()
            user_mapping = {u[1]: u[3] for u in local_users}
            event_map = get_event_map()
            logs = get_all_logs()
            # Converte timestamps para datetime
            for log in logs:
                if not isinstance(log['timestamp'], datetime):
                    log['timestamp'] = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            logs_sorted = sorted(logs, key=lambda log: log['timestamp'], reverse=True)
            # Filtro de datas
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
            if start_date and end_date:
                # Aplica filtro de intervalo nas datas
                filtered = [log for log in logs_sorted if start_date <= log['timestamp'].date() <= end_date]
            else:
                filtered = logs_sorted
            self.log_count_label.config(text=f"Total de logs: {len(filtered)}")
            for log in filtered:
                try:
                    status_code = int(log['status'])
                except:
                    status_code = log['status']
                student_name = user_mapping.get(log['user_id'], log['user_id'])
                event_name = event_map.get(status_code, log['status'])
                # Exibe data/hora no formato DD/MM/YYYY HH:MM:SS
                ts_display = log['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                self.log_list.insert('', 'end', values=(ts_display, student_name, event_name))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar logs locais: {str(e)}")

    def open_user_detail(self, user_id):
        """Abre janela de detalhes do usuário"""
        if not self.device:
            messagebox.showerror("Erro", "Por favor, conecte-se ao dispositivo primeiro.")
            return
        try:
            from database import add_device, get_user_info, get_logs_by_user
            device_info = self.device.get_device_info()
            current_device_id = add_device(device_info.get("mac"))
            user_info = get_user_info(user_id, current_device_id)
            logs = get_logs_by_user(user_id, current_device_id)
            if not user_info:
                messagebox.showerror("Erro", "Usuário não encontrado no banco.")
                return
            detail = UserDetailForm(self, user_info, logs)
            self.wait_window(detail)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir detalhes: {str(e)}")

    def clear_date_filter(self):
        """Limpa os filtros de data e atualiza a lista de logs"""
        from datetime import datetime, date, timedelta
        today = date.today()
        # Define valores padrão: 30 dias atrás até hoje
        self.start_date_entry.set_date(today - timedelta(days=30))
        self.end_date_entry.set_date(today)
        # Atualiza sem filtro
        self.refresh_log_list()

    def start_scheduler(self):
        """Agenda sincronização automática a cada intervalo configurado (minutos)."""
        intervalo = int(get_config_value("sync_interval", "10"))
        # Converter para milissegundos
        self.after(intervalo * 60 * 1000, self.auto_sync)

    def auto_sync(self):
        """Executa sincronização automática e reagenda."""
        self.add_log(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Iniciando sincronização automática...")
        try:
            # Usa sync_full para pull do dispositivo e push ao cloud
            from core.sync import sync_full
            if not self.device:
                raise Exception("Dispositivo não conectado")
            sync_full(self.device)
            self.add_log(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Sincronização automática concluída com sucesso.")
            # Atualiza interface
            try:
                self.refresh_device_info()
                self.refresh_user_list()
                self.refresh_log_list()
            except Exception:
                pass
        except Exception as e:
            self.add_log(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Erro na sincronização automática: {e}")
        finally:
            self.start_scheduler()