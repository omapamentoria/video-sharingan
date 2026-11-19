# Contexto do publicador MAPA (estado em 19/11/2026)

Leia junto com o `RUNBOOK.md`. Se os dois discordarem, vale o RUNBOOK. Este arquivo explica o porquê das regras e o
que estava em andamento na migração.

## Endereços
- Repositório: `omapamentoria/video-sharingan`.
  - Ramo `mapa-posts`: scripts, RUNBOOK e relatórios.
  - Ramo `instagram-midia`: imagens e vídeos publicados.
    URL pública: `https://raw.githubusercontent.com/omapamentoria/video-sharingan/instagram-midia/<caminho>`.
  - Fluxo de trabalho com a mídia:
    ```
    S=<scratchpad>
    git fetch origin instagram-midia
    git worktree add -B instagram-midia $S/wt origin/instagram-midia
    ```
    Depois copie a mídia para `$S/wt/<pasta>/`, faça commit e `git push origin instagram-midia`.
    Antes de agendar, confira que o link raw responde 200.
- Calendário de Posts (fila): https://claude.ai/artifact/32aVhi2usJ6EUvW8FrFC2r, coleção `posts` (recriado em 19/11 na conta da empresa). Antigo, só leitura:
  `https://claude.ai/artifact/PfeNXpXEZcuZBFDyCdx3jw`.
- Roteiro + calendário editorial (vídeos 001–070, de 12/11 a 31/01): https://claude.ai/artifact/LzEcaehDNmrc23ouJWbXRK
- Planilha (Claude Sheets; ler pelo conector Claude Docs, `guide` → topic.sheets): https://claude.ai/artifact/UVmZJgpB4Vhpk6r4B5dUBe
- Drive dos vídeos brutos: pasta "CRIATIVOS MAPA 2027", id `1kIWZiVcthuAMYoiXQUhWgm7i8uMF_zLQ`.
  - Até 19/11 estava vazia.
  - Listagem sem conector:
    ```
    curl -sSL "https://drive.google.com/embeddedfolderview?id=1kIWZiVcthuAMYoiXQUhWgm7i8uMF_zLQ#list" | grep -o 'flip-entry-title">[^<]*'
    ```

## Grade (decisão do dono, 13/11)
- **12h**: notícia do dia. Só se for forte e tiver fonte oficial; senão, um Reel da agência (`reel-AAAA-MM-DD-12h`).
- **15h**: Reel da agência (`plano_reels.json`).
- **19h**: conteúdo do roteiro (artifact LzEc…).
  - É a prioridade, porque é o que tem mais alcance.
  - Se o dia tiver 2+ posts do roteiro, o extra ocupa as 15h no lugar do Reel da agência.
  - Enquanto os vídeos do roteiro não chegam no Drive, as 19h usam os carrosséis da agência já agendados.
- **Dias de prova** (8/11, 15/11, 6/12 e 13/12):
  - carrossel "Boa prova" às 12h;
  - notícia às 15h, mas não no dia do ENEM;
  - sem Reel da agência.
- **Carrosséis**: quem faz é você.
  - O conteúdo sai da página do roteiro e da planilha; o dono não manda texto.
  - Visual claro do MAPA: `carrossel/gerar.py`, até 10 slides.
- **Notícia**: modelo escuro "Plantão MAPA", aprovado pelo dono. Usa `noticia_post.py` e depois `previa.py`, que gera a
  prévia em data URI para o calendário, já que o artifact não carrega imagem externa.

## Regras do dono
- Nada inventado.
  - Os [colchetes] do roteiro só se preenchem com dado real.
  - Post de resultado só com material real e nomes borrados.
  - Nada de encenação.
- Rostos da marca: Matheus e Nando. Mentores: Arthur (SSA), Letícia (ENEM) e Breno (FPS).
- Post fora da rotina (fotos de alunos, colagem, prints): mostre a prévia e espere o "aprovado".
- Assinatura:
  - Não use o rodapé "@omapamentoria" nem "MAPA Mentoria" escrito embaixo das fotos.
  - Use o emoji Ⓜ️ no lugar de 💙.
- **Lote Black Friday**: o 1º lote já foi lançado pelo time por volta de 17/11. Não anuncie "lançamento" de novo.
  Preço, vagas e prazo só com o dado que o dono mandar.

## Aprendizados de desempenho
Relatórios em `relatorios/desempenho-*.md`; o plano está em `relatorios/planejamento-2026-11-14_30.md`.
- Os posts com mais engajamento são de **pessoas, bastidores e aulão**. O melhor post até agora foi a colagem de
  fotos e prints "energia" do dia do ENEM.
- Carrossel de fórmulas tem muitos salvamentos.
- Notícia e carrossel institucional da agência rendem pouco (nota ~20).
- Seguidores: 1575 → 1658 (13 a 16/11).
- Toda segunda, às 7h, rode `python3 desempenho.py <export_publicados.json> <pasta>` e use o resultado para planejar.
  Pesos: curtida 1, comentário 3, salvamento 3, compartilhamento 4, seguidor 10.

## Pendências em 19/11
- Hoje, 19/11:
  - 15h: `reel-2026-11-19` (pegadinha do coco);
  - 19h: `car-2026-11-19`.
- Dados reais que faltam pedir ao dono:
  - acertos por área (post de 21/11);
  - antes/depois do simulado (24/11);
  - preço, vagas e prazo do lote Black Friday (posts de 27/11 e 30/11).
- `car-2026-11-25` ("Letícia: a primeira aluna do MAPA"): liberado pelo dono em 19/11, pode publicar.
- Segunda 23/11: rodada de desempenho.
- Os vídeos 001–070 do roteiro ainda não chegaram no Drive. Quando chegarem:
  - edite os Reels com ffmpeg;
  - legende com `migracao/transcrever.py` (faster-whisper);
  - publique às 19h, na ordem do calendário do roteiro.

## Como gerar
- **Notícia**:
  ```
  python3 noticia_post.py spec.json pasta
  python3 previa.py pasta/slide_*.jpg > previa.out
  ```
  O formato do spec está no topo do script.
- **Carrossel**:
  ```
  python3 carrossel/gerar.py spec.json pasta
  ```
  Se o Python não tiver playwright, o script gera o HTML e tira o print com `node carrossel/shot.js` (Playwright do
  Node, já instalado no Claude Code na nuvem).
- **Publicar, conferir e verificar**: os comandos estão no RUNBOOK. `publicar.py` evita publicar duas vezes a mesma
  legenda dentro de 36 h.

## Problemas já vistos
- O ArtifactData às vezes dá 502/503: tente de novo depois de alguns minutos.
- Se o worker reiniciar e uma rodada se perder, a verificação seguinte publica o atrasado. Foi o que aconteceu em
  18/11, quando o post saiu às 15h10.
- Glifos que faltam na Poppins (setas, bullets) foram desenhados como formas.
- Texto que estoura o cartão: os geradores já reduzem a fonte sozinhos.
