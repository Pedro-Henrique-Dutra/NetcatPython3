
import socket
import argparse
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

# Argumentos da linha de comando
parser = argparse.ArgumentParser(
    description="Cliente TCP com protocolo simples"
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
        f"[INFO] Conectando em {HOST}:{PORT}"
    )

    cliente.connect((HOST, PORT))

    print(
        "[INFO] Conexão estabelecida com sucesso"
    )

    while True:

        tipo = input(
            "\n[INPUT] Escolha (msg/cmd/file/sair/get/shell): "
        ).lower()

        if tipo == "sair":

            print(
                "[INFO] Encerrando conexão..."
            )

            break

        elif tipo == "msg":

            texto = input(
                "[MSG] Digite a mensagem: "
            )

            mensagem = (
                f"{MSG}{texto}"
            )
            # Envia para o servidor
            cliente.sendall(
                mensagem.encode("utf-8")
            )

        elif tipo == "shell":

            print(
                "[INFO] Shell interativa iniciada"
            )

            while True:

                comando = input(
                    "shell> "
                )

                if comando.lower() == "exit":

                    break

                mensagem = (
                    f"{CMD}{comando}"
                )

                cliente.sendall(
                    mensagem.encode("utf-8")
                )

                resposta = cliente.recv(
                    BUFFER_SIZE
                )

                print(
                    resposta.decode("utf-8")
                )

            continue
        elif tipo == "cmd":

            comando = input(
                "[CMD] Digite o comando: "
            )

            mensagem = (
                f"{CMD}{comando}"
            )
            # Envia para o servidor
            cliente.sendall(
                mensagem.encode("utf-8")
            )
        elif tipo == "file":
            
            caminho = input(
                "[FILE] Digite o caminho do arquivo: "
            )

            nome_arquivo = os.path.basename(
                caminho
            )

            tamanho = os.path.getsize(
                caminho
            )

            cabecalho = (
                f"FILE:{nome_arquivo}:{tamanho}"
            )

            cliente.sendall(
                cabecalho.encode("utf-8")
            )

            resposta = cliente.recv(BUFFER_SIZE)

            print(
                resposta.decode("utf-8")
            )

            with open(caminho, "rb") as arquivo:

                while True:

                    bloco = arquivo.read(BUFFER_SIZE)

                    if not bloco:
                        break

                    cliente.sendall(bloco)

            print(
                "[INFO] Arquivo enviado"
            )
            resposta = cliente.recv(BUFFER_SIZE)
            print(
                f"[SERVER] {resposta.decode('utf-8')}"
            )
            continue
        elif tipo == "get":

            nome_arquivo = input(
                "[GET] Nome do arquivo: "
            )

            mensagem = (
                f"{GET}{nome_arquivo}"
            )

            cliente.sendall(
                mensagem.encode("utf-8")
            )

            cabecalho = cliente.recv(
                BUFFER_SIZE
            ).decode("utf-8")

            # Servidor retornou erro
            if cabecalho.startswith("ERROR"):

                print(
                    f"[SERVER] {cabecalho}"
                )

                continue

            # Verifica se o cabeçalho recebido é FILE
            if not cabecalho.startswith(FILE):

                print(
                    "[ERROR] Resposta inesperada do servidor"
                )

                continue

            partes = cabecalho.split(":")

            if len(partes) != 3:

                print(
                    "[ERROR] Cabeçalho FILE inválido"
                )

                continue

            nome_recebido = partes[1]

            tamanho = int(
                partes[2]
            )

            print(
                f"[INFO] Recebendo arquivo "
                f"{nome_recebido} "
                f"({tamanho} bytes)"
            )

            cliente.send(
                b"READY"
            )

            recebido = 0

            with open(
                f"download_{nome_recebido}",
                "wb"
            ) as arquivo:

                while recebido < tamanho:

                    bloco = cliente.recv(
                        BUFFER_SIZE
                    )

                    if not bloco:
                        break

                    arquivo.write(
                        bloco
                    )

                    recebido += len(
                        bloco
                    )

            print(
                f"[INFO] Arquivo "
                f"{nome_recebido} "
                f"baixado com sucesso"
            )

            continue
        else:

            print(
                "[WARNING] Tipo inválido"
            )

            continue

        

        # Recebe resposta
        resposta = cliente.recv(BUFFER_SIZE)
        

        if not resposta:

            print(
                "[WARNING] O servidor encerrou a conexão"
            )

            break

        print(
            f"[SERVER] {resposta.decode('utf-8')}"
        )

except ConnectionRefusedError:

    print(
        f"[ERROR] Não foi possível conectar em {HOST}:{PORT}"
    )

except socket.gaierror:

    print(
        "[ERROR] Endereço IP inválido"
    )

except KeyboardInterrupt:

    print(
        "\n[INFO] Cliente encerrado pelo usuário"
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