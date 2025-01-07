# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
import tkinter.messagebox as messagebox

class FaceCaptureWindow(tk.Toplevel):
    def __init__(self, parent, device, user_id):
        super().__init__(parent)
        self.title("Captura Facial")
        self.geometry("400x200")
        
        self.device = device
        self.user_id = user_id
        self.check_timer = None
        self.success = False
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.status_label = ttk.Label(
            main_frame, 
            text="Iniciando captura facial...",
            wraplength=350
        )
        self.status_label.pack(pady=20)
        
        # Progresso
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        
        # Botão cancelar
        self.cancel_button = ttk.Button(
            main_frame, 
            text="Cancelar", 
            command=self.cancel_capture
        )
        self.cancel_button.pack(pady=10)
        
        # Inicia captura após construir a interface
        self.after(100, self.start_capture)
        
    def start_capture(self):
        try:
            print(f"\n[FACE] Iniciando processo de captura para usuário {self.user_id}")
            self.progress.start()
            self.status_label.config(text="Iniciando módulo facial...")
            
            # Tenta iniciar o cadastro facial
            success = self.device.face_capture.start_enrollment(self.user_id)
            
            if not success:
                raise Exception("Falha ao iniciar cadastro facial")
                
            print("[FACE] Captura iniciada com sucesso")
            self.status_label.config(text="Posicione seu rosto na frente do dispositivo")
            self.check_timer = self.after(1000, self.check_status)
            
        except Exception as e:
            print(f"[FACE] Erro durante captura: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}")
            self.progress.stop()
            messagebox.showerror("Erro", str(e))
            # Não fecha a janela automaticamente em caso de erro
            
    def check_status(self):
        try:
            status = self.device.face_capture.check_enrollment_status()
            
            if status:
                print("[FACE] Captura concluída com sucesso!")
                self.progress.stop()
                self.success = True
                self.status_label.config(text="Cadastro realizado com sucesso!")
                messagebox.showinfo("Sucesso", "Cadastro facial realizado com sucesso!")
                self.destroy()
            else:
                self.check_timer = self.after(1000, self.check_status)
                
        except Exception as e:
            print(f"[FACE] Erro ao verificar status: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}")
            self.progress.stop()
            messagebox.showerror("Erro", str(e))
            
    def cancel_capture(self):
        """Cancela a captura facial"""
        try:
            print("[FACE] Cancelando captura facial...")
            if self.check_timer:
                self.after_cancel(self.check_timer)
                
            # Cancela o cadastro no dispositivo
            self.device.face_capture.cancel_enrollment()
            
            print("[FACE] Captura cancelada com sucesso")
            self.destroy()
            
        except Exception as e:
            print(f"[FACE] Erro ao cancelar captura: {str(e)}")
            self.destroy() 