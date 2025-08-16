from sys import argv
import io


# Constantes
VALOR_BAIXO = ''
VALOR_ALTO = '~'

# Variável Global
numEOF = 0


def inicialize(caminho: str, numListas: int) -> tuple[list[str], list[str], list[io.TextIOWrapper], io.TextIOWrapper, bool]:
    
    anteriores: list[str] = [VALOR_BAIXO] * numListas
    nomes: list[str] = [VALOR_BAIXO] * numListas
    listas = [None] * numListas
    
    for i in range(numListas):
        nomeArq = f'{caminho}/lista{i}.txt'
        arq = open(nomeArq, 'r')
        listas[i] = arq
        
    saida = open('saida_kwaymerge.txt', 'w')
    existem_mais_nomes = True
    
    return anteriores, nomes, listas, saida, existem_mais_nomes


def finalize(listas: list[io.TextIOWrapper], saida: io.TextIOWrapper, numListas: int):
    
    for i in range(numListas):
        listas[i].close()
    
    saida.close()
    
    
def leia_nome(lista: io.TextIOWrapper, nome_ant: str, existem_mais_nomes: bool, numListas: int) -> tuple[str, str, bool]:
    
    global numEOF
    nome = lista.readline()
    
    if nome == '':
        nome = VALOR_ALTO
        numEOF += 1
        if numEOF == numListas:
            existem_mais_nomes = False
    else:
        if nome <= nome_ant:
            raise ValueError("Erro de Sequência!")
        
    nome_ant = nome
    
    return nome, nome_ant, existem_mais_nomes


def kwaymerge(caminho: str, numListas: int) -> None:
    anteriores, nomes, listas, saida, existem_mais_nomes = inicialize(caminho, numListas)
    
    for i in range(numListas):
        nomes[i], anteriores[i], existem_mais_nomes = leia_nome(listas[i], anteriores[i], existem_mais_nomes, numListas)
        
    while existem_mais_nomes:
        menor = 0
        # Encontra o menor nome nas listas
        for i in range(numListas):
            if nomes[i] < nomes[menor]:
                menor = i
        saida.write(nomes[menor])
        nomes[menor], anteriores[menor], existem_mais_nomes = leia_nome(listas[menor], anteriores[menor], existem_mais_nomes, numListas)
        
    finalize(listas, saida, numListas)


def main() -> None:

    if len(argv) < 3:
        raise TypeError('Número incorreto de argumentos.'+ f'\nModo de uso:\n nome_arquivo diretorio_listas numListas')
    
    kwaymerge(argv[1], int(argv[2]))


if __name__ == '__main__':
    main()   
      