# Logistics build scripts

Headless Blender 5.2.2 LTS scripts for the inbound, outbound and on-site logistics assets
(section 12 of the copper refinery equipment research). Each script writes `.blend`, `.fbx`,
preview PNGs and a README into `Meshes/<Folder>/`.

```
sh Tools/Blender/Logistics/build_all.sh                        # everything
blender -b --factory-startup --python Tools/Blender/Logistics/build_road_vehicles.py
blender -b --factory-startup --python Tools/Blender/Logistics/build_road_vehicles.py -- TractorUnit
```

A run with asset names after `--` rebuilds only those assets and leaves the folder README alone.

| Script | Output folder(s) | Assets |
|---|---|---|
| build_rail_vehicles.py | RailVehicles | SM_ShuntingLocomotive, SM_HopperWagon, SM_SideTipWagon, SM_FlatWagon, SM_AcidTankWagon |
| build_rail_track.py | RailTrackKit | SM_Track_Straight_10m, SM_Track_Straight_2m5, SM_Track_Curve_R190_15deg, SM_Turnout_1to9_Left, SM_BufferStop, SM_LevelCrossingPanel |
| build_plant_rail_cars.py | LadleTransferCar, AnodeTransferCar | SM_LadleTransferCar, SM_AnodeTransferCar |
| build_road_vehicles.py | RoadVehicles | SM_TractorUnit, SM_TipperTrailer, SM_FlatbedTrailer, SM_AcidTankTrailer, SM_Container20ft, SM_FlatbedTruck, SM_SecureVan |
| build_yard_equipment.py | YardEquipment | SM_WheelLoader, SM_SkidSteer, SM_HeavyForklift16t, SM_Forklift3t, SM_TuggerTrain |
| build_weighbridge_sampling.py | Weighbridge, SamplingStation | SM_Weighbridge, SM_SamplingStation |
| build_warehouse.py | Warehouse, Consumables | SM_Warehouse, SM_PalletRackBay, SM_PalletRackFrame, 10 consumable props |
| build_utilities.py | Substation, OxygenPlant, FuelStorage, FluxStorage | SM_Substation, SM_OxygenPlant, SM_FuelOilTankFarm, SM_GasMeteringStation, SM_FluxStorage |

## Helpers

- `psh_logi.py` puts `Tools/Blender` (shared `psh_build.py`) and `Tools/Blender/Maintenance`
  (`psh_maint.py`: wheels, hydraulic cylinders, stairs, `finish_asset`, README writer) on
  `sys.path`, and adds rail running gear (wheelsets, bogies, UIC buffers, underframes) and road
  axles.

## Conventions

- Real-world metres, Z up. Vehicles: +X forward, origin on the ground (road) or on the track
  centre at top of rail (rail). Fixed facilities: origin on the ground, +X east, +Y north, not
  placed in the plant; each README lists footprint and connection points.
- Rail: standard gauge 1.435 m, UIC buffers 1.06 m high and 1.75 m apart.
- Road: tractor origin is the ground under the fifth-wheel centre and each trailer's origin is the
  ground under its kingpin (both at z 1.20), so a trailer placed at the tractor origin is coupled.
- Moving parts are separate objects with their pivot on the joint. The REF collection is never
  exported.
