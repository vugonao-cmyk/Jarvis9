# Jarvis: seu assistente pessoal (versão celular)

Um app de voz estilo "Jarvis" que roda no navegador e pode ser instalado no celular como um aplicativo. É grátis: GitHub Pages para hospedar e uma chave gratuita de IA.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `index.html` | O app inteiro: visual, voz, chat e o prompt de personalidade |
| `manifest.json` | Permite "instalar" o app na tela inicial |
| `sw.js` | Faz o app abrir rápido e funcionar como aplicativo |
| `icon.svg`, `icon-192.png`, `icon-512.png` | Ícones do app |

---

## Passo 1: pegar a chave gratuita da IA

**Opção A: Google Gemini (recomendada)**
1. Entre em https://aistudio.google.com/apikey com sua conta Google.
2. Clique em **Create API key** e copie a chave.

**Opção B: Groq (muito rápido)**
1. Entre em https://console.groq.com/keys e crie uma conta.
2. Clique em **Create API Key** e copie a chave.

> ⚠️ **Nunca** coloque a chave dentro dos arquivos do GitHub. Você cola a chave só dentro do app, e ela fica guardada apenas no seu aparelho.

## Passo 2: publicar no GitHub (grátis)

1. Crie uma conta em https://github.com, se ainda não tiver.
2. Clique em **+** → **New repository**. Nome: `jarvis`. Deixe **Public** e clique em **Create repository**.
3. Na página do repositório, clique em **uploading an existing file**.
4. Arraste **todos os arquivos desta pasta** (não a pasta, os arquivos) e clique em **Commit changes**.
5. Vá em **Settings** → **Pages**.
6. Em **Branch**, escolha `main` e a pasta `/ (root)` e clique em **Save**.
7. Espere 1 a 2 minutos. O endereço vai aparecer ali:
   `https://SEU-USUARIO.github.io/jarvis/`

Dá para fazer tudo isso pelo celular, no navegador, mas é mais fácil no computador.

## Passo 3: instalar no celular

**Android (Chrome):** abra o endereço → menu **⋮** → **Instalar app** (ou "Adicionar à tela inicial").

**iPhone (Safari):** abra o endereço → botão **Compartilhar** → **Adicionar à Tela de Início**.
No iPhone, o reconhecimento de voz pode ser limitado. Se o microfone falhar, use o microfone do teclado para ditar.

## Passo 4: configurar

1. Abra o app. A tela de configurações aparece sozinha na primeira vez.
2. Escolha o provedor (Gemini ou Groq) e cole a chave.
3. Toque em **Buscar modelos disponíveis** para ver os modelos liberados na sua conta.
4. Escolha a voz, como ele deve te chamar ("senhor", "Tony", "chefe"…) e toque em **Salvar**.
5. Toque no círculo azul, permita o microfone e fale!

**Modo conversa:** ative nas configurações para ele voltar a ouvir sozinho depois de responder, como um diálogo contínuo.

## Personalizar a personalidade

Nas configurações há o campo **Personalidade (prompt do sistema)**. Edite à vontade, por exemplo:
- "Seja mais sarcástico, como o Jarvis dos filmes."
- "Você é especialista em eletrônica e me ajuda com minha loja."
- "Responda sempre com uma curiosidade no final."

Os marcadores `{NOME}`, `{TRATAMENTO}` e `{DATA}` são trocados automaticamente.

## (Opcional) Gerar um APK para Android

1. Com o app já no ar no GitHub Pages, entre em https://www.pwabuilder.com
2. Cole o seu endereço (`https://SEU-USUARIO.github.io/jarvis/`) e clique em **Start**.
3. Escolha **Android** → **Generate Package** e baixe o `.zip`.
4. Dentro dele há um `.apk`. Passe para o celular e instale (o Android vai pedir para permitir "fontes desconhecidas").

## Problemas comuns

| Problema | Solução |
|---|---|
| "API key not valid" | Confira se copiou a chave inteira, sem espaços. |
| Erro de modelo "not found" | Toque em **Buscar modelos disponíveis** e escolha outro. |
| Erro de cota ou limite (429) | O plano grátis tem limite por minuto e por dia. Espere um pouco ou troque de provedor. |
| O microfone não funciona | O app precisa estar em `https://` (o GitHub Pages já é). Permita o microfone nas configurações do navegador. Use o Chrome. |
| Ele não fala | Confira se "Responder em voz alta" está ligado e o volume de mídia está alto. |
| Mudei os arquivos e nada mudou | Feche e abra o app de novo (às vezes duas vezes) para ele pegar a atualização. |

## Próxima fase: versão para computador

A versão para PC (em Python) vai poder abrir programas, pesquisar na internet, tocar música e ler arquivos, coisas que o navegador sozinho não consegue fazer.
