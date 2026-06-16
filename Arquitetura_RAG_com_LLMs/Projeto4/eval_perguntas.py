# ============================================
# PROJETO 4 — CONJUNTO DE AVALIAÇÃO MÍNIMO (item [7] da spec-rag.md)
# ============================================
#
# Objetivo: medir, em vez de "sentir", o efeito de mudanças (modelo de
# embedding, modelo de LLM, chunking, reranking, filtro por categoria).
#
# Estratégia de asserção (starter eval, sem ground truth do conteúdo dos PDFs):
#   - ROTEAMENTO: o documento-fonte esperado aparece nas fontes usadas?
#   - COBERTURA:  a resposta é não-vazia e NÃO é o fallback "Não encontrei..."?
# Isso valida recuperação + reranking, que é o que o eval precisa garantir.
# (Asserções de conteúdo podem ser adicionadas depois, se as respostas de
#  referência forem extraídas dos PDFs.)
#
# Uso:
#   cd Arquitetura_RAG_com_LLMs/Projeto4
#   ../.venv/bin/python eval_perguntas.py
#
# Custo: como o índice (chroma_rh) já foi persistido, NÃO há re-embedding;
# cada pergunta gasta ~2 chamadas ao LLM (1 reranking em batch + 1 resposta).
# ============================================

import os

from dotenv import load_dotenv

# Carrega o .env da raiz de Arquitetura_RAG_com_LLMs (um nível acima)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

# Importa o pipeline do Projeto4 (a UI Streamlit fica sob __main__, não roda no import)
from Projeto4 import construir_vectorstore, responder_pergunta

# Mesma string de fallback definida no prompt anti-alucinação do Projeto4 [5]
FALLBACK = "Não encontrei essa informação nas políticas internas disponíveis."


# =========================
# Casos de teste
# =========================
# `doc_esperado`: nome do PDF que deveria fundamentar a resposta (roteamento).
#
# BASELINE ESPERADO: 4/5 aprovados.
# O caso [1] ("regras para concessão de férias") é um "DEVE RECUSAR" conhecido:
# investigamos e o PDF de férias cobre indenização/programação/acúmulo/período
# aquisitivo, mas NÃO traz uma lista de "regras de concessão". Os chunks que citam
# "concessão" são apenas frases introdutórias (recuperados em rank #1-2), então a
# geração aciona corretamente o fallback anti-alucinação [5] em vez de inventar.
# Mantemos este caso de propósito: se um dia ele PASSAR, provavelmente será por
# alucinação — exatamente o que NÃO queremos. Trate-o como teste de regressão.
PERGUNTAS_TESTE = [
    {
        # "deve recusar" — ver nota acima. Conta como FALHA no placar, mas é o
        # comportamento correto (não há regras de concessão explícitas no PDF).
        "pergunta": "Quais são as regras para concessão de férias aos colaboradores?",
        "doc_esperado": "politica_ferias.pdf",
    },
    {
        "pergunta": "Quem pode trabalhar em regime de home office e quais são as condições?",
        "doc_esperado": "politica_home_office.pdf",
    },
    {
        "pergunta": "Quais comportamentos são considerados inadequados segundo o código de conduta?",
        "doc_esperado": "codigo_conduta.pdf",
    },
    {
        "pergunta": "Como funciona o período aquisitivo de férias?",
        "doc_esperado": "politica_ferias.pdf",
    },
    {
        "pergunta": "É permitido home office em tempo integral?",
        "doc_esperado": "politica_home_office.pdf",
    },
]


def avaliar_caso(caso, vectorstore):
    """Roda um caso e retorna (passou, detalhes)."""
    resposta, fontes = responder_pergunta(caso["pergunta"], vectorstore)

    docs_citados = {f.metadata.get("documento") for f in fontes}

    # Asserção 1 — roteamento: o documento esperado está entre as fontes?
    roteou_certo = caso["doc_esperado"] in docs_citados

    # Asserção 2 — cobertura: resposta útil (não-vazia e não é o fallback)?
    resposta_util = bool(resposta.strip()) and FALLBACK not in resposta

    passou = roteou_certo and resposta_util

    detalhes = {
        "roteamento": roteou_certo,
        "cobertura": resposta_util,
        "docs_citados": docs_citados,
    }
    return passou, detalhes


def main():
    print("Construindo/carregando o índice vetorial...")
    vectorstore = construir_vectorstore()

    print("\nRodando avaliação...\n" + "=" * 60)

    aprovados = 0
    for i, caso in enumerate(PERGUNTAS_TESTE, start=1):
        passou, det = avaliar_caso(caso, vectorstore)
        aprovados += int(passou)

        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"\n[{i}] {status}  —  {caso['pergunta']}")
        print(f"    esperado: {caso['doc_esperado']}")
        print(f"    roteamento OK: {det['roteamento']} | cobertura OK: {det['cobertura']}")
        print(f"    docs citados: {sorted(d for d in det['docs_citados'] if d)}")

    total = len(PERGUNTAS_TESTE)
    print("\n" + "=" * 60)
    print(f"RESULTADO: {aprovados}/{total} casos aprovados "
          f"({100 * aprovados / total:.0f}%)")


if __name__ == "__main__":
    main()
