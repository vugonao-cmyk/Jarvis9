#!/usr/bin/env python3
"""Bot de monitoramento financeiro: acompanha cotações e avisa por e-mail.

Não compra, não vende, não toma nenhuma decisão financeira sozinho — só avisa.
Fonte das cotações: AwesomeAPI (economia.awesomeapi.com.br), gratuita e sem chave.
"""
import argparse
import json
import smtplib
import sys
import time
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

import requests

PASTA = Path(__file__).parent
CONFIG_PATH = PASTA / "config.json"
ESTADO_PATH = PASTA / "estado.json"
API_URL = "https://economia.awesomeapi.com.br/json/last/{pares}"


def carregar_config():
    if not CONFIG_PATH.exists():
        sys.exit(
            f"Não encontrei {CONFIG_PATH}.\n"
            "Copie config.exemplo.json para config.json e preencha seus dados "
            "(veja o README.md desta pasta)."
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def carregar_estado():
    if ESTADO_PATH.exists():
        return json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
    return {}


def salvar_estado(estado):
    ESTADO_PATH.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")


def buscar_cotacoes(codigos):
    pares = ",".join(f"{c}-BRL" for c in codigos)
    r = requests.get(API_URL.format(pares=pares), timeout=15)
    r.raise_for_status()
    dados = r.json()
    # a API devolve chaves tipo "USDBRL"
    return {v["code"]: v for v in dados.values()}


def enviar_email(cfg_email, assunto, corpo):
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = cfg_email["remetente"]
    msg["To"] = cfg_email["destinatario"]
    with smtplib.SMTP(cfg_email["servidor_smtp"], cfg_email["porta"]) as s:
        s.starttls()
        s.login(cfg_email["remetente"], cfg_email["senha_app"])
        s.sendmail(cfg_email["remetente"], [cfg_email["destinatario"]], msg.as_string())


def verificar_uma_vez(cfg, estado):
    codigos = [m["codigo"] for m in cfg["moedas"]]
    try:
        cotacoes = buscar_cotacoes(codigos)
    except Exception as e:
        print(f"[aviso] falha ao buscar cotações: {e}")
        return estado

    hoje = date.today().isoformat()
    alertas = []

    for moeda in cfg["moedas"]:
        codigo = moeda["codigo"]
        c = cotacoes.get(codigo)
        if not c:
            continue
        preco = float(c["bid"])
        variacao_pct = float(c["pctChange"])
        nome = moeda.get("nome", codigo)
        chave = estado.setdefault(codigo, {"acima": False, "abaixo": False, "variacao_dia": None})

        alvo_acima = moeda.get("alvo_acima")
        if alvo_acima is not None:
            if preco >= alvo_acima and not chave["acima"]:
                alertas.append(f"{nome} ({codigo}) passou de R$ {alvo_acima:.4f} — agora R$ {preco:.4f}.")
                chave["acima"] = True
            elif preco < alvo_acima:
                chave["acima"] = False

        alvo_abaixo = moeda.get("alvo_abaixo")
        if alvo_abaixo is not None:
            if preco <= alvo_abaixo and not chave["abaixo"]:
                alertas.append(f"{nome} ({codigo}) caiu abaixo de R$ {alvo_abaixo:.4f} — agora R$ {preco:.4f}.")
                chave["abaixo"] = True
            elif preco > alvo_abaixo:
                chave["abaixo"] = False

        limite_variacao = moeda.get("variacao_pct")
        if limite_variacao is not None and abs(variacao_pct) >= limite_variacao and chave["variacao_dia"] != hoje:
            sinal = "subiu" if variacao_pct > 0 else "caiu"
            alertas.append(f"{nome} ({codigo}) {sinal} {abs(variacao_pct):.2f}% hoje — agora R$ {preco:.4f}.")
            chave["variacao_dia"] = hoje

        print(f"{nome} ({codigo}): R$ {preco:.4f}  ({variacao_pct:+.2f}% hoje)")

    if alertas:
        corpo = "\n".join(alertas) + "\n\n(Isto é só um aviso automático de preço, não é recomendação de compra ou venda.)"
        try:
            enviar_email(cfg["email"], "Alerta de cotação — Jarvis", corpo)
            print(f"[ok] e-mail de alerta enviado ({len(alertas)} aviso(s)).")
        except Exception as e:
            print(f"[erro] não consegui enviar o e-mail: {e}")

    return estado


def main():
    parser = argparse.ArgumentParser(description="Monitor de cotações com alerta por e-mail.")
    parser.add_argument("--uma-vez", action="store_true", help="Confere uma vez e sai (ideal para cron/Agendador de Tarefas).")
    args = parser.parse_args()

    cfg = carregar_config()
    estado = carregar_estado()

    if args.uma_vez:
        estado = verificar_uma_vez(cfg, estado)
        salvar_estado(estado)
        return

    intervalo = cfg.get("intervalo_minutos", 15) * 60
    print(f"Monitorando a cada {cfg.get('intervalo_minutos', 15)} minuto(s). Ctrl+C para parar.")
    while True:
        estado = verificar_uma_vez(cfg, estado)
        salvar_estado(estado)
        time.sleep(intervalo)


if __name__ == "__main__":
    main()
