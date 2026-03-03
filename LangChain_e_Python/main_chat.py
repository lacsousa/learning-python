import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory


load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")


my_model = ChatOpenAI(
    model = "gpt-3.5-turbo",
    temperature = 0.5,
    api_key = my_api_key
)

suggestion_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um guia de viagem especializado em destinos no Brasil. Apresente-se como Sr. Passeios"),
        ("placeholder", "{history}"),
        ("human", "{query}")
    ]
)

chain = suggestion_prompt | my_model | StrOutputParser()

memory = {}
session = "langchain_python_class"


def history_by_session(session_id: str):
    if session_id not in memory:
        memory[session_id] = InMemoryChatMessageHistory()
    return memory[session_id]


questions = [
    "Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?",
    "Qual a melhor época do ano para ir?"
]

chain_with_memory = RunnableWithMessageHistory(
    runnable = chain,
    get_session_history = history_by_session,
    input_messages_key = "query",
    history_messages_key = "history"
)


for one_question in questions:
    response = chain_with_memory.invoke(
        {
            "query": one_question
        },
        config={"session_id": session}
    )

    print(f"Usuário: {one_question}")
    print(f"IA: {response}", "\n")
    print("-" * 50, "\n")

