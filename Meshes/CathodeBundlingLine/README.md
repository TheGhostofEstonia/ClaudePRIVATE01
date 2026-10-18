# SM_CathodeBundlingLine - cathode squaring, weighing, strapping and labelling

Turns each stack of stripped sheets into a shipping bundle. Stacks arrive on rollers from
SM_CathodeStrippingMachine, are squared, weighed, strapped lengthwise, turned 90°, strapped
crosswise, labelled by a robot and collected at the end for the forklift.

**Own design** for the layout and machine sizes. Sourced: bundle mass, steel strapping, labels
carrying product, bundle number and net weight.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Bundles move along +X.
- Footprint: x -0.2 to 21.9, y -2.5 to 2.9 (about 22.1 x 5.4 m).
- Infeed: roller top z = 0.45 m, roller length 1.3 m, at x = 0. Matches the stripping machine's stack
  conveyor (also z = 0.45); place this line so x = 0 meets its open end.
- Outfeed: forklift pickup at the end stop, x = 21.65, room for about three bundles.
- Bundle: 0.915 x 1.016 x 0.25 m, 30 sheets, about 2.0 t.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| BL_*_Roller_NN | Spin about Y | roller axes |
| BL_Squarer_L/R | Slide along Y toward the stack, 0.10 m | see table |
| BL_SquareStop | Pops up 0.25 m between the rollers (drawn up) | (4.62, 0, 0.45) |
| BL_Strap1/2_PressPlaten | Moves down onto the bundle while the strap is tensioned and sealed | see table |
| BL_Turntable | Rotates 90° about Z; its rollers and frame are parented to it | (10.2, 0, 0.25) |
| BL_LabelRobot_J1..J6 | Six-axis arm, links parented in order; J1 about Z, J2/J3/J5 about local Y, J4/J6 about local X | see table |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| BL_Dressing | (0.00, 0.00, 0.00) |
| BL_Guards | (0.00, 0.00, 0.00) |
| BL_Infeed_Frame | (0.00, 0.00, 0.00) |
| BL_Infeed_Roller_00 | (0.15, 0.00, 0.39) |
| BL_Infeed_Roller_01 | (0.46, 0.00, 0.39) |
| BL_Infeed_Roller_02 | (0.78, 0.00, 0.39) |
| BL_Infeed_Roller_03 | (1.09, 0.00, 0.39) |
| BL_Infeed_Roller_04 | (1.40, 0.00, 0.39) |
| BL_Infeed_Roller_05 | (1.72, 0.00, 0.39) |
| BL_Infeed_Roller_06 | (2.03, 0.00, 0.39) |
| BL_Infeed_Roller_07 | (2.34, 0.00, 0.39) |
| BL_Infeed_Roller_08 | (2.66, 0.00, 0.39) |
| BL_Infeed_Roller_09 | (2.97, 0.00, 0.39) |
| BL_Infeed_Roller_10 | (3.28, 0.00, 0.39) |
| BL_Infeed_Roller_11 | (3.60, 0.00, 0.39) |
| BL_Infeed_Roller_12 | (3.91, 0.00, 0.39) |
| BL_Infeed_Roller_13 | (4.22, 0.00, 0.39) |
| BL_Infeed_Roller_14 | (4.54, 0.00, 0.39) |
| BL_Infeed_Roller_15 | (4.85, 0.00, 0.39) |
| BL_LabelRobot_J0Pedestal | (14.50, -1.35, 0.00) |
| BL_LabelRobot_J1Base | (14.50, -1.35, 0.12) |
| BL_LabelRobot_J2Upper | (14.50, -1.17, 0.65) |
| BL_LabelRobot_J3Fore | (14.50, -1.17, 1.23) |
| BL_LabelRobot_J4Roll | (14.50, -0.85, 1.23) |
| BL_LabelRobot_J5Wrist | (14.50, -0.59, 1.23) |
| BL_LabelRobot_J6Flange | (14.50, -0.41, 1.23) |
| BL_LabelStation | (14.50, -1.35, 0.00) |
| BL_Label_Frame | (13.45, 0.00, 0.00) |
| BL_Label_Roller_00 | (13.60, 0.00, 0.39) |
| BL_Label_Roller_01 | (13.95, 0.00, 0.39) |
| BL_Label_Roller_02 | (14.30, 0.00, 0.39) |
| BL_Label_Roller_03 | (14.65, 0.00, 0.39) |
| BL_Label_Roller_04 | (15.00, 0.00, 0.39) |
| BL_Label_Roller_05 | (15.35, 0.00, 0.39) |
| BL_OutfeedStop | (21.50, 0.00, 0.00) |
| BL_Outfeed_Frame | (15.55, 0.00, 0.00) |
| BL_Outfeed_Roller_00 | (15.70, 0.00, 0.39) |
| BL_Outfeed_Roller_01 | (16.01, 0.00, 0.39) |
| BL_Outfeed_Roller_02 | (16.33, 0.00, 0.39) |
| BL_Outfeed_Roller_03 | (16.64, 0.00, 0.39) |
| BL_Outfeed_Roller_04 | (16.96, 0.00, 0.39) |
| BL_Outfeed_Roller_05 | (17.27, 0.00, 0.39) |
| BL_Outfeed_Roller_06 | (17.58, 0.00, 0.39) |
| BL_Outfeed_Roller_07 | (17.90, 0.00, 0.39) |
| BL_Outfeed_Roller_08 | (18.21, 0.00, 0.39) |
| BL_Outfeed_Roller_09 | (18.52, 0.00, 0.39) |
| BL_Outfeed_Roller_10 | (18.84, 0.00, 0.39) |
| BL_Outfeed_Roller_11 | (19.15, 0.00, 0.39) |
| BL_Outfeed_Roller_12 | (19.47, 0.00, 0.39) |
| BL_Outfeed_Roller_13 | (19.78, 0.00, 0.39) |
| BL_Outfeed_Roller_14 | (20.09, 0.00, 0.39) |
| BL_Outfeed_Roller_15 | (20.41, 0.00, 0.39) |
| BL_Outfeed_Roller_16 | (20.72, 0.00, 0.39) |
| BL_Outfeed_Roller_17 | (21.04, 0.00, 0.39) |
| BL_Outfeed_Roller_18 | (21.35, 0.00, 0.39) |
| BL_Prop_CathodeBundle | (20.80, 0.00, 0.45) |
| BL_ScaleBase | (6.00, 0.00, 0.00) |
| BL_SquareFrame | (4.00, 0.00, 0.00) |
| BL_SquareStop | (4.62, 0.00, 0.45) |
| BL_SquarerCyl_L_Barrel | (4.00, 1.00, 0.57) |
| BL_SquarerCyl_L_Rod | (4.00, 0.80, 0.57) |
| BL_SquarerCyl_R_Barrel | (4.00, -1.00, 0.57) |
| BL_SquarerCyl_R_Rod | (4.00, -0.80, 0.57) |
| BL_Squarer_L | (4.00, 0.62, 0.57) |
| BL_Squarer_R | (4.00, -0.62, 0.57) |
| BL_Strap1In_Frame | (7.05, 0.00, 0.00) |
| BL_Strap1In_Roller_00 | (7.18, 0.00, 0.39) |
| BL_Strap1In_Roller_01 | (7.43, 0.00, 0.39) |
| BL_Strap1In_Roller_02 | (7.70, 0.00, 0.39) |
| BL_Strap1In_Roller_03 | (7.95, 0.00, 0.39) |
| BL_Strap1Out_Frame | (8.32, 0.00, 0.00) |
| BL_Strap1Out_Roller_00 | (8.44, 0.00, 0.39) |
| BL_Strap1Out_Roller_01 | (8.81, 0.00, 0.39) |
| BL_Strap1Out_Roller_02 | (9.18, 0.00, 0.39) |
| BL_Strap1_Arch | (8.20, 0.00, 0.00) |
| BL_Strap1_PressCyl_Barrel | (8.20, 0.35, 1.75) |
| BL_Strap1_PressCyl_Rod | (8.20, 0.35, 0.80) |
| BL_Strap1_PressPlaten | (8.20, 0.00, 0.75) |
| BL_Strap2In_Frame | (11.10, 0.00, 0.00) |
| BL_Strap2In_Roller_00 | (11.23, 0.00, 0.39) |
| BL_Strap2In_Roller_01 | (11.59, 0.00, 0.39) |
| BL_Strap2In_Roller_02 | (11.95, 0.00, 0.39) |
| BL_Strap2Out_Frame | (12.32, 0.00, 0.00) |
| BL_Strap2Out_Roller_00 | (12.44, 0.00, 0.39) |
| BL_Strap2Out_Roller_01 | (12.72, 0.00, 0.39) |
| BL_Strap2Out_Roller_02 | (13.00, 0.00, 0.39) |
| BL_Strap2Out_Roller_03 | (13.27, 0.00, 0.39) |
| BL_Strap2_Arch | (12.20, 0.00, 0.00) |
| BL_Strap2_PressCyl_Barrel | (12.20, 0.35, 1.75) |
| BL_Strap2_PressCyl_Rod | (12.20, 0.35, 0.80) |
| BL_Strap2_PressPlaten | (12.20, 0.00, 0.75) |
| BL_Turntable | (10.20, 0.00, 0.25) |
| BL_TurntableBase | (10.20, 0.00, 0.00) |
| BL_Turntable_Frame | (9.50, 0.00, 0.25) |
| BL_Turntable_Roller_00 | (9.65, 0.00, 0.39) |
| BL_Turntable_Roller_01 | (10.02, 0.00, 0.39) |
| BL_Turntable_Roller_02 | (10.38, 0.00, 0.39) |
| BL_Turntable_Roller_03 | (10.75, 0.00, 0.39) |
| BL_Weigh_Frame | (5.05, 0.00, 0.00) |
| BL_Weigh_Roller_00 | (5.20, 0.00, 0.39) |
| BL_Weigh_Roller_01 | (5.53, 0.00, 0.39) |
| BL_Weigh_Roller_02 | (5.86, 0.00, 0.39) |
| BL_Weigh_Roller_03 | (6.19, 0.00, 0.39) |
| BL_Weigh_Roller_04 | (6.52, 0.00, 0.39) |
| BL_Weigh_Roller_05 | (6.85, 0.00, 0.39) |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute puts every part at the asset origin with its
pivot at the origin too, which is right for static parts. For the moving parts, import a second
time with it off (or use the pivots above) so each part rotates or slides about its own pivot.
Blender +Y becomes Unreal -Y with the default FBX axis settings, so check rotation signs.
Parented robot links keep their hierarchy only with Transform Vertex to Absolute off.

Chains: 1 UV unit = 0.5 m along the chain, so panner speed (U per second) = chain speed (m/s) / 0.5.
The chain mesh is a closed loop with continuous U, like the belt conveyors.

BL_Prop_CathodeBundle is a finished bundle (straps and label included) to use as a prop or a
physics actor. Its pivot is its base centre.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Bundle mass | about 2.0 t | Sourced: 1-4 t per bundle (Tata AIG cargo note), ~2,000 kg at one producer |
| Strapping | Steel straps, 2 each way | Steel strapping sourced; strap count and 32 x 4 mm strap estimated |
| Label | Product, bundle number, net weight | Sourced (producer); 200 x 120 mm label size estimated |
| Sheet | 1.016 x 0.915 m x 8 mm | Estimated, same as the stripping machine |
| Strapping arches 2.4 m wide x 2.1 m high, turntable Ø1.9 m, robot reach ~1.3 m | | Estimated |

Sources: research/copper-refinery/copper-refinery-equipment.md [S26] [S27].

## Files

- SM_CathodeBundlingLine.blend / .fbx (REF bundles, floor and figure not exported)
- Preview_Overview.png, Preview_Strapping.png, Preview_Label.png
