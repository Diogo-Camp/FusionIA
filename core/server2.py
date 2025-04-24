import socket
import threading

class Servidor:
    def __init__(self, host='127.0.0.1', porta=5555):
        self.host = host
        self.porta = porta
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.host, self.porta))
        self.servidor_socket.listen(5)
        print(f"[Servidor] Rodando em {self.host}:{self.porta}")

    def lidar_com_cliente(self, conn, addr):
        print(f"[Conexão] Cliente conectado: {addr}")
        while True:
            try:
                dados = conn.recv(1024).decode()
                if not dados:
                    break
                print(f"[Recebido de {addr}] {dados}")
                resposta = f"Servidor recebeu: {dados}"
                conn.send(resposta.encode())
            except:
                break
        print(f"[Desconectado] Cliente {addr} desconectado.")
        conn.close()

    def iniciar(self):
        print("[Servidor] Aguardando conexões...")
        while True:
            conn, addr = self.servidor_socket.accept()
            thread = threading.Thread(target=self.lidar_com_cliente, args=(conn, addr))
            thread.start()
            print(f"[Ativos] Conexões ativas: {threading.active_count() - 1}")

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
