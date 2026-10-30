# Naddi cottage: dome interior and washroom

Design work for Anish's cottage in Naddi village, above McLeod Ganj, Dharamsala, Himachal Pradesh (about 2,000 m; around 3,000 mm of rain a year; frosty winters, occasional snow). One person lives here, with occasional guests.

This folder continues a claude.ai conversation (Oct 26–30, 2026). Everything decided there is summarised below; the full write-ups are in `docs/`.

## Working with Anish

- Plain language. He is not a programmer; explain any setup step by step.
- Feet and inches first, metric in brackets where it helps (e.g. 4" (110 mm)). Costs in ₹, large sums in lakh.
- Local, buildable answers: materials and trades available around Dharamsala and Kangra.
- He likes to compare options visually: renders side by side, with and without.
- He will interact with Blender through its GUI while you drive it through the Blender MCP server (see SETUP.md). Save his file before running code in his Blender session.

## The building

**Main dome**: 1V geodesic dome, an icosahedron with 12 ft struts, cut at its lower ring.
- 15 triangles: a ring of 10 wall facets ("up" and "down" triangles alternating, leaning about 11° out and in) and 5 roof facets sloping about 37°.
- Floor on the lower ring: pentagon, ~250 sq ft to the outer skin, ~220 sq ft inside the lining.
- Upper ring 10'-2" (10.21 ft) above the floor; apex 16'-6" (16.51 ft); icosahedron centre 5'-1" above the floor; inradius 9.07 ft.
- Steel frame: 2×4" struts (painted yellow); 1×2" vertical purlins carry horizontal fibre-cement planks outside (painted brown).
- Roof: 80 mm PUF sandwich panels, tin both faces, off-white inside. Staying as is; the roof struts below are painted off-white.
- Floor: raised metal frame, 20 mm fibre-cement base board, wood floor to come on an underlay. The void under it is sealed in painted tin, lined with 1" foam, over HDPE and weed-control fabric.
- A loft at 9'-0" over the washroom side is ASSUMED (not confirmed). The ladder will be a proper wooden one.
- Windows and doors in the model are placed approximately from photos (`OPENINGS` in `code/dome.py`).
- Anish has the exact steel structure in Onshape (struts only, no walls). He will export it into `onshape/`. When it arrives, check it against the constants in `code/dome.py` and switch the model to the real geometry.

**Washroom**: the extension of one dome triangle (front opening 12 ft equilateral, ~7 ft deep, back wall ~7 ft, estimated). Front and back walls lean back; Anish estimated 15°, dome geometry suggests about 11°; `code/geom.py` uses 15°. Toilet floor is 1 ft above the upper terrace.

**Site**: terraced field. House, washroom and biodigester on the upper terrace; the biodigester outlet is about 12" above the lower terrace (to be checked with a water-level tube). Reed bed and soak trench go on the lower terrace.

## Decisions so far

**Main dome walls** (docs/dome_interior_walls.md, drawing D-01)
1. Planks (existing), then a 50 mm drained gap (the purlin depth), kept open; its foot closed from the floor void with insect mesh and a flashing that weeps out over the tin.
2. Optional breather membrane.
3. 50 mm FR-grade EPS continuous over the purlins' inner face, flush with the 2×4" struts; thin foam tape on the 2×4 faces only.
4. 25 mm treated timber battens, horizontal at 16" (400 mm) centres, screwed through the EPS.
5. 8 mm fibre-cement board on every wall, full height (fire protection for the EPS). 10 mm on any lower wall without pine; 12 mm near a stove.
6. Below the 3'-3" datum (sill line): 15 mm timber strips over the board, vertical pine boards secret-nailed to them (backs oiled), a timber datum ledge on top, skirting last. The pine stands 25–30 mm proud of the upper wall.
7. Above the datum: limewash (mineral primer or 1.5–2 mm lime skim, then 2–4 thin coats, above 8 °C), or matte emulsion over alkali-resistant primer.
- No polythene behind the main-room lining.
- Wainscot finish depends on the floor tone: natural pine over a darker floor; limewashed or painted boards over a pine-tone floor (renders C1, C2).
- Recommended: Scheme 2 (pine wainscot, limewash above, roof struts painted), about ₹0.8–1.5 lakh for ~495 sq ft of wall.
- Wiring: everything in conduit (PVC cable must not touch polystyrene); metal boxes in the wainscot band (57 mm from pine face to foam); earth the steel frame; 30 mA RCCB.
- Rejected: marine ply as the lining (burns over the EPS; limewash won't take). Parked by Anish: CNC/laser-cut medallions at the upper vertices (code in `code/parked/`).
- Order of work: battens and wiring, board everywhere, finish the upper walls, wood floor, then strips, pine, ledge and skirting.

**Washroom** (docs/washroom_design.md, drawings A-01 to A-05, W-06, renders R1–R7)
- Layout A: dry zone at the front (WC left, vanity right, on 2'-9" service ledges), shower at the back under the ridge, raked glass screen; vertical door portal.
- Palettes: 1 Slate & Lime (recommended), 2 Bright & Panelised, 3 Kota & Whitewash (low cost).
- Floor: stone plinth wall to firm ground; rubble fill; sand blinding; 200 µm polythene; 50 mm XPS + 25 mm XPS edge strip; 75–100 mm M15–M20 slab with mesh, to falls (1:80 dry, 1:50–60 shower); 2-coat polymer cement waterproofing; tile or slate in C2 adhesive.

**Wastewater** (drawings S-01 to S-03)
- Toilet only → 500 L biodigester (4 × 4 × 1.15 ft, rated for 5; inlet 8" below the upper terrace) → test chamber T → junction J → reed bed → outlet chamber → soak trench.
- T: 12 × 12" brick box on the lower terrace, lid ~18" up, inlet turned down 6" above the outlet; jar test (clear/pale tea = working; grey, murky, rotten-egg smell = recharge bacteria).
- Greywater bypasses the biodigester: grease trap (kitchen) + two-chamber 200–300 L settling tank → J.
- Reed bed: one horizontal subsurface-flow bed, 9 ft (inlet to outlet) × 6 ft, 2 ft of gravel. Levels from the lower terrace ground: walls +9", gravel +3", inlet spreader +1", water −1", outlet −8", floor −20"/−21", dig −24". 1'-6" zones of 1½–3" stone at each end; ½–¾" washed gravel between with 3" pea gravel on top; 4" perforated spreader and collector; swivel elbow in an 18 × 18" outlet chamber; stone walls + plaster + 0.5 mm HDPE liner; Phragmites 18" apart.
- Pipes: PVC SWR Type B (~3.2 mm wall). 110 mm WC → biodigester → T → J → bed; greywater 40–50 mm branches, 75 mm main; 110 mm perforated in the bed and soak trench.

## Open questions

- Bukhari or other stove: where? (No timber behind it.)
- Wiring plan; final floor wood and its tone.
- Washroom back-wall width and the real lean angle.
- Biodigester outlet height above the lower terrace (assumed 12").
- What the east extension is for.
- Whether to drop the toilet floor and/or move the shower inboard (see the headroom
  budget in `docs/onshape_frame_check.md`).

Answered by the Onshape export (30 Oct 2026) — **read
`docs/onshape_frame_check.md` before touching `code/dome.py`**:

- **The loft is real**: a suspended platform at **8'-5"** (not the assumed 9'-0"),
  hung from five hangers at the upper-ring vertices plus a 3×3" drop from the apex,
  with radial struts to the NNE, NW and SW hangers — a 144° sector over the washroom
  side. The radial struts are missing from the export and need modelling.
- **`dome.py` is rotated 108° from the real frame.** Two constants fix it.
- The frame has **two extensions**, not one: the washroom (7'-8½" deep, facing NW)
  and a second one 6'-5¾" deep facing **east**, which sets the building's compass
  orientation (bearing = 144° − model angle).
- The dome stands **1'-3" above ground** on screw anchors, one per vertex plus one at
  the pentagon centre.
- Theoretical edge 12'-0"; actual steel strut **11'-5"**, the rest hub.
- The upper ring is **doubled** (10.20 and 10.44 ft); the roof is rafters with eaves,
  not bare cap edges; the floor is spanning beams, not a ring.

## The code (`code/`)

All geometry is in feet, converted to metres for Blender (`M = 0.3048`). Origin at floor centre, z up.

| File | What it makes |
| --- | --- |
| `geom.py` | Washroom geometry and design parameters |
| `scene.py` | Washroom Blender scene, materials, palettes p1/p2/p3, shared helpers, line renders |
| `dome.py` | Main dome scene: icosahedron faces (`up{k}`, `down{k}`, `cap{k}`), lining, openings, struts, loft, furniture, wall schemes in `SCHEMES` |
| `drawings.py` | Washroom plans and sections (A-01 to A-05) |
| `wall_section.py` | D-01 wall build-up |
| `floor_layers.py` | W-06 washroom floor make-up |
| `wastewater.py` | S-01 wastewater system |
| `reedbed.py` | S-02 reed bed section and layers, S-03 plan and build steps |
| `compare.py` | Side-by-side comparison sheets from graded renders |
| `grade.py` | Light colour grade for renders: `python3 grade.py in.png out.jpg` |
| `parked/` | Vertex-medallion experiment (paused) |

Outputs go to `code/out/`.

Run:
```bash
# drawings (matplotlib, numpy, pillow, shapely)
python3 code/drawings.py && python3 code/wall_section.py && python3 code/floor_layers.py
python3 code/wastewater.py && python3 code/reedbed.py

# renders, with Blender as a Python module (pip install bpy, if a wheel exists for this Python)
python3 code/dome.py w_wainscot_limed hero code/out/test.png 64 1200 800
python3 code/scene.py p1 v1 code/out/wash.png 64 1200 800

# or with the Blender app (args after --)
/Applications/Blender.app/Contents/MacOS/Blender -b --python code/dome.py -- w_wainscot_limed hero code/out/test.png 64 1200 800
```
- Dome schemes: `w_lime`, `w_wainscot`, `w_wainscot_limed`, `w_wainscot_paint`, `w_wainscot_pine`, `w_timber`, `w_wainscot_pinefloor`, `w_lime_pinefloor` (older `lime`, `wainscot`, `canopy`, `frame`, `timber`, `combo` assume a lined roof). Views: `hero`, `back`, `cut`, `line_cut`, `line_hero`.
- Washroom views: `v1` (from the door), `v2` (from the shower), `v3`, `v4`, `cut`, `line_v1`, `line_v2`, `line_cut`.
- Built and tested with bpy 5.2.3 LTS. If running inside Blender's own Python, install `shapely` and `imageio` into it.
- Render settings: Cycles CPU, AgX "Medium High Contrast", 64 samples, denoised; 1200 × 800 took ~6 min on 2 cloud cores. Use EEVEE or low samples for interactive previews.
- Drawing style: matplotlib with the Inter font (`brew install --cask font-inter`); colours ink #1d1d1b, grey #8a8780, accent #b5552b, water #3d7ea6; sheet codes in the top-right corner.

## Other folders

- `drawings/`, `renders/`: the latest delivered sheets and renders.
- `photos/`: Anish's site photos (washroom extension, dome interior, biodigester pit).
- `docs/`: markdown copies of the two design docs (images stripped). The live docs are on claude.ai, and can't be edited from here: treat `docs/` as the working copy.
  - Washroom: https://claude.ai/artifact/P5yVDSaWoC734S8383WT8Z
  - Dome interior walls: https://claude.ai/artifact/5LzB56rCFacnNBF7GFnBfp
- `onshape/`: drop the Onshape export here (see `onshape/README.md`).

## Next steps

1. ~~Connect the Blender MCP server~~ — registered; waiting on the Blender install to
   enable the add-on and run the test cube.
2. ~~Check the Onshape export against `dome.py`~~ — done, see
   `docs/onshape_frame_check.md`. **Still to do**: rebuild the dome scene on the real
   frame (the +108° rotation, `GROUND_Z`, the suspended loft, the doubled upper ring,
   the second extension, rafters with eaves).
3. Rebuild the lining schemes on the real geometry and redo the key renders for comparison.
4. Re-test the washroom layout against the real roof line (headroom at the back).

### This machine (Intel Mac, macOS 15.7)

Blender 5.x is **arm64-only on macOS**, so this Mac runs **Blender 4.5.15 LTS**, the
last Intel build — not the 5.2.3 the scripts were written against. `bpy==4.5.15` is
the matching wheel. Homebrew has no `uv` bottle for Intel any more (uv lives in
`~/.local/bin`), and `cryptography` must be held to `<49` for an Intel wheel. The
Blender MCP server runs from its own venv at `~/.local/share/blender-mcp-env`.
