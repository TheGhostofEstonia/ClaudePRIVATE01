"""
build_refractory_relining.py - refractory relining gear, each a standalone prop at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_refractory_relining.py
      (add  -- BrickConveyor  to build one asset only)

Assets (Meshes/RefractoryRelining/):
    SM_BrickConveyor        mobile inclined brick conveyor (feeds bricks up into a vessel mouth)
    SM_LadleReliningTower   frame over a ladle with a rising/rotating bricklaying deck and brick hoist
    SM_GunningMachine       dry-process rotor gunning machine with hose and nozzle
    SM_GunningManipulator   wheeled hot-gunning manipulator with a telescopic lance
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

FOLDER = "RefractoryRelining"


def brick_stack(p, x0, y0, z0, nx, ny, nz, m, size=(0.23, 0.114, 0.076)):
    """Pallet-style stack of standard 230 x 114 x 76 mm bricks (simplified as one box per course)."""
    w, d, h = size
    p.box_mm((x0, y0, z0), (x0 + nx * w, y0 + ny * d, z0 + nz * h), m['refr'])


# ===========================================================================
# Brick conveyor
# ===========================================================================

def build_brick_conveyor():
    name = "SM_BrickConveyor"
    col, ref, m = pm.start(name)
    TAIL = Vector((0.0, 0.0, 0.85))
    ANG = math.radians(22)
    L = 9.0
    HEAD = TAIL + Vector((L * math.cos(ANG), 0, L * math.sin(ANG)))
    W = 0.6
    conv = pb.conveyor("BC", TAIL, HEAD, W, col, m, ground_z=0.0, walkway=False, trough=0.0,
                       pulley_r=0.16, uv_m=0.6, legs=False)
    # side guides and cleats are on the structure (bricks ride flat on the belt)
    fr = pb.Part("BC_Undercarriage")
    for s in (1, -1):   # tail wheel axle frame
        fr.beam_between((0.3, s * 0.55, 0.45), (0.3, s * 0.55, 0.75), 0.1, 0.1, m['steel'])
    fr.beam_between((0.3, 0.6, 0.45), (0.3, -0.6, 0.45), 0.1, 0.1, m['steel'])
    pv = TAIL + (HEAD - TAIL) * 0.55 - Vector((0, 0, 0.35))   # A-frame top pin under the boom
    for s in (1, -1):
        fr.beam_between((pv.x - 0.6, s * 0.55, 0.45), pv + Vector((0, s * 0.42, 0)), 0.1, 0.1, m['yellow'])
        fr.beam_between((pv.x + 0.6, s * 0.55, 0.45), pv + Vector((0, s * 0.42, 0)), 0.1, 0.1, m['yellow'])
    fr.beam_between((pv.x, 0.6, 0.45), (pv.x, -0.6, 0.45), 0.1, 0.1, m['steel'])
    fr.box_mm((-0.5, -0.25, 0.30), (0.0, 0.25, 0.75), m['steel'])        # drive motor at the tail
    fr.box_mm((-0.9, -0.45, 0.70), (0.4, 0.45, 0.78), m['grey'])          # loading table at the tail
    fr.beam_between((-0.9, 0, 0.5), (-1.6, 0, 0.35), 0.06, 0.06, m['steel'])   # tow bar
    for s in (1, -1):   # brick side guides along the belt
        side = Vector((0, s * (W / 2 + 0.05), 0.12))
        fr.beam_between(TAIL + side, HEAD + side, 0.02, 0.15, m['grey'])
    ob_fr = fr.finish(col)
    wheels = []
    for x, t in ((0.3, "T"), (pv.x - 0.6, "M"), (pv.x + 0.6, "H")):
        if t == "T":
            continue
        for s, u in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"BC_Wheel_{t}{u}", (x, s * 0.68, 0.30), 0.30, 0.16, col, m))
    for s, u in ((1, "L"), (-1, "R")):
        wheels.append(pm.wheel(f"BC_Wheel_T{u}", (0.3, s * 0.68, 0.30), 0.30, 0.16, col, m))
    bricks = pb.Part("BC_Bricks_Load")    # a few bricks on the belt (hide or drive with the panner)
    d = (HEAD - TAIL).normalized()
    for i in range(6):
        c = TAIL + d * (1.0 + i * 1.3) + Vector((0, 0, 0.06))
        bricks.box((0.23, 0.114, 0.076), c, m['refr'], rot=(0, -math.degrees(ANG), 0))
    bricks.finish(col)
    pb.ref_human(ref, (-0.6, 1.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_BrickConveyor.png", (5.5, -12.5, 6.0), (4.2, 0, 2.2), 30),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_BrickConveyor.png",
                about=f"""
Mobile inclined brick conveyor: 0.6 m flat belt, {L:.0f} m long at {math.degrees(ANG):.0f}°, head at
{HEAD.z:.2f} m. Used to feed bricks from the aisle floor up into a converter mouth or furnace
opening during a reline. Origin is the ground point under the tail pulley; the head points +X.
Own design (no drawing found); proportions follow portable belt conveyors used by relining
contractors.
""",
                moving=f"""
| Part | Motion |
|---|---|
| BC_Belt | Continuous UVs: 1 U = 0.6 m, so panner U speed = belt speed (m/s) / 0.6. Loop length {conv['loop_length']:.2f} m |
| BC_HeadPulley, BC_TailPulley | Spin about the pulley axis (local Y) |
| BC_Wheel_* | Spin about local Y |
| BC_Bricks_Load | Static sample bricks on the belt; hide or move along the belt |

The incline is fixed in this model.
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Brick 230 × 114 × 76 mm | | Standard (ISO 'straight' size) |
| Belt width, length, angle, chassis | | Own design |
""",
                sources="research/copper-refinery file, US5330690 (ladle relining, title only)")


# ===========================================================================
# Ladle relining tower
# ===========================================================================

LADLE_R_IN, LADLE_R_OUT, LADLE_H = 1.40, 1.75, 3.8


def build_ladle_relining_tower():
    name = "SM_LadleReliningTower"
    col, ref, m = pm.start(name)
    TOP = 6.2
    HALF = 2.6
    fr = pb.Part("LRT_Frame")
    for x in (-HALF, HALF):
        for y in (-HALF, HALF):
            fr.beam_between((x, y, 0), (x, y, TOP), 0.25, 0.25, m['yellow'])
            fr.box((0.5, 0.5, 0.03), (x, y, 0.015), m['steel'])
    for z in (TOP - 0.15, 2.2):
        for y in (-HALF, HALF):
            fr.beam_between((-HALF, y, z), (HALF, y, z), 0.2, 0.3, m['yellow'])
        if z == TOP - 0.15:
            for x in (-0.45, 0.45):   # mast guide beams
                fr.beam_between((x, -HALF, z), (x, HALF, z), 0.2, 0.3, m['yellow'])
    for y in (-HALF, HALF):   # X braces on the two sides without stairs
        fr.beam_between((-HALF, y, 2.2), (HALF, y, TOP - 0.3), 0.08, 0.08, m['steel'])
    # rim-level landing on the +X side with stair down to the floor
    LZ = LADLE_H + 0.25
    fr.box_mm((LADLE_R_OUT + 0.15, -1.5, LZ - 0.06), (HALF, 1.5, LZ), m['grey'])
    pm.guard_box(fr, LADLE_R_OUT + 0.15, -1.5, HALF, 1.5, LZ, m['yellow'], open_side='x0')
    pm.stair(fr, (HALF + 4.6, 0, 0), (HALF + 0.05, 0, LZ), 0.9, m['steel'], m['yellow'])
    fr.box_mm((-0.6, -0.6, TOP), (0.6, 0.6, TOP + 0.9), m['steel'])        # mast drive (winch box)
    fr.box_mm((-HALF, -0.15, TOP + 0.15), (HALF, 0.15, TOP + 0.35), m['steel'])   # hoist runway
    ob_fr = fr.finish(col)
    # deck rides on a mast; the pair moves up and down together and rotates about Z
    DZ = 1.0                                                   # deck floor height (rest)
    dk = pb.Part("LRT_Deck", pivot=(0, 0, DZ))
    dk.cyl(LADLE_R_IN - 0.25, 0.12, (0, 0, DZ - 0.06), m['steel'], seg=40)
    dk.beam_between((0, 0, DZ), (0, 0, DZ + TOP - 0.2), 0.32, 0.32, m['grey'])   # mast
    for a in range(0, 360, 30):   # perimeter rail posts
        c = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0)) * (LADLE_R_IN - 0.32)
        dk.cyl_between(c + Vector((0, 0, DZ)), c + Vector((0, 0, DZ + 1.0)), 0.02, m['yellow'], seg=6)
    for z in (0.5, 1.0):
        n = 24
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            r = LADLE_R_IN - 0.32
            dk.cyl_between((r * math.cos(a0), r * math.sin(a0), DZ + z),
                           (r * math.cos(a1), r * math.sin(a1), DZ + z), 0.02, m['yellow'], seg=6)
    brick_stack(dk, -0.6, -0.9, DZ, 4, 3, 5, m)
    ob_dk = dk.finish(col)
    ho = pb.Part("LRT_HoistTrolley", pivot=(HALF - 0.6, 0, TOP + 0.15))
    ho.box_mm((HALF - 0.9, -0.3, TOP - 0.15), (HALF - 0.3, 0.3, TOP + 0.15), m['orange'])
    ob_ho = ho.finish(col)
    cg = pb.Part("LRT_BrickCage", pivot=(HALF - 0.6, 0, TOP - 0.15))
    cz = LZ + 0.1
    cg.cyl_between((HALF - 0.6, 0, TOP - 0.15), (HALF - 0.6, 0, cz + 1.0), 0.012, m['rope'], seg=6)
    cg.box_mm((HALF - 1.1, -0.45, cz), (HALF - 0.1, 0.45, cz + 0.08), m['steel'])
    for x in (HALF - 1.1, HALF - 0.12):
        for y in (-0.45, 0.43):
            cg.box_mm((x, y, cz), (x + 0.02, y + 0.02, cz + 1.0), m['steel'])
    brick_stack(cg, HALF - 1.05, -0.4, cz + 0.08, 4, 7, 6, m)
    ob_cg = cg.finish(col)
    pm.parent(ob_cg, ob_ho)
    # REF ladle (not exported): copper converter-aisle ladle proxy, worn lining stripped out
    lp = pb.Part("REF_Ladle")
    lm = pb.mat("M_REF_LadleShell", (0.2, 0.2, 0.2), 0.6, 0.6)
    n = 32
    rows = []
    for r, z in ((LADLE_R_OUT, LADLE_H), (LADLE_R_OUT, 0.3), (LADLE_R_OUT - 0.2, 0.0),
                 (LADLE_R_IN, 0.0 + 0.4), (LADLE_R_IN, LADLE_H)):
        rows.append([(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z)
                     for i in range(n + 1)])
    lp.quad_strip([list(x) for x in zip(*rows)], lm, closed=False)
    lp.finish(ref)
    pb.ref_human(ref, (0.4, 0.3, DZ))
    pb.ref_human(ref, (HALF + 1.0, 1.2, 0))

    def pose():
        """Deck raised to 2.6 m and turned; cage lowered to the landing."""
        ob_dk.location.z += 1.6
        ob_dk.rotation_euler.z = math.radians(40)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_LadleReliningTower.png", (8, -10, 12), (0.3, 0, 2.6), 35),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_LadleReliningTower.png (deck raised 1.6 m)",
                about=f"""
Four-post tower that stands over a ladle for rebricking. A round work deck on a central mast
rises inside the ladle as each brick course goes in, and turns so the bricklayer stays at the
working face. A hoist trolley on the top runway lowers brick cages to a landing at rim level,
reached by a stair on the +X side. Origin is the floor under the ladle centre. The REF ladle
(Ø{2 * LADLE_R_OUT:.1f} m outside, {LADLE_H} m tall) is a proxy and not exported.
Own design. US5330690 is titled as a ladle relining apparatus but I have not read its drawings,
so this is not based on it.
""",
                moving=f"""
| Part | Motion |
|---|---|
| LRT_Deck | Moves along Z (floor {DZ} m to about {LADLE_H - 0.6:.1f} m) and rotates about Z. The mast is part of the deck |
| LRT_HoistTrolley | Moves along X on the runway (x = -{HALF - 0.6:.1f} to +{HALF - 0.6:.1f}) |
| LRT_BrickCage | Child of the trolley; moves along Z. Its rope is part of the cage; scale is not needed for the short drop to the landing |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Ladle proxy Ø3.5 m × 3.8 m | | Estimated (converter-aisle copper ladle size, not sourced) |
| Tower 5.2 m square × 6.2 m, deck Ø2.3 m | | Own design |
| Bricks 230 × 114 × 76 mm | | Standard size |
""",
                sources="US5330690 (title only); research/copper-refinery file (reline practice)")


# ===========================================================================
# Rotor gunning machine
# ===========================================================================

def build_gunning_machine():
    name = "SM_GunningMachine"
    col, ref, m = pm.start(name)
    # Sourced envelope: 1245 x 813 x 1219 mm, 363 kg (Putzmeister/Allentown Piccola rotor gun).
    L, W, H = 1.245, 0.813, 1.219
    bd = pb.Part("GM_Body")
    bd.box_mm((-L / 2, -W / 2 + 0.06, 0.12), (L / 2, W / 2 - 0.06, 0.22), m['steel'])       # skid
    bd.cyl(0.33, 0.28, (0, 0, 0.42), m['grey'], seg=28)                                     # rotor housing
    bd.cyl(0.36, 0.05, (0, 0, 0.585), m['steel'], seg=28)                                   # wear plates/clamp
    bd.cyl(0.30, 0.60, (0, 0, 0.90), m['orange'], seg=28, r2=0.40)                          # hopper, wide at the top
    bd.cyl(0.40, 0.02, (0, 0, H - 0.01), m['steel'], seg=28)                                 # screen
    bd.box_mm((-L / 2, -0.25, 0.22), (-0.30, 0.25, 0.62), m['blue'])                         # motor + gearbox
    bd.cyl_between((0.33, 0, 0.36), (L / 2, 0, 0.36), 0.04, m['steel'], seg=12)             # material outlet 38 mm
    bd.cyl_between((-0.2, 0.30, 0.5), (-0.2, W / 2, 0.5), 0.03, m['grey'], seg=10)          # air inlet
    for s in (1, -1):                                                                       # push handle
        bd.cyl_between((-L / 2 + 0.1, s * 0.25, 0.22), (-L / 2 - 0.2, s * 0.25, 0.95), 0.016, m['steel'], seg=8)
    bd.cyl_between((-L / 2 - 0.2, 0.25, 0.95), (-L / 2 - 0.2, -0.25, 0.95), 0.016, m['steel'], seg=8)
    ob_bd = bd.finish(col)
    wheels = [pm.wheel(f"GM_Wheel_{t}", (-0.35, s * (W / 2 - 0.03), 0.14), 0.14, 0.06, col, m)
              for s, t in ((1, "L"), (-1, "R"))]
    # material hose: a coil on the floor, then a run to the nozzle
    hs = pb.Part("GM_Hose")
    r, n, turns = 0.55, 64, 3
    for k in range(n * turns):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        rr0, rr1 = r - 0.045 * k / n, r - 0.045 * (k + 1) / n
        c = Vector((1.75, 0, 0.04))
        hs.cyl_between(c + Vector((rr0 * math.cos(a0), rr0 * math.sin(a0), 0)),
                       c + Vector((rr1 * math.cos(a1), rr1 * math.sin(a1), 0)), 0.035, m['rubber'], seg=8)
    hs.cyl_between((L / 2, 0, 0.36), (1.20, 0, 0.04), 0.035, m['rubber'], seg=8)
    hs.cyl_between((1.75 + r - 0.135, 0, 0.04), (2.8, 0.6, 0.04), 0.035, m['rubber'], seg=8)
    ob_hs = hs.finish(col)
    nz = pb.Part("GM_Nozzle", pivot=(2.8, 0.6, 0.04))
    nz.cyl_between((2.8, 0.6, 0.04), (3.9, 0.6, 0.04), 0.03, m['steel'], seg=10)          # nozzle pipe
    nz.cyl(0.05, 0.12, (3.0, 0.6, 0.04), m['grey'], rot=(0, 90, 0), seg=12)                # water ring
    nz.cyl_between((3.0, 0.6, 0.09), (3.0, 1.2, 0.04), 0.012, m['blue'], seg=6)            # water hose stub
    ob_nz = nz.finish(col)
    pb.ref_human(ref, (0.0, 1.2, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_GunningMachine.png", (3.6, -3.4, 2.2), (1.2, 0, 0.5), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_GunningMachine.png",
                about="""
Dry-process rotor gunning machine (gunite / refractory gun) on a two-wheel skid with a coiled
38 mm material hose and a hand nozzle with water ring. Used for repair gunning of furnace,
converter and ladle linings. Origin is the floor under the rotor centre; the outlet points +X.
""",
                moving="""
| Part | Motion |
|---|---|
| GM_Wheel_L/R | Spin about local Y |
| GM_Nozzle | Pivot at the hose end; free to rotate for hand-held aiming |
| GM_Hose | Static coil |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Machine L × W × H | 1245 × 813 × 1219 mm | Sourced (Putzmeister Piccola rotary gun data) |
| Weight 363 kg, 38 mm outlet, output 0.76-4.6 m³/h, rotor 10-14 rpm | | Sourced (same page) |
| Hopper shape, wheel size, hose coil, nozzle | | Estimated |
""",
                sources="https://www.putzmeister.com/web/oceania/product-detail/-/product/309/piccola-rotary-gun")


# ===========================================================================
# Hot-gunning manipulator
# ===========================================================================

def build_gunning_manipulator():
    name = "SM_GunningManipulator"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    ca = pb.Part("GMN_Carrier")
    ca.box_mm((-2.6, -1.1, 0.45), (2.6, 1.1, 1.15), paint)
    ca.box_mm((-2.6, -1.1, 1.15), (-1.0, 1.1, 2.3), m['grey'])          # material hopper + air module
    ca.cyl(0.65, 0.9, (-1.8, 0, 2.7), m['orange'], seg=24, r2=0.3)      # pressure vessel / hopper cone
    ca.box_mm((1.4, 0.2, 1.15), (2.6, 1.1, 2.9), m['white'])              # shielded operator cab
    ca.box_mm((2.58, 0.3, 1.9), (2.61, 1.0, 2.7), m['glass'])
    ca.box_mm((2.65, 0.1, 0.9), (2.8, 1.2, 3.1), m['steel'])              # heat shield in front of the cab
    ob_ca = ca.finish(col)
    wheels = []
    for x, t in ((1.7, "F"), (-1.7, "R")):
        for s, u in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"GMN_Wheel_{t}{u}", (x, s * 0.92, 0.55), 0.55, 0.4, col, m))
    SZ = 1.15
    tu = pb.Part("GMN_Turret", pivot=(0.3, -0.3, SZ))
    tu.cyl(0.5, 0.25, (0.3, -0.3, SZ + 0.125), m['grey'], seg=24)
    for s in (1, -1):
        tu.box_mm((0.0, -0.3 + s * 0.22 - 0.05, SZ + 0.25), (0.6, -0.3 + s * 0.22 + 0.05, SZ + 1.0), paint)
    ob_tu = tu.finish(col)
    P = Vector((0.3, -0.3, SZ + 0.85))
    bo = pb.Part("GMN_Boom", pivot=P)
    bo.box_mm((P.x - 0.4, P.y - 0.15, P.z - 0.18), (P.x + 4.0, P.y + 0.15, P.z + 0.18), paint)
    bo.box_mm((P.x + 1.0, P.y - 0.08, P.z - 0.35), (P.x + 1.4, P.y + 0.08, P.z - 0.18), m['steel'])
    ob_bo = bo.finish(col)
    lances = []
    for i, (r, c) in enumerate(((0.09, m['grey']), (0.065, m['galv']))):
        x0 = P.x + 0.8 + i * 0.4
        ln = pb.Part(f"GMN_Lance{i + 1}", pivot=P)
        ln.cyl_between((x0, P.y, P.z), (P.x + 4.3 + i * 0.6, P.y, P.z), r, c, seg=14)
        lances.append(ln.finish(col))
    NZ = Vector((P.x + 4.9, P.y, P.z))
    nz = pb.Part("GMN_NozzleHead", pivot=NZ)
    nz.cyl_between(NZ, NZ + Vector((0.45, 0, 0)), 0.08, m['steel'], seg=14)
    nz.cyl_between(NZ + Vector((0.45, 0, 0)), NZ + Vector((0.55, 0, -0.15)), 0.05, m['steel'], seg=10)
    ob_nz = nz.finish(col)
    pm.hyd_cyl("GMN_LuffCyl", (1.0, -0.3, SZ + 0.25), (P.x + 1.2, P.y, P.z - 0.35), 0.08, col, m, ob_tu, ob_bo)
    for w in wheels + [ob_tu]:
        pm.parent(w, ob_ca)
    pm.parent(ob_bo, ob_tu)
    pm.parent(lances[0], ob_bo)
    pm.parent(lances[1], lances[0])
    pm.parent(ob_nz, lances[1])
    pb.ref_human(ref, (0.0, 1.8, 0))

    def pose():
        """Lance raised 15 deg and extended 3 m, slewed 10 deg, nozzle turned."""
        ob_tu.rotation_euler.z = math.radians(10)
        ob_bo.rotation_euler.y = math.radians(-15)
        for ln in lances:
            ln.location.x += 1.5
        ob_nz.rotation_euler.x = math.radians(60)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_GunningManipulator.png", (10, -9, 5), (2.5, 0, 1.8), 35),
        ("Preview_GunningManipulator_Working.png", (11, -8, 6), (3.5, 0, 2.5), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_GunningManipulator.png, Preview_GunningManipulator_Working.png",
                about="""
Wheeled hot-gunning manipulator: a material pressure vessel and air module on the carrier, a
shielded operator cab, and a slewing, luffing boom with a two-stage telescopic lance. It reaches
into a hot converter mouth or ladle to gun repair mix onto worn lining without cooling the
vessel. Origin is the ground point at the carrier centre; the boom points +X.
Own design. The task (hot repair gunning of converter mouths) is sourced; no drawing of a
specific machine was found.
""",
                moving="""
| Part | Motion |
|---|---|
| GMN_Turret | Slews about local Z |
| GMN_Boom | Luffs about local Y (negative raises) |
| GMN_Lance1, GMN_Lance2 | Slide along the boom's local +X, about 1.5 m each (Lance2 rides on Lance1) |
| GMN_NozzleHead | Rotates about local X (the lance axis) to aim the bent nozzle |
| GMN_LuffCyl_Barrel / _Rod | Look-at pair |
| GMN_Wheel_* | Spin about local Y |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Whole machine (5.4 × 2.4 × 3.3 m, ~6 m lance reach) | | Own design |
""",
                sources="KNS converter mouth paper (hot gunning repairs of mouth refractory), https://onemine.org/documents/peirce-smith-converter-mouth-redesign-overview")


BUILDERS = dict(BrickConveyor=build_brick_conveyor, LadleReliningTower=build_ladle_relining_tower,
                GunningMachine=build_gunning_machine, GunningManipulator=build_gunning_manipulator)

INTRO = """
Gear for relining furnaces, converters and ladles. Each asset is a standalone prop at its own
origin. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_refractory_relining.py`. For the tear-out step see
Meshes/DemolitionRobot. Real reline example from the research file: the Mount Isa anode furnace
rebrick (2024) took 33 days, used a demolition robot for break-out, oxy-lancing for shell plate,
hand-laid bricks and about 60 extra trades.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
