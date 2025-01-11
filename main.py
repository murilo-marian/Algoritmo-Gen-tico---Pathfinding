import random
from json.encoder import INFINITY
from operator import truediv

import numpy as np

# parâmetros
TAMANHO_POPULAÇÃO = 50
TAMANHO_GENOMA = 20
GERACOES = 5
TAXA_MUTACAO = 0.005

#genes: left/right preference binary; ignore obstacle weight threshold; ignore obstacle distance threshold

mapa = np.array([[random.randint(0, 9) for _ in range(5)] for _ in range(5)], dtype=object)
# mapa = np.array([[0, 7, 6, 9, 4],
#                    [4, 8, 8, 9, 7],
#                    [4, 4, 5, 6, 0],
#                    [3, 5, 1, 8, 8],
#                    [5, 3, 5, 8, 3]], dtype=object)
pos_inicial = [2, 0]
pos_alvo = [4, 4]


def percorrer_caminho(matriz, pos_inicial, pos_final, distancia_ignorar_pesos, delta_maximo, left_right_preference, up_down_preference):
    pos_atual = list(pos_inicial)
    visitados = set()

    # Lista de movimentos possíveis: (delta_x, delta_y)

    visitados.add(tuple(pos_atual))  # Marca a posição atual como visitada
    matriz[pos_atual[0], pos_atual[1]] = "X"

    print_matriz_formatada_np(matriz)

    while tuple(pos_atual) != tuple(pos_final):
        distancia_x = abs(pos_atual[0] - pos_final[0])
        distancia_y = abs(pos_atual[1] - pos_final[1])

        movimentos_validos = obter_movimentos_validos(matriz, pos_atual, visitados)
        print(movimentos_validos)
        print("----------------")
        #primeiro teste é se ele tá perto o suficiente do alvo pra só ignorar os pesos completamente
        #caso não esteja, ele faz todos os outros testes
        if distancia_x <= distancia_ignorar_pesos and distancia_y <= distancia_ignorar_pesos:
            #mover normal
            pos_atual = movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final, movimentos_validos)
        else:
            #fazer os outros testes pra decidir onde ele vai seguir
            #o algoritmo tem que levar em consideração todos os genes que eu escolhi

            #gene 1 & 2: preferência entre esquerda/direita e cima/baixo em casos em que o custo é o mesmo
            #realisticamente cada caso em que isso ocorra a resposta ideal seria diferente
            #mas em um contexto de um mapa com pesos aleatórios, seria difícil isso acontecer muitas vezes pra importar o suficiente

            #gene 3: distância do objetivo final em que o algoritmo ignora os outros genes e apenas corre diretamente para o resultado
            #já foi implementado acima

            #gene 4: delta de pesos em que o algoritmo vai preferir ir para o lado mais próximo do alvo ao invés de seguir pelo caminho de menor resistência
            #ex: o alvo está a direita, e o caminho de menor resistência é ir para cima, caso
            #a diferença entre apenas seguir para a direita e subir for pequena o suficiente, o algoritmo
            #vai dar preferência a seguir para a direita ao invés de desviar para cima

            if movimentos_validos:
                movimentos_validos.sort(key=lambda x: x[0])

                #aqui ele vai ter que fazer os testes do gene 1, 2 e 4

                #primeira coisa a se fazer é determinar qual direção ele seguiria se fosse a movimentação normal
                direcao_x = [0, 0]
                direcao_y = [0, 0]
                if pos_atual[0] < pos_final[0]:
                    direcao_x[0] += 1
                elif pos_atual[0] > pos_final[0]:
                    direcao_x[0] += -1

                if pos_atual[1] < pos_final[1]:
                    direcao_y[1] += 1
                elif pos_atual[1] > pos_final[1]:
                    direcao_y[1] += -1

                #agora o algoritmo deve determinar se essa direção é viável, se não, ele vai escolher outra para desviar

                #se a melhor direção já for a com o menor peso, só vai
                #TODO adicionar checagem de se outros valores do array movimentos_validos tem peso igual
                #TODO já que ele só testa o primeiro elemento, e se o sort deixou o elemento optimo em segundo ele não vai funcionar direito

                if direcao_x == [a - b for a, b in zip(movimentos_validos[0][1], pos_atual)] or direcao_y == [a - b for a, b in zip(movimentos_validos[0][1], pos_atual)]:
                    proxima_pos = movimentos_validos[0][1]
                    pos_atual = list(proxima_pos)
                else:
                    #aqui que vai rolar os desvios e os caralho aquático
                    #primeira coisa é ver o gene 4
                    #se a direção certa tá dentro do delta, manda bala
                    #caso contrário, desvia pro caminho de menos resistência
                    #caso tenha dois empatados, aí entra em jogo o gene 1 e 2
                    nova_pos_x = tuple([x + y for x, y in zip(direcao_x, pos_atual)])
                    nova_pos_y = tuple([x + y for x, y in zip(direcao_y, pos_atual)])
                    if any(nova_pos_x == movimento or nova_pos_y == movimento for _, movimento in movimentos_validos):
                        indice_x = next((i for i, (_, movimento) in enumerate(movimentos_validos) if movimento == nova_pos_x), None)
                        indice_y = next((i for i, (_, movimento) in enumerate(movimentos_validos) if movimento == nova_pos_y), None)
                        diferenca_de_pesos_x = INFINITY
                        diferenca_de_pesos_y = INFINITY
                        if indice_x:
                            diferenca_de_pesos_x = abs(movimentos_validos[0][0] - movimentos_validos[indice_x][0])
                        elif indice_y:
                            diferenca_de_pesos_y = abs(movimentos_validos[0][0] - movimentos_validos[indice_y][0])
                        if diferenca_de_pesos_x <= delta_maximo:
                            pos_atual = list(nova_pos_x)
                        elif diferenca_de_pesos_y <= delta_maximo:
                            pos_atual = list(nova_pos_y)
                        else:
                            #primeiro ele vê o peso dos caminhos disponíveis pra desvio
                            #e vai escolher o mais leve
                            #caso tiver mais de um peso mais leve, e não tiver pendendo pra um lado em específico, ele vai usar o gene 1/2 pra decidir qual vai escolher
                            menor_peso = movimentos_validos[0][0]
                            movimentos_com_menor_peso = [movimento for movimento in movimentos_validos if
                                                         movimento[0] == menor_peso]

                            if len(movimentos_com_menor_peso) > 1:
                                movimentos_opostos = []
                                for i, mov1 in enumerate(movimentos_com_menor_peso):
                                    if movimentos_opostos:
                                        break
                                    for j, mov2 in enumerate(movimentos_com_menor_peso):
                                        if i != j and movimentos_sao_opostos(mov1[1], mov2[1], pos_atual):
                                            movimentos_opostos = [mov1, mov2]
                                            break

                                if movimentos_opostos:
                                    mov1, mov2 = movimentos_opostos
                                    left_right_preference_new_position = [a + b for a, b in zip(pos_atual, left_right_preference)]
                                    up_down_new_position = [a + b for a, b in zip(pos_atual, up_down_preference)]
                                    if left_right_preference_new_position == list(mov1[1]) or left_right_preference_new_position == list(mov2[1]):
                                        pos_atual = left_right_preference_new_position
                                    else:
                                        pos_atual = up_down_new_position
                                else:
                                    # Caso não sejam opostos ou só há um movimento válido
                                    pos_atual = movimentos_com_menor_peso[0][1]
                            else:
                                # Apenas um movimento com menor peso
                                pos_atual = movimentos_com_menor_peso[0][1]
                    else:
                        print("sem caminho disponível - preso")
                        break

            else:
                print("Sem movimentos válidos! Caminho bloqueado.")
                break


        visitados.add(tuple(pos_atual))  # Marca a posição atual como visitada
        matriz[pos_atual[0], pos_atual[1]] = "X"

        print_matriz_formatada_np(matriz)
        print("----------------")


def movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final, movimentos_validos):
    nova_pos_x = pos_atual[:]
    nova_pos_y = pos_atual[:]

    nova_pos_x[0] += 1 if pos_atual[0] < pos_final[0] else -1
    nova_pos_y[1] += 1 if pos_atual[1] < pos_final[1] else -1

    #checa se alguma das posições a considerar é a final, aí já pula direto pq o resto é irrelevante
    if nova_pos_x == pos_final:
        return nova_pos_x
    elif nova_pos_y == pos_final:
        return nova_pos_y

    if any(tuple(nova_pos_x) == movimento for _, movimento in movimentos_validos) and distancia_x != 0:
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
        nova_pos = (pos_atual[0] + dx, pos_atual[1] + dy)

        # Verifica se a nova posição está dentro dos limites da matriz
        if 0 <= nova_pos[0] < matriz.shape[0] and 0 <= nova_pos[1] < matriz.shape[1]:
            if nova_pos not in visitados:
                peso = matriz[nova_pos[0], nova_pos[1]]
                movimentos_validos.append((peso, nova_pos))
    return movimentos_validos

#
# def inicializar_populacao():
#     """gera populaçao inicial de indivíduos"""
#     return [[random.randint(0, 1) for _ in range(TAMANHO_GENOMA)] for _ in range(TAMANHO_POPULAÇÃO)]
#
#
# def avaliar_fitness(individuo):
#     return sum(individuo)
#
#
# def selecionar_pais_torneio(populacao, fitness):
#     tamanho_torneio = 3
#     pai1 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
#     pai2 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
#     return pai1, pai2
#
#
# def crossover(pai1, pai2):
#     # sorteia ponto de corte:
#     ponto_corte = random.randint(1, TAMANHO_GENOMA - 1)
#     filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
#     filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
#     return filho1, filho2
#
# def mutar(individuo):
#     for i in range(TAMANHO_GENOMA):
#         if random.random() < TAXA_MUTACAO:
#             individuo[i] = 1 - individuo[i]
#     return individuo
#
#
# def algoritmo_genetico():
#     populacao = inicializar_populacao()
#
#     for geracao in range(GERACOES):
#         fitness = [avaliar_fitness(individuo) for individuo in populacao]
#
#         melhor_individuo = max(populacao, key=avaliar_fitness)
#         print(
#             f"Geracao {geracao} : Melhor fitness = {avaliar_fitness(melhor_individuo)} Melhor indivíduo = {melhor_individuo}")
#
#         nova_populacao = []
#
#         while len(nova_populacao) < TAMANHO_POPULAÇÃO:
#             pai1, pai2 = selecionar_pais_torneio(populacao, fitness)
#             filho1, filho2 = crossover(pai1, pai2)
#             nova_populacao.append(mutar(filho1))
#             nova_populacao.append(mutar(filho2))
#
#         populacao = nova_populacao
#
#     return max(populacao, key=avaliar_fitness)
#
#

def print_matriz_formatada_np(matriz):
    # Converte a matriz em strings formatadas
    matriz_str = np.array([[f"{str(el):>3}" for el in linha] for linha in matriz])
    print("\n".join(" ".join(linha) for linha in matriz_str))
    print("----------------")

# melhor_solucao = algoritmo_genetico()
# print("melhor solucao encontrada")
# print(f"genes da melhor solução: {melhor_solucao}")
# print(f"Fitness : {avaliar_fitness(melhor_solucao)}")

percorrer_caminho(mapa, pos_inicial, pos_alvo, 2, 3, [0, 1], [1, 0])