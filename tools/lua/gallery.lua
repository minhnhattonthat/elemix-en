-- Dialogue gallery: the n-th call of the printer (0x08018340, r0 = window) prints slot START+n instead of the
-- game's own string; a shot is taken at every page wait (0x08018396) and at string end (0x0801854E).
--   emu.py build.gba --state-in village.mss --mash 40 --script tools/lua/gallery.lua --var START=0 --var COUNT=5
local GBA = emu.memType.gbaMemory
local SLOTS, start, count = 0x083D6FB8, START or 0, COUNT or 60
local n, cur, page = 0, nil, 0
local function rd32(a)
  return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) | (emu.read(a + 2, GBA) << 16) | (emu.read(a + 3, GBA) << 24)
end
local function wr32(a, v)
  for i = 0, 3 do emu.write(a + i, (v >> (8 * i)) & 0xFF, GBA) end
end
L.on_exec(0x08018340, 0x08018340, function()
  if n >= count or start + n >= 60 then cur = nil; return end
  local win = emu.getState()["cpu.r0"]
  cur, page = start + n, 0
  wr32(win + 0x1C, rd32(SLOTS + 4 * cur))
  L.log(string.format("f%d d%02d", L.frame, cur))
  n = n + 1
end)
local function snap()
  if cur then
    page = page + 1
    L.shot(string.format("d%02d_p%d.png", cur, page))
  end
end
L.on_exec(0x08018396, 0x08018396, snap)
L.on_exec(0x0801854E, 0x0801854E, snap)
