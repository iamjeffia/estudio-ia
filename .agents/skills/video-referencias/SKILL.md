---
name: video-referencias
description: Método obrigatório antes de montar qualquer vídeo com motion (documentário, explicativo, anúncio, lançamento, Reel musical) — assistir a referência quadro a quadro e com áudio, medir o movimento, baixar os assets reais do assunto, vestir a marca tirada do site oficial, reproduzir as plataformas que o público reconhece e buscar pessoas e ambientes reais. Usar quando chegar uma referência de vídeo, uma notícia ou produto para virar vídeo, ou um pedido de anúncio.
---

# Vídeo com referências reais

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** vídeo sem referência sai genérico; o que gera conexão é a pessoa reconhecer o que está vendo. Antes de animar: medir a referência quadro a quadro e ouvir o áudio, juntar o material real do assunto, vestir a marca de verdade e reproduzir as plataformas que o público usa. A escolha de motor e receita está na [estudio-video](../estudio-video/SKILL.md); os números, em [regras.md](../../../06-metodo/regras.md).

## Onde guardar

- Referência que chegou solta vai para `03-referencias/_entrada/` e é organizada pelo `scripts/referencias.py` ([como funciona](../../../03-referencias/_LEIA.md)). Antes de buscar fora, procure no [catálogo](../../../03-referencias/catalogo.md): `rg -i "palavra" 03-referencias/catalogo.md`.
- Referência que vai guiar um vídeo ganha análise em `03-referencias/analises/AAAA-MM-DD-assunto.md`, detalhada o bastante para ninguém precisar reabrir a fonte.
- Assets do vídeo (prints, logos, fotos, gravações) ficam em `04-projetos/<projeto>/referencias/`, com um `FONTES.md` (link e data de cada um).

## 1. Definir o estilo

| Estilo | Quando | Como soa e se move |
|---|---|---|
| **Documentário / explicativo** | explicar notícia, conceito, produto | narração, textura, palavra-chave grande, material real em molduras, ritmo de documentário |
| **Comercial / hype** | anúncio, lançamento, demonstração | sem narração (no máximo uma fala), música de energia, interface reconhecível, câmera contínua sobre a UI, muitos efeitos sincronizados, humor leve |

## 2. Assistir a referência de verdade

Assistir é destrinchar imagem **e** som, não olhar meia dúzia de quadros.

1. **Baixar:** jogue o link em `03-referencias/_entrada/links.md` e rode `uv run scripts/referencias.py novos` (usa o yt-dlp).
2. **Estrutura:** `uv run scripts/referencias.py olhar <arquivo>` gera a folha de contato. Para entender fala, música e intenção do vídeo inteiro, use a skill `watch`.
3. **Medir o que o olho vê rodando.** Folha de contato e modelos que amostram 1 quadro por segundo não pegam a deriva da câmera, a tremida, a duração dos chicotes, o degradê ou o brilho do texto:
   - `uv run scripts/video/olho_quadro_a_quadro.py camera <video>`: curva do movimento global por fluxo óptico; separa trajetória e tremida e devolve amplitude e frequência da tremida, duração dos chicotes e velocidade da deriva. São os números da sua câmera.
   - `uv run scripts/video/olho_quadro_a_quadro.py ampliar <video>`: recorte ampliado sem suavizar, ao lado de uma versão com contraste esticado; revela degradê, halo e contorno.
   - `uv run scripts/video/olho_quadro_a_quadro.py compara`: curvas do original e da recriação no mesmo gráfico, para fechar a revisão com números.

   (Confira os argumentos exatos com `--help`.) **O imperfeito humaniza:** a câmera da referência quase nunca para. Meça a deriva e a tremida e reproduza; movimento perfeito e parado parece robô.
4. **Áudio:** transcreva a fala e marque os golpes da música (batidas, drop, pausas). A análise de som em detalhe é da skill [som-do-video](../som-do-video/SKILL.md).
5. **Escreva antes de qualquer código**, na análise: a **gramática de movimento** (tabela recurso × onde × como) e a **tabela som × imagem** (tempo, faixa, o que aparece).

Referência que é "antes e depois" lado a lado ou comparação de versões: recorte o painel que interessa antes de medir.

## 3. Coletar o material real do assunto

Tudo o que a fala cita aparece na tela, com imagem real:

- **Produto ou sistema próprio** → grave a tela real ou recrie a interface fielmente ([ui-para-video](../ui-para-video/SKILL.md)).
- **Notícia, post ou site citado** → abra, capture, recorte e finalize como asset. Site que bloqueia download: captura de tela pelo navegador.
- **Página oficial de produto** → liste imagens e vídeos da página (inclusive iframes de player), baixe os vídeos oficiais, olhe numa folha de contato e escolha os trechos limpos, sem rótulo queimado. Crédito na tela quando couber.
- **Pessoa citada** → foto real. **Lugar, objeto ou dado** → imagem real ou print da fonte.

### A marca do assunto, tirada do site

Os vídeos que mais superam o original vestem a marca real. Não confie na memória:

1. Baixe o HTML do site e liste os assets (`/assets/*`): fontes, SVG do símbolo, ícones, às vezes vídeo do produto.
2. Cores: tokens com nome no CSS (`--color-<marca>-*`) ou os hex mais usados no CSS compilado.
3. Abra `/brand`, `/press` ou o kit de imprensa, e as **capturas oficiais do produto antes da home** (a home mostra o marketing; a captura mostra o produto). Meça a cor das métricas na captura (leitura de pixel).
4. Logo e ícones em SVG oficial (uma extensão de exportar SVG no navegador ajuda).
5. Cada valor com a fonte num `BRAND.md` do projeto. Confira números do site no dia: material antigo envelhece.

## 4. Reproduzir as plataformas que o público reconhece

Toda ação mostrada usa o visual da plataforma que a pessoa usa no dia a dia. Antes de desenhar, busque uma referência visual **atual** (site oficial, captura, Pinterest) e copie cores, tipografia, componentes e ícones. Para o público brasileiro, por exemplo:

| Ação no vídeo | Plataforma de referência |
|---|---|
| Mensagem com cliente, atendimento | WhatsApp (e WhatsApp Business) |
| E-mail | Gmail |
| Planilha, lista, controle | Google Planilhas |
| Agenda, horários | Google Agenda |
| Conversa com IA | ChatGPT, Claude ou a IA que o vídeo cita |
| Post, repercussão | X, Instagram |
| Pedido de comida | o app de delivery mais usado no público |
| Pagamento | Pix; o banco que o público usa |
| Notificação | banner de notificação do iPhone ou do Android |
| DM de cliente em negócio local | Instagram Direct |

Mantenha essa lista viva no projeto: plataforma nova, referência usada e as cores medidas. Para marcas, o site oficial costuma render mais que o Pinterest (logo vetorial, cores exatas pelo CSS); o Pinterest ajuda com telas do app.

## 5. Pessoas e ambientes

Busque no Pinterest (sessão do navegador da pessoa) por palavras-chave curtas: nicho + público + ambiente. A pessoa real da foto é referência de look, idade, roupa, cenário e luz; **se a imagem for gerada, o rosto é outro**. Salve em `referencias/pinterest/` com o link de cada pin no `FONTES.md`.

## 6. Montar

- Transição pelo estilo (catálogo na [estudio-video](../estudio-video/references/saidas-e-truques.md)).
- Texto surge do desfoque para o nítido; listas com item em foco; pilhas 3D; grades que abrem.
- **Cursor visível em todo clique**, com som de clique; um efeito sonoro para cada ação que importa (receitas de som na [som-do-video](../som-do-video/SKILL.md)).
- Um toque de humor quando couber (o robô que erra, a expressão), sem virar piada.
- Revise por prévia e folha de contato antes do render final. O agente não escuta: o som depende do retorno do dono ou de um modelo que ouve (skill `watch`).

## 7. Revisão contra a referência

1. **Salto:** `uv run scripts/video/detectar_saltos.py render/final.mp4` em todo render; cada salto restante é corte de propósito, no tempo forte.
2. **Vazio:** nenhum quadro chapado ou isolado no master.
3. **Cortes:** quadro antes, no corte e depois de cada corte; nenhum vira dissolve de 1 quadro nem dupla exposição.
4. **Parado:** procure trechos de 0,3 a 0,5 s sem movimento; compare com o original.
5. **"O original grita mais?"** no celular, original em cima e nosso embaixo: contraste, saturação, peso do tipo, tamanho dos elementos. Se o original ganha impacto, ainda não superou, mesmo que o nosso esteja mais sofisticado.
6. **Escala:** elementos do mesmo tamanho ou maiores que no original; UI legível no celular.
7. **Som:** cada efeito no seu evento, nível contra a música (skill `som-do-video`).

## Limites

- Mostrar plataformas como **ferramenta usada** é o objetivo. Não coloque o logo de outra empresa como parceira nem diga que um produto dela está integrado quando não está.
- Não apresente uma empresa real como cliente num anúncio publicado. Caso fictício usa marca fictícia com os códigos visuais do nicho.
- Use a referência para estrutura, movimento e ritmo; não copie marca, texto ou ilustração de terceiros como se fossem seus.
- Credenciais, e-mails e dados pessoais nunca aparecem na tela: troque por valores de exemplo.
