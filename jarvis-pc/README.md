# Jarvis PC (versão para computador)

É o mesmo Jarvis do navegador, mas rodando no seu computador — o que permite três coisas que
o navegador sozinho não consegue fazer: **abrir programas** (de uma lista que você escolhe),
**ler arquivos locais** (de pastas que você escolhe) e **tocar música com um player de
verdade**. Pesquisa no Google, clima, Wikipédia, cotação e a memória compartilhada com o
celular funcionam igual ao app do navegador.

**Importante:** isto é uma ferramenta pessoal, para uso na sua própria máquina. Abrir
programas e ler arquivos por pedido de um assistente de IA é uma capacidade nova e mais
sensível que um app de navegador — por isso ela só funciona dentro de listas que **você**
configura (nunca "abra qualquer coisa"), e leia a seção **Riscos e limites** antes de usar.

## O que tem na pasta

| Arquivo/pasta | Para que serve |
|---|---|
| `jarvis_pc.py` | Ponto de entrada — é o que você roda |
| `jarvis/` | O código do assistente (IA, ferramentas, voz, memória) |
| `config.exemplo.json` | Modelo de configuração (copie para `config.json`) |
| `config.json` | Sua configuração real, com sua chave — **não vai para o GitHub** |
| `estado/` | Criado sozinho pelo bot: histórico e fatos guardados localmente (se você não usar o código de sincronização) |
| `requirements.txt` | Dependências Python |

## Passo 1: instalar

Precisa de Python 3.9+ instalado.

```
cd jarvis-pc
pip install -r requirements.txt
```

Duas das dependências (`pyaudio`, para o microfone) às vezes pedem uma biblioteca do
sistema operacional antes de instalar pelo pip:

- **Linux (Debian/Ubuntu):** `sudo apt install portaudio19-dev espeak-ng` antes do `pip install`.
- **macOS:** `brew install portaudio` antes do `pip install`.
- **Windows:** normalmente instala direto; se `pip install pyaudio` falhar, procure por "pyaudio wheel windows" para baixar um pacote pré-compilado da sua versão do Python.

Se não quiser lidar com isso agora, pode pular — o Jarvis funciona só por texto (veja a
seção de voz mais abaixo).

## Passo 2: pegar a chave gratuita da IA

Igual ao app do navegador:

**Opção A: Google Gemini (recomendada, dá acesso a mais ferramentas)**
1. Entre em https://aistudio.google.com/apikey com sua conta Google.
2. Clique em **Create API key** e copie a chave.

**Opção B: Groq (muito rápido)**
1. Entre em https://console.groq.com/keys e crie uma conta.
2. Clique em **Create API Key** e copie a chave.

> Na v1, abrir programas e ler arquivos só funcionam com o **Gemini** (é o único dos dois
> provedores gratuitos com essas ferramentas ligadas por enquanto). No Groq o Jarvis PC
> continua conversando normalmente, só sem essas duas capacidades extras.

## Passo 3: configurar

1. Copie `config.exemplo.json` para `config.json`.
2. Preencha `key` com a chave do passo 2, e `provider` com `"gemini"` ou `"groq"`.
3. Ajuste `programas_permitidos`: um apelido (o que você vai falar) apontando para o caminho
   real do programa. Exemplos por sistema:
   - **Windows:** `"calculadora": "calc.exe"`, `"navegador": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"`
   - **macOS:** `"calculadora": "/System/Applications/Calculator.app/Contents/MacOS/Calculator"`
   - **Linux:** `"calculadora": "gnome-calculator"`, `"navegador": "firefox"`
4. Ajuste `pastas_permitidas`: as pastas onde o Jarvis pode ler arquivos, ex: `["~/Documents", "~/Desktop/relatorios"]`. Ele só lê texto, PDF e Word (`.txt`, `.md`, `.csv`, `.json`, `.py`, `.log`, `.pdf`, `.docx`) e nunca sai dessas pastas — nem com `..`, nem com um atalho/symlink que aponte para fora.
5. Deixe `confirmar_acoes_locais: true` (o padrão) para ele sempre perguntar antes de abrir um programa. Só desligue se tiver certeza do que está fazendo.

**Nunca envie o `config.json` para o GitHub** — ele tem sua chave. O `.gitignore` já bloqueia isso.

## Passo 4: rodar

```
python3 jarvis_pc.py
```

Aperte ENTER (mensagem vazia) para falar pelo microfone, ou digite sua pergunta e aperte
ENTER. Peça, por exemplo:
- "Qual é a previsão do tempo em Curitiba?"
- "Toca uma música lofi"
- "Abre a calculadora" (vai pedir confirmação antes de abrir, se `confirmar_acoes_locais` estiver ligado)
- "Leia o arquivo relatorio.txt e me resuma"
- "Pesquisa no Google as notícias de hoje sobre IA" (só no Gemini)

## Memória compartilhada com o celular (opcional)

Use o mesmo **código de sincronização** (`space`) que você já usa no app do navegador, no
campo `space` do `config.json`. A partir daí a conversa e os fatos guardados ficam
compartilhados entre o celular e o PC, na mesma nuvem (Supabase). **Trate o código como uma
senha** — quem souber o código acessa essa memória (o mesmo aviso já vale hoje para o app do
navegador). Sem `space` configurado, o Jarvis PC guarda o histórico só localmente, em `estado/`.

## Sobre a voz

O reconhecimento de fala (`SpeechRecognition`) usa um serviço gratuito e **não-oficial** do
Google embutido na biblioteca — funciona sem nenhuma configuração ou chave, mas por não ser
um serviço oficial ele pode ter algum limite de uso ou mudar de comportamento sem aviso no
futuro. Se isso acontecer, ou se você preferir, digitar continua funcionando exatamente
igual, sem depender de voz nenhuma. A fala de resposta (`pyttsx3`) é totalmente offline; a
qualidade da voz em português varia por sistema operacional (melhor no Windows/macOS, mais
robótica no Linux com `espeak-ng`). Não existe ainda um "modo de prontidão" contínuo tipo
"Jarvis, acorda" como no navegador — por enquanto é sempre aperte-para-falar.

## Riscos e limites (leia antes de usar)

- **Abrir programas e ler arquivos só funcionam dentro de listas fixas que você mesmo
  configura** (`programas_permitidos`, `pastas_permitidas`). O modelo de IA nunca recebe nem
  inventa um caminho — ele só pode citar um apelido ou um caminho relativo, e o código
  Python confere tudo antes de agir. Nada fora dessas listas é aceito, ponto.
- **Na v1, abrir um programa nunca recebe argumentos vindos do modelo** — por exemplo, não
  dá para pedir "abre o navegador nesse site"; ele só abre o programa puro, do jeito
  configurado. Isso é proposital: evita que um texto malicioso (vindo de uma pesquisa na
  internet, ou de uma memória sincronizada) tente usar um programa como atalho para abrir
  uma URL ou arquivo perigoso.
- **Se você usa o código de sincronização (`space`), trate-o como senha de verdade.**
  Qualquer texto guardado nele (mensagens, fatos) entra na conversa como contexto "de
  confiança" — e agora essa conversa está ao lado de ferramentas que tocam seu computador.
  A allowlist de programas/pastas já limita bastante o estrago possível, mas por isso vale
  manter `confirmar_acoes_locais: true` e não espalhar o código do `space`.
- **Isto não é um antivírus nem uma sandbox.** É um assistente pessoal com limites simples e
  auditáveis (allowlist + confirmação), pensado para uso individual — não para rodar sem
  supervisão numa máquina compartilhada ou de trabalho sem avaliar isso com quem administra ela.

## Problemas comuns

| Problema | Solução |
|---|---|
| "Não encontrei config.json" | Copie `config.exemplo.json` para `config.json` e preencha. |
| `pip install pyaudio` falha | Veja as dependências de sistema no Passo 1 (portaudio/espeak-ng). |
| Microfone não funciona | Confira a permissão de microfone do seu sistema operacional para o terminal/Python. Digitar continua funcionando normalmente. |
| "Executável configurado para 'X' não encontrado" | Confira o caminho em `programas_permitidos` no `config.json` — no Windows use `\\\\` (barra dupla) nos caminhos. |
| "não está na lista de programas permitidos" | Adicione o apelido em `programas_permitidos` no `config.json`. |
| "Caminho fora das pastas autorizadas" | O arquivo pedido não está dentro de nenhuma pasta listada em `pastas_permitidas`, ou o caminho era absoluto (só caminhos relativos são aceitos). |
| Erro de cota (429) no Gemini/Groq | O plano grátis tem limite por minuto e por dia. Espere um pouco. |
