"""Uncompressed BG images: 12-byte descriptor {u32 tiles, u32 map-slot, u32 palettes} (GBA pointers).
  tiles    -> {u32 size, 4bpp tiles[size]}           (DMA'd by 0x0800216C)
  map-slot -> u32 -> {u16 w, u16 h, u16 entry[w*h]} (entry: tile 0-9, hflip 10, vflip 11, palette 12-15, all
                                                     relative to this image's tiles and palettes; 0x080021DC)
  palettes -> {u16 count, u16 bgr555[count*16]}

    python -X utf8 tools/gfx.py scan ROM                     list descriptors
    python -X utf8 tools/gfx.py render ROM DESC OUT.png      render one image (DESC = hex file offset)
    python -X utf8 tools/gfx.py sheet ROM OUTDIR             render every image whose map is at least 8x4 tiles
"""
import struct, sys
from pathlib import Path


def u32(d, a): return struct.unpack_from("<I", d, a)[0]
def u16(d, a): return struct.unpack_from("<H", d, a)[0]


def rp(d, v):
    return v - 0x08000000 if 0x08000000 <= v < 0x08000000 + len(d) else None


class Image:
    def __init__(self, d, desc):
        self.desc = desc
        self.tiles_at, self.mslot, self.pal_at = (rp(d, u32(d, desc + i)) for i in (0, 4, 8))
        self.size = u32(d, self.tiles_at)
        self.tiles = d[self.tiles_at + 4:self.tiles_at + 4 + self.size]
        self.map_at = rp(d, u32(d, self.mslot))
        self.w, self.h = u16(d, self.map_at), u16(d, self.map_at + 2)
        self.map = list(struct.unpack_from(f"<{self.w * self.h}H", d, self.map_at + 4))
        n = u16(d, self.pal_at)
        self.pals = [[u16(d, self.pal_at + 2 + (p * 16 + c) * 2) for c in range(16)] for p in range(n)]

    def rgb(self, c):
        return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)

    def tile_pixels(self, t):
        b = self.tiles[t * 32:t * 32 + 32]
        if len(b) < 32:
            return None
        return [[(b[y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]

    def render(self, transparent=(255, 0, 255)):
        from PIL import Image as PImage
        img = PImage.new("RGB", (self.w * 8, self.h * 8), transparent)
        px = img.load()
        for i, e in enumerate(self.map):
            tx, ty = i % self.w, i // self.w
            pix = self.tile_pixels(e & 0x3FF)
            pal = self.pals[(e >> 12) % len(self.pals)] if self.pals else [0] * 16
            if pix is None:
                continue
            for y in range(8):
                for x in range(8):
                    sx, sy = (7 - x if e & 0x400 else x), (7 - y if e & 0x800 else y)
                    v = pix[sy][sx]
                    if v:
                        px[tx * 8 + x, ty * 8 + y] = self.rgb(pal[v])
        return img


def scan(d):
    out = []
    for a in range(0, len(d) - 12, 4):
        t, m, p = (rp(d, u32(d, a + i)) for i in (0, 4, 8))
        if t is None or m is None or p is None or t + 8 > len(d):
            continue
        size = u32(d, t)
        if not (0 < size < 0x10000 and size % 32 == 0) or not (1 <= u16(d, p) <= 16):
            continue
        mp = rp(d, u32(d, m))
        if mp is None or not (1 <= u16(d, mp) <= 64 and 1 <= u16(d, mp + 2) <= 64):
            continue
        out.append(a)
    return out


if __name__ == "__main__":
    cmd, rom = sys.argv[1], open(sys.argv[2], "rb").read()
    if cmd == "scan":
        for a in scan(rom):
            im = Image(rom, a)
            print(f"{a:06X} tiles {im.tiles_at:06X}+{im.size:04X} map {im.map_at:06X} {im.w}x{im.h} pal {im.pal_at:06X} n={len(im.pals)}")
    elif cmd == "render":
        Image(rom, int(sys.argv[3], 16)).render().save(sys.argv[4])
    elif cmd == "sheet":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        for a in scan(rom):
            im = Image(rom, a)
            if im.w >= 8 and im.h >= 4:
                im.render().save(out / f"{a:06X}.png")
