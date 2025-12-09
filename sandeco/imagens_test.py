from PIL import Image 
import os 

print(os.getcwd())

imagem = Image.open("../imagens/passaros.jpg") 

imagem.show()