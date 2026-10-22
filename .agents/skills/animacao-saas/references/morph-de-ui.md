# Morph de UI: uma interface que vira outra

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** regras para a forma de uma interface se transformar em outra (botão → card, pílula → painel, mini player → tela cheia) com cara de produto Apple, não de slide. Valem em qualquer motor; a mola de partida está em [regras.md](../../../../06-metodo/regras.md).

## Forma

1. **Anime tamanho e raio** (`{cx, cy, w, h, r}`), nunca a escala: escala estica os cantos.
2. **A cor muda junto** com o tamanho, nos mesmos keyframes e na mesma curva: parece que a UI virou outra.
3. **Quando a forma cresce, o raio diminui um pouco**, proporcional ao tamanho novo. Um "quadrado Apple" nunca tem canto reto.
4. **Raio com teto:** `r = min(r, w/2, h/2)`. A pílula continua pílula e o card ganha canto fixo. Anime o raio só quando a forma muda de caráter (círculo → quadrado).
5. **Quique pequeno na chegada:** a forma passa ~10% do ponto e assenta, com a mola padrão. Câmera e troca de cena continuam na curva forte (.86, 0, .07, 1).
6. **Uma curva para tudo:** a mesma mola em tamanho, posição, escala e rotação. Para mudar o ritmo, mude a duração, não a curva.
7. **Motion blur** no morph rápido.

## Conteúdo

8. O conteúdo vem em **grupos**, cada um com posição e escala na mesma curva e nos mesmos tempos da forma: a imagem cresce no lugar, os controles descem, e o que não existe na UI nova some por opacidade.
9. **Imagem dentro da forma é recortada por máscara**, com o raio animado junto.
10. **A UI nova entra depois que a forma chega:** elementos extras por opacidade e posição.
11. **Conteúdo atrasado:** ícone e texto copiam a escala da forma com ~0,1 s de atraso.
12. **Um elemento fica:** escolha o que atravessa o morph (por exemplo, o botão) e mude o container à volta dele. O conteúdo novo entra por último.
13. **Colapso:** o que não existe na UI nova encolhe no eixo que some e vai a opacidade 0 nos mesmos quadros; o que fica muda de cor e tamanho.

## Causa e efeito

14. **O clique dispara:** antes de um morph acionado por botão, escala 100 → 96 → 100%, e o morph começa na soltura.
15. **Um empurra o outro:** quando o botão se move e o container cresce para o mesmo lado, atrase um dos dois em 1 quadro; lê-se como causa e efeito.
16. **Mudança de lugar em arco**, nunca em linha reta. A mola vai no progresso do caminho, não em x e y separados (senão a forma treme).
17. **Cor e ícone trocam juntos:** o ícone vai a opacidade 0 enquanto o rótulo novo entra preso ao botão.
18. **Texto com mola própria**, ~0,05 s entre palavras. A direção diz de onde vem a informação: rótulo cai de cima, status sobe de baixo, cabeçalho desliza do meio, número vem da direita.
19. **Inclinação global:** a UI inteira presa a um wrapper com rotação de ±3 a 5° em mola a cada morph.
20. **Bordas em molas diferentes:** indicador de aba e botão de toggle com a borda da frente mais rápida esticam como líquido.
21. **Mola somada:** valor que muda de alvo várias vezes é a soma de uma mola por mudança (no After Effects, uma expressão que soma um degrau por keyframe).

## Ritmo e referência

22. Sem narração, cada estado fica ~0,5 a 0,7 s antes do próximo morph; narrado, segue a fala.
23. **Referência real:** grave a tela do aparelho ou do site fazendo a transição e copie o movimento e o raio (medição com `uv run scripts/video/olho_quadro_a_quadro.py ampliar`).
