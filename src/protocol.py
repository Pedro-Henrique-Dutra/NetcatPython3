import os
import subprocess

BUFFER_SIZE = 1024

MSG = "MSG:"
CMD = "CMD:"
FILE = "FILE:"
GET = "GET:"


def process_msg(texto, endereco):

    print(
        f"[INFO] Mensagem recebida "
        f"de {endereco[0]}:{endereco[1]}: "
        f"{texto}"
    )

    return f"Servidor recebeu: {texto}"


def process_cmd(comando, cwd, endereco):

    print(
        f"[INFO] Comando recebido "
        f"de {endereco[0]}:{endereco[1]}: "
        f"{comando}"
    )

    if comando == "pwd":

        return cwd, cwd

    elif comando.startswith("cd "):

        destino = comando[3:].strip()

        novo_caminho = os.path.abspath(
            os.path.join(cwd, destino)
        )

        if os.path.isdir(novo_caminho):

            cwd = novo_caminho

            return (
                f"Diretório alterado para:\n{cwd}",
                cwd
            )

        return (
            "Diretório não encontrado",
            cwd
        )

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

        resposta = "Comando inexistente"

    return resposta, cwd


def process_file(partes, cliente, cwd):

    if len(partes) != 3:

        return "ERROR: cabeçalho FILE inválido"

    nome_arquivo = partes[1]

    tamanho = int(partes[2])

    print(
        f"[INFO] Recebendo arquivo "
        f"{nome_arquivo}"
    )

    cliente.send(b"READY")

    recebido = 0

    os.makedirs("uploads", exist_ok=True)

    caminho_arquivo = os.path.join(
        "uploads",
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

            arquivo.write(bloco)

            recebido += len(bloco)

    return (
        f"Arquivo {nome_arquivo} "
        f"recebido com sucesso"
    )