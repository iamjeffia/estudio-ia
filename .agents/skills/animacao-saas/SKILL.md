---
name: animacao-saas
description: Padrão de animação SaaS e de produto para vídeos de lançamento, "apresentando", demonstração de software, anúncio estilo startup ou apresentação de loja e produto físico, narrados ou só com música. Uma forma só atravessa o vídeo e vira cada função do produto; câmera de controles encadeados com curva forte; legenda palavra por palavra que nasce na cor de destaque; botão que infla no drop; fecho que repete a abertura; morph de UI por tamanho e raio. Usar antes de planejar as cenas e de novo antes de renderizar, em qualquer motor.
---

# Animação SaaS: uma forma que vira o produto inteiro

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** padrão para vídeo de produto, lançamento e demo de software, e uma variante para loja ou produto físico. Uma forma atravessa o vídeo e se transforma em cada função; a câmera viaja num mundo contínuo; nada fica morto. O padrão é neutro de motor, com notas para After Effects, EffectCraft, HyperFrames e Remotion. Números de mola, mix e render em [regras.md](../../../06-metodo/regras.md).

Antes de planejar, siga a [video-referencias](../video-referencias/SKILL.md) (a marca real do produto vem do site e do kit oficial). Morph de UI em detalhe: [references/morph-de-ui.md](references/morph-de-ui.md). Lições de recriar peças de referência: [references/licoes-recriacoes.md](references/licoes-recriacoes.md).

## As peças do padrão

| Peça | Função |
|---|---|
| **Câmera de controles encadeados** | um controle pai faz a deriva viva, os filhos fazem os movimentos; a forma sabe onde está na tela para nascer exatamente onde o botão está |
| **Logo + título** | ícone revelado por varredura diagonal, luz que atravessa, giro, nome letra por letra; abre e fecha o vídeo |
| **Arco** | traço desenhado do centro para os lados, que vira a barra de prompt |
| **Barra de prompt** | itens sobem de dentro dela; digitação com rastro na cor de destaque; o campo rola antes do microfone |
| **Mão** | cursor posicionado pela ponta do dedo; o clique aperta a mão e o botão juntos |
| **Herói (a forma)** | um objeto `{cx, cy, w, h, r, cor}` que se transforma de fase em fase; o conteúdo de cada fase é recortado por ele |
| **Frase** | legenda palavra por palavra, recentrando em saltos, com um ponto condutor |
| **Órbita** | ferramentas reais (logos oficiais) entrando uma por vez ao redor de um centro, ligadas por pontilhado |
| **Faixas + fecho** | três faixas desfocadas sobem e limpam a tela; o fecho repete a abertura |
| **Fundo** | claro, com uma luz viva da cor de destaque e uma grade de pontos discreta |

## As regras (ponto de partida; vale o que for melhor para o estilo)

1. **Uma forma vira a próxima.** Nada de vários cards espalhados: a transição é tamanho, cantos, cor e conteúdo mudando. Em anúncio de produto rápido, corte seco no bumbo também serve; neste padrão, a forma que se transforma é o caminho natural.
2. **Um elemento por vez**, na sua vez (ou na palavra, se narrado).
3. **Curvas:** bezier (.86, 0, .07, 1) em câmera e troca de cena; bezier (.33, 0, .67, 1) em entradas; um "pop" com leve passada do ponto em balões e ícones. Movimentos de câmera se sobrepõem. **Entrada de elemento (cartão, botão, balão, notificação, selo) e morph de UI usam a mola padrão** de [regras.md](../../../06-metodo/regras.md).
4. **O botão infla com pausa:** círculo → quadrado (~0,28 s, leve passada do ponto) → espera ~0,08 s → card (~0,5 s). Sem narração, o clique cai no silêncio antes do drop e a inflada no drop.
5. **A cor de destaque nasce e some:** palavras e letras nascem na cor de destaque, com brilho, e viram a cor do texto em ~2 quadros.
6. **Container é máscara:** o conteúdo nasce de dentro da forma; texto digitado nunca passa por baixo de ícone.
7. **Sem quadro morto:** o conteúdo fica até a forma começar a mudar. Movimento e som contínuos; o respiro (tudo para, em suspense) só logo antes de uma revelação com batida.
8. **Modo claro**, identidade da marca do produto com **uma** cor de destaque, ícones e telas reais.
9. **Música real**, um efeito para cada ação que importa e camadas nos momentos principais (skill [som-do-video](../som-do-video/SKILL.md)).
10. **Magic move antes de qualquer troca:** o elemento que existe nas duas cenas viaja (avatar → linha da lista, botão → metade do seletor); o resto troca por desfoque curto. Texto nunca atravessa texto.
11. **Protagonista contínuo:** um objeto (ponto, cursor, mascote) atravessa todas as cenas e muda de papel; toda transição sai dele.

## Como fazer em cada motor

| Motor | Forma e morph | Câmera | Curvas e mola |
|---|---|---|---|
| **After Effects** | camada de forma com retângulo: anime **tamanho e arredondamento**, nunca a escala; conteúdo recortado por matte | cadeia de nulls (pai = deriva, filhos = movimentos) com câmera 2D ou 3D | influência dos keyframes para as bezier; mola por expressão. Com o Motion Kit AE, use as operações prontas de mola e morph (o kit transforma uma camada em outra com mola) e revise com a ferramenta de revisão de movimento |
| **EffectCraft** | as mesmas ideias: camada de forma ou sólido com tamanho e raio animados | camadas pai encadeadas | descubra os comandos com `command_list`, aplique com `command_run`, confira com `render_preview` |
| **HyperFrames** | um `div` com `width`, `height`, `border-radius` e cor animados; `overflow: hidden` como máscara | um wrapper "mundo" transformado pela câmera | uma timeline GSAP pausada e controlada pelo tempo; bezier com `CustomEase` (`"M0,0 C.86,0 .07,1 1,1"`); mola como função do tempo (veja a skill `hyperframes-animation`) |
| **Remotion** | componente `Forma({cx, cy, w, h, r, cor})` com valores de `interpolate` | componente `Mundo` com transform da câmera | `Easing.bezier(.86, 0, .07, 1)`; `spring()` para a mola |

Em código, tudo é função do quadro: nada de `setTimeout`, relógio real ou animação CSS solta, para o mesmo quadro sair igual em todo render.

## Variante: loja ou produto físico

Para "apresentando…" de loja, marca ou produto físico, a estrutura tem 6 atos:

1. celular real com o site da loja;
2. túnel 3D de cards dos produtos;
3. botão que infla e vira o estúdio, com os produtos (caixa que abre, chicotes no compasso);
4. card que vira o chip da frase;
5. sacola com tudo;
6. logo.

Acabamento Apple: texto subindo pela máscara em negrito, cinzas de sistema no secundário, vidro com borda sutil, sombras discretas e leve relevo no logo.

## Narrado ou sem narração

- **Sem narração:** o tempo vem da trilha (drop, compassos, meias batidas). Meça com `uv run scripts/som/batida.py` e guarde as batidas como dado (`b(compasso, tempo, fração)`), sem número de quadro solto nas cenas. Um conceito por compasso, um evento por batida.
- **Narrado:** o tempo vem da fala (tempos por palavra). Siga também a [motion-narrado](../motion-narrado/SKILL.md): a frase segue as palavras ditas, com tempo de leitura; narração seca; abertura musical, se houver, antes da fala.

## Antes de animar e antes de entregar

- Briefing nas seções fixas e storyboard aprovado: molde na [estudio-video](../estudio-video/SKILL.md).
- Prévia a meia resolução, quadros cheios nos momentos críticos, folha de contato e recortes ampliados.
- `uv run scripts/video/detectar_saltos.py` no render; comparação lado a lado com a referência ("o original grita mais?").
