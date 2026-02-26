from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# LangChain é uma biblioteca de código aberto que facilita a construção de aplicações de linguagem natural. 
# Ele fornece uma interface simples para interagir com modelos de linguagem, como o GPT-3.5-turbo, 
# e permite criar fluxos de trabalho personalizados para atender às necessidades específicas do seu projeto.
# Não tem custo para ser usado, mas o uso da API do OpenAI pode ter custos associados, dependendo do modelo e da quantidade de tokens processados.


load_dotenv()
minha_api_key = os.getenv("OPENAI_API_KEY")

numero_dias = 2
numero_pessoas = 4
cidade_destino = "New York"

promptModel = PromptTemplate.from_template(
    """Crie um roteiro de viagem de {dias} dias, para uma família de {num_pessoas} pessoas, 
    sem crianças, para a cidade de {destino},
    incluindo opções de restaurantes e hotéis adequados para famílias."""
)

prompt = promptModel.format(
    dias=numero_dias, 
    num_pessoas=numero_pessoas, 
    destino=cidade_destino
)

print("Prompt: \n", prompt)

model = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.5, # próximo de 0 para respostas mais precisas e próximo de 1 para respostas mais criativas
    api_key=minha_api_key
)

response = model.invoke(prompt)
print(response.content) 