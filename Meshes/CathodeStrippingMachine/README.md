# SM_CathodeStrippingMachine - stripping machine for permanent stainless cathodes

Takes a crane load of harvested IsaKidd-type cathodes, washes them, flexes each plate to crack the
deposit edge, wedges two knives in from the top, lays the two copper sheets flat, stacks them and
sends the stacks to the bundling line. Clean blanks go to the discharge chains for the crane.

**Own design.** The sequence (receive, wash, transfer, flex, chisel, stack, discharge, reject)
follows Glencore's IsaKidd semi-automatic machine. US20070144894A1, WO2017144740A1 and
EP0482258A1 show stripping machines, but none gives dimensions. All sizes here are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Plates move along +X.
- Footprint: x -0.5 to 25.0, y -5.3 to 3.6 (about 25.5 x 8.9 m).
- Infeed: crane drop zone on the receiving chains, x 0 to 7, hanger-bar seat z = 1.80 m,
  chains at y = +-0.62. The seat is higher than the anode machine (1.60 m) so the
  sheets can tip flat at z = 0.70 m above the stacking forks.
- Blank outfeed: crane pickup zone on the discharge chains, x 19.65 to 24.25,
  46 blanks at 100 mm pitch, seat z = 1.80 m.
- Copper outfeed: stack roller conveyor along +X at y = -2.30, roller top z = 0.45 m,
  open end at x = 24.5. Feeds SM_CathodeBundlingLine (its infeed is at the same height).
- Tankhouse link: the crane carries a cell load between this machine and the tankhouse transfer stand CathodeOut at (-12, 8) for harvested cathodes in, and CathodeBlankIn at (-22, 8) for blanks out (tankhouse coordinates, seat z 1.20, electrodes stacked along Y, so this machine's X runs along the tankhouse Y there). See Meshes/Tankhouse/README.md.
- Reject rack (hanger-bar rails, seat z = 1.80) on +Y at (17.9, 2.6).

## Stations and moving parts

| Station | x (m) | Moving parts |
|---|---|---|
| Receive chains | 0 to 7 | CS_Receive_L/R_Chain, sprockets |
| Wash | 7.4 to 11.4 | CS_Wash_L/R_Chain (hood is static) |
| Walking beam | 11.9 to 17.9 | CS_WalkingBeam: up 0.05 m, +X 2.0 m, down, back |
| Flex | 13.9 | CS_FlexClamp down 0.15 m onto the hanger bar; CS_FlexRoller_Up/Down slide 0.1 m along X against the blade, alternately |
| Strip | 15.9 | CS_StripKnife_Up/Down rotate about Y at their hinges (drawn closed at the deposit edge; open = about 25° outward); CS_SheetTilter_Up/Down rotate 90° outward about Y to lay the sheets flat |
| Stack | 15.9 ± 0.56 | CS_SheetPusher_Up/Down travel -Y 2.92 m; CS_StackForks_Up/Down lower 0.30 m in steps of one sheet and leave the stack on the rollers |
| Stack conveyor | 14.6 to 24.5 | CS_StackConv_Roller_NN spin about Y |
| Exit / reject | 17.9 | CS_RejectTongs lift, CS_RejectTrolley travels +2.6 m along Y |
| Discharge | 17.6 to 24.5 | CS_Discharge_L/R_Chain, sprockets |

Cylinders: _Barrel pivot at the base end, _Rod pivot at the rod end, local +X along the axis.

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CS_Discharge_Frame | (17.60, 0.00, 0.00) |
| CS_Discharge_L_Chain | (17.60, 0.62, 1.64) |
| CS_Discharge_L_Sprocket_Head | (24.50, 0.62, 1.64) |
| CS_Discharge_L_Sprocket_Tail | (17.60, 0.62, 1.64) |
| CS_Discharge_R_Chain | (17.60, -0.62, 1.64) |
| CS_Discharge_R_Sprocket_Head | (24.50, -0.62, 1.64) |
| CS_Discharge_R_Sprocket_Tail | (17.60, -0.62, 1.64) |
| CS_Dressing | (0.00, 0.00, 0.00) |
| CS_FlexClamp | (13.90, 0.00, 2.05) |
| CS_FlexClampCyl_Barrel | (13.90, 0.00, 2.70) |
| CS_FlexClampCyl_Rod | (13.90, 0.00, 1.94) |
| CS_FlexCyl_Down_Barrel | (14.52, 0.00, 1.20) |
| CS_FlexCyl_Down_Rod | (14.17, 0.00, 1.20) |
| CS_FlexCyl_Up_Barrel | (13.28, 0.00, 1.20) |
| CS_FlexCyl_Up_Rod | (13.63, 0.00, 1.20) |
| CS_FlexFrame | (13.90, 0.00, 0.00) |
| CS_FlexRoller_Down | (14.02, 0.00, 1.20) |
| CS_FlexRoller_Up | (13.78, 0.00, 1.20) |
| CS_Guards | (0.00, 0.00, 0.00) |
| CS_KnifeCyl_Down_Barrel | (17.00, 0.70, 2.85) |
| CS_KnifeCyl_Down_Rod | (16.32, 0.42, 2.05) |
| CS_KnifeCyl_Up_Barrel | (14.80, 0.70, 2.85) |
| CS_KnifeCyl_Up_Rod | (15.48, 0.42, 2.05) |
| CS_PickupGuides | (19.65, 0.00, 0.00) |
| CS_Receive_Frame | (0.00, 0.00, 0.00) |
| CS_Receive_L_Chain | (0.00, 0.62, 1.64) |
| CS_Receive_L_Sprocket_Head | (7.00, 0.62, 1.64) |
| CS_Receive_L_Sprocket_Tail | (0.00, 0.62, 1.64) |
| CS_Receive_R_Chain | (0.00, -0.62, 1.64) |
| CS_Receive_R_Sprocket_Head | (7.00, -0.62, 1.64) |
| CS_Receive_R_Sprocket_Tail | (0.00, -0.62, 1.64) |
| CS_RejectRack | (17.90, 2.60, 0.00) |
| CS_RejectTongs | (17.90, 0.00, 2.50) |
| CS_RejectTrolley | (17.90, 0.00, 3.20) |
| CS_SheetPusher_Down | (16.46, 0.62, 0.78) |
| CS_SheetPusher_Up | (15.34, 0.62, 0.78) |
| CS_SheetTilter_Down | (15.96, 0.00, 0.70) |
| CS_SheetTilter_Up | (15.84, 0.00, 0.70) |
| CS_StackConv_Frame | (14.60, -2.30, 0.00) |
| CS_StackConv_Roller_00 | (14.75, -2.30, 0.39) |
| CS_StackConv_Roller_01 | (15.05, -2.30, 0.39) |
| CS_StackConv_Roller_02 | (15.35, -2.30, 0.39) |
| CS_StackConv_Roller_03 | (15.65, -2.30, 0.39) |
| CS_StackConv_Roller_04 | (15.95, -2.30, 0.39) |
| CS_StackConv_Roller_05 | (16.25, -2.30, 0.39) |
| CS_StackConv_Roller_06 | (16.55, -2.30, 0.39) |
| CS_StackConv_Roller_07 | (16.85, -2.30, 0.39) |
| CS_StackConv_Roller_08 | (17.15, -2.30, 0.39) |
| CS_StackConv_Roller_09 | (17.45, -2.30, 0.39) |
| CS_StackConv_Roller_10 | (17.75, -2.30, 0.39) |
| CS_StackConv_Roller_11 | (18.05, -2.30, 0.39) |
| CS_StackConv_Roller_12 | (18.35, -2.30, 0.39) |
| CS_StackConv_Roller_13 | (18.65, -2.30, 0.39) |
| CS_StackConv_Roller_14 | (18.95, -2.30, 0.39) |
| CS_StackConv_Roller_15 | (19.25, -2.30, 0.39) |
| CS_StackConv_Roller_16 | (19.55, -2.30, 0.39) |
| CS_StackConv_Roller_17 | (19.85, -2.30, 0.39) |
| CS_StackConv_Roller_18 | (20.15, -2.30, 0.39) |
| CS_StackConv_Roller_19 | (20.45, -2.30, 0.39) |
| CS_StackConv_Roller_20 | (20.75, -2.30, 0.39) |
| CS_StackConv_Roller_21 | (21.05, -2.30, 0.39) |
| CS_StackConv_Roller_22 | (21.35, -2.30, 0.39) |
| CS_StackConv_Roller_23 | (21.65, -2.30, 0.39) |
| CS_StackConv_Roller_24 | (21.95, -2.30, 0.39) |
| CS_StackConv_Roller_25 | (22.25, -2.30, 0.39) |
| CS_StackConv_Roller_26 | (22.55, -2.30, 0.39) |
| CS_StackConv_Roller_27 | (22.85, -2.30, 0.39) |
| CS_StackConv_Roller_28 | (23.15, -2.30, 0.39) |
| CS_StackConv_Roller_29 | (23.45, -2.30, 0.39) |
| CS_StackConv_Roller_30 | (23.75, -2.30, 0.39) |
| CS_StackConv_Roller_31 | (24.05, -2.30, 0.39) |
| CS_StackConv_Roller_32 | (24.35, -2.30, 0.39) |
| CS_StackForks_Down | (16.46, -3.00, 0.70) |
| CS_StackForks_Up | (15.34, -3.00, 0.70) |
| CS_StackerFrame | (15.90, -2.30, 0.00) |
| CS_StationFrame | (11.40, 0.00, 0.00) |
| CS_StripFrame | (15.90, 0.00, 0.00) |
| CS_StripKnife_Down | (16.65, 0.00, 2.75) |
| CS_StripKnife_Up | (15.15, 0.00, 2.75) |
| CS_TilterCyl_Down_Barrel | (16.56, 0.55, 0.15) |
| CS_TilterCyl_Down_Rod | (15.98, 0.55, 1.05) |
| CS_TilterCyl_Up_Barrel | (15.24, 0.55, 0.15) |
| CS_TilterCyl_Up_Rod | (15.82, 0.55, 1.05) |
| CS_WalkingBeam | (11.50, 0.00, 0.20) |
| CS_WalkingBeam_TravelCyl_Barrel | (9.40, 0.00, 0.12) |
| CS_WalkingBeam_TravelCyl_Rod | (11.42, 0.00, 0.12) |
| CS_WashHood | (7.60, 0.00, 0.00) |
| CS_Wash_Frame | (7.40, 0.00, 0.00) |
| CS_Wash_L_Chain | (7.40, 0.62, 1.64) |
| CS_Wash_L_Sprocket_Head | (11.40, 0.62, 1.64) |
| CS_Wash_L_Sprocket_Tail | (7.40, 0.62, 1.64) |
| CS_Wash_R_Chain | (7.40, -0.62, 1.64) |
| CS_Wash_R_Sprocket_Head | (11.40, -0.62, 1.64) |
| CS_Wash_R_Sprocket_Tail | (7.40, -0.62, 1.64) |

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
| Blade | 1.04 x 1.05 m below the bar, 3.25 mm 316L | Thickness sourced (patents); size matches SM_PermanentCathode (tankhouse thread) |
| Hanger bar | 1.32 m, 25 x 35 mm, copper plated | Construction sourced (patents), size matches SM_PermanentCathode |
| Copper sheet | 1.016 x 0.915 m x 8 mm, ~67 kg, top edge 0.13 m below the bar | Matches SM_PermanentCathode (estimated there) |
| Throughput | ~250 plates/h (early machines); ~500/h needs two strip stations; >600/h reported | Sourced: Wikipedia IsaKidd, Glencore patent background, CIM paper |
| Cell load | 46 cathodes | Estimated (anodes + 1, sourced rule) |
| Stack of 30 sheets, ~2.0 t | One stack = one bundle | Sourced bundle mass 1-4 t, ~2,000 kg at one producer; sheet count estimated |
| Walking-beam step 2.0 m, seat height 1.8 m | | Own design |

Sources: Glencore IsaKidd electrode handling equipment
(https://www.glencoretechnology.com/en/technologies/isakidd/electrode-handling-equipment);
US20070144894A1, WO2017144740A1, EP0482258A1, US7306706B2 (patents.google.com).

## Files

- SM_CathodeStrippingMachine.blend / .fbx (REF cathodes, sheets, floor and figure not exported)
- Preview_Overview.png, Preview_Strip.png, Preview_Wash.png
