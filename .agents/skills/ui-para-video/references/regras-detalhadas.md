# Regras de interface, com números e exemplos

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** as regras da [ui-para-video](../SKILL.md) em detalhe. Base: o vídeo "Every UI/UX Concept Explained in Under 10 Minutes" (Kole Jain, YouTube) e a medição de sites de e-commerce bem feitos. Os números são pontos de partida; o sistema visual da marca prevalece.

## 1. Affordances e signifiers

- **Affordance:** o que o elemento permite fazer. **Signifier:** a pista visual que comunica isso.
- Exemplo: três pares ícone + texto (Bebidas, Comida, Sobremesa). Uma pílula em volta de dois indica que são relacionados; uma pílula branca com sombra leve num deles indica o selecionado; texto cinza claro indica inativo. Ninguém precisa de instrução.
- Signifiers obrigatórios: estado pressionado do botão, destaque do item ativo na navegação, hover, tooltip em ícone sem rótulo.

## 2. Hierarquia visual

- Ferramentas: **tamanho, posição, cor**. Hierarquia é contraste: pequeno × grande, colorido × neutro.
- Antes: card de pedido com 7 linhas rótulo/valor iguais (Restaurante, Item, Dia, Hora, Entregar em, Retirar em, Total). Parece planilha.
- Depois:
  - logo ou imagem no topo esquerdo (imagem facilita escanear);
  - item principal ao lado, maior e em negrito;
  - dia e hora juntos numa linha menor e cinza ("Hoje 9:30");
  - preço no topo direito, alinhado à direita, na cor de destaque (único destaque);
  - origem e destino com ícones de pino e linha, menores, sem rótulos "De/Para".
- Variante com foto grande no topo também vale. Fixos: o mais importante perto do topo; maior e com cor = mais importante; imagens sempre que possível.

## 3. Grade, layout e espaçamento

- Grade de 12 colunas é guia. Landing personalizada pode não seguir coluna nenhuma.
- Conteúdo estruturado e repetido (galeria, blog, cards): 12 colunas no desktop, 8 no tablet, 4 no celular.
- Mais importante que grade: **espaço em branco**.
- Exemplo de seção (hero escuro):

| Elemento | Fonte | Altura de linha |
|---|---|---|
| Título | 64 px | 72 px |
| Subtítulo | 20 px | 28 px |
| Selo | 16 px | 20 px |
| Botão | 14 px | 18 px |

- Espaçamento: 32 px entre os itens; 16 px entre os que andam juntos (selo + título, título + subtítulo). Agrupar por proximidade é outra forma de hierarquia.
- Sistema de 4 pontos (4, 8, 12, 16, 20, 24, 28, 32, 36, 40 px): divide ao meio sem frações.

## 4. Tipografia

- Interface é quase toda texto.
- Uma família, sans-serif. Exemplos: Inter, DM Sans, SF Pro, Geist, Plus Jakarta Sans, Montserrat. Não gaste tempo escolhendo fonte.
- **Texto grande:** `letter-spacing: -0.02em` a `-0.03em` e `line-height: 1.1` a `1.2`.
- Landing: até 6 tamanhos, amplitude grande (ex.: 64 · 42 · 32 · 20 · 16 · 14 px).
- Dashboard: nada acima de 24 px (ex.: 24 · 20 · 18 · 16 · 14 · 12 px).

## 5. Cor

- Comece com **uma cor primária** (em geral a da marca).
- Clareie para fundos e escureça para textos (card lilás claro com título roxo escuro e botão roxo). Isso já é meia rampa (50 … 950), usada em chips, estados e gráficos.
- Cor onde tem função: barra de aviso, foco no campo, chip "Novo" verde.
- Semânticas: **azul** confiança, informação, foco · **vermelho** erro, urgência · **amarelo** aviso · **verde** sucesso, novo.

## 6. Modo escuro

- Borda clara em card escuro = contraste demais; abaixe até quase sumir.
- Sem sombra para dar profundidade: a superfície mais alta é **mais clara** que o fundo.
- Chip brilhante → fundo escuro dessaturado da mesma cor e texto claro dessa cor.
- Fundo escuro pode ter matiz (roxo, vinho, verde profundos), não só cinza.

## 7. Sombras

- A maioria é forte demais: **menos opacidade, mais desfoque**.
- Card pede pouca; o que fica por cima de outro conteúdo (popover, menu, modal) pede mais.
- Sombra interna (brilho na borda de cima) + externa (embaixo) = botão em relevo.
- Ponto de partida em CSS: card `0 1px 2px rgb(0 0 0 / .04), 0 8px 24px rgb(0 0 0 / .06)`; popover `0 4px 12px rgb(0 0 0 / .08), 0 16px 40px rgb(0 0 0 / .12)`.

## 8. Ícones e botões

- **Ícone = altura de linha do texto** (texto 15 px / linha 24 px → ícone 24 px), com o texto perto.
- Link de barra lateral = botão fantasma (sem fundo até o hover). Isolado ao lado do primário, vira o secundário.
- **Padding horizontal = 2× vertical** (ex.: 16 px em cima e embaixo, 32 px nas laterais).

## 9. Feedback e estados

- Toda ação tem resposta.
- Botão: padrão, hover, pressionado, desabilitado; carregando (spinner no lugar do ícone) quando houver espera.
- Campo: foco (borda azul), erro (borda vermelha + mensagem que diz o problema), aviso (borda amarela + saída, como "Este e-mail já existe. Entrar?").
- Em toda parte: spinner ao buscar, barra de progresso, confirmação ao terminar.

## 10. Microinterações

- Feedback um degrau acima: no botão de copiar, um chip "✓ Copiado!" que sobe confirma de verdade.
- Vão do prático (confirmar, mostrar disponibilidade) ao divertido (confete, transição orgânica entre telas).

## 11. Imagem com texto

- Texto branco direto sobre foto clara some; camada escura na foto inteira mata a imagem.
- **Degradê linear** transparente em cima e escuro atrás do texto; desfoque progressivo por cima como acabamento.

## 12. Animações sutis (medidas num e-commerce de referência)

- **Card que sobe:** no hover, `transform: translateY(-2px)` + `box-shadow: 0 8px 24px -16px rgba(0,0,0,.25)`, transição `transform .16s ease, box-shadow .16s ease`. Sombra larga, com spread negativo, quase invisível em repouso.
- **Toque:** ripple de 10% de preto no clique.
- **Link de texto:** escurece e ganha sublinhado com `text-underline-offset: 3px`.
- **Seleção (tamanho, filtro, aba):** hover clareia o fundo; selecionado vira a cor de destaque com texto branco.
- **Entrada:** blocos sobem com opacidade 0 → 1; carregamento com skeleton em brilho que corre; selo "novo" com pulso leve.
- Duração curta (~0,16 s nos cards, até ~0,3 s em gavetas). Nada balança ou gira sozinho fora do carregamento.
- Junto: fundo cinza muito claro com seções brancas bem separadas e raio generoso, espaçamento amplo, CTA de compra em largura cheia.

## 13. Tela escaneável

- Cada elemento encosta em 2 ou mais arestas (borda do card, linha de cima, coluna). Texto duro à esquerda; valor e hora duros à direita; centralizado só o que não é para ler.
- Faltou aresta, crie uma (banner, linha) em vez de esconder função num menu ⋮. Não encha espaço vazio só por encher.
- Linha de texto não atravessa o card inteiro.
- Densidade se resolve **diferenciando**: avatar onde cita pessoa, grupo com cabeçalho cinza, chip com ícone, link azul.
- Símbolo universal no lugar de texto; não empilhe comparação, % e (i) para "explicar mais".
- Ênfase é a diferença com os vizinhos: valor padrão e inativo em cinza; para destacar, neutralize o entorno em vez de engrossar o alvo; checkbox desligado sem cor.
- Sem caixa dentro de caixa nem raios empilhados: uma linha de 1 px pode substituir os cards.
