"""som.py — o som de um vídeo em um comando, sem esperar o render.

Qualquer motor de animação serve (After Effects, HyperFrames, Remotion, edição à mão): ele só precisa exportar a lista
de eventos, um por elemento que entra, sai ou bate na tela.

  uv run scripts/som/som.py --eventos 04-projetos/meu-video/audio/eventos.json
  uv run scripts/som/som.py --eventos eventos.json --voz voz.wav --musica musica.wav --video render/previa.mp4
  uv run scripts/som/som.py --eventos eventos.json --musica musica.wav --tom Am --drop 12.4   # vídeo só com música
  uv run scripts/som/som.py --eventos eventos.json --mapa meu_mapa.py                        # sons próprios por tipo

eventos.json = lista de {"t": segundos, "tipo": "clique", "vol": 1.0 (opcional), "pan": -1..1 (opcional),
"som": "whoosh/whoosh-2" (opcional, escolhe o arquivo)}; ou {"dur": 30.0, "eventos": [...]}.
Tipos aceitos: ver FAMILIAS em mapa_padrao.py (clique, pop, whoosh, transicao, impacto, logo, notificacao,
digitacao, riser, sucesso, glitch…). Tipo sem som padrão aparece no relatório.

Saída, na pasta do eventos.json (ou --saida): mix.wav, escuta/{voz,musica,efeitos,tonais}.wav (para ouvir cada camada),
relatorio-som.json, e com --video o <video>-som.mp4 (imagem copiada, só troca o som: remux).
"""
import argparse, importlib.util, json, subprocess, sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from mesa import Mesa  # noqa: E402


def duracao(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(f)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise SystemExit(f"não consegui ler a duração de {f} (o ffprobe está no PATH?)")


def carrega_mapa(f):
    """Arquivo .py com MAPA = {"tipo": funcao(M, e)}: sons próprios do projeto por cima do mapa padrão."""
    spec = importlib.util.spec_from_file_location("mapa_projeto", f)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not isinstance(getattr(mod, "MAPA", None), dict):
        raise SystemExit(f"{f} precisa definir MAPA = {{'tipo': lambda M, e: M.poe('pop', e['t'], -12)}}")
    return mod.MAPA


def main():
    for fluxo in (sys.stdout, sys.stderr):   # Windows: console em cp1252 quebra os acentos
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Monta o som do vídeo a partir da lista de eventos: efeitos, voz, música, master e relatório.")
    ap.add_argument("--eventos", required=True, help="eventos.json (lista de {t, tipo, vol?})")
    ap.add_argument("--voz", help="narração (wav, mp3…)")
    ap.add_argument("--voz-entra", type=float, default=0.0, help="segundo do vídeo em que a voz começa")
    ap.add_argument("--musica", help="trilha (wav, mp3…)")
    ap.add_argument("--musica-entra", type=float, default=0.0, help="segundo do vídeo em que a música começa")
    ap.add_argument("--musica-de", type=float, default=0.0, help="segundo da música por onde começar")
    ap.add_argument("--video", action="append", help="vídeo(s) para colar o som (gera <video>-som.mp4)")
    ap.add_argument("--saida", help="caminho do mix (padrão: mix.wav na pasta do eventos.json)")
    ap.add_argument("--dur", type=float, help="duração em s (padrão: 'dur' do eventos.json, o vídeo, a voz ou o último evento + 2 s)")
    ap.add_argument("--tom", help="tom da música para os tonais (ex.: Am, F#, Bb); sem tom, não há tonais")
    ap.add_argument("--drop", type=float, action="append", default=[], help="instante do drop (respiro seco antes); pode repetir")
    ap.add_argument("--impacto", type=float, nargs=2, action="append", default=[], metavar=("T0", "T1"),
                    help="trecho em que a música sobe ao nível da voz; pode repetir")
    ap.add_argument("--lufs", type=float, help="loudness final (padrão: −14 com voz ou música; −25 só com efeitos)")
    ap.add_argument("--pico", type=float, help="teto de pico verdadeiro em dBTP (padrão: −1; −3 só com efeitos)")
    ap.add_argument("--fx", type=float, help="efeitos em LUFS relativos à voz (ex.: −10); padrão: ganhos do mapa")
    ap.add_argument("--mapa", help="arquivo .py com MAPA = {tipo: f(M, e)} para sons próprios do projeto")
    a = ap.parse_args()

    t0 = time.time()
    ev_f = Path(a.eventos).resolve()
    if not ev_f.exists():
        raise SystemExit(f"não achei {ev_f}")
    dados = json.loads(ev_f.read_text(encoding="utf-8"))
    lista = dados if isinstance(dados, list) else (dados.get("eventos") or dados.get("events") or [])
    saida = Path(a.saida).resolve() if a.saida else ev_f.parent / "mix.wav"
    videos = [Path(v).resolve() for v in (a.video or [])]
    for v in videos + [Path(x) for x in (a.voz, a.musica) if x]:
        if not v.exists():
            raise SystemExit(f"não achei {v}")
    dur = a.dur or (dados.get("dur") if isinstance(dados, dict) else None)
    if not dur and videos:
        dur = duracao(videos[0])
    if not dur and a.voz:
        dur = a.voz_entra + duracao(a.voz) + 0.5
    if not dur:
        dur = max([float(e["t"]) for e in lista] + [0.0]) + 2.0

    M = Mesa(dur=dur, pasta=saida.parent, tom=a.tom)
    if not M.bib:
        raise SystemExit(f"a biblioteca de efeitos está vazia ({M.bib.raiz}): rode antes  uv run scripts/som/sintetizar_sfx.py")
    if a.voz:
        M.voz(Path(a.voz).resolve(), entra=a.voz_entra)
    if a.musica:
        M.musica(Path(a.musica).resolve(), entra=a.musica_entra, de=a.musica_de, fade_out=1.0)
    M.eventos(lista, sobrepor=carrega_mapa(a.mapa) if a.mapa else None)
    print(f"{len(lista)} eventos, {dur:.2f} s" + (f", tom {a.tom}" if a.tom else "") + (", com voz" if a.voz else "")
          + (", com música" if a.musica else ""))
    rel = M.mixar(saida.name, lufs=a.lufs, pico_max=a.pico, drops=a.drop, impactos=[tuple(x) for x in a.impacto], fx_rel=a.fx)
    for v in videos:
        out = v.with_name(v.stem + "-som.mp4")
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-i", str(saida), "-map", "0:v:0", "-map", "1:a:0",
                            "-c:v", "copy", "-af", "apad", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                            str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"falhou ao colar o som em {v.name}: {r.stderr[-800:]}")
        rel.setdefault("videos", []).append(str(out))
        print("som colado:", out)
    (saida.parent / "relatorio-som.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"mix: {saida}\nrelatório: {saida.parent / 'relatorio-som.json'}\npronto em {time.time() - t0:.0f} s"
          + ("" if rel["avisos"] else " (sem avisos)"))


if __name__ == "__main__":
    main()
