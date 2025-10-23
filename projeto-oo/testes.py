from minhas_funcoes import maior_valor, fatorial

class Testes:
    matriz1 = [
            [7 , 8, 9],
            [6, 5, 10],
            [9, 3, 1]
    ]

    def filtrar_pares(lista):
        return [numero for numero in lista if numero % 2 == 0]
    
    def adicionar_asteriscos(texto):
        return f"\n***** {texto} ***** \n"
    

    print ("\n Maior elemento :", maior_valor(), "\n" )

    print (filtrar_pares([1,2,3,4,5,6,7,8,9,10]))

    print (adicionar_asteriscos("Python é massa "))

    print(matriz1) 


print ("\n", "Fatorial de 5: ", fatorial(5))
