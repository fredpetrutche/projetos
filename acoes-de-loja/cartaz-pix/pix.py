# -*- coding: utf-8 -*-
"""Monta o BR Code (EMV QRCPS-MPM) de um PIX estático."""

def crc16(dados: str) -> str:
    """CRC-16/CCITT-FALSE, que é o exigido pelo BR Code."""
    crc = 0xFFFF
    for b in dados.encode("utf-8"):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def campo(tag: str, valor: str) -> str:
    return f"{tag}{len(valor):02d}{valor}"


def payload_pix(chave, nome, cidade, valor=None, txid="***", descricao=None):
    conta = campo("00", "BR.GOV.BCB.PIX") + campo("01", chave)
    if descricao:
        conta += campo("02", descricao)
    p  = campo("00", "01")
    p += campo("26", conta)
    p += campo("52", "0000")
    p += campo("53", "986")
    if valor is not None:
        p += campo("54", f"{valor:.2f}")
    p += campo("58", "BR")
    p += campo("59", nome[:25])
    p += campo("60", cidade[:15])
    p += campo("62", campo("05", txid))
    p += "6304"
    return p + crc16(p)


def ler_tlv(s, prefixo=""):
    i, saida = 0, []
    while i < len(s):
        tag = s[i:i+2]; n = int(s[i+2:i+4]); valor = s[i+4:i+4+n]
        saida.append((prefixo + tag, n, valor))
        if tag in ("26", "62"):
            saida += ler_tlv(valor, prefixo + tag + ".")
        i += 4 + n
    return saida


if __name__ == "__main__":
    assert crc16("123456789") == "29B1", crc16("123456789")   # vetor de teste padrão
    p = payload_pix("58517200000104", "HOLY COOK", "PAULINIA")
    print(p)
    print("tamanho:", len(p))
    for tag, n, v in ler_tlv(p):
        print(f"  {tag:7s} ({n:2d})  {v}")
    assert crc16(p[:-4]) == p[-4:]
    print("CRC confere:", p[-4:])
