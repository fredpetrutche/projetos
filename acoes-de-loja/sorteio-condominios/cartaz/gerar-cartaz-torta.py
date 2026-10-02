# -*- coding: utf-8 -*-
"""Cartaz do sorteio — versão 2: a torta cookie de 8 fatias.

Identidade da Holy Cook: fundo rosa, marrom, pílula creme, Lilita One nos
títulos. O QR é o mesmo que já está em circulação (v8, correção H, máscara 4).
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
URL = "https://fredpetrutche.github.io/projetos/acoes-de-loja/sorteio-condominios/cadastro/"

ROSA   = HexColor("#FBD4D9")
MARROM = HexColor("#4A2B20")
CREME  = HexColor("#FDE6C9")
LARANJA = HexColor("#EE5A24")
BRANCO = HexColor("#FFFFFF")
QR_COR = HexColor("#4A2B20")

pdfmetrics.registerFont(TTFont("Lilita", os.path.join(AQUI, "fontes", "LilitaOne-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Poppins-Med", os.path.join(AQUI, "fontes", "Poppins-Medium.ttf")))

MATRIX = [list(r) for r in segno.make(URL, error="H", mask=4, boost_error=False).matrix]
N = len(MATRIX)

FOTO = os.path.join(AQUI, "..", "img", "torta-fatia.jpg")
LOGO = os.path.join(AQUI, "..", "img", "holy-cook-logo.png")
_logo_img = Image.open(LOGO)
LOGO_RAZAO = _logo_img.width / _logo_img.height
_foto_img = Image.open(FOTO)
FOTO_RAZAO = _foto_img.width / _foto_img.height


def cap(fonte, tam):
    """Altura de caixa alta, que é o que importa para empilhar títulos."""
    return pdfmetrics.getAscent(fonte) / 1000.0 * tam * 0.72


def tamanho_para_largura(texto, fonte, largura):
    base = pdfmetrics.stringWidth(texto, fonte, 100)
    return 100.0 * largura / base


def desenha_qr(c, x, y, lado):
    m = lado / N
    c.setFillColor(QR_COR)
    for r, linha in enumerate(MATRIX):
        col = 0
        while col < N:
            if linha[col]:
                ini = col
                while col < N and linha[col]:
                    col += 1
                c.rect(x + ini * m, y + lado - (r + 1) * m, (col - ini) * m, m, stroke=0, fill=1)
            else:
                col += 1


def foto_arredondada(c, x, y, larg, alt, raio):
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, larg, alt, raio)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(FOTO, x, y, larg, alt, mask=None)
    c.restoreState()


def cartaz(arquivo, larg_mm, alt_mm):
    W, H = larg_mm * mm, alt_mm * mm
    s = larg_mm / 210.0
    margem = 0.072 * W
    cw = W - 2 * margem
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle("Concorra a uma torta cookie — Holy Cook")
    c.setFillColor(ROSA)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # ── tipografia: o título manda, o resto deriva dele ──────────────
    h1 = tamanho_para_largura("TORTA COOKIE", "Lilita", cw)
    f_chapeu = h1 * 0.335
    f_fatias = h1 * 0.56
    f_kg     = h1 * 0.335
    f_pilula = h1 * 0.175

    a_chapeu = cap("Lilita", f_chapeu)
    a_h1     = cap("Lilita", h1)
    a_fatias = cap("Lilita", f_fatias)
    a_kg     = cap("Lilita", f_kg)

    g_chapeu = 0.30 * a_chapeu      # chapéu → título
    g_fatias = 0.32 * a_fatias
    g_kg     = 0.34 * a_kg
    g_foto   = 3.2 * mm * s + 0.30 * a_kg
    g_pilula = 7.0 * mm * s
    g_card   = 5.5 * mm * s
    g_logo   = 6.0 * mm * s

    alt_pilula = f_pilula * 2.05
    alt_logo   = 0.12 * W
    alt_foto   = cw / FOTO_RAZAO
    pad_card   = 5.0 * mm * s

    fixo = (a_chapeu + g_chapeu + a_h1 + g_fatias + a_fatias + g_kg + a_kg
            + g_foto + alt_foto + g_pilula + alt_pilula + g_card
            + g_logo + alt_logo)
    # o card do QR fica com a folga que sobrou, dentro de limites sensatos
    disponivel = H - 2 * (0.075 * H) - fixo
    lado_card = max(0.40 * W, min(disponivel, 0.72 * W))
    qr_lado = lado_card - 2 * pad_card

    bloco = fixo + lado_card
    topo = H - (H - bloco) * 0.46

    y = topo - a_chapeu
    c.setFont("Lilita", f_chapeu); c.setFillColor(MARROM)
    c.drawCentredString(W / 2, y, "CONCORRA A UMA")

    y -= g_chapeu + a_h1
    c.setFont("Lilita", h1)
    c.drawCentredString(W / 2, y, "TORTA COOKIE")

    y -= g_fatias + a_fatias
    c.setFont("Lilita", f_fatias)
    c.drawCentredString(W / 2, y, "DE 8 FATIAS")

    y -= g_kg + a_kg
    c.setFont("Lilita", f_kg); c.setFillColor(LARANJA)
    c.drawCentredString(W / 2, y, "DE 1,7 KG")

    y -= g_foto + alt_foto
    foto_arredondada(c, margem, y, cw, alt_foto, 4.0 * mm * s)

    texto_pilula = "Leia o QR Code para participar"
    larg_pilula = pdfmetrics.stringWidth(texto_pilula, "Poppins-Med", f_pilula) + 2 * (f_pilula * 1.1)
    y -= g_pilula + alt_pilula
    c.setFillColor(CREME)
    c.roundRect((W - larg_pilula) / 2, y, larg_pilula, alt_pilula, alt_pilula / 2, stroke=0, fill=1)
    c.setFillColor(MARROM); c.setFont("Poppins-Med", f_pilula)
    c.drawCentredString(W / 2, y + alt_pilula / 2 - f_pilula * 0.35, texto_pilula)

    y -= g_card + lado_card
    c.setFillColor(BRANCO)
    c.roundRect((W - lado_card) / 2, y, lado_card, lado_card, 5.5 * mm * s, stroke=0, fill=1)
    desenha_qr(c, (W - qr_lado) / 2, y + pad_card, qr_lado)

    y -= g_logo + alt_logo
    c.drawImage(ImageReader(LOGO), (W - alt_logo * LOGO_RAZAO) / 2, y,
                alt_logo * LOGO_RAZAO, alt_logo, mask="auto")

    c.showPage(); c.save()
    print(f"ok {arquivo} {larg_mm}x{alt_mm}mm | título {h1/mm*0.72:.1f}mm | "
          f"foto {alt_foto/mm:.0f}mm | QR {qr_lado/mm:.0f}mm | logo {alt_logo/mm:.0f}mm | "
          f"margem topo {(H-bloco)*0.46/mm:.1f}mm")


if __name__ == "__main__":
    cartaz(os.path.join(AQUI, "cartaz-torta-a4.pdf"), 210, 297)
    cartaz(os.path.join(AQUI, "cartaz-torta-10x15.pdf"), 100, 150)
    cartaz(os.path.join(AQUI, "cartaz-torta-a6.pdf"), 105, 148)
