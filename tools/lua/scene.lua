-- Jump to a scene (table 0x083D68A0; 5 = intro, 6 = game, 13 = ending): at frame AT write next scene = SCENE and
-- state = 5 into the scene struct at 0x03000810 ([0] current, [1] state, [2] next).
--   emu.py game.gba --frames 6000 --script tools/lua/scene.lua --var SCENE=13 --var AT=900
local GBA = emu.memType.gbaMemory
L.on_frame(function(n)
  if n == (AT or 900) then
    emu.write(0x03000812, SCENE or 13, GBA)
    emu.write(0x03000811, 5, GBA)
    L.log(string.format("f%d scene -> %d", n, SCENE or 13))
  end
end)
