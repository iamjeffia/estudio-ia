#!/usr/bin/env python3
"""Corta as pausas da fala de um vídeo (ou áudio) com os tempos por palavra do faster-whisper + ffmpeg.

Transcreve a entrada, acha os buracos entre palavras seguidas maiores que --pausa segundos e tira esses
trechos (deixando --folga segundos de som de cada lado da fala). Corta e junta tudo numa única chamada do
ffmpeg. Nunca muda a velocidade.

Uso:
    uv run scripts/video/cut_pauses.py bruto.mp4 cortado.mp4 [--pausa 0.15] [--folga 0.02] [--modelo small]
    uv run scripts/video/cut_pauses.py --autoteste
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Acima deste número de trechos, o filter_complex vai para um arquivo temporário e entra pelo
# -filter_complex_script em vez da linha de comando (o Windows limita o tamanho da linha de comando;
# 200 trechos × ~2 filtros é uma margem segura antes disso).
MAX_TRECHOS_NA_LINHA = 200


def trechos_mantidos(palavras, limite_pausa, folga):
    """palavras: lista de (início, fim) em ordem cronológica.

    Devolve a lista de trechos [início, fim] mantidos: com `folga` segundos de cada lado da fala, partidos
    em todo buraco maior que limite_pausa, presos em 0 e unidos quando a folga os fez se sobrepor.
    """
    if not palavras:
        return []

    trechos = []
    ini = max(0.0, palavras[0][0] - folga)
    fim = palavras[0][1] + folga

    for (_, fim_ant), (prox_ini, prox_fim) in zip(palavras, palavras[1:]):
        if prox_ini - fim_ant > limite_pausa:
            trechos.append([ini, fim])
            ini = max(0.0, prox_ini - folga)
        fim = prox_fim + folga

    trechos.append([ini, fim])

    unidos = [trechos[0]]
    for s, e in trechos[1:]:
        if s <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], e)
        else:
            unidos.append([s, e])

    return unidos


def conta_pausas(palavras, limite_pausa):
    """Número de buracos entre palavras seguidas maiores que limite_pausa."""
    return sum(1 for (_, fim_ant), (prox_ini, _) in zip(palavras, palavras[1:]) if prox_ini - fim_ant > limite_pausa)


def transcreve_palavras(entrada, modelo, idioma):
    from faster_whisper import WhisperModel

    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segmentos, _info = m.transcribe(str(entrada), language=idioma or None, word_timestamps=True, vad_filter=True)

    palavras = []
    for seg in segmentos:
        for w in seg.words or []:
            palavras.append((w.start, w.end))
    return palavras


def sonda(caminho):
    """Duração e quais trilhas (vídeo/áudio) o arquivo tem, pelo ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(caminho)],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    dados = json.loads(out.stdout)
    tipos = {s.get("codec_type") for s in dados.get("streams", [])}
    return float(dados["format"]["duration"]), "video" in tipos, "audio" in tipos


def monta_filtro(trechos, tem_video):
    partes, rotulos = [], []
    for i, (s, e) in enumerate(trechos):
        if tem_video:
            partes.append(f"[0:v]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS[v{i}]")
        partes.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS[a{i}]")
        rotulos.append(f"[v{i}][a{i}]" if tem_video else f"[a{i}]")
    v = 1 if tem_video else 0
    saidas = "[outv][outa]" if tem_video else "[outa]"
    return ";".join(partes) + f";{''.join(rotulos)}concat=n={len(trechos)}:v={v}:a=1{saidas}"


def corta_e_junta(entrada, saida, trechos, tem_video):
    filtro = monta_filtro(trechos, tem_video)
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(entrada)]

    arq_filtro = None
    if len(trechos) > MAX_TRECHOS_NA_LINHA:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write(filtro)
        tmp.close()
        arq_filtro = tmp.name
        cmd += ["-filter_complex_script", arq_filtro]
    else:
        cmd += ["-filter_complex", filtro]

    if tem_video:
        cmd += ["-map", "[outv]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"]
    cmd += ["-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(saida)]

    try:
        subprocess.run(cmd, check=True)
    finally:
        if arq_filtro:
            Path(arq_filtro).unlink(missing_ok=True)


def roda(entrada, saida, pausa, folga, modelo, idioma):
    entrada, saida = Path(entrada), Path(saida)
    if not entrada.exists():
        sys.exit(f"erro: não achei o arquivo {entrada}")

    dur_entrada, tem_video, tem_audio = sonda(entrada)
    if not tem_audio:
        sys.exit("erro: o arquivo não tem trilha de áudio, então não há fala para medir as pausas")

    palavras = transcreve_palavras(entrada, modelo, idioma)

    if not palavras:
        shutil.copy2(entrada, saida)
        resumo = {
            "duracao_entrada": round(dur_entrada, 3),
            "duracao_saida": round(dur_entrada, 3),
            "pausas_removidas": 0,
            "segundos_removidos": 0.0,
            "trechos_mantidos": [],
            "nota": "nenhuma fala detectada; copiei a entrada sem mudar nada",
        }
        print(json.dumps(resumo, indent=2, ensure_ascii=False))
        return

    trechos = trechos_mantidos(palavras, pausa, folga)
    pausas = conta_pausas(palavras, pausa)
    corta_e_junta(entrada, saida, trechos, tem_video)

    dur_saida, _, _ = sonda(saida)
    resumo = {
        "duracao_entrada": round(dur_entrada, 3),
        "duracao_saida": round(dur_saida, 3),
        "pausas_removidas": pausas,
        "segundos_removidos": round(dur_entrada - dur_saida, 3),
        "trechos_mantidos": [[round(s, 3), round(e, 3)] for s, e in trechos],
    }
    print(json.dumps(resumo, indent=2, ensure_ascii=False))


def autoteste():
    # Palavras falsas com buracos de 0,05, 0,30, 0,10 e 0,50 s entre elas.
    # Com limite de 0,15 s, só os buracos de 0,30 e 0,50 contam como pausa.
    palavras = [
        (0.0, 1.0),
        (1.05, 1.55),   # buraco antes: 0,05 → junta
        (1.85, 2.35),   # buraco antes: 0,30 → parte
        (2.45, 2.95),   # buraco antes: 0,10 → junta
        (3.45, 3.95),   # buraco antes: 0,50 → parte
    ]
    pausa, folga = 0.15, 0.02

    trechos = trechos_mantidos(palavras, pausa, folga)
    esperado = [[0.0, 1.57], [1.83, 2.97], [3.43, 3.97]]

    assert len(trechos) == len(esperado), f"número de trechos: {len(trechos)} != {len(esperado)}"
    for (s, e), (es, ee) in zip(trechos, esperado):
        assert abs(s - es) < 1e-9, f"início diferente: {s} != {es}"
        assert abs(e - ee) < 1e-9, f"fim diferente: {e} != {ee}"

    pausas = conta_pausas(palavras, pausa)
    assert pausas == 2, f"esperava 2 pausas, veio {pausas}"

    print("autoteste OK")
    print(json.dumps({"trechos": trechos, "pausas_removidas": pausas}, indent=2))


def argumentos():
    p = argparse.ArgumentParser(
        description="Corta as pausas da fala de um vídeo ou áudio com os tempos por palavra do "
        "faster-whisper e o ffmpeg. Não muda a velocidade."
    )
    p.add_argument("entrada", nargs="?", help="vídeo ou áudio de entrada")
    p.add_argument("saida", nargs="?", help="arquivo de saída (ex.: cortado.mp4)")
    p.add_argument("--pausa", "--gap", type=float, default=0.15,
                   help="buraco mínimo, em segundos, para contar como pausa (padrão: 0.15)")
    p.add_argument("--folga", "--pad", type=float, default=0.02,
                   help="segundos de som mantidos de cada lado da fala (padrão: 0.02)")
    p.add_argument("--modelo", "--model", default="small",
                   help="modelo do faster-whisper: tiny, base, small, medium, large-v3 (padrão: small)")
    p.add_argument("--idioma", default="pt",
                   help="idioma da fala (padrão: pt; use '' para detectar sozinho)")
    p.add_argument("--autoteste", "--selftest", action="store_true",
                   help="roda o teste interno do cálculo dos trechos e sai")
    return p.parse_args()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = argumentos()
    if a.autoteste:
        autoteste()
        return
    if not a.entrada or not a.saida:
        print("erro: informe a entrada e a saída (ou use --autoteste)", file=sys.stderr)
        sys.exit(2)
    roda(a.entrada, a.saida, a.pausa, a.folga, a.modelo, a.idioma)


if __name__ == "__main__":
    main()
