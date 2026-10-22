# Anotações: o registro de cada sessão

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** toda sessão de trabalho termina com uma anotação curta, para o próximo agente (ou você daqui a um mês) saber o que foi feito, o que ficou decidido e o que falta. Um arquivo por assunto, organizado por mês.

## Como registrar (a IA faz antes de encerrar)

1. Arquivo `anotacoes/AAAA-MM/AAAA-MM-DD-assunto-curto.md` (minúsculas, sem acento, com hífens). Mesmo assunto no mesmo dia: continue no mesmo arquivo.
2. Uma linha no topo de `anotacoes/AAAA-MM/_indice.md`: `- DD/MM — [Título](arquivo.md)`. Mês novo: crie a pasta e o índice.
3. Escreva para o próximo agente, no modelo:

```markdown
# Título do assunto

> Data: AAAA-MM-DD · Projeto: <pasta>

- **Pedido:** o que foi pedido.
- **Feito:** o que mudou, com os caminhos dos arquivos.
- **Decisões:** o que ficou definido e por quê.
- **Verificação:** o que foi conferido e o que ficou sem conferir.
- **Próximo:** o que falta e de quem depende.
```

## Como ler

Abra o índice do mês e só os arquivos do assunto. Para achar um tema sem saber a data: `rg -il "palavra" anotacoes`. A memória do ai-memory também guarda as sessões e responde a "onde paramos?".
