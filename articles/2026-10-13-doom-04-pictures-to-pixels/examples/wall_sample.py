"""Recompute the article's wall address, using only Python's standard library.

Fixed example: eye(128,96,41), east-facing320x200 canvas, f160.
Only the x256, y0..192, z0..24 lower wall is handled.
It neither reads PNG files nor implements Doom's renderer.
MIT license: ../licenses/Example-Code-MIT.txt
"""
from fractions import Fraction as F

def wall_sample(column, row):
    if not (0 <= column < 320 and 0 <= row < 200):
        raise ValueError('screen column or row outside the teaching canvas')
    center_u, center_v = F(2 * column + 1, 2), F(2 * row + 1, 2)
    distance = F(256 - 128)
    world_y = 96 - (center_u - 160) * distance / 160
    world_z = 41 - (center_v - 100) * distance / 160
    if not (0 <= world_y <= 192 and 0 <= world_z <= 24):
        raise ValueError('this ray does not hit the chosen lower-wall rectangle')
    a, b = 192 - world_y, 24 - world_z
    column_in_image = (a.numerator // a.denominator) % 128
    row_in_image = (b.numerator // b.denominator) % 128
    return {
        'pixel_center': (center_u, center_v),
        'wall_point': (F(256), world_y, world_z),
        'source_position': (a, b),
        'source_cell': (column_in_image, row_in_image),
    }

if __name__ == '__main__':
    result = wall_sample(180, 136)
    for key, values in result.items():
        print(key, tuple(float(v) for v in values))
    assert result['wall_point'] == (256, F(398, 5), F(59, 5))
    assert result['source_position'] == (F(562, 5), F(61, 5))
    assert result['source_cell'] == (112, 12)
    assert 140 % 128 == 12
    print('Address check passed. No image file or game was opened.')
