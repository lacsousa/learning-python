class Restaurante:

    restaurantes = []

    def __init__(self, nome, categoria): #construtor
        self._nome = nome.title()    # modificando o atributo _nome para proteger o atributo    
        self._categoria = categoria.upper()
        self._ativo = False
        Restaurante.restaurantes.append(self)
    
    def __str__(self):
        return f'Nome: {self._nome} - Categoria: {self._categoria} - Ativo: {self._ativo}'

    @classmethod
    def listar_restaurantes(cls):
        print(f'{"Nome do restaurante".ljust(25)} | {"Categoria".ljust(25)} | {"Status"}' + '\n')
        for restaurante in cls.restaurantes:
            print(f'{restaurante._nome.ljust(25)} | {restaurante._categoria.ljust(25)} | {restaurante.ativo}')
        print('\n')    

    @property
    def ativo(self):
        return '✅' if self._ativo else '❌'
    
    def alternar_estado(self):   # método para os objetos
        self._ativo = not self._ativo


restaurante_praca = Restaurante('restaurante da Praça', 'Comida Caseira')
restaurante_praca.alternar_estado()
restaurante_pizza = Restaurante('pizzaria do Zé', 'Pizza')


Restaurante.listar_restaurantes()

