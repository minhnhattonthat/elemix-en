"""The built ROM differs from the original only where the build means to write (romdiff.py in test form)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import build, text, gfxtext
from gfx import Image


def allowed_ranges(rom):
    r = [(text.SLOTS, text.SLOTS_END),                 # dialogue pointer slots
         (build.FREE_LO, build.FREE_HI),               # packed English text
         (0x3F0000, 0x400000),                         # asm/main.asm: font, widths, code
         (0x01835E, 0x018360), (0x01843A, 0x01843C),   # VWF patches (asm/main.asm)
         (0x0184CA, 0x0184CE), (0x0184A8, 0x0184AC), (0x0184F8, 0x0184FC)]
    for e in gfxtext.load_spec():
        im = Image(rom, int(e["desc"], 16))
        r.append((im.desc, im.desc + 4))               # tile pointer
        n = e["count"] if e["kind"] == "pool" else 1
        slots = int(e["slots"], 16) if e["kind"] == "pool" else im.mslot
        r.append((slots, slots + 4 * n))               # map slot(s)
    return r


def test_writes_stay_in_allowed_ranges(tmp_path, rom):
    out = build.build(out=tmp_path / "en.gba")
    new = out.read_bytes()
    assert len(new) == build.ROM_SIZE
    ranges = allowed_ranges(rom)
    bad = [i for i in range(len(rom)) if rom[i] != new[i] and not any(a <= i < b for a, b in ranges)]
    assert not bad, [f"{i:06X}" for i in bad[:20]]
