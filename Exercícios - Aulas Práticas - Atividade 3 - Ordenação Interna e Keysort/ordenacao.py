from sys import argv

def leia_registros(nome_arq_entrada: str) -> list[tuple[int, bytes]]:
    
    arq = open(nome_arq_entrada, 'rb')
    numero_registros = int.from_bytes(arq.read(4))
    registros: list[tuple[int, bytes]] = []
    i = 0

    while i < numero_registros:
        tamanho_registro = int.from_bytes(arq.read(2))
        registro = arq.read(tamanho_registro)
        tamanho_bytes = (tamanho_registro).to_bytes(2)
        lista_campos_registro = registro.split(sep=b'|')
        identificador = int.from_bytes(lista_campos_registro[0])
        registros.append((identificador, tamanho_bytes + registro))
        i += 1

    arq.close()
        
    return registros


def escreva_registros_ordenados(nome_arq_saida: str, registros: list[tuple[int, bytes]]) -> None:
    
    arq = open(nome_arq_saida, 'wb')
    numero_registros = (len(registros).to_bytes(4))
    arq.write(numero_registros)

    for registro in registros:
        arq.write(registro[1])
        
    arq.close()


def ordene_arquivo_por_identificador(nome_arq_entrada: str, nome_arq_saida: str) -> None:

    registros: list[tuple[int, bytes]] = leia_registros(nome_arq_entrada)
    registros.sort(key=lambda registros: registros[0])
    escreva_registros_ordenados(nome_arq_saida, registros)

     
def main() -> None:
    if len(argv) < 3:
        raise TypeError('Número incorreto de argumentos\nModo de uso: nome_arq_entrada nome_arq_saida')

    ordene_arquivo_por_identificador(argv[1], argv[2])


if __name__ == '__main__':
    main()
    