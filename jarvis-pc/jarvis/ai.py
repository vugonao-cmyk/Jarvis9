"""Chamadas aos provedores de IA (Gemini/Groq), com troca automática de modelo e o
loop de function-calling do Gemini. Portado da lógica de index.html (askAI/callGemini/callGroq)."""
import re
import time

import requests

from .prompt import system_prompt

DEFAULT_MODELS = {"gemini": "gemini-flash-lite-latest", "groq": "llama-3.3-70b-versatile"}
FALLBACK_MODELS = {
    "gemini": ["gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-flash-latest", "gemini-3.5-flash-lite"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
}

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ApiError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.status = status


_OVERLOAD_STATUSES = {429, 500, 502, 503, 504}
_OVERLOAD_RE = re.compile(r"overload|high demand|unavailable|quota|exhausted|rate limit", re.I)
_GONE_RE = re.compile(r"no longer available|not found|is not supported for generateContent", re.I)


def is_overload(e: ApiError) -> bool:
    return e.status in _OVERLOAD_STATUSES or bool(_OVERLOAD_RE.search(str(e)))


def is_gone(e: ApiError) -> bool:
    return e.status == 404 or bool(_GONE_RE.search(str(e)))


# Pesquisa Google recusada (cota do plano grátis): pula por um tempo para não perder tempo.
# Reinicia a cada execução do processo (mais simples que persistir em disco para um uso pessoal).
_search_broken_until = 0.0


def _is_search_broken() -> bool:
    return time.time() < _search_broken_until


def _mark_search_broken():
    global _search_broken_until
    _search_broken_until = time.time() + 12 * 3600


def needs_tools(text: str, cfg: dict) -> bool:
    """Detecta pedidos que precisam das ferramentas de function-calling (música, abrir programa, ler
    arquivo), já que o Gemini não combina pesquisa do Google com ferramentas customizadas na mesma chamada."""
    if not text:
        return False
    t = text.lower()
    if re.search(r"\b(toca|tocar|toque|coloca|colocar|bota|p[oõ]e|escuta|escutar|ouvir|ouve)\w*\b.{0,40}\b(m[uú]sica|som|faixa|playlist)\b", t):
        return True
    if re.search(r"\bm[uú]sica\b.{0,40}\b(toca|tocar|toque|coloca|colocar|bota|ouvir|ouve)\w*\b", t):
        return True
    if re.search(r"\b(abre|abrir|abra|executa|executar|inicia|iniciar)\b", t):
        for apelido in (cfg.get("programas_permitidos") or {}):
            if apelido.lower() in t:
                return True
    if re.search(r"\b(l[eê]|ler|leia)\b.{0,30}\b(arquivo|documento|pdf|word)\b", t):
        return True
    return False


def gemini_request(cfg: dict, model: str, body: dict) -> dict:
    headers = {"Content-Type": "application/json", "x-goog-api-key": cfg["key"]}
    r = requests.post(GEMINI_URL.format(model=model), headers=headers, json=body, timeout=30)
    try:
        data = r.json()
    except ValueError:
        data = {}
    if not r.ok:
        raise ApiError((data.get("error") or {}).get("message") or f"Erro {r.status_code}", r.status_code)
    return data


def call_gemini(cfg: dict, model: str, recent: list, with_search: bool, decls: list, impls: dict, fatos: list) -> dict:
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["text"]}]} for m in recent]
    base = {
        "systemInstruction": {"parts": [{"text": system_prompt(cfg, with_search, fatos)}]},
        "generationConfig": {"temperature": 0.7},
        "tools": [{"google_search": {}}] if with_search else [{"functionDeclarations": decls}],
    }
    sources, players = [], []
    for _ in range(4):
        data = gemini_request(cfg, model, {**base, "contents": contents})
        cand = (data.get("candidates") or [{}])[0]
        parts = ((cand.get("content") or {}).get("parts")) or []
        calls = [p for p in parts if p.get("functionCall")]
        if calls:
            contents.append(cand["content"])
            respostas = []
            for p in calls:
                fc = p["functionCall"]
                nome, args = fc["name"], (fc.get("args") or {})
                try:
                    r = impls[nome](args)
                    if r.get("source"):
                        sources.append(r["source"])
                    if r.get("player"):
                        players.append(r["player"])
                    out = {"result": r.get("result")}
                except Exception as e:
                    out = {"erro": f"Falha ao consultar: {e}"}
                respostas.append({"functionResponse": {"name": nome, "response": out}})
            contents.append({"role": "user", "parts": respostas})
            continue
        texto = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if not texto:
            raise ApiError(f"A IA não retornou texto ({cand.get('finishReason', 'sem motivo')}).", 0)
        for c in ((cand.get("groundingMetadata") or {}).get("groundingChunks") or []):
            web = c.get("web")
            if web and web.get("uri") and not any(s.get("title") == web.get("title") for s in sources):
                sources.append(web)
        return {"text": texto, "sources": sources, "players": players}
    raise ApiError("A IA ficou consultando ferramentas sem responder.", 0)


def call_groq(cfg: dict, model: str, recent: list, fatos: list) -> dict:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg['key']}"}
    mensagens = [{"role": "system", "content": system_prompt(cfg, False, fatos)}]
    mensagens += [{"role": m["role"], "content": m["text"]} for m in recent]
    r = requests.post(GROQ_URL, headers=headers, json={"model": model, "temperature": 0.7, "messages": mensagens}, timeout=30)
    try:
        data = r.json()
    except ValueError:
        data = {}
    if not r.ok:
        raise ApiError((data.get("error") or {}).get("message") or f"Erro {r.status_code}", r.status_code)
    texto = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
    return {"text": texto, "sources": [], "players": []}


def ask_ai(cfg: dict, recent: list, fatos: list, tool_decls: list, tools_impl: dict) -> dict:
    ultimo_usuario = next((m for m in reversed(recent) if m["role"] == "user"), None)
    forcar_ferramentas = bool(ultimo_usuario) and needs_tools(ultimo_usuario["text"], cfg)
    primeiro = cfg.get("model") or DEFAULT_MODELS[cfg["provider"]]
    modelos = [primeiro] + [m for m in FALLBACK_MODELS[cfg["provider"]] if m != primeiro]
    ultimo_erro = None
    for model in modelos:
        try:
            if cfg["provider"] == "groq":
                return call_groq(cfg, model, recent, fatos)
            if cfg.get("busca") and not _is_search_broken() and not forcar_ferramentas:
                try:
                    return call_gemini(cfg, model, recent, True, None, None, fatos)
                except ApiError as e:
                    if e.status in (429, 400):
                        _mark_search_broken()
                    else:
                        raise
            return call_gemini(cfg, model, recent, False, tool_decls, tools_impl, fatos)
        except ApiError as e:
            ultimo_erro = e
            if is_overload(e) or is_gone(e):
                continue
            raise
    raise ultimo_erro or ApiError("Nenhum modelo respondeu.", 0)
