def test_rom_header(rom):
    assert rom[0xA0:0xB0] == b"ELEMIX!\0\0\0\0\0AEKJ"
