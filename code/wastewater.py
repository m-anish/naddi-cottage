"""Wastewater sheets: S-01 system (toilet -> biodigester -> test chamber -> reed bed -> soakaway), S-02 reed bed detail."""
import math, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Circle, Ellipse

plt.rcParams.update({"font.family": "Inter", "font.size": 8})
INK, GREY, ACCENT, WATER = "#1d1d1b", "#8a8780", "#b5552b", "#3d7ea6"
GREYW = "#7a6fa8"          # greywater line colour
SOIL = "#8c6a4f"
C_GROUND = "#e9e2d6"
C_STONE = "#a9a39a"
C_GRAVEL = "#d9d2c3"
C_COARSE = "#bdb4a3"
C_TANK = "#5f8a6b"
import os
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out") + os.sep


def sheet(title, sub, no):
    fig = plt.figure(figsize=(11, 8.5), dpi=200)
    fig.text(0.035, 0.955, title, fontsize=15, fontweight="semibold", color=INK, va="top")
    fig.text(0.035, 0.915, sub, fontsize=9, color=GREY, va="top")
    fig.text(0.965, 0.955, no, fontsize=15, fontweight="semibold", color=ACCENT, va="top", ha="right")
    fig.text(0.965, 0.915, "Naddi cottage · wastewater", fontsize=8, color=GREY, va="top", ha="right")
    fig.add_artist(plt.Line2D([0.035, 0.965], [0.895, 0.895], color=INK, lw=0.8, transform=fig.transFigure))
    return fig


def lab(ax, xy, txt, xytext, color=INK, fs=7.2, ha="left", va="center", rel=None):
    kw = dict(arrowstyle="-", lw=0.45, color=color, shrinkA=0, shrinkB=1)
    if rel:
        kw["relpos"] = rel
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=fs, color=color, ha=ha, va=va, arrowprops=kw,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.3, alpha=0.9), zorder=50)


def R(ax, x0, z0, w, h, **kw):
    ax.add_patch(Rectangle((x0, z0), w, h, **kw))


def pipe(ax, pts, color=INK, lw=2.2, arrow_at=None):
    xs, zs = zip(*pts)
    ax.plot(xs, zs, color=color, lw=lw, solid_capstyle="butt", zorder=8)
    if arrow_at is not None:
        i = arrow_at
        a, b = pts[i], pts[i + 1]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        d = (b[0] - a[0], b[1] - a[1])
        n = math.hypot(*d)
        ax.add_patch(FancyArrowPatch((m[0] - d[0] / n * 0.01, m[1] - d[1] / n * 0.01), (m[0] + d[0] / n * 0.6, m[1] + d[1] / n * 0.6),
                                     arrowstyle="-|>", mutation_scale=9, color=color, lw=0, zorder=9))


def gravel(ax, x0, z0, w, h, size, color, ec="#6d675e", density=1.0, seed=1):
    rnd = random.Random(seed)
    R(ax, x0, z0, w, h, fc=color, ec="none", zorder=3)
    n = int(w * h / (size * size) * 0.55 * density)
    for _ in range(n):
        cx, cz = rnd.uniform(x0 + size * 0.4, x0 + w - size * 0.4), rnd.uniform(z0 + size * 0.4, z0 + h - size * 0.4)
        r = size * rnd.uniform(0.32, 0.5)
        ax.add_patch(Ellipse((cx, cz), r * 2, r * 1.7, angle=rnd.uniform(0, 180), fc=color, ec=ec, lw=0.35, zorder=4))


def reeds(ax, x0, x1, ztop, n, seed=3, h=2.6):
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n + rnd.uniform(-0.15, 0.15)
        hh = h * rnd.uniform(0.75, 1.1)
        lean = rnd.uniform(-0.25, 0.25)
        ax.plot([x, x + lean], [ztop, ztop + hh], color="#6f8f4e", lw=0.9, zorder=6)
        for k in range(3):
            t = rnd.uniform(0.35, 0.85)
            bx, bz = x + lean * t, ztop + hh * t
            s = rnd.choice([-1, 1])
            ax.plot([bx, bx + s * rnd.uniform(0.35, 0.7)], [bz, bz + rnd.uniform(0.1, 0.45)], color="#86a862", lw=0.8, zorder=6)
        ax.plot([x + lean], [ztop + hh], marker="o", ms=1.8, color="#9a7d52", zorder=6)


# =====================================================================================================  S-01
def sheet_s01():
    fig = sheet("Wastewater — toilet to soakaway",
                "Toilet water through the biodigester and a test chamber; greywater settled separately; both polished in a reed bed",
                "S-01")
    fig.text(0.035, 0.03, "Schematic elevation along the flow; not to scale. Biodigester outlet about 12\" above the lower terrace; levels on S-02.",
             fontsize=7, color=GREY)
    ax = fig.add_axes([0.03, 0.40, 0.94, 0.48])
    ax.set_xlim(-9, 64)
    ax.set_ylim(-9.5, 7.6)
    ax.axis("off")
    # two terraces: upper (house, biodigester) and lower (test chamber, reed bed). Feet; lower terrace ground = 0
    UG = 1.83                                    # upper terrace ground: biodigester outlet (+12") is ~10" below it
    STEPX = 9.0
    ax.add_patch(Polygon([(-9, UG), (STEPX, UG), (STEPX, 0), (64, 0), (64, -9.5), (-9, -9.5)], closed=True, fc=C_GROUND,
                         ec="none", zorder=1))
    ax.plot([-9, STEPX, STEPX, 64], [UG, UG, 0, 0], color=SOIL, lw=1.0, zorder=2)
    R(ax, STEPX - 0.35, 0, 0.35, UG, fc=C_STONE, ec=INK, lw=0.6, zorder=3)          # terrace step wall
    ax.text(-8.6, UG - 0.35, "upper terrace", fontsize=6.8, color=GREY, va="top")
    ax.text(40.0, 0.2, "lower terrace", fontsize=6.8, color=GREY, va="bottom")
    # washroom: floor 1 ft above the upper terrace
    FL = UG + 1.0
    R(ax, -9, UG, 9, 1.0, fc="#c9c6bf", ec=INK, lw=0.7, zorder=5)
    ax.plot([0, 0], [FL, FL + 3.8], color=INK, lw=1.2, zorder=5)
    ax.text(-8.6, FL + 3.7, "washroom\n(dome extension)", fontsize=7.5, color=GREY, va="top")
    ax.add_patch(Polygon([(-4.9, FL), (-3.9, FL), (-3.6, FL + 0.9), (-5.2, FL + 0.9)], closed=True, fc="white", ec=INK, lw=0.8, zorder=6))
    R(ax, -5.9, FL + 0.9, 0.7, 1.1, fc="white", ec=INK, lw=0.8, zorder=6)
    ax.text(-4.4, FL + 1.25, "WC", fontsize=7, ha="center", color=INK, zorder=7)
    pipe(ax, [(-4.4, FL), (-4.4, 1.35), (2.8, 1.17)], color=INK, arrow_at=1)
    # biodigester in its ditch on the upper terrace, lid at ground
    tx0 = 3.0
    ax.add_patch(Polygon([(2.5, UG), (2.8, UG - 1.4), (7.2, UG - 1.4), (7.5, UG)], closed=True, fc="#f4efe6", ec=SOIL, lw=0.6, zorder=2))
    R(ax, tx0, UG - 1.15, 4.0, 1.15, fc=C_TANK, ec=INK, lw=0.9, zorder=6)
    for k in (1, 2):
        ax.plot([tx0 + 4.0 * k / 3] * 2, [UG - 1.15, UG - 0.25], color="#2f4a37", lw=0.7, zorder=7)
    R(ax, tx0 + 0.3, UG, 1.1, 0.12, fc="#5d5a55", ec=INK, lw=0.5, zorder=7)
    ax.plot([tx0 + 3.6] * 2, [UG, UG + 0.9], color=INK, lw=1.4, zorder=6)
    ax.add_patch(Polygon([(tx0 + 3.35, UG + 0.9), (tx0 + 3.85, UG + 0.9), (tx0 + 3.6, UG + 1.15)], fc=INK, zorder=6))
    ax.text(tx0 + 3.35, UG + 1.05, "vent (per maker)", fontsize=6.6, color=INK, va="center", ha="right", zorder=9)
    ax.text(tx0 + 2.0, UG - 0.75, "500 L", fontsize=6.8, color="white", ha="center", va="center", zorder=8)
    out_z = 1.0
    # test chamber T: raised box on the lower terrace, lid about 18" up
    Tx = 12.0
    R(ax, Tx, -0.3, 1.0, 1.8, fc="white", ec=INK, lw=0.9, zorder=6)
    R(ax, Tx - 0.1, 1.5, 1.2, 0.12, fc="#5d5a55", ec=INK, lw=0.5, zorder=7)
    pipe(ax, [(tx0 + 4.0, out_z), (Tx + 0.3, 0.9)], color=INK, arrow_at=0)
    ax.plot([Tx + 0.3, Tx + 0.3], [0.9, 0.78], color=INK, lw=2.2, zorder=8)
    ax.plot([Tx + 0.3] * 2, [0.72, 0.4], color=WATER, lw=1.2, ls=(0, (2, 1)), zorder=8)
    ax.text(Tx + 0.5, 2.0, "T", fontsize=10, fontweight="semibold", color=ACCENT, ha="center", zorder=8)
    # junction chamber J
    Jx = 17.0
    R(ax, Jx, -0.5, 1.0, 1.4, fc="white", ec=INK, lw=0.9, zorder=6)
    R(ax, Jx - 0.1, 0.9, 1.2, 0.12, fc="#5d5a55", ec=INK, lw=0.5, zorder=7)
    pipe(ax, [(Tx + 1.0, 0.33), (Jx, 0.27)], color=INK, arrow_at=0)
    ax.text(Jx - 0.45, 1.25, "J", fontsize=10, fontweight="semibold", color=ACCENT, ha="center", zorder=8)
    # greywater route (drawn above for clarity)
    gt_x, gtz = 2.4, FL + 0.55
    R(ax, gt_x, gtz, 1.0, 0.6, fc="#e8e4f2", ec=GREYW, lw=0.9, zorder=6)
    st_x, stz = 13.6, 2.6
    R(ax, st_x, stz, 3.0, 1.0, fc="#e8e4f2", ec=GREYW, lw=0.9, zorder=6)
    ax.plot([st_x + 1.5] * 2, [stz, stz + 0.75], color=GREYW, lw=0.8, zorder=7)
    pipe(ax, [(0.0, FL + 1.1), (gt_x, gtz + 0.4)], color=GREYW, lw=1.8)
    pipe(ax, [(gt_x + 1.0, gtz + 0.3), (st_x, stz + 0.8)], color=GREYW, lw=1.8, arrow_at=0)
    pipe(ax, [(st_x + 3.0, stz + 0.6), (Jx + 0.35, stz + 0.45), (Jx + 0.35, 0.4)], color=GREYW, lw=1.8, arrow_at=0)
    ax.text(4.0, FL + 1.12, "greywater: shower, basin, kitchen, laundry\n(its own pipe; drawn above ground for clarity)", fontsize=6.8,
            color=GREYW, va="bottom")
    # reed bed on the lower terrace: gravel 3" above ground, walls 9" above
    bx0, BL = 21.0, 9.0
    gtop, wl, gbot = 0.25, -0.08, -1.75
    R(ax, bx0 - 0.75, gbot - 0.25, BL + 1.5, 0.75 - gbot + 0.25, fc=C_STONE, ec=INK, lw=0.7, zorder=4)
    R(ax, bx0, gbot, BL, 0.75 - gbot, fc="white", ec="none", zorder=4)
    gravel(ax, bx0, gbot, BL, gtop - gbot, 0.28, C_GRAVEL, density=0.6, seed=5)
    ax.plot([bx0, bx0 + BL], [wl] * 2, color=WATER, lw=1.0, ls=(0, (4, 2)), zorder=7)
    reeds(ax, bx0 + 0.4, bx0 + BL - 0.4, gtop, 9, seed=5, h=2.6)
    pipe(ax, [(Jx + 1.0, 0.22), (bx0 + 0.5, 0.08)], color=INK, arrow_at=0)
    Ox = bx0 + BL + 0.75
    R(ax, Ox, gbot - 0.3, 1.5, 0.75 - gbot + 0.3, fc="white", ec=INK, lw=0.9, zorder=6)
    R(ax, Ox - 0.1, 0.75, 1.7, 0.12, fc="#5d5a55", ec=INK, lw=0.5, zorder=7)
    pipe(ax, [(bx0 + BL - 0.6, gbot + 0.25), (Ox + 0.6, gbot + 0.25), (Ox + 0.6, wl)], color=INK, lw=1.8)
    trench_x0, trench_x1 = 39.0, 56.0
    gravel(ax, trench_x0, -2.0, trench_x1 - trench_x0, 1.5, 0.3, C_COARSE, density=0.5, seed=9)
    pipe(ax, [(Ox + 1.5, -0.67), (trench_x0, -0.8), (trench_x1, -1.0)], color=INK, lw=1.8, arrow_at=0)
    for x in range(int(trench_x0) + 1, int(trench_x1)):
        z = -0.8 - (x - trench_x0) / (trench_x1 - trench_x0) * 0.2
        ax.plot([x, x - 0.15], [z - 0.12, z - 0.45], color=WATER, lw=0.7, zorder=8)
    # terrace step dimension
    ax.annotate("", xy=(STEPX + 0.4, 0), xytext=(STEPX + 0.4, UG), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))

    # labels
    lab(ax, (-4.4, 1.3), "110 mm soil pipe, fall 1:40", (-8.6, -0.9), rel=(0.85, 1))
    lab(ax, (tx0 + 1.0, UG - 1.0), "biodigester, toilet water only\n(4 × 4 × 1.15 ft, rated for 5;\nfor one person it holds 2–3 weeks)", (-8.6, -3.0), rel=(1, 0.5))
    lab(ax, (tx0 + 4.0, out_z), "its outlet: about 12\" above\nthe lower terrace", (1.2, -4.9), rel=(0.8, 1))
    lab(ax, (Tx + 0.5, 0.0), "T  test chamber, standing\non the lower terrace (detail below)", (3.0, -7.6), color=ACCENT, rel=(1, 0.5))
    lab(ax, (gt_x + 0.5, gtz + 0.6), "grease trap\n(kitchen sink)", (2.9, 5.9), color=GREYW, ha="center", rel=(0.5, 0))
    lab(ax, (st_x + 2.2, stz + 1.0), "settling tank, two\nchambers, ~200–300 L", (15.6, 5.6), color=GREYW, ha="center", rel=(0.5, 0))
    lab(ax, (Jx + 0.5, -0.2), "J  greywater joins\nafter the test", (14.0, -8.7), color=ACCENT, rel=(1, 0.5))
    lab(ax, (bx0 + 4.5, -1.0), "one reed bed, 9 × 6 ft, gravel 3\" above\nthe lower terrace (S-02, S-03)", (26.0, -8.3), rel=(0.5, 1))
    lab(ax, (bx0 + BL - 0.3, wl), "water kept 4\" below\nthe gravel surface", (33.0, 2.4), color=WATER, rel=(0, 0.5))
    lab(ax, (Ox + 0.75, -0.6), "outlet chamber: swivel\nelbow sets the level", (35.5, 4.4), rel=(0, 0.5))
    lab(ax, (48.0, -1.0), "soak trench: perforated pipe in\ngravel, well away from springs\nand wells", (48.0, -8.3), rel=(0.5, 1))
    lab(ax, (bx0 - 0.4, 0.75), "walls 9\" above\nthe lower terrace", (23.5, 3.8), rel=(0.5, 0))
    ax.text(STEPX + 0.6, UG / 2, "step\n≈ 22\"", fontsize=6.4, color=INK, va="center", zorder=9)

    # ---------------------------------------------- detail: test chamber
    bx = fig.add_axes([0.04, 0.07, 0.30, 0.30])
    bx.set_xlim(-0.5, 3.6)
    bx.set_ylim(-0.4, 2.7)
    bx.set_aspect("equal")
    bx.axis("off")
    bx.add_patch(Polygon([(-0.5, 0.55), (3.6, 0.55), (3.6, -0.4), (-0.5, -0.4)], fc=C_GROUND, ec="none", zorder=1))
    bx.plot([-0.5, 0.3], [0.55, 0.55], color=SOIL, lw=0.8, zorder=1)
    bx.plot([1.6, 3.6], [0.55, 0.55], color=SOIL, lw=0.8, zorder=1)
    R(bx, 0.3, 0.0, 0.15, 2.0, fc=C_STONE, ec=INK, lw=0.6, zorder=2)
    R(bx, 1.45, 0.0, 0.15, 2.0, fc=C_STONE, ec=INK, lw=0.6, zorder=2)
    R(bx, 0.3, -0.15, 1.3, 0.15, fc=C_STONE, ec=INK, lw=0.6, zorder=2)
    R(bx, 0.45, 0.0, 1.0, 2.0, fc="white", ec="none", zorder=2)
    bx.add_patch(Polygon([(0.45, 0.32), (1.45, 0.12), (1.45, 0.0), (0.45, 0.0)], fc="#cfcac0", ec=INK, lw=0.5, zorder=3))   # benching
    R(bx, 0.2, 2.0, 1.55, 0.1, fc="#5d5a55", ec=INK, lw=0.5, zorder=4)
    R(bx, 1.0, 2.25, 1.55, 0.1, fc="#5d5a55", ec=INK, lw=0.5, zorder=4)            # lid lifted aside
    bx.text(2.6, 2.32, "lid", fontsize=6.5, color=GREY, va="center")
    # inlet pipe with down-turned end
    bx.plot([-0.5, 0.75], [1.15, 1.15], color=INK, lw=5, solid_capstyle="butt", zorder=5)
    bx.plot([0.72, 0.72], [1.17, 0.95], color=INK, lw=5, solid_capstyle="butt", zorder=5)
    bx.plot([0.72] * 2, [0.93, 0.62], color=WATER, lw=1.5, zorder=5)
    # outlet pipe lower on the far side
    bx.plot([1.45, 3.6], [0.1, 0.02], color=INK, lw=5, solid_capstyle="butt", zorder=5)
    # glass jar under the stream
    bx.add_patch(Polygon([(0.58, 0.35), (0.86, 0.35), (0.88, 0.75), (0.56, 0.75)], fc="#e6f2fa", ec=INK, lw=0.6, zorder=6))
    bx.add_patch(Polygon([(0.59, 0.36), (0.85, 0.36), (0.86, 0.6), (0.58, 0.6)], fc="#e7d7a8", ec="none", zorder=6))
    lab(bx, (0.72, 0.8), "inlet ends turned down,\n6\" above the outlet, so\nthe flow falls in a stream", (1.95, 1.6), fs=6.8, rel=(0, 0.5))
    lab(bx, (0.72, 0.5), "clear glass jar", (1.95, 0.85), fs=6.8, rel=(0, 0.5))
    lab(bx, (1.2, 0.15), "floor benched to the outlet:\nno standing water", (1.95, 0.35), fs=6.8, rel=(0, 0.5))
    bx.text(-0.5, -0.32, "T  Test chamber · 12 × 12\" inside, brick, standing\non the lower terrace with its lid about 18\" up", fontsize=7.4,
            fontweight="semibold", color=INK, va="top")

    # ---------------------------------------------- jars: what to look for
    jx = fig.add_axes([0.37, 0.07, 0.25, 0.30])
    jx.set_xlim(0, 4)
    jx.set_ylim(-1.6, 3.0)
    jx.set_aspect("equal")
    jx.axis("off")

    def jar(x, fill, label, note, col):
        jx.add_patch(Polygon([(x, 0.4), (x + 1.2, 0.4), (x + 1.25, 2.0), (x - 0.05, 2.0)], fc="#f3f8fb", ec=INK, lw=0.8, zorder=2))
        jx.add_patch(Polygon([(x + 0.03, 0.43), (x + 1.17, 0.43), (x + 1.21, 1.7), (x - 0.01, 1.7)], fc=fill, ec="none", zorder=3))
        R(jx, x - 0.08, 2.0, 1.36, 0.14, fc="#9a958c", ec=INK, lw=0.6, zorder=3)
        jx.text(x + 0.6, 2.35, label, fontsize=8, fontweight="semibold", color=col, ha="center")
        jx.text(x + 0.6, 0.25, note, fontsize=6.6, color=INK, ha="center", va="top", linespacing=1.35)

    jar(0.3, "#e9dba8", "Working", "clear to pale tea;\nfaint earthy smell;\nlittle settles in\n30 minutes", "#4f7d3a")
    jar(2.4, "#7d776c", "Not working", "grey or black, murky;\nbits floating; rotten-\negg smell; a layer\nof sludge settles", ACCENT)
    rnd = random.Random(2)
    for _ in range(40):
        jx.plot(rnd.uniform(2.5, 3.5), rnd.uniform(0.5, 1.6), marker="o", ms=rnd.uniform(0.8, 2.2), color="#4d483f", zorder=4)
    R(jx, 2.43, 0.43, 1.14, 0.18, fc="#4d483f", ec="none", zorder=4)
    jx.text(0, -1.05, "Flush twice, then catch the stream. Same time\neach month; photograph the jar against white.",
            fontsize=6.8, color=GREY, va="top")

    # ---------------------------------------------- notes
    nx = fig.add_axes([0.65, 0.07, 0.33, 0.30])
    nx.axis("off")
    nx.set_xlim(0, 10)
    nx.set_ylim(0, 10)
    notes = [
        ("What goes where", True, ACCENT),
        ("Toilet only → biodigester → T → J → reed bed.", False, INK),
        ("Shower, basin, kitchen, laundry → grease trap", False, GREYW),
        ("(kitchen) → settling tank → J → reed bed.", False, GREYW),
        ("", False, INK),
        ("Why greywater skips the biodigester", True, ACCENT),
        ("Soap, detergent and kitchen grease slow its bacteria,", False, INK),
        ("and soapy water is naturally cloudy, so mixing it in", False, INK),
        ("would make the jar test meaningless.", False, INK),
        ("", False, INK),
        ("Never down any drain", True, ACCENT),
        ("Phenyl, acid or bleach toilet cleaners, paint,", False, INK),
        ("solvents, cooking oil, wipes, sanitary pads.", False, INK),
    ]
    for i, (t, b, c) in enumerate(notes):
        nx.text(0, 9.7 - i * 0.74, t, fontsize=7.6 if b else 7.1, fontweight="semibold" if b else "normal", color=c)
    fig.savefig(OUTDIR + "08_wastewater_system.png", dpi=200, facecolor="white")
    print("S-01 ok")


# =====================================================================================================  S-02
def sheet_s02():
    fig = sheet("Reed bed — two cells in series",
                "Horizontal subsurface flow: water runs through gravel under the surface, past the reed roots, never standing on top",
                "S-02")
    fig.text(0.035, 0.03, "Dimensions in feet and inches, inside the walls. Liner under every option. Levels indicative.",
             fontsize=7, color=GREY)
    # ------------------------------------------- long section
    ax = fig.add_axes([0.03, 0.47, 0.94, 0.41])
    ax.set_xlim(-2.6, 23.6)
    ax.set_ylim(-4.0, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    W = 0.75      # wall thickness (9")
    L = 7.0
    D = 2.0
    STEP = 0.75
    cells = [(0.0, 0.0), (L + W + 1.0 + W, -STEP)]
    # ground
    gpts = [(-2.6, 0.55), (0.0, 0.25), (L + W + 1.0 + W, 0.25 - STEP), (23.6, -1.5)]
    ax.add_patch(Polygon(gpts + [(23.6, -3.6), (-2.6, -3.6)], closed=True, fc=C_GROUND, ec="none", zorder=1))
    for (cx, base) in cells:
        top = base + 0.0
        # walls + base slab
        R(ax, cx - W, top - D - 0.25, L + 2 * W, 0.25, fc="#c9c6bf", ec=INK, lw=0.7, zorder=2)          # PCC base
        R(ax, cx - W, top - D, W, D + 0.4, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
        R(ax, cx + L, top - D, W, D + 0.4, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
        # liner
        ax.plot([cx + 0.03, cx + 0.03, cx + L - 0.03, cx + L - 0.03], [top + 0.3, top - D + 0.03, top - D + 0.03, top + 0.3],
                color="#2b2b2b", lw=1.6, zorder=6)
        # media zones
        gravel(ax, cx + 0.05, top - D + 0.05, 1.25, D - 0.05, 0.32, C_COARSE, density=1.1, seed=int(cx) + 1)
        gravel(ax, cx + 1.3, top - D + 0.05, L - 2.6, D - 0.25, 0.13, C_GRAVEL, density=0.9, seed=int(cx) + 2)
        R(ax, cx + 1.3, top - 0.2, L - 2.6, 0.2, fc="#e9e4d8", ec="none", zorder=3)
        gravel(ax, cx + L - 1.3, top - D + 0.05, 1.25, D - 0.05, 0.32, C_COARSE, density=1.1, seed=int(cx) + 3)
        for xx in (cx + 1.3, cx + L - 1.3):
            ax.plot([xx, xx], [top - D + 0.05, top], color="#8a8378", lw=0.5, ls=(0, (2, 2)), zorder=5)
        # water level
        ax.plot([cx + 0.05, cx + L - 0.05], [top - 0.33] * 2, color=WATER, lw=1.2, ls=(0, (5, 2)), zorder=7)
        # inlet spreader (perforated pipe across the width, seen end on) and outlet collector at the bottom
        ax.add_patch(Circle((cx + 0.6, top - 0.25), 0.16, fc="white", ec=INK, lw=1.0, zorder=8))
        ax.add_patch(Circle((cx + L - 0.6, top - D + 0.25), 0.2, fc="white", ec=INK, lw=1.0, zorder=8))
        reeds(ax, cx + 1.4, cx + L - 1.4, top, 6, seed=int(cx) + 5, h=2.5)
    c1, c2 = cells
    # inlet from J
    ax.plot([-2.6, c1[0] + 0.6], [-0.25, -0.25], color=INK, lw=2.4, zorder=7)
    ax.add_patch(FancyArrowPatch((-2.4, -0.25), (-1.6, -0.25), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=9))
    # level-control chamber between cells
    mx = L + W
    R(ax, mx, -D - 0.25, 1.0, D + 0.65, fc="white", ec=INK, lw=0.8, zorder=2)
    ax.plot([c1[0] + L - 0.6, mx + 0.5, mx + 0.5], [-D + 0.25, -D + 0.25, -0.33], color=INK, lw=2.4, zorder=7)
    ax.plot([mx + 0.5, mx + 0.75], [-0.33, -0.33 - 0.05], color=INK, lw=2.4, zorder=7)
    ax.plot([mx + 0.75, c2[0] + 0.6], [-0.4, c2[1] - 0.25], color=INK, lw=2.4, zorder=7)
    # outlet chamber with swivel elbow
    ox = c2[0] + L + W
    R(ax, ox, c2[1] - D - 0.25, 1.1, D + 0.65, fc="white", ec=INK, lw=0.8, zorder=2)
    ax.plot([c2[0] + L - 0.6, ox + 0.45, ox + 0.45], [c2[1] - D + 0.25, c2[1] - D + 0.25, c2[1] - 0.33], color=INK, lw=2.4, zorder=7)
    ax.plot([ox + 0.45, ox + 0.45], [c2[1] - D + 0.25, c2[1] - D + 0.6], color=INK, lw=2.4, zorder=7)
    ax.plot([ox + 0.35, ox + 1.1], [c2[1] - 0.85, c2[1] - 0.85], color=INK, lw=2.4, zorder=7)
    ax.plot([ox + 1.1, 23.6], [c2[1] - 0.85, c2[1] - 1.05], color=INK, lw=2.4, zorder=7)
    ax.add_patch(FancyArrowPatch((22.4, c2[1] - 1.0), (23.4, c2[1] - 1.04), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=9))
    # dims
    def hdim(x0, x1, z, t):
        ax.annotate("", xy=(x0, z), xytext=(x1, z), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, z - 0.12, t, fontsize=7, ha="center", va="top", color=INK)
    hdim(c1[0], c1[0] + L, -D - 0.6, "7'-0\"")
    hdim(c2[0], c2[0] + L, c2[1] - D - 0.6, "7'-0\"")
    ax.annotate("", xy=(-0.95, 0), xytext=(-0.95, -D), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    ax.text(-1.05, -1.0, "2'-0\"", fontsize=7, ha="right", va="center", rotation=90)
    # labels
    lab(ax, (c1[0] + 0.6, -0.25), "inlet: perforated 75 mm pipe across\nthe width, in 2–4\" stone", (-2.5, 2.7), rel=(0.5, 0))
    lab(ax, (c1[0] + 3.5, -1.2), "main bed: washed ½–¾\" gravel\n(10–20 mm), no fines", (2.6, 3.6), rel=(0.5, 0))
    lab(ax, (c1[0] + 3.5, -0.33), "water level 4\" below\nthe surface", (6.3, 2.2), color=WATER, rel=(0.5, 0))
    lab(ax, (c1[0] + L - 0.6, -D + 0.25), "outlet: perforated pipe at\nthe bottom, in 2–4\" stone", (2.4, -3.55), rel=(1, 0.5))
    lab(ax, (mx + 0.5, -0.9), "chamber: riser sets\ncell 1's level, spills\nto cell 2", (11.2, 3.3), rel=(0.5, 0))
    lab(ax, (ox + 0.45, c2[1] - 0.33), "outlet chamber: swivel elbow;\nturn it down to drain the bed", (20.6, 2.7), rel=(0.5, 0))
    lab(ax, (c2[0] + 5.5, c2[1] + 1.9), "common reed (Phragmites),\n~4 plants per sq m", (16.4, 3.4), color="#4f7d3a", rel=(0, 0.5))
    lab(ax, (c1[0] + 0.03, -1.5), "liner up the walls,\nabove the gravel", (-2.5, -2.4), rel=(1, 0.5))
    lab(ax, (c2[0] + L + 0.4, c2[1] + 0.3), "wall top 4–6\" above\nground: a kerb", (21.0, -2.6), rel=(0.5, 1))
    lab(ax, (3.0, -D - 0.12), "base falls ~1%\nto the outlet", (-2.5, -3.55), rel=(1, 0.5))
    ax.text(-2.5, 3.95, "Long section through both cells", fontsize=8.2, fontweight="semibold", color=INK, va="top")

    # ------------------------------------------- plan
    px = fig.add_axes([0.03, 0.07, 0.48, 0.36])
    px.set_xlim(-2.5, 23.0)
    px.set_ylim(-3.6, 6.6)
    px.set_aspect("equal")
    px.axis("off")
    Wd = 4.0
    for (cx, _) in cells:
        R(px, cx - W, -W, L + 2 * W, Wd + 2 * W, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
        R(px, cx, 0, L, Wd, fc=C_GRAVEL, ec=INK, lw=0.7, zorder=3)
        R(px, cx, 0, 1.25, Wd, fc=C_COARSE, ec="none", zorder=3)
        R(px, cx + L - 1.25, 0, 1.25, Wd, fc=C_COARSE, ec="none", zorder=3)
        px.plot([cx + 0.6] * 2, [0.2, Wd - 0.2], color=INK, lw=2.0, zorder=5)
        px.plot([cx + L - 0.6] * 2, [0.2, Wd - 0.2], color=INK, lw=2.0, ls=(0, (2, 1)), zorder=5)
        rnd = random.Random(int(cx))
        for i in range(5):
            for j in range(3):
                x, y = cx + 1.8 + i * 0.9 + rnd.uniform(-0.1, 0.1), 0.8 + j * 1.2 + rnd.uniform(-0.1, 0.1)
                px.add_patch(Circle((x, y), 0.18, fc="#86a862", ec="#4f7d3a", lw=0.4, zorder=5))
        px.text(cx + L / 2, Wd + W + 0.25, "cell 1" if cx == 0 else "cell 2 (9\" lower)", fontsize=7.4, ha="center", va="bottom",
                color=INK, fontweight="semibold")
    R(px, mx, Wd / 2 - 0.5, 1.0, 1.0, fc="white", ec=INK, lw=0.8, zorder=4)
    R(px, ox, Wd / 2 - 0.55, 1.1, 1.1, fc="white", ec=INK, lw=0.8, zorder=4)
    px.plot([c1[0] + L - 0.6, mx + 0.5], [Wd / 2] * 2, color=INK, lw=2.0, zorder=5)
    px.plot([mx + 0.5, c2[0] + 0.6], [Wd / 2] * 2, color=INK, lw=2.0, zorder=5)
    px.plot([c2[0] + L - 0.6, ox + 0.55], [Wd / 2] * 2, color=INK, lw=2.0, zorder=5)
    px.plot([ox + 1.1, 23.0], [Wd / 2] * 2, color=INK, lw=2.0, zorder=5)
    px.plot([-2.5, c1[0] + 0.6], [Wd / 2] * 2, color=INK, lw=2.0, zorder=5)
    px.add_patch(FancyArrowPatch((-2.4, Wd / 2), (-1.4, Wd / 2), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=9))
    px.text(-2.4, Wd / 2 + 0.3, "from J", fontsize=6.8, color=INK, va="bottom")
    px.text(22.9, Wd / 2 + 0.3, "to soak\ntrench", fontsize=6.8, color=INK, va="bottom", ha="right")
    px.annotate("", xy=(c1[0], -1.5), xytext=(c1[0] + L, -1.5), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    px.text(c1[0] + L / 2, -1.65, "7'-0\"", fontsize=7, ha="center", va="top")
    px.annotate("", xy=(-1.4, 0), xytext=(-1.4, Wd), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    px.text(-1.55, Wd / 2 - 0.9, "4'-0\"", fontsize=7, ha="right", va="center", rotation=90)
    px.text(-2.5, -2.5, "Plan · 2 × (4 × 7 ft) = 56 sq ft ≈ 5.2 m²: the low end of the usual 5–10 m² per\nperson, for all the household's water. One cell alone suits the toilet outflow only.",
            fontsize=7.2, color=INK, va="top")
    px.text(-2.5, 6.5, "Plan", fontsize=8.2, fontweight="semibold", color=INK, va="top")

    # ------------------------------------------- cross-section with two wall options
    cx_ = fig.add_axes([0.54, 0.07, 0.44, 0.36])
    cx_.set_xlim(-3.3, 7.6)
    cx_.set_ylim(-3.3, 3.6)
    cx_.set_aspect("equal")
    cx_.axis("off")
    # ground both sides
    cx_.add_patch(Polygon([(-3.3, -0.25), (6.7, -0.25), (7.6, -0.25), (7.6, -3.3), (-3.3, -3.3)], fc=C_GROUND, ec="none", zorder=1))
    # left half: masonry wall
    R(cx_, -0.75, -2.25, 0.75, 2.6, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
    R(cx_, -0.9, -2.5, 3.0, 0.25, fc="#c9c6bf", ec=INK, lw=0.7, zorder=2)
    cx_.plot([0.03, 0.03, 2.0], [0.3, -1.97, -1.97], color="#2b2b2b", lw=1.6, zorder=6)
    # right half: excavated pit with sloped side, liner, kerb
    side = [(4.0, -2.0), (4.6, -2.0), (5.3, -0.25)]
    cx_.add_patch(Polygon([(2.0, -2.0), (4.6, -2.0), (5.3, -0.25), (7.6, -0.25), (7.6, -2.3), (2.0, -2.3)], fc="#d8cbb5", ec="none", zorder=1))
    cx_.plot([2.0, 4.6, 5.3], [-2.03, -2.03, -0.28], color="#c9b98f", lw=3.5, zorder=2)          # sand cushion
    cx_.plot([2.0, 4.6, 5.3, 5.9], [-1.97, -1.97, -0.2, -0.2], color="#2b2b2b", lw=1.6, zorder=6)  # liner
    cx_.add_patch(Polygon([(5.0, -0.2), (6.2, -0.2), (6.2, 0.3), (5.0, 0.3)], fc=C_STONE, ec=INK, lw=0.7, zorder=7))  # kerb stones
    # fill (gravel) across both halves
    fillpoly = [(0.05, -1.95), (4.58, -1.95), (5.22, -0.2), (5.0, 0.0), (0.05, 0.0)]
    cx_.add_patch(Polygon(fillpoly, fc=C_GRAVEL, ec="none", zorder=3))
    rnd = random.Random(12)
    for _ in range(260):
        x, z = rnd.uniform(0.1, 5.0), rnd.uniform(-1.9, -0.05)
        if x > 4.58 + (z + 1.95) * (0.64 / 1.75):
            continue
        cx_.add_patch(Ellipse((x, z), 0.11, 0.09, angle=rnd.uniform(0, 180), fc=C_GRAVEL, ec="#6d675e", lw=0.3, zorder=4))
    cx_.plot([0.05, 5.1], [-0.33, -0.33], color=WATER, lw=1.2, ls=(0, (5, 2)), zorder=7)
    reeds(cx_, 0.4, 4.6, 0.0, 6, seed=21, h=2.3)
    cx_.plot([2.0, 2.0], [-2.5, 3.3], color=GREY, lw=0.6, ls=(0, (6, 3)), zorder=8)
    cx_.text(0.95, 3.4, "A  Stone walls", fontsize=7.8, fontweight="semibold", ha="center", color=INK)
    cx_.text(3.6, 3.4, "B  Lined pit", fontsize=7.8, fontweight="semibold", ha="center", color=INK)
    lab(cx_, (-0.4, -0.8), "9\" stone in cement,\n3\" PCC base; waterproof\ncement plaster inside,\nor a liner (better)", (-3.2, -1.2), fs=6.6, rel=(1, 0.5))
    lab(cx_, (0.03, 0.1), "liner or plaster\nup to the top", (-3.2, 1.3), fs=6.6, rel=(1, 0.5))
    lab(cx_, (5.0, -1.2), "0.5–1 mm HDPE pond liner\non a sand cushion, geotextile\nover it before the stone", (5.1, -2.8), fs=6.6, rel=(0.5, 1))
    lab(cx_, (5.6, 0.3), "stone kerb holds the\nliner edge, keeps\nrunoff out", (6.0, 1.9), fs=6.6, rel=(0.5, 0))
    cx_.annotate("", xy=(0.05, -2.75), xytext=(4.6, -2.75), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    cx_.text(2.3, -2.85, "4'-0\" (at the base)", fontsize=6.8, ha="center", va="top")
    cx_.text(-3.2, 3.4, "Cross-section", fontsize=8.2, fontweight="semibold", color=INK, va="bottom")
    fig.savefig(OUTDIR + "09_reed_bed.png", dpi=200, facecolor="white")
    print("S-02 ok")


if __name__ == "__main__":
    sheet_s01()      # the reed bed sheets now come from reedbed.py
