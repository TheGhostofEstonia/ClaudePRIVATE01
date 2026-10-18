# SM_AnodeSlimesPlant

Anode slimes plant and precious metals refinery: decopperizing autoclave, filter press, dryer,
Kaldo furnace with selenium scrubbing, doré anode casting, Moebius silver cells, Wohlwill gold
cells, induction furnace, bar casting and a vault, in one building. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/ByproductsRod/build_anode_slimes_plant.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Building
52 × 27 m (x 0 to 52, y -13 to 14),
14 m eaves, crane runway at 11.5 m. North bay (y > 0) is the process bay, south bay
(y < 0) the precious metals refinery with the vault in its south-east corner. The slimes
come from the tankhouse as slurry through the inlet flange below.

## Flowsheet (simplified)

Slimes slurry → agitated receiving tank → acid pressure leach in a 4-compartment autoclave with
oxygen (decopperizing; copper and part of the tellurium go into solution) → flash tank → filter
press (filtrate back to the tankhouse) → rotary dryer → Kaldo / top blown rotary converter:
smelting and converting to doré, selenium leaves as SeO2 in the off-gas and is caught in the wet
scrubbers → doré poured to the ladle car and cast into doré anodes on the turntable → Moebius
cells (silver crystals on stainless cathodes) → silver crystals melted in the induction furnace
and cast into bars. Gold-bearing anode slime from the silver cells goes to the Wohlwill cells;
the gold cathodes are melted and cast the same way. Bars go to the vault.

## Moving parts

| Part | Motion |
|---|---|
| ASP_ReceivingTank_Agitator, ASP_Autoclave_Agitator_1..4 | Spin about Z |
| ASP_FilterPress_Plate01..24 | Translate along +X one at a time to open the press and drop the cake |
| ASP_FilterPress_MovingHead | Translate along +X (≈ 1.5 m stroke) |
| ASP_RotaryDryer_Drum | Spin about X (a few rpm) |
| ASP_Kaldo_Cradle | Rotate about Y on the trunnions: working position as built (mouth 25° up); about −60° to pour, +65° to stand upright for charging. Parent ASP_Kaldo_Vessel to it |
| ASP_Kaldo_Vessel | Spin about its local X (the vessel axis, origin on the trunnion centre); Kaldo vessels rotate at up to a few tens of rpm (estimate) |
| ASP_LadleCar | Translate along −Y from under the mouth to the doré casting table |
| ASP_DoreCasting_Table | Rotate about Z in 45° steps (8 moulds) |
| ASP_InductionFurnace | Rotate about Y on its trunnions to pour (spout on +X) |
| ASP_Vault_Door | Rotate about Z at the hinge (pivot), opens outward to +Y |

### Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| ASP_Autoclave | (7.00, 6.00, 2.80) |
| ASP_Autoclave_Agitator_1 | (8.00, 6.00, 4.15) |
| ASP_Autoclave_Agitator_2 | (10.00, 6.00, 4.15) |
| ASP_Autoclave_Agitator_3 | (12.00, 6.00, 4.15) |
| ASP_Autoclave_Agitator_4 | (14.00, 6.00, 4.15) |
| ASP_BarCasting | (38.50, -6.00, 0.00) |
| ASP_Building_Frame | (0.00, -13.00, 0.00) |
| ASP_Building_Roof | (0.00, -13.00, 14.00) |
| ASP_Building_Wall_E | (52.00, -13.00, 0.00) |
| ASP_Building_Wall_N | (0.00, 14.00, 0.00) |
| ASP_Building_Wall_S | (0.00, -13.00, 0.00) |
| ASP_Building_Wall_W | (0.00, -13.00, 0.00) |
| ASP_CakeConveyor | (25.00, 6.00, 0.00) |
| ASP_DoreCasting_Base | (44.00, 1.50, 0.00) |
| ASP_DoreCasting_Table | (44.00, 1.50, 0.90) |
| ASP_FilterPress_FiltrateLine | (20.50, 7.00, 0.00) |
| ASP_FilterPress_Frame | (20.00, 6.00, 0.00) |
| ASP_FilterPress_MovingHead | (22.30, 6.00, 1.60) |
| ASP_FilterPress_Plate01 | (20.35, 6.00, 1.60) |
| ASP_FilterPress_Plate02 | (20.42, 6.00, 1.60) |
| ASP_FilterPress_Plate03 | (20.50, 6.00, 1.60) |
| ASP_FilterPress_Plate04 | (20.58, 6.00, 1.60) |
| ASP_FilterPress_Plate05 | (20.65, 6.00, 1.60) |
| ASP_FilterPress_Plate06 | (20.73, 6.00, 1.60) |
| ASP_FilterPress_Plate07 | (20.80, 6.00, 1.60) |
| ASP_FilterPress_Plate08 | (20.88, 6.00, 1.60) |
| ASP_FilterPress_Plate09 | (20.95, 6.00, 1.60) |
| ASP_FilterPress_Plate10 | (21.02, 6.00, 1.60) |
| ASP_FilterPress_Plate11 | (21.10, 6.00, 1.60) |
| ASP_FilterPress_Plate12 | (21.17, 6.00, 1.60) |
| ASP_FilterPress_Plate13 | (21.25, 6.00, 1.60) |
| ASP_FilterPress_Plate14 | (21.33, 6.00, 1.60) |
| ASP_FilterPress_Plate15 | (21.40, 6.00, 1.60) |
| ASP_FilterPress_Plate16 | (21.48, 6.00, 1.60) |
| ASP_FilterPress_Plate17 | (21.55, 6.00, 1.60) |
| ASP_FilterPress_Plate18 | (21.62, 6.00, 1.60) |
| ASP_FilterPress_Plate19 | (21.70, 6.00, 1.60) |
| ASP_FilterPress_Plate20 | (21.77, 6.00, 1.60) |
| ASP_FilterPress_Plate21 | (21.85, 6.00, 1.60) |
| ASP_FilterPress_Plate22 | (21.92, 6.00, 1.60) |
| ASP_FilterPress_Plate23 | (22.00, 6.00, 1.60) |
| ASP_FilterPress_Plate24 | (22.08, 6.00, 1.60) |
| ASP_FlashTank | (17.50, 6.00, 0.00) |
| ASP_InductionFurnace | (36.00, -6.00, 1.40) |
| ASP_InductionFurnace_Frame | (36.00, -6.00, 0.00) |
| ASP_Kaldo_Base | (39.00, 6.00, 0.00) |
| ASP_Kaldo_Cradle | (39.00, 6.00, 3.60) |
| ASP_Kaldo_Hood | (41.61, 6.00, 5.45) |
| ASP_Kaldo_Vessel | (39.00, 6.00, 3.60) |
| ASP_LadleCar | (42.41, 6.00, 0.12) |
| ASP_LadleCar_Rails | (42.41, 6.00, 0.00) |
| ASP_MoebiusCells | (6.00, -6.00, 0.00) |
| ASP_ReceivingTank | (3.50, 6.00, 0.00) |
| ASP_ReceivingTank_Agitator | (3.50, 6.00, 3.78) |
| ASP_RotaryDryer_Base | (29.00, 6.00, 0.00) |
| ASP_RotaryDryer_Drum | (29.00, 6.00, 1.60) |
| ASP_SeleniumScrubbers | (46.00, 11.00, 0.00) |
| ASP_Vault | (44.00, -12.00, 0.00) |
| ASP_Vault_Bars | (45.00, -11.20, 0.53) |
| ASP_Vault_Door | (46.00, -6.95, 0.00) |
| ASP_WohlwillCells | (29.00, -6.00, 0.00) |

## Connection points

| Point | Location |
|---|---|
| Anode slimes slurry in (from the tankhouse) | (0.3, 6.0, 3.2) |
| Oxygen supply | (5.5, 4.6, 6.0) |
| Steam supply (autoclave heating) | (14.6, 2.5, 6.0) |
| Flash vent (above roof, to scrubber) | (17.5, 6.0, 16.0) |
| Filtrate (copper-bearing) out, back to the tankhouse | (20.5, 13.8, 0.4) |
| Scrubber stack top | (51.4, 12.4, 18.0) |
| Selenium sludge drain (liquor tank 2) | (49.0, 8.0, 0.3) |
| Vault door (security perimeter boundary) | (46.7, -6.7, 0.0) |

## Unreal import

Combine Meshes off. For the moving parts, import with Transform Vertex to Absolute off and place
each part at the pivot listed above. Attach ASP_Kaldo_Vessel to ASP_Kaldo_Cradle so it tilts with
it. The building roof and walls are separate objects (ASP_Building_Roof, _Wall_N/S/E/W). The
vault walls, roof and door are solid, so the vault works as a closed room for gameplay.

## Dimensions

No general-arrangement drawing of an anode slimes plant was found. The process route is sourced;
every size and the layout are mine.

| Item | Value | Status |
|---|---|---|
| Route: pressure leach decopperization → TBRC (Kaldo) smelting to doré, selenium off as SeO2 | | Sourced (US4581064 TBRC patent; Metso slimes scope via the research notes) |
| Acid pressure leach conditions 80-120 °C, 2-8 bar O2 | | Sourced (2017 Physicochemical Problems of Mineral Processing paper) |
| Moebius cells for silver, Wohlwill cells for gold | | Sourced from a secondary review (Indonesian Mining Journal 2013); standard practice, not verified against a plant |
| Throughput basis | ≈ 500-1,000 t/a slimes | Estimated; Aurubis Hamburg's central plant takes ~8,000 t/a, a single-refinery plant is much smaller |
| Autoclave Ø2.2 × 8 m, 4 compartments | | Estimated |
| Filter press 1.2 m plates, 24 plates | | Estimated |
| Rotary dryer Ø1.2 × 5 m | | Estimated |
| Kaldo vessel Ø2.5 m, 3.6 m long | | Estimated (small-batch class) |
| Moebius cells 1.2 × 0.9 × 0.8 m, 16 cells | | Estimated |
| Silver bar ~30 kg (300 × 130 × 100 mm, rounded), gold bar ~12.5 kg (250 × 70 × 40 mm, rounded) | | Typical market bar masses; shapes simplified |
| Vault 6 × 5 m, 0.4 m walls | | Own design |

Sources: US4581064A TBRC slimes treatment (https://patents.google.com/patent/US4581064);
US4163046 recovery of selenium (https://patents.justia.com/patent/4163046); Physicochemical
Problems of Mineral Processing, pressure leaching of decopperized slimes (https://dlibra.kdm.wcss.pl/Content/38198/download);
Indonesian Mining Journal review (https://jurnal.tekmira.esdm.go.id/index.php/imj/article/view/382/255);
Aurubis Hamburg slimes plant (https://recyclinginternational.com/?p=6097).

## Files

- SM_AnodeSlimesPlant.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Kaldo.png, Preview_Hydro.png, Preview_Refinery.png (roof and south wall hidden)
