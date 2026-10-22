"""sintetizar_sfx.py — gera a biblioteca inicial de efeitos sonoros, sintetizada (determinística, sem licença).

É o que um estúdio novo tem de saída: um som para cada categoria que o mapa padrão (mapa_padrao.py) usa, com 2 a 5
variações, já no padrão da casa (nivelar.py) e com o catálogo de picos. Sintetizar em vez de baixar dá duas coisas:
cada som sabe onde fica o próprio pico, e nada depende de biblioteca de terceiros. Quando quiser sons gravados de
verdade, solte um pack em qualquer pasta e rode o nivelar.py (ver 05-biblioteca/som/README.md).

Uso:
  uv run scripts/som/sintetizar_sfx.py                      # gera em 05-biblioteca/som/sfx (refaz só os sintetizados)
  uv run scripts/som/sintetizar_sfx.py --amostra prova.wav  # também monta um arquivo com todos, um depois do outro, para ouvir
  uv run scripts/som/sintetizar_sfx.py --destino outra/pasta

Também serve de módulo: a Mesa usa `nota_sino`, `golpe_tonal` e `pad` para os tonais no tom da música.
"""
from __future__ import annotations

import argparse, sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt, stft, istft, fftconvolve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _estudio import SFX  # noqa: E402

SR = 48000
SEMENTE = 7


def rng(k=0):
    return np.random.default_rng(SEMENTE * 1000 + k)


def ruido(n, k=0):
    return rng(k).standard_normal(n)


def _sos(tipo, f):
    f = np.clip(np.asarray(f, float) / (SR / 2), 1e-4, 0.999)
    return butter(4, f if f.ndim else float(f), btype=tipo, output="sos")


def bp(x, lo, hi):
    return sosfilt(_sos("band", [lo, hi]), x, axis=0)


def lp(x, f):
    return sosfilt(_sos("low", f), x, axis=0)


def hp(x, f):
    return sosfilt(_sos("high", f), x, axis=0)


def norm(x):
    return x / (np.abs(x).max() + 1e-12)


def tempo(dur):
    return np.arange(int(dur * SR)) / SR


def senoide(f, t, fase=0.0):
    """Seno com frequência que pode variar no tempo (f escalar ou array do tamanho de t)."""
    f = np.broadcast_to(np.asarray(f, float), t.shape)
    return np.sin(2 * np.pi * np.cumsum(f) / SR + fase)


def estereo(x, p0=0.0, p1=None):
    """Mono → estéreo com pan de p0 a p1 (−1 esquerda, +1 direita), potência constante."""
    p = np.linspace(p0, p0 if p1 is None else p1, len(x))
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1) * np.sqrt(2)


def sala(x, secs=0.4, mix=0.15, brilho=6000, k=0, pre=0.008):
    """Reverb curto (ruído com decaimento de −60 dB em `secs`), canais descorrelacionados: corpo e largura."""
    x = estereo(x) if x.ndim == 1 else x
    n = int(secs * SR); t = np.arange(n) / SR
    out = np.zeros((len(x) + n + int(pre * SR), 2))
    out[: len(x)] += x * (1 - mix)
    for c in range(2):
        ir = lp(ruido(n, 900 + 2 * k + c), brilho) * np.exp(-t * 6.9 / secs)
        ir = np.concatenate([np.zeros(int(pre * SR)), ir / (np.sqrt((ir ** 2).sum()) + 1e-12)])
        w = fftconvolve(x[:, c], ir)
        out[: len(w), c] += w * mix * 4
    return out


def junta(*partes):
    """Soma camadas (mono ou estéreo) de comprimentos diferentes, todas começando em 0."""
    partes = [estereo(p) if p.ndim == 1 else p for p in partes]
    out = np.zeros((max(len(p) for p in partes), 2))
    for p in partes:
        out[: len(p)] += p
    return out


def em(x, t0, total):
    """Coloca o som x (mono ou estéreo) em t0 segundos dentro de um buffer de `total` s."""
    x = estereo(x) if x.ndim == 1 else x
    out = np.zeros((int(total * SR), 2)); a = int(t0 * SR)
    m = min(len(x), len(out) - a)
    out[a:a + m] += x[:m]
    return out


def varre_ruido(dur, f0, f1, q=0.35, k=0, curva=None):
    """Ruído num passa-banda que varre f0 → f1 (no domínio da STFT). `curva` (0–1 → 0–1) muda o ritmo da varredura."""
    n = int(dur * SR)
    x = ruido(n, k)
    nper = 1024
    f, _, Z = stft(x, fs=SR, nperseg=nper, noverlap=nper * 3 // 4)
    u = np.linspace(0, 1, Z.shape[1])
    u = curva(u) if curva else u
    fc = np.exp(np.log(max(f0, 20)) + (np.log(max(f1, 20)) - np.log(max(f0, 20))) * u)
    G = np.exp(-0.5 * ((f[:, None] - fc[None, :]) / (fc[None, :] * q)) ** 2)
    _, y = istft(Z * G, fs=SR, nperseg=nper, noverlap=nper * 3 // 4)
    y = y[:n]
    return norm(np.pad(y, (0, n - len(y))))


def notas(nome):
    """'A4' → 440 Hz; 'C#5' → 554,4 Hz."""
    N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    n, o = nome[:-1], int(nome[-1])
    return 440.0 * 2 ** ((N.index(n) + 12 * (o - 4) - 9) / 12)


# ───────────────────────── tonais (também usados pela Mesa) ─────────────────────────
def nota_sino(f, dur=1.4, brilho=1.0, k=0):
    """Nota de sino/marimba macia: parciais inarmônicos curtos sobre um fundamental longo."""
    t = tempo(dur)
    y = np.zeros_like(t)
    for m, a, tau in ((1, 1.0, 0.55), (2.0, 0.22 * brilho, 0.22), (2.76, 0.18 * brilho, 0.16), (5.4, 0.07 * brilho, 0.06),
                      (8.93, 0.03 * brilho, 0.03)):
        if f * m < SR / 2.2:
            y += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (tau * dur / 1.4))
    y *= np.minimum(1, t / 0.0015)
    return norm(y)


def golpe_tonal(f_raiz, menor=False, dur=2.6, k=0):
    """Golpe cinematográfico no tom: acorde (raiz, terça, quinta, oitava) com ataque de piano + sub com queda + cauda."""
    t = tempo(dur)
    terca = 2 ** ((3 if menor else 4) / 12)
    y = np.zeros_like(t)
    for r, a in ((1, 1.0), (terca, 0.55), (1.5, 0.7), (2, 0.5), (3, 0.18)):
        f = f_raiz * 2 * r
        y += a * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.9)
    sub = senoide(f_raiz * 0.5 * (1 + 0.9 * np.exp(-t / 0.05)), t) * np.exp(-t / 0.55) * 1.4
    ataque = lp(ruido(len(t), 300 + k), 2500) * np.exp(-t / 0.012) * 0.6
    y = np.tanh((y * 0.5 + sub + ataque) * 1.2)
    return sala(norm(y), secs=2.2, mix=0.25, brilho=4000, k=k)


def pad(freqs, dur, k=0):
    """Cama tonal: serras desafinadas de leve, passa-baixa, entrada e saída lentas (drone no tom)."""
    t = tempo(dur)
    y = np.zeros_like(t)
    for i, f in enumerate(freqs):
        for d in (-0.06, 0.0, 0.07):
            fr = f * 2 ** (d / 12)
            y += ((t * fr + 0.13 * i) % 1.0 - 0.5) / len(freqs)
    y = lp(y, 1400) * (1 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    env = np.minimum(1, t / min(1.5, dur / 3)) * np.minimum(1, (dur - t) / min(1.0, dur / 3))
    return sala(norm(y * env), secs=1.8, mix=0.3, brilho=3000, k=k)


# ───────────────────────── efeitos ─────────────────────────
# Cada função devolve o sinal (mono ou estéreo); o nivelamento e o pico ficam com nivelar.nivela.
def clique(v=0):
    f = (2700, 3300, 3900, 2400)[v % 4]
    t = tempo(0.07)
    tr = bp(ruido(len(t), 10 + v), 2200, 8000) * np.exp(-t / 0.0012) * 0.7
    bl = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) * 0.45
    corpo = np.sin(2 * np.pi * (190 + 25 * v) * t) * np.exp(-t / 0.012) * 0.5 + bp(ruido(len(t), 20 + v), 600, 1800) * np.exp(-t / 0.004) * 0.3
    return sala(norm(tr + bl + corpo), secs=0.25, mix=0.08, k=v)


def pop(v=0):
    f0, f1 = ((980, 320), (820, 260), (1250, 390), (700, 230))[v % 4]
    t = tempo(0.14)
    f = f1 + (f0 - f1) * np.exp(-t / 0.016)
    y = senoide(f, t) * np.exp(-t / 0.035) + 0.15 * senoide(2 * f, t) * np.exp(-t / 0.02)
    y += lp(ruido(len(t), 30 + v), 4000) * np.exp(-t / 0.0018) * 0.25
    return sala(norm(y * np.minimum(1, t / 0.0008)), secs=0.3, mix=0.1, k=v)


def _tecla(r, forte=1.0, espaco=False):
    t = tempo(0.16)
    lo, hi = (160, 700) if espaco else (250, 1300)
    thock = bp(r.standard_normal(len(t)), lo, hi) * np.exp(-t / (0.016 if espaco else 0.010)) * 0.9
    estalo = bp(r.standard_normal(len(t)), 2500, 8500) * np.exp(-t / 0.0008) * 0.45
    ress = np.sin(2 * np.pi * r.uniform(1700, 2600) * t) * np.exp(-t / 0.004) * 0.2
    y = thock + estalo + ress
    k = int(r.uniform(0.065, 0.1) * SR)                      # a tecla subindo
    y[k:] += (bp(r.standard_normal(len(t) - k), 1500, 6000) * np.exp(-t[: len(t) - k] / 0.0015) * 0.25)
    return norm(y) * forte


def tecla(v=0):
    return sala(_tecla(rng(40 + v), espaco=(v == 4)), secs=0.2, mix=0.06, k=v)


def digitacao(v=0):
    r = rng(60 + v)
    dur = 2.2
    out = np.zeros(int((dur + 0.2) * SR))
    t0 = 0.0
    while t0 < dur:
        y = _tecla(r, r.uniform(0.55, 1.0), espaco=r.random() < 0.12)
        a = int(t0 * SR); out[a:a + len(y)] += y[: len(out) - a]
        t0 += r.gamma(4, 0.028 if v == 0 else 0.022) + (r.random() < 0.08) * r.uniform(0.15, 0.3)
    return sala(estereo(norm(out), -0.05, 0.05), secs=0.25, mix=0.07, k=v)


def notificacao(v=0):
    seq = (("E6", 0.0), ("A6", 0.09)), (("C6", 0.0), ("E6", 0.07), ("G6", 0.14)), (("G6", 0.0),)
    s = seq[v % 3]
    out = np.zeros(int(1.3 * SR))
    for nome, t0 in s:
        y = nota_sino(notas(nome), 1.1, brilho=0.8 if v != 2 else 1.4)
        a = int(t0 * SR); out[a:a + len(y)] += y[: len(out) - a] * (0.8 if t0 == 0 and len(s) > 1 else 1.0)
    return sala(norm(out), secs=0.7, mix=0.18, brilho=8000, k=v)


def whoosh(v=0):
    dur, f0, f1, pico = ((0.34, 400, 6000, 0.62), (0.42, 300, 5000, 0.68), (0.5, 250, 4200, 0.7), (0.38, 600, 7500, 0.6))[v % 4]
    t = np.linspace(0, 1, int(dur * SR))
    env = np.where(t < pico, (t / pico) ** 2.4, np.exp(-(t - pico) / (1 - pico) * 4.5))
    corpo = varre_ruido(dur, f0, f1, q=0.45, k=70 + v, curva=lambda u: np.where(u < pico, (u / pico) ** 1.5 * 0.85, 0.85 + 0.15 * (u - pico) / (1 - pico)))
    ar = varre_ruido(dur, f1 * 0.9, f1 * 1.5, q=0.2, k=80 + v) * env ** 2 * 0.25
    y = hp(corpo * env + ar, 90)
    lado = 0.5 if v % 2 else -0.5
    return sala(estereo(norm(y), -lado, lado), secs=0.35, mix=0.1, k=v)


def whoosh_grande(v=0):
    dur, f0, f1 = ((1.05, 160, 3200), (1.25, 110, 2400), (0.95, 220, 4200))[v % 3]
    n = int(dur * SR); u = np.linspace(0, 1, n); pico = 0.62
    env = np.where(u < pico, (u / pico) ** 2.2, np.exp(-(u - pico) / (1 - pico) * 3.5))
    corpo = varre_ruido(dur, f0, f1, q=0.5, k=90 + v, curva=lambda x: np.where(x < pico, (x / pico) ** 1.3 * 0.9, 0.9 + 0.1 * (x - pico) / (1 - pico)))
    t = u * dur
    sub = senoide(45 + 35 * env, t) * env ** 1.5 * (0.9 if v == 1 else 0.45)
    y = hp(corpo * env, 60) + sub
    return sala(estereo(norm(y), -0.7, 0.7), secs=1.2, mix=0.18, brilho=5000, k=v)


def carimbo(v=0):
    t = tempo(0.4)
    f = (55 if v == 0 else 80) + (45 if v == 0 else 60) * np.exp(-t / 0.02)
    baque = senoide(f, t) * np.exp(-t / (0.07 if v == 0 else 0.045))
    tapa = bp(ruido(len(t), 100 + v), 500, 3500) * np.exp(-t / 0.018) * 0.7
    estalo = hp(ruido(len(t), 110 + v), 3000) * np.exp(-t / 0.0015) * 0.5
    y = np.tanh((baque + tapa + estalo) * 1.8)
    return sala(norm(y), secs=0.45, mix=0.16, brilho=5000, k=v)


def impacto(v=0):
    dur, fi, ff, tau = ((1.8, 120, 42, 0.42), (1.4, 160, 52, 0.3), (2.3, 90, 34, 0.6))[v % 3]
    t = tempo(dur)
    f = ff + (fi - ff) * np.exp(-t / 0.045)
    sub = senoide(f, t) * np.exp(-t / tau)
    estalo = lp(ruido(len(t), 120 + v), 3500) * np.exp(-t / 0.012) * 0.9
    corpo = bp(ruido(len(t), 130 + v), 120, 900) * np.exp(-t / 0.09) * (0.8 if v == 1 else 0.5)
    y = np.tanh((sub + estalo + corpo) * 1.6)
    return sala(norm(y), secs=1.6, mix=0.2, brilho=3000, k=v)


def logo(v=0):
    acorde = (("D5", "F#5", "A5", "D6"), ("G4", "B4", "D5", "G5"))[v % 2]
    out = np.zeros(int(2.2 * SR))
    for i, nome in enumerate(acorde):
        y = nota_sino(notas(nome), 2.0, brilho=1.1)
        a = int(i * 0.012 * SR); out[a:a + len(y)] += y[: len(out) - a] * (1 - 0.12 * i)
    t = tempo(2.2)
    sub = senoide(55 + 40 * np.exp(-t / 0.04), t) * np.exp(-t / 0.3) * 0.9
    brilho_ = hp(ruido(len(t), 140 + v), 6000) * np.exp(-t / 0.5) * 0.08
    return sala(norm(out + sub + brilho_), secs=2.0, mix=0.25, brilho=8000, k=v)


def pouso(v=0):
    t = tempo(0.3)
    f = (70 if v == 0 else 55) + 70 * np.exp(-t / 0.03)
    y = senoide(f, t) * np.exp(-t / 0.05) + lp(ruido(len(t), 150 + v), 900) * np.exp(-t / 0.03) * 0.6
    y += bp(ruido(len(t), 155 + v), 1500, 5000) * np.exp(-t / 0.006) * 0.2
    return sala(norm(y), secs=0.3, mix=0.1, k=v)


def _grao(n, k, taxa=40):
    """Modulação áspera de papel: ruído passa-baixa em `taxa` Hz, só positivo."""
    m = lp(ruido(n, k), taxa)
    return np.abs(norm(m)) * 0.7 + 0.3


def papel(v=0):
    if v == 1:   # virar: duas passadas curtas + estalos
        out = np.zeros(int(0.45 * SR))
        for j, t0 in enumerate((0.0, 0.11)):
            d = 0.13; t = np.linspace(0, 1, int(d * SR))
            y = bp(ruido(len(t), 160 + j), 1800, 8000) * np.sin(np.pi * t) ** 1.5 * _grao(len(t), 165 + j, 60)
            a = int(t0 * SR); out[a:a + len(y)] += y * (1 if j else 0.7)
        est = np.zeros(len(out)); r = rng(168)
        for _ in range(14):
            i = r.integers(0, len(out) - 200); est[i] += r.uniform(0.3, 1)
        out += hp(est, 3000) * 0.5
        return sala(estereo(norm(out), 0.2, -0.2), secs=0.3, mix=0.12, k=v)
    dur = 0.42 if v == 0 else 0.28
    t = np.linspace(0, 1, int(dur * SR))
    env = np.where(t < 0.7, (t / 0.7) ** 1.6, np.exp(-(t - 0.7) / 0.3 * 5))
    y = bp(ruido(len(t), 170 + v), 1500, 7000) * env * _grao(len(t), 175 + v)
    y += lp(ruido(len(t), 178 + v), 700) * env * 0.25
    return sala(estereo(norm(y), -0.3, 0.3), secs=0.3, mix=0.1, k=v)


def obturador(v=0):
    gap = (0.075, 0.115)[v % 2]
    out = np.zeros(int((gap + 0.15) * SR))
    for j, t0 in enumerate((0.0, gap)):
        t = tempo(0.06)
        c = bp(ruido(len(t), 180 + 2 * v + j), 1000, 6000) * np.exp(-t / 0.004) + np.sin(2 * np.pi * (900 + 300 * j) * t) * np.exp(-t / 0.006) * 0.4
        a = int(t0 * SR); out[a:a + len(c)] += c * (1.0 if j == 0 else 0.75)
    t = tempo(gap)
    out[: len(t)] += bp(ruido(len(t), 190 + v), 2000, 5000) * 0.06 * np.sin(np.pi * t / gap)
    return sala(norm(out), secs=0.25, mix=0.1, k=v)


def _tique(f, k):
    t = tempo(0.03)
    return (bp(ruido(len(t), k), 1800, 7000) * np.exp(-t / 0.0012) * 0.7 + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.005) * 0.5
            + bp(ruido(len(t), k + 1), 500, 1500) * np.exp(-t / 0.004) * 0.3)


def contador(v=0):
    dur, n = (0.75, 11) if v == 0 else (0.8, 18)
    u = np.linspace(0, 1, n) ** (2.2 if v == 0 else 0.85)       # 0: desacelera e trava; 1: rola mais regular
    out = np.zeros(int((dur + 0.1) * SR))
    for i, x in enumerate(u):
        s = _tique(2100 + 90 * (i % 3) + (300 * i / n if v == 1 else 0), 200 + i)
        a = int(x * dur * SR); out[a:a + len(s)] += s[: len(out) - a] * (0.5 + 0.5 * i / n)
    if v == 0:
        out[int(dur * SR):int(dur * SR) + len(s)] += _tique(3400, 230)[: len(out) - int(dur * SR)] * 1.2
    return sala(norm(out), secs=0.25, mix=0.08, k=v)


def relogio(v=0):
    out = np.zeros(int(2.1 * SR))
    for i in range(4):
        t = tempo(0.05)
        s = bp(ruido(len(t), 240 + i), 800, 2200) * np.exp(-t / 0.005) * 0.6 + np.sin(2 * np.pi * (3100 if i % 2 == 0 else 2500) * t) * np.exp(-t / 0.003)
        a = int(i * 0.5 * SR); out[a:a + len(s)] += s
    return sala(norm(out), secs=0.4, mix=0.15, k=v)


def sucesso(v=0):
    seq = (("C6", 0.0), ("E6", 0.075), ("G6", 0.15), ("C7", 0.225)) if v == 0 else (("G5", 0.0), ("D6", 0.1))
    out = np.zeros(int(1.2 * SR))
    for nome, t0 in seq:
        y = nota_sino(notas(nome), 0.9, brilho=0.6)
        a = int(t0 * SR); out[a:a + len(y)] += y[: len(out) - a]
    return sala(norm(out), secs=0.6, mix=0.18, brilho=8000, k=v)


def caneta(v=0):
    r = rng(260 + v)
    dur = 0.7
    n = int(dur * SR); env = np.zeros(n); t0 = 0.0
    while t0 < dur - 0.05:
        d = r.uniform(0.06, 0.13); a, b = int(t0 * SR), min(n, int((t0 + d) * SR))
        env[a:b] = np.sin(np.linspace(0, np.pi, b - a)) * r.uniform(0.6, 1.0)
        t0 += d + r.uniform(0.0, 0.03)
    lo, hi = (2500, 8000) if v == 0 else (1200, 5000)
    y = bp(ruido(n, 270 + v), lo, hi) * env * _grao(n, 275 + v, 120)
    return sala(estereo(norm(y), -0.1, 0.15), secs=0.2, mix=0.06, k=v)


def rolagem(v=0):
    n_t, passo = (12, 0.038) if v == 0 else (14, None)
    out = np.zeros(int(0.7 * SR))
    for i in range(n_t):
        t0 = i * passo if passo else 0.5 * (1 - (1 - i / n_t) ** 1.8)
        s = _tique(1600 + 200 * (i % 2), 300 + i) * (0.45 + 0.35 * np.sin(np.pi * i / n_t))
        a = int(t0 * SR); out[a:a + len(s)] += s[: len(out) - a]
    t = np.linspace(0, 1, len(out))
    out += bp(ruido(len(out), 320 + v), 2000, 6000) * np.sin(np.pi * t) * 0.04
    return sala(norm(out), secs=0.2, mix=0.06, k=v)


def riser(v=0):
    dur = 1.8 if v == 0 else 3.0
    n = int(dur * SR); u = np.linspace(0, 1, n)
    y = varre_ruido(dur, 400, 9000, q=0.3, k=340 + v) * u ** 2.2
    f = 110 * 2 ** (u * (2 if v == 0 else 2.5))
    serra = ((np.cumsum(f) / SR) % 1.0) * 2 - 1
    serra2 = ((np.cumsum(f * 1.005) / SR + 0.3) % 1.0) * 2 - 1
    y = y + lp(serra + serra2, 2500 + 2500 * (v == 1)) * u ** 3 * 0.3
    y = hp(y, 150) * (1 + 0.25 * np.sin(2 * np.pi * (4 + 10 * u) * u * dur) * u)   # trêmulo que acelera
    return estereo(norm(y), -0.3, 0.3)


def fita(v=0):
    dur = 0.45
    n = int(dur * SR); u = np.linspace(0, 1, n)
    env = np.where(u < 0.85, (u / 0.85) ** 1.2, np.exp(-(u - 0.85) / 0.15 * 6))
    est = (rng(360 + v).random(n) < 0.02 + 0.08 * u) * rng(365 + v).uniform(0.3, 1.0, n)
    y = bp(ruido(n, 370 + v), 800, 6000) * env * 0.6 + hp(est, 1500) * env
    return sala(estereo(norm(y), 0.1, -0.1), secs=0.2, mix=0.06, k=v)


def glitch(v=0):
    r = rng(400 + v)
    out = []
    while sum(len(x) for x in out) < 0.28 * SR:
        d = int(r.uniform(0.012, 0.04) * SR); t = np.arange(d) / SR
        tipo = r.integers(0, 3)
        if tipo == 0:
            s = np.sign(np.sin(2 * np.pi * r.uniform(200, 2000) * t))
        elif tipo == 1:
            s = np.round(r.standard_normal(d) * 3) / 3
        else:
            s = np.zeros(d)
        out.append(s * r.uniform(0.4, 1.0))
    y = np.concatenate(out)
    y = np.round(y * 8) / 8                                 # bitcrush
    return estereo(norm(lp(y, 9000)), r.uniform(-0.4, 0.4))


def brilho(v=0):
    if v == 2:   # sino único com brilho
        y = nota_sino(notas("A6"), 1.6, brilho=1.5)
        return sala(norm(y), secs=1.2, mix=0.25, brilho=9000, k=v)
    r = rng(420 + v)
    dur = 1.0
    out = np.zeros((int((dur + 0.3) * SR), 2))
    for i in range(26):
        t0 = dur * (i / 26) ** 1.4 + r.uniform(0, 0.02)
        f = r.uniform(2500, 7000) * (1 if v == 0 else 0.7)
        t = tempo(r.uniform(0.04, 0.14))
        s = np.sin(2 * np.pi * f * t) * np.exp(-t / (len(t) / SR / 3)) * (1 - 0.6 * i / 26)
        a = int(t0 * SR); m = min(len(s), len(out) - a)
        out[a:a + m] += estereo(s, r.uniform(-0.7, 0.7))[:m]
    out += estereo(hp(ruido(len(out), 430 + v), 6000) * np.exp(-np.linspace(0, 5, len(out))) * 0.05)
    return sala(out / (np.abs(out).max() + 1e-12), secs=0.9, mix=0.25, brilho=9000, k=v)


# categoria → (função, nº de variações). A Mesa (mapa_padrao.py) usa estas categorias.
KIT = {
    "clique": (clique, 3), "pop": (pop, 4), "tecla": (tecla, 5), "digitacao": (digitacao, 2),
    "notificacao": (notificacao, 3), "whoosh": (whoosh, 4), "whoosh-grande": (whoosh_grande, 3),
    "carimbo": (carimbo, 2), "impacto": (impacto, 3), "logo": (logo, 2), "pouso": (pouso, 2), "papel": (papel, 3),
    "obturador": (obturador, 2), "contador": (contador, 2), "relogio": (relogio, 1), "sucesso": (sucesso, 2),
    "caneta": (caneta, 2), "rolagem": (rolagem, 2), "riser": (riser, 2), "fita": (fita, 1), "glitch": (glitch, 3),
    "brilho": (brilho, 3),
}


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    import nivelar as N
    ap = argparse.ArgumentParser(description="Gera a biblioteca inicial de efeitos sintetizados, já nivelada.")
    ap.add_argument("--destino", default=str(SFX), help="pasta da biblioteca (padrão: 05-biblioteca/som/sfx)")
    ap.add_argument("--amostra", help="também grava um WAV com todos os efeitos em sequência, para ouvir")
    a = ap.parse_args()
    dest = Path(a.destino)
    antigos = N.le_catalogo(dest)
    novos, fila = {}, []
    for cat, (fn, n) in KIT.items():
        for v in range(n):
            rel = f"{cat}/{cat}-{v + 1}.wav"
            if rel in antigos and antigos[rel].get("origem") != "sintetizado":
                rel = f"{cat}/{cat}-{v + 1}-sint.wav"          # não sobrescreve um arquivo que veio de um pack
            y, info = N.nivela(fn(v), cama=cat in N.CAMAS)
            N.grava(dest / rel, y)
            novos[rel] = dict(categoria=cat, origem="sintetizado", **info)
            fila.append((rel, y))
    cat = N.escreve_catalogo(dest, novos)
    print(f"sintetizados {len(novos)} efeitos em {len(KIT)} categorias → {dest}")
    print(f"catálogo: {len(cat)} efeitos (catalogo.json e CATALOGO.md)")
    if a.amostra:
        gap = np.zeros((int(0.45 * SR), 2))
        N.grava(a.amostra, np.vstack([np.vstack([y, gap]) for _, y in fila]))
        print("amostra para ouvir:", a.amostra)


if __name__ == "__main__":
    main()
