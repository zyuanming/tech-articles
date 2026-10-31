#!/usr/bin/env python3
"""Real photographs used by the article, resized and credited. MIT.

The originals are the Wikimedia Commons files named below; `originals/` holds
the exact bytes that were downloaded, and assets/ holds the version shipped
with the article (same picture, scaled to the column width, plus the credit
line that the licence asks for).
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


def credited(src, name, credit, purpose, target_h=None, crop=None):
    im = Image.open(ORIGINALS / src).convert('RGB')
    if crop:
        im = im.crop(crop)
    if target_h:
        w = int(im.width * target_h / im.height)
        im = im.resize((w, target_h), Image.LANCZOS)
    if im.width != W:
        h = int(im.height * W / im.width)
        im = im.resize((W, h), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    line = font(34)
    text = credit
    tw = d.textlength(text, font=line)
    while tw > W - 40:
        text = text[:-2]
        tw = d.textlength(text, font=line)
    band = 56
    canvas = Image.new('RGB', (W, im.height + band), BG)
    canvas.paste(im, (0, 0))
    cd = ImageDraw.Draw(canvas)
    cd.text((20, im.height + 8), text, font=line, fill=GRAY)
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=34,
                     effective_min_at_354px=round(34 * 354 / W, 2),
                     purpose=purpose, identity='真实照片', source=credit))
    print('  ', name, canvas.size, path.stat().st_size)


def main():
    credited('lamport.jpg', '25-leslie-lamport.jpg',
             'Leslie Lamport, 2006. 摄影：Leslie Lamport / Wikimedia Commons，'
             'Copyrighted free use',
             'Leslie Lamport 的肖像')
    credited('paxos-island.jpg', '26-paxos-island.jpg',
             '希腊帕克索斯岛（Paxos）。摄影：Arxoland / Wikimedia Commons，CC BY-SA 4.0',
             '论文得名的那座岛', crop=(0, 240, 5216, 1180))
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(rows))


if __name__ == '__main__':
    main()
