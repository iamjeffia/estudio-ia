---
name: som-do-video
description: Sound design e mixagem de vídeo no estúdio. Usar sempre que for dar som a um vídeo ou animação (efeito para cada elemento que entra ou sai, música, narração, mix final, som colado na prévia), montar ou ampliar a biblioteca de efeitos (sintetizar ou nivelar um pack), medir as batidas e o drop de uma música para cortar no tempo, separar a voz da música em stems ou conferir se o som de cena está alto demais antes de entregar. Vale para vídeo feito no After Effects, HyperFrames, Remotion ou editado à mão.
---

# Som do vídeo

> Data: 2026-10-22 · Tipo: skill · Status: vigente

**Resumo:** o som de um vídeo sai de uma lista de eventos (um por elemento que aparece, sai ou bate na tela) e de um comando, `som.py`, que põe cada efeito com o pico no quadro certo, assenta a música sob a voz e entrega a mix com relatório. O som não espera o render: com o tempo da animação assentado, ele já pode ser feito. Os números da mix têm um dono só, [06-metodo/regras.md](../../../06-metodo/regras.md); esta skill traz o método, os comandos e a tabela principal.

## Quando usar

- Qualquer vídeo com motion, interface, tutorial, anúncio ou vídeo só com música que precise de efeitos sincronizados.
- Vídeo narrado: voz seca na frente, música por baixo, efeitos discretos.
- Vídeo com pessoas ou lugares que parece "mudo": som de cena (ambiência e foley). Ver [references/som-de-cena.md](references/som-de-cena.md).
- Para tratar uma música: medir batidas e drop (`batida.py`) ou separar a voz (`separar.py`).

## O método

1. **Um som para cada ação visível, e o som descreve a ação.** Card que entra faz pop, botão faz clique, troca de tela faz whoosh, carimbo bate, número rola. Densidade é por ação, não por palavra: no máximo dois efeitos soando juntos sob a voz.
2. **Só entra som que a imagem motiva.** Whoosh em corte parado, relógio sem relógio na cena e riser sem nada subindo descolam o som do vídeo. Antes de mixar, olhe o vídeo e anote o que se mexe, quando e com que material.
3. **O pico cai no quadro do evento.** Clique, pop, carimbo e impacto: o pico no quadro em que o elemento toca. Whoosh: o pico no meio do gesto (~0,2 s depois do início; o mapa padrão já faz isso). Riser: termina seco no drop ou no corte.
4. **Tonal só em hype, transição e surpresa.** Golpe no tom no impacto, no carimbo e no logo; pad curto na transição grande; sino na revelação. Nunca em clique, pop ou tecla, que viram "musiquinha" e cansam. Passe `--tom` (ex.: `Am`) só quando a música tiver tom conhecido.
5. **Música por momentos, não um tapete.** Abertura suave; desaceleração antes do drop; respiro; clímax no bumbo. Com narração, a música fica bem abaixo da voz e sobe nos respiros e nos trechos sem fala.
6. **Respiro antes do drop.** O instrumental cai seco por ~0,3–0,5 s na última batida antes do drop (`--drop T` faz isso), e a palavra-chave ou a maior mudança de imagem vai no primeiro quadro do drop. Meça o drop com `batida.py`, não no olho.
7. **Camadas só nos picos.** 2–3 sons juntos no drop, no logo e no fecho; no resto, um som por ação. Varie a altura quando o mesmo som se repete (o mapa gira entre as variações da categoria).
8. **Voz seca.** Narração sem reverb nem eco.
9. **Ouça as camadas separadas.** O `som.py` grava `escuta/voz.wav`, `musica.wav`, `efeitos.wav` e `tonais.wav`. Sincronia se confere no stem de efeitos, nunca na mix.

## Números principais

Dono: [06-metodo/regras.md](../../../06-metodo/regras.md). Se lá disser outro número, vale o de lá. A Mesa já aplica estes valores sozinha.

| O quê | Valor |
|---|---|
| Master com voz ou música | **−14 LUFS** integrado, pico verdadeiro **≤ −1 dBTP** (limitador a 4×) |
| Música sob a voz | **~15 dB abaixo** quando há fala (o relatório mede; aceita 12–18) |
| Mix sem voz com música real | trilha nivelada a **−19 LUFS** antes dos efeitos; efeitos **×2,2**; limitador; master −14 |
| Peça só de som de cena | **−25 LUFS** integrado (teto −24), curto prazo ≤ −20, momentâneo ≤ −16, pico ≤ −3. Nunca normalizar a −14 |
| Som de cena com voz | stem do som de cena **≥ 15 LU abaixo da voz** |
| Biblioteca de efeitos | curtos −20 LUFS de pico momentâneo, camas −24, pico ≤ −3 dBTP; posição `at = evento − pico_ms/1000` |
| Sincronia | mediana ≤ 25 ms no stem de efeitos |
| Batidas | beat_this, `File2Beats(checkpoint_path="final0")`; corte a ≤ 2 quadros da batida |

## Passo a passo

Todos os comandos rodam da raiz do estúdio.

1. **Biblioteca pronta?** Se `05-biblioteca/som/sfx/catalogo.json` não existe: `uv run scripts/som/sintetizar_sfx.py`. Sons gravados: `uv run scripts/som/nivelar.py <pasta do pack>` (detalhes em [05-biblioteca/som/README.md](../../../05-biblioteca/som/README.md)).
2. **Eventos.** Exporte do motor de animação um `eventos.json` na pasta `audio/` do projeto. Formato, tipos aceitos e como exportar do After Effects, HyperFrames e Remotion: [references/eventos.md](references/eventos.md).
3. **Música com batida?** `uv run scripts/som/batida.py musica.mp3 --fps 30` dá BPM, tempos fortes e drop provável. Anime os cortes nessa grade.
4. **Precisa da voz ou do instrumental da música?** `uv run scripts/som/separar.py musica.mp3` (voz + instrumental) ou `--modo 6` (seis stems).
5. **Mix:**
   ```bash
   uv run scripts/som/som.py --eventos 04-projetos/<video>/audio/eventos.json \
     --voz 04-projetos/<video>/audio/voz.wav --musica 04-projetos/<video>/audio/musica.wav \
     --video 04-projetos/<video>/render/previa.mp4 --drop 12.4
   ```
   Sai `mix.wav`, `escuta/*.wav`, `relatorio-som.json` e `previa-som.mp4` (a imagem é copiada; só o som muda).
6. **Leia o relatório e corrija até não ter aviso.** "eventos sem som" = tipo que o mapa não conhece: troque o tipo por um conhecido, ponha `"som": "categoria"` no evento ou escreva um `--mapa` (abaixo). LUFS, pico e "música abaixo da voz" fora do alvo também aparecem.
7. **Som de cena?** `uv run scripts/som/verificar_som_de_cena.py <mix só de cena>` ou `... escuta/efeitos.wav --voz escuta/voz.wav`. Reprovado não vai para entrega.
8. **Ouça.** A prévia com som vai para o dono do estúdio aprovar. No vídeo final, rode o mesmo comando com `--video render/final.mp4`: é só remux, sem renderizar de novo.

### Sons próprios do projeto (`--mapa`)

Um arquivo `.py` com `MAPA = {tipo: função(M, e)}` sobrepõe o mapa padrão só nos tipos que você listar:

```python
# 04-projetos/<video>/audio/mapa.py
MAPA = {
    "logo": lambda M, e: (M.poe("logo", e["t"], -11), M.poe("impacto", e["t"], -16), M.golpe(e["t"], -20)),
    "moeda": lambda M, e: M.poe("sucesso/sucesso-2", e["t"], -14, st=3),   # st = semitons acima
}
```

Funções da Mesa que servem no mapa: `M.poe(som, t, ganho_db, pan, alinha="pico"|"ini"|"fim", st=semitons, fim=duração, fade=s, sala=True)`, `M.tonal(t, lufs)`, `M.golpe(t, lufs)`, `M.textura(t0, t1, lufs)`, `M.riser(t_pico)`. `som` aceita uma categoria (`"whoosh"`, gira entre as variações), um arquivo da biblioteca (`"whoosh/whoosh-2"`) ou um caminho.

## Comandos

| Script | Para quê |
|---|---|
| `uv run scripts/som/som.py --eventos E.json [--voz V] [--musica M] [--video P.mp4] [--tom Am] [--drop T] [--mapa mapa.py]` | a mix completa, o relatório e o som colado no vídeo |
| `uv run scripts/som/sintetizar_sfx.py [--amostra prova.wav]` | gera a biblioteca inicial sintetizada |
| `uv run scripts/som/nivelar.py PASTA [--categoria X] [--cama] [--destino D]` | põe um pack no padrão e atualiza o catálogo |
| `uv run scripts/som/verificar_som_de_cena.py MIX.wav [--voz VOZ.wav]` | reprova som de cena alto demais (código de saída 1) |
| `uv run scripts/som/batida.py MUSICA [--fps 30] [--json grade.json] [--video render.mp4]` | batidas, tempos fortes, BPM e drop (beat_this) |
| `uv run scripts/som/separar.py MUSICA [--modo voz\|6] [--saida PASTA]` | voz + instrumental (MelBand Big Beta 4) ou 6 stems (BS-RoFormer SW) |

Outras opções do `som.py`: `--voz-entra`, `--musica-entra`, `--musica-de` (alinhar trechos), `--dur`, `--impacto T0 T1` (música sobe ao nível da voz), `--lufs`, `--pico`, `--fx -10` (efeitos em LUFS relativos à voz), `--saida`.

`batida.py` e `separar.py` usam IA e precisam do extra: `uv sync --extra cpu` (ou `--extra gpu` com placa NVIDIA). Os modelos baixam sozinhos no primeiro uso (beat_this ~80 MB; cada modelo de separação ~300–700 MB, guardados em `~/.cache/estudio-ia/`). Sem o extra, os dois param com a instrução de instalação.

## Erros comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Efeitos "altos demais" num vídeo de cena | som de cena normalizado a −14 | `som.py` sem voz nem música já mira −25; confira com `verificar_som_de_cena.py` |
| Efeitos somem sob a música num vídeo sem voz | faixa masterizada (−8 a −11 LUFS) | a Mesa nivela a trilha a −19 e sobe os efeitos ×2,2; se ainda sumir, `vol` maior no evento |
| Som "atrasado" no whoosh | evento marcado no fim do gesto | marque o início do gesto; o mapa põe o pico 0,2 s depois |
| Mesmo som repetido parece robô | categoria com uma variação só | nivele mais sons naquela categoria ou use `st` diferente no `--mapa` |
| Relatório: "categorias trocadas" | a biblioteca não tem a categoria | rode `sintetizar_sfx.py` ou nivele um pack com ela |
