import json
import subprocess
from datetime import datetime
import requests
import funcoes

def loop_interacao():
    print("\n🌐 IA Modular Ativa. Digite 'sair' para encerrar.")
    print("💬 Fale normalmente ou use: cmd:<comando> para comandos do terminal.\n")

    while True:
        try:
            user_input = input("Você > ").strip()
        except KeyboardInterrupt:
            print("\nEncerrado manualmente.")
            break

        if user_input.lower() == "sair":
            print("👋 Encerrando...")
            break

        if user_input.startswith("cmd:"):
            comando = user_input.replace("cmd:", "").strip()
            resultado = funcoes.executar_comando(comando)
            print("🛠️  Terminal:\n", resultado)
            funcoes.salvar_log(user_input, resultado, tipo="execucao_terminal")
        else:
            resposta = funcoes.gerar_resposta_ia(user_input)
            print("🤖 Bot:", resposta)
            funcoes.salvar_log(user_input, resposta, tipo="resposta_ia")

# Iniciar loop
if __name__ == "__main__":
    loop_interacao()

