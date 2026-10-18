#!/usr/bin/env bash
# Rebuilds every tankhouse asset in dependency order, renders the plant overview and runs the
# clearance checks. Usage: BLENDER=/path/to/blender ./build_all.sh [--no-render]
set -euo pipefail
cd "$(dirname "$0")"
B="${BLENDER:-blender}"
for s in build_permanent_cathode build_electrolytic_cell build_tankhouse_crane build_tankhouse_building \
         build_rectifier_busbar build_electrolyte_circulation build_liberator_cells \
         build_short_circuit_detection; do
  echo "== $s"
  "$B" -b --factory-startup --python "$s.py" -- "$@"
done
if [[ "${1:-}" != "--no-render" ]]; then
  "$B" -b --factory-startup --python render_tankhouse_overview.py
fi
"$B" -b --factory-startup --python check_tankhouse.py | grep -E "^(PASS|FAIL)"
