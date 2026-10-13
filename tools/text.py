"""Dialogue extract. Strings are reached through 60 u32 slots at SLOTS..SLOTS_END in the asset table.

    python -X utf8 tools/text.py dump [--force]     write script/dialogue.json (refuses to clobber without --force)
"""
import json, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codec import Codec, load_table, ROOT

ROM = ROOT / "rom" / "Elemix! (Japan).gba"
SCRIPT = ROOT / "script" / "dialogue.json"
SLOTS, SLOTS_END = 0x3D6FB8, 0x3D70A8  # 60 slots
TEXT_LO, TEXT_HI = 0x2C234, 0x2EAA8      # original string area (interleaved with event structs)


def slots():
    return range(SLOTS, SLOTS_END, 4)


def read_entries(rom, codec):
    out = []
    for i, s in enumerate(slots()):
        ptr = struct.unpack_from("<I", rom, s)[0] - 0x08000000
        jp, n = codec.decode(rom, ptr)
        out.append({"id": f"d{i:02d}", "slot": f"{s:06X}", "ptr": f"{ptr:06X}", "len": n, "jp": jp, "en": "",
                    "notes": ""})
    return out


def load_script(path=SCRIPT):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_script(entries, path=SCRIPT):
    Path(path).parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    if sys.argv[1:2] != ["dump"]:
        sys.exit(__doc__)
    if SCRIPT.exists() and "--force" not in sys.argv:
        sys.exit(f"{SCRIPT} exists; dump never clobbers English (pass --force to overwrite)")
    save_script(read_entries(ROM.read_bytes(), Codec(load_table())))
    print("wrote", SCRIPT)
