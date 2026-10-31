#!/usr/bin/env python3
"""The five real pictures the article uses. MIT.

originals/ holds what came off Wikimedia Commons and the patent scan; assets/
gets the scaled version with the credit line the licence asks for.
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


def picture(name, src, height, title, lines, purpose, source, identity='真实照片'):
    im = Image.open(ORIGINALS / src).convert('RGB')
    width = min(W, int(im.width * height / im.height))
    im = im.resize((width, height), Image.LANCZOS)
    canvas = Image.new('RGB', (W, height + 28 + 54 * len(lines)), BG)
    canvas.paste(im, ((W - width) // 2, 0))
    d = ImageDraw.Draw(canvas)
    d.text((24, height + 8), title, fill=INK, font=font(42))
    for i, text in enumerate(lines):
        d.text((24, height + 66 + i * 54), text, fill=GRAY, font=font(36))
    path = ASSETS / name
    canvas.save(path, quality=92)
    assert path.stat().st_size <= 5_000_000, path
    META.append(dict(path='assets/' + name, width=canvas.width,
                     height=canvas.height, min_label_px=36,
                     effective_min_at_354px=round(36 * 354 / W, 2),
                     purpose=purpose, identity=identity, source=source))
    print('  ', name, canvas.size, path.stat().st_size)


def main():
    picture('02-hedy.jpg', 'hedy.jpg', 640,
            'Hedy Lamarr，1940 年（当时 26 岁）',
            ['米高梅的宣传照，拍在专利申请的前一年',
             'Wikimedia Commons，公有领域'],
            'Hedy Lamarr 肖像', 'Wikimedia Commons, 公有领域')

    picture('03-antheil.jpg', 'antheil.jpg', 640,
            'George Antheil',
            ['作曲家，与 Lamarr 共同署名；他熟悉自动钢琴的同步机构',
             'Wikimedia Commons，公有领域'],
            'George Antheil 肖像', 'Wikimedia Commons, 公有领域')

    picture('05-patent-front.jpg', 'patent-front.jpg', 1240,
            'US 2,292,387 首页：Secret Communication System',
            ['申请日 1941-06-10，授权日 1942-08-11，署名',
             '「Hedy Kiesler Markey」与「George Antheil」',
             '公有领域（美国专利局）'],
            '专利首页扫描', '美国专利商标局，公有领域', identity='档案扫描件')

    picture('06-patent-sheet1.jpg', 'patent-sheet1.jpg', 1240,
            '专利附图第 1 张：发射端与接收端的框图',
            ['7 个调谐电容、记录纸带、同步电机都在这一张里',
             '公有领域（美国专利局）'],
            '专利附图', '美国专利商标局，公有领域', identity='档案扫描件')

    picture('04-piano-roll.jpg', 'pianoroll.jpg', 700,
            '自动钢琴的纸卷与它的读孔机构',
            ['专利里的「记录纸带」就是这个东西：一排排孔决定按下哪些键',
             '摄影 Shannon Prickett，CC BY 2.0'],
            '自动钢琴纸卷', 'Wikimedia Commons, CC BY 2.0, Shannon Prickett')

    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('visuals:', len(rows))


if __name__ == '__main__':
    main()
