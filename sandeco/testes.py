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


    quadrados = [x**2 for x in range(10)]
    print("Quadrados: ", quadrados, "\n" )


    # Quadradados dos pares
    quadrados_pares = [x**2 for x in range(20) if x % 2 == 0]
    print("Quadrados dos pares: ", quadrados_pares, "\n" )

    temperaturas_celsius = [0, 20, 30,  37.5 , 100]
    temperaturas_fahrenheit = [(c * 9/5) + 32 for c in temperaturas_celsius ]
    
    print("Temperaturas Fahrenheit: ", temperaturas_fahrenheit, "\n")


    # Extração de letras
    frase = "Python é muito legal. 4, 5, 9"
    vogais = [letra for letra in frase if letra.lower() in 'aeiou']
    print("Vogais na frase: ", vogais, "\n")

    letras = [ letra for letra in frase if letra . isalpha ()]
    print ("Letras na frase: ", letras, "\n" )

    palavras = ["Python", "é", "poderoso"]
    comprimentos = [len(palavra) for palavra in palavras]
    print("Comprimentos das palavras: ", comprimentos, "\n" )

    nomes = ["Alice", "Bob", "Charlie"]
    tuplas = [(nome , len(nome)) for nome in nomes ]
    print("Nomes e seus comprimentos: ", tuplas, "\n")

    frase2 = "Python é divertido e incrível"
    palavras_longas = [palavra for palavra in frase2.split() if len(palavra) > 5]
    print("Palavras com mais de 5 letras: ", palavras_longas, "\n")

print ("\n", "Fatorial de 5: ", fatorial(5))
