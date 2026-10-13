"""Dialogue font: 16x16 1bpp glyphs (4 tiles of 8 bytes: TL, TR, BL, BR), glyph = FONT + code * 32.

    python -X utf8 tools/font.py sheet ROM OUT.png [--first N] [--count N] [--cols 32]   numbered glyph sheet
"""
import argparse
from PIL import Image, ImageDraw

FONT = 0x352B74
GLYPH = 32


def glyph_pixels(rom, code):
    """16x16 list of rows of 0/1."""
    g = rom[FONT + code * GLYPH:FONT + (code + 1) * GLYPH]
    rows = [[0] * 16 for _ in range(16)]
    for t, (ox, oy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
        for y in range(8):
            b = g[t * 8 + y]
            for x in range(8):
                rows[oy + y][ox + x] = (b >> (7 - x)) & 1
    return rows


def sheet(rom, out, first, count, cols, zoom=2):
    cell = 16 * zoom + 2
    lab = 14
    rows_n = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * cell + lab * 2 + 20, rows_n * cell), "white")
    d = ImageDraw.Draw(img)
    for i in range(count):
        code = first + i
        r, c = divmod(i, cols)
        x0, y0 = 40 + c * cell, r * cell
        if c == 0:
            d.text((0, y0 + 8), f"{code:03X}", fill="red")
        for y, row in enumerate(glyph_pixels(rom, code)):
            for x, v in enumerate(row):
                if v:
                    d.rectangle((x0 + x * zoom, y0 + y * zoom, x0 + x * zoom + zoom - 1, y0 + y * zoom + zoom - 1), fill="black")
        d.rectangle((x0 - 1, y0 - 1, x0 + 16 * zoom, y0 + 16 * zoom), outline=(200, 200, 255))
    img.save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sheet"])
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=512)
    ap.add_argument("--cols", type=int, default=32)
    a = ap.parse_args()
    sheet(open(a.rom, "rb").read(), a.out, a.first, a.count, a.cols)
