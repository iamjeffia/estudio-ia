# Referências de interface: onde buscar e como guardar

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** antes de criar ou recriar uma tela, busque referência real. Mobbin quando a pessoa tiver; senão Dribbble, Pinterest e as capturas oficiais do produto. Guarde o que usar com link e data.

## Qual fonte usar

| Caso | Fonte |
|---|---|
| Seção de landing: hero, preço, FAQ, depoimentos, recursos, CTA, rodapé | Mobbin `search_sections` |
| Tela de app ou web: dashboard, configurações, perfil, lista, checkout, login | Mobbin `search_screens` (`platform`: `web` ou `ios`) |
| Fluxo com várias telas: onboarding, cadastro, checkout, agendamento | Mobbin `search_flows` |
| Sem Mobbin, ou ele não trouxe nada útil | Dribbble e Pinterest; o site e as capturas oficiais do produto |
| Motion, efeito animado, transição | Pinterest, Dribbble (shots animados) e as bibliotecas de [motion-e-componentes.md](motion-e-componentes.md) |
| Foto, pessoa, ambiente, estética, moodboard | Pinterest |
| Produto real citado no vídeo | o próprio produto: gravação de tela ou capturas oficiais (`/press`, loja de apps) |

## Mobbin (MCP, se instalado)

O nome do servidor muda por cliente; procure as ferramentas `search_sections`, `search_screens` e `search_flows`.

- `query`: descreva **uma** tela ou seção, com os elementos que ela teria. Bom: "pricing section with three plans and monthly/annual toggle". Evite juntar várias telas, negações e adjetivos vagos ("modern").
- Para filtrar por produto, cite o nome: "Calendly pricing page".
- `output_destination`: `code` quando a referência vai virar código; `doc` quando vira relatório.
- `task_intent`: uma frase em inglês com o objetivo, igual em todas as chamadas da mesma tarefa.
- Comece com `limit` de 6 a 10. Olhe as imagens, não só os metadados.
- Para guardar, baixe de `image_url` (o link expira) e cite o `mobbin_url`.

## Pinterest e Dribbble

1. Use o navegador da pessoa com a sessão dela já aberta. O agente não digita senha: se pedir login, a pessoa entra e o agente continua.
2. Busque por palavras-chave curtas, em geral em inglês ("fintech app dark", "SaaS dashboard", "iOS notification UI"), não por frase inteira.
3. Abra o pin ou shot, confira a imagem em tamanho cheio e baixe.
4. Pessoa real em foto é referência de look, idade, roupa, cenário e luz; numa imagem gerada, o rosto muda.

## Como guardar e usar

- Salve em `04-projetos/<projeto>/referencias/` com um `FONTES.md` (link e data de cada uma). Referência boa para outros vídeos também entra em `03-referencias/design/` pelo `uv run scripts/referencias.py mover`.
- Anote por referência o padrão aproveitado ("preço anual com selo de desconto", "plano recomendado elevado").
- Aproveite estrutura, hierarquia, espaçamento e comportamento. Não copie marca, texto, foto ou ilustração de terceiros.
