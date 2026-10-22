# Roteiro 3: a pasta de referências

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** instruções para a IA criar o lugar onde a pessoa joga todas as referências (vídeos, prints, links, músicas, logos), numa pasta do computador ou no Google Drive, e mostrar à pessoa como a IA organiza o que chega. Pronto quando o `ONDE.md` estiver preenchido, as categorias existirem e uma referência de teste tiver passado por `novos`, `olhar` e `mover`.

## Para a IA: como conduzir

Conduza como nos roteiros anteriores: português simples; você executa, a pessoa decide e faz o login. Tempo esperado: 5 minutos (mais o tempo de login no Drive, se for o caso).

### 1. Pergunte onde a mídia vai ficar

Faça uma pergunta só, com as duas opções:

- **Pasta no computador** (`03-referencias/` dentro do estúdio): mais simples e rápida; ocupa espaço no disco.
- **Google Drive**: a pessoa joga referências pelo celular (compartilhar → Drive) e acessa tudo de qualquer computador; os arquivos só são baixados quando a IA os abre.

As análises e o `catalogo.md` ficam sempre na pasta do estúdio, versionados. Só a mídia muda de lugar.

### 2a. Se for pasta no computador

1. Preencha o `03-referencias/ONDE.md`: data de hoje, `Status: vigente`, `Modo: local`, `Caminho da mídia: 03-referencias`.
2. Rode `uv run scripts/referencias.py criar`.

### 2b. Se for Google Drive

1. **Google Drive para computador instalado?**
   - Windows: procure uma unidade com a pasta `My Drive` ou `Meu Drive` (`Get-PSDrive -PSProvider FileSystem`, normalmente `G:`). Sem ela: `winget install --id Google.GoogleDrive -e`.
   - Mac: `ls ~/Library/CloudStorage/` mostra `GoogleDrive-<conta>`. Sem ela: `brew install --cask google-drive`.
2. **Login:** abra o Google Drive e peça para a pessoa entrar com a conta dela. Espere a pasta aparecer.
3. Crie a pasta `Estudio IA/referencias` dentro de `My Drive` (ou `Meu Drive`). Caminho típico:
   - Windows: `G:\My Drive\Estudio IA\referencias`
   - Mac: `~/Library/CloudStorage/GoogleDrive-<conta>/My Drive/Estudio IA/referencias`
4. Preencha o `03-referencias/ONDE.md`: data, `Status: vigente`, `Modo: google-drive` e o **caminho absoluto** no `Caminho da mídia`.
5. Rode `uv run scripts/referencias.py criar` e confira se as pastas apareceram no Drive.
6. Ensine o atalho do celular: no Instagram, no TikTok ou no YouTube, "Compartilhar → Drive → Estudio IA/referencias/_entrada". Outra opção é colar o link num arquivo `links.md`.

### 3. Traga o que a pessoa já tem

Pergunte se ela já guarda referências em algum lugar (Downloads, uma pasta solta, salvos do Instagram, uma pasta do Pinterest). Se sim, copie os arquivos para `_entrada/` (copiar, não mover, até ela conferir).

### 4. Faça uma rodada de organização como teste

1. `uv run scripts/referencias.py novos` lista o que está em `_entrada/` e baixa os links de `03-referencias/_entrada/links.md`.
2. Para cada vídeo, `uv run scripts/referencias.py olhar <arquivo>` gera a folha de contato; abra a imagem e veja o que há no vídeo. Para entender o áudio ou o vídeo inteiro, use a skill `watch`.
3. Classifique e mova: `uv run scripts/referencias.py mover <arquivo> <categoria> --tags "..." --nota "o que tem de bom" --origem <link>`.
4. Se não houver nada para organizar, faça o teste com um arquivo qualquer (um print da tela, por exemplo) e apague-o depois.
5. Mostre à pessoa o `03-referencias/catalogo.md` com as linhas novas.

### 5. Termine

1. Explique o uso do dia a dia em três passos: a pessoa joga o material em `_entrada/`, pede "organiza minhas referências" e, na hora de fazer um vídeo, pede "acha referências de <estilo> no catálogo".
2. Dê dicas de fontes por tipo: telas e interfaces no Mobbin ou no Dribbble; anúncios e fotos no Pinterest (busca por palavras curtas, não por frase); motion no Instagram e no YouTube de quem a pessoa admira.
3. `uv run setup/conferir.py` deve marcar "Pasta de referências".
4. Faça o commit local (`git add -A && git commit -m "Referências configuradas"`) e registre a anotação da sessão.
5. O estúdio está pronto. O próximo passo é o primeiro vídeo: a pessoa pede "vamos fazer um vídeo sobre <assunto>", e a IA segue o `06-metodo/video-do-zero.md`.
