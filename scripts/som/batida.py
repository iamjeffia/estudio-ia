"""batida.py — mede a música e devolve a GRADE em que o vídeo vai ser montado: batidas, tempos fortes, BPM e o drop.

Corte na batida tem que pousar a ≤ 2 quadros dela; chute "no olho" erra por 3–6 quadros, e o BPM de site ou de
catálogo às vezes está errado (uma faixa "130,8 BPM" medida tinha 98). Por isso a medida é do beat_this
(`File2Beats(checkpoint_path="final0")`), a IA de batidas que devolve batidas e tempos fortes (downbeats).

Precisa do extra de IA de áudio: `uv sync --extra cpu` (ou `--extra gpu` com placa NVIDIA). O modelo (~80 MB)
baixa sozinho no primeiro uso.

Uso:
  uv run scripts/som/batida.py musica.mp3                       # BPM, compassos, drop provável
  uv run scripts/som/batida.py musica.mp3 --fps 30 --json grade.json
  uv run scripts/som/batida.py musica.mp3 --video render.mp4    # confere os cortes do render contra a grade
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

SR = 22050


def carrega(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def batidas_ia(path, device=None):
    try:
        import torch
        from beat_this.inference import File2Beats
    except ImportError:
        raise SystemExit("batida.py precisa da IA de áudio, que não está instalada.\n"
                         "Rode na raiz do estúdio:  uv sync --extra cpu   (ou  uv sync --extra gpu  com placa NVIDIA)\n"
                         "e tente de novo. A instalação baixa alguns GB (PyTorch) uma vez só.")
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    with tempfile.TemporaryDirectory() as tmp:      # decodifica com o ffmpeg: qualquer formato entra
        wav = Path(tmp) / "trilha.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "1", "-ar", "44100", str(wav)], check=True)
        f2b = File2Beats(checkpoint_path="final0", device=device, dbn=False)
        b, d = f2b(str(wav))
    return np.asarray(b, float), np.asarray(d, float), device


def cortes_video(video, limiar=0.18):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-filter:v",
                          f"select='gt(scene,{limiar})',metadata=print:file=-", "-f", "null", "-"],
                         capture_output=True, text=True).stdout
    ts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", out)]
    ag = []
    for t in ts:
        if not ag or t - ag[-1] > 0.25:
            ag.append(t)
    return ag


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Batidas, tempos fortes, BPM e drop de uma música (beat_this).")
    ap.add_argument("trilha")
    ap.add_argument("--fps", type=float, default=30.0, help="quadros por segundo do vídeo, para dar os quadros (padrão 30)")
    ap.add_argument("--json", help="grava a grade em JSON (padrão: <trilha>.batidas.json ao lado da música)")
    ap.add_argument("--video", help="render para conferir os cortes contra a grade")
    ap.add_argument("--device", choices=["cpu", "cuda", "mps"], help="força o processador (padrão: cuda se houver, senão cpu)")
    a = ap.parse_args()
    trilha = Path(a.trilha)
    if not trilha.exists():
        raise SystemExit(f"não achei {trilha}")

    batidas, fortes, device = batidas_ia(trilha, a.device)
    if len(batidas) < 4:
        raise SystemExit("o beat_this achou menos de 4 batidas: a faixa tem batida marcada?")
    y = carrega(trilha)
    dur = len(y) / SR
    ib = np.diff(batidas)
    bpm = float(60 / np.median(ib))
    tempos = int(round(np.median(np.diff(np.searchsorted(batidas, fortes))))) if len(fortes) > 2 else 4

    # drop provável: a maior subida de volume sustentada por um compasso, no tempo forte mais próximo
    compasso = 60 / bpm * tempos
    win = int(compasso * SR)
    rms = np.array([np.sqrt(np.mean(y[i:i + win] ** 2)) for i in range(0, max(1, len(y) - win), int(SR * 60 / bpm))])
    drop = None
    if len(rms) > tempos * 2:
        antes = np.concatenate([[rms[0]] * tempos, rms[:-tempos]])
        i = int(np.argmax(rms - antes))
        t_drop = i * 60 / bpm
        drop = float(min(fortes, key=lambda x: abs(x - t_drop))) if len(fortes) else t_drop

    q = lambda s: int(round(s * a.fps))
    print(f"\n  {trilha.name}  (beat_this final0, {device})")
    print(f"  duração {dur:.2f} s | {bpm:.2f} BPM | 1 tempo = {60 / bpm:.4f} s = {60 / bpm * a.fps:.2f} quadros a {a.fps:g} qps"
          f" | {tempos} tempos por compasso | {len(batidas)} batidas, {len(fortes)} tempos fortes")
    print(f"  primeira batida {batidas[0]:.3f} s | primeiro tempo forte {fortes[0] if len(fortes) else float('nan'):.3f} s")
    if drop is not None:
        print(f"  drop provável (maior subida de volume sustentada) ≈ {drop:.3f} s (quadro {q(drop)})")
    print("\n  compasso  tempo forte (s)  quadro")
    for i, t1 in enumerate(fortes[:64]):
        print(f"  {i + 1:>8}  {t1:15.3f}  {q(t1):>6}")
    if len(fortes) > 64:
        print(f"  … mais {len(fortes) - 64} compassos no JSON")

    out = {"trilha": str(trilha), "duracao": dur, "bpm": bpm, "tempo_s": 60 / bpm, "tempos_por_compasso": tempos,
           "fps": a.fps, "batidas": batidas.tolist(), "tempos_fortes": fortes.tolist(),
           "batidas_quadro": [q(x) for x in batidas], "tempos_fortes_quadro": [q(x) for x in fortes], "drop": drop,
           "modelo": "beat_this final0"}
    if a.video:
        cs = cortes_video(a.video)
        tol = 2.0 / a.fps
        perto = [float(np.min(np.abs(batidas - c))) for c in cs]
        ok = sum(1 for d in perto if d <= tol + 1e-6)
        print(f"\n  CORTES DO RENDER: {len(cs)} | a ≤ 2 quadros de uma batida: {ok} ({(ok / len(cs) * 100 if cs else 0):.0f}%)")
        for c, d in zip(cs, perto):
            print(f"    {c:7.3f} s (quadro {q(c)}) → {d * 1000:5.0f} ms  {'ok' if d <= tol + 1e-6 else 'FORA'}")
        out["cortes_video"] = cs
        out["cortes_alinhados"] = ok
    js = Path(a.json) if a.json else trilha.with_suffix(".batidas.json")
    js.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  grade → {js}")


if __name__ == "__main__":
    main()
