"""Sincronização de memória: mesma base Supabase e mesmas tabelas do app de navegador
(index.html), para o celular e o PC compartilharem a mesma conversa e os mesmos fatos
guardados via o "código de sincronização" (`space`). Sem `space` configurado, cai para
arquivos JSON locais em jarvis-pc/estado/."""
import json
from pathlib import Path

import requests

# Mesma URL e mesma chave anônima pública já usadas em index.html — é intencional, é assim
# que o app do navegador e o do PC acabam compartilhando a mesma base.
SUPABASE_URL = "https://swszibuxhctnfzfnwukk.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN3c3ppYnV4aGN0"
    "bmZ6Zm53dWtrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAzMDkxMTksImV4cCI6MjEwNTg4NTExOX0."
    "HR_g968OiuftBuC6Dth1yIN1yxO2hzmjzcnge2fGJ9w"
)

PASTA_ESTADO = Path(__file__).resolve().parent.parent / "estado"
HISTORICO_LOCAL = PASTA_ESTADO / "historico.json"
FATOS_LOCAL = PASTA_ESTADO / "fatos.json"

LEMBRAR_FATO_DECL = {
    "name": "lembrar_fato",
    "description": "Guarda para sempre um fato pessoal e duradouro sobre o usuário: nomes de pessoas próximas, preferências, projetos, decisões. Chame sempre que algo assim for dito.",
    "parameters": {
        "type": "object",
        "properties": {"fato": {"type": "string", "description": "O fato em uma frase curta, objetiva e em terceira pessoa. Ex: \"Tem uma loja online chamada Lumora.\""}},
        "required": ["fato"],
    },
}


def cloud_ready(cfg: dict) -> bool:
    return bool(cfg.get("space"))


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def _sb(path: str, method: str = "GET", params: dict = None, **kwargs) -> requests.Response:
    r = requests.request(method, f"{SUPABASE_URL}/rest/v1/{path}", headers=_headers(), params=params, timeout=15, **kwargs)
    r.raise_for_status()
    return r


def _carregar_local(caminho: Path, padrao):
    if caminho.exists():
        try:
            return json.loads(caminho.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return padrao
    return padrao


def _salvar_local(caminho: Path, dados):
    PASTA_ESTADO.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_historico(cfg: dict) -> list:
    if not cloud_ready(cfg):
        return _carregar_local(HISTORICO_LOCAL, [])
    try:
        r = _sb("jarvis_messages", params={
            "space": f"eq.{cfg['space']}", "select": "role,content,created_at",
            "order": "created_at.asc", "limit": "300",
        })
        return [{"role": x["role"], "text": x["content"]} for x in r.json()]
    except requests.RequestException as e:
        print(f"[aviso] não consegui buscar o histórico na nuvem agora: {e}. Usando histórico local.")
        return _carregar_local(HISTORICO_LOCAL, [])


def carregar_fatos(cfg: dict) -> list:
    if not cloud_ready(cfg):
        return _carregar_local(FATOS_LOCAL, [])
    try:
        r = _sb("jarvis_facts", params={
            "space": f"eq.{cfg['space']}", "select": "fact",
            "order": "created_at.asc", "limit": "300",
        })
        return [x["fact"] for x in r.json()]
    except requests.RequestException as e:
        print(f"[aviso] não consegui buscar os fatos guardados na nuvem agora: {e}. Usando cache local.")
        return _carregar_local(FATOS_LOCAL, [])


def salvar_mensagem(cfg: dict, historico_completo: list, role: str, texto: str):
    """`historico_completo` já deve incluir esta mensagem — usado para o cache local."""
    if cloud_ready(cfg):
        try:
            _sb("jarvis_messages", method="POST", json={"space": cfg["space"], "role": role, "content": texto})
        except requests.RequestException as e:
            print(f"[aviso] não sincronizou com a nuvem: {e}")
    else:
        _salvar_local(HISTORICO_LOCAL, historico_completo[-200:])


def lembrar_fato(args: dict, fatos: list, cfg: dict) -> dict:
    fato = (args.get("fato") or "").strip()
    if not fato:
        return {"result": {"erro": "Fato vazio"}}
    fatos.append(fato)
    if cloud_ready(cfg):
        try:
            _sb("jarvis_facts", method="POST", json={"space": cfg["space"], "fact": fato})
        except requests.RequestException as e:
            print(f"[aviso] fato não sincronizou com a nuvem: {e}")
    else:
        _salvar_local(FATOS_LOCAL, fatos)
    return {"result": {"ok": True}}


def apagar_tudo(cfg: dict):
    if not cloud_ready(cfg):
        raise ValueError("Nenhum código de sincronização configurado.")
    space = cfg["space"]
    _sb("jarvis_messages", method="DELETE", params={"space": f"eq.{space}"})
    _sb("jarvis_facts", method="DELETE", params={"space": f"eq.{space}"})
