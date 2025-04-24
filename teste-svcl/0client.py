import requests

class ClienteIA:
    def __init__(self, servidor_url="http://localhost:5000"):
        self.servidor_url = servidor_url
        self.modelo = "mistral"
        self.personalidade = "neutro"

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

# Modo de uso:
if __name__ == "__main__":
    cliente = ClienteIA()
    cliente.configurar(personalidade="zoeira")

    while True:
        entrada = input("\nVocê: ")
        if entrada.lower() in ["sair", "exit", "quit"]:
            break
        resposta = cliente.conversar(entrada)
        print("IA:", resposta)
