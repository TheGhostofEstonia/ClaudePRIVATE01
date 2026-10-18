# OxygenPlant

On-site cryogenic oxygen plant (air separation unit).

Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_utilities.py`.
Fixed facility at its own origin (ground at the footprint centre, +X east, +Y north), not placed
in the plant layout. All layouts are Claude's own designs; dimensions are estimated unless the
table says otherwise.

## SM_OxygenPlant

On-site cryogenic oxygen plant (air separation unit) for oxygen-enriched flash smelting and
converting. Process order, west to east: air intake filter house, main air compressor house,
direct contact aftercooler column with chiller skid, two horizontal molecular sieve adsorbers,
expander/booster skid, main heat exchanger box and the rectification cold box with a stair tower.
Liquid oxygen and liquid nitrogen backup tanks with finned ambient vaporisers stand south, and a
2-cell cooling tower serves the compressor coolers. Product leaves on the pipe rack at the east
edge. Own layout design. Origin: ground centre of the 84 x 52 m pad.

2 parts, about 13,476 triangles. Previews: Preview_OxygenPlant.png.

### Moving parts

| Part | Motion |
|---|---|
| OX_MACDoor | Roller door, slide along local +Z by 5.0 m to open |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| OX_MACDoor | (-21.00, 4.00, 0.00) |
| OX_Site | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Basis |
|---|---|---|
| Cold box | 4.5 x 6.0 m plan, 38 m high | Inside Linde's stated coldbox range (up to 5 x 7 m section, up to 40 m long); exact size for a given capacity estimated |
| Heat exchanger box | 3.5 x 3.5 x 22 m | Estimated |
| Aftercooler column | 3.2 m dia x 22 m | Estimated |
| Adsorbers | 3.5 m dia x 13.5 m over heads | Estimated |
| LOX / LIN tanks | 4.4 m dia, ~18.6 m tall | Estimated |
| MAC house | 30 x 16 x 12 m | Estimated |
| Pipe rack | top z 6.0 m, along y 0 | Estimated |

Capacity is not designed. A flash smelter of a few hundred kt/y concentrate uses oxygen in the
order of 1,000 t/d (estimated, unsourced here); Linde quotes one project at 6 x 3,600 t/d
oxygen, so this single-train size is plausible for a smelter.

**Connection points**

| Point | Position |
|---|---|
| Gaseous oxygen out (blue, DN700) | (41.6, -0.9, 6.50) |
| Nitrogen out (white, DN500) | (41.6, 0.0, 6.40) |
| Cooling water (green, DN600) | (41.6, 0.9, 6.45) |
| Road access to LOX/LIN tanker fill | south edge, x 20 to 36 |

Sources: [Linde coldboxes](https://www.linde-engineering.com/products-and-services/plant-components/coldboxes-packaged-units-and-cryogenic-columns) for the cold box size range and the 6 x 3,600 t/d project; everything else own design.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
