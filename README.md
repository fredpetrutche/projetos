# Projetos

Cardápio central dos projetos de marketing e conteúdo. Cada card abre a página do
projeto numa aba nova. Quem não está no ar aparece no fim, com o caminho da pasta.

**No ar:** https://fredpetrutche.github.io/projetos/

## Como mexer

Tudo vive em `index.html` — um arquivo só, sem build, sem dependência.

Para adicionar um projeto novo, copie um bloco `<a class="cartao">` e troque:

- `href` — a URL da página
- `style="--cor:..."` — a cor da faixa lateral (`--tinta`, `--verde`, `--laranja`, `--roxo`, `--rosa`, `--cinza`)
- o `<span class="nome">` e o `<p class="desc">`
- o texto do `<span class="pe">` — o domínio que aparece no rodapé do card

Depois: `git commit` e `git push`. O GitHub Pages publica sozinho em ~1 min.

### Projeto que ainda não existe

Use `<div class="cartao trancado">` no lugar do `<a>` — vira card de borda tracejada,
com cadeado e o selo "ainda não começou". Não é clicável. Quando o projeto nascer,
troque o `div` por um `<a href="...">`, tire a classe `trancado` e o `<span class="trava">`,
e escreva a descrição.

### Página que mora fora do GitHub

Artefato do Claude, Notion, o que for: é um `<a>` normal, só acrescente
`<span class="selo">artefato</span>` depois do nome e ponha a origem no `<span class="pe">`.

### Projeto sem página própria

Existe e está andando, mas é acompanhado em outro lugar (hoje, nas Reuniões).
Card clicável apontando pra lá, com `<span class="selo">reuniões</span>`. Não usa
`trancado` — trancado é só pro que ainda não começou.

## Arrastar para reorganizar

O botão **Organizar** liga o modo de edição: os cards param de navegar e ganham
uma alça. Arraste para trocar a ordem ou jogar o card em outra seção; ao soltar,
salva sozinho. Perto da borda da tela a página rola sozinha, senão não dava para
levar um card da primeira seção até a última.

No celular, só a alça arrasta — o corpo do card continua rolando a página.

### Onde a ordem fica salva

Tabela `hc_cardapio_ordem` no Supabase `mkajvxyiyqxotiydkylq` (o mesmo projeto da
Máquina de Conteúdo e das Reuniões). Uma linha só, `id = 'projetos'`, com o arranjo
em JSON: `{ "<seção>": ["<id do card>", ...] }`.

O conteúdo do card **não** vai pro banco — nome, descrição, link e cor moram no HTML.
O banco só sabe onde cada card fica. Por isso:

- card novo no HTML aparece sozinho, no fim da seção onde você o escreveu;
- card removido do HTML some, e o id órfão no banco é ignorado;
- se o banco estiver fora do ar, a página abre na ordem do HTML e avisa.

Como em `hc_acoes`, a edição é aberta: quem tem o link pode reorganizar.
Se um dia isso incomodar, o caminho é pôr uma trava no modo Organizar.

A migração fica em `supabase/migrations/`. O arquivo `20260812000000_hc_reunioes.sql`
é das Reuniões, não deste projeto — está aqui só porque os dois dividem o mesmo
banco e o `supabase db push` exige o histórico completo. Não edite.
