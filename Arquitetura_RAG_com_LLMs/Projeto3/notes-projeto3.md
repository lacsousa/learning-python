# Teoria de RAG — Projeto 3: Agente de RH com Reranking

## O que é RAG (Retrieval-Augmented Generation)

RAG é uma arquitetura que combina **recuperação de informação** com **geração de texto** por um LLM. Em vez de depender apenas do conhecimento interno do modelo, o RAG busca trechos relevantes de uma base de documentos e os injeta no prompt antes de gerar a resposta. Isso reduz alucinações e permite que o modelo responda com base em fontes privadas e atualizadas.

Pipeline básico:
```
Pergunta → Recuperação de chunks → Injeção no prompt → Geração da resposta
```

---

## Pipeline implementado neste projeto

### Etapa 1 — Carregamento de documentos (`PyPDFLoader`)

Os documentos são PDFs de políticas internas de RH:
- `politica_ferias.pdf`
- `politica_home_office.pdf`
- `codigo_conduta.pdf`

O `PyPDFLoader` do LangChain lê cada página como um `Document` com `page_content` e `metadata`. Um metadado `documento` é adicionado com o nome do arquivo de origem, permitindo rastrear a fonte de cada trecho na resposta final.

### Etapa 2 — Chunking (`RecursiveCharacterTextSplitter`)

Documentos longos são divididos em pedaços menores chamados **chunks**:

```python
RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
```

**Por que chunkar?**
- Modelos de embedding têm limite de tokens por entrada.
- Chunks menores aumentam a precisão da busca vetorial — textos muito longos diluem o sinal semântico.

**`chunk_overlap`** garante que informações na fronteira entre dois chunks não sejam perdidas.

**`RecursiveCharacterTextSplitter`** tenta dividir por parágrafos (`\n\n`), depois por linhas (`\n`), depois por frases, e por último caractere a caractere — preservando a coerência semântica tanto quanto possível.

### Etapa 3 — Enriquecimento de metadados

Após o chunking, cada chunk recebe um metadado `categoria` classificado por palavras-chave no texto:

| Palavra-chave encontrada | Categoria atribuída |
|--------------------------|---------------------|
| "férias"                 | `ferias`            |
| "home office" / "remoto" | `home_office`       |
| "conduta" / "ética"      | `conduta`           |
| (nenhuma acima)          | `geral`             |

**Por que enriquecer metadados?**
Metadados permitem filtragem e exibição contextualizada na interface. No Streamlit, o usuário vê de qual documento e categoria cada trecho foi extraído — aumentando a transparência e a confiança na resposta.

### Etapa 4 — Vector Store com Chroma

Os chunks são convertidos em vetores numéricos (**embeddings**) e armazenados no **Chroma**, um banco de dados vetorial local com persistência em disco.

```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_rh"
)
```

**O que é um embedding?**
Um embedding é uma representação numérica de texto em um espaço vetorial de alta dimensão. Textos semanticamente similares ficam próximos nesse espaço. A busca por similaridade coseno (ou produto interno) encontra os chunks mais relacionados à pergunta do usuário.

**`text-embedding-3-small`** é o modelo da OpenAI usado para gerar esses vetores.

### Etapa 5 — Recuperação inicial (similarity search)

```python
documentos_recuperados = vectorstore.similarity_search(pergunta, k=8)
```

Recupera os **8 chunks mais similares** à pergunta. O `k` é intencionalmente alto para garantir que nenhum trecho relevante seja descartado antes do reranking.

### Etapa 6 — Reranking semântico com LLM ⭐

Esta é a etapa diferencial do Projeto 3. Após a recuperação por similaridade vetorial (que é rápida mas imprecisa), o **LLM avalia a relevância real de cada chunk** para a pergunta específica:

```python
prompt_rerank = PromptTemplate(
    template="""
Avalie a relevância desse trecho para responder a pergunta.
Responda apenas com um número de 0 a 10.
"""
)
```

O LLM atribui um score de 0 a 10 para cada um dos 8 chunks recuperados. Os chunks são então reordenados por score e apenas os **4 melhores** são passados para a geração da resposta.

**Por que reranking?**

A busca vetorial mede **similaridade de forma**, não **relevância de conteúdo**. Dois textos podem usar as mesmas palavras com sentidos diferentes. O LLM entende o contexto semântico profundo e consegue avaliar se um trecho realmente responde à pergunta — por isso combinar os dois métodos é mais preciso do que usar apenas um.

**Custo do reranking:** cada chunk exige uma chamada ao LLM, então com `k=8` são 8 chamadas extras antes da geração da resposta. É um trade-off entre precisão e latência/custo.

### Etapa 7 — Geração da resposta (RAG propriamente dito)

Os 4 chunks melhor rankeados são concatenados e injetados no prompt final:

```python
prompt_final = f"""
Você é um agente de RH corporativo.
Responda APENAS com base nas políticas internas abaixo.

Contexto:
{contexto_texto}

Pergunta:
{pergunta}
"""
```

A instrução `Responda APENAS com base nas políticas internas` é um **grounding constraint** — força o modelo a não inventar respostas além do que está no contexto recuperado.

---

## Arquitetura RAG com Reranking — visão geral

```
PDFs
  │
  ▼
PyPDFLoader → pages (Documents com metadata)
  │
  ▼
RecursiveCharacterTextSplitter → chunks (800 tokens, overlap 150)
  │
  ▼
Enriquecimento de metadados (categoria)
  │
  ▼
OpenAIEmbeddings → vetores
  │
  ▼
Chroma (Vector Store persistido em disco)
  │
  ▼
similarity_search(k=8) ← pergunta do usuário
  │
  ▼
Reranking LLM (score 0–10 por chunk)
  │
  ▼
Top 4 chunks
  │
  ▼
Prompt final → ChatOpenAI (gpt-4o-mini) → resposta
```

---

## Conceitos-chave

| Conceito | Descrição |
|----------|-----------|
| **Embedding** | Representação vetorial numérica de texto; textos similares ficam próximos no espaço |
| **Chunk** | Fragmento do documento original; unidade de recuperação do RAG |
| **Chunk overlap** | Sobreposição entre chunks consecutivos para não perder contexto nas bordas |
| **Vector Store** | Banco de dados otimizado para busca por similaridade vetorial |
| **Similarity search** | Busca pelos vetores mais próximos ao vetor da pergunta (similaridade coseno) |
| **Reranking** | Segunda etapa de filtragem onde um LLM reordena os chunks por relevância semântica real |
| **Grounding** | Instrução no prompt que restringe o modelo a responder apenas com base no contexto fornecido |
| **`@st.cache_data`** | Cache do Streamlit para dados serializáveis (ex: lista de documentos carregados) |
| **`@st.cache_resource`** | Cache do Streamlit para recursos não serializáveis (ex: conexão com o Vector Store) |

---

## Trade-offs de design

**`k=8` na recuperação → top 4 após reranking**
Recuperar mais do que o necessário (`k` alto) e depois filtrar com reranking é o padrão recomendado. Se recuperar direto com `k=4`, corre o risco de descartar chunks relevantes cedo demais.

**Reranking com o mesmo LLM da geração**
Simples de implementar, mas aumenta o custo e a latência. Alternativas para produção: modelos de reranking dedicados como `cross-encoder/ms-marco` (local) ou Cohere Rerank (API).

**Chroma local com persistência**
Adequado para protótipos. Em produção considerar Pinecone, Weaviate ou pgvector para suportar múltiplos usuários e escala.
