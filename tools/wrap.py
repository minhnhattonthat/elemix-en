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


def width(s, bold=False):
    """Pixel advance of a line (control tokens are 0 px, Japanese glyphs 13 px). Bold ({col:01}) glyphs get
    +1 px: the game draws them with a 1 px shadow to the right, and asm/main.asm advances by it."""
    ws = _widths()
    total = 0
    for t in TOKEN.findall(s):
        if t.startswith("{col:"):
            bold = t != "{col:00}"
        elif not (t.startswith("{") or t.startswith("[")):
            total += ws.get(t, font.JP_ADVANCE) + bold
    return total


def bold_after(s, bold=False):
    """Bold state after s, given the state before it."""
    cols = re.findall(r"\{col:(..)\}", s)
    return cols[-1] != "00" if cols else bold


def _greedy(words, limit, bold=False):
    lines, cur = [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if cur and width(cand, bold) > limit:
            lines.append(cur)
            bold = bold_after(cur, bold)
            cur = w
        else:
            cur = cand
    lines.append(cur)
    return lines


def wrap_page(text, limit=LINE_PX, bold=False):
    """Wrap one page's text (manual {n} kept as hard breaks), starting in the given bold state. Returns list of lines."""
    out = []
    for para in text.split("{n}"):
        if not para:
            continue  # the game ignores {n} at column 0, so empty lines never show
        words = para.split(" ")
        lines = _greedy(words, limit, bold)
        lo = max(width(w) for w in words) if words else 0
        best = lines
        for lim in range(lo, limit):  # balanced: shortest limit giving the same line count
            cand = _greedy(words, lim, bold)
            if len(cand) == len(lines):
                best = cand
                break
        out += best
        bold = bold_after(para, bold)
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
    bold = bold_after(head)
    for i, page in enumerate(body.split("{p}")):
        lines = wrap_page(page, bold=bold) if page else []
        room = LINES - (1 if head and i == 0 else 0)
        if len(lines) > room:
            problems.append(f"page {i + 1}: {len(lines)} lines > {room}: {lines}")
        for ln in lines:
            if width(ln, bold) > LINE_PX:
                problems.append(f"page {i + 1}: {width(ln, bold)} px > {LINE_PX}: {ln!r}")
            bold = bold_after(ln, bold)
        pages.append("{n}".join(lines))
    return head + "{p}".join(pages) + tail, problems


if __name__ == "__main__":
    text, probs = wrap(sys.argv[1])
    print(text)
    bold = False
    for ln in re.split(r"\{n\}|\{p\}", text):
        print(f"{width(ln, bold):4} {ln}")
        bold = bold_after(ln, bold)
    print("\n".join(probs) or "ok")
