"""
build_demolition_robot.py - SM_DemolitionRobot (remote-controlled demolition robot, 3.6 t class).

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_demolition_robot.py

Generic machine in the Brokk 300 size class (no branding). Local axes: +X = arm side.
Origin = ground point under the slewing centre. The arm is modelled stretched out
horizontally (rest pose); the README gives the working and transport angles.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

NAME = "SM_DemolitionRobot"
FOLDER = "DemolitionRobot"

# ---------------------------------------------------------------------------
# Parameters (m). Sourced: width 1.20, height 1.53, tail swing dia 1.827, reach 6.1 m.
# ---------------------------------------------------------------------------
HALF_W = 0.60            # minimum width 1200 mm (Brokk 300 data)
TOP_Z = 1.53             # minimum height 1530 mm (Brokk 300 data)
SWING_R = 0.913          # tail swing diameter 1827 mm (Brokk 300 sheet drawing)
TRK_R, TRK_W, TRK_Y = 0.19, 0.24, 0.48     # track idler radius, shoe width, track centre line
TRK_X0, TRK_X1 = -0.72, 0.72               # idler centres (estimated, ~1.8 m track length)
SLEW_Z = 0.62            # top of the undercarriage / slew ring
BOOM_P = (0.30, 0.0, 0.95)                 # boom foot pin
L_BOOM, L_ARM, L_TOOLARM, L_BREAKER = 1.95, 1.75, 1.00, 1.05   # sums to ~6.1 m reach
OUT_PIV = [(0.78, 0.50), (-0.78, 0.50), (0.78, -0.50), (-0.78, -0.50)]   # outrigger pins (x, y)
OUT_Z, OUT_LEN, OUT_STOW_DEG = 0.55, 0.80, 70.0


def build():
    col, ref, m = pm.start(NAME)
    m['body'] = m['orange']      # generic hi-vis orange, no logos
    x0 = BOOM_P[0]

    # --- undercarriage (static) and tracks (UV loop) ---
    ch = pb.Part("DR_Chassis")
    for s in (1, -1):
        pm.track_frame(ch, TRK_X0, TRK_X1, s * TRK_Y, TRK_R, TRK_W, m)
    ch.box_mm((-0.80, -0.36, 0.22), (0.80, 0.36, SLEW_Z - 0.05), m['steel'])
    ch.cyl(0.55, 0.05, (0, 0, SLEW_Z - 0.025), m['grey'], seg=32)          # slew ring
    for (x, y) in OUT_PIV:   # outrigger brackets
        ch.box((0.22, 0.16, 0.22), (x, y * 0.86, OUT_Z), m['steel'])
    ob_ch = ch.finish(col)
    for s, tag in ((1, "L"), (-1, "R")):
        pm.track(f"DR_Track_{tag}", TRK_X0, TRK_X1, s * TRK_Y, TRK_R, TRK_W, col, m)

    # --- outriggers: pin axis along X, stowed raised OUT_STOW_DEG above horizontal ---
    import math
    from mathutils import Vector
    outs = []
    for (x, y) in OUT_PIV:
        s = 1 if y > 0 else -1
        tag = ("F" if x > 0 else "R") + ("L" if s > 0 else "R")
        pv = Vector((x, y, OUT_Z))
        a = math.radians(OUT_STOW_DEG)
        tip = pv + Vector((0, s * math.cos(a), math.sin(a))) * OUT_LEN
        o = pb.Part(f"DR_Outrigger_{tag}", pivot=pv)
        o.beam_between(pv, tip, 0.12, 0.14, m['body'])
        o.cyl(0.1, 0.18, pv, m['grey'], rot=(0, 90, 0), seg=12)
        o.cyl(0.13, 0.05, tip + Vector((0, s * 0.03, 0.02)), m['steel'],
              rot=(-s * (90 - OUT_STOW_DEG), 0, 0), seg=16)                  # foot pad
        outs.append(o.finish(col))

    # --- turret: slews about Z; power pack, rounded tail inside SWING_R ---
    tu = pb.Part("DR_Turret", pivot=(0, 0, SLEW_Z))
    tail = [(SWING_R * math.cos(math.radians(t)), SWING_R * math.sin(math.radians(t)))
            for t in range(110, 251, 10)]
    tu.poly_prism([(0.45, 0.58), *tail, (0.45, -0.58)], SLEW_Z, 1.32, m['body'])
    tu.box_mm((-0.70, -0.48, 1.32), (0.15, 0.48, TOP_Z), m['body'])            # top cover
    tu.box_mm((-0.62, -0.42, TOP_Z - 0.02), (-0.20, 0.42, TOP_Z + 0.0), m['steel'])  # vent grille
    for s in (1, -1):   # boom foot cheeks
        tu.box_mm((0.10, s * 0.13 - 0.04, SLEW_Z), (0.45, s * 0.13 + 0.04, 1.15), m['steel'])
    tu.cyl(0.06, 0.40, BOOM_P, m['grey'], rot=(90, 0, 0), seg=12)
    tu.box_mm((0.20, -0.12, SLEW_Z), (0.62, 0.12, 0.62 + 0.12), m['steel'])   # boom cylinder foot
    for z in (0.95, 1.05, 1.15):  # hose bundle to the arm
        tu.cyl_between((-0.1, 0.3, z), (0.25, 0.22, z + 0.05), 0.02, m['rubber'], seg=8)
    tu.box_mm((-0.86, -0.12, 0.95), (-0.80, 0.12, 1.10), m['lamp'])             # rear work lamp
    ob_tu = tu.finish(col)

    # --- arm system (rest pose: straight along +X at the boom pin height) ---
    z = BOOM_P[2]
    j1, j2, j3, j4 = x0 + L_BOOM, x0 + L_BOOM + L_ARM, x0 + L_BOOM + L_ARM + L_TOOLARM, None
    j4 = j3 + L_BREAKER

    bo = pb.Part("DR_Boom", pivot=BOOM_P)
    bo.box_mm((x0, -0.11, z - 0.13), (j1, 0.11, z + 0.13), m['body'])
    bo.box_mm((x0 + 0.45, -0.06, z + 0.13), (x0 + 0.85, 0.06, z + 0.26), m['steel'])  # arm cyl lug
    bo.box_mm((x0 + 0.85, -0.06, z - 0.22), (x0 + 1.15, 0.06, z - 0.13), m['steel'])  # boom cyl lug
    bo.cyl(0.06, 0.30, (j1, 0, z), m['grey'], rot=(90, 0, 0), seg=12)
    ob_bo = bo.finish(col)

    ar = pb.Part("DR_Arm", pivot=(j1, 0, z))
    ar.box_mm((j1 - 0.10, -0.095, z - 0.11), (j2, 0.095, z + 0.11), m['body'])
    ar.box_mm((j1 + 0.05, -0.05, z + 0.11), (j1 + 0.30, 0.05, z + 0.24), m['steel'])
    ar.box_mm((j1 + 0.70, -0.05, z + 0.11), (j1 + 1.00, 0.05, z + 0.22), m['steel'])
    ar.cyl(0.055, 0.26, (j2, 0, z), m['grey'], rot=(90, 0, 0), seg=12)
    ob_ar = ar.finish(col)

    ta = pb.Part("DR_ToolArm", pivot=(j2, 0, z))
    ta.box_mm((j2 - 0.08, -0.085, z - 0.10), (j3, 0.085, z + 0.10), m['body'])
    ta.box_mm((j2 + 0.15, -0.05, z - 0.20), (j2 + 0.40, 0.05, z - 0.10), m['steel'])
    ta.cyl(0.05, 0.24, (j3, 0, z), m['grey'], rot=(90, 0, 0), seg=12)
    ob_ta = ta.finish(col)

    br = pb.Part("DR_Breaker", pivot=(j3, 0, z))
    br.box_mm((j3 - 0.05, -0.11, z - 0.16), (j3 + 0.12, 0.11, z + 0.16), m['steel'])   # adapter
    br.box_mm((j3 + 0.12, -0.13, z - 0.13), (j4 - 0.30, 0.13, z + 0.13), m['body'])    # hammer body
    br.cyl_between((j4 - 0.30, 0, z), (j4 - 0.05, 0, z), 0.045, m['grey'], seg=12)     # chisel
    br.cyl_between((j4 - 0.05, 0, z), (j4, 0, z), 0.045, m['grey'], seg=12, r2=0.008)
    ob_br = br.finish(col)


    # --- hierarchy for posing in the .blend (cylinders are parented by hyd_cyl) ---
    pm.parent(ob_tu, ob_ch)
    for o in outs:
        pm.parent(o, ob_ch)
    pm.parent(ob_bo, ob_tu)
    pm.parent(ob_ar, ob_bo)
    pm.parent(ob_ta, ob_ar)
    pm.parent(ob_br, ob_ta)
    # hydraulic cylinders: barrel rides on the first part, rod on the second
    pm.hyd_cyl("DR_BoomCyl", (0.45, 0, 0.72), (x0 + 1.0, 0, z - 0.20), 0.06, col, m, ob_tu, ob_bo)
    pm.hyd_cyl("DR_ArmCyl", (x0 + 0.65, 0, z + 0.22), (j1 + 0.17, 0, z + 0.20), 0.055, col, m, ob_bo, ob_ar)
    pm.hyd_cyl("DR_ToolArmCyl", (j1 + 0.85, 0, z + 0.18), (j2, 0, z + 0.17), 0.05, col, m, ob_ar, ob_ta)
    pm.hyd_cyl("DR_BreakerCyl", (j2 + 0.28, 0, z - 0.17), (j3 + 0.05, 0, z - 0.17), 0.045, col, m, ob_ta, ob_br)

    pb.ref_human(ref, (-1.2, 1.6, 0))

    def pose():
        """Working pose: outriggers down, turret 25 deg, boom up, breaker pointing down."""
        ob_tu.rotation_euler.z = math.radians(25)
        for o in outs:
            s = 1 if o.name[-1] == "L" else -1
            o.rotation_euler.x = math.radians(-s * 118)
        ob_bo.rotation_euler.y = math.radians(-48)
        ob_ar.rotation_euler.y = math.radians(55)
        ob_ta.rotation_euler.y = math.radians(15)
        ob_br.rotation_euler.y = math.radians(25)

    n_obj, n_tri = pm.counts(NAME)
    table = pm.finish_asset(NAME, FOLDER, [
        ("Preview_Rest.png", (6.5, -9.0, 4.0), (2.6, 0, 0.7), 35),
        ("Preview_Working.png", (6.0, -6.0, 3.5), (1.6, 0, 1.4), 35, True),
    ], pose=pose)
    return table, n_obj, n_tri


def readme(table, n_obj, n_tri):
    pm.write_readme(FOLDER, NAME, f"""
Remote-controlled demolition robot for refractory tear-out in converters, ladles and furnaces.
Generic machine in the 3.6 t class (Brokk 300 size), no branding. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_demolition_robot.py`. {n_obj} parts, about
{n_tri:,} triangles.

Local axes: +X is the arm side. Origin is the ground point under the slewing centre. The arm is
modelled stretched out level along +X (rest pose).
""", [
        ("Moving parts", """
| Part | Motion |
|---|---|
| DR_Turret | Slews about local Z (360°, 16 s per turn on the real machine) |
| DR_Outrigger_FL/FR/RL/RR | Rotate about local X. Modelled stowed at 70° above horizontal. Deployed (pad on the ground) is X = about -118° for the L legs and +118° for the R legs |
| DR_Boom, DR_Arm, DR_ToolArm, DR_Breaker | Rotate about local Y. Negative Y raises the boom; positive Y folds the next segment down |
| DR_*Cyl_Barrel / DR_*Cyl_Rod | Look-at pairs: each aims local +X at the other's pivot (Damped Track in the .blend) |
| DR_Track_L/R | UV U runs along the loop (1 U = 1 m), so panner U speed = track speed in m/s |

Preview working pose: turret 25°, boom -48°, arm +55°, tool arm +15°, breaker +25°.
A transport pose (arm folded over the body) is about boom -75°, arm +165°, tool arm +120°;
check for clipping, it was not test-rendered.

The parent chain in the .blend is Chassis > Turret > Boom > Arm > ToolArm > Breaker, with the
outriggers on the chassis and each cylinder half on the part it is pinned to. Rebuild the same
chain in an Unreal Blueprint.
"""),
        ("Pivot coordinates", "| Object | Pivot (Blender X, Y, Z) |\n|---|---|\n" + table),
        ("Unreal import", pm.UNREAL_NOTE),
        ("Dimensions", """
| Item | Value | Status |
|---|---|---|
| Minimum width × height | 1.20 × 1.53 m | Sourced: Brokk 300 product page / sheet |
| Tail swing diameter | 1.827 m | Sourced: Brokk 300 product sheet drawing |
| Reach, horizontal / vertical, incl. breaker | 6.1 / 6.5 m | Sourced (same sheet) |
| Machine weight | 3,650 kg without attachment | Sourced (same sheet) |
| Track length ~1.8 m, outrigger length 0.8 m, arm split 1.95 / 1.75 / 1.00 / 1.05 m | | Estimated from photos so the total reach matches |
| Breaker shape and size | | Estimated |

Sources: https://www.brokk.com/us/product/brokk-300/ and
https://www.brokk.com/uploads/2020/07/brokk300_product_sheet.pdf. Use at a reline: Mount Isa anode
furnace rebrick 2024, where a Brokk broke out the refractory (research file [S22]).
"""),
        ("Files", "SM_DemolitionRobot.blend / .fbx, Preview_Rest.png, Preview_Working.png"),
    ])


if __name__ == "__main__":
    readme(*build())
