"""separar.py — separa uma música em voz e instrumental, ou em 6 stems, com o audio-separator.

Modelos escolhidos em teste (MUSDB18 e ouvido cego):
- voz/instrumental: MelBand RoFormer Big Beta 4 (`melband_roformer_big_beta4.ckpt`): a voz do cantor mais limpa
  para intro de remix e voz por cima dos tonais;
- 6 stems: BS-RoFormer SW (`BS-Roformer-SW.ckpt`): vocals, drums, bass, guitar, piano, other. Ganhou do htdemucs em
  voz (11,5 × 8,8 dB de SDR), "other" e bateria. Também grava `other4.wav` (other + guitar + piano, o papel do "other"
  de 4 stems) e `instrumental.wav` (tudo menos a voz).

Precisa do extra de IA de áudio: `uv sync --extra cpu` (ou `--extra gpu` com placa NVIDIA, bem mais rápido).
Os modelos (~300–700 MB cada) baixam sozinhos no primeiro uso, para a pasta de cache do usuário
(~/.cache/estudio-ia/audio-separator), fora do repositório.

Uso:
  uv run scripts/som/separar.py musica.mp3                 # voz.wav + instrumental.wav em musica-stems/
  uv run scripts/som/separar.py musica.mp3 --modo 6        # 6 stems + other4.wav + instrumental.wav
  uv run scripts/som/separar.py a.mp3 b.mp3 --saida pasta  # várias músicas; saída em pasta/<nome>-stems/
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

MODELOS = Path.home() / ".cache" / "estudio-ia" / "audio-separator"
MODELO = {"voz": "melband_roformer_big_beta4.ckpt", "6": "BS-Roformer-SW.ckpt"}
SEIS = ("vocals", "drums", "bass", "guitar", "piano", "other")


def _separador(saida_tmp):
    try:
        from audio_separator.separator import Separator
    except ImportError:
        raise SystemExit("separar.py precisa da IA de áudio, que não está instalada.\n"
                         "Rode na raiz do estúdio:  uv sync --extra cpu   (ou  uv sync --extra gpu  com placa NVIDIA)\n"
                         "e tente de novo. A instalação baixa alguns GB (PyTorch) uma vez só.")
    MODELOS.mkdir(parents=True, exist_ok=True)
    return Separator(output_dir=str(saida_tmp), model_file_dir=str(MODELOS), output_format="WAV")


def _acha(tmp, nome):
    """Arquivo do stem `nome` na saída do audio-separator (<música>_(Vocals)_<modelo>.wav; maiúsculas variam)."""
    for f in Path(tmp).glob("*.wav"):
        if f"({nome.lower()})" in f.name.lower():
            return f
    return None


def _soma(entradas, saida):
    entradas = [e for e in entradas if e.exists()]
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for e in entradas:
        cmd += ["-i", str(e)]
    cmd += ["-filter_complex", f"amix=inputs={len(entradas)}:normalize=0", str(saida)]
    subprocess.run(cmd, check=True)


def separa(musica, modo="voz", saida=None):
    musica = Path(musica).resolve()
    pasta = (Path(saida).resolve() if saida else musica.parent) / f"{musica.stem}-stems"
    pronto = pasta / ("instrumental.wav" if modo == "voz" else "other4.wav")
    if pronto.exists():
        print(f"{musica.name}: já separada em {pasta} (apague a pasta para refazer)")
        return pasta
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    try:
        sep = _separador(tmp)
        print(f"{musica.name}: carregando {MODELO[modo]} (no primeiro uso o modelo é baixado; demora)…", flush=True)
        sep.load_model(model_filename=MODELO[modo])
        erro = None
        for _ in range(3):   # falta de memória é intermitente quando outro programa pesado está aberto
            try:
                sep.separate(str(musica)); erro = None; break
            except Exception as ex:  # noqa: BLE001
                erro = ex
        if erro:
            raise SystemExit(f"o audio-separator falhou 3 vezes: {erro}")
        if modo == "voz":
            voz = _acha(tmp, "vocals")
            inst = _acha(tmp, "instrumental") or _acha(tmp, "other")
            if not voz or not inst:
                raise SystemExit(f"saída inesperada do separador: {[f.name for f in tmp.glob('*.wav')]}")
            shutil.move(str(voz), pasta / "voz.wav"); shutil.move(str(inst), pasta / "instrumental.wav")
        else:
            for s in SEIS:
                f = _acha(tmp, s)
                if not f:
                    raise SystemExit(f"faltou o stem {s}: {[f.name for f in tmp.glob('*.wav')]}")
                shutil.move(str(f), pasta / f"{s}.wav")
            _soma([pasta / "other.wav", pasta / "guitar.wav", pasta / "piano.wav"], pasta / "other4.wav")
            _soma([pasta / f"{s}.wav" for s in SEIS if s != "vocals"], pasta / "instrumental.wav")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{musica.name} → {pasta}")
    return pasta


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Separa música em voz/instrumental (MelBand Big Beta 4) ou 6 stems (BS-RoFormer SW).")
    ap.add_argument("musicas", nargs="+")
    ap.add_argument("--modo", choices=["voz", "6"], default="voz", help="voz = voz + instrumental (padrão); 6 = seis stems")
    ap.add_argument("--saida", help="pasta onde criar <nome>-stems/ (padrão: ao lado da música)")
    a = ap.parse_args()
    for m in a.musicas:
        if not Path(m).exists():
            raise SystemExit(f"não achei {m}")
        separa(m, a.modo, a.saida)


if __name__ == "__main__":
    main()
