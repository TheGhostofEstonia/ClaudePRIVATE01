# SM_ShortCircuitDetection

Short-circuit detection for the tankhouse. A short (a bent cathode or a nodule touching an anode)
pulls current through one electrode pair; the hot contacts show up on a thermal camera, the cell
voltage drops, and the magnetic field around the shorted hanger bar rises. This set covers the
three methods the research notes list:
- **Crane IR camera:** a thermal camera on a pan/tilt head under the tankhouse crane's trolley,
  scanning the cell tops as the crane travels.
- **Cell voltage sensors:** one sensor box per cell on the -Y end wall, wired to the intercell bars
  on both sides of the cell, reporting to a display board at the west end of each row.
- **Handheld gaussmeter:** a Hall probe on a fibreglass pole that an operator runs along the
  hanger bars to find the shorted cathode.

Built in Blender 5.2.2, metres, Z up. Files: `SM_ShortCircuitDetection.blend`, `SM_ShortCircuitDetection.fbx` (FBX_SCALE_NONE, 6 objects).
Preview: `Preview_Overview.png`.

## Placement (tankhouse coordinates)

| Part | Location |
|---|---|
| SCD_IRBoom | on the crane trolley's camera bracket. With SM_TankhouseCrane in its modelled pose: (13.860000000000001, -10.85, 10.005). Attach it to TC_Trolley |
| SCD_IRHead | at the boom's pivot (13.86, -10.85, 9.055); attach to SCD_IRBoom. Pan = rotate local Z, tilt = rotate the housing about local X (single object here; split if you need both axes) |
| SCD_CellSensor | one per cell at (cell x + 0.35, row y − 2.56, 0.45), no rotation: on the cell's end wall at the feed end, beside the feed box. The two leads end on the intercell bars on both sides of the cell (cell x ± 0.66) |
| SCD_RowDisplay, row A | (-2.6, -6.25, 0), rotation 0 (screen faces -X) |
| SCD_RowDisplay, row B | (-2.6, 0.05, 0), rotation 0 (screen faces -X) |
| SCD_RowDisplay, row C | (-2.6, 6.35, 0), rotation 0 (screen faces -X) |
| SCD_RowDisplay, row D | (-2.6, 12.65, 0), rotation 0 (screen faces -X) |
| SCD_Gaussmeter | prop, carried by an operator. Origin at the grip, probe down (local −Z) |

## Parts and pivots

| Object | Pivot (local) |
|---|---|
| SCD_CellSensor | (0.00, 0.00, 0.00) |
| SCD_Gaussmeter | (0.00, 0.00, 0.00) |
| SCD_IRBoom | (0.00, 0.00, 0.00) |
| SCD_IRHead | (0.00, 0.00, -0.95) |
| SCD_RowDisplay | (0.00, 0.00, 0.00) |

## Sources and status

| Item | Status |
|---|---|
| IR detection of shorts, published methods | Sourced (research companion §8 [S30][S31]) |
| Cell voltage and short monitors (ShortMeter, CellView) | Sourced (Mipac, research companion [S24]) |
| Handheld gaussmeters and IR cameras on the crane | Sourced (research file §8) |
| Shorts cost 1–3 % of current | Sourced (research companion [S6][S23]) |
| All shapes and sizes, the sensor and display positions | Own design / estimated. No brand styling or logos |
