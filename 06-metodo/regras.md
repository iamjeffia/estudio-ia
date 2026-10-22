# Regras do estúdio: os números que valem

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** fonte única dos números técnicos de vídeo (mola, câmera, ritmo, volume, render, revisão). Quando uma skill, tutorial ou conversa disser outro número, vale este arquivo. São pontos de partida testados, não proibições: se a peça pedir outro valor, use e anote no projeto. Mudou um número de vez? Atualize aqui, com a data.

## Movimento

| Regra | Valor de partida |
|---|---|
| Mola padrão (card, botão, balão, notificação, selo) | sobe ~12% além do alvo e assenta em ~0,6 s. No After Effects: chaves lineares 0→100 em 0,25 s + expressão de inércia (amplitude 0,05 · frequência 2 · decaimento 4) |
| Mola em código (HTML, Remotion) | `1 − e^(−ζωt)(cos ω_d·t + (ζω/ω_d)·sen ω_d·t)` com ζ 0,56 e ω ≈ 12; interface mais firme: ζ 0,62–0,78 e ω 13–17. Valor com vários alvos = soma de uma mola por mudança |
| Curva de câmera e troca de cena | cubic-bezier(.86, 0, .07, 1) para trocas rápidas; (.33, 0, .23, 1) para câmera viajando num quadro contínuo |
| Câmera nunca morta | deriva contínua lenta + balanço suave num objeto pai. Parada completa só de propósito, em 2 ou 3 momentos-chave, e anotada no projeto |
| Câmera com propósito | todo movimento além da deriva tem início, fim, curva e um porquê. Nenhum movimento abaixo de ~0,8 s, exceto chicote (~0,27 s) e mergulho em Z (~0,37 s) |
| Entrada e saída | entrar já em movimento (desacelerando); sair acelerando ou com desfoque, cortando no pico. No máximo um quadro congelado |
| Nada antes de ser dito | o elemento entra quando a palavra é falada; a tela só troca depois da fala |
| Ritmo | algo novo a cada ~1 s; troca de cena a cada ~2 s, na primeira palavra da frase; nunca mais de 1,5 s sem nada mudar. Tutorial narrado: storyboard primeiro, cada elemento com propósito, sem poluir |
| Texto de destaque | sempre com acabamento: degradê, brilho, textura ou contorno |
| Digitação na tela | teclado subindo e teclas reais; nunca texto "esticando" por máscara |
| Motion blur | telas e UI: obturador de 70° e fase de 40°; câmera rápida pode ir a 180° |

## Áudio

| Regra | Valor de partida |
|---|---|
| Volume final (narrado) | −14 LUFS integrado, pico real ≤ −1 dBTP; normalizar com `loudnorm` em duas passagens |
| Música sob a voz | ~15 dB abaixo da voz, com volume estável (variação de curto prazo ≤ 2–3 dB) |
| Faixa real num mix sem voz | nivelar o trecho a −19 LUFS antes de somar os efeitos, efeitos ×2,2, limitador e então −14 LUFS |
| Efeitos sonoros | biblioteca nivelada (`scripts/som/nivelar.py`); volume relativo à voz entre 0,2 e 0,6 |
| Sincronia do efeito | `início = evento − pico_ms/1000` (o pico de cada arquivo fica no `catalogo.json` da biblioteca). Alvo: erro mediano ≤ 25 ms |
| Som de cena (ambiência, passos, objetos) | peça só com som de cena: −25 LUFS integrado; com voz, pelo menos 15 LU abaixo dela. Conferir com `scripts/som/verificar_som_de_cena.py` |
| Som que descreve a ação | cada movimento tem o som do que se vê, com a duração do gesto. Som tonal (nota musical) só em momento de hype, troca de cena ou surpresa |
| Batida da música | medir com `scripts/som/batida.py` (beat_this) antes de cortar na batida; o BPM de catálogo costuma estar errado |
| Respiro antes do drop | zerar o instrumental ~0,5 s antes do drop e pôr a palavra-chave no primeiro quadro dele |
| Voz | narração seca, sem reverb nem eco |

## Render e revisão

| Regra | Valor de partida |
|---|---|
| Ciclo de render | prévia leve a cada ajuste (sem desfoque, meia resolução); final uma vez; depois, só o trecho que mudou |
| Caminho do render | pasta sem acento nem "ç" (alguns renderizadores quebram); pasta de saída nova por vídeo |
| Motion blur em HTML | renderizar a 240 qps e juntar 4 quadros em 1 (`tmix=frames=4`) para sair a 60 qps |
| Cor | etiquetar BT.709 na junção (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`) |
| Extrair quadros para revisar | `ffmpeg -i video.mp4 -ss <tempo> ...` (o `-ss` depois do `-i`) |
| Depois de todo render | `scripts/video/detectar_saltos.py`: todo salto que sobrar tem que ser corte de propósito |
| Comparação final | referência e o seu vídeo lado a lado, mesmo tamanho. Além de "está humano?", pergunte "a referência grita mais?" |
| Texto na tela | interface com pelo menos 22 px de texto num vídeo 1080p |
