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

# Variáveis para criptografia
CLIENT_PUBLIC_KEY, CLIENT_PRIVATE_KEY = rsa.newkeys(1024)

# Configurações do cliente
CHAR_SET = 'utf8'
IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 1945

# Escolher um apelido para entrar no servidor
nickname = input("[CLIENTE] Escolha seu apelido: ")

# Conectar ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP_SERVIDOR, PORTA_SERVIDOR))

# Troca de informações com o servidor
while True:
    command = client.recv(1024).decode(CHAR_SET)
    if command == 'CLIENT_NICKNAME':
        # Enviar o apelido selecionado ao servidor
        client.send(nickname.encode(CHAR_SET))
    elif command == 'KEYS':
        client.send(CLIENT_PUBLIC_KEY.save_pkcs1('PEM'))
        SERVER_PUBLIC_KEY = rsa.PublicKey.load_pkcs1((client.recv(1024)))
        break
    else:
        print(f"[CLIENTE] Ocorreu um erro! Fechando o cliente.")
        client.close()
        break


# Função para receber mensagens do servidor
def receive() -> None:
    while True:
        try:
            # Descriptografa a mensagem com a minha chave:
            message = client.recv(1024)
            message = rsa.decrypt(message, CLIENT_PRIVATE_KEY).decode(CHAR_SET)
            print(message)
        except Exception as e:
            # Fechar a conexão em caso de erro
            print(F"[CLIENTE] Ocorreu um erro! Fechando o cliente.")
            print(e)
            client.close()
            sys.exit()


# Função para enviar mensagens para o servidor
def write() -> None:
    while True:
        time.sleep(1)
        message = input()
        # Criptografa a mensagem com a chave do servidor:
        message = rsa.encrypt(message.encode(CHAR_SET), SERVER_PUBLIC_KEY)

        # Envia a mensagem criptografada ao servidor:        
        client.send(message)


# Iniciar threads para receber e enviar mensagens
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
