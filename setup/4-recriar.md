# Roteiro 4: o primeiro vídeo, recriando um que já existe

> Data: 2026-11-14 · Tipo: guia · Status: vigente

**Resumo:** instruções para a IA conduzir a primeira recriação: a pessoa escolhe um vídeo de motion feito por um motion designer humano, a IA assiste quadro a quadro, documenta tudo o que precisa para recriar, recria cena por cena e compara com o original em câmera lenta até ficar igual. Cada acerto vira documentação no segundo cérebro. Vem depois dos roteiros 1, 2 e 3. Pronto quando o lado a lado em câmera lenta estiver aprovado pela pessoa e os acertos estiverem em `06-metodo/aprendizados.md`.

## Por que começar recriando

Ninguém aprende a desenhar inventando um estilo: copia um desenho que admira, traço por traço, até entender como foi feito. Com motion é igual. Num vídeo de motion designer humano está a técnica de verdade: o tempo de cada movimento, a câmera, as transições naturais. Recriar ensina isso à sua IA melhor do que qualquer prompt.

## O prompt

Copie o link do vídeo (YouTube, Instagram, TikTok ou um projeto aberto do Clube do Motion), abra a sua IA na pasta do estúdio e cole, trocando `[LINK]`:

```text
Baixe o vídeo deste link e assista com a skill watch, quadro a quadro em todos os trechos com movimento: [LINK]. Documente no segundo cérebro tudo o que precisa para recriá-lo do zero: o contexto, a transcrição (se tiver fala) e cada animação isolada, com o movimento de câmera, as transições, os elementos, os efeitos sonoros, as cores e a tipografia. Depois, recrie o vídeo no After Effects, cena por cena, e me mostre o original e a recriação lado a lado em câmera lenta.
```

**Insista no FRAME A FRAME.** A IA perde essa instrução com frequência e volta a olhar só alguns quadros soltos. Se a análise vier rasa ("a câmera faz um zoom suave"), cobre: "assista frame a frame os trechos com movimento e me diga quadro por quadro onde cada peça está". Só assim ela pega os movimentos completos.

## Para a IA: como conduzir

Português simples. Você executa; a pessoa escolhe o vídeo e aprova cada rodada. Abra um projeto em `04-projetos/AAAA-MM-DD-recriacao-<nome>/` com este checklist no `README.md`.

### 1. Baixar e assistir

1. Baixe com a skill `watch` (ou `yt-dlp`) para `04-projetos/<projeto>/referencias/original.mp4`. Anote duração, resolução e quadros por segundo (`ffprobe`).
2. Assista o vídeo inteiro uma vez com a skill `watch` para entender o contexto e a estrutura.
3. **Depois, quadro a quadro, sem pular** nos trechos com movimento:
   - `uv run scripts/video/olho_quadro_a_quadro.py folha original.mp4 --ini A --fim B --saida folha-A.jpg` (quadros seguidos, numerados);
   - `ampliar` para detalhe fino (brilho, contorno, degradê); `rastro` para ver o que mudou entre quadros;
   - `camera` para a curva da câmera (posição, rotação e escala por quadro).
   A análise automática erra detalhe: confira tudo no quadro antes de anotar.

### 2. Documentar no segundo cérebro

Em `04-projetos/<projeto>/recriacao.md`:

- **Contexto:** o que o vídeo é, para quem, duração.
- **Transcrição**, se tiver fala, com o tempo de cada frase.
- **Cada animação isolada**, uma por linha: em que quadro começa e termina, de onde vem, para onde vai, a curva (rápida no começo? passa do ponto e volta?), e como sai.
- **Movimento de câmera**, **transições** (corte, fusão, um elemento que vira o próximo), **elementos** (ícones, cards, fotos: de onde tirar o real), **efeitos sonoros** (o que soa em cada ação), **cores** (códigos) e **tipografia** (fonte, peso, tamanho).

Nada de "parecido": quadro, tempo e número.

### 3. Recriar cena por cena

- No After Effects, se a pessoa tiver (ponte da IA pelo `https://clubedomotion.com/kit-ae`, ver roteiro 2). Sem After Effects, no HyperFrames ou no Remotion, que o roteiro 2 já instalou.
- Uma cena por vez, na ordem. Comece por uma **cena piloto** e só escale depois que a pessoa aprovar o lado a lado dela.
- Use os tempos e as curvas que você documentou. Ícones e imagens reais, não inventados.

### 4. Comparar lado a lado em câmera lenta

```bash
ffmpeg -i original.mp4 -i recriacao.mp4 -filter_complex "[0:v]scale=540:960,setsar=1[a];[1:v]scale=540:960,setsar=1[b];[a][b]hstack[v]" -map "[v]" -map 0:a? -c:v libx264 -crf 18 comparativo.mp4
ffmpeg -i comparativo.mp4 -vf "setpts=3*PTS" -an -c:v libx264 -crf 18 comparativo-3x-lento.mp4
```

Compare **no meio do movimento**, não em quadro parado: dois quadros parados iguais escondem curvas diferentes. Para a câmera, `olho_quadro_a_quadro.py compara ref_cam.csv rec_cam.csv` mostra as duas curvas no mesmo gráfico.

### 5. Corrigir medindo de novo

Quando a pessoa apontar um trecho ("aqui não ficou igual"), volte àqueles quadros no original, meça de novo e corrija. A descrição dela é pista, não medida: meça antes de mudar. Renderize, monte o lado a lado e mostre de novo. Repita até ela aprovar.

### 6. Salvar os acertos

Cada acerto vira uma entrada em `06-metodo/aprendizados.md`: uma transição bem feita, um movimento de câmera humanizado, ícones reais em vez de falsos, a entrada e a saída de cada animação, a trilha e os efeitos sonoros. Número que vale sempre sobe para `06-metodo/regras.md`. No próximo vídeo, essa documentação já está lá.

## O que este modelo ainda não tem

A medição automática de cada peça (rastrear posição, escala e rotação de cada elemento em cada quadro e virar chave no After Effects) não vem neste modelo. Aqui a medição é pelo olho quadro a quadro, pela curva da câmera e pela comparação lado a lado. Funciona, só pede mais rodadas de ajuste.
