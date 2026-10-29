"""Maakt de knopiconen in resources/ (16, 32 en 64 px): plaat met gat en een stip in het midden.

Draaien: python tools/maak_iconen.py  (vraagt Pillow)
"""
import os
from PIL import Image, ImageDraw

MAP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
GROOT = 256


def teken():
    im = Image.new('RGBA', (GROOT, GROOT), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16, 16, 240, 240), radius=28, fill=(148, 163, 184, 255))
    d.ellipse((56, 56, 200, 200), fill=(0, 0, 0, 0))
    d.ellipse((56, 56, 200, 200), outline=(71, 85, 105, 255), width=14)
    d.line((96, 128, 160, 128), fill=(220, 38, 38, 255), width=24)
    d.line((128, 96, 128, 160), fill=(220, 38, 38, 255), width=24)
    return im


def main():
    os.makedirs(MAP, exist_ok=True)
    im = teken()
    for px in (16, 32, 64):
        im.resize((px, px), Image.LANCZOS).save(os.path.join(MAP, '%dx%d.png' % (px, px)))
    print('Iconen geschreven naar', MAP)


if __name__ == '__main__':
    main()
