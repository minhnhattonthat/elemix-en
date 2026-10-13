"""Tile pools with many small map pieces (options/records/erase-save screens): one tile block + palette shared by
`count` map slots starting at `slots`; each slot -> {u16 w, u16 h, u16 entry[w*h]} drawn by code at a fixed spot.

    python -X utf8 tools/pool.py sheet ROM DESC SLOTS COUNT OUT.png     labelled render of every piece
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gfx import Image, u16, u32, rp


class Pool:
    def __init__(self, d, desc, slots, count):
        self.img = Image(d, desc)              # tile block + palette (its own map is piece 0)
        self.slots = [slots + 4 * i for i in range(count)]
        self.pieces = []
        for s in self.slots:
            m = rp(d, u32(d, s))
            w, h = u16(d, m), u16(d, m + 2)
            self.pieces.append((w, h, list(struct.unpack_from(f"<{w * h}H", d, m + 4))))

    def piece_pixels(self, i):
        w, h, ents = self.pieces[i]
        px = [[0] * (w * 8) for _ in range(h * 8)]
        for k, e in enumerate(ents):
            p = self.img.tile_pixels(e & 0x3FF)
            if not p:
                continue
            tx, ty = k % w, k // w
            for y in range(8):
                for x in range(8):
                    px[ty * 8 + y][tx * 8 + x] = p[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
        return px

    def sheet(self, out, zoom=2):
        from PIL import Image as P, ImageDraw
        pal = [self.img.rgb(c) for c in self.img.pals[0]]
        pal[0] = (60, 60, 110)
        rows = []
        for i in range(len(self.pieces)):
            px = self.piece_pixels(i)
            im = P.new("RGB", (len(px[0]), len(px)))
            im.putdata([pal[v] for r in px for v in r])
            rows.append(im.resize((im.width * zoom, im.height * zoom), P.NEAREST))
        W = max(r.width for r in rows) + 40
        H = sum(r.height + 4 for r in rows)
        s = P.new("RGB", (W, H), (20, 20, 20))
        dr = ImageDraw.Draw(s)
        y = 0
        for i, r in enumerate(rows):
            dr.text((2, y), str(i), fill="yellow")
            s.paste(r, (36, y))
            y += r.height + 4
        s.save(out)


if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        d = open(sys.argv[2], "rb").read()
        Pool(d, int(sys.argv[3], 16), int(sys.argv[4], 16), int(sys.argv[5])).sheet(sys.argv[6])
