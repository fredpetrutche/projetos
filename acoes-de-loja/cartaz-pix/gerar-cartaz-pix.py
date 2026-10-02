# -*- coding: utf-8 -*-
"""Cartaz do PIX do balcão — A4, A6 e 10x15, na identidade da Holy Cook.

O QR é um BR Code estático (sem valor): o cliente lê, digita quanto vai pagar
e confirma. A chave é o CNPJ da loja de Paulínia. O payload é montado em
pix.py, que valida o CRC contra o vetor de teste do padrão.
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

from pix import payload_pix

AQUI = os.path.dirname(os.path.abspath(__file__))

CHAVE  = "58517200000104"           # CNPJ 58.517.200/0001-04 — Holy Cook Paulínia
CHAVE_VISIVEL = "58.517.200/0001-04"
NOME   = "HOLY COOK"
CIDADE = "PAULINIA"

ROSA   = HexColor("#FBD4D9")
MARROM = HexColor("#4A2B20")
CREME  = HexColor("#FDE6C9")
TEAL   = HexColor("#32BCAD")        # o verde do Pix, que é o que o olho procura
BRANCO = HexColor("#FFFFFF")

pdfmetrics.registerFont(TTFont("Lilita", os.path.join(AQUI, "fontes", "LilitaOne-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Poppins-Med", os.path.join(AQUI, "fontes", "Poppins-Medium.ttf")))

PAYLOAD = payload_pix(CHAVE, NOME, CIDADE)
MATRIX = [list(r) for r in segno.make(PAYLOAD, error="H", boost_error=False).matrix]
N = len(MATRIX)

LOGO = os.path.join(AQUI, "img", "holy-cook-logo.png")
_logo = Image.open(LOGO)
LOGO_RAZAO = _logo.width / _logo.height


def cap(fonte, tam):
    return pdfmetrics.getAscent(fonte) / 1000.0 * tam * 0.72


def tamanho_para_largura(texto, fonte, largura):
    return 100.0 * largura / pdfmetrics.stringWidth(texto, fonte, 100)


def desenha_qr(c, x, y, lado):
    m = lado / N
    c.setFillColor(MARROM)
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


def cartaz(arquivo, larg_mm, alt_mm):
    W, H = larg_mm * mm, alt_mm * mm
    s = larg_mm / 210.0
    margem = 0.072 * W
    cw = W - 2 * margem
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle("Pague com Pix — Holy Cook")
    c.setFillColor(ROSA); c.rect(0, 0, W, H, stroke=0, fill=1)

    f_pix    = tamanho_para_largura("PIX", "Lilita", 0.42 * cw)
    f_chapeu = f_pix * 0.40
    f_pilula = f_pix * 0.125
    f_chave  = f_pix * 0.105

    a_chapeu = cap("Lilita", f_chapeu)
    a_pix    = cap("Lilita", f_pix)

    g_pix    = 0.26 * a_chapeu
    g_pilula = 8.0 * mm * s
    g_card   = 6.0 * mm * s
    g_chave  = 6.0 * mm * s
    g_logo   = 7.0 * mm * s

    alt_pilula = f_pilula * 2.05
    alt_chave  = f_chave * 0.72
    alt_logo   = 0.13 * W
    pad_card   = 5.5 * mm * s

    fixo = (a_chapeu + g_pix + a_pix + g_pilula + alt_pilula + g_card
            + g_chave + alt_chave + g_logo + alt_logo)
    disponivel = H - 2 * (0.085 * H) - fixo
    lado_card = max(0.44 * W, min(disponivel, 0.76 * W))
    qr_lado = lado_card - 2 * pad_card

    bloco = fixo + lado_card
    topo = H - (H - bloco) * 0.46

    y = topo - a_chapeu
    c.setFont("Lilita", f_chapeu); c.setFillColor(MARROM)
    c.drawCentredString(W / 2, y, "PAGUE COM")

    y -= g_pix + a_pix
    c.setFont("Lilita", f_pix); c.setFillColor(TEAL)
    c.drawCentredString(W / 2, y, "PIX")

    texto_pilula = "Aponte a câmera do seu banco"
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

    y -= g_chave + alt_chave
    c.setFillColor(MARROM); c.setFont("Poppins-Med", f_chave)
    c.drawCentredString(W / 2, y, "Chave Pix · CNPJ " + CHAVE_VISIVEL)

    y -= g_logo + alt_logo
    c.drawImage(ImageReader(LOGO), (W - alt_logo * LOGO_RAZAO) / 2, y,
                alt_logo * LOGO_RAZAO, alt_logo, mask="auto")

    c.showPage(); c.save()
    print(f"ok {os.path.basename(arquivo)} {larg_mm}x{alt_mm}mm | QR {qr_lado/mm:.0f}mm | "
          f"logo {alt_logo/mm:.0f}mm | margem topo {(H-bloco)*0.46/mm:.1f}mm")


if __name__ == "__main__":
    print("payload:", PAYLOAD)
    cartaz(os.path.join(AQUI, "cartaz-pix-a4.pdf"), 210, 297)
    cartaz(os.path.join(AQUI, "cartaz-pix-10x15.pdf"), 100, 150)
    cartaz(os.path.join(AQUI, "cartaz-pix-a6.pdf"), 105, 148)
