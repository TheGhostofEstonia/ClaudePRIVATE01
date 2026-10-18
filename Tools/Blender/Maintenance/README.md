# Maintenance and mobile equipment build scripts

Headless Blender 5.2.2 LTS scripts for the maintenance, relining and mobile equipment assets.
Each script writes `.blend`, `.fbx`, preview PNGs and a README into `Meshes/<Folder>/`.

```
sh Tools/Blender/Maintenance/build_all.sh                       # everything (~10 min on 4 CPUs)
blender -b --factory-startup --python Tools/Blender/Maintenance/build_mobile_equipment.py
blender -b --factory-startup --python Tools/Blender/Maintenance/build_mobile_equipment.py -- MobileCrane
```

A run with asset names after `--` rebuilds only those assets and leaves the folder README alone.

| Script | Output folder | Assets |
|---|---|---|
| build_demolition_robot.py | DemolitionRobot | SM_DemolitionRobot |
| build_refractory_relining.py | RefractoryRelining | SM_BrickConveyor, SM_LadleReliningTower, SM_GunningMachine, SM_GunningManipulator |
| build_skulling_mouth_cleaning.py | SkullingStations, ConverterMouthCleaner | SM_LadleSkullingStation, SM_PotSkullingStation, SM_ConverterMouthCleaner |
| build_crane_maintenance.py | CraneMaintenance | SM_CraneRunwayWalkway, SM_RopeChangingRig, SM_SpareHookBlocks |
| build_water_cooling.py | WaterCoolingCircuit | SM_FurnaceCoolingTower, SM_CoolingWaterPumpStation, SM_EmergencyWaterTank, SM_LeakDetectionManifold |
| build_mobile_equipment.py | MobileEquipment | SM_MobileCrane, SM_ScissorLift, SM_BoomLift, SM_ScaffoldTower, SM_ScaffoldKit, SM_VacuumTruck, SM_Sweeper |
| build_spares_frp.py | SparesAndFRP | SM_AcidPumpSpare, SM_PipeSpoolRack, SM_BaghouseSpares, SM_FRPRepairStation |

## Helpers

- `psh_build.py` is a copy of `Tools/Blender/psh_build.py` from the slag handling branch, unchanged,
  so this folder runs on its own. If both copies end up on main, either can be kept.
- `psh_maint.py` adds wheels, crawler tracks with panner UVs, hydraulic cylinder look-at pairs,
  stairs and guardrails, and `finish_asset` (save, export, render) plus the README writer.

## Conventions

Real-world metres, +X forward, Z up. Moving parts are separate objects with their pivot on the
joint. In the `.blend` they are parented for posing, and hydraulic cylinder halves use Damped
Track constraints to non-exported empties. The REF collection (scale figure, proxies, camera,
sun, ground) is never exported.
