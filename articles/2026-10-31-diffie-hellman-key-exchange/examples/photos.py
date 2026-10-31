#!/usr/bin/env python3
"""Real photographs used by the article, resized and credited. MIT.

`originals/` holds the exact bytes downloaded from Wikimedia Commons. What
lands in assets/ is the same picture, scaled, with the credit line the licence
asks for. Nothing is retouched, generated or replaced.
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


def _add(name, im, caption, purpose, source, credit_h=64):
    """Put a caption band under the picture, save, and record the metadata."""
    band = credit_h
    canvas = Image.new('RGB', (W, im.height + band), BG)
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    line = font(32)
    text = caption
    while d.textlength(text, font=line) > W - 40:
        text = text[:-2]
    d.text((20, im.height + 12), text, font=line, fill=GRAY)
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=32,
                     effective_min_at_354px=round(32 * 354 / W, 2),
                     purpose=purpose, identity='真实照片', source=source))
    print('  ', name, canvas.size, path.stat().st_size)


def portraits():
    """Both authors on one canvas, at the same displayed height."""
    diffie = Image.open(ORIGINALS / 'diffie.jpg').convert('RGB').crop((0, 40, 648, 520))
    diffie = diffie.resize((int(diffie.width * 420 / diffie.height), 420), Image.LANCZOS)
    hellman = Image.open(ORIGINALS / 'hellman.jpg').convert('RGB')
    hellman = hellman.resize((int(hellman.width * 420 / hellman.height), 420), Image.LANCZOS)
    gap = 36
    total = diffie.width + gap + hellman.width
    canvas = Image.new('RGB', (W, 420 + 230), BG)
    x0 = (W - total) // 2
    canvas.paste(diffie, (x0, 10))
    canvas.paste(hellman, (x0 + diffie.width + gap, 10))
    d = ImageDraw.Draw(canvas)
    small = font(38)
    d.text((x0, 448), 'Whitfield Diffie', font=small, fill=INK)
    d.text((x0 + diffie.width + gap, 448), 'Martin Hellman', font=small, fill=INK)
    credit = font(34)
    d.text((20, 496), 'Wikimedia Commons', font=credit, fill=GRAY)
    d.text((20, 540), '左：Duncan.Hull，CC BY-SA 4.0', font=credit, fill=GRAY)
    d.text((20, 584), '右：CC BY-SA 3.0，原图 240×280 已放大', font=credit, fill=GRAY)
    path = ASSETS / '21-two-authors.jpg'
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000
    META.append(dict(path='assets/21-two-authors.jpg', width=canvas.width,
                     height=canvas.height, min_label_px=34,
                     effective_min_at_354px=round(34 * 354 / W, 2),
                     purpose='两位作者的肖像',
                     identity='真实照片（Hellman 那张经过放大）',
                     source='Wikimedia Commons, CC BY-SA 4.0 / CC BY-SA 3.0'))
    print('   21-two-authors.jpg', canvas.size, path.stat().st_size)


def main():
    portraits()
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
