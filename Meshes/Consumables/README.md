# Consumables

Palletised and packaged goods that arrive at the plant (section 12 of the equipment reference:
refractory bricks and castables, electrolyte additives and reagents, acid and oils, steel spares,
cathode blanks). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_warehouse.py`. Each prop is exported to its own FBX at its own
origin; SM_Consumables.blend holds them all in a display row. Preview: Preview_ContactSheet.png.

Origins: floor level, centre of the footprint. Long sides run along X. IBC valve and cathode-crate
lifting points as described below; the gas cage front (gates) faces -Y.

## Props

| FBX | Parts | Triangles |
|---|---|---|
| SM_EuroPallet | CS_EuroPallet | 240 |
| SM_BrickPallet | BP_PalletBricks, BP_Wrap | 2,352 |
| SM_CastableBagPallet | CB_PalletSacks, CB_Wrap | 4,392 |
| SM_ReagentSackPallet | RS_PalletSacks, RS_Wrap | 3,564 |
| SM_BulkBag | BB_BulkBag | 624 |
| SM_IBC | IBC_Tote | 1,236 |
| SM_Drum200L | DR_Drum200L | 700 |
| SM_CathodeBlankCrate | CBC_Blanks, CBC_Frame | 1,788 |
| SM_SteelSparesCrate | SSC_Contents, SSC_Crate, SSC_Lid | 860 |
| SM_GasCylinderCage | GCC_Cage, GCC_Cylinders, GCC_GateL, GCC_GateR | 2,876 |

All parts are static and pivot at the prop origin (0, 0, 0), except SSC_Lid (pivot (0, 0, 0.80),
the top of the crate) and the gas cage gates below.

## Moving parts

| Part | Motion |
|---|---|
| GCC_GateL / GCC_GateR | Swing about local Z at the hinge posts (-0.80, -0.45, 0) and (0.80, -0.45, 0). Open outward: GateL -100°, GateR +100° |
| SSC_Lid | Lift off; in the display it leans against the crate |
| BP_Wrap, CB_Wrap, RS_Wrap | Shrink wrap shells: hide them to show the bricks or sacks, or give them a translucent material in Unreal |
| CBC_Blanks | Separate from CBC_Frame, so the empty crate can be reused |

## Dimensions

| Item | Value | Status |
|---|---|---|
| EUR pallet | 1200 x 800 x 144 mm, 5 top boards, 3 cross boards, 9 blocks, 3 bottom boards | Sourced (EPAL 1 / EN 13698-1 standard sizes, from memory of the standard; board widths approximate) |
| Refractory brick | 230 x 114 x 76 mm "9-inch straight", 175 per pallet | Brick size is the standard straight size (sourced from general refractory practice, not a specific supplier). Mass about 6 kg each in magnesia-chrome (about 3.0 t/m³, estimated), about 1.05 t per pallet |
| Castable sacks | 25 kg, 0.6 x 0.4 x 0.11 m, 40 per pallet (1.0 t) | Estimated |
| Reagent sacks | 25 kg paper sacks, 0.6 x 0.4 x 0.13 m, 32 per pallet (0.8 t), for glue, thiourea, flocculant | Estimated |
| Bulk bag (FIBC) | 0.9 x 0.9 x 1.1 m body, 4 loops, tied filling spout | Estimated, typical 1 m³ bag |
| IBC | 1200 x 1000 x 1160 mm, 1000 L, DN50 outlet valve on the +X short side | Sourced as the common industry size (from memory, typical of composite IBCs) |
| 200 L drum | 585 mm outside diameter, 880 mm high, 2 rolling hoops | Typical tight-head drum size (from memory, ISO 15750 range), not checked against a supplier |
| Cathode blank crate | 1.48 x 1.16 x 1.38 m, 20 blanks at 50 mm pitch, hanger bars rest on comb rails at z 1.26 | Blank: 1.040 x 1.050 m, 3.25 mm 316L blade, 1.32 m bar 25 x 35 mm, matches the tankhouse assets (Tools/Blender/AnodeCathodeMachines/acm_common.py). Crate is an own design |
| Steel spares crate | 1.6 x 1.0 x 0.8 m timber, lid separate | Estimated |
| Gas cylinder cage | 1.6 x 0.9 x 2.0 m, 10 x 50 L cylinders (230 mm diameter, about 1.6 m with cap) | Cylinder size typical (from memory); cage estimated. Shoulder colours follow EN 1089-3 (white oxygen, maroon acetylene, dark green argon, black nitrogen) |

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
