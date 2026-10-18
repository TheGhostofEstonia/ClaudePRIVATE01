# RailVehicles

Rolling stock for the plant railway: a shunting locomotive and four wagon types for concentrate,
flux/reverts, cathode bundles and containers, and sulphuric acid. Each asset is a standalone prop
at its own origin (track centre line, top of rail z = 0, +X = A end), standard gauge 1.435 m, UIC
buffers at 1.06 m and 1.75 m spacing. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_rail_vehicles.py`. Brand names are size references only; the
models carry no logos. In the .blend the bogies, wheelsets, doors and lids are parented to the
body for posing. The REF collection (track, scale figure, sample load, camera, sun) is not exported.

Bogies are separate parts: <prefix>_BogieN_Frame yaws about its centre pivot and carries two
wheelsets. Bogie wheelbase 1.80 m (freight) or 2.40 m (locomotive).

## SM_ShuntingLocomotive

Four-axle diesel-hydraulic road switcher, Vossloh G1206 size class (no branding), for shunting concentrate, acid and cathode trains inside the plant. Origin on the track centre at top of rail under the middle of the locomotive. +X is the short-hood (cab) end.

9 parts, about 6,112 triangles. Previews: Preview_ShuntingLocomotive.png.

### Moving parts

| Part | Motion |
|---|---|
| SL_Body | Root. Moves along the track |
| SL_Bogie1_Frame / SL_Bogie2_Frame | Yaw about local Z in curves (a few degrees) |
| SL_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.50 m: 114.6 degrees per metre travelled |
| SL_CabDoor_L / _R | Swing about local Z: L positive, R negative, about 95° open |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SL_Body | (0.00, 0.00, 0.00) |
| SL_Bogie1_Frame | (3.60, 0.00, 0.75) |
| SL_Bogie1_WS1 | (2.40, 0.00, 0.50) |
| SL_Bogie1_WS2 | (4.80, 0.00, 0.50) |
| SL_Bogie2_Frame | (-3.60, 0.00, 0.75) |
| SL_Bogie2_WS1 | (-4.80, 0.00, 0.50) |
| SL_Bogie2_WS2 | (-2.40, 0.00, 0.50) |
| SL_CabDoor_L | (1.45, 1.52, 1.55) |
| SL_CabDoor_R | (1.45, -1.52, 1.55) |

### Dimensions

| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 14.70 m | Sourced |
| Width over handrails | 3.08 m (deck 3.00 m) | Sourced |
| Height over cab roof | 4.22 m | Sourced |
| Wheel diameter | 1.00 m new | Sourced |
| Bogie centres / bogie wheelbase | 7.20 m / 2.40 m | Sourced, single source |
| Frame top 1.45 m, hood heights 3.55 / 2.90 m, cab position | | Estimated |
| Buffer height 1.06 m, spacing 1.75 m | | UIC standard values |

Sources: [Wikipedia: MaK/Vossloh G1206](https://en.wikipedia.org/wiki/MaK_/_Vossloh_G1206), [Spitzke G 1206 data](https://www.spitzke.com/en/machines/locomotives-railway-wagons/diesel-locomotives/g-1206-series/).

## SM_HopperWagon

Covered four-axle bottom-discharge hopper wagon for copper concentrate (Fals / Tadns size class, no branding). Two funnel hoppers between the bogies empty through flap doors into a track hopper; three roof hatches for loading. Origin on the track centre at top of rail.

14 parts, about 5,548 triangles. Previews: Preview_HopperWagon.png, Preview_HopperWagon_Open.png (doors and hatches open).

### Moving parts

| Part | Motion |
|---|---|
| HW_Body | Root |
| HW_Bogie1_Frame / HW_Bogie2_Frame | Yaw about local Z |
| HW_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: 124.6 degrees per metre |
| HW_Door_1A, HW_Door_2A | Rotate about local Y, +60° opens (downward) |
| HW_Door_1B, HW_Door_2B | Rotate about local Y, -60° opens |
| HW_HatchLid_1..3 | Rotate about local X, -100° opens |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| HW_Body | (0.00, 0.00, 0.00) |
| HW_Bogie1_Frame | (4.00, 0.00, 0.71) |
| HW_Bogie1_WS1 | (3.10, 0.00, 0.46) |
| HW_Bogie1_WS2 | (4.90, 0.00, 0.46) |
| HW_Bogie2_Frame | (-4.00, 0.00, 0.71) |
| HW_Bogie2_WS1 | (-4.90, 0.00, 0.46) |
| HW_Bogie2_WS2 | (-3.10, 0.00, 0.46) |
| HW_Door_1A | (-1.60, 0.00, 0.74) |
| HW_Door_1B | (-0.90, 0.00, 0.74) |
| HW_Door_2A | (0.90, 0.00, 0.74) |
| HW_Door_2B | (1.60, 0.00, 0.74) |
| HW_HatchLid_1 | (-3.50, 0.60, 4.10) |
| HW_HatchLid_2 | (0.00, 0.60, 4.10) |
| HW_HatchLid_3 | (3.50, 0.60, 4.10) |

### Dimensions

| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 12.79 m | Estimated (Fals-class figure from memory, not checked) |
| Body 11.2 x 3.0 m, top 3.95 m above rail (lids 4.13 m); hoppers below the underframe | | Estimated |
| Bogie centres 8.0 m, freight bogie wheelbase 1.80 m | | Estimated |
| Wheel diameter 0.92 m | | Standard freight wheel |
| Volume about 75 m³ gross body; at 25 t axle load the payload is about 75 t | | Estimated |
| Outlets 0.70 x 2.30 m at x = ±1.25, door underside 0.72 m above rail | | Estimated, own design |

Sources: no dimension source found in the time box; proportions follow European ore and mineral hopper wagons.

## SM_SideTipWagon

Four-axle air-operated side-tipping wagon for flux, limestone, reverts and broken slag (own design in the general form of European and US air-dump cars). The body tips to the -Y side about a hinge line along the solebar; the -Y side wall drops as it tips. Origin on the track centre at top of rail.

13 parts, about 5,316 triangles. Previews: Preview_SideTipWagon.png, Preview_SideTipWagon_Tipped.png (body at 45°).

### Moving parts

| Part | Motion |
|---|---|
| ST_Underframe | Root |
| ST_Body | Rotate about local X, 0 to +45° tips to the -Y side |
| ST_DropSide | Child of the body; rotate about local X, 0 to about +75° swings it out and down. Tie it to the body angle (about 1.7 x body angle) |
| ST_TipCyl1/2_Barrel / _Rod | Look-at pair: each half aims local +X at the other's pivot |
| ST_Bogie1_Frame / ST_Bogie2_Frame | Yaw about local Z |
| ST_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: 124.6 degrees per metre |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| ST_Body | (0.00, -1.45, 1.40) |
| ST_Bogie1_Frame | (4.50, 0.00, 0.71) |
| ST_Bogie1_WS1 | (3.60, 0.00, 0.46) |
| ST_Bogie1_WS2 | (5.40, 0.00, 0.46) |
| ST_Bogie2_Frame | (-4.50, 0.00, 0.71) |
| ST_Bogie2_WS1 | (-5.40, 0.00, 0.46) |
| ST_Bogie2_WS2 | (-3.60, 0.00, 0.46) |
| ST_DropSide | (0.00, -1.45, 1.47) |
| ST_TipCyl1_Barrel | (-2.00, 0.60, 0.95) |
| ST_TipCyl1_Rod | (-2.00, 0.75, 1.40) |
| ST_TipCyl2_Barrel | (2.00, 0.60, 0.95) |
| ST_TipCyl2_Rod | (2.00, 0.75, 1.40) |
| ST_Underframe | (0.00, 0.00, 0.00) |

### Dimensions

| Dimension | Value | Status |
|---|---|---|
| Length over buffers 13.5 m, body 12.0 x 2.9 x 1.55 m (about 50 m³ struck) | | Estimated, own design |
| Hinge line y = -1.45, z = 1.40 above rail | | Estimated |
| Bogie centres 9.0 m, wheel 0.92 m | | Estimated / standard |

Sources: none; own design.

## SM_FlatWagon

Four-axle bogie flat wagon, Res class size (no branding), for strapped cathode bundles, rod coils, spares and 20 ft containers. Timber deck, removable stanchions in side pockets, folding end walls, container spigots for three 20 ft boxes. The preview's cathode bundles are REF only. Origin on the track centre at top of rail.

11 parts, about 5,104 triangles. Previews: Preview_FlatWagon.png.

### Moving parts

| Part | Motion |
|---|---|
| FW_Body | Root |
| FW_Stanchions_L / _R | Remove (hide) for container loads; slide along local Z out of the pockets |
| FW_EndWall_A | Rotate about local Y, +90° folds it outward flat |
| FW_EndWall_B | Rotate about local Y, -90° folds it outward flat |
| FW_Bogie1_Frame / FW_Bogie2_Frame | Yaw about local Z |
| FW_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: 124.6 degrees per metre |

Container spigot tops (corner-fitting centres of three 20 ft containers, deck height):

| Spigot (X, Y, Z) |
|---|
| (-9.026, -1.1295, 1.235) |
| (-9.026, 1.1295, 1.235) |
| (-3.173, -1.1295, 1.235) |
| (-3.173, 1.1295, 1.235) |
| (-2.926, -1.1295, 1.235) |
| (-2.926, 1.1295, 1.235) |
| (2.926, -1.1295, 1.235) |
| (2.926, 1.1295, 1.235) |
| (3.173, -1.1295, 1.235) |
| (3.173, 1.1295, 1.235) |
| (9.026, -1.1295, 1.235) |
| (9.026, 1.1295, 1.235) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FW_Body | (0.00, 0.00, 0.00) |
| FW_Bogie1_Frame | (7.43, 0.00, 0.71) |
| FW_Bogie1_WS1 | (6.53, 0.00, 0.46) |
| FW_Bogie1_WS2 | (8.33, 0.00, 0.46) |
| FW_Bogie2_Frame | (-7.43, 0.00, 0.71) |
| FW_Bogie2_WS1 | (-8.33, 0.00, 0.46) |
| FW_Bogie2_WS2 | (-6.53, 0.00, 0.46) |
| FW_EndWall_A | (9.25, 0.00, 1.24) |
| FW_EndWall_B | (-9.25, 0.00, 1.24) |
| FW_Stanchions_L | (0.00, 1.47, 1.24) |
| FW_Stanchions_R | (0.00, -1.47, 1.24) |

### Dimensions

| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 19.90 m | Sourced |
| Bogie centres | 14.86 m | Sourced |
| Deck 18.5 x 2.77 m, deck height 1.235 m | | Estimated (common figures, not confirmed) |
| 20 ft corner fitting centres 5.853 x 2.259 m | | ISO 668 / 1161 values, from memory |
| Stanchions 2.2 m tall at 2.4 m pitch, end walls 0.6 m | | Estimated |

Sources: [TrainsDepot Res-x 679.1](https://www.trainsdepot.org/en/vehicle/2787/res-x679-1), [Đuro Đaković Rens data](https://duro-dakovic.com/en/duro-dakovic-special-vehicles/transport/intermodal-wagons/rens/).

## SM_AcidTankWagon

Four-axle tank wagon for 93-98 % sulphuric acid (own design in the general form of European acid tank wagons, no branding). Carbon-steel tank (concentrated acid does not need a lining), top loading and top discharge only: a dip (eductor) pipe and valve, an air inlet valve and a safety valve around the manway dome, reached by side ladders and a top platform. Origin on the track centre at top of rail.

8 parts, about 7,224 triangles. Previews: Preview_AcidTankWagon.png.

### Moving parts

| Part | Motion |
|---|---|
| AT_Body | Root |
| AT_ManwayLid | Rotate about local Y, -110° opens |
| AT_Bogie1_Frame / AT_Bogie2_Frame | Yaw about local Z |
| AT_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: 124.6 degrees per metre |

Connection points: discharge valve cap at (0.75, 0, 3.87), air inlet at (-0.75, 0, 3.83),
manway at (0, 0, 3.82).

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| AT_Body | (0.00, 0.00, 0.00) |
| AT_Bogie1_Frame | (3.50, 0.00, 0.71) |
| AT_Bogie1_WS1 | (2.60, 0.00, 0.46) |
| AT_Bogie1_WS2 | (4.40, 0.00, 0.46) |
| AT_Bogie2_Frame | (-3.50, 0.00, 0.71) |
| AT_Bogie2_WS1 | (-4.40, 0.00, 0.46) |
| AT_Bogie2_WS2 | (-2.60, 0.00, 0.46) |
| AT_ManwayLid | (-0.36, 0.00, 3.86) |

### Dimensions

| Dimension | Value | Status |
|---|---|---|
| Length over buffers 12.2 m, bogie centres 7.0 m | | Estimated |
| Tank 2.20 m diameter, 8.6 m cylindrical, about 35 m³ | | Estimated |
| Top of tank 3.57 m, top of handrail 4.69 m above rail | | Estimated |

Volume note: concentrated acid weighs about 1.83 t/m³, so a 90 t (22.5 t axle load) wagon carries
about 60-65 t, which is only about 35 m³. Acid wagons are therefore small for their weight; the
60-80 m³ class is for lighter products and would be overloaded with acid.

Sources: density of sulphuric acid (standard value); wagon dimensions estimated.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
