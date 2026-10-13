"""Two-sector geometric opening calculator; original teaching example.
No network, third-party packages, WAD assets, or Doom engine execution.
Heights are in map units. Does not predict player collision or traversability.
"""

def opening(floor_a, ceiling_a, floor_b, ceiling_b):
    if ceiling_a < floor_a or ceiling_b < floor_b:
        raise ValueError("Each ceiling must be at or above its floor")
    bottom = max(floor_a, floor_b)
    top = min(ceiling_a, ceiling_b)
    return bottom, top, max(0, top - bottom)


def main():
    cases = [(0, 128), (24, 96), (24, 24), (160, 200)]
    for floor_b, ceiling_b in cases:
        bottom, top, height = opening(0, 128, floor_b, ceiling_b)
        print(f"B=({floor_b}, {ceiling_b}), bottom={bottom}, top={top}, height={height}")
    assert opening(0, 128, 0, 128) == (0, 128, 128)
    assert opening(0, 128, 24, 96) == (24, 96, 72)
    assert opening(0, 128, 24, 24) == (24, 24, 0)
    assert opening(0, 128, 160, 200) == (160, 128, 0)
    assert opening(-32, 80, 0, 128) == (0, 80, 80)
    print("All teaching examples agree.")


if __name__ == "__main__":
    main()
