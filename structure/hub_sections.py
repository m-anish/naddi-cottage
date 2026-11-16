"""Cut the cast hubs open and measure how much metal there is.

Reads the hub meshes from onshape/dome_struts.glb and slices each one with
half-planes that contain the hub's own axis, like cutting a cake. The area of
metal on each cut face is what has to carry force from the tubes on one side
of the cut to the tubes on the other. Writes structure/out/hub_sections.json.

    .venv/bin/python structure/hub_sections.py
"""
import json, pathlib
import numpy as np
from extract_frame import load_glb, accessor, GLB

OUT = pathlib.Path(__file__).resolve().parent / "out" / "hub_sections.json"


def mesh_of(j, binbuf, part):
    for n in j["nodes"]:
        if n.get("name") == part and "mesh" in n:
            pts, tris, base = [], [], 0
            for prim in j["meshes"][n["mesh"]]["primitives"]:
                p = accessor(j, binbuf, prim["attributes"]["POSITION"]).astype(float)
                ix = accessor(j, binbuf, prim["indices"]).astype(int).reshape(-1, 3) + base
                pts.append(p); tris.append(ix); base += len(p)
            return np.vstack(pts) * 1000.0, np.vstack(tris)          # mm
    raise KeyError(part)


def half_plane_area(P, T, axis_pt, axis_dir, theta):
    """Area of metal on the half-plane through the axis at angle theta (mm2)."""
    k = axis_dir / np.linalg.norm(axis_dir)
    ref = np.cross(k, [1.0, 0, 0])
    if np.linalg.norm(ref) < 0.3:
        ref = np.cross(k, [0, 1.0, 0])
    e1 = ref / np.linalg.norm(ref); e2 = np.cross(k, e1)
    r_hat = np.cos(theta) * e1 + np.sin(theta) * e2          # in-plane radial direction
    nrm = np.cross(k, r_hat)                                 # plane normal
    Q = P - axis_pt
    d = Q @ nrm
    area2 = 0.0
    for tri in T:
        dd = d[tri]
        if (dd > 0).all() or (dd < 0).all():
            continue
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            da, db = dd[a], dd[b]
            if (da > 0) != (db > 0):
                t = da / (da - db)
                pts.append(Q[tri[a]] + t * (Q[tri[b]] - Q[tri[a]]))
        if len(pts) != 2:
            continue
        # orient the cut segment with the triangle's outward normal
        tn = np.cross(Q[tri[1]] - Q[tri[0]], Q[tri[2]] - Q[tri[0]])
        dirn = np.cross(tn, nrm)
        p1, p2 = (pts[0], pts[1]) if (pts[1] - pts[0]) @ dirn > 0 else (pts[1], pts[0])
        u1, v1 = p1 @ r_hat, p1 @ k
        u2, v2 = p2 @ r_hat, p2 @ k
        if u1 <= 0 and u2 <= 0:
            continue
        if u1 < 0:                                            # clip at the axis
            s = u1 / (u1 - u2); u1, v1 = 0.0, v1 + s * (v2 - v1)
        if u2 < 0:
            s = u2 / (u2 - u1); u2, v2 = 0.0, v2 + s * (v1 - v2)
        area2 += u1 * v2 - u2 * v1
    return abs(area2) / 2


def main():
    j, binbuf = load_glb(GLB)
    out = {}
    for part in ("5-alt", "4-alt", "3-way-top"):
        P, T = mesh_of(j, binbuf, part)
        # the hub axis: the direction of least extent, through the centroid of the footprint
        c = P.mean(0)
        w, v = np.linalg.eigh(np.cov((P - c).T))
        k = v[:, 0]
        vol = abs(np.einsum("ij,ij->i", P[T[:, 0]], np.cross(P[T[:, 1]], P[T[:, 2]])).sum() / 6) / 1000.0
        if part == "5-alt":            # modelled about its own z axis, origin on the axis
            c, k = np.zeros(3), np.array([0, 0, 1.0])
        th = np.radians(np.arange(0, 360, 3))
        A = np.array([half_plane_area(P, T, c, k, t) for t in th])
        out[part] = dict(volume_cm3=vol, mass_kg=vol * 2.70 / 1000, min_mm2=float(A.min()), median_mm2=float(np.median(A)),
                         max_mm2=float(A.max()), at_deg=float(np.degrees(th[A.argmin()])), areas=A.round(0).tolist())
        print(f"{part:10s} volume {vol:6.0f} cm3 = {vol * 2.7 / 1000:4.1f} kg aluminium; cut-face metal area "
              f"min {A.min():5.0f}  median {np.median(A):5.0f}  max {A.max():5.0f} mm2")
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
