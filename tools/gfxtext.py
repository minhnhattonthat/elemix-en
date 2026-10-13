"""English redraws of image text (docs/re/graphics.md), written as new tiles + map into the expanded ROM.

script/graphics.json entries: {"desc": "2FB6D8", "kind": "caption", "jp": "...", "en": "line|line|..."}
  caption: transparent text layer (intro/ending); white text, black outline, lines centred on the original text.

    python -X utf8 tools/gfxtext.py preview OUTDIR     PNG of every entry (English over the original layer's size)
"""
import json, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font
from gfx import Image

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "script" / "graphics.json"
MAX_TILES = {"caption": 512}   # BG1 char block 2, tile base 0 (gfxlog.lua)
LINE_H = 16                    # caption line pitch in px (font ink: caps rows 3-12, descenders 13-14)


def glyphs():
    return font.load_en()


def text_width(s, g):
    return sum(g[c][1] for c in s)


def blank(w, h):
    return [[0] * w for _ in range(h)]


def draw_text(px, s, x, y, g, ink):
    for c in s:
        rows, adv = g[c]
        for ry, row in enumerate(rows):
            for rx, v in enumerate(row):
                if v and 0 <= y + ry < len(px) and 0 <= x + rx < len(px[0]):
                    px[y + ry][x + rx] = ink
        x += adv
    return x


def outline(px, fill, edge, shadow=None):
    """Add an 8-neighbour edge around `fill` pixels (and an optional +1,+1 shadow colour beyond it)."""
    h, w = len(px), len(px[0])
    out = [r[:] for r in px]
    for y in range(h):
        for x in range(w):
            if px[y][x] != fill:
                continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and out[yy][xx] == 0:
                        out[yy][xx] = edge
    if shadow is not None:
        res = [r[:] for r in out]
        for y in range(h - 1):
            for x in range(w - 1):
                if out[y][x] and not out[y + 1][x + 1]:
                    res[y + 1][x + 1] = shadow
        out = res
    return out


def ink_rows(im):
    """(top, bottom) pixel rows holding non-zero pixels in the original image."""
    rows = set()
    for i, e in enumerate(im.map):
        p = im.tile_pixels(e & 0x3FF)
        if p and any(any(r) for r in p):
            ty = i // im.w
            for y, r in enumerate(p):
                if any(r):
                    rows.add(ty * 8 + (7 - y if e & 0x800 else y))
    return (min(rows), max(rows)) if rows else (0, im.h * 8)


def caption(rom, e):
    im = Image(rom, int(e["desc"], 16))
    g = glyphs()
    w, h = im.w * 8, im.h * 8
    lines = e["en"].split("|")
    top, bot = ink_rows(im)
    y0 = (top + bot) // 2 - (len(lines) * LINE_H) // 2 - 3  # glyph ink starts at row 3
    px = blank(w, h)
    for i, ln in enumerate(lines):
        lw = text_width(ln, g)
        draw_text(px, ln, (w - lw) // 2, y0 + i * LINE_H, g, 1)
    return im, outline(px, 1, 7)


def encode(px, w_tiles, h_tiles, pal=0):
    """Index image -> (tile bytes, map entries). Tile 0 is the blank tile."""
    tiles, index, mp = [bytes(32)], {bytes(32): 0}, []
    for ty in range(h_tiles):
        for tx in range(w_tiles):
            b = bytearray()
            for y in range(8):
                row = px[ty * 8 + y]
                for x in range(0, 8, 2):
                    b.append(row[tx * 8 + x] | row[tx * 8 + x + 1] << 4)
            b = bytes(b)
            if b not in index:
                index[b] = len(tiles)
                tiles.append(b)
            mp.append(index[b] | pal << 12)
    return b"".join(tiles), mp


def render(rom, e):
    """-> (Image of the original, index pixels)"""
    if e["kind"] == "caption":
        return caption(rom, e)
    raise ValueError(e["kind"])


def check(rom, e):
    im, px = render(rom, e)
    probs = []
    g = glyphs()
    for ln in e["en"].split("|"):
        if set(ln) - set(g):
            probs.append(f"{e['desc']}: no glyph for {sorted(set(ln) - set(g))}")
        elif text_width(ln, g) + 2 > im.w * 8:
            probs.append(f"{e['desc']}: line {text_width(ln, g)} px wider than {im.w * 8 - 2}: {ln!r}")
    tiles, _ = encode(px, im.w, im.h)
    if len(tiles) // 32 > MAX_TILES[e["kind"]]:
        probs.append(f"{e['desc']}: {len(tiles) // 32} tiles > {MAX_TILES[e['kind']]}")
    return probs


def insert(rom, e, space):
    """Write new tiles + map for entry e; repoint its descriptor's tile pointer and map slot."""
    im, px = render(rom, e)
    tiles, mp = encode(px, im.w, im.h)
    t_at = space.alloc(4 + len(tiles))
    struct.pack_into("<I", rom, t_at, len(tiles))
    rom[t_at + 4:t_at + 4 + len(tiles)] = tiles
    m = struct.pack("<HH", im.w, im.h) + struct.pack(f"<{len(mp)}H", *mp)
    m_at = space.alloc(len(m))
    rom[m_at:m_at + len(m)] = m
    struct.pack_into("<I", rom, im.desc, 0x08000000 + t_at)
    struct.pack_into("<I", rom, im.mslot, 0x08000000 + m_at)


def load_spec(path=SPEC):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else []


def preview(rom, out):
    from PIL import Image as P
    pal = {0: (40, 40, 90), 1: (255, 255, 255), 7: (0, 0, 0), 6: (60, 60, 60)}
    out.mkdir(parents=True, exist_ok=True)
    for e in load_spec():
        im, px = render(rom, e)
        img = P.new("RGB", (im.w * 8, im.h * 8))
        img.putdata([pal.get(v, (255, 0, 255)) for row in px for v in row])
        img.resize((im.w * 16, im.h * 16), P.NEAREST).save(out / f"{e['desc']}.png")


if __name__ == "__main__":
    rom = (ROOT / "rom" / "Elemix! (Japan).gba").read_bytes()
    if sys.argv[1] == "preview":
        preview(rom, Path(sys.argv[2]))
        for e in load_spec():
            print("\n".join(check(rom, e)) or f"{e['desc']} ok")
