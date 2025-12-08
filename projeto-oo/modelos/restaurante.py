class Restaurante:

    restaurantes = []


    def __init__(self, nome, categoria): #construtor
        self.nome = nome
        self.categoria = categoria
        self._ativo = False
        Restaurante.restaurantes.append(self)
    

    def __str__(self):
        return f'Nome: {self.nome} - Categoria: {self.categoria} - Ativo: {self.ativo}'


    def listar_restaurantes():
        print(f'{"Nome do restaurante".ljust(25)} | {"Categoria".ljust(25)} | {"Status"}' + '\n')
        for restaurante in Restaurante.restaurantes:
            print(f'{restaurante.nome.ljust(25)} | {restaurante.categoria.ljust(25)} | {restaurante.ativo}')

        print('\n')    

    @property
    def ativo(self):
        return '✅' if self._ativo else '❌'

restaurante_praca = Restaurante('Restaurante da Praça', 'Comida Caseira')

restaurante_pizza = Restaurante('Pizzaria do Zé', 'Pizza')

#print(restaurantes)

#print(dir(restaurante_praca))
#print(vars(restaurante_praca))
#print(vars(restaurante_pizza))

Restaurante.listar_restaurantes()




