# SM_TankhouseCrane

Electrode handling crane for the electrorefining tankhouse (SM_TankhouseBuilding).
- **Bridge:** double box girder, 28.8 m span, on rails along X at y = ±14.4
  (rail top z 8.0). Travels the whole hall, x -28.0 to 60.0, from the
  service bay transfer stands to the far end of the cell rows.
- **Trolley:** runs along Y on the girders. One hoist drum with four rope falls carries the bale.
- **Bale:** a 4.9 m frame that lines up with one cell. It carries two hook sets that can work
  separately, so the crane can lift a full anode load, a full cathode load, or both:
  - anode hooks: 2 × 45 hooks at x ±0.53 whose toes slide under the anode lugs (between the anode
    body edge and the capping board);
  - cathode hooks: 2 × 46 hooks at x ±0.30 whose toes slide under the hanger bar where it
    overhangs the blade (11 mm each side).
- **Short-circuit camera:** a bracket under the trolley frame takes the IR camera boom of
  SM_ShortCircuitDetection.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates. Files: `SM_TankhouseCrane.blend`, `SM_TankhouseCrane.fbx`
(FBX_SCALE_NONE, 8 objects). Previews: `Preview_Overview.png`, `Preview_Bale.png` (bale lowered
onto a loaded cell, hooks engaged).

## Origin and placement

- Tankhouse coordinates: the FBX lines up with SM_TankhouseBuilding with no offset.
- Modelled pose: bridge over cell 10 (x 13.86), trolley over row A (y -9.45), bale at
  travel height (hook seat z 2.45), hooks open.

## Parts, pivots and motion

| Object | Motion | Range |
|---|---|---|
| TC_Bridge | translate X | x -28.0 to 60.0 (pivot x) |
| TC_Trolley | child of the bridge, translate Y | y -12.0 to 12.0 |
| TC_HoistDrum | child of the trolley, rotate about local X. Drum Ø0.9 m, 4-fall reeving on 2 drum grooves: drum turn (rad) = 2 × lift (m) / 0.45 | |
| TC_Ropes | child of the trolley, scale local Z = (rope top z 10.30 − head z) / 6.75, where head z = bale pivot z + 1.1 | |
| TC_Bale | child of the trolley, translate Z (pivot = hook seat level) | seat in cell 0.85, transfer stands 1.2, travel 2.45 (max 8.6) |
| TC_AnodeHooks | child of the bale, translate Y: 0 = open, -0.008 = toes under the lugs | |
| TC_CathodeHooks | child of the bale, translate Y: 0 = open, +0.006 = toes under the hanger bar | |

Exact pivots (tankhouse coordinates):

| Object | Pivot |
|---|---|
| TC_AnodeHooks | (13.86, -9.45, 2.45) |
| TC_Bale | (13.86, -9.45, 2.45) |
| TC_Bridge | (13.86, 0.00, 8.00) |
| TC_CathodeHooks | (13.86, -9.45, 2.45) |
| TC_HoistDrum | (13.86, -9.45, 10.90) |
| TC_Ropes | (13.86, -9.45, 10.30) |
| TC_Trolley | (13.86, -9.45, 10.05) |

**Positioning over a cell.** For cell i in a row: bridge pivot x = 0.66 + 1.32·i, trolley pivot
y = row y. The hooks are laid out for the even-cell electrode pattern, so for an odd cell move the
trolley a further -0.05 m in Y.

**Pick sequence (anodes).** Lower the bale from travel height to z 0.85 with the hooks open
(the toes pass down beside the lugs), move TC_AnodeHooks -0.008 m, then lift. The toes
reach 7.5 mm under each lug. The cathode hooks do the same under the hanger bars with +0.006 m
(toes 6 mm under the bar). `check_tankhouse.py` tests both hook sets: clear while lowering and
engaging, and every electrode caught after a 15 mm lift.
At travel height a carried anode's bottom is 0.72 m above the seat line, clear of
the electrodes in the other cells.

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off. Attach the trolley to the bridge, the
drum, ropes and bale to the trolley, and the hook sets to the bale. Attach lifted electrodes to the
bale while carried.

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Semi-automatic crane with a multi-hook bale that lifts anodes and cathodes; double lifting bale | | Sourced (research file §8, US4392934, Glencore Technology) |
| Separate anode crane 10 t and cathode crane 3.5 t at Kyshtym | | Sourced (Kuenz press release, AJOT). This crane combines both duties |
| Safe working load about 20 t (45 anodes × 0.38 t = 17.1 t plus the hooks) | | Estimated |
| Span 28.8 m, rail z 8.0, girder depth 1.4 m, trolley gauge 3.2 m | | Estimated to suit the building |
| Hook shapes, hook positions, end guide frames | | Own design. The toes are small (6–8 mm) because the gaps between anodes and cathodes are only 15–26 mm |
| Cathode hooks under the hanger bar instead of through the blade windows | | Own simplification. Real IsaKidd plates are lifted by their windows; with a 25 mm hanger bar a fixed window hook could not pass the bar inside the 15 mm gap, so it would need pivoting fingers |
| No operator cab: remote/automatic operation with a walkway and panel house for maintenance | | Sourced: Kuenz remote operating stations; layout estimated |

Sources: /mnt/project-files/copper_refinery_equipment.md §8 (US4392934); research companion §8
(double-lifting bale, automatic operation, [S2]/[S3]); https://www.ajot.com/news/kuenz-automated-anode-and-cathode-handling-cranes-with-remote-operating-stations-ros-for-kyshtym-russia
