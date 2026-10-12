"""Integer-centre, one-pixel-wide teaching rasterizer; Python 3 standard library.

Not a plotter driver or a GPU implementation. Ties are resolved after a canonical
major-axis orientation so reversing input endpoints reverses the same pixel list.
"""
from fractions import Fraction


def line_points(x0, y0, x1, y1):
    coords = (x0, y0, x1, y1)
    if not all(isinstance(v, int) for v in coords):
        raise TypeError('This example requires integer grid endpoints')
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0, x1, y1 = y0, x0, y1, x1
    reversed_input = x0 > x1
    if reversed_input:
        x0, x1, y0, y1 = x1, x0, y1, y0
    dx, dy = x1 - x0, abs(y1 - y0)
    sy = 1 if y1 >= y0 else -1
    d = 2 * dy - dx
    y = y0
    points = []
    for x in range(x0, x1 + 1):
        points.append((y, x) if steep else (x, y))
        if x == x1:
            break
        if d >= 0:
            y += sy
            d -= 2 * dx
        d += 2 * dy
    return points[::-1] if reversed_input else points


def shallow_trace(dx=11, dy=4):
    assert 0 <= dy <= dx and dx > 0
    x = y = 0
    d = 2 * dy - dx
    rows = []
    while x < dx:
        before = d
        diagonal = d >= 0
        if diagonal:
            y += 1
            d -= 2 * dx
        d += 2 * dy
        x += 1
        rows.append((x, y, before, 'NE' if diagonal else 'E', d))
    return rows


def reference_points(x0, y0, x1, y1):
    # Exact rational nearest-centre definition, independent of recurrence.
    steep = abs(y1-y0) > abs(x1-x0)
    if steep:
        x0,y0,x1,y1 = y0,x0,y1,x1
    backward = x0 > x1
    if backward:
        x0,y0,x1,y1 = x1,y1,x0,y0
    dx,dy = x1-x0,abs(y1-y0)
    sign = 1 if y1 >= y0 else -1
    result=[]
    for x in range(x0,x1+1):
        offset=Fraction(0) if dx == 0 else Fraction(dy*(x-x0),dx)
        q=offset+Fraction(1,2)
        y=y0+sign*(q.numerator//q.denominator)
        result.append((y,x) if steep else (x,y))
    return result[::-1] if backward else result


def verify():
    locations=[(x,y) for x in range(-4,5) for y in range(-4,5)]
    checked=0
    for a in locations:
        for b in locations:
            pts=line_points(*a,*b)
            assert pts == reference_points(*a,*b)
            assert pts == line_points(*b,*a)[::-1]
            assert pts[0] == a and pts[-1] == b
            assert len(pts) == max(abs(a[0]-b[0]),abs(a[1]-b[1]))+1
            assert len(set(pts)) == len(pts)
            assert all(max(abs(p[0]-q[0]),abs(p[1]-q[1]))==1
                       for p,q in zip(pts,pts[1:]))
            checked+=1
    return checked


if __name__ == '__main__':
    print('x y decision_before move decision_after')
    for row in shallow_trace():
        print(*row)
    print('points:',line_points(0,0,11,4))
    print('reverse:',line_points(2,1,0,0))
    print('verified endpoint pairs:',verify())
