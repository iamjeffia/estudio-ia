"""Verifica o volume do som de cena (ambiência + foley + efeitos criativos) ANTES de qualquer entrega.
Sound design não pode ficar alto: mede o mix (ou o stem de som de cena) e reprova se passar dos tetos de
06-metodo/regras.md ("Som de cena").

Uso:  uv run scripts/som/verificar_som_de_cena.py mix.wav [--voz voz.wav]
  sem --voz: peça só com som de cena (sem voz nem música) ou o stem do som de cena isolado
             (ex.: escuta/efeitos.wav que o som.py grava).
  --voz:     compara o stem do som de cena com o stem da voz (relação em LU), ex.: --voz escuta/voz.wav.
Sai com código 0 se aprovado e 1 se reprovado (dá para usar em script).
"""
import sys, argparse, numpy as np, soundfile as sf, pyloudnorm as pyln

TETO_INTEGRADO = -24.0      # peça só de som de cena: nunca normalizar a −14
TETO_CURTO = -20.0          # loudness de curto prazo (3 s), máximo
TETO_MOMENTANEO = -16.0     # loudness momentâneo (0,4 s), máximo: o impacto mais forte
TETO_PICO = -3.0            # dBFS (pico de amostra)
ABAIXO_DA_VOZ = 15.0        # com voz: curto prazo do som de cena ≥ 15 LU abaixo da voz (mesmo da música)


def curvas(x, sr, w, passo):
    """Loudness K-ponderado em janelas de w s (3 s = curto prazo, 0,4 s = momentâneo), sem gate."""
    m = pyln.Meter(sr, block_size=w)
    n, h = int(w * sr), int(passo * sr)
    out = []
    for i in range(0, max(1, len(x) - n + 1), h):
        try:
            out.append(m.integrated_loudness(x[i:i + n + 1]))
        except ValueError:
            out.append(-np.inf)
    return np.array(out, float)


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Reprova som de cena alto demais (tetos de 06-metodo/regras.md).")
    ap.add_argument("audio", help="mix só de som de cena, ou o stem do som de cena")
    ap.add_argument("--voz", help="stem da voz, para medir a distância em LU")
    a = ap.parse_args()
    x, sr = sf.read(a.audio)
    if x.ndim == 1: x = np.vstack([x, x]).T
    L = pyln.Meter(sr).integrated_loudness(x)
    st = curvas(x, sr, 3.0, 0.5); mo_all = curvas(x, sr, 0.4, 0.1)
    imo = int(np.argmax(mo_all))
    st, mo = st[np.isfinite(st)], mo_all[np.isfinite(mo_all)]
    pico = 20 * np.log10(np.abs(x).max() + 1e-12)
    linhas, ok = [], True

    def chk(nome, v, teto):
        nonlocal ok
        passa = v <= teto + 0.3; ok &= passa  # tolerância de medição
        linhas.append(f"{'OK  ' if passa else 'ALTO'}  {nome}: {v:6.1f}  (teto {teto})")

    if a.voz:
        v, sv_sr = sf.read(a.voz)
        if sv_sr != sr:
            raise SystemExit(f"a voz está a {sv_sr} Hz e o som de cena a {sr} Hz: use os stems da mesma mix")
        if v.ndim == 1: v = np.vstack([v, v]).T
        sv = curvas(v, sr, 3.0, 0.5); sx = curvas(x, sr, 3.0, 0.5)
        n = min(len(sv), len(sx)); sx, sv = sx[:n], sv[:n]
        fala = np.isfinite(sv) & (sv > np.nanpercentile(sv[np.isfinite(sv)], 40))
        rel = np.median(sv[fala] - sx[fala])
        linhas.append(f"{'OK  ' if rel >= ABAIXO_DA_VOZ else 'ALTO'}  som de cena abaixo da voz (mediana, com fala): {rel:5.1f} LU (mínimo {ABAIXO_DA_VOZ})")
        ok &= rel >= ABAIXO_DA_VOZ
    else:
        chk("integrado LUFS", L, TETO_INTEGRADO)
        chk("curto prazo máx LUFS", st.max(), TETO_CURTO)
        chk("momentâneo máx LUFS", mo.max(), TETO_MOMENTANEO)
        chk("pico dBFS", pico, TETO_PICO)
    print(f"{a.audio}\n  momentâneo mais alto em {imo * 0.1:.1f} s")
    print("\n".join("  " + l for l in linhas))
    print("  RESULTADO:", "APROVADO" if ok else "REPROVADO: baixar o som de cena antes de entregar")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
