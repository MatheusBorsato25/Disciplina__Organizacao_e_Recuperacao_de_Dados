from sys import argv

def leia_registros(nome_arq_entrada: str) -> list[tuple[int, int]]:
    
    arq = open(nome_arq_entrada, 'rb')
    numero_registros = int.from_bytes(arq.read(4))
    chaves: list[tuple[int, int]] = []
    i = 0

    while i < numero_registros:
        offset_atual = arq.tell()
        tamanho_registro = int.from_bytes(arq.read(2))
        registro = arq.read(tamanho_registro)
        lista_campos_registro = registro.split(sep=b'|')
        identificador = int.from_bytes(lista_campos_registro[0])
        chaves.append((identificador, offset_atual))
        i += 1

    arq.close()

    return chaves


def escreva_registros_ordenados(nome_arq_entrada: str, nome_arq_saida: str, chaves: list[tuple[int, int]]) -> None:
    
    with open(nome_arq_entrada, 'rb') as arq_entrada, open(nome_arq_saida, 'wb') as arq_saida:
        numero_registros = (int.from_bytes(arq_entrada.read(4)))
        qtd_registros = numero_registros.to_bytes(4)
        arq_saida.write(qtd_registros)

        for (chave, offset) in chaves:
            arq_entrada.seek(offset)
            tamanho_bytes = arq_entrada.read(2)
            tamanho_registro = int.from_bytes(tamanho_bytes)
            registro = arq_entrada.read(tamanho_registro)
            arq_saida.write(tamanho_bytes + registro)
    

def keysort(nome_arq_entrada: str, nome_arq_saida: str) -> None:

    chaves: list[tuple[int, int]] = leia_registros(nome_arq_entrada)
    chaves.sort(key=lambda chaves: chaves[0])
    escreva_registros_ordenados(nome_arq_entrada, nome_arq_saida, chaves)

     
def main() -> None:
    if len(argv) < 3:
        raise TypeError('Número incorreto de argumentos\nModo de uso: nome_arq_entrada nome_arq_saida')

    keysort(argv[1], argv[2])


if __name__ == '__main__':
    main()
    