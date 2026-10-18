# RefractoryRelining

Gear for relining furnaces, converters and ladles. Each asset is a standalone prop at its own
origin. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_refractory_relining.py`. For the tear-out step see
Meshes/DemolitionRobot. Real reline example from the research file: the Mount Isa anode furnace
rebrick (2024) took 33 days, used a demolition robot for break-out, oxy-lancing for shell plate,
hand-laid bricks and about 60 extra trades.

## SM_BrickConveyor

Mobile inclined brick conveyor: 0.6 m flat belt, 9 m long at 22°, head at
4.22 m. Used to feed bricks from the aisle floor up into a converter mouth or furnace
opening during a reline. Origin is the ground point under the tail pulley; the head points +X.
Own design (no drawing found); proportions follow portable belt conveyors used by relining
contractors.

12 parts, about 3,950 triangles. Previews: Preview_BrickConveyor.png.

### Moving parts

| Part | Motion |
|---|---|
| BC_Belt | Continuous UVs: 1 U = 0.6 m, so panner U speed = belt speed (m/s) / 0.6. Loop length 19.00 m |
| BC_HeadPulley, BC_TailPulley | Spin about the pulley axis (local Y) |
| BC_Wheel_* | Spin about local Y |
| BC_Bricks_Load | Static sample bricks on the belt; hide or move along the belt |

The incline is fixed in this model.

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| BC_Belt | (0.00, 0.00, 0.00) |
| BC_Bricks_Load | (0.00, 0.00, 0.00) |
| BC_HeadPulley | (8.40, 0.00, 4.07) |
| BC_Structure | (0.00, 0.00, 0.85) |
| BC_TailPulley | (0.06, 0.00, 0.70) |
| BC_Undercarriage | (0.00, 0.00, 0.00) |
| BC_Wheel_HL | (5.19, 0.68, 0.30) |
| BC_Wheel_HR | (5.19, -0.68, 0.30) |
| BC_Wheel_ML | (3.99, 0.68, 0.30) |
| BC_Wheel_MR | (3.99, -0.68, 0.30) |
| BC_Wheel_TL | (0.30, 0.68, 0.30) |
| BC_Wheel_TR | (0.30, -0.68, 0.30) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Brick 230 × 114 × 76 mm | | Standard (ISO 'straight' size) |
| Belt width, length, angle, chassis | | Own design |

Sources: research/copper-refinery file, US5330690 (ladle relining, title only)

## SM_LadleReliningTower

Four-post tower that stands over a ladle for rebricking. A round work deck on a central mast
rises inside the ladle as each brick course goes in, and turns so the bricklayer stays at the
working face. A hoist trolley on the top runway lowers brick cages to a landing at rim level,
reached by a stair on the +X side. Origin is the floor under the ladle centre. The REF ladle
(Ø3.5 m outside, 3.8 m tall) is a proxy and not exported.
Own design. US5330690 is titled as a ladle relining apparatus but I have not read its drawings,
so this is not based on it.

4 parts, about 2,708 triangles. Previews: Preview_LadleReliningTower.png (deck raised 1.6 m).

### Moving parts

| Part | Motion |
|---|---|
| LRT_Deck | Moves along Z (floor 1.0 m to about 3.2 m) and rotates about Z. The mast is part of the deck |
| LRT_HoistTrolley | Moves along X on the runway (x = -2.0 to +2.0) |
| LRT_BrickCage | Child of the trolley; moves along Z. Its rope is part of the cage; scale is not needed for the short drop to the landing |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| LRT_BrickCage | (2.00, 0.00, 6.05) |
| LRT_Deck | (0.00, 0.00, 1.00) |
| LRT_Frame | (0.00, 0.00, 0.00) |
| LRT_HoistTrolley | (2.00, 0.00, 6.35) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Ladle proxy Ø3.5 m × 3.8 m | | Estimated (converter-aisle copper ladle size, not sourced) |
| Tower 5.2 m square × 6.2 m, deck Ø2.3 m | | Own design |
| Bricks 230 × 114 × 76 mm | | Standard size |

Sources: US5330690 (title only); research/copper-refinery file (reline practice)

## SM_GunningMachine

Dry-process rotor gunning machine (gunite / refractory gun) on a two-wheel skid with a coiled
38 mm material hose and a hand nozzle with water ring. Used for repair gunning of furnace,
converter and ladle linings. Origin is the floor under the rotor centre; the outlet points +X.

5 parts, about 6,976 triangles. Previews: Preview_GunningMachine.png.

### Moving parts

| Part | Motion |
|---|---|
| GM_Wheel_L/R | Spin about local Y |
| GM_Nozzle | Pivot at the hose end; free to rotate for hand-held aiming |
| GM_Hose | Static coil |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| GM_Body | (0.00, 0.00, 0.00) |
| GM_Hose | (0.00, 0.00, 0.00) |
| GM_Nozzle | (2.80, 0.60, 0.04) |
| GM_Wheel_L | (-0.35, 0.38, 0.14) |
| GM_Wheel_R | (-0.35, -0.38, 0.14) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Machine L × W × H | 1245 × 813 × 1219 mm | Sourced (Putzmeister Piccola rotary gun data) |
| Weight 363 kg, 38 mm outlet, output 0.76-4.6 m³/h, rotor 10-14 rpm | | Sourced (same page) |
| Hopper shape, wheel size, hose coil, nozzle | | Estimated |

Sources: https://www.putzmeister.com/web/oceania/product-detail/-/product/309/piccola-rotary-gun

## SM_GunningManipulator

Wheeled hot-gunning manipulator: a material pressure vessel and air module on the carrier, a
shielded operator cab, and a slewing, luffing boom with a two-stage telescopic lance. It reaches
into a hot converter mouth or ladle to gun repair mix onto worn lining without cooling the
vessel. Origin is the ground point at the carrier centre; the boom points +X.
Own design. The task (hot repair gunning of converter mouths) is sourced; no drawing of a
specific machine was found.

12 parts, about 2,352 triangles. Previews: Preview_GunningManipulator.png, Preview_GunningManipulator_Working.png.

### Moving parts

| Part | Motion |
|---|---|
| GMN_Turret | Slews about local Z |
| GMN_Boom | Luffs about local Y (negative raises) |
| GMN_Lance1, GMN_Lance2 | Slide along the boom's local +X, about 1.5 m each (Lance2 rides on Lance1) |
| GMN_NozzleHead | Rotates about local X (the lance axis) to aim the bent nozzle |
| GMN_LuffCyl_Barrel / _Rod | Look-at pair |
| GMN_Wheel_* | Spin about local Y |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| GMN_Boom | (0.30, -0.30, 2.00) |
| GMN_Carrier | (0.00, 0.00, 0.00) |
| GMN_Lance1 | (0.30, -0.30, 2.00) |
| GMN_Lance2 | (0.30, -0.30, 2.00) |
| GMN_LuffCyl_Barrel | (1.00, -0.30, 1.40) |
| GMN_LuffCyl_Rod | (1.50, -0.30, 1.65) |
| GMN_NozzleHead | (5.20, -0.30, 2.00) |
| GMN_Turret | (0.30, -0.30, 1.15) |
| GMN_Wheel_FL | (1.70, 0.92, 0.55) |
| GMN_Wheel_FR | (1.70, -0.92, 0.55) |
| GMN_Wheel_RL | (-1.70, 0.92, 0.55) |
| GMN_Wheel_RR | (-1.70, -0.92, 0.55) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Whole machine (5.4 × 2.4 × 3.3 m, ~6 m lance reach) | | Own design |

Sources: KNS converter mouth paper (hot gunning repairs of mouth refractory), https://onemine.org/documents/peirce-smith-converter-mouth-redesign-overview

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
