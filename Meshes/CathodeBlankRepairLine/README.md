# SM_CathodeBlankRepairLine - permanent cathode blank repair and straightening line

Workshop line for stainless cathode blanks that the stripping machine's vision system flags.
Blanks arrive in transport racks, are scanned for flatness, laid flat, straightened in a gantry
press, brush-polished, have their hanger-bar contacts ground clean and their edge strips
replaced, then stand back up and go into an outgoing rack.

**Own design.** The work list (polishing, contact cleaning, straightening, flattening, edge-strip
replacement, machine vision, special racks) is sourced from Metso's Boliden Pori case study. The
layout and every size are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Blanks move along +X.
- Footprint: x -0.3 to 29.3, y -2.4 to 2.9 (about 29.6 x 5.3 m); monorails reach 4.75 m high.
- Infeed: forklift sets BR_TransportRack_In at x = 1.2, hanger-bar seat z = 1.4 m,
  20 blanks at 100 mm pitch.
- Outfeed: BR_TransportRack_Out at x = 28.0, same rack. The racks are exported as their
  own parts, so they can also be used as props on a truck or in the tankhouse.
- Chains: hanger-bar seat z = 2.15 m. Flat work height (roller top) z = 0.905 m.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| BR_HoistIn/Out_Trolley | Travels along X on the monorail | see table |
| BR_HoistIn/Out_Gripper | Moves along Z (down to the rack seat, up to clear) and rides with the trolley | see table |
| BR_ChainIn/Out _L/R_Chain, sprockets | Chain loops along +X | see table |
| BR_TiltIn | Rotation Y 0° (upright, drawn) to +90° lays the blank flat toward +X | hinge (8.45, 0, 0.905) |
| BR_TiltUp | Drawn flat (rotation Y = +90°); rotate to 0° to stand the blank up onto the out-chain | hinge (21.6, 0, 0.905) |
| BR_PressGantry | Travels along X on its rails | (12.40, 0, 0.35) |
| BR_PressCarriage | Travels along Y on the gantry beam; parented to the gantry | see table |
| BR_PressRam | Moves down onto the blade; parented to the carriage | see table |
| BR_BrushRoll_Top/Bottom | Spin about Y (counter-rotating) | roll axes |
| BR_BrushRolls_Roller_NN and other _Roller_NN | Spin about Y | roller axes |
| BR_ContactGrinder_L/R | Spin about Z and move down 0.05 m onto the hanger-bar contact | see table |
| BR_EdgePress_L/R | Slide inward along Y to press new edge strips on | see table |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| BR_BrushHousing | (16.00, 0.00, 0.00) |
| BR_BrushMotors | (16.00, -1.20, 0.00) |
| BR_BrushRoll_Bottom | (16.35, 0.00, 0.75) |
| BR_BrushRoll_Top | (15.65, 0.00, 1.07) |
| BR_BrushRolls_Frame | (15.00, 0.00, 0.00) |
| BR_BrushRolls_Roller_00 | (15.25, 0.00, 0.84) |
| BR_BrushRolls_Roller_01 | (15.75, 0.00, 0.84) |
| BR_BrushRolls_Roller_02 | (16.25, 0.00, 0.84) |
| BR_BrushRolls_Roller_03 | (16.75, 0.00, 0.84) |
| BR_ChainIn_Frame | (3.40, 0.00, 0.00) |
| BR_ChainIn_L_Chain | (3.40, 0.62, 1.99) |
| BR_ChainIn_L_Sprocket_Head | (8.00, 0.62, 1.99) |
| BR_ChainIn_L_Sprocket_Tail | (3.40, 0.62, 1.99) |
| BR_ChainIn_R_Chain | (3.40, -0.62, 1.99) |
| BR_ChainIn_R_Sprocket_Head | (8.00, -0.62, 1.99) |
| BR_ChainIn_R_Sprocket_Tail | (3.40, -0.62, 1.99) |
| BR_ChainOut_Frame | (21.60, 0.00, 0.00) |
| BR_ChainOut_L_Chain | (21.60, 0.62, 1.99) |
| BR_ChainOut_L_Sprocket_Head | (26.20, 0.62, 1.99) |
| BR_ChainOut_L_Sprocket_Tail | (21.60, 0.62, 1.99) |
| BR_ChainOut_R_Chain | (21.60, -0.62, 1.99) |
| BR_ChainOut_R_Sprocket_Head | (26.20, -0.62, 1.99) |
| BR_ChainOut_R_Sprocket_Tail | (21.60, -0.62, 1.99) |
| BR_ContactGrinder_L | (18.00, 0.60, 0.95) |
| BR_ContactGrinder_R | (18.00, -0.60, 0.95) |
| BR_Dressing | (0.00, 0.00, 0.00) |
| BR_EdgePress_L | (20.00, 0.62, 0.93) |
| BR_EdgePress_R | (20.00, -0.62, 0.93) |
| BR_EdgeStation | (20.00, 0.00, 0.00) |
| BR_FlatnessScanner | (6.00, 0.00, 0.00) |
| BR_GrinderCyl_L_Barrel | (18.00, 0.60, 1.75) |
| BR_GrinderCyl_L_Rod | (18.00, 0.60, 1.25) |
| BR_GrinderCyl_R_Barrel | (18.00, -0.60, 1.75) |
| BR_GrinderCyl_R_Rod | (18.00, -0.60, 1.25) |
| BR_GrinderFrame | (18.00, 0.00, 0.00) |
| BR_Guards | (0.00, 0.00, 0.00) |
| BR_HoistIn_Gripper | (3.60, 0.00, 2.45) |
| BR_HoistIn_Monorail | (0.20, 0.00, 4.20) |
| BR_HoistIn_Trolley | (3.60, 0.00, 4.20) |
| BR_HoistOut_Gripper | (26.00, 0.00, 2.45) |
| BR_HoistOut_Monorail | (25.80, 0.00, 4.20) |
| BR_HoistOut_Trolley | (26.00, 0.00, 4.20) |
| BR_PressBed | (12.80, 0.00, 0.00) |
| BR_PressCarriage | (12.40, 0.20, 2.60) |
| BR_PressGantry | (12.40, 0.00, 0.35) |
| BR_PressRam | (12.40, 0.20, 1.15) |
| BR_TableEdge_Frame | (18.60, 0.00, 0.00) |
| BR_TableEdge_Roller_00 | (18.75, 0.00, 0.84) |
| BR_TableEdge_Roller_01 | (19.08, 0.00, 0.84) |
| BR_TableEdge_Roller_02 | (19.41, 0.00, 0.84) |
| BR_TableEdge_Roller_03 | (19.74, 0.00, 0.84) |
| BR_TableEdge_Roller_04 | (20.08, 0.00, 0.84) |
| BR_TableEdge_Roller_05 | (20.41, 0.00, 0.84) |
| BR_TableEdge_Roller_06 | (20.74, 0.00, 0.84) |
| BR_TableEdge_Roller_07 | (21.07, 0.00, 0.84) |
| BR_TableEdge_Roller_08 | (21.40, 0.00, 0.84) |
| BR_TableGrind_Frame | (17.00, 0.00, 0.00) |
| BR_TableGrind_Roller_00 | (17.15, 0.00, 0.84) |
| BR_TableGrind_Roller_01 | (17.48, 0.00, 0.84) |
| BR_TableGrind_Roller_02 | (17.80, 0.00, 0.84) |
| BR_TableGrind_Roller_03 | (18.12, 0.00, 0.84) |
| BR_TableGrind_Roller_04 | (18.45, 0.00, 0.84) |
| BR_TableIn_Frame | (8.50, 0.00, 0.00) |
| BR_TableIn_Roller_00 | (8.65, 0.00, 0.84) |
| BR_TableIn_Roller_01 | (8.96, 0.00, 0.84) |
| BR_TableIn_Roller_02 | (9.27, 0.00, 0.84) |
| BR_TableIn_Roller_03 | (9.58, 0.00, 0.84) |
| BR_TableIn_Roller_04 | (9.89, 0.00, 0.84) |
| BR_TableIn_Roller_05 | (10.21, 0.00, 0.84) |
| BR_TableIn_Roller_06 | (10.52, 0.00, 0.84) |
| BR_TableIn_Roller_07 | (10.83, 0.00, 0.84) |
| BR_TableIn_Roller_08 | (11.14, 0.00, 0.84) |
| BR_TableIn_Roller_09 | (11.45, 0.00, 0.84) |
| BR_TableMid_Frame | (14.00, 0.00, 0.00) |
| BR_TableMid_Roller_00 | (14.15, 0.00, 0.84) |
| BR_TableMid_Roller_01 | (14.50, 0.00, 0.84) |
| BR_TableMid_Roller_02 | (14.85, 0.00, 0.84) |
| BR_TableUp_Frame | (21.65, 0.00, 0.00) |
| BR_TableUp_Roller_00 | (21.80, 0.00, 0.84) |
| BR_TableUp_Roller_01 | (22.17, 0.00, 0.84) |
| BR_TableUp_Roller_02 | (22.53, 0.00, 0.84) |
| BR_TableUp_Roller_03 | (22.90, 0.00, 0.84) |
| BR_TiltIn | (8.45, 0.00, 0.90) |
| BR_TiltInBase | (8.45, 0.00, 0.00) |
| BR_TiltUp | (21.60, 0.00, 0.90) |
| BR_TiltUpBase | (21.60, 0.00, 0.00) |
| BR_TransportRack_In | (1.20, 0.00, 0.00) |
| BR_TransportRack_Out | (28.00, 0.00, 0.00) |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute puts every part at the asset origin with its
pivot at the origin too, which is right for static parts. For the moving parts, import a second
time with it off (or use the pivots above) so each part rotates or slides about its own pivot.
Blender +Y becomes Unreal -Y with the default FBX axis settings, so check rotation signs.
Parented robot links keep their hierarchy only with Transform Vertex to Absolute off.

Chains: 1 UV unit = 0.5 m along the chain, so panner speed (U per second) = chain speed (m/s) / 0.5.
The chain mesh is a closed loop with continuous U, like the belt conveyors.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Work list | polishing, contact cleaning, straightening, flattening, edge-strip replacement | Sourced (Metso, Boliden Pori) |
| Fleet | 28,000 plates; ~300/week sent for checks; plate life ≥10 years | Sourced (same) |
| Blade | 1.0 x 1.25 m x 3.25 mm | Thickness sourced, size estimated |
| Rack of 20, press gantry 2.8 m wide, brush rolls Ø0.32 m, work height 0.90 m | | Own design |

Source: Metso case study, "Maintained cathodes ensure refinery's cost-efficiency"
(https://www.metso.com/insights/case-studies/mining-and-metals/maintained-cathodes-ensure-refinerys-cost-efficiency/).

## Files

- SM_CathodeBlankRepairLine.blend / .fbx (REF blanks, floor and figure not exported)
- Preview_Overview.png, Preview_PressBrush.png, Preview_Racks.png
