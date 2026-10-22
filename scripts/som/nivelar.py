"""nivelar.py — põe qualquer pasta de efeitos sonoros no padrão da casa e escreve o catálogo que a Mesa lê.

Padrão (o mesmo da biblioteca sintetizada pelo sintetizar_sfx.py):
- WAV 48 kHz estéreo 16 bits, DC removido; começa ~10 ms antes do primeiro som (silêncio inicial cortado),
  fade-in de 2 ms e fade-out de 20 ms; silêncio do fim cortado;
- pico momentâneo (EBU R128, janela de 400 ms) em −20 LUFS nos efeitos curtos e −24 LUFS nas camas
  (riser, ambiência, digitação contínua, relógio…);
- pico verdadeiro ≤ −3 dBTP: se o teto chega antes do alvo, o arquivo fica abaixo dele. É normal em cliques e
  teclas (a janela de 400 ms subestima sons de poucos milissegundos, que continuam audíveis);
- mede o instante do pico (envelope de 5 ms) para sincronizar: at = evento − pico_ms/1000.
Saída: <destino>/<categoria>/<nome>.wav + catalogo.json (lido pela Mesa) + CATALOGO.md (para gente ler).

Uso:
  uv run scripts/som/nivelar.py PASTA_DO_PACK                     # nivela para a biblioteca (05-biblioteca/som/sfx)
  uv run scripts/som/nivelar.py PASTA --categoria whoosh          # força a categoria de todos os arquivos
  uv run scripts/som/nivelar.py PASTA --destino outra/pasta       # outra biblioteca
  uv run scripts/som/nivelar.py 05-biblioteca/som/sfx             # renivela a biblioteca no lugar e refaz o catálogo
A categoria sai do nome da pasta e do arquivo (whoosh, click, impact, riser, notification, typing…); o que não
casar com nenhuma vira uma categoria com o nome da pasta, e a Mesa usa do mesmo jeito.
"""
from __future__ import annotations

import argparse, json, re, subprocess, sys, unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import lfilter, resample_poly

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _estudio import RAIZ, SFX  # noqa: E402

SR = 48000
ALVO_CURTO, ALVO_CAMA, TETO_TP = -20.0, -24.0, -3.0
AUDIO = (".wav", ".mp3", ".flac", ".ogg", ".aif", ".aiff", ".m4a", ".opus")
CAMAS = {"riser", "digitacao", "relogio", "ambiencia"}
PALAVRAS_CAMA = ("ambience", "ambiance", "ambiencia", "room-tone", "roomtone", "atmos", "drone", "riser", "swell",
                 "uplifter", "build-up", "buildup", "bed")
# palavra no caminho → categoria da casa (a primeira que casar vence; as mais específicas vêm antes)
CHAVES = [
    (("riser", "uplifter", "build-up", "buildup", "swell", "rise"), "riser"),
    (("ambience", "ambiance", "ambiencia", "room-tone", "roomtone", "atmos"), "ambiencia"),
    (("notification", "notificacao", "notif", "alert", "alerta", "ding", "chime", "message", "mensagem"), "notificacao"),
    (("typing", "digitacao", "digitando", "keyboard", "teclado"), "digitacao"),
    (("keystroke", "tecla", "key-press", "keypress"), "tecla"),
    (("shutter", "obturador", "camera", "photo"), "obturador"),
    (("stamp", "carimbo"), "carimbo"),
    (("glitch", "error", "erro", "digital-noise"), "glitch"),
    (("sparkle", "shimmer", "brilho", "magic", "magica", "twinkle", "bell", "sino"), "brilho"),
    (("success", "sucesso", "correct", "win", "confirm", "achievement"), "sucesso"),
    (("scroll", "rolagem", "wheel"), "rolagem"),
    (("pen", "pencil", "caneta", "scribble", "marker", "write", "escrev"), "caneta"),
    (("paper", "papel", "page", "pagina", "folha", "card-slide"), "papel"),
    (("tape", "fita"), "fita"),
    (("tick", "clock", "relogio", "tique"), "relogio"),
    (("counter", "contador", "slot", "roll"), "contador"),
    (("land", "pouso", "drop-soft", "thud-soft"), "pouso"),
    (("impact", "impacto", "hit", "boom", "punch", "slam", "thud", "smash", "bass-drop", "subdrop", "braam"), "impacto"),
    (("logo", "sting", "reveal", "intro"), "logo"),
    (("whoosh", "woosh", "swoosh", "swish", "swipe", "swoop", "transition", "transicao", "pass-by", "flyby"), "whoosh"),
    (("pop", "bubble", "bolha", "blip"), "pop"),
    (("click", "clique", "tap", "toque", "button", "botao", "ui"), "clique"),
]


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\.(wav|mp3|flac|ogg|aiff?|m4a|opus)$", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "som"


def categoria_por_nome(rel: str, dur: float) -> str:
    """Categoria da casa pelo caminho do arquivo; whoosh longo vira whoosh-grande, digitação curta vira tecla."""
    texto = "-" + slug(rel.replace("/", "-")) + "-"
    for palavras, cat in CHAVES:
        if any(f"-{p}" in texto for p in palavras):
            if cat == "whoosh" and dur > 0.9:
                return "whoosh-grande"
            if cat == "digitacao" and dur < 0.6:
                return "tecla"
            return cat
    partes = [p for p in rel.split("/")[:-1] if p]
    return slug(partes[0]) if partes else "avulsos"


# ───────────────────────── medidas ─────────────────────────
def decodifica(path) -> np.ndarray:
    """Qualquer áudio → float32 (n, 2) a 48 kHz, pelo ffmpeg do PATH."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def _kpond(x):
    """Filtro K do BS.1770 (coeficientes para 48 kHz)."""
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)


def momentanea(x, passo=0.02, janela=0.4):
    """Loudness momentânea (LUFS) em janelas de `janela` s a cada `passo` s; fora do arquivo conta como silêncio."""
    x = np.atleast_2d(x.T).T
    p = (_kpond(x) ** 2).sum(axis=1)
    w, h = int(janela * SR), max(1, int(passo * SR))
    c = np.concatenate([[0.0], np.cumsum(p)])
    idx = np.arange(-w // 2, len(p), h)
    a, b = np.clip(idx, 0, len(p)), np.clip(idx + w, 0, len(p))
    return -0.691 + 10 * np.log10((c[b] - c[a]) / w + 1e-12)


def momentaneo_max(x) -> float:
    return float(momentanea(x).max())


def pico_verdadeiro(x) -> float:
    """Pico verdadeiro aproximado (dBTP) com sobreamostragem de 4×."""
    return float(20 * np.log10(np.abs(resample_poly(x, 4, 1, axis=0)).max() + 1e-12))


def pico_ms(x) -> int:
    """Instante do pico do envelope de 5 ms, em ms desde o início do arquivo."""
    y = np.atleast_2d(x.T).T.mean(axis=1)
    n = int(0.005 * SR)
    e = np.convolve(y * y, np.ones(n) / n, mode="same")
    return int(np.argmax(e) / SR * 1000)


def nivela(x, cama=False, alvo=None):
    """Põe um sinal (n, 2) no padrão. Devolve (sinal, info)."""
    x = np.atleast_2d(np.asarray(x, np.float64).T).T
    if x.shape[1] == 1:
        x = np.hstack([x, x])
    x = x[:, :2] - x[:, :2].mean(axis=0)
    a = np.abs(x).max(axis=1)
    pk = float(a.max())
    if pk <= 1e-6:
        raise ValueError("arquivo mudo")
    thr = max(10 ** (-40 / 20), pk * 0.05)
    on = int(np.argmax(a > thr))
    lead = int(0.010 * SR)
    x = x[on - lead:] if on >= lead else np.vstack([np.zeros((lead - on, 2)), x])
    fim = len(x) - int(np.argmax(np.abs(x[::-1]).max(axis=1) > pk * 1e-3))     # corta a cauda abaixo de −60 dB do pico
    x = x[: min(len(x), fim + int(0.05 * SR))].copy()
    m = min(len(x), int(0.002 * SR)); x[:m] *= np.linspace(0, 1, m)[:, None]
    m = min(len(x), int(0.020 * SR)); x[-m:] *= np.linspace(1, 0, m)[:, None]
    alvo = alvo if alvo is not None else (ALVO_CAMA if cama else ALVO_CURTO)
    ganho = alvo - momentaneo_max(x)
    tp = pico_verdadeiro(x)
    if tp + ganho > TETO_TP:
        ganho = TETO_TP - tp
    x = x * 10 ** (ganho / 20)
    info = dict(dur_s=round(len(x) / SR, 3), pico_ms=pico_ms(x), lufs_m=round(momentaneo_max(x), 1),
                tp=round(pico_verdadeiro(x), 1), alvo=alvo, cama=bool(cama))
    return x, info


def grava(path, x):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(x, -1, 1).astype(np.float32), SR, subtype="PCM_16")


# ───────────────────────── catálogo ─────────────────────────
def le_catalogo(destino) -> dict:
    f = Path(destino) / "catalogo.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8")).get("arquivos", {})
    return {}


def escreve_catalogo(destino, novos: dict) -> dict:
    """Junta `novos` ao catalogo.json, tira o que não existe mais e refaz o CATALOGO.md."""
    destino = Path(destino)
    arq = le_catalogo(destino)
    arq.update(novos)
    arq = {k: v for k, v in sorted(arq.items()) if (destino / k).exists()}
    padrao = {"formato": "WAV 48 kHz estéreo 16 bits", "inicio": "~10 ms antes do transiente",
              "alvo_curto_lufs_m": ALVO_CURTO, "alvo_cama_lufs_m": ALVO_CAMA, "teto_dbtp": TETO_TP,
              "sincronia": "at = evento − pico_ms/1000"}
    (destino / "catalogo.json").write_text(json.dumps({"versao": 1, "padrao": padrao, "arquivos": arq},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    por_cat: dict[str, list] = {}
    for k, v in arq.items():
        por_cat.setdefault(v.get("categoria", "avulsos"), []).append((k, v))
    linhas = ["# Catálogo da biblioteca de efeitos", "",
              "> Gerado por `scripts/som/nivelar.py` · não editar à mão", "",
              f"**Resumo:** {len(arq)} efeitos em {len(por_cat)} categorias, todos no padrão da casa: WAV 48 kHz estéreo, "
              f"~10 ms antes do transiente, pico momentâneo em {ALVO_CURTO:g} LUFS (camas {ALVO_CAMA:g}), pico verdadeiro "
              f"≤ {TETO_TP:g} dBTP. Sincronia: `at = evento − pico_ms/1000`. ¹ = parou no teto de pico antes do alvo.", ""]
    for cat in sorted(por_cat):
        linhas += [f"## {cat}", "", "| Arquivo | Duração (s) | Pico no arquivo (ms) | M máx (LUFS) | Pico (dBTP) | Origem |",
                   "|---|---:|---:|---:|---:|---|"]
        for k, v in por_cat[cat]:
            nota = "¹" if v.get("lufs_m", 0) < v.get("alvo", 0) - 0.5 else ""
            linhas.append(f"| `{k}` | {v.get('dur_s', '')} | {v.get('pico_ms', '')} | {v.get('lufs_m', '')}{nota} | "
                          f"{v.get('tp', '')} | {v.get('origem', '')} |")
        linhas.append("")
    (destino / "CATALOGO.md").write_text("\n".join(linhas), encoding="utf-8")
    return arq


# ───────────────────────── execução ─────────────────────────
def _processa(job):
    src, dst, rel_origem, categoria, cama = job
    try:
        x = decodifica(src)
        if len(x) < 100:
            return None
        dur = len(x) / SR
        cat = categoria or categoria_por_nome(rel_origem, dur)
        e_cama = cama if cama is not None else (cat in CAMAS or any(p in slug(rel_origem) for p in PALAVRAS_CAMA))
        y, info = nivela(x, e_cama)
        if dst is None:
            return dict(src=src, y=y, info=info, cat=cat, rel_origem=rel_origem)
        grava(dst, y)
        return dict(dst=dst, info=info, cat=cat, rel_origem=rel_origem)
    except Exception as ex:  # noqa: BLE001
        return dict(erro=f"{rel_origem}: {ex}")


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Nivela uma pasta de efeitos sonoros no padrão da casa e escreve o catálogo.")
    ap.add_argument("origem", help="pasta com os efeitos (subpastas valem como categoria)")
    ap.add_argument("--destino", default=str(SFX), help=f"biblioteca de saída (padrão: {Path(SFX).relative_to(RAIZ) if Path(SFX).is_relative_to(RAIZ) else SFX})")
    ap.add_argument("--categoria", help="força a categoria de todos os arquivos (ex.: whoosh, clique, impacto)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cama", action="store_true", help="trata todos como cama (alvo −24 LUFS)")
    g.add_argument("--curto", action="store_true", help="trata todos como efeito curto (alvo −20 LUFS)")
    ap.add_argument("--max-dur", type=float, default=30.0, help="pula arquivos mais longos que isso, em s (músicas no pack)")
    a = ap.parse_args()
    origem, destino = Path(a.origem).resolve(), Path(a.destino).resolve()
    if not origem.is_dir():
        raise SystemExit(f"pasta não encontrada: {origem}")
    no_lugar = origem == destino or destino in origem.parents
    cama = True if a.cama else (False if a.curto else None)
    antigos = le_catalogo(destino)
    jobs, usados, pulados = [], set(), 0
    for f in sorted(origem.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in AUDIO or f.name.endswith(".tmp.wav"):
            continue
        if no_lugar:
            rel = f.relative_to(destino).as_posix()
            ant = antigos.get(rel, {})
            jobs.append((f, None, rel, a.categoria or ant.get("categoria") or None, cama if cama is not None else ant.get("cama")))
            continue
        try:
            dur = float(sf.info(str(f)).duration)
        except Exception:  # noqa: BLE001 — mp3 e outros: deixa o ffmpeg decidir
            dur = 0.0
        if dur > a.max_dur:
            pulados += 1
            continue
        jobs.append((f, "?", f.relative_to(origem).as_posix(), a.categoria, cama))
    if not no_lugar:   # nome final: <categoria>/<slug>.wav, sem sobrescrever arquivo de outra origem
        resolvidos = []
        for src, _, rel, cat, cm in jobs:
            c = cat or categoria_por_nome(rel, 0.5)
            nome, k = slug(src.stem), 2
            alvo = f"{c}/{nome}.wav"
            while alvo in usados or (alvo in antigos and antigos[alvo].get("origem") != f"{origem.name}/{rel}"):
                alvo = f"{c}/{nome}-{k}.wav"; k += 1
            usados.add(alvo)
            resolvidos.append((src, destino / alvo, rel, cat, cm))
        jobs = resolvidos
    with ThreadPoolExecutor(6) as ex:
        res = [r for r in ex.map(_processa, jobs) if r]
    novos, erros = {}, [r["erro"] for r in res if "erro" in r]
    for r in res:
        if "erro" in r:
            continue
        if no_lugar:
            grava(r["src"], r["y"])
            rel = r["rel_origem"]
            origem_txt = antigos.get(rel, {}).get("origem", "nivelado no lugar")
        else:
            dst = Path(r["dst"])
            if r["cat"] != dst.parent.name:      # categoria corrigida pela duração (whoosh → whoosh-grande)
                novo = destino / r["cat"] / dst.name
                novo.parent.mkdir(parents=True, exist_ok=True)
                dst.replace(novo); dst = novo
            rel = dst.relative_to(destino).as_posix()
            origem_txt = f"{origem.name}/{r['rel_origem']}"
        novos[rel] = dict(categoria=r["cat"], origem=origem_txt, **r["info"])
    for d in destino.rglob("*"):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    cat = escreve_catalogo(destino, novos)
    teto = sum(1 for v in novos.values() if v["lufs_m"] < v["alvo"] - 0.5)
    print(f"nivelados {len(novos)} em {destino} ({teto} pararam no teto de pico, normal em cliques e teclas)"
          + (f"; pulados {pulados} longos demais (> {a.max_dur:g} s)" if pulados else ""))
    print(f"catálogo: {len(cat)} efeitos → {destino / 'catalogo.json'} e CATALOGO.md")
    for e in erros:
        print("  erro:", e)


if __name__ == "__main__":
    main()
