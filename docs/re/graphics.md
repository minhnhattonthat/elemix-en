# Graphics text survey

All graphics found so far are uncompressed 4bpp tiles + u16 tilemaps, loaded by `0x0800216C` (tiles: DMA from
`block+4`, size `u16 [block]`... see below) and `0x080021DC` (map). Shots: `work/qa/*` (regenerate with emu.py).

## Resource format (partly decoded)
- Tile block: `{u32 ptr (palette?), u32 size, tiles[size]}`; e.g. tutorial page 1 at `0x33FB20` (size 0x2820).
- Descriptor: `{u32 tiles, u32 ?, u32 map, u32 size, ...}`; e.g. `0x342820` -> tiles `0x33FB24`, map `0x3427FC`.
- Intro text block at `0x2F9570` (size 0x380?), descriptor `0x2F9DD0`.
- Many descriptors are listed in a pointer table around `0x3DA9xx`.

## Screens with Japanese
| # | Screen | Where | Source | Notes |
|---|---|---|---|---|
| 1 | Title logo エレミックス! | title | BG tiles | redraw "ELEMIX!" |
| 2 | Intro story text, 5 pages, furigana | after title, map + ring | BG tiles `0x2F95xx`.. | outlined white text over art |
| 3 | Tutorial, 6+ pages (headers, body text, button legends) | title > TUTORIAL | BG tiles `0x33FB24`.. | large; images + text |
| 4 | Options: ボタン設定, 魔法を撃つ, 変身する, スペシャル魔法, 向き固定, レコード, SAVEDATAを消す, コントラスト調整, もどる, 暗/明 | title > OPTIONS | BG tiles | |
| 5 | Records: レコード header (rest English) | Options > レコード | BG tiles | |
| 6 | Pause: SAVEする, タイトル画面へ, ステージをやり直す, もどる | in game, START | BG/OBJ tiles | |

Already English: NEW GAME / LOAD DATA / STAGE SELECT / TUTORIAL / OPTIONS, PRESS START BUTTON, PAUSE, SCORE,
HUD ("beat"), records labels, map labels (Gwuriant, Etrlia, Khanne, Bossporei, Zahher).

## Not yet surveyed
Save/load screens, stage title cards, game over, boss intros, ending, credits, SAVEDATA erase confirm, stage select
(locked without a save). Needs a stage warp or a save file.
