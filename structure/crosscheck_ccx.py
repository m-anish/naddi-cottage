"""Independent check of the frame solver against CalculiX.

CalculiX is the finite-element solver that ships inside FreeCAD (its FEM
workbench drives it). Here the same dome frame -- same nodes, same tubes, same
orientation of every tube -- is written out as a CalculiX input deck by hand
and solved, and the answers are compared with frame3d.py.

The two programs work very differently: frame3d uses classical beam theory,
CalculiX blows every beam up into 3D solid elements with a hollow box section.
Agreement within a few per cent therefore says the geometry, the stiffness
assembly and the tube orientations are right.

    .venv/bin/python structure/crosscheck_ccx.py
"""
import pathlib, subprocess, shutil, re, json
import numpy as np
import dome_model as dm

CCX = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"
HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / "out" / "ccx"


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    f = dm.build(joints="rigid", supports="pinned", uniform=True, nseg=6, floor_tie=False)
    I = f.inputs
    # a made-up but demanding load: gravity-like, a sideways shove, and a twist
    nodal = {"A": (2e3, 0, -10e3)}
    for a in dm.UPP:
        nodal[f"U{a}"] = (3e3, 1e3, -5e3)
    nodal["T126"] = (0, 0, -2e3); nodal["T198"] = (0, 2e3, -3e3); nodal["C"] = (0, 0, -6e3)
    nodal["H198"] = (1e3, 0, -4e3)
    F, elq = f.load_vector(nodal)
    u, R = f.solve(F)

    lines = ["*NODE, NSET=NALL"]
    nn = len(f.xyz)
    for i, p in enumerate(f.xyz):
        lines.append(f"{i + 1}, {p[0]:.9e}, {p[1]:.9e}, {p[2]:.9e}")
    mids = []
    for ei, e in enumerate(f.elems):
        pm = (f.xyz[e.n1] + f.xyz[e.n2]) / 2
        mids.append(nn + ei + 1)
        lines.append(f"{nn + ei + 1}, {pm[0]:.9e}, {pm[1]:.9e}, {pm[2]:.9e}")
    for m in f.members.values():
        lines.append(f"*ELEMENT, TYPE=B32R, ELSET=E_{m.name.upper()}")
        for ei in m.elems:
            e = f.elems[ei]
            lines.append(f"{ei + 1}, {e.n1 + 1}, {mids[ei]}, {e.n2 + 1}")
    lines += ["*MATERIAL, NAME=STEEL", "*ELASTIC", "2.0e11, 0.3"]
    b, d, t = I["tube_b"] / 1e3, I["tube_d"] / 1e3, I["tube_t"] / 1e3
    for m in f.members.values():
        z = f.elems[m.elems[0]].T[2]
        lines += [f"*BEAM SECTION, ELSET=E_{m.name.upper()}, MATERIAL=STEEL, SECTION=BOX",
                  f"{d:.6f}, {b:.6f}, {t:.6f}, {t:.6f}, {t:.6f}, {t:.6f}",
                  f"{z[0]:.9f}, {z[1]:.9f}, {z[2]:.9f}"]
    sup = [f.names[s] + 1 for s in f.support_nodes]
    chk_names = ["A", "C", "H198", "T126", "T198", "T54"] + [f"U{a}" for a in dm.UPP]
    chk = [f.names[n] + 1 for n in chk_names]
    lines += ["*NSET, NSET=NSUP", ", ".join(map(str, sup)), "*NSET, NSET=NCHK", ", ".join(map(str, chk))]
    lines += ["*BOUNDARY"] + [f"{n}, 1, 3" for n in sup]
    lines += ["*STEP", "*STATIC", "*CLOAD"]
    for name, v in nodal.items():
        for j, val in enumerate(v):
            if val:
                lines.append(f"{f.names[name] + 1}, {j + 1}, {val:.6e}")
    lines += ["*NODE PRINT, NSET=NCHK", "U", "*NODE PRINT, NSET=NSUP, TOTALS=YES", "RF", "*END STEP"]
    (WORK / "dome.inp").write_text("\n".join(lines) + "\n")
    out = subprocess.run([CCX, "dome"], cwd=WORK, capture_output=True, text=True)
    ver = re.search(r"CalculiX Version ([\d.]+)", out.stdout)
    if not (WORK / "dome.dat").exists():
        print(out.stdout[-3000:], out.stderr[-2000:]); raise SystemExit("CalculiX did not produce results")
    dat = (WORK / "dome.dat").read_text().splitlines()
    U, RF, mode = {}, {}, None
    for ln in dat:
        if "displacements" in ln: mode = "U"; continue
        if "forces (fx,fy,fz)" in ln: mode = "RF"; continue
        if "total force" in ln: mode = None; continue
        p = ln.split()
        if len(p) == 4 and mode:
            try:
                (U if mode == "U" else RF)[int(p[0])] = np.array([float(x) for x in p[1:]])
            except ValueError:
                pass
    print(f"CalculiX {ver.group(1) if ver else '?'}: {len(f.elems)} beam elements, {len(f.xyz)} nodes\n")
    print(f"{'node':6s} {'frame3d  ux, uy, uz (mm)':>32s}   {'CalculiX  ux, uy, uz (mm)':>32s}   diff")
    worst = 0.0
    rows = []
    for name, nid in zip(chk_names, chk):
        a = u[(nid - 1) * 6:(nid - 1) * 6 + 3] * 1e3
        c = U[nid] * 1e3
        rel = np.linalg.norm(a - c) / np.linalg.norm(c)
        worst = max(worst, rel)
        rows.append((name, a.tolist(), c.tolist(), rel))
        print(f"{name:6s} {a[0]:10.3f} {a[1]:10.3f} {a[2]:10.3f}   {c[0]:10.3f} {c[1]:10.3f} {c[2]:10.3f}   {rel * 100:5.1f}%")
    print(f"\n{'support':8s} {'frame3d  Rx, Ry, Rz (kN)':>30s}   {'CalculiX  Rx, Ry, Rz (kN)':>30s}")
    worst_r = 0.0
    scale = max(np.linalg.norm(RF[n]) for n in sup)
    for s, nid in zip(f.support_nodes, sup):
        a = R[(nid - 1) * 6:(nid - 1) * 6 + 3] / 1e3
        c = RF[nid] / 1e3
        worst_r = max(worst_r, np.linalg.norm(a - c) * 1e3 / scale)
        print(f"{s:8s} {a[0]:9.3f} {a[1]:9.3f} {a[2]:9.3f}   {c[0]:9.3f} {c[1]:9.3f} {c[2]:9.3f}")
    print(f"\nworst displacement difference {worst * 100:.1f}%; worst reaction difference {worst_r * 100:.1f}% of the largest reaction")
    json.dump(dict(ccx_version=ver.group(1) if ver else None, worst_disp_rel=worst, worst_reaction_rel=worst_r,
                   rows=rows), open(HERE / "out" / "crosscheck_ccx.json", "w"), indent=1)


if __name__ == "__main__":
    main()
