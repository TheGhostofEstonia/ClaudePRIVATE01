# Substation

High-voltage substation for the plant.

Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_utilities.py`.
Fixed facility at its own origin (ground at the footprint centre, +X east, +Y north), not placed
in the plant layout. All layouts are Claude's own designs; dimensions are estimated unless the
table says otherwise.

## SM_Substation

HV substation feeding the plant: two incoming line bays (110 kV class, phases 2.2 m apart), each
with surge arresters, a three-pole disconnector, a live-tank circuit breaker and current
transformers, then a 40 MVA class oil transformer stepping down to medium voltage. A fire wall
separates the transformers. LV bus ducts run east into the MV switch / control house, whose cable
trench leads on to the plant (the tankhouse rectifier house and the rest of the plant load). Own
layout design. Origin: ground centre of the fenced yard, 60 x 40 m.

12 parts, about 36,760 triangles. Previews: Preview_Substation.png.

### Moving parts

| Part | Motion |
|---|---|
| SS_Disconnector_S1..S3 / N1..N3 | Rotate about local Z at the near post: 0° closed, +90° open |
| SS_Gate_S / SS_Gate_N | Swing about local Z at the gate post: S leaf -90° (opens outward, +X), N leaf +90° |
| SS_Transformer_T1 / T2 | Static, separate so they can be replaced or highlighted (fire, failure) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SS_Disconnector_N1 | (-18.70, 6.80, 4.15) |
| SS_Disconnector_N2 | (-18.70, 9.00, 4.15) |
| SS_Disconnector_N3 | (-18.70, 11.20, 4.15) |
| SS_Disconnector_S1 | (-18.70, -11.20, 4.15) |
| SS_Disconnector_S2 | (-18.70, -9.00, 4.15) |
| SS_Disconnector_S3 | (-18.70, -6.80, 4.15) |
| SS_Gate_N | (30.00, 4.00, 0.00) |
| SS_Gate_S | (30.00, -4.00, 0.00) |
| SS_Structures | (0.00, 0.00, 0.00) |
| SS_Transformer_T1 | (2.00, -9.00, 0.40) |
| SS_Transformer_T2 | (2.00, 9.00, 0.40) |
| SS_Yard | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Basis |
|---|---|---|
| Yard (fenced) | 60 x 40 m, fence 2.4 m | Estimated |
| Line gantry beam | 14 m | Estimated, 110 kV class |
| Phase spacing | 2.2 m | Estimated, 110 kV class |
| Live part support height | 2.5 m to the insulator base | Estimated (usual minimum to live parts ~2.5 m above walkways) |
| Transformer tank | 7.0 x 3.6 x 4.0 m, radiators each side, top of conservator 5.95 m | Estimated, 40 MVA class |
| MV switch / control house | 14 x 30 x 5.5 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Incoming line, south bay (3 phases at gantry) | (-26.0, -9.0 ± 2.2, 13.6) |
| Incoming line, north bay | (-26.0, 9.0 ± 2.2, 13.6) |
| MV cable trench outlet to the plant | (30.5, 0.0, -1.0), 1.6 m wide |
| Road gate (east) | x 30, y -4 to 4 |

Plant load is not sized here. The tankhouse rectifiers are about 30 kA at 55 V per circuit
(Meshes/Tankhouse); a smelter and refinery site also carries oxygen plant compressors, blowers and
pumps, so two 40 MVA units is a plausible order of magnitude, not a design figure.

Sources: own design; no plant-specific substation data used.

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
