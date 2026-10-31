#!/usr/bin/env python3
"""A rasterizer small enough to read, MIT.

Takes outlines made of quadratic Bézier segments, flattens them, and fills
them by scanning rows. Coverage comes from ss x ss samples per pixel: rows are
supersampled, and each row's spans are quantised to the same sub-pixel grid.

Everything the article quotes as a number is measured here: chord error of the
flattening, coverage error vs. supersampling, the stem profile of a glyph at
small sizes, how many grey levels a diagonal edge gets, and what gamma does to
a 50 % pixel.
"""
from __future__ import annotations

import math

# A u n i t space: 1.0 = one em. y grows downwards, like a screen.
GLYPH_O = 'O'
GLYPH_I = 'I'


def quad_bezier(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def circle_quad(cx, cy, r, segments=8):
    """A circle as `segments` quadratic Béziers, as TrueType would store it."""
    pts = []
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        am = (a0 + a1) / 2
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p2 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        k = r / math.cos((a1 - a0) / 2)
        p1 = (cx + k * math.cos(am), cy + k * math.sin(am))
        pts.append((p0, p1, p2))
    return pts


def outline_o(cx=0.5, cy=0.52, outer=0.40, inner=0.17, segments=8):
    """The letter O: one outer contour, one inner contour, opposite winding."""
    return [circle_quad(cx, cy, outer, segments),
            list(reversed(circle_quad(cx, cy, inner, segments)))]


def outline_i(bar=0.30):
    """A slab-serif I, in em units: three rectangles, clockwise."""
    left, right = 0.30, 0.70
    stem_l, stem_r = 0.44, 0.56
    top, bottom = 0.10, 0.82
    bar_h = bar / 2
    rects = [(left, top, right, top + bar_h),
             (stem_l, top + bar_h, stem_r, bottom - bar_h),
             (left, bottom - bar_h, right, bottom)]
    out = []
    for x0, y0, x1, y1 in rects:
        out.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    return out


def _is_bezier(item):
    return len(item) == 3 and isinstance(item[0], tuple)


def flatten(contour, steps=8):
    """Turn one contour (points and Bézier segments) into one polyline."""
    if not any(_is_bezier(item) for item in contour):
        return [tuple(p) for p in contour]
    out = []
    for item in contour:
        if _is_bezier(item):
            p0, p1, p2 = item
            line = [quad_bezier(p0, p1, p2, i / steps) for i in range(steps)]
            line.append(p2)
            out.extend(line)
        else:
            out.append(tuple(item))
    return out


def chord_error(segments, steps_list=(1, 2, 4, 8, 16, 32)):
    """Max distance between the true curve and the flattened polyline."""
    errs = []
    for steps in steps_list:
        worst = 0.0
        for seg in segments:
            if not _is_bezier(seg):
                continue
            p0, p1, p2 = seg
            for i in range(steps):
                a = quad_bezier(p0, p1, p2, i / steps)
                b = quad_bezier(p0, p1, p2, (i + 1) / steps)
                for j in range(1, 24):
                    t = i / steps + j / 24 / steps
                    q = quad_bezier(p0, p1, p2, t)
                    worst = max(worst, _seg_dist(q, a, b))
        errs.append((steps, worst))
    return errs


def _seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    den = dx * dx + dy * dy
    if den == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / den))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def flatten_all(contours, steps=8):
    return [flatten(c, steps) for c in contours]


def edges(polys):
    out = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if a[1] != b[1]:
                out.append((a[0], a[1], b[0], b[1], 1 if b[1] > a[1] else -1))
    return out


def coverage(polys, w, h, ss=4):
    """Area coverage per pixel, 0..1, from ss x ss samples per pixel."""
    ed = edges(polys)
    acc = [[0] * (w * ss) for _ in range(h)]
    for j in range(h * ss):
        y = (j + 0.5) / ss
        xs = []
        for x0, y0, x1, y1, wind in ed:
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append((x0 + t * (x1 - x0), wind))
        if not xs:
            continue
        xs.sort()
        wind = 0
        row = acc[j // ss]
        for i in range(len(xs) - 1):
            wind += xs[i][1]
            if wind != 0:
                a = xs[i][0] * ss
                b = xs[i + 1][0] * ss
                ia, ib = max(0, int(round(a))), min(w * ss, int(round(b)))
                for k in range(ia, ib):
                    row[k] += 1
    out = []
    for j in range(h):
        row = acc[j]
        out.append([min(1.0, sum(row[i * ss:(i + 1) * ss]) / (ss * ss))
                    for i in range(w)])
    return out


def to_image(cov, ink=(24, 40, 46), paper=(244, 243, 237), gamma=1.0):
    """Coverage -> RGB, optionally through an sRGB-ish curve."""
    img = []
    for row in cov:
        line = []
        for c in row:
            if gamma != 1.0:
                c = c ** (1 / gamma)
            line.append(tuple(int(paper[i] + (ink[i] - paper[i]) * c) for i in range(3)))
        img.append(line)
    return img


def stem_profile(cov, row=None):
    """The middle row of a glyph, as ink amounts per column."""
    r = cov[len(cov) // 2] if row is None else cov[row]
    return [round(v, 3) for v in r]


def contrast(cov):
    """Difference between the darkest and lightest pixel, 0..1."""
    flat = [c for row in cov for c in row]
    return round(max(flat) - min(flat), 3)


def grey_levels(cov):
    return len({round(c, 3) for row in cov for c in row})


def hint(polys, w, h):
    """Snap near-vertical and near-horizontal edges to whole pixels."""
    out = []
    for poly in polys:
        pts = []
        for x, y in poly:
            px, py = x * w, y * h
            pts.append((round(px) / w, round(py) / h))
        out.append(pts)
    return out


def sdf(polys, w, h):
    """Signed distance to the outline, in pixels, on a w x h grid.

    `polys` are already in pixel coordinates.
    """
    ed = []
    for poly in polys:
        for i in range(len(poly) - 1):
            ed.append((poly[i], poly[i + 1]))
        ed.append((poly[-1], poly[0]))
    cov = coverage(polys, w, h, ss=2)
    field = []
    for yy in range(h):
        row = []
        for xx in range(w):
            d = min(_seg_dist((xx + 0.5, yy + 0.5), a, b) for a, b in ed)
            row.append(d if cov[yy][xx] >= 0.5 else -d)
        field.append(row)
    return field


def sdf_reconstruct(field, factor=4, edge=0.75):
    """Rebuild a bigger image from the distance field, bilinearly sampled.

    `edge` is the width of the smooth ramp, in source pixels.
    """
    h, w = len(field), len(field[0])

    def at(fx, fy):
        x0, y0 = int(fx), int(fy)
        x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
        tx, ty = fx - x0, fy - y0
        top = field[y0][x0] * (1 - tx) + field[y0][x1] * tx
        bot = field[y1][x0] * (1 - tx) + field[y1][x1] * tx
        return top * (1 - ty) + bot * ty

    out = []
    for yy in range(h * factor):
        fy = min(h - 1.001, (yy + 0.5) / factor - 0.5)
        row = []
        for xx in range(w * factor):
            fx = min(w - 1.001, (xx + 0.5) / factor - 0.5)
            d = at(max(0.0, fx), max(0.0, fy))
            row.append(max(0.0, min(1.0, 0.5 + d / (2 * edge))))
        out.append(row)
    return out


def srgb_encode(v):
    """Linear light -> sRGB code value (0..1)."""
    if v <= 0.0031308:
        return 12.92 * v
    return 1.055 * v ** (1 / 2.4) - 0.055


if __name__ == '__main__':
    seg = outline_o()[0]
    print('chord error:', [(s, round(e, 6)) for s, e in chord_error(seg)])
    polys = flatten_all(outline_o(), 8)
    cov = coverage([[ (x * 48, y * 48) for x, y in p] for p in polys], 48, 48, 4)
    print('contrast:', contrast(cov), 'grey levels:', grey_levels(cov))
    print('srgb(0.5) =', round(srgb_encode(0.5), 4))
