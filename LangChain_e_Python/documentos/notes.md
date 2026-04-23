
*** Install Dependencies

    pip install uv
    
    uv venv .venv
    source .venv/bin/activate
    uv pip install --refresh -r requirements.txt

*** Create a file .env with the OPENAI_API_KEY=??????

*** Como corrigir "vazamento" de API Keys no histórico do Git (GitHub Push Protection)

    Se você acidentalmente incluiu chaves ou senhas nos seus commits e o GitHub bloqueou o push, você pode usar os comandos abaixo para achatar (squash) seus commits locais em um só. Importante: antes de rodar os comandos, certifique-se de que as chaves já foram removidas ou mascaradas dos arquivos no seu código atual.

    # 1. Volta o histórico para a branch remota, mantendo suas edições prontas (staged)
    git reset --soft origin/main

    # 2. Cria um novo commit limpo agrupando as alterações
    git commit -m "sua mensagem de commit aqui"

    # 3. Faz o push com sucesso
    git push origin main


