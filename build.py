"""Build the English ROM: python -X utf8 build.py [--out build/elemix_en.gba]

Entries with an `en` field are encoded, packed into free space and their slot repointed. With no English
anywhere the output is byte-identical to the original (tests/test_build.py).
"""
import argparse, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
from codec import Codec, load_table
from text import ROM, load_script, SCRIPT

FREE_LO, FREE_HI = 0x3DB504, 0x400000  # 0xFF padding at the end of the 4 MiB ROM


class Space:
    def __init__(self, lo, hi):
        self.pos, self.hi = (lo + 3) & ~3, hi

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
        data = codec.encode(e["en"])
        at = space.alloc(len(data), 2)
        rom[at:at + len(data)] = data
        struct.pack_into("<I", rom, int(e["slot"], 16), 0x08000000 + at)


def build(script=SCRIPT):
    rom = bytearray(ROM.read_bytes())
    insert_text(rom, load_script(script), Codec(load_table()), Space(FREE_LO, FREE_HI))
    return rom


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/elemix_en.gba")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(build())
    print("wrote", out)
