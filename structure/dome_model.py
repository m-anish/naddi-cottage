"""The Naddi dome as a structural model: nodes, tubes, supports and loads.

Geometry is the measured Onshape frame (docs/onshape_frame_check.md, and
structure/out/frame_members.json from extract_frame.py), idealised to hub
centres. Lengths here are in FEET as measured; build() converts to metres.
Origin at the floor centre (lower-ring datum), z up, plan angles as in the
frame check: lower ring at 18+72k degrees, upper ring at 54+72k, washroom at
198, east extension at 54.

Everything that is an assumption rather than a measurement is in INPUTS, so it
can be changed in one place when Anish confirms the real values.
"""
import numpy as np
from frame3d import Frame, Section

FT = 0.3048
G = 9.81

# ----------------------------------------------------------------------
# Inputs. "source" says where each number comes from.
# ----------------------------------------------------------------------
INPUTS = dict(
    # steel tube, mm -- from the Onshape strut part (Shell 1 = 2 mm)
    tube_b=52.07, tube_d=101.6, tube_t=2.0,
    fy=210e6, fu=330e6,            # YSt 210, the lowest IS 4923 grade: assumed
    # ground screw shaft standing 1'-3" above ground: size assumed
    stub_D=76.1, stub_t=3.2, stub_fy=240e6, stub_h_ft=1.25,
    # loads, Pa
    q_roof=180.0,                  # 80 mm PUF panel, tin both faces, + purlins (on slope)
    q_wall_now=180.0,              # fibre-cement planks + 1x2 purlins (as built)
    q_wall_lining=200.0,           # EPS + battens + 8 mm board + pine below (planned, D-01)
    q_floor_now=400.0,             # 20 mm fibre-cement board + floor steel
    q_floor_finish=150.0,          # underlay + wood floor (planned)
    q_floor_live=2000.0,           # dwelling, IS 875-2
    q_loft_dead=500.0,
    q_loft_live=2000.0,
    q_roof_live=400.0,             # IS 875-2: 0.75 less 0.02 per degree over 10, minimum 0.4
    snow_mu=0.613,                 # IS 875-4 shape factor, 37.4 deg: 0.8(60-37.4)/30
    steel_extra=1.15,              # hubs, bolts, cleats on top of tube weight
    # areas that are estimates
    eave_area_m2=2.0,              # per roof face: ~1.5 ft overhang along a 12 ft edge
    ext_roof_plan_m2=dict(W=2.8, E=3.7),   # roof wings over the two extensions
    loft_area_m2=8.6,              # two 72-degree sectors to the hangers
    floor_area_m2=23.2,            # main pentagon, 250 sq ft
    ext_floor_m2=dict(W=0.0, E=6.5),       # washroom floor is on the ground (W-06)
    floor_to_centre=0.25,          # share of the main floor carried by the centre screw: assumed
    # wind, IS 875-3
    Vb=39.0, k1=1.0, k2=1.0, Kd=0.9,
    # earthquake, IS 1893: zone V, short stiff building, low ductility assumed
    Z=0.36, R=2.0, Sa_g=2.5,
)

R_RING = 12.0 / (2 * np.sin(np.radians(36)))        # 10.2078 ft
Z_UP = 12.0 * np.sqrt((5 + np.sqrt(5)) / 10)        # 10.2078 ft
Z_TOP = Z_UP + 12.0 * np.sqrt((5 - np.sqrt(5)) / 10)  # 16.5165 ft
Z_C = Z_TOP - 12.0 * np.sin(np.radians(72))         # icosahedron centre, 5.10 ft
EDGE_TAN = (Z_TOP - Z_UP) / R_RING                  # fall of a roof hip per ft of plan

LOW = (18, 90, 162, 234, 306)
UPP = (54, 126, 198, 270, 342)


def pol(r, a, z):
    return np.array([r * np.cos(np.radians(a)), r * np.sin(np.radians(a)), z])


def node_table():
    n = {"A": np.array([0, 0, Z_TOP])}
    for a in LOW:
        n[f"L{a}"] = pol(R_RING, a, 0.0)
    for a in UPP:
        n[f"U{a}"] = pol(R_RING, a, Z_UP)
    # rafter ends: three plain eaves, two that run on to the extension corner hubs
    for a, r in ((126, 11.9), (270, 11.9), (342, 11.9), (198, 15.2), (54, 16.9)):
        n[f"T{a}"] = pol(r, a, Z_TOP - EDGE_TAN * r)
    # extension floor corners = tips of the cantilevered floor beams (measured)
    n["WF1"] = pol(14.30, 214.9, 0.0)   # washroom, west corner (beyond L234)
    n["WF2"] = pol(14.30, 181.1, 0.0)   # washroom, north corner (beyond L162)
    n["EF1"] = pol(15.95, 41.2, 0.0)    # east ext., beyond L18
    n["EF2"] = pol(15.95, 66.8, 0.0)    # east ext., beyond L90
    # loft: hanger feet and the central node (measured: 8'-5")
    for a in (126, 198, 270):
        n[f"H{a}"] = pol(9.86, a, 8.44)
    n["C"] = np.array([0, 0, 8.46])
    return n


def rhs(b, d, t, name, n=1):
    """Rectangular tube, mm. d is the depth (local z). n tubes side by side
    acting together but not bonded to one another."""
    A = b * d - (b - 2 * t) * (d - 2 * t)
    Iy = (b * d**3 - (b - 2 * t) * (d - 2 * t)**3) / 12
    Iz = (d * b**3 - (d - 2 * t) * (b - 2 * t)**3) / 12
    Am = (b - t) * (d - t); pm = 2 * ((b - t) + (d - t))
    J = 4 * Am**2 * t / pm
    return Section(name, n * A * 1e-6, n * Iy * 1e-12, n * Iz * 1e-12, n * J * 1e-12, mass=n * A * 1e-6 * 7850)


def chs(D, t, name):
    d = D - 2 * t
    A = np.pi * (D**2 - d**2) / 4
    I = np.pi * (D**4 - d**4) / 64
    return Section(name, A * 1e-6, I * 1e-12, I * 1e-12, 2 * I * 1e-12, mass=A * 1e-6 * 7850)


def build(joints="pinned", supports="stubs", tips=True, inp=None, nseg=6, uniform=False):
    """joints: 'pinned' (tubes that stop at a hub carry no moment into it) or
    'rigid'. supports: 'stubs' (ground-screw shafts modelled as short posts
    fixed at ground level) or 'pinned' (hub held directly).
    tips: are there ground screws under the extension floor corners?"""
    I = dict(INPUTS); I.update(inp or {})
    f = Frame()
    N = node_table()
    for k, v in N.items():
        f.node(k, v * FT)
    one = rhs(I["tube_b"], I["tube_d"], I["tube_t"], "2x4 tube")
    drop = chs(76.1, 3.2, "centre drop (3in pipe, wall assumed)")
    hang = Section("hanger (3x1.5 channel, assumed)", 780e-6, 70e-8, 12e-8, 0.5e-8, mass=6.1)
    stub = chs(I["stub_D"], I["stub_t"], "ground-screw shaft (assumed)")
    if uniform:                      # every member the same tube: for the CalculiX cross-check only
        drop = hang = stub = one
    pin = joints == "pinned"
    cz = np.array([0, 0, Z_C]) * FT

    def radial(a, b):
        mid = (f.xyz[f.names[a]] + f.xyz[f.names[b]]) / 2
        return mid - cz

    def add(name, nodes, sec, zdir, kind, n_tubes=1, rs=None, re=None):
        f.add_member(name, nodes, sec, zdir, kind=kind, nseg=nseg, n_tubes=n_tubes,
                     release_start=pin if rs is None else rs,
                     release_end=pin if re is None else re)

    # Every triangular face of the dome is its own frame of three tubes, each
    # tube turned so its 4 in depth is square to that face. Two faces meet at
    # every edge, so every edge carries two tubes side by side -- one per face.
    # They are joined only at the hubs. (Measured: see frame_members.json.)
    def fnormal(nodes):
        P = np.array([f.xyz[f.names[n]] for n in nodes])
        n = np.cross(P[1] - P[0], P[2] - P[0])
        n /= np.linalg.norm(n)
        return n if n @ (P.mean(0) - cz) > 0 else -n

    for az in LOW:
        a, b = (az - 36) % 360, (az + 36) % 360
        nr = fnormal(["A", f"U{a}", f"U{b}"])               # roof face over this side
        add(f"raf{a}_{az}", ["A", f"U{a}", f"T{a}"], one, nr, "rafter", re=False)
        add(f"raf{b}_{az}", ["A", f"U{b}", f"T{b}"], one, nr, "rafter", re=False)
        add(f"ur{a}_r", [f"U{a}", f"U{b}"], one, nr, "upper ring (roof tube)")
        nw = fnormal([f"U{a}", f"U{b}", f"L{az}"])          # "down" wall face
        add(f"ur{a}_w", [f"U{a}", f"U{b}"], one, nw, "upper ring (wall tube)")
        add(f"dg{az}_{a}_d", [f"L{az}", f"U{a}"], one, nw, "wall diagonal")
        add(f"dg{az}_{b}_d", [f"L{az}", f"U{b}"], one, nw, "wall diagonal")
    for az in UPP:                                          # "up" wall faces (two are open)
        a, b = (az - 36) % 360, (az + 36) % 360
        nw = fnormal([f"L{a}", f"L{b}", f"U{az}"])
        add(f"dg{a}_{az}_u", [f"L{a}", f"U{az}"], one, nw, "wall diagonal")
        add(f"dg{b}_{az}_u", [f"L{b}", f"U{az}"], one, nw, "wall diagonal")
    # floor ring: two plain tubes and three long beams that run on as cantilevers
    up = (0, 0, 1)
    add("lr18", ["L18", "L90"], one, up, "floor ring")
    add("lr162", ["L162", "L234"], one, up, "floor ring")
    add("fb26", ["EF2", "L90", "L162", "WF2"], one, up, "floor beam")
    add("fb18", ["L306", "L234", "WF1"], one, up, "floor beam")
    add("fb20", ["L306", "L18", "EF1"], one, up, "floor beam")
    # extension outer frames
    add("wfo", ["WF1", "WF2"], one, up, "extension floor edge")
    add("efo", ["EF1", "EF2"], one, up, "extension floor edge")
    for nm, a, b, az in (("wrk1", "WF1", "T198", 198), ("wrk2", "WF2", "T198", 198),
                         ("erk1", "EF1", "T54", 54), ("erk2", "EF2", "T54", 54)):
        add(nm, [a, b], one, pol(1, az, 0), "extension raker")
    # loft: central drop from the apex, three hangers, platform beams (assumed 2x4)
    add("drop", ["A", "C"], drop, (1, 0, 0), "loft centre drop", rs=False, re=False)
    for a in (126, 198, 270):
        add(f"hg{a}", [f"U{a}", f"H{a}"], hang, pol(1, a, 0), "loft hanger", rs=False, re=False)
        add(f"lb{a}", ["C", f"H{a}"], one, up, "loft beam (assumed)", rs=False, re=False)
    add("le126", ["H126", "H198"], one, up, "loft beam (assumed)", rs=False, re=False)
    add("le198", ["H198", "H270"], one, up, "loft beam (assumed)", rs=False, re=False)

    sup = [f"L{a}" for a in LOW] + (["WF1", "WF2", "EF1", "EF2"] if tips else [])
    for s in sup:
        if supports == "stubs":
            g = f.node("G" + s, f.xyz[f.names[s]] - np.array([0, 0, I["stub_h_ft"] * FT]))
            f.add_member("st" + s, ["G" + s, s], stub, (1, 0, 0), kind="ground screw", nseg=2,
                         release_start=False, release_end=True)
            f.fix("G" + s)
        else:
            f.fix(s, (0, 1, 2))
    f.assemble()
    f.support_nodes = sup
    f.supports_mode = supports
    f.inputs = I
    return f


# ----------------------------------------------------------------------
# Surfaces that collect load, and which tubes they hand it to
# ----------------------------------------------------------------------
def _poly(f, names):
    return np.array([f.xyz[f.names[n]] for n in names])


def _area_normal(P):
    n = np.zeros(3)
    for i in range(len(P)):
        n += np.cross(P[i], P[(i + 1) % len(P)])
    A = np.linalg.norm(n) / 2
    return A, n / np.linalg.norm(n)


def span(f, member, a, b):
    m = f.members[member]
    sa, sb = m.node_s[m.nodes.index(a)], m.node_s[m.nodes.index(b)]
    return (min(sa, sb), max(sa, sb))


def faces(f):
    """Each face: name, kind, area (m2), outward unit normal, plan azimuth of
    that normal, plan area, and shares = [(member, fraction, shape, sa, sb)].
    shape 'u' = uniform along the span, 'tri' = growing from zero at sa."""
    I = f.inputs
    out = []
    cz = np.array([0, 0, Z_C]) * FT

    def face(name, kind, nodes, shares, ref=cz, area=None, closed=True):
        P = _poly(f, nodes)
        A, n = _area_normal(P)
        if n @ (P.mean(0) - ref) < 0:
            n = -n
        A = area if area is not None else A
        az = np.degrees(np.arctan2(n[1], n[0])) % 360
        out.append(dict(name=name, kind=kind, area=A, n=n, az=az, plan=A * abs(n[2]),
                        shares=shares, closed=closed, nodes=nodes))

    ring_edge = {54: ("lr18", "L18", "L90"), 126: ("fb26", "L90", "L162"), 198: ("lr162", "L162", "L234"),
                 270: ("fb18", "L306", "L234"), 342: ("fb20", "L306", "L18")}
    for az in LOW:                      # roof faces sit over the "down" wall faces
        a, b = (az - 36) % 360, (az + 36) % 360
        ra, rb, ur = f"raf{a}_{az}", f"raf{b}_{az}", f"ur{a}_r"
        face(f"roof{az}", "roof", ["A", f"U{a}", f"U{b}"],
             [(ra, 0.4, "tri") + span(f, ra, "A", f"U{a}"), (rb, 0.4, "tri") + span(f, rb, "A", f"U{b}"),
              (ur, 0.2, "u") + span(f, ur, f"U{a}", f"U{b}")])
        sa = span(f, ra, f"U{a}", f"T{a}")[0]; sb = span(f, rb, f"U{b}", f"T{b}")[0]
        face(f"eave{az}", "eave", ["A", f"U{a}", f"U{b}"],
             [(ur, 0.6, "u") + span(f, ur, f"U{a}", f"U{b}"),
              (ra, 0.2, "u", sa, sa + 0.5), (rb, 0.2, "u", sb, sb + 0.5)],
             area=I["eave_area_m2"], closed=False)
        uw, da, db = f"ur{a}_w", f"dg{az}_{a}_d", f"dg{az}_{b}_d"
        face(f"wall{az}", "wall", [f"U{a}", f"U{b}", f"L{az}"],
             [(uw, 1 / 3, "u") + span(f, uw, f"U{a}", f"U{b}"),
              (da, 1 / 3, "u") + span(f, da, f"L{az}", f"U{a}"),
              (db, 1 / 3, "u") + span(f, db, f"L{az}", f"U{b}")])
    for az in (126, 270, 342):          # the three closed "up" wall faces
        a, b = (az - 36) % 360, (az + 36) % 360
        m, n1, n2 = ring_edge[az]
        da, db = f"dg{a}_{az}_u", f"dg{b}_{az}_u"
        # the floor-level tube is held sideways by the floor deck, so the
        # sideways part of its share goes straight to the hubs at its ends
        face(f"wall{az}", "wall", [f"L{a}", f"L{b}", f"U{az}"],
             [(m, 1 / 3, "floor", n1, n2) + span(f, m, n1, n2),
              (da, 1 / 3, "u") + span(f, da, f"L{a}", f"U{az}"),
              (db, 1 / 3, "u") + span(f, db, f"L{b}", f"U{az}")])
    # the two extensions: a back wall, two side walls, and a roof wing along the ridge
    ext = dict(W=dict(az=198, T="T198", U="U198", back=("WF1", "WF2"), fo="wfo", rk=("wrk1", "wrk2"),
                      sides=(("L234", "WF1", "fb18", "wrk1"), ("L162", "WF2", "fb26", "wrk2"))),
               E=dict(az=54, T="T54", U="U54", back=("EF1", "EF2"), fo="efo", rk=("erk1", "erk2"),
                      sides=(("L18", "EF1", "fb20", "erk1"), ("L90", "EF2", "fb26", "erk2"))))
    for key, e in ext.items():
        ref = _poly(f, [e["U"], e["T"], e["back"][0], e["back"][1], e["sides"][0][0], e["sides"][1][0]]).mean(0)
        face(f"ext{key}_back", "wall", [e["back"][0], e["back"][1], e["T"]],
             [(e["rk"][0], 1 / 3, "u") + span(f, e["rk"][0], e["back"][0], e["T"]),
              (e["rk"][1], 1 / 3, "u") + span(f, e["rk"][1], e["back"][1], e["T"]),
              (e["fo"], 1 / 3, "u") + span(f, e["fo"], e["back"][0], e["back"][1])], ref=ref)
        rafs = []
        for i, (L, F, fb, rk) in enumerate(e["sides"]):
            la = int(L[1:])
            # the roof face on this side of the ridge, and its rafter tube
            faz = min(LOW, key=lambda z: adiff(z, la) + adiff(z, e["az"]))
            raf = f"raf{e['az']}_{faz}"; rafs.append(raf)
            d = f"dg{la}_{e['az']}_u"
            face(f"ext{key}_side{i + 1}", "wall", [L, F, e["T"], e["U"]],
                 [(fb, 0.25, "u") + span(f, fb, L, F), (rk, 0.25, "u") + span(f, rk, F, e["T"]),
                  (raf, 0.25, "u") + span(f, raf, e["U"], e["T"]),
                  (d, 0.25, "u") + span(f, d, L, e["U"])], ref=ref)
        out.append(dict(name=f"ext{key}_roof", kind="extroof", area=I["ext_roof_plan_m2"][key] / np.cos(np.radians(37.4)),
                        n=np.array([0, 0, 1.0]), az=e["az"], plan=I["ext_roof_plan_m2"][key], closed=False,
                        shares=[(r, 0.5, "u") + span(f, r, e["U"], e["T"]) for r in rafs], nodes=[e["U"], e["T"]]))
    return out


# When True, the cladding of a triangular face is trusted to carry any load
# lying IN the plane of that face (as a stiff sheet) to the three corner hubs,
# so the tubes only bend the strong way. When False the bare tubes do it all.
DIAPHRAGM = False


def _push(f, lines, fc, F, nodal=None):
    """Hand a total force vector F (N) on a face to its tubes as line loads."""
    F = np.asarray(F, float)
    if DIAPHRAGM and nodal is not None and fc["kind"] in ("roof", "eave", "wall") and len(fc["nodes"]) == 3:
        n = fc["n"]
        Ft = F - (F @ n) * n
        for nd in fc["nodes"]:
            nodal[nd] = nodal.get(nd, 0) + Ft / 3
        F = (F @ n) * n
    for sh in fc["shares"]:
        m, frac, shape = sh[:3]
        sa, sb = sh[-2:]
        L = sb - sa
        if shape == "u":
            q = F * frac / L
            lines.append((m, q, q, sa, sb))
        elif shape == "floor":          # vertical part along the tube, sideways part to its end hubs
            q = np.array([0, 0, F[2]]) * frac / L
            lines.append((m, q, q, sa, sb))
            if nodal is not None:
                for n in sh[3:5]:
                    nodal[n] = nodal.get(n, 0) + np.array([F[0], F[1], 0]) * frac / 2
        else:
            lines.append((m, np.zeros(3), 2 * F * frac / L, sa, sb))


def wall_cp(d):
    """External pressure coefficient on a wall facet, d = angle (deg) between
    the facet's outward normal and the direction the wind comes from."""
    return float(np.interp(abs(d), [0, 36, 72, 108, 144, 180], [0.8, 0.5, -0.7, -0.7, -0.5, -0.5]))


def roof_cp(d, variant):
    first = dict(lift=(-0.2, -0.3), press=(0.3, 0.2))[variant]
    return float(np.interp(abs(d), [0, 36, 72, 108, 144, 180], [first[0], first[1], -0.8, -0.8, -0.5, -0.5]))


def adiff(a, b):
    return abs((a - b + 180) % 360 - 180)


def service_combos(I, s0_kpa=1.5, k3=1.36):
    """Unfactored (working-load) combinations, for the ground screws: soil
    capacities are normally quoted as working loads."""
    pd = wind_pressure(I, k3) / 1000.0
    Dfull = ["D_steel", "D_roof", "D_wall", "D_lining", "D_floor", "D_floorfin", "D_loft"]
    Dmin = ["D_steel", "D_roof", "D_wall", "D_floor"]
    Live = ["L_floor", "L_loft"]
    C = {"dead only (finished)": {k: 1.0 for k in Dfull},
         "dead only (today)": {k: 1.0 for k in Dmin}}
    c = {k: 1.0 for k in Dfull + Live}; c["S_bal"] = s0_kpa
    C["dead + live + snow"] = c
    for th in range(18, 360, 36):
        c = {k: 1.0 for k in Dmin}; c[f"W{th}_lift"] = pd; c["W_int"] = 0.2 * pd
        C[f"today's weight + wind from {th} (uplift)"] = c
        c = {k: 1.0 for k in Dfull}; c[f"W{th}_press"] = pd; c["W_int"] = -0.2 * pd
        C[f"finished weight + wind from {th}"] = c
        c = {k: 1.0 for k in Dfull + Live}; c["S_bal"] = 0.75 * s0_kpa; c[f"W{th}_press"] = 0.75 * pd; c["W_int"] = -0.15 * pd
        for k in Live:
            c[k] = 0.75
        C[f"dead + 0.75(live + snow + wind from {th})"] = c
    return C


def load_cases(f):
    """Unfactored basic load cases -> {name: (nodal dict, line list)}.
    Snow is per 1 kPa of ground snow; wind per 1 kPa of design pressure;
    'mass' cases can be pointed sideways to make the earthquake loads."""
    I = f.inputs
    FC = faces(f)
    cases = {}
    down = np.array([0, 0, -1.0])

    def gravity_like(direction):
        """Dead and live weights acting along `direction` (down for gravity,
        horizontal for an earthquake push)."""
        c = {}
        d = np.asarray(direction, float)
        # steel
        lines = []
        for m in f.members.values():
            if m.kind == "ground screw":
                continue
            q = m.sec.mass * G * I["steel_extra"] * d
            lines.append((m.name, q, q))
        c["D_steel"] = ({}, lines)
        for key, kinds, q in (("D_roof", ("roof", "eave", "extroof"), I["q_roof"]),
                              ("D_wall", ("wall",), I["q_wall_now"]),
                              ("D_lining", ("wall",), I["q_wall_lining"])):
            lines, nod = [], {}
            for fc in FC:
                if fc["kind"] in kinds:
                    _push(f, lines, fc, q * fc["area"] * d, nod)
            c[key] = (nod, lines)
        # floor: main pentagon to the five ring hubs and the centre screw
        # (which is not in the frame model); east extension to its four corners
        def floor(q):
            nod = {}
            Fm = q * I["floor_area_m2"] * (1 - I["floor_to_centre"]) / 5
            for a in LOW:
                nod[f"L{a}"] = Fm * d
            Fe = q * I["ext_floor_m2"]["E"] / 4
            for n in ("EF1", "EF2", "L18", "L90"):
                nod[n] = nod.get(n, 0) + Fe * d
            return nod
        c["D_floor"] = (floor(I["q_floor_now"]), [])
        c["D_floorfin"] = (floor(I["q_floor_finish"]), [])
        c["L_floor"] = (floor(I["q_floor_live"]), [])
        def loft(q):
            W = q * I["loft_area_m2"]
            return {"C": W / 3 * d, "H198": W / 3 * d, "H126": W / 6 * d, "H270": W / 6 * d}
        c["D_loft"] = (loft(I["q_loft_dead"]), [])
        c["L_loft"] = (loft(I["q_loft_live"]), [])
        return c

    cases.update(gravity_like(down))
    for tag, d in (("X", (1, 0, 0)), ("Y", (0, 1, 0))):
        for k, v in gravity_like(d).items():
            cases[f"E{tag}_{k}"] = v
    # roof live and snow act on plan area, straight down
    lines, nod = [], {}
    for fc in FC:
        if fc["kind"] in ("roof", "eave", "extroof"):
            _push(f, lines, fc, I["q_roof_live"] * fc["plan"] * down, nod)
    cases["L_roof"] = (nod, lines)
    lines, nod = [], {}
    for fc in FC:
        if fc["kind"] in ("roof", "eave", "extroof"):
            _push(f, lines, fc, 1000.0 * I["snow_mu"] * fc["plan"] * down, nod)
    cases["S_bal"] = (nod, lines)
    for az0 in (198, 54, 306):          # drifted: full on the lee side, half elsewhere
        lines, nod = [], {}
        for fc in FC:
            if fc["kind"] in ("roof", "eave", "extroof"):
                k = 1.0 if adiff(fc["az"], az0) <= 90 else 0.5
                _push(f, lines, fc, 1000.0 * I["snow_mu"] * k * fc["plan"] * down, nod)
        cases[f"S_drift{az0}"] = (nod, lines)
    # wind, per 1 kPa. External pressure pushes inward (-n) when Cp is positive.
    wall_az = {fc["name"]: fc["az"] for fc in FC if fc["kind"] == "wall"}
    for th in range(18, 360, 36):
        for var in ("lift", "press"):
            lines, wnod = [], {}
            for fc in FC:
                d = adiff(fc["az"], th)
                if fc["kind"] == "wall":
                    cp = wall_cp(d)
                    _push(f, lines, fc, -cp * 1000.0 * fc["area"] * fc["n"], wnod)
                elif fc["kind"] == "roof":
                    _push(f, lines, fc, -roof_cp(d, var) * 1000.0 * fc["area"] * fc["n"], wnod)
                elif fc["kind"] == "eave":      # top as the roof; underside sees the wall pressure below
                    under = max(wall_cp(d), 0.0)
                    _push(f, lines, fc, -(roof_cp(d, var) - under) * 1000.0 * fc["area"] * fc["n"], wnod)
                elif fc["kind"] == "extroof":   # two wings either side of the ridge: vertical part only
                    cp = 0.5 * (roof_cp(adiff(fc["az"] - 36, th), var) + roof_cp(adiff(fc["az"] + 36, th), var))
                    _push(f, lines, fc, -cp * 1000.0 * fc["plan"] * np.array([0, 0, 1.0]))
            cases[f"W{th}_{var}"] = (wnod, lines)
    # internal pressure, per 1 kPa, pushing every enclosing surface outward;
    # the floor's share goes straight down into its supports
    lines, nod = [], {}
    for fc in FC:
        if fc["closed"]:
            _push(f, lines, fc, 1000.0 * fc["area"] * fc["n"], nod)
    Fm = 1000.0 * I["floor_area_m2"] * (1 - I["floor_to_centre"]) / 5
    for a in LOW:
        nod[f"L{a}"] = Fm * down
    Fe = 1000.0 * I["ext_floor_m2"]["E"] / 4
    for n in ("EF1", "EF2", "L18", "L90"):
        nod[n] = nod.get(n, 0) + Fe * down
    cases["W_int"] = (nod, lines)
    return cases, FC


def wind_pressure(I, k3):
    Vz = I["Vb"] * I["k1"] * I["k2"] * k3
    return I["Kd"] * 0.6 * Vz**2          # Pa


def seismic_Ah(I):
    return I["Z"] / 2 * I["Sa_g"] / I["R"]


def combos(I, s0_kpa=1.5, k3=1.36):
    """Factored combinations (IS 800:2007 Table 4). Returns {name: {case: factor}}."""
    pd = wind_pressure(I, k3) / 1000.0
    Ah = seismic_Ah(I)
    Dfull = ["D_steel", "D_roof", "D_wall", "D_lining", "D_floor", "D_floorfin", "D_loft"]
    Dmin = ["D_steel", "D_roof", "D_wall", "D_floor"]          # as it stands today, unlined
    Live = ["L_floor", "L_loft"]
    C = {}

    def mk(name, parts):
        c = {}
        for cases, fac in parts:
            for k in cases:
                c[k] = c.get(k, 0) + fac
        C[name] = c

    mk("G: dead + live", [(Dfull, 1.5), (Live, 1.5), (["L_roof"], 1.5)])
    mk("S: dead + live + snow", [(Dfull, 1.5), (Live, 1.5), (["S_bal"], 1.5 * s0_kpa)])
    for az in (198, 54, 306):
        mk(f"S: drifted snow, lee side {az}", [(Dfull, 1.5), (Live, 1.5), ([f"S_drift{az}"], 1.5 * s0_kpa)])
    for th in range(18, 360, 36):
        for var in ("lift", "press"):
            for ci in (0.2, -0.2):
                mk(f"W: wind from {th}, roof {var}, inside {ci:+.1f}",
                   [(Dfull, 1.5), ([f"W{th}_{var}"], 1.5 * pd), (["W_int"], 1.5 * pd * ci)])
        mk(f"U: light building + wind from {th} (uplift)",
           [(Dmin, 0.9), ([f"W{th}_lift"], 1.5 * pd), (["W_int"], 1.5 * pd * 0.2)])
        mk(f"WS: wind from {th} + snow + live",
           [(Dfull, 1.2), (Live, 1.2), (["S_bal"], 1.2 * s0_kpa), ([f"W{th}_press"], 1.2 * pd), (["W_int"], -1.2 * pd * 0.2)])
    for tag, sx, sy in (("+x", 1, 0), ("-x", -1, 0), ("+y", 0, 1), ("-y", 0, -1),
                        ("198", np.cos(np.radians(198)), np.sin(np.radians(198))),
                        ("18", np.cos(np.radians(18)), np.sin(np.radians(18)))):
        def eq(dead, live_frac, fac):
            parts = []
            for k in dead:
                parts += [([f"EX_{k}"], fac * Ah * sx), ([f"EY_{k}"], fac * Ah * sy)]
            for k in Live:
                parts += [([f"EX_{k}"], fac * Ah * sx * live_frac), ([f"EY_{k}"], fac * Ah * sy * live_frac)]
            return parts
        mk(f"E: earthquake {tag}, full dead", [(Dfull, 1.5)] + eq(Dfull, 0.25, 1.5))
        mk(f"E: earthquake {tag}, light building", [(Dmin, 0.9)] + eq(Dmin, 0.0, 1.5))
        mk(f"E: earthquake {tag} + live", [(Dfull, 1.2), (Live, 1.2)] + eq(Dfull, 0.25, 1.2))
    return C
