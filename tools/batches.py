"""Translation batches in and out of script/dialogue.json.

    python -X utf8 tools/batches.py check FILE      validate a translation file ({"id": "EN"} JSON or id<TAB>EN TSV)
    python -X utf8 tools/batches.py merge FILE      check, then write the English into script/dialogue.json
    python -X utf8 tools/batches.py pairs OUT       review file: ">> id | JP" / "EN" for every translated entry
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text import load_script, save_script
from codec import Codec, load_table
from wrap import wrap, HEADER

JP = re.compile(r"[぀-ヿ㐀-鿿＀-￯　-〿]")


def load(path):
    s = Path(path).read_text(encoding="utf-8-sig")
    if path.endswith(".json"):
        return json.loads(s)
    return dict(line.split("\t", 1) for line in s.splitlines() if line.strip())


def readable(t):
    return t.replace("{n}", " / ").replace("{p}", " | ")


def check(tl):
    entries = {e["id"]: e for e in load_script()}
    codec, errors = Codec(load_table()), []
    for k, en in tl.items():
        if k not in entries:
            errors.append(f"{k}: unknown id")
            continue
        jp = entries[k]["jp"]
        if JP.search(en) or "\t" in en or "\\u" in en:
            errors.append(f"{k}: Japanese, tab or \\u escape")
        if set(re.sub(r"\{[^}]*\}", "", en)) & set("*<>@"):
            errors.append(f"{k}: * < > @ draw other glyphs in this font")
        try:
            codec.encode(en)
        except ValueError as ex:
            errors.append(f"{k}: {ex}")
        if bool(HEADER.match(jp)) != bool(HEADER.match(en)):
            errors.append(f"{k}: speaker header must match the JP ({{spd:00}}{{col:01}}Name{{col:00}}{{n}}{{spd:05}})")
        body = HEADER.sub("", en)
        if body.count("{col:01}") != body.count("{col:00}"):
            errors.append(f"{k}: unbalanced {{col:01}}/{{col:00}}")
        for tag in ("{at:C}", "{at:D}", "{at:E}"):
            if jp.count(tag) != en.count(tag):
                errors.append(f"{k}: {tag} count differs from JP")
        errors += [f"{k}: {p}" for p in wrap(en, jp)[1]]
    return errors


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "pairs":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for e in load_script():
                if e["en"]:
                    f.write(f">> {e['id']} | {readable(e['jp'])}\n   {readable(wrap(e['en'], e['jp'])[0])}\n\n")
        sys.exit(print("wrote", path))
    tl = load(path)
    errs = check(tl)
    print("\n".join(errs) if errs else f"OK ({len(tl)} entries)")
    if errs:
        sys.exit(1)
    if cmd == "merge":
        entries = load_script()
        for e in entries:
            if e["id"] in tl:
                e["en"] = tl[e["id"]]
        save_script(entries)
        print("merged into script/dialogue.json")
