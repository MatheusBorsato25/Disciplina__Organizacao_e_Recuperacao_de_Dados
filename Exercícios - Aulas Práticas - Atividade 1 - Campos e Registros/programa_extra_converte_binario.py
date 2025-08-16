import io

def converte_binario():
    '''
    Esta função converte um arquivo de texto para um arquivo binário, 
    armazenando o tamanho de cada linha seguido do conteúdo da linha 
    em formato binário. O nome do arquivo de texto é solicitado ao usuário 
    e o arquivo binário gerado tem o mesmo nome com a extensão ".bin".
    '''
    NOME_ARQ = input('Digite o nome do arquivo de texto: ')
    ARQUIVO_BINARIO = open(NOME_ARQ + ".bin", 'wb')
    ARQUIVO_TEXTO = open(NOME_ARQ, 'r')
    REGISTRO = ARQUIVO_TEXTO.readline()
    
    while REGISTRO != '':
        REGISTRO = REGISTRO.encode()
        TAM = len(REGISTRO)
        TAM = (TAM).to_bytes(2)
        ARQUIVO_BINARIO.write(TAM)
        ARQUIVO_BINARIO.write(REGISTRO)
        REGISTRO = ARQUIVO_TEXTO.readline()
    ARQUIVO_TEXTO.close()
    ARQUIVO_BINARIO.close()

converte_binario()
