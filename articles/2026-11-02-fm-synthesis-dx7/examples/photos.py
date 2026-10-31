#!/usr/bin/env python3
"""The three real photographs/documents the article uses. MIT.

`originals/` holds the bytes downloaded from Wikimedia Commons (the patent
sheet is page 2 of the PDF rendered at 150 dpi with PyMuPDF). What lands in
assets/ is scaled, with the credit line the licence asks for.
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


def _band(canvas, lines, top):
    d = ImageDraw.Draw(canvas)
    for i, (text, size, color) in enumerate(lines):
        d.text((20, top + i * 48), text, font=font(size), fill=color)
    return canvas


def _padd(im, pad=24):
    canvas = Image.new('RGB', (im.width + 2 * pad, im.height + 2 * pad), BG)
    canvas.paste(im, (pad, pad))
    return canvas


def _fit(src, height, box=None):
    im = Image.open(ORIGINALS / src).convert('RGB')
    if box:
        im = im.crop(box)
    width = int(im.width * height / im.height)
    return im.resize((width, height), Image.LANCZOS)


def _add(name, im, caption, purpose, source, credit_h=64):
    canvas = Image.new('RGB', (W, im.height + credit_h), BG)
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


def dx7():
    im = _fit('dx7.jpg', 620)
    _add('02-dx7.jpg', im,
         'Yamaha DX7，1983 年。面板上最显眼的不是键盘，是那块两行液晶',
         'Yamaha DX7 实物', 'Wikimedia Commons, doryfour, CC BY-SA 2.0')


def chowning():
    face = _fit('chowning.jpg', 560)
    canvas = Image.new('RGB', (W, 560 + 180), BG)
    x0 = (W - face.width) // 2
    canvas.paste(face, (x0, 10))
    _band(canvas, [('John Chowning，斯坦福 CCRMA 的创办者', 34, INK),
                   ('照片原图 452×608，已放大到 560 高', 32, GRAY)], 590)
    path = ASSETS / '03-chowning.jpg'
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/03-chowning.jpg', width=canvas.width,
                     height=canvas.height, min_label_px=32,
                     effective_min_at_354px=round(32 * 354 / W, 2),
                     purpose='John Chowning 肖像',
                     identity='真实照片（原图已放大）',
                     source='Wikimedia Commons, CC BY-SA 3.0'))
    print('   03-chowning.jpg', canvas.size, path.stat().st_size)


def patent():
    im = _fit('patent-sheet1.png', 980)
    im = _padd(im, 16)
    canvas = Image.new('RGB', (W, im.height + 250), BG)
    canvas.paste(im, ((W - im.width) // 2, 0))
    _band(canvas, [('US 4,018,121 的附图 1（1977 年 4 月 19 日授权）', 34, INK),
                   ('上半部是四个参数随时间变化的曲线，下半部是频谱', 32, GRAY),
                   ('公有领域，来自美国专利商标局', 32, GRAY)], im.height + 14)
    path = ASSETS / '04-patent-sheet.png'
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/04-patent-sheet.png', width=canvas.width,
                     height=canvas.height, min_label_px=32,
                     effective_min_at_354px=round(32 * 354 / W, 2),
                     purpose='Chowning 的 FM 专利附图',
                     identity='真实文件（专利附图扫描）',
                     source='Wikimedia Commons, 公有领域'))
    print('   04-patent-sheet.png', canvas.size, path.stat().st_size)


def main():
    dx7()
    chowning()
    patent()
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
