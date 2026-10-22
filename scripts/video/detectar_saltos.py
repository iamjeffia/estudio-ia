#!/usr/bin/env python3
"""Detector de saltos e de quadros vazios: rode depois de todo render, de preferência no master de alta taxa.

Lê o vídeo pelo ffmpeg em 192×108, cinza, e acusa:
  - salto:   a diferença média para o quadro anterior passa de 3× a mediana das 4 diferenças vizinhas
             (e de um mínimo absoluto, para o ruído de um vídeo parado não contar);
  - vazio:   quadro chapado, com desvio-padrão < 1,2 (preto, branco ou cor lisa onde devia ter imagem);
  - isolado: quadro diferente dos dois vizinhos, que por sua vez são parecidos entre si (falha de um quadro só).

Todo salto que sobrar tem de ser um corte de propósito. Trechos chapados de propósito (abertura em preto,
fade) podem ser liberados com --ignorar.

Uso:
    uv run scripts/video/detectar_saltos.py render.mp4
    uv run scripts/video/detectar_saltos.py render.mp4 --ignorar 0-0.5 --ignorar 29.5-30

Sai com código 1 se achar algum problema, 0 se o vídeo estiver limpo (dá para usar em script).
"""
import argparse
import json
import subprocess
import sys

import numpy as np

L, A = 192, 108


def sonda_fps(caminho):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate,r_frame_rate",
         "-of", "json", caminho],
        capture_output=True, text=True, encoding="utf-8",
    )
    if out.returncode != 0:
        sys.exit(f"erro: o ffprobe não conseguiu ler {caminho}\n{out.stderr.strip()}")
    streams = json.loads(out.stdout).get("streams", [])
    if not streams:
        sys.exit("erro: o arquivo não tem trilha de vídeo")
    for chave in ("avg_frame_rate", "r_frame_rate"):
        n, _, d = streams[0].get(chave, "0/0").partition("/")
        if float(d or 1) and float(n) / float(d or 1) > 0:
            return float(n) / float(d or 1)
    return 30.0


def quadros(caminho):
    """Gera os quadros, um por vez, como matrizes float32 A×L (não guarda o vídeo inteiro na memória)."""
    cmd = ["ffmpeg", "-v", "error", "-i", caminho, "-map", "0:v:0", "-vf", f"scale={L}:{A},format=gray",
           "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    tam = L * A
    try:
        while True:
            buf = proc.stdout.read(tam)
            if len(buf) < tam:
                break
            yield np.frombuffer(buf, np.uint8).reshape(A, L).astype(np.float32)
    finally:
        proc.stdout.close()
        proc.wait()


def analisa(caminho, minimo_salto=2.0, lim_vazio=1.2, lim_isolado=8.0):
    difs, desvios, isolados = [], [], []
    ant2 = ant1 = None
    n = 0
    for q in quadros(caminho):
        desvios.append(float(q.std()))
        if ant1 is not None:
            difs.append(float(np.abs(q - ant1).mean()))
        if ant2 is not None:
            # quadro do meio (ant1) diferente dos dois vizinhos, que são parecidos entre si
            d1, d2 = difs[-2], difs[-1]
            dn = float(np.abs(q - ant2).mean())
            if d1 > lim_isolado and d2 > lim_isolado and dn < min(d1, d2) / 4:
                isolados.append(n - 1)
        ant2, ant1 = ant1, q
        n += 1

    d = np.array(difs)
    saltos = []
    for i in range(len(d)):
        viz = [d[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < len(d)]
        if len(viz) < 2:
            continue
        med = float(np.median(viz))
        if d[i] > minimo_salto and d[i] > 3 * med:
            saltos.append((i + 1, float(d[i]), med))  # o salto aparece no quadro i+1
    vazios = [i for i, s in enumerate(desvios) if s < lim_vazio]
    return n, saltos, vazios, isolados, desvios


def agrupa(indices):
    """[3,4,5,9] → [(3,5),(9,9)]: quadros vazios seguidos viram um trecho só."""
    grupos = []
    for i in indices:
        if grupos and i == grupos[-1][1] + 1:
            grupos[-1][1] = i
        else:
            grupos.append([i, i])
    return grupos


def intervalo(v):
    try:
        a, b = v.split("-", 1)
        return float(a), float(b)
    except ValueError:
        raise argparse.ArgumentTypeError("use início-fim em segundos, ex.: 0-0.5")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", help="vídeo renderizado")
    p.add_argument("--ignorar", type=intervalo, action="append", default=[], metavar="INI-FIM",
                   help="trecho (em segundos) onde salto ou quadro chapado é de propósito; pode repetir")
    p.add_argument("--minimo", type=float, default=2.0,
                   help="diferença média mínima (0–255) para um salto contar (padrão: 2.0)")
    p.add_argument("--vazio", type=float, default=1.2, help="desvio-padrão abaixo do qual o quadro é chapado (padrão: 1.2)")
    a = p.parse_args()

    fps = sonda_fps(a.video)
    n, saltos, vazios, isolados, _ = analisa(a.video, a.minimo, a.vazio)
    if n == 0:
        sys.exit("erro: nenhum quadro lido (o ffmpeg está no PATH? o arquivo é um vídeo?)")

    livre = lambda i: not any(ini <= i / fps <= fim for ini, fim in a.ignorar)
    saltos = [s for s in saltos if livre(s[0])]
    vazios = [i for i in vazios if livre(i)]
    isolados = [i for i in isolados if livre(i)]

    print(f"{a.video}: {n} quadros a {fps:.3f} qps ({n / fps:.2f} s)")
    print(f"saltos: {len(saltos)}")
    for i, dif, med in saltos:
        print(f"  t={i / fps:.3f}s (quadro {i})  diferença {dif:.2f}  mediana dos vizinhos {med:.2f}")
    grupos = agrupa(vazios)
    print(f"quadros chapados: {len(vazios)}" + (f" em {len(grupos)} trecho(s)" if vazios else ""))
    for ini, fim in grupos:
        if ini == fim:
            print(f"  t={ini / fps:.3f}s (quadro {ini})")
        else:
            print(f"  t={ini / fps:.3f}–{fim / fps:.3f}s (quadros {ini}–{fim}, {fim - ini + 1} quadros)")
    print(f"quadros isolados: {len(isolados)}")
    for i in isolados:
        print(f"  t={i / fps:.3f}s (quadro {i})")

    if saltos or vazios or isolados:
        print("→ confira cada tempo acima: se não for corte de propósito, é defeito de render.")
        sys.exit(1)
    print("→ limpo: nenhum salto, quadro chapado ou isolado.")


if __name__ == "__main__":
    main()
