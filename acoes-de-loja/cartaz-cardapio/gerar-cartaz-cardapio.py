# -*- coding: utf-8 -*-
"""Cartaz de QR code do cardápio — A6 avulso e A4 com quatro A6 para cortar.

Mesma identidade dos outros cartazes da Holy Cook (fundo rosa, marrom, pílula
creme, Lilita One nos títulos): a arte é a mesma do cartaz do sorteio, só muda
o texto, a foto e o QR.

Cabem exatamente QUATRO A6 numa folha A4 — 2 × 105mm de largura e 2 × 148mm de
altura dão 210 × 296mm, e o A4 tem 297. Sobra meio milímetro em cima e embaixo.
"""
import os
import segno
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))

ROSA   = HexColor("#FBD4D9")
MARROM = HexColor("#4A2B20")
CREME  = HexColor("#FDE6C9")
LARANJA = HexColor("#EE5A24")
BRANCO = HexColor("#FFFFFF")
CORTE  = HexColor("#C9A6AC")

pdfmetrics.registerFont(TTFont("Lilita", os.path.join(AQUI, "fontes", "LilitaOne-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Poppins-Med", os.path.join(AQUI, "fontes", "Poppins-Medium.ttf")))

LOGO = os.path.join(AQUI, "img", "holy-cook-logo.png")
_l = Image.open(LOGO)
LOGO_RAZAO = _l.width / _l.height



def recortador(nome):
    """Devolve uma função que recorta a foto na razão pedida, pegando o miolo de cima."""
    def recorta(razao):
        orig = os.path.join(AQUI, "img", nome)
        saida = os.path.join(AQUI, "img", f"_corte-{razao:.2f}-{nome}")
        im = Image.open(orig).convert("RGB")
        alvo = int(im.width / razao)
        if alvo <= im.height:
            topo = int((im.height - alvo) * 0.42)
            im = im.crop((0, topo, im.width, topo + alvo))
        else:
            larg = int(im.height * razao)
            esq = int((im.width - larg) / 2)
            im = im.crop((esq, 0, esq + larg, im.height))
        im.save(saida, quality=92)
        return saida
    return recorta


def cap(fonte, tam):
    return pdfmetrics.getAscent(fonte) / 1000.0 * tam * 0.72


def tamanho_para_cap(alvo):
    """Tamanho de fonte que dá exatamente essa altura de caixa alta."""
    return alvo / (pdfmetrics.getAscent("Lilita") / 1000.0 * 0.72)


def tamanho_para_largura(texto, fonte, largura):
    return 100.0 * largura / pdfmetrics.stringWidth(texto, fonte, 100)


def desenha_qr(c, matriz, x, y, lado):
    n = len(matriz)
    m = lado / n
    c.setFillColor(MARROM)
    for r, linha in enumerate(matriz):
        col = 0
        while col < n:
            if linha[col]:
                ini = col
                while col < n and linha[col]:
                    col += 1
                c.rect(x + ini * m, y + lado - (r + 1) * m, (col - ini) * m, m, stroke=0, fill=1)
            else:
                col += 1


def foto_arredondada(c, caminho, x, y, larg, alt, raio):
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, larg, alt, raio)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(caminho, x, y, larg, alt, mask=None)
    c.restoreState()


def arte(c, peca, x0, y0, larg_mm, alt_mm):
    """Desenha uma peça inteira com a origem em (x0, y0). Serve pro A6 e pro A4."""
    W, H = larg_mm * mm, alt_mm * mm
    s = larg_mm / 210.0
    margem = 0.072 * W
    cw = W - 2 * margem

    c.setFillColor(ROSA)
    c.rect(x0, y0, W, H, stroke=0, fill=1)

    # Numa peça pequena uma palavra curta vira fonte gigante, então o título tem
    # teto de altura. E quem cede espaço é a FOTO, não a tipografia: ela entra
    # como faixa, com a altura que sobrar.
    util = H - 2 * (0.075 * H)

    h1 = min(tamanho_para_largura(peca["titulo"], "Lilita", cw),
             tamanho_para_cap(0.070 * H))
    f_chapeu = h1 * 0.335
    f_sub    = h1 * 0.335
    f_pilula = h1 * 0.175

    a_chapeu = cap("Lilita", f_chapeu)
    a_h1     = cap("Lilita", h1)
    a_sub    = cap("Lilita", f_sub)

    # cap() mede a caixa alta; o acento sobe acima dela e bateria no chapéu
    acento = 0.24 * a_h1 if any(ch in peca["titulo"] for ch in "ÁÀÃÂÉÊÍÓÕÔÚÜÇ") else 0.0
    g_chapeu = 0.30 * a_chapeu + acento
    g_sub    = 0.34 * a_sub
    g_foto   = 3.2 * mm * s + 0.30 * a_sub
    g_pilula = 7.0 * mm * s
    g_card   = 5.5 * mm * s
    g_logo   = 6.0 * mm * s

    alt_pilula = f_pilula * 2.05
    alt_logo   = 0.10 * W
    lado_card  = 0.44 * W
    pad_card   = 5.0 * mm * s
    qr_lado    = lado_card - 2 * pad_card

    sem_foto = (a_chapeu + g_chapeu + a_h1 + g_sub + a_sub + g_foto
                + g_pilula + alt_pilula + g_card + lado_card + g_logo + alt_logo)
    alt_foto = max(0.14 * H, min(cw / 1.9, util - sem_foto))
    fixo = sem_foto - lado_card + alt_foto
    foto = peca["_foto"](cw / alt_foto)

    bloco = fixo + lado_card
    y = y0 + H - (H - bloco) * 0.46 - a_chapeu
    meio = x0 + W / 2

    c.setFont("Lilita", f_chapeu); c.setFillColor(MARROM)
    c.drawCentredString(meio, y, peca["chapeu"])

    y -= g_chapeu + a_h1
    c.setFont("Lilita", h1)
    c.drawCentredString(meio, y, peca["titulo"])

    y -= g_sub + a_sub
    c.setFont("Lilita", f_sub); c.setFillColor(LARANJA)
    c.drawCentredString(meio, y, peca["sub"])

    y -= g_foto + alt_foto
    foto_arredondada(c, foto, x0 + margem, y, cw, alt_foto, 4.0 * mm * s)

    texto = peca["pilula"]
    larg_pilula = pdfmetrics.stringWidth(texto, "Poppins-Med", f_pilula) + 2 * (f_pilula * 1.1)
    y -= g_pilula + alt_pilula
    c.setFillColor(CREME)
    c.roundRect(meio - larg_pilula / 2, y, larg_pilula, alt_pilula, alt_pilula / 2, stroke=0, fill=1)
    c.setFillColor(MARROM); c.setFont("Poppins-Med", f_pilula)
    c.drawCentredString(meio, y + alt_pilula / 2 - f_pilula * 0.35, texto)

    y -= g_card + lado_card
    c.setFillColor(BRANCO)
    c.roundRect(meio - lado_card / 2, y, lado_card, lado_card, 5.5 * mm * s, stroke=0, fill=1)
    desenha_qr(c, peca["_qr"], meio - qr_lado / 2, y + pad_card, qr_lado)

    y -= g_logo + alt_logo
    c.drawImage(ImageReader(LOGO), meio - alt_logo * LOGO_RAZAO / 2, y,
                alt_logo * LOGO_RAZAO, alt_logo, mask="auto")
    return qr_lado


def a6(peca, arquivo):
    W, H = 105 * mm, 148 * mm
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle(peca["pdf_titulo"])
    qr = arte(c, peca, 0, 0, 105, 148)
    c.showPage(); c.save()
    print(f"ok {os.path.basename(arquivo)}  A6 105x148mm | QR {qr/mm:.1f}mm")


def a4_quatro(peca, arquivo):
    """Quatro A6 numa A4, com as linhas de corte."""
    W, H = 210 * mm, 297 * mm
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle(peca["pdf_titulo"] + " — 4 por folha A4")
    folga = (H - 2 * 148 * mm) / 2          # 0,5mm em cima e embaixo
    for col in (0, 1):
        for lin in (0, 1):
            qr = arte(c, peca, col * 105 * mm, folga + lin * 148 * mm, 105, 148)
    c.setStrokeColor(CORTE); c.setLineWidth(0.25); c.setDash(2, 3)
    c.line(105 * mm, 0, 105 * mm, H)
    c.line(0, folga + 148 * mm, W, folga + 148 * mm)
    c.setDash()
    c.showPage(); c.save()
    print(f"ok {os.path.basename(arquivo)}  A4 com 4 peças A6 | QR {qr/mm:.1f}mm cada")


BASE = "https://holycampinas.github.io/cardapio-holy-cook-campinas/"
PECAS = [
    {"slug": "cardapio-campinas",
     "url": BASE,
     "chapeu": "VEM VER O",
     "titulo": "CARDÁPIO",
     "sub": "DA HOLY",
     "pilula": "Leia o QR Code para ver o cardápio",
     "foto": "cookies.jpg",
     "pdf_titulo": "Cardápio Holy Cook Campinas — QR code"},
    {"slug": "comparativo-campinas",
     "url": BASE + "comparativo/",
     "chapeu": "O MESMO COOKIE",
     "titulo": "MAIS BARATO",
     "sub": "AQUI NA LOJA",
     "pilula": "Leia o QR Code e compare com o iFood",
     "foto": "kinder-nutella.jpg",
     "pdf_titulo": "Loja ou iFood — Holy Cook Campinas — QR code"},
]

if __name__ == "__main__":
    for p in PECAS:
        p["_qr"] = [list(r) for r in segno.make(p["url"], error="H").matrix]
        p["_foto"] = recortador(p["foto"])
        a6(p, os.path.join(AQUI, f"cartaz-{p['slug']}-a6.pdf"))
        a4_quatro(p, os.path.join(AQUI, f"cartaz-{p['slug']}-a4-4up.pdf"))
