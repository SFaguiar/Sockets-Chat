"""
Cliente para um Sistema de Chat via Sockets.
Feito por: Samuel Figueira Aguiar
Início: 25/11/2023
"""

import socket
import threading
import rsa
import sys
import time
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

# Variáveis para criptografia
CLIENT_PUBLIC_KEY, CLIENT_PRIVATE_KEY = rsa.newkeys(1024)
server_public_key = None

# Configurações do cliente
CHAR_SET = 'utf8'
IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 1945

class Client:
    def __init__(self, ip:str, porta:int) -> None:
        self.ip = ip
        self.porta = porta

        # Inicializar GUI
        client_message = tkinter.Tk()
        client_message.withdraw()

        # Escolher um apelido para entrar no servidor
        client_message.title('Apelido')
        self.nickname = tkinter.simpledialog.askstring(title='Apelido', prompt='Digite seu apelido:', parent=client_message)
        self.gui_done = False
        self.running = True
        
        # Conectar ao servidor:
        self.connect_to_server()
        
        gui_thread = threading.Thread(target=self.gui_loop).start()
        receive_thread = threading.Thread(target=self.receive).start()
        
        
    def gui_loop(self) -> None:
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")
        
        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)
        
        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)
        
        self.gui_done = True
        
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        
        self.win.mainloop()


    # Função para enviar mensagens para o servidor
    def write(self) -> None:
        message = self.input_area.get('1.0', 'end')
        
        # Criptografa a mensagem com a chave do servidor e a envia:
        message = rsa.encrypt(message.encode(CHAR_SET), self.server_public_key)   
        self.client.send(message)
        
        # Limpar a área de texto após enviar a mensagem:
        self.input_area.delete('1.0', 'end')


    # Função para fechar a GUI e encerrar a conexão com o servidor
    def stop(self) -> None:
        self.running = False
        self.win.destroy()
        self.client.close()
        exit(0)
        

    def connect_to_server(self):
        # Criar um socket TCP para conectar ao servidor
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ip, self.porta))
        
        # Troca de informações com o servidor
        while True:
            command = self.client.recv(1024).decode(CHAR_SET)
            if command == 'CLIENT_NICKNAME':
                # Enviar o apelido selecionado ao servidor
                self.client.send(self.nickname.encode(CHAR_SET))
            elif command == 'KEYS':
                self.client.send(CLIENT_PUBLIC_KEY.save_pkcs1('PEM'))
                self.server_public_key = rsa.PublicKey.load_pkcs1((self.client.recv(1024)))
                return
            else:
                print(f"[CLIENTE] Ocorreu um erro! Fechando o cliente.")
                self.client.close()
                break
        
    # Função para receber mensagens do servidor
    def receive(self) -> None:
        while self.running:
            try:
                if self.gui_done:
                    # Descriptografa a mensagem com a minha chave:
                    message = self.client.recv(1024)
                    message = rsa.decrypt(message, CLIENT_PRIVATE_KEY).decode(CHAR_SET)
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message)
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except Exception as e:
                # Fechar a conexão em caso de erro
                print(F"[CLIENTE] Ocorreu um erro! Fechando o cliente.")
                print(e)
                self.client.close()
                exit(-1)


def main() -> None:
    client = Client(IP_SERVIDOR, PORTA_SERVIDOR)



main()
