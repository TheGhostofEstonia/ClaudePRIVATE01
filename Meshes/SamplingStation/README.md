# SamplingStation

Truck sampling station for incoming concentrate.

## About

Automatic auger (probe) sampler for incoming concentrate trucks, with a sample preparation house.
The driver stops at the white line, the boom slews over the trailer, the carriage moves the
probe along the load and the auger drills down and lifts a core. The boom then slews round over
the receiving hopper on the house roof and the auger reverses to drop the sample, which falls
through a crusher and a rotary divider into sample jars for the laboratory. Built in Blender 5.2.2
LTS (headless, cloud) with `Tools/Blender/Logistics/build_weighbridge_sampling.py`. The layout is
an own design based on pedestal samplers with a slewing boom.

Origin: ground level (z 0) at the probe stop line on the lane centre. Trucks drive in +X.

6 parts, about 3,438 triangles. Previews: Preview_Overview.png, Preview_Sampling.png
(probe plunged 3.0 m). REF holds a 13 x 2.5 m tipper-trailer block (z 1.3 to 3.6) and a
1.8 m figure.

Rail option (not modelled): for concentrate arriving by rail the same pedestal and boom can stand
beside the track before the rotary car dumper, with the stop line replaced by a car-positioner
mark. The boom then needs about 1 m more reach because a wagon body sits further from the
pedestal than a truck trailer.

## Moving parts

| Part | Motion |
|---|---|
| SS_Boom | Slews about local Z at the pedestal axis. 0° = boom over the lane (+Y). 180° puts the carriage over the receiving hopper when the carriage is at 6.1 m from the axis |
| SS_Carriage | Travels along the boom's local Y: 1.0 m to 7.4 m from the axis (drawn at 4.5 m, which is the lane centre) |
| SS_Probe | Plunges along -Z by up to 3.0 m. Raised, the tip is at z 4.10, above a 4.0 m trailer top. Auger spins about local Z while drilling |

## Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SS_Boom | (0.00, -4.50, 8.60) |
| SS_Carriage | (0.00, 0.00, 8.60) |
| SS_Lane | (0.00, 0.00, 0.00) |
| SS_Pedestal | (0.00, 0.00, 0.00) |
| SS_Probe | (0.00, 0.00, 7.90) |
| SS_SampleHouse | (0.00, 0.00, 0.00) |

## Footprint and connection points

| Item | Value |
|---|---|
| Footprint | x -14 to 14 (lane), y -13.0 to 2.2 |
| Lane entry / exit (z 0) | (-14.0, 0.0, 0.0) / (14.0, 0.0, 0.0), 4.0 m wide |
| Probe stop line | x 0, under the probe when the boom is at 0° |
| Sample house door | (2.60, -10.80, 0.15), facing +X |
| Receiving hopper inlet | (0.00, -9.60, 3.68) |
| Pedestal ladder foot | (0.00, -5.75, 0.40) |

## Dimensions

| Item | Value | Status |
|---|---|---|
| Boom reach | 8.0 m from the axis, carriage range about 6.4 m, 360° slew | Estimated, sized to cover a 2.5 m trailer 4.5 m from the axis. A commercial collector sampler lists 2.95-5.95 m horizontal reach and 0-5 m sampling height with 180° slew ([SAUR, DirectIndustry](https://www.directindustry.com/prod/saur/product-239378-2404099.html)) |
| Auger probe | 3.8 m long, 0.22 m flight diameter, 3.0 m stroke | Estimated |
| Pedestal | 0.7 m diameter column, boom at z 8.6 | Estimated |
| Sample house | 5.2 x 4.4 x 2.7 m | Estimated |
| Truck lane | 4.0 m wide | Estimated |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
