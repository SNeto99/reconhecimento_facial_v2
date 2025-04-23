# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from core.face_device import FaceDevice
from ui.main_window import MainWindow

class ConnectionForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conectar Dispositivo")
        self.geometry("300x150")
        self.resizable(False, False)
        
        self.build_ui()

    def build_ui(self):
        # Limpa todos os widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ip_label = ttk.Label(frame, text="IP do Dispositivo:")
        ip_label.pack(pady=(10,5))
        self.ip_entry = ttk.Entry(frame)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "192.168.50.201")
        
        connect_button = ttk.Button(frame, text="Conectar", command=self.connect_device)
        connect_button.pack(pady=(5,10))
        
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
    def connect_device(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Erro", "Por favor, insira o IP do dispositivo.")
            return
        
        device = FaceDevice(ip)
        device.set_debug_callback(lambda msg: print(msg))
        self.update()
        
        # Exibe indicador de loading
        for widget in self.winfo_children():
            widget.destroy()
        loading_frame = ttk.Frame(self, padding="10")
        loading_frame.pack(fill=tk.BOTH, expand=True)
        loading_label = ttk.Label(loading_frame, text="Conectando...")
        loading_label.pack(pady=20)
        self.center_window()
        
        self.connection_finished = False
        
        import threading
        self.connection_thread = threading.Thread(target=self.connection_thread_func, args=(device,), daemon=True)
        self.connection_thread.start()
        
        # Agenda verificação de timeout após 5 segundos
        self.after(5000, self.check_connection_timeout)
        
    def connection_thread_func(self, device):
        result = device.connect()
        self.after(0, lambda: self.on_connection_result(result, device))
        
    def on_connection_result(self, result, device):
        self.connection_finished = True
        if result:
            self.destroy()
            main_window = MainWindow(device=device)
            main_window.mainloop()
        else:
            self.show_failure_options()
            
    def check_connection_timeout(self):
        if not self.connection_finished:
            self.show_failure_options()
            
    def show_failure_options(self):
        # Limpa os widgets atuais
        for widget in self.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        error_label = ttk.Label(frame, text="Não foi possível conectar ao dispositivo.")
        error_label.pack(pady=(10,5))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        
        retry_btn = ttk.Button(btn_frame, text="Tentar novamente", command=self.reset_form)
        retry_btn.pack(side=tk.LEFT, padx=5)
        
        continue_btn = ttk.Button(btn_frame, text="Continuar sem conectar", command=self.continue_without_connection)
        continue_btn.pack(side=tk.LEFT, padx=5)
        
        self.center_window()
        
    def reset_form(self):
        self.build_ui()
        
    def continue_without_connection(self):
        self.destroy()
        main_window = MainWindow(device=None)
        main_window.disable_device_controls()  # método que desabilita botões que interagem com o dispositivo
        main_window.mainloop() 