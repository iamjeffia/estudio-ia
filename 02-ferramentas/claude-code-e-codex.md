# Claude Code e Codex

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** as duas IAs que operam o estúdio. As duas leem as mesmas regras (`AGENTS.md`; o `CLAUDE.md` só importa esse arquivo), as mesmas skills (`.agents/skills`) e a mesma memória (ai-memory). Dá para começar numa e continuar na outra.

- **Como acessar:** terminal, dentro da pasta do estúdio: `claude` ou `codex`. Também funcionam nos apps de desktop e nas extensões de editor, desde que abertos nesta pasta.
- **Instalação:** Claude Code pelo instalador oficial (`irm https://claude.ai/install.ps1 | iex` no Windows, `curl -fsSL https://claude.ai/install.sh | bash` no Mac); Codex por `npm install -g @openai/codex`.
- **Credenciais:** o login fica na configuração de cada um (conta Claude e conta ChatGPT). Nada nesta pasta.
- **Comandos mais usados:**
  - `claude mcp list` / `codex mcp list`: ver as ferramentas ligadas (EffectCraft, After Effects, ai-memory).
  - `ai-memory run codex`: abre o Codex já com o contexto da última sessão do Claude Code (e vice-versa).
- **Pegadinhas:** sessão aberta antes de instalar uma skill ou um MCP não enxerga a novidade: feche e abra de novo. No Windows, o app Claude para desktop roda isolado; instaladores de serviço (como o `ai-memory setup`) precisam rodar fora dele (ver roteiro 2).
- **Log:**
