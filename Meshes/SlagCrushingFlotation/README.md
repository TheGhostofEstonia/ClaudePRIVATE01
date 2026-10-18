# SM_SlagCrushingFlotation

Slag concentrator: ROM hopper with rock breaker, jaw crusher, scalping screen and cone crusher,
fine ore bin, ball mill with cyclones, flotation cells and a concentrate thickener, in one folder
because the parts are small enough to share one asset. Built in Blender 5.2.2 LTS (headless,
cloud) with `Tools/Blender/build_slag_crushing_flotation.py`.

## Placement

Shares the flash furnace origin: place at (0, 0, 0), no rotation. Blender +X is taken as east,
+Y as north. It sits west and north of the cooling yard (x -240 to -55, y 180 to 300), away from
the acid plant east of x = 69.6. A loader carries broken slag from the yard's breaking pit
up the yard exit ramp (top at (-55, 187, 0)) straight onto this asset's loader ramp.

## Flowsheet (simplified)

ROM hopper (6 × 6 m, static grizzly at 400 mm, pedestal rock breaker) → vibrating grizzly feeder →
jaw crusher (~900 × 600 mm class) → CV01 → scalping screen (1.5 × 3.6 m, 20°) → oversize to the
cone crusher → screen undersize + cone product on CV02 → fine ore bin (Ø7 m) → CV03 → ball mill
(Ø3.2 × 4.5 m) in closed circuit with 4 cyclones → rougher/scavenger bank 4 × 10 m³ → cleaner bank
3 × 3 m³ → concentrate thickener (Ø6.4 m). Tailings leave through a stub flange.

Sizing basis (own estimate): ≈ 500 t/d of slag from the cooling yard; crushing ≈ 45 t/h on one or
two shifts, milling ≈ 22 t/h continuous, grind ~80 % passing 45 µm (Aurubis Pirdop runs its slag
flotation feed at P80 38 µm), flotation feed ≈ 50 m³/h pulp at ~35 % solids, ~30 min
rougher-scavenger residence. Slow-cooled slag is crushed and ground before flotation in the
sourced practice (US4046323: broken to ~300 mm, crushed to ~6 mm, then milled and floated).

## Moving parts

| Part | Motion |
|---|---|
| CONC_RockBreaker_Slew | Rotate about local Z |
| CONC_RockBreaker_Boom | Rotate about local Y at the boom foot (after slew yaw) |
| CONC_RockBreaker_Stick | Rotate about local Y at the boom tip; hammer is part of the stick |
| CONC_GrizzlyFeeder_Deck | Vibrate (small X/Z oscillation, ~15 Hz) |
| CONC_JawCrusher_Pitman | Swing about Y at the eccentric shaft, ±2° at ~4-5 Hz |
| CONC_JawCrusher_Flywheel_L/R | Spin about Y (~250-300 rpm) |
| CONC_Screen_Deck | Vibrate along its slope |
| CONC_ConeCrusher_Head | Gyrate: small tilt (1-2°) whose direction rotates about Z |
| CONC_ConeCrusher_Pulley | Spin about X |
| CONC_BallMill_Shell | Spin about X, ~16-17 rpm (≈75 % of critical speed for Ø3.2 m) |
| CONC_BallMill_Pinion | Spin about X, opposite direction, ~8× shell speed |
| CONC_Flot_R1..R4_Impeller, CONC_Flot_C1..C3_Impeller | Spin about Z (shaft + impeller) |
| CONC_Thickener_Rake | Spin about Z, very slow (~0.1-0.3 rpm) |
| CONC_Crane_Bridge / Trolley / Hook | Translate X / Y / Z |
| CONC_CV0x_HeadPulley, _TailPulley | Spin about the pulley axis |
| CONC_Flot_Froth | Static froth surfaces, for a panning froth material |

### Belts

0.8 m belts with continuous UVs at the conveyor kit's texel density (1 UV = 1.2 m in both
directions, so V spans 0 to 0.667 across the belt). Panner speed in U = belt speed / 1.2, same
material as the kit. Carry runs are troughed at 30°, flattening near the pulleys.

| Belt | Loop length | U at loop end |
|---|---|---|
| CONC_CV01_Belt | 99.84 m | 83.201 |
| CONC_CV02_Belt | 97.10 m | 80.915 |
| CONC_CV03_Belt | 47.56 m | 39.635 |

### Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CONC_BallMill_Base | (-168.45, 290.00, 3.00) |
| CONC_BallMill_Pinion | (-169.80, 288.10, 2.60) |
| CONC_BallMill_Shell | (-168.45, 290.00, 3.00) |
| CONC_Building_Frame | (-205.00, 268.00, 0.00) |
| CONC_Building_Roof | (-205.00, 268.00, 14.00) |
| CONC_Building_Wall_E | (-160.00, 268.00, 0.00) |
| CONC_Building_Wall_N | (-205.00, 300.00, 0.00) |
| CONC_Building_Wall_S | (-205.00, 268.00, 0.00) |
| CONC_Building_Wall_W | (-205.00, 268.00, 0.00) |
| CONC_CV01_Belt | (0.00, 0.00, 0.00) |
| CONC_CV01_HeadPulley | (-140.00, 232.88, 11.29) |
| CONC_CV01_Structure | (-140.00, 185.60, -1.25) |
| CONC_CV01_TailPulley | (-140.00, 185.68, -1.56) |
| CONC_CV02_Belt | (0.00, 0.00, 0.00) |
| CONC_CV02_HeadPulley | (-140.00, 282.09, 14.89) |
| CONC_CV02_Structure | (-140.00, 236.50, 1.40) |
| CONC_CV02_TailPulley | (-140.00, 236.59, 1.09) |
| CONC_CV03_Belt | (0.00, 0.00, 0.00) |
| CONC_CV03_HeadPulley | (-163.27, 284.00, 6.09) |
| CONC_CV03_Structure | (-141.00, 284.00, 1.30) |
| CONC_CV03_TailPulley | (-141.07, 284.00, 0.99) |
| CONC_ConeCrusher_Body | (-140.00, 237.20, 4.50) |
| CONC_ConeCrusher_Head | (-140.00, 237.20, 6.40) |
| CONC_ConeCrusher_Pulley | (-137.70, 237.20, 5.00) |
| CONC_Crane_Bridge | (-169.00, 284.00, 11.20) |
| CONC_Crane_Hook | (-169.00, 286.00, 9.20) |
| CONC_Crane_Trolley | (-169.00, 286.00, 12.20) |
| CONC_CrusherPit | (-140.00, 187.00, -2.20) |
| CONC_CycloneCluster | (-165.20, 290.00, 9.50) |
| CONC_FineOreBin | (-140.00, 284.00, 0.00) |
| CONC_Flot_C1_Impeller | (-190.00, 284.00, 3.70) |
| CONC_Flot_C2_Impeller | (-193.60, 284.00, 3.40) |
| CONC_Flot_C3_Impeller | (-197.20, 284.00, 3.10) |
| CONC_Flot_Froth | (-172.00, 276.00, 0.00) |
| CONC_Flot_R1_Impeller | (-172.00, 276.00, 4.10) |
| CONC_Flot_R2_Impeller | (-176.50, 276.00, 3.80) |
| CONC_Flot_R3_Impeller | (-181.00, 276.00, 3.50) |
| CONC_Flot_R4_Impeller | (-185.50, 276.00, 3.20) |
| CONC_Flot_Tanks | (-172.00, 276.00, 0.00) |
| CONC_GrizzlyFeeder_Deck | (-136.17, 187.00, 3.40) |
| CONC_GrizzlyFeeder_Frame | (-133.40, 187.00, 3.55) |
| CONC_JawCrusher_Flywheel_L | (-139.05, 188.15, 2.65) |
| CONC_JawCrusher_Flywheel_R | (-139.05, 185.85, 2.65) |
| CONC_JawCrusher_Frame | (-140.00, 187.00, 0.50) |
| CONC_JawCrusher_Pitman | (-139.05, 187.00, 2.65) |
| CONC_LoaderRamp | (-58.00, 187.00, 0.00) |
| CONC_ROMHopper | (-134.00, 187.00, 6.50) |
| CONC_RockBreaker_Boom | (-129.00, 193.20, 9.40) |
| CONC_RockBreaker_Pedestal | (-129.00, 193.20, 6.50) |
| CONC_RockBreaker_Slew | (-129.00, 193.20, 8.50) |
| CONC_RockBreaker_Stick | (-131.64, 189.93, 11.20) |
| CONC_ScreenTower | (-140.00, 236.00, 0.00) |
| CONC_Screen_Deck | (-140.00, 236.00, 10.60) |
| CONC_TailingsStub | (-205.50, 274.00, 1.00) |
| CONC_Thickener_Rake | (-214.00, 286.00, 4.00) |
| CONC_Thickener_Tank | (-214.00, 286.00, 0.00) |

## Connection points

| Point | Location |
|---|---|
| Loader ramp foot (from the cooling yard exit ramp at (-55, 187, 0)) | (-58.0, 187.0, 0.0), 10 % up to z 6.5 at x -123.0 |
| Cone crusher / screen tower centre | (-140.0, 236.0, 0.0) |
| Fine ore bin (≈260 m³, ≈450 t at 1.7 t/m³ bulk) | centre (-140.0, 284.0), roof z 13.6 |
| Ball mill axis (3.2 m × 4.5 m, shell rotates about X) | (-168.45, 290.0, 3.0) |
| Concentrate underflow flange (to filter / smelter return) | (-217.5, 286.0, 0.4) |
| Tailings flange (to tailings thickener / dam) | (-205.6, 274.0, 1.0) |

## Unreal import

Combine Meshes off. For the moving parts, import with Transform Vertex to Absolute off and place
each part at the pivot listed above (with it on, every pivot moves to the asset origin). The
building roof and walls are separate objects so they can be hidden for cutaways.

## Dimensions

Everything here is an estimate of a typical machine class, not a specific vendor model. I found
no published general-arrangement drawings of a slag concentrator.

| Item | Value | Status |
|---|---|---|
| Jaw crusher, 900 × 600 mm class, ~2.8 × 2.6 × 2.4 m with flywheels Ø1.6 m | | Estimated (40 × 30 in class machines weigh ~21-23 t with feeder, dealer listings) |
| Cone crusher Ø2.0 m body, ~2.2 m tall | | Estimated |
| Screen 1.5 × 3.6 m double deck, 20° | | Estimated |
| Fine ore bin Ø7 m, 8 m straight side | ≈ 260 m³ | Estimated |
| Ball mill Ø3.2 × 4.5 m, ~700 kW | | Estimated from the sizing basis |
| Flotation cells 4 × 10 m³ (Ø2.5 m), 3 × 3 m³ (Ø1.7 m), 0.3 m steps | | Estimated |
| Concentrate thickener Ø6.4 m | | Estimated |
| Building 45 × 32 m, 14 m eaves, overhead crane | | Own design |
| ROM tipping platform 6.5 m, ramp 10 % | | Own design |

Sources: US4046323A (https://patents.google.com/patent/US4046323A/en); Pavez et al. 2021 Atacama
slag flotation case study (https://repositorioacademico.uda.cl/entities/publication/e63bb582-2389-49c5-be25-c5672acb5dca);
Sarcheshmeh converter slag flotation, ~200 t/d (https://onemine.org/documents/flotation-copper-recovery-from-converter-slag-of-the-sarcheshmeh-khatoonabad-smelter);
Metso Nordberg C Series (https://metso.com/portfolio/nordberg-c-series).

## Files

- SM_SlagCrushingFlotation.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Crushing.png, Preview_MillFlotation.png (roof and south wall hidden)
