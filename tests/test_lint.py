"""Text lint over script/dialogue.json English. Quiet: one assertion per rule listing every offender."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import text
from codec import Codec, load_table
from wrap import wrap, HEADER

JP = re.compile(r"[぀-ヿ㐀-鿿＀-￯　-〿]")
BANNED = set("*<>@")  # glyph slots that draw x, arrows and (c) in this font
ENTRIES = [e for e in text.load_script() if e["en"]]


def offenders(rule):
    return [e["id"] for e in ENTRIES if rule(e)]


def test_no_japanese_left():
    assert not offenders(lambda e: JP.search(e["en"]))


def test_encodable():
    c = Codec(load_table())

    def bad(e):
        try:
            c.encode(e["en"])
        except ValueError:
            return True
    assert not offenders(bad)


def test_banned_glyphs():
    assert not offenders(lambda e: BANNED & set(re.sub(r"\{[^}]*\}", "", e["en"])))


def test_fits_box():
    probs = {e["id"]: wrap(e["en"])[1] for e in ENTRIES}
    assert not {k: v for k, v in probs.items() if v}


def test_speaker_header_kept():
    assert not offenders(lambda e: bool(HEADER.match(e["jp"])) != bool(HEADER.match(e["en"])))


def test_highlight_balanced():
    def bad(e):
        s = HEADER.sub("", e["en"])
        return s.count("{col:01}") != s.count("{col:00}")
    assert not offenders(bad)


def test_no_ordinal_after_variable():
    assert not offenders(lambda e: re.search(r"\d(st|nd|rd|th)\b", e["en"]) and "{" in e["en"])


def test_glossary_avoid():
    avoid = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 4 and cells[-1] and cells[0] not in ("JP", "---"):
            avoid += [a.strip() for a in cells[-1].split(",") if a.strip()]
    assert not offenders(lambda e: any(re.search(rf"\b{re.escape(a)}\b", e["en"]) for a in avoid))
