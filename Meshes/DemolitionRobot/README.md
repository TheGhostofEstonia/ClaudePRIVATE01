# SM_DemolitionRobot

Remote-controlled demolition robot for refractory tear-out in converters, ladles and furnaces.
Generic machine in the 3.6 t class (Brokk 300 size), no branding. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_demolition_robot.py`. 20 parts, about
3,276 triangles.

Local axes: +X is the arm side. Origin is the ground point under the slewing centre. The arm is
modelled stretched out level along +X (rest pose).

## Moving parts

| Part | Motion |
|---|---|
| DR_Turret | Slews about local Z (360°, 16 s per turn on the real machine) |
| DR_Outrigger_FL/FR/RL/RR | Rotate about local X. Modelled stowed at 70° above horizontal. Deployed (pad on the ground) is X = about -118° for the L legs and +118° for the R legs |
| DR_Boom, DR_Arm, DR_ToolArm, DR_Breaker | Rotate about local Y. Negative Y raises the boom; positive Y folds the next segment down |
| DR_*Cyl_Barrel / DR_*Cyl_Rod | Look-at pairs: each aims local +X at the other's pivot (Damped Track in the .blend) |
| DR_Track_L/R | UV U runs along the loop (1 U = 1 m), so panner U speed = track speed in m/s |

Preview working pose: turret 25°, boom -48°, arm +55°, tool arm +15°, breaker +25°.
A transport pose (arm folded over the body) is about boom -75°, arm +165°, tool arm +120°;
check for clipping, it was not test-rendered.

The parent chain in the .blend is Chassis > Turret > Boom > Arm > ToolArm > Breaker, with the
outriggers on the chassis and each cylinder half on the part it is pinned to. Rebuild the same
chain in an Unreal Blueprint.

## Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| DR_Arm | (2.25, 0.00, 0.95) |
| DR_ArmCyl_Barrel | (0.95, 0.00, 1.17) |
| DR_ArmCyl_Rod | (2.42, 0.00, 1.15) |
| DR_Boom | (0.30, 0.00, 0.95) |
| DR_BoomCyl_Barrel | (0.45, 0.00, 0.72) |
| DR_BoomCyl_Rod | (1.30, 0.00, 0.75) |
| DR_Breaker | (5.00, 0.00, 0.95) |
| DR_BreakerCyl_Barrel | (4.28, 0.00, 0.78) |
| DR_BreakerCyl_Rod | (5.05, 0.00, 0.78) |
| DR_Chassis | (0.00, 0.00, 0.00) |
| DR_Outrigger_FL | (0.78, 0.50, 0.55) |
| DR_Outrigger_FR | (0.78, -0.50, 0.55) |
| DR_Outrigger_RL | (-0.78, 0.50, 0.55) |
| DR_Outrigger_RR | (-0.78, -0.50, 0.55) |
| DR_ToolArm | (4.00, 0.00, 0.95) |
| DR_ToolArmCyl_Barrel | (3.10, 0.00, 1.13) |
| DR_ToolArmCyl_Rod | (4.00, 0.00, 1.12) |
| DR_Track_L | (0.00, 0.48, 0.19) |
| DR_Track_R | (0.00, -0.48, 0.19) |
| DR_Turret | (0.00, 0.00, 0.62) |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Minimum width × height | 1.20 × 1.53 m | Sourced: Brokk 300 product page / sheet |
| Tail swing diameter | 1.827 m | Sourced: Brokk 300 product sheet drawing |
| Reach, horizontal / vertical, incl. breaker | 6.1 / 6.5 m | Sourced (same sheet) |
| Machine weight | 3,650 kg without attachment | Sourced (same sheet) |
| Track length ~1.8 m, outrigger length 0.8 m, arm split 1.95 / 1.75 / 1.00 / 1.05 m | | Estimated from photos so the total reach matches |
| Breaker shape and size | | Estimated |

Sources: https://www.brokk.com/us/product/brokk-300/ and
https://www.brokk.com/uploads/2020/07/brokk300_product_sheet.pdf. Use at a reline: Mount Isa anode
furnace rebrick 2024, where a Brokk broke out the refractory (research file [S22]).

## Files

SM_DemolitionRobot.blend / .fbx, Preview_Rest.png, Preview_Working.png
