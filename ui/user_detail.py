# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from database import get_event_map

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
        # Filtro de data para logs
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Data Início (DD/MM/YYYY):").pack(side=tk.LEFT, padx=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="Data Fim (DD/MM/YYYY):").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
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
            # Parse intervalo de datas
            start_str = self.start_date_entry.get().strip()
            end_str = self.end_date_entry.get().strip()
            start_date = None
            end_date = None
            if start_str:
                try:
                    start_date = datetime.strptime(start_str, "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Erro", "Formato de Data Início inválido. Use DD/MM/YYYY.")
                    return
            if end_str:
                try:
                    end_date = datetime.strptime(end_str, "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Erro", "Formato de Data Fim inválido. Use DD/MM/YYYY.")
                    return
            event_map = get_event_map()
            # Insere somente logs dentro do intervalo
            for log in self.all_logs:
                ts = log.get('timestamp')
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
                d = dt.date()
                if (start_date and d < start_date) or (end_date and d > end_date):
                    continue
                status = log.get('status')
                try:
                    code = int(status)
                except:
                    code = status
                name = event_map.get(code, status)
                self.log_tree.insert("", "end", values=(dt.strftime("%d/%m/%Y"), name))
        # Botão para aplicar filtro
        filter_btn = ttk.Button(filter_frame, text="Filtrar", command=apply_filter)
        filter_btn.pack(side=tk.LEFT, padx=5)
        # Exibe logs inicialmente
        apply_filter()
        # Botão de fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=self.destroy)
        close_btn.pack(pady=5) 