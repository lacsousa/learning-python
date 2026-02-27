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


promptModelCity = PromptTemplate(
    template="""
        Sugira uma cidade dado o meu interesse por {interesse}.
    """, 
    input_variables=["interesse"]
)


model = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.5, # próximo de 0 para respostas mais precisas e próximo de 1 para respostas mais criativas
    api_key=minha_api_key
)

chain = promptModelCity | model | StrOutputParser()

response = chain.invoke(
    {
        "interesse": "praias"
    }
)

print(response) 