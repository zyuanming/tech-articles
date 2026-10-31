#!/usr/bin/env python3
"""Real photographs used by the article, resized and credited. MIT.

`originals/` holds the exact bytes downloaded from Wikimedia Commons.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from figkit import BG, GRAY, INK, font

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ORIGINALS = ART / 'originals'
META = []
W = 1062


def _save(name, canvas, purpose, source, identity='真实照片', min_px=34):
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=min_px,
                     effective_min_at_354px=round(min_px * 354 / W, 2),
                     purpose=purpose, identity=identity, source=source))
    print('  ', name, canvas.size, path.stat().st_size)


def pair():
    """Two photographs on one canvas, same displayed height."""
    knuth = Image.open(ORIGINALS / 'knuth.jpg').convert('RGB')
    knuth = knuth.resize((int(knuth.width * 420 / knuth.height), 420), Image.LANCZOS)
    nexts = Image.open(ORIGINALS / 'nextstation.jpg').convert('RGB')
    nexts = nexts.resize((int(nexts.width * 420 / nexts.height), 420), Image.LANCZOS)
    gap = 40
    total = knuth.width + gap + nexts.width
    canvas = Image.new('RGB', (W, 420 + 210), BG)
    x0 = (W - total) // 2
    canvas.paste(knuth, (x0, 10))
    canvas.paste(nexts, (x0 + knuth.width + gap, 10))
    d = ImageDraw.Draw(canvas)
    small = font(36)
    d.text((x0, 446), 'Donald Knuth', font=small, fill=INK)
    d.text((x0 + knuth.width + gap, 446), 'NeXTstation', font=small, fill=INK)
    credit = font(34)
    d.text((20, 496), 'Wikimedia Commons，CC BY-SA 2.5 / 3.0', font=credit, fill=GRAY)
    d.text((20, 540), '左：Metafont 与 TeX 的作者。', font=credit, fill=GRAY)
    d.text((20, 584), '右：1988 年的机器，屏幕有 4 级灰度。', font=credit, fill=GRAY)
    _save('21-knuth-and-next.jpg', canvas,
          'Donald Knuth 与 NeXTstation',
          'Wikimedia Commons, CC BY-SA 2.5 / CC BY-SA 3.0')


def main():
    pair()
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
