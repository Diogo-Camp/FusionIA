from config.personalidades import carregar_personalidade
from utils.formatadores import montar_conversa
import requests

class ServidorIA:
    def __init__(self, host="http://localhost:11434", modelo_default="mistral", personalidade_default="sysadmin"):
        self.host = host
        self.modelo = modelo_default
        self.personalidade = personalidade_default

    def configurar(self, modelo=None, personalidade=None):
        if modelo:
            self.modelo = modelo
        if personalidade:
            self.personalidade = personalidade

    def conversar(self, mensagem_usuario):
        mensagens = montar_conversa(
            system_prompt=carregar_personalidade(self.personalidade),
            user_input=mensagem_usuario
        )
        payload = {
            "model": self.modelo,
            "messages": mensagens,
            "stream": False
        }
        response = requests.post(f"{self.host}/api/chat", json=payload)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Erro ao conversar com o modelo: {response.text}"
