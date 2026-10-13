# Elemix! (GBA) English translation

Skill: translate-retro-game (H:/translation/elemix/rom/.agents/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work. `$SKILL` below = that directory.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`              -> build/elemix_en.gba   (not written yet)
- Check:    `python -X utf8 tools/check.py`        (pytest tests/ + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/elemix_en.gba --out work/qa/smoke --frames 2400 --smoke`
- Release:  `python -X utf8 tools/release.py`      (not written yet; patch + verify; never publish without the user)

## Paths
- Original ROM: `rom/Elemix! (Japan).gba` (gitignored; hashes in docs/re/README.md). BIOS dump: `rom/gba_bios.bin`.
- Emulator: `tools/mesen2/Mesen.exe` with `Firmware/gba_bios.bin` (headless). armips: `tools/armips/`. Both gitignored.
- Text codec: `tools/codec.py` + `tbl/jp.tbl`. Font sheet: `tools/font.py`. Lua probes: `tools/lua/`.
- Glossary + rulings: `glossary.md`. RE notes: `docs/re/README.md` (index).

## Rulings
- Edit source files only with the file-edit tool; scripts read and analyse, never `.replace()` and write back.
- Honorifics kept, hyphenated; JP name order. Hepburn + judgment (Roman names: Gracchus, Teutoburg). All graphics and credits in English. No abbreviations. Pre-approved: keep going, report at end.
- Python reads and analyses ROM; run with `python -X utf8`.

## Status
- Done: Step 0; recon of dialogue encoding, font, renderer, pointer array (docs/re/text.md).
- Next: graphics-text survey; identity build; extract to script/*.json; VWF spike.
