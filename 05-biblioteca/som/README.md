# Biblioteca de som

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** aqui ficam os efeitos sonoros que os scripts de `scripts/som/` usam, todos no mesmo padrão de volume e com o pico de cada arquivo medido. O estúdio já nasce com uma biblioteca sintetizada (um comando); quando você quiser sons gravados de verdade, solta um pack em qualquer pasta e nivela. Nada desta pasta vai para o git: cada um gera ou nivela a sua.

## O que mora aqui

| Caminho | O que é |
|---|---|
| `sfx/<categoria>/<nome>.wav` | os efeitos, uma subpasta por categoria (`clique`, `pop`, `whoosh`, `impacto`…) |
| `sfx/catalogo.json` | o catálogo que a Mesa lê: categoria, duração, pico no arquivo (ms), loudness e pico de cada efeito |
| `sfx/CATALOGO.md` | o mesmo catálogo em tabela, para ler |
| `packs/` (sugestão) | packs baixados, ainda brutos, antes de nivelar |

A música não fica aqui: vai em `05-biblioteca/musica/`. Os stems que o `separar.py` cria e a grade de batidas do `batida.py` ficam ao lado da própria música.

Quer a biblioteca em outro lugar (um HD externo, uma pasta sincronizada)? Defina a variável de ambiente `ESTUDIO_SFX` com o caminho; todos os scripts passam a usar essa pasta.

## Primeira vez: a biblioteca sintetizada

```bash
uv run scripts/som/sintetizar_sfx.py
```

Gera 56 efeitos em 22 categorias, em poucos segundos, já nivelados e catalogados: clique, pop, tecla, digitação, notificação, whoosh curto e grande, carimbo, impacto, logo, pouso, papel, obturador, contador, relógio, sucesso, caneta, rolagem, riser, fita, glitch e brilho. São sons feitos por síntese (ruído filtrado, senos, sinos), sem licença de terceiros e sempre iguais (semente fixa). Dão conta de um vídeo de interface inteiro; para foley realista (passo, porta, cidade), use sons gravados.

Para ouvir todos em sequência: `uv run scripts/som/sintetizar_sfx.py --amostra amostra.wav`.

Rodar de novo refaz só os sintetizados. Um arquivo que veio de um pack nunca é sobrescrito.

## Trazer sons de verdade: nivelar um pack

Os packs chegam com volumes muito diferentes. Um mesmo pack pode ir de −47 a −1 LUFS, 46 dB de diferença, e aí um clique some e um grave fica quase no volume da voz. Por isso todo efeito passa pelo `nivelar.py` antes de entrar:

```bash
uv run scripts/som/nivelar.py "caminho/do/pack"                   # nivela tudo para 05-biblioteca/som/sfx
uv run scripts/som/nivelar.py "caminho/do/pack/Whooshes" --categoria whoosh   # força a categoria
uv run scripts/som/nivelar.py 05-biblioteca/som/sfx               # renivela a biblioteca no lugar e refaz o catálogo
```

- **Categoria:** sai do nome da pasta e do arquivo, em português ou inglês (`whoosh`, `swoosh`, `click`, `button`, `impact`, `hit`, `riser`, `notification`, `typing`, `paper`, `shutter`, `glitch`, `sparkle`…). Whoosh com mais de 0,9 s vira `whoosh-grande`. O que não casar vira uma categoria com o nome da pasta, e você chama pelo nome (`"som": "minha-pasta/arquivo"` no evento).
- **Variações:** a Mesa gira entre todos os arquivos de uma categoria, então os sons do pack se misturam aos sintetizados. Para usar só os do pack, apague os sintetizados daquela categoria e rode `nivelar.py` na biblioteca para refazer o catálogo.
- **Arquivos longos** (música dentro do pack) são pulados: o limite é `--max-dur 30` s.

### O padrão da casa

| Item | Valor |
|---|---|
| Formato | WAV 48 kHz, estéreo, 16 bits, DC removido |
| Início | ~10 ms antes do primeiro som (silêncio cortado), fade-in de 2 ms, fade-out de 20 ms |
| Nível dos efeitos curtos | pico momentâneo (EBU R128, janela de 400 ms) em **−20 LUFS** |
| Nível das camas (riser, ambiência, digitação contínua, relógio) | **−24 LUFS** |
| Pico verdadeiro | **≤ −3 dBTP**; se o teto chega antes do alvo, o arquivo fica abaixo dele (normal em cliques e teclas, marcado com ¹ no CATALOGO.md) |
| Sincronia | pico medido em ms (envelope de 5 ms): **`at = evento − pico_ms/1000`** |

Com a biblioteca nivelada, o ganho que o mapa padrão dá a cada som é o volume real dele na mix. Não use um "ganho geral de efeitos" por cima.

## Biblioteca maior e grátis: Sonniss GDC

Todo ano a Sonniss libera um pacote grande de efeitos gravados por estúdios profissionais, o "GDC Game Audio Bundle", em [sonniss.com/gameaudiogdc](https://sonniss.com/gameaudiogdc). São dezenas de GB, então não nivele tudo:

1. Baixe um ano e descompacte em `05-biblioteca/som/packs/` (ou fora do estúdio, se faltar espaço).
2. Escolha as pastas que interessam para vídeo: whooshes e transições, interface (UI), impactos, papel, foley de mesa, ambiências.
3. Nivele uma pasta por vez, com a categoria quando o nome não deixar claro:
   ```bash
   uv run scripts/som/nivelar.py "05-biblioteca/som/packs/sonniss/Whooshes" --categoria whoosh
   uv run scripts/som/nivelar.py "05-biblioteca/som/packs/sonniss/Room Tones" --categoria ambiencia --cama
   ```
4. Abra o `sfx/CATALOGO.md` e confira o que entrou. A licença vem no próprio download.

## Por que nada disso vai para o git

Áudio pesa, e cada estúdio tem a sua biblioteca. O `.gitignore` desta pasta deixa de fora tudo menos este README. Quem clona o estúdio roda `sintetizar_sfx.py` e já tem a mesma biblioteca de partida.

Como usar os sons num vídeo, o método e os números da mix: skill `som-do-video` (`.agents/skills/som-do-video/SKILL.md`) e [06-metodo/regras.md](../../06-metodo/regras.md).
