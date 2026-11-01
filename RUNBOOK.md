# Publicador automático do Instagram do MAPA

Fila única: **Calendário de Posts MAPA** — artifact `https://claude.ai/artifact/PfeNXpXEZcuZBFDyCdx3jw`,
banco do artifact, coleção `posts` (ler/escrever com a ferramenta ArtifactData).
Campos de cada post: `tipo` ("reel" | "carrossel"), `titulo`, `legenda`, `midia` (URLs públicas, na ordem),
`quando` (ISO com -03:00), `status` ("agendado" | "publicado" | "erro" | "rascunho"), `origem`.

Credenciais (só no ambiente, nunca em arquivo ou chat): `IG_ACCESS_TOKEN`, `IG_USER_ID`
(token do "login do Instagram"; host padrão graph.instagram.com). Mídia pública: branch `instagram-midia`
deste repositório, servida em `https://raw.githubusercontent.com/omapamentoria/video-sharingan/instagram-midia/<caminho>`.

## Rodada de AGENDAMENTO (todo dia às 7h, e sempre que o dono pedir "agende mais")
Objetivo: deixar no calendário os posts do dia (ou dos próximos N dias, quando pedido), seguindo o planejamento.
1. `git pull`. Leia `plano_reels.json` (ordem oficial dos Reels) e os `posts` do calendário.
2. **Reel das 12h**: se ainda não houver post `tipo: "reel"` para o dia, pegue o primeiro Reel do plano com
   `pronto: true` que ainda não está no calendário e crie o documento `reel-AAAA-MM-DD`:
   `tipo: "reel"`, `titulo`, `legenda` (a do plano), `midia: [video]`, `capa`, `quando: "AAAA-MM-DDT12:00:00-03:00"`,
   `status: "agendado"`, `origem: "videos"`. Sem Reel pronto disponível: não crie nada e avise na resposta.
3. **Carrossel das 19h**: confirme que existe `car-AAAA-MM-DD` agendado. Se faltar, avise (não invente conteúdo).
4. **Notícia das 15h**: não crie aqui; ela nasce na rodada das 14h20. Só confirme que não há outro post às 15h.
5. Pedido "agende os próximos N dias": repita 2–4 para cada dia, nunca dois Reels no mesmo dia.
6. **Dias de prova** (8/11 e 15/11 ENEM; 6/12 e 13/12 SSA 1 e 2 — lista em `DIAS_DE_PROVA`, no `revisar.py`):
   os horários se invertem. O carrossel de "Boa prova" sai às **12h** (antes do portão do ENEM fechar, às 13h, e antes
   do SSA 2, à tarde) e o Reel vai para as **19h**. Ajuste `quando` do `car-` e do `reel-` desses dias.
   Nunca publicar "Boa prova hoje" depois que a prova começou.
7. No fim, rode a REVISÃO dos posts do dia (ou do período agendado).

## Rodada de REVISÃO (depois do agendamento das 7h, depois da notícia das 14h20 e sob demanda)
1. Exporte para `revisao.json` os posts a revisar (com `id`), rode `python3 revisar.py revisao.json`.
2. Para cada problema:
   - com `legenda_corrigida`: aplique com `update` (ou `str_replace`) no documento.
   - "hoje/amanhã", coerência de datas, fatos de notícia: leia o post e a data; corrija o texto só se estiver
     errado na data em que vai sair (ex.: "amanhã" que já passou). Notícia: confira de novo na fonte.
   - mídia fora do ar / tamanho errado / Reel inválido: marque `status: "erro"` com o motivo (não publique quebrado).
   - horário fora do plano: ajuste `quando` para o horário do plano no mesmo dia.
3. Revise também o sentido: legenda combina com o título e as imagens? Sem repetir o mesmo assunto de um post
   recente? Tom do MAPA, sem promessas (nada de "garantido", números inventados). Edite o necessário.
4. Resposta: lista curta do que foi revisado e do que mudou.

## Rodada de PUBLICAÇÃO (12h, 15h, 19h)
1. Token: use `IG_ACCESS_TOKEN` do ambiente; se não existir, use o arquivo `~/.mapa/ig_token` (fora do repositório,
   permissão 600). Se o arquivo sumiu (container novo), recrie-o com o token que o dono passou nesta conversa.
   Rode o publicador com `IG_ACCESS_TOKEN="$(cat ~/.mapa/ig_token)" python3 publicar.py post.json`.
   Nunca imprima, faça commit ou repita o token em mensagens. Sem token nenhum: responda "sem token" e pare.
2. Leia `posts` com `status == "agendado"`. Publique os que têm `quando` entre agora − 6 h e agora + 5 min,
   em ordem de horário. Nunca publique o mesmo documento duas vezes (confira `status` logo antes).
3. Para cada um: grave `{tipo, legenda, midia}` em `post.json` e rode `python3 publicar.py post.json`.
   - ok → `update` do documento: `status: "publicado"`, `ig_media_id`, `permalink`, `publicado_em` (ISO).
   - erro → `update`: `status: "erro"`, `erro` (a mensagem). Não tente de novo na mesma rodada.
4. Posts agendados há mais de 6 h e não publicados: marque `status: "erro"`, `erro: "horário perdido"`.
5. Resposta final: uma linha por post (publicado / erro).

## Rodada da NOTÍCIA DO DIA (14h20, para publicar às 15h)
1. Pesquise as notícias das últimas 24 h sobre **ENEM, SSA (UPE) e FPS** (WebSearch, modo extended).
   Prefira fontes oficiais (gov.br/inep, gov.br/mec, processodeingresso.upe.pe.gov.br, fps.edu.br) e veículos
   sérios (Agência Brasil, G1, JC, Diario de Pernambuco, CBN Recife). Abra a fonte (WebFetch) e confira cada
   número, data e horário. **Nada inventado**: só entra o que está escrito na fonte. Se não houver notícia nova
   e útil, faça um post de agenda/contagem regressiva com datas oficiais conferidas.
2. Escolha o ângulo mais útil e interessante para o aluno (o que muda pra ele, o que fazer agora).
3. Monte `spec.json` (veja `noticia_post.py`): capa (selo "NOTÍCIA DO DIA · DD/MM", título curto e forte,
   subtítulo; use `numero`/`numero_txt` para contagens), 2–3 slides `lista` com `nota` citando a fonte, e o slide `cta`.
   Renderize: `python3 noticia_post.py spec.json slides`.
4. Publique as imagens na branch `instagram-midia` em `noticias/AAAA-MM-DD/` (commit + push) e confira que as URLs
   raw respondem 200 com `image/jpeg`.
5. Crie o documento `not-AAAA-MM-DD` em `posts`: `tipo: "carrossel"`, `titulo`, `midia` (URLs), `quando:
   "AAAA-MM-DDT15:00:00-03:00"`, `status: "agendado"`, `origem: "noticias"`, e a `legenda`: gancho forte,
   2–4 frases com os fatos, chamada para salvar/compartilhar, depois
   "📍 As inscrições da Mentoria MAPA 2027 estão abertas.\n👉 Link na bio.", "Fontes: ..." e 4–5 hashtags.
   Nunca mencionar live. Tom: próximo, direto, sem exagero.
6. Rode a REVISÃO só da notícia criada.

## Regras
- Nunca escrever o token em arquivo, commit, log ou mensagem.
- Não alterar posts com `origem` diferente da rodada, exceto o `status` na publicação.
