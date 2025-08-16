import io
import os


def busca_e_atualiza() -> None:
    '''
    Gerencia um menu para o usuário com três opções:

    1) Inserir um novo registro no final do arquivo.
    2) Buscar um registro pelo RRN e oferecer a opção de alterá-lo.
    3) Encerrar o programa.
    '''
    arq = abrir_arquivo_binario()
    total_reg = int.from_bytes(arq.read(4))
    
    print("\n PROGRAMA PARA INSERÇÃO E ALTERAÇÃO DE REGISTROS \n")
    print("Opções: \n")
    print("1. Inserir um novo registro")
    print("2. Buscar um registro por RRN para alterações")
    print("3. Terminar o programa")
    
    opção = int(input("\nDigite o número da sua escolha: "))
    
    while opção != 3:
        if opção == 1:
            reg = escreve_registro()
            reg = reg.encode()
            reg = reg.ljust(64, b'\0')
            OFFSET = total_reg * 64 + 4
            arq.seek(OFFSET, os.SEEK_SET)
            arq.write(reg)
            total_reg += 1
        elif opção == 2:
            RRN = int(input("\nDigite o RRN do registro desejado: ")) # Número Relativo do Registro
            if RRN >= total_reg:
                print("\nRegistro não encontrado!")
            else:
                OFFSET = RRN * 64 + 4 # 64 = Tamanho fixo dos registros; 4 = Tamanho do cabeçalho
                arq.seek(OFFSET, os.SEEK_SET)
                reg = arq.read(64)
                reg_str = reg.decode()
                lista_campos: list[str] = reg_str.split(sep="|")
                print("\nRegistro encontrado: \n")
                for i in range(len(lista_campos) - 1):
                    print(f"Campo {i + 1}: {lista_campos[i]}")
                print("\nVocê deseja modificar este registro?")
                alterar = input("Responda S ou N, seguido de <ENTER>: ")
                if alterar == 'S':
                    reg = escreve_registro()
                    reg = reg.encode()
                    reg = reg.ljust(64, b'\0')
                    arq.seek(OFFSET, os.SEEK_SET)
                    arq.write(reg)
                elif alterar != 'N':
                    print("\nDigite uma opção válida!")
        else:
            print("\nDigite uma opção válida!")
            
        opção = int(input("\nDigite o número da sua escolha: "))
    arq.seek(0, os.SEEK_SET)
    total_reg_bytes = total_reg.to_bytes(4)
    arq.write(total_reg_bytes)
    arq.close()


def abrir_arquivo_binario() -> io.BufferedRandom:
    '''
    Abre um arquivo binário para leitura e escrita (r+b).
    Se o arquivo não existir, cria-o (w+b) e escreve no início um cabeçalho 
    com o total de registros (inicializado em zero, como 4 bytes).
    Retorna o objeto de arquivo aberto.
    '''
    nomeArq = input ("\nDigite o nome do arquivo: ")
    try:
        arq = open(nomeArq, 'r+b')
    except FileNotFoundError:
        arq = open(nomeArq, 'w+b')
        total_reg = 0
        total_reg_bytes = total_reg.to_bytes(4)
        arq.write(total_reg_bytes)
    return arq 


def escreve_registro() -> str:
    '''
    Coleta dados do usuário (sobrenome, nome, endereço, cidade, estado e CEP) através de input().
    Monta e retorna uma string com os campos separados por | e terminando com um |. 
    Essa string representa um único registro.
    '''
    reg = ''
    campo = input('\nDigite o sobrenome: ')
    reg += (campo + '|')
    campo = input('Digite o nome: ')
    reg += (campo + '|' )
    campo = input('Digite o endereço: ')
    reg += (campo + '|')
    campo = input('Digite a cidade: ')
    reg += (campo + '|')
    campo = input('Digite o estado: ')
    reg += (campo + '|')      
    campo = input('Digite o CEP: ')
    reg += (campo + '|')
    
    return reg  



busca_e_atualiza()

