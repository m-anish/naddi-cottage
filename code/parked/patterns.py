"""Medallion patterns for the dome's upper vertices, drawn in a unit disk.

Coordinates: unit disk = the medallion as seen from the dome's centre (gnomonic plane, radius 1 = edge).
The five struts meeting at a vertex project to rays at 90, 162, 234, 306 and 18 degrees, so every
pattern here has ten-fold symmetry with one mirror axis at 90 degrees.
"""
import math
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

Q = 6   # quad segments for round buffers


def P(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def disk(r, c=(0, 0)):
    return Point(c).buffer(r, quad_segs=24)


def ring(r0, r1):
    return disk(r1).difference(disk(r0))


def strap(pts, w):
    return LineString(pts).buffer(w / 2, cap_style="flat", join_style="mitre", mitre_limit=3)


def circle_line(c, r, w, n=96):
    pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    return LineString(pts).buffer(w / 2, quad_segs=Q)


def cusped(r, n, depth):
    """multifoil (cusped) outline: union of n small circles on a ring + the inner disk"""
    s = 2 * math.pi * r / n
    rc = s * 0.62
    return unary_union([disk(r - depth)] + [disk(rc, P(r - rc, 90 + 360 / n * (i + 0.5))) for i in range(n)])


def beaded(r, n, rb):
    return unary_union([disk(r)] + [disk(rb, P(r, 90 + 360 / n * i)) for i in range(n)])


def petal(r0, r1, hw, axis_deg, n=28, tip=0.75):
    """lotus petal from radius r0 to r1 along an axis, max half width hw, pointed tip"""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        h = hw * (math.sin(math.pi * min(t, 0.999) ** tip)) ** 0.85
        left.append((r, h))
        right.append((r, -h))
    pts = left + right[::-1]
    poly = Polygon(pts)
    return affinity.rotate(poly, axis_deg, origin=(0, 0))


def star_poly(n, r_out, r_in, rot=90):
    return Polygon([P(r_out if i % 2 == 0 else r_in, rot + 180 / n * i) for i in range(2 * n)])


# ------------------------------------------------------------------ motifs
def karbandi(w=0.03):
    """Persian/Mughal star vault (karbandi) with a central shamsa: tone-on-tone strapwork"""
    R = 0.88
    outline = cusped(0.985, 20, 0.05)
    parts = [outline.difference(disk(R))]
    rim = [P(R + 0.005, 90 + 18 * i) for i in range(20)]
    lines = [strap([rim[i], rim[(i + 7) % 20]], w) for i in range(20)]
    s10 = [P(0.60, 90 + 36 * i) for i in range(10)]
    lines += [strap([s10[i], s10[(i + 3) % 10]], w) for i in range(10)]
    lines += [circle_line((0, 0), 0.40, w)]
    # ten ribs from the crown out to the rim, like the ribs of a karbandi vault
    lines += [strap([P(0.18, 90 + 36 * i), P(R, 90 + 36 * i)], w * 0.85) for i in range(10)]
    parts.append(unary_union(lines).intersection(disk(R + 0.01)))
    # shamsa: ten-pointed sun with a round boss over the steel hub
    sun = star_poly(10, 0.22, 0.135).difference(disk(0.09)).union(disk(0.062))
    sun = sun.union(unary_union([strap([P(0.0, 90 + 36 * i), P(0.12, 90 + 36 * i)], w * 0.8) for i in range(10)]))
    parts.append(sun)
    return unary_union(parts), outline


def padma(w=0.03):
    """Buddhist lotus (padma): three rings of petals around a seed pod, beaded rim"""
    outline = beaded(0.955, 40, 0.028)
    parts = [outline.difference(disk(0.895))]
    pod = disk(0.15).difference(unary_union([disk(0.022)] + [disk(0.02, P(0.085, 90 + 72 * i)) for i in range(5)]))
    parts.append(pod)
    gap = 0.022
    A = unary_union([petal(0.10, 0.50, 0.082, 90 + 36 * i) for i in range(10)])
    parts.append(A)
    parts.append(ring(0.47, 0.50))
    B = unary_union([petal(0.47, 0.78, 0.150, 108 + 36 * i) for i in range(10)])
    Bs = unary_union([petal(0.56, 0.72, 0.052, 108 + 36 * i) for i in range(10)])   # slot inside each petal
    parts.append(B.difference(Bs))
    parts.append(ring(0.755, 0.785))
    C = unary_union([petal(0.76, 0.915, 0.095, 90 + 18 * i) for i in range(20)])
    parts.append(C)
    shape = unary_union(parts)
    return shape, outline


def jali(w=0.024):
    """Mughal interlaced-circle jali for backlighting"""
    outline = cusped(0.985, 20, 0.05)
    R = 0.90
    parts = [outline.difference(disk(R))]
    lines = []
    lines += [circle_line(P(0.20, 90 + 36 * i), 0.125, w) for i in range(10)]
    lines += [circle_line(P(0.44, 108 + 36 * i), 0.165, w) for i in range(10)]
    lines += [circle_line(P(0.70, 90 + 18 * i), 0.118, w) for i in range(20)]
    lines += [circle_line((0, 0), r, w) for r in (0.33, 0.585, 0.83)]
    lines += [circle_line(P(0.865, 99 + 18 * i), 0.045, w * 0.8) for i in range(20)]
    parts.append(unary_union(lines).intersection(disk(R + 0.01)))
    rose = unary_union([petal(0.0, 0.10, 0.032, 90 + 36 * i) for i in range(10)] + [disk(0.035)])
    parts.append(rose)
    return unary_union(parts), outline


MOTIFS = {"karbandi": karbandi, "padma": padma, "jali": jali}


def islands(shape):
    """pieces that would fall out when cut (not connected to the largest piece)"""
    geoms = list(shape.geoms) if isinstance(shape, MultiPolygon) else [shape]
    geoms.sort(key=lambda g: -g.area)
    return geoms[1:]


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    def draw(ax, geom, fc, ec="none"):
        geoms = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
        for g in geoms:
            if g.is_empty or g.geom_type != "Polygon":
                continue
            verts, codes = [], []
            for ringc in [g.exterior] + list(g.interiors):
                cs = list(ringc.coords)
                verts += cs
                codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), fc=fc, ec=ec, lw=0.3))

    fig, axs = plt.subplots(1, 3, figsize=(15, 5.4), dpi=110)
    for ax, (nm, fn) in zip(axs, MOTIFS.items()):
        shape, outline = fn()
        draw(ax, outline, "#b0604a")
        draw(ax, shape, "#f3eee4")
        for k in range(5):
            a = math.radians(90 + 72 * k)
            ax.plot([0, 1.05 * math.cos(a)], [0, 1.05 * math.sin(a)], color="#3a6ea5", lw=0.6, ls="--")
        isl = islands(shape)
        ax.set_title(f"{nm}  ·  {len(isl)} loose pieces", fontsize=10)
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.set_aspect("equal")
        ax.axis("off")
    import os
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "motifs_test.png"), bbox_inches="tight")
    print("ok")
