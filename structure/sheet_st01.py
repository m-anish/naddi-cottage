"""Sheet ST-01: the dome frame, and how hard each part of it is working.

Reads structure/out/results.json (made by analyse.py) and draws the summary
sheet in the house style. Writes structure/out/ST01_structure_summary.png.

    .venv/bin/python structure/sheet_st01.py
"""
import json, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
import dome_model as dm
import checks as ck

plt.rcParams.update({"font.family": "Inter", "font.size": 8})
INK, GREY, ACCENT, WATER = "#1d1d1b", "#8a8780", "#b5552b", "#3d7ea6"
PALE = "#e9e6df"
HERE = pathlib.Path(__file__).resolve().parent
R = json.load(open(HERE / "out" / "results.json"))
HUB = json.load(open(HERE / "out" / "hub_sections.json"))
A, B = R["exposures"]["1.0"], R["exposures"]["1.36"]
OPEN = ("dg90_54_u", "dg18_54_u", "dg162_198_u", "dg234_198_u")


def worst(ex, clad, pick):
    return max(v["util"] for k, v in ex[f"members_all_pinned_{clad}"].items() if pick(k, v))


def rng(pick):
    """(best case, worst case): sheltered site with the cladding helping,
    exposed ridge with the bare tubes doing everything."""
    return worst(A, "braced", pick), worst(B, "bare", pick)


stub = ck.chs_props(R["inputs"]["stub_D"], R["inputs"]["stub_t"], R["inputs"]["stub_fy"])
Mstub = lambda ex: max(v["M"] for v in ex["reactions_factored_stubs"].values()) / stub["Md"]
bolt = R["bolt_group"]["cap"]
endR = lambda ex: max(v["R"] for k, v in ex["ends_by_hub"].items() if not k.startswith("loft"))
hub_cut = 3 * endR(B) / (HUB["5-alt"]["min_mm2"] * 1e-6) / 1e6          # MPa, three tube forces across the thinnest cut
rows = [
    ("Ground-screw shafts, bending at the ground\n(shaft size assumed: 76 mm × 3.2 mm)", Mstub(A), Mstub(B)),
    ("The four tubes beside the extension openings", *rng(lambda k, v: k in OPEN)),
    ("Rafters", *rng(lambda k, v: v["kind"] == "rafter")),
    ("Upper-ring tubes", *rng(lambda k, v: v["kind"].startswith("upper ring"))),
    ("Wall diagonals, all the others", *rng(lambda k, v: v["kind"] == "wall diagonal" and k not in OPEN)),
    ("Bolts fixing each tube end to its hub\n(5 × M6 assumed; worst case allows for loose holes)", endR(A) / bolt, endR(B) / (0.7 * bolt)),
    ("Floor ring and floor beams", *rng(lambda k, v: v["kind"] in ("floor ring", "floor beam", "extension floor edge"))),
    ("Cast hubs: average stress on the thinnest cut\n(against a cautious 55 MPa for sand-cast aluminium)", hub_cut / 55 * endR(A) / endR(B), hub_cut / 55),
]

fig = plt.figure(figsize=(11, 8.5), dpi=200)
fig.text(0.035, 0.955, "Dome frame — how hard each part is working", fontsize=15, fontweight="semibold", color=INK, va="top")
fig.text(0.035, 0.915, "Demand as a share of the code limit, under the worst of 83 load combinations · wind in ten directions · snow · live load · earthquake",
         fontsize=9, color=GREY, va="top")
fig.text(0.965, 0.955, "ST-01", fontsize=15, fontweight="semibold", color=ACCENT, va="top", ha="right")
fig.text(0.965, 0.915, "Naddi cottage · main dome", fontsize=8, color=GREY, va="top", ha="right")
fig.add_artist(plt.Line2D([0.035, 0.965], [0.895, 0.895], color=INK, lw=0.8, transform=fig.transFigure))
fig.text(0.035, 0.042, "An assessment, not a certified design. Tube wall (2 mm) and bolts (5 × M6 per tube end) are from the Onshape model; ground-screw shaft and hub alloy are assumed. "
         "Each needs confirming on site.", fontsize=7, color=GREY)
fig.text(0.035, 0.026, "1.0 is the code limit, which keeps a margin of about 1.65 before steel yields.  Numbers from structure/analyse.py; write-up in docs/structural_assessment.md.",
         fontsize=7, color=GREY)

# ---------------------------------------------------------------- plan of the frame
fig.text(0.035, 0.873, "Plan of the frame", fontsize=9.5, fontweight="semibold", color=INK, va="top")
fig.text(0.035, 0.852, "ten ground screws carry everything", fontsize=7.4, color=GREY, va="top")
ax = fig.add_axes([0.035, 0.375, 0.36, 0.47])
ax.set_aspect("equal"); ax.axis("off")
f = dm.build()
P = {k: f.xyz[i] / dm.FT for k, i in f.names.items()}
for m in f.members.values():
    if m.kind in ("ground screw", "floor deck tie (assumed)", "loft beam (assumed)", "loft hanger", "loft centre drop"):
        continue
    pts = np.array([P[n] for n in m.nodes])
    hot = m.name in OPEN
    floor = m.kind in ("floor ring", "floor beam", "extension floor edge")
    ax.plot(pts[:, 0], pts[:, 1], color=ACCENT if hot else (INK if floor else GREY),
            lw=2.4 if hot else (1.3 if floor else 0.6), solid_capstyle="round", zorder=3 if hot else 2)
for s_ in f.support_nodes:
    x, y = P[s_][:2]
    ax.add_patch(Circle((x, y), 0.45, fc=WATER, ec="white", lw=0.8, zorder=5))
na = np.radians(144)          # bearing = 144 - model angle, so north is at model angle 144
cx, cy = 14.5, -12.5
ax.annotate("", xy=(cx + 2.4 * np.cos(na), cy + 2.4 * np.sin(na)), xytext=(cx, cy),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8))
ax.text(cx + 3.3 * np.cos(na), cy + 3.3 * np.sin(na), "N", fontsize=8, color=INK, ha="center", va="center")
ax.text(*dm.pol(16.2, 200, 0)[:2], "washroom", fontsize=7.4, color=INK, ha="right", va="center")
ax.text(*dm.pol(17.6, 50, 0)[:2], "east\nextension", fontsize=7.4, color=INK, ha="left", va="center")
mid = (P["L18"][:2] + P["U54"][:2]) / 2
ax.annotate("tubes beside an opening", xy=mid, xytext=(13.2, 1.5), fontsize=7.2, color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", lw=0.45, color=INK, shrinkB=2))
ax.set_xlim(-20, 21); ax.set_ylim(-14.5, 17.5)
sa, sb = A["reactions_service_stubs"], B["reactions_service_stubs"]
ring = [f"L{a}" for a in dm.LOW]
t = lambda n: n / 9810.0
dn = max(sa[s_]["down"] for s_ in ring); sd = (max(sa[s_]["side"] for s_ in ring), max(sb[s_]["side"] for s_ in ring))
upb = max(sb[s_]["up"] for s_ in ring)
dead = sum(R["totals_kN"][k] for k in ("D_steel", "D_roof", "D_wall", "D_lining", "D_floor", "D_floorfin", "D_loft"))
lg = fig.add_axes([0.035, 0.275, 0.40, 0.085]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
lg.plot(0.012, 0.86, "o", ms=6.5, color=WATER, mec="white", mew=0.9)
lg.text(0.035, 0.86, "ground screw: one under each floor hub, each extension corner and the centre", fontsize=7.2, color=INK, va="center")
lg.text(0.035, 0.58, f"Each of the five ring screws, working load:  down up to {t(dn):.1f} t (everyday about {t(max(R['reactions_everyday']['dead only (finished)'][s_] for s_ in ring)):.1f} t)", fontsize=7.2, color=INK, va="center")
lg.text(0.035, 0.34, f"sideways {t(sd[0]):.1f}–{t(sd[1]):.1f} t in a design storm, acting 1'-3\" above the ground", fontsize=7.2, color=INK, va="center")
lg.text(0.035, 0.10, f"uplift none in a sheltered spot, up to {t(upb):.1f} t on a ridge crest.  Centre screw: {t(sa['L0']['down']):.1f} t down.", fontsize=7.2, color=INK, va="center")

# ---------------------------------------------------------------- the range chart
fig.text(0.455, 0.873, "Share of capacity used", fontsize=9.5, fontweight="semibold", color=INK, va="top")
lg = fig.add_axes([0.455, 0.812, 0.51, 0.04]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
lg.plot(0.010, 0.78, "o", ms=6.5, color=WATER, mec="white", mew=0.9)
lg.text(0.028, 0.78, f"best case: sheltered site ({A['Vz']:.0f} m/s gust) and the cladding bracing the tubes", fontsize=7.2, color=INK, va="center")
lg.plot(0.010, 0.22, "D", ms=6.0, color=ACCENT, mec="white", mew=0.9)
lg.text(0.028, 0.22, f"worst case: ridge crest ({B['Vz']:.0f} m/s gust) and the bare tubes doing everything", fontsize=7.2, color=INK, va="center")
ax = fig.add_axes([0.715, 0.30, 0.25, 0.49])
n = len(rows)
ax.set_xlim(0, 1.4); ax.set_ylim(n - 0.45, -0.8)
ax.axvspan(1.0, 1.4, color=PALE, lw=0, zorder=0)
ax.axvline(1.0, color=INK, lw=0.9, zorder=1)
ax.text(1.0, -0.86, "code limit", fontsize=7.2, color=INK, ha="center", va="bottom")
for x in (0.25, 0.5, 0.75):
    ax.axvline(x, color=PALE, lw=0.6, zorder=0)
wb = dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.9)
for i, (name, lo, hi) in enumerate(rows):
    ax.plot([lo, hi], [i, i], color=GREY, lw=2.0, solid_capstyle="round", zorder=2)
    ax.plot(lo, i, "o", ms=6.5, color=WATER, mec="white", mew=0.9, zorder=3)
    ax.plot(hi, i, "D", ms=6.0, color=ACCENT, mec="white", mew=0.9, zorder=3)
    ax.text(lo - 0.05, i, f"{lo:.2f}", fontsize=7.4, color=INK, ha="right", va="center", zorder=4)
    ax.text(hi + 0.05, i, f"{hi:.2f}", fontsize=7.4, color=INK, ha="left", va="center", zorder=4,
            bbox=dict(wb, facecolor=PALE if hi + 0.05 > 1.0 else "white"))
    fig.text(0.705, ax.transData.transform((0, i))[1] / fig.bbox.height, name, fontsize=7.6, color=INK, ha="right", va="center", linespacing=1.25)
ax.set_xticks([0, 0.5, 1.0]); ax.set_xticklabels(["0", "half used", "all used"], fontsize=7, color=GREY)
ax.tick_params(axis="x", length=0, pad=4); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(False)

# ---------------------------------------------------------------- headline figures
L = R["limits"]
today = sum(R["totals_kN"][k] for k in ("D_steel", "D_roof", "D_wall", "D_floor"))
ft = lambda kpa: kpa * 1000 / 9.81 / 200 / 0.3048
tiles = [
    ("weight of the building today", f"{today / 9.81:.1f} t",
     f"{today:.0f} kN; about {dead / 9.81:.0f} t ({dead:.0f} kN)\nonce lined and floored"),
    ("snow the roof carries at the code limit", f"{ft(L['bare']['snow_kPa_members']):.0f}–{ft(L['braced']['snow_kPa_members']):.0f} ft",
     f"of settled snow lying on the ground ({L['bare']['snow_kPa_members']:.1f}–{L['braced']['snow_kPa_members']:.1f} kPa);\nNaddi's big falls are reported at 1–2 ft"),
    ("gust at which the first tubes reach the limit", f"{L['bare']['wind_ms_members'] * 3.6:.0f} km/h",
     f"the 50-year gust here is {A['Vz'] * 3.6:.0f} km/h in open\ncountry and up to {B['Vz'] * 3.6:.0f} km/h on a ridge crest"),
    ("design earthquake, zone V", f"{A['by_family']['E']['member_util_bare']:.2f}",
     "share of the worst tube's strength used;\nthe building is light, so shaking does not govern"),
]
for i, (head, big, sub) in enumerate(tiles):
    x0 = 0.035 + i * 0.2345
    fig.add_artist(FancyBboxPatch((x0, 0.085), 0.2265, 0.165, boxstyle="round,pad=0,rounding_size=0.006", fc="white", ec=PALE, lw=1.0,
                                  transform=fig.transFigure))
    fig.text(x0 + 0.012, 0.232, head, fontsize=7.6, color=GREY, va="top")
    fig.text(x0 + 0.012, 0.203, big, fontsize=17, fontweight="semibold", color=INK, va="top")
    fig.text(x0 + 0.012, 0.138, sub, fontsize=7.0, color=INK, va="top", linespacing=1.35)

out = HERE / "out" / "ST01_structure_summary.png"
fig.savefig(out, facecolor="white")
print("wrote", out)
for name, lo, hi in rows:
    print(f"  {name.splitlines()[0]:50s} {lo:.2f} -> {hi:.2f}")
