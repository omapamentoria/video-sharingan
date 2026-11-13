"""Gera carrossel no sistema visual do MAPA (claro, ondas, cartões, barra de progresso) a partir de um spec JSON.
Uso: python3 carrossel/gerar.py spec.json pasta_saida
spec: {"tag":"FÍSICA · ENEM","data":"SEX · 13 NOV","slides":[{"tipo":"capa","titulo":"...","sub":"..."},
       {"tipo":"formulas","titulo":"Cinemática","itens":[["rótulo","fórmula em HTML"],...]}, {"tipo":"cta"}]}
Fórmulas aceitam HTML: <sub>, <sup>, e frações com <span class=fr><b>num</b><b>den</b></span>."""
import json, os, sys, asyncio
from playwright.sync_api import sync_playwright
M = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = M + "/marca/fontes/"
CSS = """
@font-face{font-family:P;src:url(file://%(fd)sPoppins-Regular.ttf);font-weight:400}
@font-face{font-family:P;src:url(file://%(fd)sPoppins-Medium.ttf);font-weight:500}
@font-face{font-family:P;src:url(file://%(fd)sPoppins-SemiBold.ttf);font-weight:600}
@font-face{font-family:P;src:url(file://%(fd)sPoppins-Bold.ttf);font-weight:700}
@font-face{font-family:P;src:url(file://%(fd)sPoppins-ExtraBold.ttf);font-weight:800}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;font-family:P,Inter,sans-serif;color:#0B1A33;background:#fff;position:relative;overflow:hidden}
.ondas{position:absolute;inset:0;z-index:0}
.logo{position:absolute;left:84px;top:78px;height:50px;z-index:2}
.tag{display:inline-block;background:#1677FF;color:#fff;font-weight:700;font-size:24px;padding:8px 24px;border-radius:30px;letter-spacing:.5px}
.conta{position:absolute;right:84px;top:88px;font-weight:600;font-size:26px;color:#5A6B88;z-index:2}
.rod{position:absolute;left:84px;right:84px;bottom:70px;display:flex;justify-content:space-between;align-items:center;z-index:2}
.rod span{font-size:24px;color:#5A6B88;font-weight:500}
.prog{position:absolute;left:84px;right:84px;bottom:140px;display:flex;gap:10px;z-index:2}
.prog i{flex:1;height:6px;border-radius:3px;background:#D5DEEC}.prog i.on{background:#0B1A33}
.seta{width:46px;height:20px}
.card{position:absolute;left:84px;right:84px;top:180px;background:#EEF5FF;border:2px solid #D3E3FB;border-radius:36px;padding:44px 48px;z-index:2}
.cab{display:flex;align-items:center;gap:24px;margin-bottom:22px}
.ico{width:80px;height:80px;border-radius:20px;background:#1677FF;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:34px;flex:none}
h2{font-weight:800;font-size:54px;line-height:1.05}
.sub2{font-size:24px;color:#5A6B88;font-weight:500;margin-top:4px}
.it{padding:15px 0;border-top:2px solid #D3E3FB;display:flex;justify-content:space-between;align-items:center;gap:20px}
.it .r{font-size:25px;color:#4A5B78;font-weight:500;flex:none;max-width:42%%}
.it .f{font-size:34px;font-weight:600;text-align:right;font-family:P,Inter,sans-serif;white-space:nowrap}
.f sub,.f sup{font-size:.62em}
.fr{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;font-size:.86em;margin:0 3px}
.fr b{font-weight:600;line-height:1.1}.fr b:first-child{border-bottom:3px solid #0B1A33;padding:0 4px 2px}
.dica{margin-top:18px;background:#fff;border-radius:20px;padding:16px 22px;font-size:24px;color:#0B1A33;font-weight:500}
.dica b{color:#1677FF;font-weight:700}
.capa{position:absolute;left:84px;right:84px;top:190px;z-index:2}
.capa h1{font-weight:800;font-size:96px;line-height:1.04;margin-top:34px}
.capa .sl{width:110px;height:10px;border-radius:5px;background:#1677FF;margin-top:26px}
.capa p{font-size:36px;color:#4A5B78;margin-top:30px;line-height:1.35;font-weight:500}
.chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:40px}
.chips span{border:2px solid #C9D9F2;border-radius:24px;padding:6px 18px;font-size:23px;font-weight:600;color:#1677FF;background:#fff}
.dt{position:absolute;left:84px;bottom:220px;font-size:24px;color:#5A6B88;font-weight:500;z-index:2}
.arr{position:absolute;left:84px;bottom:150px;border:2px solid #0B1A33;border-radius:30px;padding:8px 24px;font-size:23px;font-weight:600;z-index:2}
body.dark{background:#0A162C;color:#fff}
.cta{position:absolute;left:84px;right:84px;top:250px;z-index:2}
.cta .k{font-size:32px;color:#A0B4D4;font-weight:500}
.cta h1{font-size:120px;font-weight:800;line-height:1.02;margin-top:14px}
.cta .bx{margin-top:44px;background:#1677FF;border-radius:28px;padding:30px 36px}
.cta .bx small{font-size:22px;font-weight:700;color:#C8DEFF;letter-spacing:.5px}
.cta .bx div{font-size:36px;font-weight:700;margin-top:6px;line-height:1.3}
.cta .lk{display:inline-flex;align-items:center;gap:18px;margin-top:44px;background:#fff;color:#0A162C;border-radius:50px;padding:18px 48px;font-size:38px;font-weight:700}
body.dark .prog i{background:#26406C}body.dark .prog i.on{background:#fff}body.dark .rod span{color:#A0B4D4}
"""
def ondas(dark):
    c = "#16284A" if dark else "#E4EEFC"
    rs = "".join(f'<circle cx="1000" cy="230" r="{r}" fill="none" stroke="{c}" stroke-width="3"/>' for r in range(120, 1600, 95))
    return f'<svg class="ondas" width="1080" height="1350">{rs}</svg>'
SETA = lambda c: f'<svg class="seta" viewBox="0 0 46 20"><path d="M0 10H44M32 1L44 10L32 19" stroke="{c}" stroke-width="3" fill="none"/></svg>'

def pagina(spec, s, i, n):
    dark = s["tipo"] == "cta"; logo = "logo_cor_texto_branco.png" if dark else "logo_cor_texto_navy.png"
    prog = "".join(f'<i class="{"on" if k < i else ""}"></i>' for k in range(n))
    h = [ondas(dark), f'<img class="logo" src="file://{M}/marca/{logo}">']
    if s["tipo"] == "capa":
        chips = "".join(f"<span>{c}</span>" for c in s.get("chips", []))
        h.append(f'<div class="capa"><span class="tag">{spec["tag"]}</span><h1>{s["titulo"]}</h1><div class="sl"></div><p>{s.get("sub","")}</p><div class="chips">{chips}</div></div>')
        h.append(f'<div class="dt">{spec.get("data","")}</div><div class="arr">ARRASTE PARA O LADO</div>')
        h.append(f'<div class="rod"><span>@omapamentoria</span>{SETA("#0B1A33")}</div>')
    elif s["tipo"] == "formulas":
        k = i - 1; tot = n - 2
        its = "".join(f'<div class="it"><div class="r">{r}</div><div class="f">{f}</div></div>' for r, f in s["itens"])
        dica = f'<div class="dica"><b>Dica:</b> {s["dica"]}</div>' if s.get("dica") else ""
        h.append(f'<div class="conta">{k:02d}/{tot:02d}</div><div class="card"><div class="cab"><div class="ico">{s.get("icone", k)}</div><div><h2>{s["titulo"]}</h2><div class="sub2">{s.get("sub","")}</div></div></div>{its}{dica}</div>')
        h.append(f'<div class="prog">{prog}</div><div class="rod"><span>@omapamentoria</span>{SETA("#0B1A33")}</div>')
    else:
        h.append('<div class="cta"><div class="k">MENTORIA O MAPA 2027</div><h1>INSCRIÇÕES<br>ABERTAS</h1>'
                 f'<div class="bx"><small>{s.get("chamada","SALVA ESTE POST")}</small><div>{s.get("texto","")}</div></div>'
                 '<div class="lk"><svg width="30" height="30" viewBox="0 0 30 30"><path d="M4 26L26 4M10 4H26V20" stroke="#0A162C" stroke-width="4" fill="none"/></svg>Link na bio</div></div>')
        h.append(f'<div class="prog">{prog}</div><div class="rod"><span>@omapamentoria</span>{SETA("#fff")}</div>')
    return f'<html><head><meta charset="utf-8"><style>{CSS % {"fd": FD}}</style></head><body class="{"dark" if dark else ""}">{"".join(h)}</body></html>'

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    sl = spec["slides"]; n = len(sl)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for i, s in enumerate(sl, 1):
            hp = f"{out}/slide-{i:02d}.html"; open(hp, "w").write(pagina(spec, s, i, n))
            pg.goto("file://" + hp); pg.wait_for_timeout(150)
            alt = pg.evaluate("document.querySelector('.card') ? document.querySelector('.card').getBoundingClientRect().bottom : 0")
            if alt > 1190: print(f"AVISO slide {i}: cartão passa do limite ({alt:.0f}px)")
            pg.screenshot(path=f"{out}/slide-{i:02d}.jpg", type="jpeg", quality=92); os.remove(hp)
        b.close()
    print(n, "slides")
