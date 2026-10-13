"""English title logo over the original emblem (descriptor 2BB150: 30x20 tiles, 5 palettes; letters use palette 0).

Old letters (palette 0, indices 1-10 and 15) are erased; "ELEMIX!" is drawn from Roboto Condensed Bold with the
original's top-to-bottom gradient (sampled per row), a black (10) edge and a white (15) rim. Tiles that receive
letter pixels switch to palette 0 and their emblem pixels take the nearest palette-0 colour.

spec: {"desc": "2BB150", "kind": "logo", "text": "ELEMIX!", "box": [x0, y0, x1, y1], "size": 60,
       "bounce": [dy per letter], "shear": 0.18}
"""
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
TTF = ROOT / "font" / "Roboto_Condensed-Bold.ttf"
LETTER = set(range(1, 11)) | {15}
FILL = set(range(1, 10))


def split(im):
    """-> (pal rows, idx rows) per pixel."""
    w, h = im.w * 8, im.h * 8
    pal = [[0] * w for _ in range(h)]
    idx = [[0] * w for _ in range(h)]
    for i, e in enumerate(im.map):
        p = im.tile_pixels(e & 0x3FF)
        tx, ty = i % im.w, i // im.w
        for y in range(8):
            for x in range(8):
                v = p[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
                pal[ty * 8 + y][tx * 8 + x] = e >> 12
                idx[ty * 8 + y][tx * 8 + x] = v
    return pal, idx


def text_mask(e):
    from PIL import Image as P, ImageDraw, ImageFont
    f = ImageFont.truetype(str(TTF), e["size"], layout_engine=ImageFont.Layout.BASIC)
    bounce = e.get("bounce", [0] * len(e["text"]))
    W, H = 600, 200
    img = P.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    x = 10
    for c, dy in zip(e["text"], bounce):
        d.text((x, 40 + dy), c, font=f, fill=255)
        x += d.textlength(c, font=f) + e.get("spacing", -1)
    sh = e.get("shear", 0.0)
    img = img.transform(img.size, P.AFFINE, (1, sh, -sh * 100, 0, 1, 0), resample=P.BILINEAR)
    img = img.crop(img.getbbox())
    x0, y0, x1, y1 = e["box"]
    img = img.resize((x1 - x0, y1 - y0), P.LANCZOS)
    return [[img.getpixel((x, y)) >= 110 for x in range(img.width)] for y in range(img.height)]


def render(rom, e):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gfx import Image
    im = Image(rom, int(e["desc"], 16))
    pal, idx = split(im)
    w, h = im.w * 8, im.h * 8
    # gradient of the old letters: dominant fill index per row
    rows = {}
    for y in range(h):
        c = Counter(idx[y][x] for x in range(w) if pal[y][x] == 0 and idx[y][x] in FILL)
        if c:
            rows[y] = c.most_common(1)[0][0]
    oy0, oy1 = min(rows), max(rows)
    for y in range(h):
        for x in range(w):
            if pal[y][x] == 0 and idx[y][x] in LETTER or not e.get("keep_emblem", True):
                idx[y][x] = 0
    mask = text_mask(e)
    bx0, by0, bx1, by1 = e["box"]
    new = [[0] * w for _ in range(h)]
    for my, row in enumerate(mask):
        oy = oy0 + round(my * (oy1 - oy0) / max(1, len(mask) - 1))
        while oy not in rows:
            oy += 1
        for mx, v in enumerate(row):
            if v:
                new[by0 + my][bx0 + mx] = rows[oy]
    for ink in e.get("rings", [10, 15, 15]):  # 1 px black edge, then a 2 px white rim
        grown = [r[:] for r in new]
        for y in range(h):
            for x in range(w):
                if not new[y][x] and any(0 <= y + dy < h and 0 <= x + dx < w and new[y + dy][x + dx]
                                         for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    grown[y][x] = ink
        new = grown
    # palette per tile: 0 where new letters land, else original
    tpal = [[None] * im.w for _ in range(im.h)]
    for ty in range(im.h):
        for tx in range(im.w):
            has = any(new[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            tpal[ty][tx] = 0 if has else pal[ty * 8][tx * 8]
    rgb = lambda p, i: im.rgb(im.pals[p][i])
    p0 = [rgb(0, i) for i in range(16)]
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            t = tpal[y // 8][x // 8]
            if new[y][x]:
                out[y][x] = new[y][x]
            elif idx[y][x] and t == 0 and pal[y][x] != 0:
                c = rgb(pal[y][x], idx[y][x])
                out[y][x] = min(range(11, 15), key=lambda i: sum((a - b) ** 2 for a, b in zip(c, p0[i])))
            else:
                out[y][x] = idx[y][x]
    return im, out, tpal


def encode(px, tpal, wt, ht):
    tiles, index, mp = [bytes(32)], {bytes(32): 0}, []
    for ty in range(ht):
        for tx in range(wt):
            b = bytes(px[ty * 8 + y][tx * 8 + x] | px[ty * 8 + y][tx * 8 + x + 1] << 4 for y in range(8) for x in range(0, 8, 2))
            if b not in index:
                index[b] = len(tiles)
                tiles.append(b)
            mp.append(index[b] | (tpal[ty][tx] or 0) << 12)
    return b"".join(tiles), mp
