# fusionia_project/main.py

"""
FusionIA - IA simbiótica local com:
✅ Fine-Tuning modular (PEFT + Transformers)
✅ RAG local (FAISS + contextos por embeddings)
✅ RLHF com recompensas simbólicas
✅ Escolha de personalidades e modelos
"""
60
import os
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import torch
import json

app = Flask(__name__)

# Caminhos
MODEL_DIR = "./models"
RAG_INDEX_PATH = "./rag/context.index"
PERSONALITIES_PATH = "./personalidades"
REWARDS_LOG = "./logs/rewards.json"

# Carrega embeddings e FAISS index
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
if os.path.exists(RAG_INDEX_PATH):
    faiss_index = faiss.read_index(RAG_INDEX_PATH)
else:
    faiss_index = faiss.IndexFlatL2(384)
    print("[!] FAISS index criado vazio")

# Carrega personalidade base

with open(f"{PERSONALITIES_PATH}/neutra.json", "r") as f:
    base_persona = json.load(f)

# Load modelo default
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, device_map="auto")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("mensagem", "")
    personalidade = data.get("personalidade", "neutra")
    model_name = data.get("modelo", MODEL_NAME)

    # Carrega personalidade escolhida
    try:
        with open(f"{PERSONALITIES_PATH}/{personalidade}.json", "r") as f:
            perfil = json.load(f)
    except:
        perfil = base_persona

    system_msg = perfil.get("contexto", "Você é uma IA útil e amigável.")

    # Aplica RAG (recupera contexto)
    emb = embedding_model.encode([prompt])
    D, I = faiss_index.search(emb, k=3)
    contextos = "\n".join([perfil.get("base", "")] + [f"Contexto {i+1}: {str(i)}" for i in I[0]])

    # Monta prompt
    full_prompt = f"{system_msg}\n{contextos}\nUsuário: {prompt}\nIA:"
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200)
    resposta = tokenizer.decode(outputs[0], skip_special_tokens=True).split("IA:")[-1].strip()

    # Reward simbólica (simples)
    with open(REWARDS_LOG, "a") as log:
        log.write(json.dumps({"msg": prompt, "resp": resposta, "reward": len(resposta)}) + "\n")

    return jsonify({"resposta": resposta})

@app.route("/personalidades", methods=["GET"])
def listar_personalidades():
    arquivos = os.listdir(PERSONALITIES_PATH)
    return jsonify([arq.replace(".json", "") for arq in arquivos])

@app.route("/modelos", methods=["GET"])
def listar_modelos():
    return jsonify(os.listdir(MODEL_DIR))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)