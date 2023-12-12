"""
Servidor para um Sistema de Chat via Sockets.
Feito por: Samuel Figueira Aguiar
Início: 25/11/2023
"""

import socket
import threading
import rsa


class User:
    def __init__(self, nickname:str, client:socket.socket, key:bytes) -> None:
        self.client = client
        self.nickname = nickname

# Gerar chaves pública e privada para o servidor
PUBLIC_KEY, PRIVATE_KEY = rsa.newkeys(1024)

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
def broadcast(message:bytes) -> None:
    for user in users:
        user.client.send(message)


# Função para tratar os clientes
def handle(user:User) -> None:
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
def receive() -> None:
    while True:
        # Aceitar conexões de clientes
        client, address = server.accept()
        print(f"[SERVER] Conexão de {str(address)}.")

        # Enviar mensagem de boas vindas e pedir o nickname do cliente
        # RECEBER NICKNAME DO CLIENTE
        client.send('CLIENT_NICKNAME'.encode(CHAR_SET))
        nickname = client.recv(1024).decode(CHAR_SET)
        
        # RECEBER CHAVE PÚBLICA DO CLIENTE
        client.send('CLIENT_PUBLIC_KEY'.encode(CHAR_SET))
        key = rsa.PublicKey.load_pkcs1(client.recv(1024))
        
        # ENVIAR CHAVE PÚBLICA DO SERVIDOR PARA O CLIENTE
        client.send('SERVER_PUBLIC_KEY'.encode(CHAR_SET))
        client.send(PUBLIC_KEY.save_pkcs1("PEM"))
        
        user = User(nickname, client, key)
        users.append(user)

        # Imprimir o nickname do cliente e notificar conexão
        print(f"[SERVER] O apelido de {address} é {nickname}.")
        broadcast(f"[SERVIDOR] {nickname} se juntou ao chat!".encode(CHAR_SET))

        # Dar boas-vindas (TO DO: ferramenta para mudar as boas vindas).
        client.send('[SERVIDOR] Você se conectou ao servidor!'.encode(CHAR_SET))

        # Iniciar thread para tratar o cliente
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()


# Método main()
receive()
