import socket
import argparse

# Argumentos da linha de comando
parser = argparse.ArgumentParser(
    description="Cliente TCP simples"
)

parser.add_argument(
    "--host",
    type=str,
    default="127.0.0.1",
    help="IP do servidor"
)

parser.add_argument(
    "-p",
    "--port",
    type=int,
    required=True,
    help="Porta do servidor"
)

args = parser.parse_args()

HOST = args.host
PORT = args.port

try:

    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    print(
        f"[INFO] Conectando em "
        f"{HOST}:{PORT}"
    )

    cliente.connect(
        (HOST, PORT)
    )

    print(
        f"[INFO] Conexão estabelecida "
        f"com sucesso"
    )

    while True:

        mensagem = input(
            "\n[INPUT] Digite uma mensagem "
            "(ou 'sair'): "
        )

        if mensagem.lower() == "sair":

            print(
                "[INFO] Encerrando conexão..."
            )

            break

        cliente.sendall(
            mensagem.encode("utf-8")
        )

        resposta = cliente.recv(1024)

        if not resposta:

            print(
                "[WARNING] O servidor "
                "encerrou a conexão"
            )

            break

        print(
            f"[SERVER] "
            f"{resposta.decode('utf-8')}"
        )

except ConnectionRefusedError:

    print(
        f"[ERROR] Não foi possível "
        f"conectar ao servidor "
        f"{HOST}:{PORT}"
    )

except socket.gaierror:

    print(
        "[ERROR] Endereço IP inválido"
    )

except KeyboardInterrupt:

    print(
        "\n[INFO] Cliente encerrado "
        "pelo usuário"
    )

except Exception as erro:

    print(
        f"[ERROR] {erro}"
    )

finally:

    try:

        cliente.close()

        print(
            "[INFO] Socket encerrado"
        )

    except NameError:
        pass