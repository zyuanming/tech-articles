"""Exact arithmetic for a teaching pinhole camera, not the Doom renderer.
Python 3 standard library only. No network, third-party modules or game assets.
Coordinates are continuous positions; this does not select pixel coverage.
"""
from fractions import Fraction


def project_point(d, s, q, f=160, width=320, height=200):
    """d: forward depth; s: right offset; q: height relative to the eye."""
    d, s, q, f = (Fraction(value) for value in (d, s, q, f))
    if d <= 0:
        raise ValueError("Point must be in front of the eye: d > 0")
    if f <= 0 or width <= 0 or height <= 0:
        raise ValueError("f and canvas dimensions must be positive")
    return (Fraction(width, 2) + f * s / d,
            Fraction(height, 2) - f * q / d)


def relative_to_eye(point, eye=(128, 96, 41), facing="east"):
    dx, dy, q = (p - o for p, o in zip(point, eye))
    if facing == "east":
        return dx, -dy, q
    if facing == "north":
        return dy, dx, q
    raise ValueError("This small example supports east or north only")


def main():
    examples = [(128, 0, 0), (128, 64, -17), (256, 64, -17), (128, -64, -17)]
    for d, s, q in examples:
        u, v = project_point(d, s, q)
        print(f"d={d}, s={s}, q={q} -> u={float(u):g}, v={float(v):g}")
    assert project_point(*relative_to_eye((256, 32, 24))) == (240, Fraction(485, 4))
    assert project_point(256, 64, -17) == (200, Fraction(885, 8))
    assert project_point(128, -64, -17)[0] == 80
    assert project_point(128, 64, -17, f=320)[0] == 320
    assert relative_to_eye((256, 32, 24), facing="north") == (-64, 128, -17)
    for depth in [0, -1, -128]:
        try:
            project_point(depth, 64, -17)
        except ValueError:
            pass
        else:
            raise AssertionError("Non-front point accepted")
    # Same angular direction at different distances maps to the same position.
    assert project_point(128, 64, -17) == project_point(256, 128, -34)
    print("All examples agree. No occlusion, clipping or pixel-coverage test was made.")


if __name__ == "__main__":
    main()
