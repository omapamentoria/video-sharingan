"""Publica UM post do Calendário de Posts MAPA no Instagram pela API oficial (Instagram API com login do Instagram).
Uso: python3 publicar.py post.json   -> imprime JSON {"ok": true, "media_id": ..., "permalink": ...} ou {"ok": false, "erro": ...}
post.json: {"tipo": "reel"|"carrossel", "legenda": "...", "midia": [urls públicas], "video_local": "caminho opcional do .mp4"}
Variáveis de ambiente: IG_ACCESS_TOKEN, IG_USER_ID (e opcional IG_API_HOST, padrão graph.instagram.com).
- Carrossel: cada imagem precisa de URL pública (JPG); até 10 imagens.
- Reel: o vídeo é enviado direto para a Meta (upload resumível), então não precisa de URL pública."""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

TOKEN = os.environ.get("IG_ACCESS_TOKEN", ""); IG = os.environ.get("IG_USER_ID", "")
HOST = "https://" + os.environ.get("IG_API_HOST", "graph.instagram.com") + "/v21.0"

def req(method, url, data=None, headers=None, raw=None):
    if data is not None: raw = urllib.parse.urlencode({**data, "access_token": TOKEN}).encode()
    r = urllib.request.Request(url, data=raw, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=300) as resp: return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode(errors='replace')[:500]}")

def get(path, **q): return req("GET", f"{HOST}/{path}?" + urllib.parse.urlencode({**q, "access_token": TOKEN}))

def espera(cid, limite=600):
    t0 = time.time()
    while time.time() - t0 < limite:
        st = get(cid, fields="status_code,status").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"container {cid}: {st}")
        time.sleep(8)
    raise RuntimeError(f"container {cid}: tempo esgotado processando")

def publica(cid):
    espera(cid); m = req("POST", f"{HOST}/{IG}/media_publish", {"creation_id": cid})["id"]
    return m, get(m, fields="permalink").get("permalink")

def carrossel(p):
    imgs = p["midia"][:10]
    if len(imgs) < 2: raise RuntimeError("carrossel precisa de 2 a 10 imagens")
    filhos = [req("POST", f"{HOST}/{IG}/media", {"image_url": u, "is_carousel_item": "true"})["id"] for u in imgs]
    for f in filhos: espera(f)
    cid = req("POST", f"{HOST}/{IG}/media", {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": p["legenda"]})["id"]
    return publica(cid)

def reel(p):
    c = req("POST", f"{HOST}/{IG}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": p["legenda"], "share_to_feed": "true"})
    if p.get("video_local"): corpo = open(p["video_local"], "rb").read()
    else: corpo = urllib.request.urlopen(p["midia"][0], timeout=300).read()
    req("POST", c["uri"], raw=corpo, headers={"Authorization": f"OAuth {TOKEN}", "offset": "0", "file_size": str(len(corpo))})
    return publica(c["id"])

if __name__ == "__main__":
    p = json.load(open(sys.argv[1]))
    try:
        if not TOKEN or not IG: raise RuntimeError("faltam IG_ACCESS_TOKEN / IG_USER_ID no ambiente")
        mid, link = (reel if p["tipo"] == "reel" else carrossel)(p)
        print(json.dumps({"ok": True, "media_id": mid, "permalink": link}))
    except Exception as e:
        print(json.dumps({"ok": False, "erro": str(e)[:600]})); sys.exit(1)
