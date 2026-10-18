# FluxStorage

Covered flux, limestone and reverts storage with loader hopper and belt.

Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_utilities.py`.
Fixed facility at its own origin (ground at the footprint centre, +X east, +Y north), not placed
in the plant layout. All layouts are Claude's own designs; dimensions are estimated unless the
table says otherwise.

## SM_FluxStorage

Covered storage for smelter flux and other bought-in solids: three loader bays (silica flux,
limestone, reverts) with 4 m concrete push walls under a steel monopitch roof, open to the south
for front-end loaders and trucks. A loader tips into a ground hopper with a grizzly east of the
bays; an inclined 1.0 m belt (troughed, continuous UVs, 1 UV = 1.2 m, belt loop
69.7 m) lifts it to a transfer tower, where it can join the plant's
blending conveyors. Own layout design. Origin: floor level at the hopper side of the building,
22 m west of the hopper centre (footprint below).

5 parts, about 6,428 triangles. Previews: Preview_FluxStorage.png.

### Moving parts

| Part | Motion |
|---|---|
| FX_Belt_Belt | Panner along U: U speed = belt speed (m/s) / 1.2. Loop length in the about text |
| FX_Belt_HeadPulley / TailPulley | Spin about the pulley axis (local Y): deg/s = belt speed / 0.32 m x 57.3 |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FX_Belt_Belt | (0.00, 0.00, 0.00) |
| FX_Belt_HeadPulley | (51.66, 0.00, 14.12) |
| FX_Belt_Structure | (22.00, 0.00, -2.20) |
| FX_Belt_TailPulley | (22.16, 0.00, -2.48) |
| FX_Building | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Basis |
|---|---|---|
| Bays | 3 x 15 m wide, 20 m deep, push walls 4 m | Estimated |
| Roof | eave 12 m north, ~13.6 m south (open side, loader + tipping truck clearance) | Estimated |
| Pile per bay | ~12 m base, 3.6 m high, ~17 m long: ~430 m3 (about 650 t of silica flux at ~1.5 t/m3 bulk) | Estimated |
| Hopper | 6 x 6 m grizzly top at z 0.6, pit floor -3.5 | Estimated |
| Belt | 1.0 m wide, tail (22, 0, -2.2), head (51.5, 0, 14.4) | Estimated |

Footprint: building x -31 to 16, y -12 to 12; hopper x 19 to 25; transfer tower x 49 to 55.

**Connection points**

| Point | Position |
|---|---|
| Belt head discharge in the transfer tower (to the blending conveyors) | (51.5, 0.0, 14.4) |
| Loader tipping edge (hopper west side, open) | x 19, y -3 to 3, z 0.6 |
| Bay fronts (loader / truck access, south) | y -10, x -30 to 15 |

Sources: own design; bulk density of silica sand ~1.5 t/m3 is a general handbook value (estimated, not checked against a plant).

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
