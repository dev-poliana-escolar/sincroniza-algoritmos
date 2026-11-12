import socket   
import time    

PORTA = 5000  

#cria um socket TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("0.0.0.0", PORTA))

# espera conexão
servidor.listen()
print("Servidor de tempo ligado na porta", PORTA)
print("Esperando caixas eletrônicos... (Ctrl+C para parar)")

def hora_atual_ms():
    return time.time() * 1000

while True:
    conexao, endereco = servidor.accept()
    print("Caixa conectado:", endereco)

    while True:
        pedido = conexao.recv(1024)
        if not pedido:
            break

        resposta = str(hora_atual_ms())
        conexao.send(resposta.encode())

    conexao.close()
    print("Caixa desconectado:", endereco)