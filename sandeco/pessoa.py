class Pessoa:

    def __init__(self, nome, profissao, idade):
        self.nome = nome
        self.profissao = profissao
        self.__idade = idade # Atributo privado (encapsulado)
        # Getter: Método para acessar o atributo privado 'idade'

    def get_idade(self):
        return self.__idade


# Setter: Método para modificar o atributo privado 'idade'
    def set_idade(self, nova_idade):
        if nova_idade >= 0:
            self.__idade = nova_idade
            print(f"A idade de {self.nome} foi atualizada para {self.__idade} anos. \n")
        else:
            print("Idade inválida! A idade não pode ser negativa.\n")

# Método para exibir informações da Pessoa
    def exibir_informacoes(self):
        print(f"Pessoa: {self.nome}, {self.profissao} ({self.get_idade()} anos) \n")

# Criando uma instância da classe Pessoa
cliente = Pessoa("Luciano", "Aluno", 87)

# Acessando o atributo privado através do getter
print(f"Idade de {cliente.nome}: {cliente.get_idade()} anos \n" )

# Modificando o atributo privado através do setter
cliente.set_idade(52)

# Tentando modificar com um valor inválido
cliente.set_idade(-5)

# Exibindo as informações atualizadas
cliente.exibir_informacoes()