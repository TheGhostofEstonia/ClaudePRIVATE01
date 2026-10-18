# SM_SlagPotCarrier

Kress-type U-frame slag pot carrier for the ~16 m³ slag pots. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/build_slag_pot_carrier.py`; re-run the script to rebuild.

## Placement

- Local axes: +X front (closed end, engine, cab), -X open end. Origin is the ground point under
  the pot centre when the pot is in the hooks.
- To pick up a pot, place the carrier origin on the pot's ground centre with the open end facing
  the pot. At the slag pot pit, pots are at (46.0, 8.8, -5.5) and (46.0, 15.3, -5.5) in flash
  furnace coordinates and the carrier enters from the east, so carrier yaw is 0 (front facing +X)
  and the carrier reverses west over the pot.
- This assumes the pot trunnions point along ±Y (north-south). If SM_SlagPots has its trunnions
  along X, rotate the pot or the carrier 90°. I could not read SM_SlagPots from the cloud
  environment, so the hook height (1.80 m) and trunnion span (4.04 m tip to tip, sitting in hooks 3.84 m apart) are assumed.
  Change `POT_TRUNNION_Z` and `POT_TRUNNION_HALF_SPAN` in the script and re-run to match.

## Moving parts

| Part | Motion | Pivot / axis |
|---|---|---|
| CAR_Cradle | Rotates about local Y. Front up lifts the pot. Travel pose ≈ 12° front-up, dump ≈ 140° (the patent figure). In Blender that is rotation Y = -12° and -140°. | Rear axle line (-3.60, 0, 0.935) |
| CAR_Wheel_FL/FR/RL/RR | Spin about local Y. FL/FR also steer about local Z. | Hub centre |
| CAR_LiftCyl_L/R_Barrel | Aim local +X at the matching rod pivot | Frame lug (0.50, ±1.98, 2.75) |
| CAR_LiftCyl_L/R_Rod | Moves with the cradle horn; aim local +X at the barrel pivot | Horn tip, attached to the cradle |

In the .blend the rods and the REF pot proxy are parented to CAR_Cradle and the cylinders have
Damped Track constraints, so rotating CAR_Cradle poses the whole mechanism. In Unreal, attach the
rods (and the pot) to the cradle component and use a look-at for the two cylinder halves.

Tyre circumference = 2π × 0.935 = 5.87 m, so wheel spin (deg/s) = speed (m/s) × 61.3.

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CAR_Cab | (0.00, 0.00, 0.00) |
| CAR_Cradle | (-3.60, 0.00, 0.94) |
| CAR_Frame | (0.00, 0.00, 0.00) |
| CAR_LiftCyl_L_Barrel | (0.50, 1.98, 2.75) |
| CAR_LiftCyl_L_Rod | (-3.60, 1.98, 2.09) |
| CAR_LiftCyl_R_Barrel | (0.50, -1.98, 2.75) |
| CAR_LiftCyl_R_Rod | (-3.60, -1.98, 2.09) |
| CAR_PowerModule | (0.00, 0.00, 0.00) |
| CAR_Wheel_FL | (3.95, 2.42, 0.94) |
| CAR_Wheel_FR | (3.95, -2.42, 0.94) |
| CAR_Wheel_RL | (-3.60, 2.42, 0.94) |
| CAR_Wheel_RR | (-3.60, -2.42, 0.94) |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves the pivot to the asset origin. For the moving parts, import with it off and place
each part at the pivot listed above. The Blender Y axis appears as -Y in Unreal with the default
FBX settings, so check rotation signs after import.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Overall length × width × height | 9.85 × 5.70 × 4.40 m | Sourced: Kress carriers at Mount Isa (Glencore, 2020) |
| Full pot handled | 75-80 t at Mount Isa | Sourced (same article); our pot is smaller |
| Cradle pivots on the rear wheel axis, hooks + lug stops on trunnions, seat under the pot's end lug, ~140° tip, travel-lock struts | Layout | Sourced: US4063658A (now Kress) |
| Lift by a single cylinder on a horn above the pivot | Mechanism | Own design. The patent uses a lever and link per side; I simplified it to one cylinder so it animates with a look-at. |
| Tyres ≈ 1.87 m dia × 0.65 m (29.5R25 class) | | Estimated |
| Axles at x = -3.60 and +3.95, cab on the left front corner, engine module on the front deck | | Estimated from photos, no drawings |
| Hook height 1.80 m, trunnion span 4.04 m, clear width between the cradle arms 3.84 m | | Assumed to suit the ~16 m³ pot |
| REF pot proxy: rim Ø3.6, base Ø2.4, 2.6 m tall | | Assumed, for previews only |

Sources: Glencore "Around for the long haul: Kress slag pot carriers" (Resourceful, Dec 2020) as
cited in research/copper-refinery/copper-refinery-equipment.md [S8]; US4063658A
(https://patents.google.com/patent/US4063658A/en); Kress product page
(https://kresscarrier.com/CarriersSlagPot.html: carriers up to 227 t, pots up to 45 m³).

## Files

- SM_SlagPotCarrier.blend / .fbx (the REF collection is not exported)
- Preview_Overview.png (pot in hooks), Preview_Travel.png, Preview_Dump.png
