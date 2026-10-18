# SM_SlagCoolingYard

Slag pot cooling yard with the carrier ramp out of the slag pot pit, pot cooling stations with
water sprays, a tipping station over a breaking pit, a settling pond and a pump house. Built in
Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/build_slag_cooling_yard.py`.

## Placement and layout

Shares the flash furnace origin: place at (0, 0, 0) with no rotation, like SM_SlagPots.
Blender +X is taken as east and +Y as north. The acid plant runs east from x = 69.6 with its
tank farm to the north, so everything here stays at x ≤ 70.6 (the apron's east wall). That
boundary is my assumption, since I could not see the acid plant layout from the cloud.

Carrier route: pit (pots at (46.0, 8.8) and (46.0, 15.3), z -5.5) → turning apron east of the
pit (x 50-70, y -2 to 30, z -5.5) → 10 m wide ramp at x 56-66 climbing north at 8.0 % to grade at
y = 99 → north-south haul lane x 56-66 along the east side of the pad → aisles between the rows →
tipping station at y = 175. The pit wall layout in SM_SlagPots is not known here; the apron
assumes the pit is open on its east side between y -2 and 30 at x = 50. Trim or move the apron to
match.

## Process (sourced practice, simplified)

Pots are set down at a station, left to cool in air and then under water sprays, carried to the
tipping station and inverted over the wall. The solid slag cake drops into the breaking pit, where
it is broken (impact hammer or mobile breaker) and loaded out to the concentrator's ROM bin.
Typical practice in the literature is about 24 h in air and 48 h under water sprays (Springer
2020 review); US4046323 describes 15 h or more to form a 0.25-0.38 m shell before dumping. With
27 stations and a 72 h cycle the yard handles about 9 pots/day (≈ 500 t of slag/day at
16 m³ × ~3.4 t/m³). A plant tapping more slag needs more stations, a shorter cycle, or early tipping
with cake cooling in the pit. The station count is a script parameter (`STATIONS`).

## Pot stations (pot centre at ground, carrier yaw to use)

Carrier yaw is the direction the carrier's front faces: +90° = north, -90° = south. The carrier
straddles the pot with its open end toward the station.

| Station | Pot centre | Carrier yaw |
|---|---|---|
| A1 | (-12.0, 111.0, 0.0) | +90° |
| A2 | (-4.0, 111.0, 0.0) | +90° |
| A3 | (4.0, 111.0, 0.0) | +90° |
| A4 | (12.0, 111.0, 0.0) | +90° |
| A5 | (20.0, 111.0, 0.0) | +90° |
| A6 | (28.0, 111.0, 0.0) | +90° |
| A7 | (36.0, 111.0, 0.0) | +90° |
| A8 | (44.0, 111.0, 0.0) | +90° |
| A9 | (52.0, 111.0, 0.0) | +90° |
| B1 | (-12.0, 141.0, 0.0) | -90° |
| B2 | (-4.0, 141.0, 0.0) | -90° |
| B3 | (4.0, 141.0, 0.0) | -90° |
| B4 | (12.0, 141.0, 0.0) | -90° |
| B5 | (20.0, 141.0, 0.0) | -90° |
| B6 | (28.0, 141.0, 0.0) | -90° |
| B7 | (36.0, 141.0, 0.0) | -90° |
| B8 | (44.0, 141.0, 0.0) | -90° |
| B9 | (52.0, 141.0, 0.0) | -90° |
| C1 | (-12.0, 149.0, 0.0) | +90° |
| C2 | (-4.0, 149.0, 0.0) | +90° |
| C3 | (4.0, 149.0, 0.0) | +90° |
| C4 | (12.0, 149.0, 0.0) | +90° |
| C5 | (20.0, 149.0, 0.0) | +90° |
| C6 | (28.0, 149.0, 0.0) | +90° |
| C7 | (36.0, 149.0, 0.0) | +90° |
| C8 | (44.0, 149.0, 0.0) | +90° |
| C9 | (52.0, 149.0, 0.0) | +90° |

Tipping: carriers reverse north against the curb at y = 174.2 with the front facing south
(yaw -90°). Bays are centred at x = 0.0, 20.0, 40.0. With SM_SlagPotCarrier the origin
then sits at y ≈ 169.7, and at 140° tip the pot is over the pit.

Spray nozzles: 27 nozzle tips at z = 5.9 m, one per pot (row A from the south
header at y = 106.0, rows B and C from the shared header at y = 145.0), each offset 35 %
of the way toward its pot. Use them as Niagara spray emitter locations.

## Connection points

| Point | Location |
|---|---|
| Pit apron west edge, joins the slag pot pit | x = 50.0, y -2.0 to 30.0, floor z = -5.5 |
| Ramp foot / ramp top | (61.0, 30.0, -5.5) / (61.0, 99.0, 0.0), 8.0 % |
| Spray water supply flange (from pump house) | (-24.0, 106.0, 0.3) |
| Breaking pit floor | x -20.0 to 66.0, y 175.0 to 203.0, z = -3.5 |
| Loader exit ramp top (toward the concentrator ROM bin) | (-55.0, 187.0, 0.0), 10 m wide, heading west |
| Make-up water / power entry (pump house west wall) | (-34.2, 103.0, 0.5) |

## Objects and pivots

All parts are static; YARD_PondWater is a separate object for a water material.

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| YARD_BreakingPit | (-20.00, 175.00, -3.50) |
| YARD_LightMasts | (-20.00, 99.00, 0.00) |
| YARD_Pad | (-20.00, 99.00, 0.00) |
| YARD_PitApronRamp | (56.00, 30.00, -5.50) |
| YARD_PondWater | (-34.00, 110.00, -0.80) |
| YARD_PotStations | (-12.00, 111.00, 0.00) |
| YARD_PumpHouse | (-30.00, 100.00, 0.00) |
| YARD_SettlingPond | (-34.00, 110.00, -3.00) |
| YARD_SprayHeaders | (-12.00, 106.00, 0.00) |
| YARD_TippingStation | (20.00, 175.00, 0.00) |

## Unreal import

Combine Meshes off, Transform Vertex to Absolute on (no moving parts). No UVs are authored; use
world-aligned materials for concrete and steel, and let Unreal generate lightmap UVs if you use
baked lighting. With the default FBX settings Blender +Y appears as Unreal -Y, so the carrier yaws
in the table change sign in Unreal (+90° here = -90° there).

## Dimensions

| Item | Value | Status |
|---|---|---|
| Slag pot pit floor z, pot positions | -5.5; (46.0, 8.8), (46.0, 15.3) | From SM_SlagPots |
| Ramp grade 8.0 %, 10 m wide | | Estimated (typical haul road ramp for a 5.7 m wide carrier) |
| Station pitch 8 m, 5 × 5 m steel set-down plates, aisles 22 m | | Own design, sized to the 9.85 × 5.70 m carrier footprint |
| Air then water-spray cooling, cooling times | 24 h + 48 h | Sourced (Springer 2020 review; US4046323) |
| Spray header height 6.5 m | | Estimated, clears a carrier with a lifted pot (~4.5 m) |
| Tipping wall 3.5 m drop, wear-plated face, 1.0 m wheel stop curb | | Own design (Mount Isa uses steel tipping stations, [S8]) |
| Breaking pit 86 × 28 m, loader ramp 10 % | | Estimated |
| Settling pond 12 × 40 m, two cells | | Own design |
| Light masts 25 m | | Estimated |

Sources: US4046323A (https://patents.google.com/patent/US4046323A/en); "Recovery of copper from
slag" review, Mining, Metallurgy & Exploration 2020 (https://link.springer.com/doi/10.1007/s42461-020-00274-x);
Glencore Kress article [S8] in research/copper-refinery/copper-refinery-equipment.md.

## Files

- SM_SlagCoolingYard.blend / .fbx (REF collection, proxy pots and slag heap are not exported)
- Preview_Overview.png, Preview_Ramp.png, Preview_Tipping.png
