class Restaurante:

    restaurantes = []


    def __init__(self, nome, categoria): #construtor
        self.nome = nome
        self.categoria = categoria
        self.ativo = False
        Restaurante.restaurantes.append(self)
    

    def __str__(self):
        return f'Nome: {self.nome} - Categoria: {self.categoria} - Ativo: {self.ativo}'


    def listar_restaurantes(): 
        for restaurante in Restaurante.restaurantes:    
            print(f'Nome: {restaurante.nome} - Categoria: {restaurante.categoria} - Ativo: {restaurante.ativo}')

restaurante_praca = Restaurante('Restaurante da Praça', 'Comida Caseira')

restaurante_pizza = Restaurante('Pizzaria do Zé', 'Pizza')

#print(restaurantes)

#print(dir(restaurante_praca))
#print(vars(restaurante_praca))
#print(vars(restaurante_pizza))

Restaurante.listar_restaurantes()
