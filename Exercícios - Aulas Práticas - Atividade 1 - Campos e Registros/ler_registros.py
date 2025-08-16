import io 

def ler(ENTRADA: io.BufferedReader) -> tuple[str, int]:
    TAM = ENTRADA.read(2)
    TAM_BYTES = int.from_bytes(TAM)

    if TAM_BYTES > 0:
        BUFFER = ENTRADA.read(TAM_BYTES)
        BUFFER_STRING = BUFFER.decode()
        TUPLA = (BUFFER_STRING, TAM_BYTES)
        return TUPLA
    else:
        return ('', 0)

def ler_registros():
    try:
        NOME_ARQ = input('Digite o nome do arquivo: ')
        ENTRADA = open(NOME_ARQ, 'rb')
        BUFFER = ler(ENTRADA)
        TEXTO = BUFFER[0]
        n_registros = 0
        while TEXTO != '':
            LISTA: list[str] = TEXTO.split(sep='|')
            n_registros += 1
            print(f'\nRegistro #{n_registros} - (Tam: {BUFFER[1]}): \n')
            for i in range(1, len(LISTA)):
                print(f'Campo #{i}: {LISTA[i - 1]}')
            BUFFER = ler(ENTRADA)
            TEXTO = BUFFER[0]
        ENTRADA.close()
    except FileNotFoundError as e:
        print(f'Erro: {e}') 

ler_registros()