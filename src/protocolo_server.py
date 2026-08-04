import socket
import argparse
import threading
from protocol import *

# ==========================
# Argumentos
# ==========================

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

#===========================
# Configuração do servidor
#===========================
HOST = "0.0.0.0"
PORT = args.port

# ==========================
# Socket principal
# ==========================

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