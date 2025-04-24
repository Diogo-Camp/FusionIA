# client_fusionia.py
# Cliente Python para se conectar com o servidor FusionIA remoto

import requests

class ClienteFusionIA:
    def __init__(self, servidor_url="http://0.0.0.0:5000"):
        self.servidor_url = servidor_url
        self.modelo = "mistral"
        self.personalidade = "sysadmin"

    def configurar(self, modelo=None, personalidade=None):
        if modelo:
            self.modelo = modelo
        if personalidade:
            self.personalidade = personalidade

    def conversar(self, mensagem):
        payload = {
            "mensagem": mensagem,
            "modelo": self.modelo,
            "personalidade": self.personalidade
        }
        try:
            resposta = requests.post(f"{self.servidor_url}/conversar", json=payload)
            resposta.raise_for_status()
            return resposta.json()["resposta"]
        except requests.exceptions.RequestException as e:
            return f"[ERRO] Falha na comunicação: {e}"

    def encerrar_sessao(self):
        try:
            resposta = requests.post(f"{self.servidor_url}/encerrar")
            resposta.raise_for_status()
            return resposta.json()
        except requests.exceptions.RequestException as e:
            return {"erro": str(e)}

if __name__ == "__main__":
    cliente = ClienteFusionIA()
    print("🎯 Cliente FusionIA iniciado. Digite 'sair' para encerrar.")
    cliente.configurar(
        modelo=input("Modelo (padrão: mistral): ") or "mistral",
        personalidade=input("Personalidade (padrão: sysadmin): ") or "sysadmin"
    )

    while True:
        msg = input("\nVocê: ")
        if msg.lower() in ["sair", "exit", "quit"]:
            print("💾 Salvando conversa no servidor...")
            print(cliente.encerrar_sessao())
            break
        resposta = cliente.conversar(msg)
        print("IA:", resposta)
