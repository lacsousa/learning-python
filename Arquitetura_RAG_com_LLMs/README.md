# Arquitetura_RAG_com_LLMs — Setup, correções e execução

Este diretório contém notebooks e código de exemplo para um fluxo RAG (Retrieval-Augmented Generation) usando LangChain, Chroma e OpenAI.

---

## 🐍 Ambiente Virtual (venv)

### 1. Criar o ambiente virtual

Execute **uma única vez**, na raiz do projeto (`Arquitetura_RAG_com_LLMs/`):

```bash
python3 -m venv .venv
```

### 2. Ativar o ambiente virtual

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

> Quando ativo, o prompt do terminal exibirá `(.venv)` no início.

### 3. Instalar as dependências

Com o ambiente ativo, instale os pacotes necessários:

```bash
pip install --upgrade pip
pip install langchain==0.1.20 langchain-community==0.0.38 langchain-openai==0.1.7 \
            pypdf chromadb python-dotenv openai ipykernel nbclient nbformat streamlit
```

### 4. Desativar o ambiente virtual

Quando terminar, basta rodar:

```bash
deactivate
```

### 5. Verificar se o venv está ativo

```bash
which python3
```

Se o caminho retornado contiver `.venv/bin/python3`, o ambiente está ativo. ✅

Exemplo de saída esperada:
```
/caminho/para/Arquitetura_RAG_com_LLMs/.venv/bin/python3
```

### 6. Listar dependências instaladas

Ver todos os pacotes instalados (formato tabela):
```bash
pip list
```

Ver no formato `pacote==versão` (útil para copiar ou exportar):
```bash
pip freeze
```

Gerar o arquivo `requirements.txt` com todas as dependências atuais:
```bash
pip freeze > requirements.txt
```

---

## 🚀 Executando os Projetos

### Projeto 1 — Agente RAG para Regras do Futebol

Executar como script Python (recomendado):
```bash
cd Projeto1
python3 projeto1.py
```

Executar como notebook Jupyter:
```bash
source .venv/bin/activate
jupyter lab
# Abra "Projeto 1.ipynb" e selecione o kernel "Python (Arquitetura .venv)"
```

### Projeto 3 — Agente de RH com Streamlit

Apps Streamlit **não** são executados com `python3`. Use sempre:
```bash
streamlit run "Projeto3/Projeto 3.py"
```

O app abrirá automaticamente no navegador em `http://localhost:8501`.
Para encerrar: `Ctrl+C` no terminal.

---

## 📋 Resumo das correções realizadas

### Sessão inicial
- Criado ambiente virtual local: `.venv/` (Python 3.12 recomendado).
- Criado arquivo `.env` na raiz do projeto para `OPENAI_API_KEY` (NÃO comitar).
- Registrado kernel Jupyter: `arquitetura-venv` (display name: "Python (Arquitetura .venv)").
- Patch aplicado em `Projeto 1.ipynb` para:
  - Verificar existência do PDF `regras_futebol.pdf` antes de tentar carregá-lo.
  - Ler `OPENAI_API_KEY` via `os.getenv` e lançar erro claro se ausente.
  - Usar `OpenAIEmbeddings` e `ChatOpenAI` com a chave explícita via ambiente.
- Executado e salvo notebook com saídas em: `Projeto1/Projeto 1.executed_with_env.ipynb`.

### Sessão de correções (Projeto 1 e 3)
- **Notebook → Script Python:** `Projeto 1.ipynb` convertido em `Projeto1/projeto1.py` com:
  - `load_dotenv()` adicionado para carregar o `.env` corretamente.
  - Caminhos de arquivo robustos usando `Path(__file__).resolve()`.
  - Loop interativo de perguntas ao final do script.
- **Instalação do `streamlit`:** adicionado ao `.venv` para rodar o Projeto 3.
- **Correção de caminhos no Projeto 3:** `Projeto 3.py` usava caminhos relativos (`"politica_ferias.pdf"`) que falhavam dependendo de onde o app era iniciado. Corrigido para usar `os.path.abspath(__file__)`, tornando os caminhos sempre relativos à pasta do script.
- **Gerado `requirements.txt`** com todas as dependências atuais via `pip freeze > requirements.txt`.

### Principais problemas resolvidos
- `OPENAI_API_KEY` não carregada: faltava `load_dotenv()` — resolvido.
- Erro de kernel/`ipykernel` faltando: resolvido instalando `ipykernel` e registrando o kernel.
- `ModuleNotFoundError: No module named 'streamlit'`: resolvido com `pip install streamlit`.
- `ValueError: File path politica_ferias.pdf is not a valid file or url`: caminhos absolutos corrigidos no Projeto 3.
- Comando errado para Streamlit: `python3 app.py` não funciona — o correto é `streamlit run app.py`.

Requisitos (instalar no `.venv` criado)

Recomendo criar e usar um ambiente virtual por projeto. Exemplos de comandos:

```bash
# Na pasta do projeto
python3 -m venv .venv
source .venv/bin/activate
# Instalar dependências necessárias
pip install --upgrade pip
pip install ipykernel nbclient nbformat pypdf chromadb langchain==0.1.20 \
  langchain-community==0.0.38 langchain-openai==0.1.7 openai python-dotenv
```

Registrar kernel Jupyter (após ativar `.venv`):

```bash
python -m ipykernel install --user --name=arquitetura-venv --display-name "Python (Arquitetura .venv)"
```

Criação / uso de `.env`

- Crie o arquivo `Arquitetura_RAG_com_LLMs/.env` contendo apenas a linha:

```text
OPENAI_API_KEY="sk-...sua_chave_aqui..."
```

- **Importante:** não compartilhe a chave publicamente. O repositório já contém um `.gitignore` que inclui `.env`, mas se o `.env` já foi commitado você deve removê-lo do índice (veja seção Git abaixo).

Executando o notebook

1. Execução interativa (Jupyter):

```bash
# Ative o venv e inicie JupyterLab ou Jupyter Notebook
source .venv/bin/activate
jupyter lab
# Abra Projeto 1.ipynb e selecione o kernel "Python (Arquitetura .venv)"
```

2. Execução programática (gera uma cópia com saídas):

Um comando usado durante as correções (executa o notebook e salva `Projeto 1.executed_with_env.ipynb`):

```bash
# Exemplo (substitua os caminhos conforme necessário)
set -a && . /path/to/Arquitetura_RAG_com_LLMs/.env && set +a && \
cd /path/to/Arquitetura_RAG_com_LLMs/Projeto1 && \
/path/to/Arquitetura_RAG_com_LLMs/.venv/bin/python - <<'PY'
from nbformat import read, write
from nbclient import NotebookClient
import os
full = os.path.join(os.getcwd(), 'Projeto 1.ipynb')
with open(full, 'r', encoding='utf-8') as f:
    nb = read(f, as_version=4)
client = NotebookClient(nb, kernel_name='arquitetura-venv', timeout=1800, allow_errors=False)
client.execute()
with open(full.replace('.ipynb', '.executed_with_env.ipynb'), 'w', encoding='utf-8') as f:
    write(nb, f)
PY
```

Substitua `/path/to` pelos caminhos corretos no seu ambiente. Esse fluxo garante que a variável `OPENAI_API_KEY` esteja definida no ambiente da execução.

Notas sobre arquivos de dados

- Coloque `regras_futebol.pdf` em `Projeto1/` (ou atualize o caminho na célula de carregamento). O notebook agora verifica a existência do arquivo e explica o que fazer se estiver ausente.

Git — proteger chaves e ambientes

- Garanta que `.env` está listado em `.gitignore` (o arquivo `.gitignore` no projeto já contém `.env` e `.venv/*`).
- Se você já comitou `.env` acidentalmente, remova-o do índice mantendo o arquivo local:

```bash
git rm --cached Arquitetura_RAG_com_LLMs/.env
git rm -r --cached Arquitetura_RAG_com_LLMs/.venv/ || true
git add .gitignore
git add -A
git commit -m "Ignore local env and venv; remove from index"
git push origin main
```

Arquivos gerados pelo agente

- `Projeto1/Projeto 1.executed_with_env.ipynb` — cópia do notebook com saídas após reexecução.

Ajuda adicional

- Se quiser, posso:
  - abrir/exibir trechos do notebook (células específicas),
  - commitar os arquivos gerados (se autorizar),
  - ajustar a célula para carregar `.env` automaticamente via `python-dotenv`.

Contato

- Se ocorrerem erros de autenticação, verifique se a chave em `.env` está correta e sem aspas extras/novas linhas.

---

Arquivo gerado automaticamente pelo assistente para documentar as mudanças e o fluxo de execução local.
