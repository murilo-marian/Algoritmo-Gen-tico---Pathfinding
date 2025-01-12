import random

# Parâmetros do Algoritmo Genético
TAMANHO_POPULACAO = 10
TAMANHO_GENOMA = 8  # Número de genes em cada indivíduo
GERACOES = 20
TAXA_MUTACAO = 0.005


# Passo 1: Inicializar a população
def inicializar_populacao():
    """Gera uma população inicial de indivíduos com genomas aleatórios"""
    return [[random.randint(0, 1) for _ in range(TAMANHO_GENOMA)] for _ in range(

        TAMANHO_POPULACAO)]


# Passo 2: Avaliar o fitness de cada indivíduo
def avaliar_fitness(individuo):
    return sum(individuo)


# Passo 3: Seleção de pais (torneio)
def selecionar_pais_torneio(populacao, fitness):
    tamanho_torneio = 3  # Número de indivíduos no torneio
    pai1 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda

        x: x[1])[0]

    pai2 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda

        x: x[1])[0]
    return pai1, pai2

    # Passo 4: Cruzamento (recombinação)


def crossover(pai1, pai2):
    """Realiza o cruzamento de dois pais para gerar dois filhos"""
    ponto_cruzamento = random.randint(1, TAMANHO_GENOMA - 1)
    filho1 = pai1[:ponto_cruzamento] + pai2[ponto_cruzamento:]
    filho2 = pai2[:ponto_cruzamento] + pai1[ponto_cruzamento:]
    return filho1, filho2

    # Passo 5: Mutação


def mutar(individuo):
    """Realiza a mutação de um indivíduo com base na taxa de mutação"""
    for i in range(TAMANHO_GENOMA):
        if random.random() < TAXA_MUTACAO:
        individuo[i] = 1 - individuo[i]  # alterna entre 0 e 1
    return individuo

    # Algortimo Genético


def algoritmo_genetico():
    """Executa o Algoritmo Genético"""
    # Inicializar a população
    populacao = inicializar_populacao()

    for geracao in range(GERACOES):
    # Avaliar a aptidao de cada indivíduo
    fitness = [avaliar_fitness(individuo) for individuo in populacao]

    # Exibir o melhor indivíduo da geração=
    melhor_individuo = max(populacao, key=avaliar_fitness)
    print(f"Geração {geracao}: Melhor Fitness = {avaliar_fitness(melhor_individuo)

    } | Melhor Indivíduo = {melhor_individuo}")

    # Nova geração
    nova_populacao = []

    # Criar nova geração com cruzamento e mutação
    while len(nova_populacao) < TAMANHO_POPULACAO:
        pai1, pai2 = selecionar_pais_torneio(populacao, fitness)
        filho1, filho2 = crossover(pai1, pai2)
        nova_populacao.append(mutar(filho1))
        nova_populacao.append(mutar(filho2))

    # Atualizar a população com a nova geração
    populacao = nova_populacao

    return max(populacao, key=avaliar_fitness)


# Executar o algoritmo genético
melhor_solucao = algoritmo_genetico()
print("\n Melhor solução encontrada")
print(f"Genes {melhor_solucao}")
print(f"Fitness: {avaliar_fitness(melhor_solucao)}")
