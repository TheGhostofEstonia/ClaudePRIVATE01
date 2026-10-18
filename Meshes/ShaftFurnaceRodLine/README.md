# SM_ShaftFurnaceRodLine

Cathode melting shaft furnace and continuous copper rod line: skip hoist, shaft furnace, drum
holding furnace, launders and tundish, casting wheel with steel band (Southwire SCR type), bar
preparation, 13-stand rolling mill, alcohol pickling and cooling, waxing, laying head and coil
handling. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/ByproductsRod/build_shaft_furnace_rod_line.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Not tied to the tankhouse
layout; place it wherever the cathode store is. Footprint about x -35 to 82, y -10 to 12
(hall 90 × 22 m, 10 m eaves; the shaft furnace, skip hoist
and stack stand outside the west gable).

## Flow and heights

| Step | Where |
|---|---|
| Cathode bundles arrive on the roller conveyor and drop into the skip | x -33.0 to -25.0 |
| Skip hoist, 60° track, tips into the charge door | door centre (-15.2, 0, 14.5) |
| Shaft furnace on a 6.0 m plinth, shell 6.0 to 17.0 m | centre (-14.0, 0.0) |
| Tap hole → launder → drum holding furnace (axis z 4.6) | x -6.5 to -2.5 |
| Launder → tundish → pour point on the wheel at the 10 o'clock position | (0.68, 0, 2.96) |
| Bar leaves the band at the exit band wheel, pass line z 0.90 | x ≈ 4.6 |
| Pinch rolls, flying shear, edge trimmer | x ≈ 6.6 to 10.4 |
| Rolling mill, 13 stands at 2.0 m pitch | x 11.0 to 37.0 |
| Pickling / cooling tube, air wipe, wax | x 38.0 to 63.0 |
| Laying head and coil forming | (66.0, 0) |
| Coil car (−Y) → strapping press → coil conveyor → pickup | (66.0, −7.0) to (80, −7.0) |

## Moving parts

| Part | Motion |
|---|---|
| SFR_Skip_Car | Translate along the track, direction (0.488, 0, 0.873), 16.4 m travel |
| SFR_ChargeDoor | Slide up along Z (~1.6 m) |
| SFR_HoldingFurnace | Rotate about local X to tilt for draining (pivot on the drum axis) |
| SFR_CastWheel | Spin about local Y; top of the wheel moves toward −X (pour side down). Rim speed ≈ bar speed 0.20-0.28 m/s (sourced, Palabora) → ≈ 1.3-1.8 rpm |
| SFR_BandWheel_Exit / _Tension / _Pour | Spin about local Y at the same rim speed |
| SFR_CastBand | Static loop with continuous UVs (1 UV = 1.2 m along the band); pan U at band speed / 1.2. Loop length 16.62 m |
| SFR_PinchRoll_n_Top / _Bot | Spin about Y, opposite directions |
| SFR_Shear_Blade | Rotate about Y at its pivot (flying shear, used at start-up) |
| SFR_StandNN_RollA / _RollB | Spin about their own axis (odd stands horizontal rolls about Y, even stands vertical rolls about Z), A and B opposite. Speed rises down the mill |
| SFR_LayingHead | Spin about Z |
| SFR_CoilTurntable | Spin about Z, slowly, while the coil forms |
| SFR_Coil_Forming | Static; scale Z from 0 to 1 to show the coil building up |
| SFR_CoilCar | Translate along −Y from its park position at the coiler pad (y −3.7) to the strapping press (y −7); the coil is lifted off the turntable onto it (own design) |
| SFR_StrappingPress_Ram | Translate along Z (compresses the coil) |
| SFR_Coil_Finished_n, SFR_CoilPallet_n | Translate along +X on the coil conveyor |

### Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SFR_BandWheel_Exit | (4.60, 0.00, 1.20) |
| SFR_BandWheel_Pour | (0.10, 0.00, 4.50) |
| SFR_BandWheel_Tension | (3.40, 0.00, 4.70) |
| SFR_BarPrep | (7.10, 0.00, 0.00) |
| SFR_CastBand | (0.00, 0.00, 0.00) |
| SFR_CastBar | (2.00, 0.00, 0.90) |
| SFR_CastWheel | (2.00, 0.00, 2.20) |
| SFR_Caster_Frame | (2.00, 0.00, 0.00) |
| SFR_CathodeBundle_1 | (-31.50, 0.00, 0.82) |
| SFR_CathodeBundle_2 | (-33.00, -2.60, 0.15) |
| SFR_CathodeBundle_3 | (-31.00, -2.60, 0.15) |
| SFR_ChargeDoor | (-15.40, 0.00, 14.50) |
| SFR_Charging_Pad | (-31.00, 0.00, 0.00) |
| SFR_CoilCar | (66.00, -3.70, 0.15) |
| SFR_CoilCar_Rails | (66.00, 0.00, 0.00) |
| SFR_CoilConveyor | (68.00, -7.00, 0.00) |
| SFR_CoilForming_Tub | (66.00, 0.00, 0.30) |
| SFR_CoilPallet_1 | (71.00, -7.00, 0.67) |
| SFR_CoilPallet_2 | (74.50, -7.00, 0.67) |
| SFR_CoilPallet_3 | (78.00, -7.00, 0.67) |
| SFR_CoilTurntable | (66.00, 0.00, 0.30) |
| SFR_Coil_Finished_1 | (71.00, -7.00, 0.81) |
| SFR_Coil_Finished_2 | (74.50, -7.00, 0.81) |
| SFR_Coil_Finished_3 | (78.00, -7.00, 0.81) |
| SFR_Coil_Forming | (66.00, 0.00, 0.56) |
| SFR_Coiler_Tower | (66.00, 0.00, 0.00) |
| SFR_CombustionAir | (-14.00, 5.50, 0.00) |
| SFR_Furnace_Plinth | (-14.00, 0.00, 0.00) |
| SFR_Hall_Frame | (-8.00, -10.00, 0.00) |
| SFR_Hall_Roof | (-8.00, -10.00, 10.00) |
| SFR_Hall_Wall_E | (82.00, -10.00, 0.00) |
| SFR_Hall_Wall_N | (-8.00, 12.00, 0.00) |
| SFR_Hall_Wall_S | (-8.00, -10.00, 0.00) |
| SFR_HoldingFurnace | (-4.50, 0.00, 4.60) |
| SFR_HoldingFurnace_Supports | (-4.50, 0.00, 2.60) |
| SFR_Launder_HoldingToTundish | (-2.05, 0.00, 4.90) |
| SFR_Launder_ShaftToHolding | (-12.40, 0.00, 6.35) |
| SFR_LayingHead | (66.00, 0.00, 4.60) |
| SFR_Mill_Stands | (11.00, 0.00, 0.00) |
| SFR_Pickling_Cooling | (38.00, 0.00, 0.00) |
| SFR_PinchRoll_1_Bot | (7.20, 0.00, 0.70) |
| SFR_PinchRoll_1_Top | (7.20, 0.00, 1.10) |
| SFR_PinchRoll_2_Bot | (7.60, 0.00, 0.70) |
| SFR_PinchRoll_2_Top | (7.60, 0.00, 1.10) |
| SFR_Rod | (11.00, 0.00, 0.90) |
| SFR_ShaftFurnace | (-14.00, 0.00, 6.00) |
| SFR_Shear_Blade | (8.60, 0.00, 1.30) |
| SFR_Skip_Car | (-25.00, 0.00, 0.90) |
| SFR_Skip_Track | (-25.00, 0.00, 0.90) |
| SFR_Stack | (-14.00, -6.00, 0.00) |
| SFR_Stand01_RollA | (12.00, 0.00, 1.16) |
| SFR_Stand01_RollB | (12.00, 0.00, 0.64) |
| SFR_Stand02_RollA | (14.00, 0.16, 0.90) |
| SFR_Stand02_RollB | (14.00, -0.16, 0.90) |
| SFR_Stand03_RollA | (16.00, 0.00, 1.06) |
| SFR_Stand03_RollB | (16.00, 0.00, 0.74) |
| SFR_Stand04_RollA | (18.00, 0.16, 0.90) |
| SFR_Stand04_RollB | (18.00, -0.16, 0.90) |
| SFR_Stand05_RollA | (20.00, 0.00, 1.06) |
| SFR_Stand05_RollB | (20.00, 0.00, 0.74) |
| SFR_Stand06_RollA | (22.00, 0.11, 0.90) |
| SFR_Stand06_RollB | (22.00, -0.11, 0.90) |
| SFR_Stand07_RollA | (24.00, 0.00, 1.01) |
| SFR_Stand07_RollB | (24.00, 0.00, 0.79) |
| SFR_Stand08_RollA | (26.00, 0.11, 0.90) |
| SFR_Stand08_RollB | (26.00, -0.11, 0.90) |
| SFR_Stand09_RollA | (28.00, 0.00, 1.01) |
| SFR_Stand09_RollB | (28.00, 0.00, 0.79) |
| SFR_Stand10_RollA | (30.00, 0.11, 0.90) |
| SFR_Stand10_RollB | (30.00, -0.11, 0.90) |
| SFR_Stand11_RollA | (32.00, 0.00, 1.01) |
| SFR_Stand11_RollB | (32.00, 0.00, 0.79) |
| SFR_Stand12_RollA | (34.00, 0.11, 0.90) |
| SFR_Stand12_RollB | (34.00, -0.11, 0.90) |
| SFR_Stand13_RollA | (36.00, 0.00, 1.01) |
| SFR_Stand13_RollB | (36.00, 0.00, 0.79) |
| SFR_StrappingPress | (66.00, -7.00, 0.00) |
| SFR_StrappingPress_Ram | (66.00, -7.00, 3.60) |
| SFR_Tundish | (0.38, 0.00, 3.86) |
| SFR_Tundish_Stand | (0.38, 0.00, 0.00) |

## Connection points

| Point | Location |
|---|---|
| Cathode bundle feed (roller conveyor head) | (-33.0, 0.0, 0.81) |
| Off-gas stack top | (-10.8, -6.0, 26.4) |
| Natural gas supply | (-11.2, 6.5, 0.6) |
| Caster cooling water supply | (-0.8, 1.4, 0.6) |
| Caster cooling water return (drain) | (5.4, -1.4, 0.3) |
| Alcohol (IPA) make-up | (44.5, 5.0, 0.6) |
| Finished coil pickup (end of coil conveyor) | (80.0, -7.0, 0.6) |

## Unreal import

Combine Meshes off. For the moving parts, import with Transform Vertex to Absolute off and place
each part at the pivot listed above (with it on, every pivot moves to the asset origin). The hall
roof and walls are separate objects so they can be hidden for cutaways. Copper surfaces use one
M_Copper slot; a separate emissive material for hot metal (launders, pour, bar) can be applied in
Unreal on SFR_CastBar and the launder interiors.

## Dimensions

No general-arrangement drawing of a shaft furnace rod line was found. The figures below come from
public product pages, a used-equipment listing and patents; the layout and all other sizes are mine.

| Item | Value | Status |
|---|---|---|
| Shaft furnace melting rate (design basis) | ≈ 25 t/h | Estimated; shaft furnaces for copper are built from 5 to 70 t/h (ABM paper) |
| Shaft furnace shell | Ø2.4 m × 11 m, hearth on a 6 m plinth | Estimated |
| Burner arrangement | 3 rows: 7 / 8 / 8 burners, each row fed from manifolds | Sourced (US4301997 claim 18) |
| Charging by skip hoist | | Sourced (SMS group); 60° track and heights estimated |
| Cylindrical holding furnace between shaft furnace and caster, covered heated launders, tundish with automatic pouring | | Sourced (Palabora) |
| Drum holding furnace Ø2.8 × 4.0 m | | Estimated |
| Casting wheel Ø3.05 m (10 ft), Cu-Cr-Zr rim | | Sourced (used SCR system listing) |
| Cast bar | ≈ 100 × 65 mm (≈ 6,000-6,500 mm²) | Sourced range: 6,000 mm² trapezoid (Primetals) and 10 in² (listing); modelled as a rectangle |
| Bar speed out of the caster | 0.20-0.28 m/s | Sourced (Palabora) |
| Rolling mill: 13 stands, roll Ø 457, 305, 305, 305, 305, 203, 203, 203, 203, 203, 203, 203, 203 mm | | Sourced (used SCR listing: 1 × 18 in, 4 × 12 in, 8 × 8 in; Jinchuan SCR 7000 also 13 stands) |
| Stand pitch 2.0 m, housings, drives | | Estimated |
| Product rod Ø8 mm (7.9-14 mm range) | | Sourced (Palabora, Aurubis) |
| In-line alcohol pickling, wax coating, continuous coiling | | Sourced (Palabora, SMS Contirod) |
| Coil 1.8 m OD × 1.0 m ID × 1.0 m | ≈ 5 t | Estimated; sourced coil masses 2.3-2.7 t (listing), 2-4 t (Jinchuan), 4.6 t average (Palabora), 3.5-8 t (Aurubis) |
| Hall 90 × 22 m, 10 m eaves, crane rail at 8 m | | Own design |
| Coil car, strapping press, coil conveyor layout | | Own design |

The modelled caster is the wheel-and-band type (Southwire SCR). Contirod plants use a twin-belt
(Hazelett) caster in the same position instead.

Sources: US4301997A (https://patents.google.com/patent/US4301997); US5240494A (Asarco, cathode
melting burners, https://patents.google.com/patent/US5240494); ABM proceedings, innovations in
copper processing (https://abmproceedings.com.br/en/article/download-pdf/innovations-in-the-field-of-copper-processing);
SMS group melting furnaces (https://sms-group.com/plants/melting-and-refining-furnaces) and Contirod
fact sheet; Palabora copper rod (https://palabora.com/Our-Activities/Our-products/Copper-rod);
Aurubis Olen rod production (https://www.aurubis.com/en/olen/products/wire-rod/Productionprocess);
used SCR system listing (https://www.exapro.com/southwire-scr-system-2500-p250903031/); Primetals
SCR upgrade (https://www.primetals.com/press-media/news/primetals-technologies-awarded-project-to-increase-capacity-of-southwire-scr-copper-rod-mill);
Jinchuan SCR 7000 (https://umformtechnik.net/wire/Content/Business/New-SCR-copper-rod-mill-for-Jinchuan-Group).

## Files

- SM_ShaftFurnaceRodLine.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_FurnaceCaster.png, Preview_Mill.png, Preview_Coiler.png (hall roof and south wall hidden)
