import os


def busca_rrn():
     
    try:
        nomeArq = input("\nDigite o nome do arquivo a ser aberto: ")
        entrada = open(nomeArq, 'rb')
        cabecalho = entrada.read(4)
        total_registros = int.from_bytes(cabecalho)
        RRN = int(input("\nDigite o RRN do registro desejado: ")) # Número Relativo do Registro
        
        if RRN >= total_registros:
            print("\nRegistro não encontrado!\n")
        else:
            OFFSET = RRN * 64 + 4 # 64 = Tamanho fixo dos registros; 4 = Tamanho do cabeçalho
            entrada.seek(OFFSET, os.SEEK_SET)
            reg = entrada.read(64)
            reg_str = reg.decode()
            lista_campos: list[str] = reg_str.split(sep="|")
            print("\nRegistro encontrado: \n")
            for i in range(len(lista_campos) - 1):
                print(f"Campo {i + 1}: {lista_campos[i]}")
                
        entrada.close()
        
    except FileNotFoundError as e:
        print(f'\nErro: {e}') 
        

busca_rrn()