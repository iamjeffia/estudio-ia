# Roteiro 1: instalar tudo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** instruções para a IA (Claude Code ou Codex) deixar o computador pronto para editar vídeo com IA: programas, bibliotecas Python de áudio e vídeo, skills e motores (EffectCraft, HyperFrames, Remotion e, se houver, After Effects). Pronto quando `uv run setup/conferir.py` disser "Essencial pronto".

## Para a IA: como conduzir

Quem colou o prompt pode não ser técnico. Fale em português simples, execute tudo sozinho, confira e corrija. Só chame a pessoa para login, senha do computador ou janela em que só ela pode clicar; nesses casos, deixe tudo pronto e diga em uma linha o que ela precisa fazer.

### 0. A pasta do estúdio

Se você ainda não está dentro do repositório `estudio-ia`, clone-o na pasta pessoal do usuário, fora do OneDrive e do iCloud (a pasta `.venv` é pesada e trava a sincronização):

- Windows: `git clone https://github.com/oldmoneygit/estudio-ia "$HOME\estudio-ia"`
- Mac: `git clone https://github.com/oldmoneygit/estudio-ia ~/estudio-ia`

Sem `git` no Windows, baixe o zip (`https://github.com/oldmoneygit/estudio-ia/archive/refs/heads/main.zip`), extraia-o nesse mesmo lugar e continue; o Git fica por conta do instalador. Se o nome da pasta do usuário tiver acento, "ç" ou espaço, use `C:\estudio-ia` (alguns renderizadores quebram com esses caracteres). Depois, trabalhe sempre de dentro dessa pasta.

### 1. Avise o tempo antes de começar

Conte à pessoa, antes de rodar, quanto vai demorar e quanto vai baixar:

| Parte | Download | Internet de 100 Mb/s | Internet de 30 Mb/s |
|---|---|---|---|
| Programas base (Git, Node, FFmpeg, uv) | ~250 MB | 1 a 3 min | 3 a 6 min |
| Bibliotecas Python, modo leve | ~770 MB | ~1 min | ~4 min |
| IA de áudio sem placa NVIDIA (Mac ou PC comum) | +~650 MB | +1 min | +3 min |
| IA de áudio com placa NVIDIA | +~4,4 GB | +6 min | +20 min |
| Skills, navegador de render e EffectCraft | ~400 MB | 1 a 2 min | 3 a 5 min |
| **Total típico** | **2 a 6 GB** | **10 a 20 min** | **20 a 45 min** |

Medido em 22/10/2026 em máquinas limpas do GitHub (internet de datacenter, bem mais rápida que a de casa): o instalador inteiro levou 2 min 53 s no Windows e 2 min 27 s no Mac. Em casa, a diferença é quase toda o tempo de download da tabela.

Espaço livre recomendado: 15 GB. Os modelos de separação de voz (~1,5 GB) só baixam no primeiro uso.

### 2. Rode o instalador

Os instaladores fazem tudo em sequência e pulam o que já existe. Rode o instalador em segundo plano e acompanhe a saída; a cada etapa concluída, avise a pessoa em uma linha.

- Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File setup\instalar-windows.ps1`
- Mac (Terminal): `bash setup/instalar-mac.sh` (o Homebrew pede a senha do Mac uma vez; peça para a pessoa digitar)

Opções: `-Leve` / `--leve` (sem IA de áudio, para computador fraco ou internet lenta), `-SemEffectCraft` / `--sem-effectcraft`, `-SemIAs` / `--sem-ias`.

O que cada etapa faz:

1. **Programas base:** Git, Node.js, FFmpeg e uv (que instala o próprio Python 3.11).
2. **IAs:** Claude Code e Codex. A pessoa faz o login de cada um depois (`claude` e `codex` no terminal), se ainda não fez.
3. **Bibliotecas Python** (`uv sync`), detalhadas no `pyproject.toml`: numpy, scipy, soundfile, librosa, pyloudnorm, pedalboard (efeitos de áudio), faster-whisper (transcrição e legenda), opencv e Pillow (quadros), Playwright (render de HTML), yt-dlp (baixar vídeo); com a IA de áudio, também torch, beat_this (batidas da música) e audio-separator (voz e instrumental). Com placa NVIDIA, o instalador escolhe sozinho a versão CUDA.
4. **Skills:** liga as skills do estúdio (`.agents/skills`) ao Claude Code e instala as externas no Claude Code e no Codex: HyperFrames, Remotion, transições, `watch` (assistir a vídeos) e humanizer.
5. **Sons iniciais:** gera uma biblioteca de efeitos sonoros nivelados em `05-biblioteca/som/sfx`.
6. **EffectCraft:** baixa a versão portátil oficial (gratuita) e registra o servidor MCP `effectcraft` no Claude Code e no Codex.
7. **After Effects:** só confere. O After Effects é pago e opcional; quem tiver o programa instala a ponte com a IA (Motion Kit AE) pelo comando em `https://clubedomotion.com/kit-ae`.
8. **Conferência:** `uv run setup/conferir.py` grava `02-ferramentas/inventario.md`.

### 3. Se algo falhar

Resolva antes de seguir. Caminhos alternativos:

| Falhou | Tente |
|---|---|
| `winget` não existe | instale o Instalador de Aplicativo pela Microsoft Store ou baixe o instalador do site oficial de cada programa |
| Programa instalou, mas "não encontrado" | o terminal ainda não carregou o novo PATH: abra outra janela e rode de novo |
| `uv sync` com erro de rede | rode de novo (ele continua de onde parou); internet instável: `-Leve` agora e a IA de áudio depois |
| torch ou audio-separator não instala | `uv sync --extra cpu` (sem CUDA) e siga em frente, porque essa parte é opcional |
| `npx skills add` falha | rode sozinho o comando que falhou para ver o erro; em rede com proxy, configure o npm |
| EffectCraft não baixa | baixe o zip portátil em `https://github.com/storytold/effectcraft/releases/latest` e extraia em `%LOCALAPPDATA%\Programs\EffectCraft` (Mac: `~/Applications/EffectCraft`), depois rode o instalador de novo |

### 4. Termine

1. Rode `uv run setup/conferir.py` e mostre o resumo à pessoa.
2. Se ela ainda não fez login no Claude Code ou no Codex, diga como.
3. Diga o tempo total que o instalador mostrou.
4. Próximo passo: o roteiro 2, `setup/2-segundo-cerebro.md`. Se esta sessão começou antes da instalação das skills, peça para a pessoa fechar a IA e abri-la de novo dentro da pasta do estúdio; só então siga.
