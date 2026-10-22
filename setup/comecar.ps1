# Um comando para começar do zero no Windows (PowerShell):
#   irm https://raw.githubusercontent.com/oldmoneygit/estudio-ia/main/setup/comecar.ps1 | iex
# Instala o Git, baixa o estúdio em $HOME\estudio-ia (ou C:\estudio-ia se o nome
# do usuário tiver acento ou espaço) e roda o instalador completo.
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function Atualizar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"
}

$destino = Join-Path $HOME 'estudio-ia'
if ($HOME -match '[^\x00-\x7F]|\s') { $destino = 'C:\estudio-ia' }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando o Git..."
    winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements --disable-interactivity | Out-Null
    Atualizar-Path
}
if (Test-Path (Join-Path $destino '.git')) {
    Write-Host "O estúdio já existe em $destino; atualizando"
    git -C $destino pull --ff-only
} else {
    git clone https://github.com/oldmoneygit/estudio-ia $destino
}
if (-not (Test-Path (Join-Path $destino 'setup\instalar-windows.ps1'))) {
    Write-Host "Não consegui baixar o estúdio. Confira a internet e rode o comando de novo." -ForegroundColor Red
    return
}
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $destino 'setup\instalar-windows.ps1')
Write-Host ""
Write-Host "Pronto. Agora abra a IA dentro do estúdio:" -ForegroundColor White
Write-Host "   cd `"$destino`""
Write-Host "   claude        (ou codex)"
Write-Host "e cole o prompt 2 do README: siga o roteiro setup/2-segundo-cerebro.md até o fim."
