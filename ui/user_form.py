# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import io
from .face_capture_window import FaceCaptureWindow
import time
from struct import pack
from zk import const
import base64
import json

class UserForm(tk.Toplevel):
    def __init__(self, parent, device, user=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("Editar Usuário" if user else "Cadastro de Usuário")
        self.geometry("400x700")  # Aumentei a altura para acomodar a foto
        self.device = device
        self.user = user
        self.parent = parent
        self.cadastro_realizado = False  # Flag para controlar se o usuário foi cadastrado
        self.photo_data = None  # Armazena os bytes da foto
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para a foto
        self.photo_frame = ttk.LabelFrame(main_frame, text="Foto do Usuário", padding="10")
        self.photo_frame.pack(fill=tk.X, pady=10)
        
        # Label para exibir a foto
        self.photo_label = ttk.Label(self.photo_frame)
        self.photo_label.pack(pady=5)
        
        # Botão para selecionar foto
        self.photo_button = ttk.Button(self.photo_frame, text="Selecionar Foto", command=self.select_photo)
        self.photo_button.pack(pady=5)
        
        # Campos do formulário
        self.id_label = ttk.Label(main_frame, text="ID do Aluno:")
        self.id_label.pack(pady=5)
        self.id_entry = ttk.Entry(main_frame)
        self.id_entry.pack(pady=5)
        
        self.nome_label = ttk.Label(main_frame, text="Nome:")
        self.nome_label.pack(pady=5)
        self.nome_entry = ttk.Entry(main_frame)
        self.nome_entry.pack(pady=5)
        
        self.senha_label = ttk.Label(main_frame, text="Senha:")
        self.senha_label.pack(pady=5)
        self.senha_entry = ttk.Entry(main_frame, show="*")
        self.senha_entry.pack(pady=5)
        
        # Frame para os botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Se for edição, preenche os campos
        if self.user:
            self.id_entry.insert(0, self.user['user_id'])
            self.id_entry.config(state='disabled')  # ID não pode ser alterado
            self.nome_entry.insert(0, self.user['name'])
            if 'password' in self.user:
                self.senha_entry.insert(0, self.user['password'])
            
            self.cadastrar_button = ttk.Button(button_frame, text="Salvar Alterações", command=self.salvar_usuario)
            self.cadastrar_button.pack(side=tk.LEFT, padx=5)

            # Botão de captura facial para edição
            self.capture_button = ttk.Button(button_frame, text="Atualizar Face", 
                                           command=self.iniciar_captura_facial)
            self.capture_button.pack(side=tk.LEFT, padx=5)
            self.aluno_id = int(self.user['user_id'])
            self.cadastro_realizado = True
        else:
            self.cadastrar_button = ttk.Button(button_frame, text="Cadastrar Usuário", command=self.cadastrar_usuario)
            self.cadastrar_button.pack(side=tk.LEFT, padx=5)
            
            # Botão de captura facial (inicialmente desabilitado)
            self.capture_button = ttk.Button(button_frame, text="Iniciar Captura Facial", 
                                           command=self.iniciar_captura_facial, state='disabled')
            self.capture_button.pack(side=tk.LEFT, padx=5)
        
        self.cancelar_button = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        self.cancelar_button.pack(side=tk.LEFT, padx=5)
        
    def select_photo(self):
        """Permite selecionar uma foto do usuário"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Foto",
            filetypes=[("Imagens", "*.jpg *.jpeg *.JPG *.JPEG")]  # Adicionei suporte para JPG maiúsculo
        )
        
        if file_path:
            try:
                # Abre e redimensiona a imagem se necessário
                with Image.open(file_path) as img:
                    # Calcula a proporção para redimensionar mantendo o aspect ratio
                    width, height = img.size
                    if width > 720 or height > 1280:
                        ratio = min(720/width, 1280/height)
                        new_width = int(width * ratio)
                        new_height = int(height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Converte para RGB se necessário
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Salva em um buffer de memória
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=95)  # Aumentei a qualidade
                    self.photo_data = buffer.getvalue()
                    
                    # Redimensiona para exibição no formulário
                    display_size = (150, 150)
                    img.thumbnail(display_size)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Atualiza a label com a foto
                    self.photo_label.configure(image=photo)
                    self.photo_label.image = photo  # Mantém uma referência
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar a imagem: {str(e)}")
                
        # Traz a janela de volta ao foco
        self.lift()  # Traz a janela para frente
        self.focus_force()  # Força o foco para esta janela
        
    def upload_photo(self):
        """Faz upload da foto para o dispositivo"""
        if not self.photo_data:
            print("[FACE] Erro: Nenhuma foto selecionada")
            return False
            
        try:
            user_id = self.aluno_id if hasattr(self, 'aluno_id') else int(self.user['user_id'])
            print(f"[FACE] Iniciando upload de foto para usuário {user_id}")
            
            # Desabilita o dispositivo
            self.device.conn.disable_device()
            
            try:
                # Limpa o buffer
                self.device.conn.free_data()
                
                # Converte a foto para base64
                photo_base64 = base64.b64encode(self.photo_data).decode('utf-8')
                
                # Monta o JSON no formato esperado pelo dispositivo
                face_data = {
                    "userId": str(user_id),
                    "faceData": {
                        "data": photo_base64,
                        "type": "jpg",
                        "size": len(self.photo_data)
                    }
                }
                
                # Converte para string JSON
                json_data = json.dumps(face_data)
                print(f"[FACE] JSON preparado para envio - Tamanho: {len(json_data)} bytes")
                
                # Prepara o comando
                command_data = pack('<I', len(json_data))  # Tamanho do JSON
                command_data += json_data.encode('utf-8')  # JSON em bytes
                
                # Envia o comando ADD_FACE
                response = self.device.conn._send_command(const.CMD_ADD_FACE, command_data)
                if response and response.get('status'):
                    print("[FACE] Foto enviada com sucesso")
                    return True
                    
                print("[FACE] Falha ao enviar foto")
                return False
                
            finally:
                self.device.conn.free_data()
                
        except Exception as e:
            print(f"[FACE] Erro ao enviar foto: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao enviar foto: {str(e)}")
            return False
            
        finally:
            self.device.conn.enable_device()
            
    def cadastrar_usuario(self):
        try:
            id_aluno = self.id_entry.get()
            nome = self.nome_entry.get()
            senha = self.senha_entry.get()
            
            if not id_aluno or not nome:
                messagebox.showerror("Erro", "Por favor, preencha ID e Nome do aluno.")
                return
                
            try:
                id_aluno = int(id_aluno)
            except ValueError:
                messagebox.showerror("Erro", "O ID do aluno deve ser um número inteiro.")
                return
                
            # Desabilita o dispositivo antes de fazer alterações
            self.device.conn.disable_device()
            time.sleep(0.5)  # Aguarda o dispositivo ser desabilitado
            
            try:
                # Limpa o buffer antes de cadastrar
                self.device.conn.free_data()
                time.sleep(0.5)  # Aguarda a limpeza do buffer
                
                # Cadastra o usuário básico
                self.device.conn.set_user(
                    uid=id_aluno, 
                    name=nome, 
                    password=senha if senha else '',  # Envia string vazia se não tiver senha
                    user_id=str(id_aluno),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                self.aluno_id = id_aluno
                self.cadastro_realizado = True
                
                # Se tiver foto selecionada, faz o upload
                if hasattr(self, 'photo_data') and self.photo_data:
                    if self.upload_photo():
                        messagebox.showinfo("Sucesso", "Usuário e foto cadastrados com sucesso!")
                    else:
                        messagebox.showinfo("Sucesso Parcial", "Usuário cadastrado com sucesso, mas houve erro ao enviar a foto.")
                else:
                    messagebox.showinfo(
                        "Sucesso", 
                        "Usuário cadastrado com sucesso!\nDeseja iniciar a captura facial agora?"
                    )
                
                # Habilita captura facial
                self.capture_button.config(state='normal')
                
                # Desabilita campos
                self.id_entry.config(state='disabled')
                self.nome_entry.config(state='disabled')
                self.senha_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
                # Se não tiver foto, pergunta se quer iniciar captura facial
                if not hasattr(self, 'photo_data') and messagebox.askyesno("Captura Facial", "Deseja iniciar a captura facial agora?"):
                    self.iniciar_captura_facial()
                    
            finally:
                # Sempre reabilita o dispositivo
                time.sleep(0.5)  # Aguarda antes de reabilitar
                self.device.conn.enable_device()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(e)}")
            
    def salvar_usuario(self):
        """Salva as alterações do usuário"""
        try:
            nome = self.nome_entry.get()
            senha = self.senha_entry.get()
            
            if not nome:
                messagebox.showerror("Erro", "Por favor, preencha o Nome do aluno.")
                return
                
            # Desabilita o dispositivo antes de fazer alterações
            self.device.conn.disable_device()
            time.sleep(0.5)  # Aguarda o dispositivo ser desabilitado
            
            try:
                # Limpa o buffer antes de atualizar
                self.device.conn.free_data()
                time.sleep(0.5)  # Aguarda a limpeza do buffer
                
                # Atualiza o usuário
                self.device.conn.set_user(
                    uid=int(self.user['user_id']), 
                    name=nome, 
                    password=senha if senha else '',  # Envia string vazia se não tiver senha
                    user_id=str(self.user['user_id']),  # Garante que user_id seja string
                    privilege=0,  # Usuário comum
                    group_id='0',  # Grupo padrão
                    card=0  # Sem cartão
                )
                
                # Se tiver foto selecionada, faz o upload
                if hasattr(self, 'photo_data') and self.photo_data:
                    if self.upload_photo():
                        messagebox.showinfo("Sucesso", "Usuário e foto atualizados com sucesso!")
                    else:
                        messagebox.showinfo("Sucesso Parcial", "Usuário atualizado com sucesso, mas houve erro ao enviar a foto.")
                else:
                    messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                
                # Desabilita os campos e o botão de salvar após a atualização
                self.nome_entry.config(state='disabled')
                self.senha_entry.config(state='disabled')
                self.cadastrar_button.config(state='disabled')
                
                self.parent.refresh_user_list()  # Atualiza a lista
                    
            finally:
                # Sempre reabilita o dispositivo
                time.sleep(0.5)  # Aguarda antes de reabilitar
                self.device.conn.enable_device()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
            
    def iniciar_captura_facial(self):
        """Inicia o processo de captura facial"""
        print(f"\n[FACE] Iniciando captura facial para usuário {self.aluno_id}")
        
        if not self.cadastro_realizado:
            print("[FACE] Erro: Usuário não cadastrado")
            messagebox.showerror("Erro", "Por favor, cadastre o usuário primeiro.")
            return
            
        try:
            print("[FACE] Abrindo janela de captura...")
            capture_window = FaceCaptureWindow(self, self.device, self.aluno_id)
            # Aguarda a janela de captura ser fechada antes de destruir o form
            self.wait_window(capture_window)
            print("[FACE] Captura finalizada, fechando formulário")
            self.destroy()
        except Exception as e:
            print(f"[FACE] Erro crítico: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao iniciar captura facial: {str(e)}")