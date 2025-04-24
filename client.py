import requests
import json

class ClienteIA:
    def __init__(self, servidor_url="http://localhost:5000"):
        self.servidor_url = servidor_url
        self.modelo = None
        self.personalidade = None

    def listar_modelos(self):
        try:
            r = requests.get("http://localhost:11434/api/tags")  # API do Ollama1
            modelos = [m["name"] for m in r.json()["models"]]
            return modelos
        except Exception as e:
            print(f"[ERRO] Não foi possível listar os modelos do Ollama: {e}")
            return []

    def listar_personalidades(self):
        try:
            with open("personalidades.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Não foi possível carregar as personalidades: {e}")
            return {}

    def configurar(self, modelo, personalidade):
        self.modelo = modelo
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


def menu_interativo():
    cliente = ClienteIA()

    # 1. Listar modelos
    modelos = cliente.listar_modelos()
    if not modelos:
        print("⚠️ Nenhum modelo disponível no Ollama.")
        return

    print("\n🧠 Modelos disponíveis:")
    for i, m in enumerate(modelos, 1):
        print(f"{i}. {m}")
    escolha = int(input("\nEscolha o modelo (número): "))
    modelo_escolhido = modelos[escolha - 1]

    # 2. Listar personalidades
    personalidades = cliente.listar_personalidades()
    print("\n🎭 Personalidades disponíveis:")
    nomes = list(personalidades.keys())
    for i, p in enumerate(nomes, 1):
        print(f"{i}. {p}")
    escolha_p = int(input("\nEscolha a personalidade (número): "))
    personalidade_escolhida = nomes[escolha_p - 1]

    # 3. Configurar cliente
    cliente.configurar(modelo=modelo_escolhido, personalidade=personalidade_escolhida)

    print(f"\n✅ Configurado com o modelo '{modelo_escolhido}' e personalidade '{personalidade_escolhida}'.")
    print("Digite sua mensagem ou 'sair' para encerrar.\n")

    while True:
        msg = input("Você: ")
        if msg.lower() in ["sair", "exit", "quit"]:
            break
        resposta = cliente.conversar(msg)
        print("IA:", resposta)


if __name__ == "__main__":
    menu_interativo()
