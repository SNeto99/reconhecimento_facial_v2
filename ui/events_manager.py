# Novo arquivo: ui/events_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# Define o caminho do banco de dados
DB_FILENAME = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local_data.db')

class EventsManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciar Eventos")
        self.geometry("500x350")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.load_events()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("codigo", "nome"), show="headings")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Nome")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        edit_btn = ttk.Button(btn_frame, text="Editar", command=self.edit_event)
        edit_btn.pack(side=tk.LEFT, padx=5)
        del_btn = ttk.Button(btn_frame, text="Remover", command=self.delete_event)
        del_btn.pack(side=tk.LEFT, padx=5)

    def get_connection(self):
        return sqlite3.connect(DB_FILENAME)

    def load_events(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT l.status as codigo, COALESCE(e.nome, '') as nome FROM logs l LEFT JOIN eventos e ON l.status = CAST(e.codigo as TEXT) ORDER BY CAST(l.status AS INTEGER)")
        for row in cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
        conn.close()

    def edit_event(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Erro", "Selecione um evento para editar")
            return
        codigo, nome = self.tree.item(selected, 'values')
        self.event_editor(codigo, nome)

    def delete_event(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Erro", "Selecione um evento para remover")
            return
        codigo, _ = self.tree.item(selected, 'values')
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eventos WHERE codigo = ?", (codigo,))
        conn.commit()
        conn.close()
        self.load_events()

    def event_editor(self, codigo=None, nome=""):
        editor = tk.Toplevel(self)
        editor.title("Editar Evento" if codigo else "Adicionar Evento")
        editor.geometry("300x200")
        editor.transient(self)
        editor.grab_set()

        ttk.Label(editor, text="Código:").pack(pady=5)
        codigo_entry = ttk.Entry(editor, justify="center")
        codigo_entry.pack(pady=5)
        if codigo:
            codigo_entry.insert(0, codigo)
            codigo_entry.config(state='disabled')
        
        ttk.Label(editor, text="Nome:").pack(pady=5)
        nome_entry = ttk.Entry(editor, justify="center")
        nome_entry.pack(pady=5)
        nome_entry.insert(0, nome)
        
        def save():
            new_nome = nome_entry.get().strip()
            if not new_nome:
                messagebox.showerror("Erro", "Nome não pode ser vazio")
                return
            conn = self.get_connection()
            cursor = conn.cursor()
            if codigo:
                cursor.execute("REPLACE INTO eventos (codigo, nome) VALUES (?, ?)", (codigo, new_nome))
            else:
                try:
                    new_codigo = int(codigo_entry.get().strip())
                except ValueError:
                    messagebox.showerror("Erro", "Código deve ser um número inteiro")
                    return
                cursor.execute("INSERT INTO eventos (codigo, nome) VALUES (?, ?)", (new_codigo, new_nome))
            conn.commit()
            conn.close()
            editor.destroy()
            self.load_events()
        
        save_btn = ttk.Button(editor, text="Salvar", command=save)
        save_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    EventsManager(root)
    root.mainloop() 