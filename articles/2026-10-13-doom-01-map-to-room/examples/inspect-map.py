"""Read the attached freely licensed Freedoom MAP01 without executing it.
Pure Python 3 standard library. No network or game engine required.
"""
from pathlib import Path
import hashlib
import struct

path = Path(__file__).with_name("freedoom-map01.wad")
data = path.read_bytes()
expected = "d9da5d7f8d97d6555182a04326f306dde6fd40da1186a6fec18143c7ccddd20d"
assert hashlib.sha256(data).hexdigest() == expected, "Unexpected input file"
magic, count, directory = struct.unpack_from("<4sii", data)
assert magic == b"PWAD"
lumps = {}
for i in range(count):
    offset, size, raw_name = struct.unpack_from("<ii8s", data, directory + i * 16)
    assert 0 <= offset <= offset + size <= len(data)
    lumps[raw_name.rstrip(b"\0").decode("ascii")] = data[offset:offset + size]
lines = list(struct.iter_unpack("<7H", lumps["LINEDEFS"]))
sectors = list(struct.iter_unpack("<hh8s8shhh", lumps["SECTORS"]))
sides = list(struct.iter_unpack("<hh8s8s8sh", lumps["SIDEDEFS"]))
indices = [i for i, line in enumerate(lines)
           if any(sides[side][-1] == 0 for side in line[5:7] if side != 65535)]
print("Linedefs:", len(lines))
print("Sectors:", len(sectors))
print("Sector 0 floor / ceiling:", sectors[0][0], sectors[0][1])
print("Linedefs touching sector 0:", indices)
assert len(lines) == 1272 and len(sectors) == 206
assert sectors[0][:2] == (0, 128)
