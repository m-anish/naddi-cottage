"""Vertex medallions for the main dome.

Each medallion is a pattern drawn on the plane tangent to the dome at an upper vertex, projected
from the dome's centre (5'-1" above the floor: standing eye height) onto five flat pieces, one per
facet meeting at that vertex. Seen from the centre of the room it reads as a true circle and the
fold lines underneath disappear.

usage: python3 medallion.py <motif> <view> <out.png> [samples W H] [night] [base_scheme]
"""
import sys, math
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy
from mathutils import Vector
import dome as Dm
from dome import (O, Ur, T, Lr, FACES, NORMALS, NAMES, R_IN, D_LIN, ZC, LOFT_Z, M, to_m)
import scene as S
from scene import add_obj, simple, emit_mat, plaster, render_settings
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely import affinity
import patterns as PT

ALPHA = math.radians(19.0)        # angular radius of a medallion seen from the centre
TA = math.tan(ALPHA)
LOFT_VERTS = (0, 1, 4)           # vertices over the assumed loft: medallion stops at the loft floor
# depths, measured inward from the lining plane (ft)
BACK = (0.24, 0.26)              # back plate, just inside the exposed roof struts (0.22 ft)
RIMB = (0.24, 0.38)              # edge band closing the cavity
FRONT = (0.36, 0.38)             # pierced face sheet (6 mm)
LED = (0.27, 0.275)


def vertex_frame(k):
    V = Ur[k]
    v = (V - O).normalized()
    e2 = (Vector((0, 0, 1)) - v * v.z).normalized()
    e1 = v.cross(e2).normalized()
    # neighbours and the azimuth of each edge in the tangent plane
    nbrs = [T, Ur[(k + 1) % 5], Ur[(k - 1) % 5], Lr[k], Lr[(k - 1) % 5]]
    az = []
    for N in nbrs:
        d = (N - O).normalized()
        g = d / d.dot(v) - v
        az.append(math.degrees(math.atan2(g.dot(e2), g.dot(e1))) % 360)
    faces = [f[0] for f in FACES if any((p - V).length < 1e-6 for p in f[3])]
    return v, e1, e2, sorted(az), az[0], faces


def direction(v, e1, e2, x, y):
    return v + e1 * (x * TA) + e2 * (y * TA)


def to3d(v, e1, e2, n, x, y, off):
    d = direction(v, e1, e2, x, y)
    rho = R_IN - D_LIN - off
    return O + d * (rho / n.dot(d))


def halfplane(A, B, C, L=20.0):
    nn = math.hypot(B, C)
    nb, nc = B / nn, C / nn
    p0 = (-A * nb / nn, -A * nc / nn)
    dx, dy = -nc, nb
    return Polygon([(p0[0] + dx * L, p0[1] + dy * L), (p0[0] - dx * L, p0[1] - dy * L),
                    (p0[0] - dx * L + nb * L, p0[1] - dy * L + nc * L), (p0[0] + dx * L + nb * L, p0[1] + dy * L + nc * L)])


def wedges(k):
    v, e1, e2, az_sorted, az_top, faces = vertex_frame(k)
    out = []
    for i in range(5):
        a0, a1 = az_sorted[i], az_sorted[(i + 1) % 5]
        if a1 < a0:
            a1 += 360
        am = (a0 + a1) / 2
        wp = Polygon([(0, 0)] + [(6 * math.cos(math.radians(a)), 6 * math.sin(math.radians(a))) for a in (a0, am, a1)])
        dm = direction(v, e1, e2, math.cos(math.radians(am)) * 0.5, math.sin(math.radians(am)) * 0.5)
        fn = max(faces, key=lambda f: NORMALS[f].dot(dm))
        out.append((wp, fn, (a0 % 360, a1 % 360)))
    return v, e1, e2, az_top, out


def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon" and p.area > 1e-7]


def on_ray(pt, angs, eps=1e-6):
    if math.hypot(*pt) < eps:
        return True
    for a in angs:
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        if abs(pt[0] * sa - pt[1] * ca) < eps and pt[0] * ca + pt[1] * sa > -eps:
            return True
    return False


def place(k, shape, depth, mat, name, clip_loft=False):
    """extrude a unit-disk shape between two depths and wrap it over the facets at vertex k"""
    v, e1, e2, az_top, wl = wedges(k)
    shape = affinity.rotate(shape, az_top - 90.0, origin=(0, 0))
    angs = [w[2][0] for w in wl]
    verts, faces = [], []
    lo, hi = depth
    for wp, fn, (a0, a1) in wl:
        n = NORMALS[fn]
        piece = shape.intersection(wp)
        if clip_loft:
            rho = R_IN - D_LIN - (lo + hi) / 2
            h = LOFT_Z + 0.02 - ZC
            A = rho * v.z - h * n.dot(v)
            B = TA * (rho * e1.z - h * n.dot(e1))
            C = TA * (rho * e2.z - h * n.dot(e2))
            piece = piece.intersection(halfplane(A, B, C))
        for pg in polys(piece):
            pg = shapely.set_precision(pg, 1e-7)
            if pg.is_empty or pg.geom_type != "Polygon":
                continue
            tris = shapely.constrained_delaunay_triangles(pg)
            idx = {}
            def vid(pt, off):
                key = (round(pt[0], 7), round(pt[1], 7), off)
                if key not in idx:
                    idx[key] = len(verts)
                    verts.append(to_m(to3d(v, e1, e2, n, pt[0], pt[1], off)))
                return idx[key]
            for t in tris.geoms:
                c = list(t.exterior.coords)[:3]
                faces.append([vid(c[0], hi), vid(c[1], hi), vid(c[2], hi)])
                faces.append([vid(c[2], lo), vid(c[1], lo), vid(c[0], lo)])
            for rg in [pg.exterior] + list(pg.interiors):
                cs = list(rg.coords)
                for i in range(len(cs) - 1):
                    a, b = cs[i], cs[i + 1]
                    if on_ray(a, angs) and on_ray(b, angs):
                        continue
                    faces.append([vid(a, lo), vid(b, lo), vid(b, hi), vid(a, hi)])
    if not faces:
        return None
    return add_obj(name, verts, faces, mat)


MOTIF_MATS = {
    # front sheet, back plate, edge band
    "karbandi": ("white_sheet", "terracotta", "white_sheet"),
    "padma": ("pine_sheet", "lime_back", "pine_sheet"),
    "jali": ("white_sheet", "lime_back", "white_sheet"),
}


def medallion_mats(P):
    P["white_sheet"] = simple("white_sheet", (0.86, 0.84, 0.79), 0.6)
    P["terracotta"] = plaster("terracotta", (0.62, 0.36, 0.27), (0.56, 0.31, 0.23), 0.85, 2.0, 0.05)
    P["pine_sheet"] = S.wood("pine_sheet", (0.66, 0.47, 0.27), (0.55, 0.37, 0.2), 0.5, 3.0)
    P["lime_back"] = simple("lime_back", (0.80, 0.77, 0.71), 0.85)
    P["led"] = emit_mat("led", (1.0, 0.72, 0.42), 30.0)


def medallions(P, motif, night=False):
    shape, outline = PT.MOTIFS[motif]()
    band = outline.difference(outline.buffer(-0.035))
    back = outline.buffer(-0.01)
    led = outline.buffer(-0.04).difference(outline.buffer(-0.055))
    fm, bm, rm = MOTIF_MATS[motif]
    for k in range(5):
        cl = k in LOFT_VERTS
        place(k, back, BACK, P[bm], f"med_back_{k}", cl)
        place(k, band, RIMB, P[rm], f"med_band_{k}", cl)
        place(k, shape, FRONT, P[fm], f"med_front_{k}", cl)
        if night:
            place(k, led, LED, P["led"], f"med_led_{k}", cl)


def rehang_lamp(P, lp):
    """move the paper pendant toward the middle so it does not sit in front of a medallion"""
    for ob in list(bpy.data.objects):
        if ob.type == "MESH" and (ob.name.startswith("Sphere") or ob.name.startswith("cord")):
            bpy.data.objects.remove(ob, do_unlink=True)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55 * M, location=to_m(lp), segments=32, ring_count=16)
    sp = bpy.context.active_object
    sp.data.materials.append(P["lamp"])
    for poly in sp.data.polygons:
        poly.use_smooth = True
    sp.visible_shadow = False
    S.cyl("cord", to_m(lp + Vector((0, 0, 0.5))), to_m(Vector((lp.x, lp.y, 15.6))), 0.01 * M, P["black"])
    lamp = bpy.data.objects.get("pendant")
    if lamp:
        lamp.location = to_m(lp)


VIEWS = {
    "vtx": ((0.0, 0.0, 5.1), Ur[2], 17.0),
    "wide": ((0.0, 2.4, 4.9), (0.0, -8.0, 8.0), 12.0),
    "hero": Dm.VIEWS["hero"],
    "side": ((3.2, -4.6, 5.2), (-6.0, -8.26, 10.2), 18.0),
}


def main():
    a = sys.argv[sys.argv.index('--'):] if '--' in sys.argv else sys.argv
    motif, view, out = a[1], a[2], a[3]
    samples = int(a[4]) if len(a) > 4 else 64
    W = int(a[5]) if len(a) > 5 else 1200
    H = int(a[6]) if len(a) > 6 else 800
    night = len(a) > 7 and a[7] == "night"
    base = a[8] if len(a) > 8 else "w_wainscot_limed"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S.COLL = bpy.context.scene.collection
    P = Dm.materials()
    medallion_mats(P)
    Dm.build(base, P)
    if motif != "none":
        medallions(P, motif, night)
    rehang_lamp(P, Vector((0.9, -1.4, 10.2)))
    loc, tgt, lens = VIEWS[view]
    Dm.cam_look(loc, tuple(tgt), lens)
    if night:
        w = bpy.data.worlds.new("Wn")
        bpy.context.scene.world = w
        w.use_nodes = True
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.02, 0.03, 0.06, 1)
        bg.inputs[1].default_value = 0.6
        lamp = bpy.data.objects.get("pendant")
        if lamp:
            lamp.data.energy = 25
        render_settings(samples, W, H, 0.3)
    else:
        Dm.world_sky()
        Dm.sun((0.75, 0.55, 0.55), 4.5)
        render_settings(samples, W, H, -0.2)
    sc = bpy.context.scene
    sc.cycles.diffuse_bounces = 5
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)


if __name__ == "__main__":
    main()
