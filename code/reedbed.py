"""Single reed bed, 9 x 6 ft, on a flat terrace: S-02 (section inlet->outlet + layers top->bottom), S-03 (plan + cross-section + build steps).
Units: inches. Level 0 = the lower terrace's ground. The biodigester outlet is about 12" above it."""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Circle, Ellipse
from wastewater import sheet, lab, R, INK, GREY, ACCENT, WATER, SOIL, C_GROUND, C_STONE, C_GRAVEL, C_COARSE, OUTDIR

C_PEA = "#e6dfcf"
C_LINER = "#2b2b2b"
C_PCC = "#c9c6bf"
C_PLASTER = "#d8d4cc"
GREEN = "#4f7d3a"

L, Wd = 108.0, 72.0          # inside length (inlet -> outlet) and width
WALL = 9.0
Z_TOP, Z_WL, Z_PEA = 3.0, -1.0, 0.0
Z_BASE_IN, Z_BASE_OUT = -20.0, -21.0
Z_KERB = 9.0
Z_INLET = 1.0
Z_OUT = -8.0
ZONE = 18.0


def base_z(x):
    return Z_BASE_IN + (Z_BASE_OUT - Z_BASE_IN) * (x / L)


def stones(ax, x0, x1, zf, ztop, size, color, density=1.0, seed=1, ec="#6d675e"):
    rnd = random.Random(seed)
    pts = [(x0, zf(x0)), (x1, zf(x1)), (x1, ztop), (x0, ztop)]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", zorder=3))
    area = (x1 - x0) * (ztop - zf((x0 + x1) / 2))
    n = int(area / (size * size) * 0.6 * density)
    for _ in range(n):
        cx = rnd.uniform(x0 + size * 0.45, x1 - size * 0.45)
        cz = rnd.uniform(zf(cx) + size * 0.45, ztop - size * 0.45)
        r = size * rnd.uniform(0.33, 0.5)
        ax.add_patch(Ellipse((cx, cz), r * 2, r * 1.7, angle=rnd.uniform(0, 180), fc=color, ec=ec, lw=0.35, zorder=4))


def reeds(ax, x0, x1, ztop, n, h=34.0, seed=3, s=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n + rnd.uniform(-1.5, 1.5) * s
        hh = h * rnd.uniform(0.8, 1.1)
        lean = rnd.uniform(-2.5, 2.5) * s
        ax.plot([x, x + lean], [ztop, ztop + hh], color="#6f8f4e", lw=0.9, zorder=6)
        for k in range(4):
            t = rnd.uniform(0.3, 0.85)
            bx, bz = x + lean * t, ztop + hh * t
            sg = rnd.choice([-1, 1])
            ax.plot([bx, bx + sg * rnd.uniform(4, 8) * s], [bz, bz + rnd.uniform(1, 5) * s], color="#86a862", lw=0.8, zorder=6)
        ax.add_patch(Ellipse((x + lean, ztop + hh + 1.2 * s), 1.4 * s, 3.2 * s, fc="#9a7d52", ec="none", zorder=6))
        # roots
        for k in range(3):
            ax.plot([x, x + rnd.uniform(-3, 3) * s], [ztop, ztop - rnd.uniform(5, 12) * s], color="#b89a72", lw=0.5, zorder=5)


def pipe_circle(ax, x, z, r, perforated=True):
    ax.add_patch(Circle((x, z), r, fc="white", ec=INK, lw=1.0, zorder=9))
    if perforated:
        for a in range(0, 360, 45):
            ax.plot([x + 0.55 * r * math.cos(math.radians(a))], [z + 0.55 * r * math.sin(math.radians(a))], marker="o", ms=0.9,
                    color=INK, zorder=10)


def hdim(ax, x0, x1, z, t, fs=7):
    ax.annotate("", xy=(x0, z), xytext=(x1, z), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    for x in (x0, x1):
        ax.plot([x, x], [z - 1.5, z + 1.5], color=INK, lw=0.5)
    ax.text((x0 + x1) / 2, z - 1.2, t, fontsize=fs, ha="center", va="top", color=INK)


def vdim(ax, x, z0, z1, t, fs=7):
    ax.annotate("", xy=(x, z0), xytext=(x, z1), arrowprops=dict(arrowstyle="<->", lw=0.5, color=INK, shrinkA=0, shrinkB=0))
    ax.text(x - 1.2, (z0 + z1) / 2, t, fontsize=fs, ha="right", va="center", color=INK, rotation=90)


# ==================================================================================================  S-02
def sheet_long():
    fig = sheet("Reed bed 9 × 6 ft — section, inlet to outlet",
                "One bed on the lower terrace, its gravel 3\" above the ground · water flows sideways through the gravel, 4\" below the surface",
                "S-02")
    fig.text(0.035, 0.03, "Levels in inches from the lower terrace's ground. Your biodigester outlet is about 12\" above it; check that with a "
             "water-level tube before you dig.", fontsize=7, color=GREY)
    ax = fig.add_axes([0.02, 0.36, 0.96, 0.53])
    ax.set_xlim(-58, 232)
    ax.set_ylim(-38, 70)
    ax.set_aspect("equal")
    ax.axis("off")
    # ground with the excavation
    ax.add_patch(Polygon([(-58, 0), (232, 0), (232, -38), (-58, -38)], fc=C_GROUND, ec="none", zorder=1))
    ax.plot([-58, -WALL], [0, 0], color=SOIL, lw=1.0, zorder=2)
    ax.plot([144, 232], [0, 0], color=SOIL, lw=1.0, zorder=2)
    # base slab under bed + chamber
    ax.add_patch(Polygon([(-WALL, Z_BASE_IN - 3), (144, Z_BASE_OUT - 3 - 1), (144, Z_BASE_OUT - 1), (L, Z_BASE_OUT), (0, Z_BASE_IN),
                          (-WALL, Z_BASE_IN)], closed=True, fc=C_PCC, ec=INK, lw=0.7, zorder=2))
    # walls: inlet wall, outlet wall, chamber far wall
    for x0, x1 in ((-WALL, 0), (L, L + WALL), (135, 144)):
        R(ax, x0, base_z(min(max(x0, 0), L)) if x0 < L + 1 else Z_BASE_OUT - 1, x1 - x0, Z_KERB - (base_z(min(max(x0, 0), L)) if x0 < L + 1 else Z_BASE_OUT - 1),
          fc=C_STONE, ec=INK, lw=0.7, zorder=2)
    # chamber interior + lid
    R(ax, L + WALL, Z_BASE_OUT - 1, 135 - L - WALL, Z_KERB - Z_BASE_OUT + 1, fc="white", ec="none", zorder=2)
    R(ax, L + WALL - 1, Z_KERB, 135 - L - WALL + 2, 2.5, fc="#5d5a55", ec=INK, lw=0.5, zorder=3)
    R(ax, 0, Z_TOP, L, Z_KERB - Z_TOP + 0.01, fc="white", ec="none", zorder=2)
    ax.add_patch(Polygon([(0, base_z(0)), (L, base_z(L)), (L, base_z(L) + 1.6), (0, base_z(0) + 1.6)], closed=True,
                         fc="#f1efe9", ec="none", zorder=2))
    # plaster + liner inside the bed
    ax.plot([0.5, 0.5], [Z_KERB, base_z(0) + 0.5], color=C_PLASTER, lw=2.4, zorder=3)
    ax.plot([L - 0.5, L - 0.5], [Z_KERB, base_z(L) + 0.5], color=C_PLASTER, lw=2.4, zorder=3)
    ax.plot([1.2, 1.2, L - 1.2, L - 1.2], [Z_KERB, base_z(0) + 1.2, base_z(L) + 1.2, Z_KERB], color=C_LINER, lw=1.5, zorder=7)
    # media
    zb = lambda x: base_z(x) + 1.6
    stones(ax, 1.6, ZONE, zb, Z_TOP, 2.6, C_COARSE, seed=1)
    stones(ax, ZONE, L - ZONE, zb, Z_PEA, 1.0, C_GRAVEL, density=0.75, seed=2)
    stones(ax, ZONE, L - ZONE, lambda x: Z_PEA, Z_TOP, 0.55, C_PEA, density=0.6, seed=3)
    stones(ax, L - ZONE, L - 1.6, zb, Z_TOP, 2.6, C_COARSE, seed=4)
    for xx in (ZONE, L - ZONE):
        ax.plot([xx, xx], [base_z(xx) + 1.6, Z_TOP], color="#8a8378", lw=0.5, ls=(0, (2, 2)), zorder=5)
    # water level + flow arrows
    ax.plot([1.6, L - 1.6], [Z_WL, Z_WL], color=WATER, lw=1.2, ls=(0, (5, 2)), zorder=8)
    for z in (-7, -13):
        ax.add_patch(FancyArrowPatch((30, z), (78, z - 0.4), arrowstyle="-|>", mutation_scale=10, color=WATER, lw=1.0, zorder=8, alpha=0.8))
    # inlet pipe + spreader
    ax.plot([-58, 9], [Z_INLET + 2.5, Z_INLET], color=INK, lw=4.0, solid_capstyle="butt", zorder=9)
    ax.add_patch(FancyArrowPatch((-56, Z_INLET + 2.45), (-46, Z_INLET + 2.1), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=10))
    pipe_circle(ax, 9, Z_INLET, 2.0)
    # cleanout risers (at the far end of each pipe, shown dashed)
    for x, z0 in ((9, Z_INLET + 2.0), (L - 9, base_z(L - 9) + 4.6)):
        ax.plot([x, x], [z0, Z_KERB + 2], color=INK, lw=1.0, ls=(0, (3, 2)), zorder=8)
        R(ax, x - 2.0, Z_KERB + 2, 4.0, 1.2, fc="white", ec=INK, lw=0.7, zorder=8)
    # outlet collector + swivel elbow in chamber + chamber outlet
    cz = base_z(L - 9) + 3.6
    pipe_circle(ax, L - 9, cz, 2.0)
    ax.plot([L - 9, 124], [cz, cz], color=INK, lw=4.0, solid_capstyle="butt", zorder=8)
    ax.plot([124, 124], [cz, Z_WL], color=INK, lw=4.0, solid_capstyle="butt", zorder=8)
    ax.plot([122, 126], [Z_WL, Z_WL], color=INK, lw=1.0, zorder=9)
    ax.add_patch(Circle((124, cz), 2.4, fc="none", ec=INK, lw=0.8, zorder=9))
    ax.plot([124.4, 124.4], [Z_WL - 0.6, Z_OUT + 1.0], color=WATER, lw=1.0, ls=(0, (2, 1)), zorder=9)
    ax.plot([135, 158], [Z_OUT, Z_OUT - 0.4], color=INK, lw=4.0, solid_capstyle="butt", zorder=9)
    ax.add_patch(FancyArrowPatch((150, Z_OUT - 0.25), (160, Z_OUT - 0.4), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=10))
    ax.text(147, Z_OUT - 3.5, "to soak\ntrench", fontsize=6.6, color=INK, va="top", ha="left")
    ax.plot([L + WALL, 135], [Z_WL] * 2, color=WATER, lw=0.8, ls=(0, (5, 2)), zorder=4, alpha=0.6)
    reeds(ax, ZONE + 3, L - ZONE - 3, Z_TOP, 6, seed=7)
    # dims
    hdim(ax, 0, L, -32.5, "9'-0\" inside")
    hdim(ax, 0, ZONE, -28.0, "1'-6\"", fs=6.4)
    hdim(ax, ZONE, L - ZONE, -28.0, "6'-0\"", fs=6.4)
    hdim(ax, L - ZONE, L, -28.0, "1'-6\"", fs=6.4)
    vdim(ax, -14, Z_TOP, Z_BASE_IN, "2'-0\" of gravel")
    # level ladder on the right (labels staggered so close levels stay readable)
    lx = 170
    levels = [(Z_KERB, 11, "+9\"  top of walls (kerb)"), (Z_TOP, 5.5, "+3\"  gravel surface"), (Z_INLET, 1.0, "+1\"  inlet spreader"),
              (0, -3.5, "0  lower terrace ground"), (Z_WL, -8, "−1\"  water level"), (Z_OUT, -12.5, "−8\"  outlet to soak trench"),
              (Z_BASE_OUT, -20, "−20\" / −21\"  bed floor (falls 1\")"), (Z_BASE_OUT - 3, -25, "−24\"  bottom of dig")]
    for z, zt, t in levels:
        ax.plot([lx - 6, lx - 2, lx + 1], [z, z, zt], color=GREY, lw=0.6, zorder=9)
        ax.text(lx + 2, zt, t, fontsize=6.8, color=WATER if "water" in t else INK, va="center", zorder=9,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.2, alpha=0.85))
    # labels
    lab(ax, (-30, Z_INLET + 1.6), "from J: 4\" (110 mm) pipe,\nfalling to +1\"; cover it\nwith soil or slate", (-56, -6), rel=(1, 0.5))
    lab(ax, (9, Z_INLET), "4\" perforated spreader across the\nfull 6 ft width, holes facing down,\nsitting on the stone, 2\" below the top", (-30, 60), rel=(0.6, 0))
    lab(ax, (10, -11), "inlet zone: 1½–3\"\n(40–80 mm) stone", (-56, -22), rel=(1, 0.5))
    lab(ax, (54, Z_TOP - 1.5), "3\" of pea gravel (6–10 mm)\nfor planting; stays dry", (40, 58), rel=(0.5, 0))
    lab(ax, (60, -12), "main bed: washed ½–¾\"\n(10–20 mm) gravel, no fines", (82, 60), rel=(0.3, 0))
    lab(ax, (L - 9, cz), "4\" (110 mm) perforated collector\nacross the width, on the floor", (113, -35), rel=(0, 0.5))
    lab(ax, (124, Z_OUT - 4), "swivel elbow: its top sets the water\nlevel; turn it down to drain the bed", (150, 54), rel=(0, 0.5))
    lab(ax, (9, Z_KERB + 2.6), "capped cleanout risers at one\nend of each pipe", (-56, 16), rel=(1, 0.5))
    lab(ax, (1.2, -15), "liner over plaster,\nup to the kerb", (-56, -32), rel=(1, 0.5))
    lab(ax, (L + WALL + 4, 5), "outlet chamber\n18 × 18\" inside", (150, 38), rel=(0, 0.5))

    # ---------------------------------------------- layers, top to bottom
    lx_ = fig.add_axes([0.04, 0.06, 0.40, 0.28])
    lx_.set_xlim(0, 10)
    lx_.set_ylim(-0.3, 10.4)
    lx_.axis("off")
    lx_.text(0, 10.3, "Layers, top to bottom (main bed)", fontsize=8.2, fontweight="semibold", color=INK, va="top")
    layers = [
        ("reeds, planted 18\" apart", None, 0.0),
        ("3\" pea gravel, 6–10 mm · the surface stays dry", C_PEA, 0.9),
        ("21\" washed gravel, ½–¾\" (10–20 mm) · water flows through it", C_GRAVEL, 2.7),
        ("geotextile, protects the liner", "#f1efe9", 0.6),
        ("0.5 mm HDPE liner, one sheet", C_LINER, 0.6),
        ("geotextile, or 1\" of sand on the floor", "#f1efe9", 0.6),
        ("15 mm cement plaster with waterproofer", C_PLASTER, 0.6),
        ("3\" concrete base (1:3:6), 1\" lower at the outlet", C_PCC, 0.9),
        ("rammed earth", C_GROUND, 0.6),
    ]
    y = 8.7
    for i, (t, col, h) in enumerate(layers):
        if col is None:
            for k in range(6):
                xx = 0.35 + k * 0.4
                lx_.plot([xx, xx + 0.05], [y, y + 0.75], color="#6f8f4e", lw=0.9)
            lx_.text(3.0, y + 0.35, t, fontsize=7.0, color=GREEN, va="center")
            continue
        y -= h
        lx_.add_patch(Rectangle((0.2, y), 2.4, h, fc=col, ec=INK, lw=0.5))
        if col in (C_GRAVEL, C_PEA):
            rnd = random.Random(i)
            sz = 0.14 if col == C_GRAVEL else 0.07
            for _ in range(int(2.4 * h / (sz * sz) * 0.5)):
                lx_.add_patch(Ellipse((rnd.uniform(0.3, 2.5), rnd.uniform(y + sz, y + h - sz)), sz * 1.6, sz * 1.3,
                                      fc=col, ec="#6d675e", lw=0.3))
        if col == C_PEA:
            y_pea = y
        lx_.plot([2.65, 2.9], [y + h / 2, y + h / 2], color=GREY, lw=0.5)
        lx_.text(3.0, y + h / 2, t, fontsize=7.0, color=INK, va="center")
    lx_.plot([0.2, 2.6], [y_pea - 0.15, y_pea - 0.15], color=WATER, lw=1.2, ls=(0, (4, 2)))
    lx_.text(0.2, -0.25, "Inlet and outlet zones: 1½–3\" stone the full depth instead of the two gravels.", fontsize=6.8, color=GREY)

    # ---------------------------------------------- quantities
    qx = fig.add_axes([0.50, 0.06, 0.47, 0.28])
    qx.axis("off")
    qx.set_xlim(0, 10)
    qx.set_ylim(0, 10)
    rows = [
        ("What to order (about 10% extra on stone and gravel)", True),
        ("Washed gravel ½–¾\" (10–20 mm): 63 cu ft · ~1.8 m³", False),
        ("Pea gravel 6–10 mm: 9 cu ft · ~0.25 m³", False),
        ("Stone 1½–3\" (40–80 mm): 36 cu ft · ~1.0 m³", False),
        ("HDPE liner 0.5 mm: one sheet about 16 × 13 ft; geotextile x 2", False),
        ("Pipes: 4\" (110 mm) perforated, 12 ft (spreader + collector),", False),
        ("   two capped risers, a 4\" swivel elbow, pipe boots for the liner", False),
        ("Walls: 9\" stone in 1:4 cement, ~2 m³ incl. the chamber", False),
        ("Reeds: 16–20 rhizome cuttings (common reed, Phragmites)", False),
        ("", False),
        ("Why these levels", True),
        ("The biodigester outlet is 12\" above this terrace. That", False),
        ("gives the test chamber a 6\" drop for the jar and lets the", False),
        ("gravel sit 3\" above ground, so you dig only 2 ft.", False),
    ]
    for i, (t, b) in enumerate(rows):
        qx.text(0, 9.8 - i * 0.68, t, fontsize=7.6 if b else 7.1, fontweight="semibold" if b else "normal", color=ACCENT if b else INK)
    fig.savefig(OUTDIR + "09_reed_bed.png", dpi=200, facecolor="white")
    print("S-02 ok")


# ==================================================================================================  S-03
def sheet_plan():
    fig = sheet("Reed bed 9 × 6 ft — plan and how to build it",
                "Top view with the pipes, a section across the width, and the build in order",
                "S-03")
    fig.text(0.035, 0.03, "Dimensions inside the walls unless noted. Walls 9\" stone; outlet chamber 18 × 18\" inside.",
             fontsize=7, color=GREY)
    # ------------------------------------------- plan
    px = fig.add_axes([0.02, 0.42, 0.55, 0.47])
    px.set_xlim(-62, 170)
    px.set_ylim(-30, 104)
    px.set_aspect("equal")
    px.axis("off")
    R(px, -WALL, -WALL, L + 2 * WALL, Wd + 2 * WALL, fc=C_STONE, ec=INK, lw=0.8, zorder=2)
    R(px, 0, 0, L, Wd, fc=C_PEA, ec=INK, lw=0.8, zorder=3)
    for x0 in (0, L - ZONE):
        R(px, x0, 0, ZONE, Wd, fc=C_COARSE, ec="none", zorder=3)
        rnd = random.Random(int(x0) + 3)
        for _ in range(55):
            px.add_patch(Ellipse((rnd.uniform(x0 + 2, x0 + ZONE - 2), rnd.uniform(2, Wd - 2)), 3.4, 2.8, angle=rnd.uniform(0, 180),
                                 fc=C_COARSE, ec="#6d675e", lw=0.35, zorder=4))
    px.add_patch(Rectangle((0, 0), L, Wd, fc="none", ec=INK, lw=0.8, zorder=6))
    # outlet chamber
    R(px, L + WALL, Wd / 2 - 9 - WALL, 18 + WALL, 18 + 2 * WALL, fc=C_STONE, ec=INK, lw=0.8, zorder=2)
    R(px, L + WALL, Wd / 2 - 9, 18, 18, fc="white", ec=INK, lw=0.8, zorder=3)
    # inlet pipe + spreader with holes
    px.plot([-62, 9], [Wd / 2, Wd / 2], color=INK, lw=3.0, solid_capstyle="butt", zorder=7)
    px.add_patch(FancyArrowPatch((-60, Wd / 2), (-50, Wd / 2), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=8))
    px.plot([9, 9], [4, Wd - 4], color=INK, lw=3.0, solid_capstyle="butt", zorder=7)
    for y in range(8, int(Wd) - 4, 6):
        px.plot(9, y, marker="o", ms=1.6, color="white", zorder=8)
    px.add_patch(Circle((9, Wd - 4), 2.4, fc="white", ec=INK, lw=0.9, zorder=8))
    # collector + outlet
    px.plot([L - 9, L - 9], [4, Wd - 4], color=INK, lw=3.6, solid_capstyle="butt", zorder=7)
    for y in range(8, int(Wd) - 4, 6):
        px.plot(L - 9, y, marker="o", ms=1.8, color="white", zorder=8)
    px.add_patch(Circle((L - 9, Wd - 4), 2.6, fc="white", ec=INK, lw=0.9, zorder=8))
    px.plot([L - 9, L + WALL + 7], [Wd / 2, Wd / 2], color=INK, lw=3.6, solid_capstyle="butt", zorder=7)
    px.add_patch(Circle((L + WALL + 7, Wd / 2), 3.0, fc="white", ec=INK, lw=1.0, zorder=8))
    px.plot([L + WALL + 18, 170], [Wd / 2, Wd / 2], color=INK, lw=3.0, solid_capstyle="butt", zorder=7)
    px.add_patch(FancyArrowPatch((156, Wd / 2), (168, Wd / 2), arrowstyle="-|>", mutation_scale=9, color=INK, lw=0, zorder=8))
    # reeds: 4 x 4 at 18"
    for x in (27, 45, 63, 81):
        for y in (9, 27, 45, 63):
            px.add_patch(Circle((x, y), 2.6, fc="#86a862", ec=GREEN, lw=0.5, zorder=6))
    # flow arrows
    for y in (18, 54):
        px.add_patch(FancyArrowPatch((22, y), (86, y), arrowstyle="-|>", mutation_scale=10, color=WATER, lw=1.0, zorder=7, alpha=0.7))
    # section marker A-A
    px.plot([54, 54], [-14, Wd + 11], color=ACCENT, lw=0.9, ls=(0, (8, 3)), zorder=9)
    for yy, va in ((-16, "top"), (Wd + 12, "bottom")):
        px.text(54, yy, "A", fontsize=8, fontweight="semibold", color=ACCENT, ha="center", va=va, zorder=9)
    # dims
    hdim(px, 0, L, -22, "9'-0\"")
    hdim(px, 0, ZONE, -12, "1'-6\"", fs=6.2)
    hdim(px, L - ZONE, L, -12, "1'-6\"", fs=6.2)
    vdim(px, -16, 0, Wd, "6'-0\"")
    hdim(px, -WALL, L + WALL, Wd + 27, "10'-6\" outside", fs=6.6)
    # labels
    lab(px, (-40, Wd / 2), "inlet from J", (-60, Wd / 2 + 14), rel=(0.3, 0))
    lab(px, (9, Wd - 4), "spreader cleanout riser", (-60, Wd + 8), fs=6.8, rel=(1, 0.5))
    lab(px, (9, 20), "4\" spreader, holes\nevery 6\", facing down", (-60, 10), fs=6.8, rel=(1, 0.5))
    lab(px, (27, 9), "reeds 18\" apart (16 plants)", (-60, -6), fs=6.8, color=GREEN, rel=(1, 0.5))
    lab(px, (L - 9, 20), "4\" collector, holes\nevery 6\", on the floor", (126, 6), fs=6.8, rel=(0, 0.5))
    lab(px, (L - 9, Wd - 4), "collector cleanout riser", (126, 88), fs=6.8, rel=(0, 0.5))
    lab(px, (L + WALL + 7, Wd / 2 + 3), "swivel elbow in the\noutlet chamber", (132, 64), fs=6.8, rel=(0, 0.5))
    px.text(150, Wd / 2 - 4, "to soak\ntrench", fontsize=6.8, color=INK, va="top")
    px.text(-60, 104, "Plan (from above)", fontsize=8.2, fontweight="semibold", color=INK, va="top")

    # ------------------------------------------- section A-A across the width
    sx = fig.add_axes([0.60, 0.44, 0.38, 0.45])
    sx.set_xlim(-30, 102)
    sx.set_ylim(-36, 70)
    sx.set_aspect("equal")
    sx.axis("off")
    sx.add_patch(Polygon([(-30, 0), (102, 0), (102, -36), (-30, -36)], fc=C_GROUND, ec="none", zorder=1))
    zb = -20.5
    R(sx, -WALL, zb - 3, Wd + 2 * WALL, 3, fc=C_PCC, ec=INK, lw=0.7, zorder=2)
    R(sx, -WALL, zb, WALL, Z_KERB - zb, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
    R(sx, Wd, zb, WALL, Z_KERB - zb, fc=C_STONE, ec=INK, lw=0.7, zorder=2)
    R(sx, 0, zb, Wd, Z_KERB - zb, fc="white", ec="none", zorder=2)
    sx.plot([0.5, 0.5], [Z_KERB, zb + 0.5], color=C_PLASTER, lw=2.4, zorder=3)
    sx.plot([Wd - 0.5, Wd - 0.5], [Z_KERB, zb + 0.5], color=C_PLASTER, lw=2.4, zorder=3)
    sx.plot([1.2, 1.2, Wd - 1.2, Wd - 1.2], [Z_KERB, zb + 1.2, zb + 1.2, Z_KERB], color=C_LINER, lw=1.5, zorder=7)
    stones(sx, 1.6, Wd - 1.6, lambda x: zb + 1.6, Z_PEA, 1.0, C_GRAVEL, density=0.75, seed=11)
    stones(sx, 1.6, Wd - 1.6, lambda x: Z_PEA, Z_TOP, 0.55, C_PEA, density=0.6, seed=12)
    sx.plot([1.6, Wd - 1.6], [Z_WL, Z_WL], color=WATER, lw=1.2, ls=(0, (5, 2)), zorder=8)
    reeds(sx, 6, Wd - 6, Z_TOP, 4, seed=13)
    sx.plot([-30, -WALL], [0, 0], color=SOIL, lw=1.0, zorder=2)
    sx.plot([Wd + WALL, 102], [0, 0], color=SOIL, lw=1.0, zorder=2)
    hdim(sx, 0, Wd, -30, "6'-0\" inside")
    vdim(sx, -14, Z_TOP, zb, "2'-0\"")
    lab(sx, (Wd + 4, 7), "walls 9\" above\nground", (86, 34), fs=6.8, rel=(0.5, 0))
    lab(sx, (Wd - 6, Z_WL), "water level", (86, -14), fs=6.8, color=WATER, rel=(0.5, 1))
    lab(sx, (1.2, -14), "liner", (-28, -10), fs=6.8, rel=(1, 0.5))
    lab(sx, (-4.5, -6), "9\" stone\nwall", (-28, 18), fs=6.8, rel=(1, 0.5))
    sx.text(-28, 69, "Section A–A, across the width", fontsize=8.2, fontweight="semibold", color=INK, va="top")

    # ------------------------------------------- build steps
    bx = fig.add_axes([0.035, 0.05, 0.93, 0.34])
    bx.axis("off")
    bx.set_xlim(0, 10)
    bx.set_ylim(0, 10)
    bx.text(0, 9.9, "How to build it, in order", fontsize=8.6, fontweight="semibold", color=ACCENT, va="top")
    steps = [
        "Mark out 10'-6\" × 7'-6\" plus the outlet chamber. Take every level from the biodigester outlet (+12\") with a clear water-level tube.",
        "Dig to about 2'-0\" below the lower terrace (−24\"). Level and ram the bottom.",
        "Lay a 3\" concrete base (1:3:6), 1\" lower at the outlet end.",
        "Build 9\" stone walls in 1:4 cement to 9\" above ground, with the outlet chamber; set pipe sleeves for the inlet and outlet.",
        "Plaster inside, 15 mm, with waterproofing compound; round the inside corners. Cure for a week.",
        "Line it: geotextile, the HDPE liner in one sheet, geotextile again. Fold, don't cut, at the corners; seal the pipes with boots.",
        "Fill with water for 48 hours. The level should not drop, apart from evaporation.",
        "Lay the 4\" collector on the floor at the outlet end, through the wall to the swivel elbow; fit its capped riser.",
        "Fill, with two planks as temporary dividers: stone in both end zones, washed gravel between, then 3\" of pea gravel on top.",
        "Lay the 4\" spreader on the inlet stone, 2\" below the top, holes down; fit its riser and connect the inlet.",
        "Plant the reeds in spring, 18\" apart. Keep the water 1–2\" below the surface for six weeks, then lower the elbow to 4\".",
        "Run water through: nothing should show on the surface, and the outlet chamber should flow.",
    ]
    col_x = (0.0, 5.05)
    for i, t in enumerate(steps):
        c = 0 if i < 6 else 1
        r = i if i < 6 else i - 6
        y = 8.9 - r * 1.42
        bx.text(col_x[c], y, f"{i + 1}", fontsize=8.6, fontweight="semibold", color=ACCENT, va="top")
        words, lines, cur = t.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 78:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        bx.text(col_x[c] + 0.28, y, "\n".join(lines), fontsize=7.2, color=INK, va="top", linespacing=1.35)
    fig.savefig(OUTDIR + "10_reed_bed_plan.png", dpi=200, facecolor="white")
    print("S-03 ok")


if __name__ == "__main__":
    sheet_long()
    sheet_plan()
