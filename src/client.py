import socket
import sys

PORT = 5000

# Verifica se o IP foi informado
if len(sys.argv) < 2:
    print("""
Operação inválida!

Uso:
    python3 client.py <IP>

Exemplo:
    python3 client.py 127.0.0.1
""")
    sys.exit(1)

HOST = sys.argv[1]

try:
    # Cria o socket TCP
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Conectando em {HOST}:{PORT}...")

    # Conecta ao servidor
    cliente.connect((HOST, PORT))

    print("Conectado com sucesso!\n")

    while True:
        msg = input("Digite uma mensagem (ou 'sair'): ")

        if msg.lower() == "sair":
            print("Encerrando conexão...")
            break

        # Envia a mensagem
        cliente.sendall(msg.encode("utf-8"))

        # Recebe a resposta
        resposta = cliente.recv(1024)

        # Se o servidor fechou a conexão
        if not resposta:
            print("O servidor encerrou a conexão.")
            break

        print("Servidor:", resposta.decode("utf-8"))

except ConnectionRefusedError:
    print(f"Não foi possível conectar ao servidor {HOST}:{PORT}.")
    print("Verifique se o servidor está em execução.")

except socket.gaierror:
    print("Endereço IP ou nome de host inválido.")

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

except Exception as erro:
    print(f"Erro: {erro}")

finally:
    try:
        cliente.close()
        print("Conexão encerrada.")
    except NameError:
        pass