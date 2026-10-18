# Warehouse

Spares warehouse for the plant, plus the pallet-rack props it is built from.

## SM_Warehouse

Spares and consumables warehouse with high pallet racking, three truck docks and a drive-in door.
Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_warehouse.py`.
The layout is an own design.

Origin: finished floor level (z 0) at the centre of the building. +X east, the docks face south (-Y).

22 parts, about 99,548 triangles. Previews: Preview_Exterior.png, Preview_Interior.png (roof,
north wall and lights hidden, dock 1 open with its lip out). REF holds a 3 t forklift block, two
1.8 m figures and a ground slab with the building and dock well left open.

### Layout

| Zone | Extent |
|---|---|
| Building (outside of cladding) | x -30.12 to 30.12, y -15.12 to 15.12, eave 12.0 m, ridge 13.3 m |
| Portal frames | 11 frames at 6.0 m centres, x -30 to 30 |
| Marshalling / dispatch area behind the docks | y -14.75 to -8.8 |
| Pallet racking | 8 single-depth lines (2 single, 3 back-to-back pairs), 16 bays each, x -20.0 to 24.8. Aisles 3.5 m (y -7.7..-4.2, -1.8..1.7, 4.1..7.6, 10.0..13.5) |
| Storage positions | 1,920 EUR-pallet positions (3 per beam level, 5 levels including the floor); about 68 % are filled in WH_RackLoad |
| Cantilever rack | Column line x 29.25, y -6.0 to 12.0, 1.2 m arms toward -X at z 1, 2, 3, 4 |
| Office / counter | x -29.75 to -22.0, y 7.0 to 14.75, 3.5 m high, counter window on the east face at y 10.5 to 13.5, flat roof used as a storage deck with handrail |

### Moving parts

| Part | Motion |
|---|---|
| WH_Door_Dock1..3 | Roller shutter. Slide +Z by 3.15 m to open (rolls into the coil box) |
| WH_Door_DriveIn | Roller shutter. Slide +Z by 4.95 m to open |
| WH_LevellerLip_1..3 | Hinged lip. Rotate about local X: 0° hangs down (stowed), -90° rests on the truck bed |
| WH_Roof, WH_Cladding_* | Static, separate so they can be hidden for cutaway views |
| WH_RackLoad, WH_CantileverLoad | Static stock, separate so it can be hidden or replaced with the Consumables props |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| WH_CantileverLoad | (0.00, 0.00, 0.00) |
| WH_CantileverRack | (0.00, 0.00, 0.00) |
| WH_Cladding_East | (0.00, 0.00, 0.00) |
| WH_Cladding_North | (0.00, 0.00, 0.00) |
| WH_Cladding_South | (0.00, 0.00, 0.00) |
| WH_Cladding_West | (0.00, 0.00, 0.00) |
| WH_DockApron | (0.00, 0.00, 0.00) |
| WH_DockEquipment | (0.00, 0.00, 0.00) |
| WH_Door_Dock1 | (10.00, -14.90, 0.00) |
| WH_Door_Dock2 | (15.00, -14.90, 0.00) |
| WH_Door_Dock3 | (20.00, -14.90, 0.00) |
| WH_Door_DriveIn | (-29.90, 0.00, 0.00) |
| WH_Frame | (0.00, 0.00, 0.00) |
| WH_LevellerLip_1 | (10.00, -14.88, 0.00) |
| WH_LevellerLip_2 | (15.00, -14.88, 0.00) |
| WH_LevellerLip_3 | (20.00, -14.88, 0.00) |
| WH_Lights | (0.00, 0.00, 0.00) |
| WH_Office | (0.00, 0.00, 0.00) |
| WH_RackLoad | (0.00, 0.00, 0.00) |
| WH_Racking | (0.00, 0.00, 0.00) |
| WH_Roof | (0.00, 0.00, 0.00) |
| WH_Slab | (0.00, 0.00, 0.00) |

### Footprint and connection points

| Item | Value |
|---|---|
| Dock doors (south wall) | Centres x 10.0, 15.0, 20.0, y -15.0; 3.0 x 3.2 m, sill at floor level 0.0 |
| Dock well | x 7.0 to 23.0, y -27.0 to -15.3, floor z -1.2 (truck bed about level with the warehouse floor) |
| Dock well ramp top (road joins here) | x 7.0 to 23.0 at y -37.0, z 0.0, 12 % down toward the docks |
| Drive-in door (west wall) | Centre (-30.0, 0.0, 0.0), 5.0 x 5.0 m, leads into the aisle at y -1.8..1.7 |
| Office personnel door (west wall) | (-30.0, 10.5, 0.0), 1.0 x 2.1 m |
| Fire exit (east wall) | (30.0, -11.5, 0.0), 1.0 x 2.1 m |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Building 60 x 30 m, eave 12 m | | Estimated (sizes given in the brief) |
| Rack beam clear span 2.7 m, frame depth 1.1 m, 3 EUR pallets per level | | Typical industry values for 1200 x 800 mm pallets, estimated |
| Beam levels z 1.8, 3.6, 5.4, 7.2 (frame 8.5 m) | | Estimated |
| Aisle 3.5 m | | Estimated for a 3 t counterbalance forklift (right-angle stacking aisle about 3.5-4.0 m) |
| Dock door 3.0 x 3.2 m, leveller 2.0 x 2.5 m, dock well 1.2 m deep | | Estimated, common European dock sizes |
| Cantilever arms 1.2 m, 4 levels | | Estimated |

## SM_PalletRackBay and SM_PalletRackFrame

Reusable selective pallet racking, the same geometry the warehouse uses. Both live in
SM_PalletRack.blend and export as separate FBX files. Each is one static part (PR_PalletRackBay,
PR_PalletRackFrame), pivot at its origin. Preview: Preview_PalletRack.png (three bays plus the end
frame). About 420 and 228 triangles.

Origin: floor level at the front upright of the frame, on the frame centre line. The rack runs
toward +X and its depth toward +Y (aisle on the -Y side).

To build a run of n bays, place SM_PalletRackBay at x = 0, 2.8, 2 × 2.8, ... (n copies)
and one SM_PalletRackFrame at x = n × 2.8. Back-to-back runs: second run rotated 180°
with 0.2 m between the backs.

| Item | Value | Status |
|---|---|---|
| Bay pitch 2.8 m (2.7 m clear between uprights), depth 1.1 m | | Estimated, typical for 3 EUR pallets per level |
| Frame height 8.5 m, uprights 90 x 70 mm, bracing every 1.2 m | | Estimated |
| Beam levels (tops) z 1.8, 3.6, 5.4, 7.2, 120 mm box beams, 2 deck support bars per level | | Estimated |
| Load per level | 3 EUR pallets, about 1 t each | Estimated |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
