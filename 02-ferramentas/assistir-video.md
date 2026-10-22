# watch: a IA assiste a um vídeo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** skill que deixa a IA "assistir" a um vídeo (link ou arquivo): baixa, tira quadros com o tempo de cada um e pega a transcrição. É assim que uma referência vira análise sem você descrever o vídeo.

- **Como acessar:** peça "assiste a este vídeo e me diz como é feita a transição do segundo 5" com o link ou o caminho.
- **Instalação:** instalador, passo 4 (`npx skills add bradautomates/claude-video`).
- **Credenciais:** opcional, uma chave da API do Gemini deixa o Google assistir ao vídeo inteiro com áudio. A skill explica onde guardar. Sem chave, funciona com quadros e transcrição local.
- **Complementos do estúdio:** `uv run scripts/referencias.py olhar <arquivo>` (folha de contato rápida) e `uv run scripts/video/olho_quadro_a_quadro.py` (câmera, ampliação e comparação quadro a quadro).
- **Pegadinhas:** vídeo privado ou com login não baixa: salve o arquivo e passe o caminho.
- **Log:**
