#!/usr/bin/env python3
"""The two portraits the article uses. MIT.

originals/ holds the Commons downloads; assets/ gets the scaled version with
the credit line the licence asks for.
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


def portrait(name, src, face_h, title, lines, purpose, source):
    im = Image.open(ORIGINALS / src).convert('RGB')
    width = int(im.width * face_h / im.height)
    im = im.resize((width, face_h), Image.LANCZOS)
    canvas = Image.new('RGB', (W, face_h + 32 + 52 * len(lines)), BG)
    canvas.paste(im, ((W - width) // 2, 0))
    d = ImageDraw.Draw(canvas)
    d.text((24, face_h + 14), title, fill=INK, font=font(38))
    for i, text in enumerate(lines):
        d.text((24, face_h + 68 + i * 52), text, fill=GRAY, font=font(32))
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=32,
                     effective_min_at_354px=round(32 * 354 / W, 2),
                     purpose=purpose, identity='真实照片', source=source))
    print('  ', name, canvas.size, path.stat().st_size)


def main():
    portrait('02-lempel.jpg', 'lempel.jpg', 620, 'Abraham Lempel（1936–2023）',
             ['Technion 计算机科学教授，LZ77 / LZ78 的第一作者',
              'Wikimedia Commons，CC BY 3.0'],
             'Abraham Lempel 肖像', 'Wikimedia Commons, CC BY 3.0')
    portrait('03-ziv.jpg', 'ziv.jpg', 620, 'Jacob Ziv（1931– ）',
             ['Technion 教授，信息论学家，2021 年 IEEE 荣誉勋章',
              'Wikimedia Commons，公有领域'],
             'Jacob Ziv 肖像', 'Wikimedia Commons, 公有领域')
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
