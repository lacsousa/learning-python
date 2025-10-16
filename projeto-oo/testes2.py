class Testes:

    notas = [7.5, 8.2, 9, 6, 5, 7, 9.1, 10, 10, 8.5, 1.7, 2.3, 3.4, 4.5, 5.6]

    def fatorial(self, n):
        if n == 0 or n == 1:
            return 1
        else:
            return n * self.fatorial(n - 1)

    
    def imprimir_notas(self, notas):
        for nota in notas:
            print(nota)


t = Testes()
print(t.fatorial(5))

t.imprimir_notas(t.notas)
t.notas.append(6)
t.imprimir_notas(t.notas)

media = sum(t.notas) / len(t.notas)
print("Média das notas:", media)    

notas_acima_media = [n for n in t.notas if n > media]
print("Notas acima da média:", notas_acima_media)   

notas_ordenadas = sorted(t.notas)
print("Notas ordenadas: " + str(notas_ordenadas))

print("Notas na ordem inversa: " + str(notas_ordenadas[::-1]))

