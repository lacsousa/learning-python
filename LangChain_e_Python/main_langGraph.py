from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from typing import Literal, TypedDict

import os

load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")

my_model = ChatOpenAI(
    model = "gpt-4o-mini",
    temperature = 0.5,
    api_key = my_api_key
)

beach_assistant_chain_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um consultor de viagens para destinos de praia no Brasil. Apresente-se como Sr. Praias e forneça recomendações "
        "personalizadas com base nas preferências do usuário."),
        ("human", "{query}")
    ]
)


mountain_assistant_chain_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um consultor de viagens para destinos de montanha no Brasil. Apresente-se como Sr. Montanhas e forneça recomendações "
        "personalizadas com base nas preferências do usuário."),
        ("human", "{query}")
    ]
)


beach_assistant_chain = beach_assistant_chain_prompt | my_model | StrOutputParser()
mountain_assistant_chain = mountain_assistant_chain_prompt | my_model | StrOutputParser()

router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Responda apenas com 'praia' ou 'montanha'."),
        ("human", "{query}")
    ]
)

class Route(TypedDict):
    route: Literal["praia", "montanha"]

router = router_prompt | my_model.with_structured_output(Route)


def response(pergunta :str):
    route = router.invoke({"query": pergunta})["route"].strip().lower()

    print(f"Rota selecionada: {route}")

    if route == "praia":
        return beach_assistant_chain.invoke({"query": pergunta})
    return mountain_assistant_chain.invoke({"query": pergunta})
    

print(response("Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?"))
