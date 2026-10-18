#!/bin/sh
# Rebuild every maintenance / mobile equipment asset (blend, fbx, previews, README).
# Usage: sh Tools/Blender/Maintenance/build_all.sh   (blender 5.2.x on PATH)
set -e
cd "$(dirname "$0")/../../.."
for s in build_demolition_robot build_mobile_equipment build_refractory_relining \
         build_skulling_mouth_cleaning build_crane_maintenance build_water_cooling build_spares_frp; do
    echo "== $s"
    blender -b --factory-startup --python "Tools/Blender/Maintenance/$s.py" > "/tmp/$s.log" 2>&1 \
        || { echo "failed, see /tmp/$s.log"; exit 1; }
    if grep -q "Traceback" "/tmp/$s.log"; then echo "python error, see /tmp/$s.log"; exit 1; fi
done
echo "all done"
