# 04-projetos: um projeto por vídeo

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** cada vídeo ganha a sua pasta `AAAA-MM-DD-tema/`, copiada de [_modelo/](_modelo/README.md). O `README.md` do projeto é a ficha: ideia, critério de pronto e o checklist das etapas de [video-do-zero](../06-metodo/video-do-zero.md), marcado conforme avança.

## Estrutura de um projeto

```
04-projetos/AAAA-MM-DD-tema/
├── README.md        ← ficha + checklist
├── roteiro.md       ← estrutura (IA) e texto final (seu)
├── referencias/     ← referências deste vídeo e a análise delas
├── assets/          ← prints, logos, fotos, gravações de tela
├── audio/           ← narração aprovada, trilha, eventos.json, mix
├── motor/           ← projeto do After Effects, EffectCraft, HyperFrames ou Remotion
├── render/          ← prévias e final
└── revisao/         ← quadros, comparações, notas
```

Arquivo pesado (vídeo bruto, render, projeto do After Effects) não entra no git: o `.gitignore` da raiz já cuida disso.
