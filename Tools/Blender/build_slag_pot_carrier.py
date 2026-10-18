"""
build_slag_pot_carrier.py - SM_SlagPotCarrier (Kress-type U-frame slag pot carrier).

Run:  blender -b --factory-startup --python Tools/Blender/build_slag_pot_carrier.py

Local axes: +X = front (closed end, engine and cab), -X = open end where the pot
enters. Origin = ground point under the pot centre when the pot sits in the hooks.
The carrier reverses over the pot, hooks the trunnions, and the cradle rotates
about the rear axle line: front-up lifts the pot, ~140 deg inverts it behind
the machine (dump).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "Meshes", "SlagPotCarrier")
NAME = "SM_SlagPotCarrier"

# ---------------------------------------------------------------------------
# Parameters. Sourced: overall L/W/H. Everything else estimated.
# Change POT_* to match SM_SlagPots and re-run if the hooks do not line up.
# ---------------------------------------------------------------------------
LEN_REAR, LEN_FRONT = -4.60, 5.25      # 9.85 m overall (Kress at Mount Isa)
HALF_W = 2.85                          # 5.70 m overall width
TOP_Z = 4.40                           # 4.40 m overall height
TYRE_R, TYRE_W = 0.935, 0.65           # ~29.5R25 class tyre
WHEEL_Y = 2.425                        # wheel centre line
REAR_X, FRONT_X = -3.60, 3.95          # axle positions
POT_TRUNNION_Z = 1.80                  # trunnion axis height above pot base (assumed)
POT_TRUNNION_HALF_SPAN = 2.02          # trunnion tip at |y| (assumed)
POT_RIM_R, POT_BASE_R, POT_H = 1.80, 1.20, 2.60   # REF pot proxy, ~16 m3 inside
ARM_Y0, ARM_Y1 = 1.92, 2.04            # cradle side arm plates (|y|)
BEAM_Y0 = 2.10                         # inner face of frame side beams
PIVOT = Vector((REAR_X, 0.0, TYRE_R))  # cradle pivot = rear axle line (US4063658A)
HORN_LEN = 1.15                        # cradle lever horn above the pivot
CYL_ANCHOR_X, CYL_ANCHOR_Z = 0.50, 2.75


def build():
    sc = pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")

    # --- materials ---
    yellow = pb.mat("M_Carrier_Paint", (0.85, 0.55, 0.05), 0.2, 0.45)
    steel = pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5)
    grey = pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3)
    rubber = pb.mat("M_Tyre_Rubber", (0.03, 0.03, 0.03), 0.0, 0.85)
    glass = pb.mat("M_Glass_Cab", (0.05, 0.08, 0.1), 0.0, 0.05)
    red = pb.mat("M_FireSuppression_Red", (0.6, 0.03, 0.02), 0.1, 0.4)
    shield = pb.mat("M_HeatShield", (0.6, 0.6, 0.62), 0.9, 0.35)
    light = pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0))
    m = dict(yellow=yellow, steel=steel, grey=grey)

    # =====================================================================
    # CAR_Frame: U-frame, side beams, closed front, wheel legs (static)
    # =====================================================================
    fr = pb.Part("CAR_Frame")
    for s in (1, -1):
        # side beam over the tyres, full length
        fr.box_mm((LEN_REAR + 0.25, min(s * BEAM_Y0, s * HALF_W), 2.05),
                  (4.60, max(s * BEAM_Y0, s * HALF_W), 3.05), yellow)
        # rear wheel fork: outer plate down to the hub, inner bracket carrying the cradle pin
        fr.box_mm((REAR_X - 0.55, min(s * 2.76, s * HALF_W), 0.75),
                  (REAR_X + 0.55, max(s * 2.76, s * HALF_W), 2.05), yellow)
        fr.box_mm((REAR_X - 0.45, min(s * 2.045, s * BEAM_Y0), 0.70),
                  (REAR_X + 0.45, max(s * 2.045, s * BEAM_Y0), 2.05), yellow)
        fr.cyl(0.28, 0.12, (REAR_X, s * 2.80, TYRE_R), grey, rot=(90, 0, 0))
        # rear bumper block with tipping-edge wheel stop contact
        fr.box_mm((LEN_REAR + 0.05, min(s * BEAM_Y0, s * HALF_W), 2.05),
                  (LEN_REAR + 0.35, max(s * BEAM_Y0, s * HALF_W), 2.95), steel)
        # cylinder anchor lug under the beam
        fr.box_mm((CYL_ANCHOR_X - 0.2, min(s * 1.93, s * BEAM_Y0), CYL_ANCHOR_Z - 0.15),
                  (CYL_ANCHOR_X + 0.2, max(s * 1.93, s * BEAM_Y0), 2.05), steel)
        # travel-lock strut guide (US4063658A item 52)
        fr.box_mm((-1.6, min(s * 2.045, s * BEAM_Y0), 1.55), (-1.2, max(s * 2.045, s * BEAM_Y0), 2.05), steel)
        # front wheel arch housing
        fr.box_mm((FRONT_X - 1.15, min(s * 1.95, s * 2.05), 0.9), (FRONT_X + 1.15, max(s * 1.95, s * 2.05), 2.05), yellow)
        # steps and handrail along the beam top
        pb.handrail(fr, (-3.8, s * 2.80, 3.05), (2.4, s * 2.80, 3.05), yellow)
    # closed front: low crossmember between the front wheels + full-width deck
    fr.box_mm((2.45, -1.95, 0.75), (5.05, 1.95, 2.05), yellow)
    fr.box_mm((2.40, -HALF_W, 2.05), (5.10, HALF_W, 2.60), yellow)
    fr.box_mm((5.05, -2.2, 0.85), (LEN_FRONT, 2.2, 1.6), steel)        # front bumper
    # heat shield facing the pot (stainless plate on standoffs)
    fr.box_mm((2.30, -1.9, 0.80), (2.36, 1.9, 2.55), shield)
    for y in (-1.5, 0, 1.5):
        fr.box_mm((2.36, y - 0.05, 1.2), (2.45, y + 0.05, 2.3), steel)
    # deck plating ribs and front access ladder
    pb.ladder(fr, (LEN_FRONT - 0.05, -2.45, 0.4), 2.6, steel, facing=0)
    # fuel and hydraulic tanks on the deck sides
    fr.box_mm((2.6, -2.75, 2.6), (3.6, -2.0, 3.4), yellow)
    fr.cyl(0.45, 1.3, (3.1, 2.4, 1.45), steel, rot=(0, 90, 0))
    fr.finish(col)

    # =====================================================================
    # CAR_PowerModule: engine enclosure, radiator, exhaust (static)
    # =====================================================================
    pm = pb.Part("CAR_PowerModule")
    pm.box_mm((3.55, -1.95, 2.60), (5.10, 0.75, 3.85), yellow)
    pm.box_mm((5.10, -1.80, 2.75), (5.18, 0.60, 3.75), steel)            # radiator grille
    for z in [2.85 + 0.12 * i for i in range(8)]:
        pm.box_mm((5.18, -1.75, z), (5.22, 0.55, z + 0.05), grey)
    pm.cyl(0.11, 0.9, (3.8, -1.6, 3.95), steel, seg=12)                  # exhaust stack, top at 4.40
    pm.cyl(0.18, 0.5, (3.8, -1.6, 3.75), grey, seg=12)                   # muffler
    for y in (-1.95, 0.75):                                              # side louvres
        pm.box_mm((3.9, y - 0.02, 3.0), (4.8, y + 0.02, 3.6), steel)
    # fire suppression bottles (two systems at Mount Isa)
    for i, x in enumerate((2.65, 2.95)):
        pm.cyl(0.13, 0.9, (x, -1.55, 3.05), red, seg=12)
    pm.finish(col)

    # =====================================================================
    # CAR_Cab: operator cab on the left front corner, top = overall height
    # =====================================================================
    cab = pb.Part("CAR_Cab")
    cab.box_mm((2.70, 0.95, 2.60), (4.45, 2.75, 2.95), yellow)           # cab base
    cab.box_mm((2.70, 0.95, 4.25), (4.45, 2.75, TOP_Z), yellow)          # roof
    for x, y in ((2.72, 0.97), (4.43, 0.97), (2.72, 2.73), (4.43, 2.73)):
        cab.box((0.08, 0.08, 1.3), (x, y, 3.6), yellow)                   # pillars
    cab.box_mm((2.74, 0.99, 2.95), (4.41, 2.71, 4.25), glass)            # glazing volume
    cab.box_mm((2.55, 0.95, 2.95), (2.70, 2.75, 4.30), shield)           # rear heat shield (pot side)
    for y in (1.2, 2.5):
        cab.box((0.2, 0.15, 0.1), (4.5, y, 4.3), light)                  # work lights front
        cab.box((0.2, 0.15, 0.1), (2.5, y, 4.3), light)                  # work lights rear
    cab.box_mm((4.45, 2.70, 3.6), (4.55, 2.85, 3.9), steel)              # mirror
    cab.finish(col)

    # =====================================================================
    # Wheels: pivot on hub centre; spin about local Y, front pair also steers about Z
    # =====================================================================
    for tag, x in (("F", FRONT_X), ("R", REAR_X)):
        for side, s in (("L", 1), ("R", -1)):
            c = Vector((x, s * WHEEL_Y, TYRE_R))
            w = pb.Part(f"CAR_Wheel_{tag}{side}", pivot=c)
            w.cyl(TYRE_R, TYRE_W, c, rubber, rot=(90, 0, 0), seg=32)
            w.cyl(TYRE_R * 0.93, TYRE_W + 0.04, c, rubber, rot=(90, 0, 0), seg=32)  # shoulder
            # tread lugs so the spin reads in the game
            for i in range(20):
                a = 2 * math.pi * i / 20
                p = c + Vector((math.cos(a), 0, math.sin(a))) * (TYRE_R + 0.01)
                w.box((0.12, TYRE_W * 0.42, 0.05), p + Vector((0, s * 0.15, 0)), rubber,
                      rot=(0, -math.degrees(a) + 90, 0))
            w.cyl(0.62, TYRE_W + 0.08, c, yellow, rot=(90, 0, 0), seg=24)   # rim
            w.cyl(0.25, TYRE_W + 0.14, c, grey, rot=(90, 0, 0), seg=16)     # hub
            w.finish(col)

    # =====================================================================
    # CAR_Cradle: three-sided cradle with trunnion hooks, pivots on rear axle line
    # =====================================================================
    cr = pb.Part("CAR_Cradle", pivot=PIVOT)
    for s in (1, -1):
        y0, y1 = sorted((s * ARM_Y0, s * ARM_Y1))
        cr.box_mm((REAR_X - 0.45, y0, 0.55), (2.05, y1, 1.35), yellow)    # side arm
        cr.cyl(0.35, 0.14, (REAR_X, s * 1.98, TYRE_R), grey, rot=(90, 0, 0))  # pivot boss
        # trunnion hook: two jaws either side of the trunnion, seat below it
        tz = POT_TRUNNION_Z
        cr.box_mm((-0.55, y0, 1.35), (-0.24, y1, tz + 0.25), yellow)
        cr.box_mm((0.24, y0, 1.35), (0.55, y1, tz + 0.10), yellow)
        cr.box_mm((-0.24, y0, 1.35), (0.24, y1, tz - 0.23), steel)       # seat
        # pivoted lug stop over the trunnion (US4063658A item 35), shown latched
        cr.box_mm((-0.30, y0 - 0.02 * s, tz + 0.25), (0.30, y1, tz + 0.37), steel)
        # lever horn above the pivot for the lift cylinder
        cr.beam_between(PIVOT + Vector((0, s * 1.98, 0)),
                        PIVOT + Vector((0, s * 1.98, HORN_LEN)), 0.12, 0.45, yellow)
        cr.cyl(0.12, 0.2, PIVOT + Vector((0, s * 1.98, HORN_LEN)), grey, rot=(90, 0, 0))
        # travel-lock notch plate (item 53)
        cr.box_mm((-1.6, y0, 1.35), (-1.2, y1, 1.55), steel)
    # front cross member with the seat for the pot's tipping lug
    cr.box_mm((2.00, -ARM_Y1, 0.55), (2.28, ARM_Y1, 1.15), yellow)
    cr.box_mm((1.70, -0.45, 1.05), (2.00, 0.45, 1.15), steel)
    cr.finish(col)

    # =====================================================================
    # Lift cylinders: barrel pivots at the frame lug, rod pivots at the horn.
    # Local +X of each part points along the cylinder; Damped Track keeps it aimed.
    # =====================================================================
    cyl_parts = {}
    for side, s in (("L", 1), ("R", -1)):
        a = Vector((CYL_ANCHOR_X, s * 1.98, CYL_ANCHOR_Z))
        b = PIVOT + Vector((0, s * 1.98, HORN_LEN))
        d = (b - a).normalized()
        bar = pb.Part(f"CAR_LiftCyl_{side}_Barrel", pivot=a)
        bar.cyl_between(a, a + d * 3.2, 0.17, yellow, seg=16)
        bar.cyl_between(a - d * 0.15, a + d * 0.15, 0.10, grey, seg=12)  # eye
        bar.cyl(0.10, 0.2, a, grey, rot=(90, 0, 0))
        rod = pb.Part(f"CAR_LiftCyl_{side}_Rod", pivot=b)
        rod.cyl_between(b, b - d * 3.3, 0.09, grey, seg=12)
        rod.cyl(0.09, 0.22, b, grey, rot=(90, 0, 0))
        cyl_parts[side] = (bar.finish(col, x_toward=b), rod.finish(col, x_toward=a))

    # =====================================================================
    # REF collection (not exported): proxy pot, human, ground plate
    # =====================================================================
    pot = pb.Part("REF_SlagPot_Proxy", pivot=(0, 0, POT_TRUNNION_Z))
    pm_ = pb.mat("M_REF_Pot", (0.25, 0.22, 0.2), 0.7, 0.6)
    slag = pb.mat("M_REF_Slag", (1.0, 0.35, 0.05), 0, 0.5, emit=((1, 0.3, 0.05), 6.0))
    pot.cyl(POT_BASE_R, POT_H, (0, 0, POT_H / 2), pm_, seg=32, r2=POT_RIM_R)
    pot.cyl(0.9, 0.3, (0, 0, 0.15), pm_, seg=24)
    pot.cyl(POT_RIM_R - 0.15, 0.05, (0, 0, POT_H - 0.25), slag, seg=32)
    for s in (1, -1):
        pot.cyl_between((0, s * 1.40, POT_TRUNNION_Z), (0, s * POT_TRUNNION_HALF_SPAN, POT_TRUNNION_Z),
                        0.21, pm_, seg=16)
    pot.box_mm((1.40, -0.40, 1.15), (2.0, 0.40, 1.45), pm_)              # tipping lug
    pot_ob = pot.finish(ref)
    pb.ref_human(ref, (6.2, -1.0, 0))
    g = pb.Part("REF_Ground")
    g.box((60, 60, 0.1), (0, 0, -0.05), pb.mat("M_REF_Ground", (0.3, 0.28, 0.25), 0, 0.9))
    g.finish(ref)

    return col, cyl_parts, pot_ob


def rig_for_preview(cyl_parts, pot_ob):
    """Blender-only rig: rods and pot follow the cradle, cylinders aim at each other."""
    cradle = bpy.data.objects["CAR_Cradle"]
    for side, (bar, rod) in cyl_parts.items():
        mw = rod.matrix_world.copy()
        rod.parent = cradle
        rod.matrix_world = mw
        # static empty on the barrel pivot avoids a barrel<->rod dependency cycle
        anchor = bpy.data.objects.new(f"RIG_CylAnchor_{side}", None)
        anchor.location = bar.matrix_world.translation
        pb.collection("REF").objects.link(anchor)
        c = bar.constraints.new('DAMPED_TRACK'); c.target = rod; c.track_axis = 'TRACK_X'
        c = rod.constraints.new('DAMPED_TRACK'); c.target = anchor; c.track_axis = 'TRACK_X'
    mw = pot_ob.matrix_world.copy()
    pot_ob.parent = cradle
    pot_ob.matrix_world = mw


def write_readme(col):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_SlagPotCarrier

Kress-type U-frame slag pot carrier for the ~16 m³ slag pots. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/build_slag_pot_carrier.py`; re-run the script to rebuild.

## Placement

- Local axes: +X front (closed end, engine, cab), -X open end. Origin is the ground point under
  the pot centre when the pot is in the hooks.
- To pick up a pot, place the carrier origin on the pot's ground centre with the open end facing
  the pot. At the slag pot pit, pots are at (46.0, 8.8, -5.5) and (46.0, 15.3, -5.5) in flash
  furnace coordinates and the carrier enters from the east, so carrier yaw is 0 (front facing +X)
  and the carrier reverses west over the pot.
- This assumes the pot trunnions point along ±Y (north-south). If SM_SlagPots has its trunnions
  along X, rotate the pot or the carrier 90°. I could not read SM_SlagPots from the cloud
  environment, so the hook height (1.80 m) and trunnion span (4.04 m tip to tip, sitting in hooks 3.84 m apart) are assumed.
  Change `POT_TRUNNION_Z` and `POT_TRUNNION_HALF_SPAN` in the script and re-run to match.

## Moving parts

| Part | Motion | Pivot / axis |
|---|---|---|
| CAR_Cradle | Rotates about local Y. Front up lifts the pot. Travel pose ≈ 12° front-up, dump ≈ 140° (the patent figure). In Blender that is rotation Y = -12° and -140°. | Rear axle line (-3.60, 0, 0.935) |
| CAR_Wheel_FL/FR/RL/RR | Spin about local Y. FL/FR also steer about local Z. | Hub centre |
| CAR_LiftCyl_L/R_Barrel | Aim local +X at the matching rod pivot | Frame lug (0.50, ±1.98, 2.75) |
| CAR_LiftCyl_L/R_Rod | Moves with the cradle horn; aim local +X at the barrel pivot | Horn tip, attached to the cradle |

In the .blend the rods and the REF pot proxy are parented to CAR_Cradle and the cylinders have
Damped Track constraints, so rotating CAR_Cradle poses the whole mechanism. In Unreal, attach the
rods (and the pot) to the cradle component and use a look-at for the two cylinder halves.

Tyre circumference = 2π × 0.935 = 5.87 m, so wheel spin (deg/s) = speed (m/s) × 61.3.

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

## Unreal import

Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves the pivot to the asset origin. For the moving parts, import with it off and place
each part at the pivot listed above. The Blender Y axis appears as -Y in Unreal with the default
FBX settings, so check rotation signs after import.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Overall length × width × height | 9.85 × 5.70 × 4.40 m | Sourced: Kress carriers at Mount Isa (Glencore, 2020) |
| Full pot handled | 75-80 t at Mount Isa | Sourced (same article); our pot is smaller |
| Cradle pivots on the rear wheel axis, hooks + lug stops on trunnions, seat under the pot's end lug, ~140° tip, travel-lock struts | Layout | Sourced: US4063658A (now Kress) |
| Lift by a single cylinder on a horn above the pivot | Mechanism | Own design. The patent uses a lever and link per side; I simplified it to one cylinder so it animates with a look-at. |
| Tyres ≈ 1.87 m dia × 0.65 m (29.5R25 class) | | Estimated |
| Axles at x = -3.60 and +3.95, cab on the left front corner, engine module on the front deck | | Estimated from photos, no drawings |
| Hook height 1.80 m, trunnion span 4.04 m, clear width between the cradle arms 3.84 m | | Assumed to suit the ~16 m³ pot |
| REF pot proxy: rim Ø3.6, base Ø2.4, 2.6 m tall | | Assumed, for previews only |

Sources: Glencore "Around for the long haul: Kress slag pot carriers" (Resourceful, Dec 2020) as
cited in research/copper-refinery/copper-refinery-equipment.md [S8]; US4063658A
(https://patents.google.com/patent/US4063658A/en); Kress product page
(https://kresscarrier.com/CarriersSlagPot.html: carriers up to 227 t, pots up to 45 m³).

## Files

- SM_SlagPotCarrier.blend / .fbx (the REF collection is not exported)
- Preview_Overview.png (pot in hooks), Preview_Travel.png, Preview_Dump.png
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, cyl_parts, pot_ob = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    rig_for_preview(cyl_parts, pot_ob)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render()
    cradle = bpy.data.objects["CAR_Cradle"]
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (-12, -15, 8), (0.5, 0, 1.6))
    cradle.rotation_euler.y = math.radians(-12)
    pb.render_view(os.path.join(OUT, "Preview_Travel.png"), (14, -13, 7), (0, 0, 1.8))
    cradle.rotation_euler.y = math.radians(-140)
    pb.render_view(os.path.join(OUT, "Preview_Dump.png"), (-6, -19, 5), (-3, 0, 2.2))
    cradle.rotation_euler.y = 0.0


main()
