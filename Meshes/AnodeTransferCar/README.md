# AnodeTransferCar

Rail anode transfer car between the anode casting / stacking area and the tankhouse service bay.
Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_plant_rail_cars.py`.
Runs on the RailTrackKit track (standard gauge, top of rail z = 0). Vehicle at its own origin, not
placed in the plant layout; a track into the service bay (doors 6 x 6 m, Meshes/Tankhouse/README.md)
is needed to use it there.

## SM_AnodeTransferCar

Battery-electric rail transfer car that carries cast anodes from the casting wheel / anode stacking area to the tankhouse service bay. Three stack seats, each a pair of lug rails at the lug line (y +-0.60) with yellow end guides: a forklift or crane sets a stack of 20 anodes hanging face to face by their lugs, the same way the anode preparation machine infeed takes them. Anode as in the tankhouse set: 1.00 x 1.00 x 0.045 m body, lugs to a 1.32 m span (45 mm is still the working thickness; T has not decided on thinning). Operator platform and radio/pedestal control at the A end (+X). Own design. One REF stack (not exported) sits on the middle seat in the .blend.

Stack seats (lug underside, stack centre):

| Seat | Centre (x, y, z) | Stack extent along X |
|---|---|---|
| Stack 1 | (-1.75, 0.00, 2.15) | x -2.25 to -1.25 |
| Stack 2 | (0.00, 0.00, 2.15) | x -0.50 to 0.50 |
| Stack 3 | (1.75, 0.00, 2.15) | x 1.25 to 2.25 |

Load: 3 x 20 anodes x about 415 kg = about 25 t. Highest point loaded: z 2.50 (guides), width 2.9 m over the platform, well inside the 6 x 6 m tankhouse service bay doors.

7 parts, about 4,956 triangles. Previews: Preview_AnodeTransferCar.png.

### Moving parts

| Part | Motion |
|---|---|
| ATC2_Body | Travels along X; parent of the bogies in the .blend |
| ATC2_Bogie1/2_Frame | Yaw about local Z in curves |
| ATC2_Bogie*_WS1/WS2 | Spin about local Y: 124.6 deg per metre travelled |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| ATC2_Body | (0.00, 0.00, 0.00) |
| ATC2_Bogie1_Frame | (1.90, 0.00, 0.71) |
| ATC2_Bogie1_WS1 | (1.00, 0.00, 0.46) |
| ATC2_Bogie1_WS2 | (2.80, 0.00, 0.46) |
| ATC2_Bogie2_Frame | (-1.90, 0.00, 0.71) |
| ATC2_Bogie2_WS1 | (-2.80, 0.00, 0.46) |
| ATC2_Bogie2_WS2 | (-1.00, 0.00, 0.46) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge, buffers | 1.435 m; buffers 1.75 m apart at z 1.06 | Standard / UIC |
| Length over buffers | 7.50 m, frame 2.8 m wide | Estimated |
| Deck top / lug seat | z 1.20 / z 2.15 (anode bottoms clear the deck by 0.07 m) | Estimated |
| Wheels | 920 mm, bogies at x +-1.9 | Estimated |
| Anode | 1.00 x 1.00 x 0.045 m, lug span 1.32 m, about 415 kg | From the tankhouse set (th_layout.py) |
| Stack | 20 anodes at 50 mm pitch = 1.00 m | Stack count from the anode set; pitch estimated |

Sources: own design; anode sizes from the project's tankhouse set.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
