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

## Memória na nuvem (para sempre, entre celular e computador)

Nas configurações, no campo **Código de sincronização**, crie um código (ou toque em **Gerar código aleatório**) e use **o mesmo código no celular e no computador**. A partir daí:

- Toda a conversa fica guardada **para sempre** num banco de dados na nuvem (Supabase), não só neste aparelho.
- O celular e o computador passam a **compartilhar a mesma conversa**: o que você falar em um aparece no outro.
- O Jarvis **aprende fatos duradouros sozinho** — nomes de pessoas próximas, preferências, projetos, decisões — e lembra deles em qualquer conversa futura, em qualquer aparelho.

**Trate o código como uma senha.** Quem souber o código acessa essa memória. Prefira o código gerado automaticamente (algo como `jarvis-a1b2c3`) a uma palavra fácil de adivinhar, e não compartilhe.

**Apagar:**
- **Apagar conversa** limpa só a tela deste momento; se você usa a nuvem, ela volta a aparecer no próximo acesso.
- **Apagar memória da nuvem** apaga tudo de vez — conversas e fatos guardados — e não pode ser desfeito.

Sem código de sincronização, o Jarvis funciona do mesmo jeito, só que a conversa fica salva apenas neste aparelho, como antes.

## Modo prontidão ("Jarvis, acorda")

Toque em **⏻ Modo prontidão** uma vez. A partir daí ele fica escutando, e é só chamar pelo nome:
- **"Jarvis"** ou **"Jarvis, acorda"** → ele responde "Sim, senhor?" e espera o seu pedido.
- **"Jarvis, que horas são?"** → ele já responde direto.

Conversas que não começam com o nome dele são ignoradas. A tela fica acesa enquanto a prontidão estiver ligada.
Limitação do navegador: com a tela apagada ou o app minimizado, ele não consegue escutar.

## Tocar música

Peça "toca uma música lofi", "coloca um jazz para tocar" ou "toca [nome da música/artista]". Aparece direto na conversa um player simples — um botão de play, o nome da faixa e do artista — e a música toca ali mesmo, sem abrir outra aba, sem vídeo e sem propaganda.

As músicas vêm do acervo livre do Internet Archive (artistas independentes e netlabels com licença livre), não do Spotify nem do YouTube. Por isso a versão original de um sucesso comercial famoso pode não estar disponível — nesse caso o Jarvis avisa e você pode tentar outro nome, artista ou estilo (lofi, jazz, acústico, eletrônica…). Tocar uma música nova pausa a anterior automaticamente.

**Trocar de música:** o player já vem com um botão **⏭ próxima faixa**, ao lado do play — toque nele para pular para a próxima música da mesma leva, sem precisar pedir de novo. Também dá para pedir por voz ("troca essa música", "pula essa"). Quando a fila da leva atual acabar, é só pedir outra música (por nome, artista ou estilo) que uma nova leva é montada.

## Internet e sites

- **Pesquisa no Google:** ele pesquisa sozinho quando você pergunta coisas atuais (clima, notícias, preços, jogos) e mostra as fontes. Ligue ou desligue nas configurações.
- **Abrir sites:** peça "abre o YouTube e toca lofi", "mostra no mapa a padaria mais próxima", "pesquisa no Google tal coisa". Se o navegador bloquear a abertura automática, aparece um botão **🔗 Abrir** na conversa.
- **Troca automática de modelo:** se um modelo do Google estiver sobrecarregado, ele passa sozinho para outro.

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

## Verificação automática (manutenção de graça)

Este projeto tem uma checagem automática que roda sozinha, de graça, toda vez que você publica uma atualização no GitHub (usa o **GitHub Actions**, incluído gratuitamente em repositórios públicos). Ela confere, antes de qualquer coisa:

- Se o código JavaScript de `index.html` e `baixar.html` não tem erro de digitação/sintaxe (um erro assim derruba o app inteiro).
- Se o `manifest.json` é um JSON válido.
- Se, quando `index.html` muda, a versão do cache em `sw.js` (`const CACHE = 'jarvis-vN';`) também foi atualizada — sem isso, o app instalado no celular fica "preso" numa versão antiga mesmo depois de você publicar a nova, e é exatamente esse tipo de problema que já aconteceu neste projeto.

**Onde ver o resultado:** na aba **Actions** do repositório no GitHub, depois de cada envio de arquivos. Um ✅ verde significa que está tudo certo para usar; um ❌ vermelho mostra exatamente o que corrigir antes de considerar a atualização pronta.

Não precisa configurar nada — os arquivos `.github/workflows/verificacao.yml` e `scripts/verificar.js` já vêm prontos; é só enviá-los para o repositório junto com os outros.

## Próxima fase: versão para computador

A versão para PC (em Python) vai poder abrir programas, pesquisar na internet, tocar música e ler arquivos, coisas que o navegador sozinho não consegue fazer.
