# SafetyEquipment

Safety props for the plant: emergency shower and eyewash, gas detection (SO₂ and arsine), alarm
devices, breathing-apparatus cabinets, a portable-detector charging rack and a small PPE store.
Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/WorkshopsSafetyLab/build_safety_equipment.py`; re-run it to rebuild.

Each prop has its own FBX built at its own origin, so it can be placed many times around the
plant. `SM_SafetyEquipment.blend` holds all of them in a display row (the locations below) in front
of a REF display wall. No logos or brand markings; sign panels are blank green or blue boards for
decals.

## Origins and placement

- Floor props (shower, pole detector, PPE store): origin at floor level, centre of the base.
- Wall props: origin on the wall face, the prop sticks out along local -Y. SM_EyewashStation and
  SM_SCBACabinet have the origin at floor level (their heights are built in). The others have the
  origin at the centre of the back face, so set Z to the mounting height.
- Suggested mounting heights (centre of the back face): fixed detector 1.5 m in the breathing
  zone, or 0.3-0.5 m where gas pools (see the note below); alarm beacon 2.3-2.5 m; extractive
  monitor and alarm panel 1.4-1.5 m; charging rack 1.3 m; respirator cabinet 1.5 m.
- Emergency showers and eyewashes are normally placed within 10 seconds' walk of the hazard
  (ANSI Z358.1). The shower needs about 1 m of clear floor around the spray.

## Files and parts

| FBX | Parts | Display location in the .blend |
|---|---|---|
| SM_EmergencyShower | ES_Eyewash_Caps, ES_Eyewash_PushFlag, ES_Shower_Body, ES_Shower_PullRod | (-8.0, -1.0, 0.0) |
| SM_EyewashStation | EW_Body, EW_Caps, EW_PushFlag | (-5.5, 0.0, 0.0) |
| SM_GasDetector_Fixed | GD_Fixed | (-3.8, 0.0, 1.5) |
| SM_GasAlarmBeacon | GD_AlarmBeacon | (-3.0, 0.0, 2.3) |
| SM_GasMonitor_Extractive | GD_Extractive | (-1.6, 0.0, 1.4) |
| SM_GasAlarmPanel | GD_AlarmPanel | (0.0, 0.0, 1.5) |
| SM_DetectorChargingRack | GD_ChargingRack | (1.6, 0.0, 1.3) |
| SM_GasDetector_Portable | GD_Portable | (1.6, -0.2, 0.9) |
| SM_RespiratorCabinet | RESP_Cabinet, RESP_Door | (3.4, 0.0, 1.5) |
| SM_SCBACabinet | SCBA_Cabinet, SCBA_Door | (5.2, 0.0, 0.0) |
| SM_GasDetector_Pole | GD_Pole | (7.5, -1.0, 0.0) |
| SM_PPEStore | PPE_Door, PPE_Floor, PPE_HatchFrame, PPE_HatchShutter, PPE_Interior, PPE_Resp_Cabinet, PPE_Resp_Door, PPE_Roof, PPE_SCBA_Cabinet, PPE_SCBA_Door, PPE_Vending, PPE_Walls | (0.0, 7.0, 0.0) |

## Moving parts

| Part | Motion |
|---|---|
| ES_Shower_PullRod | Pull = translate local -Z by about 0.08 m (pivot at the valve lever). |
| ES_Eyewash_PushFlag, EW_PushFlag | Turn about local Z at the valve stem, about 60°, to start the eyewash. |
| ES_Eyewash_Caps, EW_Caps | Flip open about local Y (ES) / local X (EW) by about 110° when the water starts. |
| SCBA_Door, PPE_SCBA_Door, RESP_Door, PPE_Resp_Door | Hinge on the left edge, rotate about local Z, up to about -110°. |
| PPE_Door | Hinge at floor level on the west edge of the door, rotate about local Z. |
| PPE_HatchShutter | Pivot at the top of the curtain; roll up = scale local Z from 1 to about 0.05. |

For a running shower or eyewash, spawn a Niagara water effect at the showerhead face
(0.60, 0, 2.20) or the bowl spray heads (shower: (0.38, ±0.05, 1.03); wall eyewash: (±0.05, -0.25, 1.03)).
The amber beacon on top of the shower is the flow-switch alarm many plants fit; light it when the
shower runs.

## PPE store

- Footprint 10 × 6 m outside (x -5 … 5, y -3 … 3), 3.3 m to the roof slab, 0.3 m parapet.
  Origin at floor level in the centre. Front faces -Y.
- Openings: issue hatch 1.6 × 1.0 m, sill 1.0 m, centred at x = -1.5 on the front wall, with a
  canopy and roller grille. Door 1.0 × 2.1 m centred at x = 3.0 on the front wall. Two windows on
  the back wall.
- Inside: issue counter behind the hatch, three shelving units with stock and hard hats, six
  lockers on the west wall, SCBA and respirator cabinets on the east wall, glove/boot cabinet.
  Outside: PPE vending machine next to the door.
- PPE_Roof is separate so it can be hidden for interior views.

## Gas detection notes

- SO₂ (molar mass 64) and arsine, AsH₃ (molar mass 78), are both heavier than air (29). Mounting
  guides put sensors for heavier-than-air gases low, about 0.15-0.3 m above the floor, but other
  guides say toxic-gas sensors go in the breathing zone at 1.2-1.8 m. The sources disagree; real
  plants decide per area from a hazard study. For gameplay, the breathing-zone height reads better.
- SO₂ is the main risk around the furnaces, converters and acid plant. Arsine is a risk at the
  liberator (decopperizing) cells in the tankhouse. Arsine is often monitored with extractive
  multipoint analysers that draw samples through tubes to one cabinet (SM_GasMonitor_Extractive).
  That last point is from general knowledge; I did not check it against a datasheet.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Showerhead face height | 2.20 m (standard: 2.083-2.438 m) | Sourced: ANSI/ISEA Z358.1-2014 summaries |
| Shower spray pattern | Ø0.51 m at 1.52 m above floor (for the effect) | Sourced: same |
| Eye/face wash flow height | ~1.03-1.05 m (standard: 0.838-1.346 m) | Sourced: same |
| Eyewash nozzles from wall | 0.25 m (standard: at least 0.153 m) | Sourced: same |
| Shower flow 76 L/min for 15 min, tepid water 16-38 °C | for gameplay/effects | Sourced: same |
| Fixed transmitter housing | 280 × 150 × 130 mm | Sourced: Dräger Polytron 8100 product page. Which axis is which is my guess |
| Pole detector: 3.0 m pole, transmitter at 1.6 m, sunshade, beacon | | Estimated |
| Portable multi-gas monitor | 70 × 35 × 125 mm | Estimated (typical handheld size) |
| Extractive monitor cabinet | 0.6 × 0.25 × 0.75 m | Estimated |
| Alarm panel 0.5 × 0.2 × 0.6 m, beacon/sounder | | Estimated |
| SCBA cabinet 0.7 × 0.4 × 1.0 m on 0.3 m legs, respirator cabinet 0.9 × 0.3 × 0.8 m | | Estimated |
| PPE store building and layout | | Own design |

Sources:
- ANSI/ISEA Z358.1-2014 summaries: Broen-Lab (https://safetywheel.broen-lab.com/wp-content/uploads/2024/07/ANSI-Z358.1_250624.pdf),
  Hughes Safety (https://www.hughes-safety.com/media/mageworx/downloads/attachment/file/a/n/ansi_summary_huk_26042021.pdf),
  CCOHS (https://ccohs.gc.ca/oshanswers/safety_haz/emer_showers.html). I used summaries, not the
  standard's own text.
- Dräger Polytron 8100 (https://www.draeger.com/en-us_us/Products/Draeger-Polytron-8100).
- Detector mounting heights: PK Safety (https://pksafety.com/blog/best-practices-for-fixed-gas-detector-installation-placement-location-and-maintenance/),
  gasdetection.com (https://gasdetection.com/articles/where-to-mount-a-fixed-toxic-gas-detector/).

## Unreal import

Combine Meshes off. Import each FBX with Transform Vertex to Absolute off so every part keeps its
own pivot; for one-part props it makes no difference. The Blender Y axis appears as -Y in Unreal
with the default FBX settings, so check rotation signs after import.

## Previews

Preview_Overview.png (display row), Preview_ShowerEyewash.png, Preview_GasDetection.png,
Preview_PPEStore.png (roof hidden).
