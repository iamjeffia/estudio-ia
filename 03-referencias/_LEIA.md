# 03-referencias: jogue tudo aqui, a IA organiza

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** a biblioteca de referências do estúdio. Você joga vídeos, prints, links, músicas e logos na pasta `_entrada/`; a IA olha cada arquivo, coloca na categoria certa, registra no `catalogo.md` e escreve a análise quando a referência merece. A mídia pode ficar aqui ou numa pasta do Google Drive (o roteiro `setup/3-referencias.md` configura).

## Onde está a mídia

O arquivo [ONDE.md](ONDE.md) diz se a mídia fica nesta pasta ou no Google Drive, e o caminho exato. A IA sempre lê esse arquivo antes de procurar ou mover referências. As análises (`analises/`) e o `catalogo.md` ficam sempre aqui, versionados no git; a mídia pesada nunca entra no git.

## Categorias

| Pasta | O que vai nela |
|---|---|
| `_entrada/` | Tudo que chegou e ainda não foi organizado. Links soltos vão em `_entrada/links.md`, um por linha |
| `motion/` | Vídeos e GIFs de animação, transições, câmera, tipografia animada |
| `som/` | Músicas, efeitos, trilhas e edits cujo som você quer copiar |
| `design/` | Telas de app, sites, UI, tipografia, paletas, prints de interface |
| `anuncios/` | Anúncios e campanhas (vídeo ou imagem) |
| `marcas/` | Logos e identidades (de preferência SVG ou PNG transparente) |
| `fotos/` | Pessoas, lugares, produtos, texturas |
| `analises/` | Um `.md` por referência analisada (sempre local) |

## Como a IA organiza (`scripts/referencias.py`)

1. `uv run scripts/referencias.py novos` lista o que está em `_entrada/` com tipo, duração e resolução, e baixa os links de `_entrada/links.md` com o yt-dlp.
2. Para cada vídeo, `uv run scripts/referencias.py olhar <arquivo>` gera uma folha de contato (quadros lado a lado) para a IA ver o conteúdo antes de classificar. Para entender o áudio ou o vídeo inteiro, use a skill `watch`.
3. `uv run scripts/referencias.py mover <arquivo> <categoria> --tags "tag1, tag2" --nota "o que tem de bom"` renomeia para `AAAA-MM-DD-assunto.ext`, move e acrescenta a linha no `catalogo.md`.
4. Referência que vai guiar um vídeo ganha análise em `analises/AAAA-MM-DD-assunto.md`: o que acontece, segundo a segundo, o que copiar (movimento, tempo, som, cor) e o link de origem.

## Como achar uma referência

`rg -i "mola|transição" 03-referencias/catalogo.md` ou peça à IA: "acha referências de transição com mola para um Reel de produto".
