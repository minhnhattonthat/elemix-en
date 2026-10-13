import json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
from codec import Codec, load_table
import text


def codec():
    return Codec(load_table())


def test_roundtrip_every_slot(rom):
    c = codec()
    for e in text.read_entries(rom, c):
        ptr = int(e["ptr"], 16)
        assert c.encode(e["jp"]) == rom[ptr:ptr + e["len"]], e["id"]


def test_jp_fields_match_rom(rom):
    """script/dialogue.json jp fields are what the ROM holds (regenerate with text.py dump after a table fix)."""
    c = codec()
    fresh = {e["id"]: e["jp"] for e in text.read_entries(rom, c)}
    for e in text.load_script():
        assert e["jp"] == fresh[e["id"]], e["id"]


def test_coverage(rom):
    """Every FFFF-terminated glyph string in the text area is one of the 60 slot strings or a tail of one."""
    c = codec()
    spans = []
    for e in text.read_entries(rom, c):
        p = int(e["ptr"], 16)
        spans.append((p, p + e["len"]))
    pos, missed = text.TEXT_LO, []
    while pos < text.TEXT_HI:
        if any(a <= pos < b for a, b in spans):
            pos = next(b for a, b in spans if a <= pos < b)
            continue
        # outside known strings: must not look like a string with Japanese glyphs (event structs are fine)
        words, p = [], pos
        starts = {a for a, b in spans}
        while p < text.TEXT_HI and p not in starts:
            w = rom[p] | rom[p + 1] << 8
            if w == 0xFFFF or not (w < 0x1A9 or 0x1000 <= w < 0x6000):
                break
            words.append(w)
            p += 2
        if p < text.TEXT_HI and rom[p:p + 2] == b"\xff\xff" and sum(0x5A <= w < 0x1A9 for w in words) >= 4:
            missed.append(f"{pos:06X}")
            pos = p
        pos += 2
    assert not missed, missed


def test_identity_build(tmp_path, rom):
    import build
    entries = text.load_script()
    for e in entries:
        e["en"] = ""
    p = tmp_path / "blank.json"
    p.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    assert bytes(build.build_text(p)) == rom
