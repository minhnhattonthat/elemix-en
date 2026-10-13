-- Logs the dialogue window struct (r0 at the printer 0x08018340) each time a string starts printing.
--   +0A tile base, +0C width tiles, +0D height tiles, +0E/+0F margin tiles, +17 line limit (px after the VWF
--   patch, chars before), +18 lines per page, +1C text pointer.
local GBA = emu.memType.gbaMemory
L.on_exec(0x08018340, 0x08018340, function()
  local s = emu.getState()
  local w = s["cpu.r0"]
  local t = {}
  for i = 0, 0x23 do t[#t + 1] = string.format("%02X", emu.read(w + i, GBA)) end
  L.log(string.format("f%d win=%08X %s", L.frame, w, table.concat(t, " ")))
end)
L.on_exec(0x08018364, 0x08018364, function()
  local s = emu.getState()
  L.log(string.format("f%d linelimit=%d", L.frame, s["cpu.r0"]))
end)
L.on_exec(0x0801837A, 0x0801837A, function()
  local s = emu.getState()
  L.log(string.format("f%d lines=%d", L.frame, s["cpu.r0"]))
end)
