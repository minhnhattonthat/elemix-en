-- Stage warp: forces the stage index (s16 at 0x03007244, table 0x083D6F8C, 11 stages) when a stage loads.
--   emu.py game.gba --route r.txt --script tools/lua/warp.lua [--var STAGE=5] [--var NTH=2]
-- Without STAGE it only logs each load. NTH = which load to override (1-based; default every load).
local GBA = emu.memType.gbaMemory
local n = 0
L.on_exec(0x0800449E, 0x0800449E, function()
  n = n + 1
  local cur = emu.read(0x03007244, GBA) | (emu.read(0x03007245, GBA) << 8)
  if STAGE and (not NTH or NTH == n) then
    emu.write(0x03007244, STAGE & 0xFF, GBA)
    emu.write(0x03007245, (STAGE >> 8) & 0xFF, GBA)
    L.log(string.format("f%d load#%d stage %d -> %d", L.frame, n, cur, STAGE))
  else
    L.log(string.format("f%d load#%d stage %d", L.frame, n, cur))
  end
end)
