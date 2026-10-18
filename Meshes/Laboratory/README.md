# SM_Laboratory

Plant assay and control laboratory: sample preparation, fire assay with balance room, instrument
room (WDXRF, spark OES, ICP-OES) and wet chemistry. Built in Blender 5.2.2 LTS (headless, cloud)
with `Tools/Blender/WorkshopsSafetyLab/build_laboratory.py`; re-run it to rebuild.

The building and room layout are my own design; I found no public drawings of a smelter lab.
Instrument sizes come from manufacturer pages or listings where noted below.

## Placement and footprint

- Origin: finished floor level (z = 0) at the centre of the building. +X east, +Y north.
- Footprint: x -18 … +18 m, y -9 … +9 m (36 × 18 m), walls 0.25 m, 4.5 m ceiling, flat roof
  with a 0.45 m parapet. Roof stacks reach z = 8.8 m.
- The dust collector stands outside the north wall at (-12, 11), so the overall footprint is
  y -9 … +12 m.
- Rooms: sample preparation x -18 … -6; fire assay x -6 … +6 with a glazed balance room at
  x 2 … 6, y 5 … 9; instrument room x 6 … 18, y -9 … 0; wet chemistry x 6 … 18, y 0 … 9.

### Doors

| Door | Centre (x, y) | Size W × H | Part |
|---|---|---|---|
| Sample delivery roller shutter (west) | (-18.0, 0.0) | 4.0 × 4.0 | LB_Shutter_West |
| Main entrance, double (south) | (12.0, -9.0) | 2.0 × 2.4 | LB_Door_Main_L / _R |
| Fire assay (south) | (0.0, -9.0) | 1.0 × 2.1 | LB_Door_South_FireAssay |
| Sample prep (north) | (-12.0, 9.0) | 1.0 × 2.1 | LB_Door_North_Prep |
| Wet chemistry (north) | (12.0, 9.0) | 1.0 × 2.1 | LB_Door_North_WetChem |
| Prep to fire assay, double | (-6.0, 5.4) | 2.0 × 2.4 | LB_Door_Prep_FireAssay_L / _R |
| Fire assay to instrument room | (6.0, -4.9) | 1.0 × 2.1 | LB_Door_FireAssay_Instrument |
| Fire assay to wet chemistry | (6.0, 5.1) | 1.0 × 2.1 | LB_Door_FireAssay_WetChem |
| Instrument room to wet chemistry | (12.0, 0.0) | 1.0 × 2.1 | LB_Door_Instrument_WetChem |
| Balance room | (2.75, 5.0) | 0.9 × 2.1 | LB_Door_BalanceRoom |

## Moving parts

| Part | Motion |
|---|---|
| LB_Shutter_West | Pivot at the top of the curtain; roll up = scale local Z from 1 to about 0.05. |
| LB_Door_* | Pivot on the hinge edge at floor level, leaf along local +X. Open = rotate about local Z by ±90°. |
| LB_FusionFurnace1/2_Door | Vertical-lift door: translate local +Z by 0.35 m to open. |
| LB_CupelFurnace1/2_Door | Bottom-hinged: rotate about local X by about -90° to drop it open. |
| LB_DryOven1/2_Door | Hinge on the left edge, rotate about local Z, up to about -110°. |
| LB_Pulverizer1/2_Lid | Hinged at the back, rotate about local X by about -75° to open. |
| LB_XRF_Lid | Sample-loader cover hinged at the back, rotate about local X by about -60°. |
| LB_Hood_*_Sash | Fume hood sash: translate local +Z, 0 (closed) to +0.75 m (open). |

The furnace mouths use an emissive material (M_Glow_Hot) so they read as hot in the previews.

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
| LB_BalanceRoom | (0.00, 0.00, 0.00) |
| LB_CupelFurnace1_Body | (-1.45, 8.30, 0.00) |
| LB_CupelFurnace1_Door | (-1.45, 7.91, 1.00) |
| LB_CupelFurnace2_Body | (-0.65, 8.30, 0.00) |
| LB_CupelFurnace2_Door | (-0.65, 7.91, 1.00) |
| LB_DoorFrames | (0.00, 0.00, 0.00) |
| LB_Door_BalanceRoom | (2.30, 5.00, 0.00) |
| LB_Door_FireAssay_Instrument | (6.00, -5.40, 0.00) |
| LB_Door_FireAssay_WetChem | (6.00, 4.60, 0.00) |
| LB_Door_Instrument_WetChem | (11.50, 0.00, 0.00) |
| LB_Door_Main_L | (11.00, -8.88, 0.00) |
| LB_Door_Main_R | (13.00, -8.88, 0.00) |
| LB_Door_North_Prep | (-12.50, 8.88, 0.00) |
| LB_Door_North_WetChem | (11.50, 8.88, 0.00) |
| LB_Door_Prep_FireAssay_L | (-6.00, 4.40, 0.00) |
| LB_Door_Prep_FireAssay_R | (-6.00, 6.40, 0.00) |
| LB_Door_South_FireAssay | (-0.50, -8.88, 0.00) |
| LB_DryOven1_Body | (-16.20, -8.20, 0.00) |
| LB_DryOven1_Door | (-15.48, -7.68, 0.05) |
| LB_DryOven2_Body | (-14.40, -8.20, 0.00) |
| LB_DryOven2_Door | (-13.68, -7.68, 0.05) |
| LB_DustCollector | (0.00, 0.00, 0.00) |
| LB_FireAssay_Static | (0.00, 0.00, 0.00) |
| LB_Floor | (0.00, 0.00, 0.00) |
| LB_FusionFurnace1_Body | (-4.60, 8.12, 0.00) |
| LB_FusionFurnace1_Door | (-4.60, 7.46, 0.90) |
| LB_FusionFurnace2_Body | (-2.90, 8.12, 0.00) |
| LB_FusionFurnace2_Door | (-2.90, 7.46, 0.90) |
| LB_Hood_Parting_Body | (0.00, 0.00, 0.00) |
| LB_Hood_Parting_Sash | (3.80, -7.99, 1.15) |
| LB_Hood_Wet1_Body | (0.00, 0.00, 0.00) |
| LB_Hood_Wet1_Sash | (8.20, 7.99, 1.15) |
| LB_Hood_Wet2_Body | (0.00, 0.00, 0.00) |
| LB_Hood_Wet2_Sash | (10.10, 7.99, 1.15) |
| LB_Hood_Wet3_Body | (0.00, 0.00, 0.00) |
| LB_Hood_Wet3_Sash | (14.00, 7.99, 1.15) |
| LB_Hood_Wet4_Body | (0.00, 0.00, 0.00) |
| LB_Hood_Wet4_Sash | (16.00, 7.99, 1.15) |
| LB_Instrument_Static | (0.00, 0.00, 0.00) |
| LB_Lights | (0.00, 0.00, 0.00) |
| LB_Prep_Static | (0.00, 0.00, 0.00) |
| LB_Pulverizer1_Body | (-13.00, 8.30, 0.00) |
| LB_Pulverizer1_Lid | (-13.00, 8.75, 1.00) |
| LB_Pulverizer2_Body | (-11.60, 8.30, 0.00) |
| LB_Pulverizer2_Lid | (-11.60, 8.75, 1.00) |
| LB_Roof | (0.00, 0.00, 0.00) |
| LB_RoofPlant | (0.00, 0.00, 0.00) |
| LB_Shutter_West | (-18.08, -0.00, 4.00) |
| LB_Walls | (0.00, 0.00, 0.00) |
| LB_WetChem_Static | (0.00, 0.00, 0.00) |
| LB_XRF_Body | (8.80, -7.20, 0.00) |
| LB_XRF_Lid | (8.80, -7.59, 1.35) |

## Unreal import

Combine Meshes off. With Transform Vertex to Absolute on, every part keeps the building origin as
its pivot, which suits the static parts. For the moving parts, import with it off and place each
part at the pivot above. The Blender Y axis appears as -Y in Unreal with the default FBX settings,
so check rotation signs after import. LB_Roof and LB_RoofPlant are separate so they can be hidden
for interior views. Suggested safety props from SafetyEquipment: an SM_EmergencyShower at
(7.0, 1.5, 0) in wet chemistry and at (-5.0, 0.0, 0) in fire assay; an SM_EyewashStation on the
wet chemistry island end.

## Dimensions

| Item | Value (W × D × H) | Status |
|---|---|---|
| WDXRF spectrometer (tube-above floor unit) | 1.31 × 0.89 × 1.47 m, ~620 kg | Sourced: Rigaku ZSX Primus IV product page |
| Spark OES, floor type | 0.79 × 0.625 × 1.35 m, 127 kg | Sourced: SPECTROMAXx listing on linkonbiz.com; the axis order is my guess |
| ICP-OES, benchtop | 0.625 × 0.74 × 0.887 m, ~90 kg | Sourced: Agilent 5800/5900 site preparation checklist |
| Fire assay (fusion) furnace, floor-standing | 1.45 × 1.22 × 2.16 m | Sourced: used MSA fire assay furnace listing (57 × 48 × 85 in) |
| Cupellation furnace, benchtop | 0.485 × 0.75 × 0.82 m on a 0.75 m stand | Sourced: Delmer D-C (18 cupels, 1150 °C) |
| Furnace canopy hood, stacks Ø0.7 to 8.8 m | | Estimated |
| Jaw crusher, ring-mill pulverisers, drying ovens, splitters, pellet press, fusion bead machine | | Estimated |
| Fume hoods 1.8 × 0.9 × 2.4 m | | Estimated (common size) |
| Building, rooms, door positions, dust collector | | Own design |

Sources: Rigaku ZSX Primus IV (https://rigaku.com/products/xrf-spectrometers/wdxrf/zsx-primus-iv);
SPECTROMAXx listing (https://linkonbiz.com/en/product/iframe-detail/1296); Agilent 5800/5900
site prep checklist (https://icpms.cz/paper/20842); MSA furnace (https://www.911metallurgist.com/fire-assay-furnace-for-sale);
Delmer cupellation furnaces (https://delmergroup.com/collections/cupellation-furnace).

## Files

- SM_Laboratory.blend / .fbx (the REF collection is not exported)
- Preview_Exterior.png, Preview_Cutaway.png, Preview_FireAssay.png, Preview_Instruments.png,
  Preview_SamplePrep.png (all but the exterior are rendered with the roof hidden)
