; Elemix! English patch: VWF dialogue + relocated font. Assembled by build.py with armips after text insertion.
; build.py writes build/font.bin and build/widths.bin first.
.gba
.thumb
.open ROMFILE, 0x08000000           ; build.py: -strequ ROMFILE <out>; font/widths written beside it

NEW_FONT  equ 0x083F0000          ; 0x260 glyphs * 32 = 0x4C00
WIDTHS    equ 0x083F4C00          ; 0x260 bytes, advance in px per code
CODE      equ 0x083F4E80

; --- dialogue printer 0x08018340 ---
; chars-per-line = (w - 2*margin)*8 / 13  ->  / 1: the limit is now in pixels
.org 0x0801835E
	mov r1, #1
; x = margin*8 + col*13 + xoff  ->  col is a pixel x (drop the multiply)
.org 0x0801843A
	mov r8, r8
; col += 1  ->  col += width[code]   (r6 = code, preserved across the glyph call)
.org 0x080184CA
	bl vwf_advance
; glyph base, both draw paths
.org 0x080184A8
	.word NEW_FONT
.org 0x080184F8
	.word NEW_FONT

.org NEW_FONT
	.incbin FONTBIN
.org WIDTHS
	.incbin WIDTHSBIN

.org CODE
vwf_advance:                      ; r0 = [r5+0x15] + width[r6]; may clobber r1
	ldr r1, =WIDTHS
	ldrb r1, [r1, r6]
	ldrb r0, [r5, #0x15]
	add r0, r0, r1
	bx lr
.pool

.close
