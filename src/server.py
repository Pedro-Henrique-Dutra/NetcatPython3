import socket
import argparse

# Argumentos da linha de comando
parser = argparse.ArgumentParser(
    description="Servidor TCP simples"
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

# Criação do socket
server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))
server.listen(5)

print(f"[INFO] Servidor iniciado em {HOST}:{PORT}")

try:
    while True:

        print("[INFO] Aguardando conexões...")

        cliente, endereco = server.accept()

        print(
            f"[INFO] Cliente conectado: "
            f"{endereco[0]}:{endereco[1]}"
        )

        try:
            while True:

                dados = cliente.recv(1024)

                if not dados:
                    print(
                        f"[INFO] Cliente "
                        f"{endereco[0]}:{endereco[1]} "
                        f"desconectado"
                    )
                    break

                mensagem = dados.decode("utf-8")

                print(
                    f"[INFO] Mensagem recebida "
                    f"de {endereco[0]}:{endereco[1]}: "
                    f"{mensagem}"
                )

                resposta = (
                    f"Servidor recebeu: {mensagem}"
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
                f"[ERROR] Erro ao processar "
                f"cliente: {erro}"
            )

        finally:

            cliente.close()

            print(
                f"[INFO] Socket do cliente "
                f"{endereco[0]}:{endereco[1]} "
                f"fechado"
            )

except KeyboardInterrupt:

    print("\n[INFO] Servidor encerrado pelo usuário")

finally:

    server.close()

    print("[INFO] Socket principal encerrado")