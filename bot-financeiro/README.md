# Bot de monitoramento financeiro

Fica de olho em cotações (dólar, euro, bitcoin, etc.) e manda um **e-mail** quando:
- o preço passa de um valor que você definiu ("alvo_acima");
- o preço cai abaixo de um valor que você definiu ("alvo_abaixo");
- a variação do dia passa de uma porcentagem que você definiu ("variacao_pct").

**O que ele NÃO faz:** não compra, não vende, não toma nenhuma decisão financeira sozinho.
Só avisa — a decisão e a ação são sempre suas. Isto não é recomendação de investimento.

Cotações vêm da [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas), gratuita e sem cadastro.

## Passo 1: instalar

Precisa de Python 3 instalado. Depois, dentro desta pasta:

```
pip install -r requirements.txt
```

## Passo 2: configurar o e-mail (Gmail)

1. Ative a verificação em duas etapas na sua conta Google, se ainda não tiver: https://myaccount.google.com/security
2. Crie uma **senha de app** em https://myaccount.google.com/apppasswords (escolha "Outro" e dê um nome, ex: "bot cotação").
3. Copie a senha de 16 letras que aparece — **não é a senha da sua conta**, é uma senha só para este uso.

## Passo 3: configurar o bot

1. Copie `config.exemplo.json` para `config.json`.
2. Preencha `remetente` (seu Gmail), `senha_app` (a senha de app do passo 2) e `destinatario` (para onde o alerta vai — pode ser o mesmo e-mail).
3. Em `moedas`, ajuste os códigos que quiser (USD, EUR, BTC, ETH, GBP…) e os alvos:
   - Deixe `null` para não alertar por aquele critério.
   - `variacao_pct: 2` avisa quando a moeda subir ou cair 2% ou mais no dia.

**Nunca envie o `config.json` para o GitHub** — ele tem sua senha de app. O `.gitignore` já bloqueia isso.

## Passo 4: testar

```
python3 monitor.py --uma-vez
```

Mostra as cotações no terminal e manda e-mail se algum alerta disparar. Rode de novo depois de baixar um `alvo_acima`/`alvo_abaixo` bem próximo do preço atual, só para confirmar que o e-mail chega.

## Passo 5: deixar rodando sozinho

**Opção simples (o script fica aberto monitorando):**
```
python3 monitor.py
```
Ele confere a cada `intervalo_minutos` (padrão 15) e fica rodando até você fechar (Ctrl+C).

**Opção recomendada (agendado, sem precisar deixar nada aberto):**

*Linux/Mac (cron):*
```
crontab -e
```
Adicione uma linha (ajuste os caminhos):
```
*/15 * * * * cd /caminho/para/bot-financeiro && /usr/bin/python3 monitor.py --uma-vez
```

*Windows (Agendador de Tarefas):* crie uma tarefa que roda a cada 15 minutos com:
- Programa: `python`
- Argumentos: `monitor.py --uma-vez`
- Iniciar em: a pasta `bot-financeiro`

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `monitor.py` | O bot em si |
| `config.exemplo.json` | Modelo de configuração (copie para `config.json`) |
| `config.json` | Sua configuração real, com senha — **não vai para o GitHub** |
| `estado.json` | Criado sozinho pelo bot, guarda o que já foi alertado (evita spam de e-mail repetido) |
