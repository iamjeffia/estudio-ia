# Eventos: o formato e como exportar de cada motor

> Data: 2026-10-22 · Tipo: referência · Status: vigente

**Resumo:** o `som.py` só precisa saber quando cada coisa acontece na tela e que tipo de coisa é. Este arquivo traz o formato do `eventos.json`, a lista de tipos que já têm som e um jeito de exportar do After Effects, HyperFrames e Remotion.

## Formato

```json
{
  "dur": 24.0,
  "eventos": [
    {"t": 0.50, "tipo": "logo"},
    {"t": 1.60, "tipo": "card"},
    {"t": 2.20, "tipo": "clique", "vol": 0.7, "pan": -0.4},
    {"t": 5.00, "tipo": "digitacao", "dur": 1.2},
    {"t": 7.40, "tipo": "transicao"},
    {"t": 9.10, "tipo": "qualquer", "som": "whoosh/whoosh-2", "ganho": -14}
  ]
}
```

| Campo | Obrigatório | O que é |
|---|---|---|
| `t` | sim | segundo do vídeo em que o elemento toca a tela (o quadro do evento ÷ fps) |
| `tipo` | sim | o que acontece; define o som pelo mapa padrão (lista abaixo). `kind` também é aceito |
| `vol` | não | multiplica o volume padrão: 1 = padrão, 0,5 = −6 dB, 2 = +6 dB |
| `pan` | não | −1 (esquerda) a +1 (direita); o mapa usa 60% disso, para ficar sutil |
| `dur` | não | nos sons contínuos (digitação, relógio, caneta), quanto tempo tocam |
| `som` | não | escolhe o efeito direto: categoria (`"pop"`), arquivo da biblioteca (`"pop/pop-3"`) ou caminho; `ganho` em dB (padrão −12) |

Uma lista simples `[{...}, {...}]` também vale; aí a duração sai do `--dur`, do `--video`, da voz ou do último evento + 2 s.

**Onde marcar o `t`:** no quadro em que o elemento pousa, bate ou aparece. Para movimento (troca de tela, card que voa), marque o início do gesto: o mapa já põe o pico do whoosh 0,2 s depois. Para riser, marque o instante do drop ou do corte: ele termina ali.

## Tipos com som padrão

Tipos com prefixo também valem (`pop-titulo` cai em `pop`). O mapa completo está em `scripts/som/mapa_padrao.py`.

| Família (categoria) | Tipos |
|---|---|
| pop | pop, card, bolha, balao, pilula, rotulo, widget, texto, credito, botao, estrela, anuncio, mini, item, chip, badge, entra, surge, bubble |
| clique | clique, clique-cta, liga, mira, campo, toque, tap, click, seleciona, trava, toggle |
| tecla / digitação | tecla, letras (4 teclas), palavra, digita, digitacao, typing, key |
| notificação | notifica, notificacao, mensagem, msg, alerta, notification, message |
| whoosh curto | whoosh, morph, pulo, volta, empurra, sobe, move, encolhe, sai, texto-sai, desliza, troca, colapsa, flip, wipe, swipe, slide, seta, titulo |
| whoosh grande (+ pad no tom) | transicao, viagem, chicote, salto, morph-grande, painel, mergulho, zoom, cta, sai-tela, transition |
| carimbo (+ golpe no tom) | carimbo, selo, carimbo-leve, aprovado, stamp |
| impacto (+ golpe no tom) | impacto, golpe, peso, drop, pancada, impact, hit, boom |
| logo (+ golpe no tom) | logo, marca, assinatura, marca-final |
| pouso | pouso, cai, aterrissa, land |
| papel | papel, foto, cartao, pagina, folha, paper |
| obturador | obturador, print, captura, screenshot, shutter |
| revelação (pop grave + sino no tom) | abre, iris, nasce, acende, revela, aparece, flash, reveal |
| contador | contador (rolagem de números); numero, valor, preco (pop agudo) |
| relógio | relogio, tempo, clock |
| sucesso | sucesso, ok, confirmado, check, etapa, success |
| caneta | caneta, risco, traco, circulo, sublinha, desenha, marca-texto, pen |
| rolagem | rolagem, scroll |
| riser | riser (termina em t), carregando, loading, scan, tensao (começa em t) |
| fita | fita, rebobina, tape |
| glitch | glitch, erro, error |
| brilho | brilho, sino, estrelas, magica, sparkle |

Tonais (golpe, pad, sino) só tocam quando o `som.py` recebe `--tom`.

## Exportar do After Effects

Marque cada evento com um **marcador de camada** (ou de composição) e escreva o tipo no comentário do marcador (`pop`, `clique`, `transicao`…). Depois rode este script em *Arquivo > Scripts > Executar arquivo de script…* com a composição aberta:

```javascript
// eventos.jsx: marcadores com comentário viram eventos.json
var comp = app.project.activeItem, ev = [];
function junta(m) {
  for (var k = 1; k <= m.numKeys; k++) {
    var tipo = m.keyValue(k).comment;
    if (tipo) ev.push('{"t": ' + m.keyTime(k).toFixed(3) + ', "tipo": "' + tipo + '"}');
  }
}
for (var i = 1; i <= comp.numLayers; i++) junta(comp.layer(i).property("Marker"));
junta(comp.markerProperty);
var f = File.saveDialog("Salvar eventos.json", "*.json");
if (f) { f.encoding = "UTF-8"; f.open("w"); f.write('{"dur": ' + comp.duration + ', "eventos": [' + ev.join(", ") + ']}'); f.close(); }
```

Se a camada começa depois do 0 da composição, o tempo do marcador já vem no tempo da composição; não precisa somar nada.

## Exportar do HyperFrames (ou qualquer animação em HTML/GSAP)

Os instantes já estão no código: são os mesmos números que você passa para a timeline (`tl.to(el, {...}, 1.6)`) ou para o `data-start` dos elementos. Junte-os numa lista ao lado da composição e grave o JSON. O jeito mais simples é manter a lista na própria página:

```javascript
// na composição, junto da timeline
window.__eventos = [
  { t: 0.5, tipo: "logo" },
  { t: 1.6, tipo: "card" },   // o mesmo 1.6 do tl.to(card, …, 1.6)
];
```

e copiar o resultado de `JSON.stringify({dur: <duração>, eventos: window.__eventos})` (console do navegador ou um script do Playwright) para `audio/eventos.json`. Quando um tempo mudar na animação, mude na lista e rode o `som.py` de novo.

## Exportar do Remotion

Guarde os eventos em quadros num arquivo compartilhado pela composição e por um script de exportação:

```ts
// src/eventos.ts
export const FPS = 30;
export const eventos = [
  { frame: 15, tipo: "logo" },
  { frame: 48, tipo: "card" },
];
```

```ts
// scripts/exportar-eventos.ts  (rodar com: npx tsx scripts/exportar-eventos.ts)
import { writeFileSync } from "node:fs";
import { eventos, FPS } from "../src/eventos";
writeFileSync("audio/eventos.json", JSON.stringify({
  eventos: eventos.map((e) => ({ t: e.frame / FPS, tipo: e.tipo })),
}, null, 1));
```

Use os mesmos `frame` dentro da composição (`<Sequence from={eventos[1].frame}>`), assim som e imagem nunca se desencontram. O `mix.wav` entra no Remotion como `<Audio src={staticFile("mix.wav")} />`, ou cole no render com `som.py --video`.

## Vídeo editado à mão

Anote os tempos assistindo ao vídeo (ou numa folha de contato a 10 quadros por segundo: `ffmpeg -i video.mp4 -vf "fps=10,scale=320:-1,tile=10x5" folha-%02d.png`) e escreva o JSON à mão. Dez eventos bem marcados valem mais que cinquenta no chute.
