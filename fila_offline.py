"""Modo econômico: publica os posts da fila fixa (fila_ate_sexta.json) cujo horário já chegou, sem ler o calendário.
Nunca duplica: antes de cada post, procura na conta um post com a mesma legenda. O calendário é sincronizado depois
pela rodada de VERIFICAÇÃO (verificar.py marca como publicado o que já está na conta).
Uso: IG_ACCESS_TOKEN=... python3 fila_offline.py   -> uma linha por post (publicado / já estava / aguardando / erro)"""
import json, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
import publicar as P
agora = datetime.now(timezone(timedelta(hours=-3)))
P.descobre()
for p in json.load(open("fila_ate_sexta.json"))["posts"]:
    q = datetime.fromisoformat(p["quando"])
    if q > agora + timedelta(minutes=5): print(p["id"], "aguardando", q.strftime("%d/%m %H:%M")); continue
    if agora - q > timedelta(hours=12): print(p["id"], "fora da janela (mais de 12 h)"); continue
    ja = P.ja_publicado(p["legenda"], horas=48)
    if ja: print(p["id"], "já estava publicado", ja[1]); continue
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(p, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, "publicar.py", f.name], capture_output=True, text=True)
    print(p["id"], (r.stdout.strip().splitlines() or ["sem saída"])[-1])
