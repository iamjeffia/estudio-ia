#!/usr/bin/env bash
# Instalador do estúdio no Mac. Pode rodar de novo quantas vezes quiser:
# o que já está instalado é pulado.
#   bash setup/instalar-mac.sh                    (completo)
#   bash setup/instalar-mac.sh --leve             (sem a IA de áudio)
#   bash setup/instalar-mac.sh --sem-effectcraft  pula o EffectCraft
#   bash setup/instalar-mac.sh --sem-ias          não instala o Claude Code nem o Codex
set -u

LEVE=0; SEM_EC=0; SEM_IAS=0
for a in "$@"; do
  case "$a" in
    --leve) LEVE=1 ;;
    --sem-effectcraft) SEM_EC=1 ;;
    --sem-ias) SEM_IAS=1 ;;
  esac
done

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
INICIO=$(date +%s)
RESUMO=""
PASSO=""; PASSO_T=0

fechar() { if [ -n "$PASSO" ]; then RESUMO="$RESUMO$(printf '%-38s %5s s' "$PASSO" "$(( $(date +%s) - PASSO_T ))")\n"; fi; }
passo() { fechar; PASSO="$1"; PASSO_T=$(date +%s); printf '\n\033[36m== %s\033[0m\n' "$1"; }
ok() { printf '   \033[32mok\033[0m  %s\n' "$1"; }
aviso() { printf '   \033[33m!!\033[0m  %s\n' "$1"; }
tem() { command -v "$1" >/dev/null 2>&1; }

echo "Estúdio de IA: setup do Mac"
echo "Pasta: $RAIZ"

# Homebrew no PATH (Apple Silicon e Intel)
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
[ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
export PATH="$HOME/.local/bin:$PATH"

# 1. Programas base -----------------------------------------------------------
passo "1. Programas base"
if ! xcode-select -p >/dev/null 2>&1; then
  aviso "instalando as ferramentas de linha de comando da Apple (vai abrir uma janela: clique em Instalar e rode este script de novo depois)"
  xcode-select --install
fi
if ! tem brew; then
  echo "   ... instalando Homebrew (vai pedir a senha do Mac)"
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
fi
if tem brew; then
  for par in git:git node:node ffmpeg:ffmpeg uv:uv; do
    pacote="${par%%:*}"; comando="${par##*:}"
    if tem "$comando"; then ok "$pacote já instalado"
    else echo "   ... instalando $pacote"; brew install "$pacote" >/dev/null && ok "$pacote instalado" || aviso "$pacote falhou"; fi
  done
else
  aviso "Homebrew não instalou; instale em https://brew.sh e rode de novo"
fi

# 2. As IAs -------------------------------------------------------------------
passo "2. Claude Code e Codex"
if [ "$SEM_IAS" = 1 ]; then ok "pulado (--sem-ias)"
else
  if tem claude; then ok "Claude Code já instalado"
  else echo "   ... instalando Claude Code"; curl -fsSL https://claude.ai/install.sh | bash >/dev/null; export PATH="$HOME/.local/bin:$PATH"
       tem claude && ok "Claude Code instalado" || aviso "Claude Code não respondeu (abra um terminal novo)"; fi
  if tem codex; then ok "Codex já instalado"
  elif tem npm; then echo "   ... instalando Codex"; npm install -g @openai/codex --silent >/dev/null 2>&1
       tem codex && ok "Codex instalado" || aviso "Codex não respondeu"
  else aviso "npm não encontrado; o Codex fica para a próxima rodada"; fi
fi

# 3. Bibliotecas Python -------------------------------------------------------
passo "3. Bibliotecas Python"
if tem uv; then
  if [ "$LEVE" = 1 ]; then ok "modo leve: só a base"; uv sync
  else ok "IA de áudio com o chip do Mac (~1,5 GB)"; uv sync --extra cpu; fi
  [ $? -eq 0 ] && ok "bibliotecas instaladas em .venv" || aviso "uv sync falhou"
  echo "   ... navegador para render de HTML (Playwright)"
  uv run playwright install chromium >/dev/null 2>&1 && ok "Chromium do Playwright pronto" || aviso "playwright install falhou"
else
  aviso "uv não encontrado; pulei as bibliotecas"
fi

# 4. Skills ------------------------------------------------------------------
passo "4. Skills"
mkdir -p .claude
[ -e .claude/skills ] || ln -s ../.agents/skills .claude/skills
[ -e .claude/skills ] && ok "skills do estúdio ligadas ao Claude Code (.claude/skills -> .agents/skills)"
if tem npx; then
  # pacote:skill-dele; se a skill já existe, o pacote é pulado (não sobrescreve skill editada)
  for par in heygen-com/hyperframes:hyperframes remotion-dev/skills:remotion-best-practices \
             Jakubantalik/transitions.dev:transitions-dev bradautomates/claude-video:watch blader/humanizer:humanizer; do
    p="${par%%:*}"; marca="${par##*:}"
    if [ -e "$HOME/.claude/skills/$marca" ] || [ -e "$HOME/.agents/skills/$marca" ]; then ok "$p já instalado"; continue; fi
    echo "   ... $p"
    npx -y skills add "$p" -g -y -s '*' -a claude-code codex >/dev/null 2>&1 && ok "$p" || aviso "$p falhou"
  done
else
  aviso "npx não encontrado; skills externas ficam para a próxima rodada"
fi

# 5. Sons iniciais -----------------------------------------------------------
passo "5. Biblioteca de sons inicial"
if tem uv && [ -f scripts/som/sintetizar_sfx.py ]; then
  uv run scripts/som/sintetizar_sfx.py && ok "efeitos sonoros gerados em 05-biblioteca/som/sfx" || aviso "sintetizar_sfx.py falhou"
else aviso "pulei os sons (falta o uv ou o script)"; fi

# 6. EffectCraft -------------------------------------------------------------
passo "6. EffectCraft"
EC_DIR="$HOME/Applications/EffectCraft"
EC_CLI="$(ls "$EC_DIR"/effectcraft-cli 2>/dev/null || find "$EC_DIR" -name effectcraft-cli -type f 2>/dev/null | head -1)"
if [ "$SEM_EC" = 1 ]; then ok "pulado (--sem-effectcraft)"
else
  if [ -n "$EC_CLI" ]; then ok "EffectCraft já instalado"
  else
    echo "   ... baixando a última versão (GitHub storytold/effectcraft)"
    # o link de "última versão" redireciona para a tag (sem o limite de consultas da API do GitHub)
    TAG="$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/storytold/effectcraft/releases/latest | sed 's#.*/##')"
    VER="${TAG#v}"; BASE="https://github.com/storytold/effectcraft/releases/download/$TAG"
    URL_CLI=""; URL_APP=""
    if [ -n "$VER" ]; then URL_CLI="$BASE/effectcraft-cli-$VER-macos-universal.zip"; URL_APP="$BASE/effectcraft-$VER-macos-universal.dmg"; fi
    mkdir -p "$EC_DIR"
    if [ -n "$URL_CLI" ]; then
      curl -fsSL "$URL_CLI" -o /tmp/effectcraft-cli.zip && unzip -oq /tmp/effectcraft-cli.zip -d "$EC_DIR" && rm -f /tmp/effectcraft-cli.zip
      xattr -dr com.apple.quarantine "$EC_DIR" 2>/dev/null
    fi
    if [ -n "$URL_APP" ]; then
      curl -fsSL "$URL_APP" -o /tmp/effectcraft.dmg && MNT="$(hdiutil attach -nobrowse /tmp/effectcraft.dmg | tail -1 | awk -F'\t' '{print $NF}')" \
        && cp -R "$MNT"/*.app "$HOME/Applications/" 2>/dev/null; hdiutil detach "$MNT" -quiet 2>/dev/null; rm -f /tmp/effectcraft.dmg
    fi
    EC_CLI="$(find "$EC_DIR" -name effectcraft-cli -type f 2>/dev/null | head -1)"
    [ -n "$EC_CLI" ] && chmod +x "$EC_CLI" && ok "EffectCraft em $EC_DIR" || aviso "não consegui instalar o EffectCraft"
  fi
  if [ -n "$EC_CLI" ]; then
    if tem claude; then claude mcp get effectcraft >/dev/null 2>&1 || claude mcp add effectcraft -s user -- "$EC_CLI" mcp >/dev/null 2>&1; ok "EffectCraft ligado ao Claude Code"; fi
    if tem codex; then codex mcp get effectcraft >/dev/null 2>&1 || codex mcp add effectcraft -- "$EC_CLI" mcp >/dev/null 2>&1; ok "EffectCraft ligado ao Codex"; fi
  fi
fi

# 7. After Effects -----------------------------------------------------------
passo "7. After Effects"
AE="$(ls -d /Applications/Adobe\ After\ Effects* 2>/dev/null | sort -r | head -1)"
if [ -n "$AE" ]; then
  ok "After Effects encontrado: $(basename "$AE")"
  if [ -d "$HOME/Library/Application Support/MotionKitAE" ]; then ok "Motion Kit AE já instalado"
  else aviso "falta o Motion Kit AE (ponte da IA com o After Effects): pegue o comando em https://clubedomotion.com/kit-ae"; fi
else
  aviso "After Effects não encontrado. Ele é opcional: o EffectCraft, o HyperFrames e o Remotion funcionam sem ele"
fi

# 8. Conferência -------------------------------------------------------------
passo "8. Conferência"
tem uv && uv run setup/conferir.py || aviso "sem uv, não deu para conferir"
fechar; PASSO=""

echo
echo "Tempo de cada etapa:"
printf "$RESUMO" | sed 's/^/   /'
T=$(( $(date +%s) - INICIO ))
printf 'Total: %02d:%02d\n' $((T/60)) $((T%60))
echo "Inventário salvo em 02-ferramentas/inventario.md"
