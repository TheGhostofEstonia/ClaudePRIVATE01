# SM_LiberatorCells

Liberator (decopperizing) cells. A bleed stream of tankhouse electrolyte is electrowon here with
insoluble lead anodes to take out copper, and then arsenic, antimony and bismuth before the
solution goes to the nickel sulfate plant. The last stage can release **arsine** gas, so every
cell has an FRP hood that exhausts through a scrubber, fan and stack.

- **Annex:** east of the hall, x 64.0 to 82.0, y -10.0 to 4.0, 9.0 m high, sharing
  the hall's east wall. Scrubber, fan and 20 m stack stand outside the east wall (x about 84–87).
- **Cells:** one row of 8 cells. The shells are SM_ElectrolyticCell instances (not repeated
  in this FBX). They stand in a pit (floor z -1.8) on support beams, so their rims are 0.8 m above
  the annex floor like in the main hall.
- **Electrodes:** 45 lead anodes (LC_LeadAnode, exported here) and 46 permanent cathodes
  (SM_PermanentCathode) per cell, same positions as in the main cells.
- **Hoods:** 8 separate hoods (LC_Hood_1..8), each lifted off by the annex crane for harvesting.
- **Supply:** feed tank (bleed in), product tank (decopperized solution out), pumps, a small
  rectifier on its own DC circuit, and a 5 t single-girder crane with a lifting beam.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates. Files: `SM_LiberatorCells.blend`, `SM_LiberatorCells.fbx`
(FBX_SCALE_NONE). Previews: `Preview_Exterior.png`, `Preview_Cells.png` (shell hidden, one hood
lifted).

## Cell placement (SM_ElectrolyticCell instances)

| Cell | Location (tankhouse), no rotation |
|---|---|
| 0 | (66.86, -3.0, 0) |
| 1 | (68.18, -3.0, 0) |
| 2 | (69.50, -3.0, 0) |
| 3 | (70.82, -3.0, 0) |
| 4 | (72.14, -3.0, 0) |
| 5 | (73.46, -3.0, 0) |
| 6 | (74.78, -3.0, 0) |
| 7 | (76.10, -3.0, 0) |

Lead anode j: LC_LeadAnode at (cell x, anode_y(j), 0.85) with no rotation (header bar along X).
Cathode k: SM_PermanentCathode at (cell x, cathode_y(k), 0.85). anode_y / cathode_y as in
ElectrolyticCell/README.md; use the even pattern for cells 0, 2, 4, 6.

## Connection points

| Point | Position (tankhouse) |
|---|---|
| Scrubber bleed (to effluent treatment) | (85.5, -4.0, 0.8) |
| Bleed electrolyte in (from SM_ElectrolyteCirculation) | (64.3, 2.0, 2.2) |
| Decopperized solution out (to the nickel sulfate / evaporator plant) | (72.8, 3.2, 0.8) |

## Parts and pivots

| Object | Use |
|---|---|
| LC_AnnexShell | walls and roof; hide for cutaways |
| LC_FloorPit | floor, pit, beams, launder, feed header, end supports and end bar |
| LC_Hood_1..8 | lift +Z at the pivot (lifting lugs) to remove |
| LC_Exhaust | header, branch ducts (on the hoods), scrubber, fan, stack |
| LC_TanksRectifier | tanks, pumps, rectifier, DC bus |
| LC_CraneRunway | static |
| LC_CraneBridge | translate X, x 66 to 80 |
| LC_CraneHoist | child of the bridge, translate Y between the rails; hook block and lifting beam are part of it (scale the rope in Unreal or split if needed) |
| LC_LeadAnode | instance per anode position, origin at the header bar underside centre |

| Object | Pivot |
|---|---|
| LC_AnnexShell | (0.00, 0.00, 0.00) |
| LC_CraneBridge | (70.82, -3.00, 6.50) |
| LC_CraneHoist | (70.82, -3.00, 6.75) |
| LC_CraneRunway | (0.00, 0.00, 0.00) |
| LC_Exhaust | (0.00, 0.00, 0.00) |
| LC_FloorPit | (0.00, 0.00, 0.00) |
| LC_Hood_1 | (66.86, -3.00, 2.25) |
| LC_Hood_2 | (68.18, -3.00, 2.25) |
| LC_Hood_3 | (69.50, -3.00, 2.25) |
| LC_Hood_4 | (70.82, -3.00, 2.25) |
| LC_Hood_5 | (72.14, -3.00, 2.25) |
| LC_Hood_6 | (73.46, -3.00, 2.25) |
| LC_Hood_7 | (74.78, -3.00, 2.25) |
| LC_Hood_8 | (76.10, -3.00, 2.25) |
| LC_LeadAnode | (0.00, 0.00, 0.00) |
| LC_TanksRectifier | (0.00, 0.00, 0.00) |

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Liberator cells look like the main cells and have hoods for arsine | | Sourced (research file §9, WO2017191458A1; arsine risk in research companion §9) |
| 8 cells, same shells as the main cells, lead anodes 0.96 × 0.98 m × 12 mm | | Estimated |
| Hood, duct, scrubber, fan and stack sizes, annex layout, 5 t crane | | Estimated / own design |
| Bleed 0.1–0.5 m³ per t Cu | | Sourced (research companion §8) |

Sources: /mnt/project-files/copper_refinery_equipment.md §9; research companion §9 ([S5]);
WO2017191458A1, WO2017144912A1.
