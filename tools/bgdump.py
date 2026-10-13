"""Render one GBA text BG (4bpp) from an emu.py ppudump: python tools/bgdump.py PREFIX BG OUT.png
PREFIX = work/qa/x/ppu_000110 (reads .vram.bin .pal.bin .io.bin)."""
import struct, sys
from PIL import Image

prefix, bg, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
vram = open(prefix + ".vram.bin", "rb").read()
pal = open(prefix + ".pal.bin", "rb").read()
io = open(prefix + ".io.bin", "rb").read()
cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
char, screen, size = (cnt >> 2) & 3, (cnt >> 8) & 31, cnt >> 14
w, h = (32, 32) if size == 0 else (64, 32) if size == 1 else (32, 64) if size == 2 else (64, 64)
img = Image.new("RGB", (w * 8, h * 8), (255, 0, 255))
px = img.load()
for ty in range(h):
    for tx in range(w):
        blk = (tx // 32) + (ty // 32) * (w // 32)
        e = struct.unpack_from("<H", vram, screen * 0x800 + blk * 0x800 + ((ty % 32) * 32 + tx % 32) * 2)[0]
        t, pn = e & 0x3FF, e >> 12
        base = char * 0x4000 + t * 32
        for y in range(8):
            for x in range(8):
                sx, sy = (7 - x if e & 0x400 else x), (7 - y if e & 0x800 else y)
                v = (vram[base + sy * 4 + sx // 2] >> (4 * (sx & 1))) & 15 if base + 32 <= len(vram) else 0
                if v:
                    c = struct.unpack_from("<H", pal, (pn * 16 + v) * 2)[0]
                    px[tx * 8 + x, ty * 8 + y] = ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)
img.save(out)
print(f"BG{bg} char {char} screen {screen} {w}x{h} -> {out}")
