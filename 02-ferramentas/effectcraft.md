# EffectCraft

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** editor de motion graphics gratuito e de código aberto, no estilo do After Effects (camadas, keyframes, efeitos com os mesmos nomes), com servidor MCP: a IA cria a composição, anima, aplica efeitos e renderiza sem você clicar. Bom para começar sem pagar o After Effects.

- **Como acessar:** app EffectCraft; a IA usa o MCP `effectcraft` (ferramentas `command_list`, `command_run`, `render_preview`, `get_comp`).
- **Instalação:** passo 6 do instalador (versão portátil oficial de `github.com/storytold/effectcraft/releases`) e registro do MCP: `claude mcp add effectcraft -s user -- <caminho>/effectcraft-cli mcp` e `codex mcp add effectcraft -- <caminho>/effectcraft-cli mcp`.
- **Credenciais:** nenhuma.
- **Fluxo típico da IA:** `comp.new` → `layer.newText` / `layer.newSolid` → `set_property` / `add_keyframe` → `effect.apply` → `render_preview` para olhar o resultado. Tempos em segundos.
- **Pegadinhas:** projeto novo (versões alfa, mudam rápido): atualize rodando o instalador de novo. Pode ser mais lento e usar mais memória que o After Effects em renders longos. Fonte que só o After Effects enxerga (pasta de fontes da Adobe) precisa ser instalada no sistema para o EffectCraft usar.
- **Log:**
