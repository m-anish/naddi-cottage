# Structural model of the dome frame

The write-up is `docs/structural_assessment.md`; the summary sheet is
`drawings/dome/ST01_structure_summary.png`. This folder holds the calculation behind
them. Everything runs with the repo's `.venv` (numpy and matplotlib only).

| File | What it does |
| --- | --- |
| `extract_frame.py` | Reads `onshape/dome_struts.glb`: every part's centreline, section and which way its depth faces → `out/frame_members.json` |
| `frame3d.py` | The 3D frame solver (direct stiffness, beam elements, pinned ends, loads along members) |
| `verify.py` | 17 textbook checks of the solver. Should print `ALL OK` |
| `dome_model.py` | The dome: nodes, tubes, supports, load cases, load combinations. **All assumed inputs are in `INPUTS` at the top** |
| `checks.py` | Capacities to IS 800: tubes, bolted tube ends, ground-screw shaft |
| `analyse.py` | Runs 8 model variants × 83 combinations × 2 wind exposures → `out/results.json`, log in `out/analyse_log.txt` |
| `crosscheck_ccx.py` | Same frame solved by CalculiX (needs FreeCAD installed) and compared |
| `hub_sections.py` | Slices the cast hubs and measures the metal on each cut → `out/hub_sections.json` |
| `sheet_st01.py` | Draws sheet ST-01 from `out/results.json` |

Run, from the repo root:

```bash
.venv/bin/python structure/verify.py
.venv/bin/python structure/analyse.py        # about a minute
.venv/bin/python structure/sheet_st01.py
```

## When Anish confirms the real values

Change them in `INPUTS` in `dome_model.py` (tube wall `tube_t`, grade `fy`/`fu`,
ground-screw shaft `stub_D`/`stub_t`) and in the default arguments of `bolt_group()` in
`checks.py` (bolt count, diameter, grade), then re-run `analyse.py` and
`sheet_st01.py` and update the numbers in the write-up from `out/analyse_log.txt`.

## Units and conventions

- Geometry is in feet in `dome_model.py` (as measured) and converted to metres for the
  solver. Forces in newtons, moments in newton-metres.
- Origin at the floor centre, z up. Lower-ring hubs `L18 … L306`, upper-ring hubs
  `U54 … U342`, apex `A`; the number is the plan angle. Washroom at 198°, east
  extension at 54°. Compass bearing = 144° − plan angle.
- Tube names: `raf{hip}_{face}` rafters, `ur{a}_r` / `ur{a}_w` the roof-side and
  wall-side tubes of the upper ring, `dg{L}_{U}_d` / `_u` the wall diagonal belonging to
  the "down" or "up" wall face, `fb..` the long floor beams, `lr..` the plain floor-ring
  tubes.
- Utilisation 1.0 = the IS 800 limit, with its factors of 1.5 on loads and 1.10 on steel.

## Where the Onshape model is

Document **"1V Dome Hubs 12ft-6ft"**, id `966089be573aed8795ce08e7`, branch **B1**
(workspace `894fc1306dcda50ec7610802`). Assembly `1Vdome` is element
`e07e26e3030b2c0c24dbf773`; the tube is Part Studio `strut-12ft`
(`b7ed1a4ec8695eff8bf464ec`); the five-way hub is `5-way-alternate`
(`a9f94866f2292df5b827d46e`), the four-way `4-way-alternate`
(`26fe58f7de629d09f4b595c1`); hub dimensions are in the Variable Studio `Large`
(`45e8bc702c4ab746bcb97863`). The Onshape API allowance is limited: the glb in
`onshape/` already holds the geometry, so go back to Onshape only for things it lacks.

## Known limits of the model

- Hubs are points: tube ends meet at the hub centre. Real ends stop 3½" short.
- The floor joists and the loft beams are not in the Onshape model and are not checked.
- Wind pressures on the faces are adapted from the IS 875-3 tables for round and
  pitched-roof buildings; no code table fits this shape.
- Each face's load is shared a third to each of its three tubes.
