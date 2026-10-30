"""Main dome interior: 1V icosahedral dome (12 ft struts), floor on the lower pentagon ring.

usage: python3 dome.py <scheme> <view> <out.png> [samples] [W] [H]
schemes: lime | wainscot | canopy | frame | timber | combo
views:   hero | back | cut | line_cut | line_hero
"""
import sys, math, os, random
import bpy, bmesh
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as S
from scene import (V, M, add_obj, prism, cyl, box, clip_poly, planar_uv, simple, plaster, tiles, wood,
                   glass_mat, emit_mat, towel_mat, fabric_mat, nodes_mat, inp, tex_coord, noise, ramp, bump,
                   render_settings, setup_world, line_render)

# ------------------------------------------------------------------ geometry (feet)
A_EDGE = 12.0
R_CIRC = A_EDGE * math.sin(2 * math.pi / 5)          # 11.41
H_RING = R_CIRC / math.sqrt(5)                        # 5.10
R_RING = 2 * R_CIRC / math.sqrt(5)                    # 10.21
ZC = H_RING                                           # icosahedron centre above floor
R_IN = A_EDGE * ((1 + math.sqrt(5)) / 2) ** 2 / (2 * math.sqrt(3))   # 9.07 inradius
D_LIN = 0.45                                          # lining plane inside the exterior skin
Z_UP = 2 * H_RING                                     # 10.21 upper ring (the lower of the pair)
Z_UP2 = Z_UP + 0.24                                   # 10.44 the frame doubles this ring
Z_TOP = H_RING + R_CIRC                               # 16.51
DATUM = 3.25                                          # wainscot / sill datum
GROUND_Z = -1.25                                      # the frame stands 1'-3" clear of the ground
STRUT_LEN = 11.417                                    # real steel strut, 11'-5"
HUB_SETBACK = 3.5 / 12                                # hub at each end makes up the 12 ft edge

# Loft: measured off the Onshape frame. Not a slab on posts - a platform hung from
# the five upper-ring vertices and from a 3x3" drop off the apex, with radial
# struts to three of the five hangers (NNE, NW, SW), so it is a 144 deg sector.
LOFT_Z = 8.46                                         # platform datum, 8'-5"
LOFT_FACES = (4, 0, 1)                                # Ur indices carrying radial struts
HANG_TOP_R, HANG_TOP_Z = 9.37, 10.11                  # hanger head, on the upper ring
HANG_FOOT_R = 10.19                                   # hanger foot, at LOFT_Z
DROP_TOP_Z = 16.14                                    # central drop, just under the apex hub
O = Vector((0, 0, ZC))

ROT = 108.0   # the model was turned this far to match the frame as built


def pol(r, deg, z):
    a = math.radians(deg)
    return Vector((r * math.cos(a), r * math.sin(a), z))


def rot_z(p, deg=ROT):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return Vector((p.x * c - p.y * s, p.x * s + p.y * c, p.z))


# Turned +108 deg from the first guess so the model sits the way the frame is built:
# floor ring at 18+72k, upper ring at 54+72k, both measured off the Onshape export.
# Face names do not change, so OPENINGS and SCHEMES still mean the same walls -
# up0 is the washroom (NW) and up3 the east extension. See docs/onshape_frame_check.md.
Lr = [pol(R_RING, 234 + 72 * k, 0.0) for k in range(5)]
Ur = [pol(R_RING, 198 + 72 * k, Z_UP) for k in range(5)]
T = Vector((0, 0, Z_TOP))

FACES = []   # (name, kind, k, verts)
for k in range(5):
    FACES.append((f"up{k}", "up", k, [Lr[(k - 1) % 5], Lr[k], Ur[k]]))
    FACES.append((f"down{k}", "down", k, [Ur[k], Ur[(k + 1) % 5], Lr[k]]))
    FACES.append((f"cap{k}", "cap", k, [T, Ur[k], Ur[(k + 1) % 5]]))


def face_normal(verts):
    a, b, c = verts
    n = (b - a).cross(c - a).normalized()
    cen = (a + b + c) / 3
    if n.dot(cen - O) < 0:
        n = -n
    return n


NORMALS = {f[0]: face_normal(f[3]) for f in FACES}
NAMES = [f[0] for f in FACES]


def hs(name, off=D_LIN):
    n = NORMALS[name]
    return lambda p: (R_IN - off) - n.dot(p - O)


def floor_hs(p):
    return p.z


def dedupe(poly, eps=1e-4):
    out = []
    for p in poly:
        if not out or (p - out[-1]).length > eps:
            out.append(p)
    while len(out) > 1 and (out[0] - out[-1]).length <= eps:
        out.pop()
    return out


def lining_poly(name):
    verts = [f for f in FACES if f[0] == name][0][3]
    n = NORMALS[name]
    cen = sum(verts, Vector()) / 3
    big = [cen + (v - cen) * 3.0 for v in verts]
    big = [p - n * (n.dot(p - O) - (R_IN - D_LIN)) for p in big]   # project onto lining plane
    poly = big
    for other in NAMES:
        if other == name:
            continue
        poly = clip_poly(poly, hs(other))
        if len(poly) < 3:
            return []
    poly = clip_poly(poly, floor_hs)
    return dedupe(poly)


def section_at_z(z):
    s = 30
    poly = [Vector((-s, -s, z)), Vector((s, -s, z)), Vector((s, s, z)), Vector((-s, s, z))]
    for nm in NAMES:
        poly = clip_poly(poly, hs(nm))
    return dedupe(poly)


def face_frame(name):
    """origin on lining plane at floor below face centre, U horizontal (right seen from inside), W up-slope"""
    n = NORMALS[name]
    U = Vector((0, 0, 1)).cross(n).normalized()       # from inside looking at the face: n points away, so U = z x n is to the right
    W = n.cross(U).normalized()
    if W.z < 0:
        W = -W
    az = math.atan2(n.y, n.x)
    denom = n.x * math.cos(az) + n.y * math.sin(az)
    rho = (R_IN - D_LIN + n.z * ZC) / denom
    o = Vector((rho * math.cos(az), rho * math.sin(az), 0.0))
    return o, U, W, n


def plane_pt(name, u, z, off=0.0):
    o, U, W, n = face_frame(name)
    t = z / W.z
    return o + U * u + W * t + n * off


def to_m(p):
    return Vector((p.x * M, p.y * M, p.z * M))


def bearing(deg):
    """plan angle in the model -> compass bearing. The east extension (up3, 54 deg)
    faces east, so bearing = 144 - angle. See docs/onshape_frame_check.md."""
    return (144.0 - deg) % 360.0


def sun_dir(bearing_deg, altitude_deg):
    """direction towards the sun, in model coordinates, from a compass bearing"""
    a = math.radians(144.0 - bearing_deg)
    el = math.radians(altitude_deg)
    return (math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))


# Dharamsala is 32.2 N, 76.3 E. Mid-morning, when the east extension takes the sun
# and the light rakes across the room rather than facing the camera.
SUN_BEARING, SUN_ALT = 118.0, 34.0


def member(name, a, b, w, d, mat, bevel=0.01):
    """a rectangular steel member from a to b (feet): w across, d through"""
    e = (b - a).normalized()
    side = e.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side = side.normalized()
    nrm = side.cross(e).normalized()
    r0 = [a + side * w / 2 + nrm * d / 2, a - side * w / 2 + nrm * d / 2,
          a - side * w / 2 - nrm * d / 2, a + side * w / 2 - nrm * d / 2]
    r1 = [p + (b - a) for p in r0]
    return prism(name, [to_m(p) for p in r0], [to_m(p) for p in r1], mat, bevel=bevel)


def sector_clip(poly, a_from, a_to):
    """keep the part of poly inside the sector running anticlockwise a_from -> a_to
    (sectors up to 180 deg; ours is 144)"""
    n1 = math.radians(a_from + 90)
    n2 = math.radians(a_to - 90)
    poly = clip_poly(poly, lambda p: p.x * math.cos(n1) + p.y * math.sin(n1))
    poly = clip_poly(poly, lambda p: p.x * math.cos(n2) + p.y * math.sin(n2))
    return dedupe(poly)


def loft_sector():
    angs = [(198 + 72 * k) % 360 for k in LOFT_FACES]
    return angs[0], angs[-1]


def lining_radius(deg, z, hi=14.0):
    """plan radius of the finished lining surface at this angle and height"""
    a = math.radians(deg)
    lo = 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        p = Vector((mid * math.cos(a), mid * math.sin(a), z))
        if min(hs(nm)(p) for nm in NAMES) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def lining_apex_z(hi=20.0):
    """height of the lining on the dome axis"""
    lo = 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if min(hs(nm)(Vector((0, 0, mid))) for nm in NAMES) > 0:
            lo = mid
        else:
            hi = mid
    return lo


# ------------------------------------------------------------------ openings
# kind, face, u-centre, width, z0, z1
OPENINGS = [
    ("door_portal", "up0", 0.0, 2.5, 0.0, 6.667),     # washroom door
    ("window", "down0", 0.0, 5.0, 7.3, 8.6),          # high strip window
    ("window", "down4", 0.0, 2.5, 3.5, 6.5),          # casement
    ("window", "up1", 0.0, 2.5, 3.5, 6.0),            # casement over daybed
    ("window", "up4", 0.0, 4.5, 3.25, 6.0),           # sliding window
    ("door_portal", "up3", 0.0, 3.0, 0.0, 6.9),       # main door (behind camera)
    ("window", "down1", 0.0, 5.0, 7.3, 8.6),
    ("window", "up2", 0.0, 2.5, 3.5, 6.0),
]

# ------------------------------------------------------------------ extensions
# Both extensions spring from an "up" face. The floor is the lower-ring edge carried
# out on the cantilevered floor beams (the tips below are measured off the frame);
# the ridge is the rafter running out past the upper-ring vertex. Walls lean out ~16
# deg, which is what Anish estimated (15) rather than the ~11 the dome alone suggests.
#   up0  washroom, NW: 12 ft opening, 5'-8" deep at the floor, 6'-10" at the ridge
#   up3  east,      E: 12 ft opening, 7'-6" deep at the floor, 8'-7" at the ridge
EXT_GEOM = {
    "up0": (((-14.27, -0.28), (-11.71, -8.16)), 15.13, 7.36),
    "up3": (((12.00, 10.51), (6.29, 14.66)), 16.84, 6.31),
}


def extension(P, name, wall_mat, floor_mat):
    (t1, t2), rr, rz = EXT_GEOM[name]
    b1, b2, ua = [f for f in FACES if f[0] == name][0][3]
    T1 = Vector((t1[0], t1[1], 0.0))
    T2 = Vector((t2[0], t2[1], 0.0))
    ang = math.atan2(ua.y, ua.x)
    RG = Vector((rr * math.cos(ang), rr * math.sin(ang), rz))
    panels = [("floor", (b1, T1, T2, b2), floor_mat),
              ("s1", (b1, T1, RG, ua), wall_mat),
              ("s2", (b2, T2, RG, ua), wall_mat),
              ("outer", (T1, T2, RG), wall_mat)]
    for tag, poly, mat in panels:
        ob = add_obj(f"ext_{name}_{tag}", [to_m(p) for p in poly],
                     [list(range(len(poly)))], mat)
        sm = ob.modifiers.new("solid", "SOLIDIFY")
        sm.thickness = 0.25 * M
        sm.offset = 1.0 if tag == "floor" else -1.0
    return RG


# ------------------------------------------------------------------ materials
def boards(name, c1, c2, board_w_ft, board_l_ft, vertical=False, rough=0.55, gap_in=0.08, grain=0.35):
    m, nt, b = nodes_mat(name)
    co = tex_coord(nt, "UV")
    mp = nt.nodes.new("ShaderNodeMapping")
    if vertical:
        mp.inputs["Rotation"].default_value = (0, 0, math.radians(90))
    nt.links.new(co, mp.inputs["Vector"])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = board_l_ft * M
    br.inputs["Row Height"].default_value = board_w_ft * M
    br.inputs["Mortar Size"].default_value = gap_in / 12 * M
    br.offset = 0.37
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (0.1, 0.07, 0.05, 1)
    nt.links.new(mp.outputs[0], br.inputs["Vector"])
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = (1.0, 28.0, 1.0)
    if vertical:
        mp2.inputs["Rotation"].default_value = (0, 0, math.radians(90))
        mp2.inputs["Scale"].default_value = (28.0, 1.0, 1.0)
    nt.links.new(co, mp2.inputs["Vector"])
    nz = noise(nt, mp2.outputs[0], 4.0, 8, 0.62)
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X" if vertical else "Y"
    wv.inputs["Scale"].default_value = 30.0
    wv.inputs["Distortion"].default_value = 4.0
    wv.inputs["Detail"].default_value = 2.0
    nt.links.new(co, wv.inputs["Vector"])
    mixg = nt.nodes.new("ShaderNodeMix")
    mixg.data_type = "FLOAT"
    mixg.inputs[0].default_value = 0.5
    nt.links.new(nz.outputs[0], mixg.inputs[2])
    nt.links.new(wv.outputs["Fac"], mixg.inputs[3])
    ov = nt.nodes.new("ShaderNodeMix")
    ov.data_type = "RGBA"
    ov.blend_type = "OVERLAY"
    ov.inputs[0].default_value = grain
    nt.links.new(br.outputs["Color"], ov.inputs[6])
    nt.links.new(mixg.outputs[0], ov.inputs[7])
    nt.links.new(ov.outputs[2], inp(b, "Base Color"))
    inp(b, "Roughness").default_value = rough
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    bump(nt, b, inv.outputs[0], 0.35, 0.003)
    return m


def materials():
    P = {}
    P["lime"] = plaster("lime", (0.83, 0.80, 0.74), (0.78, 0.75, 0.69), 0.9, 1.1, 0.05)
    P["pine_v"] = boards("pine_v", (0.62, 0.44, 0.25), (0.56, 0.38, 0.21), 0.375, 9.0, vertical=True)
    P["pine_h"] = boards("pine_h", (0.62, 0.44, 0.25), (0.56, 0.38, 0.21), 0.375, 9.0, vertical=False)
    P["deodar"] = wood("deodar", (0.46, 0.28, 0.14), (0.32, 0.18, 0.08), 0.5)
    P["floor"] = boards("floorboards", (0.36, 0.22, 0.12), (0.31, 0.19, 0.1), 0.6, 8.0, rough=0.45, grain=0.3)
    P["floor_pine"] = boards("floor_pine", (0.6, 0.42, 0.24), (0.54, 0.37, 0.2), 0.6, 8.0, rough=0.45, grain=0.3)
    P["loft"] = boards("loft_boards", (0.6, 0.43, 0.25), (0.54, 0.38, 0.21), 0.5, 8.0, rough=0.5)
    P["upvc"] = simple("upvc", (0.86, 0.86, 0.84), 0.3)
    P["glass"] = glass_mat("glass", (0.97, 0.99, 0.985))
    P["door"] = wood("door", (0.5, 0.33, 0.18), (0.38, 0.23, 0.12), 0.6, along="Z")
    P["ladder"] = wood("ladder", (0.66, 0.48, 0.28), (0.54, 0.37, 0.2), 0.5)
    P["rug"] = towel_mat("jute", (0.52, 0.42, 0.28))
    P["cushion"] = fabric_mat("cushion", (0.36, 0.42, 0.33))
    P["cushion2"] = fabric_mat("cushion2", (0.7, 0.5, 0.36))
    P["lamp"] = emit_mat("paper_lamp", (1.0, 0.86, 0.66), 3.5)
    P["black"] = simple("black_metal", (0.03, 0.03, 0.03), 0.5, metal=0.5)
    P["leaf"] = simple("leaf", (0.06, 0.2, 0.07), 0.45)
    P["pot"] = plaster("pot", (0.55, 0.36, 0.25), (0.45, 0.28, 0.2), 0.8, 8)
    P["poche"] = simple("poche", (0.11, 0.105, 0.1), 0.9)
    P["puf"] = boards("puf_panel", (0.8, 0.79, 0.76), (0.79, 0.78, 0.75), 3.28, 40.0, vertical=True, rough=0.38,
                      gap_in=0.06, grain=0.02)
    P["steel_paint"] = simple("steel_offwhite", (0.74, 0.73, 0.7), 0.42)
    P["pine_case"] = wood("pine_case", (0.66, 0.48, 0.28), (0.54, 0.37, 0.2), 0.5)
    # wainscot variants that avoid wood-on-wood with the floor
    P["pine_v_limed"] = boards("pine_v_limed", (0.74, 0.70, 0.62), (0.70, 0.66, 0.58), 0.375, 9.0, vertical=True,
                               rough=0.6, grain=0.32)
    P["limed_ledge"] = simple("limed_ledge", (0.68, 0.64, 0.56), 0.55)
    P["pine_v_paint"] = boards("pine_v_paint", (0.2, 0.25, 0.21), (0.2, 0.25, 0.21), 0.375, 9.0, vertical=True,
                               rough=0.5, grain=0.03, gap_in=0.1)
    P["sage_paint"] = simple("sage_paint", (0.2, 0.25, 0.21), 0.5)
    return P


SCHEMES = {
    # walls only; the roof stays as off-white PUF panels with its struts visible
    "w_lime":     ("lime", "lime", "puf", None, "steel_paint"),
    "w_wainscot": ("pine_v", "lime", "puf", None, "steel_paint"),
    "w_wainscot_pinefloor": ("pine_v", "lime", "puf", None, "steel_paint"),
    "w_lime_pinefloor": ("lime", "lime", "puf", None, "steel_paint"),
    "w_wainscot_pine": ("pine_v", "lime", "puf", None, "pine_case"),
    "w_wainscot_limed": ("pine_v_limed", "lime", "puf", None, "steel_paint"),
    "w_wainscot_paint": ("pine_v_paint", "lime", "puf", None, "steel_paint"),
    "w_timber":   ("pine_h", "pine_h", "puf", None, "steel_paint"),
    # (lower belt below datum, belt above datum, cap, frame)
    "lime":     ("lime", "lime", "lime", None),
    "wainscot": ("pine_v", "lime", "lime", None),
    "canopy":   ("lime", "lime", "pine_h", None),
    "frame":    ("lime", "lime", "lime", "deodar"),
    "timber":   ("pine_h", "pine_h", "pine_h", None),
    "combo":    ("pine_v", "lime", "pine_h", None),
}


# ------------------------------------------------------------------ build
def oriented(poly, name):
    n = NORMALS[name]
    pn = (poly[1] - poly[0]).cross(poly[2] - poly[0])
    if pn.dot(n) > 0:     # want normals pointing into the room
        poly = list(reversed(poly))
    return poly


def lining_piece(name, poly, mat, tag):
    poly = oriented(poly, name)
    ob = add_obj(f"lin_{name}_{tag}", [to_m(p) for p in poly], [list(range(len(poly)))], mat)
    sm = ob.modifiers.new("solid", "SOLIDIFY")
    sm.thickness = 0.06 * M
    sm.offset = -1.0      # thickness goes outward (away from the room)
    return ob


def opening_cutter(name, uc, w, z0, z1, depth=1.5):
    o, U, Wd, n = face_frame(name)
    if z0 <= 0.0:   # door portal: vertical box from the base line outward
        base = plane_pt(name, 0, 0)
        corners0 = [base + U * (uc - w / 2) + Vector((0, 0, z0 - 0.3)), base + U * (uc + w / 2) + Vector((0, 0, z0 - 0.3)),
                    base + U * (uc + w / 2) + Vector((0, 0, z1)), base + U * (uc - w / 2) + Vector((0, 0, z1))]
        nh = Vector((n.x, n.y, 0)).normalized()
        r0 = [c - nh * 0.3 for c in corners0]
        r1 = [c + nh * 3.0 for c in corners0]
    else:
        corners = [plane_pt(name, uc - w / 2, z0), plane_pt(name, uc + w / 2, z0), plane_pt(name, uc + w / 2, z1),
                   plane_pt(name, uc - w / 2, z1)]
        r0 = [c - n * 0.3 for c in corners]
        r1 = [c + n * depth for c in corners]
    ob = prism(f"cut_{name}", [to_m(p) for p in r0], [to_m(p) for p in r1], None)
    ob.hide_render = True
    ob.display_type = "WIRE"
    return ob


def apply_cutters(cutters):
    lin = [o for o in bpy.data.objects if o.name.startswith("lin_")]
    for ob in lin:
        for c in cutters:
            bm = ob.modifiers.new("cut", "BOOLEAN")
            bm.operation = "DIFFERENCE"
            bm.solver = "EXACT"
            bm.object = c


def window_assembly(P, name, uc, w, z0, z1, reveal_mat):
    o, U, Wd, n = face_frame(name)
    def q(u, z, off):
        return plane_pt(name, u, z, off)
    D = D_LIN
    u0, u1 = uc - w / 2, uc + w / 2
    # reveals (lining plane -> skin)
    for (a, b, mt) in (((u0, z0), (u1, z0), "sill"), ((u1, z0), (u1, z1), reveal_mat), ((u1, z1), (u0, z1), reveal_mat),
                       ((u0, z1), (u0, z0), reveal_mat)):
        pts = [q(a[0], a[1], 0), q(b[0], b[1], 0), q(b[0], b[1], D), q(a[0], a[1], D)]
        mat = P["deodar"] if mt == "sill" else P[mt]
        add_obj("reveal", [to_m(p) for p in pts], [[0, 1, 2, 3], [3, 2, 1, 0]], mat)
    # sill board projecting
    s0 = [q(u0 - 0.15, z0 - 0.02, -0.25), q(u1 + 0.15, z0 - 0.02, -0.25), q(u1 + 0.15, z0 - 0.02, D * 0.6),
          q(u0 - 0.15, z0 - 0.02, D * 0.6)]
    s1 = [p + Vector((0, 0, -0.1)) for p in s0]
    prism("sill", [to_m(p) for p in s1], [to_m(p) for p in s0], P["deodar"])
    # uPVC frame ring + glass at the skin
    fr = 0.22
    off_a, off_b = D * 0.55, D * 0.9
    for (a0, b0, a1, b1) in ((u0, z0, u1, z0 + fr), (u0, z1 - fr, u1, z1), (u0, z0, u0 + fr, z1), (u1 - fr, z0, u1, z1)):
        r0 = [q(a0, b0, off_a), q(a1, b0, off_a), q(a1, b1, off_a), q(a0, b1, off_a)]
        r1 = [q(a0, b0, off_b), q(a1, b0, off_b), q(a1, b1, off_b), q(a0, b1, off_b)]
        prism("winframe", [to_m(p) for p in r0], [to_m(p) for p in r1], P["upvc"])
    if w > 3.5:   # sliding: centre mullion
        um = uc
        r0 = [q(um - 0.1, z0, off_a), q(um + 0.1, z0, off_a), q(um + 0.1, z1, off_a), q(um - 0.1, z1, off_a)]
        r1 = [q(um - 0.1, z0, off_b), q(um + 0.1, z0, off_b), q(um + 0.1, z1, off_b), q(um - 0.1, z1, off_b)]
        prism("mullion", [to_m(p) for p in r0], [to_m(p) for p in r1], P["upvc"])
    g = [q(u0 + fr, z0 + fr, off_a + 0.1), q(u1 - fr, z0 + fr, off_a + 0.1), q(u1 - fr, z1 - fr, off_a + 0.1),
         q(u0 + fr, z1 - fr, off_a + 0.1)]
    add_obj("winglass", [to_m(p) for p in g], [[0, 1, 2, 3]], P["glass"])


def door_assembly(P, name, uc, w, z1, reveal_mat, glazed=False):
    o, U, Wd, n = face_frame(name)
    nh = Vector((n.x, n.y, 0)).normalized()
    base = plane_pt(name, 0, 0)
    u0, u1 = uc - w / 2, uc + w / 2
    # depth of soffit: the face leans outward, so at z1 the lining is outward of the base line
    top = plane_pt(name, 0, z1)
    deep = (Vector((top.x, top.y, 0)) - Vector((base.x, base.y, 0))).dot(nh)
    def bp(u, z, d):
        return base + U * u + Vector((0, 0, z)) + nh * d
    # cheeks and soffit
    for uu in (u0, u1):
        pts = [bp(uu, 0, 0), bp(uu, 0, deep + 0.2), bp(uu, z1, deep + 0.2), bp(uu, z1, 0)]
        add_obj("cheek", [to_m(p) for p in pts], [[0, 1, 2, 3], [3, 2, 1, 0]], P[reveal_mat])
    pts = [bp(u0, z1, 0), bp(u1, z1, 0), bp(u1, z1, deep + 0.2), bp(u0, z1, deep + 0.2)]
    add_obj("soffit", [to_m(p) for p in pts], [[0, 1, 2, 3], [3, 2, 1, 0]], P[reveal_mat])
    # frame + leaf set back at the base line (washroom side)
    dd = 0.25
    for (a0, a1, b0, b1) in ((u0, u0 + 0.15, 0, z1), (u1 - 0.15, u1, 0, z1), (u0, u1, z1 - 0.15, z1)):
        r0 = [bp(a0, b0, dd), bp(a1, b0, dd), bp(a1, b1, dd), bp(a0, b1, dd)]
        r1 = [bp(a0, b0, dd + 0.3), bp(a1, b0, dd + 0.3), bp(a1, b1, dd + 0.3), bp(a0, b1, dd + 0.3)]
        prism("doorframe", [to_m(p) for p in r0], [to_m(p) for p in r1], P["upvc"] if glazed else P["deodar"])
    r0 = [bp(u0 + 0.15, 0.02, dd + 0.1), bp(u1 - 0.15, 0.02, dd + 0.1), bp(u1 - 0.15, z1 - 0.15, dd + 0.1), bp(u0 + 0.15, z1 - 0.15, dd + 0.1)]
    r1 = [p + nh * 0.12 * 1 for p in r0]
    prism("doorleaf", [to_m(p) for p in r0], [to_m(p) for p in r1], P["glass"] if glazed else P["door"])
    if not glazed:
        hp = bp(u1 - 0.45, 3.4, dd + 0.05)
        cyl("handle", to_m(hp), to_m(hp + U * -0.4), 0.035 * M, P["black"])


def datum_ledge(P, mat):
    """small timber ledge along the wainscot datum on the belt faces"""
    for nm in NAMES:
        if nm.startswith("cap") or nm == "up0" or nm == "up3":
            continue
        poly = lining_poly(nm)
        lo = clip_poly(poly, lambda p: DATUM - p.z)
        # intersection segment at z = DATUM
        pts = [p for p in lo if abs(p.z - DATUM) < 1e-6]
        if len(pts) < 2:
            continue
        a, b = pts[0], pts[-1]
        n = NORMALS[nm]
        nh = Vector((n.x, n.y, 0)).normalized()
        r0 = [a, b, b - nh * 0.28, a - nh * 0.28]
        r1 = [p + Vector((0, 0, 0.09)) for p in r0]
        prism("ledge", [to_m(p) for p in r0], [to_m(p) for p in r1], mat, bevel=0.01)


def struts(P, mat, roof_only=False, steel=False):
    done = set()
    polys = {nm: lining_poly(nm) for nm in NAMES}
    for nm, poly in polys.items():
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            if a.z < 0.01 and b.z < 0.01:
                continue
            if roof_only and min(a.z, b.z) < Z_UP - 0.7:
                continue
            key = tuple(sorted([tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b)]))
            if key in done or (b - a).length < 0.5:
                continue
            done.add(key)
            # neighbour face sharing this edge
            mid = (a + b) / 2
            nb = [o for o in NAMES if o != nm and abs(hs(o)(mid)) < 1e-3]
            n1 = NORMALS[nm]
            n2 = NORMALS[nb[0]] if nb else n1
            m = -(n1 + n2).normalized()
            e = (b - a).normalized()
            wv = e.cross(m).normalized()
            hw, dp = (0.13, 0.22) if steel else (0.19, 0.24)
            r0 = [a + wv * hw - m * 0.05, a - wv * hw - m * 0.05, a - wv * hw + m * dp, a + wv * hw + m * dp]
            r1 = [p + (b - a) for p in r0]
            prism("strut", [to_m(p) for p in r0], [to_m(p) for p in r1], mat, bevel=0.012)
            # the frame doubles the upper ring: a second member Z_UP2 - Z_UP above it
            if abs(a.z - Z_UP) < 0.3 and abs(b.z - Z_UP) < 0.3:
                dz = Vector((0, 0, Z_UP2 - Z_UP))
                prism("strut_ring2", [to_m(p + dz) for p in r0],
                      [to_m(p + dz) for p in r1], mat, bevel=0.012)


def loft(P):
    """Suspended platform on the real frame: a 144 deg sector hung off three of the
    five upper-ring hangers, its inner corner carried by a 3x3" drop from the apex.
    Replaces the straight-edged slab on posts that the brief assumed."""
    a0, a1 = loft_sector()
    top = sector_clip(section_at_z(LOFT_Z), a0, a1)
    if len(top) < 3:
        return
    bot_z = LOFT_Z - 0.25
    r1 = [to_m(p) for p in top]
    r0 = [to_m(Vector((p.x, p.y, bot_z))) for p in top]
    prism("loft_slab", r0, r1, P["loft"])

    # The five hangers dropping off the upper-ring vertices. Measured, their feet sit
    # at radius HANG_FOOT_R, which is about 9 in OUTSIDE the lining plane - they would
    # be buried in the wall build-up. Drawn pulled in to the lining face instead, so
    # the platform is seen to bear on something. The clash is real and the lining has
    # to be notched around them; see docs/onshape_frame_check.md.
    for k in range(5):
        ang = (198 + 72 * k) % 360
        a = math.radians(ang)
        rf = min(HANG_FOOT_R, lining_radius(ang, LOFT_Z) - 0.08)
        head = Vector((HANG_TOP_R * math.cos(a), HANG_TOP_R * math.sin(a), HANG_TOP_Z))
        foot = Vector((rf * math.cos(a), rf * math.sin(a), LOFT_Z))
        member(f"loft_hanger{k}", head, foot, 3.0 / 12, 9.55 / 12, P["steel_paint"])

    # the central drop from the apex hub, stopped at the roof lining
    ztop = min(DROP_TOP_Z, lining_apex_z() - 0.05)
    member("loft_drop", Vector((0, 0, ztop)), Vector((0, 0, LOFT_Z - 0.07)),
           3.0 / 12, 3.0 / 12, P["steel_paint"])

    # radial struts: centre node out to three of the hangers (missing from the export)
    zr = LOFT_Z - 0.42
    for k in LOFT_FACES:
        a = math.radians(198 + 72 * k)
        member(f"loft_strut{k}", Vector((0, 0, zr)),
               Vector((HANG_FOOT_R * math.cos(a), HANG_FOOT_R * math.sin(a), zr)),
               2.0 / 12, 4.0 / 12, P["steel_paint"])

    # railing along the two open radial edges; the second is left open for the ladder
    rail_h = 3.0
    for idx, ang in enumerate((a0, a1)):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        rmax = max((p.x * d.x + p.y * d.y) for p in top)
        gap = (rmax - 3.9, rmax - 2.3) if idx == 1 else None
        n = 7
        for i in range(n + 1):
            r = 0.7 + (rmax - 1.2) * i / n
            if gap and gap[0] < r < gap[1]:
                continue
            c = Vector((r * d.x, r * d.y, LOFT_Z))
            member(f"loft_post{idx}_{i}", c, c + Vector((0, 0, rail_h)), 0.18, 0.18, P["loft"])
        spans = ((0.7, gap[0]), (gap[1], rmax - 0.5)) if gap else ((0.7, rmax - 0.5),)
        for si, (ra, rb) in enumerate(spans):
            if rb - ra < 0.3:
                continue
            member(f"loft_rail{idx}_{si}",
                   Vector((ra * d.x, ra * d.y, LOFT_Z + rail_h)),
                   Vector((rb * d.x, rb * d.y, LOFT_Z + rail_h)), 0.26, 0.15, P["loft"])
            for zz in (LOFT_Z + 1.0, LOFT_Z + 2.0):
                cyl("rail_bar", to_m(Vector((ra * d.x, ra * d.y, zz))),
                    to_m(Vector((rb * d.x, rb * d.y, zz))), 0.03 * M, P["black"])

    # ladder, climbing to the gap left in the second railing
    a = math.radians(a1)
    d = Vector((math.cos(a), math.sin(a), 0))
    side = Vector((-d.y, d.x, 0))
    rmax = max((p.x * d.x + p.y * d.y) for p in top)
    rl = rmax - 3.1
    land = Vector((rl * d.x, rl * d.y, LOFT_Z + 0.2))
    foot = Vector((rl * d.x, rl * d.y, 0.0)) - d * 2.7
    for s in (-1, 1):
        o = side * s * 0.6
        member("stringer", foot + o, land + o, 0.14, 0.4, P["ladder"])
    nr = 10
    for i in range(1, nr):
        p = foot + (land - foot) * (i / nr)
        member("tread", p - side * 0.55, p + side * 0.55, 0.42, 0.12, P["ladder"])

def furniture(P):
    # rug
    seg = 64
    vs = [to_m(Vector((0.4 + 3.2 * math.cos(2 * math.pi * i / seg), -2.0 + 3.2 * math.sin(2 * math.pi * i / seg), 0.02))) for i in range(seg)]
    ob = add_obj("rug", vs, [list(range(seg))], P["rug"])
    sm = ob.modifiers.new("s", "SOLIDIFY")
    sm.thickness = 0.02 * M
    # daybed along up1 base (left)
    nm = "up1"
    o, U, Wd, n = face_frame(nm)
    nh = Vector((n.x, n.y, 0)).normalized()
    base = plane_pt(nm, 0, 0)
    def bp(u, d, z):
        return base + U * u + nh * (-d) + Vector((0, 0, z))
    L = 6.0
    for (d0, d1, z0, z1, mat) in ((0.3, 3.0, 0.0, 1.15, P["ladder"]), (0.4, 2.9, 1.15, 1.55, P["cushion2"])):
        r0 = [bp(-L / 2, d0, z0), bp(L / 2, d0, z0), bp(L / 2, d1, z0), bp(-L / 2, d1, z0)]
        r1 = [bp(-L / 2, d0, z1), bp(L / 2, d0, z1), bp(L / 2, d1, z1), bp(-L / 2, d1, z1)]
        prism("daybed", [to_m(p) for p in r0], [to_m(p) for p in r1], mat, bevel=0.05)
    for u in (-1.8, 0.0, 1.8):
        c = bp(u, 0.75, 2.2)
        r0 = [c + U * -0.8 + nh * 0.25 - Vector((0, 0, 0.65)), c + U * 0.8 + nh * 0.25 - Vector((0, 0, 0.65)),
              c + U * 0.8 - nh * 0.15 - Vector((0, 0, 0.65)), c + U * -0.8 - nh * 0.15 - Vector((0, 0, 0.65))]
        r1 = [p + Vector((0, 0, 1.3)) + nh * 0.25 for p in r0]
        prism("cushion", [to_m(p) for p in r0], [to_m(p) for p in r1], P["cushion"], bevel=0.12)
    # side table + plant
    cyl("table", to_m(Vector((2.6, -0.6, 0))), to_m(Vector((2.6, -0.6, 1.5))), 0.8 * M, P["ladder"], seg=40)
    cyl("pot", to_m(Vector((2.6, -0.6, 1.5))), to_m(Vector((2.6, -0.6, 2.2))), 0.35 * M, P["pot"], seg=32)
    random.seed(5)
    root = Vector((2.6, -0.6, 2.15))
    for i in range(14):
        a = random.uniform(0, 2 * math.pi)
        tilt = random.uniform(0.15, 0.6)
        Lf = random.uniform(1.2, 2.0)
        d = Vector((math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt)))
        side = Vector((-math.sin(a), math.cos(a), 0)) * 0.16
        vs = []
        for k in range(7):
            f = k / 6
            wdt = math.sin(math.pi * min(0.98, 0.15 + f * 0.85)) * (1 - 0.8 * f)
            c = root + d * Lf * f + Vector((0, 0, -0.25 * f * f * tilt * 3))
            vs += [to_m(c - side * wdt), to_m(c + side * wdt)]
        fs = [[2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2] for k in range(6)]
        lf = add_obj("leaf", vs, fs, P["leaf"], smooth=True)
        lf.modifiers.new("s", "SOLIDIFY").thickness = 0.004
    # paper pendant lamp hanging from the cap
    lp = Vector((3.0, -3.6, 9.4))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55 * M, location=to_m(lp), segments=32, ring_count=16)
    sp = bpy.context.active_object
    sp.data.materials.append(P["lamp"])
    for poly in sp.data.polygons:
        poly.use_smooth = True
    sp.visible_shadow = False
    cyl("cord", to_m(lp + Vector((0, 0, 0.5))), to_m(Vector((3.0, -3.6, 14.0))), 0.01 * M, P["black"])
    L = bpy.data.lights.new("pendant", "POINT")
    L.energy = 60
    L.color = (1.0, 0.82, 0.6)
    L.shadow_soft_size = 0.3
    lo = bpy.data.objects.new("pendant", L)
    S.COLL.objects.link(lo)
    lo.location = to_m(lp)


def build(scheme, P, cut=False):
    spec = SCHEMES[scheme]
    lower, upper, cap, frame = spec[:4]
    roof_struts = spec[4] if len(spec) > 4 else None
    for nm in NAMES:
        if cut and _cut_away(nm):
            continue
        poly = lining_poly(nm)
        if not poly:
            continue
        if nm.startswith("cap"):
            lining_piece(nm, poly, P[cap], "cap")
            continue
        lo = dedupe(clip_poly(poly, lambda p: DATUM - p.z))
        hi = dedupe(clip_poly(poly, lambda p: p.z - DATUM))
        if len(lo) >= 3:
            lining_piece(nm, lo, P[lower], "lo")
        if len(hi) >= 3:
            lining_piece(nm, hi, P[upper], "hi")
    cutters = []
    for kind, nm, uc, w, z0, z1 in OPENINGS:
        if cut and _cut_away(nm):
            continue
        cutters.append(opening_cutter(nm, uc, w, z0, z1))
        rm = upper if z1 > DATUM + 0.5 else lower
        if kind == "window":
            window_assembly(P, nm, uc, w, z0, z1, rm)
        else:
            door_assembly(P, nm, uc, w, z1, rm, glazed=(nm == "up3"))
    apply_cutters(cutters)
    # floor
    fl = [to_m(Vector((p.x, p.y, 0.0))) for p in section_at_z(0.0005)]
    ob = add_obj("floor", fl, [list(range(len(fl)))], P["floor_pine"] if scheme.endswith("pinefloor") else P["floor"])
    ob.modifiers.new("s", "SOLIDIFY").thickness = 0.3 * M
    # ground: the frame stands GROUND_Z clear of it, so the floor void reads in the cut
    g = 26.0
    add_obj("ground", [to_m(Vector(p)) for p in
                       ((-g, -g, GROUND_Z), (g, -g, GROUND_Z), (g, g, GROUND_Z), (-g, g, GROUND_Z))],
            [[0, 1, 2, 3]], P["poche"])
    # the washroom (up0) and east (up3) extensions, seen through their door portals
    for ext in EXT_GEOM:
        if not (cut and _cut_away(ext)):
            extension(P, ext, P["lime"], P["floor"])
    if roof_struts:
        struts(P, P[roof_struts], roof_only=True, steel=(roof_struts == "steel_paint"))
    if scheme in ("wainscot", "combo", "w_wainscot", "w_wainscot_pine", "w_wainscot_pinefloor"):
        datum_ledge(P, P["deodar"])
    elif scheme == "w_wainscot_limed":
        datum_ledge(P, P["limed_ledge"])
    elif scheme == "w_wainscot_paint":
        datum_ledge(P, P["sage_paint"])
    if frame:
        struts(P, P[frame])
    loft(P)
    furniture(P)


CUT_X = 0.0


def _cut_away(nm):
    """for the cutaway: drop faces whose centre lies at x > CUT_X"""
    verts = [f for f in FACES if f[0] == nm][0][3]
    cen = sum(verts, Vector()) / 3
    return cen.x > 2.0


def sun(direction_from, strength=4.0):
    s = bpy.data.lights.new("sun", "SUN")
    s.energy = strength
    s.angle = math.radians(1.5)
    s.color = (1.0, 0.95, 0.86)
    so = bpy.data.objects.new("sun", s)
    S.COLL.objects.link(so)
    d = -Vector(direction_from).normalized()
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def world_sky():
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[1].default_value = 0.45
    mr.inputs[2].default_value = 0.8
    nt.links.new(sep.outputs[2], mr.inputs[0])
    col = ramp(nt, mr.outputs[0], [(0.0, (0.2, 0.3, 0.12)), (0.12, (0.55, 0.62, 0.55)), (0.4, (0.62, 0.74, 0.9)),
                                    (1.0, (0.3, 0.48, 0.85))])
    nt.links.new(col, bg.inputs[0])
    bg.inputs[1].default_value = 1.6


def cam_look(loc, tgt, lens, shift=(0, 0)):
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens
    cam.sensor_width = 36
    cam.shift_x, cam.shift_y = shift
    cam.clip_start = 0.05
    co = bpy.data.objects.new("cam", cam)
    S.COLL.objects.link(co)
    co.location = to_m(Vector(loc))
    co.rotation_euler = (to_m(Vector(tgt)) - co.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co


# Camera positions are written as they always were, against the room rather than the
# compass, and turned with the building by ROT when the camera is made. So "hero"
# still looks at the same wall it always did.
VIEWS = {
    "hero": ((0.3, -7.7, 5.2), (0.0, 3.0, 7.6), 13.0),
    "back": ((4.6, -2.6, 5.0), (-4.0, 0.6, 6.6), 15.0),
    # outside, on the NNE bisector, so both extensions show at once
    "massing": ((42.8, 14.0, 22.0), (0.0, 0.0, 6.0), 35.0),
}
CUT_VIEW = ((26.0, -14.0, 20.0), (0.0, 0.5, 5.5), 30.0)


def main():
    # works both as `python3 x.py args` and `blender -b --python x.py -- args`
    argv = sys.argv[sys.argv.index('--'):] if '--' in sys.argv else sys.argv
    scheme, view, out = argv[1], argv[2], argv[3]
    samples = int(argv[4]) if len(argv) > 4 else 128
    W = int(argv[5]) if len(argv) > 5 else 1500
    H = int(argv[6]) if len(argv) > 6 else 1000
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S.COLL = bpy.context.scene.collection
    P = materials()
    cut = view in ("cut", "line_cut")
    build(scheme, P, cut=cut)
    loc, tgt, lens = CUT_VIEW if cut else VIEWS[view.replace("line_", "")]
    cam_look(rot_z(Vector(loc)), rot_z(Vector(tgt)), lens)
    if view.startswith("line"):
        line_render(out, W, H)
        print("WROTE", out)
        return
    world_sky()
    sun(sun_dir(SUN_BEARING, SUN_ALT), 4.5)
    render_settings(samples, W, H, -0.2)
    sc = bpy.context.scene
    sc.cycles.diffuse_bounces = 5
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)


if __name__ == "__main__":
    main()
