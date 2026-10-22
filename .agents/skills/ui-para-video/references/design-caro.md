# Design caro × barato: decidir fácil, não só parecer limpo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** lições do vídeo da uxpeak "The Same App Designed By An $80K vs $250K Designer" (YouTube), que mostra o mesmo app feito por designers de níveis diferentes em dois casos: lista de restaurantes e filtro de imóveis. O "caro" não está no enfeite: está em imagem com espaço, hierarquia que deixa escanear, controles que mostram a consequência e interface que pergunta o que a pessoa sabe. As medidas são pontos de partida.

## A. Card e lista (app de comida)

| # | Barato | Caro | Medida de partida |
|---|---|---|---|
| A1 | Logo da loja como imagem | Foto do produto | o logo diz quem vende; a foto diz o que você vai comer |
| A2 | Miniatura de 56 pt à esquerda | Foto como o maior elemento do card | 56 → 172 pt em grade de 2 colunas → largura total; nunca menos de ~80 pt quando a imagem vende |
| A3 | Encher a primeira dobra com 6 itens ilegíveis | 1 a 4 itens bonitos e completos | todo mundo rola a tela |
| A4 | Filtros em dropdowns com opções escondidas | 3 a 8 chips visíveis; o resto num sheet | chip ativo preenchido; o toque filtra na hora |
| A5 | Título e metadado pequenos numa linha cinza corrida | 3 degraus: título, dado de decisão, apoio | título ~18 pt semibold; a nota em peso ou cor; apoio cinza |
| A6 | Cantos de 4 pt misturados com círculos | Uma escala de raio | campo ~10, foto ~12, card grande ~16, chip em pílula |
| A7 | Cards com borda cinza e vão apertado | Separação por espaço; busca preenchida, sem borda | margem lateral ~20 pt; cor só para estado ativo ou ação |
| A8 | Fotos de categoria brigando com as do feed | Ícones ou ilustrações na navegação | — |
| A9 | Navegação colorida como o conteúdo | Navegação com saturação menor que o conteúdo | fundo de ícone neutro |
| A10 | Lista sem noção do tamanho | Contador do conjunto ao lado do título | "640 lugares" em cinza, ~60% do título |
| A11 | Uma visualização só | Alternar cards (emoção) × lista (comparar) | sem padrão certo para todos, dê o controle |
| A12 | Placeholder vago | Placeholder que ensina o escopo | "Busque lugares, pratos ou cozinhas" |
| A13 | Selos espalhados | Um único selo por tela, com base em dados | pílula pequena, versal espaçada |
| A14 | Texto essencial sobre a foto enviada por terceiros | Foto limpa em cima, detalhes embaixo | o card fica igual seja qual for a foto |
| A15 | Branco puro | Branco e cinza quentes | ex.: tela `#FBF9F7`, card `#FFFFFC`, texto `#171712` |

## B. Filtros e controles (filtro de imóveis)

| # | Barato | Caro | Medida de partida |
|---|---|---|---|
| B1 | "Limpo" porque cada filtro vive numa subpágina | Todas as decisões na mesma vista | conte os toques da tarefa comum; filtro curto mora na tela principal |
| B2 | Filtro em tela cheia escondendo os resultados | Bottom sheet sobre os resultados | o contexto continua visível |
| B3 | Botão mudo ("Aplicar") | Botão que diz a consequência | "Ver 41 imóveis", "Pagar R$ 239,90", em tempo real |
| B4 | Cortar elementos para parecer simples | Aceitar o elemento que elimina um passo ou uma dúvida | parecer simples ≠ decidir fácil |
| B5 | Só slider, ou só campo | Slider para explorar + campos para precisão | os dois sincronizados |
| B6 | Stepper + e − para escolher um número | Opções visíveis (1+, 2+, 3+, 4+) | stepper só para ajustar algo que já existe |
| B7 | Valor exato que corta o 4 quando se pede 3 | "3+" como padrão; exato opcional | o rótulo mostra a regra |
| B8 | Opção só com texto | Opção com ícone | tipo, categoria, tamanho |
| B9 | Controle que só pede o valor | Controle que mostra o mercado | histograma dentro do slider; mediana marcada |
| B10 | Bloco sem contexto | Cada seção diz quanto do total representa | número forte + total fraco |
| B11 | Pedir o que a pessoa não sabe (preço máximo) | Perguntar o que ela sabe e fazer a conta | entrada + parcela → "você alcança R$ 708 mil" |
| B12 | Opção sem consequência | Contagem em cada opção antes do clique | opção que dá zero fica desabilitada |
| B13 | Escolha de um valor só | Seleção por faixa quando se pensa em intervalo | toque em 2 e em 4 = pílula contínua 2–4 |
| B14 | Mais dados = mais caro | Cada dado responde a uma pergunta daquele momento | o resto sai ou fica atrás de um toque |

## C. Em tela de vídeo

A tela simulada segue as mesmas regras. Num vídeo, o "caro" ainda ajuda a câmera: um botão que diz "Pagar R$ 239,90" conta a história sem legenda, e uma foto grande dá onde a câmera fechar.

## D. Checklist rápido

- [ ] A imagem que vende é o maior elemento do card?
- [ ] Há 3 degraus de texto, com o dado de decisão destacado?
- [ ] Os filtros frequentes estão à mostra e o resto num sheet?
- [ ] O botão principal diz a consequência?
- [ ] As opções mostram a contagem antes do clique?
- [ ] A interface pergunta o que a pessoa sabe e faz a conta?
- [ ] Texto de terceiros fora da foto? Um único selo? Navegação mais quieta que o conteúdo?
- [ ] Uma escala de raio, e espaço no lugar de bordas?
- [ ] Algum dado não ajuda a decidir? Sai ou fica atrás de um toque.
