import requests
import json

class ServidorIA:
    def __init__(self, host="http://localhost:11434", modelo_default="mistral", personalidade_default="neutro"):
        self.host = host
        self.modelo = modelo_default
        self.personalidade = personalidade_default
        self.personalidades = self.carregar_personalidades()

    def carregar_personalidades(self):
        try:
            with open("0personalidades.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"neutro": "Você é uma IA útil e direta."}

    def definir_modelo(self, modelo):
        self.modelo = modelo

    def definir_personalidade(self, nome):
        if nome in self.personalidades:
            self.personalidade = nome
        else:
            raise ValueError("Personalidade não encontrada.")

    def conversar(self, mensagem_usuario):
        system_prompt = self.personalidades.get(self.personalidade, "Você é uma IA neutra.")
        payload = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensagem_usuario}
            ],
            "stream": False
        }
        response = requests.post(f"{self.host}/api/chat", json=payload)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Erro ao conversar com o modelo: {response.text}"
