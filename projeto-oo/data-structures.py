print("\n Dicionários ....")

livro = {
    "titulo": "Aprendendo Python",
    "autor": "João Silva",
    "ano": 2021,
    "preco": 59.90
}

print("Título do livro:", livro["titulo"])
print("Autor do livro:", livro["autor"])

print("\n", livro)

print("\n Adicionando mais chaves...")

livro["disponivel"] = True
livro["categorias"] = ["programação", "desenvolvimento", "python"]
livro["copias"] = 5
print("\n", livro)

print("\n Removendo a chave [cópias]...") 
del livro["copias"]
print("\n", livro)

print("\n Tuplas ....")

contatos = ('Joao', '1234 -5678', 'joao@email.com')

print('Nome:', contatos[0])
print('Telefone:', contatos[1])
print('Email:', contatos[2])

print ("\n", contatos)


print("\n Conjuntos ....")

frutas = {'maças', 'peras', 'uvas'}
print("\n", frutas)
frutas.add('bananas')
print("\n", frutas)
frutas.remove('peras')
print("\n", frutas)
print("Verificando se 'maças' está no conjunto:", 'maças' in frutas)    

frutas_tropicais = {'abacaxi', 'manga', 'laranjas'}
todas_frutas = frutas.union(frutas_tropicais)
print("\n Todas as frutas:", todas_frutas)
