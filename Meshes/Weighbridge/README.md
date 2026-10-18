# Weighbridge

Road weighbridge for all trucks entering or leaving the plant.

## About

Surface-mounted (pitless) road weighbridge for inbound concentrate, flux and reagent trucks and
outbound cathode, acid and slag trucks. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_weighbridge_sampling.py`. The layout is an own design.

Origin: ground level (z 0) at the centre of the deck. Trucks drive in +X (entry at -X). The booth,
traffic lights, barriers and RFID post sit on the driver's side (-Y).

11 parts, about 2,056 triangles. Previews: Preview_Overview.png, Preview_Entry.png
(entry barrier raised). REF holds a 16.5 m articulated-truck block (hidden in the renders), a
1.8 m figure and a ground slab with the weighbridge footprint left open.

## Moving parts

| Part | Motion |
|---|---|
| WB_BarrierArm_Entry / _Exit | Rotate about local X at the hinge. Closed = 0°, open = +85° (arm tips up). Arm spans +Y across the lane |
| WB_Deck | Static. Separate so a material or decal can mark it; the real deflection under load is a few mm |
| WB_TrafficLights | Static. Red and green lamps are separate material slots (M_Lamp_Red / M_Lamp_Green): swap the emissive strength in Unreal to switch |

## Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| WB_BarrierArm_Entry | (-13.50, -2.15, 0.90) |
| WB_BarrierArm_Exit | (13.50, -2.15, 0.90) |
| WB_BarrierHousing_Entry | (0.00, 0.00, 0.00) |
| WB_BarrierHousing_Exit | (0.00, 0.00, 0.00) |
| WB_BarrierRest_Entry | (0.00, 0.00, 0.00) |
| WB_BarrierRest_Exit | (0.00, 0.00, 0.00) |
| WB_Booth | (0.00, 0.00, 0.00) |
| WB_Deck | (0.00, 0.00, 0.00) |
| WB_Foundation | (0.00, 0.00, 0.00) |
| WB_RFIDPost | (0.00, 0.00, 0.00) |
| WB_TrafficLights | (0.00, 0.00, 0.00) |

Load cells (inside WB_Foundation):

| Item | Position |
|---|---|
| Load cell 1 | (-8.40, 1.15, 0.05) |
| Load cell 2 | (-8.40, -1.15, 0.05) |
| Load cell 3 | (-3.00, 1.15, 0.05) |
| Load cell 4 | (-3.00, -1.15, 0.05) |
| Load cell 5 | (3.00, 1.15, 0.05) |
| Load cell 6 | (3.00, -1.15, 0.05) |
| Load cell 7 | (8.40, 1.15, 0.05) |
| Load cell 8 | (8.40, -1.15, 0.05) |

## Footprint and connection points

| Item | Value |
|---|---|
| Footprint incl. ramps and barriers | x -13.8 to 13.8, y -5.3 to 2.1 |
| Lane entry (road joins here, z 0) | (-14.5, 0.0, 0.0), heading +X |
| Lane exit | (14.5, 0.0, 0.0), heading +X |
| Lane width on the deck | 3.0 m between kerb guides (3.3 m between kerb centres) |
| Deck top | z 0.35, x -9.0 to 9.0 |
| Booth door | (-1.50, -3.90, 0.15), opens toward -X |
| Barrier hinge lines | x -13.5 (entry), x 13.5 (exit) |

## Dimensions

| Item | Value | Status |
|---|---|---|
| Deck | 18 x 3 m, 3 modules, 8 load cells | Sourced size class: 18 x 3 m, 3 modules with 8 weigh bars, about 100 t ([Avery Weigh-Tronix BMS spec](https://secure.averyweigh-tronix.com/en/wp-content/uploads/sites/5/2021/11/bridgemont-bms_spec_uk500291.pdf)); 18 x 3 m is listed at 80-120 t with 8 or 10 cells ([Sri Lanka Measurement Units dept.](https://measurementsdept.gov.lk/images/Pattern_Approval-Download/WEIGHBRIDGE_REQUIREMENTS/WEB_WEIGHBRIDGE_REQUIREMENTS.pdf)) |
| Ramp gradient | 1:8.6 (3.0 m long) | Sourced limit: ramps no steeper than 1:8 (same Sri Lanka note); length estimated |
| Deck top height | 0.35 m | Estimated; real height depends on the load-cell mounting |
| Booth 3.0 x 2.4 x 2.7 m, barrier arm 4.2 m at 0.9 m | | Estimated |
| Traffic light head 3.2 m | | Estimated |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
