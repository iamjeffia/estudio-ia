# Roteiro 2: o segundo cérebro

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** instruções para a IA transformar esta pasta no segundo cérebro da pessoa: memória entre sessões e entre agentes (ai-memory), perfil preenchido numa conversa curta, docs das ferramentas atualizados com o que foi instalado e a pasta separada do modelo original. Pronto quando o `conferir.py` marcar "Perfil preenchido" e "Projeto no ai-memory", e uma sessão nova da IA souber responder "o que você sabe sobre mim?".

## Para a IA: como conduzir

Conduza do mesmo jeito que no roteiro 1: português simples, você executa e confere, a pessoa só entra para login, senha ou decisão. Tempo esperado: 5 a 10 minutos, metade disso na conversa do perfil.

### 1. Instale o ai-memory

O ai-memory é um servidor local de memória (código aberto, `github.com/akitaonrails/ai-memory`). Ele grava sozinho o que acontece nas sessões do Claude Code e do Codex num wiki em markdown, e devolve o contexto na sessão seguinte, em qualquer um dos dois. Nada sai do computador.

- Mac: `curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/install.sh | sh`
- Windows (PowerShell): `irm https://github.com/akitaonrails/ai-memory/releases/latest/download/install.ps1 | iex`

Depois, ligue-o aos agentes instalados:

```
ai-memory setup --yes --agent claude-code --agent codex
```

Num terminal aberto antes da instalação, o comando ainda não está no PATH: chame `~/.local/bin/ai-memory` (Mac) ou `& "$env:LOCALAPPDATA\Programs\ai-memory\ai-memory.exe"` (Windows).

**Pegadinha do Windows com o app do Claude:** o aplicativo Claude para desktop roda isolado (pacote MSIX). Um comando de instalação executado dentro dele grava os dados num lugar virtual, que os outros programas não enxergam. Se você estiver dentro do app (o caminho do executável ou o `$env:LOCALAPPDATA` aponta para `...\Packages\Claude_...`), rode o `setup` fora do isolamento:

```powershell
$exe = "$env:LOCALAPPDATA\Programs\ai-memory\ai-memory.exe"
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "`"$exe`" setup --yes --agent claude-code --agent codex" }
```

Espere uns 20 segundos e confira com `ai-memory status` (a saída deve dizer que o servidor está respondendo). Se o `setup` terminar com linhas `problem:`, mostre-as à pessoa; não tente contornar o problema editando configurações à mão.

**Codex: aprovar os ganchos uma vez.** O Codex não executa ganchos novos sem permissão, e o `setup` avisa que os ganchos do ai-memory ainda não foram aprovados. Peça para a pessoa abrir o `codex` na pasta do estúdio, digitar `/hooks` e aprovar os ganchos do ai-memory. Sem isso, o Codex lê a memória, mas não grava as sessões dele.

### 2. Dê um nome ao projeto na memória

Pergunte o nome ou apelido da pessoa (vai servir para o perfil também) e crie o `.ai-memory.toml` na raiz:

```toml
# ai-memory: fixa a memória deste estúdio num projeto só, para o Claude Code
# e o Codex caírem no mesmo lugar.
workspace = "default"
project = "<apelido-em-minusculas>-estudio"
```

Depois acrescente o bloco de instruções do ai-memory ao `AGENTS.md` (o `CLAUDE.md` importa o `AGENTS.md`, então os dois agentes leem o bloco):

```
ai-memory install-instructions --target AGENTS.md
```

Confira se o bloco entrou no fim do `AGENTS.md` sem apagar o resto.

### 3. Separe a pasta do modelo

Esta pasta veio de um modelo público. O conteúdo da pessoa (perfil, projetos, anotações) é dela e não deve ir para lá. Renomeie o remoto, para que continue possível puxar as atualizações do modelo:

```
git remote rename origin modelo
```

Para atualizar o modelo no futuro: `git pull modelo main`. Se a pessoa quiser backup na nuvem, sugira um repositório **privado** na conta dela no GitHub (`gh repo create meu-estudio --private --source . --push`) e só o crie com o consentimento dela.

### 4. Preencha o perfil numa conversa curta

Faça as perguntas de `01-sobre-mim/perfil.md` em blocos de 2 ou 3, como uma conversa, não como formulário. Aceite respostas curtas e áudio transcrito. Preencha o arquivo com as palavras da pessoa, troque a data, mude o status para `vigente` e **apague as duas linhas de comentário do topo** (o marcador `PERFIL-EM-BRANCO`).

Se ela tiver um perfil público (Instagram, YouTube, site), você pode olhá-lo para entender o estilo dela, desde que ela permita.

### 5. Atualize os docs das ferramentas

1. Rode `uv run setup/conferir.py` para atualizar `02-ferramentas/inventario.md`.
2. Em cada doc de `02-ferramentas/` cuja ferramenta está instalada, acrescente no **Log** a versão e o caminho reais desta máquina (veja no inventário) e a data de hoje. Nos docs de ferramentas que não estão instaladas, mude o status para `não instalado`.
3. Se a pessoa usa alguma ferramenta que não tem doc (outro editor, banco de imagens, conta de voz), crie o doc seguindo o modelo do `02-ferramentas/_LEIA.md`. Nunca escreva chave, senha ou token: registre só onde cada um está guardado.

### 6. Guarde o primeiro fato na memória

Grave no ai-memory, como página durável, um resumo do perfil (quem é, o que cria, estilo, objetivo) e a decisão de usar esta pasta como segundo cérebro. Use a skill `ai-memory-durable-pages` se ela estiver instalada; senão, a ferramenta `memory_write_page` do MCP.

### 7. Teste e termine

1. Faça o primeiro commit local: `git add -A && git commit -m "Meu estúdio: perfil e ferramentas"`.
2. Registre a sessão em `anotacoes/` (método no `_LEIA.md` da pasta).
3. Peça para a pessoa fechar a IA, abri-la de novo na pasta do estúdio e perguntar: **"o que você sabe sobre mim e sobre este estúdio?"**. A resposta tem que trazer o perfil e o que foi instalado. Se a sessão estiver no Codex, dá para testar também no Claude Code: os dois leem a mesma memória.
4. Próximo passo: o roteiro 3, `setup/3-referencias.md`.
