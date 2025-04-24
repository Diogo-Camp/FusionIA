import os
import json
import requests
import subprocess
from datetime import datetime

OLLAMA_HOST = "http://localhost:11434"
HISTORICO_PATH = "./historico_conversas"
os.makedirs(HISTORICO_PATH, exist_ok=True)

LIMITE_MENSAGENS = 10
SYSTEM_PROMPT = {
    "role": "system",
    "content": "Você é um assistente direto, inteligente, com acesso ao terminal Linux. Quando o usuário digitar 'cmd: <comando>', execute no sistema e use a saída como base para suas próximas respostas."
}

# Utilidades

def listar_modelos():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        print(f"Erro ao buscar modelos: {e}")
        exit()

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
        print("Entrada inválida.")

def salvar_arquivo():
    caminho = input("\nCaminho completo do arquivo: ").strip()
    conteudo = input("Conteúdo do arquivo: ").strip()
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")

def salvar_historico(messages, modelo):
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"{HISTORICO_PATH}/chat_{modelo}_{agora}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Histórico salvo em {nome_arquivo}")

def resumir_conversa(messages, modelo):
    prompt = [SYSTEM_PROMPT] + messages[-LIMITE_MENSAGENS:] + [{"role": "user", "content": "Resuma nossa conversa em 3 frases."}]
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": modelo, "messages": prompt},
            stream=False
        )
        resumo = response.json().get("message", {}).get("content", "")
        print(f"\nResumo gerado:\n{resumo.strip()}")
        return [{"role": "system", "content": f"Resumo da conversa: {resumo.strip()}"}]
    except Exception as e:
        print(f"Erro ao resumir: {e}")
        return [SYSTEM_PROMPT]

def executar_comando(comando):
    try:
        output = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"[Erro ao executar]: {e.output}"

def chat_loop(modelo):
    print(f"\nIniciando com o modelo: {modelo}\nDigite 'sair' para encerrar.")
    messages = [SYSTEM_PROMPT]

    while True:
        user_input = input("\nVocê: ").strip()
        if user_input.lower() in ["sair", "exit"]:
            salvar_historico(messages, modelo)
            break
        elif user_input.lower() == "salvar":
            salvar_arquivo()
            continue
        elif user_input.lower() in ["resumir", "limpar"]:
            messages = resumir_conversa(messages, modelo)
            continue

        if user_input.startswith("cmd:"):
            comando = user_input[4:].strip()
            resultado = executar_comando(comando)
            print(f"\n[Saída do comando]:\n{resultado}")
            messages.append({"role": "user", "content": f"cmd: {comando}"})
            messages.append({"role": "assistant", "content": f"Resultado do comando '{comando}':\n{resultado}"})
        else:
            messages.append({"role": "user", "content": user_input})

            try:
                response = requests.post(
                    f"{OLLAMA_HOST}/api/chat",
                    json={"model": modelo, "messages": messages, "stream": True},
                    stream=True
                )

                print("Modelo: ", end="", flush=True)
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8').replace("data: ", ""))
                        content = chunk.get("message", {}).get("content", "")
                        print(content, end="", flush=True)
                        full_content += content
                messages.append({"role": "assistant", "content": full_content})

            except Exception as e:
                print(f"Erro na requisição: {e}")

        if len(messages) > LIMITE_MENSAGENS * 2:
            print("\n[Alerta] Histórico grande. Use 'resumir' para limpar o contexto.")

if __name__ == "__main__":
    modelos = listar_modelos()
    escolhido = escolher_modelo(modelos)
    chat_loop(escolhido)
