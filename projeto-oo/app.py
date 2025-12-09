from modelos.restaurante import Restaurante


restaurante_praca = Restaurante('restaurante da Praça', 'Comida Caseira')
restaurante_pizza = Restaurante('pizzaria do Zé', 'Pizza')
restaurante_mexicano = Restaurante('El Mexicano', 'Comida Mexicana')
restaurante_japones = Restaurante('Sushi Top', 'Comida Japonesa')

restaurante_japones.alternar_estado()

restaurante_praca.receber_avaliacao('Ana', 5)
restaurante_praca.receber_avaliacao('Bruno', 2)
restaurante_praca.receber_avaliacao('Luciano', 4)    



def main():
    Restaurante.listar_restaurantes()


if __name__ == "__main__":
    print("Bem-vindo ao Sistema de Gerenciamento de Restaurantes!")
    main()
