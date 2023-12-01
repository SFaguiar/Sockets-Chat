"""
Servidor para um Sistema de Chat via Sockets.
Feito por: Samuel Figueira Aguiar
Início: 25/11/2023
"""

import socket
import threading

# Constantes para a criação do servidor
PORT = 1945
SERVER_IP = socket.gethostbyname(socket.gethostname())
CHAR_SET = 'utf-8'

# Inicialização do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()

# Lista de clientes e nicknames:
clients = []
nicknames = []

print(f"[LOG] SERVIDOR INICIADO EM {SERVER_IP}.")


# Função para enviar mensagens para todos os clientes
def broadcast(message):
    for client in clients:
        client.send(message)


# Função para tratar os clientes
def handle(client):
    while True:
        try:
            # Enviar mensagens para todos os clientes se houverem mensagens para enviar
            message = client.recv(1024)
            broadcast(message)
        except:
            # Remover cliente e nickname quando o cliente desconectar
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} saiu!'.encode(CHAR_SET))
            nicknames.remove(nickname)
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
        nicknames.append(nickname)
        clients.append(client)

        # Imprimir o nickname do cliente e notificar conexão
        print(f"[LOG] O apelido de {address} é {nickname}.")
        broadcast(f"[SERVIDOR] {nickname} se juntou ao chat!".encode())

        # Dar boas-vindas (TO DO: ferramenta para mudar as boas vindas).
        client.send('[SERVIDOR] Você se conectou ao servidor!'.encode(CHAR_SET))

        # Iniciar thread para tratar o cliente
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


# Método main()
receive()
