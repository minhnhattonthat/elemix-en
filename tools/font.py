"""Dialogue font: 16x16 1bpp glyphs (4 tiles of 8 bytes: TL, TR, BL, BR), glyph = FONT + code * 32.

English glyphs come from font/en_vwf.txt (16 rows, '#' = ink, row width = advance incl. 1 px spacing) and go to
codes EN_BASE + ord(c) - 0x20 in a relocated font; Japanese glyphs keep their codes and a 13 px advance.

    python -X utf8 tools/font.py sheet ROM OUT.png [--first N] [--count N] [--cols 32]   numbered glyph sheet
"""
import argparse
from pathlib import Path

FONT = 0x352B74
GLYPH = 32
EN_BASE = 0x200
CODES = 0x260          # relocated font size in glyphs (0x000-0x1FF Japanese area, 0x200-0x25F ASCII 0x20-0x7F)
JP_ADVANCE = 13
ROOT = Path(__file__).resolve().parent.parent
EN_FONT = ROOT / "font" / "en_vwf.txt"


def glyph_pixels(rom, code, base=FONT):
    """16x16 list of rows of 0/1."""
    g = rom[base + code * GLYPH:base + (code + 1) * GLYPH]
    rows = [[0] * 16 for _ in range(16)]
    for t, (ox, oy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
        for y in range(8):
            b = g[t * 8 + y]
            for x in range(8):
                rows[oy + y][ox + x] = (b >> (7 - x)) & 1
    return rows


def pack_glyph(rows):
    out = bytearray()
    for ox, oy in ((0, 0), (8, 0), (0, 8), (8, 8)):
        for y in range(8):
            b = 0
            for x in range(8):
                b = b << 1 | rows[oy + y][ox + x]
            out.append(b)
    return bytes(out)


def load_en(path=EN_FONT):
    """{char: (rows 16x16, advance)}"""
    glyphs, name, rows = {}, None, []

    def flush():
        if name is not None:
            assert len(rows) == 16, f"glyph {name!r}: {len(rows)} rows"
            w = len(rows[0])
            assert all(len(r) == w for r in rows) and w <= 16, f"glyph {name!r}: ragged or too wide"
            glyphs[" " if name == "space" else name] = ([[c == "#" for c in r] + [0] * (16 - w) for r in rows], w)

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith(";") or line.startswith("#") and not set(line) <= set("#."):
            continue
        if line.startswith("char "):
            flush()
            name, rows = line[5:], []
        elif line:
            rows.append(line)
    flush()
    return glyphs


def en_codes():
    """{char: code} for every English glyph."""
    return {c: EN_BASE + ord(c) - 0x20 for c in load_en()}


def build_font(rom):
    """(font bytes for CODES glyphs, width table bytes)."""
    font = bytearray(rom[FONT:FONT + EN_BASE * GLYPH]) + bytes((CODES - EN_BASE) * GLYPH)
    widths = bytearray([JP_ADVANCE] * CODES)
    for c, (rows, w) in load_en().items():
        code = EN_BASE + ord(c) - 0x20
        assert EN_BASE <= code < CODES, c
        font[code * GLYPH:(code + 1) * GLYPH] = pack_glyph([[int(v) for v in r] for r in rows])
        widths[code] = w
    return bytes(font), bytes(widths)


def sheet(rom, out, first, count, cols, zoom=2, base=FONT):
    from PIL import Image, ImageDraw
    cell = 16 * zoom + 2
    rows_n = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * cell + 48, rows_n * cell), "white")
    d = ImageDraw.Draw(img)
    for i in range(count):
        code = first + i
        r, c = divmod(i, cols)
        x0, y0 = 40 + c * cell, r * cell
        if c == 0:
            d.text((0, y0 + 8), f"{code:03X}", fill="red")
        for y, row in enumerate(glyph_pixels(rom, code, base)):
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
    ap.add_argument("--base", type=lambda s: int(s, 0), default=FONT, help="font file offset (built ROM: NEW_FONT)")
    a = ap.parse_args()
    sheet(open(a.rom, "rb").read(), a.out, a.first, a.count, a.cols, base=a.base)
