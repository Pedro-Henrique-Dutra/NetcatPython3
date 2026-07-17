import socket

HOST = "0.0.0.0"  # Escuta em todas as interfaces
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"Servidor iniciado em {HOST}:{PORT}")

while True:
    cliente, endereco = server.accept()

    print(f"\nCliente conectado!")
    print(f"IP: {endereco[0]}")
    print(f"Porta: {endereco[1]}")

    while True:
        dados = cliente.recv(1024)

        if not dados:
            print("Cliente desconectado.")
            break

        mensagem = dados.decode("utf-8")
        print(f"Mensagem recebida: {mensagem}")

        resposta = f"Servidor recebeu: {mensagem}"
        cliente.send(resposta.encode("utf-8"))

    cliente.close()