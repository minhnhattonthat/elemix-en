# Elemix! (GBA) English translation

Skill: translate-retro-game (H:/translation/elemix/rom/.agents/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work. `$SKILL` below = that directory.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`              -> build/elemix_en.gba (8 MiB; text + VWF asm + graphics)
- Check:    `python -X utf8 tools/check.py`        (pytest: roundtrip, identity, coverage, lint, graphics fit, romdiff; pre-commit runs it)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/elemix_en.gba --out work/qa/smoke --sav work/saves/blank.sav --frames 2400 --smoke`
- Release:  `python -X utf8 tools/release.py --version 1.0` -> dist/Elemix_EN_v1.0.zip (bps + README; never publish without the user)
- Translate: edit work/tl/all.out.json, `python -X utf8 tools/batches.py merge work/tl/all.out.json` (check runs first)

## Paths
- Original ROM: `rom/Elemix! (Japan).gba` (gitignored; hashes in docs/re/README.md). BIOS dump: `rom/gba_bios.bin`.
- Emulator: `tools/mesen2/Mesen.exe` + `Firmware/gba_bios.bin` (headless). armips: `tools/armips/`. Both gitignored.
- Dialogue: `script/dialogue.json` (60 slots; `{n}` `{p}` `{spd:XX}` `{col:XX}` `{at:X}`; build wraps at 188 px, 3 lines/page).
- Graphics: `script/graphics.json` (captions), `script/tutorial.json`, `script/screens.json` (logo, pools, credits) -> tools/gfxtext.py.
- Engine: asm/main.asm (VWF, font at 0x3F0000). Font art: font/en_vwf.txt. Codec: tools/codec.py + tbl/jp.tbl.
- RE notes: docs/re/README.md (index), text.md, graphics.md. Glossary + rulings: glossary.md.

## Rulings
- Edit source/data files only with the file-edit tool. Python reads and analyses; run with `python -X utf8`.
- Honorifics kept, hyphenated; JP name order. Official map spellings (Gwuriant, Etrlia, Khanne), else Hepburn + judgment. All graphics and credits English. No abbreviations. Pre-approved: keep going, report at end.
- Mesen keeps .sav files between runs: always pass `--sav work/saves/blank.sav` (or village.sav) or menus shift.
- `< > * @` draw ◀ ▶ × © in the VWF font: lint bans them in dialogue.

## Status (2026-10-13)
- Done: all 60 dialogue entries (reviewed), intro/ending captions, tutorial, options/records/erase, pause, save confirm, time-attack prompt, title logo, staff roll. Every dialogue page checked in game via tools/lua/gallery.lua; v1.0 release zip built and verified (not published).
- Not seen in game: time-attack and expert-mode screens (need a cleared save); result screen after a real stage clear.
- Open questions for the user: credit line in README, blanked score unit, dropped logo emblem.
