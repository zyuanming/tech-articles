"""Bresenham 画线、中点圆，以及和浮点 DDA 的逐像素对照。

全部整数运算，除 DDA（故意用浮点，用来当对照）和圆半径的平方根外不引入浮点。
只用标准库。
"""


def bresenham(x0, y0, x1, y1):
    """Bresenham 1965 的整数画线。返回经过的像素（(x, y) 列表，按 x 递增）。

    只写第一八分圆（0 <= dy <= dx），其余七种情况由调用者做轴交换和符号翻转，
    这也是原算法的结构：一段 40 行的内循环，外面套 8 个变换。
    """
    pts = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    steep = dy > dx
    if steep:
        dx, dy = dy, dx
    # 误差项：D = 2*dy - dx，初值取第一列的中点判定
    d = 2 * dy - dx
    x, y = x0, y0
    for _ in range(dx + 1):
        pts.append((x, y))
        if steep:
            y += sy
        else:
            x += sx
        if d > 0:
            if steep:
                x += sx
            else:
                y += sy
            d -= 2 * dx
        d += 2 * dy
    return pts


def err_trace(x0, y0, x1, y1):
    """同一条线段上误差项的逐步取值，给手算用。

    返回每步的 (k, d, 判据)，判据为 'y' 表示这一步 y 增 1。
    """
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    assert dy <= dx
    d = 2 * dy - dx
    rows = []
    for k in range(dx + 1):
        rows.append((k, d, 'y' if d > 0 else '-'))
        if d > 0:
            d -= 2 * dx
        d += 2 * dy
    return rows


def dda_round(x0, y0, x1, y1):
    """浮点 DDA：y = y0 + k*(y1-y0)/(x1-x0)，四舍五入到最近的像素。"""
    pts = []
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        t = i / float(n)
        pts.append((int(round(x0 + t * (x1 - x0))), int(round(y0 + t * (y1 - y0)))))
    return pts


def midpoint_circle(r):
    """Bresenham 1977 的中点圆：只用整数加法和移位，画第一八分圆再 8 路镜像。"""
    pts = set()
    x, y = 0, r
    d = 1 - r
    while x <= y:
        for sx, sy in ((x, y), (y, x)):
            pts.add((sx, sy))
            pts.add((-sx, sy))
            pts.add((sx, -sy))
            pts.add((-sx, -sy))
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
    return sorted(pts)


def circle_round(r):
    """对照：对每个 x 算 sqrt(r^2 - x^2) 再四舍五入。"""
    pts = set()
    for x in range(-r, r + 1):
        v = (r * r - x * x) ** 0.5
        for y in (int(round(v)), -int(round(v))):
            pts.add((x, y))
        if v != int(v):
            pts.add((x, int(v)))
            pts.add((x, -int(v)))
    return sorted(pts)


def lcg(seed):
    """固定种子的线性同余，给「几千条线段」那组实验用。"""
    state = [seed & 0xFFFFFFFF]

    def nxt():
        state[0] = (1103515245 * state[0] + 12345) & 0x7FFFFFFF
        return state[0]

    return nxt


def rand_segments(count, seed=20270329, span=48):
    nxt = lcg(seed)
    out = []
    for _ in range(count):
        x0 = nxt() % (2 * span + 1) - span
        y0 = nxt() % (2 * span + 1) - span
        x1 = nxt() % (2 * span + 1) - span
        y1 = nxt() % (2 * span + 1) - span
        if (x0, y0) == (x1, y1):
            continue
        out.append((x0, y0, x1, y1))
    return out


def to_center(pts):
    """像素坐标 (ix, iy) -> 像素中心 (ix + 0.5, iy + 0.5)。"""
    return [(x + 0.5, y + 0.5) for (x, y) in pts]


def dist_to_line(p, a, b):
    """点 p 到过 a、b 的直线的垂直距离。"""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    n = (dx * dx + dy * dy) ** 0.5
    return abs((p[0] - ax) * dy - (p[1] - ay) * dx) / n


def max_dev(pts, x0, y0, x1, y1):
    """每个被点亮的像素中心到理想线段的垂直距离，取最大值（单位：像素）。"""
    a, b = (x0, y0), (x1, y1)
    return max(dist_to_line(p, a, b) for p in to_center(pts))


def dev_integer(pts, x0, y0, x1, y1):
    """沿主轴量：整数坐标处的理想值与被点亮像素之间，差多少（单位：像素）。

    这是 Bresenham 真正保证的量。主轴是 x 时比较 y(x) 与像素的 y，
    主轴是 y 时比较 x(y) 与像素的 x。
    """
    dx, dy = x1 - x0, y1 - y0
    steep = abs(dy) > abs(dx)
    worst = 0.0
    for (x, y) in pts:
        if steep:
            ideal = x0 + (y - y0) * (dx / float(dy))
            worst = max(worst, abs(ideal - x))
        else:
            ideal = y0 + (x - x0) * (dy / float(dx))
            worst = max(worst, abs(ideal - y))
    return worst


def dev_center(pts, x0, y0, x1, y1):
    """沿主轴量，但在像素中心处取值：|理想(中心) − 像素中心|。"""
    dx, dy = x1 - x0, y1 - y0
    steep = abs(dy) > abs(dx)
    worst = 0.0
    for (x, y) in pts:
        if steep:
            ideal = x0 + (y + 0.5 - y0) * (dx / float(dy))
            worst = max(worst, abs(ideal - (x + 0.5)))
        else:
            ideal = y0 + (x + 0.5 - x0) * (dy / float(dx))
            worst = max(worst, abs(ideal - (y + 0.5)))
    return worst


def wu_coverage(x0, y0, x1, y1):
    """Xiaolin Wu 1991 的 8 级抗锯齿画线（只做 0<=dy<=dx 的浅斜率）。

    返回 [(像素, 覆盖度 0..255)]，用来和 1 位的 Bresenham 画在同一张图上。
    """
    out = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    assert dy <= dx
    grad = dy / float(dx) if dx else 0.0
    bloat = 255

    def fpart(v):
        return v - int(v)

    def rfpart(v):
        return 1.0 - fpart(v)

    x = x0
    yy = float(y0)
    for _ in range(dx + 1):
        ip = int(yy)
        frac = fpart(yy)
        out.append(((x, ip), int((1 - frac) * bloat)))
        out.append(((x, ip + 1), int(frac * bloat)))
        x += 1
        yy += grad
    return out


def ops_breakdown(x0, y0, x1, y1):
    """数一条线段上两种算法各用了多少次乘除。

    Bresenham：内循环里除 2*dy、2*dx 这类常量倍之外没有乘除，
    而 2*n 是移位，正文按 0 次算。
    朴素做法：每列重算 y = y0 + k*dy/dx，一次乘法一次除法，全程浮点。
    """
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    return {'pixels': n, 'mul_bresenham': 0, 'div_bresenham': 0,
            'mul_naive': n, 'div_naive': n}
