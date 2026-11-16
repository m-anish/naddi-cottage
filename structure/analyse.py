"""Run the dome frame under every load combination and check it.

    .venv/bin/python structure/analyse.py

Writes structure/out/results.json (everything the write-up and the drawings
quote) and prints a summary. The numbers in docs/structural_assessment.md come
from this file's output, not from hand typing.
"""
import json, pathlib
import numpy as np
from frame3d import stations
import dome_model as dm
import checks as ck

OUT = pathlib.Path(__file__).resolve().parent / "out"
E_CONN = 0.053          # m: tube centre to the middle of the hub flange it bolts to
SKIP = ("ground screw", "loft centre drop", "loft hanger", "loft beam (assumed)", "floor deck tie (assumed)")


class Run:
    """One model variant, solved for every basic load case."""

    def __init__(self, joints="pinned", supports="stubs", cladding="bare", tips=True, inp=None):
        self.joints, self.supports, self.cladding, self.tips = joints, supports, cladding, tips
        self.f = f = dm.build(joints, supports, tips, inp)
        self.key = f"{joints}/{supports}/{cladding}" + ("" if tips else "/no-ext-screws")
        dm.DIAPHRAGM = cladding == "braced"
        self.cases, self.faces = dm.load_cases(f)
        dm.DIAPHRAGM = False
        self.st, self.R, self.u, self.applied = {}, {}, {}, {}
        for name, (nod, lines) in self.cases.items():
            F, elq = f.load_vector(nod, lines)
            u, R = f.solve(F)
            self.st[name] = stations(f.end_forces(u, elq))
            self.R[name] = R
            self.u[name] = u
            self.applied[name] = F.reshape(-1, 6)[:, :3].sum(0)
        self.sup_dof = {}
        for s in f.support_nodes:
            n = f.names["G" + s] if f.supports_mode == "stubs" else f.names[s]
            self.sup_dof[s] = n * 6
        # station bookkeeping for the member checks
        self.mnames = [m.name for m in f.members.values() if m.kind not in SKIP]
        midx = {n: i for i, n in enumerate(self.mnames)}
        self.el_m = np.full(len(f.elems), -1)
        self.el_L = np.ones(len(f.elems))
        self.el_span = [""] * len(f.elems)
        for m in f.members.values():
            if m.kind in SKIP:
                continue
            for i in range(len(m.nodes) - 1):
                sa, sb = m.node_s[i], m.node_s[i + 1]
                free = m.nodes[i + 1] in ("T126", "T270", "T342")
                for ei in m.elems:
                    if sa - 1e-9 <= f.elems[ei].s0 < sb - 1e-9:
                        self.el_m[ei] = midx[m.name]
                        self.el_L[ei] = (2 if free else 1) * (sb - sa)
                        self.el_span[ei] = f"{m.nodes[i]}-{m.nodes[i + 1]}"
        # tube ends at hubs
        self.ends = []      # (member, node, kind, [(elem, end, sign)])
        for m in f.members.values():
            if m.kind in ("ground screw", "loft beam (assumed)", "floor deck tie (assumed)"):
                continue
            self.ends.append((m.name, m.nodes[0], m.kind, [(m.elems[0], 0, 1.0)]))
            self.ends.append((m.name, m.nodes[-1], m.kind, [(m.elems[-1], 1, 1.0)]))
            for i in range(1, len(m.nodes) - 1):
                s = m.node_s[i]
                left = [ei for ei in m.elems if abs(f.elems[ei].s0 + f.elems[ei].L - s) < 1e-9][0]
                right = [ei for ei in m.elems if abs(f.elems[ei].s0 - s) < 1e-9][0]
                self.ends.append((m.name, m.nodes[i], m.kind, [(right, 0, 1.0), (left, 1, -1.0)]))
        self.ends = [e for e in self.ends if e[1] not in ("T126", "T270", "T342")]

    def equilibrium(self):
        worst = 0.0
        for name in self.cases:
            Rsum = sum(self.R[name][d:d + 3] for d in self.sup_dof.values())
            worst = max(worst, np.abs(Rsum + self.applied[name]).max())
        return worst

    def combine(self, combo):
        st = sum(self.st[k] * v for k, v in combo.items())
        R = sum(self.R[k] * v for k, v in combo.items())
        return st, R

    def reactions(self, R):
        out = {}
        for s, d in self.sup_dof.items():
            r = R[d:d + 6]
            out[s] = dict(V=float(r[2]), H=float(np.hypot(r[0], r[1])), M=float(np.hypot(r[3], r[4])))
        return out

    def member_utils(self, st, props):
        """Worst utilisation per member: arrays (util, N, My, Mz, elem)."""
        braced = self.cladding == "braced"
        mask = self.el_m >= 0
        N = st[:, :, 0]; My = st[:, :, 4]; Mz = st[:, :, 5]
        L = np.repeat(self.el_L[:, None], 2, 1)
        u, ax, by, bz = ck.tube_util_vec(N, My, Mz, L, props, E_CONN, braced)
        u = np.where(mask[:, None], u, 0.0)
        nm = len(self.mnames)
        best = np.zeros(nm); arg = np.zeros((nm, 2), int)
        flat_m = np.repeat(self.el_m[:, None], 2, 1)
        for ei, en in zip(*np.nonzero(mask[:, None] & np.ones((1, 2), bool))):
            mi = flat_m[ei, en]
            if u[ei, en] > best[mi]:
                best[mi] = u[ei, en]; arg[mi] = (ei, en)
        return best, arg, (N, My, Mz, ax, by, bz)

    def end_forces(self, st):
        out = {}
        for name, node, kind, parts in self.ends:
            v = sum(sg * st[ei, en, :3] for ei, en, sg in parts)
            out[(name, node)] = (float(np.linalg.norm(v)), float(v[0]), float(np.hypot(v[1], v[2])), kind)
        return out


def envelope(run, combos, props):
    mem, ends, reac = {}, {}, {}
    for cname, combo in combos.items():
        st, R = run.combine(combo)
        best, arg, (N, My, Mz, ax, by, bz) = run.member_utils(st, props)
        for mi, name in enumerate(run.mnames):
            if name not in mem or best[mi] > mem[name]["util"]:
                ei, en = arg[mi]
                mem[name] = dict(util=float(best[mi]), combo=cname, N=float(N[ei, en]), My=float(My[ei, en]),
                                 Mz=float(Mz[ei, en]), axial=float(ax[ei, en]), bend_y=float(by[ei, en]),
                                 bend_z=float(bz[ei, en]), span=run.el_span[ei], L=float(run.el_L[ei]),
                                 kind=run.f.members[name].kind)
        for k, (Rr, Nn, V, kind) in run.end_forces(st).items():
            if k not in ends or Rr > ends[k]["R"]:
                ends[k] = dict(R=Rr, N=Nn, V=V, kind=kind, combo=cname)
        for s, v in run.reactions(R).items():
            e = reac.setdefault(s, dict(down=-1e99, up=-1e99, side=0.0, M=0.0))
            if v["V"] > e["down"]: e["down"], e["down_combo"] = v["V"], cname
            if -v["V"] > e["up"]: e["up"], e["up_combo"], e["side_with_up"] = -v["V"], cname, v["H"]
            if v["H"] > e["side"]: e["side"], e["side_combo"], e["V_with_side"] = v["H"], cname, v["V"]
            e["M"] = max(e["M"], v["M"])
    return mem, ends, reac


def merge(envs):
    """Envelope of several (mem, ends, reac) envelopes."""
    mem, ends, reac = {}, {}, {}
    for key, (m, e, r) in envs.items():
        for k, v in m.items():
            if k not in mem or v["util"] > mem[k]["util"]:
                mem[k] = dict(v, variant=key)
        for k, v in e.items():
            if k not in ends or v["R"] > ends[k]["R"]:
                ends[k] = dict(v, variant=key)
        for s, v in r.items():
            t = reac.setdefault(s, dict(down=-1e99, up=-1e99, side=0.0, M=0.0))
            for q in ("down", "up", "side"):
                if v[q] > t[q]:
                    t[q] = v[q]; t[q + "_combo"] = v[q + "_combo"]; t[q + "_variant"] = key
            t["M"] = max(t["M"], v["M"])
    return mem, ends, reac


def by_kind(mem):
    out = {}
    for name, v in mem.items():
        if v["kind"] not in out or v["util"] > out[v["kind"]]["util"]:
            out[v["kind"]] = dict(v, member=name)
    return out


def hub_of(node):
    if node == "A": return "apex hub"
    if node[0] == "U": return "upper-ring hubs"
    if node[0] == "L": return "floor-ring hubs"
    if node[0] == "T": return "extension roof-corner hubs"
    if node[0] in "WE": return "extension floor-corner hubs"
    return "loft"


def ends_by_hub(ends):
    out = {}
    for (name, node), v in ends.items():
        if v["kind"] in ("loft centre drop", "loft hanger"):
            h = v["kind"]
        else:
            h = hub_of(node)
        if h not in out or v["R"] > out[h]["R"]:
            out[h] = dict(v, member=name, node=node)
    return out


def clean(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, str) else "@".join(map(str, k)) if isinstance(k, tuple) else str(k)): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


def wind_resultants(run):
    """Net wind force on the whole building per 1 kPa, by direction."""
    out = {}
    for th in range(18, 360, 36):
        F = run.applied[f"W{th}_lift"]
        w = np.array([np.cos(np.radians(th)), np.sin(np.radians(th))])   # wind comes FROM th
        out[th] = dict(drag_kN=float(-(F[:2] @ w) / 1e3), lift_kN=float(F[2] / 1e3),
                       press_down_kN=float(-run.applied[f"W{th}_press"][2] / 1e3))
    return out


def main():
    I = dm.INPUTS
    props = ck.tube_props(I["tube_b"], I["tube_d"], I["tube_t"], I["fy"])
    runs = {}
    for joints in ("pinned", "rigid"):
        for supports in ("stubs", "pinned"):
            for cladding in ("bare", "braced"):
                r = Run(joints, supports, cladding)
                runs[r.key] = r
                print(f"{r.key:24s} nodes {len(r.f.xyz):4d} elements {len(r.f.elems):4d} equilibrium error {r.equilibrium():.1e} N")
    base = runs["pinned/stubs/bare"]
    tot = {k: float(-base.applied[k][2]) / 1e3 for k in base.cases if not k.startswith(("E", "W"))}
    wr = wind_resultants(base)
    res = dict(inputs=I, tube=props, totals_kN=tot, wind_resultants_per_kPa=wr, Ah=dm.seismic_Ah(I),
               face_areas={fc["name"]: fc["area"] for fc in base.faces}, E_CONN=E_CONN, exposures={})
    print("\nTotals kN:", {k: round(v, 1) for k, v in tot.items()})
    print("Wind per 1 kPa (drag, lift) kN:", {k: (round(v["drag_kN"], 1), round(v["lift_kN"], 1)) for k, v in wr.items()})

    for k3 in (1.0, 1.36):
        s0 = 1.5
        C = dm.combos(I, s0_kpa=s0, k3=k3)
        Cs = dm.service_combos(I, s0_kpa=s0, k3=k3)
        envs = {key: envelope(r, C, props) for key, r in runs.items()}
        senv = {key: envelope(r, Cs, props) for key, r in runs.items()}
        ex = dict(k3=k3, s0=s0, pd_kPa=dm.wind_pressure(I, k3) / 1e3, Vz=I["Vb"] * k3, n_combos=len(C))
        for clad in ("bare", "braced"):
            sub = {k: v for k, v in envs.items() if k.startswith("pinned/") and k.endswith(clad)}
            mem, ends, reac = merge(sub)
            ex[f"members_pinned_{clad}"] = by_kind(mem)
            ex[f"members_all_pinned_{clad}"] = mem
            subr = {k: v for k, v in envs.items() if k.startswith("rigid/") and k.endswith(clad)}
            ex[f"members_rigid_{clad}"] = by_kind(merge(subr)[0])
        mem, ends, reac = merge(envs)
        ex["ends_by_hub"] = ends_by_hub(ends)
        ex["ends_all"] = ends
        ex["reactions_factored"] = reac
        ex["reactions_service"] = merge(senv)[2]
        ex["reactions_service_stubs"] = merge({k: v for k, v in senv.items() if "/stubs/" in k})[2]
        ex["reactions_factored_stubs"] = merge({k: v for k, v in envs.items() if "/stubs/" in k})[2]
        # by load family (which kind of event drives what), design-basis variants
        fam = {}
        for tag in ("G", "S", "W", "U", "WS", "E"):
            Cf = {k: v for k, v in C.items() if k.split(":")[0] == tag}
            e2 = merge({key: envelope(r, Cf, props) for key, r in runs.items() if key.startswith("pinned/")})
            eb = merge({key: envelope(r, Cf, props) for key, r in runs.items() if key == "pinned/stubs/braced" or key == "pinned/pinned/braced"})
            worst = max(e2[0].values(), key=lambda v: v["util"])
            worstb = max(eb[0].values(), key=lambda v: v["util"])
            wend = max((v for v in e2[1].values() if v["kind"] not in ("loft centre drop", "loft hanger")), key=lambda v: v["R"])
            fam[tag] = dict(member_util_bare=worst["util"], member_bare=worst["kind"], member_util_braced=worstb["util"],
                            member_braced=worstb["kind"], end_R=wend["R"],
                            up=max(v["up"] for v in e2[2].values()), down=max(v["down"] for v in e2[2].values()),
                            side=max(v["side"] for v in e2[2].values()))
        ex["by_family"] = fam
        res["exposures"][str(k3)] = ex
        print(f"\n=== k3 = {k3}  (gust {ex['Vz']:.0f} m/s, design pressure {ex['pd_kPa']:.2f} kPa), ground snow {s0} kPa ===")
        for clad in ("bare", "braced"):
            print(f" members, pinned joints, cladding {clad}:")
            for kind, v in sorted(ex[f"members_pinned_{clad}"].items(), key=lambda kv: -kv[1]["util"]):
                print(f"   {kind:26s} {v['util']:5.2f}  (axial {v['axial']:.2f} strong {v['bend_y']:.2f} weak {v['bend_z']:.2f})  N {v['N'] / 1e3:6.1f} kN  {v['member']:13s} {v['combo']}")
        print(" tube ends (force into hub, per tube):")
        for h, v in sorted(ex["ends_by_hub"].items(), key=lambda kv: -kv[1]["R"]):
            print(f"   {h:28s} {v['R'] / 1e3:5.1f} kN  (axial {v['N'] / 1e3:6.1f}, shear {v['V'] / 1e3:4.1f})  {v['member']}@{v['node']}  {v['combo']}")
        print(" ground screws: factored | working load (down, up, side kN):")
        for s in reac:
            a, b = ex["reactions_factored"][s], ex["reactions_service"][s]
            print(f"   {s:5s} {a['down'] / 1e3:5.1f} {max(a['up'], 0) / 1e3:5.1f} {a['side'] / 1e3:5.1f} | {b['down'] / 1e3:5.1f} {max(b['up'], 0) / 1e3:5.1f} {b['side'] / 1e3:5.1f}")
        print(" by load family:", {k: (round(v['member_util_bare'], 2), round(v['member_util_braced'], 2), round(v['end_R'] / 1e3, 1)) for k, v in fam.items()})

    # ---- sensitivity: wall thickness and steel grade (forces barely change; capacities do)
    sens = []
    for t in (1.6, 2.0, 2.5, 3.2):
        for fy, fu in ((210e6, 330e6), (310e6, 450e6)):
            p = ck.tube_props(I["tube_b"], I["tube_d"], t, fy)
            row = dict(t=t, fy=fy / 1e6, kg_m=p["kg_m"], Td=p["Td"], Mdy=p["Mdy"], Mdz=p["Mdz"],
                       Pd_unbraced=ck.strut_capacity(3.658, p), Pd_braced=ck.strut_capacity(3.658, p, True),
                       cls_y=p["cls_y"], cls_z=p["cls_z"])
            cap, gov, parts = ck.bolt_group(t_steel=t, fu_steel=fu)
            row.update(bolt_cap=cap, bolt_gov=gov)
            for k3 in (1.0, 1.36):
                C = dm.combos(I, 1.5, k3)
                for clad in ("bare", "braced"):
                    u = 0
                    for sup in ("stubs", "pinned"):
                        r = runs[f"pinned/{sup}/{clad}"]
                        for combo in C.values():
                            st, _ = r.combine(combo)
                            u = max(u, r.member_utils(st, p)[0].max())
                    row[f"util_{clad}_{k3}"] = float(u)
            sens.append(row)
    res["sensitivity"] = sens
    print("\nSensitivity (worst member utilisation):")
    for r in sens:
        print(f"  t={r['t']} fy={r['fy']:.0f}: bare {r['util_bare_1.0']:.2f}/{r['util_bare_1.36']:.2f}  braced {r['util_braced_1.0']:.2f}/{r['util_braced_1.36']:.2f}  "
              f"strut {r['Pd_unbraced'] / 1e3:.0f}/{r['Pd_braced'] / 1e3:.0f} kN  Mdy {r['Mdy'] / 1e3:.2f}  bolts {r['bolt_cap'] / 1e3:.1f} ({r['bolt_gov']})")

    # ---- how much snow, how much wind: scale one action until something reaches 1.0
    def worst_util(combo_fn, x, clad):
        u, e = 0.0, 0.0
        for sup in ("stubs", "pinned"):
            r = runs[f"pinned/{sup}/{clad}"]
            for combo in combo_fn(x).values():
                st, _ = r.combine(combo)
                u = max(u, r.member_utils(st, props)[0].max())
                e = max(e, max(v[0] for k, v in r.end_forces(st).items() if v[3] not in ("loft centre drop", "loft hanger")))
        return u, e

    def solve(fn, target, lo, hi):
        for _ in range(28):
            mid = (lo + hi) / 2
            if fn(mid) < target: lo = mid
            else: hi = mid
        return (lo + hi) / 2

    bolt_cap = ck.bolt_group()[0]
    lim = {}
    for clad in ("bare", "braced"):
        snow = lambda s0: {k: v for k, v in dm.combos(I, s0, 1.0).items() if k.startswith("S:")}
        wind = lambda k3: {k: v for k, v in dm.combos(I, 1.5, k3).items() if k.split(":")[0] in ("W", "U")}
        lim[clad] = dict(
            snow_kPa_members=solve(lambda x: worst_util(snow, x, clad)[0], 1.0, 0.0, 20.0),
            snow_kPa_bolts=solve(lambda x: worst_util(snow, x, clad)[1], bolt_cap, 0.0, 20.0),
            wind_k3_members=solve(lambda x: worst_util(wind, x, clad)[0], 1.0, 0.3, 4.0),
            wind_k3_bolts=solve(lambda x: worst_util(wind, x, clad)[1], bolt_cap, 0.3, 4.0))
        lim[clad]["wind_ms_members"] = lim[clad]["wind_k3_members"] * I["Vb"]
        lim[clad]["wind_ms_bolts"] = lim[clad]["wind_k3_bolts"] * I["Vb"]
    res["limits"] = lim
    res["bolt_group"] = dict(cap=bolt_cap, gov=ck.bolt_group()[1], parts=ck.bolt_group()[2])
    print("\nLimits:", json.dumps(clean(lim), indent=1))

    # ---- what if there were no ground screws under the extension floor corners?
    r2 = Run("pinned", "stubs", "braced", tips=False)
    m2, e2, rc2 = envelope(r2, dm.combos(I, 1.5, 1.0), props)
    res["no_ext_screws"] = dict(members=by_kind(m2), reactions=rc2)
    print("\nWithout screws under the extension corners (sheltered wind):",
          {k: round(v["util"], 2) for k, v in by_kind(m2).items()})

    # ---- everyday loads on the ground screws (no wind, no snow, nobody home)
    rb = runs["pinned/stubs/braced"]
    Cs = dm.service_combos(I, 1.5, 1.0)
    res["reactions_everyday"] = {k: {s: v["V"] for s, v in rb.reactions(rb.combine(Cs[k])[1]).items()}
                                 for k in ("dead only (finished)", "dead only (today)", "dead + live + snow")}
    stub = ck.chs_props(I["stub_D"], I["stub_t"], I["stub_fy"])
    res["stub"] = stub

    # ---- deflections under working snow
    r = runs["pinned/stubs/braced"]
    u = sum(r.u[k] * v for k, v in dm.service_combos(I, 1.5, 1.0)["dead + live + snow"].items())
    d = np.linalg.norm(u.reshape(-1, 6)[:, :3], axis=1)
    i = int(d.argmax())
    name = [k for k, v in r.f.names.items() if v == i][0]
    res["deflection_snow_mm"] = dict(max=float(d.max() * 1e3), node=name, apex=float(d[r.f.names["A"]] * 1e3))
    print("max deflection under working dead+live+snow: %.1f mm at %s; apex %.1f mm" % (d.max() * 1e3, name, d[r.f.names["A"]] * 1e3))

    json.dump(clean(res), open(OUT / "results.json", "w"), indent=1)
    print(f"\nwrote {OUT / 'results.json'}")
    return runs, res


if __name__ == "__main__":
    main()
