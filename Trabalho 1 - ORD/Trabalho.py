import io
import os
from sys import argv

# Alunos: Guilherme Jucoski da Silva - RA: 138642; Matheus Henrique Borsato - RA: 138246.

# Constantes
PONTEIRO = 4
CABECALHO = 4
TAM = 2
FINAL_LED = (-1).to_bytes(4, signed=True)
CARACTER_REMOCAO = b'*'
 
 
def le_arquivo_operacoes(nome_arq_operacoes: str) -> list[tuple[str, str]]:
    '''
    Abre o arquivo de operações e lê todas as operações que devem ser realizadas e
    as separam em bandeira e argumento. 
    '''
    lista = []

    try:
        arq_op = open(nome_arq_operacoes, 'r', encoding='utf-8')
        linhas = arq_op.readlines()
        for linha in linhas:
            # Divide a linha em duas partes, com a bandeira no primeiro espaço e o argumento no segundo.
            l = linha.split(maxsplit = 1) # Divide a partir do primeiro espaço da linha
            lista.append((l[0], l[1].strip('\n'))) # Remover o \n do final do argumento.

        arq_op.close()

        return lista
    except FileNotFoundError:
        print(f"\nArquivo de operações '{nome_arq_operacoes}' não encontrado!\n")
    

def realiza_operacoes(operacoes: list[tuple[str, str]], filmes: io.BufferedRandom):
    '''
    Escolhe qual a operação deve ser realizada a partir de cada instrução em *operações*.
    Caso a bandeira seja 'b', temos que realizar uma busca por uma dada chave, caso seja 'i', devemos inserir
    um dado registro e, caso seja 'r', devemos remover um registro pela sua chave.
    
    As operações são realizadas dentro de *filmes*.
    '''
    for operacao in operacoes:
        if operacao[0] == 'b':
            print(f'Busca pelo registro de chave "{operacao[1]}"')
            resultado_busca = busca_registro(operacao[1], filmes)

            if resultado_busca is not None:
                print(resultado_busca[0] + f" ({resultado_busca[2]} bytes)")
                print(f"Local: offset = {resultado_busca[1]} bytes ({hex(resultado_busca[1])})\n")

        elif operacao[0] == 'i':
            registro = operacao[1]
            registro_bytes = registro.encode()
            identificador = registro.split('|')[0]
            tamanho_registro = len(registro_bytes)
            print(f'Inserção do registro de chave "{identificador}" ({tamanho_registro} bytes)')
            insere_registro(registro_bytes, tamanho_registro, filmes)
    
        elif operacao[0] == 'r':
            print(f'Remoção do registro de chave "{operacao[1]}"')
            resultado_busca = busca_registro(operacao[1], filmes)
            if resultado_busca is not None:
                remove_registro(resultado_busca[1], resultado_busca[2], filmes)
            
            
def busca_registro(identificador: str, filmes: io.BufferedRandom) -> tuple[str, int, int] | None:
    '''
    Realiza a busca por um registro com chave *identificador* no arquivo *filmes*, ignorando registros removidos.
    Retorna None e uma mensagem de erro caso o registro especificado não seja encontrado.
    Retorna uma tupla com o registro, o seu offset e o seu tamanho caso o registro seja encontrado.
    '''
    filmes.seek(CABECALHO)
    offset = CABECALHO
    tamanho_registro = filmes.read(TAM)
    tamanho_int = int.from_bytes(tamanho_registro)
    achou = False

    while tamanho_int != 0 and not achou:
        primeiro = filmes.read(1) 

        if primeiro != CARACTER_REMOCAO: 
            filmes.seek(-1, os.SEEK_CUR) # Retorna o ponteiro de leitura/escrita em 1 posição
            reg = filmes.read(tamanho_int).decode()
            if reg.split(sep='|')[0] == identificador:
                achou = True
            else:
                offset += tamanho_int + TAM 
                while filmes.read(1) == b'#': # Avançar em caso de fragmentação interna!
                    offset += 1

                filmes.seek(offset)
                tamanho_registro = filmes.read(TAM)
                tamanho_int = int.from_bytes(tamanho_registro)

        else:
            offset += tamanho_int + TAM
            filmes.seek(offset) # Posiciona corretamente o ponteiro, não necessariamente no próximo registro ainda
            while filmes.read(1) == b'#': # tamanho_int pode ser menor que o tamanho realmente ocupado pelo registro 
                offset += 1
            filmes.seek(offset) 
            tamanho_registro = filmes.read(TAM)
            tamanho_int = int.from_bytes(tamanho_registro)


    if not achou:
        print("Erro: Registro não encontrado!\n")
        return None
    else:
        return (reg, offset, tamanho_int)

    
def remove_registro(offset: int, tamanho_registro: int, filmes: io.BufferedRandom):
    '''
    Remove um registro com posição em *offset* e tamanho de *tamanho_registro* no arquivo *filmes*.
    O registro é marcado com *CARACTER_REMOCAO* e é adicionado na Lista de Espaços Disponíveis (LED).
    '''
    filmes.seek(offset + TAM)
    
    filmes.write(CARACTER_REMOCAO)
    complemento = b'#'.ljust(tamanho_registro - len(CARACTER_REMOCAO), b'#')
    filmes.write(complemento)
    print(f"Registro removido! ({tamanho_registro} bytes)")
    print(f"Local: offset = {offset} bytes ({hex(offset)})\n")
    
    insere_LED(offset, tamanho_registro, filmes)


def insere_registro(registro: bytes, tamanho_registro: int, filmes: io.BufferedRandom):
    '''
    Insere *registro* de tamanho *tamanho_registro* no arquivo *filmes*.
    Primeiramente é verificado se existe algum espaço disponível na LED que seria adequado para o novo registro. 
    Caso ele seja inserido em alguma posição que estava na LED, ela é atualizada, removendo aquele espaço da LED.
    Caso não houver espaço disponível para ele na LED, o registro é inserido no fim do arquivo. 
    '''
    filmes.seek(0)
    cabeca_led = filmes.read(CABECALHO)
    inserido = False
    
    offset_atual = int.from_bytes(cabeca_led, signed=True) 
    while not inserido and offset_atual != int.from_bytes(FINAL_LED, signed=True): 
        filmes.seek(offset_atual)
        tamanho_atual = int.from_bytes(filmes.read(TAM))
        filmes.seek(1, os.SEEK_CUR) # Pula o caracter de remoção
        proximo_offset = int.from_bytes(filmes.read(PONTEIRO), signed=True) 
        if tamanho_registro <= tamanho_atual: # Inserção do registro em um espaço de registro removido
            filmes.seek(offset_atual)
            filmes.write(tamanho_registro.to_bytes(TAM))
            filmes.write(registro)
            inserido = True # Registro inserido em um espaço armazenado na LED
            remove_LED(offset_atual, proximo_offset, filmes)
            print(f"Tamanho do espaço reutilizado: {tamanho_atual} bytes")
            print(f"Local: offset = {offset_atual} bytes ({hex(offset_atual)})\n")
        else:
            offset_atual = proximo_offset # Atualiza o offset e continua a busca na LED
                
    # Inserção no final do arquivo
    if not inserido:    
        filmes.seek(0, os.SEEK_END)
        tamanho_bytes = tamanho_registro.to_bytes(TAM)
        filmes.write(tamanho_bytes + registro)
        print("Local: fim do arquivo\n")
        
       
def insere_LED(offset: int, tamanho_registro: int, filmes: io.BufferedRandom):
    '''
    Insere um espaço com *offset* e *tamanho_registro* na LED armazenada em *filmes*.
    '''
    filmes.seek(0)
    cabeca = filmes.read(CABECALHO) 
    
    if cabeca == FINAL_LED:
        filmes.seek(0)
        offset_bytes = (offset).to_bytes(CABECALHO, signed=True)
        filmes.write(offset_bytes)
        filmes.seek(offset + TAM + len(CARACTER_REMOCAO))
        filmes.write(FINAL_LED)
    
    else:
        anterior = None
        atual = int.from_bytes(cabeca, signed=True)
        local_correto = False
        
        while not local_correto: # Enquanto não acha o local para inserir ordenado na LED
            filmes.seek(atual)
            tamanho_atual = int.from_bytes(filmes.read(TAM))
            filmes.seek(atual + TAM + len(CARACTER_REMOCAO))
            proximo_offset = filmes.read(PONTEIRO) # Grava o próximo ponteiro
            
            if proximo_offset == FINAL_LED:
                proximo = None
            else:
                proximo = int.from_bytes(proximo_offset, signed=True)
                
            if tamanho_registro < tamanho_atual:
                local_correto = True # Inserção depois de anterior

            else: # Se não encontrou o lugar certo, avança os ponteiros
                anterior = atual
                atual = proximo
                if atual is None: # Fim da LED
                    local_correto = True

        if anterior is None: # Insere na cabeça da LED
            filmes.seek(0)
            filmes.write(offset.to_bytes(CABECALHO, signed=True))
            filmes.seek(offset + TAM + len(CARACTER_REMOCAO))
            filmes.write(atual.to_bytes(PONTEIRO, signed=True))

        else:
            filmes.seek(anterior + TAM + len(CARACTER_REMOCAO))
            filmes.write(offset.to_bytes(CABECALHO))
            filmes.seek(offset + TAM + len(CARACTER_REMOCAO))
            if atual is None:  # Insere no final da LED
                filmes.write(FINAL_LED)
            else:  # Insere atual após o offset inserido na LED
                filmes.write(atual.to_bytes(CABECALHO, signed=True))


def remove_LED(offset: int, ponteiro_proximo: int, filmes: io.BufferedRandom):
    '''
    Remove um espaço da LED, atualizando e mantendo a ordem crescente na LED armazenada em *filmes*.
    A nova ligação é estabelecida a partir de *ponteiro_proximo*.
    '''
    filmes.seek(0)
    cabeca_led = filmes.read(CABECALHO)

    anterior = None
    atual = int.from_bytes(cabeca_led, signed=True)
    removido = False
    
    while not removido and atual != int.from_bytes(FINAL_LED, signed=True):
        filmes.seek(atual + TAM + len(CARACTER_REMOCAO))
        offset_proximo = int.from_bytes(filmes.read(PONTEIRO), signed=True)

        if atual == offset:
            if anterior is None: # Atualiza a cabeça da LED
                filmes.seek(0)
                filmes.write(ponteiro_proximo.to_bytes(CABECALHO, signed=True))
            else: 
                filmes.seek(anterior + TAM + len(CARACTER_REMOCAO))
                filmes.write(ponteiro_proximo.to_bytes(PONTEIRO, signed=True))
            removido = True
        
        # Atualização dos ponteiros
        anterior = atual
        atual = offset_proximo
            
            
def compacta_arquivo(filmes: io.BufferedRandom):
    '''
    Compacta o arquivo, mudando o arquivo *filmes*, retirando todos os registros removidos,
    ou seja, removendo a fragmentação externa.
    '''
    filmes.seek(CABECALHO)
    lista_registros: list[tuple[bytes, bytes]] = []    
    tamanho_registro = filmes.read(TAM)
    tamanho_int = int.from_bytes(tamanho_registro)
    
    while tamanho_int != 0:
        
        primeiro = filmes.read(1)

        if primeiro != CARACTER_REMOCAO:
            filmes.seek(-1, os.SEEK_CUR) # Retorna 1 posição
            reg = filmes.read(tamanho_int)
            lista_registros.append((tamanho_registro, reg))
            
            proximo_caracter = filmes.read(1)
            if proximo_caracter: # Caso o arquivo acabe ele não precisa voltar
                while proximo_caracter == b'#':
                    proximo_caracter = filmes.read(1)
                filmes.seek(-1, os.SEEK_CUR)
                
            tamanho_registro = filmes.read(TAM)
            tamanho_int = int.from_bytes(tamanho_registro)
              
        else:
            
            filmes.seek(tamanho_int - 1, os.SEEK_CUR)

            proximo_caracter = filmes.read(1)
            if proximo_caracter: 
                while proximo_caracter == b'#':
                    proximo_caracter = filmes.read(1)
                filmes.seek(-1, os.SEEK_CUR) # volta um

            tamanho_registro = filmes.read(TAM)
            tamanho_int = int.from_bytes(tamanho_registro)
       
    filmes.close()
    novo_arquivo = open('temporario.dat', 'wb')
    novo_arquivo.write(FINAL_LED)
    
    for registro in lista_registros:
        novo_arquivo.write(registro[0])
        novo_arquivo.write(registro[1])

    novo_arquivo.close()
    os.remove('filmes.dat')
    os.rename('temporario.dat', 'filmes.dat')
    
    
def imprime_led(filmes: io.BufferedRandom):
    '''
    Imprime todos os elementos da LED em ordem crescente de tamanho, juntamente ao offset
    vinculado e mostra o total de registros removidos.
    '''
    filmes.seek(0)
    cabeca_led = int.from_bytes(filmes.read(CABECALHO), signed=True)
    offset_atual = cabeca_led
    total_led = 0 # Contador de elementos na LED

    lista_led: list[tuple[int, int]] = []

    while offset_atual != int.from_bytes(FINAL_LED, signed=True):
        filmes.seek(offset_atual)
        tamanho_registro_removido = int.from_bytes(filmes.read(TAM))
        lista_led.append((offset_atual, tamanho_registro_removido)) # Lista de tuplas com o offset e o tamanho de cada registro removido
        total_led += 1
        filmes.seek(offset_atual + TAM + len(CARACTER_REMOCAO))
        offset_atual = int.from_bytes(filmes.read(PONTEIRO), signed=True)
        
    print("\nLED -> ", end='')
    for elemento in lista_led:
        print(f"[offset: {elemento[0]}, tam: {elemento[1]}] -> ", end='')
    print("FIM")
    print(f"Total: {total_led} espaços disponíveis.")
    print("A LED foi impressa com sucesso!\n")


def main():

    try:
        filmes = open("filmes.dat", 'r+b')
        if len(argv) < 2 or len(argv) > 3:
            raise TypeError('Número incorreto de argumentos!\n')
        
        elif len(argv) == 2:
            if argv[1] == '-c':
                compacta_arquivo(filmes)
                print("\nCompactação realizada com sucesso!\n")
            elif argv[1] == "-p":
                imprime_led(filmes)
            else:
                raise TypeError('Comando incorreto!\n')
            
        else: # len(argv) == 3
            if argv[1] == '-e':
                operacoes = le_arquivo_operacoes(argv[2])
                if os.path.exists(argv[2]):
                    realiza_operacoes(operacoes, filmes)
                    print(f"As operações do arquivo '{argv[2]}' foram executadas com sucesso!\n")
            else:
                raise TypeError('Comando incorreto!\n')

            filmes.close()
    except FileNotFoundError:
        print("\nArquivo de registros não encontrado!\n")
        

if __name__ == "__main__":
    main()
