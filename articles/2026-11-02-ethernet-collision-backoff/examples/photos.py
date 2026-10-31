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
    text = caption
    while d.textlength(text, font(32)) > W - 40:
        text = text[:-2]
    d.text((20, im.height + 12), text, font=font(32), fill=GRAY)
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=32,
                     effective_min_at_354px=round(32 * 354 / W, 2),
                     purpose=purpose, identity='真实照片', source=source))
    print('  ', name, canvas.size, path.stat().st_size)


def _fit(src, height, box=None):
    im = Image.open(ORIGINALS / src).convert('RGB')
    if box:
        im = im.crop(box)
    width = int(im.width * height / im.height)
    return im.resize((width, height), Image.LANCZOS)


def portrait():
    """Metcalfe, from the official National Medal of Technology photograph.

    The source is 229x350, so it is enlarged to 420 high (1.2x) inside a
    two-panel canvas next to the memo he wrote in 1973.
    """
    face = _fit('metcalfe.jpg', 420)
    memo = _fit('memo.jpg', 420)
    gap = 36
    total = face.width + gap + memo.width
    canvas = Image.new('RGB', (W, 420 + 240), BG)
    x0 = (W - total) // 2
    canvas.paste(face, (x0, 10))
    canvas.paste(memo, (x0 + face.width + gap, 10))
    d = ImageDraw.Draw(canvas)
    small = font(38)
    d.text((x0, 452), 'Robert Metcalfe', font=small, fill=INK)
    d.text((x0 + face.width + gap, 452), '1973 年的备忘录', font=small, fill=INK)
    credit = font(34)
    d.text((20, 506), '左：美国国家技术奖官方照，公有领域，原图 229×350 已放大',
           font=credit, fill=GRAY)
    d.text((20, 552), '右：梅特卡夫备忘录封面与首页，公有领域', font=credit,
           fill=GRAY)
    d.text((20, 598), '两图均来自 Wikimedia Commons', font=credit, fill=GRAY)
    path = ASSETS / '02-metcalfe-and-memo.jpg'
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/02-metcalfe-and-memo.jpg', width=canvas.width,
                     height=canvas.height, min_label_px=34,
                     effective_min_at_354px=round(34 * 354 / W, 2),
                     purpose='梅特卡夫肖像与 1973 年以太网备忘录',
                     identity='真实照片（肖像原图 229×350 已放大）',
                     source='Wikimedia Commons, 公有领域'))
    print('   02-metcalfe-and-memo.jpg', canvas.size, path.stat().st_size)


def alto():
    im = _fit('alto.jpg', 620)
    _add('03-xerox-alto.jpg', im,
         'Xerox Alto（1973），施乐帕克研究中心，现存于计算机历史博物馆',
         '施乐 Alto 工作站', 'Wikimedia Commons, The wub, CC BY-SA 4.0')


def connector():
    im = _fit('connector.jpg', 620)
    _add('19-ethernet-connector.jpg', im,
         '早期以太网收发器接头，上面有 Bob Metcalfe 的签名',
         '早期以太网接头实物', 'Wikimedia Commons, Daderot, CC0')


def main():
    portrait()
    alto()
    connector()
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
