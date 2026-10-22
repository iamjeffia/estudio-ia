---
name: motion-narrado
description: Regras para montar motion graphics sobre uma narração (Reels explicativos, tutoriais e anúncios narrados com telas de interface) — a cena se constrói conforme a fala, sem spoiler; legenda com tempo de leitura e sem marca-texto; um elemento real ou metáfora visual para cada ideia dita; destaques variados; troca de cena só depois da fala e na batida da trilha. Usar em todo vídeo narrado com motion, em After Effects, EffectCraft, HyperFrames ou Remotion, antes de escrever as cenas e de novo antes de renderizar.
---

# Motion narrado: a cena se constrói pela fala

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** regras para animar sobre a narração: nada aparece antes de ser dito, a legenda dá tempo de ler, cada ideia ganha um elemento real ou uma metáfora visual, e a tela só troca depois que a frase termina. Vale em qualquer motor (escolha na [estudio-video](../estudio-video/SKILL.md)). Números de partida em [regras.md](../../../06-metodo/regras.md).

Antes de começar, siga a [video-referencias](../video-referencias/SKILL.md) (referência assistida e assets reais). Vídeo narrado de produto ou software soma estas regras com o padrão da [animacao-saas](../animacao-saas/SKILL.md), com a fala no lugar da batida dando o tempo de cada transformação.

## O insumo: tempos por palavra

Tudo parte da narração **aprovada** e transcrita palavra por palavra (`words.json`: palavra, início, fim). Se a narração for acelerada depois, transcreva o arquivo já acelerado e anime sobre ele.

## Storyboard antes de ritmo

Em tutorial e explicativo, menos é mais: cada elemento tem propósito, entra na hora certa e sai ou vira o próximo. Animações mais longas e suaves, uma ideia principal na tela por vez, sempre algo vivo, e efeito sonoro só onde soma. Ponto de partida:

- uma composição por frase, de 4 a 6 s;
- elemento novo a cada 1,5 a 2 s, na palavra que o nomeia;
- no máximo 3 coisas além da legenda (1 principal + 2 apoios);
- metade das trocas é um elemento virando o próximo, não um corte.

Abertura de Reel cinético pode correr bem mais rápido (algo novo a cada meio segundo); declare no projeto qual ritmo vale para cada trecho. Durações de entrada, saída e câmera em [regras.md](../../../06-metodo/regras.md).

## Regra 1 — Nada aparece antes de ser dito

Cada elemento entra **no momento da palavra que o justifica** (até ~0,15 s antes, nunca segundos antes). A cena começa vazia ou só com a legenda e vai se montando.

| Errado | Certo |
|---|---|
| o card do produto visível desde o início da cena | o ícone nasce quando a voz diz o nome, com animação própria; no nome completo ele voa para o cabeçalho e o card se monta |
| barras paradas esperando ser ativadas | as barras surgem na palavra "primeira parte" e a primeira enche em seguida |
| três passos esmaecidos antes de serem citados | cada passo entra quando é falado |
| o celular já aberto em "funciona assim" | a foto do assunto entra quando ele é dito; o celular entra em "pesquisa no app" |

**Como aplicar:** antes de animar, escreva a tabela `palavra → tempo → elemento que entra`. Na revisão, procure na folha de contato qualquer elemento que apareça sem ter sido falado.

**Exceção:** o herói da cena (o celular onde a ação acontece) pode estar na tela desde o começo, se a voz já fala dele.

## Regra 2 — Legenda que dá tempo de ler

- Frases de 4 a 9 palavras, em até 2 linhas quebradas à mão. Trechos de 1 ou 2 palavras trocando sem parar somem antes de serem lidos.
- **Tempo mínimo de leitura:** cada frase fica pelo menos ~0,6 s depois da última palavra entrar. A próxima espera a anterior sair; pode atrasar até ~0,5 s em relação à fala, nunca adiantar.
- **Sem quebra automática:** a fonte encolhe para caber. Isso garante que nunca nasce uma 3ª linha escondida atrás do celular.
- **Palavra por palavra com máscara:** cada palavra sobe de dentro de uma caixa recortada (de 100% para 0, com leve desfoque). Palavra flutuando solta, com desfoque e deslocamento livre, parece amadora.
- Gerar a legenda a partir da fala: `uv run scripts/video/make_captions.py`.

## Regra 3 — Destaque sem marca-texto e sem repetição

- **Evite marca-texto** (faixa colorida atrás da palavra): é cortado pela máscara palavra a palavra e fica repetitivo.
- **Padrão:** a palavra-chave muda para a cor de destaque do vídeo e sobe um peso. No máximo uma por frase.
- **Varie** quando o destaque importa: logo oficial dentro da linha, um elemento que nasce da palavra (a letra do logo), um contador, um anel de destaque no card. Não repita o mesmo recurso em cenas seguidas.
- Texto de destaque grande sempre com acabamento: degradê, brilho, textura, contorno ou a palavra preenchida com filmagem.

## Regra 4 — Elemento real e metáfora para cada ideia

- **Lugar real → print real.** "Negócio local" pede o mapa de verdade: captura do Google Maps pelo Chrome sem janela (`--headless --window-size=1900,1600 --force-device-scale-factor=2 --virtual-time-budget=20000` e a URL `.../maps/place/<cidade>/@lat,lng,13.5z`). Por cima, marcadores de negócios reais, posicionados por projeção Mercator com o mesmo centro e zoom (confira plotando todos os pontos antes). "Sua empresa" é o único pino na cor de destaque.
- **Analogia popular → ilustração dela.** "Mais lento que fila de posto de saúde" pede o símbolo oficial do serviço, a foto de uma fila (pessoas de costas, sem texto legível) e o painel de senha em LED com "tempo de espera: 4 horas". Uma senha genérica não comunica a piada.
- **Logo, ícone e SVG:** sempre o oficial do site da marca. Logo de terceiro identifica o assunto, nunca aparece como parceiro.
- **Ilustre o conceito, não liste.** "Gargalo" é um fluxo que trava: clientes chegando e se acumulando numa etapa, contador subindo, carregamento que para, etiqueta "travado".
- **Emoção sem vídeo reaproveitado.** Não use vídeo de pessoa feito para outra situação. Um emoji em SVG que muda com a fala (neutro → bravo → vermelho com vapor) funciona melhor; pessoa real pede material novo.
- Cada frase falada deve ter uma tradução visual literal. Se a frase não tem elemento, a legenda sozinha precisa bastar.

## Regra 5 — Trocas de cena, fala e batida

- **Troca de tela só depois da fala.** A cena nova começa depois que a última palavra da frase anterior terminou (fim da palavra + um respiro curto). Se a transição cobre a tela antes do corte, conte esse tempo. Só então ajuste para a batida mais próxima, se estiver a até ~0,2 s.
- **Medir a trilha:** `uv run scripts/som/batida.py` marca batidas e tempos fortes (veja `--help`; também confere um render contra a trilha). Meta: a maioria dos cortes na batida.
- Abertura de cena no bumbo; a parada da trilha cai na virada do roteiro (adiante ou atrase a música).
- **Narração seca**, música abaixando sob a fala e seguindo o vídeo inteiro. Se houver abertura musical cinematográfica, a fala vem depois dela, nunca por cima. Escolha de música, efeitos e mix: skill [som-do-video](../som-do-video/SKILL.md).

## Regra 6 — Acabamento

- **Nada atrás do herói:** legenda numa faixa própria (no topo, em vídeo vertical), herói abaixo dela.
- **Nenhum efeito cortado no meio por uma transição:** um destaque só começa se tiver tempo de terminar antes da saída da frase.
- **Transição suave:** a cena nova entra por cima, saindo do desfoque e de uma escala levemente maior. A cena antiga **continua opaca**, só desfoca e encolhe; duas cenas semitransparentes deixam um véu cinza.
- Cena escura só de texto pode respirar até ~1 s antes da primeira palavra; cena clara não abre vazia por mais de ~0,3 s, a não ser que o elemento ainda não tenha sido dito.

## Regra 7 — Recursos de acabamento que funcionam

| Recurso | Quando usar | Como |
|---|---|---|
| **Câmera que acompanha a ação** | digitação, toque, mensagem: o olho precisa ir para o detalhe | fecha (escala ~1,3–1,5) no ponto da ação e volta; a legenda fica fora da câmera |
| **Mão-cursor com ondas** | todo clique ou toque mostrado | ponta do dedo no alvo; aperta e solta duas ondas; som de toque |
| **Transição de pontos** | 2 ou 3 viradas grandes (cena de impacto, marca, CTA); não em todas | malha de bolinhas nas cores do vídeo que cobre a tela, corte no meio, revela a próxima |
| **Pino com foto + radar** | mapa ou local | foto redonda com borda branca e nome; radar girando no pino principal |
| **Pilha de palavras** | benefícios falados em série | a palavra dita entra no centro, a anterior sobe apagada |
| **Ilha do topo do celular** | notificação ou mensagem chegando | pílula preta que expande com mola |
| **Logo por traço** | revelação da marca | traço que se desenha e depois preenche |
| **Fundo claro com brilho pastel** | cena clara | um tom por cena |
| **Contador que rola** | número citado | sobe até o valor ao entrar |
| **Onda com pílulas** | "de ponta a ponta", processo em etapas | linha ondulada que se desenha e recebe uma pílula por etapa falada |
| **Elemento-fio que a câmera segue** | jornada por várias telas | um ponto viaja entre telas reais num "mundo" maior que a tela; cada tela acende quando ele chega; no fim a câmera abre e mostra tudo |

No After Effects com o Motion Kit AE, prefira as operações prontas do kit (mola, entrada, saída, câmera viva) a escrever expressão do zero. Em HyperFrames ou Remotion, tudo vira função do tempo (`t`), sem relógio real, para o mesmo quadro sair igual em todo render.

## Checklist antes de renderizar

- [ ] Tabela palavra → elemento escrita; nenhum elemento antes da palavra.
- [ ] Legenda: frases de 4 a 9 palavras, no máximo 2 linhas, leitura mínima, nada atrás do herói.
- [ ] Nenhum marca-texto; destaques variados.
- [ ] Cada analogia, lugar ou marca citada tem imagem real ou ilustração clara.
- [ ] Nenhuma troca de tela antes do fim da frase; trocas conferidas contra a batida.
- [ ] Cliques mostrados com mão-cursor; câmera fecha nas ações pequenas; no máximo 3 transições de pontos.
- [ ] Nenhum vídeo reaproveitado fora do contexto original.
- [ ] Folha de contato e recortes ampliados revisados, procurando spoiler, texto escondido, efeito cortado e tela vazia (`uv run scripts/video/detectar_saltos.py` no render).
- [ ] Comparado lado a lado com a referência e com o melhor vídeo anterior do mesmo tipo: está melhor no conjunto? Se não, ainda não está pronto.
