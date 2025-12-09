from modelos.avaliacao import Avaliacao

class Restaurante:
    """Representa um restaurante e suas características."""

    restaurantes = []

    def __init__(self, nome, categoria): #construtor
        """
        Inicializa uma instância de Restaurante.

        Parâmetros:
        - nome (str): O nome do restaurante.
        - categoria (str): A categoria do restaurante.
        """
        self._nome = nome.title()    # modificando o atributo _nome para proteger o atributo    
        self._categoria = categoria.upper()
        self._ativo = False
        self._avaliacoes = []
        Restaurante.restaurantes.append(self)
    
    def __str__(self):
        return f'Nome: {self._nome} - Categoria: {self._categoria} - Ativo: {self._ativo}'

    @classmethod
    def listar_restaurantes(cls):
        """Exibe uma lista formatada de todos os restaurantes."""

        print(f'{"Nome do restaurante".ljust(25)} | {"Categoria".ljust(25)} |  {"Avaliação".ljust(25)}  | {"Status"}' + '\n')
        for restaurante in cls.restaurantes:
            print(f'{restaurante._nome.ljust(25)} | {restaurante._categoria.ljust(25)} | {str(restaurante.calcular_media_avaliacoes).ljust(25)}| {restaurante.ativo}')
        print('\n')    


    @property
    def ativo(self):
        """Retorna um símbolo indicando o estado de atividade do restaurante."""
        return '✅' if self._ativo else '❌'
    
    
    def alternar_estado(self):   # método para os objetos
        self._ativo = not self._ativo


    def receber_avaliacao(self, cliente, nota ):
        if 0 < nota <= 5:
            avaliacao = Avaliacao(cliente, nota)
            self._avaliacoes.append(avaliacao)

    @property
    def calcular_media_avaliacoes(self):
        if not self._avaliacoes:
            return '-'
        
        total = sum(avaliacao._nota for avaliacao in self._avaliacoes)
        media = round(total / len(self._avaliacoes),1)
        return media
    

