"""MIT licensed: render two original toy brick rows from actual parser results.
Optional Pillow dependency; not a screenshot or commercial game asset.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from parser_lab import Parser, evaluate
HERE=Path(__file__).resolve().parent
for name,source in [('normal','2+3*4'),('grouped','(2+3)*4')]:
    count=evaluate(Parser(source).parse())
    im=Image.new('RGB',(600,100),'#263f49');d=ImageDraw.Draw(im)
    for i in range(count):
        x=18+i*28
        d.rectangle((x,30,x+25,73),fill='#ca8b51' if i%2==0 else '#b97646')
        d.line((x+2,32,x+23,32),fill='#e7b57d',width=2)
    im.save(HERE/f'{name}-tiles.png')
    print(source,count)
