# SparesAndFRP

Spares and repair gear for the corrosive areas (acid plant, tankhouse) and the dust-collection
baghouses. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_spares_frp.py`. Each asset is a standalone prop at its own origin.

## SM_AcidPumpSpare

Spare acid-service pump, ready to swap in: a lined end-suction centrifugal pump (PTFE-lined
casing, white flange faces) on its baseplate on a pallet, without motor; a spare impeller on a
stand; and a crate for mechanical seals and liners. Origin is the floor under the pallet centre.

5 parts, about 1,080 triangles. Previews: Preview_AcidPumpSpare.png.

### Moving parts

| Part | Motion |
|---|---|
| AP_Shaft | Spins about local X (once the pump is installed) |
| AP_SpareImpeller | Loose prop; pivot at its hub |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| AP_ImpellerStand | (0.00, 0.00, 0.00) |
| AP_Pump | (0.00, 0.00, 0.00) |
| AP_SealCrate | (0.00, 0.00, 0.00) |
| AP_Shaft | (0.00, 0.00, 0.62) |
| AP_SpareImpeller | (1.45, 0.00, 0.64) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Pump about 1.6 m baseplate, Ø0.6 m volute, 200/160 mm nozzles | | Estimated (mid-size acid transfer pump) |

Sources: research file (tankhouse and acid plant are very corrosive; acid-resistant pump spares)

## SM_PipeSpoolRack

Single-sided cantilever rack (6 m) holding spare pipe for the acid plant and tankhouse:
FRP spools (green) on the bottom level, PTFE-lined steel spools with white liner faces on the
second, HDPE lengths on the third and FRP elbows/tees on the top. Origin is the floor at the
first column; arms point +Y.

2 parts, about 4,016 triangles. Previews: Preview_PipeSpoolRack.png.

### Moving parts

Static. PSR_Spools is one part; split it in Unreal if single spools must be picked up.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| PSR_Rack | (0.00, 0.00, 0.00) |
| PSR_Spools | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Rack 6 m, 4 levels, 1.2 m arms; pipe DN200-DN300 | | Estimated |

Sources: research file (acid-resistant pipe spares)

## SM_BaghouseSpares

Storage rack for pulse-jet baghouse spares: twelve wire cages on the middle level, boxed filter
bags above and below, and one loose bag and one loose cage on the floor in front for handheld
or install animations. Origin is the floor at the rack's -X/-Y corner. Bags and cages lie along
+X; the collar/snap-band end is at -X.

5 parts, about 33,900 triangles. Previews: Preview_BaghouseSpares.png.

### Moving parts

| Part | Motion |
|---|---|
| BH_FilterBag_Single, BH_FilterCage_Single | Loose props; pivot at the collar end. Stand upright (rotate Y = -90°) to drop into a tube sheet |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| BH_BagBoxes | (0.00, 0.00, 0.00) |
| BH_Cages_Stack | (0.00, 0.00, 0.00) |
| BH_FilterBag_Single | (0.10, -0.60, 0.08) |
| BH_FilterCage_Single | (0.10, -1.00, 0.08) |
| BH_Rack | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Bag Ø6 in (152 mm) × 120 in (3.05 m), cage Ø5.75 in | | Sourced (common 6 in bag / 5.75 in cage pairing, 96/120/144 in standard lengths) |
| 12 cage wires, rings every 8 in | | Sourced range (10/12/14 wires for most felts); ring spacing estimated |
| Rack 3.4 × 1.1 × 2.2 m | | Estimated |

Sources: https://www.baghouse.com/how-to-measure-your-baghouse-filters-cages/ ; mpparts.com 6 in × 120 in bag listing

## SM_FRPRepairStation

Workshop corner for repairing FRP pipe, ducts and tank parts from the acid plant and tankhouse:
a steel bench with mixing bucket and cutting board, resin and hardener drums on a spill pallet,
a glass-mat roll stand, a flammables cabinet, an FRP pipe on trestles with a wet patch wrap, and
a two-joint fume extraction arm over the job. Origin is the floor at the bench's -X/-Y corner.

4 parts, about 1,128 triangles. Previews: Preview_FRPRepairStation.png.

### Moving parts

| Part | Motion |
|---|---|
| FRP_ExtractArm1 | Rotates about local Z on the post |
| FRP_ExtractArm2 | Child of Arm1; rotates about local Y and Z at the elbow |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FRP_ExtractArm1 | (-0.40, 1.20, 2.60) |
| FRP_ExtractArm2 | (1.00, 1.20, 2.60) |
| FRP_ExtractPost | (0.00, 0.00, 0.00) |
| FRP_Station | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| 205 L drums (Ø0.58 × 0.88 m) | | Standard drum size |
| Everything else | | Estimated |

Sources: research file (FRP repair for corrosive areas)

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
