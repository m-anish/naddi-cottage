"""2D architectural line drawings (plan + sections) for the dome-extension washroom."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse, Arc, Rectangle, FancyBboxPatch
from matplotlib.path import Path
from matplotlib import patheffects as pe
from geom import *

plt.rcParams.update({
    "font.family": "Inter",
    "font.size": 8.5,
    "axes.linewidth": 0,
})
INK = "#1d1d1b"
GREY = "#8a8780"
LIGHT = "#bdb9b1"
POCHE = "#4a4844"
ACCENT = "#b5552b"      # terracotta accent for annotations
WATER = "#3d7ea6"
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
import os
os.makedirs(OUT, exist_ok=True)

LW_CUT = 2.4
LW_MED = 1.2
LW_THIN = 0.6
LW_HAIR = 0.35


# ---------------------------------------------------------------- helpers
def new_sheet(w=11.0, h=8.5):
    fig = plt.figure(figsize=(w, h), dpi=200)
    fig.patch.set_facecolor("white")
    return fig


def title_block(fig, title, sub, no):
    fig.text(0.035, 0.955, title, fontsize=15, fontweight="semibold", color=INK, va="top")
    fig.text(0.035, 0.915, sub, fontsize=9, color=GREY, va="top")
    fig.text(0.965, 0.955, no, fontsize=15, fontweight="semibold", color=ACCENT, va="top", ha="right")
    fig.text(0.965, 0.915, "Naddi cottage · dome extension washroom", fontsize=8, color=GREY, va="top", ha="right")
    fig.add_artist(plt.Line2D([0.035, 0.965], [0.895, 0.895], color=INK, lw=0.8, transform=fig.transFigure))
    fig.text(0.035, 0.03, f"Indicative design drawings — dimensions in feet-inches; geometry measured off the Onshape frame, Oct 2026 (back base {fmt_ftin(BW)}, depth {fmt_ftin(D)}).",
             fontsize=7, color=GREY)


def dim(ax, p1, p2, off, text=None, side=1, fs=7.5, color=INK, ext=True, tpos=0.5):
    """aligned dimension line between p1 and p2 offset by `off` (perpendicular)."""
    p1, p2 = np.array(p1, float), np.array(p2, float)
    d = p2 - p1
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]]) * side
    a, b = p1 + n * off, p2 + n * off
    if ext:
        for p, q in ((p1, a), (p2, b)):
            ax.plot([p[0] + n[0] * 0.12, q[0] + n[0] * 0.15], [p[1] + n[1] * 0.12, q[1] + n[1] * 0.15],
                    color=color, lw=LW_HAIR)
    ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=LW_HAIR)
    # ticks
    t = (u + n) / np.linalg.norm(u + n) * 0.12
    for q in (a, b):
        ax.plot([q[0] - t[0], q[0] + t[0]], [q[1] - t[1], q[1] + t[1]], color=color, lw=0.9)
    if text is None:
        text = fmt_ftin(L)
    ang = math.degrees(math.atan2(u[1], u[0]))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    m = a + (b - a) * tpos + n * 0.17
    ax.text(m[0], m[1], text, fontsize=fs, rotation=ang, ha="center", va="center", color=color,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.6))


def label(ax, xy, txt, xytext, fs=7.5, color=INK, ha="left", weight="normal"):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=fs, color=color, ha=ha, va="center", fontweight=weight,
                arrowprops=dict(arrowstyle="-", lw=0.45, color=color, shrinkA=0, shrinkB=1.5),
                bbox=dict(facecolor="white", edgecolor="none", pad=0.4, alpha=0.9))


def tag(ax, xy, txt, fs=7.2, color=GREY, rot=0, ha="center", weight="normal", style="normal"):
    ax.text(xy[0], xy[1], txt, fontsize=fs, color=color, ha=ha, va="center", rotation=rot,
            fontweight=weight, style=style)


def local(origin, s_dir, t_dir, pts):
    o, s, t = np.array(origin), np.array(s_dir), np.array(t_dir)
    return np.array([o + s * a + t * b for a, b in pts])


def ellipse_pts(cs, ct, rs, rt, n=60, a0=0, a1=2 * math.pi):
    return [(cs + rs * math.cos(a), ct + rt * math.sin(a)) for a in np.linspace(a0, a1, n)]


# person silhouettes (feet), side view facing +x (face=+1) or -x (face=-1)
FIG_FC, FIG_EC = "#ddd8ce", "#9a958c"


def _xf(pts, x0, z0, f, s=1.0, lean=0.0, pivot=2.9):
    out = []
    ca, sa = math.cos(lean), math.sin(lean)
    for bx, bz in pts:
        if bz > pivot and lean:
            dx, dz = bx, bz - pivot
            bx, bz = dx * ca + dz * sa, -dx * sa + dz * ca + pivot
        out.append((x0 + f * bx * s, z0 + bz * s))
    return out


def person_side(ax, x0, z0=0.0, h=5.83, face=1, lean=0.0, color=FIG_FC, ec=FIG_EC):
    s = h / 5.83
    body = [(-0.25, 0), (0.55, 0), (0.2, 0.25), (0.22, 1.5), (0.26, 1.78), (0.22, 2.55), (0.34, 3.05), (0.36, 3.9),
            (0.2, 4.62), (0.12, 4.78), (-0.14, 4.82), (-0.3, 4.55), (-0.36, 3.95), (-0.24, 3.25), (-0.36, 2.78),
            (-0.26, 1.9), (-0.3, 1.05), (-0.2, 0.25)]
    arm = [(-0.08, 4.55), (0.1, 4.55), (0.08, 3.55), (0.24, 2.75), (0.14, 2.6), (-0.06, 3.5)]
    ax.add_patch(Polygon(_xf(body, x0, z0, face, s, lean), closed=True, fc=color, ec=ec, lw=0.6, zorder=5))
    ax.add_patch(Polygon(_xf(arm, x0, z0, face, s, lean), closed=True, fc="#d2ccc1", ec=ec, lw=0.5, zorder=6))
    hc = _xf([(0.1, 5.33)], x0, z0, face, s, lean)[0]
    ax.add_patch(Circle(hc, 0.36 * s, fc=color, ec=ec, lw=0.6, zorder=6))


def person_seated(ax, xback, zseat, face=1, color=FIG_FC, ec=FIG_EC):
    legs = [(0.0, 0.0), (1.38, 0.04), (1.56, 0.12), (1.66, -0.05), (1.7, -1.25), (1.98, -1.32), (1.98, -1.38),
            (1.46, -1.38), (1.4, -0.22), (0.25, -0.06)]
    torso = [(0.0, 0.0), (-0.03, 0.6), (0.02, 1.6), (0.14, 2.12), (0.44, 2.1), (0.62, 1.6), (0.64, 0.6), (0.78, 0.18)]
    arm = [(0.18, 1.95), (0.36, 1.95), (0.4, 1.15), (0.95, 0.55), (0.88, 0.42), (0.22, 1.05)]
    ax.add_patch(Polygon(_xf(legs, xback, zseat, face), closed=True, fc=color, ec=ec, lw=0.6, zorder=5))
    ax.add_patch(Polygon(_xf(torso, xback, zseat, face), closed=True, fc=color, ec=ec, lw=0.6, zorder=5))
    ax.add_patch(Polygon(_xf(arm, xback, zseat, face), closed=True, fc="#d2ccc1", ec=ec, lw=0.5, zorder=6))
    ax.add_patch(Circle(_xf([(0.32, 2.58)], xback, zseat, face)[0], 0.36, fc=color, ec=ec, lw=0.6, zorder=6))


# ------------------------------------------------------------- geometry helpers
def floor_poly():
    return [(-FW / 2, 0), (FW / 2, 0), (BW / 2, D), (-BW / 2, D)]


FRONT_LEDGE_Y = front_y(LEDGE_H)   # 0.737


def walk_poly():
    yl = FRONT_LEDGE_Y
    return [(-DOOR_HW, 0), (-DOOR_HW, yl), (-ledge_x(yl), yl), (-ledge_x(D), D), (ledge_x(D), D),
            (ledge_x(yl), yl), (DOOR_HW, yl), (DOOR_HW, 0)]


def headroom_portal(x, y):
    h = headroom(x, y)
    if abs(x) <= DOOR_HW and 0 <= y <= front_y(DOOR_H):
        h = max(h, min(DOOR_H, side_z(x, y)))
    return h


SIN_E, COS_E = math.sin(math.radians(EDGE_ANG)), math.cos(math.radians(EDGE_ANG))
# left edge: along (front->back) = (SIN_E, COS_E); inward normal = (COS_E, -SIN_E)
L_ALONG, L_IN = (SIN_E, COS_E), (COS_E, -SIN_E)
R_ALONG, R_IN = (-SIN_E, COS_E), (-COS_E, -SIN_E)


def ledge_pt(side, y):
    return (side * ledge_x(y), y)


# ======================================================================== PLAN A
def draw_plan_A(fname="01_plan_layoutA.png", p3=False):
    fig = new_sheet(11, 8.5)
    if p3:
        title_block(fig, "Palette 3 — Floor plan (low-cost build)", "Layout A unchanged · tiled brick partition + curtain instead of glass · back-to-wall WC · Kota stone", "A-05")
    else:
        title_block(fig, "Layout A — Floor plan (recommended)", "Dry zone at the front, shower at the back under the ridge · shading = clear standing headroom", "A-01")
    ax = fig.add_axes([0.015, 0.06, 0.66, 0.82])
    ax.set_aspect("equal")
    ax.set_xlim(-10.4, 8.9)
    ax.set_ylim(-3.3, 10.2)
    ax.axis("off")

    # headroom field
    xs = np.linspace(-6.05, 6.05, 500)
    ys = np.linspace(0, 7, 300)
    X, Y = np.meshgrid(xs, ys)
    Hh = np.vectorize(headroom_portal)(X, Y)
    inside = np.abs(X) <= half_floor(Y)
    Hm = np.where(inside, Hh, np.nan)
    cols = ["#e9e5de", "#f6efe3", "#e6eff5", "#ffffff"]
    ax.contourf(X, Y, Hm, levels=[0, 4.5, 6.0, 6.5, 30], colors=cols, zorder=0)
    cs = ax.contour(X, Y, Hm, levels=[4.5, 6.0, 6.5], colors=["#b9a98c", "#8fa9bd", "#5f87a6"],
                    linewidths=[0.6, 0.7, 0.8], linestyles=["--", "--", "-"], zorder=1)
    # hatch the very low zone
    ax.contourf(X, Y, Hm, levels=[0, 4.5], colors="none", hatches=["////"], zorder=1)
    for c in ax.collections[-1:]:
        try:
            c.set_edgecolor("#cfc8bb")
            c.set_linewidth(0)
        except Exception:
            pass

    # floor edge (base of sloping walls)
    ax.plot([-DOOR_HW, -FW / 2, -BW / 2, BW / 2, FW / 2, DOOR_HW], [0, 0, D, D, 0, 0], color=INK, lw=LW_CUT,
            zorder=4, solid_joinstyle="miter")
    ax.plot([-DOOR_HW, DOOR_HW], [0, 0], color=INK, lw=LW_HAIR, zorder=4)

    # ledges (service walls) - poche
    for sd in (-1, 1):
        yl = FRONT_LEDGE_Y
        pts = [(sd * FW / 2, 0), (sd * half_floor(D), D), (sd * ledge_x(D), D), (sd * ledge_x(yl), yl),
               (sd * DOOR_HW, yl), (sd * DOOR_HW, 0)]
        ax.add_patch(Polygon(pts, closed=True, fc="#cfcac1", ec=INK, lw=LW_MED, zorder=3, hatch="....",
                             joinstyle="miter"))
    # redraw ledge face lines heavier
    for sd in (-1, 1):
        ax.plot([sd * ledge_x(FRONT_LEDGE_Y), sd * ledge_x(D)], [FRONT_LEDGE_Y, D], color=INK, lw=1.6, zorder=4)
        ax.plot([sd * DOOR_HW, sd * ledge_x(FRONT_LEDGE_Y)], [FRONT_LEDGE_Y, FRONT_LEDGE_Y], color=INK, lw=1.6, zorder=4)

    # overhead lines: triangle edges, ridge, back wall projection
    ov = dict(color=GREY, lw=LW_THIN, ls=(0, (4, 3)), zorder=4)
    ax.plot([-FW / 2, 0, FW / 2], [0, APEX_F[1], 0], **ov)
    ax.plot([-BW / 2, 0, BW / 2], [D, APEX_B[1], D], **ov)
    ax.plot([0, 0], [APEX_F[1], APEX_B[1]], color=GREY, lw=0.8, ls=(0, (8, 2, 1, 2)), zorder=4)
    tag(ax, (-0.2, 4.6), "ridge above", fs=5.8, rot=90, color=GREY)
    # door portal soffit (overhead)
    py = front_y(DOOR_H)
    ax.plot([-DOOR_HW, -DOOR_HW, DOOR_HW, DOOR_HW], [0, py, py, 0], **ov)

    # door: outswing into main room
    ax.plot([-DOOR_HW, -DOOR_HW - 0.25], [0, 0], color=INK, lw=LW_CUT)
    ax.plot([DOOR_HW, DOOR_HW + 0.25], [0, 0], color=INK, lw=LW_CUT)
    ax.plot([DOOR_HW, DOOR_HW], [0, -2.5], color=INK, lw=1.4, zorder=5)
    ax.add_patch(Arc((DOOR_HW, 0), 5.0, 5.0, theta1=180, theta2=270, color=INK, lw=LW_HAIR, ls="--"))

    # WC (left)
    o = ledge_pt(-1, WC_Y)
    s, t = L_ALONG, L_IN
    if p3:   # concealed cistern built into the brick ledge, no frame
        frame = local(o, s, t, [(-0.55, -0.1), (0.55, -0.1), (0.55, -0.42), (-0.55, -0.42)])
    else:
        frame = local(o, s, t, [(-0.83, -0.05), (0.83, -0.05), (0.83, -0.5), (-0.83, -0.5)])
    ax.add_patch(Polygon(frame, closed=True, fc="none", ec=GREY, lw=LW_THIN, ls="--", zorder=5))
    pan = local(o, s, t, [(-0.6, 0)] + ellipse_pts(0, 0.75, 0.6, 1.02, 40, math.pi, 2 * math.pi)[::-1][::-1] + [(0.6, 0)])
    pan = local(o, s, t, [(-0.6, 0.0), (-0.6, 0.55)] + ellipse_pts(0, 0.62, 0.6, 1.15, 50, math.pi, 0)[1:-1][::-1][::-1] + [(0.6, 0.55), (0.6, 0.0)])
    bowl = local(o, s, t, ellipse_pts(0, 0.95, 0.42, 0.7, 50))
    seat = local(o, s, t, [(a, b) for a, b in ellipse_pts(0, 0.82, 0.6, 0.95, 60)])
    ax.add_patch(Polygon(seat, closed=True, fc="white", ec=INK, lw=LW_MED, zorder=6))
    ax.add_patch(Polygon(bowl, closed=True, fc="white", ec=INK, lw=LW_THIN, zorder=6))
    hf = local(o, s, t, [(1.05, 0.05)])[0]
    ax.add_patch(Circle(hf, 0.09, fc=INK, zorder=6))

    # Vanity (right)
    o = ledge_pt(1, VAN_Y)
    s, t = R_ALONG, R_IN
    tback = -(LEDGE_DX - LEDGE_H / A) * COS_E
    ctr = local(o, s, t, [(-1.25, tback), (1.25, tback), (1.25, 1.04), (-1.25, 1.04)])
    ax.add_patch(Polygon(ctr, closed=True, fc="#f2eee7", ec=INK, lw=LW_MED, zorder=6))
    basin = local(o, s, t, ellipse_pts(0, 0.42, 0.72, 0.5, 60))
    ax.add_patch(Polygon(basin, closed=True, fc="white", ec=INK, lw=LW_MED, zorder=7))
    tap = local(o, s, t, [(0, -0.2)])[0]
    ax.add_patch(Circle(tap, 0.07, fc=INK, zorder=7))
    # mirror on slope (overhead) z 4.6..6.3
    t0 = 4.6 / A * COS_E - LEDGE_DX * COS_E
    t1 = 6.3 / A * COS_E - LEDGE_DX * COS_E
    mir = local(o, s, t, [(-1.1, t0), (1.1, t0), (1.1, t1), (-1.1, t1)])
    ax.add_patch(Polygon(mir, closed=True, fc="none", ec=WATER, lw=0.8, ls=(0, (3, 2)), zorder=7))

    # towel radiator (or plain bar) on front ledge face (right)
    if p3:
        ax.add_patch(Rectangle((1.6, FRONT_LEDGE_Y), 1.5, 0.08, fc=INK, ec=INK, lw=LW_THIN, zorder=6))
    else:
        ax.add_patch(Rectangle((1.55, FRONT_LEDGE_Y), 1.6, 0.18, fc="white", ec=INK, lw=LW_THIN, zorder=6))

    gy = GLASS_Y
    lx = ledge_x(gy)
    if p3:
        # tiled brick partition: cut at 4'-0" it runs from the opening to the ledge face;
        # below the cut it continues over the ledge top to the slope
        y0, y1 = gy - PART_T / 2, gy + PART_T / 2
        for sd in (-1, 1):
            ax.add_patch(Polygon([(sd * OP_HW, y0), (sd * lx, y0), (sd * lx, y1), (sd * OP_HW, y1)], closed=True,
                                 fc=POCHE, ec=INK, lw=LW_MED, zorder=6))
            xs0, xs1 = slope_x_at(LEDGE_H, y0), slope_x_at(LEDGE_H, y1)
            ax.add_patch(Polygon([(sd * lx, y0), (sd * xs0, y0), (sd * xs1, y1), (sd * lx, y1)], closed=True,
                                 fc="#8d8981", ec=INK, lw=LW_THIN, zorder=6))
        # curtain on a rod, shower side
        cy = y1 + 0.13
        ax.plot([-OP_HW, OP_HW], [cy, cy], color=INK, lw=0.8, zorder=6)
        xx = np.linspace(-OP_HW + 0.05, OP_HW - 0.05, 120)
        ax.plot(xx, cy + 0.07 * np.sin(xx * 2 * np.pi / 0.3), color=WATER, lw=0.8, zorder=6)
    else:
        for sd in (-1, 1):
            ax.plot([sd * lx, sd * GLASS_DOOR_HW], [gy, gy], color=WATER, lw=2.0, zorder=6, solid_capstyle="butt")
        ax.plot([-GLASS_DOOR_HW, -GLASS_DOOR_HW + 0.0], [gy, gy - 2.0], color=WATER, lw=1.0, zorder=6)
        ax.add_patch(Arc((-GLASS_DOOR_HW, gy), 4.0, 4.0, theta1=270, theta2=360, color=WATER, lw=LW_HAIR, ls="--"))
    # shower floor tint
    sp = [(-ledge_x(gy), gy), (ledge_x(gy), gy), (ledge_x(D), D), (-ledge_x(D), D)]
    ax.add_patch(Polygon(sp, closed=True, fc=WATER, alpha=0.06, ec="none", zorder=2))
    if p3:   # square trap, four-way falls
        ax.add_patch(Rectangle((-0.25, 5.85), 0.5, 0.5, fc="white", ec=INK, lw=LW_THIN, hatch="xxxx", zorder=6))
        for a, b in (((-1.5, 6.1), (-0.32, 6.1)), ((1.5, 6.1), (0.32, 6.1)), ((0, 4.55), (0, 5.78)), ((0, 6.95), (0, 6.42))):
            ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=0.5, color=WATER, mutation_scale=7))
    else:
        # linear drain
        ax.add_patch(Rectangle((-1.35, 6.62), 2.7, 0.16, fc="white", ec=INK, lw=LW_THIN, hatch="||||", zorder=6))
        # falls
        for xx in (-0.9, 0.9):
            ax.annotate("", xy=(xx, 6.5), xytext=(xx, 4.4), arrowprops=dict(arrowstyle="-|>", lw=0.5, color=WATER, mutation_scale=7))
    # rain head (overhead)
    ax.add_patch(Circle(SHOWER_HEAD[:2], 0.42, fc="none", ec=WATER, lw=0.8, ls=(0, (2, 1.5)), zorder=7))
    ax.add_patch(Circle(SHOWER_HEAD[:2], 0.05, fc=WATER, zorder=7))
    # dry floor trap
    ax.add_patch(Rectangle((-0.75, 3.15), 0.35, 0.35, fc="white", ec=INK, lw=LW_THIN, hatch="xxxx", zorder=6))
    # window + mixer on back wall (overhead projection)
    wy0, wy1 = D + WIN_V[0] * S15, D + WIN_V[1] * S15
    ax.add_patch(Rectangle((-WIN_HW, wy0), 2 * WIN_HW, wy1 - wy0, fc="none", ec=GREY, lw=LW_THIN, ls="--", zorder=6))
    ax.add_patch(Circle((-0.95, back_y(3.4)), 0.11, fc="none", ec=INK, lw=0.7, zorder=6))
    # exhaust fan overhead on right slope
    ax.add_patch(Circle((0.75, 3.35), 0.3, fc="none", ec=GREY, lw=0.7, ls="--", zorder=6))
    tag(ax, (0.75, 3.35), "EF", fs=5.5, color=GREY)

    # labels
    tag(ax, (-3.6, -1.0), "MAIN DOME ROOM", fs=7.5, color=GREY, weight="semibold")
    tag(ax, (0.0, 1.2), "entry\nportal", fs=6.5, color=GREY)
    tag(ax, (0, 6.75 if p3 else 6.02), "SHOWER", fs=8, color=WATER, weight="semibold")
    tag(ax, (0.05, 2.72), "DRY ZONE", fs=8, color=INK, weight="semibold")
    tag(ax, (-0.95, 3.32), "floor trap", fs=6.0, color=INK, ha="right")
    LX = -10.25
    RX = 5.35
    if p3:
        label(ax, local(ledge_pt(-1, WC_Y), L_ALONG, L_IN, [(0, 1.3)])[0], "Back-to-wall floor WC;\nconcealed cistern built\ninto the brick ledge", (LX, 1.0), fs=6.8)
        label(ax, hf, "health faucet", (LX, 2.9), fs=6.8)
        label(ax, (-ledge_x(5.5) - 0.5, 5.5), "2'-9\" brick ledge, tiled:\npipes + cistern inside,\nKota stone top", (LX, 5.3), fs=6.8)
        label(ax, (-0.95, back_y(3.4)), "exposed mixer + hand\nshower on back wall", (LX, 8.4), fs=6.8)
        label(ax, local(ledge_pt(1, VAN_Y), R_ALONG, R_IN, [(0.4, 0.42)])[0], "Kota counter + shelf,\ntable-top basin", (RX, 3.3), fs=6.8)
        label(ax, local(ledge_pt(1, VAN_Y), R_ALONG, R_IN, [(-0.9, 0.95)])[0], "Plain mirror on the\nslope (4'-7\"–6'-4\")", (6.05, 1.2), fs=6.8, color=WATER)
        label(ax, (2.35, FRONT_LEDGE_Y + 0.04), "towel bar", (3.0, -1.2), fs=6.8)
        label(ax, (2.2, gy), "4\" tiled brick partition;\n2'-5\" A-shaped opening\nup to the slopes", (RX, 5.4), fs=6.8)
        label(ax, (0.6, gy + PART_T / 2 + 0.15), "curtain on a rod at 6'-4\"", (RX, 6.6), fs=6.8, color=WATER)
        label(ax, (0.2, 6.1), "square floor trap,\nfour-way falls", (RX, 7.6), fs=6.8)
        label(ax, (0.3, SHOWER_HEAD[1]), "8\" overhead shower\nfrom the ridge", (RX, 8.6), fs=6.8, color=WATER)
    else:
        label(ax, local(ledge_pt(-1, WC_Y), L_ALONG, L_IN, [(0, 1.3)])[0], "Wall-hung WC on low\nconcealed frame\n(79–98 cm high)", (LX, 1.0), fs=6.8)
        label(ax, hf, "health faucet", (LX, 2.9), fs=6.8)
        label(ax, (-ledge_x(5.5) - 0.5, 5.5), "2'-9\" service ledge:\npipes + cistern inside,\n6\" shelf on top,\nniche in shower", (LX, 5.3), fs=6.8)
        label(ax, (-0.95, back_y(3.4)), "mixer + hand shower\non back wall", (LX, 8.4), fs=6.8)
        label(ax, local(ledge_pt(1, VAN_Y), R_ALONG, R_IN, [(0.4, 0.42)])[0], "Vanity: stone top\non the ledge +\ncounter basin", (RX, 3.3), fs=6.8)
        label(ax, local(ledge_pt(1, VAN_Y), R_ALONG, R_IN, [(-0.9, 0.95)])[0], "Mirror on the slope\nabove (4'-7\"–6'-4\")", (6.05, 1.2), fs=6.8, color=WATER)
        label(ax, (2.35, FRONT_LEDGE_Y + 0.12), "heated towel rail", (3.0, -1.2), fs=6.8)
        label(ax, (1.8, gy), "8 mm toughened glass:\nraked fixed panels +\n2'-0\" centre door", (RX, 5.4), fs=6.8, color=WATER)
        label(ax, (1.0, 6.7), "linear drain", (RX, 7.0), fs=6.8)
        label(ax, (0.3, SHOWER_HEAD[1]), "rain shower\nfrom the ridge", (RX, 8.0), fs=6.8, color=WATER)
    label(ax, (0.3, wy1), "existing small\nwindow", (2.2, 9.7), fs=6.8, color=GREY)
    label(ax, (DOOR_HW, -1.6), "2'-6\" door, opens out", (2.0, -2.25), fs=6.8)
    label(ax, (0.95, 3.35), "exhaust fan high\non slope", (RX, 4.35), fs=6.8, color=GREY)

    # dimensions
    dim(ax, (-FW / 2, 0), (FW / 2, 0), 1.85, side=-1, text="12'-0\" (front triangle base)")
    dim(ax, (-BW / 2, D), (BW / 2, D), 1.6, side=1, text=f"{fmt_ftin(BW)} back base")
    dim(ax, (-FW / 2, 0), (-FW / 2, gy), 0.55, side=1, text="4'-0\"")
    dim(ax, (-FW / 2, gy), (-FW / 2, D), 0.55, side=1, text="3'-0\"")
    dim(ax, (-FW / 2, 0), (-FW / 2, D), 1.25, side=1, text=f"{fmt_ftin(D)} deep")
    # clear width between WC front and vanity front
    wcf = local(ledge_pt(-1, WC_Y), L_ALONG, L_IN, [(0, 1.77)])[0]
    vf = local(ledge_pt(1, VAN_Y), R_ALONG, R_IN, [(0, 1.04)])[0]
    yy = 2.15
    ax.annotate("", xy=(wcf[0], yy), xytext=(vf[0], yy), arrowprops=dict(arrowstyle="<->", lw=0.5, color=ACCENT, mutation_scale=6))
    tag(ax, ((wcf[0] + vf[0]) / 2 + 0.3, yy - 0.25), f"{fmt_ftin(vf[0]-wcf[0])} clear", fs=6.6, color=ACCENT)

    # scale bar
    for i in range(4):
        ax.add_patch(Rectangle((-10.0 + i, -3.0), 1, 0.13, fc=INK if i % 2 == 0 else "white", ec=INK, lw=0.4))
    for i in range(5):
        tag(ax, (-10.0 + i, -2.68), str(i) + (" ft" if i == 4 else ""), fs=6.0, color=INK)

    # legend panel
    lg = fig.add_axes([0.69, 0.06, 0.29, 0.82])
    lg.axis("off")
    lg.set_xlim(0, 10)
    lg.set_ylim(0, 30)
    yy = 28.5
    lg.text(0, yy, "Clear standing headroom", fontsize=9, fontweight="semibold", color=INK)
    rows = [("#ffffff", "6'-6\" and above — walk & shower upright", "-", "#5f87a6"),
            ("#e6eff5", "6'-0\" to 6'-6\" — upright for most people", "--", "#8fa9bd"),
            ("#f6efe3", "4'-6\" to 6'-0\" — sitting, bending, reaching", "--", "#b9a98c"),
            ("#e9e5de", "below 4'-6\" — ledges, storage, services", None, None)]
    for i, (c, t, ls, lc) in enumerate(rows):
        y0 = yy - 1.6 - i * 1.25
        lg.add_patch(Rectangle((0, y0 - 0.38), 0.9, 0.76, fc=c, ec="#9c978d", lw=0.5, hatch="////" if i == 3 else None))
        lg.text(1.2, y0, t, fontsize=7.2, va="center", color=INK)
    y = yy - 7.4
    lg.text(0, y, "Why this layout", fontsize=9, fontweight="semibold", color=INK)
    notes = [
        f"The space is a tapering 'tent': floor {fmt_ftin(FW)} wide at the front,",
        f"{fmt_ftin(BW)} at the back, both side slopes at ~{math.degrees(math.atan(A)):.0f}°.",
        "Only a central strip has full standing height, so standing",
        "tasks (entry, basin, shower) sit on the centre line and the",
        "WC / vanity tuck against the slopes where you sit or bend.",
        "",
        "• A 2'-9\" vertical service ledge along both slopes squares",
        "  off the unusable low corner, hides all pipes and the",
        "  cistern, and doubles as shelf + vanity top.",
        "• The front wall leans in over the floor, so the door sits",
        "  in a small vertical 'portal' box (6'-8\" soffit) instead",
        "  of in the leaning plane.",
        f"• Shower is at the back under the ridge ({fmt_ftin(SHOWER_HEAD[2])} head,",
        f"  ridge {fmt_ftin(side_z(0, SHOWER_HEAD[1]))} above you); the dry",
        ("  zone stays dry behind a tiled partition + curtain." if p3 else "  zone stays dry behind a raked glass screen."),
        f"• Steam rises to the front apex ({fmt_ftin(APEX_F[2])}): exhaust fan high",
        "  on the slope near the ridge, ducted outside.",
        "",
        f"Floor: {(FW + BW) / 2 * D:.1f} sq ft gross · ~{walkable_area(6.0):.0f} sq ft over 6'-0\"",
    ]
    if p3:
        notes = notes[:-1] + [
            "• Palette 3 swaps cost, not durability: the partition's",
            "  opening rises to meet the slopes, so a straight rod",
            "  and curtain close it; ledges and partition are brick",
            "  on the concrete slab, finished in 6\"×6\" ceramic.",
            "",
            notes[-1]]
    for i, n in enumerate(notes):
        lg.text(0, y - 1.0 - i * 0.92, n, fontsize=7.0, color=INK if not n.startswith("Floor") else ACCENT,
                fontweight="semibold" if n.startswith("Floor") else "normal")
    fig.savefig(f"{OUT}/{fname}", dpi=200, facecolor="white")
    plt.close(fig)


# ===================================================================== SECTION A-A (long)
def draw_long_section(fname="02_section_long.png"):
    fig = new_sheet(11, 8.5)
    title_block(fig, "Section A–A — through the centre line", "Looking toward the WC side · shows the leaning front & back walls and the ridge falling toward the back", "A-02")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.82])
    ax.set_aspect("equal")
    ax.set_xlim(-4.3, 13.2)
    ax.set_ylim(-3.6, 11.4)
    ax.axis("off")
    T = 0.42  # wall/roof assembly thickness

    # ground + fill
    gl = -1.9
    ax.add_patch(Rectangle((-0.3, gl), D + 0.6, -gl - 0.42, fc="#efebe4", ec="none", hatch="oo", zorder=0))
    ax.add_patch(Rectangle((-0.3, -0.42), D + 0.6, 0.34, fc="#dcd7cf", ec=INK, lw=LW_THIN, hatch="..", zorder=1))
    ax.add_patch(Rectangle((-0.3, -0.08), D + 0.6, 0.08, fc=POCHE, ec=INK, lw=LW_THIN, zorder=2))
    ax.plot([-4.3, 13.2], [gl, gl], color=INK, lw=LW_THIN)
    # main room floor
    ax.add_patch(Rectangle((-4.3, -0.3), 4.0, 0.3, fc="#cfcac1", ec=INK, lw=LW_MED))
    # perimeter plinth at back
    ax.add_patch(Rectangle((D - 0.1, gl), 0.75, -gl, fc="#b9b3a9", ec=INK, lw=LW_MED, hatch="xx"))

    # cut roof/ridge: offset outward
    def thick_line(p, q, t, fc=POCHE, outward=(0, 1)):
        p, q = np.array(p), np.array(q)
        u = (q - p) / np.linalg.norm(q - p)
        n = np.array([-u[1], u[0]])
        if np.dot(n, outward) < 0:
            n = -n
        poly = [p, q, q + n * t, p + n * t]
        ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=INK, lw=LW_MED, zorder=3))

    Fy, Fz = APEX_F[1], APEX_F[2]
    By, Bz = APEX_B[1], APEX_B[2]
    # front wall above the door portal
    pz = DOOR_H
    py = front_y(pz)
    thick_line((py, pz), (Fy, Fz), T, outward=(-1, 0.3))
    thick_line((Fy, Fz), (By, Bz), T, outward=(0.3, 1))
    # back wall with window gap
    w0 = (D + WIN_V[0] * S15, WIN_V[0] * C15)
    w1 = (D + WIN_V[1] * S15, WIN_V[1] * C15)
    thick_line((D, 0), w0, T, outward=(1, -0.2))
    thick_line(w1, (By, Bz), T, outward=(1, -0.2))
    # window frame
    ax.plot([w0[0], w1[0]], [w0[1], w1[1]], color=WATER, lw=1.6, zorder=4)
    ax.plot([w0[0] + 0.15, w1[0] + 0.15], [w0[1] - 0.04, w1[1] - 0.04], color=WATER, lw=0.8, zorder=4)
    # door portal soffit + door
    ax.add_patch(Rectangle((0, pz), py, 0.28, fc=POCHE, ec=INK, lw=LW_MED, zorder=3))
    ax.add_patch(Rectangle((-0.15, 0), 0.15, pz, fc="white", ec=INK, lw=LW_MED, zorder=3))
    tag(ax, (-0.5, 3.3), "door (opens out)", fs=6.6, rot=90, color=GREY)

    # beyond: left slope elements (thin)
    # ledge top line beyond
    ax.plot([FRONT_LEDGE_Y, D], [LEDGE_H, LEDGE_H], color=GREY, lw=LW_THIN)
    ax.plot([0, FRONT_LEDGE_Y], [0, LEDGE_H], color=GREY, lw=LW_THIN, ls="--")
    # floor edge beyond is the floor; left slope meets front wall (projection = front line) - draw front plane line below portal dashed
    ax.plot([0, py], [0, pz], color=GREY, lw=LW_THIN, ls=(0, (4, 3)))
    tag(ax, (0.75, 4.4), f"front wall plane\n({math.degrees(LEAN):.0f}° lean)", fs=6.2, rot=75, color=GREY)
    # WC beyond (side elevation)
    wy = WC_Y
    ax.add_patch(FancyBboxPatch((wy - 0.62, 1.0), 1.24, 0.33, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="white", ec=GREY, lw=LW_THIN, zorder=2))
    ax.add_patch(Polygon([(wy - 0.5, 1.0), (wy + 0.5, 1.0), (wy + 0.35, 0.55), (wy - 0.35, 0.55)], closed=True, fc="white", ec=GREY, lw=LW_THIN, zorder=2))
    tag(ax, (wy - 0.2, 0.3), "WC beyond", fs=6.0, color=GREY)

    # glass screen (cut through door)
    ax.add_patch(Rectangle((GLASS_Y - 0.05, 0.05), 0.1, GLASS_TOP - 0.05, fc="#d5e6f0", ec=WATER, lw=0.9, zorder=4))
    # rain shower
    sy, sz = SHOWER_HEAD[1], SHOWER_HEAD[2]
    rz = side_z(0, sy)
    ax.plot([sy, sy], [sz, rz], color=INK, lw=1.0)
    ax.add_patch(Rectangle((sy - 0.42, sz - 0.08), 0.84, 0.1, fc=INK, ec=INK))
    for k in np.linspace(-0.35, 0.35, 6):
        ax.plot([sy + k, sy + k * 1.25], [sz - 0.15, sz - 1.0], color=WATER, lw=0.4, ls=(0, (1, 2)))
    # mixer on back wall
    mz = 3.25
    ax.add_patch(Circle((back_y(mz) - 0.12, mz), 0.13, fc="white", ec=INK, lw=0.8, zorder=5))
    # linear drain
    ax.add_patch(Rectangle((6.62, -0.12), 0.18, 0.12, fc="white", ec=INK, lw=LW_THIN, zorder=5))
    # exhaust fan (beyond, right slope near ridge) shown dashed
    ax.add_patch(Circle((3.35, 8.0), 0.3, fc="none", ec=GREY, lw=0.7, ls="--"))
    tag(ax, (3.35, 8.0), "EF", fs=5.5, color=GREY)
    # ridge LED
    ax.plot([Fy + 0.3, By - 0.3], [Fz - 0.22 - 0.711 * 0.3, Bz - 0.22 + 0.711 * 0.3], color="#e3b04b", lw=1.6, alpha=0.9)

    # people
    person_side(ax, sy - 0.05, 0, h=5.83, face=1)
    person_side(ax, 3.05, 0, h=5.6, face=-1)

    # headroom line at 6'-6" (hair) for reference
    ax.plot([0.1, 8.3], [6.5, 6.5], color="#5f87a6", lw=0.5, ls=(0, (1, 2)), zorder=1)
    tag(ax, (8.75, 6.5), "6'-6\"", fs=6.2, color="#5f87a6")

    # dims
    def vdim(x, z0, z1, txt=None, side=1):
        dim(ax, (x, z0), (x, z1), 0.0, text=txt, side=side, ext=False)
    vdim(-2.2, 0, Fz, f"{fmt_ftin(Fz)} front apex")
    vdim(10.4, 0, Bz, f"{fmt_ftin(Bz)} back apex")
    vdim(-1.2, 0, pz, "6'-8\"")
    vdim(sy + 0.75, 0, sz, "7'-0\"")
    vdim(sy + 1.6, 0, rz, fmt_ftin(rz))
    vdim(11.35, w0[1], w1[1], "win.")
    dim(ax, (0, -3.15), (D, -3.15), 0.0, text=f"{fmt_ftin(D)} floor", ext=False)
    dim(ax, (0, -2.45), (GLASS_Y, -2.45), 0.0, text=f"{fmt_ftin(GLASS_Y)} dry zone", ext=False)
    dim(ax, (GLASS_Y, -2.45), (D, -2.45), 0.0, text=f"{fmt_ftin(D - GLASS_Y)} shower", ext=False)
    dim(ax, (0, pz + 0.75), (py, pz + 0.75), 0.0, text=fmt_ftin(py), ext=False, fs=6.6)

    # labels
    label(ax, (Fy + 1.2, Fz - 0.711 * 1.2 + 0.2), "Roof/side assembly: ext. fibre-cement +\niron purlins + 50 mm insulation + vapour\ncontrol + interior lining", (6.4, 10.7), fs=6.8)
    label(ax, (5.6, -0.2), "Floor build-up: slate / anti-skid tile on adhesive ·\ncementitious waterproofing · 100 mm PCC laid to\nfalls · 200 µm DPM · compacted rubble fill", (8.7, -0.75), fs=6.6)
    label(ax, (D + 0.35, -1.3), "perimeter plinth wall\n(close the open sides)", (8.7, -2.3), fs=6.6)
    label(ax, (w1[0] + 0.1, (w0[1] + w1[1]) / 2), "existing window\n(frosted, openable)", (10.9, 3.0), fs=6.6, color=WATER)
    label(ax, (back_y(mz) - 0.12, mz), "concealed mixer (beside window)", (8.7, 1.3), fs=6.6)
    label(ax, (sy, sz), "rain shower 7'-0\"", (5.95, 9.35), fs=6.6, color=WATER)
    label(ax, (GLASS_Y, 5.5), "glass door\n6'-6\"", (2.9, 7.25), fs=6.6, color=WATER)
    tag(ax, (-2.8, 1.0), "MAIN ROOM", fs=7.5, color=GREY, weight="semibold")
    tag(ax, (1.5, 9.4), "", fs=7)
    label(ax, (Fy + 4.4, Fz - 0.711 * 4.4 - 0.22), "warm LED strip along ridge", (9.3, 7.6), fs=6.6)
    fig.savefig(f"{OUT}/{fname}", dpi=200, facecolor="white")
    plt.close(fig)


# ===================================================================== SECTION B-B (cross)
def draw_cross_section(fname="03_section_cross.png"):
    fig = new_sheet(11, 8.5)
    title_block(fig, "Section B–B — across the dry zone", "Cut 2'-3\" behind the front base line, looking toward the shower · WC left, vanity right", "A-03")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.82])
    ax.set_aspect("equal")
    ax.set_xlim(-8.6, 8.6)
    ax.set_ylim(-3.3, 10.6)
    ax.axis("off")
    yc = 2.3
    hf = half_floor(yc)
    T = 0.42
    ztop = yc / T15  # front wall cuts the section here
    xt = slope_x_at(ztop, yc)

    # beyond: back wall triangle, glass screen, ridge
    ax.add_patch(Polygon([(-BW / 2, 0), (BW / 2, 0), (0, APEX_B[2])], closed=True, fc="#f5f2ed", ec=GREY, lw=LW_THIN, zorder=0))
    ax.add_patch(Rectangle((-WIN_HW, WIN_V[0] * C15), 2 * WIN_HW, (WIN_V[1] - WIN_V[0]) * C15, fc="#dbe9f2", ec=GREY, lw=LW_THIN, zorder=1))
    gy = GLASS_Y
    lx = ledge_x(gy)
    sx = slope_x_at(GLASS_TOP, gy)
    sx2 = slope_x_at(LEDGE_H, gy)
    for sd in (-1, 1):
        pts = [(sd * lx, 0), (sd * GLASS_DOOR_HW, 0), (sd * GLASS_DOOR_HW, GLASS_TOP), (sd * sx, GLASS_TOP),
               (sd * sx2, LEDGE_H), (sd * lx, LEDGE_H)]
        ax.add_patch(Polygon(pts, closed=True, fc="#d5e6f0", ec=WATER, lw=0.6, alpha=0.75, zorder=1))
    ax.add_patch(Rectangle((-GLASS_DOOR_HW, 0.05), 2 * GLASS_DOOR_HW, GLASS_TOP - 0.05, fc="#e3eef5", ec=WATER, lw=0.6, alpha=0.8, zorder=1))
    ax.plot([0, 0], [APEX_B[2], ztop], color=GREY, lw=LW_THIN, ls=(0, (8, 2, 1, 2)))
    # shower head beyond
    ax.add_patch(Rectangle((-0.42, SHOWER_HEAD[2] - 0.08), 0.84, 0.1, fc=GREY, ec=GREY, zorder=2))
    ax.plot([0, 0], [SHOWER_HEAD[2], side_z(0, SHOWER_HEAD[1])], color=GREY, lw=0.8)

    # floor build-up
    ax.add_patch(Rectangle((-hf, -1.6), 2 * hf, 1.18, fc="#efebe4", ec="none", hatch="oo", zorder=0))
    ax.add_patch(Rectangle((-hf, -0.42), 2 * hf, 0.34, fc="#dcd7cf", ec=INK, lw=LW_THIN, hatch="..", zorder=1))
    ax.add_patch(Rectangle((-hf, -0.08), 2 * hf, 0.08, fc=POCHE, ec=INK, lw=LW_THIN, zorder=2))

    # cut slopes (thick)
    for sd in (-1, 1):
        p = np.array([sd * hf, 0.0])
        q = np.array([sd * xt, ztop])
        u = (q - p) / np.linalg.norm(q - p)
        n = np.array([-u[1], u[0]])
        if n[0] * sd < 0:
            n = -n
        ax.add_patch(Polygon([p, q, q + n * T, p + n * T], closed=True, fc=POCHE, ec=INK, lw=LW_MED, zorder=4))
    ax.add_patch(Rectangle((-xt - 0.2, ztop), 2 * xt + 0.4, T * 0.8, fc=POCHE, ec=INK, lw=LW_MED, zorder=4))
    tag(ax, (0, ztop + 0.75), "front wall leans over this point (cut)", fs=6.3, color=GREY)

    # ledges (cut)
    for sd in (-1, 1):
        lxx = ledge_x(yc)
        sxl = slope_x_at(LEDGE_H, yc)
        pts = [(sd * hf, 0), (sd * lxx, 0), (sd * lxx, LEDGE_H), (sd * sxl, LEDGE_H)]
        ax.add_patch(Polygon(pts, closed=True, fc="#e7e3dc", ec=INK, lw=LW_CUT, zorder=4, hatch="////"))
    # WC (left) frame inside ledge (dashed) + pan
    lxx = ledge_x(yc)
    ax.add_patch(Rectangle((-lxx - 0.55, 0.05), 0.45, 2.6, fc="none", ec=GREY, lw=LW_THIN, ls="--", zorder=5))
    tag(ax, (-lxx - 0.33, 1.3), "frame", fs=5.5, rot=90, color=GREY)
    pan = [(-lxx, 0.72), (-lxx, 1.33), (-lxx + 1.72, 1.33), (-lxx + 1.72, 1.2), (-lxx + 1.25, 0.72)]
    ax.add_patch(Polygon(pan, closed=True, fc="white", ec=INK, lw=LW_MED, zorder=6))
    person_seated(ax, -lxx + 0.28, 1.38, face=1)
    # head clearance check (average adult, head top ~4'-4")
    hx = -lxx + 0.6
    htop = 1.38 + 2.58 + 0.36
    ax.annotate("", xy=(hx, htop + 0.02), xytext=(hx, side_z(hx, yc) - 0.03), arrowprops=dict(arrowstyle="<->", lw=0.5, color=ACCENT, mutation_scale=6))
    tag(ax, (hx + 0.62, htop + 0.38), f"≈{round((side_z(hx, yc) - htop) * 12)}\" clear", fs=6.2, color=ACCENT)

    # vanity (right)
    sxl = slope_x_at(LEDGE_H, yc)
    cf = lxx - 1.04 / COS_E * COS_E  # projected front
    cf = lxx - 1.0
    ax.add_patch(Rectangle((cf, LEDGE_H - 0.1), sxl - cf, 0.12, fc="#bfb7aa", ec=INK, lw=LW_MED, zorder=6))
    ax.add_patch(Rectangle((cf + 0.02, 0.5), lxx - cf - 0.02, LEDGE_H - 0.62, fc="#f2eee7", ec=INK, lw=LW_THIN, zorder=5))
    bc = lxx - 0.42
    ax.add_patch(Polygon([(bc - 0.7, LEDGE_H + 0.02), (bc + 0.7, LEDGE_H + 0.02), (bc + 0.62, LEDGE_H + 0.42), (bc - 0.62, LEDGE_H + 0.42)],
                         closed=True, fc="white", ec=INK, lw=LW_MED, zorder=7))
    ax.plot([bc + 0.62, bc + 0.62, bc + 0.2], [LEDGE_H + 0.02, LEDGE_H + 0.85, LEDGE_H + 0.85], color=INK, lw=1.4, zorder=7, solid_capstyle="round")
    # mirror on slope
    m0 = (slope_x_at(4.6, yc), 4.6)
    m1 = (slope_x_at(6.3, yc), 6.3)
    ax.plot([m0[0] - 0.06, m1[0] - 0.06], [m0[1], m1[1]], color=WATER, lw=3.0, zorder=7, solid_capstyle="butt")
    person_side(ax, 1.2, 0, h=5.75, face=1, lean=0.12)
    # sight line
    ax.plot([1.6, (m0[0] + m1[0]) / 2 - 0.06], [5.35, 5.45], color=WATER, lw=0.5, ls=(0, (2, 2)))

    # dims
    dim(ax, (-hf, 0), (hf, 0), -2.75, side=1, text=f"{fmt_ftin(2*hf)} floor width at this cut")
    dim(ax, (-lxx + 1.72, 0), (cf, 0), -2.05, side=1, text=f"{fmt_ftin(cf - (-lxx + 1.72))} between WC and vanity")
    dim(ax, (-lxx, 0), (-lxx, LEDGE_H), 0.0, text="2'-9\"", ext=False)
    dim(ax, (7.2, 0), (7.2, 4.6), 0.0, text="4'-7\"", ext=False)
    dim(ax, (7.9, 0), (7.9, 6.3), 0.0, text="6'-4\"", ext=False)
    ax.plot([m0[0] + 0.1, 7.3], [4.6, 4.6], color=GREY, lw=LW_HAIR)
    ax.plot([m1[0] + 0.1, 8.0], [6.3, 6.3], color=GREY, lw=LW_HAIR)

    label(ax, ((m0[0] + m1[0]) / 2, 5.45), "mirror fixed to the slope — it tilts\n~25° downward, like an accessible\ntilt-mirror; a vertical mirror would\nhang into your head when washing", (3.8, 8.9), fs=6.6, color=WATER)
    label(ax, (-hf + 0.9, 1.4), f"insulated, lined\nslope ({math.degrees(math.atan(A)):.0f}°)", (-8.4, 3.6), fs=6.6)
    label(ax, (-lxx - 0.3, LEDGE_H), "ledge shelf", (-8.4, 2.3), fs=6.6)
    label(ax, (-1.6, 5.4), "raked glass screen,\nshower beyond", (-8.4, 6.3), fs=6.4, color=WATER)
    label(ax, (0, APEX_B[2] - 0.4), "back wall + window beyond", (-6.6, 7.6), fs=6.4, color=GREY)
    fig.savefig(f"{OUT}/{fname}", dpi=200, facecolor="white")
    plt.close(fig)


# ===================================================================== PLAN B (alternative)
def draw_plan_B(fname="04_plan_layoutB.png"):
    fig = new_sheet(11, 8.5)
    title_block(fig, "Layout B — Floor plan (alternative)", "WC at the back under the window, shower along the left slope, vanity on the right", "A-04")
    ax = fig.add_axes([0.015, 0.06, 0.66, 0.82])
    ax.set_aspect("equal")
    ax.set_xlim(-10.4, 8.9)
    ax.set_ylim(-3.3, 10.2)
    ax.axis("off")
    xs = np.linspace(-6.05, 6.05, 500)
    ys = np.linspace(0, 7, 300)
    X, Y = np.meshgrid(xs, ys)
    Hh = np.vectorize(headroom_portal)(X, Y)
    inside = np.abs(X) <= half_floor(Y)
    Hm = np.where(inside, Hh, np.nan)
    cols = ["#e9e5de", "#f6efe3", "#e6eff5", "#ffffff"]
    ax.contourf(X, Y, Hm, levels=[0, 4.5, 6.0, 6.5, 30], colors=cols, zorder=0)
    ax.contour(X, Y, Hm, levels=[4.5, 6.0, 6.5], colors=["#b9a98c", "#8fa9bd", "#5f87a6"],
               linewidths=[0.6, 0.7, 0.8], linestyles=["--", "--", "-"], zorder=1)
    ax.plot([-DOOR_HW, -FW / 2, -BW / 2, BW / 2, FW / 2, DOOR_HW], [0, 0, D, D, 0, 0], color=INK, lw=LW_CUT, zorder=4)
    for sd in (-1, 1):
        yl = FRONT_LEDGE_Y
        pts = [(sd * FW / 2, 0), (sd * half_floor(D), D), (sd * ledge_x(D), D), (sd * ledge_x(yl), yl),
               (sd * DOOR_HW, yl), (sd * DOOR_HW, 0)]
        ax.add_patch(Polygon(pts, closed=True, fc="#cfcac1", ec=INK, lw=LW_MED, zorder=3, hatch="...."))
    ov = dict(color=GREY, lw=LW_THIN, ls=(0, (4, 3)), zorder=4)
    ax.plot([-FW / 2, 0, FW / 2], [0, APEX_F[1], 0], **ov)
    ax.plot([-BW / 2, 0, BW / 2], [D, APEX_B[1], D], **ov)
    ax.plot([0, 0], [APEX_F[1], APEX_B[1]], color=GREY, lw=0.8, ls=(0, (8, 2, 1, 2)))
    ax.plot([DOOR_HW, DOOR_HW], [0, -2.5], color=INK, lw=1.4)
    ax.add_patch(Arc((DOOR_HW, 0), 5.0, 5.0, theta1=180, theta2=270, color=INK, lw=LW_HAIR, ls="--"))
    # WC at back centre, against back ledge (back wall leans out above)
    ax.add_patch(Rectangle((-1.0, D - 0.55), 2.0, 0.55, fc="#cfcac1", ec=INK, lw=LW_MED, hatch="....", zorder=5))
    ax.add_patch(Ellipse((0, D - 0.55 - 0.85), 1.2, 1.9, fc="white", ec=INK, lw=LW_MED, zorder=6))
    ax.add_patch(Ellipse((0, D - 0.55 - 0.95), 0.84, 1.3, fc="white", ec=INK, lw=LW_THIN, zorder=6))
    # shower on left: glass along x=-0.25 from y=1.6 to 4.6, door in middle
    gx = -0.25
    ax.plot([gx, gx], [1.6, 2.4], color=WATER, lw=2.0)
    ax.plot([gx, gx], [4.0, 4.6], color=WATER, lw=2.0)
    ax.plot([gx, -ledge_x(4.6)], [4.6, 4.6], color=WATER, lw=2.0)
    ax.plot([gx, -ledge_x(1.6)], [1.6, 1.6], color=WATER, lw=2.0)
    ax.plot([gx, gx + 1.6], [2.4, 2.4], color=WATER, lw=1.0)
    ax.add_patch(Arc((gx, 2.4), 3.2, 3.2, theta1=0, theta2=90, color=WATER, lw=LW_HAIR, ls="--"))
    sp = [(gx, 1.6), (gx, 4.6), (-ledge_x(4.6), 4.6), (-ledge_x(1.6), 1.6)]
    ax.add_patch(Polygon(sp, closed=True, fc=WATER, alpha=0.07, ec="none"))
    ax.add_patch(Circle((-1.25, 3.1), 0.42, fc="none", ec=WATER, lw=0.8, ls=(0, (2, 1.5))))
    tag(ax, (-1.6, 3.95), "SHOWER", fs=7.5, color=WATER, weight="semibold")
    # vanity right
    o = ledge_pt(1, 2.6)
    s, t = R_ALONG, R_IN
    tback = -(LEDGE_DX - LEDGE_H / A) * COS_E
    ctr = local(o, s, t, [(-1.25, tback), (1.25, tback), (1.25, 1.04), (-1.25, 1.04)])
    ax.add_patch(Polygon(ctr, closed=True, fc="#f2eee7", ec=INK, lw=LW_MED, zorder=6))
    ax.add_patch(Polygon(local(o, s, t, ellipse_pts(0, 0.42, 0.72, 0.5, 60)), closed=True, fc="white", ec=INK, lw=LW_MED, zorder=7))
    tag(ax, (0, -0.65), "MAIN DOME ROOM", fs=7.5, color=GREY, weight="semibold")
    label(ax, (0, 5.6), "WC on axis, window above", (2.4, 8.6), fs=6.8)
    label(ax, local(o, s, t, [(0, 0.5)])[0], "vanity + mirror\non the slope", (5.35, 4.2), fs=6.8)
    label(ax, (gx, 4.3), "glass screen + door", (-10.2, 6.2), fs=6.8, color=WATER)
    tag(ax, (-10.2, -2.6), "Shading: clear standing headroom, as on A-01", fs=6.6, color=GREY, ha="left")
    lg = fig.add_axes([0.69, 0.06, 0.29, 0.82])
    lg.axis("off")
    lg.set_xlim(0, 10)
    lg.set_ylim(0, 30)
    lines = [
        ("Trade-offs vs Layout A", True),
        ("+ Uses the lowest part of the room (back) for the", False),
        ("  seated activity, leaving the best headroom for the", False),
        ("  shower (7'+ where you stand).", False),
        ("+ Window ventilates the WC directly.", False),
        ("– The WC is the first thing you see on axis from the", False),
        ("  door (and from the main room when the door is open).", False),
        ("– The wet zone sits in the middle; the path to the WC", False),
        ("  runs alongside the shower glass, so the floor near", False),
        ("  the vanity gets wet more often.", False),
        ("– Plumbing runs are longer (WC soil pipe exits at the", False),
        ("  back, shower drain in the middle).", False),
        ("", False),
        ("Verdict: workable, slightly better shower headroom,", True),
        ("but Layout A is calmer, drier and easier to build.", True),
    ]
    for i, (n, b) in enumerate(lines):
        lg.text(0, 28.5 - i * 1.0, n, fontsize=7.4 if not b else 8.2, fontweight="semibold" if b else "normal", color=INK)
    fig.savefig(f"{OUT}/{fname}", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    draw_plan_A()
    draw_plan_A("05_plan_palette3.png", p3=True)
    draw_long_section()
    draw_cross_section()
    draw_plan_B()
    print("done")
