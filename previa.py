"""Prévia de carrossel para o Calendário de Posts (a página não carrega imagens externas):
junta os slides numa tira 216x270 por slide e imprime um data URL JPEG (~40-80 KB) para o campo `previa` do post.
Uso: python3 previa.py slide_01.jpg slide_02.jpg ...   (arquivos locais ou URLs)"""
import base64, io, sys, urllib.request
from PIL import Image
ims = []
for a in sys.argv[1:]:
    b = urllib.request.urlopen(a, timeout=60).read() if a.startswith("http") else open(a, "rb").read()
    ims.append(Image.open(io.BytesIO(b)).convert("RGB").resize((216, 270), Image.LANCZOS))
sp = Image.new("RGB", (216 * len(ims), 270))
for k, im in enumerate(ims): sp.paste(im, (216 * k, 0))
buf = io.BytesIO(); sp.save(buf, "JPEG", quality=70)
print("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
