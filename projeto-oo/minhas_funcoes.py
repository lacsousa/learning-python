
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


def fatorial(self, n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * self.fatorial(n - 1)


def calcula_media(notas):
    return sum(notas) / len(notas)

def calc_media2_notas(nota1, nota2):
    return (nota1 + nota2) / 2
