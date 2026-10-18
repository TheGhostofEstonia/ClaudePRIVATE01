# SM_AnodePrepMachine - anode preparation machine

Takes cast anodes from the stacking area, weighs them, flattens them, straightens and mills the
lug undersides, rejects bad ones and sets the rest at cell pitch for the tankhouse crane.

**Own design.** The station sequence follows US4903519 (straightening press), US5799529 (lug
straightening and machining) and US8227345 (high-capacity anode preparation). I found no drawings
with dimensions, so the layout and every machine size here are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Anodes move along +X.
- Footprint: x -0.5 to 28.9, y -4.7 to 3.6 (about 29.4 x 8.3 m including pulpit and HPU).
- Infeed: forklift sets a load of anodes (face to face) on the infeed chains, x 0 to 7, lug seat at
  z = 1.60 m. Chains at y = +-0.56.
- Outfeed: crane pickup zone on the spacing chain, x 23.75 to 28.20,
  45 anodes at 100 mm pitch, lug seat z = 1.60 m. End stop at x = 28.85.
- Reject rack (lug rails, seat z = 1.60) on the -Y side, centred at (15.0, -2.6).
- Lug span 1.24 m; the crane bale (tankhouse thread) must match.

## Stations

| Station | x (m) | Moving parts |
|---|---|---|
| Infeed chains | 0 to 7 | AP_Infeed_L/R_Chain, sprockets |
| Walking beam pick | 7.5 | AP_WalkingBeam: up 0.05 m, +X 1.5 m, down, back (rectangular cycle); lift and travel cylinders follow |
| Weigh | 9.0 | none (rail on load cells) |
| Flatten press | 10.5 | AP_PressPlaten_Up/Down slide along X toward the anode, 0.3 m stroke |
| Lug straightening | 12.0 | AP_LugPressHead_L/R move down 0.17 m onto the lugs |
| Lug milling | 13.5 | AP_MillHead_L/R and AP_MillCutter_L/R rise 0.05 m together; cutters spin about Z |
| Inspection + reject | 15.0 | AP_RejectTongs lift 0.3 m (move along Z), AP_RejectTrolley travels -2.6 m along Y to the reject rack; tongs ride with the trolley |
| Spacing chain + pickup | 16.0 to 28.5 | AP_Spacer_L/R_Chain, AP_SpacerDogs (move with the chain) |

Hydraulic cylinders are split into _Barrel (pivot at the base end) and _Rod (pivot at the rod end),
both with local +X along the cylinder axis, so they can be aimed at each other.

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| AP_Dressing | (0.00, 0.00, 0.00) |
| AP_Guards | (0.00, 0.00, 0.00) |
| AP_Infeed_Frame | (0.00, 0.00, 0.00) |
| AP_Infeed_L_Chain | (0.00, 0.56, 1.44) |
| AP_Infeed_L_Sprocket_Head | (7.00, 0.56, 1.44) |
| AP_Infeed_L_Sprocket_Tail | (0.00, 0.56, 1.44) |
| AP_Infeed_R_Chain | (0.00, -0.56, 1.44) |
| AP_Infeed_R_Sprocket_Head | (7.00, -0.56, 1.44) |
| AP_Infeed_R_Sprocket_Tail | (0.00, -0.56, 1.44) |
| AP_InspectReject | (15.00, 0.00, 0.00) |
| AP_LugPressCyl_L_Barrel | (12.00, 0.58, 2.45) |
| AP_LugPressCyl_L_Rod | (12.00, 0.58, 1.85) |
| AP_LugPressCyl_R_Barrel | (12.00, -0.58, 2.45) |
| AP_LugPressCyl_R_Rod | (12.00, -0.58, 1.85) |
| AP_LugPressFrame | (12.00, 0.00, 0.00) |
| AP_LugPressHead_L | (12.00, 0.58, 1.85) |
| AP_LugPressHead_R | (12.00, -0.58, 1.85) |
| AP_MillCutter_L | (13.50, 0.58, 1.55) |
| AP_MillCutter_R | (13.50, -0.58, 1.55) |
| AP_MillFrame | (13.50, 0.00, 0.00) |
| AP_MillHead_L | (13.50, 0.58, 0.80) |
| AP_MillHead_R | (13.50, -0.58, 0.80) |
| AP_PickupGuides | (23.75, 0.00, 0.00) |
| AP_PressCyl_Down_Barrel | (11.48, 0.00, 1.18) |
| AP_PressCyl_Down_Rod | (11.01, 0.00, 1.18) |
| AP_PressCyl_Up_Barrel | (9.52, 0.00, 1.18) |
| AP_PressCyl_Up_Rod | (9.99, 0.00, 1.18) |
| AP_PressFrame | (10.50, 0.00, 0.00) |
| AP_PressPlaten_Down | (10.85, 0.00, 1.18) |
| AP_PressPlaten_Up | (10.15, 0.00, 1.18) |
| AP_RejectTongs | (15.00, 0.00, 2.60) |
| AP_RejectTrolley | (15.00, 0.00, 3.40) |
| AP_SpacerDogs | (16.00, 0.00, 1.60) |
| AP_Spacer_Frame | (16.00, 0.00, 0.00) |
| AP_Spacer_L_Chain | (16.00, 0.56, 1.44) |
| AP_Spacer_L_Sprocket_Head | (28.50, 0.56, 1.44) |
| AP_Spacer_L_Sprocket_Tail | (16.00, 0.56, 1.44) |
| AP_Spacer_R_Chain | (16.00, -0.56, 1.44) |
| AP_Spacer_R_Sprocket_Head | (28.50, -0.56, 1.44) |
| AP_Spacer_R_Sprocket_Tail | (16.00, -0.56, 1.44) |
| AP_StationFrame | (7.00, 0.00, 0.00) |
| AP_WalkingBeam | (7.00, 0.00, 0.40) |
| AP_WalkingBeam_LiftCyl_0_Barrel | (7.00, 0.00, 0.00) |
| AP_WalkingBeam_LiftCyl_0_Rod | (7.00, 0.00, 0.28) |
| AP_WalkingBeam_LiftCyl_1_Barrel | (15.60, 0.00, 0.00) |
| AP_WalkingBeam_LiftCyl_1_Rod | (15.60, 0.00, 0.28) |
| AP_WalkingBeam_TravelCyl_Barrel | (5.60, 0.00, 0.18) |
| AP_WalkingBeam_TravelCyl_Rod | (6.92, 0.00, 0.18) |

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
| Capacity | up to 500 anodes/h | Sourced, Metso brochure (vendor claim) |
| Anode body | 0.96 x 0.98 x 0.04 m, ~340 kg with lugs | Estimated inside the sourced 1 x 1 x 0.04-0.05 m, 300-380 kg range |
| Lug span | 1.24 m | Estimated |
| Electrode pitch | 0.1 m | Sourced (same-type pitch in the cell) |
| Anodes per cell load | 45 | Inside the sourced 30-50 range; change LOAD in the script |
| Lug seat height 1.6 m, chains 7 m and 12.5 m, 1.5 m station step | | Own design |
| Press frame 2.3 x 2.4 x 3.3 m, platens 0.92 x 0.90 m | | Estimated |

Sources: US4903519A, US5799529A, US8227345B2 (patents.google.com); Metso copper electrorefining
brochure (https://metso.com/globalassets/industry-pages/metals-refining/hydrometallurgy/mo_copper_electrorefining_brochure_final_lowres.pdf).

## Files

- SM_AnodePrepMachine.blend / .fbx (REF collection with anodes, floor and figure is not exported)
- Preview_Overview.png, Preview_PressMill.png, Preview_Pickup.png
