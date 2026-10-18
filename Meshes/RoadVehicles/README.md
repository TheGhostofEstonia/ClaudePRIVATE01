# RoadVehicles

Road vehicles for plant logistics: inbound concentrate, flux and reagents, outbound cathode,
acid and slimes. Each asset is a standalone prop at its own origin (not tied to the plant
layout). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_road_vehicles.py`. Brand names are size references only; the models
carry no logos. In the .blend the moving parts are parented for posing.

Coupling rule: the tractor's origin is the ground point under its fifth-wheel centre, and each
semi-trailer's origin is the ground point under its kingpin. Placing a trailer at the tractor's
origin couples it (fifth-wheel top and kingpin rubbing plate both at z = 1.20 m). For a turning
combination, rotate the trailer about the vertical axis through that point.

## SM_TractorUnit

Three-axle 6x4 semi-trailer tractor (European cab-over-engine, no branding). Origin is the ground
point under the fifth-wheel centre (kingpin lock). +X is the cab end. Every semi-trailer in this
folder uses the same origin rule, so a coupled trailer is placed at the tractor's origin with the
same rotation; when articulating, rotate the trailer about the vertical line through
(0, 0, 1.20).

13 parts, about 5,184 triangles. Previews: Preview_TractorUnit.png.

### Moving parts

| Part | Motion |
|---|---|
| TU_Wheel_A1L/R | Spin about local Y and steer about local Z (front axle) |
| TU_Wheel_A2*, A3* | Spin about local Y (twin tyres, drive axles) |
| All wheels | Tyre circumference 3.38 m: 106.5°/m travelled |
| TU_Door_L | Hinge on the front edge: rotate about local Z, negative opens (about -70°) |
| TU_Door_R | Same hinge, positive opens (about +70°) |

Coupling: fifth-wheel top at (0, 0, 1.20); the throat opens to the rear (-X).

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| TU_Chassis | (0.00, 0.00, 0.00) |
| TU_Door_L | (4.60, 1.25, 1.35) |
| TU_Door_R | (4.60, -1.25, 1.35) |
| TU_Wheel_A1L | (3.53, 1.04, 0.54) |
| TU_Wheel_A1R | (3.53, -1.04, 0.54) |
| TU_Wheel_A2L | (0.22, 1.04, 0.54) |
| TU_Wheel_A2L2 | (0.22, 0.69, 0.54) |
| TU_Wheel_A2R | (0.22, -1.04, 0.54) |
| TU_Wheel_A2R2 | (0.22, -0.69, 0.54) |
| TU_Wheel_A3L | (-1.12, 1.04, 0.54) |
| TU_Wheel_A3L2 | (-1.12, 0.69, 0.54) |
| TU_Wheel_A3R | (-1.12, -1.04, 0.54) |
| TU_Wheel_A3R2 | (-1.12, -0.69, 0.54) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Width 2.49 m cab, 2.50 m over tyres | EU limit 2.55 m | Limit sourced (Directive 96/53/EC); body estimated |
| Height 3.90 m over roof deflector | EU limit 4.00 m | Limit sourced; model estimated |
| Length 6.95 m, wheelbase 3.30 m + 1.35 m tandem | | Estimated (typical 6x4 tractor) |
| Fifth-wheel height 1.20 m, lead 0.45 m ahead of bogie centre | | Estimated (typical 1.15-1.25 m) |
| Cab back to kingpin 2.55 m | ≥ 2.04 m trailer front swing radius | Radius sourced (96/53/EC); clearance follows |
| Tyres 315/80R22.5, 1.076 m diameter | | Sourced from the tyre size code |

Sources: Council Directive 96/53/EC (maximum dimensions); ISO tyre size designation

## SM_TipperTrailer

Three-axle steel tipping semi-trailer, front-tip telescopic hoist, for concentrate, silica flux,
limestone and granulated slag. Origin is the ground point under the kingpin (see SM_TractorUnit);
kingpin at (0, 0, 1.20). +X is the front. The preview stands on its landing legs.

16 parts, about 4,420 triangles. Previews: Preview_TipperTrailer.png, Preview_TipperTrailer_Tipped.png.

### Moving parts

| Part | Motion |
|---|---|
| TT_Body | Tips about local Y at the rear hinge (-7.95, 0, 1.45); negative raises the front, about -45° to empty |
| TT_Tailgate | Child of the body, hinge at the top: positive swings the bottom out (+60° in the preview; keep it near vertical in world while tipping) |
| TT_Hoist_Stage1..6 | Telescopic cylinder from (1.15, 0, 1.35) to the body pin (1.15, 0, 3.00) when lowered. Aim each stage's local +X at the body pin's world position; stage i (1-6) slides (i-1)/5 of the extension along +X. Fully tipped the cylinder is about 8.5 m long |
| TT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
| TT_Wheel_* | Spin about local Y; 106.9°/m travelled |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| TT_Body | (-7.95, 0.00, 1.45) |
| TT_Chassis | (0.00, 0.00, 0.00) |
| TT_Hoist_Stage1 | (1.15, 0.00, 1.35) |
| TT_Hoist_Stage2 | (1.15, 0.00, 1.35) |
| TT_Hoist_Stage3 | (1.15, 0.00, 1.35) |
| TT_Hoist_Stage4 | (1.15, 0.00, 1.35) |
| TT_Hoist_Stage5 | (1.15, 0.00, 1.35) |
| TT_Hoist_Stage6 | (1.15, 0.00, 1.35) |
| TT_LandingLegs | (-2.30, 0.00, 0.00) |
| TT_Tailgate | (-7.99, 0.00, 2.75) |
| TT_Wheel_A1L | (-4.99, 1.07, 0.54) |
| TT_Wheel_A1R | (-4.99, -1.07, 0.54) |
| TT_Wheel_A2L | (-6.30, 1.07, 0.54) |
| TT_Wheel_A2R | (-6.30, -1.07, 0.54) |
| TT_Wheel_A3L | (-7.61, 1.07, 0.54) |
| TT_Wheel_A3R | (-7.61, -1.07, 0.54) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Kingpin height 1.20 m, 2 in (50.8 mm) kingpin | | Kingpin size sourced (ISO 337); height estimated |
| Kingpin to rear 9.30 m, width 2.50 m, height 3.05 m | EU limits 12.0 m / 2.55 m / 4.0 m | Limits sourced (96/53/EC); model estimated |
| Body 8.9 × 2.5 × 1.3 m, ~27 m³ struck | | Estimated. At 2.0-2.4 t/m³ (concentrate) a ~27 t payload fills only about half of it; flux and slag are lighter |
| Axles 3 × 1.31 m spacing, 385/65R22.5 tyres | | Spacing typical (estimated); tyre size sourced |
| Tip angle 45°, six-stage front hoist | | Estimated |

Sources: Directive 96/53/EC; ISO 337 (kingpin); tyre size code

## SM_FlatbedTrailer

13.6 m three-axle flatbed semi-trailer with a timber deck, stake pockets and fixed container
twistlocks, for cathode bundles, rod coils, spares and containers. Origin is the ground point under
the kingpin (0, 0, 1.20 kingpin height). +X is the front. The preview shows the tractor
(SM_TractorUnit, REF copy) coupled and twelve REF cathode bundles.

8 parts, about 4,216 triangles. Previews: Preview_FlatbedTrailer.png.

### Moving parts

| Part | Motion |
|---|---|
| FT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
| FT_Wheel_* | Spin about local Y; 106.9°/m travelled |

Deck top z = 1.55. Twistlock centres (one 40 ft, or two 20 ft 76 mm apart; the outer four serve both):

| Twistlock (X, Y, Z) |
|---|
| (-11.877, 1.129, 1.55) |
| (-11.877, -1.129, 1.55) |
| (-6.024, 1.129, 1.55) |
| (-6.024, -1.129, 1.55) |
| (-5.744, 1.129, 1.55) |
| (-5.744, -1.129, 1.55) |
| (0.110, 1.129, 1.55) |
| (0.110, -1.129, 1.55) |

Suggested cathode-bundle grid, 2 across × 6 rows (12 bundles ≈ 24 t), bundle centres (X, Y) on the
deck: (-1.95, 0.6), (-1.95, -0.6), (-3.25, 0.6), (-3.25, -0.6), (-4.55, 0.6), (-4.55, -0.6), (-5.85, 0.6), (-5.85, -0.6), (-7.15, 0.6), (-7.15, -0.6), (-8.45, 0.6), (-8.45, -0.6). The rows sit between the kingpin and the axles so the load is shared. Bundles are
strapped down through the stake pockets.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FT_Chassis | (0.00, 0.00, 0.00) |
| FT_LandingLegs | (-2.30, 0.00, 0.00) |
| FT_Wheel_A1L | (-6.39, 1.07, 0.54) |
| FT_Wheel_A1R | (-6.39, -1.07, 0.54) |
| FT_Wheel_A2L | (-7.70, 1.07, 0.54) |
| FT_Wheel_A2R | (-7.70, -1.07, 0.54) |
| FT_Wheel_A3L | (-9.01, 1.07, 0.54) |
| FT_Wheel_A3R | (-9.01, -1.07, 0.54) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Length 13.60 m, kingpin to rear 12.00 m, front radius 1.60 m | EU limits 12.0 m and 2.04 m | Limits sourced (96/53/EC); model at the limit |
| Width 2.50 m, deck height 1.55 m | | Estimated (typical 1.45-1.60 m) |
| Twistlock layout | ISO 1161 casting centres 5.853 / 11.985 × 2.259 m | Sourced |
| Cathode bundle 1.016 × 0.915 m sheets, 30 per bundle ≈ 2.0 t | | From the project's cathode size (Meshes/CathodeBundlingLine) |
| Payload ~24-28 t | | Estimated (40-44 t gross combination) |

Sources: Directive 96/53/EC; ISO 1161 / ISO 668 (container fittings); tyre size code

## SM_AcidTankTrailer

Three-axle sulphuric acid tank semi-trailer: a small-diameter stainless (or rubber-lined steel)
barrel because concentrated acid is dense, top manway with loading and vent valves, top walkway
with a fold-down handrail, rear ladder and a rear valve cabinet over the bottom outlet. Origin is
the ground point under the kingpin (kingpin at (0, 0, 1.20)). +X is the front.

13 parts, about 5,464 triangles. Previews: Preview_AcidTankTrailer.png.

### Moving parts

| Part | Motion |
|---|---|
| AT_ManwayLid | Hinge on its -X edge: rotate about local Y, negative opens (about -110°) |
| AT_Handrail | Raised in the model; fold flat by rotating about local X by about 90° (road travel) |
| AT_ValveCabinetDoor | Hinge on the left (+Y) edge: rotate about local Z, positive opens |
| AT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
| AT_Wheel_* | Spin about local Y; 106.9°/m travelled |

Loading point: manway / top loading valve at (-3.65, 0, 3.30). Unloading point:
bottom outlet in the valve cabinet, (-8.05, 0, 1.50).

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| AT_Chassis | (0.00, 0.00, 0.00) |
| AT_Handrail | (-3.65, 0.24, 3.17) |
| AT_LandingLegs | (-2.30, 0.00, 0.00) |
| AT_ManwayLid | (-3.93, 0.00, 3.27) |
| AT_Tank | (0.00, 0.00, 0.00) |
| AT_ValveCabinet | (0.00, 0.00, 0.00) |
| AT_ValveCabinetDoor | (-8.80, 0.60, 0.85) |
| AT_Wheel_A1L | (-5.70, 1.07, 0.54) |
| AT_Wheel_A1R | (-5.70, -1.07, 0.54) |
| AT_Wheel_A2L | (-7.01, 1.07, 0.54) |
| AT_Wheel_A2R | (-7.01, -1.07, 0.54) |
| AT_Wheel_A3L | (-8.32, 1.07, 0.54) |
| AT_Wheel_A3R | (-8.32, -1.07, 0.54) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Tank 1.60 m diameter × 8.5 m over heads, ≈17.7 m³ gross | | Estimated |
| Payload check: 98 % H2SO4 is about 1.84 t/m³, so 17.7 m³ ≈ 33 t | | Density sourced (standard value); payload estimated, near a 40-44 t combination limit |
| Height 3.95 m over the raised handrail (3.15 m folded at the tank top) | EU limit 4.0 m | Estimated |
| Kingpin to rear 8.9 m | | Estimated |

Sources: Directive 96/53/EC; sulphuric acid density (CRC Handbook value, 98 % ≈ 1.84 g/cm³)

## SM_Container20ft

ISO 668 type 1CC 20 ft dry freight container with corrugated walls, corner castings, forklift
pockets and two hinged doors at the -X end. Origin is the ground point under the centre of the
container (bottom of the corner castings at z = 0). It fits the twistlocks of SM_FlatbedTrailer
(corner castings at ±2.9265 m along X, ±1.1295 m along Y from the origin).

3 parts, about 1,288 triangles. Previews: Preview_Container20ft.png.

### Moving parts

| Part | Motion |
|---|---|
| C20_Door_L (+Y leaf) | Hinge on the outer edge: rotate about local Z, negative opens, up to -270° flat against the side |
| C20_Door_R (-Y leaf) | Same, positive opens, up to +270° |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| C20_Body | (0.00, 0.00, 0.00) |
| C20_Door_L | (-3.05, 1.16, 0.25) |
| C20_Door_R | (-3.05, -1.16, 0.25) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| External 6.058 × 2.438 × 2.591 m | | Sourced (ISO 668, 1CC) |
| Corner castings 178 × 162 × 118 mm, centres 5.853 × 2.259 m | | Sourced (ISO 1161) |
| Max gross 30.48 t (newer ratings 36 t), tare ≈2.2 t | | Sourced (ISO 668 rating); tare typical |
| Corrugation pitch 0.278 m, forklift pockets at ±1.03 m | | Estimated |

Sources: ISO 668 (series 1 freight containers); ISO 1161 (corner fittings)

## SM_FlatbedTruck

Rigid 6x2 drop-side flatbed truck (day cab, rear tag axle) for in-plant moves of spares, cathode
bundles and pallets. Origin is the ground point at the middle of the chassis. +X is the cab end.
Deck 7.4 × 2.48 m, top at z = 1.40; room for 2 × 6 cathode bundles by area, but the payload
(about 14 t) limits it to about 6-7 bundles.

16 parts, about 4,116 triangles. Previews: Preview_FlatbedTruck.png.

### Moving parts

| Part | Motion |
|---|---|
| FB_DropSide_L1/L2 | Hinge on the bottom edge: rotate about local X, negative drops the side outward (about -100°) |
| FB_DropSide_R1/R2 | Same, positive drops outward |
| FB_Tailgate | Hinge on the bottom edge: rotate about local Y, negative drops it rearward |
| FB_Door_L / _R | Cab doors, hinge at the front edge: rotate about local Z, L negative, R positive |
| FB_Wheel_A1L/R | Spin and steer (local Z) |
| All wheels | Spin about local Y, 106.5°/m. A3 (tag) can be lifted 0.15 m along Z when empty |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FB_Chassis | (0.00, 0.00, 0.00) |
| FB_Door_L | (4.60, 1.25, 1.35) |
| FB_Door_R | (4.60, -1.25, 1.35) |
| FB_DropSide_L1 | (0.81, 1.24, 1.40) |
| FB_DropSide_L2 | (-2.85, 1.24, 1.40) |
| FB_DropSide_R1 | (0.81, -1.24, 1.40) |
| FB_DropSide_R2 | (-2.85, -1.24, 1.40) |
| FB_Tailgate | (-4.70, 0.00, 1.40) |
| FB_Wheel_A1L | (3.50, 1.04, 0.54) |
| FB_Wheel_A1R | (3.50, -1.04, 0.54) |
| FB_Wheel_A2L | (-1.60, 1.04, 0.54) |
| FB_Wheel_A2L2 | (-1.60, 0.69, 0.54) |
| FB_Wheel_A2R | (-1.60, -1.04, 0.54) |
| FB_Wheel_A2R2 | (-1.60, -0.69, 0.54) |
| FB_Wheel_A3L | (-2.95, 1.04, 0.54) |
| FB_Wheel_A3R | (-2.95, -1.04, 0.54) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Length 9.85 m, width 2.50 m, cab height 3.20 m | | Estimated (typical 26 t 6x2 rigid) |
| Deck 7.4 × 2.48 m at 1.40 m, drop sides 0.60 m | | Estimated |
| Gross 26 t, payload ≈14 t | EU 3-axle rigid 26 t (with drive-axle conditions) | Limit sourced (96/53/EC); payload estimated |
| Tyres 315/80R22.5 | | Sourced from the size code |

Sources: Directive 96/53/EC

## SM_SecureVan

Armoured cash-in-transit style truck on a two-axle 7.5-12 t chassis, for moving anode slimes,
doré bars and precious-metal samples under security. Plain armour grey, no branding. Armoured
body with small windows, gun ports, roof camera dome and hatch, rear double doors and a crew door
on the right. Origin is the ground point at the middle of the vehicle. +X is the cab end.

10 parts, about 3,428 triangles. Previews: Preview_SecureVan.png.

### Moving parts

| Part | Motion |
|---|---|
| SV_RearDoor_L (+Y leaf) | Hinge on the outer edge: rotate about local Z, negative opens (up to about -180°) |
| SV_RearDoor_R (-Y leaf) | Same, positive opens |
| SV_SideDoor | Hinge on the front edge: rotate about local Z, positive opens outward (about +90°) |
| SV_Wheel_A1L/R | Spin and steer (local Z) |
| All wheels | 265/70R19.5, spin about local Y, 132.3°/m |

Cab doors are modelled closed (part of SV_Chassis).

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SV_Chassis | (0.00, 0.00, 0.00) |
| SV_RearDoor_L | (-3.80, 1.18, 1.05) |
| SV_RearDoor_R | (-3.80, -1.18, 1.05) |
| SV_SideDoor | (1.20, -1.20, 1.05) |
| SV_Wheel_A1L | (2.50, 0.95, 0.43) |
| SV_Wheel_A1R | (2.50, -0.95, 0.43) |
| SV_Wheel_A2L | (-1.40, 0.98, 0.43) |
| SV_Wheel_A2L2 | (-1.40, 0.62, 0.43) |
| SV_Wheel_A2R | (-1.40, -0.98, 0.43) |
| SV_Wheel_A2R2 | (-1.40, -0.62, 0.43) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Length 7.75 m, width 2.40 m, height 3.25 m (3.45 m over the dome) | | Estimated (typical 12 t CIT truck) |
| Wheelbase 3.90 m, 265/70R19.5 tyres | | Estimated; tyre diameter from the size code |
| Gun ports, window sizes, door layout | | Own design |

Sources: no specific vehicle; general CIT truck proportions

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
