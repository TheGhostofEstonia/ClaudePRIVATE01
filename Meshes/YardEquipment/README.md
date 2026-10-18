# YardEquipment

On-site mobile plant for logistics: loaders for flux, reverts and clean-up, forklifts for anode and
cathode bundles and for the spares warehouse, and a tugger train for parts. Each asset is a
standalone prop at its own origin (not tied to the plant layout). Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Logistics/build_yard_equipment.py`. Brand names are size
references only; the models carry no logos. In the .blend the moving parts are parented for
posing; hydraulic cylinder halves and the loader tilt link use Damped Track constraints to
non-exported empties. REF objects (scale figure, loads, camera, sun, ground) are not exported.

## SM_WheelLoader

Articulated wheel loader with a Z-bar linkage and a 5.4 m³ general-purpose bucket (Cat 980 size,
no branding). Moves flux, limestone and reverts in the receiving area and clears slag and spillage.
Origin is the ground point under the articulation hinge. +X is the bucket end.

20 parts, about 4,012 triangles. Previews: Preview_WheelLoader.png, Preview_WheelLoader_Raised.png.

### Moving parts

| Part | Motion |
|---|---|
| WL_FrontFrame | Articulates (yaw) about local Z at the hinge, about ±40° (estimated). Child of WL_RearFrame |
| WL_LiftArms | Rotate about local Y at the arm pivot. 0° = carry; about -85.0° (negative Y raises) = maximum lift, hinge pin 4.55 m |
| WL_Bucket | Rotates about local Y at the hinge pin, relative to the arms. The linkage reaches about -40° (rack back, negative Y) to +45° (dump). At full lift the preview uses arms -85.0° and bucket +40.0°, i.e. racked back 45° in world |
| WL_TiltLever | Bell-crank on the arm cross tube; rotates about local Y. Follows the bucket: solve it so the link (0.75 m, lower lever arm 0.45 m) closes between the lever pin and the bucket top pin (the script's solve_lever does this) |
| WL_TiltLink | Look-at: pivot on the lever, local +X aims at the bucket top pin (Damped Track in the .blend) |
| WL_TiltCyl / WL_LiftCyl_L/R / WL_SteerCyl_L/R _Barrel / _Rod | Look-at pairs: each half aims local +X at the other's pivot |
| WL_Wheel_FL..RR | Spin about local Y, 61.3° per metre travelled (r 0.935 m) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| WL_Bucket | (3.90, 0.00, 0.68) |
| WL_FrontFrame | (0.00, 0.00, 1.15) |
| WL_LiftArms | (1.50, 0.00, 2.30) |
| WL_LiftCyl_L_Barrel | (0.92, 0.55, 1.08) |
| WL_LiftCyl_L_Rod | (2.25, 0.55, 1.53) |
| WL_LiftCyl_R_Barrel | (0.92, -0.55, 1.08) |
| WL_LiftCyl_R_Rod | (2.25, -0.55, 1.53) |
| WL_RearFrame | (0.00, 0.00, 1.15) |
| WL_SteerCyl_L_Barrel | (-0.95, 0.48, 1.05) |
| WL_SteerCyl_L_Rod | (0.55, 0.48, 1.05) |
| WL_SteerCyl_R_Barrel | (-0.95, -0.48, 1.05) |
| WL_SteerCyl_R_Rod | (0.55, -0.48, 1.05) |
| WL_TiltCyl_Barrel | (0.75, 0.00, 1.95) |
| WL_TiltCyl_Rod | (2.97, 0.00, 2.36) |
| WL_TiltLever | (3.27, 0.00, 1.71) |
| WL_TiltLink | (3.12, 0.00, 1.29) |
| WL_Wheel_FL | (1.90, 1.22, 0.94) |
| WL_Wheel_FR | (1.90, -1.22, 0.94) |
| WL_Wheel_RL | (-1.90, 1.22, 0.94) |
| WL_Wheel_RR | (-1.90, -1.22, 0.94) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Wheelbase, tread | 3.80 m, 2.44 m | Sourced (Cat 980 spec sheet) |
| Length without bucket, hood height, ROPS height | 8.155 m, 3.064 m, 3.83 m | Sourced |
| Hinge pin height at carry / maximum lift | 0.68 m / 4.55 m | Sourced (configuration-dependent; 0.63 m and 4.78 m are also published) |
| Bucket 5.4 m³ | Width 3.25 m, profile | Capacity sourced; width and profile estimated |
| Tyres 29.5R25 | r 0.935, 0.75 wide | Size sourced, model dimensions approximate |
| Arm pivot, linkage geometry, articulation hinge height 1.15 m | | Estimated (own layout, not from a Cat drawing) |

Sources: Cat 980 product and dealer spec pages (cat.com, zieglercat.com, ringpower.com)

## SM_SkidSteer

Skid steer loader with radial lift arms and a 1.73 m low-profile bucket (Cat 262 size, no
branding), for clean-up under conveyors and in the shed. Origin is the ground point midway between
the axles. +X is the bucket end. Skid steering: left and right wheels turn independently.

16 parts, about 3,096 triangles. Previews: Preview_SkidSteer.png, Preview_SkidSteer_Raised.png.

### Moving parts

| Part | Motion |
|---|---|
| SS_LiftArms | Rotate about local Y at the rear tower pivot; 0° carry, about -60.9° = full height (bucket pin 3.17 m) |
| SS_Bucket | Rotates about local Y at the pin. +60.9° keeps it level at full height; about -30° racks back, +50° dumps |
| SS_CabDoor | Front door, hinged on its left vertical edge: rotate about local Z, 0 to +80° (opens outward) |
| SS_LiftCyl_L/R, SS_TiltCyl_L/R _Barrel / _Rod | Look-at pairs |
| SS_Wheel_FL..RR | Spin about local Y, 136.4° per metre (r 0.42 m). Left pair and right pair at independent speeds |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SS_Body | (0.00, 0.00, 0.00) |
| SS_Bucket | (1.40, 0.00, 0.20) |
| SS_CabDoor | (0.57, 0.50, 1.10) |
| SS_LiftArms | (-1.15, 0.00, 1.65) |
| SS_LiftCyl_L_Barrel | (-1.05, 0.70, 0.62) |
| SS_LiftCyl_L_Rod | (-0.25, 0.70, 1.62) |
| SS_LiftCyl_R_Barrel | (-1.05, -0.70, 0.62) |
| SS_LiftCyl_R_Rod | (-0.25, -0.70, 1.62) |
| SS_TiltCyl_L_Barrel | (0.67, 0.45, 1.42) |
| SS_TiltCyl_L_Rod | (1.33, 0.45, 0.65) |
| SS_TiltCyl_R_Barrel | (0.67, -0.45, 1.42) |
| SS_TiltCyl_R_Rod | (1.33, -0.45, 0.65) |
| SS_Wheel_FL | (0.62, 0.68, 0.42) |
| SS_Wheel_FR | (0.62, -0.68, 0.42) |
| SS_Wheel_RL | (-0.62, 0.68, 0.42) |
| SS_Wheel_RR | (-0.62, -0.68, 0.42) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Wheelbase, width over tyres, cab top | 1.249 m, 1.676 m, 2.11 m | Sourced (Cat 262D3 spec) |
| Length without / with bucket | 2.995 m / 3.71 m | Sourced; the model is 2.95 / 3.67 m |
| Bucket pin carry / max lift | 0.20 m / 3.17 m | Sourced |
| Bucket width 1.73 m | | Sourced; depth and profile estimated |
| Tyres 12x16.5 (r 0.42 m) | | Size sourced, radius approximate |
| Arm pivot, knee, cylinder pins | | Estimated |

Sources: Cat 262D3 spec pages (cat.com, ringpower.com, miltoncat.com)

## SM_HeavyForklift16t

Heavy counterbalance forklift, 16 t at 1.2 m load centre (Kalmar DCG160-12 size, no branding), for
anode stacks and cathode bundles between the casting wheel, tankhouse service bay, stripping line
and dispatch. Enclosed cab, twin front tyres, duplex mast with free lift and hydraulic side shift.
Origin is the ground point under the front (drive) axle centre. +X is the fork end. The Raised
preview carries two 2 t cathode bundles from the REF collection (not exported).

17 parts, about 3,916 triangles. Previews: Preview_HeavyForklift16t.png, Preview_HeavyForklift16t_Raised.png.

### Moving parts

| Part | Motion |
|---|---|
| HF_MastOuter | Tilts about local Y at the tilt pins: forward 6° (positive Y), back 10° (negative Y). Child of HF_Body |
| HF_MastInner | Slide along local +Z, each child of the stage before. Model convention for fork lift h: carriage rises inside the innermost stage first up to the free lift (1.5 m), then the 1 moving stage takes the rest. Max lift 4.5 m |
| HF_Carriage | Slides along local +Z inside the innermost stage, 0 to 1.5 m |
| HF_SideShift | Slides along local Y, ±0.15 m |
| HF_Fork_L/R | Slide along local Y on the carriage bars to set the fork spread (centres ±0.75 m as modelled) |
| HF_TiltCyl_L/R _Barrel / _Rod | Look-at pairs |
| HF_Wheel_F* | Spin about local Y, 92.4° per metre (r 0.62 m) |
| HF_Wheel_RL/RR | Spin about local Y, 92.4° per metre (r 0.62 m), and steer about local Z (about ±75°; rear-wheel steering) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| HF_Body | (0.00, 0.00, 0.00) |
| HF_Carriage | (1.19, 0.00, 0.10) |
| HF_Fork_L | (1.31, 0.75, 1.07) |
| HF_Fork_R | (1.31, -0.75, 1.07) |
| HF_MastInner | (0.75, 0.00, 0.30) |
| HF_MastOuter | (0.75, 0.00, 0.70) |
| HF_SideShift | (1.26, 0.00, 0.10) |
| HF_TiltCyl_L_Barrel | (-0.35, 0.22, 0.75) |
| HF_TiltCyl_L_Rod | (0.69, 0.22, 1.85) |
| HF_TiltCyl_R_Barrel | (-0.35, -0.22, 0.75) |
| HF_TiltCyl_R_Rod | (0.69, -0.22, 1.85) |
| HF_Wheel_FL | (0.00, 0.94, 0.62) |
| HF_Wheel_FL2 | (0.00, 0.61, 0.62) |
| HF_Wheel_FR | (0.00, -0.94, 0.62) |
| HF_Wheel_FR2 | (0.00, -0.61, 0.62) |
| HF_Wheel_RL | (-3.40, 1.04, 0.62) |
| HF_Wheel_RR | (-3.40, -1.04, 0.62) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Rated capacity 16 t at 1.2 m load centre | | Sourced (model designation) |
| Overall width 2.54 m, cab (construction) height 2.92 m, turning radius 5.175 m | | Sourced (Lectura specs for DCG160-12) |
| Overall height lowered 3.945 m, fork length 2.40 m, lift 4.5 m (duplex free-lift mast) | | Sourced (dealer listing, one configuration) |
| Length to fork face ~5.7 m (8.1 m with 2.4 m forks) | | Sourced loosely (dealer listing); model is 5.65 m |
| Wheelbase 3.40 m, tyres r 0.62 m, free lift 1.50 m, fork section 250 × 100 mm, carriage 2.30 m | | Estimated |

Sources: lectura-specs.com DCG160-12, krommenhoek.nl and forkliftcenter.com listings

## SM_Forklift3t

Standard 3 t counterbalance forklift with a triplex full-free-lift mast and side shift (Linde
H30 size, no branding), for the spares warehouse racks, pallets, drums and IBCs. Open overhead
guard. Origin is the ground point under the front axle centre. +X is the fork end. The Raised
preview carries a REF pallet and crate (not exported).

16 parts, about 3,372 triangles. Previews: Preview_Forklift3t.png, Preview_Forklift3t_Raised.png.

### Moving parts

| Part | Motion |
|---|---|
| FL_MastOuter | Tilts about local Y at the tilt pins: forward 6° (positive Y), back 8° (negative Y). Child of FL_Body |
| FL_MastMiddle, FL_MastInner | Slide along local +Z, each child of the stage before. Model convention for fork lift h: carriage rises inside the innermost stage first up to the free lift (1.39 m), then the 2 moving stages share the rest equally. Max lift 4.68 m |
| FL_Carriage | Slides along local +Z inside the innermost stage, 0 to 1.39 m |
| FL_SideShift | Slides along local Y, ±0.1 m |
| FL_Fork_L/R | Slide along local Y on the carriage bars to set the fork spread (centres ±0.35 m as modelled) |
| FL_TiltCyl_L/R _Barrel / _Rod | Look-at pairs |
| FL_Wheel_F* | Spin about local Y, 171.0° per metre (r 0.335 m) |
| FL_Wheel_RL/RR | Spin about local Y, 197.6° per metre (r 0.29 m), and steer about local Z (about ±75°; rear-wheel steering) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| FL_Body | (0.00, 0.00, 0.00) |
| FL_Carriage | (0.67, 0.00, 0.10) |
| FL_Fork_L | (0.79, 0.35, 0.52) |
| FL_Fork_R | (0.79, -0.35, 0.52) |
| FL_MastInner | (0.32, 0.00, 0.10) |
| FL_MastMiddle | (0.32, 0.00, 0.10) |
| FL_MastOuter | (0.32, 0.00, 0.36) |
| FL_SideShift | (0.74, 0.00, 0.10) |
| FL_TiltCyl_L_Barrel | (-0.23, 0.22, 0.41) |
| FL_TiltCyl_L_Rod | (0.26, 0.22, 1.05) |
| FL_TiltCyl_R_Barrel | (-0.23, -0.22, 0.41) |
| FL_TiltCyl_R_Rod | (0.26, -0.22, 1.05) |
| FL_Wheel_FL | (0.00, 0.53, 0.34) |
| FL_Wheel_FR | (0.00, -0.53, 0.34) |
| FL_Wheel_RL | (-1.65, 0.47, 0.29) |
| FL_Wheel_RR | (-1.65, -0.47, 0.29) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Rated capacity 3 t at 0.5 m load centre | | Sourced (model class) |
| Length to fork face 2.756 m, width 1.256 m, overall height 2.165 m | | Sourced (dealer listing, Linde H 30 T); model length 2.62 m |
| Triplex mast: max lift 4.68 m, free lift 1.39 m | | Sourced (same listing) |
| Wheelbase 1.65 m, tyres r 0.335 / 0.29 m, forks 1.20 m × 100 × 45 mm | | Estimated |

Sources: exapro.com Linde H 30 T listings

## SM_TuggerTrain

Electric seated tow tractor (6 t towing class, Linde P60 / Hyster T6.0UT size, no branding) with
three 2.0 × 1.0 m platform carts for spares, reagents and drums between the warehouse, workshops
and the plant. Origin is the ground point under the tractor's rear axle line (x = 0 at 0.10 m in
front of it). +X is forward. Each cart's tow bar eye sits on the hitch pin of the vehicle ahead.

29 parts, about 7,800 triangles. Previews: Preview_TuggerTrain.png.

### Moving parts

| Part | Motion |
|---|---|
| TT_Tractor_Wheel_FL/FR | Spin about local Y, 286.5° per metre (r 0.20 m); steer about local Z ±60° |
| TT_Tractor_Wheel_RL/RR | Drive wheels, spin about local Y, 229.2° per metre (r 0.25 m) |
| TT_CartN_Frame | Free body; follows the hitch ahead. Pivot at the cart centre on the ground |
| TT_CartN_TowBar | Yaws about local Z (±70°) and lifts about local Y (±15°) at the cart bracket; the eye drops on the hitch pin ahead |
| TT_CartN_Castor_FL/FR | Swivel about local Z (trailing castor, wheel axle 0.06 m behind the swivel) |
| TT_CartN_Wheel_* | Spin about local Y, 382.0° per metre (r 0.15 m). Front wheels are children of the castors |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| TT_Cart1_Castor_FL | (-1.55, 0.38, 0.30) |
| TT_Cart1_Castor_FR | (-1.55, -0.38, 0.30) |
| TT_Cart1_Frame | (-2.35, 0.00, 0.00) |
| TT_Cart1_TowBar | (-1.29, 0.00, 0.40) |
| TT_Cart1_Wheel_FL | (-1.61, 0.38, 0.15) |
| TT_Cart1_Wheel_FR | (-1.61, -0.38, 0.15) |
| TT_Cart1_Wheel_RL | (-3.10, 0.38, 0.15) |
| TT_Cart1_Wheel_RR | (-3.10, -0.38, 0.15) |
| TT_Cart2_Castor_FL | (-4.40, 0.38, 0.30) |
| TT_Cart2_Castor_FR | (-4.40, -0.38, 0.30) |
| TT_Cart2_Frame | (-5.20, 0.00, 0.00) |
| TT_Cart2_TowBar | (-4.14, 0.00, 0.40) |
| TT_Cart2_Wheel_FL | (-4.46, 0.38, 0.15) |
| TT_Cart2_Wheel_FR | (-4.46, -0.38, 0.15) |
| TT_Cart2_Wheel_RL | (-5.95, 0.38, 0.15) |
| TT_Cart2_Wheel_RR | (-5.95, -0.38, 0.15) |
| TT_Cart3_Castor_FL | (-7.25, 0.38, 0.30) |
| TT_Cart3_Castor_FR | (-7.25, -0.38, 0.30) |
| TT_Cart3_Frame | (-8.05, 0.00, 0.00) |
| TT_Cart3_TowBar | (-6.99, 0.00, 0.40) |
| TT_Cart3_Wheel_FL | (-7.31, 0.38, 0.15) |
| TT_Cart3_Wheel_FR | (-7.31, -0.38, 0.15) |
| TT_Cart3_Wheel_RL | (-8.80, 0.38, 0.15) |
| TT_Cart3_Wheel_RR | (-8.80, -0.38, 0.15) |
| TT_Tractor | (0.00, 0.00, 0.00) |
| TT_Tractor_Wheel_FL | (1.18, 0.40, 0.20) |
| TT_Tractor_Wheel_FR | (1.18, -0.40, 0.20) |
| TT_Tractor_Wheel_RL | (-0.10, 0.40, 0.25) |
| TT_Tractor_Wheel_RR | (-0.10, -0.40, 0.25) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Tractor 1.73 × 0.996 × 1.96 m (roof) | | Sourced (Linde P 60 Z dealer listing); model 1.77 × 0.98 × 1.96 m |
| Tractor wheelbase 1.28 m, 6 t towing capacity | | Sourced (Hyster T6.0UT brochure) |
| Wheel sizes, hitch height 0.40 m | | Estimated |
| Carts 2.0 × 1.0 m, deck 0.55 m, side stakes 1.05 m, tow bar 0.8 m | | Estimated (own design) |

Sources: exapro.com Linde P 60 Z listing; Hyster T6.0UT brochure (hyster.com)

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
