# Estúdio de IA

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** um modelo pronto para editar vídeo com IA. São três prompts colados na sua IA (Claude Code ou Codex): o primeiro transforma uma pasta sua no seu segundo cérebro, o segundo instala tudo o que a edição precisa (programas, bibliotecas de áudio e vídeo, skills de motion e de som, e os motores After Effects, EffectCraft, HyperFrames e Remotion) e o terceiro cria a sua pasta de referências.

## O que vem dentro

- **Segundo cérebro e instalação, um prompt cada,** para Windows e Mac. O instalador pula o que você já tem e mostra quanto tempo levou cada etapa.
- **Segundo cérebro organizado:** pastas para ideias, perfil, ferramentas, referências, projetos, biblioteca e método, com regras que o Claude Code e o Codex leem automaticamente.
- **Memória entre sessões e entre IAs** com o [ai-memory](https://github.com/akitaonrails/ai-memory): o que você fez ontem no Claude Code, o Codex sabe hoje.
- **Pasta de referências**, no computador ou no Google Drive: você joga tudo numa pasta e a IA organiza, cataloga e analisa.
- **Método de vídeo do zero** em 10 etapas, com os números que funcionam (mola, câmera, volume, render).
- **Skills do estúdio:** `estudio-video` (por onde todo vídeo começa), `video-referencias`, `motion-narrado`, `animacao-saas`, `ui-para-video` e `som-do-video`. O instalador acrescenta as skills externas: HyperFrames, Remotion, transições, `watch` (para a IA assistir a vídeos) e humanizer.
- **Scripts de som e vídeo:** mesa de som que gera a mixagem a partir dos eventos da animação, nivelamento de efeitos sonoros, detecção das batidas da música, separação de voz e instrumental, legendas, corte de pausas, análise quadro a quadro e detector de quadros pulados.

## Como começar

### Prompt 1: o segundo cérebro

Crie uma pasta nova onde você quer guardar o seu segundo cérebro (de preferência fora do OneDrive e do iCloud, e sem acento no nome), abra o Claude Code ou o Codex dentro dela e cole:

```text
Quero transformar esta pasta no meu segundo cérebro para vídeo com IA. Baixe o modelo de https://github.com/iamjeffia/estudio-ia para dentro dela e siga o roteiro setup/1-segundo-cerebro.md até o fim. Fale comigo em português simples.
```

A IA baixa a estrutura, liga a memória e conversa com você por uns minutos para preencher o seu perfil. Leva de 5 a 10 minutos. Daqui em diante, abra a sua IA sempre dentro dessa pasta.

### Prompt 2: as ferramentas de edição

Na mesma pasta, cole:

```text
Siga o roteiro setup/2-instalar.md até o fim e deixe meu computador pronto para editar vídeo.
```

**Quanto demora:** de 10 a 20 minutos numa internet de 100 Mb/s (de 20 a 45 minutos numa de 30 Mb/s), e quase todo esse tempo é espera de download. São de 2 a 6 GB, conforme o computador tenha ou não placa NVIDIA. Deixe 15 GB livres. A IA só te chama se precisar de login ou senha.

**Ainda não tem nenhuma IA instalada?** Um comando baixa o estúdio em `estudio-ia` na sua pasta pessoal e instala tudo, inclusive o Claude Code e o Codex. Depois é só abrir a IA nessa pasta e colar o prompt 1.

- Windows (PowerShell):

  ```powershell
  irm https://raw.githubusercontent.com/iamjeffia/estudio-ia/main/setup/comecar.ps1 | iex
  ```

- Mac (Terminal):

  ```bash
  curl -fsSL https://raw.githubusercontent.com/iamjeffia/estudio-ia/main/setup/comecar.sh | bash
  ```

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
- Atualizar o modelo sem perder o que é seu: `git pull modelo main` (o roteiro 1 dá esse nome ao remoto).
- Rodar o instalador de novo é seguro: ele só instala o que falta.

## Requisitos

Windows 10 ou 11, ou macOS 13 ou mais novo, com 8 GB de RAM (16 GB recomendados para render) e 15 GB livres em disco. A placa NVIDIA é opcional: acelera a separação de voz e a detecção de batidas. O After Effects é opcional e pago; o EffectCraft, o HyperFrames e o Remotion são gratuitos.
