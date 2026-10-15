"""Optional real PPM decoder check; requires Pillow, does not run rsync. MIT."""
from pathlib import Path
from PIL import Image, __version__
import hashlib,json
HERE=Path(__file__).resolve().parent
with Image.open(HERE/'landscape-old.ppm') as old, Image.open(HERE/'landscape-new.ppm') as new:
    old.load();new.load()
    assert old.size==new.size==(96,64) and old.mode==new.mode=='RGB'
    assert old.tobytes()==new.tobytes()
    result=dict(decoder='Pillow',pillow_version=__version__,size=old.size,mode=old.mode,decoded_bytes=len(old.tobytes()),pixels_equal=True,pixel_sha256=hashlib.sha256(old.tobytes()).hexdigest(),first_pixel=list(old.getpixel((0,0))))
(HERE/'pixel-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
