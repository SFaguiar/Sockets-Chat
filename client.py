"""
Cliente para um Sistema de Chat via Sockets.
Feito por: Samuel Figueira Aguiar
Início: 25/11/2023
"""

import socket
import threading
import rsa

PUBLIC_KEY, PRIVATE_KEY = rsa.newkeys(1024)

# Configurações do cliente
CHAR_SET = 'utf-8'
IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 1945

# Escolher um apelido para entrar no servidor
nickname = input("[CLIENTE] Escolha seu apelido: ")

# Conectar ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP_SERVIDOR, PORTA_SERVIDOR))

# Função para receber mensagens do servidor
def receive() -> None:
    while True:
        try:
            # Se receber a palavra-chave 'NICK', enviar o apelido selecionado
            message = client.recv(1024).decode(CHAR_SET)
            if message == 'CLIENT_NICKNAME':
                # Enviar o apelido selecionado ao servidor
                client.send(nickname.encode(CHAR_SET))
            elif message == 'CLIENT_PUBLIC_KEY':
                # Enviar a chave pública ao servidor
                client.send(PUBLIC_KEY.save_pkcs1("PEM"))
            elif message == 'SERVER_PUBLIC_KEY':
                SERVER_PUBLIC_KEY = rsa.PublicKey.load_pkcs1(client.recv(1024))
            else:
                # Imprimir a mensagem recebida, caso o nickname já tenha sido enviado
                print(message)
        except:
            # Fechar a conexão em caso de erro
            print("[CLIENTE] Ocorreu um erro! Fechando o cliente.")
            client.close()
            break


# Função para enviar mensagens para o servidor
def write() -> None:
    while True:
        message = input("[CLIENTE] Digite sua mensagem: ")
        client.send(message.encode(CHAR_SET))


# Iniciar threads para receber e enviar mensagens
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
