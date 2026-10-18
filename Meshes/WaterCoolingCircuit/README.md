# WaterCoolingCircuit

Cooling-water circuit for the furnace and converter cooling jackets. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_water_cooling.py`. Each asset sits at its
own origin; the stub flanges listed per asset are where they connect, so lay pipe between them
in Unreal once the plant layout fixes their positions. The cooling tower is deliberately
different from the acid plant's gas-cleaning tower (GasCleaning folder, on T's computer).
Loop: jackets -> leak detection manifold -> plate heat exchangers -> pumps -> jackets (closed,
treated water); tower basin -> pumps -> exchangers -> tower (open); emergency tank -> jackets by
gravity.

## SM_FurnaceCoolingTower

Three-cell induced-draft counterflow cooling tower in cast concrete for the furnace and process
water. It is built to look different from the acid plant's two-cell gas-cleaning tower: concrete
casing and cell walls, inlet louvres along both long faces, FRP fan stacks, an external hot-water
riser and a stair to the fan deck. Origin is the -X/-Y outer corner of the cells at basin rim
level (0.0); cells run along +X (27 × 9 m in plan, fan deck at 10 m).

4 parts, about 4,948 triangles. Previews: Preview_FurnaceCoolingTower.png.

### Moving parts

| Part | Motion |
|---|---|
| CT_Fan1..3 | Spin about local Z (about 120-150 rpm is typical for this fan size; game value) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CT_Fan1 | (4.50, 4.50, 11.30) |
| CT_Fan2 | (13.50, 4.50, 11.30) |
| CT_Fan3 | (22.50, 4.50, 11.30) |
| CT_Structure | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Cell plan 9 × 9 m, fan Ø7.3 m, fan deck 10 m, basin 1.5 m deep | | Estimated (field-erected tower proportions; packaged towers like the Marley NC have 2.1-3.7 m fans) |
| Hot water inlet Ø0.7 m at (-2.5, -1.5, 0.0); cold water outlet Ø0.9 m at (30.0, 4.5, -0.9) | | Connection points (stub flanges) |

Sources: Marley NC listings (fan sizes, cell sizes for packaged towers) via equipt.com/genemco.com; research file

## SM_CoolingWaterPumpStation

Open-sided pump shelter on a slab: three horizontal split-case pumps (two duty, one standby)
with motors, isolation and check valves, a suction header from the tower basin, a discharge
header, and two plate heat exchangers that separate the closed furnace-jacket loop from the
open tower loop. Origin is the slab corner at floor level; the station runs along +X.
Pipe colours: blue = cold/suction, green = pumped supply, red = warm return from the jackets.
Own layout.

4 parts, about 2,716 triangles. Previews: Preview_CoolingWaterPumpStation.png.

### Moving parts

| Part | Motion |
|---|---|
| WCP_Pump1..3_Shaft | Spin about local Y (coupling hub visible between pump and motor; impellers are inside the casings and not modelled) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| WCP_Pump1_Shaft | (1.50, 3.45, 0.95) |
| WCP_Pump2_Shaft | (4.70, 3.45, 0.95) |
| WCP_Pump3_Shaft | (7.90, 3.45, 0.95) |
| WCP_Station | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Station 18 × 10 m, pumps, exchangers, headers (Ø0.6-0.7 m) | | Own design; sizes are estimates for a flash furnace jacket circuit |
| Suction header inlet Ø0.7 m at (-1.0, 1.0, 0.8); discharge header outlet Ø0.6 m at (16.5, 6.5, 2.6) | | Connection points (stub flanges) |

Sources: Hatch, 'Monitoring of Copper Cooling Components in Furnaces Using Leak Detection and NDT Methods' (closed cooling circuits on smelting furnaces)

## SM_EmergencyWaterTank

Elevated steel tank (about 302 m³) on a four-leg tower, bottom at 22 m. If the cooling pumps
stop, a fail-open valve lets it feed the furnace jackets by gravity long enough to drain or
freeze the bath safely. Origin is the ground at the tower centre. Outlet stub Ø0.5 m at
(6.0, 0.0, 1.0).
Common practice for smelter jacket cooling, but not sourced to a specific plant; size is a
guess. The research file notes that loss of jacket water risks a steam explosion, which makes
this tank a good game hazard hook.

1 parts, about 3,948 triangles. Previews: Preview_EmergencyWaterTank.png.

### Moving parts

Static. The valve handwheel is part of the tank mesh.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| EWT_Tank | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Ø8 × 6 m tank, 22 m tower | | Estimated |

Sources: research file (jacket water loss -> steam explosion hazard)

## SM_LeakDetectionManifold

Distribution and return manifold for 8 furnace cooling-jacket circuits. Each circuit has a
supply flow meter and a return flow meter, a sight glass, a temperature probe and an isolation
valve. The panel compares supply and return flow per circuit; a shortfall means water is leaking
into the furnace, and that circuit's lamp and the beacon go red. Origin is the rack corner at
floor level; circuits run along +X at 0.9 m pitch; jacket pipes leave the back (-Y).
Own layout. Sourced: smelters run automatic leak detection systems on furnace cooling circuits,
including pressure-based systems sensitive to a few drips per minute.

10 parts, about 4,804 triangles. Previews: Preview_LeakDetectionManifold.png.

### Moving parts

| Part | Motion |
|---|---|
| LDM_Lamp1..8 | Static; swap material (green / red) per circuit state |
| LDM_Beacon | Static; drive emissive strength or rotate a light for the alarm |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| LDM_Beacon | (9.40, 0.60, 2.10) |
| LDM_Lamp1 | (9.83, 0.15, 0.80) |
| LDM_Lamp2 | (9.83, 0.28, 0.80) |
| LDM_Lamp3 | (9.83, 0.41, 0.80) |
| LDM_Lamp4 | (9.83, 0.54, 0.80) |
| LDM_Lamp5 | (9.83, 0.66, 0.80) |
| LDM_Lamp6 | (9.83, 0.79, 0.80) |
| LDM_Lamp7 | (9.83, 0.92, 0.80) |
| LDM_Lamp8 | (9.83, 1.05, 0.80) |
| LDM_Rack | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Rack, pipe sizes, meter sizes | | Own design |
| Supply header inlet at (-0.5, 0.3, 2.8); return header outlet at (8.7, 0.9, 0.7) | | Connection points |

Sources: https://hatch.com/About-Us/Publications/Technical-Papers/2014/05/Monitoring-of-Copper-Cooling-Components-in-Furnaces-Using-Leak-Detection-and-NDT-Methods

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
