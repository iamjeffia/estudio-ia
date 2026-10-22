# Roteiro 1: o segundo cérebro

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** instruções para a IA transformar a pasta que a pessoa criou no segundo cérebro dela: baixa o modelo para dentro da pasta, liga a memória entre sessões e entre agentes (ai-memory) e preenche o perfil numa conversa curta. Pronto quando o `01-sobre-mim/perfil.md` estiver preenchido, o `.ai-memory.toml` existir e uma sessão nova da IA souber responder "o que você sabe sobre mim?". Próximo passo: o roteiro 2, `setup/2-instalar.md`.

## Para a IA: como conduzir

Quem colou o prompt pode não ser técnico. Fale em português simples, execute tudo sozinho, confira e corrija. Só chame a pessoa para login, senha do computador, uma janela que só ela pode clicar ou uma decisão; nesses casos, deixe tudo pronto e diga em uma linha o que ela precisa fazer. Tempo esperado: 5 a 10 minutos, metade disso na conversa do perfil.

Este roteiro vem **antes** da instalação das ferramentas: não use `uv`, Python ou outra coisa que só o roteiro 2 instala.

### 1. Baixe o modelo para dentro desta pasta

A pasta do estúdio é a pasta em que a IA foi aberta. Se ela já tem o `AGENTS.md` e a pasta `setup/` deste modelo, pule para o passo 2.

1. **Confira o lugar.** Se o caminho tiver acento, "ç" ou espaço, ou estiver dentro do OneDrive ou do iCloud (a pasta `.venv` da instalação é pesada e trava a sincronização), avise a pessoa e sugira uma pasta como `C:\estudio-ia` ou `~/estudio-ia`. Se ela preferir ficar onde está, siga.
2. **Git instalado?** Teste `git --version`. Sem ele: no Windows, `winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements` (feche e abra o terminal se o comando não aparecer); no Mac, `xcode-select --install` e peça para a pessoa clicar em Instalar na janela que abrir.
3. **Baixe o modelo para a pasta atual.** Funciona com a pasta vazia ou com arquivos da pessoa dentro (os dela não são apagados):

   ```
   git init -b main
   git remote add modelo https://github.com/oldmoneygit/estudio-ia
   git fetch modelo main
   git checkout -B main --track modelo/main
   ```

   Se o `checkout` recusar porque um arquivo da pessoa tem o mesmo nome de um arquivo do modelo, renomeie o dela (ex.: `README.md` vira `README-meu.md`), avise e rode o `checkout` de novo.
4. O remoto se chama `modelo` de propósito: o conteúdo da pessoa (perfil, projetos, anotações) é dela e não deve ir para o repositório público. Para puxar atualizações do modelo no futuro: `git pull modelo main`. Se ela quiser backup na nuvem, sugira um repositório **privado** na conta dela no GitHub e só o crie com o consentimento dela.

### 2. Instale o ai-memory

O ai-memory é um servidor local de memória (código aberto, `github.com/akitaonrails/ai-memory`). Ele grava sozinho o que acontece nas sessões do Claude Code e do Codex num wiki em markdown, e devolve o contexto na sessão seguinte, em qualquer um dos dois. Nada sai do computador.

- Mac: `curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/install.sh | sh`
- Windows (PowerShell): `irm https://github.com/akitaonrails/ai-memory/releases/latest/download/install.ps1 | iex`

Depois, ligue-o à IA que está rodando agora (e ao Codex também, se ele já estiver instalado):

```
ai-memory setup --yes --agent claude-code
```

Troque por `--agent codex` se você for o Codex, ou passe os dois (`--agent claude-code --agent codex`) quando os dois estiverem instalados. O roteiro 2 liga o agente que for instalado depois.

Num terminal aberto antes da instalação, o comando ainda não está no PATH: chame `~/.local/bin/ai-memory` (Mac) ou `& "$env:LOCALAPPDATA\Programs\ai-memory\ai-memory.exe"` (Windows).

**Pegadinha do Windows com o app do Claude:** o aplicativo Claude para desktop roda isolado (pacote MSIX). Um comando de instalação executado dentro dele grava os dados num lugar virtual, que os outros programas não enxergam. Se você estiver dentro do app (o caminho do executável ou o `$env:LOCALAPPDATA` aponta para `...\Packages\Claude_...`), rode o `setup` fora do isolamento:

```powershell
$exe = "$env:LOCALAPPDATA\Programs\ai-memory\ai-memory.exe"
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "`"$exe`" setup --yes --agent claude-code" }
```

Espere uns 20 segundos e confira com `ai-memory status` (a saída deve dizer que o servidor está respondendo). Se o `setup` terminar com linhas `problem:`, mostre-as à pessoa; não tente contornar o problema editando configurações à mão.

**Codex: aprovar os ganchos uma vez.** O Codex não executa ganchos novos sem permissão, e o `setup` avisa que os ganchos do ai-memory ainda não foram aprovados. Quando o Codex estiver ligado, peça para a pessoa abrir o `codex` na pasta do estúdio, digitar `/hooks` e aprovar os ganchos do ai-memory. Sem isso, o Codex lê a memória, mas não grava as sessões dele.

### 3. Dê um nome ao projeto na memória

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

### 4. Preencha o perfil numa conversa curta

Faça as perguntas de `01-sobre-mim/perfil.md` em blocos de 2 ou 3, como uma conversa, não como formulário. Aceite respostas curtas e áudio transcrito. Preencha o arquivo com as palavras da pessoa, troque a data, mude o status para `vigente` e **apague as duas linhas de comentário do topo** (o marcador `PERFIL-EM-BRANCO`).

Se ela tiver um perfil público (Instagram, YouTube, site), você pode olhá-lo para entender o estilo dela, desde que ela permita.

### 5. Guarde o primeiro fato na memória

Grave no ai-memory, como página durável, um resumo do perfil (quem é, o que cria, estilo, objetivo) e a decisão de usar esta pasta como segundo cérebro. Use a skill `ai-memory-durable-pages` se ela estiver instalada; senão, a ferramenta `memory_write_page` do MCP (ela só aparece depois de reabrir a IA: se for o caso, deixe este passo para o começo da próxima sessão).

### 6. Teste e termine

1. Faça o primeiro commit local: `git add -A && git commit -m "Meu estúdio: segundo cérebro"`. Se o git pedir nome e e-mail, use os da pessoa só para este repositório (`git config user.name` / `git config user.email`, sem `--global`).
2. Registre a sessão em `anotacoes/` (método no `_LEIA.md` da pasta).
3. Peça para a pessoa fechar a IA, abri-la de novo nesta pasta e perguntar: **"o que você sabe sobre mim e sobre este estúdio?"**. A resposta tem que trazer o perfil.
4. Explique a regra que vale daqui em diante: **sempre abrir a IA dentro desta pasta.**
5. Próximo passo: o roteiro 2, `setup/2-instalar.md`, que instala as ferramentas de edição.
