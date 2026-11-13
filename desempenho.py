"""Analisador de desempenho dos posts do MAPA no Instagram (API oficial, login do Instagram).
Uso: python3 desempenho.py calendario.json [saida_dir]
  calendario.json: lista de documentos do Calendário de Posts (com "id"; os publicados têm "ig_media_id").
Gera em saida_dir (padrão: ./desempenho):
  - desempenho.json: métricas de cada post + médias por categoria, formato, origem, horário e dia da semana
  - relatorio.md: ranking, o que funciona, o que não funciona e recomendações para o planejamento
Também lista posts da conta que não estão no calendário (ex.: os que a agência postou), para comparar.
Métricas: alcance, curtidas, comentários, compartilhamentos, salvamentos, seguidores ganhos (follows; a Meta só
entrega em post de feed), visitas ao perfil e visualizações. Nota de engajamento (pesos pensados no objetivo do
MAPA: trazer seguidor e conversa): curtida 1, comentário 3, salvamento 3, compartilhamento 4, seguidor 10.
Post com menos de 48 h entra no relatório marcado como "recente" e fica fora das médias (números ainda sobem)."""
import json, os, sys, time, statistics as st, urllib.error
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publicar as P

PESOS = {"likes": 1, "comments": 3, "saved": 3, "shares": 4, "follows": 10}
METRICAS = ["reach", "likes", "comments", "shares", "saved", "views", "total_interactions", "follows", "profile_visits"]
BR = timezone(timedelta(hours=-3)); DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

def insights(mid):
    """Pede as métricas em bloco; se a Meta recusar alguma (varia por formato), pede uma a uma e pula as recusadas."""
    def pede(ms):
        r = P.get(f"{mid}/insights", metric=",".join(ms))
        return {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value")) for d in r.get("data", [])}
    try: return pede(METRICAS)
    except RuntimeError:
        out = {}
        for m in METRICAS:
            try: out.update(pede([m]))
            except RuntimeError: pass
        return out

def categoria(p):
    """Assunto do post, para comparar o que puxa engajamento. Usa plano_id (Reels) e palavras do título."""
    pid = (p.get("plano_id") or "").lower(); t = ((p.get("titulo") or "") + " " + pid).lower()
    if p.get("origem") == "noticias": return "Notícia do dia"
    regras = [("aulão", "Aulão em escola (bastidor)"), ("aulao", "Aulão em escola (bastidor)"), ("festa", "Bastidores / comunidade MAPA"),
              ("+1 ano", "Bastidores / comunidade MAPA"), ("um dia comigo", "Bastidores / comunidade MAPA"), ("absurdo", "Bastidores / comunidade MAPA"),
              ("aprovação", "Aprovação de aluno (foto)"), ("aprovacao", "Aprovação de aluno (foto)"), ("banca da fps", "Aprovação de aluno (foto)"),
              ("dominado", "Aprovados / resultado"), ("chegou ao mapa", "Depoimento / história de aluno"), ("foi assim que", "Depoimento / história de aluno"),
              ("análise", "Análise de prova"), ("analise", "Análise de prova"), ("gabarito", "Análise de prova"), ("fez o ssa", "Análise de prova"),
              ("fez o primeiro dia", "Análise de prova"), ("erro", "Método MAPA (erros, correção)"), ("diagnóstico", "Método MAPA (erros, correção)"),
              ("cronograma", "Método MAPA (erros, correção)"), ("caderno", "Método MAPA (erros, correção)"), ("interpretação", "Método MAPA (erros, correção)"),
              ("desconto", "Venda / mentoria"), ("lançar", "Venda / mentoria"), ("próximo passo", "Venda / mentoria"), ("nasceu", "Institucional"),
              ("direção", "Motivacional"), ("meses podem", "Motivacional"), ("começar tarde", "Motivacional"), ("começado tarde", "Motivacional"),
              ("enem_1_minuto", "Questão do ENEM em 1 minuto"), ("fórmula", "Fórmulas / revisão"), ("formula", "Fórmulas / revisão"),
              ("revis", "Fórmulas / revisão"), ("checklist", "Checklist / guia de prova"), ("véspera", "Véspera / dia de prova"),
              ("vespera", "Véspera / dia de prova"), ("boa prova", "Véspera / dia de prova"), ("pegadinha", "Pegadinhas"),
              ("redac", "Redação"), ("redaç", "Redação"), ("fisica", "Física"), ("física", "Física"), ("bio", "Biologia"),
              ("pais", "Para pais"), ("filho", "Para pais"), ("aprovad", "Aprovados / resultado"), ("acerto", "Aprovados / resultado"),
              ("história", "Aprovados / resultado"), ("de 118", "Aprovados / resultado"), ("tri", "TRI / estratégia"),
              ("estrat", "TRI / estratégia"), ("tempo", "TRI / estratégia"), ("vaga", "Venda / mentoria"), ("mentoria", "Venda / mentoria"),
              ("lançamento", "Venda / mentoria"), ("quem somos", "Institucional"), ("mapa é", "Institucional"),
              ("reta final", "Dicas de estudo"), ("estud", "Dicas de estudo"), ("simulado", "Dicas de estudo")]
    for k, c in regras:
        if k in t: return c
    return "Outros"

def nota(m):
    return sum(PESOS[k] * (m.get(k) or 0) for k in PESOS)

def resumo(grupo):
    g = [x for x in grupo if not x["recente"]]
    if not g: return None
    md = lambda k: round(st.mean([(x["m"].get(k) or 0) for x in g]), 1)
    taxa = [x["taxa"] for x in g if x["taxa"] is not None]
    return {"posts": len(g), "nota_media": round(st.mean([x["nota"] for x in g]), 1), "alcance_medio": md("reach"),
            "curtidas": md("likes"), "comentarios": md("comments"), "compart": md("shares"), "salvos": md("saved"),
            "seguidores": md("follows"), "taxa_engaj_%": round(st.mean(taxa), 2) if taxa else None}

def agrupa(itens, chave):
    gs = {}
    for x in itens: gs.setdefault(chave(x), []).append(x)
    out = {k: resumo(v) for k, v in gs.items()}
    return dict(sorted(((k, v) for k, v in out.items() if v), key=lambda kv: -kv[1]["nota_media"]))

def main():
    if sys.argv[1] == "--relatorio":  # refaz categorias e relatório a partir de um desempenho.json, sem chamar a API
        r = json.load(open(sys.argv[2])); saida = os.path.dirname(sys.argv[2]) or "."
        for x in r["posts"]: x["categoria"] = categoria({**x, "origem": x["origem"] if x["origem"] == "noticias" else ""})
        r["por_categoria"] = agrupa(r["posts"], lambda x: x["categoria"])
        json.dump(r, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
        open(f"{saida}/relatorio.md", "w").write(relatorio(r)); print(relatorio(r)); return
    cal = json.load(open(sys.argv[1])); saida = sys.argv[2] if len(sys.argv) > 2 else "desempenho"
    os.makedirs(saida, exist_ok=True)
    if not P.TOKEN: sys.exit("falta IG_ACCESS_TOKEN no ambiente")
    P.descobre()
    agora = datetime.now(timezone.utc); itens = []; ids_cal = set()
    pub = [p for p in cal if p.get("ig_media_id")]
    # Posts da conta (últimos ~100), para pegar também o que não passou pelo calendário
    conta = []
    try:
        r = P.get(f"{P.IG}/media", fields="id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count", limit=100)
        conta = r.get("data", [])
    except RuntimeError as e: print("aviso: não li a lista de posts da conta:", e, file=sys.stderr)
    por_id = {m["id"]: m for m in conta}
    fontes = [(p, True) for p in pub] + [({"id": "conta-" + m["id"], "ig_media_id": m["id"], "titulo": (m.get("caption") or "")[:70].replace("\n", " "),
              "tipo": "reel" if m.get("media_product_type") == "REELS" else "carrossel" if m.get("media_type") == "CAROUSEL_ALBUM" else "foto",
              "origem": "fora do calendário"}, False) for m in conta if m["id"] not in {p["ig_media_id"] for p in pub}]
    for p, no_cal in fontes:
        mid = p["ig_media_id"]; info = por_id.get(mid)
        try:
            if not info: info = P.get(mid, fields="id,media_type,media_product_type,timestamp,permalink,like_count,comments_count")
            m = insights(mid)
        except RuntimeError as e:
            print(f"aviso: {p['id']} ({mid}) sem métricas: {str(e)[:160]}", file=sys.stderr); continue
        m.setdefault("likes", info.get("like_count")); m.setdefault("comments", info.get("comments_count"))
        ts = datetime.strptime(info["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(BR)
        taxa = round(100 * sum((m.get(k) or 0) for k in ("likes", "comments", "shares", "saved")) / m["reach"], 2) if m.get("reach") else None
        itens.append({"id": p["id"], "titulo": p.get("titulo", ""), "tipo": p.get("tipo"), "origem": p.get("origem"),
                      "categoria": categoria(p), "plano_id": p.get("plano_id"), "permalink": info.get("permalink"),
                      "publicado": ts.isoformat(), "hora": ts.hour, "dia": DIAS[ts.weekday()], "m": m, "nota": nota(m),
                      "taxa": taxa, "recente": (agora - ts) < timedelta(hours=48), "no_calendario": no_cal})
        time.sleep(0.3)
    seg = {}
    try:
        u = P.get(P.IG, fields="followers_count,media_count,username"); seg = {"seguidores_agora": u.get("followers_count"), "posts_na_conta": u.get("media_count")}
    except RuntimeError: pass
    itens.sort(key=lambda x: -x["nota"])
    res = {"gerado_em": agora.astimezone(BR).isoformat(timespec="minutes"), "conta": seg, "pesos": PESOS,
           "por_categoria": agrupa(itens, lambda x: x["categoria"]), "por_formato": agrupa(itens, lambda x: x["tipo"]),
           "por_origem": agrupa(itens, lambda x: x["origem"]), "por_horario": agrupa(itens, lambda x: f"{x['hora']}h"),
           "por_dia": agrupa(itens, lambda x: x["dia"]), "posts": itens}
    json.dump(res, open(f"{saida}/desempenho.json", "w"), ensure_ascii=False, indent=1)
    open(f"{saida}/relatorio.md", "w").write(relatorio(res)); print(relatorio(res))

def relatorio(r):
    L = [f"# Desempenho do Instagram do MAPA ({r['gerado_em'][:16].replace('T', ' ')})", ""]
    if r["conta"]: L += [f"Seguidores agora: **{r['conta'].get('seguidores_agora')}**", ""]
    ok = [x for x in r["posts"] if not x["recente"]]
    L += [f"{len(ok)} posts analisados (+{len(r['posts']) - len(ok)} com menos de 48 h, fora das médias). "
          "Nota = curtidas + 3×comentários + 3×salvos + 4×compartilhamentos + 10×seguidores ganhos.", ""]
    cab = "| Post | Formato | Categoria | Alcance | Curt. | Coment. | Compart. | Salvos | Seguid. | Taxa | Nota |\n|---|---|---|---|---|---|---|---|---|---|---|"
    lin = lambda x: (f"| [{(x['titulo'] or x['id'])[:42]}]({x['permalink']}) | {x['tipo']} | {x['categoria']} | {x['m'].get('reach') or '–'} | "
                     f"{x['m'].get('likes') or 0} | {x['m'].get('comments') or 0} | {x['m'].get('shares') or 0} | {x['m'].get('saved') or 0} | "
                     f"{x['m'].get('follows') if x['m'].get('follows') is not None else '–'} | {str(x['taxa']) + '%' if x['taxa'] is not None else '–'} | {x['nota']} |")
    L += ["## Top 5", cab] + [lin(x) for x in ok[:5]] + ["", "## Os 5 mais fracos", cab] + [lin(x) for x in ok[-5:][::-1]] + [""]
    def tab(t, d):
        L.extend([f"## {t}", "| Grupo | Posts | Nota média | Alcance médio | Coment. | Compart. | Salvos | Seguid. | Taxa |", "|---|---|---|---|---|---|---|---|---|"])
        L.extend(f"| {k} | {v['posts']} | {v['nota_media']} | {v['alcance_medio']} | {v['comentarios']} | {v['compart']} | {v['salvos']} | {v['seguidores']} | {v['taxa_engaj_%']}% |" for k, v in d.items())
        L.append("")
    tab("Por categoria", r["por_categoria"]); tab("Por formato", r["por_formato"]); tab("Por origem", r["por_origem"])
    tab("Por horário", r["por_horario"]); tab("Por dia da semana", r["por_dia"])
    L += ["## Recomendações para o planejamento"] + recomendacoes(r) + [""]
    rec = [x for x in r["posts"] if x["recente"]]
    if rec: L += ["## Recentes (ainda subindo)", cab] + [lin(x) for x in rec] + [""]
    return "\n".join(L)

def recomendacoes(r):
    R = []; cat = [(k, v) for k, v in r["por_categoria"].items() if v["posts"] >= 2 and k != "Outros"] or list(r["por_categoria"].items())
    if cat:
        R.append(f"- **Mais conteúdo de:** {', '.join(k for k, _ in cat[:3])} (maior nota média). Priorize esses assuntos na fila de Reels e nos carrosséis.")
        if len(cat) > 3: R.append(f"- **Menos conteúdo de:** {', '.join(k for k, _ in cat[-2:])} (menor nota média): reformule o gancho ou espace mais.")
    seg = sorted(((k, v) for k, v in r["por_categoria"].items()), key=lambda kv: -(kv[1]["seguidores"] or 0))
    if seg and (seg[0][1]["seguidores"] or 0) > 0: R.append(f"- **O que mais traz seguidor:** {seg[0][0]} ({seg[0][1]['seguidores']} por post, em média).")
    sv = sorted(r["por_categoria"].items(), key=lambda kv: -((kv[1]["salvos"] or 0) + (kv[1]["compart"] or 0)))
    if sv: R.append(f"- **Mais salvo e compartilhado:** {sv[0][0]} — formato de \"guardar pra depois\"; vale virar série fixa.")
    cm = sorted(r["por_categoria"].items(), key=lambda kv: -(kv[1]["comentarios"] or 0))
    if cm and (cm[0][1]["comentarios"] or 0) > 0: R.append(f"- **Mais comentado:** {cm[0][0]}. Use pergunta direta no fechamento (\"comenta aí...\") nos outros assuntos também.")
    fm = list(r["por_formato"].items())
    if len(fm) >= 2: R.append(f"- **Formato que rende mais:** {fm[0][0]} (nota {fm[0][1]['nota_media']} contra {fm[-1][1]['nota_media']} de {fm[-1][0]}).")
    hr = [(k, v) for k, v in r["por_horario"].items() if v["posts"] >= 2]
    if hr: R.append(f"- **Melhor horário até agora:** {hr[0][0]} (alcance médio {hr[0][1]['alcance_medio']}). Amostra pequena: confirme com mais semanas antes de mudar a grade.")
    R.append("- Repetir o que funcionou com ângulo novo (mesma categoria, outro gancho) e nunca o mesmo post.")
    return R

if __name__ == "__main__": main()
