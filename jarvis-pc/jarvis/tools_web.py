"""Ferramentas gratuitas e sem chave, portadas de index.html: clima, Wikipédia, cotação e música livre."""
import random
import re
import shutil
import subprocess
import webbrowser
from urllib.parse import quote

import requests

WMO = {
    0: "céu limpo", 1: "predominantemente limpo", 2: "parcialmente nublado", 3: "nublado",
    45: "neblina", 48: "neblina com geada", 51: "garoa fraca", 53: "garoa", 55: "garoa forte",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte", 66: "chuva congelante", 67: "chuva congelante forte",
    71: "neve fraca", 73: "neve", 75: "neve forte", 80: "pancadas de chuva fracas", 81: "pancadas de chuva",
    82: "pancadas de chuva fortes", 95: "trovoadas", 96: "trovoadas com granizo", 99: "trovoadas fortes com granizo",
}

GENEROS = {
    "pop": "pop OR dance OR synthpop", "jazz": "jazz OR swing OR bossa", "reggae": "reggae OR dub OR ska",
    "rap": 'rap OR "hip hop" OR hiphop', "hip hop": '"hip hop" OR rap OR hiphop', "rock": "rock OR punk OR indie",
    "eletronica": "electronic OR techno OR house OR edm", "eletrônica": "electronic OR techno OR house OR edm",
    "electronic": "electronic OR techno OR house OR edm", "lofi": 'lofi OR "lo-fi" OR chillhop',
    "funk": "funk OR soul", "classica": "classical OR orchestral", "clássica": "classical OR orchestral",
    "mpb": "mpb OR bossa OR brazilian", "sertanejo": "sertanejo OR brazilian", "ambient": "ambient OR chillout",
}

DECLS = [
    {"name": "clima", "description": "Clima atual e previsão de 3 dias de uma cidade (temperatura, chuva, vento).",
     "parameters": {"type": "object", "properties": {"cidade": {"type": "string", "description": "Nome da cidade, ex: São Paulo"}}, "required": ["cidade"]}},
    {"name": "wikipedia", "description": "Resumo da Wikipédia em português sobre uma pessoa, lugar, empresa, conceito ou fato histórico.",
     "parameters": {"type": "object", "properties": {"termo": {"type": "string", "description": "O que pesquisar"}}, "required": ["termo"]}},
    {"name": "cotacao", "description": "Cotação atual de moedas e cripto em relação ao real, ex: USD, EUR, BTC.",
     "parameters": {"type": "object", "properties": {"moedas": {"type": "string", "description": "Códigos separados por vírgula, ex: USD,EUR,BTC"}}, "required": ["moedas"]}},
    {"name": "tocar_musica", "description": "Toca uma música gratuita e livre de direitos autorais, do acervo do Internet Archive.",
     "parameters": {"type": "object", "properties": {"busca": {"type": "string", "description": "Nome da música e/ou artista, ou um estilo (ex: lofi, jazz) se o pedido for genérico"}}, "required": ["busca"]}},
]


def _get_json(url: str) -> dict:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


def clima(args: dict) -> dict:
    cidade = args.get("cidade", "")
    g = _get_json(f"https://geocoding-api.open-meteo.com/v1/search?name={quote(cidade)}&count=1&language=pt")
    resultados = g.get("results") or []
    if not resultados:
        return {"result": {"erro": "Cidade não encontrada"}}
    loc = resultados[0]
    f = _get_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code&timezone=auto&forecast_days=3"
    )
    c = f["current"]
    dias = f["daily"]
    previsao = [
        {
            "dia": dias["time"][i],
            "min_c": dias["temperature_2m_min"][i],
            "max_c": dias["temperature_2m_max"][i],
            "chance_chuva_pct": dias["precipitation_probability_max"][i],
            "condicao": WMO.get(dias["weather_code"][i], dias["weather_code"][i]),
        }
        for i in range(len(dias["time"]))
    ]
    return {
        "source": {"uri": "https://open-meteo.com/", "title": "Open-Meteo"},
        "result": {
            "local": f"{loc['name']}, {loc.get('admin1', '')} {loc.get('country', '')}".strip(),
            "agora": {
                "temperatura_c": c["temperature_2m"], "sensacao_c": c["apparent_temperature"],
                "umidade_pct": c["relative_humidity_2m"], "chuva_mm": c["precipitation"],
                "vento_kmh": c["wind_speed_10m"], "condicao": WMO.get(c["weather_code"], c["weather_code"]),
                "horario_local": c["time"],
            },
            "previsao": previsao,
        },
    }


def wikipedia(args: dict) -> dict:
    termo = args.get("termo", "")
    s = _get_json(f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(termo)}&srlimit=1&format=json&origin=*")
    busca = ((s.get("query") or {}).get("search")) or []
    if not busca:
        return {"result": {"erro": "Nada encontrado"}}
    title = busca[0]["title"]
    p = _get_json(f"https://pt.wikipedia.org/api/rest_v1/page/summary/{quote(title)}")
    return {
        "source": {
            "uri": (p.get("content_urls") or {}).get("desktop", {}).get("page", "https://pt.wikipedia.org"),
            "title": "Wikipédia: " + title,
        },
        "result": {"titulo": title, "resumo": (p.get("extract") or "")[:1800]},
    }


def cotacao(args: dict) -> dict:
    moedas = str(args.get("moedas", "")).upper()
    codigos = [t for t in re.split(r"[^A-Z]+", moedas) if t][:5]
    pares = ",".join(c + "-BRL" for c in codigos)
    d = _get_json(f"https://economia.awesomeapi.com.br/json/last/{pares}")
    return {
        "source": {"uri": "https://economia.awesomeapi.com.br", "title": "AwesomeAPI (cotações)"},
        "result": [
            {"moeda": v["name"], "compra": v["bid"], "venda": v["ask"], "variacao_pct": v["pctChange"], "atualizado": v["create_date"]}
            for v in d.values()
        ],
    }


def _expandir_genero(termo: str) -> str:
    chave = termo.lower().strip()
    for k, v in GENEROS.items():
        if chave == k or k in chave:
            return v
    return termo


def _buscar_docs(q: str) -> list:
    url = "https://archive.org/advancedsearch.php?q=" + quote(q) + "&fl[]=identifier&rows=25&output=json&sort[]=" + quote("downloads desc")
    s = _get_json(url)
    return (s.get("response") or {}).get("docs") or []


def _pick_audio_file(identifier: str):
    meta = _get_json(f"https://archive.org/metadata/{identifier}")
    arquivos = meta.get("files") or []
    audio = next((f for f in arquivos if str(f.get("name", "")).lower().endswith("mp3") and "mp3" in str(f.get("format", "")).lower()), None)
    if not audio:
        audio = next((f for f in arquivos if str(f.get("name", "")).lower().endswith((".mp3", ".ogg"))), None)
    if not audio:
        return None
    bruto = (audio.get("title") or audio["name"].rsplit(".", 1)[0]).strip()
    return {
        "nome": bruto or identifier,
        "artista": (meta.get("metadata") or {}).get("creator") or (meta.get("metadata") or {}).get("title") or "Artista independente",
        "url": f"https://archive.org/download/{identifier}/{audio['name']}",
    }


def tocar_musica(args: dict) -> dict:
    termo_original = (args.get("busca") or "").strip() or "electronic"
    termo = _expandir_genero(termo_original)
    docs = []
    for q in (
        f"mediatype:audio AND collection:(netlabels OR opensource_audio OR etree) AND ({termo})",
        f"mediatype:audio AND ({termo})",
    ):
        try:
            docs = _buscar_docs(q)
        except requests.RequestException:
            docs = []
        if docs:
            break
    if not docs:
        return {"result": {"erro": "Nenhuma música livre encontrada para esse pedido"}}
    ordem = docs[:]
    random.shuffle(ordem)
    faixas = []
    for doc in ordem:
        if len(faixas) >= 8:
            break
        try:
            track = _pick_audio_file(doc["identifier"])
            if track:
                faixas.append(track)
        except requests.RequestException:
            continue
    if not faixas:
        return {"result": {"erro": "Não consegui carregar um arquivo de áudio para esse pedido"}}
    primeira, fila = faixas[0], faixas[1:]
    primeira["fila"] = fila
    return {
        "source": {"uri": "https://archive.org/details/" + docs[0].get("identifier", ""), "title": "Internet Archive: " + primeira["nome"]},
        "result": {"ok": True, "tocando": primeira["nome"], "artista": primeira["artista"], "mais_na_fila": len(fila)},
        "player": primeira,
    }


def tocar(track: dict, cfg: dict):
    """Toca a faixa escolhida por tocar_musica: um player local se houver, senão o navegador."""
    url = track["url"]
    preferencia = cfg.get("musica_player", "auto")
    if preferencia == "navegador":
        webbrowser.open(url)
        return
    if preferencia not in ("auto", ""):
        try:
            subprocess.Popen([preferencia, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            pass
    for player, extra in (("mpv", []), ("ffplay", ["-nodisp", "-autoexit"]), ("vlc", [])):
        caminho = shutil.which(player)
        if caminho:
            try:
                subprocess.Popen([caminho, *extra, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except OSError:
                continue
    webbrowser.open(url)


IMPLS = {"clima": clima, "wikipedia": wikipedia, "cotacao": cotacao, "tocar_musica": tocar_musica}
