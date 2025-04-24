import requests
import ollama
PERSONALIDADES = {
    "1": "sabio",
    "2": "zoeiro"
}

OLLAMA_HOST = "http://localhost:11434"

#lista todos os modelos ollama na maquina
def listar_modelos():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        print(f"[erro] Erro ao buscar modelos: {e}")
        exit()



#pergunta pro usuario os modelos, separando por id e nome.
def escolher_modelo(modelos):
    for idx, nome in enumerate(modelos, 1):
        print(f"[{idx}] {nome}")
    while True:
        try:
            idx = int(input("\nDigite o número do modelo: ")) - 1
            if 0 <= idx < len(modelos):
                return modelos[idx]
        except ValueError:
            pass
        print("[erro] Entrada inválida.")

def enviar_prompt(modelo, personalidade, historico):
    url = "http://localhost:8000/generate"
    payload = {
        "model": modelo,
        "personality": personalidade,
        "messages": historico
    }
    response = requests.post(url, json=payload)
    return response.json()