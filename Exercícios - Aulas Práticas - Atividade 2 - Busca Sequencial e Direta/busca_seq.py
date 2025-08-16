import io


def busca_seq():
    
    try:
        nomeArq = input("\nDigite o nome do arquivo: ")
        entrada = open(nomeArq, 'rb')
        sobrenome = input("\nDigite o SOBRENOME (chave primária de acesso): ")
        achou = False
        reg = ler(entrada)
        while reg != '' and not achou:
            lista_campos: list[str] = reg.split(sep='|')
            if sobrenome == lista_campos[0]:
                achou = True
            reg = ler(entrada)
        if achou:
            print("\nRegistro encontrado: \n")
            for i in range(len(lista_campos) - 1):
                print(f'Campo {i + 1}: {lista_campos[i]}')
        else:
            print("\nRegistro não encontrado!\n")
            
        entrada.close()
        
    except FileNotFoundError as e:
        print(f'\nErro: {e}') 


def ler(ENTRADA: io.BufferedReader) -> str:
    TAM = ENTRADA.read(2)
    TAM_BYTES = int.from_bytes(TAM)

    if TAM_BYTES > 0:
        BUFFER = ENTRADA.read(TAM_BYTES)
        BUFFER_STRING = BUFFER.decode()
        return BUFFER_STRING
    else:
        return ''
    
    
busca_seq()