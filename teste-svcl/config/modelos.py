import requests

def listar_modelos_ollama():
    """
    Consulta a API do Ollama local e retorna uma lista de modelos disponíveis.
    """
    try:
        resposta = requests.get("http://localhost:11434/api/tags")
        resposta.raise_for_status()
        return [modelo["name"] for modelo in resposta.json()["models"]]
    except Exception as e:
        print(f"[ERRO] Falha ao buscar modelos: {e}")
        return []

def validar_modelo(nome_modelo):
    """
    Verifica se o modelo existe no Ollama.
    """
    return nome_modelo in listar_modelos_ollama()
