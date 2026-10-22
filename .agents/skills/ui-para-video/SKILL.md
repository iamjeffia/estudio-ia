---
name: ui-para-video
description: Regras de UI/UX para telas recriadas dentro de vídeos (app, site, dashboard, chat, notificação) e para páginas simples, para o resultado parecer produto de verdade e não tela feita por IA. Usar ao desenhar, recriar, auditar ou polir qualquer interface que vai aparecer num vídeo ou numa página, inclusive quando for preciso buscar referência visual (Mobbin se disponível; senão Pinterest ou Dribbble).
---

# UI para vídeo (e páginas simples)

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** a tela "cara" é o que torna o motion crível. Esta skill reúne regras universais de interface (hierarquia, espaço, tipografia, cor, estados) e o que muda quando a tela vai para um vídeo: legível no celular, recriada em camadas, cada peça animável. Serve também para página simples (landing, link na bio). Números e exemplos em [references/regras-detalhadas.md](references/regras-detalhadas.md).

Duas formas de uso:

- **Criar:** desenhar uma tela nova ou recriar a de um produto real para o vídeo.
- **Revisar:** auditar uma tela pronta, apontar o que quebra cada regra e corrigir se o pedido incluir.

## 1. Contexto antes de desenhar

1. Ache o sistema visual do projeto ou da marca do assunto: tokens (cores, fontes, espaçamentos, raios) e componentes. Para marca de terceiros, tire do site oficial (método na [video-referencias](../video-referencias/SKILL.md), seção 3). As regras abaixo ajustam a execução, não trocam a marca.
2. Defina o tipo de tela: **landing/site** (amplitude grande de tipografia) ou **app/dashboard** (densidade alta, texto até 24 px).
3. Liste o que cada bloco precisa comunicar e qual é o elemento mais importante de cada um. Em vídeo: o que a narração diz naquele momento.

## 2. Referências antes de desenhar

| Precisa de | Fonte |
|---|---|
| Tela de app ou site, seção de landing (hero, preço, FAQ, depoimento), dashboard, fluxo (onboarding, checkout) | **Mobbin**, se a pessoa tiver (MCP com `search_sections`, `search_screens`, `search_flows`) |
| Sem Mobbin, ou o Mobbin não tem | **Dribbble** e **Pinterest** (palavras-chave curtas em inglês) e capturas reais do produto |
| Motion, efeito animado, estética, foto, ambiente | **Pinterest** |
| Produto real citado no vídeo | **o próprio produto**: grave a tela ou capture as telas oficiais |
| Transição pronta, ícone que muda de forma, microinteração, tela de agente de IA | bibliotecas de componentes: [references/motion-e-componentes.md](references/motion-e-componentes.md) |

Como buscar e guardar: [references/referencias.md](references/referencias.md). Junte de 3 a 6 referências por tela e anote o padrão aproveitado de cada uma. Use a referência para estrutura, hierarquia, espaçamento e comportamento; não copie marca, texto ou imagem de terceiros.

## 3. Regras (resumo)

1. **Signifiers:** a tela se explica sozinha. Agrupe com contêiner, destaque o selecionado, acinzente o inativo. Clicável mostra hover, pressionado e item ativo; ícone sem texto ganha tooltip.
2. **Hierarquia:** tamanho, posição e cor. O mais importante no topo, maior e em negrito; o secundário menor e cinza. Um destaque de cor por bloco. Imagem, logo e ícone no lugar de rótulos ("De:", "Restaurante:"). Lista "rótulo: valor" toda igual é planilha, não design.
3. **Espaço:** espaço em branco antes de grade. Múltiplos de 4 (4 a 40 px). Um espaçamento base entre blocos (ex.: 32 px) e metade (16 px) entre itens que andam juntos.
4. **Tipografia:** uma família sans-serif. Texto grande com espaçamento entre letras de −2% a −3% e altura de linha de 110 a 120%. Landing: até 6 tamanhos. Dashboard: até 24 px.
5. **Cor:** uma primária, com versões claras para fundo e escuras para texto (rampa 50–950). Outras cores só com função: azul foco, vermelho erro, amarelo aviso, verde sucesso.
6. **Modo escuro:** borda clara quase sumindo; profundidade por superfície mais clara que o fundo; chip com fundo escuro dessaturado e texto claro da mesma cor.
7. **Sombra:** opacidade baixa, desfoque alto. Se a sombra é a primeira coisa que se nota, está errada.
8. **Ícones e botões:** ícone do tamanho da altura de linha do texto, perto dele. Padding horizontal = 2× o vertical. Par de CTA: primário preenchido + secundário fantasma.
9. **Feedback:** botão com padrão, hover, pressionado, desabilitado e carregando. Campo com foco, erro com mensagem e aviso. Toda ação responde.
10. **Imagem com texto:** degradê localizado atrás do texto, não camada escura na foto toda.
11. **Animações sutis em toda interface:** card sobe ~2 px com sombra larga e fraca no hover, ripple leve no clique, blocos entram subindo com fade, skeleton com brilho no carregamento. Curto e discreto: nada se mexe sozinho fora do carregamento.
12. **Design caro é decidir fácil, não só parecer limpo:** a imagem que vende é o maior elemento do card; 3 degraus de texto, com o dado de decisão em peso ou cor; botão que diz a consequência ("Ver 41 imóveis", "Pagar R$ 239,90"); um selo por tela; navegação mais quieta que o conteúdo; uma escala de raio. Tabelas em [references/design-caro.md](references/design-caro.md).
13. **Tela escaneável:** ninguém lê a tela, caça a resposta. Cada elemento encosta em 2 ou mais arestas (texto à esquerda, valor e hora à direita; centralizado só o que não é para ler). Densidade se resolve diferenciando (avatar, grupo com cabeçalho, chip com ícone), não espaçando. Ênfase é a diferença com os vizinhos: para destacar, neutralize o entorno. Sem caixa dentro de caixa.

## 4. Tela dentro do vídeo

- **Legível no celular:** corpo de interface com pelo menos ~22 px num quadro de 1080 de largura; títulos de impacto bem maiores. Teste: pare o quadro 1 s no tamanho do celular. O que se vê primeiro é o que a narração está dizendo?
- **Recriada em camadas, nunca print colado:** cada botão, texto, ícone e balão é uma camada própria, para animar sozinho (entrar com mola, acender, ser clicado). Print entra só como prova (notícia, post real).
- **Fiel ao produto real:** mesmas cores, fonte, raios, ícones e componentes do app que o público conhece (WhatsApp, Gmail, banco). Ícones oficiais (SF Symbols, Material Symbols ou o SVG da marca).
- **Estados de verdade em movimento:** digitação com o teclado real do sistema subindo e teclas acendendo, nunca texto "esticando" por máscara; botão que aperta no clique; carregamento que carrega; notificação no formato real da plataforma.
- **Dados de exemplo plausíveis:** nomes, valores e horários que fazem sentido no nicho; nada de "Lorem ipsum", e nenhum dado pessoal real, e-mail ou credencial na tela.
- **Uma ideia por tela no quadro:** se a tela tem 10 informações e a fala cita uma, as outras ficam neutras e a câmera fecha na que importa.

## 5. Modo Revisar

1. Renderize a tela (navegador, prévia do motor ou quadro do vídeo) e capture desktop e celular, ou o quadro no tamanho do celular.
2. Passe o checklist e registre cada problema com: onde, regra quebrada, valor atual e correção proposta.
3. Ordene por impacto: hierarquia e legibilidade, depois espaço e tipografia, depois polimento (sombra, estados, microinteração).
4. Corrija em mudanças pequenas e verificáveis, preservando a marca e o texto.

### Checklist (cada item é também um "cheiro de IA")

- [ ] Algum card ou lista parece planilha (rótulos repetidos, tudo do mesmo tamanho)?
- [ ] Cada bloco tem um único elemento dominante? Há mais de um destaque de cor competindo?
- [ ] Espaçamentos fora de múltiplos de 4, ou iguais entre itens que deviam ficar agrupados?
- [ ] Mais de uma família de fonte? Mais de 6 tamanhos (landing) ou texto acima de 24 px (dashboard)?
- [ ] Títulos grandes com espaçamento de letras e altura de linha padrão?
- [ ] Cor usada só para decorar, ou cores semânticas trocadas?
- [ ] Sombra pesada ou visível antes do conteúdo? Borda clara forte no escuro? Chip neon?
- [ ] Ícone maior que a altura de linha do texto, longe do rótulo, ou pequeno e torto dentro do quadrado colorido (o desenho deve ocupar ~55% da caixa)?
- [ ] Botões com padding desproporcional, ou dois CTAs com o mesmo peso?
- [ ] Faltam estados (hover, pressionado, foco, desabilitado, carregando, erro)?
- [ ] Texto branco direto sobre foto, ou foto inteira escurecida?
- [ ] Rótulo em caixa alta acima do título em toda seção, ou "3 passos numerados" com ícone centralizado no lugar de mostrar a coisa real?
- [ ] Design barato: imagem pequena, metadado corrido em cinza, botão mudo ("Aplicar"), mais de um selo, raios misturados?
- [ ] Elemento solto, sem 2 arestas? Card dentro de card?
- [ ] Degradê roxo-azul genérico, emoji como ícone, cantos e sombras iguais em tudo, texto de preenchimento?
- [ ] Em vídeo: legível no celular? Recriada em camadas? Fiel ao produto real? O primeiro olhar cai no que a fala diz?

## 6. Verificação

- Renderize e olhe: desktop (1440 px) e celular (390 px), claro e escuro se existir; em vídeo, o quadro no tamanho do celular.
- Confira no código os números das regras (tamanhos, alturas de linha, espaçamentos, sombras).
- Interaja: hover, clique, foco e envio mostram resposta.
- Compare antes e depois e liste o que mudou e por quê.
