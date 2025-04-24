import os
import subprocess
import ollama

# 🧠 Memória da conversa
conversa = [
    {
        "role": "system",
        "content": (
            "Você é um assistente com acesso ao terminal Linux. "
            "Pode executar comandos reais usando 'cmd: <comando>' "
            "ou criar arquivos usando 'file: <caminho>' seguido por 'conteúdo:'. "
            "Lembre-se do que foi feito anteriormente e responda de forma clara."
        )
    }
]

# 📁 Execução de comandos do terminal
def executar_comando_terminal(comando):
    try:
        resultado = subprocess.check_output(
            comando, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar: {e.output}"

# 📂 Criação de arquivos
def criar_arquivo(caminho, conteudo):
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return f"✅ Arquivo '{caminho}' criado com sucesso."
    except Exception as e:
        return f"❌ Erro ao criar arquivo: {str(e)}"

# 🔁 Loop principal
while True:
    user_input = input("\n🧍 Você: ")
    conversa.append({"role": "user", "content": user_input})

    # ⏳ Streaming de resposta
    print("\n🤖 Mistral: ", end="", flush=True)
    stream = ollama.chat(model='mistral', messages=conversa, stream=True)

    texto = ""
    for parte in stream:
        token = parte['message']['content']
        print(token, end="", flush=True)
        texto += token

    print()  # Nova linha depois da resposta

    # 🧠 Adiciona resposta ao histórico
    conversa.append({"role": "assistant", "content": texto})

    # 🛠️ Checa se é criação de arquivo
    if texto.startswith("file:"):
        try:
            linhas = texto.splitlines()
            caminho = linhas[0].replace("file:", "").strip()
            idx_conteudo = next(i for i, l in enumerate(linhas) if l.startswith("conteúdo:"))
            conteudo = "\n".join(linhas[idx_conteudo + 1:])
            resultado = criar_arquivo(caminho, conteudo)
        except Exception as e:
            resultado = f"❌ Erro ao interpretar comando de criação de arquivo: {str(e)}"

        print(f"\n📁 Resultado da criação:\n{resultado}")
        conversa.append({"role": "user", "content": f"O resultado da criação foi:\n{resultado}"})

    # 💻 Checa se é comando de terminal
    elif texto.startswith("cmd:"):
        comando = texto.replace("cmd:", "").strip()
        resultado = executar_comando_terminal(comando)
        print(f"\n📥 Resultado do comando:\n{resultado}")
        conversa.append({"role": "user", "content": f"O resultado do comando '{comando}' foi:\n{resultado}"})

    # 🧾 Caso seja só conversa normal, já está no histórico
