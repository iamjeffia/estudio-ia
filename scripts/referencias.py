#!/usr/bin/env python3
"""Organiza a biblioteca de referências: o que chegou em _entrada/, folha de contato, mover e catalogar.

A mídia fica na pasta indicada no 03-referencias/ONDE.md (esta pasta ou uma pasta do Google Drive). O
catálogo, as análises e a lista de links ficam SEMPRE no repositório:

  03-referencias/catalogo.md          uma linha por referência organizada
  03-referencias/analises/            um .md por referência analisada
  03-referencias/_entrada/links.md    links para baixar, um por linha (mesmo com a mídia no Drive)
  <mídia>/_entrada/                   arquivos que chegaram e ainda não foram organizados
  <mídia>/<categoria>/                arquivos organizados (motion, som, design, anuncios, marcas, fotos)

Comandos:
  novos                       lista o que está em <mídia>/_entrada/ (tipo, tamanho, duração, resolução) e
                              baixa com o yt-dlp cada link pendente de _entrada/links.md, marcando a linha
  olhar <arquivo>             vídeo/GIF: gera uma folha de contato (quadros com o tempo) e mostra o caminho;
                              imagem ou áudio: mostra as informações
  mover <arquivo> <categoria> renomeia para AAAA-MM-DD-assunto.ext, move para <mídia>/<categoria>/ e
                              acrescenta a linha no catalogo.md
  criar [pasta]               cria as pastas das categorias na pasta da mídia (ou na pasta indicada)

Exemplos:
  uv run scripts/referencias.py novos
  uv run scripts/referencias.py olhar "transição bonita.mp4"
  uv run scripts/referencias.py mover "transição bonita.mp4" motion --tags "mola, câmera" --nota "entrada com overshoot"
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _estudio import FONTES, REFERENCIAS, midia_referencias  # noqa: E402

CATEGORIAS = {
    "motion": "animação, transições, câmera, tipografia animada",
    "som": "músicas, efeitos, trilhas e edits cujo som vale copiar",
    "design": "telas de app, sites, UI, tipografia, paletas",
    "anuncios": "anúncios e campanhas, em vídeo ou imagem",
    "marcas": "logos e identidades",
    "fotos": "pessoas, lugares, produtos, texturas",
}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".wmv", ".flv", ".mpg", ".mpeg", ".3gp"}
GIF = {".gif"}
IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".heic", ".heif", ".bmp", ".tif", ".tiff", ".svg"}
AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".aif", ".aiff", ".wma"}
LINKS = REFERENCIAS / "_entrada" / "links.md"
CATALOGO = REFERENCIAS / "catalogo.md"
CABECALHO_LINKS = "<!-- Cole um link por linha; `uv run scripts/referencias.py novos` baixa cada um para _entrada/ e marca a linha como [baixado]. -->\n"
URL = re.compile(r"https?://[^\s<>()\"'\]]+")


# ---------- utilidades ----------

def tipo_de(caminho: Path) -> str:
    ext = caminho.suffix.lower()
    if ext in VIDEO:
        return "vídeo"
    if ext in GIF:
        return "gif"
    if ext in IMAGEM:
        return "imagem"
    if ext in AUDIO:
        return "áudio"
    return "outro"


def tamanho_legivel(n: int) -> str:
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidade == "GB":
            return f"{n:.0f} {unidade}" if unidade == "B" else f"{n:.1f} {unidade}"
        n /= 1024
    return f"{n:.1f} GB"


def sonda(caminho: Path) -> dict:
    """Duração, resolução e se tem som, pelo ffprobe. Devolve {} se o ffprobe não ler o arquivo."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,width,height,avg_frame_rate:stream_side_data=rotation",
             "-of", "json", str(caminho)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        sys.exit("erro: não achei o ffprobe no PATH. Instale o ffmpeg (roteiro setup/2-instalar.md).")
    if out.returncode != 0:
        return {}
    dados = json.loads(out.stdout or "{}")
    info = {}
    dur = dados.get("format", {}).get("duration")
    if dur not in (None, "N/A"):
        info["duracao"] = float(dur)
    for s in dados.get("streams", []):
        if s.get("codec_type") == "video" and "largura" not in info and s.get("width"):
            w, h = int(s["width"]), int(s["height"])
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                rot = int(float(sd.get("rotation", 0) or 0))
            if abs(rot) in (90, 270):  # vídeo de celular gravado em pé
                w, h = h, w
            info["largura"], info["altura"] = w, h
            n, _, d = (s.get("avg_frame_rate") or "0/0").partition("/")
            if float(d or 0):
                info["fps"] = float(n) / float(d)
        if s.get("codec_type") == "audio":
            info["som"] = True
    return info


def resolucao_imagem(caminho: Path):
    if caminho.suffix.lower() == ".svg":
        return None
    try:
        from PIL import Image
        with Image.open(caminho) as im:
            return im.size
    except Exception:
        info = sonda(caminho)
        return (info["largura"], info["altura"]) if "largura" in info else None


def fmt_duracao(s: float) -> str:
    m, s = divmod(s, 60)
    return f"{int(m)}:{s:04.1f}" if m else f"{s:.1f} s"


def slug(texto: str, limite: int = 60) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto[:limite].rstrip("-") or "referencia"


def celula(texto: str) -> str:
    """Texto seguro para uma célula de tabela Markdown (sem quebra de linha nem barra vertical solta)."""
    return " ".join((texto or "").split()).replace("|", "\\|")


def entrada_midia() -> Path:
    return midia_referencias() / "_entrada"


def acha_arquivo(nome: str) -> Path:
    """Aceita caminho completo, caminho relativo ao diretório atual ou só o nome do arquivo em _entrada/."""
    p = Path(nome).expanduser()
    for candidato in (p, entrada_midia() / nome, midia_referencias() / nome):
        if candidato.is_file():
            return candidato.resolve()
    sys.exit(f"erro: não achei '{nome}' (procurei no caminho dado e em {entrada_midia()})")


def lista_entrada() -> list[Path]:
    pasta = entrada_midia()
    if not pasta.exists():
        return []
    ignorar = {"links.md", "desktop.ini", "thumbs.db", ".ds_store"}
    return sorted(
        (f for f in pasta.iterdir()
         if f.is_file() and f.name.lower() not in ignorar and not f.name.startswith(".")
         and f.suffix.lower() not in (".part", ".ytdl", ".tmp")),
        key=lambda f: f.name.lower(),
    )


# ---------- links ----------

def garante_links():
    LINKS.parent.mkdir(parents=True, exist_ok=True)
    if not LINKS.exists():
        LINKS.write_text(CABECALHO_LINKS, encoding="utf-8", newline="\n")


def links_pendentes(linhas: list[str]) -> list[tuple[int, str]]:
    pendentes, em_comentario = [], False
    for i, linha in enumerate(linhas):
        t = linha.strip()
        if t.startswith("<!--"):
            em_comentario = "-->" not in t
            continue
        if em_comentario:
            em_comentario = "-->" not in t
            continue
        if not t or t.startswith("#") or "[baixado" in t:
            continue
        m = URL.search(t)
        if m:
            pendentes.append((i, m.group(0).rstrip(".,;")))
    return pendentes


def baixa(url: str, destino: Path) -> list[Path]:
    """Baixa um link com o yt-dlp do próprio ambiente (python -m yt_dlp). Devolve os arquivos gerados."""
    destino.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-progress", "--restrict-filenames",
           "--merge-output-format", "mp4", "-o", str(destino / "%(title).70B__%(id)s.%(ext)s"),
           "--print", "after_move:filepath", url]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        erro = [l for l in r.stderr.splitlines() if "ERROR" in l] or r.stderr.strip().splitlines()[-1:]
        raise RuntimeError(erro[0] if erro else f"o yt-dlp saiu com código {r.returncode}")
    return [Path(l.strip()) for l in r.stdout.splitlines() if l.strip() and Path(l.strip()).exists()]


def origem_no_links(nome_arquivo: str) -> str | None:
    """Acha o link de onde veio um arquivo baixado pelo `novos` (a linha marcada guarda o nome)."""
    if not LINKS.exists():
        return None
    for linha in LINKS.read_text(encoding="utf-8").splitlines():
        if "[baixado" in linha and nome_arquivo in linha:
            m = URL.search(linha)
            if m:
                return m.group(0)
    return None


# ---------- comandos ----------

def cmd_novos(a):
    garante_links()
    linhas = LINKS.read_text(encoding="utf-8").splitlines(keepends=True)
    pendentes = links_pendentes(linhas)
    if pendentes and not a.sem_baixar:
        print(f"Baixando {len(pendentes)} link(s) de {LINKS.relative_to(REFERENCIAS.parent).as_posix()}...")
        hoje = dt.date.today().isoformat()
        for i, url in pendentes:
            try:
                arquivos = baixa(url, entrada_midia())
            except RuntimeError as e:
                print(f"  ✗ {url}\n    {e}\n    (a linha fica pendente; se o site não deixar, baixe à mão e jogue em _entrada/)")
                continue
            nomes = ", ".join(f.name for f in arquivos) or "?"
            print(f"  ✓ {url} → {nomes}")
            fim = "\n" if linhas[i].endswith("\n") else ""
            linhas[i] = f"[baixado {hoje}] {url} → {nomes}{fim}"
            LINKS.write_text("".join(linhas), encoding="utf-8", newline="\n")  # grava a cada link: se cair no meio, não baixa de novo
        print()
    elif pendentes:
        print(f"{len(pendentes)} link(s) pendente(s) em links.md (não baixados por causa do --sem-baixar).\n")

    arquivos = lista_entrada()
    print(f"Em {entrada_midia()}: {len(arquivos)} arquivo(s)")
    for f in arquivos:
        tipo = tipo_de(f)
        partes = [tipo, tamanho_legivel(f.stat().st_size)]
        if tipo in ("vídeo", "gif", "áudio"):
            info = sonda(f)
            if "duracao" in info:
                partes.append(fmt_duracao(info["duracao"]))
            if "largura" in info and tipo != "áudio":
                partes.append(f"{info['largura']}×{info['altura']}")
            if tipo == "vídeo":
                partes.append("com som" if info.get("som") else "sem som")
        elif tipo == "imagem":
            res = resolucao_imagem(f)
            if res:
                partes.append(f"{res[0]}×{res[1]}")
        print(f"  - {f.name}  [{' · '.join(partes)}]")
    if arquivos:
        print("\nPróximo passo: `olhar <arquivo>` para ver cada vídeo e `mover <arquivo> <categoria>` para organizar.")


def acha_fonte():
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


def fonte(tamanho):
    from PIL import ImageFont
    caminho = acha_fonte()
    if caminho:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def folha_de_contato(video: Path, saida: Path, n: int, colunas: int, largura: int) -> Path:
    from PIL import Image, ImageDraw

    info = sonda(video)
    dur = info.get("duracao")
    if not dur:
        sys.exit("erro: o ffprobe não leu a duração; o arquivo pode estar corrompido")
    passo = dur / n
    tempos = [passo * (k + 0.5) for k in range(n)]
    quadros = []
    with tempfile.TemporaryDirectory() as tmp:
        for k, t in enumerate(tempos):
            jpg = Path(tmp) / f"q{k:02d}.jpg"
            # -ss DEPOIS do -i: mais lento, mas o quadro sai inteiro (antes do -i alguns H.264 saem com blocos)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ss", f"{t:.3f}", "-frames:v", "1",
                            "-vf", f"scale={largura}:-2", "-q:v", "3", str(jpg)], capture_output=True)
            if jpg.exists():
                with Image.open(jpg) as im:
                    quadros.append((t, im.convert("RGB").copy()))
    if not quadros:
        sys.exit("erro: o ffmpeg não conseguiu tirar nenhum quadro do arquivo")

    w, h = quadros[0][1].size
    linhas = (len(quadros) + colunas - 1) // colunas
    topo, borda = 44, 4
    folha = Image.new("RGB", (colunas * (w + borda) + borda, topo + linhas * (h + borda) + borda), (16, 16, 18))
    d = ImageDraw.Draw(folha)
    titulo = f"{video.name}  ·  {fmt_duracao(dur)}"
    if "largura" in info:
        titulo += f"  ·  {info['largura']}×{info['altura']}"
    if info.get("fps"):
        titulo += f"  ·  {info['fps']:.2f} qps"
    d.text((borda + 6, 10), titulo, font=fonte(22), fill=(235, 235, 240))
    f_tempo = fonte(max(14, w // 16))
    for k, (t, im) in enumerate(quadros):
        x = borda + (k % colunas) * (w + borda)
        y = topo + borda + (k // colunas) * (h + borda)
        folha.paste(im.resize((w, h)) if im.size != (w, h) else im, (x, y))
        rotulo = fmt_duracao(t)
        caixa = d.textbbox((0, 0), rotulo, font=f_tempo)
        d.rectangle([x, y, x + caixa[2] + 12, y + caixa[3] + 8], fill=(0, 0, 0))
        d.text((x + 6, y + 3), rotulo, font=f_tempo, fill=(255, 214, 10))
    saida.parent.mkdir(parents=True, exist_ok=True)
    folha.save(saida, quality=88)
    return saida


def cmd_olhar(a):
    arq = acha_arquivo(a.arquivo)
    tipo = tipo_de(arq)
    print(f"{arq.name}  [{tipo} · {tamanho_legivel(arq.stat().st_size)}]")
    if tipo == "imagem":
        res = resolucao_imagem(arq)
        if res:
            print(f"resolução: {res[0]}×{res[1]}")
        print(f"caminho: {arq}")
        print("É imagem: abra o arquivo direto para ver.")
        return
    info = sonda(arq)
    if "duracao" in info:
        print(f"duração: {fmt_duracao(info['duracao'])}")
    if tipo == "áudio" or "largura" not in info:
        print("Sem imagem para olhar. Para ouvir e entender o som, use a skill `watch` ou abra no player.")
        return
    print(f"resolução: {info['largura']}×{info['altura']}" + (f" · {info['fps']:.2f} qps" if info.get("fps") else "")
          + (" · com som" if info.get("som") else " · sem som"))
    if a.saida:
        saida = Path(a.saida)
    else:
        # fora da _entrada/ para não virar "arquivo novo" nem subir para o Drive
        saida = Path(tempfile.gettempdir()) / "estudio-ia-folhas" / f"{slug(arq.stem)}-folha.jpg"
    folha_de_contato(arq, saida, a.quadros, a.colunas, a.largura)
    print(f"folha de contato ({a.quadros} quadros): {saida}")


def cmd_mover(a):
    arq = acha_arquivo(a.arquivo)
    categoria = a.categoria.lower()
    if categoria not in CATEGORIAS:
        sys.exit(f"erro: categoria '{a.categoria}' não existe. Use uma destas: {', '.join(CATEGORIAS)}")
    data = a.data or dt.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
        sys.exit("erro: --data deve ser AAAA-MM-DD")
    origem = a.origem or origem_no_links(arq.name) or ""
    # o assunto vem do --assunto ou do nome do arquivo (sem o "__<id>" que o `novos` põe nos baixados)
    base = a.assunto or arq.stem
    if not a.assunto and origem and "__" in base:
        base = base.rsplit("__", 1)[0]
    base = re.sub(r"^\d{4}-\d{2}-\d{2}[-_ ]*", "", base) or arq.stem  # não repete a data se já vier no nome
    pasta = midia_referencias() / categoria
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{data}-{slug(base)}{arq.suffix.lower()}"
    destino, n = pasta / nome, 2
    while destino.exists():
        destino = pasta / f"{data}-{slug(base)}-{n}{arq.suffix.lower()}"
        n += 1
    shutil.move(str(arq), str(destino))

    rel = destino.relative_to(midia_referencias()).as_posix()
    linha = f"| {data} | {categoria} | {celula(rel)} | {celula(a.tags)} | {celula(a.nota)} | {celula(origem)} |\n"
    texto = CATALOGO.read_text(encoding="utf-8") if CATALOGO.exists() else ""
    if texto and not texto.endswith("\n"):
        texto += "\n"
    CATALOGO.write_text(texto + linha, encoding="utf-8", newline="\n")
    print(f"movido: {arq.name} → {destino}")
    print(f"catálogo: {linha.strip()}")
    if not a.nota:
        print("dica: uma --nota curta (o que tem de bom) ajuda muito a achar depois.")


def cmd_criar(a):
    raiz = Path(a.pasta).expanduser() if a.pasta else midia_referencias()
    raiz.mkdir(parents=True, exist_ok=True)
    for nome in ["_entrada", *CATEGORIAS]:
        (raiz / nome).mkdir(exist_ok=True)
    (REFERENCIAS / "analises").mkdir(parents=True, exist_ok=True)
    garante_links()
    print(f"pastas prontas em {raiz}:")
    for nome in ["_entrada", *CATEGORIAS]:
        print(f"  {nome}/" + (f"  ({CATEGORIAS[nome]})" if nome in CATEGORIAS else "  (o que chegou e ainda não foi organizado)"))
    print(f"análises e links ficam no repositório: {REFERENCIAS / 'analises'} e {LINKS}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="comando")

    s = sub.add_parser("novos", help="lista _entrada/ e baixa os links de links.md")
    s.add_argument("--sem-baixar", action="store_true", help="só lista, sem baixar os links pendentes")
    s.set_defaults(f=cmd_novos)

    s = sub.add_parser("olhar", help="folha de contato de um vídeo/GIF (ou informações de imagem e áudio)")
    s.add_argument("arquivo", help="nome do arquivo em _entrada/ ou caminho")
    s.add_argument("--quadros", type=int, default=16, help="quantos quadros na folha (padrão: 16)")
    s.add_argument("--colunas", type=int, default=4, help="quadros por linha (padrão: 4)")
    s.add_argument("--largura", type=int, default=480, help="largura de cada quadro em px (padrão: 480)")
    s.add_argument("--saida", help="onde gravar o JPG (padrão: pasta temporária do sistema)")
    s.set_defaults(f=cmd_olhar)

    s = sub.add_parser("mover", help="renomeia, move para a categoria e registra no catalogo.md")
    s.add_argument("arquivo", help="nome do arquivo em _entrada/ ou caminho")
    s.add_argument("categoria", help=f"uma de: {', '.join(CATEGORIAS)}")
    s.add_argument("--tags", default="", help='palavras para busca, ex.: "mola, câmera, reel"')
    s.add_argument("--nota", default="", help="o que a referência tem de bom, em uma frase")
    s.add_argument("--origem", default="", help="link de onde veio (se baixado pelo `novos`, é achado sozinho)")
    s.add_argument("--assunto", default="", help="assunto para o nome do arquivo (padrão: o nome atual)")
    s.add_argument("--data", default="", help="data do nome e do catálogo, AAAA-MM-DD (padrão: hoje)")
    s.set_defaults(f=cmd_mover)

    s = sub.add_parser("criar", help="cria as pastas das categorias na pasta da mídia")
    s.add_argument("pasta", nargs="?", help="pasta da mídia (padrão: a do ONDE.md)")
    s.set_defaults(f=cmd_criar)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
