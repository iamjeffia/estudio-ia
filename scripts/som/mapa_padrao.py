"""mapa_padrao.py — som padrão para cada tipo de evento (`tipo` no eventos.json). Um vídeo novo já sai com
"um som para cada elemento que entra ou sai" sem escrever mapa; o projeto sobrepõe só o que for especial
(`som.py --mapa meu_mapa.py` ou `M.eventos(..., sobrepor={"logo": minha_funcao})`).

Cada família toca uma CATEGORIA da biblioteca (05-biblioteca/som/sfx/<categoria>/), girando entre as variações para
não repetir o mesmo arquivo em seguida. Ganhos em dB sobre a biblioteca nivelada (pico momentâneo −20 LUFS); o `vol`
do evento (padrão 1) multiplica o volume (0,5 = −6 dB, 2 = +6 dB). Whoosh tem o pico ~0,2 s depois do início do gesto
(é o meio do movimento). Tonais só quando a Mesa tem tom, e só nos momentos de hype, transição ou surpresa:
transição grande, impacto, carimbo, logo e revelação. Nunca em clique, pop ou tecla.
"""
import math

FAMILIAS = {
    "pop": ["pop", "card", "bolha", "balao", "pilula", "rotulo", "widget", "texto", "credito", "botao", "estrela",
            "anuncio", "mini", "item", "chip", "badge", "entra", "surge", "bubble"],
    "clique": ["clique", "clique-cta", "liga", "mira", "campo", "toque", "tap", "click", "seleciona", "trava", "toggle"],
    "tecla": ["tecla", "letras", "palavra", "digita", "digitacao", "typing", "key"],
    "notifica": ["notifica", "notificacao", "mensagem", "msg", "alerta", "notification", "message"],
    "whoosh": ["whoosh", "morph", "pulo", "volta", "empurra", "sobe", "move", "encolhe", "sai", "texto-sai", "desliza",
               "troca", "colapsa", "flip", "wipe", "swipe", "slide", "seta", "titulo"],
    "whoosh-grande": ["transicao", "viagem", "chicote", "salto", "morph-grande", "painel", "mergulho", "zoom", "cta",
                      "sai-tela", "transition"],
    "carimbo": ["carimbo", "selo", "carimbo-leve", "aprovado", "stamp"],
    "impacto": ["impacto", "golpe", "peso", "drop", "pancada", "impact", "hit", "boom"],
    "logo": ["logo", "marca", "assinatura", "marca-final"],
    "pouso": ["pouso", "cai", "aterrissa", "land"],
    "papel": ["papel", "foto", "cartao", "pagina", "folha", "paper"],
    "obturador": ["obturador", "print", "captura", "screenshot", "shutter"],
    "abre": ["abre", "iris", "nasce", "acende", "revela", "aparece", "flash", "reveal"],
    "contador": ["contador", "numero", "valor", "preco", "counter"],
    "relogio": ["relogio", "tempo", "clock"],
    "sucesso": ["sucesso", "ok", "confirmado", "check", "etapa", "success"],
    "caneta": ["caneta", "risco", "traco", "circulo", "sublinha", "desenha", "marca-texto", "pen"],
    "rolagem": ["rolagem", "scroll"],
    "riser": ["riser", "carregando", "loading", "scan", "tensao"],
    "fita": ["fita", "rebobina", "tape"],
    "glitch": ["glitch", "erro", "error"],
    "brilho": ["brilho", "sino", "estrelas", "magica", "sparkle"],
}
TIPO = {k: fam for fam, ks in FAMILIAS.items() for k in ks}


def _vol(e):
    return 20 * math.log10(max(float(e.get("vol", 1.0)), 0.05))


def tocar(M, e):
    """Toca o som padrão do evento; devolve False se o tipo não tem som padrão (vai para o relatório)."""
    k = e["tipo"]
    fam = TIPO.get(k) or TIPO.get(k.split("-")[0])
    if fam is None:
        return False
    t, p, v = e["t"], float(e.get("pan", 0.0)) * 0.6, _vol(e)
    tem_tom = M.tom(t) is not None
    if fam == "pop":
        M.poe("pop", t, -13 + v, p)
    elif fam == "clique":
        M.poe("clique", t, -9 + v, p)
    elif fam == "tecla":
        if k == "letras":
            for j in range(4):
                M.poe("tecla", t + 0.03 + j * 0.065, -10 + v - (j % 2) * 2, p)
        elif k in ("digita", "digitacao", "typing"):
            M.poe("digitacao", t, -17 + v, p, alinha="ini", fim=float(e.get("dur", 0.9)), fade=0.12)
        else:
            M.poe("tecla", t, -14 + v, p)
    elif fam == "notifica":
        M.poe("notificacao", t, -14 + v, p)
    elif fam == "whoosh":
        M.poe("whoosh", t + 0.2, -14 + v, p)
    elif fam == "whoosh-grande":
        M.poe("whoosh-grande", t + 0.4, -12 + v, p * 0.5)
        if tem_tom:
            M.tonal(t + 0.45, -31, timbre="pad", dur=1.6)
    elif fam == "carimbo":
        M.poe("carimbo", t, -10 + v, p, sala=True)
        if tem_tom:
            M.golpe(t, -25)
    elif fam == "impacto":
        M.poe("impacto", t, -11 + v, 0, sala=True)
        if tem_tom:
            M.golpe(t, -20)
    elif fam == "logo":
        M.poe("logo", t, -13 + v, 0)
        if tem_tom:
            M.golpe(t, -21)
    elif fam == "pouso":
        M.poe("pouso", t, -14 + v, p)
    elif fam == "papel":
        M.poe("papel", t, -15 + v, p)
    elif fam == "obturador":
        M.poe("obturador", t + 0.02, -15 + v, p)
    elif fam == "abre":
        M.poe("pop", t, -12 + v, p, st=-1)
        if tem_tom:
            M.tonal(t + 0.02, -28, pan=p)
    elif fam == "contador":
        if k == "contador":
            M.poe("contador", t, -14 + v, p, alinha="ini")
        else:
            M.poe("pop", t, -13 + v, p, st=2)
    elif fam == "relogio":
        M.poe("relogio", t, -19 + v, p, alinha="ini", fim=float(e.get("dur", 1.5)), fade=0.3)
    elif fam == "sucesso":
        M.poe("sucesso", t, -16 + v, p)
    elif fam == "caneta":
        M.poe("caneta", t, -14 + v, p, alinha="ini", fim=float(e.get("dur", 0.8)), fade=0.15)
    elif fam == "rolagem":
        M.poe("rolagem", t, -18 + v, p, alinha="ini")
    elif fam == "riser":
        M.poe("riser", t, -14 + v, p, alinha="fim" if k == "riser" else "ini")
    elif fam == "fita":
        M.poe("fita", t, -12 + v, p)
    elif fam == "glitch":
        M.poe("glitch", t, -16 + v, p)
    elif fam == "brilho":
        M.poe("brilho", t, -18 + v, p)
    return True
