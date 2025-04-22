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
        
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ip_label = ttk.Label(frame, text="IP do Dispositivo:")
        ip_label.pack(pady=(10,5))
        self.ip_entry = ttk.Entry(frame)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "192.168.50.201")
        
        connect_button = ttk.Button(frame, text="Conectar", command=self.connect_device)
        connect_button.pack(pady=(5,10))

    def connect_device(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Erro", "Por favor, insira o IP do dispositivo.")
            return
        
        device = FaceDevice(ip)
        device.set_debug_callback(lambda msg: print(msg))
        self.update()
        
        if device.connect():
            messagebox.showinfo("Sucesso", "Dispositivo conectado com sucesso!")
            self.destroy()
            main_window = MainWindow(device=device)
            main_window.mainloop()
        else:
            messagebox.showerror("Erro", "Não foi possível conectar ao dispositivo.") 