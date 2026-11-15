"""Read onshape/dome_struts.glb and write structure/out/frame_members.json.

Every part's mesh is resolved to world coordinates, then described by its own
principal axes: the long axis is the member centreline, the two short extents
are the section. Output is in FEET, origin at the floor centre (lower ring
datum), z up -- the same frame as code/dome.py and docs/onshape_frame_check.md.

Run:  .venv/bin/python structure/extract_frame.py
"""
import json, struct, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
GLB = ROOT / "onshape" / "dome_struts.glb"
OUT = ROOT / "structure" / "out" / "frame_members.json"
M2FT = 3.280839895

def load_glb(path):
    b = path.read_bytes()
    clen, _ = struct.unpack_from("<II", b, 12)
    j = json.loads(b[20:20 + clen])
    blen, _ = struct.unpack_from("<II", b, 20 + clen)
    binbuf = b[28 + clen: 28 + clen + blen]
    return j, binbuf

def accessor(j, binbuf, idx):
    a = j["accessors"][idx]
    bv = j["bufferViews"][a["bufferView"]]
    comp = {5126: "<f4", 5123: "<u2", 5125: "<u4", 5121: "<u1"}[a["componentType"]]
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0)
    if stride and stride != np.dtype(comp).itemsize * n:
        raw = np.frombuffer(binbuf, dtype=np.uint8, count=stride * a["count"], offset=off)
        raw = raw.reshape(a["count"], stride)[:, : np.dtype(comp).itemsize * n]
        return np.frombuffer(raw.tobytes(), dtype=comp).reshape(a["count"], n)
    return np.frombuffer(binbuf, dtype=comp, count=a["count"] * n, offset=off).reshape(a["count"], n)

def node_matrix(n):
    if "matrix" in n:
        return np.array(n["matrix"], float).reshape(4, 4).T
    M = np.eye(4)
    if "scale" in n:
        M = np.diag(list(n["scale"]) + [1.0]) @ M
    if "rotation" in n:
        x, y, z, w = n["rotation"]
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        R4 = np.eye(4); R4[:3, :3] = R
        M = R4 @ M
    if "translation" in n:
        T = np.eye(4); T[:3, 3] = n["translation"]
        M = T @ M
    return M

def main():
    j, binbuf = load_glb(GLB)
    mesh_cache = {}
    def mesh_points(mi):
        if mi not in mesh_cache:
            pts, tris = [], []
            base = 0
            for prim in j["meshes"][mi]["primitives"]:
                p = accessor(j, binbuf, prim["attributes"]["POSITION"]).astype(float)
                if "indices" in prim and prim.get("mode", 4) == 4:
                    ix = accessor(j, binbuf, prim["indices"]).astype(int).reshape(-1, 3) + base
                    tris.append(ix)
                pts.append(p); base += len(p)
            mesh_cache[mi] = (np.vstack(pts), np.vstack(tris) if tris else np.zeros((0, 3), int))
        return mesh_cache[mi]

    parts = []
    def walk(ni, M, name_stack):
        n = j["nodes"][ni]
        Mw = M @ node_matrix(n)
        nm = n.get("name", "")
        if "mesh" in n:
            p, tris = mesh_points(n["mesh"])
            pw = (Mw @ np.c_[p, np.ones(len(p))].T).T[:, :3]
            parts.append((nm, name_stack + [nm], pw, tris))
        for c in n.get("children", []):
            walk(c, Mw, name_stack + [nm])
    for r in j["scenes"][j.get("scene", 0)]["nodes"]:
        walk(r, np.eye(4), [])

    # glTF is y-up; Onshape export of a z-up model stores y-up. Detect: the apex
    # is the origin and the building hangs below it. Find the axis with all
    # coordinates <= ~0 and large extent.
    allp = np.vstack([p for _, _, p, _ in parts])
    mins, maxs = allp.min(0), allp.max(0)
    up = int(np.argmax(-(mins + maxs)))          # axis whose range is most negative
    out = []
    for nm, stack, pw, tris in parts:
        # volume by divergence theorem (m^3), before re-ordering axes
        vol = 0.0
        if len(tris):
            a, b, c = pw[tris[:, 0]], pw[tris[:, 1]], pw[tris[:, 2]]
            vol = abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)
        # to z-up, feet
        if up == 1:      # y-up  -> (x, -z, y)
            q = np.c_[pw[:, 0], -pw[:, 2], pw[:, 1]]
        elif up == 2:
            q = pw.copy()
        else:
            q = np.c_[pw[:, 1], pw[:, 2], pw[:, 0]]
        q = q * M2FT
        c = q.mean(0)
        # principal axes of the vertex cloud
        w, v = np.linalg.eigh(np.cov((q - c).T))
        order = np.argsort(w)[::-1]
        axes = v[:, order].T                          # rows: long, mid, short
        proj = (q - c) @ axes.T
        lo, hi = proj.min(0), proj.max(0)
        ext = hi - lo
        mid = c + ((lo + hi) / 2) @ axes
        p0 = mid - axes[0] * ext[0] / 2
        p1 = mid + axes[0] * ext[0] / 2
        out.append(dict(
            name=nm.replace("occurrence of ", ""), path=stack,
            p0=p0.tolist(), p1=p1.tolist(), length_ft=float(ext[0]),
            sec_in=[float(ext[1] * 12), float(ext[2] * 12)],
            axis_long=axes[0].tolist(), axis_mid=axes[1].tolist(), axis_short=axes[2].tolist(),
            centroid=c.tolist(), volume_cm3=float(vol * 1e6), nverts=int(len(q)),
        ))
    # shift origin from apex to floor datum: floor = lowest *lower-ring strut centreline* z.
    zs = sorted(set(round(min(m["p0"][2], m["p1"][2]), 2) for m in out if m["name"] == "12ft"))
    json.dump(dict(up_axis=up, members=out), open(OUT, "w"), indent=1)
    print(f"{len(out)} parts with geometry -> {OUT.relative_to(ROOT)}  (up axis {up})")
    print("bbox ft (apex-origin):", (mins * M2FT).round(2), (maxs * M2FT).round(2))

if __name__ == "__main__":
    main()
