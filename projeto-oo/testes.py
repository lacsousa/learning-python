class Testes:
    matriz1 = [
            [7 , 8, 9],
            [6, 5, 10],
            [9, 3, 1]
    ]


    def maior_valor():
        matriz = [   [7 , 8, 9],
            [6, 5, 7],
            [9, 10, 10]
        ]

        maior = matriz [0][0]
        for linha in matriz:
            for elemento in linha :
                if elemento > maior :
                    maior = elemento

        return maior



    def filtrar_pares(lista):
        return [numero for numero in lista if numero % 2 == 0]
    
    def adicionar_asteriscos(texto):
        return f"\n***** {texto} ***** \n"
    
    def fatorial(self, n):
        if n == 0 or n == 1:
            return 1
        else:
            return n * self.fatorial(n - 1)
        

    print ("\n Maior elemento :", maior_valor(), "\n" )

    print (filtrar_pares([1,2,3,4,5,6,7,8,9,10]))

    print (adicionar_asteriscos("Python é massa "))

    print(matriz1) 

t = Testes()
print (t.fatorial(5))
