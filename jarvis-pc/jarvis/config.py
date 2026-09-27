"""Carrega e valida a configuração do Jarvis PC."""
import json
import sys
from pathlib import Path

PASTA_RAIZ = Path(__file__).resolve().parent.parent
CONFIG_PATH = PASTA_RAIZ / "config.json"

PADROES = {
    "nome": "Jarvis",
    "tratamento": "senhor",
    "provider": "gemini",
    "key": "",
    "model": "",
    "voz": True,
    "busca": True,
    "space": "",
    "prompt": "",
    "confirmar_acoes_locais": True,
    "programas_permitidos": {},
    "pastas_permitidas": [],
    "extensoes_permitidas": [".txt", ".md", ".csv", ".json", ".py", ".log", ".pdf", ".docx"],
    "tamanho_max_kb": 300,
    "musica_player": "auto",
}


def carregar_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"Não encontrei {CONFIG_PATH}.\n"
            "Copie config.exemplo.json para config.json e preencha seus dados "
            "(veja o README.md desta pasta)."
        )
    try:
        bruto = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"config.json tem um erro de formatação: {e}")
    cfg = {**PADROES, **bruto}
    if not cfg.get("key"):
        sys.exit("Preencha o campo 'key' em config.json com sua chave de API gratuita (Gemini ou Groq).")
    if cfg.get("provider") not in ("gemini", "groq"):
        sys.exit("O campo 'provider' em config.json deve ser 'gemini' ou 'groq'.")
    return cfg
