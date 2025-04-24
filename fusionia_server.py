# fusionia_server.py
# Servidor Flask completo com suporte a sessões, PostgreSQL, exportação JSON, e integração com Ollama

import os
import uuid
import json
import psycopg2
import threading
import requests
from flask import Flask, request, jsonify, g
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# ========== CONFIGURAÇÃO ==========
#DB_URL = os.getenv("DATABASE_URL", "postgresql://usuario:senha@localhost/fusiondb")
DB_URL = os.getenv("DATABASE_URL")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://0.0.0.0:11434")
CONVERSAS_DIR = "conversas"
ollama_lock = threading.Lock()

if not os.path.exists(CONVERSAS_DIR):
    os.makedirs(CONVERSAS_DIR)


app = Flask(__name__)

# ========== PERSONALIDADES ==========
def carregar_personalidades():
    try:
        with open("personalidades.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar JSON de personalidades: {e}")
        return {}

def carregar_personalidade(nome):
    return carregar_personalidades().get(nome, {
        "role": "system",
        "content": "Você é uma IA neutra e objetiva."
    })

# ========== BANCO DE DADOS ==========
def conectar_db():
    return psycopg2.connect(DB_URL)

# ========== GERENCIADOR DE SESSÃO ==========
class GerenciadorSessao:
    def __init__(self, modelo, personalidade):
        self.conn = conectar_db()
        self.sessao_id = str(uuid.uuid4())
        self.conversa_json = []
        self.modelo = modelo
        self.personalidade = personalidade
        self.criar_sessao()

    def criar_sessao(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessao (id, modelo, personalidade, criado_em) VALUES (%s, %s, %s, %s)",
                (self.sessao_id, self.modelo, self.personalidade, datetime.now())
            )
            self.conn.commit()

    def salvar_mensagem(self, tipo, conteudo):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO mensagem (sessao_id, tipo, conteudo, criado_em) VALUES (%s, %s, %s, %s)",
                (self.sessao_id, tipo, conteudo, datetime.now())
            )
            self.conn.commit()
        self.conversa_json.append({"tipo": tipo, "mensagem": conteudo})

    def exportar_json(self):
        with open(f"{CONVERSAS_DIR}/{self.sessao_id}.json", "w", encoding="utf-8") as f:
            json.dump(self.conversa_json, f, ensure_ascii=False, indent=2)

# ========== ROTA PRINCIPAL ==========
@app.before_request
def criar_sessao():
    if request.endpoint == 'conversar':
        data = request.get_json()
        modelo = data.get("modelo", "mistral")
        personalidade = data.get("personalidade", "sysadmin")
        g.sessao = GerenciadorSessao(modelo, personalidade)

@app.route("/conversar", methods=["POST"])
def conversar():
    data = request.get_json()
    mensagem = data.get("mensagem")
    modelo = data.get("modelo", "mistral")
    personalidade = data.get("personalidade", "sysadmin")

    if not mensagem:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

    prompt = carregar_personalidade(personalidade)
    mensagens = [prompt, {"role": "user", "content": mensagem}]

    payload = {
        "model": modelo,
        "messages": mensagens,
        "stream": False
    }

    with ollama_lock:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)

    if response.status_code != 200:
        return jsonify({"erro": "Falha ao se comunicar com o modelo."}), 500

    resposta = response.json()["message"]["content"]

    g.sessao.salvar_mensagem("user", mensagem)
    g.sessao.salvar_mensagem("ia", resposta)

    return jsonify({"resposta": resposta})

# ========== ENCERRAR SESSÃO ==========
@app.route("/encerrar", methods=["POST"])
def encerrar():
    g.sessao.exportar_json()
    return jsonify({"status": "Sessão salva em JSON", "id": g.sessao.sessao_id})

# ========== INICIAR SERVIDOR ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
