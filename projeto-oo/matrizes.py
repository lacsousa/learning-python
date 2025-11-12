notas = [[7,8,9], 
         [6,5,4], 
         [10,9,8]]

matriz = [[7 , 8, 9],
        [60, 5, 7],
        [90, 1000, 100]]

for linha in notas:
    media = sum(linha)/len(linha)

print(linha)
print("Média:", media)


maior = matriz[0][0]
for li in matriz:
    for elemento in li:
        if elemento > maior:
            maior = elemento

print("Maior elemento da matriz:", maior)


new_var = range(len(matriz))
new_var1 = range(len(matriz[0]))
transposta = [
    [matriz[j][i] 
        for j in new_var] for i in new_var1 ] 

print("Matriz: ", matriz)

print("Matriz transposta:", transposta)



matriz1 = [[1 , 2], [3, 4]]
matriz2 = [[5 , 6], [7, 8]]
concatenada = matriz1 + matriz2
print (concatenada)


matriz3 = [[1 , 2, 3], [4, 5, 6], [7, 8, 9]]
if len(matriz3) == len( matriz3[0]):
    print ("A matriz é quadrada .")
else:
    print ("A matriz não é quadrada .")