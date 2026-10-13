"""Build the English ROM: python -X utf8 build.py  -> build/elemix_en.gba

1. Text: entries with an `en` field are encoded, packed into free space and their slot repointed.
2. Engine (asm/main.asm, armips): VWF dialogue printer + relocated font with English glyphs (tools/font.py).
With no English and no engine step the output is byte-identical to the original (tests/test_text.py).
"""
import struct, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from codec import Codec, load_table
from text import ROM, load_script, SCRIPT
from wrap import wrap
import font, gfxtext

OUT = ROOT / "build" / "elemix_en.gba"
ARMIPS = ROOT / "tools" / "armips" / "armips.exe"
FREE_LO, FREE_HI = 0x3DB504, 0x3F0000  # 0xFF padding; 0x3F0000+ belongs to asm/main.asm (font, widths, code)
GFX_LO, ROM_SIZE = 0x400000, 0x800000  # expanded area (EEPROM saves are fine up to 16 MiB): redrawn images


class Space:
    def __init__(self, lo, hi):
        self.pos, self.hi = lo, hi

    def alloc(self, n, align=4):
        self.pos = (self.pos + align - 1) & ~(align - 1)
        at = self.pos
        if at + n > self.hi:
            raise SystemExit(f"free space overflow: need {n:#x} at {at:#x}, limit {self.hi:#x}")
        self.pos += n
        return at


def insert_text(rom, entries, codec, space):
    for e in entries:
        if not e["en"]:
            continue
        data = codec.encode(wrap(e["en"], e["jp"])[0])
        at = space.alloc(len(data), 2)
        rom[at:at + len(data)] = data
        struct.pack_into("<I", rom, int(e["slot"], 16), 0x08000000 + at)


def build_text(script=SCRIPT):
    rom = bytearray(ROM.read_bytes())
    insert_text(rom, load_script(script), Codec(load_table()), Space(FREE_LO, FREE_HI))
    return rom


def build(script=SCRIPT, out=OUT):
    rom = build_text(script)
    rom += b"\xff" * (ROM_SIZE - len(rom))
    gspace = Space(GFX_LO, ROM_SIZE)
    for e in gfxtext.load_spec():
        if e.get("en") or e.get("ops"):
            gfxtext.insert(rom, e, gspace)
    out.parent.mkdir(exist_ok=True)
    fnt, widths = font.build_font(rom)
    fbin, wbin = out.with_suffix(".font.bin"), out.with_suffix(".widths.bin")
    fbin.write_bytes(fnt)
    wbin.write_bytes(widths)
    out.write_bytes(rom)
    r = subprocess.run([str(ARMIPS), str(ROOT / "asm" / "main.asm"), "-root", str(ROOT),
                        "-strequ", "ROMFILE", out.resolve().as_posix(), "-strequ", "FONTBIN", fbin.resolve().as_posix(),
                        "-strequ", "WIDTHSBIN", wbin.resolve().as_posix()], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("armips failed:\n" + r.stdout + r.stderr)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=Path, default=SCRIPT)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    print("wrote", build(a.script, a.out))
