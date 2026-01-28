# Guia Passo a Passo: Youtube Sem Sofrimento

Parabéns pelo seu novo SaaS! Aqui está o caminho detalhado para você tirar o projeto do papel e colocá-lo no ar.

---

## 1. Preparando o Terreno (No seu Computador)

Como você recebeu o projeto em um arquivo `.zip`, o processo de "clonagem" aqui significa extrair e organizar os arquivos para o seu GitHub.

1.  **Baixe e Extraia:** Baixe o arquivo `youtube_sem_sofrimento_v2.zip` e extraia em uma pasta no seu computador (ex: `C:\Projetos\youtube-saas`).
2.  **Instale o Python:** Se não tiver, baixe em [python.org](https://www.python.org/). Marque a opção **"Add Python to PATH"** durante a instalação.
3.  **Abra o Terminal:** Vá na pasta do projeto, clique na barra de endereços, digite `cmd` e dê Enter.
4.  **Crie um Ambiente Virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # No Windows
    source venv/bin/activate  # No Mac/Linux
    ```
5.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 2. Criando seu Repositório no GitHub

Para fazer o deploy (colocar o site no ar), você precisa que o código esteja no seu GitHub.

1.  Acesse [github.com](https://github.com/) e crie um novo repositório chamado `youtube-sem-sofrimento`.
2.  **Não** inicialize com README ou licença (deixe ele vazio).
3.  No seu terminal (dentro da pasta do projeto), execute:
    ```bash
    git init
    git add .
    git commit -m "Primeiro commit: MVP Youtube Sem Sofrimento"
    git branch -M main
    git remote add origin https://github.com/SEU_USUARIO/youtube-sem-sofrimento.git
    git push -u origin main
    ```

---

## 3. Conseguindo sua YouTube API Key (O Coração do Sistema)

O sistema precisa de uma "chave" para conversar com o YouTube.

1.  Vá ao [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um **Novo Projeto**.
3.  No menu lateral, vá em **APIs e Serviços > Biblioteca**.
4.  Procure por **YouTube Data API v3** e clique em **Ativar**.
5.  Vá em **APIs e Serviços > Credenciais**.
6.  Clique em **+ Criar Credenciais > Chave de API**.
7.  **Copie essa chave.** Você vai precisar dela no próximo passo.

---

## 4. Colocando no Ar (Deploy no Render.com)

O Render é uma plataforma excelente e gratuita para começar.

1.  Crie uma conta em [render.com](https://render.com/) usando seu GitHub.
2.  Clique em **New +** > **Web Service**.
3.  Conecte seu repositório `youtube-sem-sofrimento`.
4.  **Configurações de Build:**
    *   **Runtime:** `Python`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn run:app`
5.  **Variáveis de Ambiente (Crucial):** Clique em **Advanced** > **Add Environment Variable**:
    *   `YOUTUBE_API_KEY` = (Cole a chave que você pegou no Google)
    *   `SECRET_KEY` = (Crie uma senha qualquer, ex: `gabriela123`)
    *   `PYTHON_VERSION` = `3.11.0`
6.  Clique em **Create Web Service**.

---

## 5. Próximos Passos Sugeridos

Agora que o MVP está pronto, aqui estão ideias para você evoluir:

*   **Domínio Próprio:** Conecte um domínio como `app.youtubesemsofrimento.com.br` no Render.
*   **Pagamentos:** Integrar com Kiwify ou Hotmart para liberar o acesso apenas para alunos/assinantes.
*   **Filtros de IA:** Usar a API da OpenAI para resumir os vídeos encontrados e dizer por que eles são promissores.

---
**Dúvidas?** O arquivo `README.md` dentro da pasta também tem essas instruções de forma técnica. Sucesso no seu SaaS, Gabriela! 🚀
