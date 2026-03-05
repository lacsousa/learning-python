from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig


import asyncio
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

class State(TypedDict):
    query: str
    route: Route
    response: str

router = router_prompt | my_model.with_structured_output(Route)


async def router_node(state: State, config: RunnableConfig):
    return { "route" : await router.ainvoke({"query" : state["query"]}, config)}


async def beach_node(state: State, config: RunnableConfig):
    return { "response" : await beach_assistant_chain.ainvoke({"query" : state["query"]}, config)}

async def mountain_node(state: State, config: RunnableConfig):
    return { "response" : await mountain_assistant_chain.ainvoke({"query" : state["query"]}, config)}


def choose_node(state: State) -> Literal["praia", "montanha"]:
    return "praia" if state["route"]["route"] == "praia" else "montanha"

graph = StateGraph(State)
graph.add_node("rotear", router_node)
graph.add_node("praia", beach_node)
graph.add_node("montanha", mountain_node)

graph.add_edge(START, "rotear")
graph.add_conditional_edges("rotear", choose_node)
graph.add_edge("praia", END)
graph.add_edge("montanha", END)

app = graph.compile()

async def main():
    #query = "Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?"
    query = "Quero escalar montanhas no Brasil. Pode sugerir?"
    state = {"query": query}
    result = await app.ainvoke(state)
    return result["response"]

print(asyncio.run(main()))
