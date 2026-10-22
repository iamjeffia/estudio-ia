# Instalador do estúdio no Windows. Pode rodar de novo quantas vezes quiser:
# o que já está instalado é pulado.
#   powershell -ExecutionPolicy Bypass -File setup\instalar-windows.ps1            (completo)
#   powershell -ExecutionPolicy Bypass -File setup\instalar-windows.ps1 -Leve      (sem a IA de áudio)
#   ... -SemEffectCraft   pula o EffectCraft
#   ... -SemIAs           não instala o Claude Code nem o Codex (já estão na máquina)
param(
    [switch]$Leve,
    [switch]$SemEffectCraft,
    [switch]$SemIAs
)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$Raiz = Split-Path -Parent $PSScriptRoot
Set-Location $Raiz

$inicio = Get-Date
$resumo = New-Object System.Collections.ArrayList
$script:passoInicio = $null
$script:passoNome = $null

function Passo([string]$nome) {
    Fechar-Passo
    $script:passoNome = $nome
    $script:passoInicio = Get-Date
    Write-Host ""
    Write-Host "== $nome" -ForegroundColor Cyan
}
function Fechar-Passo {
    if ($script:passoNome) {
        $s = [int]((Get-Date) - $script:passoInicio).TotalSeconds
        [void]$resumo.Add(("{0,-38} {1,5} s" -f $script:passoNome, $s))
    }
}
function Ok([string]$t) { Write-Host "   ok  $t" -ForegroundColor Green }
function Aviso([string]$t) { Write-Host "   !!  $t" -ForegroundColor Yellow }
function Tem([string]$cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Atualizar-Path {
    $maquina = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $usuario = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$maquina;$usuario;$env:LOCALAPPDATA\Microsoft\WinGet\Links;$env:USERPROFILE\.local\bin"
}
function Winget-Instalar([string]$id, [string]$comando, [string]$nome) {
    if (Tem $comando) { Ok "$nome já instalado"; return }
    if (-not (Tem 'winget')) { Aviso "winget não encontrado: instale o 'Instalador de Aplicativo' pela Microsoft Store e rode de novo"; return }
    Write-Host "   ... instalando $nome"
    winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements --disable-interactivity | Out-Null
    Atualizar-Path
    if (Tem $comando) { Ok "$nome instalado" } else { Aviso "$nome não respondeu depois da instalação (feche e abra o terminal e rode de novo)" }
}

Write-Host "Estúdio de IA: setup do Windows" -ForegroundColor White
Write-Host "Pasta: $Raiz"
Atualizar-Path

# 1. Programas base -----------------------------------------------------------
Passo "1. Programas base"
if (-not (Tem 'winget')) {
    # Windows sem o Instalador de Aplicativo (ou com ele quebrado): o módulo oficial da Microsoft repara
    Write-Host "   ... winget não encontrado; instalando pelo módulo oficial Microsoft.WinGet.Client"
    try {
        Install-PackageProvider -Name NuGet -Force -Scope CurrentUser -ErrorAction Stop | Out-Null
        Install-Module Microsoft.WinGet.Client -Force -Scope CurrentUser -AllowClobber -ErrorAction Stop | Out-Null
        Import-Module Microsoft.WinGet.Client -ErrorAction Stop
        Repair-WinGetPackageManager -Latest -Force -ErrorAction Stop | Out-Null
        Atualizar-Path
    } catch { Aviso "não deu para instalar o winget: $($_.Exception.Message)" }
    if (Tem 'winget') { Ok "winget instalado" }
}
Winget-Instalar 'Git.Git' 'git' 'Git'
Winget-Instalar 'OpenJS.NodeJS.LTS' 'node' 'Node.js'
Winget-Instalar 'Gyan.FFmpeg' 'ffmpeg' 'FFmpeg'
Winget-Instalar 'astral-sh.uv' 'uv' 'uv (gerenciador de Python)'

# 2. As IAs -------------------------------------------------------------------
Passo "2. Claude Code e Codex"
if ($SemIAs) {
    Ok "pulado (-SemIAs)"
} else {
    if (Tem 'claude') { Ok "Claude Code já instalado" }
    else {
        Write-Host "   ... instalando Claude Code"
        # processo separado: o instalador oficial usa 'exit' quando falha
        powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex"
        Atualizar-Path
        if (Tem 'claude') { Ok "Claude Code instalado" } else { Aviso "Claude Code não respondeu (feche e abra o terminal)" }
    }
    if (Tem 'codex') { Ok "Codex já instalado" }
    elseif (Tem 'npm') {
        Write-Host "   ... instalando Codex"
        npm install -g @openai/codex --silent 2>$null | Out-Null
        Atualizar-Path
        if (Tem 'codex') { Ok "Codex instalado" } else { Aviso "Codex não respondeu" }
    } else { Aviso "npm não encontrado; o Codex fica para a próxima rodada" }
}

# 3. Bibliotecas Python -------------------------------------------------------
Passo "3. Bibliotecas Python"
if (-not (Tem 'uv')) {
    Aviso "uv não encontrado; pulei as bibliotecas"
} else {
    $extra = @()
    if ($Leve) { Ok "modo leve: só a base (sem batidas e separação de voz)" }
    elseif (Tem 'nvidia-smi') { $extra = @('--extra', 'gpu'); Ok "placa NVIDIA encontrada: IA de áudio com CUDA (~5 GB)" }
    else { $extra = @('--extra', 'cpu'); Ok "sem placa NVIDIA: IA de áudio no processador (~1,4 GB)" }
    uv sync @extra
    if ($LASTEXITCODE -eq 0) { Ok "bibliotecas instaladas em .venv" } else { Aviso "uv sync falhou (código $LASTEXITCODE)" }
    Write-Host "   ... navegador para render de HTML (Playwright)"
    uv run playwright install chromium 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok "Chromium do Playwright pronto" } else { Aviso "playwright install falhou" }
}

# 4. Skills ------------------------------------------------------------------
Passo "4. Skills"
$claudeSkills = Join-Path $Raiz '.claude\skills'
if (-not (Test-Path $claudeSkills)) {
    New-Item -ItemType Directory -Force (Join-Path $Raiz '.claude') | Out-Null
    cmd /c mklink /J "$claudeSkills" "$(Join-Path $Raiz '.agents\skills')" | Out-Null
}
if (Test-Path $claudeSkills) { Ok "skills do estúdio ligadas ao Claude Code (.claude\skills -> .agents\skills)" }
if (Tem 'npx') {
    # pacote -> uma skill dele; se ela já existe, o pacote é pulado (não sobrescreve skill editada)
    $pacotes = [ordered]@{
        'heygen-com/hyperframes'       = 'hyperframes'
        'remotion-dev/skills'          = 'remotion-best-practices'
        'Jakubantalik/transitions.dev' = 'transitions-dev'
        'bradautomates/claude-video'   = 'watch'
        'blader/humanizer'             = 'humanizer'
    }
    foreach ($p in $pacotes.Keys) {
        $marca = $pacotes[$p]
        if ((Test-Path "$HOME\.claude\skills\$marca") -or (Test-Path "$HOME\.agents\skills\$marca")) { Ok "$p já instalado"; continue }
        Write-Host "   ... $p"
        npx -y skills add $p -g -y -s '*' -a claude-code codex 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Ok "$p" } else { Aviso "$p falhou (código $LASTEXITCODE)" }
    }
} else { Aviso "npx não encontrado; skills externas ficam para a próxima rodada" }

# 5. Sons iniciais -----------------------------------------------------------
Passo "5. Biblioteca de sons inicial"
$sintetizar = Join-Path $Raiz 'scripts\som\sintetizar_sfx.py'
if ((Tem 'uv') -and (Test-Path $sintetizar)) {
    uv run $sintetizar
    if ($LASTEXITCODE -eq 0) { Ok "efeitos sonoros gerados em 05-biblioteca\som\sfx" } else { Aviso "sintetizar_sfx.py falhou" }
} else { Aviso "pulei os sons (falta o uv ou o script)" }

# 6. EffectCraft -------------------------------------------------------------
Passo "6. EffectCraft"
$ecPasta = Join-Path $env:LOCALAPPDATA 'Programs\EffectCraft'
# só procura em pastas que existem: com pasta inexistente, o -Recurse do PowerShell varre a pasta de cima inteira
$ecPastas = @($ecPasta, "$env:ProgramFiles\EffectCraft") | Where-Object { Test-Path $_ }
$ecCli = if ($ecPastas) { Get-ChildItem -Path $ecPastas -Filter 'effectcraft-cli.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 } else { $null }
if ($SemEffectCraft) {
    Ok "pulado (-SemEffectCraft)"
} else {
    if ($ecCli) { Ok "EffectCraft já instalado" }
    else {
        try {
            Write-Host "   ... baixando a última versão (GitHub storytold/effectcraft)"
            $rel = Invoke-RestMethod 'https://api.github.com/repos/storytold/effectcraft/releases/latest' -Headers @{ 'User-Agent' = 'estudio-ia' }
            $asset = $rel.assets | Where-Object { $_.name -like '*windows-x64-portable.zip' } | Select-Object -First 1
            $zip = Join-Path $env:TEMP $asset.name
            Invoke-WebRequest $asset.browser_download_url -OutFile $zip
            New-Item -ItemType Directory -Force $ecPasta | Out-Null
            Expand-Archive $zip -DestinationPath $ecPasta -Force
            Remove-Item $zip -Force
            $ecCli = Get-ChildItem -Path $ecPasta -Filter 'effectcraft-cli.exe' -Recurse | Select-Object -First 1
            if ($ecCli) { Ok "EffectCraft $($rel.tag_name) em $ecPasta" } else { Aviso "zip baixado, mas o effectcraft-cli.exe não apareceu" }
        } catch { Aviso "não consegui baixar o EffectCraft: $($_.Exception.Message)" }
    }
    if ($ecCli) {
        if (Tem 'claude') {
            claude mcp get effectcraft 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) { claude mcp add effectcraft -s user -- "$($ecCli.FullName)" mcp 2>&1 | Out-Null }
            Ok "EffectCraft ligado ao Claude Code (MCP effectcraft)"
        }
        if (Tem 'codex') {
            codex mcp get effectcraft 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) { codex mcp add effectcraft -- "$($ecCli.FullName)" mcp 2>&1 | Out-Null }
            Ok "EffectCraft ligado ao Codex (MCP effectcraft)"
        }
    }
}

# 7. After Effects -----------------------------------------------------------
Passo "7. After Effects"
$ae = Get-ChildItem "$env:ProgramFiles\Adobe" -Directory -Filter 'Adobe After Effects*' -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName 'Support Files\AfterFX.exe' } | Where-Object { Test-Path $_ } |
    Sort-Object -Descending | Select-Object -First 1 | ForEach-Object { Get-Item $_ }
if ($ae) {
    Ok "After Effects encontrado: $($ae.Directory.Parent.Name)"
    $kit = Join-Path $env:LOCALAPPDATA 'MotionKitAE'
    if (Test-Path $kit) { Ok "Motion Kit AE já instalado" }
    else { Aviso "falta o Motion Kit AE (ponte da IA com o After Effects): pegue o comando em https://clubedomotion.com/kit-ae" }
} else {
    Aviso "After Effects não encontrado. Ele é opcional: o EffectCraft, o HyperFrames e o Remotion funcionam sem ele"
}

# 8. Conferência -------------------------------------------------------------
Passo "8. Conferência"
if (Tem 'uv') { uv run setup/conferir.py } else { Aviso "sem uv, não deu para conferir" }
Fechar-Passo
$script:passoNome = $null

$total = (Get-Date) - $inicio
Write-Host ""
Write-Host "Tempo de cada etapa:" -ForegroundColor White
$resumo | ForEach-Object { Write-Host "   $_" }
Write-Host ("Total: {0:mm\:ss}" -f $total) -ForegroundColor White
Write-Host "Inventário salvo em 02-ferramentas\inventario.md"
