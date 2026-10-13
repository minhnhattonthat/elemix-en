Elemix! (GBA) - English translation patch v{VERSION}
=====================================================

An unofficial fan translation of Elemix! (Sims, 2002, Game Boy Advance; Japan only).
All dialogue, the intro and ending, the tutorial, menus, options, records, the pause and save screens, the title
logo and the staff roll are in English.

Patching
--------
Apply Elemix_EN_v{VERSION}.bps with Flips, beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/)
to a clean dump of the Japanese ROM:

  Elemix! (Japan).gba   4,194,304 bytes
  CRC32 FA28BED8
  MD5   f65e87d6867d2ae8561ffcd1ab9ed57b
  SHA-1 e9e11a2d0a1ab20b103f846b8c123fba42fd9c23

The patched ROM is 8 MiB (the English graphics live in the added space). Patched ROM:
{PATCHED}

Notes
-----
- Tested in Mesen 2 (with a GBA BIOS) and should work in any accurate GBA emulator or on hardware/flash carts
  that support EEPROM saves.
- Start from a cold boot after patching. Saves from the Japanese version keep working.
- Names keep Japanese honorifics (e.g. Marius-sama). Place names follow the spellings on the game's own map
  (Gwuriant, Etrlia, Khanne). Staff names are in Japanese order with the family name in capitals.
- The point unit after scores (Japanese "ten") is left out on the records and result screens.

Credits
-------
Translation, hacking and graphics: minhnhattonthat, with AI assistance (Claude by Anthropic) for reverse
engineering, translation drafts, review and QA.
Fonts: the dialogue font is an original pixel font; the title logo is drawn with Roboto Condensed Bold
(Apache License 2.0).

This patch contains no ROM data. Do not ask for or distribute pre-patched ROMs.
Elemix! is (c) 2002 SIMS Co., Ltd. This project is not affiliated with SIMS.
