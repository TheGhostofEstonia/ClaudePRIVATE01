# SkullingStations

Stations for knocking solidified skull out of ladles and slag pots. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_skulling_mouth_cleaning.py`. Both are fixed
installations at their own origin; place them beside the converter aisle (ladles) and on the slag
pot route between the cooling yard and the furnace (pots).

## SM_LadleSkullingStation

The crane sets a ladle into the cradle by its trunnions. A geared drive on each pedestal (ring gear
on the cradle journal, motor and gearbox on the pedestal) tips the cradle about
150° so the mouth faces down over a steel-lined skull bunker (-1.2 m floor), and a
pedestal-mounted hydraulic breaker on a plinth knocks the skull and lip build-up loose. A loader
clears the bunker from the open -X end. Origin is the floor under the tipping axis; the tipping
axis runs along Y at 4.400000095367432 m. The REF ladle (Ø3.5 × 3.8 m, trunnions 2.6 m above its
base) is not exported.
Own design. Sourced practice: skull is knocked out with hydraulic or pneumatic hammers, and
hydraulic pushers were used on ladles (see Sources).

11 parts, about 1,600 triangles. Previews: Preview_LadleSkulling.png (upright), Preview_LadleSkulling_Working.png (inverted, breaker in).

### Moving parts

| Part | Motion |
|---|---|
| LSS_Cradle | Rotates about local Y; tip is negative Y (preview -150°). Carry the ladle with it |
| LSS_BreakerTurret | Slews about local Z |
| LSS_BreakerBoom | Rotates about local Y (negative raises) |
| LSS_BreakerStick, LSS_BreakerHammer | Rotate about local Y (positive folds down) |
| LSS_BoomCyl, LSS_StickCyl | Look-at pairs |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| LSS_Base | (0.00, 0.00, 0.00) |
| LSS_BoomCyl_Barrel | (-2.60, 3.60, 3.45) |
| LSS_BoomCyl_Rod | (-1.30, 3.60, 3.58) |
| LSS_BreakerBoom | (-2.70, 3.60, 4.00) |
| LSS_BreakerHammer | (4.90, 3.60, 4.00) |
| LSS_BreakerPedestal | (0.00, 0.00, 0.00) |
| LSS_BreakerStick | (1.50, 3.60, 4.00) |
| LSS_BreakerTurret | (-3.00, 3.60, 3.20) |
| LSS_Cradle | (0.00, 0.00, 4.40) |
| LSS_StickCyl_Barrel | (-1.90, 3.60, 4.40) |
| LSS_StickCyl_Rod | (1.35, 3.60, 4.45) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Whole station | | Own design, sized to the REF ladle |
| Breaker reach about 9 m from the pedestal | | Estimated (pedestal breakers for grizzlies cover 6-12 m) |

Sources: onemine.org 'A New Method of Removing Skulls from Direct-Metal Ladles' (hydraulic push-out); US4047708 background (jack hammers for skull); research file (Mount Isa 'pot knock' for slag pots)

## SM_PotSkullingStation

"Pot knock" station for slag pots that come back from the cooling yard with skull stuck inside.
The crane (or a pot carrier with a crane assist) hangs the pot upside down by its trunnions in
two V-saddles at 3.0 m. A hydraulic ram in the top beam strikes the pot base, the skull drops
onto a wear plate, and a loader clears it from the open +X side. Origin is the floor under the
pot centre. Trunnions lie along Y, matching SM_SlagPotCarrier's assumed pot (trunnion
1.8 m above the base, tips at ±2.02 m).
Own design. Mount Isa runs a "pot knock" deskulling system on its pot route (sourced), but I
found no drawing of it.

2 parts, about 416 triangles. Previews: Preview_PotSkulling.png (ram down on an inverted pot).

### Moving parts

| Part | Motion |
|---|---|
| PSS_Ram | Moves along -Z; 0.25 m down touches the base of the REF pot (preview pose) |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| PSS_Frame | (0.00, 0.00, 0.00) |
| PSS_Ram | (0.00, 0.00, 6.15) |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Pot proxy rim Ø3.6, base Ø2.4, 2.6 m tall | | Assumed (same as SM_SlagPotCarrier) |
| Frame 4.4 × 5.2 × 6.8 m, saddles at 3.0 m | | Own design |

Sources: research file [S8]: Mount Isa slag pot route with a 'pot knock' deskulling system

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
