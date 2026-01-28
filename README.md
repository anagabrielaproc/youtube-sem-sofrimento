# Youtube Sem Sofrimento - SaaS MVP

Este é um MVP de um SaaS para garimpo de canais e vídeos promissores no YouTube, inspirado na metodologia "Consumidor → Validação → Engenharia Reversa".

## Funcionalidades

- **Autenticação:** Sistema de login seguro.
- **Garimpo de Canais:** Busca avançada de vídeos com filtros de idioma, país, período e limite de resultados.
- **Canais Promissores:** Identificação automática de canais com alto potencial (poucos inscritos e muitas views).
- **Dashboard:** Visão geral e explicação da metodologia.
- **Identidade Visual:** Design moderno e elegante inspirado no estilo de gabiproenca.com.br (tema escuro com rosa de destaque).

## Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Banco de Dados:** SQLite (SQLAlchemy)
- **API:** YouTube Data API v3

## Como Executar Localmente

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure sua API Key do YouTube no arquivo `.env` ou diretamente nas configurações do sistema:
   ```env
   YOUTUBE_API_KEY=sua_chave_aqui
   SECRET_KEY=sua_chave_secreta
   ```
4. Execute a aplicação:
   ```bash
   python run.py
   ```
5. Acesse `http://localhost:5000`.
   - **Usuário padrão:** `admin`
   - **Senha padrão:** `admin123`

## Deploy no Render

1. Crie uma conta em [render.com](https://render.com).
2. Conecte seu repositório GitHub.
3. Crie um novo "Web Service".
4. Configure:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Adicione as Variáveis de Ambiente (`Environment Variables`):
   - `YOUTUBE_API_KEY`: Sua chave da API do Google.
   - `SECRET_KEY`: Uma string aleatória para segurança da sessão.
   - `PYTHON_VERSION`: 3.11.0 (ou superior).

---
Desenvolvido com foco em praticidade e agilidade para criadores de conteúdo.
