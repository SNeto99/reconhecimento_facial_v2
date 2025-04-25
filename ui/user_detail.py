# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from database import get_event_map

class UserDetailForm(tk.Toplevel):
    def __init__(self, parent, user_info, logs, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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
        # Obtém o mapeamento de códigos para nomes
        event_map = get_event_map()
        from datetime import datetime
        # Converte timestamps e ordena do mais recente ao mais antigo
        logs_converted = []
        for log in logs:
            ts = log['timestamp']
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except:
                dt = None
            logs_converted.append({"dt": dt, "status": log["status"], "original_ts": ts})
        logs_sorted = sorted(logs_converted, key=lambda x: x["dt"] or datetime.min, reverse=True)
        for entry in logs_sorted:
            dt = entry["dt"]
            ts_display = dt.strftime("%d/%m/%Y") if dt else entry["original_ts"]
            # Converte status para nome de evento
            status = entry["status"]
            try:
                code = int(status)
            except:
                code = status
            status_name = event_map.get(code, status)
            log_tree.insert("", "end", values=(ts_display, status_name))
        # Botão de fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=self.destroy)
        close_btn.pack(pady=5) 