# Som de cena: ambiência e foley

> Data: 2026-10-22 · Tipo: referência · Status: vigente

**Resumo:** quando o vídeo tem pessoas ou lugares (filmados ou gerados) e parece "mudo" ou "de banco de imagem", ele ganha uma camada de som de cena: a ambiência de cada lugar e um som para cada ação na tela. É a terceira camada, por baixo de voz e música. Não substitui os efeitos de interface; ali segue "um efeito por elemento". Os tetos de volume estão em [06-metodo/regras.md](../../../../06-metodo/regras.md).

## O processo

1. **Mapa de ações.** Faça uma folha de contato a 10 quadros por segundo (`ffmpeg -i video.mp4 -vf "fps=10,scale=320:-1,tile=10x5" folha-%02d.png`) e anote, por cena: o lugar (o que se ouviria ali), quem se mexe, quando e com que material (salto em madeira, caneca de cerâmica, teclado de notebook), e o que acontece fora do quadro e faria som. **Só entra som que a imagem motiva.**
2. **Meça os tempos que importam.** Evento visível pelo brilho ou movimento da região (a tela do celular acende); passos pelo balanço do corpo quando os pés não aparecem.
3. **Escolha os sons.** Biblioteca nivelada primeiro (`05-biblioteca/som/sfx`, packs gravados como o Sonniss GDC). Som genérico descola: passo grave sem clique, teclado mecânico num notebook. Se faltar, gere ou grave sob medida, descrevendo material + ação + espaço + o que não pode ter ("sem música, sem anúncio de alto-falante").
4. **Monte as camadas** (no `eventos.json` com `"som": "categoria/arquivo"`, ou num `--mapa` do projeto):
   - **ambiência por cena**, cruzando o corte: começa 0,25–0,7 s antes da imagem (J-cut) ou continua abafada depois dela (L-cut, passa-baixa ~1 kHz, "atrás da porta");
   - **foley** (passo, gole, tecla, tecido, vibração) com o início no quadro medido;
   - **pan sutil** de quem se move (de +0,1 a +0,65 saindo pela direita);
   - **reverb pelo tamanho do lugar** (`sala=True` no `M.poe`): sala vazia com mais reverb; som de longe com mais reverb e menos agudo;
   - **passa-baixa** no que está atrás do vidro (cidade: 1,3–1,8 kHz; abaixo de ~1 kHz some no celular);
   - **silêncio antes do impacto:** quase nada por ~1 s antes do som principal da cena.
5. **Confira o balanço por janela.** Cena a cena, foley contra ambiência. Um som denso domina o loudness e esconde o resto; o teclado tem que ficar acima da cidade; o passo precisa de clique (agudo) para atravessar a conversa.
6. **Verifique o volume antes de entregar (obrigatório):**
   ```bash
   uv run scripts/som/verificar_som_de_cena.py audio/mix.wav                               # peça só de cena
   uv run scripts/som/verificar_som_de_cena.py audio/escuta/efeitos.wav --voz audio/escuta/voz.wav   # com voz
   ```
   O `som.py` sem voz nem música já entrega a −25 LUFS e pico ≤ −3. Nunca normalize o som de cena sozinho a −14 LUFS. Meça de novo no áudio do `.mp4` final.

## O que já deu errado

| Erro | Correção |
|---|---|
| Som de cena sozinho normalizado a −14 LUFS ("muito alto") | −25 LUFS sem voz; ≥ 15 LU abaixo da voz com voz; verificador |
| Efeito sem motivo na imagem: relógio, whoosh e riser em corte parado | mapa de ações primeiro; só som motivado |
| Transiente nivelado por LUFS (tique a −33 LUFS com pico perto de 0 dBFS) | efeito curto nivelado pelo pico (é o que o `nivelar.py` faz) |
| `loudnorm` em peça curta cai no modo dinâmico e mexe no balanço | ganho linear medido; limitador só se passar do pico |
| Passo grave sem clique some sob a conversa | somar um estalo de piso duro (passa-alta 1,8 kHz) bem abaixo do baque |
| Cidade com passa-baixa de 650 Hz inaudível no celular | 1,3–1,8 kHz |
