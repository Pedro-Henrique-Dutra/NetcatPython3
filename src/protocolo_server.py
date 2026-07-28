
import socket
import argparse
import threading

# Prefixos do protocolo
TIPOS = {
    "msg": "MSG:",
    "cmd": "CMD:",
    "file": "FILE:"
}


# Função para tratar o cliente
def handle_client(cliente,endereco):
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
            try:
                mensagem = dados.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if mensagem.startswith(TIPOS["msg"]):
                texto = mensagem[4:]
                print(
                    f"[INFO] Mensagem recebida "
                    f"de {endereco[0]}:{endereco[1]}: "
                    f"{texto}"
                )

                resposta = (
                    f"Servidor recebeu: {texto}"
                )

            elif mensagem.startswith(TIPOS["cmd"]):
                print(
                    f"[INFO] Comando recebido "
                    f"de {endereco[0]}:{endereco[1]}: "
                    f"{mensagem}"
                )
    
                resposta = (
                    f"Servidor recebeu: {mensagem}"
                )
            elif mensagem.startswith(TIPOS["file"]):
                
                partes = mensagem.split(":")

                nome_arquivo = partes[1]

                tamanho = int(
                    partes[2]
                )

                print(
                    f"[INFO] Recebendo arquivo "
                    f"{nome_arquivo}"
                )

                cliente.send(
                    b"READY"
                )

                recebido = 0

                with open(
                    f"recebido_{nome_arquivo}",
                    "wb"
                ) as arquivo:

                    while recebido < tamanho:

                        bloco = cliente.recv(1024)

                        arquivo.write(bloco)

                        recebido += len(
                            bloco
                        )

                resposta = (
                    f"Arquivo {nome_arquivo} "
                    f"recebido com sucesso"
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

# Permite reutilizar a porta logo após encerrar o servidor
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

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
            daemon= True
        )

        thread.start()
        

except KeyboardInterrupt:

    print("\n[INFO] Servidor encerrado pelo usuário")

finally:

    server.close()

    print("[INFO] Socket principal encerrado")