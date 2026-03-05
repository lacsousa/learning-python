from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from pathlib import Path

load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")

my_model = ChatOpenAI(
    model = "gpt-4o-mini",
    temperature = 0.5,
    api_key = my_api_key
)


# Convert text to embeddings
embeddings = OpenAIEmbeddings()
base_dir = Path(__file__).resolve().parent
files = [
    str(base_dir / "documentos" / "GTB_gold_Nov23.pdf"),
    str(base_dir / "documentos" / "GTB_platinum_Nov23.pdf"),
    str(base_dir / "documentos" / "GTB_standard_Nov23.pdf"),
]

docs = sum(
    [
        PyPDFLoader(file).load() for file in files
    ], [])

pieces =RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
).split_documents(docs)

recovered_data = FAISS.from_documents(
    pieces, embeddings
).as_retriever(search_kwargs={"k": 2}) # 2 more relevant pieces


insurance_chain_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Responda usando exclusivamente o conteúdo fornecido"),
        ("human", "{query}\n\n Contexto: \n{context} \n\n Resposta: ")
    ]
)

chain = insurance_chain_prompt | my_model | StrOutputParser()

def reply(question : str):
    excerpts = recovered_data.invoke(question)
    context = "\n\n".join([excerpt.page_content for excerpt in excerpts])
    state = {"query": question, "context": context}
    return chain.invoke(state)


print(reply("Como devo proceder caso eu tenha um item comprado roubado e caso eu tenha um cartão Gold?"))


