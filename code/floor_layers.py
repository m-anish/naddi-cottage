"""Washroom floor make-up: stepped oblique cutaway, layer by layer (W-06).

Revised Oct 2026: no rubble sub-base. The loads are trivial and the HDPE already
on the ground breaks capillary rise, so sand goes straight onto compacted subgrade.
The DPM is the existing HDPE BELOW the sand; a second polythene above the XPS is a
slip layer that keeps wet concrete out of the board joints.
"""
import math, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch

plt.rcParams.update({"font.family": "Inter", "font.size": 8})
INK, GREY, ACCENT, WATER, TEAL = "#1d1d1b", "#8a8780", "#b5552b", "#3d7ea6", "#3c8582"
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "07_floor_layers.png")

DX, DY = 0.5 * math.cos(math.radians(30)), 0.5 * math.sin(math.radians(30))
ZS = 3.0
DEPTH = 700


def P(x, y, z):
    return (x + y * DX, z * ZS + y * DY)


fig = plt.figure(figsize=(11, 8.5), dpi=200)
fig.text(0.035, 0.955, "Washroom floor — make-up, layer by layer", fontsize=15, fontweight="semibold", color=INK, va="top")
fig.text(0.035, 0.915, "Sand on compacted subgrade — no rubble fill · insulated slab inside a stone plinth wall · about 8½ in all told",
         fontsize=9, color=GREY, va="top")
fig.text(0.965, 0.955, "W-06", fontsize=15, fontweight="semibold", color=ACCENT, va="top", ha="right")
fig.text(0.965, 0.915, "Naddi cottage · washroom", fontsize=8, color=GREY, va="top", ha="right")
fig.add_artist(plt.Line2D([0.035, 0.965], [0.895, 0.895], color=INK, lw=0.8, transform=fig.transFigure))
fig.text(0.035, 0.03, "Illustrative, not to scale: thicknesses drawn 3× and the two thin sheets thicker still, so every layer shows.",
         fontsize=7, color=GREY)

ax = fig.add_axes([0.02, 0.05, 0.96, 0.84])
ax.set_xlim(-800, 2390)
ax.set_ylim(-560, 1260)
ax.set_aspect("equal")
ax.axis("off")

# key, z0, z1 (real mm; 0 = top of compacted subgrade), right end x, start x, colour, hatch
LAYERS = [
    ("sub", -120, 0, 1600, 0, "#b4ad9f", "////"),
    ("hdpe", 0, 8, 1490, 0, "#2f7f5f", None),
    ("sand", 8, 58, 1400, 0, "#ecdfc2", "...."),
    ("xps", 58, 108, 1180, 30, "#f2b8a8", None),
    ("dpm", 108, 116, 1070, 0, "#4f8fc0", None),
    ("slab", 116, 216, 990, 30, "#c9c7c1", None),
    ("wp", 216, 222, 900, 0, "#5aa3a0", None),
    ("bed", 222, 229, 790, 0, "#e3e0d9", None),
    ("tile", 229, 243, 660, 0, "#6d6f70", None),
]
K = {l[0]: l for l in LAYERS}
random.seed(4)


def face(pts, fc, ec=INK, lw=0.7, hatch=None, z=2):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, zorder=z))


def shade(c, f):
    c = c.lstrip("#")
    return "#%02x%02x%02x" % tuple(min(255, int(int(c[i:i + 2], 16) * f)) for i in (0, 2, 4))


for i, (key, z0, z1, x1, x0, col, hatch) in enumerate(LAYERS):
    if key == "xps":
        x0 = 30
    face([P(x0, 0, z0), P(x1, 0, z0), P(x1, 0, z1), P(x0, 0, z1)], col, hatch=hatch, z=3 + i)
    face([P(x0, 0, z1), P(x1, 0, z1), P(x1, DEPTH, z1), P(x0, DEPTH, z1)], shade(col, 1.07) if key != "tile" else "#7d7f80",
         hatch=hatch, z=3 + i)
    face([P(x1, 0, z0), P(x1, DEPTH, z0), P(x1, DEPTH, z1), P(x1, 0, z1)], shade(col, 0.82), hatch=hatch, z=3 + i)

# compacted subgrade: speckled earth, a few stones, no rubble raft
for _ in range(40):
    cx, cz = random.uniform(30, 1580), random.uniform(-108, -12)
    r = random.uniform(7, 15)
    pts = []
    for k in range(6):
        a = 2 * math.pi * k / 6 + random.uniform(-0.3, 0.3)
        rr = r * random.uniform(0.6, 1.0)
        pts.append(P(cx + rr * math.cos(a), 0, cz + rr * math.sin(a) / ZS * 0.9))
    face(pts, random.choice(["#9d968b", "#8c867c", "#a8a296"]), ec="#6d685f", lw=0.3, z=4)
for _ in range(220):
    ax.plot(*P(random.uniform(30, 1590), 0, random.uniform(-112, -8)), marker=".", ms=1.1,
            color="#6f6a61", zorder=5)
xs = list(range(-330, 1700, 30))
gl = [P(x, 0, -128 - 6 * math.sin(x / 60)) for x in xs]
ax.plot([p[0] for p in gl], [p[1] for p in gl], color=INK, lw=0.6, zorder=20)
ax.text(*P(1500, 0, -150), "firm ground below", fontsize=7, color=GREY, va="top", ha="right")

# slab aggregate + mesh
for _ in range(150):
    x, z = random.uniform(45, 980), random.uniform(122, 212)
    ax.plot(*P(x, 0, z), marker=(3, 0, random.uniform(0, 120)), ms=1.5, color="#8f8c86", zorder=9)
for x in range(70, 975, 65):
    ax.add_patch(plt.Circle(P(x, 0, 162), 5, fc="#5d5a55", ec="none", zorder=10))
ax.plot([P(50, 0, 162)[0], P(975, 0, 162)[0]], [P(50, 0, 162)[1]] * 2, color="#5d5a55", lw=0.8, zorder=10)
for x in range(915, 990, 35):
    ax.plot(*zip(P(x, 30, 216), P(x, DEPTH - 30, 216)), color="#8a877f", lw=0.5, zorder=11)
# tile joints
for x in range(180, 660, 150):
    ax.plot(*zip(P(x, 0, 243), P(x, DEPTH, 243)), color="#4a4c4d", lw=0.6, zorder=13)
for y in (175, 350, 525):
    ax.plot(*zip(P(30, y, 243), P(660, y, 243)), color="#4a4c4d", lw=0.6, zorder=13)
# XPS board joint on its step
ax.plot(*zip(P(1085, 0, 108), P(1085, DEPTH, 108)), color="#c98b7a", lw=0.8, zorder=8)
ax.plot(*zip(P(990, 330, 108), P(1180, 330, 108)), color="#c98b7a", lw=0.8, zorder=8)

# plinth wall (left), cut
WX0 = -280
face([P(WX0, 0, -128), P(0, 0, -128), P(0, 0, 300), P(WX0, 0, 300)], "#aaa49b", z=2)
face([P(WX0, 0, 300), P(0, 0, 300), P(0, DEPTH, 300), P(WX0, DEPTH, 300)], "#c2bdb4", z=2)
random.seed(11)
for zc in range(-100, 300, 52):
    xc = WX0 + random.uniform(-40, 0)
    while xc < -10:
        w = random.uniform(70, 120)
        x0, x1 = max(WX0 + 5, xc + 5), min(-6, xc + w - 5)
        h = random.uniform(16, 21)
        if x1 - x0 > 25:
            pts = [P(x0 + random.uniform(0, 8), 0, zc - h), P(x1 - random.uniform(0, 8), 0, zc - h + random.uniform(-3, 3)),
                   P(x1, 0, zc + h), P(x0, 0, zc + h + random.uniform(-3, 3))]
            face(pts, random.choice(["#968f84", "#a29b90", "#8b857b", "#9c9589"]), ec="#5d5a55", lw=0.4, z=3)
        xc += w
ax.plot(*zip(P(-1, 0, 0), P(-1, 0, 116)), color="#2f7f5f", lw=2.2, zorder=12)          # polythene up the wall
face([P(3, 0, 58), P(30, 0, 58), P(30, 0, 216), P(3, 0, 216)], "#f2b8a8", z=7.5)          # XPS edge strip
face([P(-7, 0, 216), P(-1, 0, 216), P(-1, 0, 300), P(-7, 0, 300)], "#5aa3a0", z=12)     # waterproofing upturn

# fall arrow on the tiles
a0, a1 = P(600, 470, 243), P(110, 470, 243)
ax.add_patch(FancyArrowPatch(a0, a1, arrowstyle="-|>", mutation_scale=10, color="#9fd0f0", lw=1.4, zorder=30))
ax.text(a1[0] + 20, a1[1] - 18, "falls to the drain", fontsize=6.8, color="#e4f3fd", va="top", zorder=30)


def topstrip(key, frac=0.5):
    i = [l[0] for l in LAYERS].index(key)
    x1 = K[key][3]
    xprev = LAYERS[i + 1][3] if i + 1 < len(LAYERS) else 30
    return P(xprev + (x1 - xprev) * 0.55, DEPTH * frac, K[key][2])


TX = 1935


def lab(xy, title, sub, ty, color=INK, title_color=None):
    ax.annotate("", xy=xy, xytext=(TX - 25, ty + 16), arrowprops=dict(arrowstyle="-", lw=0.5, color=color, shrinkA=0, shrinkB=0),
                zorder=40)
    ax.text(TX, ty + 4, title, fontsize=8.4, fontweight="semibold", color=title_color or color, va="bottom", zorder=40)
    ax.text(TX, ty - 6, sub, fontsize=7.1, color=GREY if color == INK else color, va="top", zorder=40, linespacing=1.3)


lab(topstrip("tile", 0.6), "9  Finish", "anti-skid tile or slate\nin C2 adhesive · 15–25 mm", 1140)
lab(topstrip("wp", 0.55), "8  Waterproofing", "2-coat polymer cement;\nup 300 mm on the walls", 1007, color=TEAL)
lab(topstrip("slab", 0.5), "7  Concrete slab", "100 mm M20, mesh on\nspacers, laid to falls", 874)
lab(topstrip("dpm", 0.5), "6  Polythene slip layer", "200 µm over the boards: keeps\nwet concrete out of the joints", 741, color=WATER)
lab(topstrip("xps", 0.5), "5  XPS insulation  ← here", "50 mm boards, butt-jointed\ntight, joints taped", 608, color=ACCENT)
lab(topstrip("sand", 0.5), "4  Sharp sand", "50 mm, screeded dead level —\nnot fine river sand", 475)
lab(topstrip("hdpe", 0.5), "3  HDPE + geofabric", "already on the ground;\nthis is the damp-proof layer", 342, color="#2f7f5f")
lab(P(1450, 0, -60), "2  Compacted subgrade", "no rubble raft needed. Ram it\nhard first; if it is recent fill\nover 150 mm deep, put stone\nback and compact in layers", 185)

# left callouts
LXL = -780


def llab(xy, txt, ty, color):
    ax.annotate(txt, xy=xy, xytext=(LXL, ty), fontsize=7.2, color=color, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=color, shrinkA=0, shrinkB=0, relpos=(1, 0.5)), zorder=40)


llab(P(-4, 0, 270), "waterproofing turned\nup the wall", 830, TEAL)
llab(P(16, 0, 140), "5  25 mm XPS strip on edge\n    round the slab: it never\n    touches the cold stone", 640, ACCENT)
llab(P(-1, 0, 60), "3  HDPE lapped and turned\n    up the inner face", 420, "#2f7f5f")
llab(P(-150, 0, -40), "1  Stone plinth wall,\n    pointed in cement,\n    down to firm ground;\n    anti-termite treatment", 120, INK)

# finished floor level and the height the layers take
ax.plot(*zip(P(WX0 + 10, 0, 243), P(-12, 0, 243)), color="white", lw=1.0, ls=(0, (4, 2)), zorder=13)
llab(P(-150, 0, 243), "finished floor level =\nmain-room threshold", 1010, GREY)
hx = P(1600, 0, 0)[0] + 60
ax.text(*P(250, 0, -175), "Layers 3–9 add about 219 mm (8\u00bd in) above the compacted subgrade — a little over half the old make-up.",
        fontsize=7.4, color=INK, va="top", zorder=40)
fig.savefig(OUT, dpi=200, facecolor="white")
print("ok")
