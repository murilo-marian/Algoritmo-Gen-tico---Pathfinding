import copy
import random
from json.encoder import INFINITY

import numpy as np

# parâmetros
TAMANHO_POPULACAO = 10
TAMANHO_GENOMA = 4
GERACOES = 5
TAXA_MUTACAO = 0.005

# genes: left/right preference binary; ignore obstacle weight threshold; ignore obstacle distance threshold

mapa = np.array([[random.randint(0, 9) for _ in range(100)] for _ in range(100)], dtype=object)
# mapa = np.array([[1, 8, 8, 1, 3],
#                   [3, 8, 4, 2, 1],
#                   [4, 5, 7, 2, 1],
#                   [2, 1, 7, 5, 7],
#                   [0, 0, 3, 9, 1]], dtype=object)
pos_inicial = [0, 0]
pos_alvo = [99, 99]


def percorrer_caminho(matriz, pos_inicial, pos_final, individuo):
    left_right_preference = individuo[0]
    up_down_preference = individuo[1]
    distancia_ignorar_pesos = individuo[2]
    delta_maximo = individuo[3]

    fitness = 0
    pos_atual = pos_inicial
    fitness -= matriz[pos_atual[0]][pos_atual[1]]
    visitados = []
    visitados.append(pos_atual)  # Marca a posição atual como visitada
    matriz[pos_atual[0], pos_atual[1]] = "X"

    print_matriz_formatada_np(matriz)
    iteracao = 0
    while pos_atual != pos_final:
        iteracao += 1
        distancia_x = abs(pos_atual[0] - pos_final[0])
        distancia_y = abs(pos_atual[1] - pos_final[1])

        movimentos_validos = obter_movimentos_validos(matriz, pos_atual, visitados)
        print(movimentos_validos)
        print("----------------")
        # primeiro teste é se ele tá perto o suficiente do alvo pra só ignorar os pesos completamente
        # caso não esteja, ele faz todos os outros testes

        if not movimentos_validos:
            fitness -= 200
            print("sem movimentos válidos")
            break
        if distancia_x <= distancia_ignorar_pesos and distancia_y <= distancia_ignorar_pesos:
            # mover normal
            pos_atual = movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final, movimentos_validos)
        else:
            pos_atual= decidir_movimento(movimentos_validos, pos_atual, pos_final, delta_maximo, left_right_preference,
                                          up_down_preference)
            if pos_atual is None:
                fitness -= 200
                print(iteracao)
                print("Sem movimentos válidos! Caminho bloqueado.")
                break
        peso = matriz[pos_atual[0]][pos_atual[1]]
        if peso != "X":
            fitness -= peso
        visitados.append(pos_atual)  # Marca a posição atual como visitada
        matriz[pos_atual[0], pos_atual[1]] = "X"

        print_matriz_formatada_np(matriz)
        print("----------------")
    return fitness


def decidir_movimento(movimentos_validos, pos_atual, pos_final, delta_maximo, left_right_preference,
                      up_down_preference):
    # aqui ele vai ter que fazer os testes do gene 1, 2 e 4
    movimentos_validos.sort(key=lambda x: x[0])
    menor_peso = movimentos_validos[0][0]
    movimentos_com_menor_peso = [movimento for movimento in movimentos_validos if
                                 movimento[0] == menor_peso]

    # aqui ele vai ter que fazer os testes do gene 1, 2 e 4

    # primeira coisa a se fazer é determinar qual direção ele seguiria se fosse a movimentação normal
    direcao_x = [0, 0]
    direcao_y = [0, 0]
    if pos_atual[0] < pos_final[0]:
        direcao_x = pos_atual[:]
        direcao_x[0] += 1
    elif pos_atual[0] > pos_final[0]:
        direcao_x = pos_atual[:]
        direcao_x[0] += -1

    if pos_atual[1] < pos_final[1]:
        direcao_y = pos_atual[:]
        direcao_y[1] += 1
    elif pos_atual[1] > pos_final[1]:
        direcao_y = pos_atual[:]
        direcao_y[1] += -1

        # agora o algoritmo deve determinar se essa direção é viável, se não, ele vai escolher outra para desviar

        # se a melhor direção já for a com o menor peso, só vai
    if direcao_x == movimentos_validos[0][1] or direcao_y == movimentos_validos[0][1]:
        proxima_pos = movimentos_validos[0][1]
        pos_atual = proxima_pos
        return pos_atual
    else:
        if any(direcao_x == movimento or direcao_y == movimento for _, movimento in movimentos_validos):
            indice_x = next(
                (i for i, (_, movimento) in enumerate(movimentos_validos) if movimento == direcao_x), None)
            indice_y = next(
                (i for i, (_, movimento) in enumerate(movimentos_validos) if movimento == direcao_y), None)
            diferenca_de_pesos_x = INFINITY
            diferenca_de_pesos_y = INFINITY
            if indice_x:
                diferenca_de_pesos_x = abs(movimentos_validos[0][0] - movimentos_validos[indice_x][0])
            elif indice_y:
                diferenca_de_pesos_y = abs(movimentos_validos[0][0] - movimentos_validos[indice_y][0])
            if diferenca_de_pesos_x <= delta_maximo:
                pos_atual = direcao_x
                return pos_atual
            elif diferenca_de_pesos_y <= delta_maximo:
                pos_atual = direcao_y
                return pos_atual
        else:
            pos_atual = desviar(movimentos_com_menor_peso, pos_atual, left_right_preference, up_down_preference)
            return pos_atual

    return movimentos_validos[0][1]


def desviar(movimentos_com_menor_peso, pos_atual, left_right_preference, up_down_preference):
    # primeiro ele vê o peso dos caminhos disponíveis pra desvio
    # e vai escolher o mais leve
    # caso tiver mais de um peso mais leve, e não tiver pendendo pra um lado em específico, ele vai usar o gene 1/2 pra decidir qual vai escolher
    if len(movimentos_com_menor_peso) > 1:
        movimentos_opostos = procurar_movimentos_opostos(movimentos_com_menor_peso, pos_atual)
        if movimentos_opostos:
            mov1, mov2 = movimentos_opostos
            left_right_preference_new_position = pos_atual[:]
            left_right_preference_new_position[1] += left_right_preference

            up_down_new_position = pos_atual[:]
            up_down_new_position[0] += up_down_preference

            if left_right_preference_new_position == mov1[1] or left_right_preference_new_position == mov2[1]:
                pos_atual = left_right_preference_new_position
                return pos_atual
            else:
                pos_atual = up_down_new_position
                return pos_atual
        else:
            # Caso não sejam opostos ou só há um movimento válido
            pos_atual = movimentos_com_menor_peso[0][1]
            return pos_atual
    else:
        # Apenas um movimento com menor peso
        pos_atual = movimentos_com_menor_peso[0][1]
        return pos_atual


def procurar_movimentos_opostos(movimentos_com_menor_peso, pos_atual):
    movimentos_opostos = []
    for i, mov1 in enumerate(movimentos_com_menor_peso):
        if movimentos_opostos:
            break
        for j, mov2 in enumerate(movimentos_com_menor_peso):
            if i != j and movimentos_sao_opostos(mov1[1], mov2[1], pos_atual):
                movimentos_opostos = [mov1, mov2]
                break
    return movimentos_opostos


def movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final, movimentos_validos):
    nova_pos_x = pos_atual[:]
    nova_pos_y = pos_atual[:]

    if distancia_x != 0:
        nova_pos_x[0] += 1 if pos_atual[0] < pos_final[0] else -1
    if distancia_y != 0:
        nova_pos_y[1] += 1 if pos_atual[1] < pos_final[1] else -1

    # checa se alguma das posições a considerar é a final, aí já pula direto pq o resto é irrelevante
    if nova_pos_x == pos_final:
        return nova_pos_x
    elif nova_pos_y == pos_final:
        return nova_pos_y

    # TODO colocar pra preferir entre os dois movimentos o com menor peso

    # Verifica os pesos das posições candidatas
    peso_x = next((peso for peso, movimento in movimentos_validos if movimento == nova_pos_x), float('inf'))
    peso_y = next((peso for peso, movimento in movimentos_validos if movimento == nova_pos_y), float('inf'))

    # Escolhe o movimento com menor peso
    if peso_x < peso_y:
        return nova_pos_x
    elif peso_y < peso_x:
        return nova_pos_y
    else:
        if distancia_x > distancia_y:
            return nova_pos_x
        else:
            return nova_pos_y


def movimentos_sao_opostos(mov1, mov2, pos_atual):
    primeiro = [abs(a - b) for a, b in zip(mov1, pos_atual)]
    segundo = [abs(a - b) for a, b in zip(mov2, pos_atual)]
    if primeiro == segundo:
        return True
    return False


def obter_movimentos_validos(matriz, pos_atual, visitados):
    movimentos = [
        (1, 0),  # baixo
        (-1, 0),  # cima
        (0, 1),  # direita
        (0, -1)  # esquerda
    ]
    movimentos_validos = []

    # tira da lista de movimentos possíveis as casas já visitadas e movimentos que sairiam do mapa
    for dx, dy in movimentos:
        nova_pos = [pos_atual[0] + dx, pos_atual[1] + dy]

        # Verifica se a nova posição está dentro dos limites da matriz
        if 0 <= nova_pos[0] < matriz.shape[0] and 0 <= nova_pos[1] < matriz.shape[1]:
            if nova_pos not in visitados:
                peso = matriz[nova_pos[0], nova_pos[1]]
                movimentos_validos.append([peso, nova_pos])
    return movimentos_validos



def inicializar_populacao(matriz):
    """gera populaçao inicial de indivíduos"""
    populacao = []
    for i in range(TAMANHO_POPULACAO):
        individuo = []
        left_right_preference = random.choice([-1, 1])
        individuo.append(left_right_preference)

        up_down_preference = random.choice([-1, 1])
        individuo.append(up_down_preference)

        distancia_ignorar_pesos = random.randint(1, max(matriz.shape))
        individuo.append(distancia_ignorar_pesos)

        delta_maximo = random.randint(0, 9)
        individuo.append(delta_maximo)
        populacao.append(individuo)
    return populacao


def avaliar_fitness(individuo, matriz, pos_inicial, pos_final):
    mapa_copia = copy.deepcopy(matriz)
    return percorrer_caminho(mapa_copia, pos_inicial, pos_final, individuo)


def selecionar_pais_torneio(populacao, fitness):
    tamanho_torneio = 3
    pai1 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
    pai2 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
    return pai1, pai2


def crossover(pai1, pai2):
    # sorteia ponto de corte:
    ponto_corte = random.randint(1, TAMANHO_GENOMA - 1)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2

def mutar(individuo, matriz):
    for i in range(TAMANHO_GENOMA):
        if random.random() < TAXA_MUTACAO:
            if i == 0 or i == 1:
                individuo[i] *= -1
            elif i == 2:
                numbers = [i for i in range(1, max(matriz.shape) + 1) if i != individuo[i]]
                individuo[i] = random.choice(numbers)
            elif i == 3:
                numbers = [i for i in range(1, 9 + 1) if i != individuo[i]]
                individuo[i] = random.choice(numbers)
    return individuo


def algoritmo_genetico(matriz, pos_inicial, pos_final):
    populacao = inicializar_populacao(matriz)
    fitness = []
    for geracao in range(GERACOES):
        fitness = [avaliar_fitness(individuo, matriz, pos_inicial, pos_final) for individuo in populacao]

        melhor_individuo = max(populacao, key=lambda individuo: avaliar_fitness(individuo, matriz, pos_inicial, pos_final))
        print(
            f"Geracao {geracao} : Melhor fitness = {avaliar_fitness(melhor_individuo, matriz, pos_inicial, pos_final)} Melhor indivíduo = {melhor_individuo}")

        # nova_populacao = []
        #
        # while len(nova_populacao) < TAMANHO_POPULAÇÃO:
        #     pai1, pai2 = selecionar_pais_torneio(populacao, fitness)
        #     filho1, filho2 = crossover(pai1, pai2)
        #     nova_populacao.append(mutar(filho1))
        #     nova_populacao.append(mutar(filho2))
        #
        # populacao = nova_populacao

    print(fitness)
    return max(populacao, key=lambda individuo: avaliar_fitness(individuo, matriz, pos_inicial, pos_final))



def print_matriz_formatada_np(matriz):
    # Converte a matriz em strings formatadas
    matriz_str = np.array([[f"{str(el):>3}" for el in linha] for linha in matriz])
    print("\n".join(" ".join(linha) for linha in matriz_str))
    print("----------------")


melhor_solucao = algoritmo_genetico(mapa, pos_inicial, pos_alvo)
print("melhor solucao encontrada")
print(f"genes da melhor solução: {melhor_solucao}")
print(f"Fitness : {avaliar_fitness(melhor_solucao, mapa, pos_inicial, pos_alvo)}")
# individuo = [1, -1, 3, 4]
# percorrer_caminho(mapa, pos_inicial, pos_alvo, individuo)
