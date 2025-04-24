import os
import subprocess
import shlex
import readline #seta pra cima
from datetime import datetime

HISTORY_LOG = ".mini_shell_history.log"

def salvar_comando_log(comando, saida, erro):
    with open(HISTORY_LOG, "a") as f:
        f.write(f"\n[{datetime.now()}] $ {comando}\n")
        if saida:
            f.write(saida)
        if erro:
            f.write(erro)
def executar_pipeline(comando_input):
    comandos = [shlex.split(cmd.strip()) for cmd in comando_input.split('|')]
    processos = []
    anterior = None

    for i, cmd in enumerate(comandos):
        if i == 0:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            p = subprocess.Popen(cmd, stdin=anterior.stdout, stdout=subprocess.PIPE, stderr= subprocess.PIPE, text=True)
        anterior = p
        processos.append(p)
        
    saida, erro = processos[-1].communicate()
    return saida, erro

def tratar_redirecionamento(comando_input):
    if ">>" in comando_input:
        partes = comando_input.split(">>")
        comando = partes[0].strip()
        arquivo = partes[1].strip()
        saida, erro = executar_pipeline(comando)
        with open(arquivo, "a") as f:
            f.write(saida)
        return "", erro

    elif ">" in comando_input:
        partes = comando_input.split(">")
        comando = partes[0].strip()
        arquivo = partes[1].strip()
        saida, erro = executar_pipeline(comando)
        with open(arquivo, "w") as f:
            f.write(saida)
        return "", erro
    else:
        return executar_pipeline(comando_input)
    
def imprimir_com_cor(texto, cor):
    cores = {
            "verde": "\033[92m",
            "vermelho": "\033[91m",
            "reset" : "\033[0m"
    }
    print(f"{cores[cor]}{texto}{cores['reset']}", end="")

def main():
    print("Mini shell v3 - com um + a mais.")
    while True:
            try:
                cwd = os.getcwd()
                comando_input = input(f"{cwd} >> ")


                if not comando_input.strip():
                    continue

                if comando_input.strip() in ["exit", "sair", "quit"]:
                    print("saindo do mini shell")
                    break

                tokens = shlex.split(comando_input)
                if tokens[0] == "cd":
                    if len(tokens) > 1:
                        try: 
                            os.chdir(tokens[1])
                        except FileNotFoundError:
                            imprimir_com_cor("diretorio nao encontrado")
                    else:
                        os.chdir(os.path.expanduser("~"))
                    continue

                saida, erro = tratar_redirecionamento(comando_input)

                if saida:
                    imprimir_com_cor(saida, "verde")

                if erro:
                    imprimir_com_cor(erro, "vermelho")

                salvar_comando_log(comando_input, saida, erro)

            except KeyboardInterrupt:
                print("\n INterrompido com ctrl c")
            except EOFError:
                 print("\n EOF detectado (ctrl + d), saindo..")
                 break
            except Exception as e:
                imprimir_com_cor(f" Erro inesperado {e}\n", "vermelho")

if __name__ == "__main__":
    main()
