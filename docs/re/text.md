# Dialogue text

## Encoding
- u16 little-endian codes, string ends at `FFFF`. Codec: `tools/codec.py`, table `tbl/jp.tbl`.
- `0000-01A8`: glyph index. Font at ROM `0x352B74`, 32 bytes per glyph (16x16 1bpp, tiles TL TR BL BR), ends
  `0x356094`. Gojuon grid order; gap slots render blank (`0024` is used as a space). Duplicate glyphs:
  `0110` = 家 (also `00E2`), `0192` = 者 (also `0139`).
- Control words (handler jump table at `0x0801841C`, top nibble 1-5):
  - `1xxx` newline (only `1000` seen)
  - `2xxx` text speed, low byte (`2000` instant, `2005` normal, `2009` pause)
  - `3xxx` style, low byte -> `[win+0x12]` (`3001` bold: name tag, key words, drawn with a 1 px shadow at x+1,
    so the VWF advances 1 px more per glyph; `3000` normal)
  - `4xxx` wait for button, new page (only `4000` seen)
  - `5xxx` attribute, low nibble (`500C`/`500E`/`5001` around magic names)
- Typical line: `{spd:00}{col:01}NAME{col:00}{n}{spd:05}text{n}text{p}{n}...`

## Renderer (THUMB)
- `0x08018340` dialogue printer: reads words via `[win+0x1C]`, x = `col*13 + ...` (13 px advance, fixed),
  y = `row*13`; `[win+0x17]` chars per line, `[win+0x18]` lines per page. Window struct at `0x03007960`.
- Glyph pointer = `code*32 + 0x08352B74`, literal pool at `0x080184A8` and `0x080184F8`.
- `0x0801826C` -> `0x08017FC4` draws one glyph into IWRAM `0x03007990` at any pixel x (shift = x & 7),
  then DMA to VRAM `0x0600C000+`. Pixel-x support already exists, so VWF = replace `col*13` with a running x.

## Locations
- Dialogue strings: `0x02C214-0x02EAA6`, interleaved with event structs (`0x02C9CC`, `0x02CED0`, ...).
- Pointer array: 60 u32 slots `0x3D6FB8-0x3D70A4` (part of a larger asset table at `0x3D6Fxx`).
- Free space: `0x3DB504-0x3FFFFF` (0xFF). ROM is 4 MiB; may grow.
- No Shift-JIS text in ROM. Sound mixer (IWRAM `0x030006C4`) reads PCM `0x37xxxx-0x39xxxx`; music `0x3Cxxxx`.
