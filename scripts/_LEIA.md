# scripts: as ferramentas de som, vídeo e referências

> Data: 2026-10-22 · Tipo: entrada · Status: vigente

**Resumo:** scripts Python que as skills chamam. Todos rodam da raiz do estúdio com `uv run`, que usa o `.venv` certo sozinho. Cada um tem `--help` em português.

## Referências

| Comando | O que faz |
|---|---|
| `uv run scripts/referencias.py novos` | lista o que chegou em `_entrada/` e baixa os links de `03-referencias/_entrada/links.md` |
| `uv run scripts/referencias.py olhar <arquivo>` | folha de contato com 16 quadros e o tempo de cada um |
| `uv run scripts/referencias.py mover <arquivo> <categoria> --tags "..." --nota "..."` | renomeia, move e registra no catálogo |
| `uv run scripts/referencias.py criar` | cria as pastas das categorias onde a mídia fica (local ou Drive) |

## Vídeo

| Comando | O que faz |
|---|---|
| `uv run scripts/video/make_captions.py <video> legendas.json` | legenda palavra por palavra (JSON para Remotion e SRT) com o faster-whisper |
| `uv run scripts/video/cut_pauses.py <entrada> <saida>` | corta as pausas da fala sem mudar a velocidade |
| `uv run scripts/video/olho_quadro_a_quadro.py camera\|folha\|rastro\|ampliar\|compara ...` | mede câmera, amplia detalhes e compara a referência com a recriação |
| `uv run scripts/video/detectar_saltos.py <video>` | depois de todo render: acha quadros pulados, vazios ou isolados |

## Som

Os detalhes e o método estão na skill `som-do-video` e no [README da biblioteca de som](../05-biblioteca/som/README.md).

| Comando | O que faz |
|---|---|
| `uv run scripts/som/sintetizar_sfx.py` | gera a biblioteca inicial de efeitos (o instalador já roda) |
| `uv run scripts/som/nivelar.py <pasta>` | nivela um pack de efeitos seu no padrão do estúdio e cataloga o pico de cada um |
| `uv run scripts/som/som.py --eventos eventos.json ...` | gera a mixagem (efeitos, voz, música) a partir dos eventos da animação |
| `uv run scripts/som/verificar_som_de_cena.py <mix>` | reprova som de cena alto demais antes da entrega |
| `uv run scripts/som/batida.py <musica>` | batidas, tempos fortes e BPM (precisa da IA de áudio) |
| `uv run scripts/som/separar.py <musica>` | separa voz e instrumental (precisa da IA de áudio) |

## Para quem escreve scripts novos

Use `scripts/_estudio.py` para achar as pastas (`RAIZ`, `SFX`, `MUSICA`, `midia_referencias()`), nunca caminho fixo. Biblioteca nova entra no `pyproject.toml`, seguida de `uv sync`.
