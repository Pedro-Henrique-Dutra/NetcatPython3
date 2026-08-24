import socket
import argparse
import threading
import os

from protocol import (
    BUFFER_SIZE,
    MSG,
    CMD,
    GET,
    FILE,
    process_msg,
    process_cmd,
    process_file
)


def handle_client(cliente, endereco):
    # Correção: Formatação adequada para tupla de endereço (IP:PORTA)
    print(f"[INFO] Cliente conectado: {endereco[0]}:{endereco[1]}")

    cwd = os.getcwd()

    try:
        while True:
            dados = cliente.recv(BUFFER_SIZE)

            if not dados:
                print(f"[INFO] Cliente {endereco[0]}:{endereco[1]} desconectado")
                break

            try:
                mensagem = dados.decode("utf-8")
            except UnicodeDecodeError:
                print("[WARNING] Dados binários recebidos fora do protocolo")
                continue
            
            # --- CONDICIONAL 1: MENSAGEM DE TEXTO (MSG) ---
            if mensagem.startswith(MSG):
                texto = mensagem[len(MSG):]
                resposta = process_msg(texto, endereco)

            # --- CONDICIONAL 2: COMANDO REMOTO (CMD) ---
            elif mensagem.startswith(CMD):
                comando = mensagem[len(CMD):].strip()
                # Mantém o estado do diretório atualizado na sessão do cliente
                resposta, cwd = process_cmd(comando, cwd, endereco)

            # --- CONDICIONAL 3: UPLOAD DE ARQUIVO (FILE) ---
            elif mensagem.startswith(FILE):
                partes = mensagem.split(":")
                resposta = process_file(partes, cliente, cwd)

            # --- CONDICIONAL 4: DOWNLOAD DE ARQUIVO (GET) ---
            elif mensagem.startswith(GET):
                nome_arquivo = mensagem[len(GET):].strip()

                # Como você sempre enviará o caminho absoluto, expandimos o '~' se houver
                # e pegamos o caminho absoluto real e normalizado do Linux
                caminho_arquivo = os.path.abspath(os.path.expanduser(nome_arquivo))

                if not os.path.exists(caminho_arquivo):
                    resposta = f"ERROR: arquivo não encontrado em {caminho_arquivo}"
                    cliente.send(resposta.encode("utf-8"))
                    continue

                tamanho = os.path.getsize(caminho_arquivo)

                # CORREÇÃO CRUCIAL PARA O CLIENTE: Extraímos apenas o nome base (ex: "foto.png")
                # Se enviássemos o caminho absoluto no cabeçalho, o cliente tentaria criar
                # subpastas locais inexistentes (como download_/home/kiritos/...) e quebraria.
                nome_base_envio = os.path.basename(caminho_arquivo)

                cabecalho = f"FILE:{nome_base_envio}:{tamanho}"
                cliente.send(cabecalho.encode("utf-8"))

                ack = cliente.recv(BUFFER_SIZE)
                if ack != b"READY":
                    continue

                # Transmissão binária do arquivo em blocos (chunks)
                with open(caminho_arquivo, "rb") as arquivo:
                    while True:
                        bloco = arquivo.read(BUFFER_SIZE)
                        if not bloco:
                            break
                        cliente.sendall(bloco)

                print(f"[INFO] Arquivo {caminho_arquivo} enviado com sucesso")
                continue  # O fluxo do GET termina aqui e volta a escutar o cliente

            # --- TRATAMENTO DE TIPOS DESCONHECIDOS ---
            else:
                resposta = "ERROR: tipo de mensagem desconhecido"

            # Envia a resposta final para as condicionais MSG, CMD e FILE
            cliente.send(resposta.encode("utf-8"))

    except ConnectionResetError:
        print(f"[WARNING] Conexão encerrada abruptamente por {endereco[0]}:{endereco[1]}")
    except Exception as erro:
        print(f"[ERROR] Ocorreu uma falha: {erro}")
    finally:
        cliente.close()
        print(f"[INFO] Socket do cliente {endereco[0]}:{endereco[1]} fechado")


# --- INICIALIZAÇÃO DO SERVIDOR ---
parser = argparse.ArgumentParser(description="Servidor TCP")
parser.add_argument("-p", "--port", type=int, required=True, help="Porta que será escutada")
args = parser.parse_args()

HOST = "0.0.0.0"
PORT = args.port

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"[INFO] Servidor iniciado em {HOST}:{PORT}")

try:
    while True:
        print("[INFO] Aguardando conexões...")
        cliente, endereco = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(cliente, endereco),
            daemon=True
        )
        thread.start()

except KeyboardInterrupt:
    print("\n[INFO] Servidor encerrado pelo usuário")
finally:
    server.close()
    print("[INFO] Socket principal encerrado")
