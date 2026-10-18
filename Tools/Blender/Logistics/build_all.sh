#!/bin/sh
# Rebuild every logistics asset (blend, fbx, previews, README).
# Usage: sh Tools/Blender/Logistics/build_all.sh   (blender 5.2.x on PATH)
set -e
cd "$(dirname "$0")/../../.."
for s in build_rail_vehicles build_rail_track build_plant_rail_cars build_road_vehicles \
         build_yard_equipment build_weighbridge_sampling build_warehouse build_utilities; do
    echo "== $s"
    blender -b --factory-startup --python "Tools/Blender/Logistics/$s.py" > "/tmp/$s.log" 2>&1 \
        || { echo "failed, see /tmp/$s.log"; exit 1; }
    if grep -q "Traceback" "/tmp/$s.log"; then echo "python error, see /tmp/$s.log"; exit 1; fi
done
echo "all done"
