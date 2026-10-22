"""Caminhos do estúdio, para todo script achar as pastas sem caminho fixo.

Uso nos scripts:
    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from _estudio import RAIZ, BIBLIOTECA, SFX, MUSICA, REFERENCIAS, midia_referencias
"""
from __future__ import annotations

import os
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BIBLIOTECA = RAIZ / "05-biblioteca"
SOM = BIBLIOTECA / "som"
SFX = Path(os.environ.get("ESTUDIO_SFX", SOM / "sfx"))
MUSICA = Path(os.environ.get("ESTUDIO_MUSICA", BIBLIOTECA / "musica"))
FONTES = BIBLIOTECA / "fontes"
REFERENCIAS = RAIZ / "03-referencias"
PROJETOS = RAIZ / "04-projetos"


def midia_referencias() -> Path:
    """Pasta onde fica a mídia das referências: lê o '- **Caminho da mídia:**' do ONDE.md."""
    onde = REFERENCIAS / "ONDE.md"
    if onde.exists():
        m = re.search(r"\*\*Caminho da mídia:\*\*\s*(.+)", onde.read_text(encoding="utf-8"))
        if m:
            caminho = Path(m.group(1).strip().strip("`"))
            return caminho if caminho.is_absolute() else RAIZ / caminho
    return REFERENCIAS
