-- Per PC: count, lowest and highest ROM address read in a frame window. Finds text/font readers on GBA.
--   emu.py game.gba ... --script tools/lua/romreads.lua --var FROM=1150 --var TO=1300
local from, to = FROM or 0, TO or math.huge
local stats = {}
L.on_read(0x08000000, 0x09FFFFFF, function(addr)
  if L.frame < from or L.frame > to then return end
  local pc = L.pc()
  local s = stats[pc]
  if not s then s = {n = 0, lo = addr, hi = addr}; stats[pc] = s end
  s.n = s.n + 1
  if addr < s.lo then s.lo = addr end
  if addr > s.hi then s.hi = addr end
end)
L.on_frame(function(n)
  if n == to + 1 then
    for pc, s in pairs(stats) do
      L.log(string.format("pc=%08X n=%d lo=%08X hi=%08X", pc, s.n, s.lo, s.hi))
    end
  end
end)
