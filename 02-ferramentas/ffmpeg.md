# FFmpeg

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** o canivete de vídeo e áudio: corta, converte, junta, extrai quadros, mede volume. Quase todo script do estúdio usa por baixo.

- **Como acessar:** `ffmpeg` e `ffprobe` no terminal.
- **Instalação:** Windows `winget install Gyan.FFmpeg`; Mac `brew install ffmpeg`.
- **Credenciais:** nenhuma.
- **Comandos mais usados:**
  - Quadro de um instante: `ffmpeg -i video.mp4 -ss 00:00:03.5 -frames:v 1 quadro.png` (o `-ss` depois do `-i` dá o quadro exato).
  - Volume final a −14 LUFS: `ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1:LRA=11 saida.wav` (para precisão, duas passagens).
  - Juntar áudio no vídeo: `ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k final.mp4`.
  - Informações: `ffprobe -v error -show_format -show_streams video.mp4`.
- **Pegadinhas:** caminho com acento ou "ç" quebra alguns renderizadores (não o FFmpeg em si); etiquete a cor (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`) ao juntar trechos.
- **Log:**
