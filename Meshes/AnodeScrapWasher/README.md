# SM_AnodeScrapWasher - anode scrap washing and stacking machine

Spent anodes come out of the cells on the tankhouse crane with slimes on them. The line washes
them, tips them flat and builds stacks for the forklift, which takes them back to the anode furnace.
Wash water carries the slimes to a cone-bottom settling tank; its underflow is pumped toward the
anode slimes plant.

**Own design.** The research only gives "spray wash line and stacker" and the scrap fraction
(80-87 % of each anode is consumed, so 13-20 % comes back). No drawings were found.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Anodes move along +X.
- Footprint: x -0.5 to 21.9, y -4.4 to 3.6 (about 22.4 x 8.0 m).
- Infeed: crane drop zone on the receiving chains, x 0 to 6, lug seat z = 1.60 m, chains at y = +-0.56.
  Same seat height and lug span as SM_AnodePrepMachine.
- Outfeed: stacks of 20 flat scrap anodes on the roller conveyor, roller top z = 0.45 m,
  forklift pickup at the end stop x = 21.7. Stack width 1.24 m across the lugs.
- Slimes pipe stub to the slimes plant at (11.1, -4.7, 3.6), pointing -Y.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| SW_Receive / SW_Wash _L/R_Chain, sprockets | Chain loops along +X, sprockets spin about Y | see table |
| SW_WalkingBeam | Up 0.05 m, +X 1.5 m, down, back | (11.50, 0, 0.30) |
| SW_Tilter | Rotates about Y; Blender rotation Y = +90° lays the anode flat with the lugs toward +X and the back bars underneath | hinge (13.43, 0.0, 0.85) |
| SW_StackForks | Lifts the flat anode off the tilter, then lowers one anode thickness per anode; at the bottom the stack sits on the rollers | (13.91, -1.15, 0.82) |
| SW_StackConv_Roller_NN | Spin about Y | roller axes |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SW_Dressing | (0.00, 0.00, 0.00) |
| SW_Guards | (0.00, 0.00, 0.00) |
| SW_Receive_Frame | (0.00, 0.00, 0.00) |
| SW_Receive_L_Chain | (0.00, 0.56, 1.44) |
| SW_Receive_L_Sprocket_Head | (6.00, 0.56, 1.44) |
| SW_Receive_L_Sprocket_Tail | (0.00, 0.56, 1.44) |
| SW_Receive_R_Chain | (0.00, -0.56, 1.44) |
| SW_Receive_R_Sprocket_Head | (6.00, -0.56, 1.44) |
| SW_Receive_R_Sprocket_Tail | (0.00, -0.56, 1.44) |
| SW_SlimesTank | (8.90, -3.20, 0.00) |
| SW_StackConv_Frame | (13.13, 0.00, 0.00) |
| SW_StackConv_Roller_00 | (13.28, 0.00, 0.39) |
| SW_StackConv_Roller_01 | (13.59, 0.00, 0.39) |
| SW_StackConv_Roller_02 | (13.90, 0.00, 0.39) |
| SW_StackConv_Roller_03 | (14.21, 0.00, 0.39) |
| SW_StackConv_Roller_04 | (14.52, 0.00, 0.39) |
| SW_StackConv_Roller_05 | (14.83, 0.00, 0.39) |
| SW_StackConv_Roller_06 | (15.14, 0.00, 0.39) |
| SW_StackConv_Roller_07 | (15.45, 0.00, 0.39) |
| SW_StackConv_Roller_08 | (15.76, 0.00, 0.39) |
| SW_StackConv_Roller_09 | (16.07, 0.00, 0.39) |
| SW_StackConv_Roller_10 | (16.38, 0.00, 0.39) |
| SW_StackConv_Roller_11 | (16.69, 0.00, 0.39) |
| SW_StackConv_Roller_12 | (17.00, 0.00, 0.39) |
| SW_StackConv_Roller_13 | (17.32, 0.00, 0.39) |
| SW_StackConv_Roller_14 | (17.63, 0.00, 0.39) |
| SW_StackConv_Roller_15 | (17.94, 0.00, 0.39) |
| SW_StackConv_Roller_16 | (18.25, 0.00, 0.39) |
| SW_StackConv_Roller_17 | (18.56, 0.00, 0.39) |
| SW_StackConv_Roller_18 | (18.87, 0.00, 0.39) |
| SW_StackConv_Roller_19 | (19.18, 0.00, 0.39) |
| SW_StackConv_Roller_20 | (19.49, 0.00, 0.39) |
| SW_StackConv_Roller_21 | (19.80, 0.00, 0.39) |
| SW_StackConv_Roller_22 | (20.11, 0.00, 0.39) |
| SW_StackConv_Roller_23 | (20.42, 0.00, 0.39) |
| SW_StackConv_Roller_24 | (20.73, 0.00, 0.39) |
| SW_StackConv_Roller_25 | (21.04, 0.00, 0.39) |
| SW_StackConv_Roller_26 | (21.35, 0.00, 0.39) |
| SW_StackForks | (13.91, -1.15, 0.82) |
| SW_StackerFrame | (13.91, -1.40, 0.00) |
| SW_StationFrame | (11.40, 0.00, 0.00) |
| SW_Tilter | (13.43, 0.00, 0.85) |
| SW_TilterFrame | (13.43, 0.00, 0.00) |
| SW_WalkingBeam | (11.50, 0.00, 0.30) |
| SW_WalkingBeam_TravelCyl_Barrel | (9.90, 0.00, 0.12) |
| SW_WalkingBeam_TravelCyl_Rod | (11.42, 0.00, 0.12) |
| SW_WashHood | (6.60, 0.00, 0.00) |
| SW_Wash_Frame | (6.40, 0.00, 0.00) |
| SW_Wash_L_Chain | (6.40, 0.56, 1.44) |
| SW_Wash_L_Sprocket_Head | (11.40, 0.56, 1.44) |
| SW_Wash_L_Sprocket_Tail | (6.40, 0.56, 1.44) |
| SW_Wash_R_Chain | (6.40, -0.56, 1.44) |
| SW_Wash_R_Sprocket_Head | (11.40, -0.56, 1.44) |
| SW_Wash_R_Sprocket_Tail | (6.40, -0.56, 1.44) |

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
| Scrap fraction | 13-20 % of the anode | Sourced (80-87 % consumed, BCcampus Aqueous Pathways) |
| Scrap anode proxy | 0.96 x 0.80 x 0.012 m body, full lugs (~80 kg) | Estimated |
| Cell load | 45 anodes | Inside the sourced 30-50 range |
| Stack of 20, wash hood 4.6 m, settling tank Ø2.2 m | | Own design |

## Files

- SM_AnodeScrapWasher.blend / .fbx (REF scrap anodes, floor and figure not exported)
- Preview_Overview.png, Preview_Tilter.png
