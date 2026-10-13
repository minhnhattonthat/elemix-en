"""Copy an EEPROM save with bytes changed: python tools/savpatch.py IN OUT OFF=VAL [OFF=VAL ...] (hex)."""
import sys

data = bytearray(open(sys.argv[1], "rb").read())
for kv in sys.argv[3:]:
    k, v = kv.split("=")
    data[int(k, 16)] = int(v, 16)
open(sys.argv[2], "wb").write(data)
