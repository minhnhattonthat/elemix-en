-- Logs BG image loads: tiles 0x0800216C(r0 block, r1 layer, r2 tile offset), map 0x080021DC(r0, r1, r2).
local GBA = emu.memType.gbaMemory
local function rd32(a)
  return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) | (emu.read(a + 2, GBA) << 16) | (emu.read(a + 3, GBA) << 24)
end
L.on_exec(0x0800216C, 0x0800216C, function()
  local s = emu.getState()
  local blk = s["cpu.r0"]
  L.log(string.format("f%d tiles blk=%08X size=%X tiles=%d layer=%d off=%d lr=%08X", L.frame, blk, rd32(blk),
    rd32(blk) // 32, s["cpu.r1"], s["cpu.r2"], s["cpu.r14"]))
end)
L.on_exec(0x080021DC, 0x080021DC, function()
  local s = emu.getState()
  local o = s["cpu.r0"]
  local function rd16(a) return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) end
  L.log(string.format("f%d map r0=%08X r1=%d r2=%X lr=%08X obj: tiles=%08X map=%08X +0C=%d +10(base)=%d +12(size)=%X",
    L.frame, o, s["cpu.r1"], s["cpu.r2"], s["cpu.r14"], rd32(o), rd32(o + 4), rd16(o + 0xC), rd16(o + 0x10), rd16(o + 0x12)))
end)
