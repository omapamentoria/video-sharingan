"""Publica UM post do Calendário de Posts MAPA no Instagram pela API oficial (Instagram API com login do Instagram).
Uso: python3 publicar.py post.json   -> imprime JSON {"ok": true, "media_id": ..., "permalink": ...} ou {"ok": false, "erro": ...}
post.json: {"tipo": "reel"|"carrossel", "legenda": "...", "midia": [urls públicas], "video_local": "caminho opcional do .mp4"}
Variável de ambiente: IG_ACCESS_TOKEN (opcionais: IG_USER_ID e IG_API_HOST; se faltarem, são descobertos pelo token).
- Carrossel: cada imagem precisa de URL pública (JPG); até 10 imagens.
- Reel: a Meta baixa o vídeo pelo link público (midia[0]); se falhar, tenta o upload direto (resumível)."""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

TOKEN = os.environ.get("IG_ACCESS_TOKEN", ""); IG = os.environ.get("IG_USER_ID", "")
HOST = "https://" + os.environ.get("IG_API_HOST", "graph.instagram.com") + "/v21.0"

def descobre():
    """Acha o host certo para o token (login do Instagram -> graph.instagram.com; usuário do sistema / login do
    Facebook -> graph.facebook.com) e, se IG_USER_ID não estiver no ambiente, o ID da conta do Instagram."""
    global HOST, IG
    for h in ([HOST] if os.environ.get("IG_API_HOST") else ["https://graph.instagram.com/v21.0", "https://graph.facebook.com/v21.0"]):
        try:
            if "graph.instagram.com" in h:
                me = json.loads(urllib.request.urlopen(f"{h}/me?fields=user_id,username&access_token={TOKEN}", timeout=60).read())
                HOST = h; IG = IG or str(me.get("user_id") or me.get("id")); return
            r = json.loads(urllib.request.urlopen(f"{h}/me/accounts?fields=instagram_business_account&access_token={TOKEN}", timeout=60).read())
            ids = [p["instagram_business_account"]["id"] for p in r.get("data", []) if p.get("instagram_business_account")]
            if not ids:  # usuário do sistema: contas do Instagram atribuídas direto ao portfólio
                me = json.loads(urllib.request.urlopen(f"{h}/me?fields=id&access_token={TOKEN}", timeout=60).read())
                for ed in ("instagram_accounts", "owned_instagram_accounts"):
                    try:
                        r = json.loads(urllib.request.urlopen(f"{h}/me/{ed}?fields=id,username&access_token={TOKEN}", timeout=60).read())
                        ids = [a["id"] for a in r.get("data", [])]
                        if ids: break
                    except urllib.error.HTTPError: pass
            HOST = h; IG = IG or (ids[0] if ids else ""); return
        except urllib.error.HTTPError: continue

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
    # Primeiro pelo link público (a Meta baixa o vídeo da branch instagram-midia). O upload direto dos bytes
    # (resumable) falhou com o token de usuário do sistema ("400 ProcessingFailedError") e fica só como reserva.
    if p.get("midia") and not p.get("video_local"):
        try:
            c = req("POST", f"{HOST}/{IG}/media", {"media_type": "REELS", "video_url": p["midia"][0], "caption": p["legenda"], "share_to_feed": "true"})
            return publica(c["id"])
        except RuntimeError as e:
            print(json.dumps({"aviso": f"video_url falhou, tentando upload direto: {str(e)[:300]}"}), file=sys.stderr)
    c = req("POST", f"{HOST}/{IG}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": p["legenda"], "share_to_feed": "true"})
    if p.get("video_local"): corpo = open(p["video_local"], "rb").read()
    else: corpo = urllib.request.urlopen(p["midia"][0], timeout=300).read()
    req("POST", c["uri"], raw=corpo, headers={"Authorization": f"OAuth {TOKEN}", "offset": "0", "file_size": str(len(corpo))})
    return publica(c["id"])

def ja_publicado(legenda, horas=36):
    """Procura nos posts recentes da conta um com a mesma legenda (protege contra post duplicado quando a Meta
    publicou mas a resposta se perdeu). Devolve (media_id, permalink) ou None."""
    alvo = " ".join((legenda or "").split())[:200]
    r = get(f"{IG}/media", fields="id,caption,permalink,timestamp", limit=25)
    for m in r.get("data", []):
        if " ".join((m.get("caption") or "").split())[:200] == alvo:
            ts = time.mktime(time.strptime(m["timestamp"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            if time.time() - ts < horas * 3600: return m["id"], m.get("permalink")
    return None

def confere(media_id):
    """Confirma que o post existe na conta. Devolve o permalink ou None."""
    try: return get(media_id, fields="id,permalink").get("permalink")
    except RuntimeError: return None

TENTATIVAS, ESPERAS = 3, (60, 180)

if __name__ == "__main__":
    # Uso extra: publicar.py --confere <media_id>  -> {"ok": true/false, "permalink": ...}
    if sys.argv[1] == "--confere":
        descobre(); link = confere(sys.argv[2]); print(json.dumps({"ok": bool(link), "permalink": link})); sys.exit(0 if link else 1)
    p = json.load(open(sys.argv[1])); erro = ""
    if not TOKEN: print(json.dumps({"ok": False, "erro": "falta IG_ACCESS_TOKEN no ambiente"})); sys.exit(1)
    for t in range(TENTATIVAS):
        try:
            descobre()
            if not IG: raise RuntimeError("não achei a conta do Instagram ligada a este token")
            ja = ja_publicado(p["legenda"])
            if ja:
                print(json.dumps({"ok": True, "media_id": ja[0], "permalink": ja[1], "ja_estava_publicado": True})); sys.exit(0)
            mid, link = (reel if p["tipo"] == "reel" else carrossel)(p)
            print(json.dumps({"ok": True, "media_id": mid, "permalink": link or confere(mid), "tentativas": t + 1})); sys.exit(0)
        except SystemExit: raise
        except Exception as e:
            erro = str(e)[:600]
            print(json.dumps({"tentativa": t + 1, "erro": erro}), file=sys.stderr)
            if t < TENTATIVAS - 1: time.sleep(ESPERAS[t])
    print(json.dumps({"ok": False, "erro": erro, "tentativas": TENTATIVAS})); sys.exit(1)
