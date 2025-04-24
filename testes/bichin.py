import subprocess
import ollama

# Histórico da conversa e comandos executados
conversa = [
    {"role": "system", "content": "Você é um assistente com acesso ao terminal Linux. Use 'cmd:' para comandos. Lembre-se do que foi executado e seus resultados."}
]
comandos_executados = {}

def executar_comando_terminal(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, text=True)
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar: {e.output}"

while True:
    user_input = input("Você: ")
    conversa.append({"role": "user", "content": user_input})

   #resposta = ollama.chat(model='mistral', messages=conversa)
    stream = ollama.chat(model='mistral', messages=conversa, stream=True)

    resposta_texto = ""
    for parte in stream:
        token = parte['message']['content']
        print(token, end="", flush=True)
        resposta_texto += token

    texto = resposta['message']['content']
    print(f"\n🤖 Mistral: {texto}")

    if texto.startswith("cmd:"):
        comando = texto.replace("cmd:", "").strip()
        resultado = executar_comando_terminal(comando)
        print(f"\n📥 Resultado do comando:\n{resultado}\n")

        # Armazena comando e resultado
        comandos_executados[comando] = resultado

        # Adiciona o resultado ao contexto para memória da IA
        conversa.append({"role": "assistant", "content": texto})
        conversa.append({"role": "user", "content": f"O resultado do comando '{comando}' foi:\n{resultado}"})
    else:
        # Apenas resposta comum da IA, sem execução
        conversa.append({"role": "assistant", "content": texto})
