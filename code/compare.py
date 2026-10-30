"""Compose labelled with/without wainscot comparison sheets from graded renders."""
import sys
from PIL import Image, ImageDraw, ImageFont

import os
def _font(name):
    for d in ("/usr/share/fonts/opentype/inter", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT = _font("Inter-Regular.otf")
FONT_B = _font("Inter-SemiBold.otf")
INK = (34, 32, 30)
GREY = (120, 116, 110)
ACCENT = (178, 84, 46)


def sheet(panels, cols, title, sub, out, pw=1000):
    ph = int(pw * 2 / 3)
    g, top, cap = 26, 118, 74
    rows = (len(panels) + cols - 1) // cols
    W = cols * pw + (cols + 1) * g
    H = top + rows * (ph + cap) + g
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(FONT_B, 34)
    fs = ImageFont.truetype(FONT, 22)
    fl = ImageFont.truetype(FONT_B, 24)
    fn = ImageFont.truetype(FONT, 20)
    d.text((g, 26), title, font=ft, fill=INK)
    d.text((g, 72), sub, font=fs, fill=GREY)
    for i, (path, letter, name, note) in enumerate(panels):
        r, c = divmod(i, cols)
        x = g + c * (pw + g)
        y = top + r * (ph + cap)
        p = Image.open(path).convert("RGB").resize((pw, ph), Image.LANCZOS)
        im.paste(p, (x, y))
        d.text((x, y + ph + 12), letter, font=fl, fill=ACCENT)
        d.text((x + 34, y + ph + 12), name, font=fl, fill=INK)
        d.text((x + 34, y + ph + 42), note, font=fn, fill=GREY)
    im.save(out, quality=90)
    print(out, im.size)


if __name__ == "__main__":
    BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "dome")
    D = os.path.join(BASE, "schemes") + os.sep          # the graded renders
    C = os.path.join(BASE, "wainscot_compare") + os.sep  # the sheets this writes
    which = sys.argv[1]
    if which == "A":
        sheet([
            (D + "W1_lime.jpg", "A", "Without: limewash down to the floor", "Brightest; the floor is the only wood, but walls scuff at hand height"),
            (D + "W2_wainscot_painted.jpg", "B", "Natural pine wainscot", "Warm band at hand height; reads well over a darker floor"),
            (D + "W2b_wainscot_limed.jpg", "C", "Limewashed pine wainscot", "Wood texture, pale tone; quietest with any floor"),
            (D + "W2c_wainscot_painted_sage.jpg", "D", "Painted boards (sage green)", "Most contrast with a wood floor; a colour you can change later"),
        ], 2, "With and without the 3'-3\" wainscot",
            "Same view and same mid-brown wood floor in all four; only the lower walls change.",
            C + "C1_wainscot_compare.jpg")
    else:
        sheet([
            (D + "W1b_lime_pinefloor.jpg", "E", "Pine-tone floor, no wainscot", "The floor stands alone as the one warm surface"),
            (D + "W2d_wainscot_pinefloor.jpg", "F", "Pine-tone floor + natural pine wainscot", "Floor and walls merge into one wood colour: the 'too much' case"),
        ], 2, "If the floor is the same tone as the pine",
            "Same view as above with a honey-pine floor instead of mid-brown.",
            C + "C2_same_tone_floor.jpg")
