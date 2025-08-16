import io

# Constantes
VALOR_BAIXO = ''
VALOR_ALTO = '~'

def inicialize() -> tuple[str, str, io.TextIOWrapper, io.TextIOWrapper, io.TextIOWrapper, bool]:

    ant1 = VALOR_BAIXO
    ant2 = VALOR_BAIXO

    lista1 = open('lista1.txt', 'r')
    lista2 = open('lista2.txt', 'r')
    saida = open('saida.txt', 'w')

    existem_mais_nomes = True

    return ant1, ant2, lista1, lista2, saida, existem_mais_nomes

def finalize(lista1: io.TextIOWrapper, lista2: io.TextIOWrapper, saida: io.TextIOWrapper):
    
    lista1.close()
    lista2.close()
    saida.close()

def leia_nome(lista: io.TextIOWrapper, nome_ant: str, nome_outra_lista: str, existem_mais_nomes: bool) -> tuple[str, str, bool]:

    nome = lista.readline()
    if nome == '':
        if nome_outra_lista == VALOR_ALTO:
            existem_mais_nomes = False
        else:
            nome = VALOR_ALTO
    else:
        if nome <= nome_ant:
            raise ValueError("Erro de Sequência!")
    
    nome_ant = nome

    return nome, nome_ant, existem_mais_nomes

def merge() -> None:

    ant1, ant2, lista1, lista2, saida, existem_mais_nomes = inicialize()

    nome1, ant1, existem_mais_nomes = leia_nome(lista1, ant1, ant2, existem_mais_nomes)
    nome2, ant2, existem_mais_nomes = leia_nome(lista2, ant2, ant1, existem_mais_nomes)

    while existem_mais_nomes:
        if nome1 < nome2:
            saida.write(nome1)
            nome1, ant1, existem_mais_nomes = leia_nome(lista1, ant1, ant2, existem_mais_nomes)
        elif nome1 > nome2:
            saida.write(nome2)
            nome2, ant2, existem_mais_nomes = leia_nome(lista2, ant2, ant1, existem_mais_nomes)
        else: # nome1 == nome2
            saida.write(nome1)
            nome1, ant1, existem_mais_nomes = leia_nome(lista1, ant1, ant2, existem_mais_nomes)
            nome2, ant2, existem_mais_nomes = leia_nome(lista2, ant2, ant1, existem_mais_nomes)

    finalize(lista1, lista2, saida)
    
    
if __name__ == '__main__':
    merge()