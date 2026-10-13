-- Logs each distinct map object passed to the map-rectangle copier 0x08002374 (scrolling layers: credits).
local GBA = emu.memType.gbaMemory
local seen = {}
local function rd32(a)
  return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) | (emu.read(a + 2, GBA) << 16) | (emu.read(a + 3, GBA) << 24)
end
local function rd16(a) return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) end
L.on_exec(0x08002374, 0x08002374, function()
  local o = emu.getState()["cpu.r0"]
  local key = rd32(o + 4)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d obj=%08X tiles=%08X map=%08X w=%d +10=%d +14=%d", L.frame, o, rd32(o), key,
    rd16(o + 0xC), rd16(o + 0x10), rd16(o + 0x14)))
end)
