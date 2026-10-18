# ConverterMouthCleaner

Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_skulling_mouth_cleaning.py`. Standalone at its own origin; lay the
rails along the converter aisle in front of the converter row.

## SM_ConverterMouthCleaner

Rail-mounted converter mouth cleaner ("mouth breaker"). It runs on a 3.0 m gauge track along
the converter aisle. With a converter rolled so its mouth faces the aisle, the luffing boom
pushes a hydraulic ram with a chisel blade into the mouth and shears off the accretions
(frozen slag and metal) that build up on the lip. A heat shield protects the cab. Origin is the
rail-level point at the carriage centre; the boom points +X. The REF converter shell (Ø4.4 m) and
rails are not exported.
Own design. Sourced: mouth build-up must be scraped off and this damages mouth refractory, which
then needs hot gunning; C21C5/4693 "Skull removal; Cleaning of the converter mouth" is a patent
class of its own. I found no drawing of a specific machine.

11 parts, about 1,256 triangles. Previews: Preview_MouthCleaner.png, Preview_MouthCleaner_Working.png.

### Moving parts

| Part | Motion |
|---|---|
| CMC_Carriage | Travels along X on the rails |
| CMC_RailWheel_* | Spin about local Y; circumference 2.51 m |
| CMC_Turret | Slews about local Z (±30° is enough to square up to a mouth) |
| CMC_Boom | Luffs about local Y (negative raises) |
| CMC_Ram | Slides along the boom's local +X (stroke about 2 m) |
| CMC_Blade | Tilts about local Y |
| CMC_LuffCyl_Barrel / _Rod | Look-at pair |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| CMC_Blade | (6.80, 0.60, 2.75) |
| CMC_Boom | (0.60, 0.60, 2.75) |
| CMC_Carriage | (0.00, 0.00, 0.00) |
| CMC_LuffCyl_Barrel | (1.60, 0.60, 1.65) |
| CMC_LuffCyl_Rod | (2.35, 0.60, 2.20) |
| CMC_RailWheel_FL | (1.80, 1.50, 0.40) |
| CMC_RailWheel_FR | (1.80, -1.50, 0.40) |
| CMC_RailWheel_RL | (-1.80, 1.50, 0.40) |
| CMC_RailWheel_RR | (-1.80, -1.50, 0.40) |
| CMC_Ram | (0.60, 0.60, 2.75) |
| CMC_Turret | (0.80, 0.60, 1.35) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Converter shell Ø4.4 m | | Typical 4-4.5 m from the research file (not sourced to one plant) |
| Machine 5.2 × 3.5 m, boom + ram ≈ 7 m reach, 3.0 m gauge | | Own design |

Sources: https://onemine.org/documents/peirce-smith-converter-mouth-redesign-overview ; https://patents.google.com/patent/US4591134 (classification C21C5/4693)

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
