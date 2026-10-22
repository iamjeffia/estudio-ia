# Identidade visual de cada vídeo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** todo vídeo ganha identidade própria, tirada do assunto: fonte, cores, ícones, componentes e transição. Este arquivo diz como escolher e descreve a base "Apple light", que serve para assuntos sem identidade forte.

## Qual identidade usar

| O vídeo fala de… | Identidade | Exemplo |
|---|---|---|
| Serviço, explicação, assunto sem marca forte | **Apple light** (abaixo): UI do iPhone, cores do sistema, SF Pro, modo claro | "como organizar a agenda da clínica" |
| Uma marca com identidade forte | **a marca do assunto no vídeo inteiro**: tipografia, cores, elementos, desenhos, personagens, produtos | uma rede de fast-food: as cores dela, o símbolo, os lanches |
| "Estilo Apple + X" | **mescla**: pesquise a referência de X e misture com a base Apple light | Apple + um app de música: esta gramática com o verde, as capas e a tipografia do app |
| Nicho com paleta própria | a base Apple light na paleta do nicho | clínica de estética em rosa claro e tom de pele; comida nas cores das marcas citadas |
| Ritmo de música, peça sem narração | estilo SaaS: skill [animacao-saas](../../animacao-saas/SKILL.md) | lançamento de app |

- **Assunto muda, identidade muda.** Começou falando de uma ferramenta e passou para outra? Faça uma transição de assunto e troque cores e componentes.
- **A marca vem do site e do kit oficial**, nunca da memória (método na [video-referencias](../../video-referencias/SKILL.md), seção 3). Cada valor com a fonte num `BRAND.md` do projeto.
- **Fonte não é regra fixa:** depende do estilo e do projeto.
- **Marca vestida não pode apagar o contraste.** Em vídeo rápido, use a versão mais saturada de cada cor no fundo e a fonte mais pesada disponível nos títulos de impacto; a fonte decorativa da marca fica no logo e nos subtítulos.

## Base Apple light: os 10 princípios

1. **Cada frase vira um app do celular que a mostra sem precisar escrever.** Falta de tempo vira o calendário lotado; "como fazer" vira a busca do sistema; um plano vira a lista de lembretes.
2. **Nada entra antes de ser dito.** Cada elemento nasce no quadro da palavra (tempos da transcrição por palavra).
3. **Dor e solução usam o mesmo objeto.** O calendário lotado do começo volta calmo no fim.
4. **A transição nasce de um elemento:** a ilha do topo do celular cresce, tudo se recolhe num ponto, os itens viram as linhas da próxima tela.
5. **O degradê colorido de "inteligência artificial" é só para IA.** O resto usa cores de estado do sistema: verde = feito, vermelho = problema, azul = ação.
6. **Antes da revelação, um respiro.** Tudo vira um ponto, entra uma palavra, e o logo explode no drop da música.
7. **Movimento de Apple:** curvas que saem rápido e assentam longo, cascata de 2 a 3 quadros, mola na chegada, desfoque por letra nos títulos, câmera viva no vídeo inteiro.
8. **Interface recriada em camadas, nunca print colado:** cada botão, texto e ícone anima sozinho. Ícones oficiais (SF Symbols ou o SVG da marca).
9. **Som para cada elemento**, com o pico no quadro do evento (skill `som-do-video`).
10. **O fim mostra o que acontece depois do clique** (formulário enviado, mensagem chegando) e fecha no logo, com um pedido simples.

### Checklist do estilo

- [ ] Toda palavra-chave tem um evento visual e um som no mesmo quadro.
- [ ] Nenhuma tela fica vazia mais de ~0,5 s e nada para morto.
- [ ] Degradê da IA só onde a fala diz IA.
- [ ] Nenhum texto da tela repete o que outro elemento já mostra no mesmo quadro.
- [ ] Texto legível no celular (regras de tela na [ui-para-video](../../ui-para-video/SKILL.md)).
- [ ] Transições sem rastro: o que sai some antes de o próximo ocupar o lugar.
- [ ] O fim não contradiz o que acabou de ser mostrado.
