# ============================================
# PROJETO 4 — AGENTE DE RH COM RAG + RERANKING
# Versão melhorada com base em spec-rag.md
# LangChain + Streamlit
# ============================================
#
# Melhorias implementadas (ver spec-rag.md) — TODAS as fases:
#   [1] Reranking em UMA única chamada (batch + JSON)  -> reduz ~8x o custo dessa etapa
#   [2] Vector Store NÃO é reconstruído a cada execução -> embeddings rodam só uma vez
#   [3] Parsing robusto do score de reranking           -> sem `except:` nu
#   [4] Modelos configuráveis por etapa                 -> custo baixo, upgrade seletivo
#   [5] Prompt com fallback anti-alucinação             -> confiabilidade no contexto de RH
#   [6] Filtro por metadados na recuperação             -> opcional (USAR_FILTRO_CATEGORIA)
#   [7] Conjunto de avaliação mínimo                    -> ver eval_perguntas.py
# ============================================

# =========================
# 1. IMPORTAÇÕES
# =========================

import os
import json
import re

import streamlit as st

# Injeta a chave como variável de ambiente
from dotenv import load_dotenv

load_dotenv()

# Loaders e chunking
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings e LLM
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Vector Store
from langchain_community.vectorstores import Chroma


# =========================
# 2. CONFIGURAÇÕES GERAIS
# =========================

# Diretório onde este script (e os PDFs) está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório do banco vetorial (persistido ao lado do script)
PERSIST_DIRECTORY = os.path.join(SCRIPT_DIR, "chroma_rh")

# Modelo de embeddings
# [4] text-embedding-3-small é o padrão de baixo custo.
#     Trocar para "text-embedding-3-large" SÓ se a recuperação estiver falhando.
EMBEDDING_MODEL = "text-embedding-3-small"

# [4] Modelos configuráveis POR ETAPA (mantém custo baixo):
#   - Reranking: tarefa simples (pontuar), modelo barato basta.
#   - Resposta: subir para "gpt-4o" só se a qualidade exigir (medir com eval antes).
LLM_RERANK_MODEL = "gpt-4o-mini"
LLM_ANSWER_MODEL = "gpt-4o-mini"

# Parâmetros de recuperação
K_RECUPERACAO = 8   # recupera mais (k alto) e filtra no reranking
K_CONTEXTO = 4      # nº de chunks que vão para a geração da resposta

# [6] Filtro por metadados na recuperação.
#     DEFAULT = False (desligado) de propósito: com apenas 3 PDFs o ganho é
#     marginal e a categoria é classificada por substring (ruidosa) — um chunk
#     de home office que cite "férias" é marcado como "ferias", o que pode
#     EXCLUIR silenciosamente o trecho certo em perguntas cruzadas.
#     Ligar quando a base de documentos crescer e a categorização for confiável.
USAR_FILTRO_CATEGORIA = False


# =========================
# 3. LEITURA DOS DOCUMENTOS
# =========================

@st.cache_data
def carregar_documentos():
    """
    Carrega os PDFs de políticas internas de RH desta pasta.
    """
    caminhos = [
        os.path.join(SCRIPT_DIR, "politica_ferias.pdf"),
        os.path.join(SCRIPT_DIR, "politica_home_office.pdf"),
        os.path.join(SCRIPT_DIR, "codigo_conduta.pdf"),
    ]

    documentos = []

    for caminho in caminhos:
        loader = PyPDFLoader(caminho)
        docs = loader.load()

        for doc in docs:
            doc.metadata["documento"] = os.path.basename(caminho)

        documentos.extend(docs)

    return documentos


# =========================
# 4. CHUNKING
# =========================

def gerar_chunks(documentos):
    """
    Divide os documentos em chunks semânticos.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    return splitter.split_documents(documentos)


# =========================
# 5. ENRIQUECIMENTO COM METADADOS
# =========================

def enriquecer_chunks(chunks):
    """
    Classifica os chunks por categoria semântica (usado na exibição das fontes).
    """
    for chunk in chunks:
        texto = chunk.page_content.lower()

        if "férias" in texto:
            chunk.metadata["categoria"] = "ferias"
        elif "home office" in texto or "remoto" in texto:
            chunk.metadata["categoria"] = "home_office"
        elif "conduta" in texto or "ética" in texto:
            chunk.metadata["categoria"] = "conduta"
        else:
            chunk.metadata["categoria"] = "geral"

    return chunks


def detectar_categoria(pergunta):
    """
    [6] Classifica a PERGUNTA em uma categoria por palavras-chave (custo zero,
        sem chamada ao LLM). Retorna None quando nenhuma categoria é detectada,
        sinalizando que a busca deve ocorrer sem filtro.
    """
    texto = pergunta.lower()

    if "férias" in texto or "ferias" in texto:
        return "ferias"
    elif "home office" in texto or "remoto" in texto or "remota" in texto:
        return "home_office"
    elif "conduta" in texto or "ética" in texto or "etica" in texto:
        return "conduta"

    return None


# =========================
# 6. VECTOR STORE
# =========================

@st.cache_resource
def criar_vectorstore(_chunks):
    """
    [2] Cria o banco vetorial apenas se ele ainda não existir.
        Se já houver um índice persistido, apenas CARREGA (sem re-embeddar).
        -> Os embeddings dos PDFs são gerados uma única vez.

        O parâmetro _chunks não entra no hash do cache.
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    indice_existe = (
        os.path.exists(PERSIST_DIRECTORY)
        and len(os.listdir(PERSIST_DIRECTORY)) > 0
    )

    if indice_existe:
        # Apenas carrega o índice já persistido
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings,
        )
    else:
        # Primeira execução: gera os embeddings e persiste em ./Projeto4/chroma_rh
        # (no chromadb >= 0.4.x a persistência em disco é automática ao passar
        #  persist_directory — os arquivos chroma.sqlite3 + coleção são gravados ali).
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

        vectorstore = Chroma.from_documents(
            documents=_chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
        )

    return vectorstore


# =========================
# 7. RERANKING EM BATCH (PARTE CHAVE!)
# =========================

def _parse_scores(conteudo, n_esperado):
    """
    [3] Parsing robusto do JSON de scores retornado pelo LLM.
        Faz fallback seguro caso o modelo desvie do formato esperado.
    """
    try:
        dados = json.loads(conteudo)
        scores = dados["scores"]
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: tenta extrair números soltos do texto
        numeros = re.findall(r"\d+(?:\.\d+)?", conteudo or "")
        scores = [float(n) for n in numeros]

    # Normaliza tamanho: completa com 0 ou corta para casar com os trechos
    scores = [float(s) for s in scores][:n_esperado]
    scores += [0.0] * (n_esperado - len(scores))

    return scores


def rerank_documentos(pergunta, documentos, llm_rerank):
    """
    [1] Reordena TODOS os documentos recuperados em UMA única chamada ao LLM,
        usando saída estruturada (JSON). Antes eram N chamadas (uma por chunk).
    """
    if not documentos:
        return []

    # Monta a lista numerada de trechos
    trechos_numerados = "\n\n".join(
        f"[{i}] {doc.page_content}"
        for i, doc in enumerate(documentos)
    )

    prompt_rerank = f"""Você é um especialista em políticas internas de RH.

Pergunta do usuário:
{pergunta}

Avalie a relevância de CADA trecho abaixo para responder à pergunta,
atribuindo uma nota de 0 a 10 (0 = irrelevante, 10 = totalmente relevante).

Retorne APENAS um JSON no formato:
{{"scores": [nota_do_trecho_0, nota_do_trecho_1, ...]}}
na MESMA ordem dos trechos. Não inclua nenhum texto fora do JSON.

Trechos:
{trechos_numerados}
"""

    resposta = llm_rerank.invoke(prompt_rerank)
    scores = _parse_scores(resposta.content, len(documentos))

    # Ordena do mais relevante para o menos relevante
    documentos_ordenados = sorted(
        zip(scores, documentos),
        key=lambda x: x[0],
        reverse=True,
    )

    return [doc for _, doc in documentos_ordenados]


# =========================
# 8. PIPELINE RAG COMPLETO
# =========================

def responder_pergunta(pergunta, vectorstore):
    """
    Pipeline completo: Recuperação -> Reranking (batch) -> Geração.
    """

    # [4] LLM de reranking em modo JSON (saída estruturada)
    llm_rerank = ChatOpenAI(
        model=LLM_RERANK_MODEL,
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    # [4] LLM de geração da resposta
    llm_resposta = ChatOpenAI(
        model=LLM_ANSWER_MODEL,
        temperature=0,
    )

    # [6] Filtro por metadados (opcional — ver USAR_FILTRO_CATEGORIA)
    filtro = None
    if USAR_FILTRO_CATEGORIA:
        categoria = detectar_categoria(pergunta)
        if categoria:
            filtro = {"categoria": categoria}

    # Recuperação inicial (top-k mais alto)
    documentos_recuperados = vectorstore.similarity_search(
        pergunta,
        k=K_RECUPERACAO,
        filter=filtro,
    )

    # Fallback de segurança: se o filtro não retornou nada, busca sem filtro
    if filtro and not documentos_recuperados:
        documentos_recuperados = vectorstore.similarity_search(
            pergunta,
            k=K_RECUPERACAO,
        )

    # [1] Reranking em batch
    documentos_rerankeados = rerank_documentos(
        pergunta,
        documentos_recuperados,
        llm_rerank,
    )

    # Seleciona os melhores
    contexto_final = documentos_rerankeados[:K_CONTEXTO]

    contexto_texto = "\n\n".join(
        doc.page_content for doc in contexto_final
    )

    # [5] Prompt com fallback anti-alucinação
    prompt_final = f"""Você é um agente de RH corporativo.
Responda APENAS com base nas políticas internas abaixo.

Se a resposta não estiver nas políticas, responda EXATAMENTE:
"Não encontrei essa informação nas políticas internas disponíveis."
Não invente informações que não estejam no contexto.

Contexto:
{contexto_texto}

Pergunta:
{pergunta}
"""

    resposta = llm_resposta.invoke(prompt_final)

    return resposta.content, contexto_final


# =========================
# 9. PIPELINE DE INDEXAÇÃO (reutilizável: UI e eval)
# =========================

def construir_vectorstore():
    """
    Executa a indexação completa (carregar -> chunk -> enriquecer -> vector store).
    Reutilizado tanto pela interface Streamlit quanto pelo eval_perguntas.py.
    """
    documentos = carregar_documentos()
    chunks = gerar_chunks(documentos)
    chunks = enriquecer_chunks(chunks)
    return criar_vectorstore(chunks)


# =========================
# 10. INTERFACE STREAMLIT
# =========================
# Guardada sob __main__ para que `import Projeto4` (usado pelo eval) NÃO renderize
# a página nem dispare indexação. Sob `streamlit run`, __name__ == "__main__".

if __name__ == "__main__":
    st.set_page_config(page_title="Agente de RH com RAG", layout="wide")
    st.title("🤖 Agente de RH — Políticas Internas (Projeto 4)")

    # [2] Botão para reindexar quando os PDFs mudarem
    with st.sidebar:
        st.header("Administração")
        st.caption("Reindexe se os PDFs de políticas forem alterados.")
        if st.button("🔄 Reconstruir índice"):
            import shutil

            if os.path.exists(PERSIST_DIRECTORY):
                shutil.rmtree(PERSIST_DIRECTORY)
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Índice removido. Faça uma pergunta para reconstruir.")

    pergunta = st.text_input("Digite sua pergunta sobre políticas internas de RH:")

    if pergunta:
        with st.spinner("Consultando políticas internas..."):
            vectorstore = construir_vectorstore()
            resposta, fontes = responder_pergunta(pergunta, vectorstore)

        st.subheader("Resposta")
        st.write(resposta)

        st.subheader("Fontes utilizadas")
        for i, doc in enumerate(fontes, start=1):
            st.markdown(f"**Trecho {i}**")
            st.write(f"Documento: {doc.metadata.get('documento')}")
            st.write(f"Categoria: {doc.metadata.get('categoria')}")
            st.write(doc.page_content)
            st.divider()


# Perguntas de exemplo:
## Quais são as regras para concessão de férias aos colaboradores?
## Quem pode trabalhar em regime de home office e quais são as condições?
## Quais comportamentos são considerados inadequados segundo o código de conduta da empresa?
