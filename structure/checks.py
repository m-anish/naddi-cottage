"""Capacity checks: what a tube, a bolted tube end and a ground-screw shaft can
take, to the Indian steel code IS 800:2007 (limit state method).

Partial safety factors: 1.10 on yield, 1.25 on bolts and ultimate strength.
Thin walls that would buckle locally before yielding are handled with the
effective-width rule of EN 1993-1-5 (IS 800 sends such sections to IS 801;
the rule is the same idea and gives near-identical numbers at these ratios).
"""
import numpy as np

E = 2.0e11
GM0, GM1, GMB = 1.10, 1.25, 1.25


def tube_props(b, d, t, fy):
    """b, d, t in mm (d = depth, strong direction); fy in Pa. Returns SI."""
    A = b * d - (b - 2 * t) * (d - 2 * t)
    Iy = (b * d**3 - (b - 2 * t) * (d - 2 * t)**3) / 12
    Iz = (d * b**3 - (d - 2 * t) * (b - 2 * t)**3) / 12
    Zey, Zez = Iy / (d / 2), Iz / (b / 2)
    Zpy = (b * d**2 - (b - 2 * t) * (d - 2 * t)**2) / 4
    Zpz = (d * b**2 - (d - 2 * t) * (b - 2 * t)**2) / 4
    eps = np.sqrt(250e6 / fy)
    e235 = np.sqrt(235e6 / fy)
    cd, cb = d - 3 * t, b - 3 * t            # flat widths of the 4 in and 2 in walls

    def rho(c):                              # share of a wall that stays effective in compression
        lam = (c / t) / (28.4 * e235 * 2.0)
        return 1.0 if lam <= 0.673 else (lam - 0.22) / lam**2

    Aeff = A - 2 * (1 - rho(cd)) * cd * t - 2 * (1 - rho(cb)) * cb * t

    def bend(Zp, Ze, c, I, half):            # c = flat width of the compression flange
        r = c / t
        if r <= 33.5 * eps:
            return min(Zp, 1.2 * Ze), "compact"
        if r <= 42 * eps:
            return Ze, "semi-compact"
        Ieff = I - (1 - rho(c)) * c * t * half**2
        return Ieff / half, "slender"

    Zy, cls_y = bend(Zpy, Zey, cb, Iy, d / 2)
    Zz, cls_z = bend(Zpz, Zez, cd, Iz, b / 2)
    return dict(A=A * 1e-6, Aeff=Aeff * 1e-6, Iy=Iy * 1e-12, Iz=Iz * 1e-12,
                ry=np.sqrt(Iy / A) * 1e-3, rz=np.sqrt(Iz / A) * 1e-3,
                Td=A * 1e-6 * fy / GM0, Mdy=Zy * 1e-9 * fy / GM0, Mdz=Zz * 1e-9 * fy / GM0,
                cls_y=cls_y, cls_z=cls_z, fy=fy, kg_m=A * 1e-6 * 7850,
                rho_d=rho(cd), rho_b=rho(cb), b=b, d=d, t=t)


def chi(slender, fy, alpha=0.34):
    """Buckling reduction, IS 800 cl. 7.1.2.1; curve b for cold-formed tubes."""
    lam = slender / np.pi * np.sqrt(fy / E)
    phi = 0.5 * (1 + alpha * (lam - 0.2) + lam**2)
    return min(1.0, 1 / (phi + np.sqrt(max(phi**2 - lam**2, 1e-12))))


def tube_util(N, My, Mz, L, p, e_conn=0.0, braced_weak=False):
    """Utilisation of one tube (1.0 = at its code limit).
    N tension positive (N), My strong-axis and Mz weak-axis moments (N.m),
    L buckling length (m). e_conn: offset of the bolted face from the tube
    centre, which bends the tube by N*e all along it.
    Returns (utilisation, dict of the parts)."""
    My = abs(My) + abs(N) * e_conn
    Mz = abs(Mz)
    if N >= 0:
        parts = dict(axial=N / p["Td"], bend_y=My / p["Mdy"], bend_z=Mz / p["Mdz"])
        return sum(parts.values()), parts
    P = -N
    cy = chi(L / p["ry"], p["fy"])
    cz = 1.0 if braced_weak else chi(L / p["rz"], p["fy"])
    Pd = min(cy, cz) * p["Aeff"] * p["fy"] / GM0
    Ncy = np.pi**2 * E * p["Iy"] / L**2
    Ncz = np.pi**2 * E * p["Iz"] / L**2
    ay = 1 / max(1 - P / Ncy, 0.05)
    az = 1.0 if braced_weak else 1 / max(1 - P / Ncz, 0.05)
    parts = dict(axial=P / Pd, bend_y=My * ay / p["Mdy"], bend_z=Mz * az / p["Mdz"])
    return sum(parts.values()), parts


def strut_capacity(L, p, braced_weak=False):
    cy = chi(L / p["ry"], p["fy"])
    cz = 1.0 if braced_weak else chi(L / p["rz"], p["fy"])
    return min(cy, cz) * p["Aeff"] * p["fy"] / GM0


# ----------------------------------------------------------------------
# Bolted tube end: n small bolts through one 2 in face of the tube into the
# cast aluminium flange of the hub (single shear).
# ----------------------------------------------------------------------
def bolt_group(n=5, d=6.0, fub=400e6, t_steel=2.0, fu_steel=330e6,
               t_al=5.0, fu_al=140e6, kb=0.8, gamma_cast=2.0):
    """Design resistance of one tube end, N, and what governs.
    kb: bearing factor for edge distance and spacing (IS 800 cl. 10.3.4);
    gamma_cast: safety factor on castings (EN 1999-1-1 uses 2.0)."""
    An = 0.78 * np.pi * d**2 / 4 * 1e-6
    shear = fub / (np.sqrt(3) * GMB) * An
    bear_steel = 2.5 * kb * d * t_steel * 1e-6 * fu_steel / GMB
    bear_al = 2.5 * kb * d * t_al * 1e-6 * fu_al / gamma_cast
    parts = {"bolt shear": shear, "bearing on the tube wall": bear_steel, "bearing on the cast flange": bear_al}
    gov = min(parts, key=parts.get)
    return n * parts[gov], gov, {k: n * v for k, v in parts.items()}


def flange_tension(width=52.0, t=5.0, n_holes_across=2, d0=7.0, f02=60e6, fu=140e6, gamma_cast=2.0):
    """Cast flange pulled along the tube axis: yield of the gross strip and
    fracture of the net strip. LM6-type sand casting assumed (0.2% proof about
    60 MPa, UTS about 140-160 MPa); castings get a factor of 2.0 on fracture."""
    gross = width * t * 1e-6 * f02 / GM0
    net = 0.9 * (width - n_holes_across * d0) * t * 1e-6 * fu / gamma_cast
    return min(gross, net), dict(gross_yield=gross, net_fracture=net)


def chs_props(D, t, fy):
    d = D - 2 * t
    A = np.pi * (D**2 - d**2) / 4
    I = np.pi * (D**4 - d**4) / 64
    Zp = (D**3 - d**3) / 6
    return dict(A=A * 1e-6, I=I * 1e-12, Md=Zp * 1e-9 * fy / GM0, Td=A * 1e-6 * fy / GM0, fy=fy)


def tube_util_vec(N, My, Mz, L, p, e_conn=0.0, braced_weak=False):
    """tube_util for arrays of stations at once. Returns (util, axial, bend_y, bend_z)."""
    N = np.asarray(N, float); L = np.asarray(L, float)
    My = np.abs(My) + np.abs(N) * e_conn
    Mz = np.abs(Mz)
    P = np.maximum(-N, 0.0)
    lam_y = L / p["ry"] / np.pi * np.sqrt(p["fy"] / E)
    lam_z = L / p["rz"] / np.pi * np.sqrt(p["fy"] / E)

    def chi_v(lam):
        phi = 0.5 * (1 + 0.34 * (lam - 0.2) + lam**2)
        return np.minimum(1.0, 1 / (phi + np.sqrt(np.maximum(phi**2 - lam**2, 1e-12))))

    cy = chi_v(lam_y)
    cz = np.ones_like(cy) if braced_weak else chi_v(lam_z)
    Pd = np.minimum(cy, cz) * p["Aeff"] * p["fy"] / GM0
    ay = 1 / np.maximum(1 - P / (np.pi**2 * E * p["Iy"] / L**2), 0.05)
    az = np.ones_like(ay) if braced_weak else 1 / np.maximum(1 - P / (np.pi**2 * E * p["Iz"] / L**2), 0.05)
    tens = N >= 0
    axial = np.where(tens, N / p["Td"], P / Pd)
    by = np.where(tens, My / p["Mdy"], My * ay / p["Mdy"])
    bz = np.where(tens, Mz / p["Mdz"], Mz * az / p["Mdz"])
    return axial + by + bz, axial, by, bz
