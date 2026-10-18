# SM_NickelSulfate

Nickel sulfate plant for the tankhouse electrolyte bleed: forced-circulation evaporative
crystallizer with vacuum condenser, pusher centrifuge, fluid bed dryer and 25 kg bagging, in one
building. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/ByproductsRod/build_nickel_sulfate.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Building
42 × 18 m (x 0 to 42, y -10 to 8),
13 m eaves; the dryer vent stands above the roof. Place it next to the liberator cells
(Tankhouse thread); the only process feed is the decopperized bleed flange below.

## Flowsheet (simplified)

Decopperized bleed (copper already electrowon out in the liberator cells) → feed tank (FRP,
Ø3.0 × 4.0 m) → forced-circulation crystallizer: vertical heater (Ø1.2 × 5 m, LP steam) and
vapour body (Ø2.5 m, 4 m straight side, cone bottom), axial circulation pump, vacuum from a
surface condenser and liquid ring vacuum pump → NiSO4·6H2O slurry drawn off to the agitated slurry
tank → pusher centrifuge (wet crystals) → screw conveyor → fluid bed dryer (6 × 1.6 m bed, cyclone
and bag filter on the exhaust) → rotary valve → bucket elevator → product bin → 25 kg bags on 1 t
pallets. The centrifuge mother liquor (black acid, strong H2SO4 with residual Ni/As/Sb) goes to
its own tank and leaves through a flange.

Many refineries use an evaporation-and-cooling route with a separate cooling crystallizer, and
some newer ones replace evaporation with ion exchange / acid retardation (Palabora runs acid
retardation and three IX stages before its crystallizer). The IX stage is not modelled.

## Moving parts

| Part | Motion |
|---|---|
| NIS_SlurryTank_Agitator | Spin about Z |
| NIS_Centrifuge_Basket | Spin about X (pusher centrifuges run roughly 1,000-2,000 rpm; estimate) |
| NIS_Centrifuge_Pusher | Translate along X, short stroke (~50 mm) at ~1 Hz, while also spinning with the basket |
| NIS_ScrewConveyor_Flight | Spin about its own axis (the axis runs from its pivot toward the dryer feed) |
| NIS_RotaryValve | Spin about Y |

### Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| NIS_Bags_25kg | (38.00, -0.50, 0.00) |
| NIS_BucketElevator | (35.00, -4.00, 0.00) |
| NIS_Building_Frame | (0.00, -10.00, 0.00) |
| NIS_Building_Roof | (0.00, -10.00, 13.00) |
| NIS_Building_Wall_E | (42.00, -10.00, 0.00) |
| NIS_Building_Wall_N | (0.00, 8.00, 0.00) |
| NIS_Building_Wall_S | (0.00, -10.00, 0.00) |
| NIS_Building_Wall_W | (0.00, -10.00, 0.00) |
| NIS_Centrifuge | (21.50, -4.00, 4.00) |
| NIS_Centrifuge_Basket | (21.50, -4.00, 5.20) |
| NIS_Centrifuge_Pusher | (21.10, -4.00, 5.20) |
| NIS_CirculationLoop | (8.00, 0.00, 0.00) |
| NIS_Condenser | (14.00, 3.50, 0.00) |
| NIS_Deck_Centrifuge | (15.00, -7.50, 0.00) |
| NIS_FeedTank | (3.00, 4.00, 0.00) |
| NIS_FluidBedDryer | (27.00, -4.00, 0.00) |
| NIS_Heater | (8.00, 0.00, 0.00) |
| NIS_MotherLiquorTank | (20.00, -9.70, 0.00) |
| NIS_Platform_Evaporator | (6.50, -2.00, 0.00) |
| NIS_ProductBin | (38.00, -4.00, 0.00) |
| NIS_RotaryValve | (33.40, -4.00, 1.20) |
| NIS_RotaryValve_Housing | (33.00, -4.00, 1.20) |
| NIS_ScrewConveyor | (22.40, -4.00, 3.70) |
| NIS_ScrewConveyor_Flight | (22.40, -4.00, 3.70) |
| NIS_SlurryTank | (17.00, -4.00, 4.00) |
| NIS_SlurryTank_Agitator | (17.00, -4.00, 6.78) |
| NIS_VapourBody | (11.50, 0.00, 0.00) |

## Connection points

| Point | Location |
|---|---|
| Bleed feed in (decopperized electrolyte from the liberators) | (0.4, 4.0, 3.8) |
| Low-pressure steam in | (5.5, 0, 12.0) |
| Steam condensate out | (6.4, -2.5, 0.5) |
| Cooling water in (condenser) | (19.9, 3.5, 10.75) |
| Cooling water out (condenser) | (19.9, 3.5, 10.25) |
| Process condensate out (to electrolyte make-up) | (18.3, 7.8, 0.6) |
| Mother liquor (black acid) out, to acid return / electrolyte make-up | (22.3, -9.8, 0.6) |
| Dryer exhaust vent (above roof) | (38.0, -7.4, 16.0) |
| Bagged NiSO4·6H2O pallet pickup | (38.5, -0.5, 0.0) |

## Unreal import

Combine Meshes off. For the moving parts, import with Transform Vertex to Absolute off and place
each part at the pivot listed above. The building roof and walls are separate objects
(NIS_Building_Roof, _Wall_N/S/E/W) so they can be hidden for cutaways.

## Dimensions

I found no published drawing of a copper-refinery nickel sulfate plant. The process chain
(evaporative crystallizer → centrifuge → fluid bed dryer → rotary valve → product bin → 25 kg
bags) is sourced from Palabora's description; all sizes and the layout are estimates.

| Item | Value | Status |
|---|---|---|
| Process chain and 25 kg bag product | | Sourced (Palabora) |
| Black acid (mother liquor) by-product | | Sourced (Aurubis Olen factsheet, as quoted in a search result; the PDF itself was not opened) |
| Throughput basis | ~1-2 t/d NiSO4·6H2O | Estimate for a mid-size refinery bleed |
| Feed tank Ø3.0 × 4.0 m FRP | ≈ 28 m³ | Estimated |
| Heater Ø1.2 × 5 m, vapour body Ø2.5 m × 4 m + cone | | Estimated |
| Condenser Ø1.2 × 4.5 m, condensate receiver Ø1.6 × 2 m | | Estimated |
| Slurry tank Ø2.2 × 2.4 m, centrifuge basket Ø1.2 × 1.4 m | | Estimated |
| Fluid bed dryer bed 6.0 × 1.6 m | | Estimated |
| Product bin Ø2.6 × 3 m + cone | ≈ 20 m³ | Estimated |
| Building 42 × 18 m, 13 m eaves | | Own design |

Sources: Palabora nickel sulphate production (https://palabora.co.za/Our-Activities/Our-products/Nickel-Sulphate-production);
Aurubis Olen factsheet (https://aurubis.com/dam/jcr:cd8a8481-e965-4fd8-a11e-de02ecfa7a91/2024_12_factsheet_BOB_EN.pdf);
emew on liberator cells and nickel recovery (https://emew.com/blog/liberating-copper-and-nickel-a-true-story).

## Files

- SM_NickelSulfate.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Evaporator.png, Preview_CentrifugeDryer.png (roof and south wall hidden)
