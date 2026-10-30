import sys
import numpy as np
from PIL import Image, ImageEnhance
def grade(src, dst, contrast=1.06, sat=1.07, bg=None, crop=False):
    im = Image.open(src).convert("RGBA")
    if bg is not None:
        base = Image.new("RGBA", im.size, bg)
        base.alpha_composite(im)
        im = base
    rgb = im.convert("RGB")
    a = np.asarray(rgb).astype(np.float32) / 255.0
    # gentle S-curve around mid-grey
    a = np.clip(0.5 + (a - 0.5) * contrast, 0, 1)
    a = a + 0.04 * np.sin(np.pi * a) * (a - 0.5) * 2 * 0.5
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(sat)
    if crop:
        al = np.asarray(Image.open(src).convert("RGBA"))[..., 3]
        ys, xs = np.where(al > 8)
        m = 50
        box = (max(0, xs.min() - m), max(0, ys.min() - m), min(out.width, xs.max() + m), min(out.height, ys.max() + m))
        out = out.crop(box)
    out.save(dst, quality=92)
if __name__ == "__main__":
    grade(sys.argv[1], sys.argv[2])
