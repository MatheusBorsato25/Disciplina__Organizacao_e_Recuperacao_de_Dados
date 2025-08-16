def escrever_campos():
    NOME_ARQ = input("Nome do arquivo a ser criado: ")
    SAÍDA = open(NOME_ARQ, 'w')
    SOBRENOME = input('Digite o sobrenome (Clique em Enter para encerrar o programa): ')

    while SOBRENOME != '':
        SAÍDA.write(SOBRENOME + '|')
        NOME = input('Digite o nome: ')
        SAÍDA.write(NOME + '|')
        ENDERECO = input('Digite o endereço: ')
        SAÍDA.write(ENDERECO + '|')
        CIDADE = input('Digite a cidade: ')
        SAÍDA.write(CIDADE + '|')
        ESTADO = input('Digite o estado: ')
        SAÍDA.write(ESTADO + '|')
        CEP = input('Digite o CEP: ')
        SAÍDA.write(CEP + '|')

        SOBRENOME = input('\nDigite o sobrenome (Clique em Enter para encerrar o programa): ')
        
    SAÍDA.close()

escrever_campos()



