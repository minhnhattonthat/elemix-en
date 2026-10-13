import hashlib
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Elemix! (Japan).gba"
ROM_SHA1 = "e9e11a2d0a1ab20b103f846b8c123fba42fd9c23"


@pytest.fixture(scope="session")
def rom():
    if not ROM.exists():
        pytest.skip(f"original ROM missing: {ROM}")
    data = ROM.read_bytes()
    assert hashlib.sha1(data).hexdigest() == ROM_SHA1, "rom/ holds a different dump"
    return data
