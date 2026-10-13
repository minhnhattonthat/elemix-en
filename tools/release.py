"""Release gate + package: python -X utf8 tools/release.py [--version 1.0]

check -> build -> smoke boot -> leftover-Japanese scan (dialogue slots) -> BPS (re-applied and verified by bps.py)
-> dist/Elemix_EN_v<ver>.zip holding the patch and README.txt only. Stops at the first failure. Never publishes.
"""
import argparse, hashlib, subprocess, sys, zipfile, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents" / "skills" / "translate-retro-game" / "scripts"
ORIG = ROOT / "rom" / "Elemix! (Japan).gba"
BUILT = ROOT / "build" / "elemix_en.gba"
PY = [sys.executable, "-X", "utf8"]


def run(step, cmd):
    print(f"== {step}")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"release stopped: {step} failed (exit {r.returncode})")


def hashes(data):
    return (f"CRC32 {zlib.crc32(data):08X}", f"MD5 {hashlib.md5(data).hexdigest()}",
            f"SHA-1 {hashlib.sha1(data).hexdigest()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="1.0")
    v = ap.parse_args().version
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    slots = ROOT / "build" / "slots.txt"
    run("check", PY + ["tools/check.py"])
    run("build", PY + ["build.py"])
    run("smoke", PY + [str(SKILL / "emu.py"), str(BUILT), "--out", "work/qa/release_smoke", "--sav",
                       "work/saves/blank.sav", "--frames", "2400", "--smoke"])
    slots.write_text("".join(f"{s:06X}\n" for s in range(0x3D6FB8, 0x3D70A8, 4)))
    run("leftover Japanese", PY + [str(SKILL / "jp_left.py"), str(BUILT), "--tbl", "tbl/jp.tbl", "--le16",
                                   "--slots", str(slots), "--min", "2"])
    patch = dist / f"Elemix_EN_v{v}.bps"
    run("bps", PY + [str(SKILL / "bps.py"), "make", str(ORIG), str(BUILT), str(patch)])
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = readme.replace("{VERSION}", v).replace("{PATCHED}", "\n".join(hashes(BUILT.read_bytes())))
    zp = dist / f"Elemix_EN_v{v}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    print("wrote", zp)
