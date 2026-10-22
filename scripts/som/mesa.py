"""mesa.py — motor de som dos vídeos. Tudo que cada mixador de projeto reescreveria do zero:

    import sys; sys.path.insert(0, "scripts/som"); from mesa import Mesa
    M = Mesa(dur=62.0, pasta="04-projetos/meu-video/audio", tom="Am")   # tom opcional: "A", "Am", "F#m"… ou [(0, 11.2, "Bm"), (11.2, 62, "F")]
    M.voz("voz.wav", entra=0.85)          # narração (sem voz = vídeo musical)
    M.musica("musica.wav")                # trilha; várias chamadas = trechos; devolve o trecho para mexer
    M.eventos("eventos.json")             # um som para cada evento, pelo mapa padrão (mapa_padrao.py) + o que o projeto sobrepor
    M.poe("impacto", 12.4, -10)           # efeito avulso: categoria da biblioteca, "categoria/arquivo" ou caminho
    M.golpe(12.4, -20)                    # tonal sintetizado no tom do instante (só quando há tom)
    M.mixar(drops=[12.4])                 # mix.wav + escuta/{voz,musica,efeitos,tonais}.wav + relatorio-som.json

Regras de origem (números: 06-metodo/regras.md): efeito com o pico no instante do evento (at = evento − pico_ms/1000);
música ~15 dB abaixo da voz na fala, −9 nos respiros, +2 nos trechos só de música, vão seco antes do drop; sem voz,
a trilha é nivelada a −19 LUFS e os efeitos sobem ×2,2; bus de efeitos −3 dB em 3,2 kHz e sidechain pela voz (−4 dB);
master −14 LUFS e pico verdadeiro ≤ −1 dBTP (limitador a 4× para pegar o pico entre amostras). Peça só de efeitos
(som de cena, sem voz nem música): −25 LUFS e pico ≤ −3, nunca −14.
A biblioteca de efeitos é a pasta SFX do estúdio (05-biblioteca/som/sfx): uma subpasta por categoria e o
catalogo.json do nivelar.py com o pico de cada arquivo.
"""
import json, re, subprocess, sys
from pathlib import Path

import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import fftconvolve, lfilter, butter, sosfilt

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent)); sys.path.insert(0, str(AQUI))
from _estudio import SFX  # noqa: E402

NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BEMOL = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
PENTA = {"maior": [0, 2, 4, 7, 9], "menor": [0, 3, 5, 7, 10]}
# categoria que falta na biblioteca → a mais parecida que costuma existir
RESERVA = {"whoosh-grande": ["whoosh"], "carimbo": ["impacto", "pouso"], "logo": ["impacto", "pop"], "pouso": ["impacto"],
           "papel": ["whoosh"], "obturador": ["clique"], "contador": ["tecla", "clique"], "relogio": ["contador", "clique"],
           "sucesso": ["notificacao", "brilho"], "caneta": ["papel"], "rolagem": ["tecla", "clique"], "fita": ["papel", "whoosh"],
           "glitch": ["clique"], "brilho": ["notificacao", "sucesso"], "digitacao": ["tecla"], "tecla": ["clique"],
           "notificacao": ["pop"], "riser": ["whoosh-grande"]}
db = lambda g: 10 ** (g / 20)


def _tom(s):
    """'F#m' → ('F#', 'menor'); 'Ab' → ('G#', 'maior')."""
    menor = s.endswith("m") and len(s) > 1
    n = s[:-1] if menor else s
    n = n[0].upper() + n[1:]
    n = BEMOL.get(n, n)
    if n not in NOTAS:
        raise ValueError(f"tom desconhecido: {s} (use A, Am, F#m, Bb…)")
    return n, ("menor" if menor else "maior")


class Biblioteca:
    """Efeitos da pasta SFX: catalogo.json do nivelar.py (pico de cada arquivo) ou, sem catálogo, os WAV soltos."""

    def __init__(self, raiz=SFX):
        self.raiz = Path(raiz)
        cat = self.raiz / "catalogo.json"
        arq = json.loads(cat.read_text(encoding="utf-8")).get("arquivos", {}) if cat.exists() else {}
        if not arq and self.raiz.exists():
            arq = {p.relative_to(self.raiz).as_posix(): {} for p in sorted(self.raiz.rglob("*.wav"))}
        self.info, self.por_cat = {}, {}
        for rel, inf in sorted(arq.items()):
            if (self.raiz / rel).exists():
                c = inf.get("categoria") or self.categoria_de(rel)
                self.info[rel] = inf
                self.por_cat.setdefault(c, []).append(rel)

    @staticmethod
    def categoria_de(rel):
        partes = rel.split("/")
        return partes[0] if len(partes) > 1 else re.sub(r"[-_ ]?\d+$", "", Path(rel).stem)

    def __bool__(self):
        return bool(self.info)


class Mesa:
    def __init__(self, dur, sr=48000, tom=None, pasta=None, sfx=None):
        self.sr, self.dur = sr, float(dur)
        self.n = int(self.dur * sr)
        self.pasta = Path(pasta or ".")
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.tons = [(0.0, 1e9, tom)] if isinstance(tom, str) else (tom or [])
        for _, _, s in self.tons:
            if s:
                _tom(s)
        cauda = sr * 8
        self.bus = {k: np.zeros((2, self.n + cauda)) for k in ("sfx", "ton", "sala", "direto")}   # direto: sem curva, EQ nem duck (demos A/B no mesmo volume)
        self.vz = None
        self.mus = np.zeros((2, self.n))
        self._cache, self._cont, self.sem_som, self.faltou = {}, {}, {}, {}
        self.bib = Biblioteca(sfx or SFX)
        self.meter = pyln.Meter(sr)

    # ───────────────────────── utilidades ─────────────────────────
    def tom(self, t):
        for a, b, s in self.tons:
            if a <= t < b and s:
                return _tom(s)
        return None

    def escala(self, t):
        """Semitons da pentatônica do tom no instante t (relativos à tônica)."""
        tm = self.tom(t)
        return PENTA[tm[1]] if tm else PENTA["maior"]

    def prox(self, chave):
        self._cont[chave] = self._cont.get(chave, -1) + 1
        return self._cont[chave]

    def degrau(self, chave, t):
        """Próxima nota da pentatônica (sobe a cada chamada): escadas de sino no tom do trecho."""
        e = self.escala(t)
        return e[self.prox(chave) % len(e)]

    def _caminho(self, f):
        p = Path(f)
        if p.is_absolute() or p.exists():
            return p
        return self.pasta / p if (self.pasta / p).exists() else p

    def arquivo(self, som):
        """'whoosh' → próxima variação da categoria; 'whoosh/whoosh-2' → aquele arquivo da biblioteca; caminho → ele mesmo.
        Devolve (caminho, pico_ms do catálogo ou None)."""
        s = str(som)
        if isinstance(som, Path) or Path(s).suffix.lower() in (".wav", ".mp3", ".flac", ".ogg", ".aif", ".aiff"):
            p = self._caminho(som)
            if not p.exists() and (self.bib.raiz / s).exists():
                p = self.bib.raiz / s
            if not p.exists():
                raise FileNotFoundError(f"efeito não encontrado: {som}")
            return p, None
        if "/" in s:
            rel = s if s.endswith(".wav") else s + ".wav"
            if rel not in self.bib.info:
                raise KeyError(f"efeito '{s}' não está na biblioteca ({self.bib.raiz})")
            return self.bib.raiz / rel, self.bib.info[rel].get("pico_ms")
        for c in [s] + RESERVA.get(s, []):
            if self.bib.por_cat.get(c):
                if c != s:
                    self.faltou[s] = c
                lista = self.bib.por_cat[c]
                rel = lista[self.prox("cat-" + c) % len(lista)]
                return self.bib.raiz / rel, self.bib.info[rel].get("pico_ms")
        raise KeyError(f"categoria '{s}' sem arquivos na biblioteca ({self.bib.raiz}): rode sintetizar_sfx.py ou nivelar.py")

    def carrega(self, f, ini=0.0, fim=None, st=0):
        k = (str(f), ini, fim, st)
        if k not in self._cache:
            try:
                y, sr = sf.read(str(f), always_2d=True)
                y = y.T
            except RuntimeError:
                y, sr = None, None
            if y is None or sr != self.sr:          # mp3, outra taxa: o ffmpeg converte
                y = self._ler(f, 2)
            if y.shape[0] == 1:
                y = np.vstack([y, y])
            y = y[:2, int(ini * self.sr): int(fim * self.sr) if fim else None]
            if st:   # muda a altura (e a duração) reamostrando, como um sampler
                import librosa
                y = np.vstack([librosa.resample(c, orig_sr=self.sr * 2 ** (st / 12), target_sr=self.sr) for c in y])
            m = min(y.shape[1], int(0.006 * self.sr))
            if ini > 0 and m:
                y[:, :m] *= np.linspace(0, 1, m)
            self._cache[k] = y
        return self._cache[k]

    def _pico(self, y):
        """Instante do pico do envelope de 5 ms (o mesmo critério do catálogo), em amostras."""
        n = int(0.005 * self.sr)
        return int(np.argmax(np.convolve(y.mean(axis=0) ** 2, np.ones(n) / n, mode="same")))

    # ───────────────────────── efeitos ─────────────────────────
    def poe(self, som, t, g=-12.0, pan=0.0, alinha="pico", off=0.0, ini=0.0, fim=None, st=0, fade=None, fade_in=None,
            bus="sfx", pico_em=None, sala=False):
        """Põe um som com o PICO no instante t (alinha='ini': começo em t; 'fim': fim em t; pico_em: segundo do arquivo que cai em t).
        g em dB sobre a biblioteca nivelada; st = semitons (muda a altura e a duração)."""
        f, pico_ms = self.arquivo(som)
        y = self.carrega(f, ini, fim, st).copy()
        if fade_in:
            m = min(y.shape[1], int(fade_in * self.sr)); y[:, :m] *= np.linspace(0, 1, m)
        if fade:
            m = min(y.shape[1], int(fade * self.sr)); y[:, -m:] *= np.linspace(1, 0, m)
        if pico_em is not None:
            a = int((t + off - (pico_em - ini)) * self.sr)
        elif alinha == "pico":
            p = int(pico_ms / 1000 * self.sr) if pico_ms is not None and not ini and not st else self._pico(y)
            a = int((t + off) * self.sr) - p
        elif alinha == "fim":
            a = int((t + off) * self.sr) - y.shape[1]
        else:
            a = int((t + off) * self.sr)
        if a < 0:
            y, a = y[:, -a:], 0
        B = self.bus[bus]
        L, R = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        s = y[:, : max(0, B.shape[1] - a)] * db(g)
        B[0, a:a + s.shape[1]] += s[0] * L * 1.4142
        B[1, a:a + s.shape[1]] += s[1] * R * 1.4142
        if sala:
            self.bus["sala"][:, a:a + s.shape[1]] += s

    def _freq(self, t, semitons=0, oitava=5):
        tm = self.tom(t) or ("C", "maior")
        i = NOTAS.index(tm[0]) + semitons + 12 * (oitava - 4) - 9
        return 440.0 * 2 ** (i / 12), tm[1] == "menor"

    def _poe_tonal(self, y, t, lufs, pan=0.0, alinha="ini", fade=None):
        """Coloca um tonal sintetizado (n, 2) pelo pico momentâneo em `lufs`."""
        y = np.asarray(y, float).T
        if fade:
            m = min(y.shape[1], int(fade * self.sr)); y[:, -m:] *= np.linspace(1, 0, m)
        g = lufs - self._pico_curto(y)
        a = int(t * self.sr) - (self._pico(y) if alinha == "pico" else 0)
        if a < 0:
            y, a = y[:, -a:], 0
        B = self.bus["ton"]
        L, R = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        s = y[:, : max(0, B.shape[1] - a)] * db(g)
        B[0, a:a + s.shape[1]] += s[0] * L * 1.4142
        B[1, a:a + s.shape[1]] += s[1] * R * 1.4142

    def tonal(self, t, lufs=-30.0, timbre="sino", grau=None, oitava=5, pan=0.0, dur=1.4, chave="tonal"):
        """Nota no tom do instante (sino macio ou pad curto). Sem tom, não toca: tonal é opcional.
        grau = semitons sobre a tônica; None = próxima nota da pentatônica a cada chamada com a mesma `chave`."""
        if self.tom(t) is None:
            return
        import sintetizar_sfx as S
        st = self.degrau(chave, t) if grau is None else grau
        f, menor = self._freq(t, st, oitava if timbre == "sino" else 3)
        if timbre == "pad":
            y = S.pad([f, f * 1.5, f * 2], dur)
        else:
            y = S.sala(S.nota_sino(f, dur), secs=1.0, mix=0.22)
        self._poe_tonal(y, t, lufs, pan, fade=0.4)

    def golpe(self, t, lufs=-22.0, oitava=2, off=0.0):
        """Golpe tonal (acorde + sub + cauda) no tom do instante, pico momentâneo em `lufs`. Sem tom, não toca."""
        if self.tom(t) is None:
            return
        import sintetizar_sfx as S
        f, menor = self._freq(t, 0, oitava)
        self._poe_tonal(S.golpe_tonal(f, menor), t + off, lufs, alinha="pico", fade=0.8)

    def textura(self, t0, t1, lufs=-31.0):
        """Cama tonal contínua de t0 a t1 no tom de t0 (drone de raiz, quinta e oitava). Sem tom, não toca."""
        if self.tom(t0) is None:
            return
        import sintetizar_sfx as S
        f, _ = self._freq(t0, 0, 3)
        y = np.asarray(S.pad([f, f * 1.5, f * 2], t1 - t0), float).T
        a = int(t0 * self.sr); B = self.bus["ton"]
        m = min(y.shape[1], B.shape[1] - a)
        B[:, a:a + m] += y[:, :m] * db(lufs - self.meter.integrated_loudness(y.T))

    def riser(self, t_pico, g=-14.0, pan=0.0):
        """Riser da biblioteca terminando no instante (drop, corte, revelação)."""
        self.poe("riser", t_pico, g, pan)

    def _pico_curto(self, y):
        m = self._momentanea(y, 0.05, 0.4)
        return float(m.max()) if len(m) else -70.0

    def eventos(self, arquivo="eventos.json", sobrepor=None, sem_padrao=False):
        """Efeitos de todos os eventos. Aceita lista [{t, tipo, vol?, pan?, som?, ganho?}] ou {"dur": s, "eventos": [...]}.
        `som` no evento escolhe o efeito direto (categoria, "categoria/arquivo" ou caminho). `sobrepor` = {tipo: f(M, e)}."""
        from mapa_padrao import tocar
        if isinstance(arquivo, (str, Path)):
            dados = json.loads(self._caminho(arquivo).read_text(encoding="utf-8"))
        else:
            dados = arquivo
        lista = dados if isinstance(dados, list) else (dados.get("eventos") or dados.get("events") or [])
        sobrepor = sobrepor or {}
        for e in lista:
            e = dict(e); e["tipo"] = str(e.get("tipo") or e.get("kind") or "").strip().lower()
            e["t"] = float(e["t"])
            k = e["tipo"]
            try:
                if k in sobrepor:
                    sobrepor[k](self, e)
                elif e.get("som"):
                    g = float(e.get("ganho", -12.0)) + 20 * np.log10(max(float(e.get("vol", 1.0)), 0.05))
                    self.poe(e["som"], e["t"], g, float(e.get("pan", 0.0)) * 0.6)
                elif sem_padrao or not tocar(self, e):
                    self.sem_som[k or "(sem tipo)"] = self.sem_som.get(k or "(sem tipo)", 0) + 1
            except (KeyError, FileNotFoundError) as ex:
                self.sem_som[f"{k} ({ex.args[0]})"] = self.sem_som.get(f"{k} ({ex.args[0]})", 0) + 1
        return lista

    # ───────────────────────── voz e música ─────────────────────────
    def _ler(self, f, ch=1, filtro=None):
        cmd = ["ffmpeg", "-v", "error", "-i", str(f)] + (["-af", filtro] if filtro else []) + \
              ["-f", "f32le", "-ac", str(ch), "-ar", str(self.sr), "-"]
        raw = subprocess.run(cmd, capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).copy()
        return x.reshape(-1, ch).T if ch > 1 else x

    def voz(self, arquivo, entra=0.0, lufs=-16.0, compressor=True, passa_alta=70):
        """Narração seca: passa-alta + compressor leve, nivelada a `lufs` antes do master."""
        f = self._caminho(arquivo)
        af = f"highpass=f={passa_alta}" + (",acompressor=threshold=-20dB:ratio=3:attack=5:release=120" if compressor else "")
        v = self._ler(f, 1, af)
        self.vz = np.zeros(self.n, np.float32)
        a = int(entra * self.sr); m = max(0, min(len(v), self.n - a))
        self.vz[a:a + m] = v[:m]
        self.vz *= db(lufs - self._integrada(self.vz))
        self.voz_lufs = lufs
        return self.vz

    def musica(self, arquivo, entra=0.0, de=0.0, ate=None, ganho=0.0, fade_in=0.0, fade_out=0.0):
        """Põe um trecho de música (arquivo ou array 2×n) em `entra`. Devolve a fatia colocada (para filtros do projeto)."""
        if isinstance(arquivo, np.ndarray):
            y = np.atleast_2d(arquivo)
        else:
            y = self._ler(self._caminho(arquivo), 2)
        y = y[:, int(de * self.sr): int(ate * self.sr) if ate else None] * db(ganho)
        a = int(entra * self.sr); m = max(0, min(y.shape[1], self.n - a))
        y = y[:, :m].copy()
        if fade_in:
            k = min(m, int(fade_in * self.sr)); y[:, :k] *= np.linspace(0, 1, k)
        if fade_out:
            k = min(m, int(fade_out * self.sr)); y[:, -k:] *= np.linspace(1, 0, k)
        self.mus[:, a:a + m] += y
        return self.mus[:, a:a + m]

    # ───────────────────────── medidas ─────────────────────────
    def _kpond(self, x):
        b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585]
        b2, a2 = [1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621]
        return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)

    def _momentanea(self, x, passo=0.05, janela=0.4):
        y = self._kpond(x)
        p = (y ** 2) if y.ndim == 1 else (y ** 2).sum(axis=0)
        c = np.concatenate([[0], np.cumsum(p)]); h, w = int(passo * self.sr), int(janela * self.sr)
        idx = np.arange(0, len(p), h)
        a, b = np.clip(idx - w // 2, 0, len(p)), np.clip(idx + w // 2, 0, len(p))
        return -0.691 + 10 * np.log10((c[b] - c[a]) / np.maximum(1, b - a) + 1e-12)

    def _integrada(self, x):
        m = self._momentanea(x, 0.1, 0.4); m = m[m > -70]
        if not len(m):
            return -70.0
        rel = 10 * np.log10(np.mean(10 ** (m / 10))) - 10; m = m[m > rel]
        return float(10 * np.log10(np.mean(10 ** (m / 10))))

    @staticmethod
    def _suaviza(g, ataque, solta, passo, rapido=None, t_rap=0.03):
        out = np.empty_like(g); v = g[0]
        for i, x in enumerate(g):
            tc = t_rap if rapido is not None and rapido[i] else (ataque if x < v else solta)
            v += (x - v) * (1 - np.exp(-passo / tc)); out[i] = v
        return out

    def _hall(self, secs=2.6):
        """Resposta de sala sintética (ruído estéreo com decaimento de −60 dB em `secs`), para o bus 'sala'."""
        n = int(secs * self.sr); t = np.arange(n) / self.sr
        r = np.random.default_rng(11)
        sos = butter(2, 6000 / (self.sr / 2), output="sos")
        ir = np.vstack([sosfilt(sos, r.standard_normal(n)) * np.exp(-t * 6.9 / secs) for _ in range(2)])
        ir = np.hstack([np.zeros((2, int(0.018 * self.sr))), ir])
        return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))

    # ───────────────────────── mixagem ─────────────────────────
    def _curva_musica(self, sob_voz, respiro, so_musica, drops, impactos):
        """Ganho da música pela voz: −15 dB na fala, −9 nos respiros curtos, +2 nos trechos só de música (≥ 2,5 s),
        trilha mais baixa na frase antes de cada drop e no nível da voz nos impactos."""
        P, V = 0.05, self.voz_lufs
        fala = self._momentanea(self.vz, P, 0.2) > V - 22
        fh = fala.copy(); ult = -10 ** 9
        for i in range(len(fala)):
            if fala[i]: ult = i
            fh[i] = i - ult <= int(0.7 / P)
        som_ = np.zeros_like(fh); i = 0
        while i < len(fh):
            if not fh[i]:
                j = i
                while j < len(fh) and not fh[j]: j += 1
                if (j - i) * P >= 2.5: som_[i:j] = True
                i = j
            else:
                i += 1
        pre = []
        for D in drops:
            u = max((k for k in range(int((D - 4) / P), int(D / P)) if 0 <= k < len(fala) and fala[k]), default=int((D - 0.75) / P))
            a, b = min(u + 2, int((D - 0.75) / P)), int(D / P); fh[a:b] = False; som_[a:b] = False; pre.append((a, b))
        for a, b in impactos:
            fh[int(a / P):int(b / P)] = False
        alvo = np.where(fh, V + sob_voz, np.where(som_, V + so_musica, V + respiro))
        for a, b in pre: alvo[a:b] = V - 6
        for a, b in impactos: alvo[int(a / P):int(b / P)] = V
        rap = np.zeros(len(alvo), bool)
        for D in list(drops) + [a for a, _ in impactos]: rap[max(0, int((D - 0.8) / P)):int((D + 0.25) / P)] = True
        alvo = self._suaviza(alvo, 0.25, 0.9, P, rap)
        mm = self._momentanea(self.mus, P, 3.0)
        i = 0
        while i < len(som_):
            if som_[i]:
                j = i
                while j < len(som_) and som_[j]: j += 1
                a, b = i * int(P * self.sr), min(self.n, j * int(P * self.sr))
                if b - a > self.sr: mm[i:j] = self._integrada(self.mus[:, a:b])
                i = j
            else:
                i += 1
        for a, b in pre:
            if b > a: mm[a:b] = self._integrada(self.mus[:, a * int(P * self.sr):b * int(P * self.sr)])
        n_ = min(len(mm), len(alvo))
        g = np.clip(alvo[:n_] - mm[:n_], -40, 6); g = np.where(mm[:n_] < -55, np.minimum(g, 0), g)
        g = self._suaviza(g, 0.12, 0.6, P, rap[:n_])
        return db(np.interp(np.arange(self.n) / self.sr, np.arange(n_) * P, g))

    def _vao_seco(self, drops):
        """Respiro antes do drop: −14 dB de D−0,32 a D−0,02, para o drop bater."""
        tt = np.arange(self.n) / self.sr
        c = np.ones(self.n)
        for D in drops:
            c *= np.interp(tt, [0, D - 0.42, D - 0.32, D - 0.03, D - 0.005, self.dur + 1], [1, 1, db(-14), db(-14), 1, 1])
        return c

    def _sidechain(self, voz, profundidade):
        """Ganho dos efeitos pela voz (abaixa até `profundidade` dB quando há fala), calculado a 1 kHz e interpolado."""
        sr, k = self.sr, 48
        env = np.convolve(np.abs(voz), np.ones(480) / 480, mode="same")[::k]
        nv = 20 * np.log10(env + 1e-9)
        fl = np.clip((nv - (self.voz_lufs - 29)) / 15, 0, 1); sol = np.exp(-k / (0.25 * sr))
        g = np.empty_like(fl); acc = 0.0
        for i, x in enumerate(fl):
            acc = x if x > acc else acc * sol + x * (1 - sol); g[i] = acc
        g = np.interp(np.arange(len(voz)), np.arange(len(g)) * k, g)
        return db(profundidade * g)

    def mixar(self, saida="mix.wav", lufs=None, pico_max=None, sob_voz=-15.0, respiro=-9.0, so_musica=2.0, drops=(),
              impactos=(), fx_rel=None, eq=(3200, -3.0), sidechain=-4.0, sala_db=-24.0, fade_fim=1.2,
              musica_automatica=True, musica_sem_voz=-19.0, fx_sem_voz=2.2, stems=True):
        """Soma voz, música e efeitos; grava `saida` e escuta/*.wav; devolve o relatório (e imprime).
        lufs/pico_max: None = −14 / −1 com voz ou música; −25 / −3 numa peça só de efeitos (som de cena).
        fx_rel: LUFS dos efeitos relativo à voz (ex.: −10); None = ganhos como escritos (biblioteca nivelada).
        Sem voz: a música vai a `musica_sem_voz` LUFS e os efeitos são multiplicados por `fx_sem_voz` antes do master."""
        sr, n = self.sr, self.n
        tt = np.arange(n) / sr
        B = self.bus
        tem_musica = bool(np.abs(self.mus).max() > 0)
        so_efeitos = self.vz is None and not tem_musica
        lufs = (-25.0 if so_efeitos else -14.0) if lufs is None else lufs
        pico_max = (-3.0 if so_efeitos else -1.0) if pico_max is None else pico_max
        sfx = B["sfx"].copy()
        if np.abs(B["sala"]).max() > 0:
            ir = self._hall()
            for c in range(2):
                sfx[c] += fftconvolve(B["sala"][c], ir[c])[: sfx.shape[1]] * db(sala_db)
        efe = sfx[:, :n]
        ton = B["ton"][:, :n].copy()
        voz = np.zeros(n) if self.vz is None else self.vz
        mus = self.mus.copy()
        k = 1.0
        if tem_musica and self.vz is not None and musica_automatica:
            mus *= self._curva_musica(sob_voz, respiro, so_musica, drops, impactos)[None]
        elif tem_musica and self.vz is None and musica_sem_voz is not None:
            mus *= db(musica_sem_voz - self._integrada(mus))     # faixa masterizada esconde os efeitos: nivela antes
            efe = efe * fx_sem_voz; ton = ton * fx_sem_voz
        if drops and tem_musica:
            mus *= self._vao_seco(drops)[None]
        fx = efe + ton
        if fx_rel is not None and self.vz is not None and np.abs(fx).max() > 0:
            at = self._momentanea(fx, 0.1, 0.4); lf = 10 * np.log10(np.mean(10 ** (at[at > -60] / 10)))
            k = db(self.voz_lufs + fx_rel - lf); efe = efe * k; ton = ton * k
        if eq:
            f0, g0 = eq; A = 10 ** (g0 / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / 2
            b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A]); a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
            efe = lfilter(b / a[0], a / a[0], efe, axis=1); ton = lfilter(b / a[0], a / a[0], ton, axis=1)
        if sidechain and self.vz is not None:
            duck = self._sidechain(voz, sidechain); efe = efe * duck[None]; ton = ton * duck[None]
        fim = np.interp(tt, [0, max(0.0, self.dur - fade_fim), self.dur], [1, 1, 0])[None]
        dir_ = B["direto"][:, :n]
        mix = (voz[None] + mus + efe + ton + dir_) * fim
        if not np.abs(mix).max() > 0:
            raise SystemExit("a mix ficou muda: nenhum evento tocou e não há voz nem música")
        gm = lufs - self.meter.integrated_loudness(mix.T)
        pasta = self.pasta
        pre = pasta / (Path(saida).stem + "-pre.wav")
        sf.write(pre, (mix * db(gm)).T.astype(np.float32), sr)
        out = pasta / saida
        g_ = 0.0
        lim = db(pico_max - 0.3)
        for _ in range(4):   # limitador a 4× (pico verdadeiro), sem atraso (latency=1), e ajuste do LUFS
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre), "-af",
                            f"volume={g_:.2f}dB,aresample=192000,alimiter=limit={lim:.3f}:level=false:attack=1.5:release=60:latency=1,aresample={sr}",
                            "-c:a", "pcm_f32le", str(out)], check=True)
            x, _ = sf.read(out); d = lufs - self.meter.integrated_loudness(x)
            if abs(d) < 0.05: break
            g_ += d
        pre.unlink(missing_ok=True)
        self.alvo = (lufs, pico_max)
        if stems:
            (pasta / "escuta").mkdir(exist_ok=True)
            kk = db(gm + g_) * fim
            for nome, s in (("voz", np.vstack([voz, voz])), ("musica", mus + dir_), ("efeitos", efe), ("tonais", ton)):
                p = pasta / "escuta" / f"{nome}.wav"
                if np.abs(s).max() > 0:
                    sf.write(p, (s * kk).T.astype(np.float32), sr)
                else:
                    p.unlink(missing_ok=True)
        return self.relatorio(out)

    def relatorio(self, out):
        x, _ = sf.read(out)
        r = subprocess.run(["ffmpeg", "-nostats", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        tp = re.findall(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", r)
        lufs, pico_max = getattr(self, "alvo", (-14.0, -1.0))
        rel = {"arquivo": str(out), "duracao_s": round(len(x) / self.sr, 2), "lufs": round(float(self.meter.integrated_loudness(x)), 1),
               "pico_verdadeiro_dbtp": float(tp[-1]) if tp else None, "alvo_lufs": lufs, "alvo_pico_dbtp": pico_max, "stems": {}}
        esc = self.pasta / "escuta"
        for nome in ("voz", "musica", "efeitos", "tonais"):
            p = esc / f"{nome}.wav"
            if p.exists():
                y, _ = sf.read(p); rel["stems"][nome] = round(float(self.meter.integrated_loudness(y)), 1)
        mb = None
        if (esc / "voz.wav").exists() and (esc / "musica.wav").exists():
            v, _ = sf.read(esc / "voz.wav"); m_, _ = sf.read(esc / "musica.wav")
            mv, mm = self._momentanea(v.T, 1.0, 3.0), self._momentanea(m_.T, 1.0, 3.0); k = mv > -35
            if k.any():
                mb = rel["musica_abaixo_da_voz_db"] = round(float(np.median((mv - mm)[k])), 1)
        if self.sem_som:
            rel["eventos_sem_som"] = self.sem_som
        if self.faltou:
            rel["categorias_substituidas"] = self.faltou
        avisos = []
        if abs(rel["lufs"] - lufs) > 0.5: avisos.append(f"LUFS {rel['lufs']} (alvo {lufs:g})")
        if rel["pico_verdadeiro_dbtp"] is not None and rel["pico_verdadeiro_dbtp"] > pico_max + 0.2:
            avisos.append(f"pico verdadeiro {rel['pico_verdadeiro_dbtp']} dBTP (teto {pico_max:g})")
        if mb is not None and not 12 <= mb <= 18: avisos.append(f"música {mb} dB abaixo da voz (regra ~15)")
        if self.sem_som: avisos.append(f"{sum(self.sem_som.values())} eventos sem som: {', '.join(self.sem_som)}")
        if self.faltou: avisos.append("categorias que faltam na biblioteca, trocadas: " + ", ".join(f"{a}→{b}" for a, b in self.faltou.items()))
        rel["avisos"] = avisos
        print(f"mix: {rel['lufs']} LUFS (alvo {lufs:g}), pico verdadeiro {rel['pico_verdadeiro_dbtp']} dBTP (teto {pico_max:g}); "
              f"stems {rel['stems']}" + (f"; música {mb} dB abaixo da voz" if mb is not None else ""))
        for a in avisos:
            print("  aviso:", a)
        (self.pasta / "relatorio-som.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
        return rel
