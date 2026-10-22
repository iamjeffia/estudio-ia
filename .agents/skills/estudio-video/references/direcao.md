# Direção do vídeo: decisões antes de animar

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** decisões de direção que todo vídeo com motion toma antes de animar, registradas num `DIRECAO-VISUAL.md` do projeto (molde no fim). Duas delas valem só em casos específicos e estão marcadas. Os números de partida (durações de câmera, overlap entre cenas) ficam em [regras.md](../../../../06-metodo/regras.md).

## A pergunta de controle

Em cada movimento: **"isso está humano ou robotizado?"** Robotizado é a câmera ou o card que anima, para morto e ressuscita num movimento rápido. Humano é continuar vivo o tempo todo, nem que seja com o mínimo: deriva lenta, flutuação, balanço. Use peso e física reais (antecipação, exagero na medida, assentamento com mola) e acabamento limpo.

- **Câmera nunca parada:** deriva contínua mais um tremor lento num controle pai. O imperfeito humaniza: meça a deriva e a tremida da referência e reproduza.
- **Movimento e som contínuos; o respiro é exceção**, usado logo antes de uma revelação: o ritmo cresce, tudo para por um instante, e vem o impacto.

## As decisões

| # | Decisão | Como fazer | Quando |
|---|---|---|---|
| 1 | **Arco de cor com causa física** | 2 ou 3 fundos, cada um com uma função na história (escuro = suspense, claro = leitura, cor da marca = virada). Tabela cena → fundo → função. **Nenhum fundo muda sozinho:** a troca nasce de um objeto (ponto que explode, card que estoura e vira o fundo, wipe que sai de quem sai) | todo vídeo com mais de um fundo |
| 2 | **O material muda com o fundo** | O mesmo objeto troca de pele na troca: vidro translúcido escuro com desfoque e borda fina no fundo escuro; vidro claro na cor da marca; no fundo claro, superfície sólida com sombra levemente colorida, sem vidro | todo vídeo com mais de um fundo |
| 3 | **Câmera que para de propósito** *(casos específicos)* | Em vez da câmera sempre viva, ela para por completo em 2 ou 3 momentos de verdade (a piada, a negação, a frase honesta). Declare as paradas no `DIRECAO-VISUAL.md`, para a revisão saber que são de propósito | vídeo-manifesto, opinião; não em tour nem anúncio rápido |
| 4 | **Anti-design como piada** *(casos específicos)* | Uma cena feia de propósito (fora da paleta, sem animação, sem câmera) prova por contraste que todo o resto foi decidido | quando a fala mostra "o jeito errado" |
| 5 | **Câmera com propósito** | Cada movimento tem início e fim (x, y, z), curva e uma linha de **por quê** ("orbita para mostrar que tem corpo", "mergulha para convocar"). Movimento sem porquê fica na deriva padrão | todo movimento além da deriva |
| 6 | **A marca em 3 escalas** | objeto herói (apresentação), ícone dentro da interface (ferramenta), miniatura no sistema (ecossistema) | vídeo de produto ou marca própria |
| 7 | **O fio da interface vira o CTA** | o elemento que nasce no começo (campo de texto, botão) é o mesmo que fecha o vídeo como chamada: campo digitado → botão → caixa de comentário "Comenta X" | Reel com CTA e assunto de app, chat ou IA |
| 8 | **Cor reservada e vilão recorrente** | uma cor só aparece com um significado; um objeto representa o problema e volta 2 ou 3 vezes, igual | todo vídeo com tese |
| 9 | **Último quadro = primeiro quadro** | o fim volta ao fundo, à luz e à posição do quadro 0, para o Reel recomeçar sem emenda no loop. Confira os dois lado a lado | todo vertical que não fecha num cartão de marca |

## Molde do `DIRECAO-VISUAL.md`

```markdown
# Direção visual — <tema>

- Tese visual: <o vídeo inteiro pertence a qual mundo?>
- Metáfora central: <uma imagem que traduz a mensagem>
- Objeto-fio: <elemento que reaparece e conecta as cenas>
- Fio da interface → CTA: <qual elemento nasce no começo e fecha como CTA, ou "não se aplica">
- Vilão recorrente: <o objeto do problema e as cenas em que volta>
- Cor reservada: <cor → único significado>
- Arco de cor: tabela cena → fundo → função; como cada troca nasce de um objeto
- Material por fundo: <pele do mesmo objeto em cada fundo>
- Marca em 3 escalas: <herói / ícone / miniatura, em que cenas>
- Câmera: <gramática geral> · paradas de propósito: <cenas e por quê, ou "nenhuma">
- Ficha de câmera: tabela movimento → início, fim, curva, por quê
- Movimento: <peso, velocidade, entrada / estado ativo / saída>
- Transições: <as saídas escolhidas em saidas-e-truques.md e as criadas para este vídeo>
- Exceções declaradas: <anti-design, corte seco, parada de câmera>
- Loop: <como o último quadro casa com o primeiro>
- Som: <família de impactos, cliques, whooshes e ambiência>
- Referências: <3 a 5; o que será aproveitado de cada uma>
- Não fazer: <clichês e movimentos incompatíveis>
```

Campo que não se aplica fica escrito "não se aplica", para ficar claro que foi pensado.
