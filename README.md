# Estúdio de IA

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** um modelo pronto para editar vídeo com IA. Você cola um prompt na sua IA (Claude Code ou Codex) e ela instala tudo: programas, bibliotecas de áudio e vídeo, skills de motion e de som, e os motores de edição (After Effects, EffectCraft, HyperFrames e Remotion). Depois, com mais dois prompts, ela monta o seu segundo cérebro e a sua pasta de referências.

## O que vem dentro

- **Instalação em um prompt** para Windows e Mac. O instalador pula o que você já tem e mostra quanto tempo levou cada etapa.
- **Segundo cérebro organizado:** pastas para ideias, perfil, ferramentas, referências, projetos, biblioteca e método, com regras que o Claude Code e o Codex leem automaticamente.
- **Memória entre sessões e entre IAs** com o [ai-memory](https://github.com/akitaonrails/ai-memory): o que você fez ontem no Claude Code, o Codex sabe hoje.
- **Pasta de referências**, no computador ou no Google Drive: você joga tudo numa pasta e a IA organiza, cataloga e analisa.
- **Método de vídeo do zero** em 10 etapas, com os números que funcionam (mola, câmera, volume, render).
- **Skills do estúdio:** `estudio-video` (por onde todo vídeo começa), `video-referencias`, `motion-narrado`, `animacao-saas`, `ui-para-video` e `som-do-video`. O instalador acrescenta as skills externas: HyperFrames, Remotion, transições, `watch` (para a IA assistir a vídeos) e humanizer.
- **Scripts de som e vídeo:** mesa de som que gera a mixagem a partir dos eventos da animação, nivelamento de efeitos sonoros, detecção das batidas da música, separação de voz e instrumental, legendas, corte de pausas, análise quadro a quadro e detector de quadros pulados.

## Como começar

### Prompt 1: instalar tudo

Abra o Claude Code ou o Codex e cole:

```text
Quero montar meu estúdio de edição de vídeo com IA. Baixe o modelo de https://github.com/oldmoneygit/estudio-ia e siga o roteiro setup/1-instalar.md até o fim. Fale comigo em português simples, faça tudo sozinho e só me chame quando eu precisar fazer login ou digitar uma senha.
```

**Ainda não tem nenhuma IA instalada?** Um comando faz o mesmo e já instala o Claude Code e o Codex:

- Windows (PowerShell):

  ```powershell
  irm https://raw.githubusercontent.com/oldmoneygit/estudio-ia/main/setup/comecar.ps1 | iex
  ```

- Mac (Terminal):

  ```bash
  curl -fsSL https://raw.githubusercontent.com/oldmoneygit/estudio-ia/main/setup/comecar.sh | bash
  ```

**Quanto demora:** de 10 a 20 minutos numa internet de 100 Mb/s (de 20 a 45 minutos numa de 30 Mb/s), e quase todo esse tempo é espera de download. São de 2 a 6 GB, conforme o computador tenha ou não placa NVIDIA. Deixe 15 GB livres.

### Prompt 2: o segundo cérebro

Abra a IA dentro da pasta `estudio-ia` e cole:

```text
Siga o roteiro setup/2-segundo-cerebro.md até o fim.
```

A IA instala a memória, conversa com você por uns minutos para preencher o seu perfil e atualiza os docs das ferramentas. Leva de 5 a 10 minutos.

### Prompt 3: as referências

```text
Siga o roteiro setup/3-referencias.md até o fim.
```

Você escolhe se a pasta fica no computador ou no Google Drive, e a IA cria as categorias e faz uma rodada de organização como teste.

### Depois disso

Peça o primeiro vídeo: "vamos fazer um vídeo sobre <assunto>". A IA segue o [passo a passo](06-metodo/video-do-zero.md), abre um projeto em `04-projetos/` e vai marcando cada etapa.

## As pastas

| Pasta | O que guarda |
|---|---|
| `00-entrada/` | Ideia crua, ditado, print solto |
| `01-sobre-mim/` | Seu perfil: quem é, o que cria, como fala |
| `02-ferramentas/` | Um doc por ferramenta e o inventário gerado pelo setup |
| `03-referencias/` | Referências organizadas, catálogo e análises |
| `04-projetos/` | Um projeto por vídeo |
| `05-biblioteca/` | Efeitos sonoros, músicas, fontes e assets |
| `06-metodo/` | Passo a passo, números que valem e aprendizados |
| `scripts/` | Scripts de som, vídeo e referências |
| `anotacoes/` | O registro de cada sessão |
| `setup/` | Instaladores e os três roteiros |

## Conferir e atualizar

- Ver o que está instalado: `uv run setup/conferir.py` (gera `02-ferramentas/inventario.md`).
- Atualizar o modelo sem perder o que é seu: `git pull modelo main` (o roteiro 2 dá esse nome ao remoto).
- Rodar o instalador de novo é seguro: ele só instala o que falta.

## Requisitos

Windows 10 ou 11, ou macOS 13 ou mais novo, com 8 GB de RAM (16 GB recomendados para render) e 15 GB livres em disco. A placa NVIDIA é opcional: acelera a separação de voz e a detecção de batidas. O After Effects é opcional e pago; o EffectCraft, o HyperFrames e o Remotion são gratuitos.
