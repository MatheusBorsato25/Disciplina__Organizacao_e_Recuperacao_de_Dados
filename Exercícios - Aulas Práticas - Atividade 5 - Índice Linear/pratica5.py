from struct import pack, unpack, calcsize
import io
import os

# CONSTANTES
FORMATO_ELEMINDICE = '2i'   # dois inteiros de 4 bytes
FORMATO_HEADER = 'i'        # um inteiro de 4 bytes
FORMATO_TAMREG = 'h'        # um inteiro de 2 bytes
SIZEOF_ELEMINDICE = calcsize(FORMATO_ELEMINDICE)    # 8 bytes
SIZEOF_HEADER = calcsize(FORMATO_HEADER)            # 4 bytes
SIZEOF_TAMREG = calcsize(FORMATO_TAMREG)            # 2 bytes

# por padrão, as funções do módulo struct representam os dados em formato 'little endian'
# para facilitar, o arquivo 'trabalhos.dat' também foi gravado em formato 'little endian'

def leia_reg(arq: io.BufferedRandom) -> tuple[str, int]:
    
    tamanho_registro = unpack(FORMATO_TAMREG, arq.read(SIZEOF_TAMREG))[0]
    registro = arq.read(tamanho_registro)
    registro_decodificado = registro.decode()
    return (registro_decodificado, tamanho_registro)


def constroi_indice(arq: io.BufferedRandom) -> list[tuple[int, int]]:
    
    numero_registros = unpack(FORMATO_HEADER, arq.read(SIZEOF_HEADER))[0]
    lista: list[tuple[int, int]] = []

    for i in range(numero_registros):
        offset_atual = arq.tell()
        arq.seek(offset_atual + SIZEOF_TAMREG)
        rem = arq.read(1)
        if rem != b'*':
            arq.seek(offset_atual) 
            registro = leia_reg(arq)
            texto = registro[0]
            identificador = int(texto.split(sep='|')[0])
            lista.append((identificador, offset_atual))

    lista.sort()
    return lista


def grava_indice(indice: list[tuple[int, int]]) -> None:
    
    arq_indice = open('indice.dat', 'wb')
    total_registros = len(indice)
    total = pack(FORMATO_HEADER, total_registros)
    arq_indice.write(total)

    for elemento in indice:
        combinacao = pack(FORMATO_ELEMINDICE, elemento[0], elemento[1])
        arq_indice.write(combinacao)

    arq_indice.close()


def carrega_indice() -> list[tuple[int, int]]:
    
    arq_indice = open('indice.dat', 'rb')
    numero_registros = unpack(FORMATO_HEADER, arq_indice.read(SIZEOF_HEADER))[0]
    lista: list[tuple[int, int]] = []

    for i in range(numero_registros):
        elemento = unpack(FORMATO_ELEMINDICE, arq_indice.read(SIZEOF_ELEMINDICE))
        lista.append(elemento)
    
    arq_indice.close()
    
    return lista


def busca_binaria(chave: int, indice: list[tuple[int, int]]) -> int:
    
    inicio = 0
    fim = len(indice) - 1

    while inicio <= fim:
        meio = (inicio + fim) // 2
        if indice[meio][0] == chave:
            return meio
        elif indice[meio][0] < chave:
            inicio = meio + 1
        else:
            fim = meio - 1
    
    return -1
   

def le_e_imprime(arq: io.BufferedRandom, offset: int) -> None:
    
    arq.seek(offset)
    tamanho_registro = unpack(FORMATO_TAMREG, arq.read(SIZEOF_TAMREG))[0]
    registro = arq.read(tamanho_registro).decode()
    lista_campos = registro.split('|')[:-1]
    
    print(f"\nInformações do Registro | Offset {offset} | {tamanho_registro} bytes:\n")
    for i in range(len(lista_campos)):
        print(f"Campo {i + 1}: {lista_campos[i]}")
        
        
def imprime_indice(indice: list[tuple[int, int]]) -> None:
    
    for elemento in indice:
        print(f'Identificador: {elemento[0]}; Offset: {elemento[1]}')


def remove_registro(arq: io.BufferedRandom, id: int, indice: list[tuple[int, int]]):
    
    ind = busca_binaria(id, indice)
    
    if ind != -1:
        offset = indice[ind][1]
        indice.pop(ind)
        arq.seek(offset + SIZEOF_TAMREG)
        arq.write('*'.encode())
        
        arq.seek(0, os.SEEK_SET)
        numero_registros = unpack(FORMATO_HEADER, arq.read(SIZEOF_HEADER))[0]
        numero_registros -= 1
        arq.seek(0, os.SEEK_SET)
        total_registros = pack(FORMATO_HEADER, numero_registros)
        arq.write(total_registros)
    
    
def main() -> None:
    arq = open('trabalhos.dat', 'r+b')
    if os.path.exists('indice.dat'):
        indice = carrega_indice()
    else:
        indice = constroi_indice(arq)
        grava_indice(indice)

    # imprime_indice(indice)
    id = input("\nDigite o ID (ou Enter para sair): ")
    while id != '':
        ind = busca_binaria(int(id), indice)
        if ind == -1:
            print("\nRegistro não encontrado!")
        else:
            offset = indice[ind][1]
            le_e_imprime(arq, offset)
            remove = input("\nVocê deseja remover o registro? (S/N): ")
            
            if remove == 'S':
                remove_registro(arq, int(id), indice)
                
        id = input("\n\nDigite o ID (ou Enter para sair): ")
        
    grava_indice(indice)
    arq.close()
  
    
if __name__ == '__main__':
    main()
    