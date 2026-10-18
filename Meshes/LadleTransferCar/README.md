# LadleTransferCar

Rail ladle transfer car for the converter aisle. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_plant_rail_cars.py`. Runs on the RailTrackKit track (standard gauge,
top of rail z = 0). Vehicle at its own origin, not placed in the plant layout. In the .blend the
moving parts are parented to LTC_Body for posing.

## SM_LadleTransferCar

Self-propelled rail ladle car for the converter aisle: carries a matte or blister copper ladle between the furnace tapping launders and the converter-aisle crane. Electric drive fed from a cable reel at the A end (+X); two four-wheel bogies; UIC buffers so the plant locomotive can shunt it. The ladle is a separate part that the converter-aisle crane lifts by its two trunnions (along Y) and pours by lifting the tipping lug on the -X side with the auxiliary hook. Slag pots use the existing straddle carrier (Meshes/SlagPotCarrier), not this car.

Ladle: 9.8 m3 brim-full, 9.0 m3 working. Loaded with 9.0 m3 of matte at about 5 t/m3 that is about 45 t of matte (blister copper at about 7.8 t/m3 would be about 70 t, so fill blister ladles to about 6 m3). Own design. Origin: track centre, top of rail, under the ladle centre.

10 parts, about 6,692 triangles. Previews: Preview_LadleTransferCar.png, Preview_LadleTransferCar_LidOpen.png.

### Moving parts

| Part | Motion |
|---|---|
| LTC_Body | Travels along X. Parent of everything else in the .blend |
| LTC_Bogie1/2_Frame | Yaw about local Z in curves |
| LTC_Bogie*_WS1/WS2 | Spin about local Y: 124.6 deg per metre travelled |
| LTC_CableReel | Spins about local Y as the car travels (pays out / winds the trailing cable) |
| LTC_Ladle | Lifted off by the crane; pivot on the trunnion axis (z 2.85), tilt about local Y to pour toward +X |
| LTC_Lid | Hinge on the -X rim; rotate about local Y, -100 deg = open (preview 2) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| LTC_Body | (0.00, 0.00, 0.00) |
| LTC_Bogie1_Frame | (2.10, 0.00, 0.71) |
| LTC_Bogie1_WS1 | (1.20, 0.00, 0.46) |
| LTC_Bogie1_WS2 | (3.00, 0.00, 0.46) |
| LTC_Bogie2_Frame | (-2.10, 0.00, 0.71) |
| LTC_Bogie2_WS1 | (-3.00, 0.00, 0.46) |
| LTC_Bogie2_WS2 | (-1.20, 0.00, 0.46) |
| LTC_CableReel | (2.85, 0.75, 2.50) |
| LTC_Ladle | (0.00, 0.00, 2.85) |
| LTC_Lid | (-1.82, 0.00, 3.60) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge, buffers | 1.435 m; buffers 1.75 m apart at z 1.06 | Standard / UIC |
| Wheels | 920 mm, two bogies at x +-2.1, wheelbase 1.8 m | Estimated |
| Length over buffers | 8.70 m; frame width 3.0 m | Estimated |
| Deck top | z 1.20 | Estimated |
| Ladle | inner 2.90 / 2.20 m diameter, 1.90 m deep; outer 3.40 m top, 2.15 m tall; 9.8 m3 full | Estimated (own design) |
| Trunnion axis | z 2.85, trunnion ends at y +-2.19 | Estimated |
| Top of ladle rim / lid | z 3.55 / about z 3.78 | Estimated |
| Mass (estimated) | car about 25 t, empty lined ladle about 20 t, 45 t matte: about 90 t total, 22.5 t axle load | Estimated |
| Matte density | about 5 t/m3 | Typical (brief) |

Sources: no sourced ladle dimensions found; historical converter-aisle descriptions mention ladles of 10 t and more (https://www.911metallurgist.com/blog/smelter-slags-mattes/). Everything here is an own design.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
