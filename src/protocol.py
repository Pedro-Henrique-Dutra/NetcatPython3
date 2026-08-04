import os
import subprocess

# ==========================
# Constantes
# ==========================

BUFFER_SIZE = 1024

msg = "MSG:"
cmd = "CMD:"
arquivo = "FILE:"

# ==========================
# Funções de processamento
# ==========================
def process_msg(texto, endereco):

    print(
        f"[INFO] Mensagem recebida "
        f"de {endereco[0]}:{endereco[1]}: "
        f"{texto}"
    )

    return (
        f"Servidor recebeu: {texto}"
    )
def process_cmd(
    comando,
    cwd,
    endereco
):

    print(
        f"[INFO] Comando recebido "
        f"de {endereco[0]}:{endereco[1]}: "
        f"{comando}"
    )

# ==========================
#  Comando pwd
# ==========================
    if comando == "pwd":

        return cwd, cwd
# ==========================
# Comando cd
# ==========================
    elif comando.startswith("cd "):

        destino = comando[3:].strip()

        novo_caminho = os.path.abspath(
            os.path.join(
                cwd,
                destino
            )
        )

        if os.path.isdir(
            novo_caminho
        ):

            cwd = novo_caminho

            return (
                f"Diretório alterado para:\n{cwd}",
                cwd
            )

        return (
            "Diretório não encontrado",
            cwd
        )
# ==========================
# Demais comandos
# ==========================
    try:

        resultado = subprocess.run(
            comando.split(),
            cwd=cwd,
            capture_output=True,
            text=True
        )

        if resultado.returncode == 0:

            resposta = (
                resultado.stdout
                if resultado.stdout
                else "Comando executado com sucesso"
            )

        else:

            resposta = (
                resultado.stderr
                if resultado.stderr
                else "Erro ao executar comando"
            )

    except FileNotFoundError:

        resposta = (
            "Comando inexistente"
        )

    return resposta, cwd

def process_file(
    partes,
    cliente,
    cwd
):

    if len(partes) != 3:

        return (
            "ERROR: cabeçalho FILE inválido"
        )

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

    caminho_arquivo = os.path.join(
        cwd,
        f"recebido_{nome_arquivo}"
    )

    with open(
        caminho_arquivo,
        "wb"
    ) as arquivo:

        while recebido < tamanho:

            bloco = cliente.recv(
                BUFFER_SIZE
            )

            arquivo.write(
                bloco
            )

            recebido += len(
                bloco
            )

    return (
        f"Arquivo {nome_arquivo} "
        f"recebido com sucesso"
    )

def handle_client(
    cliente,
    endereco
):

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

            # MSG

            if mensagem.startswith(msg):

                texto = mensagem[4:]

                resposta = process_msg(
                    texto,
                    endereco
                )

            # CMD

            elif mensagem.startswith(cmd):

                comando = (
                    mensagem[4:]
                    .strip()
                )

                resposta, cwd = (
                    process_cmd(
                        comando,
                        cwd,
                        endereco
                    )
                )

            # FILE

            elif mensagem.startswith(arquivo):

                partes = (
                    mensagem.split(":")
                )

                resposta = (
                    process_file(
                        partes,
                        cliente,
                        cwd
                    )
                )

            else:

                resposta = (
                    "ERROR: tipo de mensagem desconhecido"
                )

            cliente.send(
                resposta.encode(
                    "utf-8"
                )
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
