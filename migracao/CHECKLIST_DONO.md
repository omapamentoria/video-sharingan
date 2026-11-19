# Checklist: levar o publicador para o Claude da empresa

Faça na ordem. Os itens marcados com ★ só você consegue fazer. O Claude novo te guia no resto.

## Antes de começar
- [ ] ★ **GitHub**: na conta da empresa, abra claude.ai/code e conecte o GitHub com um usuário que tenha acesso de
      escrita ao repositório `omapamentoria/video-sharingan`. Se o app do Claude não estiver instalado nesse
      repositório, instale em github.com/apps/claude.
- [ ] ★ **Token do Instagram**: tenha em mãos o token da API do Instagram (login do Instagram) da @omapamentoria.
      Ele sai do painel de desenvolvedor da Meta e dura uns 60 dias. Não mande o token no chat.
- [ ] ★ **Conectores** (claude.ai → Configurações → Conectores) na conta da empresa:
  - [ ] Google Drive, com acesso à pasta "CRIATIVOS MAPA 2027";
  - [ ] Claude Docs, para ler a planilha.
- [ ] ★ **Compartilhar com a conta da empresa**, se ela ainda não for dona:
  - [ ] página do roteiro: claude.ai/artifact/LzEcaehDNmrc23ouJWbXRK
  - [ ] planilha: claude.ai/artifact/UVmZJgpB4Vhpk6r4B5dUBe
- [ ] Habilidades (skills): nenhuma é obrigatória para o publicador.

## Instalação (no Claude Code da empresa)
1. [ ] Abra uma sessão nova em claude.ai/code com o repositório `omapamentoria/video-sharingan`.
2. [ ] Cole o texto de `migracao/PROMPT_NOVO_CLAUDE.md` (do `---` para baixo).
3. [ ] ★ Quando ele pedir, cole o token em Configurações do ambiente → Variáveis de ambiente, como
       `IG_ACCESS_TOKEN=...`. Depois abra uma sessão nova.
4. [ ] Aprove as propostas de rede e de setup script que ele fizer.
5. [ ] Ele recria o **Calendário de Posts** nessa conta, com os 95 posts importados, e te passa o link novo.
6. [ ] Ele roda os testes (conferir token, gerar notícia e carrossel de teste) e te mostra as imagens.

## Virada sem post duplicado
7. [ ] ★ Escolha um horário fora das rodadas (por exemplo, depois das 21h31).
8. [ ] ★ Aqui, nesta conta antiga, me diga **"pause as rotinas"**. Eu desligo as 6 rotinas daqui.
9. [ ] ★ Lá, diga **"pode ligar"**. Ele cria as 6 rotinas de `migracao/rotinas.json`.
10. [ ] No dia seguinte, confira se as rodadas das 12h, 15h e 19h saíram de lá.

## Depois
- [ ] Quando o token vencer (erro 190), gere outro e troque a variável de ambiente.
- [ ] Os vídeos do roteiro vão para a mesma pasta do Drive, com o número no começo do nome (ex.: `012 - ...mp4`).
