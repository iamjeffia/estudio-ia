"""Olho quadro a quadro: ver nos vídeos os detalhes que a folha de contato comum e a análise por IA perdem.

Nasceu da recriação de um tutorial em que a referência parecia "perfeita" e não era: a câmera derivava e
tremia de leve, e o texto tinha acabamento próprio. O imperfeito humaniza, e só se vê medindo.

Comandos (todos aceitam --ini/--fim em segundos e --recorte x,y,l,a em pixels do vídeo):

  camera   curva do movimento global (x, y, rotação, escala por quadro) por fluxo óptico (Lucas-Kanade + afim
           parcial), separa trajetória (Savitzky-Golay ~0,5 s) e tremida (resíduo), mede amplitude/frequência
           da tremida e a duração dos "chicotes". Saída: CSV + PNG com o gráfico. Use --rotulo para nomear.
  folha    quadros SEGUIDOS na taxa nativa, numerados, em grade (não pula nenhum quadro).
  rastro   onion skin (média de N quadros) e diferença entre quadros (só o que mudou), em PNG.
  compara  duas curvas de câmera no mesmo gráfico (ex.: original × recriação), com resumo numérico.
  ampliar  recorte ampliado de um quadro (vizinho mais próximo, sem suavizar) + versão com contraste esticado,
           para revelar degradê, brilho e contorno.

Exemplos:
  uv run scripts/video/olho_quadro_a_quadro.py camera ref.mp4 --ini 19.6 --fim 26.6 --recorte 20,20,400,680 --saida ref_cam
  uv run scripts/video/olho_quadro_a_quadro.py compara ref_cam.csv rec_cam.csv --saida comp_cam
  uv run scripts/video/olho_quadro_a_quadro.py folha ref.mp4 --ini 24.0 --fim 25.2 --saida ref_folha.jpg
  uv run scripts/video/olho_quadro_a_quadro.py ampliar ref.mp4 --ini 3.2 --recorte 600,300,200,120 --zoom 6 --saida brilho.png
"""
import argparse, csv, os, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _estudio import FONTES  # noqa: E402

try:
    from scipy.signal import savgol_filter
except ImportError:  # média móvel se o SciPy faltar
    savgol_filter = None


def acha_fonte():
    """Fonte sem serifa do sistema (Windows, macOS, Linux); senão a primeira de 05-biblioteca/fontes."""
    nomes = ("segoeui.ttf", "arial.ttf", "Arial.ttf", "SFNS.ttf", "Helvetica.ttc", "DejaVuSans.ttf")
    pastas = (Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts", Path("/System/Library/Fonts"),
              Path("/System/Library/Fonts/Supplemental"), Path("/Library/Fonts"), Path.home() / "Library/Fonts",
              Path("/usr/share/fonts/truetype/dejavu"))
    for pasta in pastas:
        for n in nomes:
            if (pasta / n).exists():
                return str(pasta / n)
    if FONTES.exists():
        for f in sorted(FONTES.rglob("*")):
            if f.suffix.lower() in (".ttf", ".otf", ".ttc"):
                return str(f)
    return None


FONTE = acha_fonte()


def fonte(t):
    if FONTE:
        try:
            return ImageFont.truetype(FONTE, t)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=t)  # Pillow ≥ 10.1
    except TypeError:
        return ImageFont.load_default()


def ler_quadros(caminho, ini=0.0, fim=None, recorte=None, largura=None):
    if not os.path.exists(caminho):
        sys.exit(f"erro: não achei o vídeo {caminho}")
    cap = cv2.VideoCapture(caminho)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
    quadros, tempos = [], []
    while True:
        t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        ok, q = cap.read()
        if not ok or (fim is not None and t > fim):
            break
        if recorte:
            x, y, l, a = recorte
            q = q[y:y + a, x:x + l]
        if largura and q.shape[1] != largura:
            q = cv2.resize(q, (largura, int(q.shape[0] * largura / q.shape[1])), interpolation=cv2.INTER_AREA)
        quadros.append(q)
        tempos.append(t)
    cap.release()
    if not quadros:
        sys.exit("erro: nenhum quadro lido; confira --ini/--fim e se o arquivo é um vídeo")
    return quadros, tempos, fps


def suaviza(x, fps, janela_s=0.5):
    w = max(5, int(fps * janela_s) | 1)
    if len(x) < w:
        return x.copy()
    if savgol_filter:
        return savgol_filter(x, w, 3)
    k = np.ones(w) / w
    return np.convolve(np.pad(x, w // 2, mode="edge"), k, mode="valid")


def curva_camera(quadros):
    """Movimento global quadro a quadro: deslocamento do CENTRO (px), rotação (graus) e escala relativa."""
    g0 = cv2.cvtColor(quadros[0], cv2.COLOR_BGR2GRAY)
    h, w = g0.shape
    c = np.array([w / 2, h / 2, 1.0])
    linhas = [(0.0, 0.0, 0.0, 1.0)]
    for q in quadros[1:]:
        g1 = cv2.cvtColor(q, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(g0, maxCorners=500, qualityLevel=0.01, minDistance=8)
        M = None
        if p0 is not None and len(p0) >= 6:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, winSize=(21, 21), maxLevel=3)
            bom = st.ravel() == 1
            if bom.sum() >= 6:
                M, _ = cv2.estimateAffinePartial2D(p0[bom], p1[bom], method=cv2.RANSAC, ransacReprojThreshold=2.0)
        if M is None:  # fundo liso: tenta correlação de fase (só translação)
            (dx, dy), _ = cv2.phaseCorrelate(np.float32(g0), np.float32(g1))
            linhas.append((dx, dy, 0.0, 1.0))
        else:
            d = M @ c - c[:2]
            linhas.append((d[0], d[1], np.degrees(np.arctan2(M[1, 0], M[0, 0])), float(np.hypot(M[0, 0], M[1, 0]))))
        g0 = g1
    a = np.array(linhas)
    return np.column_stack([a[:, 0].cumsum(), a[:, 1].cumsum(), a[:, 2].cumsum(), a[:, 3].cumprod(), a[:, 0], a[:, 1]])


def resumo(traj, fps):
    x, y, rot, esc, vx, vy = traj.T
    vel = np.hypot(vx, vy) * fps  # px/s
    base_x, base_y = suaviza(x, fps), suaviza(y, fps)
    tx, ty = x - base_x, y - base_y
    tremida = np.hypot(tx, ty)
    espec = np.abs(np.fft.rfft(tx - tx.mean())) + np.abs(np.fft.rfft(ty - ty.mean()))
    fr = np.fft.rfftfreq(len(tx), 1 / fps)
    f_dom = float(fr[1:][espec[1:].argmax()]) if len(fr) > 1 else 0.0
    # chicotes: trechos com velocidade acima de 3× a mediana
    lim = max(np.median(vel) * 3, 200)
    rapido = vel > lim
    chicotes, ini = [], None
    for i, r in enumerate(rapido):
        if r and ini is None:
            ini = i
        if not r and ini is not None:
            chicotes.append(i - ini)
            ini = None
    parado = vel < max(np.median(vel), 1)
    return {
        "quadros": len(x),
        "tremida_rms_px": round(float(np.sqrt((tremida ** 2).mean())), 2),
        "tremida_freq_hz": round(f_dom, 2),
        "vel_mediana_px_s": round(float(np.median(vel)), 1),
        "vel_pico_px_s": round(float(vel.max()), 1),
        "chicotes": len(chicotes),
        "chicote_quadros_medio": round(float(np.mean(chicotes)), 1) if chicotes else 0,
        "pct_quase_parado": round(float(parado.mean() * 100), 1),
        "rot_amplitude_graus": round(float(rot.max() - rot.min()), 2),
        "escala_min_max": [round(float(esc.min()), 3), round(float(esc.max()), 3)],
    }


def grafico(series, saida, fps, titulo):
    """series: [(rótulo, traj, cor)] — desenha velocidade e tremida (x) no tempo."""
    W, H, m = 1600, 900, 60
    im = Image.new("RGB", (W, H), (18, 18, 20))
    d = ImageDraw.Draw(im)
    d.text((m, 15), titulo, font=fonte(26), fill="white")
    paineis = [("velocidade da câmera (px/s)", lambda t: np.hypot(t[:, 4], t[:, 5]) * fps),
               ("tremida em x (px) = posição − trajetória suavizada", lambda t: t[:, 0] - suaviza(t[:, 0], fps))]
    ph = (H - 2 * m - 40) // 2
    for p, (nome, fn) in enumerate(paineis):
        y0 = m + 30 + p * (ph + 20)
        d.rectangle([m, y0, W - m, y0 + ph], outline=(70, 70, 75))
        d.text((m + 8, y0 + 4), nome, font=fonte(18), fill=(190, 190, 195))
        vals = [fn(t) for _, t, _ in series]
        vmin = min(v.min() for v in vals); vmax = max(v.max() for v in vals)
        if vmax - vmin < 1e-6:
            vmax = vmin + 1
        n = max(len(v) for v in vals)
        for (rot_, _, cor), v in zip(series, vals):
            pts = [(m + i * (W - 2 * m) / max(n - 1, 1), y0 + ph - (vv - vmin) / (vmax - vmin) * (ph - 30) - 5) for i, vv in enumerate(v)]
            if len(pts) > 1:
                d.line(pts, fill=cor, width=2)
        d.text((W - m - 260, y0 + 4), f"{vmin:.1f} … {vmax:.1f}", font=fonte(16), fill=(150, 150, 155))
    x = m
    for rot_, _, cor in series:
        d.rectangle([x, H - 32, x + 18, H - 14], fill=cor); d.text((x + 26, H - 36), rot_, font=fonte(18), fill="white"); x += 360
    im.save(saida)


def cmd_camera(a):
    q, t, fps = ler_quadros(a.video, a.ini, a.fim, a.recorte, a.largura)
    traj = curva_camera(q)
    with open(a.saida + ".csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["t", "x", "y", "rot_graus", "escala", "dx", "dy", "fps"])
        for ti, r in zip(t, traj):
            w.writerow([round(ti, 4)] + [round(float(v), 4) for v in r] + [fps])
    r = resumo(traj, fps)
    grafico([(a.rotulo, traj, (52, 199, 89))], a.saida + ".png", fps, f"Câmera — {a.rotulo}")
    print(r)
    print(f"curva → {a.saida}.csv | gráfico → {a.saida}.png")


def ler_csv(c):
    with open(c, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    traj = np.array([[float(r[k]) for k in ("x", "y", "rot_graus", "escala", "dx", "dy")] for r in rows])
    return traj, float(rows[0]["fps"])


def cmd_compara(a):
    (ta, fa), (tb, fb) = ler_csv(a.csv_a), ler_csv(a.csv_b)
    ra, rb = resumo(ta, fa), resumo(tb, fb)
    grafico([(a.rotulo_a, ta, (240, 240, 245)), (a.rotulo_b, tb, (52, 199, 89))], a.saida + ".png", fa, f"{a.rotulo_a} × {a.rotulo_b}")
    print(a.rotulo_a, ra); print(a.rotulo_b, rb)
    print(f"gráfico → {a.saida}.png")


def cmd_folha(a):
    q, t, fps = ler_quadros(a.video, a.ini, a.fim, a.recorte, a.largura or 240)
    cols = a.colunas
    h, w = q[0].shape[:2]
    linhas = (len(q) + cols - 1) // cols
    im = Image.new("RGB", (cols * w, linhas * h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (qq, ti) in enumerate(zip(q, t)):
        x, y = (i % cols) * w, (i // cols) * h
        im.paste(Image.fromarray(cv2.cvtColor(qq, cv2.COLOR_BGR2RGB)), (x, y))
        d.rectangle([x, y, x + 96, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 2), f"{ti:.3f}", font=fonte(16), fill="yellow")
    im.save(a.saida, quality=88)
    print(f"{len(q)} quadros seguidos a {fps:.2f} qps → {a.saida}")


def cmd_rastro(a):
    q, t, fps = ler_quadros(a.video, a.ini, a.fim, a.recorte, a.largura)
    pilha = np.stack([x.astype(np.float32) for x in q])
    media = pilha.mean(0)
    dif = np.abs(np.diff(pilha, axis=0)).max(0) if len(q) > 1 else np.zeros_like(media)
    dif = np.clip(dif * 4, 0, 255)
    base = os.path.splitext(a.saida)[0]
    Image.fromarray(cv2.cvtColor(media.astype(np.uint8), cv2.COLOR_BGR2RGB)).save(base + "_rastro.png")
    Image.fromarray(cv2.cvtColor(dif.astype(np.uint8), cv2.COLOR_BGR2RGB)).save(base + "_diferenca.png")
    print(f"rastro e diferença de {len(q)} quadros → {base}_rastro.png / {base}_diferenca.png")


def cmd_ampliar(a):
    q, t, fps = ler_quadros(a.video, a.ini, a.ini + 0.1, a.recorte)
    img = cv2.cvtColor(q[0], cv2.COLOR_BGR2RGB)
    z = cv2.resize(img, None, fx=a.zoom, fy=a.zoom, interpolation=cv2.INTER_NEAREST)
    lut = np.clip((np.arange(256) - 64) * 2.0, 0, 255).astype(np.uint8)  # estica os meios-tons: brilho e degradê aparecem
    est = cv2.LUT(z, lut)
    lado = np.concatenate([z, est], axis=1)
    Image.fromarray(lado).save(a.saida)
    print(f"quadro em {t[0]:.3f} s, recorte ×{a.zoom} (normal | contraste esticado) → {a.saida}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="comando")

    def comum(s, video=True):
        if video:
            s.add_argument("video", help="vídeo a analisar")
        s.add_argument("--ini", type=float, default=0.0, help="início do trecho, em segundos (padrão: 0)")
        s.add_argument("--fim", type=float, default=None, help="fim do trecho, em segundos (padrão: até o fim)")
        s.add_argument("--recorte", type=lambda v: [int(x) for x in v.split(",")], default=None,
                       help="só esta região: x,y,largura,altura em pixels do vídeo")
        s.add_argument("--largura", type=int, default=None, help="reduz cada quadro para esta largura antes de analisar")
        s.add_argument("--saida", required=True, help="arquivo (ou prefixo, em camera/compara) de saída")
    s = sub.add_parser("camera", help="curva da câmera: trajetória, tremida e chicotes (CSV + PNG)")
    comum(s); s.add_argument("--rotulo", default="vídeo", help="nome da série no gráfico"); s.set_defaults(f=cmd_camera)
    s = sub.add_parser("folha", help="quadros seguidos, numerados, em grade")
    comum(s); s.add_argument("--colunas", type=int, default=10, help="quadros por linha (padrão: 10)"); s.set_defaults(f=cmd_folha)
    s = sub.add_parser("rastro", help="onion skin e diferença entre quadros (PNG)")
    comum(s); s.set_defaults(f=cmd_rastro)
    s = sub.add_parser("ampliar", help="recorte ampliado de um quadro + contraste esticado")
    comum(s); s.add_argument("--zoom", type=int, default=4, help="ampliação (padrão: 4)"); s.set_defaults(f=cmd_ampliar)
    s = sub.add_parser("compara", help="duas curvas de câmera (CSVs do comando camera) no mesmo gráfico")
    s.add_argument("csv_a", help="CSV da primeira curva (ex.: a referência)"); s.add_argument("csv_b", help="CSV da segunda curva")
    s.add_argument("--saida", required=True, help="prefixo do PNG de saída")
    s.add_argument("--rotulo-a", default="original"); s.add_argument("--rotulo-b", default="recriação"); s.set_defaults(f=cmd_compara)
    a = p.parse_args()
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    a.f(a)


if __name__ == "__main__":
    main()
