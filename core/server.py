import socket

def conectar_servidor(host, porta):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, porta))
    return s

def enviar_msg(sock, msg):
    sock.sendall(msg.encode())

def receber_resposta(sock):
    return sock.recv(1024).decode()
