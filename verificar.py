"""Verificador de publicação: garante que nenhum Reel ou carrossel do calendário fique sem sair.
Uso: python3 verificar.py posts.json   (todos os documentos de `posts`, cada um com "id")
Saída: JSON [{"id", "acao", "motivo"}] com o que a rodada de VERIFICAÇÃO deve fazer:
- "publicar":    post agendado cujo horário já passou há mais de 10 min e ainda não saiu (rodada perdida/atrasada),
                 ou post em erro com menos de MAX_TENTATIVAS tentativas, ainda dentro do prazo do dia.
- "republicar":  marcado como publicado, mas o post não existe mais na conta (confere pelo ig_media_id).
- "marcar_publicado": o post já está na conta (mesma legenda), só o calendário não foi atualizado.
- "perdido":     passou do prazo (23h do dia) sem sair, ou estourou MAX_TENTATIVAS. Reel perdido volta para o plano
                 (a rodada das 7h o escolhe de novo); carrossel/notícia perdido é avisado ao dono.
Precisa de IG_ACCESS_TOKEN no ambiente para conferir a conta; sem ele, só faz as checagens de horário."""
import json, os, sys
from datetime import datetime, timedelta, timezone

BR = timezone(timedelta(hours=-3)); MAX_TENTATIVAS = 4; PRAZO_HORA = 23
agora = datetime.now(BR)

def conta():
    if not os.environ.get("IG_ACCESS_TOKEN"): return None
    import publicar as p
    p.descobre(); return p

def main(posts):
    p = None
    try: p = conta()
    except Exception as e: print(json.dumps({"aviso": f"sem acesso à conta: {e}"}), file=sys.stderr)
    out = []
    for d in posts:
        if not d.get("quando") or d.get("tipo") not in ("reel", "carrossel"): continue
        q = datetime.fromisoformat(d["quando"]); st = d.get("status"); tent = int(d.get("tentativas") or 0)
        prazo = q.replace(hour=PRAZO_HORA, minute=0, second=0)
        if st == "publicado":
            if p and d.get("ig_media_id") and agora - q < timedelta(days=3) and not p.confere(d["ig_media_id"]):
                out.append({"id": d["id"], "acao": "republicar", "motivo": "marcado como publicado, mas não está na conta"})
            continue
        if st not in ("agendado", "erro") or q > agora - timedelta(minutes=10): continue
        if p:
            try:
                ja = p.ja_publicado(d.get("legenda"), horas=48)
                if ja:
                    out.append({"id": d["id"], "acao": "marcar_publicado", "motivo": "já está na conta", "media_id": ja[0], "permalink": ja[1]}); continue
            except Exception: pass
        if agora > prazo:
            out.append({"id": d["id"], "acao": "perdido", "motivo": f"não saiu até {PRAZO_HORA}h de {q:%d/%m}"})
        elif tent >= MAX_TENTATIVAS:
            out.append({"id": d["id"], "acao": "perdido", "motivo": f"{tent} tentativas com erro: {d.get('erro', '')[:200]}"})
        else:
            out.append({"id": d["id"], "acao": "publicar", "motivo": "erro anterior, nova tentativa" if st == "erro" else f"horário {q:%H:%M} passou e não saiu"})
    return out

if __name__ == "__main__":
    print(json.dumps(main(json.load(open(sys.argv[1]))), ensure_ascii=False, indent=1))
