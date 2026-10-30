"""A-06  Washroom: headroom on the measured frame, and what it does to Layout A.

The extension is a hipped wedge, so clear height falls away steeply to the sides.
Heights are read where the PERSON'S HEAD is, not at the counter: 1.1 ft inboard of
the ledge face for someone standing at the basin, 0.7 ft for someone seated on the WC.
Plotted from the Onshape frame (see docs/onshape_frame_check.md), not from estimates.

usage: python3 washroom_headroom.py [out.png]
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Rectangle

INK, GREY, ACCENT, WATER = "#1d1d1b", "#8a8780", "#b5552b", "#3d7ea6"
for f in ("Inter", "Inter Display"):
    if any(f == n for n in {fn.name for fn in matplotlib.font_manager.fontManager.ttflist}):
        plt.rcParams["font.family"] = f
        break
plt.rcParams["font.size"] = 8

# ----------------------------------------------------------------- geometry
# Everything comes from geom.py so the drawing cannot drift from the model.
# geom.headroom() limits by BOTH the side slope and the front wall, which leans
# in over the floor: near the dome face the ceiling is the wall coming at you.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import (FW, BW, D, LEDGE_H, half_floor, headroom, walkable_area,
                  fmt_ftin, A, C, T15)

LEDGE_A = 1.90      # Layout A as drawn: ledge face this far in from the floor edge
LEDGE_B = 2.25      # revised: 4 in further in
STAND, SEAT = 1.10, 0.70    # how far inboard of the ledge face a head sits


def head(x, y):
    return headroom(abs(x), y)


def half_at(h, y):
    """half-width where the clear height is h; 0 if nowhere at this depth"""
    if headroom(0.0, y) < h:
        return 0.0
    lo, hi = 0.0, half_floor(y)
    for _ in range(40):
        mid = (lo + hi) / 2
        if headroom(mid, y) >= h:
            lo = mid
        else:
            hi = mid
    return lo


def band(h):
    ys = np.linspace(0.0, D, 90)
    right = [(min(half_at(h, y), half_floor(y)), y) for y in ys]
    return [(-x, y) for x, y in reversed(right)] + right


ftin = fmt_ftin


def mark(ax, x, y, label, need):
    h = head(x, y)
    ok = h >= need
    c = WATER if ok else ACCENT
    ax.plot(x, y, "o", ms=7, mfc="white", mec=c, mew=1.7, zorder=11)
    ax.text(x, y + 0.30, label, ha="center", color=INK, fontsize=7.2,
            fontweight="bold", zorder=11)
    txt = ftin(h) if ok else f"{ftin(h)}  needs {ftin(need)}"
    ax.text(x, y - 0.50, txt, ha="center", color=c, fontsize=6.9,
            fontweight="normal" if ok else "bold", zorder=11)


def draw_plan(ax, ledge_dx):
    ax.set_aspect("equal")
    ax.axis("off")
    for h, c in ((4.4, "#f4f1ec"), (6.0, "#e4e0d6"), (6.5, "#cfcabc"), (7.0, "#b8b2a2")):
        ax.add_patch(MplPoly(band(h), closed=True, fc=c, ec="none", zorder=1))
    for s in (-1, 1):
        xs = [s * (half_floor(0) - ledge_dx), s * half_floor(0),
              s * half_floor(D), s * (half_floor(D) - ledge_dx)]
        ax.add_patch(MplPoly(list(zip(xs, [0, 0, D, D])), closed=True,
                             fc="#efe7dc", ec=GREY, lw=0.9, zorder=5))
    ax.add_patch(MplPoly([(-FW / 2, 0.0), (FW / 2, 0.0), (BW / 2, D), (-BW / 2, D)],
                         closed=True, fc="none", ec=INK, lw=1.6, zorder=6))
    for h, y in ((7.0, 2.6), (6.5, 3.2), (6.0, 3.8), (4.4, 4.9)):
        x = min(max(half_at(h, y), 0), half_floor(y))
        ax.text(x + 0.14, y, f"{h:g}'", color=GREY, fontsize=6.4, va="center", zorder=7)
    ax.plot([-FW / 2, FW / 2], [0, 0], color=INK, lw=2.4, zorder=7)
    ax.add_patch(Rectangle((-1.25, -0.18), 2.5, 0.18, fc="white", ec=INK, lw=1.0, zorder=8))
    ax.text(0, -0.55, "door", ha="center", color=INK, fontsize=7, zorder=8)

    lx = lambda y: half_floor(y) - ledge_dx
    mark(ax, -(lx(2.2) - SEAT), 2.2, "WC, seated", 4.4)
    mark(ax, (lx(2.3) - STAND), 2.3, "vanity, standing", 6.4)
    mark(ax, 0.0, 5.2, "shower", 6.6)
    ax.plot([-1.25, 1.25], [5.2, 5.2], color=WATER, lw=0.9, zorder=9)
    ax.text(1.42, 5.2, f"{ftin(head(1.25, 5.2))} at 1'-3\" off centre",
            color=WATER, fontsize=6.3, va="center", zorder=9)
    ax.annotate("", xy=(FW / 2 + 0.8, 0), xytext=(FW / 2 + 0.8, D),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8))
    ax.text(FW / 2 + 1.05, D / 2, f"{D:.2f} ft deep", color=GREY, fontsize=7,
            rotation=90, va="center")
    ax.set_xlim(-FW / 2 - 0.9, FW / 2 + 2.3)
    ax.set_ylim(-1.15, D + 0.9)


def main(out):
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.0))
    fig.patch.set_facecolor("white")
    draw_plan(axes[0], LEDGE_A)
    draw_plan(axes[1], LEDGE_B)
    axes[0].set_title("A   Layout A as drawn — ledge face 1'-11\" in from the floor edge",
                      color=INK, fontsize=9, fontweight="bold", loc="left", pad=8)
    axes[1].set_title("B   Vanity ledge pulled in 4 inches, to 2'-3\"",
                      color=INK, fontsize=9, fontweight="bold", loc="left", pad=8)
    fig.text(0.032, 0.95, "Washroom: where you can actually stand", color=INK,
             fontsize=14, fontweight="bold")
    fig.text(0.032, 0.915,
             "Shaded by clear height over the floor, read at head height. The extension is a "
             "hipped wedge AND the dome face leans in over the floor, so the usable band is "
             "narrow.", color=GREY, fontsize=8.2)
    vA = head(half_floor(2.3) - LEDGE_A - STAND, 2.3)
    vB = head(half_floor(2.3) - LEDGE_B - STAND, 2.3)
    fig.text(0.032, 0.045,
             f"A  Layout A very nearly works on the real frame. The WC is fine seated and the shower "
             f"has {ftin(head(0, 5.2))} on the centre line. The one failure is the vanity: "
             f"{ftin(vA)} standing at the basin.\n"
             f"B  Pulling that ledge face in four inches gives {ftin(vB)}. Only "
             f"{walkable_area(6.0):.0f} of the {(FW + BW) / 2 * D:.0f} sq ft floor has 6 ft over it "
             f"\u2014 the front strip is lost to the dome face leaning in over it, not the side slopes.",
             color=INK, fontsize=7.8, linespacing=1.6)
    fig.text(0.967, 0.95, "A-06", color=INK, fontsize=11, fontweight="bold", ha="right")
    fig.subplots_adjust(left=0.025, right=0.975, top=0.875, bottom=0.17, wspace=0.04)
    fig.savefig(out, dpi=170, facecolor="white")
    print("ok", out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else
         os.path.join(here, "out", "A-06_washroom_headroom.png"))
