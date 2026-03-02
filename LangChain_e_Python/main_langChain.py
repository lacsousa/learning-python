from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain.globals import set_debug
import os

# LangChain é uma biblioteca de código aberto que facilita a construção de aplicações de linguagem natural. 
# Ele fornece uma interface simples para interagir com modelos de linguagem, como o GPT-3.5-turbo, 
# e permite criar fluxos de trabalho personalizados para atender às necessidades específicas do seu projeto.
# Não tem custo para ser usado, mas o uso da API do OpenAI pode ter custos associados, dependendo do modelo e da quantidade de tokens processados.

set_debug(True) # Ativa o modo de depuração para exibir informações detalhadas sobre a execução do código

load_dotenv()
minha_api_key = os.getenv("OPENAI_API_KEY")


class CitySuggestion(BaseModel):
    cidade: str = Field(..., description="A cidade recomendada para visitar")
    motivo: str = Field(..., description="O motivo pelo qual a cidade é recomendada")


class RestaurantsSuggestion(BaseModel):
    cidade: str = Field(..., description="A cidade recomendada para visitar")
    restaurantes: str = Field(..., description="O restaurante recomendado para visitar")
   

    
parseador_city_json = JsonOutputParser(pydantic_object=CitySuggestion)
parseador_restaurants_json = JsonOutputParser(pydantic_object=RestaurantsSuggestion)


promptModelCity = PromptTemplate(
    template="""
        Sugira uma cidade dado o meu interesse por {interesse}.
        {output_parser}
    """, 
    input_variables=["interesse"],
    partial_variables={"output_parser": parseador_city_json.get_format_instructions()}
)


promptModelRestaurants = PromptTemplate(
    template="""
        Sugira restaurantes em locais da cidade {cidade}.
        {output_parser}
    """, 
    partial_variables={"output_parser": parseador_restaurants_json.get_format_instructions()}
)

promptCultural = PromptTemplate(
    template="""
        Sugira atividades e locais culturais em {cidade}.
    """
)


model = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.5, # próximo de 0 para respostas mais precisas e próximo de 1 para respostas mais criativas
    api_key=minha_api_key
)

chain1 = promptModelCity | model | parseador_city_json
chain2 = promptModelRestaurants | model | parseador_restaurants_json
chain3 = promptCultural | model | StrOutputParser()

chain = (chain1 | chain2 | chain3)

response = chain.invoke(
    {
        "interesse": "praias"
    }
)

print(response) 