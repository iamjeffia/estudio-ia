# 02-ferramentas: o que está instalado e como usar

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** um doc por programa, biblioteca ou serviço do estúdio, para qualquer agente saber o que existe e como usar sem depender da memória da conversa. O `inventario.md` é gerado pelo `setup/conferir.py`; os outros docs a IA escreve e atualiza.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `inventario.md` | Tabela gerada: cada ferramenta, versão e se está pronta. Rode `python setup/conferir.py` para atualizar |
| `<ferramenta>.md` | Um doc por ferramenta, no modelo abaixo |

## Regra

Instalou, trocou de versão ou descobriu uma pegadinha? Atualize o doc da ferramenta na mesma sessão. Nunca escreva a chave, a senha ou o token: diga só onde ele está guardado.

## Modelo (`nome-da-ferramenta.md`)

```markdown
# Nome da ferramenta

> Data: AAAA-MM-DD · Tipo: guia · Status: vigente

**Resumo:** para que usamos, em uma frase.

- **Como acessar:** CLI, app, MCP ou biblioteca Python; onde roda.
- **Instalação:** o comando usado e a versão.
- **Credenciais:** onde estão guardadas (nunca o valor).
- **Comandos mais usados:** exemplos reais, para copiar e colar.
- **Pegadinhas:** limites, custo, o que quebra.
- **Log:** AAAA-MM-DD, o que mudou.
```
