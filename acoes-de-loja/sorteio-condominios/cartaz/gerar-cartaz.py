# -*- coding: utf-8 -*-
"""Cartaz do sorteio — versão 1: só tipografia e o QR, em A4, A6 e 10x15."""
import os
import segno
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://fredpetrutche.github.io/projetos/acoes-de-loja/sorteio-condominios/cadastro/"
INK   = HexColor("#1C140C")
MARCA = HexColor("#9C2B1B")
PAPEL = HexColor("#FFFFFF")

HN = "/System/Library/Fonts/HelveticaNeue.ttc"
pdfmetrics.registerFont(TTFont("HN-Bold", HN, subfontIndex=1))
pdfmetrics.registerFont(TTFont("HN-Medium", HN, subfontIndex=10))
BOLD, MED = "HN-Bold", "HN-Medium"

# mesmos modulos do QR que ja esta em circulacao (v8, erro H, mascara 4)
MATRIX = [list(r) for r in segno.make(URL, error="H", mask=4, boost_error=False).matrix]
N = len(MATRIX)

def centro(c, txt, font, size, y, cor):
    c.setFont(font, size); c.setFillColor(cor)
    c.drawCentredString(c._pagesize[0] / 2, y, txt)

def altura_cap(font, size):
    return pdfmetrics.getAscent(font) / 1000.0 * size * 0.72

def desenha_qr(c, x, y, lado):
    """QR vetorial: um retangulo por corrida de modulos escuros."""
    m = lado / N
    c.setFillColor(INK)
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
    c = canvas.Canvas(arquivo, pagesize=(W, H))
    c.setTitle("Participe do sorteio — Holy Cook")
    c.setFillColor(PAPEL); c.rect(0, 0, W, H, stroke=0, fill=1)

    s = larg_mm / 210.0           # escala relativa ao A4
    f_chapeu  = 30 * s            # "PARTICIPE DO"
    f_titulo  = 86 * s            # "SORTEIO"
    f_instr   = 27 * s            # "Leia o QR Code"
    f_marca   = 34 * s            # "Holy Cook"

    # alturas do bloco, de cima para baixo
    h_chapeu = altura_cap(BOLD, f_chapeu)
    h_titulo = altura_cap(BOLD, f_titulo)
    h_instr  = altura_cap(MED, f_instr)
    h_marca  = altura_cap(BOLD, f_marca)
    g1 = 5.0 * mm * s   # chapeu -> titulo
    g2 = 9.0 * mm * s   # titulo -> regua
    g3 = 8.0 * mm * s   # regua -> instrucao
    g4 = 12.0 * mm * s  # instrucao -> QR
    g5 = 9.0 * mm * s   # QR -> Holy Cook
    regua = 1.6 * mm * s

    # o QR cresce para o bloco ocupar ~80% da altura, com teto de 66% da largura
    sem_qr = h_chapeu + g1 + h_titulo + g2 + regua + g3 + h_instr + g4 + g5 + h_marca
    qr_lado = min(0.66 * W, 0.80 * H - sem_qr)
    bloco = sem_qr + qr_lado
    sobra = H - bloco
    topo = H - sobra * 0.45        # respiro ligeiramente maior embaixo

    y = topo - h_chapeu
    c.setFont(BOLD, f_chapeu); c.setFillColor(MARCA)
    c.drawCentredString(W / 2, y, "PARTICIPE DO")

    y -= g1 + h_titulo
    c.setFont(BOLD, f_titulo); c.setFillColor(INK)
    c.drawCentredString(W / 2, y, "SORTEIO")

    y -= g2 + regua
    c.setFillColor(MARCA)
    c.rect((W - 0.17 * W) / 2, y, 0.17 * W, regua, stroke=0, fill=1)

    y -= g3 + h_instr
    centro(c, "Leia o QR Code", MED, f_instr, y, INK)

    y -= g4 + qr_lado
    desenha_qr(c, (W - qr_lado) / 2, y, qr_lado)

    y -= g5 + h_marca
    centro(c, "Holy Cook", BOLD, f_marca, y, MARCA)

    c.showPage(); c.save()
    print("ok", arquivo, f"{larg_mm}x{alt_mm}mm", "QR", round(qr_lado/mm, 1), "mm")

if __name__ == "__main__":
    cartaz(os.path.join(AQUI, "cartaz-sorteio-a4.pdf"), 210, 297)
    cartaz(os.path.join(AQUI, "cartaz-sorteio-10x15.pdf"), 100, 150)
    cartaz(os.path.join(AQUI, "cartaz-sorteio-a6.pdf"), 105, 148)
