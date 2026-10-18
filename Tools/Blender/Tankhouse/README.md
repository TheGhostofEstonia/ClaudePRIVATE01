# Tankhouse build scripts

Headless Blender 5.2.2 scripts for the copper electrorefining tankhouse assets in `Meshes/`.

| Script | Output folder |
|---|---|
| `th_layout.py` | shared layout constants (origin, cell pitch, rows, seat height, crane rails, transfer points), materials and preview helpers. Imports `../psh_build.py` |
| `build_permanent_cathode.py` | `Meshes/PermanentCathode` |
| `build_electrolytic_cell.py` | `Meshes/ElectrolyticCell` |
| `build_tankhouse_crane.py` | `Meshes/TankhouseCrane` |
| `build_tankhouse_building.py` | `Meshes/Tankhouse` (hall, basement, runway, transfer stands; its README is the layout reference) |
| `build_rectifier_busbar.py` | `Meshes/RectifierBusbar` |
| `build_electrolyte_circulation.py` | `Meshes/ElectrolyteCirculation` |
| `build_liberator_cells.py` | `Meshes/LiberatorCells` |
| `build_short_circuit_detection.py` | `Meshes/ShortCircuitDetection` |
| `render_tankhouse_overview.py` | `Meshes/Tankhouse/Preview_PlantOverview.png`, `Preview_PlantCutaway.png` |
| `check_tankhouse.py` | prints PASS/FAIL clearance checks (electrodes in cells, crane hooks, carried loads) |

Run everything in order:

```
BLENDER=/path/to/blender ./build_all.sh            # add --no-render to skip previews
```

or one script: `blender -b --factory-startup --python build_<asset>.py [-- --no-render]`.
The later scripts load earlier `.blend` files for their previews, so build in the order above.
To change the layout (cell count, pitch, row positions, crane height), edit `th_layout.py` and
rebuild all.
