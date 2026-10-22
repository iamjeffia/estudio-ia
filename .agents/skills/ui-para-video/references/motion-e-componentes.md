# Motion e componentes prontos para interface

> Data: 2026-10-22 · Tipo: referência · Status: vigente

**Resumo:** quando a tela precisa de movimento, ícone vivo ou componente de IA, confira estas bibliotecas antes de escrever animação à mão. Todas são públicas; preços e licenças mudam, então confira no site antes de usar.

## O que usar

| Precisa de | Use | Como |
|---|---|---|
| Transição de abrir e fechar (modal, dropdown, painel, toast, abas, tooltip, accordion, toggle, check de sucesso, tremida de erro, skeleton) | **transitions.dev** | skill `transitions-dev`, se instalada; ou as receitas do site |
| Revisar e afinar o movimento que já existe | skill `transitions-polish` | se instalada |
| UI aparecendo como se a IA estivesse gerando (wireframe pontilhado → tela) | skill `transitions-ui-generation` | funciona em HTML puro |
| Ícone que vira outro (menu ↔ X, play ↔ pause, copiar ↔ check) | **morphicons** | `npm i morphicons lucide` |
| Ícone que se mexe no hover (carrinho, coração, sino, enviar) | **itshover** | componentes instaláveis via shadcn (precisa de `motion`) |
| "Pensando", borda de luz, voz, avatar de bot, imagem sendo gerada | **libraries.dev** | skill `libraries-dev`, se instalada; pacotes npm do site |
| Microinteração rica (ilha dinâmica, toast em pilha, like com contador, código OTP, upload, reações) | **bencho** | blocos com código no site |
| Tela de agente de IA (pensando, streaming, aprovação, chamadas de ferramenta, prompt bar) | **beautifului** | componentes via shadcn |

## Régua de movimento de interface

- **Durações:** ~150 ms para fechar ou trocar texto; ~250 ms para abrir (modal, dropdown, aba, ícone); 350 a 400 ms para painel e toast; ~500 ms para ênfase (badge, check). Stagger de ~40 ms, total abaixo de ~300 ms.
- **Curvas:** padrão `cubic-bezier(0.22, 1, 0.36, 1)`; pop de entrada `cubic-bezier(0.34, 1.36, 0.64, 1)`.
- **Regras:** fechar é mais rápido que abrir; bounce só na entrada; nunca atrasar um fechamento; translação acima de ~40 px fica arrastada.
- **Escala e blur:** escala de entrada de 0,96 a 0,99; blur de ~2 px em troca de texto ou ícone.
- **Molas de UI:** rígida (~400 de rigidez, ~32 de amortecimento, assenta em ~0,4 s) e suave (~180 / 26).
- **Acessibilidade:** em página, respeite `prefers-reduced-motion`.

Esta régua é para interface interativa (página, app). Em vídeo, a interface pode ser mais lenta e expressiva para a câmera acompanhar: a mola e os tempos de vídeo estão em [regras.md](../../../../06-metodo/regras.md).

## Em vídeo feito em código (HyperFrames, Remotion)

O vídeo precisa sair igual em todo render, então tudo é controlado pelo tempo `t` da composição:

- **morphicons:** controle o progresso pelo tempo (`seek` ou `progress`).
- **itshover:** toque com `animate()` do `motion` e ajuste `controls.time = t`; o valor aparece 1 quadro depois, então espere 2 quadros por seek.
- **transitions.dev:** leve os números da receita (duração, curva) para a timeline da composição, em vez de colar o CSS que roda em tempo real.
- **libraries.dev e beautifului:** usam canvas, WebGL e timers em tempo real. Para vídeo, grave a tela ou recrie o efeito no motor.
