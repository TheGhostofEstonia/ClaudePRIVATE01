# CraneMaintenance

Gear for keeping the overhead cranes running: runway walkway sections, rope-changing equipment
and spare hook blocks. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_crane_maintenance.py`. Each asset sits at its own origin. The
research file notes that cranes are single points of failure in a smelter, which is why spares
are kept ready.

## SM_CraneRunwayWalkway

Walkway along an overhead crane runway girder for inspecting rails, end stops and the crane's
long-travel wheels. CRW_Section is a 6 m tile: place copies every 6 m along +X. Origin is
the inner edge of the walkway floor at the section start; the girder side is -Y, the open side
+Y. The floor is at the girder top flange (rail base). CRW_CageLadder climbs 12 m from the floor
below to the walkway and sits just before the section start; move it to suit (its pivot is the
ladder foot). The REF girder (1.6 m deep with a crane rail) is not exported.

2 parts, about 4,092 triangles. Previews: Preview_CraneRunwayWalkway.png.

### Moving parts

Static.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CRW_CageLadder | (-0.60, 0.40, -12.00) |
| CRW_Section | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Walkway 0.8 m clear, guardrail 1.1 m with mid rail, 150 mm toe board | | Common industrial practice (e.g. ISO 14122-2/-3 ranges); not sourced to one plant |
| Ladder cage from 2.5 m above the floor, hoops every 0.9 m | | Common practice, estimated |
| Girder depth 1.6 m, 12 m ladder | | Estimated |

Sources: research file (crane maintenance list); ISO 14122 is the governing standard family (not checked line by line)

## SM_RopeChangingRig

Ground rig for reeving a new hoist rope into an overhead crane. The new rope pays off a reel on a
jack stand with a band brake, runs over floor guide rollers, and a pulling winch draws it (with
the old rope as a messenger) through the crane's sheaves. Origin is the floor under the reel
axle; the winch is 9 m along +X. RCR_Rope is a static straight-line run; replace it with a
spline in Unreal if the rope must follow the crane.

6 parts, about 1,240 triangles. Previews: Preview_RopeChangingRig.png.

### Moving parts

| Part | Motion |
|---|---|
| RCR_Reel | Spins about local Y |
| RCR_WinchDrum | Spins about local Y. Rope speed = drum r (0.32 m) × ω |
| RCR_ReelStand, RCR_Winch, RCR_GuideRollers, RCR_Rope | Static |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| RCR_GuideRollers | (0.00, 0.00, 0.00) |
| RCR_Reel | (0.00, 0.00, 1.15) |
| RCR_ReelStand | (0.00, 0.00, 0.00) |
| RCR_Rope | (0.00, 0.00, 0.00) |
| RCR_Winch | (0.00, 0.00, 0.00) |
| RCR_WinchDrum | (9.00, 0.00, 0.75) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Reel Ø2.0 × 1.0 m, winch, roller spacing | | Estimated (typical wire-rope reel sizes, no one source) |

Sources: research file (crane maintenance: rope-changing gear)

## SM_SpareHookBlocks

Two spare hook blocks laid on their side plates on timber cradles on a skid: a 4-sheave 50 t
block and a 2-sheave 16 t block, each with a hook on a swivel and a safety latch. Each block is a
set of parts so it can be picked up by a crane in game. Origin is the floor at the stand centre.
The block frames carry a rotation of X = +90° (hook pointing +Y); set rotation X = 0 to hang a
block upright from a crane.

11 parts, about 3,604 triangles. Previews: Preview_SpareHookBlocks.png.

### Moving parts

| Part | Motion |
|---|---|
| SHB_Block50t_Frame, SHB_Block16t_Frame | Root of each block: move as a whole when lifted (sheave pin centre is the pivot) |
| SHB_Block*_SheaveN | Spin about local Y |
| SHB_Block*_Hook | Swivels about local Z |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SHB_Block16t_Frame | (1.00, -0.35, 0.48) |
| SHB_Block16t_Hook | (1.00, 0.18, 0.48) |
| SHB_Block16t_Sheave1 | (1.00, -0.35, 0.42) |
| SHB_Block16t_Sheave2 | (1.00, -0.35, 0.53) |
| SHB_Block50t_Frame | (-1.00, -0.35, 0.61) |
| SHB_Block50t_Hook | (-1.00, 0.38, 0.61) |
| SHB_Block50t_Sheave1 | (-1.00, -0.35, 0.43) |
| SHB_Block50t_Sheave2 | (-1.00, -0.35, 0.55) |
| SHB_Block50t_Sheave3 | (-1.00, -0.35, 0.66) |
| SHB_Block50t_Sheave4 | (-1.00, -0.35, 0.78) |
| SHB_Stand | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| 50 t, 5-sheave block for 16 mm rope weighs about 475 kg (mobile crane type) | | Sourced (Tadano listing) but overhead-crane blocks are heavier; Mennens 5-sheave blocks run about 1.8-3.6 t |
| Sheave Ø0.72 m (50 t) / Ø0.50 m (16 t), plate sizes, hook size | | Estimated (sheave Ø ≈ 25-30 × rope Ø for 22-28 mm rope) |

Sources: cranetrader.com Tadano 50 t block listing; mennens.nl 5-sheave block product sheet

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
