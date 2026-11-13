"""Carrossel de notícia do dia (ENEM / SSA / FPS): mesmo sistema visual dos carrosséis do MAPA, em versão escura,
com a marca própria da notícia (selo "PLANTÃO MAPA", carimbo de data e fonte, faixa de manchete no rodapé).
Uso: noticia_post.py spec.json pasta_saida
spec: {"fonte":"Inep, 10/11/2026", "data":"11/11", "tema":"ENEM 2026", "slides":[...]}; tipos de slide:
- capa:  {"tipo":"capa","selo":"NOTÍCIA DO DIA","titulo":"...","sub":"...","numero":"15/11","numero_txt":"2º DIA DO ENEM"}
- lista: {"tipo":"lista","titulo":"...","itens":["...","..."],"nota":"..."}   (itens com "**" no começo ganham destaque)
- cta:   {"tipo":"cta"}  (inscrições da Mentoria MAPA 2027 abertas · link na bio)"""
import json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont
M = os.path.dirname(os.path.abspath(__file__))
BG = (10, 22, 44); CARD = (19, 36, 66); LINE = (38, 64, 108); ARC = (22, 40, 72)
BLUE = (22, 119, 255); WHITE = (255, 255, 255); YEL = (255, 204, 0); SOFT = (160, 180, 212); DIM = (92, 112, 148)
FD = M + "/marca/fontes/"
def F(n, s): return ImageFont.truetype(FD + f"Poppins-{n}.ttf", s)
W, H = 1080, 1350; PAD = 84; S = 2  # desenha em 2x e reduz (bordas suaves)

def quebra(d, t, f, larg):
    linhas, cur = [], ""
    for p in t.split():
        x = (cur + " " + p).strip()
        if d.textlength(x, font=f) <= larg: cur = x
        else: linhas.append(cur); cur = p
    if cur: linhas.append(cur)
    return linhas

class Tela:
    def __init__(s, spec, i, n):
        s.spec, s.i, s.n = spec, i, n
        s.im = Image.new("RGB", (W * S, H * S), BG); s.d = ImageDraw.Draw(s.im)
        # ondas concêntricas do sistema MAPA (aqui em tom escuro), saindo do canto superior direito
        cx, cy = W * 0.92, H * 0.18
        for r in range(140, 1500, 95):
            s.d.ellipse(s.b((cx - r, cy - r, cx + r, cy + r)), outline=ARC, width=3 * S)
        lg = Image.open(M + "/marca/logo_cor_texto_branco.png").convert("RGBA"); lw = 250 * S
        lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS); s.im.paste(lg, (PAD * S, 72 * S), lg)
        # selo PLANTÃO com ponto "ao vivo" — a assinatura da notícia
        f = F("Bold", 24); t = "PLANTÃO MAPA"; tw = s.d.textlength(t, font=s.f(f)) / S; x1 = W - PAD; x0 = x1 - tw - 74
        s.d.rounded_rectangle(s.b((x0, 70, x1, 116)), radius=23 * S, outline=YEL, width=2 * S)
        s.d.ellipse(s.b((x0 + 20, 86, x0 + 34, 100)), fill=YEL); s.txt((x0 + 46, 76), t, f, YEL)
        s.faixa()

    def b(s, box): return tuple(v * S for v in box)
    def f(s, font): return font.font_variant(size=font.size * S)
    def txt(s, xy, t, font, fill): s.d.text((xy[0] * S, xy[1] * S), t, font=s.f(font), fill=fill)
    def tl(s, t, font): return s.d.textlength(t, font=s.f(font)) / S
    def wrap(s, t, font, larg): return quebra(s.d, t, s.f(font), larg * S)

    def faixa(s):  # faixa de manchete no rodapé: tema · data · fonte, como um letreiro de jornal
        y0 = H - 92; s.d.rectangle(s.b((0, y0, W, H)), fill=BLUE)
        sp = s.spec; partes = [sp.get("tema", "VESTIBULAR"), "NOTÍCIA DO DIA" + (" · " + sp["data"] if sp.get("data") else ""), "@omapamentoria"]
        f = F("SemiBold", 24); gap = 46; ws = [s.tl(p.upper(), f) for p in partes]
        x = (W - sum(ws) - gap * (len(partes) - 1)) / 2
        for k, p in enumerate(partes):
            s.txt((x, y0 + 30), p.upper(), f, WHITE); x += ws[k]
            if k < len(partes) - 1: s.d.ellipse(s.b((x + gap / 2 - 5, y0 + 42, x + gap / 2 + 5, y0 + 52)), fill=WHITE); x += gap

    def progresso(s, y):
        n, g = s.n, 10; w = (W - 2 * PAD - g * (n - 1)) / n
        for k in range(n):
            x = PAD + k * (w + g); s.d.rounded_rectangle(s.b((x, y, x + w, y + 6)), radius=3 * S, fill=WHITE if k < s.i else LINE)
        s.seta(W - PAD - 44, y + 52)

    def seta(s, x, y, w=44, cor=WHITE):  # seta "→" desenhada (a fonte não tem o glifo)
        s.d.line(s.b((x, y, x + w, y)), fill=cor, width=3 * S)
        s.d.line(s.b((x + w - 14, y - 12, x + w, y)), fill=cor, width=3 * S); s.d.line(s.b((x + w - 14, y + 12, x + w, y)), fill=cor, width=3 * S)

    def fonte(s, y):
        fo = s.spec.get("fonte")
        if not fo: return
        f = F("Medium", 24); t = "FONTE: " + fo.upper(); s.txt((PAD, y), t, f, SOFT)

    def icone(s, x, y, tipo):
        s.d.rounded_rectangle(s.b((x, y, x + 84, y + 84)), radius=20 * S, fill=BLUE)
        if tipo == "jornal":
            s.d.rounded_rectangle(s.b((x + 20, y + 22, x + 64, y + 62)), radius=4 * S, outline=WHITE, width=4 * S)
            for k, (a, c) in enumerate([(28, 56), (28, 46), (28, 56)]):
                s.d.line(s.b((x + a, y + 33 + k * 9, x + c, y + 33 + k * 9)), fill=WHITE, width=3 * S)
        else:  # número do bloco
            f = F("Bold", 36); s.txt((x + (84 - s.tl(tipo, f)) / 2, y + 18), tipo, f, WHITE)

    def png(s): return s.im.resize((W, H), Image.LANCZOS)

def capa(sp, s, t):
    y = 250; f = F("Bold", 24); sel = s.get("selo", "NOTÍCIA DO DIA").upper(); w = t.tl(sel, f) + 48
    t.d.rounded_rectangle(t.b((PAD, y, PAD + w, y + 52)), radius=26 * S, fill=BLUE); t.txt((PAD + 24, y + 11), sel, f, WHITE)
    y += 100; ft = F("ExtraBold", 80)
    linhas = t.wrap(s["titulo"], ft, W - 2 * PAD)
    for ln in linhas: t.txt((PAD, y), ln, ft, WHITE); y += 94
    t.d.rounded_rectangle(t.b((PAD, y + 14, PAD + 110, y + 24)), radius=5 * S, fill=YEL); y += 64
    for ln in t.wrap(s.get("sub", ""), F("Regular", 34), W - 2 * PAD): t.txt((PAD, y), ln, F("Regular", 34), SOFT); y += 48
    if s.get("numero"):  # dado-chave em destaque, num cartão
        y += 34; t.d.rounded_rectangle(t.b((PAD, y, W - PAD, y + 170)), radius=28 * S, fill=CARD, outline=LINE, width=2 * S)
        fn = F("ExtraBold", 104); t.txt((PAD + 40, y + 22), s["numero"], fn, YEL); x = PAD + 40 + t.tl(s["numero"], fn) + 34
        fl = F("Bold", 34)
        ls = t.wrap(s.get("numero_txt", ""), fl, W - PAD - 40 - x)
        y0 = y + 85 - len(ls) * 22
        for k, ln in enumerate(ls): t.txt((x, y0 + k * 44), ln, fl, WHITE)
    yb = H - 92 - 150; f = F("SemiBold", 24); tt = "ARRASTE PARA O LADO"; w = t.tl(tt, f) + 48
    t.d.rounded_rectangle(t.b((PAD, yb, PAD + w, yb + 52)), radius=26 * S, outline=WHITE, width=2 * S); t.txt((PAD + 24, yb + 11), tt, f, WHITE)
    t.seta(W - PAD - 44, yb + 26)

def lista(sp, s, t):
    x0, y0, x1 = PAD, 190, W - PAD; k = t.i - 1; tot = t.n - 2
    # mede o conteúdo para dimensionar o cartão
    for tam in (36, 34, 32, 30, 28):  # reduz a letra até o cartão caber acima da fonte
        ft = F("Bold", tam + 20); fi = F("Medium", tam); fd = F("SemiBold", tam); lh = int(tam * 1.4)
        tit = t.wrap(s["titulo"], ft, x1 - x0 - 96)
        itens = [(it.startswith("**"), t.wrap(it.lstrip("*").strip(), fd if it.startswith("**") else fi, x1 - x0 - 150)) for it in s["itens"]]
        h = 48 + 84 + 40 + len(tit) * (tam + 32) + 30 + sum(len(l) * lh + 34 for _, l in itens) + 30
        if y0 + h <= H - 92 - 190 - 30: break
    t.d.rounded_rectangle(t.b((x0, y0, x1, y0 + h)), radius=32 * S, fill=CARD, outline=LINE, width=2 * S)
    t.icone(x0 + 48, y0 + 48, "jornal")
    c = f"{k:02d}/{tot:02d}"; f = F("SemiBold", 26); t.txt((x1 - 48 - t.tl(c, f), y0 + 60), c, f, SOFT)
    y = y0 + 48 + 84 + 40
    for ln in tit: t.txt((x0 + 48, y), ln, ft, WHITE); y += tam + 32
    y += 30
    for dest, ls in itens:
        cor = YEL if dest else BLUE
        t.d.ellipse(t.b((x0 + 52, y + tam * 0.42, x0 + 72, y + tam * 0.42 + 20)), fill=cor)
        for ln in ls: t.txt((x0 + 100, y), ln, fd if dest else fi, WHITE if dest else (220, 230, 245)); y += lh
        y += 34
    if s.get("nota") and not sp.get("fonte"):
        for ln in t.wrap(s["nota"], F("Regular", 26), W - 2 * PAD): t.txt((PAD, y0 + h + 30), ln, F("Regular", 26), SOFT)
    t.fonte(H - 92 - 190); t.progresso(H - 92 - 120)

def cta(sp, s, t):
    y = 300; t.txt((PAD, y), "MENTORIA O MAPA 2027", F("Medium", 34), SOFT); y += 60
    for ln in ("INSCRIÇÕES", "ABERTAS"): t.txt((PAD, y), ln, F("ExtraBold", 112), WHITE); y += 122
    y += 40; ls = t.wrap("Notícia do vestibular todo dia, explicada sem enrolação.", F("Bold", 34), W - 2 * PAD - 72)
    t.d.rounded_rectangle(t.b((PAD, y, W - PAD, y + 96 + 46 * len(ls))), radius=26 * S, fill=BLUE)
    t.txt((PAD + 36, y + 28), "ACOMPANHE O PLANTÃO", F("Bold", 24), (200, 222, 255))
    for k, ln in enumerate(ls): t.txt((PAD + 36, y + 64 + k * 46), ln, F("Bold", 34), WHITE)
    y += 96 + 46 * len(ls) + 50; f = F("Bold", 38); tt = "Link na bio"; w = t.tl(tt, f) + 170
    t.d.rounded_rectangle(t.b((PAD, y, PAD + w, y + 92)), radius=46 * S, fill=WHITE); t.txt((PAD + 110, y + 18), tt, f, BG)
    ax, ay = PAD + 56, y + 62  # seta diagonal ↗
    t.d.line(t.b((ax, ay, ax + 30, ay - 30)), fill=BG, width=4 * S); t.d.line(t.b((ax + 8, ay - 30, ax + 30, ay - 30)), fill=BG, width=4 * S); t.d.line(t.b((ax + 30, ay - 30, ax + 30, ay - 8)), fill=BG, width=4 * S)
    t.progresso(H - 92 - 120)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    if not spec.get("data"):
        m = re.search(r"(\d{2}/\d{2})", json.dumps(spec["slides"][0].get("selo", ""), ensure_ascii=False))
        if m: spec["data"] = m.group(1)
    sl = spec["slides"]; n = len(sl); arqs = []
    for i, s in enumerate(sl, 1):
        t = Tela(spec, i, n); {"capa": capa, "lista": lista, "cta": cta}[s["tipo"]](spec, s, t)
        p = f"{out}/slide_{i:02d}.jpg"; t.png().save(p, quality=92); arqs.append(p)
    print("\n".join(arqs))
