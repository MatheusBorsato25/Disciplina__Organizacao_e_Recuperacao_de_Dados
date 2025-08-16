
# Alunos: Guilherme Jucoski da Silva - RA: 138642; Matheus Henrique Borsato - RA: 138246.

from sys import argv
from struct import pack, unpack, calcsize
import io
import os



# CONSTANTES
TAM_MAX_BUCKET = 5
FORMATO_HEADER = 'i'
FORMATO_INT = 'i' # um inteiro de 4 bytes
FORMATO_BUCKET = (TAM_MAX_BUCKET + 2) * 'i'
SIZEOF_HEADER = calcsize(FORMATO_HEADER)
SIZEOF_INT = calcsize(FORMATO_INT)
SIZEOF_BUCKET = calcsize(FORMATO_BUCKET)



class Bucket():
    # Representa um bucket com sua profundidade local, sua quantidade de chaves e a lista de chaves
    profundidade: int
    cont_chaves: int
    chaves: list[int]
    
    def __init__(self, profundidade: int = 0, cont_chaves: int = 0) -> None:
        self.profundidade = profundidade
        self.cont_chaves = cont_chaves
        self.chaves = [-1] * TAM_MAX_BUCKET # Inicializa as posições com -1, indicando locais vazios.



class Diretorio():
    # Representa o diretório do hashing extensível, com a profundidade global, o tamanho e a lista de referências para os buckets
    profundidade_dir: int
    tamanho_dir: int
    referencias: list[int]
    
    def __init__(self, profundidade_dir: int = 0, tamanho_dir: int = 1) -> None:
        self.profundidade_dir = profundidade_dir
        self.tamanho_dir = tamanho_dir
        self.referencias = []
      
        

class PED():
    # Gerencia a Pilha de Espaços Disponíveis (PED) dentro do arquivo de buckets 
    arquivo_buckets: io.BufferedRandom
    
    def __init__(self, arquivo: io.BufferedRandom) -> None:
        self.arquivo_buckets = arquivo
        
        
    def __ped_vazia(self) -> bool:
        '''
        Verifica se a PED está vazia (cabeçalho == -1).
        '''
        self.arquivo_buckets.seek(0, os.SEEK_SET)
        cabecalho = unpack(FORMATO_HEADER, self.arquivo_buckets.read(SIZEOF_HEADER))[0]
        if cabecalho == -1:
            return True
        return False
    
    
    def insere_ped(self, rrn: int) -> None:
        '''
        Insere um novo RRN no topo da PED, encadeando o antigo topo na PED dentro do arquivo.
        '''
        self.arquivo_buckets.seek(0, os.SEEK_SET)
        topo = unpack(FORMATO_HEADER, self.arquivo_buckets.read(SIZEOF_HEADER))[0]
        
        self.arquivo_buckets.seek(0, os.SEEK_SET)
        self.arquivo_buckets.write(pack(FORMATO_HEADER, rrn))
        
        self.arquivo_buckets.seek(rrn * SIZEOF_BUCKET + SIZEOF_INT, os.SEEK_CUR)
        self.arquivo_buckets.write(pack(FORMATO_INT, topo))
        
        
    def remove_ped(self) -> int:
        '''
        Remove o topo da PED e retorna o RRN disponível, atualizando o novo topo.
        Retorna -1 em caso de PED vazia.
        '''
        if self.__ped_vazia():
            return -1

        self.arquivo_buckets.seek(0, os.SEEK_SET)
        rrn_topo = unpack(FORMATO_HEADER, self.arquivo_buckets.read(SIZEOF_HEADER))[0]
        
        self.arquivo_buckets.seek(rrn_topo * SIZEOF_BUCKET + SIZEOF_INT, os.SEEK_CUR)
        novo_topo = self.arquivo_buckets.read(SIZEOF_INT)
        
        self.arquivo_buckets.seek(0, os.SEEK_SET)
        self.arquivo_buckets.write(novo_topo)
        
        return rrn_topo
    
    
    def imprime_ped(self) -> None:
        '''
        Imprime todos os RRNs disponíveis na PED, mostrando o encadeamento e o total de espaços.
        '''
        print("-----PED-----\n")
        if self.__ped_vazia():
            print("PED vazia!\n")
        else:
            lista_ped: list[int] = []
            self.arquivo_buckets.seek(0, os.SEEK_SET)
            elemento_ped = unpack(FORMATO_HEADER, self.arquivo_buckets.read(SIZEOF_HEADER))[0]
            while elemento_ped != -1:
                lista_ped.append(elemento_ped)
                self.arquivo_buckets.seek(SIZEOF_HEADER + elemento_ped * SIZEOF_BUCKET + SIZEOF_INT, os.SEEK_SET)
                elemento_ped = unpack(FORMATO_INT, self.arquivo_buckets.read(SIZEOF_INT))[0]
                
            print("PED -> ", end='')
            for elemento in lista_ped:
                print(f"[RRN: {elemento}] -> ", end='')
            print("FIM")
            print(f"Total: {len(lista_ped)} espaços disponíveis.")
            print("A PED foi impressa com sucesso!\n")

                
                
class HashingExtensível():
    # Implementa o hashing extensível com diretório e arquivo de buckets
    arq_buckets: io.BufferedRandom
    diretorio: Diretorio
    ped: PED
    
    def __init__(self) -> None:    
        self.diretorio = Diretorio()
        self.inicializa()
        self.ped = PED(self.arq_buckets)
    
    
    def inicializa(self) -> None:
        # Se os arquivos de diretório e buckets existem, carrega os dados salvos
        if os.path.exists('dir.dat') and os.path.exists('buckets.dat'):
            dir = open('dir.dat', 'r+b')
            self.arq_buckets = open('buckets.dat', 'r+b')
            self.diretorio.profundidade_dir = unpack(FORMATO_INT, dir.read(SIZEOF_INT))[0]
            self.diretorio.tamanho_dir = 2 ** self.diretorio.profundidade_dir
            quantidade_referencias: str = f'{self.diretorio.tamanho_dir}i'
            self.diretorio.referencias = list(unpack(quantidade_referencias, dir.read(SIZEOF_INT * self.diretorio.tamanho_dir)))
        # Caso contrário, cria a estrutura inicial com um único bucket
        else:
            self.arq_buckets = open('buckets.dat', 'w+b')
            primeiro_bucket = Bucket()
            self.arq_buckets.write(pack(FORMATO_HEADER, -1))
            rrn = 0
            self.__escreve_bucket(primeiro_bucket, rrn)
            self.diretorio.referencias.append(rrn)
    
    
    def finaliza(self) -> None:
        '''
        Finaliza o Hashing Extensível salvando o diretório e fechando o arquivo de buckets
        '''
        self.__escreve_diretorio()
        self.arq_buckets.close()
        
        
    def __escreve_diretorio(self):
        '''
        Escreve a profundidade e as referências atuais do diretório no arquivo 'dir.dat', além de fechar o arquivo.
        '''
        arquivo_diretorio = open('dir.dat', 'wb')
        arquivo_diretorio.write(pack(FORMATO_INT, self.diretorio.profundidade_dir))
        formato_quantidade_referencias: str = f'{self.diretorio.tamanho_dir}i'
        arquivo_diretorio.write(pack(formato_quantidade_referencias, *self.diretorio.referencias))
        arquivo_diretorio.close()
        
        
    def __escreve_bucket(self, bucket: Bucket, rrn: int):
        '''
        Escreve *bucket* no arquivo de buckets com base na posição calculada a partir de *rrn*.
        '''
        offset = SIZEOF_HEADER + rrn * SIZEOF_BUCKET
        self.arq_buckets.seek(offset, os.SEEK_SET)
        informacoes_bucket = pack(FORMATO_BUCKET, bucket.profundidade, bucket.cont_chaves, *bucket.chaves)
        self.arq_buckets.write(informacoes_bucket)
        
        
    def __le_bucket(self, rrn: int) -> Bucket:
        '''
        Lê um bucket do arquivo de buckets a partir do *rrn* e reconstrói o objeto.
        '''
        offset = SIZEOF_HEADER + rrn * SIZEOF_BUCKET
        self.arq_buckets.seek(offset, os.SEEK_SET)
        dados = self.arq_buckets.read(SIZEOF_BUCKET)
        valores = unpack(FORMATO_BUCKET, dados)
            
        bucket = Bucket(valores[0], valores[1])
        bucket.chaves = list(valores[2:])
        
        return bucket    
    
    
    def __calcula_rrn(self) -> int:
        '''
        Calcula o RRN do próximo bucket com base na posição final do arquivo de buckets, em caso de PED vazia.
        No caso da PED não estar vazia, recupera seu topo.
        '''
        topo_ped = self.ped.remove_ped()
        
        if topo_ped == -1:
            self.arq_buckets.seek(0, os.SEEK_END)
            offset_final = self.arq_buckets.tell()
            rrn = (offset_final - SIZEOF_HEADER) // SIZEOF_BUCKET
        else:
            rrn = topo_ped
            
        return rrn        
     
     
    def __gera_endereco(self, chave: int, profundidade: int) -> int:
        '''
        Gera o endereço de *chave* com base em *profundidade*, a partir de um processo de inversão dos bits.
        '''
        endereco = 0
        mascara = 1
        valor_hash = chave
        
        for i in range(profundidade):
            endereco <<= 1
            bit_baixa_ordem = valor_hash & mascara
            endereco = endereco | bit_baixa_ordem
            valor_hash >>= 1
            
        return endereco
    
    
    def busca_chave(self, chave: int) -> tuple[bool, int, Bucket]:
        '''
        Busca a chave no hashing extensível dentro do bucket obtido pelo endereço
        e retorna se achou, o RRN e o bucket correspondente.
        '''
        endereco = self.__gera_endereco(chave, self.diretorio.profundidade_dir)
        rrn_bucket = self.diretorio.referencias[endereco]
        bucket_encontrado = self.__le_bucket(rrn_bucket)
        achou = self.__procura_bucket(chave, bucket_encontrado)[0]
        if achou:
            return True, rrn_bucket, bucket_encontrado
        
        return False, rrn_bucket, bucket_encontrado
        
    
    def __procura_bucket(self, chave: int, bucket: Bucket) -> tuple[bool, int]:
        '''
        Procura a chave dentro do bucket e retorna se encontrou e sua posição no bucket.
        Retorna False e -1, caso não tenha encontrado.
        '''
        chaves = bucket.chaves
        for indice in range(bucket.cont_chaves):
            if chaves[indice]== chave:
                return True, indice
        return False, -1 
    
    
    def __calcula_quantidade_bucket(self) -> tuple[int, int]:
        '''
        Calcula o total de buckets existentes e quantos estão válidos (não removidos).
        '''
        self.arq_buckets.seek(0, os.SEEK_END)
        offset_final = self.arq_buckets.tell()
        quantidade_buckets = (offset_final - SIZEOF_HEADER) // SIZEOF_BUCKET
        quantidade_removidos = self.__calcula_quantidade_buckets_removidos(quantidade_buckets)
 
        quantidade_buckets_validos = quantidade_buckets - quantidade_removidos
        return quantidade_buckets, quantidade_buckets_validos
    
    
    def __calcula_quantidade_buckets_removidos(self, quantidade_buckets: int) -> int:
        '''
        Percorre todos os buckets e conta quantos estão marcados como removidos (profundidade == -1)
        '''
        self.arq_buckets.seek(SIZEOF_HEADER, os.SEEK_SET)
        contador_removidos: int = 0
 
        for i in range(quantidade_buckets):
            profundidade = unpack(FORMATO_INT, self.arq_buckets.read(SIZEOF_INT))[0]
            if profundidade == -1:
                contador_removidos += 1
            self.arq_buckets.seek(SIZEOF_BUCKET - SIZEOF_INT, os.SEEK_CUR) # Pula o restante do bucket.
        
        return contador_removidos
    
        
    def insere_chave(self, chave: int) -> bool:
        '''
        Tenta inserir uma chave. Se já existir, retorna False. Se não, insere a chave e retorna True.
        '''
        achou, rrn_bucket, bucket_encontrado = self.busca_chave(chave)
        if achou:
            return False # Chave duplicada
        else:
            self.__insere_chave_bucket(chave, rrn_bucket, bucket_encontrado)
            return True
    
    
    def __insere_chave_bucket(self, chave: int, rrn_bucket: int, bucket: Bucket):
        '''
        Insere a chave no bucket, se houver espaço. Caso contrário, divide o bucket e tenta novamente.
        '''
        if bucket.cont_chaves < TAM_MAX_BUCKET:
            bucket.chaves[bucket.cont_chaves] = chave
            bucket.cont_chaves += 1
            self.__escreve_bucket(bucket, rrn_bucket)
        else:
            self.__divide_bucket(rrn_bucket, bucket)
            self.insere_chave(chave)
            
            
    def __divide_bucket(self, rrn_bucket: int, bucket: Bucket):
        '''
        Divide *bucket*, que está cheio, criando um novo e redistribuindo as chaves.
        Depois, escreve os dois no arquivo de buckets.
        '''
        if bucket.profundidade == self.diretorio.profundidade_dir:
            self.__dobra_dir() # Dobra o diretório se for necessário para alocar mais chaves.
        novo_bucket = Bucket()
        rrn_novo_bucket = self.__calcula_rrn() # RRN onde o novo bucket será armazenado
        # Determina o intervalo de índices do diretório que devem apontar para o novo bucket
        novo_inicio, novo_fim = self.__encontra_novo_intervalo(bucket)
        for i in range(novo_inicio, novo_fim + 1):
            self.diretorio.referencias[i] = rrn_novo_bucket
        bucket.profundidade += 1
        novo_bucket.profundidade = bucket.profundidade
        self.__redistribui_chaves(bucket, novo_bucket)
        self.__escreve_bucket(bucket, rrn_bucket)
        self.__escreve_bucket(novo_bucket, rrn_novo_bucket)
        
            
    def __dobra_dir(self):
        '''
        Dobra o diretório duplicando todas as referências e atualizando sua profundidade e seu tamanho.
        '''
        novas_referencias: list[int] = []
        for ref in self.diretorio.referencias:
            novas_referencias.append(ref)
            novas_referencias.append(ref)
        self.diretorio.referencias = novas_referencias
        self.diretorio.profundidade_dir += 1
        self.diretorio.tamanho_dir *= 2
    
    
    def __encontra_novo_intervalo(self, bucket: Bucket) -> tuple[int, int]:
        '''
        Calcula o intervalo de índices do diretório que devem apontar para o novo bucket com base no *bucket*
        que vai ser dividido.
        '''
        mascara = 1
        chave = bucket.chaves[0]
        endereco_comum = self.__gera_endereco(chave, bucket.profundidade)
        endereco_comum <<= 1
        endereco_comum = endereco_comum | mascara
        bits_a_preencher = self.diretorio.profundidade_dir - (bucket.profundidade + 1)
        novo_inicio, novo_fim = endereco_comum, endereco_comum
        for i in range(bits_a_preencher):
            novo_inicio <<= 1
            novo_fim <<= 1
            novo_fim = novo_fim | mascara
            
        return novo_inicio, novo_fim
    
    
    def __armazena_chaves_bucket(self, bucket: Bucket) -> list[int]:
        '''
        Filtra e retorna as chaves válidas de *bucket*.
        '''
        chaves_validas: list[int] = []
        for chave in bucket.chaves:
            if chave != -1:
                chaves_validas.append(chave)
        
        return chaves_validas


    def __redistribui_chaves(self, bucket_original: Bucket, novo_bucket: Bucket):
        '''
        Redistribui as chaves entre *bucket_original* e *novo_bucket* após a divisão do original.
        '''
        chaves_validas: list[int] = self.__armazena_chaves_bucket(bucket_original)
        bucket_original.cont_chaves = 0
        bucket_original.chaves = [-1] * TAM_MAX_BUCKET
        
        for chave in chaves_validas:
            endereco = self.__gera_endereco(chave, self.diretorio.profundidade_dir)
            bit_redistribuicao = endereco >> (self.diretorio.profundidade_dir - bucket_original.profundidade)
            bit_diferenciador = bit_redistribuicao & 1
            if bit_diferenciador == 0:
                bucket_original.chaves[bucket_original.cont_chaves] = chave
                bucket_original.cont_chaves += 1
            elif bit_diferenciador == 1:
                novo_bucket.chaves[novo_bucket.cont_chaves] = chave
                novo_bucket.cont_chaves += 1            
    
   
    def remove_chave(self, chave: int) -> bool:
        '''
        Remove uma chave do Hashing Extensível. Se ela não estiver nele, retorna False.
        '''
        achou, rrn_bucket, bucket_encontrado = self.busca_chave(chave)
        if not achou:
            return False
        removeu = self.__remove_chave_bucket(chave, rrn_bucket, bucket_encontrado)
        return removeu
    
    
    def __remove_chave_bucket(self, chave: int, rrn_bucket: int, bucket: Bucket) -> bool:
        '''
        Remove a chave do bucket e reordena os elementos, escrevendo o novo bucket na sequência.
        Tenta concatenar os buckets se possível.
        '''
        removeu = False
        resultado_busca_bucket = self.__procura_bucket(chave, bucket)
        indice = resultado_busca_bucket[1]
        if resultado_busca_bucket[0]:
            chave_removida = bucket.chaves[indice]
            bucket.cont_chaves -= 1
            for i in range(indice, bucket.cont_chaves):
                bucket.chaves[i] = bucket.chaves[i + 1]
            bucket.chaves[bucket.cont_chaves] = -1
            self.__escreve_bucket(bucket, rrn_bucket)
            removeu = True
        
        if removeu:
            self.__tenta_combinar_bucket(chave_removida, rrn_bucket, bucket)
            return True
        
        return False
    
    
    def __tenta_combinar_bucket(self, chave_removida: int, rrn_bucket: int, bucket: Bucket) -> None:
        '''
        Tenta concatenar o bucket com seu "amigo" se houver espaço suficiente neles. 
        Se concatenar, tenta diminuir o diretório. Se diminuir o diretório, tenta concatenar novamente.
        '''
        tem_amigo, endereco_amigo = self.__encontra_bucket_amigo(chave_removida, bucket)
        if not tem_amigo:
            return
        if endereco_amigo is not None:
            rrn_bucket_amigo = self.diretorio.referencias[endereco_amigo]
            bucket_amigo = self.__le_bucket(rrn_bucket_amigo)
            if (bucket.cont_chaves + bucket_amigo.cont_chaves) <= TAM_MAX_BUCKET:
                bucket_concatenado = self.__combina_buckets(rrn_bucket, bucket, rrn_bucket_amigo, bucket_amigo)
                self.diretorio.referencias[endereco_amigo] = rrn_bucket
                if self.__tenta_diminuir_diretorio():
                    self.__tenta_combinar_bucket(chave_removida, rrn_bucket, bucket_concatenado)
    
    
    def __encontra_bucket_amigo(self, chave_removida: int, bucket: Bucket) -> tuple[bool, int|None]:
        '''
        Encontra o bucket "amigo" de *bucket*, se houver, com endereço diferindo apenas no último bit.
        '''
        if self.diretorio.profundidade_dir == 0:
            return False, None
        if bucket.profundidade < self.diretorio.profundidade_dir:
            return False, None
        endereco_comum = self.__gera_endereco(chave_removida, bucket.profundidade)
        endereco_bucket_amigo = endereco_comum ^ 1
        return True, endereco_bucket_amigo
    
    
    def __combina_buckets(self, rrn_bucket: int, bucket: Bucket, rrn_bucket_amigo: int, bucket_amigo: Bucket) -> Bucket:
        '''
        Junta as chaves de *bucket* e *bucket_amigo*, concatenando-os e retornando o bucket concatenado e atualizado.
        Realiza a remoção lógica do bucket amigo.
        '''
        for i in range(bucket_amigo.cont_chaves):
            bucket.chaves[bucket.cont_chaves] = bucket_amigo.chaves[i]
            bucket.cont_chaves += 1
        bucket.profundidade -= 1
        self.__escreve_bucket(bucket, rrn_bucket)
        
        # Remoção Lógica:
        bucket_amigo.profundidade = -1
        self.__escreve_bucket(bucket_amigo, rrn_bucket_amigo)
        self.ped.insere_ped(rrn_bucket_amigo)
        
        return bucket
    
    
    def __tenta_diminuir_diretorio(self) -> bool:
        '''
        Verifica se o diretório pode ser diminuído pela metade. Retorna True se foi reduzido.
        '''
        if self.diretorio.profundidade_dir == 0:
            return False
        diminuir = True
        for i in range(0, self.diretorio.tamanho_dir, 2):
            if self.diretorio.referencias[i] != self.diretorio.referencias[i + 1]:
                diminuir = False
                break
        if diminuir:
            novas_referencias: list[int] = []
            for i in range(0, self.diretorio.tamanho_dir - 1, 2):
                rrn = self.diretorio.referencias[i]
                novas_referencias.append(rrn)
            self.diretorio.referencias = novas_referencias
            self.diretorio.profundidade_dir -= 1
            self.diretorio.tamanho_dir //= 2
        return diminuir
    
    
    def imprime_diretorio(self) -> None:
        '''
        Imprime a tabela do diretório: cada posição aponta para um bucket.
        Imprime também a profundidade do diretório, seu tamanho e o total de buckets referenciados.
        '''
        print("\n----- Diretório -----\n")
        posicao_diretorio: int = 0
        
        for rrn in self.diretorio.referencias:
            print(f"dir[{posicao_diretorio}] = bucket[{rrn}]")
            posicao_diretorio += 1
            
        print(f"\nProfundidade = {self.diretorio.profundidade_dir}")
        print(f"Tamanho atual = {self.diretorio.tamanho_dir}")
        total_buckets = self.__calcula_quantidade_bucket()[1]
        print(f"Total de buckets = {(total_buckets)}")
        print('\n')
       
       
    def imprime_buckets(self) -> None:
        '''
        Imprime o conteúdo de todos os buckets ativos (profundidade, quantidade de chaves e as chaves).
        Sinaliza os buckets removidos e imprime a PED.
        '''
        print("\n----- Buckets -----")
        
        for i in range(self.__calcula_quantidade_bucket()[0]):            
            bucket = self.__le_bucket(i)
            if bucket.profundidade != -1:
                print(f"\nBucket {i} (Prof = {bucket.profundidade}):")
                print(f"ContaChaves = {bucket.cont_chaves}")
                print(f"Chaves = {bucket.chaves}")
            else:
                print(f"\nBucket {i} --> Removido")
        print('\n')
        
        self.ped.imprime_ped()
    
    
    
def le_arquivo_operacoes(nome_arq_operacoes: str) -> list[tuple[str, str]]:
    '''
    Abre o arquivo de operações e lê todas as operações que devem ser realizadas e
    as separam em bandeira e argumento. 
    '''
    lista = []

    try:
        arq_op = open(nome_arq_operacoes, 'r')
        linhas = arq_op.readlines()
        for linha in linhas:
            # Divide a linha em duas partes, com a bandeira no primeiro espaço e o argumento no segundo.
            elementos = linha.split() # Divide a partir do primeiro espaço da linha
            lista.append((elementos[0], elementos[1].strip('\n'))) # Remover o \n do final do argumento.

        arq_op.close()

        return lista
    except FileNotFoundError:
        print(f"\nArquivo de operações '{nome_arq_operacoes}' não encontrado!\n")
    


def realiza_operacoes(operacoes: list[tuple[str, str]], hashing: HashingExtensível):
    '''
    Realiza todas as *operacoes* de busca, inserção e remoção dentro de *hashing*, imprimindo
    todas as mensagens correspondentes ao que foi realizado.
    '''
    for operacao in operacoes:
        if operacao[0] == 'b': # Busca
            chave = int(operacao[1])
            resultado_busca = hashing.busca_chave(chave)
            if resultado_busca[0]:
                print(f"> Busca pela chave {chave}: Chave encontrada no bucket {resultado_busca[1]}.")
            else:
                print(f"> Busca pela chave {chave}: Chave não encontrada.")
                
        elif operacao[0] == 'i': # Inserção
            chave = int(operacao[1])
            inseriu = hashing.insere_chave(chave)
            if inseriu:
                print(f"> Inserção da chave {chave}: Sucesso.")
            else:
                print(f"> Inserção da chave {chave}: Falha - Chave duplicada")
            
        elif operacao[0] == 'r': # Remoção
            chave = int(operacao[1])
            removeu = hashing.remove_chave(chave)
            if removeu:
                print(f"> Remoção da chave {chave}: Sucesso.")
            else:
                print(f"> Remoção da chave {chave}: Falha - Chave não encontrada.")    

        
        
def main() -> None:
    '''
    Função principal que interpreta os argumentos da linha de comando e executa 
    ações como imprimir diretório, imprimir buckets ou processar o arquivo de operações.
    '''
    if len(argv) < 2 or len(argv) > 3:
        raise TypeError('Número incorreto de argumentos!\n')
    
    elif len(argv) == 2:
        if argv[1] == '-pd' or argv[1] == '-pb':
            if not os.path.exists('dir.dat') or not os.path.exists('buckets.dat'):
                print("\nHashing extensível ainda não inicializado!\n")
                return
            else:
                hashing = HashingExtensível()
                if argv[1] == '-pd':
                    hashing.imprime_diretorio()
                    hashing.finaliza()
                elif argv[1] == '-pb':
                    hashing.imprime_buckets()
                    hashing.finaliza()
        else:
            raise TypeError('Comando incorreto!\n')
        
    else: # len(argv) == 3
        if argv[1] == '-e':
            operacoes = le_arquivo_operacoes(argv[2])
            if os.path.exists(argv[2]):
                hashing = HashingExtensível()
                realiza_operacoes(operacoes, hashing)
                print(f"As operações do arquivo '{argv[2]}' foram executadas com sucesso!\n")
                hashing.finaliza()
        else:
            raise TypeError('Comando incorreto!\n')
        

if __name__ == "__main__":
    main()
    