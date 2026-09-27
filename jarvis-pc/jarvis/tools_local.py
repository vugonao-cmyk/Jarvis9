"""Ferramentas que tocam a máquina local: abrir_programa e ler_arquivo.

Estas são a única superfície nova de execução/leitura local do projeto (o navegador nunca
teve isso), então cada função valida tudo no código Python — nunca confia no que o modelo
mandou como argumento. O schema de function-calling (enum de programas, descrição das
pastas) é só uma dica para o modelo; o controle de verdade é sempre feito aqui.
"""
import os
import subprocess


def build_decls(cfg: dict) -> list:
    apelidos = sorted((cfg.get("programas_permitidos") or {}).keys())
    return [
        {
            "name": "abrir_programa",
            "description": "Abre um programa da lista fixa e pré-aprovada pelo usuário. Não é possível abrir nada fora dessa lista.",
            "parameters": {
                "type": "object",
                "properties": {"programa": {"type": "string", "enum": apelidos or ["nenhum_configurado"]}},
                "required": ["programa"],
            },
        },
        {
            "name": "ler_arquivo",
            "description": "Lê um arquivo (texto, PDF ou Word) dentro das pastas autorizadas pelo usuário. Caminho deve ser relativo a uma dessas pastas, nunca absoluto.",
            "parameters": {
                "type": "object",
                "properties": {"caminho": {"type": "string"}},
                "required": ["caminho"],
            },
        },
    ]


def abrir_programa(args: dict, cfg: dict) -> dict:
    apelido = args.get("programa", "")
    mapa = cfg.get("programas_permitidos") or {}
    if apelido not in mapa:
        return {"result": {"erro": f"'{apelido}' não está na lista de programas permitidos."}}
    if cfg.get("confirmar_acoes_locais", True):
        resposta = input(f"[Jarvis] Confirmar abertura de '{apelido}'? (s/N) ").strip().lower()
        if resposta != "s":
            return {"result": {"erro": "Ação cancelada pelo usuário."}}
    try:
        subprocess.Popen([mapa[apelido]], shell=False)
        return {"result": {"ok": True, "abriu": apelido}}
    except FileNotFoundError:
        return {"result": {"erro": f"Executável configurado para '{apelido}' não encontrado: {mapa[apelido]}"}}
    except OSError as e:
        return {"result": {"erro": f"Não consegui abrir '{apelido}': {e}"}}


def _resolver_caminho(caminho_pedido: str, pastas_permitidas: list):
    """Só devolve um caminho se ele estiver de fato dentro de uma pasta permitida (via realpath,
    o que também fecha o caso de um symlink apontando para fora)."""
    if not caminho_pedido or os.path.isabs(caminho_pedido):
        return None
    for base in pastas_permitidas:
        base_real = os.path.realpath(os.path.expanduser(base))
        candidato = os.path.realpath(os.path.join(base_real, caminho_pedido))
        if candidato == base_real or candidato.startswith(base_real + os.sep):
            return candidato
    return None


def _extrair_texto(caminho: str, ext: str) -> str:
    if ext == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(caminho).pages)
    if ext == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(caminho).paragraphs)
    with open(caminho, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def ler_arquivo(args: dict, cfg: dict) -> dict:
    alvo = _resolver_caminho(args.get("caminho", ""), cfg.get("pastas_permitidas") or [])
    if not alvo or not os.path.isfile(alvo):
        return {"result": {"erro": "Caminho fora das pastas autorizadas ou arquivo inexistente."}}
    ext = os.path.splitext(alvo)[1].lower()
    if ext not in (cfg.get("extensoes_permitidas") or []):
        return {"result": {"erro": f"Extensão '{ext}' não autorizada."}}
    limite = cfg.get("tamanho_max_kb", 300) * 1024
    if os.path.getsize(alvo) > limite:
        return {"result": {"erro": f"Arquivo maior que o limite de {cfg.get('tamanho_max_kb', 300)} KB."}}
    try:
        texto = _extrair_texto(alvo, ext)
    except Exception as e:
        return {"result": {"erro": f"Não consegui ler esse arquivo: {e}"}}
    return {"result": {"caminho": args["caminho"], "conteudo": texto[:20000]}}
