"""
Servidor para um Sistema de Chat via Sockets.
Feito por: Samuel Figueira Aguiar
Início: 25/11/2023
"""

import socket
import threading

class User:
    def __init__(self, nickname, client):
        self.client = client
        self.nickname = nickname
        

# Constantes para a criação do servidor
PORT = 1945
SERVER_IP = socket.gethostbyname(socket.gethostname())
CHAR_SET = 'utf-8'

# Inicialização do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()
print(f"[LOG] SERVIDOR INICIADO EM {SERVER_IP}.")

# Lista de clientes e nicknames:
users = []

# Função para enviar mensagens para todos os clientes
def broadcast(message):
    for user in users:
        user.client.send(message)

# Função para tratar os clientes
def handle(user):
    while True:
        try:
            # Enviar mensagens para todos os clientes se houverem mensagens para enviar
            message = user.client.recv(1024)
            message = f"[{user.nickname}]: {message.decode(CHAR_SET)}".encode(CHAR_SET)
            broadcast(message)
        except:
            # Remover cliente e nickname quando o cliente desconectar
            nickname = user.nickname
            users.remove(user)
            user.client.close()
            broadcast(f'{nickname} saiu!'.encode(CHAR_SET))
            break


# Função para receber mensagens e enviar para todos os clientes (método "main")
def receive():
    while True:
        # Aceitar conexões de clientes
        client, address = server.accept()
        print(f"[LOG] Conexão de {str(address)}.")

        # Enviar mensagem de boas vindas e pedir o nickname do cliente
        client.send('NICK'.encode(CHAR_SET))
        nickname = client.recv(1024).decode(CHAR_SET)
        user = User(nickname, client)
        users.append(user)

        # Imprimir o nickname do cliente e notificar conexão
        print(f"[LOG] O apelido de {address} é {nickname}.")
        broadcast(f"[SERVIDOR] {nickname} se juntou ao chat!".encode())

        # Dar boas-vindas (TO DO: ferramenta para mudar as boas vindas).
        client.send('[SERVIDOR] Você se conectou ao servidor!'.encode(CHAR_SET))

        # Iniciar thread para tratar o cliente
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()


# Método main()
receive()
