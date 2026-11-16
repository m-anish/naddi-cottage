# Is the dome strong enough? A structural assessment of the frame

16 Nov 2026 · summary sheet **ST-01** (`drawings/dome/ST01_structure_summary.png`) ·
scripts and raw numbers in `structure/`.

> **What this is, and is not.** This is a careful calculation by an AI assistant. It is
> not a certificate from a structural engineer, and I am not one. It is built on the
> Onshape model and three site photos, not on a survey of what was actually bolted
> together, and several of its inputs are assumed ([listed here](#what-i-need-from-you)).
> It is good enough to say where the frame is comfortable, where it is tight, and what
> to go and measure. It is **not** good enough on its own to promise the building is
> safe in a once-in-fifty-years storm. The places where a qualified engineer's judgement
> genuinely matters are marked.

## The short answer

**(a) Is it adequate for the loads it will see?**

- **Everyday, yes, easily.** Standing there finished, lined and furnished, with no
  weather, the hardest-worked tube uses about a quarter of its strength.
- **Heavy snow with a full house, yes.** With 2½ ft of settled snow on the ground
  (more than Naddi's reported worst of 1–2 ft), every room loaded to the code figure
  and the loft full, the worst tube is at 0.5 to 0.9 of the code limit. The steep tin
  roof is the reason: it sheds roughly 40% of what falls on it.
- **The design windstorm: yes if the plot is ordinary, marginal if it sits on the
  ridge crest.** In the 50-year gust for open country here (140 km/h) the worst tube is
  at 0.65–0.7. If the cottage catches the full speed-up the code allows for a ridge
  crest (191 km/h), a handful of tubes go 0–16% past the code limit and so do the
  ground-screw shafts, on the size I had to assume for them. The first tubes reach the
  limit at a gust of about **177 km/h**.
- **Earthquake is not what governs.** Kangra is in the highest seismic zone, but the
  building is light, about 7 t when finished, and shaking loads scale with weight. The
  design earthquake uses under half the frame's strength.

"Past the code limit" does not mean "falls down". The limit keeps a margin of about
1.65 before steel starts to yield. Going to 1.16 means that margin has shrunk to about
1.4. It is a reason to act, not a reason to move out.

**(b) Where are the weak links?** Your instinct was right, with one addition.

1. **The ground screws, above all sideways.** Everything goes through ten of them, and
   each stands 1'-3" clear of the ground like a short flagpole. In a design storm each
   ring screw is pushed sideways with 0.4–0.8 t at the top of that 1'-3". I do not know
   what the screws are, so I cannot say whether that is fine; with a typical 3" (76 mm)
   shaft it is 60–120% of what the shaft takes in bending. This is the least known and
   most important item.
2. **The bolts between the tubes and the cast hubs.** On five 6 mm bolts per tube end
   they are 50–90% used. The cast aluminium around them is not highly stressed on
   paper, but paper is not the worry with a casting: hidden porosity and cracks are.
3. **The four tubes beside the two extension openings** (the addition). They take the
   extension's side walls on their weak side. They are the first tubes over the limit
   in the ridge-crest storm, and the fix is cheap.
4. **The loft's hanging points.** A fully loaded loft hangs about 0.8 t from the apex
   hub and 0.7 t from the north-west upper hub (1.2 t and 1.1 t once the code's safety
   factor is on). I could not establish how either is fastened. Hanging people off a
   casting deserves a second look.

The tubes themselves, away from the openings, are fine. They are thin, though: at a
2 mm wall they are doing real work, not idling.

**(c) What is genuinely uncertain?** The ground screws and the soil (unknown); the
tube wall and steel grade (taken from the model; a thinner wall would change the
verdict, a thicker one would make most of this comfortable); the alloy and soundness
of the hub castings (unknowable without looking); how exposed the plot really is; and
the floor framing, which is in no model I was given and so is **not assessed at all**.

**(d) What to do?** In order, most of it cheap:

1. Tell me the four facts in the [table below](#what-i-need-from-you). Fifteen minutes
   with calipers and a tape. They may settle most of this.
2. Have one ground screw pull-tested, up and sideways, and get the screws and the hub
   and loft fixings looked at by a structural engineer on site. This is the one place
   an engineer's signature is worth paying for.
3. Inspect every hub for cracks and every bolt for tightness.
4. Stitch the paired tubes together beside the two extension openings.
5. Do not load the loft until its fixings have been checked.

Details of each are in [What to do about it](#what-to-do-about-it).

## What I need from you

Each of these is currently a value from the Onshape model or a plain assumption.

| What | What I used | Why it matters | How to check |
| --- | --- | --- | --- |
| **Tube wall thickness** | 2.0 mm (Onshape `Shell 1`) | Strength scales almost directly with it. At 1.6 mm the worst tube goes from 0.92 to 1.19 in snow; at 2.5 mm it drops to 0.74. | Calipers on a cut end or at a bolt hole. Or weigh an offcut: 3.8 kg per metre is 1.6 mm, 4.7 is 2 mm, 5.8 is 2.5 mm, 7.4 is 3.2 mm. |
| **Steel grade** | YSt 210, the lowest tube grade sold | YSt 310 would give about a third more strength. | The mill stamp on the tube, or the supplier's invoice (Tata Structura and APL Apollo print it). |
| **Bolts at the hubs** | Five M6, ordinary grade 4.6, per tube end (five 6 mm holes in the Onshape tube; the photos show about five small bolts per flange) | They are the tightest part of the hub joint. | Count and measure at any hub. Is the head marked 4.6, 8.8 or nothing? Are they bolts with nuts, or self-drilling screws? Do they fit the hub holes snugly (the model has 8 mm holes in the hub for 6 mm bolts)? |
| **Ground screws** | 3" (76 mm) shaft, 3.2 mm wall, mild steel, fixed in firm ground | The whole building stands on them. | Make and model, shaft diameter, length in the ground, what soil they went into (fill, clay, weathered rock?), and whether an installation torque was recorded. A photo of one screw head and how the hub sits on it. |
| **Hub alloy and caster** | A basic sand-cast aluminium like LM6, treated cautiously | Sets how much the hubs can be trusted. | Whatever the foundry told you. Whether any hub was ever tested, dropped, or cracked. |
| **Anything added since the model** | Nothing | Props, braces or extra posts change the answer, usually for the better. | Especially: anything under the floor, and are there screws under **both** east-extension corners as there are under the washroom's? |
| **How exposed the plot is** | Both extremes | It moves the wind load by a factor of 1.85. | Is the cottage on the crest or the edge of a steep drop, or tucked into the slope with higher ground and trees around it? A photo from across the valley would do. |
| **The loft** | Designed load: people, bed, 200 kg/m² | Decides what hangs off the hubs. | Is the deck built? What will be on it? How are the hangers and the centre drop fastened to the hubs? |
| **The floor framing** | Not modelled | See [the floor](#the-floor-is-not-assessed). | A sketch or photo of the steel under the floor: joist size, spacing, which way they run, what they sit on. |

## How the frame actually works

The Onshape model shows something the earlier frame check did not draw out: **every
triangular face of the dome is its own frame of three tubes**, each tube turned so its
4" depth is square to that face. Two faces meet along every edge, so every edge of the
dome has **two tubes side by side**, about 3½" apart centre to centre, one belonging to
each face. That is why the upper ring is "doubled", why the rafters come in pairs, and
why there are 20 wall diagonals where a textbook dome has 10. The pairs are joined to
one another only at the hubs.

This is a good arrangement. Each tube carries the cladding of its own face the strong
way, and each hub is a cast aluminium dish with a pocket for every face corner. Each
tube end lies on a flat cast flange inside its pocket and is held by a cluster of small
bolts through one 2" face of the tube.

| Part | From the Onshape model |
| --- | --- |
| Tube | 2.05 × 4.00 in (52 × 102 mm) rectangular, 2 mm wall, 11'-5" long; 4.7 kg per metre |
| Tubes in the frame | 51, about 1.0 t of steel in all |
| Five-way hub (apex and upper ring) | 14" across, 3.7 kg of aluminium; flanges 5 mm, ribs 10 mm, base 5 mm |
| Four-way hub (floor ring) | 10" across, 3.2 kg |
| Three-way hub (extension roof corners) | 6½" across, 0.8 kg |
| Supports | a ground screw under each of the 5 floor hubs, the 4 extension floor corners and the centre: 10 |

The four extension-corner screws matter more than they look. The model was run without
them, to see: the cantilevered floor beams and the long rafters over the extensions
come out four times over their limit. The photos show screws under both washroom
corners. **Please confirm there are screws under both east-extension corners too.**

## What it has to carry

Loads are from the Indian loading code IS 875, combined and factored as IS 800 requires
for steel. 1 kN is about 100 kg.

| Load | What I took | Total on the building |
| --- | --- | --- |
| Steel frame, hubs, bolts | tube weight + 15% | 1.2 t |
| Roof | 80 mm PUF panel with tin both faces, purlins: 18 kg/m² | 0.9 t |
| Walls as built | fibre-cement planks on 1×2" purlins: 18 kg/m² | 1.4 t |
| Wall lining to come | EPS, battens, 8 mm board, pine below (drawing D-01): 20 kg/m² | 1.5 t |
| Floor | 20 mm board and steel now (40 kg/m²); wood floor to come (15 kg/m²) | 1.2 t + 0.5 t |
| Loft deck | 50 kg/m² over 92 sq ft | 0.4 t |
| **Building today / finished** | | **4.6 t / 7.0 t** |
| People and furniture, floor | 200 kg/m² (IS 875-2, dwellings) | 6.1 t |
| People and furniture, loft | 200 kg/m² | 1.8 t |
| Snow | 1.5 kPa on the ground, ×0.61 for the 37° roof (IS 875-4) | 3.5 t on the roof |
| Wind, open country | 39 m/s gust (140 km/h): 0.82 kPa | 1.0–2.7 t sideways, 1.7–2.3 t lifting the roof |
| Wind, ridge crest | 53 m/s gust (191 km/h): 1.52 kPa | 1.9–5.0 t sideways, 3.2–4.3 t lifting the roof |
| Earthquake | zone V; 22% of the building's weight applied sideways | 2.0 t sideways |

Three of these need a word.

**Snow.** The code gives no snow figure for Dharamsala; it tells the designer to find
local data. Press and weather-blog reports put Naddi's heavy falls at one to two feet
([2014](https://mcleodganj-weathergeek.blogspot.com/2014/02/highlight-of-season-pm15feb14.html),
[2019](https://mcleodganj-weathergeek.blogspot.com/2019/01/instability-lingers-pm23jan19.html),
[Tribune](https://www.tribuneindia.com/news/himachal/locals-rush-to-naddi-to-enjoy-snow-29800)).
I took 1.5 kPa, which is 2½ ft of settled snow at 200 kg per cubic metre, to stay on
the safe side of that. If you or your neighbours have seen deeper, tell me.

**Wind.** Himachal is in the 39 m/s basic wind zone
([BMTPC Vulnerability Atlas](https://vai.bmtpc.org/risk_tables/pdf/HIMACHALPRADESH_2018_1.pdf):
98.9% of the state). On a hill the code multiplies the wind speed by up to 1.36 near
the crest of a steep ridge, which nearly doubles the pressure. Naddi is a ridge
village, but I cannot tell from here whether your terrace gets that speed-up or is
tucked below it. So everything is run twice, and the truth is somewhere between the
two. The wind is tried from ten directions, with the roof both pressed and lifted, and
with the inside of the house both blown up and sucked down.

The wind has more to push on from the north-north-east (model angle 126°) than from
anywhere else, because from there it hits the side of both extensions at once. The
drag from that direction is two and a half times the drag from due east.

**Earthquake.** Zone V is the highest zone in IS 1893:2016. I used a low ductility
factor (2) because bolted castings cannot be relied on to bend before they break. If a
later edition of the code raises the shaking, there is room: the worst tube is at 0.46.

## How it was analysed, and why this way

**The tools were checked first.** The `onshape` server reads your document
("1V Dome Hubs 12ft-6ft", branch B1, assembly `1Vdome`); the strut section, its 2 mm
shell, the hub dimensions and the bolt-hole sizes above come straight from it. The
`freecad` server is connected to FreeCAD 1.1.4, and its FEM workbench does run through
the bridge: I ran its stock cantilever example end to end (mesh, CalculiX solve,
results read back).

**I did not use FreeCAD's FEM workbench for the dome, for two reasons.**

- Its beam tools are built for simple cases. This frame has 60 tubes each turned to
  its own angle, and a 2×4 turned the wrong way is half as strong. Setting that up by
  hand in a GUI is slow and easy to get wrong without anyone noticing. (I judged this
  from how the workbench handles beam orientation; I did not try to build the dome in
  it.)
- An FEM model nobody can check is worse than none. That stock example makes the
  point: with its default coarse mesh it reports a 41 mm deflection where the textbook
  answer is 88 mm, and nothing on screen says so.

**What I did instead** is the method a structural engineer would use for a frame like
this, kept small enough to check:

1. **A 3D frame analysis** written in about 250 lines of numpy (`structure/frame3d.py`).
   Every tube is a beam; loads are spread along the tubes the way the cladding delivers
   them. It was tested against 17 textbook answers (`structure/verify.py`; all within
   0.1%).
2. **An independent cross-check against CalculiX**, the solver inside FreeCAD, fed a
   hand-written input for the same frame (`structure/crosscheck_ccx.py`). The two
   programs work in completely different ways and agree to **1.5% on how far the frame
   moves and 0.1% on the support reactions**. Every load case also balances: what goes
   in equals what comes out at the supports, to a hundred-millionth of a newton.
3. **Hand-calculation checks to the steel code** IS 800:2007 for each tube (tension,
   buckling, bending both ways, all combined), each bolted tube end, and each
   ground-screw shaft (`structure/checks.py`).

The model was run eight ways to bracket what I cannot know:

- **Joints pinned or rigid.** A cluster of five small bolts cannot hold a tube rigidly,
  so "pinned" is the honest design case and is what the results below use. Rigid joints
  give lower numbers everywhere.
- **Screws flexible or perfectly stiff sideways.**
- **Cladding helping or not.** The roof panels and the wall planks, screwed to purlins,
  act as a stiff sheet across each triangle. "Braced" trusts that sheet to stop a tube
  bowing sideways within its own face; "bare" trusts nothing but the tubes. The truth
  is between them, nearer "braced" for the roof.

83 load combinations each, 664 in all.

## Results

A number below is the share of the code limit in use. 1.0 is the limit; the limit
itself has about 1.65 in hand before steel yields.

### The tubes

| | Sheltered plot (140 km/h gust) | Ridge crest (191 km/h gust) |
| --- | --- | --- |
| | *cladding braces → bare tubes* | *cladding braces → bare tubes* |
| Tubes beside the extension openings | 0.65 | **1.16** |
| Rafters | 0.56 → 0.91 | 0.70 → **1.01** |
| Upper ring, roof-side tube | 0.49 → 0.92 | 0.67 → 0.92 |
| Upper ring, wall-side tube | 0.42 → 0.66 | 0.68 → 0.92 |
| Other wall diagonals | 0.48 → 0.76 | 0.78 → **1.08** |
| Floor ring and floor beams | 0.33 → 0.41 | 0.56 → 0.63 |
| Extension rakers and floor edges | 0.37 → 0.41 | 0.63 → 0.66 |

By kind of event, worst tube anywhere:

| Event | Sheltered | Ridge crest |
| --- | --- | --- |
| Dead load only, finished building | 0.17 → 0.25 | same |
| Full floor, full loft, roof maintenance load | 0.38 → 0.60 | same |
| The above with design snow | 0.54 → 0.92 | same |
| Design wind | 0.65 → 0.71 | **1.16** |
| Wind lifting the building as it stands today, unlined | 0.47 → 0.48 | 0.92 |
| Wind and snow and full house together | 0.56 → 0.87 | 0.86 → **1.01** |
| Design earthquake | 0.30 → 0.46 | same |

What the pattern says:

- **Snow tests the roof, wind tests the walls.** Under snow the roof tubes are the
  busiest; under wind it is the wall diagonals.
- **The cladding matters.** Counting the roof panels and planks as bracing takes the
  snow case from 0.92 to 0.54. They are already there and already doing it.
- **The tubes beside the openings are a special case.** The side walls of each
  extension hang off the dome tube beside the opening, and push on it sideways, the
  2" way, where a 2×4 is half as strong. Nothing braces it in that direction: its
  partner tube sits 3½" away and is not connected to it. Hence the same 1.16 whether
  or not the cladding helps.
- Under working snow the frame moves about ¼" (7.5 mm) at most. Nothing to notice.

At the code limit, on the roof alone: **1.7 kPa of ground snow with bare tubes, 3.5 kPa
with the cladding bracing them**, which is about 3 to 6 ft of settled snow lying on the
ground. And **49 m/s (177 km/h)** of gust before the first tube reaches its limit.

### If the tube wall is not 2 mm

Worst tube anywhere, sheltered → ridge crest, bare tubes:

| Wall | YSt 210 steel | YSt 310 steel | Weight per metre |
| --- | --- | --- | --- |
| 1.6 mm | **1.19 → 1.50** | 0.95 → **1.11** | 3.8 kg |
| **2.0 mm (model)** | 0.92 → **1.16** | 0.71 → 0.84 | 4.7 kg |
| 2.5 mm | 0.74 → 0.92 | 0.54 → 0.65 | 5.8 kg |
| 3.2 mm | 0.56 → 0.67 | 0.41 → 0.50 | 7.4 kg |

This is why the first row of the questions table matters. Common "2×4" tube is sold in
all four of these walls and they look identical once painted.

### The hubs

**Each tube end pushes or pulls on its hub with at most 1.1 t (10.8 kN) on a sheltered
plot and 1.3 t (13.1 kN) on the ridge crest.** The busiest are the wall diagonals where
they meet the floor-ring hubs and the upper-ring hubs on the north-west (washroom) side.
The apex hub sees half that.

What five M6 bolts through a 2 mm tube wall into a 5 mm cast flange can take:

| Way of failing | Capacity per tube end |
| --- | --- |
| The bolts shearing (grade 4.6) | 2.1 t (20.4 kN) |
| The cast flange crushing at the bolt holes (140 MPa alloy, safety factor 2 for a casting) | 2.1 t (21.0 kN) |
| The tube wall crushing at the bolt holes | 3.2 t (31.7 kN) |
| Either of the first two, if the bolts sit loose in oversize holes (×0.7) | 1.5 t (14.3 kN) |

So the bolted joints are **0.53–0.64 used if the bolts fit their holes, up to 0.92 if
they are loose** in the 8 mm holes the model shows. Grade 8.8 bolts would nearly double
the first line. Fewer than five bolts, or self-drilling screws instead of bolts, would
cut it.

**The casting itself.** I cut each hub open in the computer, like a cake, through its
own axis every 3°, and measured the metal on the cut face
(`structure/hub_sections.py`). The thinnest cut has 2,018 mm² of aluminium in the
five-way hub, 1,932 mm² in the four-way and 616 mm² in the three-way. Even if three of
the hardest-pulled tubes all pulled across the same cut, the average stress is about
20 MPa, against a cautious 55 MPa for a plain sand casting: **about a third used**.

That is the limit of what calculation can honestly say about a casting. It says the
hubs are amply thick. It cannot say they are sound. A sand casting from a small foundry
can hide gas holes and shrinkage cracks, and cast aluminium gives little warning: it
does not bend first. **This is a matter for inspection, not arithmetic.**

### The ground screws

Working loads, which is how soil capacities are quoted (no safety factors applied):

| | Each of the 5 ring screws | Centre | Extension corners |
| --- | --- | --- | --- |
| Everyday, building finished | 1.0–1.2 t down | 0.3 t | 0.2–0.3 t |
| Full house and design snow | **2.6–3.3 t down** | 1.5 t | 0.2–0.7 t |
| Design wind, sheltered | 0.4 t sideways, no uplift | 0.4 t sideways | 0.2 t sideways |
| Design wind, ridge crest | **0.7–0.8 t sideways, up to 0.6 t uplift** | 0.7 t sideways | 0.4 t sideways, 0.1 t uplift |

Three things to take from this.

- **Downward** the screws carry 1 t each every day and are asked for up to 3.3 t in
  the code's worst case (every room at 200 kg/m², the loft full, and deep snow, all at
  once, which will rarely if ever happen). If a screw is overloaded downward it
  settles; you would see doors binding and cracks in the lining long before anything
  worse.
- **Uplift is small.** On a sheltered plot the building's own weight holds it down. On
  the ridge crest, today's light unlined building needs up to 0.6 t of hold-down per
  screw. The lining you are planning adds 1.5 t and helps.
- **Sideways is the question.** A ground screw is good at pushing down and pulling up
  and poor at resisting a sideways push, and yours take that push at the top of a
  1'-3" stalk. For a 76 × 3.2 mm shaft the bending at ground level is 0.63 of the limit
  on a sheltered plot and **1.17 on the ridge crest**, before asking whether the soil
  can hold the screw upright. A thicker shaft changes this completely (a 4½" (114 mm)
  shaft is 2½ to 3 times as strong), which is why I need to know what is there.

The numbers assume the floor deck ties the screw heads together so they share the
push. If the heads are not tied to one another, the busiest screw gets more.

### The loft

With the loft fully loaded the centre drop pulls down on the **apex hub with 1.2 t**
(11.6 kN, factored) and the hanger on the **north-west upper hub with 1.1 t**. Those are
design figures with the safety factor on; the actual weight is about 0.8 t and 0.7 t.
The dome itself barely notices: this is the same order as one tube's force. The
question is the fixing. The Onshape apex hub has an 8 mm hole through a small central
boss, and the model shows a round flange plate on top of the centre drop, but I could
not establish how the two are joined. For scale: one ordinary M8 bolt in tension is
good for about 1.0 t, so if the drop hangs from a single one of those it has nothing in
hand, and it is hanging from the casting. The hanger at the upper hub is on a single
larger bolt through two cast lugs, as the washroom photos show.

I could not see either detail properly, and the loft's radial beams are not in the
model, so the loft is **not assessed**. It needs looking at before anyone sleeps on it.

### The floor is not assessed

The frame model has the five floor-edge tubes but no joists. The Onshape `1Vdome-floor`
assembly turned out to contain the same frame and nothing more.

What I can say: a single 12 ft floor-edge tube, on its own, can carry only about
150 kg per metre run as a beam, which is a strip of fully loaded floor about 2 ft wide.
So the floor cannot be relying on the edge tubes alone. There must be joists going to
other supports, and I have assumed the centre screw takes a quarter of the floor. A
sketch of what is under the boards would let me check it properly. Until then, treat
the floor as unchecked. It has presumably been walked on for some time without
complaint, which is worth something, but it is not a calculation.

## The weak links, ranked

| | Used, sheltered → ridge | How sure am I | If it gave way |
| --- | --- | --- | --- |
| 1. Ground screws, sideways | 0.63 → **1.17** on an assumed shaft; soil unknown | Low: the screw is a guess | A lean, in an extreme storm. Sudden. |
| 2. Tube-to-hub bolts | 0.53 → 0.92 | Medium: bolt count from photos | Local, and the frame has other load paths. Casting cracks would be sudden. |
| 3. Tubes beside the openings | 0.65 → **1.16** | Medium: depends how the side walls are fixed | A bent tube. Visible, gradual. |
| 4. Loft hanging points | not known | Low | Sudden, with someone on it. |
| 5. Roof tubes in deep snow | 0.54 → 0.92 | Good | Sagging first. Gradual. |
| 6. Everything else | under 0.7 | Good | |

## What is solid, what is assumed, where an engineer matters

**Solid.** The geometry (measured from your model to the inch). The arithmetic (two
independent solvers agree; every case balances). The pattern of which parts are busy
and which are idle: that does not change with the assumptions. The conclusion that the
tubes away from the openings are adequate for snow, gravity and earthquake on a 2 mm
wall.

**Resting on assumptions.** Every number that depends on the tube wall, the steel
grade, the bolt count and the screw. The wind pressures on the faces: the code has no
table for a ten-sided leaning drum with a pyramid roof and two wedges stuck on it, so I
adapted its tables for round and pitched-roof buildings. That is ordinary practice but
it is judgement, and a wind engineer might move individual face pressures by 20–30%.
How the cladding shares load among the three tubes of a face (I took a third each).

**Where a qualified engineer's sign-off genuinely matters.**

- **The foundations.** No calculation from a desk can stand in for knowing the soil and
  testing a screw. This is the one I would not skip.
- **The hub castings and the loft fixings.** Someone who can look at them, and who
  carries the responsibility for saying they are sound.
- **If you ever need this on paper** for the panchayat, an insurer or a buyer: only a
  registered engineer's stamp counts, and they will want to redo the numbers their own
  way. This write-up and the scripts would save them most of the work.

A structural engineer from Dharamsala or Kangra, or the civil department at NIT
Hamirpur or IIT Mandi, would be the natural people to ask. One site visit should do.

## What to do about it

**1. Measure the four facts** (tube wall, bolt size and count, screw size, exposure)
and send them. No cost. I can re-run everything in a minute; the inputs are in one
block at the top of `structure/dome_model.py`.

**2. Test a ground screw and have an engineer look.** A pull test is simple: for
uplift, a short beam across two timber packs and a bottle jack with a gauge, or a chain
block and a crane scale, taken to about 1 t and held. For the sideways push, a chain
block from a tree or a parked vehicle to the screw head, with a crane scale in the
line, taken to about 1 t while someone watches the head for movement. If a screw moves
visibly under 1 t, the fix is one of:

- a concrete collar around each screw head at ground level, about 18" across and 18"
  deep, which turns the stalk from a flagpole into a post in a footing;
- knee braces from the floor frame down to the screw shafts near the ground;
- tying the floor hubs on the washroom side to the new stone plinth and 4" slab
  (drawing W-06) with steel brackets. That slab is the heaviest thing on site and it
  is about to be built right where the wind loads are largest. It would be a pity not
  to use it.

**3. Inspect the hubs and bolts.** Every hub, with a torch: look for hairline cracks at
the roots of the flanges and around the bolt holes. A dye-penetrant kit (three aerosol
cans from a welding supplier) makes cracks show red, but keep the sprays well away from
the EPS when the lining goes in. Check every bolt is present and tight, with a washer
under the nut. If the bolts are unmarked or loose in their holes, replacing them with
snug-fitting grade 8.8 bolts is a cheap, large gain. Do this before the lining covers
the hubs for good, and consider leaving a removable panel at each hub.

**4. Stitch the pairs beside the openings.** At the four tubes marked in red on ST-01,
bolt the two side-by-side tubes together through a spacer at two or three points along
their length. They then resist the sideways push together and the 1.16 roughly halves.
A fabricator's morning.

**5. Hold off loading the loft** until the centre drop and hanger fixings are known. If
the centre really hangs from one small bolt in the casting, pass a steel strap or
saddle over the top of the apex hub so the load sits on the hub rather than hanging
from it.

**6. Keep going with the lining.** Its weight helps against wind, and the board and
battens add to the bracing the tubes already get from the planks.

**Not needed:** thicker tubes, more struts in the dome proper, or anything for
earthquake.

## Checking the numbers yourself

```bash
cd ~/Documents/GitHub/naddi-cottage
```

```bash
.venv/bin/python structure/verify.py
```

```bash
.venv/bin/python structure/crosscheck_ccx.py
```

```bash
.venv/bin/python structure/analyse.py
```

The first should print `ALL OK`; the second compares against CalculiX (it needs
FreeCAD installed); the third takes under a minute and writes every number quoted here
to `structure/out/results.json`. `structure/sheet_st01.py` redraws the sheet from that
file.

One number worked by hand, so you can see there is no magic. A roof face is 62 sq ft
(5.8 m²) and in plan 4.6 m². Factored, with design snow, it carries
1.5 × (0.18 × 5.8 + 1.5 × 0.613 × 4.6) = 7.9 kN. Two-fifths of that goes to each
rafter tube, rising from nothing at the apex to most at the ring: 3.2 kN on a 12 ft
(3.66 m) span. The bending moment for that shape of load is 0.128 × load × span =
1.5 kN·m, of which the part square to the roof is about 1.2. The tube can take 3.7 the
strong way. Add the compression in the rafter and the sideways component and the
program's 0.9 for a bare rafter in snow is about what you would expect.

## Sources

- IS 875 (Parts 1–5), *Design loads for buildings and structures*; IS 800:2007,
  *General construction in steel*; IS 1893 (Part 1):2016, *Earthquake resistant
  design*. Effective widths for thin walls from EN 1993-1-5; the safety factor on
  castings from EN 1999-1-1.
- Wind zone: [BMTPC Vulnerability Atlas of India, Himachal Pradesh table](https://vai.bmtpc.org/risk_tables/pdf/HIMACHALPRADESH_2018_1.pdf).
- Snow depths at Naddi and McLeod Ganj: [McLeod Ganj weather blog, Feb 2014](https://mcleodganj-weathergeek.blogspot.com/2014/02/highlight-of-season-pm15feb14.html),
  [Jan 2019](https://mcleodganj-weathergeek.blogspot.com/2019/01/instability-lingers-pm23jan19.html);
  [The Tribune](https://www.tribuneindia.com/news/himachal/locals-rush-to-naddi-to-enjoy-snow-29800).
- Geometry: `onshape/dome_struts.glb` and the Onshape document itself; see
  `docs/onshape_frame_check.md`.
