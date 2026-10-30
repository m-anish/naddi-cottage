# Onshape frame: check against `code/dome.py`

Checked 30 Oct 2026 against `onshape/dome_struts.glb` (exported from the `1Vdome`
assembly, generator "ONSHAPE BY PTC INC, 1.222").

Measured straight from the glTF: every part's placement matrix is resolved to world
coordinates, and each member's centreline is taken as the long axis of its own
bounding box. Lengths and angles below are good to about an inch and a fifth of a
degree. The hub plates and the exact joint details still want a proper look in
Blender — see [Still to check](#still-to-check).

## What is in the file

| | |
| --- | --- |
| Members with geometry | 81 |
| Of those, 2×4" struts | 51 |
| Hub plates, gussets, brackets | 30 |
| Units | metres (glTF standard); 1 unit = 3.2808 ft |
| Orientation | z up, and the origin sits **at the apex** — the whole building hangs below z = 0 |

Measured strut section: **2.05 × 4.00 in** — the 2×4" struts of the brief, confirmed.

Plate thicknesses come out at 0.39 in (10 mm) for the `Part 1`/`Part 3` gussets and
3.2–4.2 in for the deeper `4-alt` / `5-alt` / `3-way-top` hub blocks.

## The dome itself matches, to the inch

Taking the highest strut end as the apex and fitting the ideal 12 ft icosahedron:

| Quantity | `dome.py` | Onshape | Verdict |
| --- | --- | --- | --- |
| Theoretical edge | 12.000 ft | 12 ft (strut 11.417 + hubs) | ✔ |
| Ring radius `R_RING` | 10.208 ft | 10.17–10.29 ft at the strut ends | ✔ |
| Upper ring `Z_UP` | 10.208 ft | 10.23 ft | ✔ |
| Apex `Z_TOP` | 16.517 ft | 16.41 ft to the lower strut faces | ✔ |
| Ring angular spacing | 72° | 72°, mean error 0.00°, spread ±1.94° | ✔ |

17 of the 25 dome edges are present as a strut of **11.417 ft (11'-5")** — and every
single one measures exactly that, not a millimetre of variation. Each strut end sits a
mean 4.2 in (max 4.6 in) short of the ideal icosahedron vertex.

So: **the theoretical edge is 12'-0"; the steel strut is 11'-5"; the remaining 7 in is
hub, about 3½ in at each end.** Nothing in `dome.py` needs changing for this — but if
struts are ever drawn as real members rather than lines, that is the number to use.

The 8 "missing" edges are not missing. They are made of longer members that run
through the vertex instead of stopping at it (see below).

## One real correction: the dome is rotated 36°

The frame's rings sit at these plan angles:

- **lower ring** vertices at 18°, 90°, 162°, 234°, 306°
- **upper ring** vertices at 54°, 126°, 198°, 270°, 342°

`dome.py` currently has the lower ring at 126° + 72k and the upper at 90° + 72k — the
right shape, turned the wrong way. The rings are offset 36° from where they are built.

### Which way to turn it

The rotation is pinned by the two extensions, not guessed. The frame has framing
projecting from two of the five "up" wall triangles, centred at **198°** and **54°** —
exactly **144° apart**. `dome.py` already puts its washroom door on `up0` and its main
door on `up3`, and those two faces are also 144° apart. Only one of the two possible
alignments makes both of them land on a real extension:

- Anchor the washroom on 198° → `up3` falls on 54°, the other real extension. ✔
- Anchor the washroom on 54° → `up3` falls on 270°, where there is nothing. ✘

**Anish has since confirmed this independently**: the two extensions are built from a
6 ft and an 8 ft projecting strut, and the bathroom is in the 8 ft one. The measured
projections are **7.71 ft at 198°** and **6.48 ft at 54°** — so the washroom is the
198° face, exactly as the geometry predicted.

**The fix is a +108° rotation about z**, which is two edits in `code/dome.py`:

```python
Lr = [pol(R_RING, 234 + 72 * k, 0.0)  for k in range(5)]   # was 126
Ur = [pol(R_RING, 198 + 72 * k, Z_UP) for k in range(5)]   # was 90
```

After that the face names line up with the building:

| Face | Plan angle | What is there |
| --- | --- | --- |
| `up0` | 198° | washroom extension (~7'-8" deep) |
| `up1` | 270° | — |
| `up2` | 342° | — |
| `up3` | 54° | second extension (~6'-6" deep) |
| `up4` | 126° | — |

Everything in `OPENINGS` is written against these face names, so it rides along
unchanged. The camera positions in the `hero` / `back` / `cut` views will need
re-aiming, since the room turns under them.

## There are two extensions, not one

The brief describes only the washroom. The frame has two.

**At 198° — the washroom, the "8 ft" one.** Framed from 24 ft stock cut to **7.71 ft**
(7'-8½"): one member at floor level (mid-radius 13.9 ft), a pair at mid-height
(mid-radius 14.9 ft, at 192° and 204°), and a pair of 18 ft rafters overhead. The
brief estimated ~7 ft deep; **7'-8½" is the number to use**, and
`code/geom.py`'s washroom depth should be reset to it.

Its outer corner hub (`3-way-top`) sits at radius 14.9–15.3 ft and only
**6.59–7.39 ft above the floor**. The washroom design puts the shower at the back
"under the ridge" — but the back of the extension is where the roof is *lowest*, about
6'-7" at the corner. Worth checking the shower head and the raked screen against that
before anything is ordered.

**At 54° — the "6 ft" one, facing east.** Framed from 24 ft stock cut to **6.48 ft**
(6'-5¾"): one member at floor level (mid-radius 15.8 ft), a pair at mid-height
(mid-radius 16.7 ft, at 48° and 60°), and a pair of 20 ft rafters. It sits about 2 ft
further out in plan than the washroom does, and its outer corner hub is lower still —
radius 16.6–17.0 ft at **5.54–6.34 ft** above the floor. Anish says it takes the
morning sun. What it is *for* is still open — on the rotation above it is the face
`dome.py` calls `up3`, which carries the main door.

## Which way the building faces

Anish places the 6 ft extension "roughly east". That extension is the 54° face, so
**model 54° = due east**, and since model angles run anticlockwise while compass
bearings run clockwise:

> **bearing = 144° − model angle**

| Face | Model angle | Bearing | Faces | |
| --- | --- | --- | --- | --- |
| `up3` | 54° | 90° | **east** | 6 ft extension, morning sun |
| `up4` | 126° | 18° | NNE | |
| `up0` | 198° | 306° | NW | washroom, 8 ft extension |
| `up1` | 270° | 234° | SW | |
| `up2` | 342° | 162° | SSE | |

Two things worth drawing out of this, because they bear on decisions already taken:

- **The washroom faces northwest** — the coldest, dullest aspect, and at 2,000 m with
  frosty winters that matters for a wet room. Worth a look at the glazing and at how
  much heat the shower end loses.
- **The main living space gets its best light from the SSE and SW faces** (`up2`,
  `up1`). The brief's recommended Scheme 2 — pine wainscot below, limewash above —
  reads very differently in hard afternoon SW light than in the soft north light the
  renders currently assume. The renders should use the real sun for Dharamsala
  (32.2° N, 76.3° E) rather than a generic sky.

This is *roughly* east by Anish's own words, so treat the bearings as ±10° until
someone takes a compass bearing on site.

## The roof is rafters with eaves, not bare cap edges

The five cap edges do not exist as 11'-5" struts. Instead, **pairs of rafters run
radially over each upper-ring vertex**, continuing past it to form an overhang:

| Plan angle | Rafter stock | Actual length | Overhang past the ring |
| --- | --- | --- | --- |
| 126°, 270°, 342° | 14 ft | 13.42 ft | ~2 ft |
| 198° (washroom) | 18 ft | 17.42 ft | ~6 ft |
| 54° (2nd extension) | 20 ft | 19.42 ft | ~8 ft |

The two extended faces carry the long rafters, which is how the extensions get
roofed. `dome.py` models the roof as the five flat `cap` facets with 80 mm PUF panels
and treats the eaves as nothing — fine for interior renders, but the real frame has a
projecting roof, and the longer rafters over the two extensions are what carry it.

## The whole dome stands 1'-3" off the ground

Anish: the structure is held **1.25 ft above ground**, on ground-screw anchors at
every vertex plus **one in the dead centre of the pentagon base** — which is the same
axis the loft's central hanger drops down. So the centre of the building is anchored
top and bottom.

The export's own z = 0 (the lower-ring datum, and `dome.py`'s floor origin) therefore
sits **1.25 ft above ground**. Everything below is a measured height restated against
ground level, which is what the washroom question turns on:

| | Above floor datum | Above ground |
| --- | --- | --- |
| Ground | −1.25 ft | 0 |
| Washroom extension, floor steel | −0.13 to +0.46 ft | 1.12–1.71 ft |
| Toilet floor as designed (1 ft over the terrace) | ~−0.25 ft | ~1.0 ft |
| Washroom extension, mid-height rail | 3.49 ft | 4.74 ft |
| Washroom rafter, outer end (centreline) | 7.36 ft | 8.61 ft |
| Washroom outer corner hub | 6.59–7.39 ft | 7.84–8.64 ft |
| Upper ring (lower of the pair) | 10.20 ft | 11.45 ft |
| Loft datum | 8.46 ft | 9.71 ft |
| Apex | 16.52 ft | 17.77 ft |

`dome.py` should carry a `GROUND_Z = -1.25` so that drawings and renders can show the
ground line and the floor void honestly. Note the brief's "raised metal frame ... void
under it sealed in painted tin" is this 1'-3".

## The upper ring is doubled

The upper pentagon is not five struts but **ten** — two complete rings of five, both
dead level, at **10.20 ft and 10.44 ft** above the floor. Each is 11.42 ft long with
its midpoint at radius 8.3–8.4 ft, which is exactly the chord of a 10.21 ft pentagon.

So the upper ring is a paired member about 3 in apart in height — worth knowing,
because the brief's 10'-2" (10.21 ft) upper-ring datum is the *lower* of the two, and
the lining detail has to clear both.

## The loft is a suspended frame, and it is at 8'-5", not 9'-0"

The brief carries the loft at 9'-0" as an assumption. The steel settles it, and the
arrangement is more interesting than a platform on posts — **it hangs**.

Five hangers drop from the upper-ring vertices:

| | |
| --- | --- |
| Member | 1.84 ft long, section **3.00 × 9.55 in** |
| Count | 5 — one on every upper-ring vertex line (54°, 126°, 198°, 270°, 342°) |
| Runs from | radius 9.37 ft at z = 10.11 ft (the upper ring) |
| down to | radius 10.19 ft at z = **8.46 ft**, splaying slightly outward |

At the foot of each is a small cleat — 0.92 ft of 3.68 × 0.39 in (10 mm) plate at
z = 8.32 ft, radius 9.81 ft.

And the centre is hung from the apex:

| | |
| --- | --- |
| Member | **3.00 × 3.00 in** square section, 7.75 ft long |
| Position | exactly on the dome axis, radius 0.00 ft |
| Runs from | z = 16.14 ft, just under the apex hub at 16.52 ft |
| down to | z = **8.39 ft**, where an 11.53 × 0.39 in plate forms the central node |

So there are six prepared points — five at the perimeter, one dead centre — all within
two inches of the same level. **The loft datum is about 8'-5", not 9'-0".** That is
7 in lower than the brief assumes, and it matters: it is headroom both under the loft
and over it.

### The radial struts are missing from the export

The struts that would join the central node to the perimeter hangers are **not in this
file** — there is no member anywhere that spans the axis to the wall at that level.
Anish confirms they exist in the design and are simply missing from the export, and
has asked for them to be modelled.

They run from three of the five hangers. By the bearings above the five hangers face
**E, NNE, NW, SW and SSE** — there is no hanger due west, and Anish has confirmed the
three are the **NNE, NW and SW** ones (model angles 126°, 198°, 270°).

So the platform spans a 144° sector centred on **NW — the washroom side**, which is
where the brief puts it. The two unused hangers are the E one (over the morning-sun
extension) and the SSE one, which keeps the loft clear of the best daylight.

Either way the loft is a **three-sided suspended platform, not the straight-edged slab
`dome.py` currently draws** (`loft()`, with `LOFT_Z = 9.0` and a cut at `LOFT_Y = 2.6`).
That function needs rebuilding on the real frame.

## The floor: three of the five edges are cantilevers that carry the extensions

This is the cleverest part of the frame. Naming the floor vertices by the compass
direction they face:

| Vertex | Model angle | Faces | Position (ft) |
| --- | --- | --- | --- |
| `L-SE` | 18° | SE | (9.71, 3.15) |
| `L-NE` | 90° | NE | (0.00, 10.21) |
| `L-NNW` | 162° | NNW | (−9.71, 3.15) |
| `L-W` | 234° | **W** | (−6.00, −8.26) |
| `L-SSW` | 306° | SSW | (6.00, −8.26) |

The washroom sits on the `L-NNW`–`L-W` edge, so **`L-W` is the westernmost floor
vertex** and the washroom's west corner.

Two of the five edges are plain 11.42 ft struts — `L-NE`–`L-SE`, and
`L-NNW`–`L-W` (the washroom's own base). The other three are **single long beams that
run along an edge and cantilever out past the pentagon**:

| Beam | Runs along | Cantilevers to |
| --- | --- | --- |
| 25.42 ft | `L-NNW`–`L-NE` | 4.5 ft past `L-NNW` (into the washroom) **and** 6.9 ft past `L-NE` (into the east extension) |
| 17.42 ft | `L-SSW`–`L-W` | 5.7 ft past `L-W` (into the washroom) |
| 19.42 ft | `L-SSW`–`L-SE` | 6.9 ft past `L-SE` (into the east extension) |

The extensions' outer edges then simply tie the cantilever tips together: the
washroom's 7.71 ft member spans from the 17.42 ft beam's tip to the 25.42 ft beam's
tip, and the east extension's 6.48 ft member spans the 25.42 ft and 19.42 ft tips.

So **both extensions are carried on cantilevers off the main floor beams** — no
separate foundations, which is why the 25.42 ft beam is longer than the dome is wide.
It is also why those three beams are not optional.

### The two chords Anish wants removed

Anish says two chords run from the washroom's western edges toward the centre of the
pentagon's main strut, were only ever there to support a raised fibre-cement deck, and
can go with a floor laid on the ground.

**They are not in this export.** Every floor-level member is accounted for in the
tables above: five edges (two plain, three cantilevered), the two extension outer
edges, and ten hub blocks. Nothing runs from `L-W` or `L-NNW` inward toward the centre
or toward the middle of any strut.

Like the loft's radial struts, they are presumably modelled elsewhere or simply left
out of the export. Either way the conclusion is the same and nothing is blocked:
**with the washroom floor laid on the ground there is no floor-support steel needed in
the washroom**, and the rebuild should leave it out. Worth pointing at them in Blender
once it is up, to be sure we mean the same members.

## Can the toilet floor drop, for more headroom?

Anish asks whether the washroom floor can sit lower than the dome's, closer to the
ground, to win vertical space. The frame says yes — but only about **5 to 8 inches**,
and the thing that stops it is drainage, not structure.

### What headroom there is now

The washroom's roof is the pair of 18 ft rafters running radially out along the 198°
centre line, so the roof is highest on that centre line and falls away to each side.
At the back, where the shower goes:

| Where | Clear height over the toilet floor |
| --- | --- |
| Back wall, **on the centre line** (the shower) | **about 7'-6"**, rafters the lowest element |
| Back **corners**, off to the sides | about 6'-10" |
| At the dome wall line, 7'-8" further in | about 9'-5" |

So the shower as placed is adequate but not generous, and the corners are tight. The
figures are read off a tessellated export, so treat them as ±2 in.

### The drainage: a floor at +6 in works

Anish proposes a finished floor **6 in above ground** with the biodigester inlet
**8 in below**, leaving 1'-2" of fall, and asks whether that is enough. **It is**, and
with more room than my first estimate suggested.

That first estimate was too pessimistic: it deducted the whole floor build-up (XPS and
slab) from the budget. That is the wrong measure. What matters is the **invert level of
the pipe at the WC**, and the build-up only matters if the drain has to pass beneath
it. Two cases:

| WC type | Invert at the WC | Fall available to the inlet at −8 in |
| --- | --- | --- |
| **P-trap** (horizontal outlet) — pipe leaves *above* the slab and drops outside | ≈ +11 in | **19 in** |
| **S-trap** (floor outlet) — bend sits under the slab | ≈ +1 in | **9 in** |

Against that, the run needs 1:40–1:60. Over a 12 ft run that is **1.8–3.6 in**.

So even the worse case — an S-trap and a long run — leaves about **5 in spare**, and a
P-trap leaves 15 in. The proposal is sound. A P-trap or back-to-wall WC is the better
choice here, because it keeps the drain out of the slab entirely.

Two numbers to nail down before building:

- **Get a level on the biodigester inlet.** The 8 in is from the brief. If the unit is
  already in the ground, measure it — everything hangs on this one figure, and the
  brief already flags its outlet height as unconfirmed.
- **Measure the run** from the WC to the biodigester. Beyond about 15 ft, redo the sum.

And do not spend the surplus badly: with 9–19 in to play with there is a temptation to
drop steeply then run flat. Keep a steady 1:40–1:60 all the way and take any surplus
as a back-drop in the chamber at the biodigester end.

### The arguments against — five of them

Anish asked for these, and they are worth taking seriously. None is fatal; two need a
real answer in the detailing.

**1. The washroom becomes the lowest point of the building, in a 3,000 mm climate.**
The dome floor is 15 in above ground; this would be 6 in. In a cloudburst, water
sheeting across the terrace needs only 6 in to come in, and it will find the door.
This is the strongest objection, because it is a permanent vulnerability rather than a
detail. It wants the plinth standing proud, the terrace positively graded away, and a
cut-off drain upslope — the washroom faces NW, so find out which way the terrace
actually falls before committing.

**2. A 9 in step down from the dome.** Comfortable risers are 6–7 in; 9 in is a lurch,
barefoot and wet, at night. In a room 7'-8" deep there is not much space for two
steps. This is the objection most likely to annoy, daily, for years.

**3. The dome's own base strut becomes something to step over.** The washroom sits on
the `L-NNW`–`L-W` edge, a 2×4 whose top is about 15 in above ground. With the floor at
6 in, that steel stands 9 in proud *inside* the doorway — so the threshold is both a
step down and a step over. It has to be boxed in as a kerb. Done well that is a
positive (it contains shower water, and the tanking turns up over it); done badly it
is a shin-barker.

**4. A colder floor on the cold side.** NW aspect at 2,000 m with frost. Nearer grade
means more edge heat loss and a floor that is colder underfoot and slower to dry in a
shaded wet room. Keep the 50 mm XPS, keep the 25 mm edge strip, and run the edge strip
deeper down the plinth than the current detail shows.

**5. You are digging into the terrace.** A finished floor at +6 in with 8–9 in of
build-up puts the bottom of the fill about 3 in *below* ground, so the sub-base can
collect water and the polythene becomes a bathtub. Use free-draining fill and give it
somewhere to go.

### What it actually buys, and the cheaper alternative

Dropping from +12 in to +6 in is **6 in of headroom** — the shower on the centre line
goes from about 7'-6" to **8'-0"**.

Moving the shower 2 ft inboard gains about **15 in**, for nothing, with none of the
five objections above. Doing both gives roughly **9'-3"**.

There is one genuine benefit of the low floor that relocating the shower does not
give: with the whole washroom below the dome floor, any leak or overflow drains
*outward* to the terrace rather than back into the living space. That is worth
something in a wet room.

### A bigger lever than the floor

The roof climbs steeply going inboard — about 7½ in of height for every foot towards
the dome. **Moving the shower 2 ft in from the back wall gains about 15 in of
headroom**, roughly twice what dropping the floor gives, and for nothing.

Layout A puts the shower at the back deliberately, to keep the wet end away from the
door and the dry zone. But the back is the one place the roof is lowest, and the
shower is the one fixture that needs full standing height — a WC and a basin do not.
Worth re-testing the layout against the real roof line before settling it. Both moves
together would give a shower with well over 8 ft of clear height.

## What to change in `code/dome.py`

1. **Rotate +108°** — the two `pol(...)` lines above. Everything else follows, because
   `OPENINGS` and `SCHEMES` are written against face names, not angles.
2. Keep `A_EDGE = 12.0` as the theoretical edge; add `STRUT_LEN = 11.417` and
   `HUB_SETBACK = 3.5/12` if struts are ever drawn as real members.
3. `R_RING`, `Z_UP`, `Z_TOP`, `ZC` and `R_IN` are all confirmed — leave them.
4. Re-aim the cameras after the rotation, and give the sun a real bearing for
   Dharamsala instead of a generic sky.
5. Model the upper ring as a pair at 10.20 and 10.44 ft.
6. Reset the washroom depth in `code/geom.py` to **7'-8½"**.
7. Rebuild `loft()` as a suspended platform at `LOFT_Z = 8.46`, hung from the five
   vertex hangers and the central drop, spanning the NNE–NW–SW sector, and add the
   missing radial struts.
8. Add `GROUND_Z = -1.25` and draw the ground line and the floor void.
9. Decide what to do about the east extension at `up3` and the roof overhang.

## Still to check

- Import the glb into Blender and compare it against the generated faces side by
  side, which is the real test of the +108° rotation. *(Blocked until Blender
  finishes installing — see the note at the end.)*
- The hub plates: the `5-alt` blocks at the upper ring, the `4-alt` blocks at the
  floor ring and the `3-way-top` corners on the two extensions set the true working
  lengths. Positions are measured; their internal geometry is not.
- Which three hangers carry the loft's radial struts.
- What the east extension is for.
- The washroom's real back-wall width and lean angle, which the extension framing
  should now settle — the brief has 15° against the dome's ~11°.
- A compass bearing on site, to firm up "roughly east".
- A STEP export would give exact dimensions; the glb is tessellated, so every number
  here is read off triangle vertices rather than true edges.

## How these numbers were taken

`glTF` stores each part as a mesh plus a placement matrix. The script resolves the
full node tree to world coordinates, then takes each member's centreline as the long
axis of its own bounding box, and its section as the two shorter extents. That is
exact for straight rectangular members, which is all of them. Endpoint clustering at
a 4.7 in tolerance recovers the joints.

The one thing this method cannot see is *how* members meet inside a hub — only where
their ends fall. Hence the 4.2 in mean gap to the ideal vertex, which is the hub
setback rather than an error in the frame.

