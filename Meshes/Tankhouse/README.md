# Tankhouse (SM_TankhouseBuilding and layout reference)

Copper electrorefining tankhouse: hall, basement and crane runway. This README is also the
**layout reference** for every tankhouse asset (cells, cathodes, crane, rectifiers and busbars,
short-circuit detection, electrolyte circulation, liberator cells) and for the anode preparation
and cathode stripping machines built in other threads.

Built in Blender 5.2.2, metres, Z up. Files: `SM_TankhouseBuilding.blend`, `SM_TankhouseBuilding.fbx` (FBX_SCALE_NONE, mesh only),
`Preview_Exterior.png`, `Preview_Interior.png` (walls and roof hidden), `Preview_Basement.png`,
`Preview_PlantOverview.png` and `Preview_PlantCutaway.png` (every tankhouse asset placed; made by render_tankhouse_overview.py). Rebuild scripts:
`Tools/Blender/Tankhouse/` (shared constants in `th_layout.py`).

## Tankhouse coordinates

- **Origin:** west end of the cell area, on the hall centreline, at operating floor level (z 0).
  +X runs along the hall (west to east), +Y across it (south to north).
- **Placement in the plant:** put the tankhouse origin at **flash-furnace world
  (0, -150, 0) with no rotation**. All tankhouse
  assets use this one origin, so they line up when placed at the same transform. My choice: south
  of the smelter, clear of the slag concentrator (x -240 to -55, y 180 to 300) and the acid plant
  (east of x 69.6, tanks to the north). World extents including annexes: x -32 to 82,
  y -177 to -123.
- **Anode set:** SM_RotaryAnodeFurnace and its casting wheel / take-off / stacking machines are not
  tied to the flash furnace. Anode stacks reach the tankhouse by forklift through the service bay
  doors, so their placement is free.

## Key numbers

| Item | Value |
|---|---|
| Hall | x -32.0 to 64.0, y ±15.0; eaves 12.5, ridge 14.5 (+ ridge vent); columns every 6.0 m |
| Service bay (at grade, forklifts) | x -32.0 to -4.0. Doors: south and north walls at x -21 to -15 (6 × 6 m), west wall centre (6 × 6 m) |
| Operating floor / walkways | z 0. Cells stand 0.80 m above it |
| Basement (piping, launders, leak detection) | z -3.0, x -2.0 to 62.0, y ±12.6. Stair at x 55.0 to 61.0, y 10.0 to 11.4 |
| Cell rows | A y -9.45, B y -3.15, C y 3.15, D y 9.45 (row centrelines) |
| Cells per row | 40, total 160 |
| Cell pitch along a row (X) | 1.32 m; cell i centre x = 0.66 + 1.32·i (cells span x 0 to 52.8) |
| Cell outside | 1.28 (X) × 5.10 (Y) m, bottom z -0.52, rim z 0.80 |
| Electrode seat line (top of intercell bars) | z 0.85 |
| Electrolyte level | z 0.73 |
| Electrodes per cell | 45 anodes, 46 cathodes, 100 mm anode pitch (see ElectrolyticCell/README.md for positions) |
| Crane rails | y ±14.4 (span 28.8 m), rail top z 8.0, bridge travel x -28.0 to 60.0 |
| Crane hook seat | in a cell 0.85; at the transfer stands 1.2; travel 2.45 |
| Current path | rectifier (+) → row D east end, west along D → C, east along C → B, west along B → A, east along A → rectifier (−). See RectifierBusbar/README.md |

## Transfer points (crane ↔ machines)

Each transfer stand holds one full cell load: electrodes hanging along Y at the cell spacing, with
their lugs / hanger bar ends on two rails at x ±0.60 from the stand centre, seat z 1.2.
The crane picks or sets a load with the bale centred on the stand. The anode preparation and
cathode stripping machines (other thread) should deliver to / collect from these points, or replace
the stands with their own racks at the same position and seat height.

| Stand | Tankhouse (x, y, seat z) | World (x, y) |
|---|---|---|
| AnodeIn | (-12.0, -8.0, 1.2) | (-12.0, -158.0) |
| AnodeScrapOut | (-22.0, -8.0, 1.2) | (-22.0, -158.0) |
| CathodeOut | (-12.0, 8.0, 1.2) | (-12.0, -142.0) |
| CathodeBlankIn | (-22.0, 8.0, 1.2) | (-22.0, -142.0) |

- **AnodeIn:** 45 prepared anodes from the anode preparation machine, spaced for the crane
  (anode pitch 0.10 m).
- **AnodeScrapOut:** 45 spent anodes (anode scrap) to the anode scrap washing machine.
- **CathodeOut:** 46 cathodes with copper deposit to the cathode stripping machine.
- **CathodeBlankIn:** 46 stripped blanks back from the stripping machine.

## Annexes (other tankhouse assets, same origin)

| Asset | Where |
|---|---|
| SM_RectifierBusbar | rectifier yard north of the east end (x 40 to 60, y 15 to 27), DC bus in the basement at the east end |
| SM_ElectrolyteCirculation | circulation annex south of the west end (x -32 to 0, y -27 to -15), headers in the basement |
| SM_LiberatorCells | liberator annex east of the hall (x 64 to 82, y -10 to 4) |
| SM_ShortCircuitDetection | crane-mounted IR camera, cell voltage boxes on the rows, handheld gaussmeter |

## Parts and pivots

| Object | Use |
|---|---|
| TH_Frame | static steel frame |
| TH_CraneRunway | runway girders and rails |
| TH_OperatingFloor | slabs, gratings between rows |
| TH_Basement | slab, walls, cell support beams, trench liners, stair |
| TH_Walls / TH_Roof | hide for cutaways |
| TH_TransferStand_* | separate so the machine thread can replace them |

| Object | Pivot |
|---|---|
| TH_Basement | (0.00, 0.00, 0.00) |
| TH_CraneRunway | (0.00, 0.00, 0.00) |
| TH_Frame | (0.00, 0.00, 0.00) |
| TH_OperatingFloor | (0.00, 0.00, 0.00) |
| TH_Roof | (0.00, 0.00, 0.00) |
| TH_TransferStand_AnodeIn | (-12.00, -8.00, 0.00) |
| TH_TransferStand_AnodeScrapOut | (-22.00, -8.00, 0.00) |
| TH_TransferStand_CathodeBlankIn | (-22.00, 8.00, 0.00) |
| TH_TransferStand_CathodeOut | (-12.00, 8.00, 0.00) |
| TH_Walls | (0.00, 0.00, 0.00) |

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off. The hall is large (96 × 30 m),
so consider splitting TH_Walls / TH_Roof into HLODs.

## Dimensions

| Item | Status |
|---|---|
| Cell size, electrodes per cell, electrode pitch | Sourced (see ElectrolyticCell/README.md) |
| Refineries have 800–2,400 cells | Sourced. This tankhouse has 160, a deliberately small game-scale refinery (about 45–50 kt/yr of cathode at 30 kA and 95 % current efficiency, my calculation) |
| Parallel cell rows with a crane bridge across them; crane rails parallel to the rows in US4392934, here the bridge runs along the hall and spans all four rows | Layout: own design based on US4392934 and photos |
| Hall size, eaves, basement depth, walkway widths, doors, ridge vent | Estimated |
| Rows on a basement with leak trenches | Estimated (common practice, no drawing found) |

Sources: /mnt/project-files/copper_refinery_equipment.md §8; research companion §8; US4392934.
