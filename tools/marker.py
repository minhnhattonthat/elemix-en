"""Marker script: every line -> its id + filler with the original line/page layout, for width and box QA.

    python -X utf8 tools/marker.py [--out build/marker.json] [--fill TEXT] [--torture ID]
Then: python -X utf8 build.py --script build/marker.json --out build/marker.gba
"""
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text import load_script, save_script

FILL = "The quick brown fox jumps over the lazy dog and"
TORTURE = "!\"#$%&'()*+,-./0123456789:;<=>?@{n}ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`{n}abcdefghijklmnopqrstuvwxyz|~  x  y"
HEADER = re.compile(r"^(\{spd:00\}\{col:01\})(.*?)(\{col:00\}\{n\}\{spd:05\})")
SPLIT = re.compile(r"(\{n\}|\{p\})")


def marker(e, fill):
    jp = e["jp"]
    m = HEADER.match(jp)
    head, body = (m[1] + e["id"] + m[3], jp[m.end():]) if m else ("", jp)
    out, first = [head], not m
    for part in SPLIT.split(body):
        if part in ("{n}", "{p}"):
            out.append(part)
        elif part.strip("　"):
            out.append((f"[{e['id']}] " if first else "") + fill)
            first = False
    return "".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/marker.json")
    ap.add_argument("--fill", default=FILL)
    ap.add_argument("--torture", default="d00", help="id whose text becomes the glyph torture lines")
    a = ap.parse_args()
    entries = load_script()
    for e in entries:
        e["en"] = marker(e, a.fill)
        if e["id"] == a.torture:
            e["en"] = HEADER.match(e["jp"])[0] + TORTURE + "{p}" + e["en"]
    Path(a.out).parent.mkdir(exist_ok=True)
    save_script(entries, a.out)
    print("wrote", a.out)
