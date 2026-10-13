"""Pixel widths and line wrapping for the VWF dialogue box (measured in game, docs/re/text.md):
line limit 192 px (the game wraps once x >= 192), 3 lines per page, the name tag uses line 1 of page 1.

Translators write sentences with {p} page breaks; wrap() inserts {n} at spaces (balanced: it picks the smallest
width that still fits the same number of lines) and reports pages that need more than 3 lines.

    python -X utf8 tools/wrap.py "Some text{p}More text"     print the wrapped text and widths
"""
import re, sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font

LINE_PX = 188          # budget per line; the game's hard limit is 192, keep a little air before the frame
LINES = 3
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]|.", re.S)
HEADER = re.compile(r"^\{spd:00\}\{col:01\}.*?\{col:00\}\{n\}\{spd:05\}")


@lru_cache(None)
def _widths():
    return {c: w for c, (_, w) in font.load_en().items()}


def width(s):
    """Pixel advance of a line (control tokens are 0 px, Japanese glyphs 13 px)."""
    ws = _widths()
    total = 0
    for t in TOKEN.findall(s):
        if t.startswith("{") or t.startswith("["):
            continue
        total += ws.get(t, font.JP_ADVANCE)
    return total


def _greedy(words, limit):
    lines, cur = [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if cur and width(cand) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    lines.append(cur)
    return lines


def wrap_page(text, limit=LINE_PX):
    """Wrap one page's text (manual {n} kept as hard breaks). Returns list of lines."""
    out = []
    for para in text.split("{n}"):
        if not para:
            continue  # the game ignores {n} at column 0, so empty lines never show
        words = para.split(" ")
        lines = _greedy(words, limit)
        lo = max(width(w) for w in words) if words else 0
        best = lines
        for lim in range(lo, limit):  # balanced: shortest limit giving the same line count
            cand = _greedy(words, lim)
            if len(cand) == len(lines):
                best = cand
                break
        out += best
    return out


TAIL = re.compile(r"(\{[np]\})+$")


def wrap(en, jp=""):
    """Full entry text -> (wrapped text with {n}, list of problems). Trailing breaks are taken from jp."""
    m = HEADER.match(en)
    head, body = (m[0], en[m.end():]) if m else ("", en)
    body = TAIL.sub("", body)
    t = TAIL.search(jp)
    tail = t[0] if t else ""
    pages, problems = [], []
    for i, page in enumerate(body.split("{p}")):
        lines = wrap_page(page) if page else []
        room = LINES - (1 if head and i == 0 else 0)
        if len(lines) > room:
            problems.append(f"page {i + 1}: {len(lines)} lines > {room}: {lines}")
        for ln in lines:
            if width(ln) > LINE_PX:
                problems.append(f"page {i + 1}: {width(ln)} px > {LINE_PX}: {ln!r}")
        pages.append("{n}".join(lines))
    return head + "{p}".join(pages) + tail, problems


if __name__ == "__main__":
    text, probs = wrap(sys.argv[1])
    print(text)
    for ln in re.split(r"\{n\}|\{p\}", text):
        print(f"{width(ln):4} {ln}")
    print("\n".join(probs) or "ok")
