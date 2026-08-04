import socket
import argparse
import threading
import os

from protocol import (
    BUFFER_SIZE,
    MSG,
    CMD,
    FILE,
    process_msg,
    process_cmd,
    process_file
)


def handle_client(cliente, endereco):

    print(
        f"[INFO] Cliente conectado: "
        f"{endereco[0]}:{endereco[1]}"
    )

    cwd = os.getcwd()

    try:

        while True:

            dados = cliente.recv(
                BUFFER_SIZE
            )

            if not dados:

                print(
                    f"[INFO] Cliente "
                    f"{endereco[0]}:{endereco[1]} "
                    f"desconectado"
                )

                break

            try:

                mensagem = dados.decode(
                    "utf-8"
                )

            except UnicodeDecodeError:

                print(
                    "[WARNING] Dados binários "
                    "recebidos fora do protocolo"
                )

                continue

            if mensagem.startswith(MSG):

                texto = mensagem[
                    len(MSG):
                ]

                resposta = process_msg(
                    texto,
                    endereco
                )

            elif mensagem.startswith(CMD):

                comando = mensagem[
                    len(CMD):
                ].strip()

                resposta, cwd = process_cmd(
                    comando,
                    cwd,
                    endereco
                )

            elif mensagem.startswith(FILE):

                partes = mensagem.split(":")

                resposta = process_file(
                    partes,
                    cliente,
                    cwd
                )

            else:

                resposta = (
                    "ERROR: tipo de mensagem desconhecido"
                )

            cliente.send(
                resposta.encode("utf-8")
            )

    except ConnectionResetError:

        print(
            f"[WARNING] Conexão encerrada "
            f"abruptamente por "
            f"{endereco[0]}:{endereco[1]}"
        )

    except Exception as erro:

        print(
            f"[ERROR] {erro}"
        )

    finally:

        cliente.close()

        print(
            f"[INFO] Socket do cliente "
            f"{endereco[0]}:{endereco[1]} "
            f"fechado"
        )


parser = argparse.ArgumentParser(
    description="Servidor TCP"
)

parser.add_argument(
    "-p",
    "--port",
    type=int,
    required=True,
    help="Porta que será escutada"
)

args = parser.parse_args()

HOST = "0.0.0.0"
PORT = args.port

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (HOST, PORT)
)

server.listen(5)

print(
    f"[INFO] Servidor iniciado "
    f"em {HOST}:{PORT}"
)

try:

    while True:

        print(
            "[INFO] Aguardando conexões..."
        )

        cliente, endereco = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(cliente, endereco),
            daemon=True
        )

        thread.start()

except KeyboardInterrupt:

    print(
        "\n[INFO] Servidor encerrado pelo usuário"
    )

finally:

    server.close()

    print(
        "[INFO] Socket principal encerrado"
    )