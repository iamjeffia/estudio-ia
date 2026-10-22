# Lições de recriar peças de referência

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** o que mais fez diferença ao recriar, peça por peça, vídeos de produto e showreels de referência para superá-los. Valem no After Effects e em código. Números de partida em [regras.md](../../../../06-metodo/regras.md).

1. **Especificação quadro a quadro antes de animar.** Batida como fórmula, cortes em quadros fixos ~2 quadros antes do tempo forte, tabela de valores por plano (posição, escala, desfoque), entrada já em movimento, saída acelerando, no máximo um quadro congelado e 4 quadros de aprovação escolhidos antes do render.
2. **Folha de batidas como dado.** As batidas medidas viram uma função `b(compasso, tempo, fração)`; nenhuma cena guarda número de quadro. Orçamento por compasso, como ponto de partida: abertura 1–2, frase 1–1,5, função do produto 2–4, prova 1,5–2,5, fim 2.
3. **Um conceito por compasso** em peça sem narração: troca no tempo forte, um evento por batida.
4. **Magic move antes de qualquer troca.** Logo voando para dentro da frase: anime o próprio item com deslocamento `(origem − destino)·(1 − q)`, e o pouso fica exato.
5. **Identidade real tirada do site e do kit de marca:** CSS computado (fundo, tinta, destaque, raio, fontes), logo SVG, mascote, textura de assinatura e capturas oficiais do produto, cada valor com a fonte num `BRAND.md` do projeto, que vence o padrão da skill. Não invente um tema escuro para uma marca que é clara.
6. **Logo com partes vira capítulos:** N partes do logo (barras, pontos, blocos) = N passos do produto; a parte ativa vira o indicador.
7. **Gráfico vira gráfico:** linha → funil interpolando os dois contornos na mesma curva; contador em odômetro sem dígito cortado (máscara em degradê; a casa só rola junto com as de baixo quando elas passam do 9).
8. **Protagonista contínuo:** um objeto atravessa todas as cenas e muda de papel (ponto final, cometa, núcleo, assinatura). Toda transição sai dele.
9. **Mascote com corpo:** rig por parâmetros a partir do SVG oficial (olhar, piscar, humor); antecipação curta, estica no ar, pousa amassando, respira o tempo todo.
10. **Marca sem perder impacto:** a identidade não tira o contraste nem o peso do título; a marca entra no destaque, no símbolo e na assinatura. Versões mais "sofisticadas" costumam perder impacto no celular: compare sempre com o original no tamanho real.
11. **Formas que crescem até a tela** (íris, flood, círculo de cor) precisam de pouco deslocamento por quadro, senão viram cópias: use curva suave, borda suavizada e, em código, subquadros com motion blur.
12. **Revisão com detectores:** `uv run scripts/video/detectar_saltos.py` em todo render; cada salto restante é corte de propósito. Folha com o quadro antes, o do corte e o depois em cada corte.
