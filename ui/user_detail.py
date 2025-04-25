# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from database import get_event_map
from tkcalendar import DateEntry
from datetime import date, timedelta

class UserDetailForm(tk.Toplevel):
    def __init__(self, parent, user_info, logs, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Armazena todos os logs para filtragem
        self.all_logs = logs
        self.title(f"Detalhes do Usuário {user_info.get('user_id')}")
        self.geometry("600x500")
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Seção de informações do usuário
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Usuário", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        fields = [
            ('ID do Dispositivo', user_info.get('user_id')),
            ('ID do Sistema', user_info.get('system_id')),
            ('Nome', user_info.get('name')),
            ('Nome API', user_info.get('api_name')),
            ('RA', user_info.get('ra')),
            ('Série', user_info.get('serie')),
            ('Turma', user_info.get('turma'))
        ]
        for i, (label_text, value) in enumerate(fields):
            ttk.Label(info_frame, text=f"{label_text}:").grid(row=i, column=0, sticky='e', padx=5, pady=2)
            ttk.Label(info_frame, text=value or '').grid(row=i, column=1, sticky='w', padx=5, pady=2)
        # Filtro de data com seletor de calendário
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Data Início:").pack(side=tk.LEFT, padx=5)
        # Inicializa com data 30 dias atrás
        today = date.today()
        self.start_date_entry = DateEntry(filter_frame, date_pattern='dd/MM/yyyy', width=12)
        self.start_date_entry.set_date(today - timedelta(days=30))
        self.start_date_entry.pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="Data Fim:").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = DateEntry(filter_frame, date_pattern='dd/MM/yyyy', width=12)
        self.end_date_entry.set_date(today)
        self.end_date_entry.pack(side=tk.LEFT)
        # Seção de logs
        log_frame = ttk.LabelFrame(main_frame, text="Registros de Acesso", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        columns = ("Timestamp", "Status")
        log_tree = ttk.Treeview(log_frame, columns=columns, show='headings')
        for col in columns:
            log_tree.heading(col, text=col)
            log_tree.column(col, anchor='center', width=150)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=log_tree.yview)
        log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_tree.pack(fill=tk.BOTH, expand=True)
        # Guarda referência à árvore de logs
        self.log_tree = log_tree
        # Função para filtrar e exibir logs
        def apply_filter():
            # Limpa árvore de logs
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            from datetime import datetime
            from tkinter import messagebox
            # Obtém datas do DateEntry
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
            event_map = get_event_map()
            # Insere somente logs dentro do intervalo
            filtered_logs = []
            for log in self.all_logs:
                ts = log.get('timestamp')
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
                d = dt.date()
                # Filtra logs dentro do intervalo de datas
                if not (start_date <= d <= end_date):
                    continue
                filtered_logs.append({"dt": dt, "status": log.get("status")})
            # Ordena do mais recente para o mais antigo
            filtered_logs = sorted(filtered_logs, key=lambda x: x["dt"], reverse=True)
            for entry in filtered_logs:
                dt = entry["dt"]
                status = entry["status"]
                try:
                    code = int(status)
                except:
                    code = status
                name = event_map.get(code, status)
                self.log_tree.insert("", "end", values=(dt.strftime("%d/%m/%Y"), name))
        # Botões para filtrar e limpar
        filter_btn = ttk.Button(filter_frame, text="Filtrar", command=apply_filter)
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        def clear_filter():
            # Reset para valores padrão (30 dias atrás até hoje)
            today = date.today()
            self.start_date_entry.set_date(today - timedelta(days=30))
            self.end_date_entry.set_date(today)
            apply_filter()
            
        clear_btn = ttk.Button(filter_frame, text="Limpar Filtro", command=clear_filter)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Exibe logs inicialmente
        apply_filter()
        # Botão de fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=self.destroy)
        close_btn.pack(pady=5) 