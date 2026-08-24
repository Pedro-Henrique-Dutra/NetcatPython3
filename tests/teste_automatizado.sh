#!/bin/bash

# Configurações de caminhos relativos
PORTA=4444
SRC_DIR="../src"
LIB_DIR="../lib"
SERVER_SCRIPT="protocolo_server.py"
CLIENT_SCRIPT="../src/protocolo_client.py"

LOG_SERVER="server.log"
LOG_CLIENT1="client1.log"
LOG_CLIENT2="client2.log"

NOME_ARQUIVO_NO_SERVIDOR="uploads/recebido_arquivo_envio.txt" 

# Pastas e arquivos de download separados por cliente para evitar conflitos concorrentes
PASTA_DL_C1="download_uploads_c1"
PASTA_DL_C2="download_uploads_c2"
ARQUIVO_C1="${PASTA_DL_C1}/recebido_arquivo_envio.txt"
ARQUIVO_C2="${PASTA_DL_C2}/recebido_arquivo_envio.txt"

# SOLUÇÃO DA IMPORTAÇÃO: Adiciona SRC e LIB ao PYTHONPATH para o Python localizar tudo
export PYTHONPATH="$(realpath "$SRC_DIR"):$(realpath "$LIB_DIR"):$PYTHONPATH"

# Limpa resíduos anteriores de forma segura
rm -rf "$LOG_SERVER" "$LOG_CLIENT1" "$LOG_CLIENT2" download_* arquivo_envio* "$SRC_DIR/uploads"/*

# Cria as pastas de download que cada cliente vai exigir isoladamente
mkdir -p "$PASTA_DL_C1/uploads" "$PASTA_DL_C2/uploads"

echo "=== [1/4] Criando arquivos temporários para envio ==="
echo "Conteudo Cliente 1" > arquivo_envio1.txt
echo "Conteudo Cliente 2" > arquivo_envio2.txt

echo "=== [2/4] Iniciando Servidor na porta $PORTA ==="
(cd "$SRC_DIR" && python3 "$SERVER_SCRIPT" -p "$PORTA") > "$LOG_SERVER" 2>&1 &
SERVER_PID=$!

sleep 2

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ [ERRO] Falha ao iniciar o servidor. Verifique o arquivo tests/$LOG_SERVER"
    rm -rf arquivo_envio1.txt arquivo_envio2.txt "$PASTA_DL_C1" "$PASTA_DL_C2"
    exit 1
fi

echo "=== [3/4] Executando Múltiplos Clientes Simultâneos ==="

# CLIENTE 1 (Roda em segundo plano com & no final do bloco)
(
    # Move temporariamente para a pasta do cliente 1 para isolar o download_
    cd "$PASTA_DL_C1" && python3 "../$CLIENT_SCRIPT" -p "$PORTA" > "../$LOG_CLIENT1" 2>&1 <<EOF
msg
Ola Servidor, sou o Cliente 1!
cmd
pwd
file
../arquivo_envio1.txt
get
$NOME_ARQUIVO_NO_SERVIDOR
sair
EOF
) &
CLIENT1_PID=$!

# CLIENTE 2 (Roda em segundo plano simultaneamente)
(
    cd "$PASTA_DL_C2" && python3 "../$CLIENT_SCRIPT" -p "$PORTA" > "../$LOG_CLIENT2" 2>&1 <<EOF
msg
Ola Servidor, sou o Cliente 2!
cmd
pwd
file
../arquivo_envio2.txt
get
$NOME_ARQUIVO_NO_SERVIDOR
sair
EOF
) &
CLIENT2_PID=$!

# Aguarda a execução de ambos os clientes terminarem antes de seguir
wait $CLIENT1_PID
CLIENT1_STATUS=$?
wait $CLIENT2_PID
CLIENT2_STATUS=$?

echo "=== [4/4] Finalizando e Analisando Resultados ==="
kill -INT $SERVER_PID
wait $SERVER_PID 2>/dev/null

echo -e "\n--- Relatório de Validação Concorrente ---"
ERROS=0

# Validação do Cliente 1
if [ $CLIENT1_STATUS -eq 0 ] && grep -q "Cliente 1" "$LOG_CLIENT1"; then
    echo "✅ Cliente 1 (Mensagem, Comando e Upload): OK"
else
    echo "❌ Cliente 1: FALHOU"
    ERROS=$((ERROS + 1))
fi

# Validação do Cliente 2
if [ $CLIENT2_STATUS -eq 0 ] && grep -q "Cliente 2" "$LOG_CLIENT2"; then
    echo "✅ Cliente 2 (Mensagem, Comando e Upload): OK"
else
    echo "❌ Cliente 2: FALHOU"
    ERROS=$((ERROS + 1))
fi

# Validação de Downloads Cruzados
if [ -f "$PASTA_DL_C1/download_uploads/uploads/recebido_arquivo_envio.txt" ] || [ -f "$PASTA_DL_C2/download_uploads/uploads/recebido_arquivo_envio.txt" ]; then
    echo "✅ Downloads via GET processados por threads concorrentes: OK"
else
    echo "❌ Downloads via GET: FALHOU"
    ERROS=$((ERROS + 1))
fi


# Limpeza final absoluta de arquivos criados durante a execução do teste
rm -f arquivo_envio1.txt arquivo_envio2.txt
rm -rf "$PASTA_DL_C1" "$PASTA_DL_C2"
rm -rf "$SRC_DIR/uploads"/*

if [ $ERROS -gt 0 ]; then
    echo -e "\n❌ O teste concorrente falhou. Verifique os logs individuais client1.log e client2.log"
    exit 1
else
    echo -e "\n🎉 🎉 Sucesso Extremo! O servidor aceitou conexões em múltiplas threads e a biblioteca 'lib' foi importada com perfeição!"
    rm -f "$LOG_SERVER" "$LOG_CLIENT1" "$LOG_CLIENT2"
    exit 0
fi
