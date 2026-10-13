-- Logs each call of the glyph renderer 0x08017FC4: frame, caller (lr), glyph bitmap pointer (5th stack arg).
--   emu.py game.gba ... --script tools/lua/glyphlog.lua [--var FROM=N --var TO=M]
local from, to = FROM or 0, TO or math.huge
local GBA = emu.memType.gbaMemory
local dumped = false
local function rd32(a)
  return emu.read(a, GBA) | (emu.read(a + 1, GBA) << 8) | (emu.read(a + 2, GBA) << 16) | (emu.read(a + 3, GBA) << 24)
end
L.on_exec(0x08017FC4, 0x08017FC4, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  if not dumped then
    dumped = true
    local keys = {}
    for k, v in pairs(s) do if k:find("^cpu%.r") then keys[#keys + 1] = k .. "=" .. tostring(v) end end
    table.sort(keys)
    L.log("keys " .. table.concat(keys, " "))
  end
  local sp, lr = s["cpu.r13"], s["cpu.r14"]
  L.log(string.format("f%d lr=%08X r0=%X r1=%X r2=%X r3=%X glyph=%08X", L.frame, lr or 0, s["cpu.r0"] or 0,
    s["cpu.r1"] or 0, s["cpu.r2"] or 0, s["cpu.r3"] or 0, sp and rd32(sp + 0x0c) or 0))
end)
