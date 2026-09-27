#!/usr/bin/env python3
"""Jarvis PC: ponto de entrada do assistente de voz para computador."""
import webbrowser

from jarvis import config as configmod
from jarvis import memory
from jarvis import tools_local
from jarvis import tools_web
from jarvis import voice
from jarvis.ai import ApiError, ask_ai
from jarvis.prompt import extract_open


def montar_ferramentas(cfg: dict, fatos: list):
    decls = list(tools_web.DECLS) + tools_local.build_decls(cfg)
    impls = dict(tools_web.IMPLS)
    impls["abrir_programa"] = lambda args: tools_local.abrir_programa(args, cfg)
    impls["ler_arquivo"] = lambda args: tools_local.ler_arquivo(args, cfg)
    if memory.cloud_ready(cfg):
        decls = decls + [memory.LEMBRAR_FATO_DECL]
        impls["lembrar_fato"] = lambda args: memory.lembrar_fato(args, fatos, cfg)
    return decls, impls


def main():
    cfg = configmod.carregar_config()
    historico = memory.carregar_historico(cfg)
    fatos = memory.carregar_fatos(cfg)
    decls, impls = montar_ferramentas(cfg, fatos)

    print(f"{cfg['nome']} online. Aperte ENTER para falar pelo microfone, ou digite sua mensagem e ENTER.")
    if not cfg.get("programas_permitidos"):
        print("(nenhum programa liberado ainda em 'programas_permitidos' no config.json)")
    if not cfg.get("pastas_permitidas"):
        print("(nenhuma pasta liberada ainda em 'pastas_permitidas' no config.json)")

    while True:
        try:
            digitado = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais!")
            break

        if digitado:
            texto = digitado
        else:
            texto = voice.ouvir()
            if not texto:
                continue
            print(f"Você: {texto}")

        historico.append({"role": "user", "text": texto})
        memory.salvar_mensagem(cfg, historico, "user", texto)

        try:
            resposta = ask_ai(cfg, historico[-24:], fatos, decls, impls)
        except ApiError as e:
            print(f"[erro] {e}")
            historico.pop()
            continue

        clean, url = extract_open(resposta["text"])
        texto_resposta = clean or "Pronto, senhor."
        historico.append({"role": "assistant", "text": texto_resposta})
        memory.salvar_mensagem(cfg, historico, "assistant", texto_resposta)

        print(f"{cfg['nome']}: {texto_resposta}")
        for s in resposta.get("sources", []):
            print(f"  fonte: {s.get('title')} — {s.get('uri')}")

        for player in resposta.get("players", []):
            tools_web.tocar(player, cfg)

        if url:
            webbrowser.open(url)

        voice.falar(texto_resposta, cfg)


if __name__ == "__main__":
    main()
