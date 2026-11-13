# Publicador automático do Instagram do MAPA

Fila única: **Calendário de Posts MAPA** — artifact `https://claude.ai/artifact/PfeNXpXEZcuZBFDyCdx3jw`,
banco do artifact, coleção `posts` (ler/escrever com a ferramenta ArtifactData).
Campos de cada post: `tipo` ("reel" | "carrossel"), `titulo`, `legenda`, `midia` (URLs públicas, na ordem),
`quando` (ISO com -03:00), `status` ("agendado" | "publicado" | "erro" | "perdido" | "rascunho"), `tentativas`, `origem`.

Credenciais (só no ambiente, nunca em arquivo ou chat): `IG_ACCESS_TOKEN`, `IG_USER_ID`
(token do "login do Instagram"; host padrão graph.instagram.com). Mídia pública: branch `instagram-midia`
deste repositório, servida em `https://raw.githubusercontent.com/omapamentoria/video-sharingan/instagram-midia/<caminho>`.

## Grade de horários (definida pelo dono em 13/11/2026)
- **12h – Notícia do dia** (hora do almoço). Nasce na rodada das 11h20.
- **15h – Reel da agência** (vídeos já editados, fila do `plano_reels.json`).
- **19h – Conteúdo do roteiro** (página https://claude.ai/artifact/LzEcaehDNmrc23ouJWbXRK: vídeos 001–070 do Drive
  e carrosséis que o MAPA monta), com `origem: "roteiro"`. É o horário de maior alcance. Se o post do roteiro do
  dia não estiver pronto, o carrossel da agência (`car-AAAA-MM-DD`) segura as 19h; se estiver, o `car-` do dia
  vira `rascunho` (fica guardado para outro dia).

## Rodada de AGENDAMENTO (todo dia às 7h, e sempre que o dono pedir "agende mais")
Objetivo: deixar no calendário os posts do dia (ou dos próximos N dias, quando pedido), seguindo o planejamento.
1. `git pull`. Leia `plano_reels.json` (ordem oficial dos Reels) e os `posts` do calendário.
2. **Reel das 15h**: se ainda não houver post `tipo: "reel"` para o dia, pegue o primeiro Reel do plano com
   `pronto: true`, sem `ja_postado`, que ainda não está no calendário (conta como "no calendário" só um `reel-` com
   `plano_id` igual e `status` "agendado", "publicado" ou "erro"; um Reel "perdido" volta para a fila) e crie o documento `reel-AAAA-MM-DD`:
   `tipo: "reel"`, `titulo`, `legenda` (a do plano), `midia: [video]`, `capa`, `quando: "AAAA-MM-DDT15:00:00-03:00"`,
   `status: "agendado"`, `origem: "videos"`, `plano_id` (o `id` do plano). Sem Reel pronto disponível: não crie nada e avise na resposta.
3. **19h**: veja no "Calendário de posts" da página do roteiro o que vai ao ar hoje. Se o post do roteiro estiver
   pronto (vídeo no Drive editado, ou carrossel montado), ele fica às 19h (`origem: "roteiro"`) e o `car-` do dia
   vira `rascunho`. Senão, confirme o `car-AAAA-MM-DD` agendado às 19h. Se faltar tudo, avise (não invente conteúdo).
4. **Notícia das 12h**: não crie aqui; ela nasce na rodada das 11h20. Só confirme que não há outro post às 12h.
5. Pedido "agende os próximos N dias": repita 2–4 para cada dia, nunca dois Reels no mesmo dia.
6. **Dias de prova** (8/11 e 15/11 ENEM; 6/12 e 13/12 SSA 1 e 2 — lista em `DIAS_DE_PROVA`, no `revisar.py`):
   o carrossel de "Boa prova" sai às **12h** (antes do portão do ENEM fechar, às 13h, e antes do SSA 2, à tarde),
   a notícia vai para as **15h** e o Reel da agência não sai (volta para a fila). 19h segue com o conteúdo do roteiro.
   Nunca publicar "Boa prova hoje" depois que a prova começou.
7. No fim, rode a REVISÃO dos posts do dia (ou do período agendado).

## Rodada de REVISÃO (depois do agendamento das 7h, depois da notícia das 11h20 e sob demanda)
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
0. `git pull` antes de tudo (o `publicar.py` pode ter sido corrigido).
1. Token: use `IG_ACCESS_TOKEN` do ambiente; se não existir, use o arquivo `~/.mapa/ig_token` (fora do repositório,
   permissão 600). Se o arquivo sumiu (container novo), recrie-o com o token que o dono passou nesta conversa.
   Rode o publicador com `IG_ACCESS_TOKEN="$(cat ~/.mapa/ig_token)" python3 publicar.py post.json`.
   Nunca imprima, faça commit ou repita o token em mensagens. Sem token nenhum: responda "sem token" e pare.
2. Leia `posts` com `status == "agendado"`. Publique os que têm `quando` entre agora − 6 h e agora + 5 min,
   em ordem de horário. Nunca publique o mesmo documento duas vezes (confira `status` logo antes).
3. Para cada um: grave `{tipo, legenda, midia}` em `post.json` e rode `python3 publicar.py post.json`.
   O `publicar.py` já tenta 3 vezes (espera 1 e 3 min) e, antes de cada tentativa, procura na conta um post com a
   mesma legenda, para nunca duplicar (se achar, devolve `ja_estava_publicado: true` com o link).
   - ok → `update` do documento: `status: "publicado"`, `ig_media_id`, `permalink`, `publicado_em` (ISO), apague `erro`.
   - erro → `update`: `status: "erro"`, `erro` (a mensagem), `tentativas` (+1). A rodada de VERIFICAÇÃO tenta de novo.
4. No fim, rode a VERIFICAÇÃO (abaixo) do dia.
5. Resposta final: uma linha por post (publicado / erro).

## Rodada de VERIFICAÇÃO (12h31, 15h31, 19h31 e 21h31; também no fim de cada PUBLICAÇÃO e do AGENDAMENTO das 7h)
Objetivo: nenhum Reel ou carrossel fica sem sair. Se algo falhou, trabalhar até postar.
0. `git pull`. Token como na PUBLICAÇÃO.
1. Exporte para `verifica.json` os posts dos últimos 3 dias e de hoje (com `id`) e rode
   `python3 verificar.py verifica.json`. Para cada item:
   - `publicar`: confira o `status` de novo (não pode ter virado "publicado") e publique como na PUBLICAÇÃO
     (`tentativas` +1 em caso de erro). Antes, entenda o erro anterior e corrija a causa se estiver ao seu alcance:
     URL de mídia fora do ar (confira com curl; se a imagem/vídeo sumiu da branch `instagram-midia`, recoloque),
     legenda acima de 2.200 caracteres ou com mais de 30 hashtags (encurte), imagem fora de 1080x1350/1080x1080
     (corrija o arquivo), token expirado (avise o dono). Erros temporários da Meta (5xx, "try again", limite de taxa):
     só tente de novo.
   - `marcar_publicado`: o post já está na conta; só atualize o documento (`status: "publicado"`, `ig_media_id`,
     `permalink`).
   - `republicar`: o post sumiu da conta; publique de novo e atualize o documento.
   - `perdido`: `update` com `status: "perdido"` e o motivo em `erro`. Reel perdido volta para a fila do plano (a
     rodada das 7h o agenda de novo num dia livre). Carrossel ou notícia perdidos: avise o dono na resposta.
2. Resposta: uma linha por item tratado; se não houver nada, responda "tudo publicado".

## Rodada da NOTÍCIA DO DIA (11h20, para publicar às 12h; em dia de prova, às 15h)
1. Pesquise as notícias das últimas 24 h sobre **ENEM, SSA (UPE) e FPS** (WebSearch, modo extended).
   Prefira fontes oficiais (gov.br/inep, gov.br/mec, processodeingresso.upe.pe.gov.br, fps.edu.br) e veículos
   sérios (Agência Brasil, G1, JC, Diario de Pernambuco, CBN Recife). Abra a fonte (WebFetch) e confira cada
   número, data e horário. **Nada inventado**: só entra o que está escrito na fonte. Se não houver notícia nova
   e útil, faça um post de agenda/contagem regressiva com datas oficiais conferidas.
2. Escolha o ângulo mais útil e interessante para o aluno (o que muda pra ele, o que fazer agora).
3. Monte `spec.json` (veja `noticia_post.py`): capa (selo "NOTÍCIA DO DIA · DD/MM", título curto e forte,
   subtítulo; use `numero`/`numero_txt` para contagens), 2–3 slides `lista` e o slide `cta`. No topo do spec:
   `fonte` (ex.: "Inep, 10/11/2026", aparece em todo slide), `tema` (ex.: "ENEM 2026", "SSA 2026", "FPS 2027") e
   `data` ("DD/MM"). Modelo escuro "Plantão MAPA" aprovado pelo dono em 13/11; não mude o visual sem pedido.
   Renderize: `python3 noticia_post.py spec.json slides`.
4. Publique as imagens na branch `instagram-midia` em `noticias/AAAA-MM-DD/` (commit + push) e confira que as URLs
   raw respondem 200 com `image/jpeg`.
5. Crie o documento `not-AAAA-MM-DD` em `posts`: `tipo: "carrossel"`, `titulo`, `midia` (URLs), `quando:
   "AAAA-MM-DDT12:00:00-03:00"` (dia de prova: 15h), `status: "agendado"`, `origem: "noticias"`, e a `legenda`: gancho forte,
   2–4 frases com os fatos, chamada para salvar/compartilhar, depois
   "📍 As inscrições da Mentoria MAPA 2027 estão abertas.\n👉 Link na bio.", "Fontes: ..." e 4–5 hashtags.
   Nunca mencionar live. Tom: próximo, direto, sem exagero.
   Inclua também o campo `previa`: `python3 previa.py slides/slide_*.jpg` (o Calendário de Posts não carrega
   imagens externas; sem a prévia, a notícia aparece sem imagens na página).
6. Rode a REVISÃO só da notícia criada.

## Regras
- Nunca escrever o token em arquivo, commit, log ou mensagem.
- Não alterar posts com `origem` diferente da rodada, exceto o `status` na publicação.
