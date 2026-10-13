"""English redraws of image text (docs/re/graphics.md), written as new tiles + map into the expanded ROM.

script/graphics.json entries: {"desc": "2FB6D8", "kind": "caption", "jp": "...", "en": "line|line|..."}
  caption: transparent text layer (intro/ending); white text, black outline, lines centred on the original text.

    python -X utf8 tools/gfxtext.py preview OUTDIR     PNG of every entry (English over the original layer's size)
"""
import json, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font
from gfx import Image

ROOT = Path(__file__).resolve().parent.parent
SPECS = [ROOT / "script" / "graphics.json", ROOT / "script" / "tutorial.json", ROOT / "script" / "screens.json"]
MAX_TILES = {"caption": 512,   # BG1 char block 2, tile base 0 (gfxlog.lua)
             "page": 1024}     # BG0 char block 0, may run into block 1 (BG1 uses block 2)
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


def pixels(im):
    """Original image as rows of palette indices (map flips applied)."""
    w = im.w * 8
    px = blank(w, im.h * 8)
    for i, e in enumerate(im.map):
        p = im.tile_pixels(e & 0x3FF)
        if not p:
            continue
        tx, ty = i % im.w, i // im.w
        for y in range(8):
            for x in range(8):
                px[ty * 8 + y][tx * 8 + x] = p[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
    return px


ICON = re.compile(r"\{(\w+)\}")


def page(rom, e):
    """Full-screen page (tutorial): start from the original pixels, then run e["ops"] in order:
      {"clear": [x0, y0, x1, y1]}                       fill with e["bg"] (x1/y1 exclusive)
      {"text": "a|b", "x": X, "y": Y, "ink": I, "align": "left|center|right", "pitch": 16, "outline": O}
           x is the left edge, centre or right edge per align; y is the top of the first line's ink;
           {NAME} draws icon NAME = e["icons"][NAME] ([x0, y0, x1, y1] of the ORIGINAL image) inline.
           outline: draw `ink` and then an 8-neighbour edge in index O (footer labels)."""
    im = Image(rom, int(e["desc"], 16))
    return im, run_ops(pixels(im), e["ops"], e.get("icons", {}), e["bg"])


def run_ops(orig, ops, icons, bg):
    """Apply page ops (see page()) to a copy of orig; icons are rects in orig."""
    px = [r[:] for r in orig]
    g = glyphs()

    def seg_width(s):
        w = 0
        for i, part in enumerate(ICON.split(s)):
            w += (icons[part][2] - icons[part][0] + 1) if i % 2 else text_width(part, g)
        return w

    for op in ops:
        if "clear" in op:
            x0, y0, x1, y1 = op["clear"]
            for y in range(y0, y1):
                for x in range(x0, x1):
                    px[y][x] = bg
            continue
        pitch, align = op.get("pitch", 16), op.get("align", "left")
        layer = blank(len(px[0]), len(px)) if "outline" in op else px
        for li, line in enumerate(op["text"].split("|")):
            w = seg_width(line)
            x = op["x"] - (w // 2 if align == "center" else w if align == "right" else 0)
            y = op["y"] + li * pitch - 3          # glyph ink starts at font row 3
            for i, part in enumerate(ICON.split(line)):
                if i % 2:                          # icon: copy from the original, vertically centred on the caps
                    ix0, iy0, ix1, iy1 = icons[part]
                    top = y + 3 + 5 - (iy1 - iy0 + 1) // 2
                    top = max(0, min(top, len(px) - (iy1 - iy0 + 1)))
                    for yy in range(iy0, iy1 + 1):
                        for xx in range(ix0, ix1 + 1):
                            if orig[yy][xx] != bg:
                                px[top + yy - iy0][x + xx - ix0] = orig[yy][xx]
                    x += ix1 - ix0 + 1
                else:
                    if op.get("bold"):
                        draw_text(layer, part, x + 1, y, g, op["ink"])
                    x = draw_text(layer, part, x, y, g, op["ink"]) + (1 if op.get("bold") else 0)
        if "outline" in op:
            layer = outline(layer, op["ink"], op["outline"])
            for y, row in enumerate(layer):
                for x, v in enumerate(row):
                    if v:
                        px[y][x] = v
    return px


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
    if e["kind"] == "page":
        return page(rom, e)
    raise ValueError(e["kind"])


def check(rom, e):
    if e["kind"] == "pool":
        return pool_check(rom, e)
    im, px = render(rom, e)
    probs = []
    g = glyphs()
    texts = [e["en"]] if e["kind"] == "caption" else [ICON.sub("", op["text"]) for op in e["ops"] if "text" in op]
    for ln in (l for t in texts for l in t.split("|")):
        if set(ln) - set(g):
            probs.append(f"{e['desc']}: no glyph for {sorted(set(ln) - set(g))}")
        elif e["kind"] == "caption" and text_width(ln, g) + 2 > im.w * 8:
            probs.append(f"{e['desc']}: line {text_width(ln, g)} px wider than {im.w * 8 - 2}: {ln!r}")
    if e["kind"] == "page":
        icons = e.get("icons", {})
        for op in (o for o in e["ops"] if "text" in o):
            for ln in op["text"].split("|"):
                parts = ICON.split(ln)
                w = sum(icons[p][2] - icons[p][0] + 1 if i % 2 else text_width(p, g) for i, p in enumerate(parts))
                a = op.get("align", "left")
                lo = op["x"] - (w // 2 if a == "center" else w if a == "right" else 0)
                if lo < 2 or lo + w > im.w * 8 - 2 or lo + w > op.get("max_x", 999):
                    probs.append(f"{e['desc']}: {ln!r} spans x {lo}..{lo + w}")
    tiles, _ = encode(px, im.w, im.h)
    if len(tiles) // 32 > MAX_TILES[e["kind"]]:
        probs.append(f"{e['desc']}: {len(tiles) // 32} tiles > {MAX_TILES[e['kind']]}")
    return probs


def insert(rom, e, space):
    """Write new tiles + map for entry e; repoint its descriptor's tile pointer and map slot."""
    if e["kind"] == "pool":
        return pool_insert(rom, e, space)
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


def pool_render(rom, e):
    """Pool entry {"kind": "pool", "desc", "slots", "count", "bg": 0, "pieces": {"i": {"ops", "icons"}}}
    -> (Pool, [piece pixels]). Pieces without an entry are re-encoded unchanged."""
    from pool import Pool
    p = Pool(rom, int(e["desc"], 16), int(e["slots"], 16), e["count"])
    out = []
    for i in range(e["count"]):
        orig = p.piece_pixels(i)
        spec = e["pieces"].get(str(i))
        out.append(run_ops(orig, spec["ops"], spec.get("icons", {}), e["bg"]) if spec else orig)
    return p, out


def pool_encode(p, pieces):
    """Shared deduped tile block for all pieces -> (tile bytes, [map entries per piece])."""
    tiles, index, maps = [bytes(32)], {bytes(32): 0}, []
    for (w, h, _), px in zip(p.pieces, pieces):
        mp = []
        for ty in range(h):
            for tx in range(w):
                b = bytes(px[ty * 8 + y][tx * 8 + x] | px[ty * 8 + y][tx * 8 + x + 1] << 4
                          for y in range(8) for x in range(0, 8, 2))
                if b not in index:
                    index[b] = len(tiles)
                    tiles.append(b)
                mp.append(index[b])
        maps.append(mp)
    return b"".join(tiles), maps


def pool_check(rom, e):
    p, pieces = pool_render(rom, e)
    probs = []
    g = glyphs()
    for i, spec in e["pieces"].items():
        w = p.pieces[int(i)][0] * 8
        for op in (o for o in spec["ops"] if "text" in o):
            for ln in op["text"].split("|"):
                icons = spec.get("icons", {})
                parts = ICON.split(ln)
                if set("".join(parts[::2])) - set(g):
                    probs.append(f"pool {e['desc']} piece {i}: missing glyphs in {ln!r}")
                    continue
                lw = sum(icons[q][2] - icons[q][0] + 1 if k % 2 else text_width(q, g) for k, q in enumerate(parts))
                lw += len(parts[::2]) if op.get("bold") else 0
                a = op.get("align", "left")
                lo = op["x"] - (lw // 2 if a == "center" else lw if a == "right" else 0)
                if lo < 0 or lo + lw > w:
                    probs.append(f"pool {e['desc']} piece {i}: {ln!r} spans x {lo}..{lo + lw} of {w}")
    tiles, _ = pool_encode(p, pieces)
    if len(tiles) // 32 > p.img.size // 32:
        probs.append(f"pool {e['desc']}: {len(tiles) // 32} tiles > original {p.img.size // 32}")
    return probs


def pool_insert(rom, e, space):
    p, pieces = pool_render(rom, e)
    tiles, maps = pool_encode(p, pieces)
    t_at = space.alloc(4 + len(tiles))
    struct.pack_into("<I", rom, t_at, len(tiles))
    rom[t_at + 4:t_at + 4 + len(tiles)] = tiles
    struct.pack_into("<I", rom, p.img.desc, 0x08000000 + t_at)
    for slot, (w, h, _), mp in zip(p.slots, p.pieces, maps):
        m = struct.pack("<HH", w, h) + struct.pack(f"<{len(mp)}H", *mp)
        m_at = space.alloc(len(m))
        rom[m_at:m_at + len(m)] = m
        struct.pack_into("<I", rom, slot, 0x08000000 + m_at)


def load_spec(paths=SPECS):
    return [e for p in paths if Path(p).exists() for e in json.loads(Path(p).read_text(encoding="utf-8"))]


def preview(rom, out):
    from PIL import Image as P
    out.mkdir(parents=True, exist_ok=True)
    for e in load_spec():
        if e["kind"] == "pool":
            p, pieces = pool_render(rom, e)
            pal = [p.img.rgb(c) for c in p.img.pals[0]]
            pal[0] = (40, 40, 90)
            ims = [P.new("RGB", (len(px[0]), len(px))) for px in pieces]
            for im_, px in zip(ims, pieces):
                im_.putdata([pal[v] for row in px for v in row])
            sel = [int(i) for i in e["pieces"]]
            H = sum(ims[i].height * 2 + 4 for i in sel)
            sheet = P.new("RGB", (max(ims[i].width for i in sel) * 2, H))
            y = 0
            for i in sel:
                sheet.paste(ims[i].resize((ims[i].width * 2, ims[i].height * 2), P.NEAREST), (0, y))
                y += ims[i].height * 2 + 4
            sheet.save(out / f"pool_{e['desc']}.png")
            continue
        im, px = render(rom, e)
        pal = [im.rgb(c) for c in im.pals[0]]
        pal[0] = (40, 40, 90)
        img = P.new("RGB", (im.w * 8, im.h * 8))
        img.putdata([pal[v] for row in px for v in row])
        img.resize((im.w * 16, im.h * 16), P.NEAREST).save(out / f"{e['desc']}.png")


if __name__ == "__main__":
    rom = (ROOT / "rom" / "Elemix! (Japan).gba").read_bytes()
    if sys.argv[1] == "preview":
        preview(rom, Path(sys.argv[2]))
        for e in load_spec():
            print("\n".join(check(rom, e)) or f"{e['desc']} ok")
