#!/usr/bin/env python3
"""Transcreve um vídeo ou áudio com o faster-whisper e grava as legendas palavra por palavra.

Saídas:
  - JSON no formato Caption do @remotion/captions (uma entrada por palavra: text, startMs, endMs,
    timestampMs, confidence), pronto para o Remotion ou para montar legenda animada em outro motor;
  - SRT comum, com as palavras agrupadas em blocos curtos, para CapCut, Premiere, DaVinci, YouTube etc.
    Vai ao lado do JSON com o mesmo nome (troque com --srt ou desligue com --sem-srt).

Uso:
    uv run scripts/video/make_captions.py video.mp4 legendas.json [--modelo small]
    uv run scripts/video/make_captions.py video.mp4 legendas.json --roteiro roteiro.txt
    uv run scripts/video/make_captions.py --autoteste
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path


def transcreve_legendas(entrada, modelo, idioma):
    from faster_whisper import WhisperModel

    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segmentos, _info = m.transcribe(str(entrada), language=idioma or None, word_timestamps=True, vad_filter=True)

    legendas = []
    for seg in segmentos:
        for w in seg.words or []:
            ini_ms = round(w.start * 1000)
            fim_ms = round(w.end * 1000)
            # O Remotion separa as páginas pelo espaço do começo, então todo texto começa com exatamente
            # um espaço; a pontuação fica grudada do jeito que o faster-whisper devolveu.
            legendas.append({
                "text": " " + w.word.strip(" "),
                "startMs": ini_ms,
                "endMs": fim_ms,
                "timestampMs": round((ini_ms + fim_ms) / 2),
                "confidence": None,
            })

    transcricao = " ".join(c["text"].strip() for c in legendas if c["text"].strip())
    return legendas, transcricao


def normaliza(palavra):
    """Minúsculas, sem acento e sem pontuação, para comparar no alinhamento."""
    palavra = unicodedata.normalize("NFKD", palavra.lower())
    palavra = "".join(c for c in palavra if not unicodedata.combining(c))
    return re.sub(r"[^\w]", "", palavra, flags=re.UNICODE)


def corrige_pelo_roteiro(legendas, palavras_transcritas, palavras_roteiro):
    """Troca legenda["text"] no lugar pelas palavras do roteiro lido.
    Os tempos nunca mudam e nenhuma entrada é acrescentada ou tirada.
    Devolve (quantas_trocadas, método), com método "posicional" ou "difflib".
    """
    if len(palavras_transcritas) == len(palavras_roteiro):
        metodo = "posicional"
        corrigidas = list(palavras_roteiro)
    else:
        metodo = "difflib"
        corrigidas = list(palavras_transcritas)
        norm_t = [normaliza(w) for w in palavras_transcritas]
        norm_r = [normaliza(w) for w in palavras_roteiro]
        comp = difflib.SequenceMatcher(a=norm_t, b=norm_r, autojunk=False)
        for tag, i1, i2, j1, j2 in comp.get_opcodes():
            if tag in ("equal", "replace") and (i2 - i1) == (j2 - j1):
                for k in range(i2 - i1):
                    corrigidas[i1 + k] = palavras_roteiro[j1 + k]

    trocadas = sum(1 for antiga, nova in zip(palavras_transcritas, corrigidas) if antiga != nova)
    for leg, nova in zip(legendas, corrigidas):
        leg["text"] = " " + nova
    return trocadas, metodo


def blocos_srt(legendas, max_caracteres=42, max_segundos=5.0, pausa_quebra=0.6):
    """Agrupa as palavras em blocos de legenda: quebra no fim de frase, numa pausa maior que
    pausa_quebra, ou quando o bloco passaria de max_caracteres ou de max_segundos."""
    blocos, atual = [], []
    for leg in legendas:
        palavra = leg["text"].strip()
        if not palavra:
            continue
        if atual:
            texto = " ".join(p for p, _, _ in atual)
            ultima = atual[-1][0]
            quebra = (
                ultima[-1:] in ".?!…"
                or (leg["startMs"] - atual[-1][2]) / 1000 > pausa_quebra
                or len(texto) + 1 + len(palavra) > max_caracteres
                or (leg["endMs"] - atual[0][1]) / 1000 > max_segundos
            )
            if quebra:
                blocos.append(atual)
                atual = []
        atual.append((palavra, leg["startMs"], leg["endMs"]))
    if atual:
        blocos.append(atual)
    return [(b[0][1], b[-1][2], " ".join(p for p, _, _ in b)) for b in blocos]


def tempo_srt(ms):
    h, ms = divmod(int(ms), 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def texto_srt(legendas, max_caracteres):
    linhas = []
    for i, (ini, fim, texto) in enumerate(blocos_srt(legendas, max_caracteres), 1):
        linhas += [str(i), f"{tempo_srt(ini)} --> {tempo_srt(fim)}", texto, ""]
    return "\n".join(linhas)


def roda(entrada, saida_json, modelo, idioma, roteiro=None, saida_srt=None, max_caracteres=42):
    if not Path(entrada).exists():
        sys.exit(f"erro: não achei o arquivo {entrada}")
    legendas, transcricao = transcreve_legendas(entrada, modelo, idioma)

    if roteiro and legendas:
        # Neste ponto legendas[i]["text"] ainda é exatamente a palavra transcrita (com o espaço do começo),
        # então serve como lista de palavras transcritas.
        transcritas = [c["text"].strip(" ") for c in legendas]
        palavras_roteiro = Path(roteiro).read_text(encoding="utf-8").split()
        trocadas, metodo = corrige_pelo_roteiro(legendas, transcritas, palavras_roteiro)
        print(f"correção pelo roteiro: método {metodo}, {trocadas} palavra(s) trocada(s)")
        transcricao = " ".join(c["text"].strip() for c in legendas)

    Path(saida_json).write_text(json.dumps(legendas, ensure_ascii=False, indent=2), encoding="utf-8")
    if saida_srt:
        Path(saida_srt).write_text(texto_srt(legendas, max_caracteres), encoding="utf-8")

    if not legendas:
        print("nenhuma fala detectada: gravei a legenda vazia")
    else:
        print(transcricao)
    print(f"palavras: {len(legendas)}")
    print(f"JSON (Remotion): {saida_json}")
    if saida_srt:
        print(f"SRT: {saida_srt}")


def autoteste():
    # Caso 1: mesmo número de palavras, duas transcritas errado (a troca "IA"/"a" e "Contexto"/"Contesto",
    # que é o erro típico de sigla e de palavra parecida).
    leg1 = [
        {"text": " a", "startMs": 0, "endMs": 100, "timestampMs": 50, "confidence": None},
        {"text": " gosta", "startMs": 100, "endMs": 200, "timestampMs": 150, "confidence": None},
        {"text": " de", "startMs": 200, "endMs": 300, "timestampMs": 250, "confidence": None},
        {"text": " Contesto", "startMs": 300, "endMs": 400, "timestampMs": 350, "confidence": None},
    ]
    trocadas1, metodo1 = corrige_pelo_roteiro(leg1, ["a", "gosta", "de", "Contesto"], ["IA", "gosta", "de", "Contexto"])
    assert metodo1 == "posicional", metodo1
    assert trocadas1 == 2, trocadas1
    assert [c["text"] for c in leg1] == [" IA", " gosta", " de", " Contexto"]
    assert leg1[0]["startMs"] == 0 and leg1[0]["endMs"] == 100
    assert leg1[3]["startMs"] == 300 and leg1[3]["endMs"] == 400

    # Caso 2: número diferente — a transcrição tem uma palavra a mais ("muito") que o roteiro não tem,
    # e uma palavra errada de verdade ("Contesto" → "Contexto").
    leg2 = [
        {"text": " eu", "startMs": 0, "endMs": 100, "timestampMs": 50, "confidence": None},
        {"text": " gosto", "startMs": 100, "endMs": 200, "timestampMs": 150, "confidence": None},
        {"text": " muito", "startMs": 200, "endMs": 300, "timestampMs": 250, "confidence": None},
        {"text": " de", "startMs": 300, "endMs": 400, "timestampMs": 350, "confidence": None},
        {"text": " Contesto", "startMs": 400, "endMs": 500, "timestampMs": 450, "confidence": None},
    ]
    trocadas2, metodo2 = corrige_pelo_roteiro(leg2, ["eu", "gosto", "muito", "de", "Contesto"], ["eu", "gosto", "de", "Contexto"])
    assert metodo2 == "difflib", metodo2
    assert len(leg2) == 5, "nenhuma entrada pode ser acrescentada ou tirada"
    assert leg2[2]["text"] == " muito", "a palavra a mais da transcrição fica intacta"
    assert leg2[2]["startMs"] == 200 and leg2[2]["endMs"] == 300
    assert leg2[4]["text"] == " Contexto", "o trecho 'replace' troca pela palavra do roteiro"
    assert trocadas2 == 1, trocadas2

    # Caso 3: SRT quebra no ponto final e na pausa longa, com tempo no formato HH:MM:SS,mmm.
    leg3 = [
        {"text": " Oi,", "startMs": 0, "endMs": 300},
        {"text": " tudo", "startMs": 320, "endMs": 600},
        {"text": " bem?", "startMs": 620, "endMs": 900},
        {"text": " Hoje", "startMs": 1000, "endMs": 1200},
        {"text": " vamos", "startMs": 2500, "endMs": 2800},
    ]
    blocos = blocos_srt(leg3)
    assert [b[2] for b in blocos] == ["Oi, tudo bem?", "Hoje", "vamos"], blocos
    assert tempo_srt(3_723_456) == "01:02:03,456"
    assert texto_srt(leg3, 42).startswith("1\n00:00:00,000 --> 00:00:00,900\nOi, tudo bem?\n")

    print("autoteste OK")


def argumentos():
    p = argparse.ArgumentParser(
        description="Transcreve um vídeo ou áudio e grava legendas palavra por palavra: JSON no formato "
        "Caption do Remotion e um SRT comum ao lado."
    )
    p.add_argument("entrada", nargs="?", help="vídeo ou áudio de entrada")
    p.add_argument("saida_json", nargs="?", help="JSON de saída (formato Caption do Remotion)")
    p.add_argument("--modelo", "--model", default="small",
                   help="modelo do faster-whisper: tiny, base, small, medium, large-v3 (padrão: small)")
    p.add_argument("--idioma", default="pt", help="idioma da fala (padrão: pt; use '' para detectar sozinho)")
    p.add_argument("--roteiro", "--script", metavar="ARQUIVO",
                   help=".txt (UTF-8) com o texto exato que foi lido; corrige as palavras transcritas sem mexer nos tempos")
    p.add_argument("--srt", metavar="ARQUIVO", help="onde gravar o SRT (padrão: mesmo nome do JSON, com .srt)")
    p.add_argument("--sem-srt", action="store_true", help="não grava o SRT")
    p.add_argument("--max-caracteres", type=int, default=42, help="tamanho máximo de cada bloco do SRT (padrão: 42)")
    p.add_argument("--autoteste", "--selftest", action="store_true",
                   help="roda o teste interno do alinhamento e do SRT e sai")
    return p.parse_args()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = argumentos()
    if a.autoteste:
        autoteste()
        return
    if not a.entrada or not a.saida_json:
        sys.exit("erro: informe a entrada e o JSON de saída (ou use --autoteste)")
    srt = None if a.sem_srt else (a.srt or str(Path(a.saida_json).with_suffix(".srt")))
    roda(a.entrada, a.saida_json, a.modelo, a.idioma, a.roteiro, srt, a.max_caracteres)


if __name__ == "__main__":
    main()
