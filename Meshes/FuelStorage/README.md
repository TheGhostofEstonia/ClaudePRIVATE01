# FuelStorage

Fuel receiving and storage: fuel oil tank farm and natural gas metering station.

Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_utilities.py`.
Fixed facility at its own origin (ground at the footprint centre, +X east, +Y north), not placed
in the plant layout. All layouts are Claude's own designs; dimensions are estimated unless the
table says otherwise.

## SM_FuelOilTankFarm

Fuel oil storage for burners (anode furnace, converters, ladle preheat, dryer backup). Two
vertical fixed-roof tanks inside a 40 x 24 m concrete bund, a manifold to a two-pump transfer bay
south of the bund, and a covered road tanker unloading stand with a gantry walkway and a swinging
unloading arm. Own layout design. Origin: ground centre of the bund. The research file lists
"natural gas / fuel oil, coke or coal (some processes)"; coke storage is not modelled because the
flash smelting route here uses little or none.

3 parts, about 8,296 triangles. Previews: Preview_FuelOilTankFarm.png.

### Moving parts

| Part | Motion |
|---|---|
| FT_UnloadArm_Inner | Swing about local Z at the riser, ±90° |
| FT_UnloadArm_Outer | Swing about local Z at the elbow (child of the inner arm), ±150° |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FT_Site | (0.00, 0.00, 0.00) |
| FT_UnloadArm_Inner | (-4.00, -23.00, 1.20) |
| FT_UnloadArm_Outer | (-4.00, -25.20, 1.20) |

### Dimensions

| Item | Value | Basis |
|---|---|---|
| Tanks | 12 m dia x 12 m shell, ~1,350 m3 gross each | Estimated |
| Bund | 40 x 24 m inside, wall 1.5 m: ~1,440 m3 gross less tank footprints ~1,100 m3, about 80 % of one tank | Estimated. Many codes ask for 110 % of the largest tank; raise the wall to ~2.0 m for that |
| Unloading stand | 20 x 6 m slab, canopy 6.0 m, gantry deck 3.7 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Transfer pump discharge (to burners, DN150) | pump bay (±1.8, -17.0, 1.3), take off east |
| Tanker hose coupling (outer arm tip, stowed) | (-2.0, -25.2, 0.75) |
| Road lane through the unloading stand | along X at y -27, 6 m wide |

Sources: own design.

## SM_GasMeteringStation

Natural gas pressure reducing and metering station at the site boundary: buried inlet riser,
two parallel streams (duty and standby) each with filter, meter, pressure regulator and slam-shut
valve, a relief vent stack, a small kiosk for the flow computer, gravel yard and fence. Own layout
design. Origin: ground centre of the 14 x 10 m yard.

2 parts, about 2,332 triangles. Previews: Preview_GasMeteringStation.png.

### Moving parts

| Part | Motion |
|---|---|
| GM_Gate | Swing about local Z at the west post, -90° opens outward |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| GM_Gate | (-1.50, -5.00, 0.00) |
| GM_Station | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Basis |
|---|---|---|
| Yard | 14 x 10 m, fence 2.4 m | Estimated |
| Stream pipe | DN200, centre 1.0 m | Estimated |
| Vent stack top | 4.5 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Gas inlet (buried, from the supplier) | (-7.5, 0.0, -0.5) |
| Gas outlet to the plant ring main (DN300 flange) | (7.5, 0.0, 1.0) |

Sources: own design.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
