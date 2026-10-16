"""Deterministic figure toolkit: draw, then prove the geometry is sane.

Every text placement is recorded with its real pixel bbox. `verify()` refuses
to let a figure ship when a glyph leaves the canvas, crosses a box border it
was declared inside, collides with another label, or falls under the mobile
font floor. MIT.
"""
from __future__ import annotations
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W = 1062                      # canvas width used by this series
DISPLAY_W = 354.0             # 390px phone minus 2x18px gutters
MIN_DESIGN_PX = 38            # hard floor for any glyph on the canvas
TARGET_EFFECTIVE_PX = 12.0    # repo floor for key labels at display width

BG = '#f4f3ed'; WHITE = '#ffffff'; INK = '#183440'; INK_SOFT = '#4a6570'
TEAL = '#147d84'; BLUE = '#3468ad'; AMBER = '#ab640b'; RED = '#bc4650'
GRAY = '#697c82'; LIGHT = '#dce6e3'; PALE = '#e8f0f6'; GREEN = '#3f7d4e'
CREAM = '#fdf6e3'; TINT_T = '#e2f0f0'; TINT_B = '#e6edf7'; TINT_A = '#f6ecd9'
TINT_R = '#f7e6e8'; TINT_G = '#e6f0e7'

PALETTE = {BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY, LIGHT,
           PALE, GREEN, CREAM, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G}

_FONT_CANDIDATES = [
    ('/System/Library/Fonts/Hiragino Sans GB.ttc', 0, 2),
    ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 2, 2),
    ('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 2, 2),
    ('/Library/Fonts/Arial Unicode.ttf', 0, 0),
    ('/System/Library/Fonts/STHeiti Medium.ttc', 1, 1),
]
_cache: dict = {}


def _resolve(bold: bool):
    key = 'bold' if bold else 'reg'
    if key in _cache:
        return _cache[key]
    for path, reg_idx, bold_idx in _FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        idx = bold_idx if bold else reg_idx
        try:
            ImageFont.truetype(path, 10, index=idx)
        except OSError:
            continue
        _cache[key] = (path, idx)
        return _cache[key]
    raise RuntimeError('no CJK font found; add one to _FONT_CANDIDATES')


def font(size: int, bold: bool = False):
    path, idx = _resolve(bold)
    return ImageFont.truetype(path, size, index=idx)


class Fig:
    def __init__(self, height: int, bg: str = BG, width: int = W):
        """`height` is a hint; the canvas is allocated tall and cropped to the
        content in save(), so nothing is ever drawn outside the bitmap."""
        assert bg in PALETTE, bg
        self.w = width
        self.h = max(height, 4000)
        self.im = Image.new('RGB', (self.w, self.h), bg)
        self.d = ImageDraw.Draw(self.im)
        self.labels: list[dict] = []
        self.boxes: dict[str, tuple] = {}
        self.shapes: list[tuple] = []      # (kind, bbox, color)
        self.min_px = 10 ** 6
        self.meta: list[dict] = []

    # ---------- primitives ----------
    def box(self, name, x0, y0, x1, y1, fill=WHITE, outline=LIGHT, width=3,
            radius=20):
        for c in (fill, outline):
            assert c in PALETTE, f'stray colour {c}'
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill,
                                 outline=outline, width=width)
        self.boxes[name] = (x0, y0, x1, y1)
        self.shapes.append(('box', (x0, y0, x1, y1), outline))

    def rect(self, x0, y0, x1, y1, fill=WHITE, outline=None, width=2, radius=0):
        for c in (fill, outline):
            assert c is None or c in PALETTE, f'stray colour {c}'
        if radius:
            self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill,
                                     outline=outline, width=width)
        else:
            self.d.rectangle((x0, y0, x1, y1), fill=fill, outline=outline,
                             width=width)
        self.shapes.append(('rect', (x0, y0, x1, y1), outline or fill))

    def line(self, a, b, color=GRAY, width=4, dash=None):
        assert color in PALETTE
        if dash:
            self._dashed(a, b, color, width, dash)
        else:
            self.d.line([a, b], fill=color, width=width)
        self.shapes.append(('line', (min(a[0], b[0]), min(a[1], b[1]),
                                     max(a[0], b[0]), max(a[1], b[1])), color))

    def _dashed(self, a, b, color, width, dash):
        import math
        total = math.hypot(b[0] - a[0], b[1] - a[1])
        if total == 0:
            return
        ux, uy = (b[0] - a[0]) / total, (b[1] - a[1]) / total
        pos = 0.0
        while pos < total:
            end = min(pos + dash, total)
            self.d.line([(a[0] + ux * pos, a[1] + uy * pos),
                         (a[0] + ux * end, a[1] + uy * end)], fill=color,
                        width=width)
            pos = end + dash

    def arrow(self, a, b, color=TEAL, width=5, head=16, dash=None):
        import math
        assert color in PALETTE
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        tip = b
        back = (b[0] - head * 1.6 * math.cos(ang), b[1] - head * 1.6 * math.sin(ang))
        self.line(a, back, color=color, width=width, dash=dash)
        self.d.polygon([tip,
                        (b[0] - head * 2.0 * math.cos(ang - .42),
                         b[1] - head * 2.0 * math.sin(ang - .42)),
                        (b[0] - head * 2.0 * math.cos(ang + .42),
                         b[1] - head * 2.0 * math.sin(ang + .42))], fill=color)

    def circle(self, cx, cy, r, fill=None, outline=TEAL, width=4):
        for c in (fill, outline):
            assert c is None or c in PALETTE, f'stray colour {c}'
        self.d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill,
                       outline=outline, width=width)
        self.shapes.append(('circle', (cx - r, cy - r, cx + r, cy + r),
                            outline or fill))

    def poly(self, pts, fill=TEAL, outline=None):
        assert fill in PALETTE
        self.d.polygon(pts, fill=fill, outline=outline)

    def text(self, xy, s, size, bold=False, color=INK, anchor='la',
             inside=None, allow_overlap=False, tag=None):
        assert color in PALETTE, f'stray colour {color}'
        assert size >= MIN_DESIGN_PX, f'{size}px below the {MIN_DESIGN_PX}px floor: {s!r}'
        f = font(size, bold)
        bb = self.d.textbbox(xy, s, font=f, anchor=anchor)
        self.labels.append(dict(s=s, size=size, bbox=bb, inside=inside,
                                anchor=anchor, allow_overlap=allow_overlap,
                                tag=tag))
        self.min_px = min(self.min_px, size)
        self.d.text(xy, s, font=f, fill=color, anchor=anchor)
        return bb

    def width_of(self, s, size, bold=False):
        return self.d.textbbox((0, 0), s, font=font(size, bold))[2]

    def wrap(self, xy, s, size, max_w, bold=False, color=INK, anchor='la',
             leading=1.35, inside=None, allow_overlap=False):
        lines, cur = [], ''
        for ch in s:
            if ch == '\n':
                lines.append(cur); cur = ''; continue
            if self.width_of(cur + ch, size, bold) > max_w and cur:
                lines.append(cur); cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
        x, y = xy
        for i, ln in enumerate(lines):
            self.text((x, y + i * size * leading), ln, size, bold=bold,
                      color=color, anchor=anchor, inside=inside,
                      allow_overlap=allow_overlap)
        return len(lines)

    # ---------- verification ----------
    def verify(self, margin=8, min_width_coverage=0.86, max_bottom_frac=0.13):
        problems = []
        for lb in self.labels:
            x0, y0, x1, y1 = lb['bbox']
            if x0 < 0 or y0 < 0 or x1 > self.w or y1 > self.h:
                problems.append(f"OFFCANVAS {lb['s']!r} {lb['bbox']}")
            if lb['inside']:
                if lb['inside'] not in self.boxes:
                    problems.append(f"UNKNOWN inside={lb['inside']} for {lb['s']!r}")
                else:
                    bx0, by0, bx1, by1 = self.boxes[lb['inside']]
                    if not (bx0 + margin <= x0 and x1 <= bx1 - margin
                            and by0 + margin <= y0 and y1 <= by1 - margin):
                        problems.append(
                            f"NOT_INSIDE {lb['s']!r} bbox={lb['bbox']} "
                            f"box={self.boxes[lb['inside']]}")
        lab = [l for l in self.labels if not l['allow_overlap']]
        for i in range(len(lab)):
            for j in range(i + 1, len(lab)):
                a, b = lab[i]['bbox'], lab[j]['bbox']
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 2 and oy > 2:
                    problems.append(f"TEXT_OVERLAP {lab[i]['s']!r} / {lab[j]['s']!r}")
        # content extent
        xs0 = min(l['bbox'][0] for l in self.labels)
        xs1 = max(l['bbox'][2] for l in self.labels)
        ys1 = max(l['bbox'][3] for l in self.labels)
        cov = (xs1 - xs0) / self.w
        if cov < min_width_coverage:
            problems.append(f'WIDTH_COVERAGE {cov:.3f} < {min_width_coverage} '
                            f'(x {xs0}..{xs1})')
        bottom = self.h - ys1
        if bottom > max(140, max_bottom_frac * self.h):
            problems.append(f'BOTTOM_GAP {bottom}px of {self.h} unused')
        eff = self.min_px * DISPLAY_W / self.w
        if eff < TARGET_EFFECTIVE_PX:
            problems.append(f'FONT_FLOOR min {self.min_px}px -> {eff:.2f}px at '
                            f'{DISPLAY_W:.0f}px display')
        if problems:
            raise AssertionError('\n'.join(problems))
        return dict(width=self.w, height=self.h, min_label_px=self.min_px,
                    effective_min_at_354px=round(eff, 2))

    def audit_pixels(self, min_ink=40, min_contrast=22.0):
        """Catch labels that drew nothing, or that vanish into what is behind."""
        px = self.im.load()

        def lum(p):
            return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]

        bad = []
        for lb in self.labels:
            x0, y0, x1, y1 = [int(v) for v in lb['bbox']]
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(self.w, x1 + 1), min(self.h, y1 + 1)
            inside = [px[xx, yy] for yy in range(y0, y1) for xx in range(x0, x1)]
            if not inside:
                bad.append((lb['s'], 'empty bbox'))
                continue
            ink = sum(1 for q in inside if q != BG)
            if ink < min_ink:
                bad.append((lb['s'], f'ink={ink}'))
                continue
            ls = sorted(lum(q) for q in inside)
            dark = sum(ls[:max(1, len(ls) // 6)]) / max(1, len(ls) // 6)
            light = sum(ls[-max(1, len(ls) // 6):]) / max(1, len(ls) // 6)
            if light - dark < min_contrast:
                bad.append((lb['s'], f'contrast={light - dark:.1f}'))
        assert not bad, f'labels that will not read: {bad}'
        return True

    def trim(self, margin=52):
        """Crop the empty band under the last drawn thing.

        Canvas height is decided by the content, not by a template, so a
        figure never ships with a dead strip at the bottom.
        """
        ys = max(l['bbox'][3] for l in self.labels)
        for _, bb, _ in self.shapes:
            ys = max(ys, bb[3])
        new_h = int(ys + margin)
        if new_h < self.h:
            self.im = self.im.crop((0, 0, self.w, new_h))
        elif new_h > self.h:
            taller = Image.new('RGB', (self.w, new_h), BG)
            taller.paste(self.im, (0, 0))
            self.im = taller
        self.h = new_h
        self.d = ImageDraw.Draw(self.im)
        return self

    def save(self, path, purpose, identity='原创教学示意', source=None, **vkw):
        self.trim()
        report = self.verify(**vkw)
        self.audit_pixels()
        self.im.save(path)
        row = dict(path=str(path).split('articles/')[-1], width=self.w,
                   height=self.h, min_label_px=self.min_px,
                   effective_min_at_354px=report['effective_min_at_354px'],
                   purpose=purpose, identity=identity)
        if source:
            row['source'] = source
        self.meta.append(row)
        return row


# ---------------------------------------------------------------- chess boards
PIECE_GLYPH = {'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝',
               'N': '♞', 'P': '♟'}
LIGHT_SQ = '#f2e6d0'
DARK_SQ = '#c6b189'
PALETTE.update({LIGHT_SQ, DARK_SQ})


SYMBOL_FONTS = ['/Library/Fonts/Arial Unicode.ttf',
                '/System/Library/Fonts/Apple Symbols.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']


def _symbol_font(size):
    for p in SYMBOL_FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size, index=0)
            except OSError:
                continue
    return font(size)


def glyph_available(ch='♚', size=40) -> bool:
    """True when the CJK/Unicode font really has this glyph (not .notdef)."""
    f = _symbol_font(size)
    def ink(chx):
        im = Image.new('L', (size * 2, size * 2), 0)
        ImageDraw.Draw(im).text((size // 2, size // 2), chx, font=f, fill=255)
        return sum(1 for p in im.getdata() if p > 40)
    return ink(ch) > 60 and ink(ch) != ink('')


def _add_chessboard(cls):
    def chessboard(self, x, y, sq, rows, flip=False, marks=(), arrows=(),
                   files='abcdefgh', label_color=GRAY, labels=True,
                   label_size=40):
        """rows: 8 strings of 8 chars, '.'=empty, upper=white, lower=black."""
        for c in (LIGHT_SQ, DARK_SQ):
            assert c in PALETTE
        for r in range(8):
            for c in range(8):
                rr, cc = (7 - r, 7 - c) if flip else (r, c)
                light = (rr + cc) % 2 == 0
                x0, y0 = x + c * sq, y + r * sq
                self.rect(x0, y0, x0 + sq, y0 + sq,
                          fill=LIGHT_SQ if light else DARK_SQ, outline=None)
        if labels:
            for c in range(8):
                rr = 7 if flip else 0
                cc = 7 - c if flip else c
                self.text((x + c * sq + sq // 2, y + 8 * sq + 14), files[cc],
                          label_size, color=label_color, anchor='ma')
            for r in range(8):
                rr = 7 - r if flip else r
                self.text((x - 16, y + r * sq + sq // 2), str(rr + 1),
                          label_size, color=label_color, anchor='rm')
        for kind, a, b, col in marks:
            if kind == 'sq':
                self.rect(x + a * sq, y + b * sq, x + (a + 1) * sq,
                          y + (b + 1) * sq, fill=None, outline=col, width=6)
            elif kind == 'dot':
                self.circle(x + a * sq + sq // 2, y + b * sq + sq // 2,
                            sq // 7, fill=col, outline=col, width=2)
        for r in range(8):
            for c in range(8):
                ch = rows[r][c]
                if ch == '.':
                    continue
                x0, y0 = x + c * sq, y + r * sq
                white = ch.isupper()
                self.d.text((x0 + sq // 2, y0 + sq // 2), PIECE_GLYPH[ch.upper()],
                            font=_symbol_font(int(sq * 0.82)),
                            fill=WHITE if white else INK,
                            anchor='mm', stroke_width=3,
                            stroke_fill=INK if white else WHITE)
        for a, b, col in arrows:
            self.arrow((x + a[0] * sq + sq // 2, y + a[1] * sq + sq // 2),
                       (x + b[0] * sq + sq // 2, y + b[1] * sq + sq // 2),
                       color=col, width=7, head=14)
        self.shapes.append(('board', (x, y, x + 8 * sq, y + 8 * sq), None))
    cls.chessboard = chessboard


_add_chessboard(Fig)


def bars_are_honest(rows):
    """rows: [(label, value, length_px)] -> raise when the picture lies."""
    by_val = sorted(rows, key=lambda r: r[1])
    by_len = sorted(rows, key=lambda r: r[2])
    assert [r[0] for r in by_val] == [r[0] for r in by_len], \
        'bar length order differs from value order: ' + repr(rows)
