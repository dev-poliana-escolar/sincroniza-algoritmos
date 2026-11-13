# sincroniza-algoritmos
Laborátorio de atividade sobre algoritmos de sincronização de relógios de Sistemas Distribuidos. São eles, Christian e Berkeley.

## SUMÁRIO
1. [Algoritmo de Christian](#algoritmo-de-christian)
2. [Algoritmo de Berkeley](#algoritmo-de-berkeley)

---

## Algoritmo de Christian
Esse algoritmo é responsável por sincronizar relógios de até dois computadores, sendo um o cliente e outro servidor. Quando o cliente faz a requisição, ele mede o tempo de ida da pergunta até a resposta chegar.
</br></br>
Para a atividade, simulei um caixa eletrónico que faz cinco requisições ao "servidor".

### Como executar?

1. Entre na pasta do projeto:
    ```bash
    cd sincroniza-algoritmos
    ```

1.  Execute o comando que inicia o **servidor** diretamente ou entre na pasta do algoritmo:
    ```bash
    # OPÇÃO 1: executar diretamente
    python3 christian/servidor.py

    # OPÇÃO 2: entrar na pasta
    cd christian 

    python3 servidor.py #execute
    ```

2. Em outro terminal, execute o comando que inicia o **caixa**:
    ```bash
    # OPÇÃO 1
    python3 christian/caixa_eletronico.py

    # OPÇÃO 2
    python3 caixa_eletronico.py #execute se entrou na pasta christian
    ```
> Crtl+C para parar o `servidor.py`

### O que o programa faz?
1. `servidor.py`\
    Após criar um socket, canal por onde se envia e recebe os dados. Teremos o seguinte _loop_:

    ```python
    while True:
    conexao, endereco = servidor.accept() #aceitar a conexão do caixa
    print("Caixa conectado:", endereco)

    while True:
        pedido = conexao.recv(1024) #espera receber o pedido do caixa
        if not pedido: 
            break #se não houver, fechar a conexao do caixa

        resposta = str(hora_atual_ms()) # retorna a hora atual do sistema
        conexao.send(resposta.encode()) 

    conexao.close()
    print("Caixa desconectado:", endereco)
    ```
2. `caixa_eletronico.py`\
    Um caixa que está adiantado em 1 minuto. Contém duas funções: `hora_do_caixa` e `formatar`. A primeira vai retornar a hora atual do caixa e a outra só vai deixar no formato que conhecemos.
    </br></br>
    No laço de repetição acontece o calculo do RTT e a correção da hora.
    ```python
    menor_rtt = None
    melhor_correcao = 0

    for numero in range(1, QUANTIDADE_PEDIDOS + 1):
        t0 = time.perf_counter() # guarda o valor da ida da pergunta
        caixa.send(b"hora?") # o caixa pergunta a hora ao servidor
        resposta = caixa.recv(1024) # espera a resposta

        t1 = time.perf_counter() # guarda o valor da volta

        # RTT = tempo de ida e volta = t1 - t0
        rtt_ms = (t1 - t0) * 1000
        hora_do_servidor = float(resposta.decode()) # vem em byte, entao convertemos

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
    ```

---  

## Algoritmo de Berkeley
Diferente do anterior, o Berkeley pode sincronizar mais de um computador ao mesmo tempo. Basta existir um _servidor central_ que irá balancear os atrasos dos demais.
</br></br>
Para a atividade, simulei uma urna eletrônica. No arquivo, contém 5 urnas, todas estão erradas, inclusive a _central_.

### Como executar?
1. Entre na pasta do projeto:
    ```bash
    cd sincroniza-algoritmos
    ```
1.  Execute o comando que inicia a **urna** diretamente ou entre na pasta do algoritmo:
    ```bash
    # OPÇÃO 1: executar diretamente
    python3 berkeley/urna.py

    # OPÇÃO 2: entrar na pasta
    cd berkeley 

    python3 urna.py #execute
    ```

### O que o programa faz?
1. `urna.py`\
    Diferente do algoritmo anterior (onde o cliente, _caixa eletronico_, pede a hora ao servidor), aqui **a central toma a iniciativa** de perguntar a hora de todas as urnas, calcula a média ignorando desvios absurdos (como a Urna 5) e envia o ajuste individual para cada uma.

    * **Descarte de outliers e cálculo da média (Central):**
      ```python
      soma, quantidade = 0.0, 1
      descartadas = []
      for (nome, _, _), dif in zip(URNAS, antes):
          if abs(dif) > LIMITE_MS:
              descartadas.append(nome)
          else:
              soma += dif
              quantidade += 1
      media = soma / quantidade
      ```

    * **Envio dos ajustes individuais para cada urna:**
      ```python
      for (nome, porta, _), dif in zip(URNAS, antes):
          perguntar(porta, f"AJUSTAR:{media - dif:.3f}")
      ajuste_central = media
      ```
