# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
from datetime import datetime

# === CONFIGS INICIAIS ===
OLLAMA_HOST = "http://localhost:11434"
HISTORICO_PATH = "./historico_conversas"
LIMITE_MENSAGENS = 10

os.makedirs(HISTORICO_PATH, exist_ok=True)

# === PERSONALIDADES ===
class PersonalidadeBase:
    def __init__(self):
        self.nome = "default"

    def mensagem_system(self):
        return {"role": "system", "content": "Você é uma IA genérica."}

class SysadminPersonality(PersonalidadeBase):
    def __init__(self):
        self.nome = "sysadmin"

    def mensagem_system(self):
        return {
            "role": "system",
            "content": (
                "Você é um sysadmin experiente, sarcástico e direto. "
                "Auxilie no terminal Linux, explicando comandos como ls -la, chmod, etc. "
                "Use tags como [cmd], [resposta], [erro], [atalho] e seja técnico."
            )
        }

class FriendlyPersonality(PersonalidadeBase):
    def __init__(self):
        self.nome = "amigavel"

    def mensagem_system(self):
        return {
            "role": "system",
            "content": (
                "Você é um assistente simpático e curioso, respondendo de forma natural, descontraída e útil."
            )
        }

# === CLASSE PRINCIPAL ===
class TerminalAssistente:
    def __init__(self, modelo, personalidade):
        self.modelo = modelo
        self.personalidade = personalidade
        self.messages = [self.personalidade.mensagem_system()]
        self.current_dir = os.getcwd()

    def executar_cmd(self, comando):
        try:
            if comando.startswith("cd "):
                path = comando.split("cd ", 1)[1].strip()
                new_path = os.path.abspath(os.path.join(self.current_dir, path))
                if os.path.isdir(new_path):
                    self.current_dir = new_path
                    return f"[atalho] Diretório alterado para: {self.current_dir}"
                return f"[erro] Diretório não encontrado: {new_path}"
            output = subprocess.check_output(
                comando, shell=True, stderr=subprocess.STDOUT, text=True, cwd=self.current_dir
            )
            return output
        except subprocess.CalledProcessError as e:
            return f"[erro ao executar]: {e.output}"

    def resumir(self):
        resumo_prompt = self.messages[-LIMITE_MENSAGENS:] + [
            {"role": "user", "content": "Resuma nossa conversa em 3 frases."}
        ]
        prompt = [self.personalidade.mensagem_system()] + resumo_prompt
        try:
            response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": self.modelo, "messages": prompt})
            data = response.json()
            resumo = data.get("message", {}).get("content", "")
            print(f"\n[resumo]: {resumo.strip()}")
            self.messages = [self.personalidade.mensagem_system(), {"role": "assistant", "content": resumo}]
        except Exception as e:
            print(f"[erro] Falha ao resumir: {e}")

    def salvar_historico(self):
        base = f"chat_{self.modelo}_{datetime.now().strftime('%Y-%m-%d')}_"
        n = 1
        while os.path.exists(f"{HISTORICO_PATH}/{base}{n}.json"):
            n += 1
        path = f"{HISTORICO_PATH}/{base}{n}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)
        print(f"[resposta] Histórico salvo em {path}")

    def responder_chat(self, entrada):
        self.messages.append({"role": "user", "content": entrada})
        payload = {
            "model": self.modelo,
            "messages": self.messages,
            "stream": False
        }
        try:
            response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            data = response.json()
            resposta = data.get("message", {}).get("content", "")
            print(f"[assistente]: {resposta.strip()}")
            self.messages.append({"role": "assistant", "content": resposta})
        except Exception as e:
            print(f"[erro] Falha ao gerar resposta: {e}")

# === FLUXO PRINCIPAL ===
def listar_modelos():
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags")
        return [m["name"] for m in r.json().get("models", [])]
    except:
        return []

def escolher_modelo():
    modelos = listar_modelos()
    for i, nome in enumerate(modelos, 1):
        print(f"[{i}] {nome}")
    idx = int(input("Escolha o modelo: ")) - 1
    return modelos[idx] if 0 <= idx < len(modelos) else modelos[0]

def escolher_personalidade():
    print("[1] Sysadmin\n[2] Conversa Amigável")
    escolha = input("Escolha a personalidade: ")
    return SysadminPersonality() if escolha == "1" else FriendlyPersonality()

def main():
    modelo = escolher_modelo()
    personalidade = escolher_personalidade()
    assistente = TerminalAssistente(modelo, personalidade)

    print("\nDigite 'sair' para encerrar, 'resumir' para resumir ou cmd: <comando> para comandos do terminal.")

    while True:
        entrada = input("\nVocê: ").strip()
        if entrada.lower() in ["sair", "exit"]:
            assistente.salvar_historico()
            break
        elif entrada.lower().startswith("cmd:"):
            comando = entrada[4:].strip()
            resultado = assistente.executar_cmd(comando)
            print(f"[resposta]:\n{resultado}")
            assistente.messages.append({"role": "user", "content": entrada})
            assistente.messages.append({"role": "assistant", "content": resultado})
        elif entrada.lower() == "resumir":
            assistente.resumir()
        else:
            assistente.responder_chat(entrada)

if __name__ == "__main__":
    main()