# SM_Workshops

Plant maintenance workshop: crane-served high bay (machine shop + welding/fabrication) with a
lean-to holding the electrical shop, instrument shop and tool store. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/WorkshopsSafetyLab/build_workshops.py`; re-run it to rebuild.

The layout is my own design. I found no public drawings of a smelter maintenance workshop, so the
building, room sizes and machine placement are estimates. Machine sizes are taken from real
machine classes where noted below.

## Placement and footprint

- Origin: finished floor level (z = 0) at the centre of the high bay. +X east, +Y north.
- Footprint: x -24 … +24 m, y -9 … +17 m (48 × 26 m). Slab extends 0.3 m beyond the walls.
- High bay: 48 × 18 m (y -9 … +9), eaves 9.0 m, ridge 9.95 m, 6° roof.
- Lean-to: 48 × 8 m (y +9 … +17), roof falls from 5.8 m to 5.0 m.
- Rooms: machine shop x -24 … 6, welding/fabrication x 6 … 24 (both in the high bay, no wall
  between them; the three welding booths are screened). Lean-to: electrical shop x -24 … -6,
  instrument shop x -6 … 8, tool store x 8 … 24.
- Central aisle y -2.6 … +2.6 is kept clear, marked by yellow floor lines, from the west door to
  the east door.

### Doors

| Door | Centre (x, y) | Size W × H | Part |
|---|---|---|---|
| East roller shutter (main vehicle door) | (24.0, 0.0) | 6.0 × 6.0 | WS_Shutter_East |
| West roller shutter | (-24.0, 0.0) | 5.0 × 5.0 | WS_Shutter_West |
| South roller shutter, machine shop | (-3.0, -9.0) | 5.0 × 5.0 | WS_Shutter_South |
| Electrical shop, from high bay | (-15.0, 9.0) | 3.0 × 3.5 | WS_Shutter_ElecInner |
| Electrical shop, outside (drive-through for motors) | (-15.0, 17.0) | 3.0 × 3.5 | WS_Shutter_ElecOuter |
| Tool store serving hatch (sill 0.95 m) | (10.0, 9.0) | 2.0 × 1.3 | WS_Shutter_StoreHatch |
| Personnel door, machine shop south | (-15.0, -9.0) | 1.0 × 2.1 | WS_Door_South_Machine |
| Personnel door, welding bay south | (20.0, -9.0) | 1.0 × 2.1 | WS_Door_South_Weld |
| Instrument shop, from high bay | (-2.0, 9.0) | 1.0 × 2.1 | WS_Door_Instrument_Inner |
| Tool store, from high bay | (13.0, 9.0) | 1.0 × 2.1 | WS_Door_Store_Inner |
| Electrical shop, outside | (-9.0, 17.0) | 1.0 × 2.1 | WS_Door_Elec_Outer |
| Instrument shop, outside | (0.0, 17.0) | 1.0 × 2.1 | WS_Door_Instrument_Outer |
| Tool store, outside | (20.0, 17.0) | 1.0 × 2.1 | WS_Door_Store_Outer |

## Moving parts

| Part | Motion |
|---|---|
| WS_Shutter_* | Pivot at the top of the curtain under the coil box. Roll up = scale local Z from 1 to about 0.05. |
| WS_Door_* | Pivot on the hinge edge at floor level, leaf along local +X. Open = rotate about local Z, ±90° (pick the sign for the swing side you want). |
| WS_Crane_Bridge | Travels along X on the rails at z = 7.0 (y = ±8.4). Limits about x = -22 … +22. |
| WS_Crane_Trolley | Attach to the bridge. Travels along Y, about ±7 m. |
| WS_Crane_Hook | Attach to the trolley. Moves along Z (hook built at z = 4.0; floor clearance down to about 0.6 m). |
| WS_Crane_Ropes | Attach to the trolley. Pivot at the drum; scale local Z = (pivot z - hook block top z) / 3.76 to keep the ropes reaching the hook. |
| WS_Lathe1/2_Chuck | Spins about local X (spindle axis). |
| WS_Lathe1/2_Carriage, _Tailstock | Slide along local X (bed axis). |
| WS_Mill_Table | Slides along local X, about ±0.35 m. |
| WS_RadialDrill_Arm | Swings about local Z at the column axis (about ±150°), rises along Z up to about +0.4 m. |
| WS_Bandsaw_Bow | Hinge along local X at the rear; raise = rotate about local X by up to about -40°. |
| WS_Press_Ram | Slides along local Z, down to about -0.4 m. |
| WS_FumeArm_1/2/3 | Swing about Z at the wall bracket (about ±80°). |
| WS_Plasma_Gantry | Slides along local X, about -2.0 … +4.5 m from its built position. |
| WS_Oven_Door | Hinge on the left edge, rotate about local Z by up to -100°. |

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| WS_Bandsaw_Base | (-5.50, 4.50, 0.00) |
| WS_Bandsaw_Bow | (-5.50, 4.78, 0.85) |
| WS_Crane_Bridge | (-10.00, 0.00, 7.00) |
| WS_Crane_Hook | (-10.00, -0.20, 4.45) |
| WS_Crane_Ropes | (-10.00, -0.20, 8.21) |
| WS_Crane_Trolley | (-10.00, 0.00, 8.21) |
| WS_DoorFrames | (0.00, 0.00, 0.00) |
| WS_Door_Elec_Outer | (-9.50, 17.00, 0.00) |
| WS_Door_Instrument_Inner | (-2.50, 9.00, 0.00) |
| WS_Door_Instrument_Outer | (-0.50, 17.00, 0.00) |
| WS_Door_South_Machine | (-15.50, -9.00, 0.00) |
| WS_Door_South_Weld | (19.50, -9.00, 0.00) |
| WS_Door_Store_Inner | (12.50, 9.00, 0.00) |
| WS_Door_Store_Outer | (19.50, 17.00, 0.00) |
| WS_Electrical_Static | (0.00, 0.00, 0.00) |
| WS_Floor | (0.00, 0.00, 0.00) |
| WS_FumeArm_1 | (7.40, -8.70, 2.60) |
| WS_FumeArm_2 | (11.40, -8.70, 2.60) |
| WS_FumeArm_3 | (15.40, -8.70, 2.60) |
| WS_Instrument_Static | (0.00, 0.00, 0.00) |
| WS_Lathe1_Bed | (-12.50, -6.00, 0.00) |
| WS_Lathe1_Carriage | (-13.20, -6.00, 0.95) |
| WS_Lathe1_Chuck | (-16.13, -6.00, 1.50) |
| WS_Lathe1_Tailstock | (-8.20, -6.00, 0.95) |
| WS_Lathe2_Bed | (-21.00, -6.00, 0.00) |
| WS_Lathe2_Carriage | (-20.88, -6.00, 0.85) |
| WS_Lathe2_Chuck | (-21.80, -6.00, 1.23) |
| WS_Lathe2_Tailstock | (-19.64, -6.00, 0.85) |
| WS_MachineShop_Furniture | (0.00, 0.00, 0.00) |
| WS_Mill_Body | (-19.00, 4.50, 0.00) |
| WS_Mill_Table | (-19.00, 4.38, 0.95) |
| WS_Oven_Body | (-22.40, 15.40, 0.00) |
| WS_Oven_Door | (-23.35, 14.45, 0.05) |
| WS_PedestalDrill | (-9.00, 4.50, 0.00) |
| WS_Plasma_Gantry | (11.00, 4.50, 0.90) |
| WS_Plasma_Table | (12.00, 4.50, 0.00) |
| WS_Press_Frame | (-1.00, 4.50, 0.00) |
| WS_Press_Ram | (-1.00, 4.50, 1.80) |
| WS_RadialDrill_Arm | (-14.50, 4.50, 2.00) |
| WS_RadialDrill_Base | (-13.50, 4.50, 0.00) |
| WS_Roof | (0.00, 0.00, 0.00) |
| WS_Shutter_East | (24.17, -0.00, 6.00) |
| WS_Shutter_ElecInner | (-15.00, 8.83, 3.50) |
| WS_Shutter_ElecOuter | (-15.00, 17.17, 3.50) |
| WS_Shutter_South | (-3.00, -9.17, 5.00) |
| WS_Shutter_StoreHatch | (10.00, 8.83, 2.25) |
| WS_Shutter_West | (-24.17, -0.00, 5.00) |
| WS_Structure | (0.00, 0.00, 0.00) |
| WS_ToolStore_Static | (0.00, 0.00, 0.00) |
| WS_Walls | (0.00, 0.00, 0.00) |
| WS_WeldBay_Static | (0.00, 0.00, 0.00) |

## Unreal import

Combine Meshes off. With Transform Vertex to Absolute on, every part keeps the building origin as
its pivot, which suits the static parts. For the moving parts, import with it off and place each
part at the pivot above. The Blender Y axis appears as -Y in Unreal with the default FBX settings,
so check rotation signs after import. WS_Roof is a separate part so it can be hidden for interior
views; it has no underside lining.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Large lathe (WS_Lathe1), 1000 mm swing × 6 m between centres class | 9.5 × 1.9 × 1.8 m | Estimated (scaled up from the 660 × 2000 class) |
| Medium lathe (WS_Lathe2), 660 mm swing × 2000 mm between centres | 3.63 × 1.20 × 1.52 m | Sourced: Bernardo Titan 660 × 2000 and Cormak 660 × 2000 listings (3630 × 1200 × 1520-1700 mm, 2.9-3.8 t) |
| Turret milling machine | ~1.5 × 1.7 × 2.2 m | Estimated |
| Radial arm drill (1.6 m arm) | base 2.6 × 1.1 m, 3.2 m tall | Estimated |
| Horizontal bandsaw, pedestal drill, bench grinder | | Estimated |
| 100 t H-frame press | 1.7 × 1.0 × 2.6 m | Estimated |
| 10 t double-girder crane, 16.8 m span, rail at 7.0 m | | Estimated |
| Welding booths | 4 × 3.7 m, 2.0 m screens, curtain on the aisle side | Own design |
| CNC plasma table | 6.5 × 2.5 m water table | Estimated (common 6 × 2 m cutting area) |
| Benches 0.9 m high, shelving, cabinets, gas cylinders Ø0.23 × 1.5 m | | Estimated |
| Building, room sizes, door positions | | Own design |

Sources: Bernardo Titan 660 × 2000 (https://www.machineseeker.com/bernardo-titan+660+-+2000/i-19924365),
Cormak 660 × 2000 (https://www.cormak.pl/gb/product/1429-660x2000-industrial-lathe.html).

## Files

- SM_Workshops.blend / .fbx (the REF collection is not exported)
- Preview_Exterior.png, Preview_Cutaway.png, Preview_MachineShop.png, Preview_WeldBay.png,
  Preview_LeanTo.png (all but the exterior are rendered with WS_Roof hidden)
