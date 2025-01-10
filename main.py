import random
import numpy as np

# parâmetros
TAMANHO_POPULAÇÃO = 50
TAMANHO_GENOMA = 20
GERACOES = 5
TAXA_MUTACAO = 0.005

#genes: left/right preference binary; ignore obstacle weight threshold; ignore obstacle distance threshold

mapa = np.array([[random.randint(0, 9) for _ in range(5)] for _ in range(5)], dtype=object)
mapa = np.array([[1, 4, 1, 1],
                 [1, 5, 7, 1],
                 [1, 1, 6, 8],
                 [1, 1, 1, 4]], dtype=object)
pos_inicial = [0, 0]
pos_alvo = [3, 3]


def percorrer_caminho(matriz, pos_inicial, pos_final, distancia_ignorar_pesos, delta_maximo):
    pos_atual = list(pos_inicial)
    visitados = set()

    # Lista de movimentos possíveis: (delta_x, delta_y)

    visitados.add(tuple(pos_atual))  # Marca a posição atual como visitada
    matriz[pos_atual[0], pos_atual[1]] = "X"

    print_matriz_formatada_np(matriz)
    print("----------------")

    while tuple(pos_atual) != tuple(pos_final):
        distancia_x = abs(pos_atual[0] - pos_final[0])
        distancia_y = abs(pos_atual[1] - pos_final[1])


        #primeiro teste é se ele tá perto o suficiente do alvo pra só ignorar os pesos completamente
        #caso não esteja, ele faz todos os outros testes
        if distancia_x <= distancia_ignorar_pesos and distancia_y <= distancia_ignorar_pesos:
            #mover normal
            pos_atual = movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final)
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

            movimentos_validos = obter_movimentos_validos(matriz, pos_atual, visitados)

            if movimentos_validos:
                movimentos_validos.sort(key=lambda x: x[0])

                #aqui ele vai ter que fazer os testes do gene 1, 2 e 4

                #primeira coisa a se fazer é determinar qual direção ele seguiria se fosse a movimentação normal
                direcao = [0, 0]
                if distancia_x > distancia_y:
                    direcao[0] += 1 if pos_atual[0] < pos_final[0] else -1
                else:
                    direcao[1] += 1 if pos_atual[1] < pos_final[1] else -1

                #agora o algoritmo deve determinar se essa direção é viável, se não, ele vai escolher outra para desviar

                #se a melhor direção já for a com o menor peso, só vai
                #TODO adicionar checagem de se outros valores do array movimentos_validos tem peso igual
                #TODO já que ele só testa o primeiro elemento, e se o sort deixou o elemento optimo em segundo ele não vai funcionar direito
                if direcao == [a - b for a, b in zip(movimentos_validos[0][1], pos_atual)]:
                    proxima_pos = movimentos_validos[0][1]
                    print(movimentos_validos)
                    print(movimentos_validos[0][0])
                    print(movimentos_validos[1][1])
                    print(movimentos_validos[0][1])
                    print(movimentos_validos[1][0])

                    pos_atual = list(proxima_pos)
                else:
                    #aqui que vai rolar os desvios e os caralho aquático
                    #primeira coisa é ver o gene 4
                    #se a direção certa tá dentro do delta, manda bala
                    #caso contrário, desvia pro caminho de menos resistência
                    #caso tenha dois empatados, aí entra em jogo o gene 1 e 2
                    nova_pos = tuple([x + y for x, y in zip(direcao, pos_atual)])
                    if any(nova_pos == movimento for _, movimento in movimentos_validos):
                        indice = next((i for i, (_, movimento) in enumerate(movimentos_validos) if movimento == nova_pos), None)
                        diferenca_de_pesos = abs(movimentos_validos[0][0] - movimentos_validos[indice][0])
                        if diferenca_de_pesos < delta_maximo:
                            #se a diferença for pequena o suficiente, ignora e segue o baile
                            pos_atual = movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final)
                        else:
                            #desvio maroto
                            print("teste")
            else:
                print("Sem movimentos válidos! Caminho bloqueado.")
                break


        visitados.add(tuple(pos_atual))  # Marca a posição atual como visitada
        matriz[pos_atual[0], pos_atual[1]] = "X"

        print_matriz_formatada_np(matriz)
        print("----------------")


def movimentacao_base(distancia_x, distancia_y, pos_atual, pos_final):
    if distancia_x > distancia_y:
        pos_atual[0] += 1 if pos_atual[0] < pos_final[0] else -1
    else:
        pos_atual[1] += 1 if pos_atual[1] < pos_final[1] else -1
    return pos_atual

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

percorrer_caminho(mapa, pos_inicial, pos_alvo, 0, 2)