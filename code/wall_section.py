"""Wall build-up drawing for the main dome walls (section at base + plan detail at a steel strut)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Ellipse
import numpy as np

plt.rcParams.update({"font.family": "Inter", "font.size": 8})
INK = "#1d1d1b"
GREY = "#8a8780"
ACCENT = "#b5552b"
WATER = "#3d7ea6"
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "06_wall_buildup.png")

C_PLANK = "#b07a52"
C_STEEL_Y = "#e2b93b"
C_STEEL_B = "#7a3b2a"
C_EPS = "#f4f4f1"
C_XPS = "#9fc4d9"
C_BATTEN = "#d9b58a"
C_BOARD = "#c9c6bf"
C_PINE = "#dcae74"
C_PLINTH = "#a9a39a"


def label(ax, xy, txt, xytext, color=INK, fs=7.4, ha="left", edge=False):
    rel = (0.5, 0.5)
    if edge:
        rel = (0.0, 0.5) if xytext[0] > xy[0] else (1.0, 0.5)
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=fs, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.45, color=color, shrinkA=0, shrinkB=1, relpos=rel),
                bbox=dict(facecolor="white", edgecolor="none", pad=0.4, alpha=0.95))


fig = plt.figure(figsize=(11, 8.5), dpi=200)
fig.text(0.035, 0.955, "Main dome wall — build-up", fontsize=15, fontweight="semibold", color=INK, va="top")
fig.text(0.035, 0.915, "Drained gap behind the planks · foam over the purlins · battens · 8 mm board everywhere · pine over it below the datum",
         fontsize=9, color=GREY, va="top")
fig.text(0.965, 0.955, "D-01", fontsize=15, fontweight="semibold", color=ACCENT, va="top", ha="right")
fig.text(0.965, 0.915, "Naddi cottage · main dome", fontsize=8, color=GREY, va="top", ha="right")
fig.add_artist(plt.Line2D([0.035, 0.965], [0.895, 0.895], color=INK, lw=0.8, transform=fig.transFigure))
fig.text(0.035, 0.03, "Schematic, not to scale between panels; thicknesses in mm. Dimensions from site: 2×4\" struts, 1×2\" purlins, 50 mm EPS.   "
         "Nothing solvent-based near the EPS \u2014 aerosol and solvent paints dissolve polystyrene on contact.",
         fontsize=7, color=GREY)

# ------------------------------------------------------------ section at the base (mm, horizontal x2.5)
ax = fig.add_axes([0.03, 0.06, 0.55, 0.81])
ax.set_xlim(-780, 1100)
ax.set_ylim(-700, 1330)
ax.axis("off")
SX = 2.5
PL = 10; GAP = 50; MEM = 2; EPS = 50; BAT = 25; BRD = 8; GRD = 15; PIN = 12
X = lambda mm: mm * SX
x_pl0, x_pl1 = 0, PL
x_gap1 = x_pl1 + GAP
x_mem1 = x_gap1 + MEM
x_eps1 = x_mem1 + EPS
x_bat1 = x_eps1 + BAT
x_brd1 = x_bat1 + BRD
x_gr1 = x_brd1 + GRD
x_pn1 = x_gr1 + PIN
z1 = 1200
datum = 990
RIGHT = 250
def R(x0, z0, w, h, **kw):
    ax.add_patch(Rectangle((X(x0), z0), X(w), h, **kw))
# ---- floor: wood on underlay, 20 mm fibre-cement base board, metal frame, sealed void
R(x_brd1 + 6, 0, RIGHT - x_brd1 - 6, 5, fc="#9fc4d9", ec=INK, lw=0.4)                 # underlay
R(x_brd1 + 6, 5, RIGHT - x_brd1 - 6, 15, fc="#a8744a", ec=INK, lw=0.6)               # wood floor
R(x_mem1 - 2, -20, RIGHT - x_mem1 + 2, 20, fc="#d8d3ca", ec=INK, lw=0.8)              # base board
R(x_mem1 + 2, -120, 48, 100, fc="#8d8b86", ec=INK, lw=0.8)                           # perimeter frame member
R(x_mem1 + 6, -116, 40, 92, fc="white", ec=INK, lw=0.4)
R(x_mem1 + 50, -100, RIGHT - x_mem1 - 50, 80, fc="none", ec=GREY, lw=0.5, ls="--")    # joist beyond
# tin skirting + 25 mm foam inside, behind the lowest plank
ax.plot([X(x_pl0 + 2)] * 2, [-150, -690], color="#4a4844", lw=2.2)
R(x_pl0 + 4, -690, 25, 540, fc=C_EPS, ec=INK, lw=0.6, hatch="...")
ax.text(X(RIGHT) - 10, -470, "sealed floor void", fontsize=6.8, color=GREY, ha="right")
ax.plot([X(-120), X(x_pl0 + 2)], [-690, -690], color=INK, lw=0.6)
# planks (shiplap), lowest one lapping over the tin
for zz in range(-120, 1200, 160):
    ax.add_patch(Polygon([(X(x_pl0 - 3), zz), (X(x_pl1), zz + 4), (X(x_pl1), zz + 170), (X(x_pl0 - 3), zz + 166)], closed=True,
                         fc=C_PLANK, ec=INK, lw=0.6))
# purlin beyond
R(x_pl1 + 2, -88, GAP - 4, 1288, fc=C_STEEL_B, ec=INK, lw=0.5, ls="--", alpha=0.22)
for zz in (1080, 520):
    ax.add_patch(FancyArrowPatch((X(x_pl1 + GAP / 2), zz), (X(x_pl1 + GAP / 2), zz - 170), arrowstyle="-|>", mutation_scale=8, color=WATER, lw=0.9))
# membrane
ax.plot([X(x_gap1) + 1.5] * 2, [-110, z1], color=WATER, lw=1.8, ls=(0, (5, 2)))
# sloped flashing closing the foot of the gap from the floor void, weeping out over the tin
ax.add_patch(Polygon([(X(x_gap1 + 2), -92), (X(x_gap1 + 2), -104), (X(x_pl0 - 14), -160), (X(x_pl0 - 14), -148)], closed=True,
                     fc="#7d7a74", ec=INK, lw=0.6))
ax.plot([X(x_pl1), X(x_gap1)], [-84, -84], color=INK, lw=1.4, ls=(0, (1, 1)))
ax.add_patch(FancyArrowPatch((X(x_pl1 + GAP / 2), -40), (X(x_pl0 - 45), -230), arrowstyle="-|>", mutation_scale=8, color=WATER, lw=0.9,
                             connectionstyle="arc3,rad=-0.3"))
# EPS, battens, board, timber strips, pine
R(x_mem1, -20 + 20, EPS, z1, fc=C_EPS, ec=INK, lw=0.8, hatch="...")
BZ = (110, 510, 910)
for zz in BZ:
    R(x_eps1, zz, BAT, 50, fc=C_BATTEN, ec=INK, lw=0.6, hatch="////")
R(x_bat1, 12, BRD, z1 - 12, fc=C_BOARD, ec=INK, lw=0.8)                               # 8 mm board, full height
ax.plot([X(x_brd1) + 2] * 2, [datum + 40, z1], color="#e8e0d2", lw=2.5)               # limewash above the datum
for zz in BZ:
    R(x_brd1, zz, GRD, 50, fc=C_BATTEN, ec=INK, lw=0.6)                               # timber strips (grounds)
    ax.plot([X(x_brd1 - 30), X(x_gr1 - 2)], [zz + 25, zz + 25], color=INK, lw=0.8)    # screw through board into batten
R(x_gr1, 25, PIN, datum - 25, fc=C_PINE, ec=INK, lw=0.8)                              # vertical pine boards
R(x_brd1, datum, x_pn1 - x_brd1 + 30, 40, fc=C_BATTEN, ec=INK, lw=0.8)                # datum ledge
R(x_pn1, 20, 18, 80, fc=C_BATTEN, ec=INK, lw=0.8)                                     # skirting on the finished floor
R(x_mem1, 0, EPS, 8, fc="#f0d080", ec=INK, lw=0.5)
# wiring: conduit in the batten void, metal box through the board and pine
cz = 800
R(x_eps1 + 3, 690, 19, cz - 690, fc="#e9e6df", ec=INK, lw=0.5, zorder=3)
ax.add_patch(Ellipse((X(x_eps1 + 12.5), cz), X(20), 20, fc="#e9e6df", ec=INK, lw=0.6, zorder=3))
ax.add_patch(Ellipse((X(x_eps1 + 12.5), cz), X(7), 7, fc=ACCENT, ec="none", zorder=4))
R(x_pn1 - 50, 610, 50, 80, fc="#b9bcc0", ec=INK, lw=0.7, zorder=3)                    # metal box
R(x_pn1 - 46, 614, 42, 72, fc="#e3e4e6", ec=INK, lw=0.4, zorder=3)
R(x_pn1, 595, 4, 110, fc="white", ec=INK, lw=0.6, zorder=3)                           # plate
# labels
LX, RX = -770, X(x_pn1) + 100
label(ax, (X(x_pl0 + 3), 1110), "1  Fibre-cement planks (existing),\n    painted brown outside", (LX, 1250), edge=True)
label(ax, (X(x_pl1 + GAP / 2), 960), "2  50 mm drainage and drying gap\n    (the 1×2\" purlin depth); keep it open", (LX, 1000), color=WATER, edge=True)
label(ax, (X(x_pl1 + 8), 690), "vertical 1×2\" steel purlin beyond;\nthe planks are screwed to it", (LX, 720), edge=True)
label(ax, (X(x_mem1 + 25), 400), "4  50 mm FR-grade EPS on the purlins'\n    inner face, flush with the 2×4 struts.\n    Tape the butt joints: that alone stops\n    air washing through, and is the cheap\n    alternative to the membrane above", (LX, 520), edge=True)
label(ax, (X(x_gap1 - 15), -104), "close the foot of the gap from the floor\nvoid: insect mesh + a flashing sloping\nout, so water weeps over the tin", (LX, 150), color=WATER, edge=True)
label(ax, (X(x_pl0 + 2), -400), "painted tin skirting with 25 mm\nfoam inside (existing)", (LX, -330), edge=True)
label(ax, (X(-60), -690), "ground: HDPE + weed-control\nfabric under the tin (existing)", (LX, -560), edge=True)
label(ax, (X(x_gap1) + 2, 1185), "3  Breather membrane (optional):\n    vapour-OPEN only \u2014 polythene or\n    felt here traps damp, and the room\n    side has no barrier to dry through", (RX + 42, 1255), color=WATER, edge=True)
label(ax, (X(x_brd1) + 2, 1120), "6  8 mm fibre-cement board, full height;\n    limewash above the datum", (RX, 1145), edge=True)
label(ax, (X(x_pn1 + 12), 1010), "9  Datum ledge at 3'-3\" (sill height)", (RX, 1025), edge=True)
label(ax, (X(x_eps1 + 12.5), cz + 4), "wiring in conduit in the batten void,\nnever touching the EPS", (RX, 910), color=ACCENT, edge=True)
label(ax, (X(x_pn1 - 20), 650), "metal box fixed to a timber block;\n57 mm from pine face to foam", (RX, 795), color=ACCENT, edge=True)
label(ax, (X(x_eps1 + 12), 535), "5  25 mm treated battens @ 400 mm,\n    horizontal, screwed through the EPS", (RX, 680), edge=True)
label(ax, (X(x_brd1 + 8), 470), "7  15 mm timber strips over the board,\n    screwed through it into the battens", (RX, 565), edge=True)
label(ax, (X(x_gr1 + 6), 330), "8  Vertical pine boards, backs oiled,\n    secret-nailed to the strips", (RX, 450), edge=True)
label(ax, (X(x_mem1 + 30), 4), "foam seal under the EPS", (RX, 345), edge=True)
label(ax, (X(x_pn1 + 9), 60), "skirting, fitted last", (RX, 250), edge=True)
FX = X(RIGHT) + 30
label(ax, (X(RIGHT) - 12, 13), "wood floor on an underlay", (FX, 80), edge=True)
label(ax, (X(RIGHT) - 12, -10), "20 mm fibre-cement base\nboard (existing)", (FX, -25), edge=True)
label(ax, (X(RIGHT) - 12, -60), "metal floor frame (existing)", (FX, -130), edge=True)
ax.text(X(x_pl0) - 15, 1305, "OUTSIDE", fontsize=7.5, color=GREY, ha="right", fontweight="semibold")
ax.text(X(x_pn1) + 15, 1305, "INSIDE", fontsize=7.5, color=GREY, fontweight="semibold")
ax.annotate("", xy=(X(x_pl1), 1238), xytext=(X(x_eps1), 1238), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
for xx in (x_pl1, x_eps1):
    ax.plot([X(xx)] * 2, [1205, 1252], color=INK, lw=0.4)
ax.text(X(x_pl1) + 10, 1262, "100 mm = 2×4\" strut", fontsize=6.6, color=INK, va="bottom")
ax.text(X(90), -690, "Section at the base of a wall\nthicknesses drawn 2.5×; shown upright\n(the dome's walls lean about 11°)", fontsize=7.2, color=INK, fontweight="semibold", va="bottom")

# ------------------------------------------------------------ plan at a batten
bx = fig.add_axes([0.60, 0.38, 0.38, 0.50])
bx.set_aspect("equal")
bx.set_xlim(-330, 330)
bx.set_ylim(-150, 330)
bx.axis("off")
bx.add_patch(Rectangle((-320, 0), 640, PL, fc=C_PLANK, ec=INK, lw=0.7))
for px in (-190, 110):
    bx.add_patch(Rectangle((px - 20, PL), 40, GAP, fc=C_STEEL_B, ec=INK, lw=0.7))
bx.plot([-320, 320], [PL + GAP + 1, PL + GAP + 1], color=WATER, lw=1.6, ls=(0, (5, 2)))
y_m = PL + GAP + MEM
sx0, sx1 = 225, 275
y_face = y_m + EPS
bx.add_patch(Rectangle((-320, y_m), sx0 - 4 + 320, EPS, fc=C_EPS, ec=INK, lw=0.7, hatch="..."))
bx.add_patch(Rectangle((sx1 + 4, y_m), 320 - sx1 - 4, EPS, fc=C_EPS, ec=INK, lw=0.7, hatch="..."))
bx.add_patch(Rectangle((sx0, PL), sx1 - sx0, y_face - 6 - PL, fc=C_STEEL_Y, ec=INK, lw=0.9))
bx.add_patch(Rectangle((sx0 + 4, PL + 4), sx1 - sx0 - 8, y_face - 6 - PL - 8, fc="white", ec=INK, lw=0.5))
bx.add_patch(Rectangle((sx0 - 4, y_face - 6), sx1 - sx0 + 8, 6, fc=C_XPS, ec=INK, lw=0.6))
bx.add_patch(Rectangle((-320, y_face), 640, BAT, fc=C_BATTEN, ec=INK, lw=0.7, hatch="////"))
bx.add_patch(Rectangle((-320, y_face + BAT), 640, BRD, fc=C_BOARD, ec=INK, lw=0.7))
for px in (-190, 110):
    bx.plot([px, px], [y_face + BAT + BRD, PL + 12], color=INK, lw=0.9)
    bx.plot([px - 6, px + 6], [y_face + BAT + BRD, y_face + BAT + BRD], color=INK, lw=1.2)
bx.text(-325, -20, "OUTSIDE", fontsize=7, color=GREY, fontweight="semibold")
bx.text(-325, 318, "INSIDE", fontsize=7, color=GREY, fontweight="semibold")
label(bx, (-190, PL + 25), "existing 1×2\" vertical purlin;\nthe planks are screwed to it", (-325, -70), fs=7.0)
label(bx, (-40, PL + GAP / 2), "purlin depth = drainage gap", (20, -85), fs=7.0, color=WATER)
label(bx, (-60, y_m + 25), "EPS runs continuously over the\npurlins: the foam is the thermal break", (-325, 200), fs=7.0)
label(bx, (-10, y_face + 12), "batten runs across the purlins;\nlong screws through the EPS into each one", (-325, 270), fs=7.0)
label(bx, (250, y_face - 3), "2×4\" strut, flush with\nthe foam: thin foam\ntape on its face", (40, 215), fs=7.0, color=ACCENT)
label(bx, (300, y_face + BAT + 4), "8 mm board", (238, 300), fs=7.0)
label(bx, (300, PL + GAP + 1), "membrane", (250, -40), fs=7.0, color=WATER)
bx.text(-325, -148, "Plan at a batten · battens run horizontally across the vertical purlins", fontsize=7.6, color=INK, fontweight="semibold")

# ------------------------------------------------------------ notes
nx = fig.add_axes([0.60, 0.05, 0.38, 0.37])
nx.axis("off")
nx.set_xlim(0, 10)
nx.set_ylim(0, 10)
notes = [
    ("Why the gap matters", True),
    ("Your planks get damp on the inside in heavy rain and dry", False),
    ("because the inside is open. Foam pressed against them", False),
    ("traps that water: the gap and membrane keep it moving out.", False),
    ("", False),
    ("Why the thermal break", True),
    ("Timber battens already slow the cold through the steel.", False),
    ("Add thin foam tape on the 2×4 strut faces only; the foam", False),
    ("itself covers the purlins. Avoid metal battens.", False),
    ("", False),
    ("Why board everywhere", True),
    ("The board runs full height, so the EPS is sealed behind", False),
    ("non-combustible board even behind the pine. Use 12 mm", False),
    ("board near a bukhari. Mesh the gap's openings against rats.", False),
    ("", False),
    ("Wiring", True),
    ("All cables in conduit: PVC cable touching polystyrene goes", False),
    ("brittle. Metal boxes in the wainscot band. Earth the steel", False),
    ("frame and fit a 30 mA RCCB.", False),
]
for i, (t, b) in enumerate(notes):
    nx.text(0, 9.75 - i * 0.5, t, fontsize=7.6 if b else 7.2, fontweight="semibold" if b else "normal",
            color=ACCENT if b else INK)
fig.savefig(OUT, dpi=200, facecolor="white")
print("ok")
