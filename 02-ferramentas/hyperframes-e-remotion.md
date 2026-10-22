# HyperFrames e Remotion: vídeo em código

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** dois jeitos de fazer vídeo escrevendo código, sem programa de edição: HyperFrames usa HTML e GSAP, Remotion usa React. A IA escreve a composição, mostra a prévia no navegador e renderiza em MP4. Ótimos para telas de app, texto animado, gráficos e peças em série.

- **Como acessar:** pelas skills (`hyperframes` e `remotion-best-practices`), que a IA carrega sozinha quando você pede um vídeo nesses motores. Os comandos rodam por `npx` dentro da pasta `motor/` do projeto.
- **Instalação:** as skills vêm do instalador (`npx skills add heygen-com/hyperframes` e `npx skills add remotion-dev/skills`). O programa em si é instalado por projeto, na primeira vez.
- **Credenciais:** nenhuma para uso local.
- **Comandos mais usados:**
  - HyperFrames: `npx hyperframes preview`, `npx hyperframes check`, `npx hyperframes render` (a skill `hyperframes` explica o resto).
  - Remotion: `npx create-video@latest --yes --blank meu-video`, `npx remotion studio`, `npx remotion render src/index.ts <Composicao> render/final.mp4`.
- **Pegadinhas:** caminho com "ç" quebra a extração de vídeo do HyperFrames: renderize de uma pasta sem acento. Desfoque de movimento em HTML: renderize a 240 qps e junte 4 quadros (ver `06-metodo/regras.md`).
- **Log:**
