"""
Agente Explicador de Regras do Futebol com RAG (LangChain)
===========================================================
Curso: LangChain — Criando Chatbots Inteligentes com RAG (Foundation)

Objetivo:
    Construir um agente conversacional simples utilizando Retrieval-Augmented
    Generation (RAG) para responder perguntas sobre regras do futebol,
    com base em documentos oficiais.

Dependências (instale antes de rodar):
    pip install langchain==0.1.20 langchain-community==0.0.38 langchain-openai==0.1.7
    pip install pypdf chromadb python-dotenv
"""

import os
from pathlib import Path

# ── Carrega variáveis do arquivo .env ─────────────────────────────────────────
from dotenv import load_dotenv

# Sobe um nível a partir da pasta do script para encontrar o .env
BASE_DIR = Path(__file__).resolve().parent.parent  # Arquitetura_RAG_com_LLMs/
load_dotenv(dotenv_path=BASE_DIR / ".env")

# ── Importações LangChain ──────────────────────────────────────────────────────

# Loader de documentos PDF
from langchain_community.document_loaders import PyPDFLoader

# Divisão de texto em blocos
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings
from langchain_openai import OpenAIEmbeddings

# Banco vetorial
from langchain_community.vectorstores import Chroma

# LLM
from langchain_openai import ChatOpenAI

# Cadeia RAG
from langchain.chains import RetrievalQA


# ══════════════════════════════════════════════════════════════════════════════
# 1️⃣  DEFINIÇÃO DO PROBLEMA
# ══════════════════════════════════════════════════════════════════════════════
# LLMs possuem conhecimento estático e podem alucinar.
# O objetivo é garantir respostas confiáveis, conectando o modelo
# a documentos oficiais sobre regras do futebol.


# ══════════════════════════════════════════════════════════════════════════════
# 2️⃣  CARREGAMENTO DO PDF
# ══════════════════════════════════════════════════════════════════════════════

# O PDF deve estar na mesma pasta que este script
SCRIPT_DIR = Path(__file__).resolve().parent
CAMINHO_PDF = SCRIPT_DIR / "regras_futebol.pdf"

if not CAMINHO_PDF.is_file():
    raise FileNotFoundError(
        f"Arquivo '{CAMINHO_PDF}' não encontrado. "
        "Coloque o PDF na mesma pasta deste script e tente novamente."
    )

try:
    loader = PyPDFLoader(str(CAMINHO_PDF))
    documents = loader.load()
except Exception as e:
    raise RuntimeError(f"Erro ao carregar o PDF: {e}")

print(f"✅ PDF carregado — {len(documents)} páginas")


# ══════════════════════════════════════════════════════════════════════════════
# 3️⃣  DIVISÃO EM CHUNKS
# ══════════════════════════════════════════════════════════════════════════════

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(documents)
print(f"✅ Texto dividido em {len(chunks)} chunks")


# ══════════════════════════════════════════════════════════════════════════════
# 4️⃣  EMBEDDINGS E BANCO VETORIAL (ChromaDB)
# ══════════════════════════════════════════════════════════════════════════════

# Verifica a chave OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise EnvironmentError(
        "OPENAI_API_KEY não definida. "
        f"Verifique o arquivo .env em: {BASE_DIR / '.env'}"
    )

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=openai_key,
)

# Diretório onde o ChromaDB persiste os dados
CHROMA_DIR = str(SCRIPT_DIR / "chroma_regras_futebol")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=CHROMA_DIR,
)
vectorstore.persist()
print(f"✅ Banco vetorial criado e salvo em: {CHROMA_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# 5️⃣  RETRIEVER
# ══════════════════════════════════════════════════════════════════════════════

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},  # retorna os 4 chunks mais relevantes
)


# ══════════════════════════════════════════════════════════════════════════════
# 6️⃣  LLM + CADEIA RAG
# ══════════════════════════════════════════════════════════════════════════════

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=openai_key,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# 7️⃣  TESTES E VALIDAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

perguntas_teste = [
    "Quantos jogadores cada time pode ter em campo?",
    "O que é impedimento no futebol?",
    "Quais são as dimensões oficiais do campo de futebol?",
    "Quando um gol é anulado?",
]


def perguntar(pergunta: str) -> None:
    """Faz uma pergunta ao agente RAG e exibe a resposta com as fontes."""
    print(f"\n{'='*60}")
    print(f"🔎 Pergunta: {pergunta}")
    resultado = qa_chain({"query": pergunta})
    print(f"\n💬 Resposta:\n{resultado['result']}")
    print("\n📄 Fontes utilizadas:")
    for doc in resultado["source_documents"]:
        pagina = doc.metadata.get("page", "?")
        print(f"   • Página {pagina + 1}")


if __name__ == "__main__":
    print("\n🏟️  Agente RAG — Regras do Futebol")
    print("=" * 60)

    # Roda as perguntas de teste
    for pergunta in perguntas_teste:
        perguntar(pergunta)

    # Loop interativo (opcional)
    print(f"\n{'='*60}")
    print("💡 Modo interativo — digite sua pergunta ou 'sair' para encerrar.")
    while True:
        entrada = input("\n❓ Sua pergunta: ").strip()
        if entrada.lower() in ("sair", "exit", "quit", ""):
            print("👋 Encerrando o agente.")
            break
        perguntar(entrada)
