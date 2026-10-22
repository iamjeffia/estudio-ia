# ai-memory: a memória do estúdio

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** servidor local de memória, de código aberto, que grava sozinho as sessões do Claude Code e do Codex num wiki em markdown e devolve o contexto na sessão seguinte, em qualquer um dos dois. É a memória do projeto: fatos duráveis, regras aprendidas e decisões ficam nele.

- **Como acessar:** automático (hooks e MCP). No terminal: `ai-memory status`, `ai-memory search "palavra"`. Painel web: `http://127.0.0.1:49374/web`.
- **Instalação:** roteiro 2 (`setup/2-segundo-cerebro.md`). Projeto deste estúdio: `.ai-memory.toml` na raiz.
- **Credenciais:** o token de acesso fica num arquivo só do dono, na pasta de dados do ai-memory. Nunca copiar para doc, chat ou configuração.
- **Comandos mais usados:**
  - `ai-memory doctor`: confere se cada agente está gravando neste projeto.
  - `ai-memory run codex` (ou `claude`): abre o agente já com o histórico da sessão anterior do outro.
  - `ai-memory install-instructions --target AGENTS.md`: atualiza o bloco de instruções no `AGENTS.md`.
  - `ai-memory upgrade`: nova versão.
- **No dia a dia, peça à IA:** "onde paramos?", "o que fizemos sobre X?", "lembra disso para sempre: …".
- **Pegadinhas:** sessão aberta antes da instalação só passa a gravar depois de reiniciar o agente. No Windows, rodar o `setup` de dentro do app Claude para desktop grava num lugar virtual (ver roteiro 2).
- **Log:**
