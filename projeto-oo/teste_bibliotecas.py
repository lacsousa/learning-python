import numpy as np
import pandas as pd

array = np.array([1, 2, 3, 4, 5])

#print("Array:", array)


df = pd.read_csv("dados/tabela_produtos_missing.csv")
# print(df)

# Filtrar vendas do Produto que começam com a letra 'A'
vendas_produto_a = df[df["nome_produto"].str.lower().str.startswith("a", na=False)]
print("\nVendas do Produto que começam com 'A':")
print(vendas_produto_a)

nulos = df.isnull().sum()
print("\nContagem de valores nulos por coluna:")
print(nulos)    
