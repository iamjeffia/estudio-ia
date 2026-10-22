"""Confere o que está instalado no estúdio e grava 02-ferramentas/inventario.md.

    uv run setup/conferir.py            (relatório)
    uv run setup/conferir.py --estrito  (sai com erro se faltar algo essencial; usado no teste automático)

Não instala nada: só olha. Rode depois do instalador, ou quando algo parar de funcionar.
"""
from __future__ import annotations

import datetime as dt
import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
HOME = Path.home()
WINDOWS = os.name == "nt"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def rodar(*cmd: str, timeout: int = 30) -> tuple[int, str]:
    exe = shutil.which(cmd[0])
    if not exe:
        return 127, ""
    try:
        p = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or p.stderr).strip()
    except Exception as e:  # noqa: BLE001 — conferência nunca quebra
        return 1, str(e)


def versao(*cmd: str) -> str | None:
    cod, saida = rodar(*cmd)
    if cod != 0 or not saida:
        return None
    return saida.splitlines()[0][:60]


linhas: list[tuple[str, str, bool, str, bool]] = []  # grupo, nome, ok, detalhe, essencial


def item(grupo: str, nome: str, ok: bool, detalhe: str = "", essencial: bool = False) -> None:
    linhas.append((grupo, nome, ok, detalhe, essencial))


# Programas ------------------------------------------------------------------
for nome, cmd, essencial in [
    ("Git", ("git", "--version"), True),
    ("Node.js", ("node", "--version"), True),
    ("npm", ("npm", "--version"), True),
    ("FFmpeg", ("ffmpeg", "-version"), True),
    ("FFprobe", ("ffprobe", "-version"), True),
    ("uv", ("uv", "--version"), True),
    ("Claude Code", ("claude", "--version"), False),
    ("Codex", ("codex", "--version"), False),
    ("ai-memory", ("ai-memory", "--version"), False),
]:
    v = versao(*cmd)
    item("Programas", nome, v is not None, v or "não encontrado", essencial)

if not (shutil.which("claude") or shutil.which("codex")):
    item("Programas", "Uma IA (Claude Code ou Codex)", False, "instale pelo menos uma", True)

# Bibliotecas Python -----------------------------------------------------------
for mod, nome, essencial in [
    ("numpy", "numpy", True), ("scipy", "scipy", True), ("soundfile", "soundfile", True),
    ("librosa", "librosa", True), ("pyloudnorm", "pyloudnorm", True), ("pedalboard", "pedalboard", False),
    ("faster_whisper", "faster-whisper", True), ("cv2", "opencv", True), ("PIL", "Pillow", True),
    ("playwright", "playwright", False), ("yt_dlp", "yt-dlp", True),
    ("torch", "torch (IA de áudio)", False), ("beat_this", "beat_this (batidas)", False),
    ("audio_separator", "audio-separator (voz e instrumental)", False),
]:
    try:
        m = importlib.import_module(mod)
        det = getattr(m, "__version__", "") or "ok"
        if mod == "torch":
            det += " · CUDA" if m.cuda.is_available() else (
                " · chip Apple (MPS)" if getattr(m.backends, "mps", None) and m.backends.mps.is_available() else " · processador")
        item("Python", nome, True, str(det)[:60], essencial)
    except Exception:  # noqa: BLE001
        dica = "uv sync --extra cpu (ou gpu)" if mod in ("torch", "beat_this", "audio_separator") else "uv sync"
        item("Python", nome, False, f"falta: {dica}", essencial)

chromium = list((HOME / ("AppData/Local/ms-playwright" if WINDOWS else (
    "Library/Caches/ms-playwright" if sys.platform == "darwin" else ".cache/ms-playwright"))).glob("chromium*"))
item("Python", "Chromium do Playwright", bool(chromium), "ok" if chromium else "uv run playwright install chromium")

# Skills -----------------------------------------------------------------------
locais = sorted(s.parent.name for s in (RAIZ / ".agents" / "skills").glob("*/SKILL.md"))
item("Skills", "Skills do estúdio", bool(locais), ", ".join(locais) or "nenhuma em .agents/skills", True)
item("Skills", "Ligação .claude/skills", (RAIZ / ".claude" / "skills").exists(),
     "ok" if (RAIZ / ".claude" / "skills").exists() else "rode o instalador de novo")
pastas_globais = [HOME / ".claude" / "skills", HOME / ".agents" / "skills"]
for nome, alvo in [("HyperFrames", "hyperframes"), ("Remotion", "remotion-best-practices"),
                   ("Transições", "transitions-dev"), ("watch (assistir vídeo)", "watch"),
                   ("humanizer", "humanizer")]:
    achou = any((p / alvo).exists() for p in pastas_globais)
    item("Skills", nome, achou, "ok" if achou else "npx skills add ... (veja setup/2-instalar.md)")

# Motores de vídeo -------------------------------------------------------------
cod, saida = rodar("claude", "mcp", "list", timeout=60) if shutil.which("claude") else (1, "")
mcps = saida.lower()
if WINDOWS:
    ec = [p for base in (Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "EffectCraft",
                         Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "EffectCraft")
          for p in base.rglob("effectcraft-cli.exe")] if os.environ.get("LOCALAPPDATA") else []
    ae = sorted(Path(os.environ.get("ProgramFiles", "C:/Program Files"), "Adobe").glob("Adobe After Effects*/Support Files/AfterFX.exe"))
    kit = Path(os.environ.get("LOCALAPPDATA", "")) / "MotionKitAE"
else:
    ec = list((HOME / "Applications" / "EffectCraft").rglob("effectcraft-cli"))
    ae = sorted(Path("/Applications").glob("Adobe After Effects*"))
    kit = HOME / "Library" / "Application Support" / "MotionKitAE"
item("Motores", "EffectCraft", bool(ec), str(ec[0].parent) if ec else "rode o instalador (passo 6)")
item("Motores", "EffectCraft no Claude Code", "effectcraft" in mcps, "MCP effectcraft" if "effectcraft" in mcps else "não registrado")
item("Motores", "After Effects", bool(ae), ae[-1].parts[-3] if ae and WINDOWS else (ae[-1].name if ae else "opcional"))
item("Motores", "Motion Kit AE", kit.exists(), "ok" if kit.exists() else "opcional: clubedomotion.com/kit-ae")
item("Motores", "HyperFrames e Remotion", bool(shutil.which("npx")), "rodam por npx dentro de cada projeto")

# Segundo cérebro --------------------------------------------------------------
perfil = RAIZ / "01-sobre-mim" / "perfil.md"
perfil_ok = perfil.exists() and "PERFIL-EM-BRANCO" not in perfil.read_text(encoding="utf-8")
item("Cérebro", "Perfil preenchido", perfil_ok, "ok" if perfil_ok else "roteiro 1 (setup/1-segundo-cerebro.md)")
marcador = RAIZ / ".ai-memory.toml"
item("Cérebro", "Projeto no ai-memory", marcador.exists(), "ok" if marcador.exists() else "roteiro 1")
onde = (RAIZ / "03-referencias" / "ONDE.md").read_text(encoding="utf-8") if (RAIZ / "03-referencias" / "ONDE.md").exists() else ""
item("Cérebro", "Pasta de referências", "AAAA-MM-DD" not in onde, "ok" if "AAAA-MM-DD" not in onde else "roteiro 3 (setup/3-referencias.md)")
sfx = list((RAIZ / "05-biblioteca" / "som" / "sfx").rglob("*.wav"))
item("Cérebro", "Efeitos sonoros", bool(sfx), f"{len(sfx)} arquivos" if sfx else "uv run scripts/som/sintetizar_sfx.py")

# Saída -------------------------------------------------------------------------
faltam_essenciais = [n for _, n, ok, _, e in linhas if e and not ok]
agora = dt.datetime.now()
md = [
    "# Inventário do estúdio",
    "",
    f"> Data: {agora:%Y-%m-%d} · Tipo: dados · Status: vigente",
    "",
    f"**Como usar:** gerado por `uv run setup/conferir.py` em {agora:%d/%m/%Y %H:%M} "
    f"({platform.system()} {platform.release()}, {platform.machine()}). Não edite à mão: rode o script de novo.",
    "",
    "| Grupo | Item | Pronto | Detalhe |",
    "|---|---|---|---|",
]
grupo_anterior = None
print()
for grupo, nome, ok, det, essencial in linhas:
    if grupo != grupo_anterior:
        print(f"\n{grupo}")
        grupo_anterior = grupo
    marca = "ok" if ok else ("FALTA" if essencial else "--")
    print(f"  {marca:>5}  {nome:<38} {det}")
    md.append(f"| {grupo} | {nome} | {'sim' if ok else ('**falta**' if essencial else 'não')} | {det.replace('|', '/')} |")

md += ["", "## Resultado", "",
       "Tudo o que é essencial está pronto." if not faltam_essenciais
       else "Falta o essencial: " + ", ".join(faltam_essenciais) + "."]
(RAIZ / "02-ferramentas").mkdir(exist_ok=True)
(RAIZ / "02-ferramentas" / "inventario.md").write_text("\n".join(md) + "\n", encoding="utf-8")

print()
if faltam_essenciais:
    print("Falta o essencial: " + ", ".join(faltam_essenciais))
    if "--estrito" in sys.argv:
        sys.exit(1)
else:
    print("Essencial pronto. Itens marcados com -- são opcionais.")
