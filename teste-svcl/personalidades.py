import json

def carregar_personalidades_json():
    try:
        with open("personalidades.json", "r", encoding="utf-8") as f:
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
