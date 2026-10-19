# Elemix! English translation

Unofficial English fan translation of **Elemix!** (Game Boy Advance, Sims, 2002; Japan only): the source text and tools
that build the patch.

**No game data is included.** Download the BPS patch from the [latest release](../../releases/latest) and apply it to
your own dump, `Elemix! (Japan).gba` (4,194,304 bytes, CRC32 FA28BED8). The release README lists the hashes and
patching steps. The patched ROM is 8 MiB.

## What is translated
All dialogue, the intro and ending, the tutorial, menus, options, records, the pause and save screens, the title logo
and the staff roll.

## Building from source
You need your own ROM under `rom/` (gitignored). See `CLAUDE.md` for the commands (`python -X utf8 build.py`,
`tools/check.py`, `tools/release.py`) and `docs/re/` for the engine research.

- `script/`: dialogue, graphics captions, tutorial and screen text (Japanese + English)
- `asm/`: variable-width font engine
- `font/`: dialogue font art
- `tools/`: codec, insertion, graphics text, batch and release tools
- `glossary.md`: naming rulings

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project
owner. Elemix! is (c) 2002 SIMS Co., Ltd.; this project is not affiliated with SIMS. Do not share patched ROMs.
