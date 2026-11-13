import socket
import time

IP_SERVIDOR = "127.0.0.1" #localhost
PORTA = 5000
NOME_CAIXA = "Caixa 1"
DESVIO_MS = 60000 # relógio do caixa adiantado 1 min em ms
QUANTIDADE_PEDIDOS = 5 

# simulei um relogio errado, portanto, somo o desvio com o ajuste (que começa em 0))
def hora_do_caixa(ajuste_ms):
    return time.time() * 1000 + DESVIO_MS + ajuste_ms

def formatar(hora_ms):
    segundos = int(hora_ms // 1000)
    milissegundos = int(hora_ms % 1000) 
    texto = time.strftime("%H:%M:%S", time.localtime(segundos))
    return texto + "." + str(milissegundos).zfill(3)

ajuste = 0  
print(f"Hora do caixa ANTES: {formatar(hora_do_caixa(ajuste))}")

caixa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
caixa.connect((IP_SERVIDOR, PORTA))

menor_rtt = None
melhor_correcao = 0

for numero in range(1, QUANTIDADE_PEDIDOS + 1):
    t0 = time.perf_counter()

    caixa.send(b"hora?") # pergunta a hora
    resposta = caixa.recv(1024) # espera a resposta

    t1 = time.perf_counter()

    # RTT = tempo de ida e volta = t1 - t0
    rtt_ms = (t1 - t0) * 1000
    hora_do_servidor = float(resposta.decode())

    hora_certa = hora_do_servidor + rtt_ms / 2
    correcao = hora_certa - hora_do_caixa(0)

    print("Pedido", numero, "-> RTT =", round(rtt_ms, 3), "ms",
          "| correção =", round(correcao, 3), "ms")

    # guarda se esta for a medição com menor RTT
    if menor_rtt is None or rtt_ms < menor_rtt:
        menor_rtt = rtt_ms
        melhor_correcao = correcao

caixa.close()

ajuste = melhor_correcao

print()
print("Menor RTT:", round(menor_rtt, 3), "ms")
print("Correção aplicada:", round(ajuste, 3), "ms")
print("Hora do caixa DEPOIS:", formatar(hora_do_caixa(ajuste)))
print()

#simulei transações no caixa para ver a hora depois do ajuste
print("Transação:", NOME_CAIXA, "| SAQUE     R$ 200,00 |",
      formatar(hora_do_caixa(ajuste)))
print("Transação:", NOME_CAIXA, "| DEPÓSITO  R$ 500,00 |",
      formatar(hora_do_caixa(ajuste)))

erro = hora_do_caixa(ajuste) - time.time() * 1000 #comparei com a hora do meu computador
print()
print("Diferença final para a hora real:", round(erro, 3), "ms")