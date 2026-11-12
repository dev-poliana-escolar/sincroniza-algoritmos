import socket
import threading
import time
import random

LIMITE_MS = 10000          
DESVIO_CENTRAL_MS = 800    # erro do relógio da central

URNAS = [
    ("Urna 1", 6001, 2500),
    ("Urna 2", 6002, -1800),
    ("Urna 3", 6003, 4200),
    ("Urna 4", 6004, -700),
    ("Urna 5", 6005, 60000),  # um minuto de diferença  
]

def formatar(hora_ms):
    segundos = int(hora_ms // 1000)
    ms = int(hora_ms % 1000)
    return time.strftime("%H:%M:%S", time.localtime(segundos)) + "." + str(ms).zfill(3)

### central
ajuste_central = 0.0

def hora_da_central():
    return time.time() * 1000 + DESVIO_CENTRAL_MS + ajuste_central

def perguntar(porta, mensagem):
    """Manda uma mensagem para uma urna. Devolve (resposta, RTT em ms)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", porta))
    t0 = time.perf_counter()
    s.send(mensagem.encode())
    resposta = s.recv(1024).decode()
    t1 = time.perf_counter()
    s.close()
    return resposta, (t1 - t0) * 1000

def medir_diferencas():
    """Devolve (diferenças, horas): a diferença (ms) de cada urna para a central,
    compensando o RTT/2, e a hora que cada urna informou."""
    diferencas = []
    horas = []
    for nome, porta, _ in URNAS:
        resposta, rtt = perguntar(porta, "HORA?")
        hora_informada = float(resposta)
        hora_urna = hora_informada + rtt / 2
        diferencas.append(hora_urna - hora_da_central())
        horas.append(hora_informada)
    return diferencas, horas

### urna
def urna(porta, desvio_ms):
    ajuste_ms = 0.0

    def hora_da_urna():
        return time.time() * 1000 + desvio_ms + ajuste_ms

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("127.0.0.1", porta))
    servidor.listen()

    while True:
        conexao, _ = servidor.accept()
        mensagem = conexao.recv(1024).decode() #espera mensagem da central

        if mensagem == "HORA?":
            conexao.send(str(hora_da_urna()).encode())
        elif mensagem.startswith("AJUSTAR:"):
            ajuste_ms += float(mensagem.split(":")[1])
            conexao.send(b"OK")
        elif mensagem == "VOTAR":
            candidato = random.choice(["11", "20", "33", "40", "BRANCO"])
            conexao.send(f"{candidato}|{formatar(hora_da_urna())}".encode())

        conexao.close()


### liga as urnas
for nome, porta, desvio in URNAS:
    threading.Thread(target=urna, args=(porta, desvio), daemon=True).start()
time.sleep(0.5)

antes, horas_antes = medir_diferencas()

### calcular media
soma, quantidade = 0.0, 1
descartadas = []
for (nome, _, _), dif in zip(URNAS, antes):
    if abs(dif) > LIMITE_MS:
        descartadas.append(nome)
    else:
        soma += dif
        quantidade += 1
media = soma / quantidade

for (nome, porta, _), dif in zip(URNAS, antes):
    perguntar(porta, f"AJUSTAR:{media - dif:.3f}")
ajuste_central = media

# resultado do ajuste
depois, horas_depois = medir_diferencas()

# registrar voto
votos = [perguntar(porta, "VOTAR")[0].split("|") for _, porta, _ in URNAS]

## saida
print("\n=== RELOGIOS DAS URNAS === \n")
print(f"{'Urna':<8}{'Hora ANTES':<14}{'Hora DEPOIS':<14}{'Erro antes':>11}{'Erro depois':>13}   Voto")
print("-" * 80)
for i, (nome, _, _) in enumerate(URNAS):
    candidato, hora_voto = votos[i]
    print(f"{nome:<8}{formatar(horas_antes[i]):<14}{formatar(horas_depois[i]):<14}"
          f"{antes[i]:>+9.1f}ms{depois[i]:>+11.3f}ms   {candidato} às {hora_voto}")
print("-" * 80)

if descartadas:
    print(f"({', '.join(descartadas)} ficou fora da média por ter erro muito grande)")
print(f"Maior diferença após sincronizar: {max(abs(d) for d in depois):.3f} ms\n")