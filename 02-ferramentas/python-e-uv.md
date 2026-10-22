# Python e uv: as bibliotecas de áudio e vídeo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** o uv instala o Python 3.11 e todas as bibliotecas do `pyproject.toml` numa pasta `.venv` só do estúdio, sem mexer no resto do computador. Todo script roda com `uv run`.

- **Como acessar:** `uv run scripts/<pasta>/<script>.py` na raiz do estúdio. Não precisa ativar ambiente.
- **Instalação:** `uv sync` (base), `uv sync --extra cpu` (com IA de áudio, sem placa NVIDIA), `uv sync --extra gpu` (com placa NVIDIA, CUDA 12.8). Rodar de novo atualiza.
- **Credenciais:** nenhuma.
- **O que tem e para quê:**

| Biblioteca | Para quê |
|---|---|
| numpy, scipy | matemática do sinal: filtros, picos, reverb |
| soundfile, librosa | ler e gravar áudio, trocar a afinação de efeitos tonais |
| pyloudnorm | medir volume em LUFS (o padrão das plataformas) |
| pedalboard | reverb, compressor e efeitos na voz |
| mido | gravar MIDI (acordes) |
| faster-whisper | transcrever com o tempo de cada palavra: legenda e corte de pausas |
| opencv, Pillow | analisar quadros, folhas de contato, títulos |
| playwright | renderizar animações em HTML quadro a quadro |
| yt-dlp | baixar vídeos de referência |
| torch, beat_this | achar as batidas e os tempos fortes da música (extra `cpu`/`gpu`) |
| audio-separator | separar voz e instrumental (modelos RoFormer; extra `cpu`/`gpu`) |

- **Pegadinhas:** biblioteca nova entra no `pyproject.toml` e depois `uv sync`; nunca `pip install` solto. Sem placa NVIDIA, a separação de voz é lenta: no teste de 22/10/2026, numa máquina de 4 núcleos, 15 s de música levaram ~3 min. Separe só o trecho que vai usar, não a música inteira. Com placa NVIDIA, leva segundos. O primeiro uso baixa o modelo (~1,5 GB) e o de batidas (pequeno); depois ficam guardados.
- **Log:**
