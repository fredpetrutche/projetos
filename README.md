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
