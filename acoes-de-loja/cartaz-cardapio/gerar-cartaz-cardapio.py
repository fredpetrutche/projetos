# -*- coding: utf-8 -*-
"""Cartaz de QR code — réplica do modelo A5 que a loja já usa.

O original é `Holy Cook - QR Cardapio Paulinia (A5).pdf`. Este script refaz a
mesma arte em vetor, com as medidas tiradas do próprio PDF (148 × 210 mm):

    logo lockup   topo 11,0 mm · altura 34,1 mm
    título        topo 50,3 mm · 2 linhas, a mais larga com 65,7 mm
    pílula creme  topo 78,1 mm · 94,7 × 10,3 mm
    card branco   topo 95,2 mm · 84,2 mm de lado, QR de 67,9 mm dentro
    @ do perfil   topo 187,4 mm
    endereço      topo 196,7 mm

O que muda de uma peça para outra é só o destino do QR, o título, a frase da
pílula e os dados da loja. Em A4 cabem duas peças A5 — o A5 é a metade exata.
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

ROSA     = HexColor("#FBD4D9")
MARROM   = HexColor("#4A2B20")
CREME    = HexColor("#FDE6C9")
LARANJA  = HexColor("#EF5B25")
ENDERECO = HexColor("#6D4C45")
BRANCO   = HexColor("#FFFFFF")
SOMBRA   = HexColor("#ECC6C9")
CORTE    = HexColor("#C9A6AC")

pdfmetrics.registerFont(TTFont("Lilita", os.path.join(AQUI, "fontes", "LilitaOne-Regular.ttf")))
pdfmetrics.registerFont(TTFont("QS", os.path.join(AQUI, "fontes", "Quicksand-SemiBold.ttf")))

LOGO = os.path.join(AQUI, "img", "holy-cook-logo.png")
LOGO_RAZAO = (lambda i: i.width / i.height)(Image.open(LOGO))

# ── medidas do modelo, em mm de uma folha A5 ────────────────────────────────
LOGO_TOPO, LOGO_ALT = 11.0, 34.1
TIT_TOPO, TIT_LARG_MAX = 50.3, 65.7
TIT_PT, TIT_ENTRELINHA = 39.0, 12.2
PIL_TOPO, PIL_LARG, PIL_ALT, PIL_PT = 78.1, 94.7, 10.3, 11.8
CARD_TOPO, CARD_LADO, QR_LADO = 95.2, 84.2, 67.9
AT_TOPO, AT_PT = 187.4, 18.0   # o @ do modelo é Lilita One, não Quicksand
END_TOPO, END_PT = 196.7, 9.8
# Fração do lado do QR tomada pelo selo redondo do meio. No modelo são ~25%.
# Com correção H o código tolera ~30% de área perdida; 25% do lado dá 4,9%.
SELO = 0.25


def cap(fonte, tam):
    return pdfmetrics.getAscent(fonte) / 1000.0 * tam * 0.72


def cabe(texto, fonte, pt, larg_mm):
    """Reduz o corpo se a frase for mais longa que a do modelo."""
    larg = pdfmetrics.stringWidth(texto, fonte, pt)
    return pt * min(1.0, (larg_mm * mm) / larg)


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


def arte(c, peca, x0, y0):
    """Uma peça A5 inteira, com a origem no canto inferior esquerdo dela."""
    W, H = 148 * mm, 210 * mm
    meio = x0 + W / 2
    topo = lambda t: y0 + H - t * mm          # mm medidos do alto da folha

    c.setFillColor(ROSA)
    c.rect(x0, y0, W, H, stroke=0, fill=1)

    # logo
    alt = LOGO_ALT * mm
    c.drawImage(ImageReader(LOGO), meio - alt * LOGO_RAZAO / 2, topo(LOGO_TOPO) - alt,
                alt * LOGO_RAZAO, alt, mask="auto")

    # título, duas linhas
    pt = min(TIT_PT, *(cabe(l, "Lilita", TIT_PT, TIT_LARG_MAX) for l in peca["titulo"]))
    c.setFont("Lilita", pt); c.setFillColor(MARROM)
    y = topo(TIT_TOPO) - cap("Lilita", pt)
    for linha in peca["titulo"]:
        c.drawCentredString(meio, y, linha)
        y -= TIT_ENTRELINHA * mm

    # pílula
    c.setFillColor(CREME)
    c.roundRect(meio - PIL_LARG * mm / 2, topo(PIL_TOPO) - PIL_ALT * mm,
                PIL_LARG * mm, PIL_ALT * mm, PIL_ALT * mm / 2, stroke=0, fill=1)
    pt = cabe(peca["pilula"], "QS", PIL_PT, PIL_LARG - 10)
    c.setFillColor(MARROM); c.setFont("QS", pt)
    c.drawCentredString(meio, topo(PIL_TOPO) - PIL_ALT * mm / 2 - pt * 0.34, peca["pilula"])

    # card branco com sombra, e o QR dentro
    lado = CARD_LADO * mm
    c.setFillColor(SOMBRA)
    c.roundRect(meio - lado / 2, topo(CARD_TOPO) - lado - 2.2 * mm, lado, lado, 7 * mm, stroke=0, fill=1)
    c.setFillColor(BRANCO)
    c.roundRect(meio - lado / 2, topo(CARD_TOPO) - lado, lado, lado, 7 * mm, stroke=0, fill=1)
    qr = QR_LADO * mm
    qx, qy = meio - qr / 2, topo(CARD_TOPO) - lado + (lado - qr) / 2
    desenha_qr(c, peca["_qr"], qx, qy, qr)

    # selo redondo com o logo no miolo do código
    d = qr * SELO
    c.setFillColor(BRANCO)
    c.circle(meio, qy + qr / 2, d / 2, stroke=0, fill=1)
    alt = d * 0.70
    c.drawImage(ImageReader(LOGO), meio - alt * LOGO_RAZAO / 2, qy + qr / 2 - alt / 2,
                alt * LOGO_RAZAO, alt, mask="auto")

    # @ do perfil e endereço
    pt = cabe(peca["arroba"], "Lilita", AT_PT, 100)
    c.setFillColor(LARANJA); c.setFont("Lilita", pt)
    c.drawCentredString(meio, topo(AT_TOPO) - cap("Lilita", pt), peca["arroba"])
    pt = cabe(peca["endereco"], "QS", END_PT, 110)
    c.setFillColor(ENDERECO); c.setFont("QS", pt)
    c.drawCentredString(meio, topo(END_TOPO) - cap("QS", pt), peca["endereco"])


def a5(peca, arquivo):
    c = canvas.Canvas(arquivo, pagesize=(148 * mm, 210 * mm))
    c.setTitle(peca["pdf_titulo"])
    arte(c, peca, 0, 0)
    c.showPage(); c.save()
    print(f"ok {os.path.basename(arquivo)}  A5 148x210mm | QR {QR_LADO}mm")


def a4_duas(peca, arquivo):
    """Duas peças A5 numa A4, uma em cima da outra, com a linha de corte."""
    W, H = 210 * mm, 297 * mm
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle(peca["pdf_titulo"] + " — 2 por folha A4")
    # A4 (210 × 297) é exatamente duas A5. Cortando a folha ao meio, cada metade
    # mede 210 × 148,5 — que é uma A5 deitada. Por isso a peça entra girada 90°:
    # depois do corte, é só virar o papel e ela está em pé.
    c.setFillColor(ROSA)             # forra a folha: some com a emenda de meio milímetro
    c.rect(0, 0, W, H, stroke=0, fill=1)
    for i in (0, 1):
        c.saveState()
        c.translate(W, i * 148.5 * mm)
        c.rotate(90)
        arte(c, peca, 0, 0)
        c.restoreState()
    c.setStrokeColor(CORTE); c.setLineWidth(0.25); c.setDash(2, 3)
    c.line(0, 148.5 * mm, W, 148.5 * mm)
    c.setDash()
    c.showPage(); c.save()
    print(f"ok {os.path.basename(arquivo)}  A4 com 2 peças A5 (giradas) | QR {QR_LADO}mm cada")


LOJAS = {
    "campinas": {
        "base": "https://holycampinas.github.io/cardapio-holy-cook-campinas/",
        "arroba": "@holycook.campinas",
        "endereco": "R. Cônego Nery, 463 — Campinas",
    },
    "paulinia": {
        "base": "https://holycampinas.github.io/cardapio-holy-cook-paulinia/",
        "arroba": "@holycook.paulinia",
        "endereco": "Av. José Paulino, 1615 — Paulínia",
    },
    "piracicaba": {
        "base": "https://holycampinas.github.io/cardapio-holy-cook-piracicaba/",
        "arroba": "@holycook.piracicaba",
        "endereco": "R. Quinze de Novembro, 630 — Piracicaba",
    },
}
DESTINOS = {
    "cardapio": {
        "sufixo": "",
        "titulo": ["ACESSE O", "CARDÁPIO"],
        "pilula": "Aponte a câmera do celular para o código",
    },
    "comparativo": {
        "sufixo": "comparativo/",
        "titulo": ["AQUI SAI", "MAIS BARATO"],
        "pilula": "Compare o preço do iFood com o da loja",
    },
}

if __name__ == "__main__":
    for lj, loja in LOJAS.items():
        for ds, destino in DESTINOS.items():
            peca = {
                "arroba": loja["arroba"], "endereco": loja["endereco"],
                "titulo": destino["titulo"], "pilula": destino["pilula"],
                "pdf_titulo": f"Holy Cook {lj.capitalize()} — QR {ds}",
            }
            peca["_qr"] = [list(r) for r in
                           segno.make(loja["base"] + destino["sufixo"], error="H").matrix]
            a5(peca, os.path.join(AQUI, f"cartaz-{ds}-{lj}-a5.pdf"))
            a4_duas(peca, os.path.join(AQUI, f"cartaz-{ds}-{lj}-a4-2up.pdf"))
