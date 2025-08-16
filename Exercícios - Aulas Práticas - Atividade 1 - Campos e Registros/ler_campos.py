import io

def le_campos():
    try:
        NOME_ARQ = input('Digite o nome do arquivo: ')
        ENTRADA = open(NOME_ARQ, 'r')
        CAMPO = leia_campo(ENTRADA)
        n = 1
        while CAMPO != '':
            print(f'Campo {n}#: {CAMPO}')
            n += 1
            CAMPO = leia_campo(ENTRADA)
        ENTRADA.close()
    except FileNotFoundError as e:
        print(f'Erro: {e}')

def leia_campo(ENTRADA: io.TextIOWrapper) -> str:

    campo = ''
    c = ENTRADA.read(1)
    while c != '' and c != '|':
        campo += c
        c = ENTRADA.read(1)
    return campo

le_campos()