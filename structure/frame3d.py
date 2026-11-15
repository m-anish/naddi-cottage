"""A small 3D frame solver (direct stiffness method), numpy only.

Euler-Bernoulli beam elements with 6 degrees of freedom per node. It does three
things a truss-only calculation cannot: members that run continuously through
a joint, loads spread along a member (cladding, snow), and joints that are
either rigid or pinned (end releases, by static condensation).

Units are SI throughout: metres, newtons, pascals.

Local axes of an element:
    x  along the member, from node 1 to node 2
    z  the "depth" direction given for the member (made square to x)
    y  completes the right-handed set
Bending in the depth direction is bending about local y and uses Iy, so for a
2x4 tube with its 4 in depth along z, Iy is the strong-axis value.

The solver is checked against textbook cases in verify.py, and against
CalculiX (the solver that ships with FreeCAD) on the real frame.
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Section:
    name: str
    A: float          # m2
    Iy: float         # m4, bending in the depth direction (strong for a 2x4)
    Iz: float         # m4
    J: float          # m4
    E: float = 2.0e11
    G: float = 7.7e10
    mass: float = 0.0  # kg/m


@dataclass
class Element:
    n1: int
    n2: int
    sec: Section
    zdir: np.ndarray
    member: str
    rel: tuple = ()            # local dof indices (0..11) released
    s0: float = 0.0            # distance of n1 along the parent member (m)
    L: float = 0.0
    T: np.ndarray = None       # 3x3, rows = local x, y, z in global coords


@dataclass
class Member:
    name: str
    kind: str
    sec: Section
    elems: list = field(default_factory=list)
    length: float = 0.0
    n_tubes: int = 1
    nodes: tuple = ()          # names of the model nodes it runs through
    node_s: tuple = ()         # distance along the member at each of those nodes (m)


def k_local(sec, L):
    E, G, A, Iy, Iz, J = sec.E, sec.G, sec.A, sec.Iy, sec.Iz, sec.J
    k = np.zeros((12, 12))
    a = E * A / L
    t = G * J / L
    for i, j, v in ((0, 0, a), (0, 6, -a), (6, 6, a), (3, 3, t), (3, 9, -t), (9, 9, t)):
        k[i, j] = v; k[j, i] = v
    # bending in the x-y plane (v, rz), stiffness E*Iz
    b = E * Iz
    kb = np.array([[12 * b / L**3, 6 * b / L**2, -12 * b / L**3, 6 * b / L**2],
                   [6 * b / L**2, 4 * b / L, -6 * b / L**2, 2 * b / L],
                   [-12 * b / L**3, -6 * b / L**2, 12 * b / L**3, -6 * b / L**2],
                   [6 * b / L**2, 2 * b / L, -6 * b / L**2, 4 * b / L]])
    idx = [1, 5, 7, 11]
    k[np.ix_(idx, idx)] = kb
    # bending in the x-z plane (w, ry), stiffness E*Iy; note the sign of the coupling
    b = E * Iy
    kb = np.array([[12 * b / L**3, -6 * b / L**2, -12 * b / L**3, -6 * b / L**2],
                   [-6 * b / L**2, 4 * b / L, 6 * b / L**2, 2 * b / L],
                   [-12 * b / L**3, 6 * b / L**2, 12 * b / L**3, 6 * b / L**2],
                   [-6 * b / L**2, 2 * b / L, 6 * b / L**2, 4 * b / L]])
    idx = [2, 4, 8, 10]
    k[np.ix_(idx, idx)] = kb
    return k


def feq_local(w, L):
    """Equivalent nodal loads for a uniform line load w = (wx, wy, wz) in local axes."""
    wx, wy, wz = w
    f = np.zeros(12)
    f[0] = f[6] = wx * L / 2
    f[1] = f[7] = wy * L / 2
    f[5] = wy * L**2 / 12
    f[11] = -wy * L**2 / 12
    f[2] = f[8] = wz * L / 2
    f[4] = -wz * L**2 / 12
    f[10] = wz * L**2 / 12
    return f


class Frame:
    def __init__(self):
        self.xyz = []
        self.names = {}
        self.elems = []
        self.members = {}
        self.fixed = set()            # (node, dof)
        self.springs = []             # (node, dof, k)

    # ---- building -----------------------------------------------------
    def node(self, name, xyz=None):
        if name in self.names:
            return self.names[name]
        self.xyz.append(np.asarray(xyz, float))
        self.names[name] = len(self.xyz) - 1
        return self.names[name]

    def add_member(self, name, node_names, sec, zdir, kind="", nseg=6,
                   release_start=False, release_end=False, n_tubes=1):
        """A physical member running through node_names (continuous over the
        intermediate ones). Each span is cut into nseg elements. Releases pin
        the bending rotations at the member's own two ends."""
        m = Member(name, kind, sec, n_tubes=n_tubes, nodes=tuple(node_names))
        zdir = np.asarray(zdir, float)
        s = 0.0
        node_s = [0.0]
        spans = list(zip(node_names[:-1], node_names[1:]))
        for si, (a, b) in enumerate(spans):
            pa, pb = self.xyz[self.names[a]], self.xyz[self.names[b]]
            prev = self.names[a]
            for i in range(1, nseg + 1):
                if i == nseg:
                    cur = self.names[b]
                else:
                    cur = self.node(f"{name}#{si}.{i}", pa + (pb - pa) * i / nseg)
                p1, p2 = self.xyz[prev], self.xyz[cur]
                L = np.linalg.norm(p2 - p1)
                x = (p2 - p1) / L
                z = zdir - (zdir @ x) * x
                z /= np.linalg.norm(z)
                y = np.cross(z, x)
                rel = []
                if release_start and si == 0 and i == 1:
                    rel += [4, 5]
                if release_end and si == len(spans) - 1 and i == nseg:
                    rel += [10, 11]
                e = Element(prev, cur, sec, z, name, tuple(rel), s, L, np.vstack([x, y, z]))
                self.elems.append(e)
                m.elems.append(len(self.elems) - 1)
                s += L
                prev = cur
            node_s.append(s)
        m.node_s = tuple(node_s)
        m.length = s
        self.members[name] = m
        return m

    def fix(self, name, dofs=(0, 1, 2, 3, 4, 5)):
        for d in dofs:
            self.fixed.add((self.names[name], d))

    def spring(self, name, dof, k):
        self.springs.append((self.names[name], dof, k))

    # ---- element matrices ----------------------------------------------
    def _Tg(self, e):
        T = np.zeros((12, 12))
        for i in range(4):
            T[3 * i:3 * i + 3, 3 * i:3 * i + 3] = e.T
        return T

    def _condense(self, k, f, rel):
        """Static condensation of released dofs. Returns condensed k, f and the
        recovery pair (kcc_inv, kcr) for end-force recovery."""
        if not rel:
            return k, f
        c = list(rel)
        r = [i for i in range(12) if i not in c]
        kcc_inv = np.linalg.inv(k[np.ix_(c, c)])
        krc = k[np.ix_(r, c)]
        kk = np.zeros((12, 12)); ff = np.zeros(12)
        kk[np.ix_(r, r)] = k[np.ix_(r, r)] - krc @ kcc_inv @ krc.T
        ff[r] = f[r] - krc @ kcc_inv @ f[c]
        return kk, ff

    # ---- solve ---------------------------------------------------------
    def assemble(self):
        n = len(self.xyz) * 6
        K = np.zeros((n, n))
        self._ke = []
        for e in self.elems:
            kl = k_local(e.sec, e.L)
            kc, _ = self._condense(kl, np.zeros(12), e.rel)
            Tg = self._Tg(e)
            kg = Tg.T @ kc @ Tg
            dof = np.r_[e.n1 * 6:e.n1 * 6 + 6, e.n2 * 6:e.n2 * 6 + 6]
            K[np.ix_(dof, dof)] += kg
            self._ke.append((kl, Tg, dof))
        for nd, d, k in self.springs:
            K[nd * 6 + d, nd * 6 + d] += k
        # a whisker of rotational stiffness everywhere, so a joint whose members
        # are all pinned cannot spin freely (1 N.m/rad: irrelevant to results)
        for nd in range(len(self.xyz)):
            for d in (3, 4, 5):
                K[nd * 6 + d, nd * 6 + d] += 1.0
        self.K = K
        fixed = sorted(nd * 6 + d for nd, d in self.fixed)
        self.free = np.setdiff1d(np.arange(n), fixed)
        self.fixed_idx = np.array(fixed, int)
        self._Kff_inv = None
        return K

    def load_vector(self, nodal=None, line=None):
        """nodal: {node name: (Fx,Fy,Fz[,Mx,My,Mz])};
        line: list of (member name, q1, q2[, sa, sb]) with q the global line
        load (N/m) at distance sa and sb along the member (default: its two
        ends), linear in between and zero outside; piecewise uniform per
        element."""
        n = len(self.xyz) * 6
        F = np.zeros(n)
        elq = {}
        for name, v in (nodal or {}).items():
            v = np.asarray(v, float)
            F[self.names[name] * 6: self.names[name] * 6 + len(v)] += v
        for item in (line or []):
            mname, q1, q2 = item[:3]
            m = self.members[mname]
            sa, sb = (item[3], item[4]) if len(item) > 3 else (0.0, m.length)
            q1 = np.asarray(q1, float); q2 = np.asarray(q2, float)
            for ei in m.elems:
                e = self.elems[ei]
                smid = e.s0 + e.L / 2
                if smid < sa or smid > sb:
                    continue
                q = q1 + (q2 - q1) * (smid - sa) / (sb - sa)
                elq[ei] = elq.get(ei, np.zeros(3)) + q
        for ei, q in elq.items():
            e = self.elems[ei]
            kl, Tg, dof = self._ke[ei]
            fl = feq_local(e.T @ q, e.L)
            _, fc = self._condense(kl, fl, e.rel)
            F[dof] += Tg.T @ fc
        return F, elq

    def solve(self, F):
        if self._Kff_inv is None:
            Kff = self.K[np.ix_(self.free, self.free)]
            self._Kff_inv = np.linalg.inv(Kff)
        u = np.zeros(len(F))
        u[self.free] = self._Kff_inv @ F[self.free]
        R = self.K @ u - F
        return u, R

    def end_forces(self, u, elq):
        """Per element: local end forces (12,) acting on the element."""
        out = np.zeros((len(self.elems), 12))
        for ei, e in enumerate(self.elems):
            kl, Tg, dof = self._ke[ei]
            ul = Tg @ u[dof]
            fl = feq_local(e.T @ elq[ei], e.L) if ei in elq else np.zeros(12)
            if e.rel:
                c = list(e.rel)
                r = [i for i in range(12) if i not in c]
                kcc_inv = np.linalg.inv(kl[np.ix_(c, c)])
                ul = ul.copy()
                ul[c] = kcc_inv @ (fl[c] - kl[np.ix_(c, r)] @ ul[r])
            out[ei] = kl @ ul - fl
        return out


def stations(ef):
    """Internal actions at both ends of every element from end forces.
    Returns array (nelem, 2, 6): N (tension +), Vy, Vz, T, My, Mz."""
    s = np.zeros((ef.shape[0], 2, 6))
    s[:, 0, :] = -ef[:, 0:6]
    s[:, 1, :] = ef[:, 6:12]
    return s
