"""Elemix! dialogue text codec: u16 little-endian codes, FFFF-terminated.

  0000-01A8  glyph (tbl/jp.tbl)         1xxx {n}       newline
  2xxx {spd:XX}  text speed (low byte)  3xxx {col:XX}  colour (3001 = name tag, 3000 = normal)
  4xxx {p}       wait for button, new page
  5xxx {at:X}    attribute (low nibble)
Any other word, or a glyph with no table entry, is written [XXXX] so decode -> encode is exact.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
END = 0xFFFF
TOKEN = re.compile(r"\{(n|p|spd|col|at)(?::([0-9A-F]+))?\}|\[([0-9A-F]{4})\]|(.)", re.S)


def load_table(path=ROOT / "tbl" / "jp.tbl", english=True):
    """Japanese table plus (english=True) the ASCII glyphs the build adds at font.EN_BASE+."""
    dec = {}
    if english:
        from font import en_codes
        dec.update({code: c for c, code in en_codes().items()})
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            k, _, v = line.partition("=")
            dec[int(k, 16)] = "　" if v == r"\s" else v  # editors strip a trailing full-width space
            assert dec[int(k, 16)], f"empty table value: {line!r}"
    return dec


class Codec:
    def __init__(self, dec):
        self.dec = dec
        self.enc = {v: k for k, v in dec.items()}
        assert len(self.enc) == len(dec), "duplicate table values"

    def decode_words(self, words):
        out = []
        for w in words:
            top = w >> 12
            if w in self.dec:
                out.append(self.dec[w])
            elif w == 0x1000:
                out.append("{n}")
            elif top == 2 and w & 0xF00 == 0:
                out.append(f"{{spd:{w & 0xFF:02X}}}")
            elif top == 3 and w & 0xF00 == 0:
                out.append(f"{{col:{w & 0xFF:02X}}}")
            elif w == 0x4000:
                out.append("{p}")
            elif top == 5 and w & 0xFF0 == 0:
                out.append(f"{{at:{w & 0xF:X}}}")
            else:
                out.append(f"[{w:04X}]")
        return "".join(out)

    def decode(self, rom, off):
        """Decode the string at file offset off. Returns (text, byte length incl. FFFF)."""
        words, p = [], off
        while True:
            w = rom[p] | rom[p + 1] << 8
            p += 2
            if w == END:
                return self.decode_words(words), p - off
            words.append(w)

    def encode_words(self, text):
        words = []
        for m in TOKEN.finditer(text):
            name, arg, hexw, ch = m.groups()
            if hexw:
                words.append(int(hexw, 16))
            elif name:
                words.append({"n": 0x1000, "p": 0x4000}.get(name) if arg is None else
                             {"spd": 0x2000, "col": 0x3000, "at": 0x5000}[name] | int(arg, 16))
            elif ch in self.enc:
                words.append(self.enc[ch])
            else:
                raise ValueError(f"no code for {ch!r} in {text!r}")
        return words

    def encode(self, text):
        return b"".join(w.to_bytes(2, "little") for w in self.encode_words(text)) + b"\xff\xff"
