#!/usr/bin/env bash
# Um comando para começar do zero no Mac (Terminal):
#   curl -fsSL https://raw.githubusercontent.com/oldmoneygit/estudio-ia/main/setup/comecar.sh | bash
# Baixa o estúdio em ~/estudio-ia e roda o instalador completo.
set -u
DESTINO="$HOME/estudio-ia"

if ! command -v git >/dev/null 2>&1; then
  echo "O Mac vai pedir para instalar as ferramentas de linha de comando (Git incluso)."
  echo "Clique em Instalar, espere terminar e rode este comando de novo."
  xcode-select --install
  exit 0
fi
if [ -d "$DESTINO/.git" ]; then
  echo "O estúdio já existe em $DESTINO; atualizando"
  git -C "$DESTINO" pull --ff-only
else
  git clone https://github.com/oldmoneygit/estudio-ia "$DESTINO" || { echo "Não consegui baixar o estúdio. Confira a internet e rode de novo."; exit 1; }
fi
bash "$DESTINO/setup/instalar-mac.sh" </dev/tty
echo
echo "Pronto. Agora abra a IA dentro do estúdio:"
echo "   cd ~/estudio-ia && claude        (ou codex)"
echo "e cole o prompt 2 do README: siga o roteiro setup/2-segundo-cerebro.md até o fim."
