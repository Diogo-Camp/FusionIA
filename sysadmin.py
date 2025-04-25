# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
from datetime import datetime
import re

OLLAMA_HOST = "http://localhost:11434"
HISTORICO_PATH = "./historico_conversas"
os.makedirs(HISTORICO_PATH, exist_ok=True)

LIMITE_MENSAGENS = 10
current_dir = os.getcwd()

# === PERSONALIDADE SYSADMIN ROBÔ ===
def carregar_personalidade():
    return {
        "role": "system",
        "content": (
            "Você é um sysadmin experiente, sarcástico e direto. "
            "Seu trabalho é auxiliar o usuário no uso do terminal Linux, explicando comandos como ls -la, chmod, ps aux, e analisando arquivos do sistema. "
            "Quando receber 'cmd: <comando>', execute no shell e interprete a saída como um especialista faria. "
            "Use tags como [cmd], [resposta], [resumo], [erro], [leitura], [atalho] para organização. Seja técnico, preciso e sem rodeios."
        )
    }

# === NOVO: Personalidade leve para bate-papo ===
def conversa_normal(user_input, modelo, messages):
    mensagem = user_input.replace("!conversa:", "").strip()

    prompt = [
        {
            "role": "system",
            "content": (
                "Você é um assistente simpático e curioso, respondendo de forma natural, descontraída e útil."
            )
        },
        {"role": "user", "content": mensagem}
    ]
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": modelo, "messages": prompt, "stream": False},
            timeout=60
        )
        data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        print(f"\n[conversa]: {content}")
        messages.append({"role": "user", "content": mensagem})
        messages.append({"role": "assistant", "content": content})
    except Exception as e:
        print(f"[erro] Conversa falhou: {e}")

# === UTILITÁRIOS ===
def listar_modelos():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        print(f"[erro] Erro ao buscar modelos: {e}")
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
        print("[erro] Entrada inválida.")

def salvar_arquivo():
    caminho = input("\n[tag: salvar] Caminho completo do arquivo: ").strip()
    conteudo = input("Conteúdo do arquivo: ").strip()
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"[resposta] Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"[erro] Falha ao salvar: {e}")

def salvar_historico(messages, modelo):
    base = f"chat_{modelo}_{datetime.now().strftime('%Y-%m-%d')}"
    n = 1
    while os.path.exists(f"{HISTORICO_PATH}/{base}_{n}.json"):
        n += 1
    nome_arquivo = f"{HISTORICO_PATH}/{base}_{n}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"[resposta] Histórico salvo em {nome_arquivo}")

def resumir_conversa(messages, modelo):
    prompt = [carregar_personalidade()] + messages[-LIMITE_MENSAGENS:] + [{"role": "user", "content": "Resuma nossa conversa em 3 frases."}]
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": prompt}, stream=False)
        lines = response.text.splitlines()
        content = ""
        for line in lines:
            if line.startswith("data: "):
                data = line.replace("data: ", "")
                chunk = json.loads(data)
                content += chunk.get("message", {}).get("content", "")
        print(f"\n[resumo]\n{content.strip()}")
        return [{"role": "system", "content": f"Resumo da conversa: {content.strip()}"}]
    except Exception as e:
        print(f"[erro] Erro ao resumir: {e}")
        return [carregar_personalidade()]

def interpretar_comando_personalizado(comando):
    if comando.startswith("nano ") or comando.startswith("cat "):
        arquivo = comando.split(" ", 1)[-1]
        try:
            with open(os.path.join(current_dir, arquivo), 'r', encoding='utf-8') as f:
                return f"[atalho] Conteúdo do arquivo {arquivo}:\n\n" + f.read()
        except Exception as e:
            return f"[erro] Não foi possível abrir {arquivo}: {e}"
    return None

def executar_comando(comando):
    global current_dir
    atalho = interpretar_comando_personalizado(comando)
    if atalho:
        return atalho
    if comando.startswith("cd "):
        try:
            path = comando.split("cd ", 1)[1].strip()
            new_path = os.path.abspath(os.path.join(current_dir, path))
            if os.path.isdir(new_path):
                current_dir = new_path
                return f"[atalho] Diretório alterado para: {current_dir}"
            else:
                return f"[erro] Diretório não encontrado: {new_path}"
        except Exception as e:
            return f"[erro] Falha ao mudar de diretório: {e}"
    try:
        output = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, text=True, cwd=current_dir)
        return output
    except subprocess.CalledProcessError as e:
        return f"[erro ao executar]: {e.output}"

def ler_arquivo(caminho):
    try:
        with open(os.path.join(current_dir, caminho), 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return conteudo
    except Exception as e:
        return f"[erro] Não foi possível ler o arquivo: {e}"

def comandos_internos(user_input):
    comandos = {
        "!ajuda": (
            "[comandos internos]\n"
            "- cmd: <comando> -- executa comandos no terminal\n"
            "- ler: <arquivo> -- lê conteúdo de arquivos\n"
            "- salvar -- cria um arquivo\n"
            "- resumir -- resume a conversa atual\n"
            "- !tarefa: <ação> -- executa uma tarefa interpretada pela IA\n"
            "- !conversa: <mensagem> -- conversa leve com a IA\n"
            "- !ajuda -- mostra este menu"
        )
    }
    return comandos.get(user_input.strip(), None)

def extrair_comandos(texto):
    comandos = []
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("["):
            comandos.append(linha)
    return comandos

def interpretar_tarefa(user_input, modelo, messages):
    tarefa = user_input.replace("!tarefa:", "").strip()
    prompt = [carregar_personalidade()] + messages[-LIMITE_MENSAGENS:] + [
        {"role": "user", "content": f"Analise esta tarefa: {tarefa}. Retorne apenas os comandos necessários no Linux para executar isso."}
    ]
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": prompt}, stream=False)
        content = response.text
        comandos = []
        for line in content.splitlines():
            if line.startswith("data: "):
                data = line.replace("data: ", "")
                try:
                    parsed = json.loads(data)
                    trecho = parsed.get("message", {}).get("content", "")
                    comandos.extend(extrair_comandos(trecho))
                except json.JSONDecodeError:
                    continue
        for cmd in comandos:
            print(f"\n[executando]: {cmd}")
            resultado = executar_comando(cmd)
            print(resultado)
        return '\n'.join(comandos)
    except Exception as e:
        print(f"[erro] Falha ao interpretar tarefa: {e}")
        return "[erro] Tarefa não interpretada."

def chat_loop(modelo):
    print(f"\nIniciando com o modelo: {modelo}\nDigite 'sair' para encerrar.")
    messages = [carregar_personalidade()]

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

        resposta_comando = comandos_internos(user_input)
        if resposta_comando:
            print(resposta_comando)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": resposta_comando})
            continue

        if user_input.startswith("cmd:"):
            comando = user_input[4:].strip()
            resultado = executar_comando(comando)
            print(f"\n[cmd]: {comando}\n[resposta]:\n{resultado}")
            messages.append({"role": "user", "content": f"cmd: {comando}"})
            messages.append({"role": "assistant", "content": f"[cmd] {comando}\n[resposta]\n{resultado}"})
        elif user_input.startswith("ler:"):
            caminho = user_input[4:].strip()
            conteudo = ler_arquivo(caminho)
            print(f"\n[leitura do arquivo]\n{conteudo}")
            messages.append({"role": "user", "content": f"ler: {caminho}"})
            messages.append({"role": "assistant", "content": f"[leitura]\n{conteudo}"})
        elif user_input.startswith("!tarefa:"):
            interpretada = interpretar_tarefa(user_input, modelo, messages)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": interpretada})
        elif user_input.startswith("!conversa:"):
            conversa_normal(user_input, modelo, messages)
        else:
            messages.append({"role": "user", "content": user_input})
            try:
                response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": messages, "stream": True}, stream=True)
                print("[assistente]: ", end="", flush=True)
                full_content = ""
                for line in response.iter_lines():
                    if line and line.startswith(b"data: "):
                        chunk = json.loads(line.decode('utf-8').replace("data: ", ""))
                        content = chunk.get("message", {}).get("content", "")
                        print(content, end="", flush=True)
                        full_content += content
                messages.append({"role": "assistant", "content": full_content})
            except Exception as e:
                print(f"[erro] Erro na requisição: {e}")

        if len(messages) > LIMITE_MENSAGENS * 2:
            print("\n[alerta] Histórico longo. Use 'resumir' para otimizar o contexto.")

if __name__ == "__main__":
    modelos = listar_modelos()
    escolhido = escolher_modelo(modelos)
    chat_loop(escolhido)
