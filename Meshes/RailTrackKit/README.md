# RailTrackKit

Modular standard-gauge track for the plant railway (concentrate wagons, acid tank wagons, cathode
flat wagons, ladle and anode transfer cars). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_rail_track.py`. Each piece is its own .blend/.fbx.

Conventions for every piece: origin on the track centre line at top of rail (z = 0) at the start
of the piece; the piece runs along +X. Formation (bottom of ballast) is at z = -0.65, so place the
pieces with their origin 0.65 m above the ground surface, or sink the ground under the ballast.
Each piece has a `_Track` mesh (rails, sleepers, clips) and a `_Ballast` mesh. The ballast has
UVs in metres (U along the track, V across the ballast surface), so a tiling ballast material
with 1 UV = 1 m lines up across pieces. Rails have no UVs (use a triplanar or world-aligned steel
material). Ends are open; pieces join end to end without caps.

## SM_Track_Straight_10m

Straight track, 10.0 m.

Connection: start (0, 0, 0) heading +X; end (10.00, 0, 0) heading +X.

2 parts, about 1,236 triangles. Previews: Preview_TrackKit.png.

### Moving parts

None.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_Track_Straight_10m_Ballast | (0.00, 0.00, 0.00) |
| SM_Track_Straight_10m_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |

Sources: rail profile from UIC 60 nominal dimensions; everything else estimated.

## SM_Track_Straight_2m5

Straight track, 2.5 m.

Connection: start (0, 0, 0) heading +X; end (2.50, 0, 0) heading +X.

2 parts, about 294 triangles. Previews: Preview_TrackKit.png.

### Moving parts

None.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_Track_Straight_2m5_Ballast | (0.00, 0.00, 0.00) |
| SM_Track_Straight_2m5_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |

Sources: rail profile from UIC 60 nominal dimensions; everything else estimated.

## SM_Track_Curve_R190_15deg

190 m radius curve through 15 degrees to the left (+Y), arc length 49.74 m on the centre line. No cant (plant speeds). Use it mirrored (scale Y -1) for a right-hand curve.

Connection: start (0, 0, 0) heading +X; end (49.176, 6.474, 0) heading 15.0 deg (rotate the next piece by +15 deg about Z).

2 parts, about 7,680 triangles. Previews: Preview_TrackKit.png.

### Moving parts

None.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_Track_Curve_R190_15deg_Ballast | (0.00, 0.00, 0.00) |
| SM_Track_Curve_R190_15deg_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |
| Radius | 190 m (common minimum for standard-gauge sidings) | Estimated |

Sources: estimated.

## SM_Turnout_1to9_Left

Left-hand 1:9 turnout. The diverging route leaves to +Y. Bearers lengthen to carry both routes. A point machine sits on the right side at the toe. Mirror (scale Y -1) for a right-hand turnout and swap the blade signs.

Connection: start (0, 0, 0) heading +X; end straight route (33.13, 0, 0) heading 0 deg; diverging route (33.13, 1.835, 0) heading 6.34 deg.

4 parts, about 6,796 triangles. Previews: Preview_TrackKit.png.

### Moving parts

| Part | Motion |
|---|---|
| SM_Turnout_1to9_Left_SwitchBlade_L | Straight blade beside the left stock rail. Rotates about local Z at its heel. Straight route: 0 deg (closed). Diverging route: +0.764 deg (toe moves 0.16 m toward -Y, open) |
| SM_Turnout_1to9_Left_SwitchBlade_R | Curved blade beside the right stock rail. Straight route (as exported): -0.764 deg (toe 0.16 m open toward +Y). Diverging route: 0 deg (closed) |

Throw the two blades together; one is always closed. The exported file is set for the straight route.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_Turnout_1to9_Left_Ballast | (0.00, 0.00, 0.00) |
| SM_Turnout_1to9_Left_SwitchBlade_L | (12.00, 0.75, 0.00) |
| SM_Turnout_1to9_Left_SwitchBlade_R | (11.74, -0.52, 0.00) |
| SM_Turnout_1to9_Left_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |
| Diverging radius | 300 m, held until the 1:9 angle (6.34 deg) | Estimated after the common EW 60-300-1:9 type |
| Length | 33.13 m (EW 60-300-1:9 is about 33.2 m long, from memory, unverified) | Estimated |
| Switch blades | 12.0 m, throw 0.16 m at the toe | Estimated |
| Frog | crossing point at x = 30.07 m; modelled as crossing rails on a cast block, no flangeway cut-outs | Simplified |

Sources: estimated; see the dimensions table.

## SM_BufferStop

5 m of track ending in a fixed friction-free buffer stop. Buffer faces at x = 2.0, centres at y +-0.875, z 1.06 (matches the UIC buffers on the rail vehicles).

Connection: start (0, 0, 0) heading +X; end none (dead end); track continues to x = 5.0 under the frame.

3 parts, about 1,016 triangles. Previews: Preview_TrackKit.png.

### Moving parts

None.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_BufferStop_Ballast | (0.00, 0.00, 0.00) |
| SM_BufferStop_Stop | (0.00, 0.00, 0.00) |
| SM_BufferStop_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |
| Stop frame | beam 2.6 m wide, struts to rail clamps 2.6 m long | Estimated |

Sources: estimated.

## SM_LevelCrossingPanel

10 m of track (the road runs across it, along Y) with four 2.5 m bays of concrete panels flush with the rail top: gauge panels between the rails and 1.2 m outer panels. Road surface level z = -0.005; the road must meet the outer panel edges at y = +-2.0.

Connection: start (0, 0, 0) heading +X; end (10.00, 0, 0) heading +X.

3 parts, about 1,524 triangles. Previews: Preview_TrackKit.png.

### Moving parts

None.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SM_LevelCrossingPanel_Ballast | (0.00, 0.00, 0.00) |
| SM_LevelCrossingPanel_Panels | (0.00, 0.00, 0.00) |
| SM_LevelCrossingPanel_Track | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |
| Panels | 2.5 m bays, 70 mm flangeways, outer panels 1.2 m | Estimated |

Sources: estimated.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
