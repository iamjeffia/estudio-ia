# Vídeo do zero: passo a passo

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** as etapas de um vídeo com IA, da ideia ao render final. Vale para a maioria dos vídeos: narrado, tutorial, anúncio, Reel musical. A IA monta este checklist no `README.md` do projeto (`04-projetos/AAAA-MM-DD-tema/`) e marca cada etapa ao concluir.

## As etapas

1. **Ideia e critério de pronto.** Registre a ideia no `README.md` do projeto: o que o vídeo mostra, para quem, formato (9:16, 16:9), duração e onde vai ser publicado. Se o formato ou a entrega não estiverem claros, a IA pergunta agora, uma vez.

2. **Roteiro enxuto, texto seu.** A IA faz só a estrutura em `roteiro.md`: gancho, partes e os pontos de cada uma. O texto final é seu. Roteiro escrito inteiro por IA costuma sair genérico, e é a sua fala que dá personalidade ao vídeo. Depois de escrito, a IA não reescreve a fala; no máximo aponta erro ou trecho confuso.

3. **Narração.** Grave com a sua voz (celular perto da boca, lugar silencioso) ou gere com a sua voz clonada numa ferramenta de voz. Escreva como se fala: se uma palavra sai com a pronúncia errada, ajuste a grafia (ex.: "IÁ" no lugar de "IA").

4. **Aprovação do áudio.** Ouça o áudio inteiro antes de seguir. Está natural, no ritmo certo, sem palavra errada? Esta é uma parada do processo: a edição só começa com o áudio aprovado, porque todo o resto é sincronizado com ele.

5. **Referências e assets: a etapa que mais pesa no resultado.** Vale gastar tempo aqui (skill `video-referencias`). Procure primeiro em `03-referencias/` e na `05-biblioteca/`. Tudo o que a fala cita tem que aparecer na tela:
   - produto ou sistema seu → grave a tela real ou recrie a interface fielmente;
   - post, notícia ou site citado → abra, tire o print, recorte e finalize como asset;
   - plataforma, empresa ou app → ícone ou SVG oficial;
   - pessoa citada → foto real; lugar, objeto ou dado → imagem real ou print da fonte.

   Imagem real deixa o vídeo dinâmico e crível. Essa busca vem antes de começar a animar.

6. **Identidade visual do vídeo.** Cada vídeo ganha fonte, cores, ícones, componentes e transição tirados do assunto. Falou de uma marca forte? O vídeo veste a marca: tipografia, cores e elementos dela. Assunto sem identidade forte? Use uma base limpa (UI clara, estilo Apple) e reserve uma cor de destaque. Mudou de assunto no meio do vídeo? Faça uma transição e troque a identidade junto.

   **Direções em quadros antes de animar.** Para o gancho e para o corpo do vídeo, a IA junta pelo menos 10 referências numa prancha (do `03-referencias/`, do Pinterest, de templates de motion) e propõe **3 direções de verdade em quadros parados**, nas mesmas 3 cenas, para a comparação ser justa. Cada direção tem nome, uma frase de conceito e um elemento diferente que costura as cenas. Você escolhe uma, mistura duas ou pede outra rodada com mais pesquisa. A escolha vai para o [escolhas.md](escolhas.md): o que estava na mesa, o que ganhou e por quê. Na próxima vez, a IA começa pelas regras que saíram dali.

7. **Trilha e sound design** (skill `som-do-video`). Música real escolhida por momentos (abertura suave, respiro antes do drop, clímax), um efeito sonoro para cada elemento que entra ou sai, com o som do que se vê (clique é clique, arrastar é deslize). O som pode sair dos eventos da animação pelo `scripts/som/som.py`, sem esperar o render final.

8. **Montagem e motion.** Escolha o motor pelo tipo de peça (skill `estudio-video`):
   - **After Effects** (com o Motion Kit AE): acabamento fino, transições, molas, 3D;
   - **EffectCraft**: alternativa gratuita ao After Effects;
   - **HyperFrames** ou **Remotion**: vídeo em código (HTML ou React), ótimo para telas, texto animado e peças que se repetem.

   Pergunta de controle em cada movimento: **"isso está humano ou robotizado?"** Robotizado é o card ou a câmera que anima, para morto e ressuscita num movimento rápido. Humano é continuar vivo o tempo todo, nem que seja com o mínimo: deriva, flutuação, um balanço lento. Use peso e física reais. Os números de partida (mola, câmera, tempos) estão em [regras.md](regras.md).

9. **Revisar e entregar.** Assista quadro a quadro com áudio. Rode `uv run scripts/video/detectar_saltos.py render/final.mp4` para achar quadros pulados ou vazios. Compare com a referência lado a lado: a referência "grita mais" (contraste, tamanho, peso do texto)? Então ainda não superou. Corrija, renderize o final e registre no `README.md` do projeto e numa anotação.

10. **Aprendeu algo? Registre.** Número que funcionou vai para `regras.md`; técnica nova vai para `aprendizados.md`. É assim que o próximo vídeo sai melhor que este.
