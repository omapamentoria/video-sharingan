"""Revisor dos posts do Calendário de Posts MAPA. Confere cada post e devolve os problemas encontrados,
com a correção sugerida quando ela é automática.
Uso: python3 revisar.py posts.json   (lista de posts como estão no calendário, cada um com "id")
Saída: JSON [{"id", "problemas": [...], "legenda_corrigida": "..." (só quando há correção automática)}]
Checagens:
- mídia: links públicos respondendo 200; carrossel com 2 a 10 imagens JPG 1080x1350/1080x1080; Reel em MP4 de 3 s a 15 min
- legenda: até 2.200 caracteres, até 30 hashtags, CTA de inscrições + link na bio, nada de live/31 de outubro,
  "Black Friday" só até 30/11, sem datas passadas tratadas como futuras ("amanhã", "hoje") fora do dia do post
- horário: ISO com -03:00 e dentro dos horários do plano (desde 13/11: 12h notícia, 15h Reel da agência,
  19h conteúdo do roteiro/carrossel; nos dias de prova o "Boa prova" vai às 12h e a notícia às 15h)"""
import io, json, re, subprocess, sys, urllib.request
from datetime import datetime

def baixa(u, n=None):
    r = urllib.request.Request(u, headers={"Range": f"bytes=0-{n - 1}"} if n else {})
    with urllib.request.urlopen(r, timeout=60) as resp: return resp.status, resp.read()

def confere_midia(p, prob):
    m = p.get("midia") or []
    if p.get("tipo") == "carrossel":
        if not 2 <= len(m) <= 10: prob.append(f"carrossel com {len(m)} imagens (precisa de 2 a 10)")
        try: from PIL import Image
        except ImportError: Image = None
        for u in m:
            try:
                st, b = baixa(u)
                if st not in (200, 206): prob.append(f"imagem fora do ar ({st}): {u}"); continue
                if Image:
                    im = Image.open(io.BytesIO(b))
                    if im.format != "JPEG" or im.size not in ((1080, 1350), (1080, 1080)): prob.append(f"imagem {im.format} {im.size[0]}x{im.size[1]} (esperado JPG 1080x1350 ou 1080x1080): {u}")
            except Exception as e: prob.append(f"imagem inacessível: {u} ({e})")
    else:
        if not m: prob.append("Reel sem vídeo"); return
        try:
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", m[0]], capture_output=True, text=True, timeout=120).stdout.strip() or 0)
            if not 3 <= d <= 900: prob.append(f"duração do Reel fora do permitido: {d:.1f}s")
        except Exception as e: prob.append(f"vídeo inacessível: {m[0]} ({e})")

def confere_legenda(p, prob):
    L = p.get("legenda") or ""; nova = L
    q = datetime.fromisoformat(p["quando"]) if p.get("quando") else None
    if len(L) > 2200: prob.append(f"legenda com {len(L)} caracteres (máx. 2.200)")
    if len(re.findall(r"#\w+", L)) > 30: prob.append("mais de 30 hashtags")
    if not re.search(r"link (na|da) bio", L, re.I): prob.append("legenda sem 'link na bio'")
    if not re.search(r"inscri[çc][õo]es", L, re.I): prob.append("legenda sem o CTA de inscrições")
    if re.search(r"\blive\b|ao vivo|31/10|31 de outubro", L, re.I): prob.append("legenda menciona a live (já passou)")
    if q and q.date() > datetime(2026, 11, 30).date() and re.search(r"black friday", L, re.I):
        prob.append("menciona Black Friday depois de 30/11")
        nova = "\n".join(l for l in nova.split("\n") if not re.search(r"black friday", l, re.I))
    if q and p.get("origem") != "noticias" and re.search(r"\b(hoje|amanhã)\b", L, re.I):
        prob.append("usa 'hoje'/'amanhã': conferir se faz sentido na data do post")
    return nova if nova != L else None

# Dias de prova: o carrossel de "Boa prova" sai às 12h (antes do portão do ENEM, que fecha às 13h, e antes do
# SSA 2, que é à tarde) e a notícia vai para as 15h. Datas conferidas no edital do ENEM 2026 e no site da UPE (SSA 2027).
DIAS_DE_PROVA = {"2026-11-08": "ENEM", "2026-11-15": "ENEM", "2026-12-06": "SSA", "2026-12-13": "SSA"}

def horario_plano(p, dia):
    # Grade definida pelo dono em 13/11/2026: notícia 12h (almoço), Reel da agência 15h, conteúdo do roteiro
    # (origem "roteiro") e carrosséis 19h (maior alcance). Dia de prova: "Boa prova" 12h e notícia 15h.
    prova = dia in DIAS_DE_PROVA
    if p.get("origem") == "noticias": return 15 if prova else 12
    if p.get("origem") == "roteiro": return 19
    if str(p.get("id", "")).endswith("-12h"): return 12  # Reel no lugar da notícia (dia sem notícia forte)
    return {"reel": 15, "carrossel": 12 if prova else 19}.get(p.get("tipo"))

def confere_horario(p, prob):
    try: q = datetime.fromisoformat(p["quando"])
    except Exception: prob.append(f"data/hora inválida: {p.get('quando')}"); return
    if q.utcoffset() is None or q.utcoffset().total_seconds() != -3 * 3600: prob.append("horário sem fuso -03:00")
    esp = horario_plano(p, q.date().isoformat())
    if esp and q.hour != esp: prob.append(f"{p.get('tipo')} às {q:%H:%M} (plano: {esp}h{' — dia de prova' if q.date().isoformat() in DIAS_DE_PROVA else ''})")
    if re.search(r"boa prova", p.get("legenda") or "", re.I) and re.search(r"\bhoje\b", p.get("legenda") or "", re.I) and q.hour >= 13:
        prob.append(f"'Boa prova hoje' às {q:%H:%M}: a prova já começou ou acabou; publique às 12h")

if __name__ == "__main__":
    out = []
    for p in json.load(open(sys.argv[1])):
        prob = []; confere_midia(p, prob); nova = confere_legenda(p, prob); confere_horario(p, prob)
        if prob: out.append({"id": p.get("id"), "problemas": prob, **({"legenda_corrigida": nova} if nova else {})})
    print(json.dumps(out, ensure_ascii=False, indent=1))
