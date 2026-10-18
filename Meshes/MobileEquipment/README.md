# MobileEquipment

Shutdown and clean-up vehicles. Each asset is a standalone prop at its own origin (not tied to the
plant layout). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_mobile_equipment.py`. Brand names are size references only; the
models carry no logos. In the .blend the moving parts are parented for posing; hydraulic cylinder
halves use Damped Track constraints to non-exported empties.

## SM_MobileCrane

Five-axle all-terrain crane, 100 t class (Liebherr LTM 1100-5.2 size, no branding). Origin is the
ground point under the slewing centre. +X is the cab end.

29 parts, about 6,136 triangles. Previews: Preview_MobileCrane.png (travel), Preview_MobileCrane_SetUp.png.

### Moving parts

| Part | Motion |
|---|---|
| MC_Superstructure | Slews about local Z |
| MC_Boom_Base | Luffs about local Y at the foot pin; negative Y raises the boom (0 to about -82°) |
| MC_Boom_Tele1..4 | Slide along the boom's local +X. Each section can extend about 10 m; the preview uses 7, 14, 21, 28 m (cumulative) |
| MC_HoistRope | Pivot at the head sheave; scale Z = hanging rope length in metres. Not parented: keep it vertical in world space and move its pivot with the boom head |
| MC_HookBlock | Pivot at the rope end; place it at head sheave position minus the rope length |
| MC_OutriggerBeam_xx | Slide along local Y: +2.25 m on the L side, -2.25 m on the R side for the full 7.0 m width |
| MC_OutriggerJack_xx | Slide along -Z (0.30 m reaches the ground and lifts the tyres slightly) |
| MC_LuffCyl_Barrel / _Rod | Look-at pair: each half aims local +X at the other's pivot |
| MC_Wheel_A1L..A5R | Spin about local Y. Tyre circumference 4.65 m: deg/s = speed (m/s) × 77.4. Axles 1-2 and 4-5 steer |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| MC_Boom_Base | (-2.80, 0.00, 3.05) |
| MC_Boom_Tele1 | (-2.80, 0.00, 3.05) |
| MC_Boom_Tele2 | (-2.80, 0.00, 3.05) |
| MC_Boom_Tele3 | (-2.80, 0.00, 3.05) |
| MC_Boom_Tele4 | (-2.80, 0.00, 3.05) |
| MC_Carrier | (0.00, 0.00, 0.00) |
| MC_HoistRope | (8.98, 0.00, 3.40) |
| MC_HookBlock | (9.30, 0.00, 2.40) |
| MC_LuffCyl_Barrel | (0.75, 0.00, 2.50) |
| MC_LuffCyl_Rod | (-0.20, 0.00, 2.75) |
| MC_OutriggerBeam_FL | (3.10, 1.25, 1.20) |
| MC_OutriggerBeam_FR | (3.10, -1.25, 1.20) |
| MC_OutriggerBeam_RL | (-4.28, 1.25, 1.20) |
| MC_OutriggerBeam_RR | (-4.28, -1.25, 1.20) |
| MC_OutriggerJack_FL | (3.10, 1.25, 1.00) |
| MC_OutriggerJack_FR | (3.10, -1.25, 1.00) |
| MC_OutriggerJack_RL | (-4.28, 1.25, 1.00) |
| MC_OutriggerJack_RR | (-4.28, -1.25, 1.00) |
| MC_Superstructure | (0.00, 0.00, 1.95) |
| MC_Wheel_A1L | (3.90, 1.13, 0.74) |
| MC_Wheel_A1R | (3.90, -1.13, 0.74) |
| MC_Wheel_A2L | (2.25, 1.13, 0.74) |
| MC_Wheel_A2R | (2.25, -1.13, 0.74) |
| MC_Wheel_A3L | (-0.90, 1.13, 0.74) |
| MC_Wheel_A3R | (-0.90, -1.13, 0.74) |
| MC_Wheel_A4L | (-2.55, 1.13, 0.74) |
| MC_Wheel_A4R | (-2.55, -1.13, 0.74) |
| MC_Wheel_A5L | (-4.20, 1.13, 0.74) |
| MC_Wheel_A5R | (-4.20, -1.13, 0.74) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Transport length × width × height | 13.64 × 2.75 × 4.0 m | Sourced (LTM 1100-5.2 operator listings, trucks-cranes.nl; LECTURA) |
| Outrigger base | 7.385 × 7.0 m | Sourced (LECTURA spec page) |
| Main boom | 11.5 m retracted, 52 m fully out | Sourced; sections shortened so the model stays inside 13.64 m |
| Axle positions, tyre size, cab layout, counterweight size | | Estimated from photos |

Sources: trucks-cranes.nl LTM 1100-5.2 fleet pages; https://www.lectura-specs.com/en/model/cranes/all-terrain-cranes-liebherr/ltm-1100-5-2-11734400

## SM_ScissorLift

Electric slab scissor lift, 9.8 m platform class (Genie GS-3246 size, no branding). Origin is the
ground point under the chassis centre. +X is the deck-extension end.

27 parts, about 3,460 triangles. Previews: Preview_ScissorLift.png (stowed), Preview_ScissorLift_Raised.png.

### Moving parts

Five stages of crossed arms, each arm a separate part with its pivot on its centre pin. For a
target platform floor height H (1.25 to 9.78 m):

- θ = asin((H - 0.1 - 0.6) / (5 × 2.0)), stowed θ0 = 3.15°
- arm of stage i (1..5): X = -0.95 + 1.0 × cos θ, Z = 0.6 + (i - 0.5) × 2.0 × sin θ
- arms 'A' (yellow, rising toward +X): rotation Y = -(θ - θ0); arms 'B' (blue): +(θ - θ0)
- SL_Platform: Z = H, no X shift (the hinged pins all sit on the line X = -0.95; the other ends slide)
- SL_DeckExtension slides along local +X up to 0.9 m

| Part | Motion |
|---|---|
| SL_Arm_1AL ... SL_Arm_5BR | As above |
| SL_Platform, SL_DeckExtension | As above |
| SL_Wheel_FL/FR/RL/RR | Spin about local Y (front pair steers about Z) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SL_Arm_1AL | (0.05, 0.40, 0.65) |
| SL_Arm_1AR | (0.05, -0.40, 0.65) |
| SL_Arm_1BL | (0.05, 0.32, 0.65) |
| SL_Arm_1BR | (0.05, -0.32, 0.65) |
| SL_Arm_2AL | (0.05, 0.40, 0.76) |
| SL_Arm_2AR | (0.05, -0.40, 0.76) |
| SL_Arm_2BL | (0.05, 0.32, 0.76) |
| SL_Arm_2BR | (0.05, -0.32, 0.76) |
| SL_Arm_3AL | (0.05, 0.40, 0.88) |
| SL_Arm_3AR | (0.05, -0.40, 0.88) |
| SL_Arm_3BL | (0.05, 0.32, 0.88) |
| SL_Arm_3BR | (0.05, -0.32, 0.88) |
| SL_Arm_4AL | (0.05, 0.40, 0.99) |
| SL_Arm_4AR | (0.05, -0.40, 0.99) |
| SL_Arm_4BL | (0.05, 0.32, 0.99) |
| SL_Arm_4BR | (0.05, -0.32, 0.99) |
| SL_Arm_5AL | (0.05, 0.40, 1.10) |
| SL_Arm_5AR | (0.05, -0.40, 1.10) |
| SL_Arm_5BL | (0.05, 0.32, 1.10) |
| SL_Arm_5BR | (0.05, -0.32, 1.10) |
| SL_Chassis | (0.00, 0.00, 0.00) |
| SL_DeckExtension | (1.10, 0.00, 1.25) |
| SL_Platform | (0.00, 0.00, 1.25) |
| SL_Wheel_FL | (0.82, 0.47, 0.19) |
| SL_Wheel_FR | (0.82, -0.47, 0.19) |
| SL_Wheel_RL | (-0.82, 0.47, 0.19) |
| SL_Wheel_RR | (-0.82, -0.47, 0.19) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Stowed length × width | 2.44 × 1.16 m | Sourced (Genie GS-3246 spec table) |
| Stowed height | 2.40 m rails up | Sourced; the model's rail top is ≈2.35 m |
| Max platform height | 9.78 m | Sourced |
| Platform with extension | ≈3.2 m long | Sourced as 125 in (Cat Rental listing), model 3.18 m |
| Stage count, arm length 2.0 m, chassis height | | Estimated |

Sources: Genie GS-2046/2646/3246 spec sheet (via aerialtitans.com PDF); Cat Rental GS-3246 listing

## SM_BoomLift

Diesel 4x4 telescopic boom lift, 20 m platform class (Genie S-65 size, no branding). Origin is the
ground point under the slewing centre. +X is the platform end when stowed.

13 parts, about 2,736 triangles. Previews: Preview_BoomLift.png (stowed), Preview_BoomLift_Raised.png.

### Moving parts

| Part | Motion |
|---|---|
| BL_Turntable | Slews about local Z |
| BL_Boom_Base | Rotates about local Y at the foot pin; negative Y raises (0 to about -75°) |
| BL_Boom_Tele1, BL_Boom_Tele2 | Each slides along the boom's local +X, up to about 5.3 m (Tele2 rides on Tele1) |
| BL_Jib | Rotates about local Y at the jib pin (about ±70°) |
| BL_Platform | Rotates about local Y to stay level: platform Y = -(boom Y + jib Y) |
| BL_LiftCyl_Barrel / _Rod | Look-at pair |
| BL_Wheel_FL..RR | Spin about local Y; tyre circumference 3.27 m. Front pair steers |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| BL_Boom_Base | (-0.40, 0.00, 2.30) |
| BL_Boom_Tele1 | (-0.40, 0.00, 2.30) |
| BL_Boom_Tele2 | (-0.40, 0.00, 2.30) |
| BL_Chassis | (0.00, 0.00, 0.00) |
| BL_Jib | (6.50, 0.00, 2.30) |
| BL_LiftCyl_Barrel | (0.25, 0.00, 1.50) |
| BL_LiftCyl_Rod | (0.85, 0.00, 2.00) |
| BL_Platform | (7.70, 0.00, 2.30) |
| BL_Turntable | (0.00, 0.00, 1.00) |
| BL_Wheel_FL | (1.15, 1.04, 0.52) |
| BL_Wheel_FR | (1.15, -1.04, 0.52) |
| BL_Wheel_RL | (-1.15, 1.04, 0.52) |
| BL_Wheel_RR | (-1.15, -1.04, 0.52) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Stowed length × width × height | 9.42 × 2.49 × 2.72 m | Sourced, but listings vary (9.42-10.57 m long depending on jib position) |
| Platform height / horizontal reach | 19.8 / 17.1 m | Sourced (dealer listings citing Genie data) |
| Platform 2.44 × 0.91 m, boom split, tyre size | | Estimated |

Sources: Boom & Bucket and Construction Equipment Guide Genie S-65 listings; Truck1 S-65 listing (metric)

## SM_ScaffoldTower

Cup-lock style access tower, one 2.5 × 1.3 m bay, 4 lifts of 2.0 m
(working deck at 8.0 m) with guardrails, toe boards and an internal ladder. Origin is
the base of the standard at the -X/-Y corner; the tower extends along +X and +Y. Static.

4 parts, about 4,940 triangles. Previews: Preview_ScaffoldTower.png.

### Moving parts

Static. SC_Standards, SC_LedgersTransoms, SC_Boards and SC_Ladder are separate so boards or the ladder can be hidden.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SC_Boards | (0.00, 0.00, 0.00) |
| SC_Ladder | (0.00, 0.00, 0.00) |
| SC_LedgersTransoms | (0.00, 0.00, 0.00) |
| SC_Standards | (0.00, 0.00, 0.00) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Bay length 2.5 m, ledger 2452 mm actual | | Sourced (cup-lock supplier data: 2.5 m is the basic access bay) |
| Cup nodes every 0.5 m | | Sourced (standards with cups at 500 mm intervals) |
| 48.3 mm tube | | Sourced (EN 12810/BS 1139 standard scaffold tube) |
| Transom 1.3 m, lift height 2.0 m, 225 mm boards, internal ladder | | Estimated (common practice, not checked against one manual) |

Sources: scaffolding-direct.co.uk cup-lock ledger pages; bfs-industries.com cup-lock pages

## SM_ScaffoldKit

Loose cup-lock components for building other scaffold shapes in Unreal. Each part's pivot is its
lower or -X end on the floor/tube centreline; they are laid out 0.5 m apart along +Y.
Snap rule: standards on a 2.5 × 1.3 m grid, ledgers at multiples of 0.5 m height.

8 parts, about 536 triangles. Previews: Preview_ScaffoldKit.png.

### Moving parts

Static props.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SCK_BaseJack | (0.00, 3.50, 0.00) |
| SCK_Board_2p5m | (0.00, 2.50, 0.00) |
| SCK_Brace_2p5x2m | (0.00, 2.00, 0.00) |
| SCK_Ledger_1p3m | (0.00, 1.50, 0.00) |
| SCK_Ledger_2p5m | (0.00, 1.00, 0.00) |
| SCK_Standard_2m | (0.00, 0.50, 0.00) |
| SCK_Standard_3m | (0.00, 0.00, 0.00) |
| SCK_ToeBoard_2p5m | (0.00, 3.00, 0.00) |

### Dimensions

Same sources and estimates as SM_ScaffoldTower.

Sources: As SM_ScaffoldTower

## SM_VacuumTruck

Three-axle industrial vacuum loader (Supersucker / Vacall AllVac size, no branding) for dust,
spill and baghouse clean-up. Origin is the ground point at the chassis middle. +X is the cab end.

13 parts, about 3,748 triangles. Previews: Preview_VacuumTruck.png, Preview_VacuumTruck_Dump.png.

### Moving parts

| Part | Motion |
|---|---|
| VT_DebrisBody | Tips about local Y at the rear hinge; dump is about -40° |
| VT_RearDoor | Swings up about local Y at its top hinge (+80° open); child of the body |
| VT_Boom | Slews about local Z and luffs about local Y at its pin on the body |
| VT_SuctionHose | Hangs from the boom tip; rotate about X/Y to swing |
| VT_TipCyl_Barrel / _Rod | Look-at pair |
| VT_Wheel_A1L..A3R | Spin about local Y; circumference 3.33 m. A1 steers |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| VT_Boom | (-0.85, 0.00, 3.46) |
| VT_Chassis | (0.00, 0.00, 0.00) |
| VT_DebrisBody | (-5.05, 0.00, 1.15) |
| VT_RearDoor | (-5.05, 0.00, 3.30) |
| VT_SuctionHose | (4.15, 0.00, 2.96) |
| VT_TipCyl_Barrel | (-0.50, 0.00, 1.05) |
| VT_TipCyl_Rod | (-1.20, 0.00, 1.60) |
| VT_Wheel_A1L | (3.55, 1.07, 0.53) |
| VT_Wheel_A1R | (3.55, -1.07, 0.53) |
| VT_Wheel_A2L | (-1.95, 1.07, 0.53) |
| VT_Wheel_A2R | (-1.95, -1.07, 0.53) |
| VT_Wheel_A3L | (-3.30, 1.07, 0.53) |
| VT_Wheel_A3R | (-3.30, -1.07, 0.53) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Length × width × height | 10.67 × 2.44 × 3.91 m | Sourced (Super Products Supersucker data) |
| Debris body | ≈13 m³ gross in the model | Estimated; real 9-14 m³ (DISAB SDC 100 9 m³, AllVac 18 yd³ ≈ 13.8 m³) |
| Dump angle 40° | | Sourced (Vacall AllVac) |
| 8 in (≈200 mm) boom and hose, module layout | | Estimated |

Sources: Super Products Supersucker spec sheet (directindustry PDF); Southeastern Equipment Vacall AllVac page; DISAB SDC 100 data

## SM_Sweeper

Ride-on industrial sweeper with a high-dump hopper (Tennant S30 size, no branding). Origin is the
ground point under the main broom. +X is forward (hopper end).

9 parts, about 1,752 triangles. Previews: Preview_Sweeper.png, Preview_Sweeper_Dump.png.

### Moving parts

| Part | Motion |
|---|---|
| SW_MainBroom | Spins about local Y |
| SW_SideBrush_L/R | Spin about local Z (L clockwise seen from above, R anticlockwise) |
| SW_HopperArm | Rotates about local Y; about -115° raises the hopper to dump height |
| SW_Hopper | Child of the arm; rotate about local Y to tip (preview +150° with the arm raised) |
| SW_Wheel_FL/FR/Rear | Spin about local Y; the rear wheel steers about Z |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| SW_Chassis | (0.00, 0.00, 0.00) |
| SW_Hopper | (1.20, 0.00, 0.40) |
| SW_HopperArm | (0.95, 0.00, 0.95) |
| SW_MainBroom | (0.00, 0.00, 0.18) |
| SW_SideBrush_L | (1.00, 0.55, 0.06) |
| SW_SideBrush_R | (1.00, -0.55, 0.06) |
| SW_Wheel_FL | (0.70, 0.62, 0.22) |
| SW_Wheel_FR | (0.70, -0.62, 0.22) |
| SW_Wheel_Rear | (-0.95, 0.00, 0.22) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Length × width × height (guard) | 2.36 × 1.59 × 2.095 m | Sourced (Tennant S30 dealer data). Width here is the single side-brush path; the model body is 1.40 m |
| Hopper 395 L, dump height up to 1.525 m | | Sourced |
| Three-wheel layout, arm geometry, broom size | | Estimated (not checked against an S30 drawing) |

Sources: clemas.co.uk and hughcrane.co.uk Tennant S30 pages

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
