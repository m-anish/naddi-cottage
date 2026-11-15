"""Checks of the frame solver against textbook answers.

Run:  .venv/bin/python structure/verify.py
Every line should say OK. These are the reasons to trust frame3d.py before it
is pointed at the dome.
"""
import numpy as np
from frame3d import Frame, Section, stations

S = Section("test", A=6.0e-4, Iy=8.0e-7, Iz=3.0e-7, J=6.0e-7)
E = S.E
ok_all = True

def check(label, got, want, tol=1e-3):
    global ok_all
    err = abs(got - want) / (abs(want) if want else 1.0)
    ok = err < tol
    ok_all &= ok
    print(f"{'OK  ' if ok else 'FAIL'} {label:58s} got {got: .6g}  want {want: .6g}  ({err * 100:.3f}%)")

L, P, w = 3.0, 1000.0, 500.0

# 1. cantilever, tip load in the depth direction and across it
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=4); f.fix("a"); f.assemble()
F, q = f.load_vector(nodal={"b": (0, 0, -P)}); u, R = f.solve(F)
check("cantilever tip deflection, strong way  PL3/3EI", -u[f.names["b"] * 6 + 2], P * L**3 / (3 * E * S.Iy))
F, q = f.load_vector(nodal={"b": (0, P, 0)}); u, R = f.solve(F)
check("cantilever tip deflection, weak way", u[f.names["b"] * 6 + 1], P * L**3 / (3 * E * S.Iz))
F, q = f.load_vector(line=[("m", (0, 0, -w), (0, 0, -w))]); u, R = f.solve(F)
check("cantilever under UDL  wL4/8EI", -u[f.names["b"] * 6 + 2], w * L**4 / (8 * E * S.Iy))
st = stations(f.end_forces(u, q))
check("cantilever root moment  wL2/2", abs(st[0, 0, 4]), w * L**2 / 2)

# 2. simply supported beam under UDL, made with pinned-end releases
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=4, release_start=True, release_end=True)
f.fix("a"); f.fix("b"); f.assemble()
F, q = f.load_vector(line=[("m", (0, 0, -w), (0, 0, -w))]); u, R = f.solve(F)
mid = f.names["m#0.2"]
check("simply supported midspan deflection  5wL4/384EI", -u[mid * 6 + 2], 5 * w * L**4 / (384 * E * S.Iy))
st = stations(f.end_forces(u, q))
check("simply supported midspan moment  wL2/8", abs(st[1, 1, 4]), w * L**2 / 8)
check("released end carries no moment", abs(st[0, 0, 4]) + 1.0, 1.0)

# 3. fixed-fixed beam under UDL
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=4); f.fix("a"); f.fix("b"); f.assemble()
F, q = f.load_vector(line=[("m", (0, 0, -w), (0, 0, -w))]); u, R = f.solve(F)
st = stations(f.end_forces(u, q))
check("fixed-fixed end moment  wL2/12", abs(st[0, 0, 4]), w * L**2 / 12)
check("fixed-fixed midspan moment  wL2/24", abs(st[1, 1, 4]), w * L**2 / 24)

# 4. propped cantilever: prop reaction 3wL/8
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=4); f.fix("a"); f.fix("b", (0, 1, 2)); f.assemble()
F, q = f.load_vector(line=[("m", (0, 0, -w), (0, 0, -w))]); u, R = f.solve(F)
check("propped cantilever prop reaction  3wL/8", R[f.names["b"] * 6 + 2], 3 * w * L / 8)

# 5. triangular line load on a simply supported beam: reactions W/3 and 2W/3
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=24, release_start=True, release_end=True)
f.fix("a"); f.fix("b"); f.assemble()
F, q = f.load_vector(line=[("m", (0, 0, 0), (0, 0, -w))]); u, R = f.solve(F)
W = w * L / 2
check("triangular load, reaction at the light end  W/3", R[f.names["a"] * 6 + 2], W / 3, 2e-3)
check("triangular load, reaction at the heavy end  2W/3", R[f.names["b"] * 6 + 2], 2 * W / 3, 2e-3)

# 6. five-legged pyramid, pinned, load on the apex: N = P / (5 sin a)
f = Frame(); h, r = 2.0, 3.0
f.node("apex", (0, 0, h))
for k in range(5):
    a = np.radians(72 * k)
    f.node(f"b{k}", (r * np.cos(a), r * np.sin(a), 0)); f.fix(f"b{k}")
    f.add_member(f"leg{k}", ["apex", f"b{k}"], S, (0, 0, 1), nseg=2, release_start=True, release_end=True)
f.assemble()
F, q = f.load_vector(nodal={"apex": (0, 0, -P)}); u, R = f.solve(F)
st = stations(f.end_forces(u, q))
check("pyramid leg force  P/(5 sin a)", -st[0, 0, 0], P / (5 * h / np.hypot(h, r)))
check("pyramid: reactions add up to the load", sum(R[f.names[f'b{k}'] * 6 + 2] for k in range(5)), P)

# 7. a cantilever pointing in an arbitrary direction behaves the same
f = Frame(); d = np.array([1.0, 2.0, 0.7]); d /= np.linalg.norm(d)
zref = np.cross(d, [0.3, -0.2, 1.0]); zref /= np.linalg.norm(zref)
f.node("a", (0, 0, 0)); f.node("b", d * L)
f.add_member("m", ["a", "b"], S, zref, nseg=3); f.fix("a"); f.assemble()
F, q = f.load_vector(nodal={"b": tuple(zref * P)}); u, R = f.solve(F)
check("skew cantilever, load along its depth axis", u[f.names["b"] * 6: f.names["b"] * 6 + 3] @ zref, P * L**3 / (3 * E * S.Iy))
yref = np.cross(zref, d)
F, q = f.load_vector(nodal={"b": tuple(yref * P)}); u, R = f.solve(F)
check("skew cantilever, load across its depth axis", u[f.names["b"] * 6: f.names["b"] * 6 + 3] @ yref, P * L**3 / (3 * E * S.Iz))

# 8. torsion of a cantilever: twist = T L / G J
f = Frame(); f.node("a", (0, 0, 0)); f.node("b", (L, 0, 0))
f.add_member("m", ["a", "b"], S, (0, 0, 1), nseg=2); f.fix("a"); f.assemble()
F, q = f.load_vector(nodal={"b": (0, 0, 0, 100.0, 0, 0)}); u, R = f.solve(F)
check("torsion twist  TL/GJ", u[f.names["b"] * 6 + 3], 100.0 * L / (S.G * S.J))

print("\nALL OK" if ok_all else "\nSOMETHING FAILED")
