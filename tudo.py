# Estrutura completa do projeto em um script Python só.
# Este é um servidor Flask com sistema de seleção dinâmica de modelos e personalidades via JSON.

import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ======= CONFIGURAÇÕES =======

# Caminho para o arquivo JSON de personalidades
CAMINHO_PERSONALIDADES = "personalidades.json"


# ======= PERSONALIDADES =======

def carregar_personalidades_json():
    try:
        with open(CAMINHO_PERSONALIDADES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar JSON de personalidades: {e}")
        return {}

def carregar_personalidade(nome):
    return carregar_personalidades_json().get(nome, {
        "role": "system",
        "content": "Você é uma IA neutra e objetiva."
    })

def listar_personalidades():
    return list(carregar_personalidades_json().keys())


# ======= MODELOS =======

def listar_modelos_ollama():
    try:
        resposta = requests.get("http://localhost:11434/api/tags")
        resposta.raise_for_status()
        return [modelo["name"] for modelo in resposta.json()["models"]]
    except Exception as e:
        print(f"[ERRO] Falha ao buscar modelos: {e}")
        return []

def validar_modelo(nome_modelo):
    return nome_modelo in listar_modelos_ollama()


# ======= FORMATADOR =======

def montar_conversa(system_prompt, user_input):
    return [
        system_prompt,
        {"role": "user", "content": user_input}
    ]


# ======= SERVIDOR IA =======

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


# ======= FLASK API =======

ia = ServidorIA()

@app.route("/conversar", methods=["POST"])
def conversar():
    try:
        data = request.get_json(force=True)
        print("🔍 Dados recebidos:", data)

        mensagem = data.get("mensagem")
        modelo = data.get("modelo")
        personalidade = data.get("personalidade")

        if not mensagem:
            return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

        if modelo and not validar_modelo(modelo):
            return jsonify({"erro": f"Modelo inválido: {modelo}"}), 400

        if personalidade and personalidade not in listar_personalidades():
            return jsonify({"erro": f"Personalidade não reconhecida: {personalidade}"}), 400

        ia.configurar(modelo=modelo, personalidade=personalidade)
        resposta = ia.conversar(mensagem)
        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


# ======= EXECUÇÃO =======

if __name__ == "__main__":
    app.run(port=5000)
