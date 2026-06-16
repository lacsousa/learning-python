# Spec — Melhorias do RAG (Projeto 3)

> Especificação de melhorias incrementais para o Agente de RH com RAG + Reranking.
> Base: [notes-projeto3.md](notes-projeto3.md) e [Projeto 3.py](Projeto%203.py)
>
> **Princípios desta spec:** simplicidade primeiro, custo baixo, melhorias incrementais.
> Cada item é independente e pode ser implementado isoladamente.

---

## Visão geral das prioridades

| # | Melhoria | Impacto | Esforço | Custo |
|---|----------|---------|---------|-------|
| 1 | Reranking em uma única chamada (batch) | 🔴 Alto | Baixo | **↓↓ reduz ~8x** |
| 2 | Não reconstruir o Vector Store a cada execução | 🔴 Alto | Baixo | ↓ |
| 3 | Parsing robusto do score de reranking | 🟠 Médio | Baixo | = |
| 4 | Upgrade seletivo de modelos (LLM + embedding) | 🟠 Médio | Baixo | ↑ controlado |
| 5 | Prompt com fallback "não sei" (anti-alucinação) | 🟠 Médio | Baixo | = |
| 6 | Filtro por metadados na recuperação | 🟢 Baixo | Médio | ↓ |
| 7 | Conjunto de avaliação mínimo (eval) | 🟢 Base | Médio | ↑ pontual |

> Recomendação de ordem: **1 → 2 → 3** primeiro (ganho imediato de custo/robustez sem mudar a arquitetura), depois 4 e 5.

---

## 1. Reranking em uma única chamada (batch) 🔴

### Problema atual
A função `rerank_documentos` faz **1 chamada ao LLM por chunk**. Com `k=8`, são **8 chamadas por pergunta**, somadas à chamada de geração = **9 chamadas/pergunta**. É o maior custo e a maior latência do pipeline.

### Proposta
Enviar todos os chunks em **uma única chamada** e pedir os scores de todos de uma vez, usando **saída estruturada (JSON)**.

```python
# Pseudo-implementação
prompt_rerank = """
Você é especialista em políticas internas de RH.
Pergunta: {pergunta}

Avalie a relevância de CADA trecho abaixo (0 a 10).
Retorne APENAS um JSON: {{"scores": [n1, n2, ...]}} na ordem dos trechos.

Trechos:
{trechos_numerados}
"""
```

- **Custo:** de ~8 chamadas para **1 chamada** de reranking (redução de ~8x nessa etapa).
- **Latência:** muito menor (sem loop sequencial de chamadas).
- **Robustez:** combinar com `response_format={"type": "json_object"}` ou `with_structured_output()` do LangChain.

> Alternativa futura (não agora): modelo de reranking dedicado (Cohere Rerank, `cross-encoder` local). Fica fora do escopo por adicionar dependência/complexidade.

---

## 2. Não reconstruir o Vector Store a cada execução 🔴

### Problema atual
`criar_vectorstore` sempre chama `Chroma.from_documents(...)`, que **re-embeda e regrava** todos os chunks no diretório persistido a cada inicialização — gerando custo de embeddings repetido e possível duplicação de dados no `./chroma_rh`.

### Proposta
Verificar se o banco já existe e, em caso afirmativo, **apenas carregar**:

```python
if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
else:
    vectorstore = Chroma.from_documents(
        documents=_chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
    )
```

- **Custo:** embeddings dos PDFs são gerados **uma única vez**, não a cada execução.
- **Cuidado:** incluir uma forma simples de invalidar/reconstruir quando os PDFs mudarem (ex.: flag/botão "reindexar" no Streamlit, ou apagar a pasta).

---

## 3. Parsing robusto do score de reranking 🟠

### Problema atual
```python
try:
    score = float(score)
except:
    score = 0
```
O `except:` nu engole qualquer erro e o LLM pode responder `"8/10"`, `"Nota: 7"` etc., zerando chunks relevantes silenciosamente.

### Proposta
- Usar **saída estruturada** (já contemplada no item 1) elimina o parsing frágil.
- Caso permaneça parsing de texto: extrair o número com regex e logar quando falhar, em vez de silenciar.
- Tratar `except Exception` específico, nunca `except:` nu.

---

## 4. Upgrade seletivo de modelos 🟠

Manter custo baixo significa **subir o modelo só onde agrega valor**, não em tudo.

### Embeddings
| Modelo | Qualidade | Custo relativo | Recomendação |
|--------|-----------|----------------|--------------|
| `text-embedding-3-small` (atual) | Boa | 1x | Manter como padrão |
| `text-embedding-3-large` | Melhor recall | ~6x | Só se a recuperação estiver falhando |

> Embedding roda uma vez por chunk (item 2 garante isso). Mesmo o `large` tem custo pontual baixo. Vale testar o `large` **se** notar chunks relevantes ficando de fora — caso contrário, manter o `small`.

### LLM (geração e reranking)
Estratégia de **dois modelos por etapa** mantém custo baixo:

| Etapa | Modelo sugerido | Justificativa |
|-------|-----------------|---------------|
| Reranking | `gpt-4o-mini` (atual) | Tarefa simples (pontuar), modelo barato basta |
| Geração da resposta | `gpt-4o-mini` → testar `gpt-4o` | Subir só aqui se a qualidade da resposta exigir |

- Tornar os modelos **configuráveis por etapa** (constantes separadas: `LLM_RERANK_MODEL`, `LLM_ANSWER_MODEL`).
- `temperature=0` já está correto para respostas determinísticas/factuais — manter.

> Nota de engenharia: o projeto usa OpenAI. Se futuramente quiser comparar custo/qualidade, vale fazer um teste A/B controlado num conjunto fixo de perguntas (ver item 7) antes de trocar — nunca trocar modelo "no escuro".

---

## 5. Prompt com fallback anti-alucinação 🟠

### Problema atual
O prompt instrui a responder com base no contexto, mas não define o que fazer quando o contexto **não contém** a resposta. O modelo pode preencher a lacuna inventando.

### Proposta
Adicionar instrução explícita de fallback:

```
Se a resposta não estiver nas políticas acima, responda exatamente:
"Não encontrei essa informação nas políticas internas disponíveis."
Não invente informações que não estejam no contexto.
```

- **Custo:** zero.
- **Impacto:** aumenta a confiabilidade — essencial para um agente de RH onde respostas erradas têm peso.

---

## 6. Filtro por metadados na recuperação 🟢

### Contexto
O pipeline já enriquece chunks com `categoria` (`ferias`, `home_office`, `conduta`, `geral`), mas **não usa** esse metadado na busca.

### Proposta (opcional, mais adiante)
Classificar a pergunta em uma categoria e aplicar filtro na `similarity_search`:

```python
vectorstore.similarity_search(pergunta, k=8, filter={"categoria": categoria_detectada})
```

- **Benefício:** recuperação mais precisa e **menos chunks irrelevantes** chegando ao reranking → menos custo.
- **Cuidado:** classificar a pergunta adiciona uma chamada/heurística; só vale se o volume de documentos crescer. Para 3 PDFs, o ganho é marginal — deixar para quando a base aumentar.

---

## 7. Conjunto de avaliação mínimo (eval) 🟢

### Por que
Toda mudança acima (modelo, chunking, reranking) precisa ser medida, não "sentida". Sem baseline, não dá para saber se uma melhoria ajudou ou piorou.

### Proposta mínima
Criar um arquivo `eval_perguntas.py` com ~10 perguntas e respostas esperadas (as 3 do final do `Projeto 3.py` já servem de semente):

```python
PERGUNTAS_TESTE = [
    {"pergunta": "Quais são as regras para concessão de férias?", "deve_conter": ["..."]},
    # ...
]
```

Rodar o pipeline em cada uma e checar se a resposta contém os termos esperados / cita o documento correto. Mantém-se simples (assert de substring), sem framework de eval pesado.

- **Custo:** pontual (roda sob demanda, não em produção).
- **Valor:** permite comparar `small` vs `large`, `mini` vs `4o`, etc., com dados.

---

## Resumo: caminho recomendado de implementação

1. **Fase 1 — Custo & robustez (sem mudar arquitetura):** itens 1, 2, 3.
2. **Fase 2 — Qualidade da resposta:** itens 5 e 4 (subir modelo só onde o eval mostrar ganho).
3. **Fase 3 — Escala (quando a base de documentos crescer):** itens 6 e 7.

Cada fase é entregável e testável de forma independente, preservando a simplicidade do projeto.
