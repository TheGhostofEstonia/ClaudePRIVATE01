# Project Safe Haven assets

Meshes for the PSH Unreal project. Each asset folder under `Meshes/` holds the `.blend`, the `.fbx`
for Unreal, preview renders and a README with dimensions, pivots and connection points.
Build scripts for assets made in the cloud environment are in `Tools/Blender/`.

All build scripts import the shared helper module `Tools/Blender/psh_build.py`. Scripts for one
set live in their own subfolder (`Tankhouse/`, `AnodeCathodeMachines/`, `ByproductsRod/`,
`Maintenance/`, `WorkshopsSafetyLab/`, `Logistics/`) next to any set-specific helpers; the slag handling
scripts sit directly in `Tools/Blender/`. Run any of them headless with
`blender -b --factory-startup --python Tools/Blender/<path>/build_<name>.py`.
