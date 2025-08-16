def escreve_registros():
    NOME_ARQ = input("Nome do arquivo a ser criado: ")
    SAÍDA = open(NOME_ARQ, 'wb')
    CAMPO = input('\nDigite o sobrenome (Clique em Enter para encerrar o programa): ')

    while CAMPO != '':
        BUFFER = ''
        BUFFER += (CAMPO + '|')
        CAMPO = input('Digite o nome: ')
        BUFFER += (CAMPO + '|' )
        CAMPO = input('Digite o endereço: ')
        BUFFER += (CAMPO + '|')
        CAMPO = input('Digite a cidade: ')
        BUFFER += (CAMPO + '|')
        CAMPO = input('Digite o estado: ')
        BUFFER += (CAMPO + '|')      
        CAMPO = input('Digite o CEP: ')
        BUFFER += (CAMPO + '|')
        BUFFER = BUFFER.encode()
        TAM = len(BUFFER)
        TAM = (TAM).to_bytes(2)
        SAÍDA.write(TAM)
        SAÍDA.write(BUFFER)

        CAMPO = input('\nDigite o sobrenome (Clique em Enter para encerrar o programa): ')
        
    SAÍDA.close()

escreve_registros()
