# SM_ElectrolyteCirculation

Electrolyte circulation for the tankhouse. The electrolyte is kept at 60–65 °C, filtered and dosed
with additives, and fed to every cell.
- **Pump room annex:** south of the hall's west end, x -32.0 to 0.0, y -27.0 to -15.0,
  floor z -5.0 (below the hall basement, so the cell overflow returns by gravity). Stair down
  from grade at the west wall; monorail over the pumps.
- **Circulation tanks:** 2 FRP tanks Ø6 × 4 m, about 158 m³ working volume in total.
- **Pumps:** 3 horizontal centrifugal pumps (2 duty, 1 standby). Each rotor (impeller, shaft,
  coupling hub) is a separate object that spins about its local Y axis.
- **Filters:** 2 vertical pressure filters.
- **Heat exchangers:** 2 plate-and-frame exchangers with titanium plates, steam heated.
- **Additive dosing:** glue and thiourea tanks with dosing pumps on one skid.
- **Basement:** a feed manifold at x -1.2 supplies four row feed headers (one under the feed
  flanges of each row, z -1.3), each with a riser and flow valve to every cell. The cells
  overflow into four open return launders (floor z -1.5), which drain at the west end into the
  return main back to the tanks.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates (lines up with SM_TankhouseBuilding and
SM_ElectrolyticCell). Files: `SM_ElectrolyteCirculation.blend`, `SM_ElectrolyteCirculation.fbx` (FBX_SCALE_NONE). Previews:
`Preview_PumpRoom.png` (shell hidden), `Preview_Basement.png` (hall basement with headers and
launders, cells shown).

## Connection points

| Point | Position (tankhouse) |
|---|---|
| Cell feed risers end at each cell's feed flange | (0.66 + 1.32·i, row y -2.65, -1.025) |
| Cell drain flanges discharge into the launders | (0.66 + 1.32·i, row y +2.65, -1.0) |
| PHE 1 Steam in | (-8.25, -19.7, -3.1) |
| PHE 1 Condensate out | (-8.25, -19.7, -4.4) |
| PHE 2 Steam in | (-4.75, -19.7, -3.1) |
| PHE 2 Condensate out | (-4.75, -19.7, -4.4) |
| Bleed to liberator cells | (-0.6, -16.6, -1.8) |

The bleed line to SM_LiberatorCells is left as a stub at the annex's east wall. The route to the
liberator annex at the far east end of the hall is open; run it along the south wall of the hall.

## Parts and pivots

| Object | Use |
|---|---|
| EL_AnnexShell | walls above grade and roof; hide for cutaways |
| EL_AnnexPit | pit floor, retaining walls, bund kerbs, sump |
| EL_Access | stair, monorail |
| EL_Tanks, EL_Pumps, EL_FiltersExchangers, EL_AnnexPiping | static |
| EL_PumpRotor_1..3 | rotate about local Y (the pump shaft). About 1,480 rpm (4-pole motor, estimated) |
| EL_FeedHeaders, EL_ReturnLaunders | static, basement |

| Object | Pivot |
|---|---|
| EL_Access | (0.00, 0.00, 0.00) |
| EL_AnnexPiping | (0.00, 0.00, 0.00) |
| EL_AnnexPit | (0.00, 0.00, 0.00) |
| EL_AnnexShell | (0.00, 0.00, 0.00) |
| EL_FeedHeaders | (0.00, 0.00, 0.00) |
| EL_FiltersExchangers | (0.00, 0.00, 0.00) |
| EL_PumpRotor_1 | (-15.00, -19.20, -4.25) |
| EL_PumpRotor_2 | (-13.00, -19.20, -4.25) |
| EL_PumpRotor_3 | (-11.00, -19.20, -4.25) |
| EL_Pumps | (0.00, 0.00, 0.00) |
| EL_ReturnLaunders | (0.00, 0.00, 0.00) |
| EL_Tanks | (0.00, 0.00, 0.00) |

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Electrolyte 60–65 °C in, 55–60 °C out; 40–50 g/L Cu, 180–200 g/L H2SO4; glue 1–10 mg/L | | Sourced (research companion §8) |
| Flow 0.015–0.02 m³/min per cell → 160 cells × 0.02 = 192 m³/h | | Sourced rate, my total |
| Pump room under the cell floor; titanium plate heat exchangers | | Sourced (research file §8) |
| Tanks, pumps, filters, heat exchanger sizes and the annex layout | | Estimated |
| Gravity return with a pump room below the hall basement | | Own design |

Sources: /mnt/project-files/copper_refinery_equipment.md §8; research companion §8 ([S5], [S6]).
