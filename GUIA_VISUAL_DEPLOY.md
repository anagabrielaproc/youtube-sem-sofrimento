# 📸 Guia Visual: Como Colocar seu SaaS no Ar

Olá, Gabriela! Este guia foi criado para que você visualize exatamente onde clicar e o que digitar em cada etapa.

---

## 1. No seu Computador (CMD - Prompt de Comando)

Após baixar e extrair o arquivo `.zip`, você precisa abrir o terminal dentro da pasta do projeto.

### Como abrir o CMD na pasta certa:
1. Abra a pasta onde você extraiu os arquivos.
2. Clique na **barra de endereços** no topo da janela.
3. Digite `cmd` e aperte **Enter**.

### Comandos para rodar (Copie e Cole):
> **Dica:** No CMD, você pode colar clicando com o botão direito do mouse.

```bash
# 1. Criar o ambiente para o Python não bagunçar seu PC
python -m venv venv

# 2. Ativar esse ambiente
venv\Scripts\activate

# 3. Instalar as bibliotecas do projeto
pip install -r requirements.txt
```

---

## 2. No GitHub (Guardando seu Código)

O Render precisa ler seu código do GitHub para colocá-lo na internet.

1. Acesse [github.com/new](https://github.com/new).
2. Em **Repository name**, digite `youtube-sem-sofrimento`.
3. Deixe como **Public** ou **Private** (você escolhe).
4. Clique no botão verde **Create repository**.

### Enviando os arquivos via CMD:
Volte ao CMD que você abriu na etapa 1 e digite:
```bash
git init
git add .
git commit -m "Meu primeiro SaaS"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/youtube-sem-sofrimento.git
git push -u origin main
```

---

## 3. No Google Cloud (Pegando sua Chave)

Esta é a parte que permite ao sistema pesquisar no YouTube.

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Clique em **Selecionar um projeto** > **Novo Projeto**.
3. No menu (três risquinhos), vá em **APIs e Serviços** > **Biblioteca**.
4. Pesquise por `YouTube Data API v3` e clique em **Ativar**.
5. Vá em **Credenciais** > **Criar Credenciais** > **Chave de API**.
6. **Copie a chave gerada.**

---

## 4. No Render.com (O Grande Final)

Aqui é onde o site ganha vida e um link oficial.

1. No [Render](https://dashboard.render.com/), clique em **New +** > **Web Service**.
2. Escolha o seu repositório do GitHub.
3. Preencha assim:
   - **Name:** `youtube-sem-sofrimento`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. **IMPORTANTE:** Clique em **Advanced** > **Add Environment Variable**:
   - Chave: `YOUTUBE_API_KEY` | Valor: (Sua chave do Google)
   - Chave: `SECRET_KEY` | Valor: `gabriela_proenca_saas`
5. Clique em **Create Web Service**.

---

## 🚀 Pronto!
Em alguns minutos, o Render vai te dar um link (ex: `https://youtube-sem-sofrimento.onrender.com`). 

**Seu SaaS está oficialmente no ar!** 🎉
