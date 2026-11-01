"""Carrossel de notícia do dia (ENEM / SSA / FPS) na identidade do MAPA: slides 1080x1350 em JPG.
Uso: noticia_post.py spec.json pasta_saida   (spec: {"slides":[...], "fonte":"..."}; tipos de slide: capa, lista, cta)
- capa:  {"tipo":"capa","selo":"NOTÍCIA DO DIA","titulo":"...","sub":"..."}
- lista: {"tipo":"lista","titulo":"...","itens":["...","..."],"nota":"..."}   (itens com "**" no começo ganham destaque)
- cta:   {"tipo":"cta"}  (inscrições da Mentoria MAPA 2027 abertas · link na bio)"""
import json, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
M = os.path.dirname(os.path.abspath(__file__))
NAVY = (0, 22, 46); BLUE = (0, 128, 255); WHITE = (255, 255, 255); YEL = (255, 210, 0); SOFT = (170, 190, 225)
FONT = "/usr/share/fonts/opentype/inter/"
def F(nome, s):
    p = FONT + nome
    return ImageFont.truetype(p if os.path.exists(p) else FONT + "Inter-ExtraBold.otf", s)
XB = lambda s: F("Inter-ExtraBold.otf", s); BK = lambda s: F("Inter-Black.otf", s); SB = lambda s: F("Inter-SemiBold.otf", s)
W, H = 1080, 1350; PAD = 90

def quebra(d, t, f, larg):
    linhas, cur = [], ""
    for p in t.split():
        x = (cur + " " + p).strip()
        if d.textlength(x, font=f) <= larg: cur = x
        else: linhas.append(cur); cur = p
    if cur: linhas.append(cur)
    return linhas

def base(i, n):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 14), fill=BLUE)
    lg = Image.open(M + "/marca/logo_branca.png").convert("RGBA"); lw = 230; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    im.paste(lg, (PAD, 70), lg)
    f = SB(30); t = f"{i}/{n}"; d.text((W - PAD - d.textlength(t, font=f), 78), t, font=f, fill=SOFT)
    d.text((PAD, H - 90), "@omapamentoria", font=SB(30), fill=SOFT)
    return im, d

def capa(s, i, n):
    im, d = base(i, n); y = 300
    f = XB(32); t = s.get("selo", "NOTÍCIA DO DIA"); w = d.textlength(t, font=f) + 60
    d.rounded_rectangle((PAD, y, PAD + w, y + 64), 32, fill=YEL); d.text((PAD + 30, y + 13), t, font=f, fill=NAVY); y += 120
    for ln in quebra(d, s["titulo"], BK(92), W - 2 * PAD): d.text((PAD, y), ln, font=BK(92), fill=WHITE); y += 104
    y += 30
    for ln in quebra(d, s.get("sub", ""), SB(40), W - 2 * PAD): d.text((PAD, y), ln, font=SB(40), fill=SOFT); y += 54
    if s.get("numero"):  # contagem regressiva em destaque (ex.: "7" + "DIAS PARA O ENEM")
        y += 50; fn = BK(260); d.text((PAD - 8, y - 40), s["numero"], font=fn, fill=YEL)
        x = PAD + d.textlength(s["numero"], font=fn) + 30
        for k, ln in enumerate(quebra(d, s.get("numero_txt", ""), XB(52), W - x - PAD)): d.text((x, y + 40 + k * 62), ln, font=XB(52), fill=WHITE)
    d.text((PAD, H - 170), "Arrasta para o lado  →", font=XB(34), fill=BLUE)
    return im

def lista(s, i, n):
    im, d = base(i, n); y = 230
    for ln in quebra(d, s["titulo"], BK(64), W - 2 * PAD): d.text((PAD, y), ln, font=BK(64), fill=WHITE); y += 76
    y += 40
    for it in s["itens"]:
        dest = it.startswith("**"); it = it.lstrip("*").strip(); f = XB(40) if dest else SB(38)
        ls = quebra(d, it, f, W - 2 * PAD - 60)
        d.ellipse((PAD, y + 14, PAD + 22, y + 36), fill=YEL if dest else BLUE)
        for ln in ls: d.text((PAD + 50, y), ln, font=f, fill=WHITE); y += 52
        y += 26
    if s.get("nota"):
        y = max(y + 10, H - 250)
        for ln in quebra(d, s["nota"], SB(30), W - 2 * PAD): d.text((PAD, y), ln, font=SB(30), fill=SOFT); y += 40
    return im

def cta(s, i, n):
    im, d = base(i, n); y = 360
    def ct(t, f, fill=WHITE):
        nonlocal y; d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)
    ct("MENTORIA", XB(64)); y += 80; ct("MAPA 2027", BK(130)); y += 210
    f = XB(52); t = "INSCRIÇÕES ABERTAS"; w = d.textlength(t, font=f) + 100; x = (W - w) / 2
    d.rounded_rectangle((x, y, x + w, y + 104), 52, fill=BLUE); d.text((x + 50, y + 18), t, font=f, fill=WHITE); y += 190
    f = XB(60); t = "LINK NA BIO"; w = d.textlength(t, font=f) + 130; x = (W - w) / 2
    d.rounded_rectangle((x, y, x + w, y + 124), 62, fill=WHITE); d.text((x + 65, y + 22), t, font=f, fill=NAVY); y += 200
    ct("Quem sabe onde quer chegar, segue o MAPA.", SB(36), SOFT)
    return im

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    sl = spec["slides"]; n = len(sl); arqs = []
    for i, s in enumerate(sl, 1):
        im = {"capa": capa, "lista": lista, "cta": cta}[s["tipo"]](s, i, n)
        p = f"{out}/slide_{i:02d}.jpg"; im.save(p, quality=92); arqs.append(p)
    print("\n".join(arqs))
