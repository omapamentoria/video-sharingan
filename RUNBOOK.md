# Publicador automático do Instagram do MAPA

Fila única: **Calendário de Posts MAPA** — artifact `https://claude.ai/artifact/PfeNXpXEZcuZBFDyCdx3jw`,
banco do artifact, coleção `posts` (ler/escrever com a ferramenta ArtifactData).
Campos de cada post: `tipo` ("reel" | "carrossel"), `titulo`, `legenda`, `midia` (URLs públicas, na ordem),
`quando` (ISO com -03:00), `status` ("agendado" | "publicado" | "erro" | "rascunho"), `origem`.

Credenciais (só no ambiente, nunca em arquivo ou chat): `IG_ACCESS_TOKEN`, `IG_USER_ID`
(token do "login do Instagram"; host padrão graph.instagram.com). Mídia pública: branch `instagram-midia`
deste repositório, servida em `https://raw.githubusercontent.com/omapamentoria/video-sharingan/instagram-midia/<caminho>`.

## Rodada de PUBLICAÇÃO (12h, 15h, 19h)
1. Se `IG_ACCESS_TOKEN` não existir no ambiente: não publique nada; responda "sem token" e pare.
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

## Regras
- Nunca escrever o token em arquivo, commit, log ou mensagem.
- Não alterar posts com `origem` diferente da rodada, exceto o `status` na publicação.
