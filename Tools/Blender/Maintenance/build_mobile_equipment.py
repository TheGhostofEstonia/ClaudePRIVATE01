"""
build_mobile_equipment.py - shutdown and clean-up vehicles, each a standalone prop at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_mobile_equipment.py
      (add  -- MobileCrane  to build one asset only)

Assets (Meshes/MobileEquipment/):
    SM_MobileCrane     5-axle all-terrain crane, 100 t class
    SM_ScissorLift     electric slab scissor lift, ~9.8 m platform height
    SM_BoomLift        telescopic boom lift, ~20 m platform height
    SM_ScaffoldTower   cup-lock access scaffold tower, 2.5 x 1.3 m bay, 4 lifts
    SM_ScaffoldKit     loose scaffold components for building other shapes
    SM_VacuumTruck     industrial vacuum loader truck
    SM_Sweeper         ride-on industrial sweeper

All: +X = front / forward travel, origin on the ground (see each README section).
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

FOLDER = "MobileEquipment"


# ===========================================================================
# Shared: simple truck cab (box with windscreen, used by crane and vacuum truck)
# ===========================================================================

def cab(p, x0, x1, y0, y1, z0, z1, m, paint):
    """Cab box from (x0, y0, z0) to (x1, y1, z1); windscreen on the +X face, side windows."""
    p.box_mm((x0, y0, z0), (x1, y1, z1), paint)
    p.box_mm((x1 - 0.02, y0 + 0.08, z0 + (z1 - z0) * 0.45), (x1 + 0.01, y1 - 0.08, z1 - 0.1), m['glass'])
    for y in (y0 - 0.01, y1 - 0.0):
        p.box_mm((x0 + 0.15, y, z0 + (z1 - z0) * 0.45), (x1 - 0.2, y + 0.01, z1 - 0.12), m['glass'])
    p.box_mm((x1 - 0.05, y0 + 0.1, z0 + 0.15), (x1 + 0.02, y0 + 0.35, z0 + 0.3), m['lamp'])
    p.box_mm((x1 - 0.05, y1 - 0.35, z0 + 0.15), (x1 + 0.02, y1 - 0.1, z0 + 0.3), m['lamp'])


# ===========================================================================
# Mobile crane
# ===========================================================================

def build_mobile_crane():
    name = "SM_MobileCrane"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    # Sourced: transport 13.64 x 2.75 x 4.0 m; outrigger base 7.385 x 7.0 m; boom 11.5-52 m.
    HW = 1.375                                    # half width 2.75 m
    TYRE_R, TYRE_W = 0.74, 0.45                   # 445/95R25 class (estimated)
    AXLES = [3.90, 2.25, -0.90, -2.55, -4.20]     # axle x positions (estimated)
    SLEW_Z = 1.95                                 # top of the carrier deck / slew ring
    FOOT = Vector((-2.80, 0.0, 3.05))             # boom foot pin on the superstructure
    BOOM_L = 11.5                                 # base boom length (sourced)
    OUT_X = (3.10, -4.285)                        # outrigger box lines: 7.385 m apart
    OUT_Y_IN, OUT_Y_OUT = 1.25, 3.50              # jack centre retracted / fully out (7.0 m)

    # --- carrier ---
    ca = pb.Part("MC_Carrier")
    ca.box_mm((-4.90, -1.15, 0.85), (5.40, 1.15, 1.55), m['steel'])         # chassis frame
    ca.box_mm((-4.90, -HW, 1.55), (3.30, HW, SLEW_Z - 0.05), paint)         # deck
    for x in AXLES:   # wheel arches
        ca.box_mm((x - 0.85, -HW, 1.50), (x + 0.85, HW, 1.62), m['steel'])
    cab(ca, 3.30, 5.40, -HW, 0.20, 1.00, 3.30, m, paint)                    # driver cab, left
    ca.box_mm((3.30, 0.25, 1.00), (5.30, HW, 2.30), paint)                   # engine/fuel side
    ca.cyl(1.05, 0.10, (0, 0, SLEW_Z - 0.05), m['grey'], seg=40)            # slew ring
    ca.box_mm((6.6 - 1.25, -0.5, 3.40), (5.40, 0.5, 3.55), m['steel'])     # boom rest over cab
    for x in OUT_X:                                                         # outrigger boxes
        ca.box_mm((x - 0.25, -HW, 0.95), (x + 0.25, HW, 1.45), m['steel'])
    ob_ca = ca.finish(col)

    wheels = []
    for i, x in enumerate(AXLES):
        for s, t in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"MC_Wheel_A{i + 1}{t}", (x, s * (HW - TYRE_W / 2 - 0.02), TYRE_R),
                                   TYRE_R, TYRE_W, col, m))

    # --- outriggers: beam slides along Y, jack slides along -Z ---
    outs, jacks = [], []
    for x, xt in ((OUT_X[0], "F"), (OUT_X[1], "R")):
        for s, t in ((1, "L"), (-1, "R")):
            yj = s * OUT_Y_IN
            bm = pb.Part(f"MC_OutriggerBeam_{xt}{t}", pivot=(x, yj, 1.20))
            bm.box_mm((x - 0.18, min(yj, s * 0.05), 1.03), (x + 0.18, max(yj, s * 0.05), 1.37), m['white'])
            bm.box_mm((x - 0.22, yj - 0.22, 1.00), (x + 0.22, yj + 0.22, 1.60), m['white'])  # jack housing
            outs.append(bm.finish(col))
            jk = pb.Part(f"MC_OutriggerJack_{xt}{t}", pivot=(x, yj, 1.00))
            jk.cyl(0.13, 0.75, (x, yj, 1.00 + 0.1), m['grey'], seg=16)
            jk.cyl(0.32, 0.08, (x, yj, 0.70), m['steel'], seg=24)                    # pad
            jacks.append(jk.finish(col))

    # --- superstructure: slews about Z ---
    su = pb.Part("MC_Superstructure", pivot=(0, 0, SLEW_Z))
    su.box_mm((-3.40, -1.10, SLEW_Z), (1.20, 1.10, SLEW_Z + 0.55), paint)          # turntable frame
    for s in (1, -1):                                                              # boom foot cheeks
        su.box_mm((-3.20, s * 0.62 - 0.08, SLEW_Z + 0.4), (-2.40, s * 0.62 + 0.08, FOOT.z + 0.35), paint)
    su.cyl(0.10, 1.40, FOOT, m['grey'], rot=(90, 0, 0), seg=12)
    su.box_mm((-4.75, -1.25, SLEW_Z + 0.10), (-3.40, 1.25, SLEW_Z + 1.25), m['steel'])  # counterweight
    su.box_mm((-3.30, -1.25, SLEW_Z + 0.55), (-2.0, -0.70, SLEW_Z + 1.6), paint)       # hoist winch housing
    su.cyl(0.38, 0.8, (-3.0, -0.95, SLEW_Z + 1.05), m['steel'], rot=(90, 0, 0), seg=20)  # hoist drum
    cab(su, -0.30, 1.25, 0.75, 1.30, SLEW_Z + 0.25, SLEW_Z + 1.85, m, paint)           # crane cab, right
    su.box_mm((0.35, -0.30, SLEW_Z + 0.2), (1.05, 0.30, SLEW_Z + 0.75), m['steel'])     # luff cyl foot
    ob_su = su.finish(col)

    # --- boom: base section pivots at FOOT; 4 telescopic sections slide along local X ---
    bo_dir = Vector((1, 0, 0))
    bw, bh = 0.95, 1.05
    secs = []
    base = pb.Part("MC_Boom_Base", pivot=FOOT)
    base.box_mm((FOOT.x - 0.3, -bw / 2, FOOT.z - 0.2), (FOOT.x + BOOM_L - 0.6, bw / 2, FOOT.z + bh - 0.2), paint)
    base.box_mm((FOOT.x + 2.2, -0.25, FOOT.z - 0.35), (FOOT.x + 3.0, 0.25, FOOT.z - 0.2), m['steel'])   # luff lug
    ob_base = base.finish(col)
    secs.append(ob_base)
    for i in range(4):
        k = (i + 1) * 0.06
        w, h = bw - 2 * k, bh - 2 * k
        x0 = FOOT.x + 0.2 + i * 0.15
        x1 = FOOT.x + BOOM_L - 0.55 + (i + 1) * 0.12
        sp = pb.Part(f"MC_Boom_Tele{i + 1}", pivot=FOOT)
        sp.box_mm((x0, -w / 2, FOOT.z - 0.2 + k), (x1, w / 2, FOOT.z - 0.2 + k + h), paint)
        if i == 3:   # boom head with sheaves
            hx = x1 + 0.35
            sp.box_mm((x1, -0.3, FOOT.z - 0.1), (hx, 0.3, FOOT.z + 0.75), m['steel'])
            for y in (-0.15, 0.0, 0.15):
                sp.cyl(0.32, 0.07, (hx, y, FOOT.z + 0.35), m['grey'], rot=(90, 0, 0), seg=20)
        secs.append(sp.finish(col))
    tip_x = FOOT.x + BOOM_L - 0.55 + 0.48 + 0.35          # boom head sheave line (retracted)

    # --- hoist rope: 1 m long along -Z from the head sheave; scale Z = hanging length ---
    rp = pb.Part("MC_HoistRope", pivot=(tip_x, 0, FOOT.z + 0.35))
    for y in (-0.06, 0.06):
        rp.cyl_between((tip_x + 0.32, y, FOOT.z + 0.35), (tip_x + 0.32, y, FOOT.z - 0.65), 0.012, m['rope'], seg=6)
    ob_rope = rp.finish(col)
    hb = pb.Part("MC_HookBlock", pivot=(tip_x + 0.32, 0, FOOT.z - 0.65))
    hz = FOOT.z - 0.65
    hb.box_mm((tip_x + 0.0, -0.22, hz - 0.85), (tip_x + 0.64, 0.22, hz), paint)
    hb.cyl(0.08, 0.35, (tip_x + 0.32, 0, hz - 1.05), m['steel'], seg=12)
    hb.cyl(0.18, 0.08, (tip_x + 0.32, 0, hz - 1.30), m['steel'], rot=(90, 0, 0), seg=16)
    ob_hook = hb.finish(col)

    # --- luffing cylinder ---
    pm.hyd_cyl("MC_LuffCyl", (0.75, 0, SLEW_Z + 0.55), (FOOT.x + 2.6, 0, FOOT.z - 0.3), 0.17,
               col, m, ob_su, ob_base)

    # hierarchy (posing in the .blend)
    for o in [ob_su] + wheels + outs:
        pm.parent(o, ob_ca)
    for j, o in zip(jacks, outs):
        pm.parent(j, o)
    pm.parent(ob_base, ob_su)
    for s in secs[1:]:
        pm.parent(s, ob_base)
    # rope and hook stay unparented so the rope hangs vertically whatever the boom does
    pb.ref_human(ref, (2.0, -3.0, 0))

    def pose():
        """Set up: outriggers fully out, jacks down 0.30 m, slew 30 deg, boom 55 deg, sections out."""
        for o in outs:
            s = 1 if o.name.endswith("L") else -1
            o.location.y += s * (OUT_Y_OUT - OUT_Y_IN)
        for j in jacks:
            j.location.z -= 0.30
        ob_su.rotation_euler.z = math.radians(30)
        ob_base.rotation_euler.y = math.radians(-55)
        for i, s in enumerate(secs[1:]):
            s.location.x += 7.0 * (i + 1)
        import bpy
        bpy.context.view_layer.update()
        head = secs[-1].matrix_world @ (Vector((tip_x + 0.32, 0, FOOT.z + 0.35)) - FOOT)
        drop = 20.0
        ob_rope.location = head - Vector((0.32, 0, 0))
        ob_rope.scale.z = drop
        ob_hook.location = head - Vector((0, 0, drop))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_MobileCrane.png", (14, -14, 7), (0.5, 0, 2.0), 35),
        ("Preview_MobileCrane_SetUp.png", (48, -62, 22), (10, 0, 17), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_MobileCrane.png (travel), Preview_MobileCrane_SetUp.png",
                about="""
Five-axle all-terrain crane, 100 t class (Liebherr LTM 1100-5.2 size, no branding). Origin is the
ground point under the slewing centre. +X is the cab end.
""",
                moving="""
| Part | Motion |
|---|---|
| MC_Superstructure | Slews about local Z |
| MC_Boom_Base | Luffs about local Y at the foot pin; negative Y raises the boom (0 to about -82°) |
| MC_Boom_Tele1..4 | Slide along the boom's local +X. Each section can extend about 10 m; the preview uses 7, 14, 21, 28 m (cumulative) |
| MC_HoistRope | Pivot at the head sheave; scale Z = hanging rope length in metres. Not parented: keep it vertical in world space and move its pivot with the boom head |
| MC_HookBlock | Pivot at the rope end; place it at head sheave position minus the rope length |
| MC_OutriggerBeam_xx | Slide along local Y: +2.25 m on the L side, -2.25 m on the R side for the full 7.0 m width |
| MC_OutriggerJack_xx | Slide along -Z (0.30 m reaches the ground and lifts the tyres slightly) |
| MC_LuffCyl_Barrel / _Rod | Look-at pair: each half aims local +X at the other's pivot |
| MC_Wheel_A1L..A5R | Spin about local Y. Tyre circumference 4.65 m: deg/s = speed (m/s) × 77.4. Axles 1-2 and 4-5 steer |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Transport length × width × height | 13.64 × 2.75 × 4.0 m | Sourced (LTM 1100-5.2 operator listings, trucks-cranes.nl; LECTURA) |
| Outrigger base | 7.385 × 7.0 m | Sourced (LECTURA spec page) |
| Main boom | 11.5 m retracted, 52 m fully out | Sourced; sections shortened so the model stays inside 13.64 m |
| Axle positions, tyre size, cab layout, counterweight size | | Estimated from photos |
""",
                sources="trucks-cranes.nl LTM 1100-5.2 fleet pages; https://www.lectura-specs.com/en/model/cranes/all-terrain-cranes-liebherr/ltm-1100-5-2-11734400")


# ===========================================================================
# Scissor lift
# ===========================================================================

SL_N, SL_L = 5, 2.0                 # scissor stages, arm length (pin to pin)
SL_BASE_Z, SL_DECK_OFF = 0.60, 0.10  # lower pins height, deck floor above the top pins
SL_XF = -0.95                       # x of the fixed (hinged) pin line


def build_scissor_lift():
    name = "SM_ScissorLift"
    col, ref, m = pm.start(name)
    paint = m['blue']
    # Stowed 2.44 x 1.16 m (sourced); platform floor stowed ~1.25 m, max 9.78 m (sourced).
    th0 = math.asin((1.25 - SL_DECK_OFF - SL_BASE_Z) / (SL_N * SL_L))
    ch = pb.Part("SL_Chassis")
    ch.box_mm((-1.22, -0.50, 0.12), (1.22, 0.50, SL_BASE_Z - 0.08), paint)
    for s in (1, -1):        # battery / hydraulic trays and pothole guards
        ch.box_mm((-0.90, s * 0.50, 0.15), (0.90, s * 0.58, 0.48), m['steel'])
    ch.box_mm((1.22, -0.25, 0.25), (1.27, 0.25, 0.45), m['steel'])
    ch.box_mm((-1.10, -0.48, SL_BASE_Z - 0.08), (1.10, 0.48, SL_BASE_Z - 0.04), m['steel'])
    ob_ch = ch.finish(col)
    wheels = []
    for x, t in ((0.82, "F"), (-0.82, "R")):
        for s, u in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"SL_Wheel_{t}{u}", (x, s * 0.47, 0.19), 0.19, 0.13, col, m))

    # scissor arms: each separate, pivot at its centre pin
    arms = []
    for i in range(SL_N):
        zc = SL_BASE_Z + (i + 0.5) * SL_L * math.sin(th0)
        xc = SL_XF + SL_L / 2 * math.cos(th0)
        for k, sgn in ((0, 1), (1, -1)):    # 0 = rises toward +X, 1 = falls toward +X
            for s in (1, -1):
                d = Vector((math.cos(th0), 0, sgn * math.sin(th0))) * (SL_L / 2 + 0.06)
                y = s * (0.40 if k == 0 else 0.32)
                c = Vector((xc, y, zc))
                a = pb.Part(f"SL_Arm_{i + 1}{'AB'[k]}{'L' if s > 0 else 'R'}", pivot=c)
                a.beam_between(c - d, c + d, 0.06, 0.09, m['yellow'] if k == 0 else paint)
                a.cyl(0.04, 0.10, c, m['grey'], rot=(90, 0, 0), seg=10)
                arms.append((a.finish(col), i, sgn))

    deck_z = SL_BASE_Z + SL_N * SL_L * math.sin(th0) + SL_DECK_OFF
    dk = pb.Part("SL_Platform", pivot=(0, 0, deck_z))
    dk.box_mm((-1.18, -0.56, deck_z - 0.10), (1.10, 0.56, deck_z), m['steel'])
    pm.guard_box(dk, -1.15, -0.53, 1.07, 0.53, deck_z, m['yellow'], open_side='x1')
    dk.box_mm((-1.16, -0.25, deck_z + 0.85), (-1.12, 0.25, deck_z + 1.1), m['yellow'])   # entry gate bar
    dk.box_mm((-1.0, 0.35, deck_z + 0.9), (-0.85, 0.5, deck_z + 1.15), m['steel'])       # control box
    ob_dk = dk.finish(col)
    # roll-out extension: rests on the front of the deck with its own rails, slides +X 0.9 m
    ex = pb.Part("SL_DeckExtension", pivot=(1.10, 0, deck_z))
    ex.box_mm((0.15, -0.50, deck_z), (1.10, 0.50, deck_z + 0.04), m['grey'])
    pm.guard_box(ex, 0.18, -0.48, 1.10, 0.48, deck_z + 0.04, m['yellow'], h=1.05, open_side='x0')
    ob_ex = ex.finish(col)
    pm.parent(ob_ex, ob_dk)
    pb.ref_human(ref, (-0.3, 1.4, 0))

    def pose():
        """Raise to 9.78 m platform height and slide the extension out 0.9 m."""
        th = math.asin((9.78 - SL_DECK_OFF - SL_BASE_Z) / (SL_N * SL_L))
        for ob, i, sgn in arms:
            ob.location.x = SL_XF + SL_L / 2 * math.cos(th)
            ob.location.z = SL_BASE_Z + (i + 0.5) * SL_L * math.sin(th)
            ob.rotation_euler.y = -sgn * (th - th0)
        ob_dk.location.z = 9.78
        ob_ex.location.x += 0.9

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_ScissorLift.png", (4.5, -5.0, 2.6), (0, 0, 0.9), 35),
        ("Preview_ScissorLift_Raised.png", (13, -16, 8), (0, 0, 5.6), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_ScissorLift.png (stowed), Preview_ScissorLift_Raised.png",
                about="""
Electric slab scissor lift, 9.8 m platform class (Genie GS-3246 size, no branding). Origin is the
ground point under the chassis centre. +X is the deck-extension end.
""",
                moving=f"""
Five stages of crossed arms, each arm a separate part with its pivot on its centre pin. For a
target platform floor height H (1.25 to 9.78 m):

- θ = asin((H - {SL_DECK_OFF} - {SL_BASE_Z}) / ({SL_N} × {SL_L})), stowed θ0 = {math.degrees(th0):.2f}°
- arm of stage i (1..5): X = {SL_XF} + {SL_L / 2} × cos θ, Z = {SL_BASE_Z} + (i - 0.5) × {SL_L} × sin θ
- arms 'A' (yellow, rising toward +X): rotation Y = -(θ - θ0); arms 'B' (blue): +(θ - θ0)
- SL_Platform: Z = H, no X shift (the hinged pins all sit on the line X = {SL_XF}; the other ends slide)
- SL_DeckExtension slides along local +X up to 0.9 m

| Part | Motion |
|---|---|
| SL_Arm_1AL ... SL_Arm_5BR | As above |
| SL_Platform, SL_DeckExtension | As above |
| SL_Wheel_FL/FR/RL/RR | Spin about local Y (front pair steers about Z) |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Stowed length × width | 2.44 × 1.16 m | Sourced (Genie GS-3246 spec table) |
| Stowed height | 2.40 m rails up | Sourced; the model's rail top is ≈2.35 m |
| Max platform height | 9.78 m | Sourced |
| Platform with extension | ≈3.2 m long | Sourced as 125 in (Cat Rental listing), model 3.18 m |
| Stage count, arm length 2.0 m, chassis height | | Estimated |
""",
                sources="Genie GS-2046/2646/3246 spec sheet (via aerialtitans.com PDF); Cat Rental GS-3246 listing")


# ===========================================================================
# Telescopic boom lift
# ===========================================================================

def build_boom_lift():
    name = "SM_BoomLift"
    col, ref, m = pm.start(name)
    paint = m['orange']
    # Sourced: stowed ~9.42 x 2.49 x 2.72 m, platform height 19.8 m, reach 17.1 m.
    HW = 1.245
    ch = pb.Part("BL_Chassis")
    ch.box_mm((-1.35, -1.0, 0.45), (1.35, 1.0, 0.95), paint)
    for x in (1.15, -1.15):   # axles
        ch.box_mm((x - 0.15, -HW + 0.4, 0.40), (x + 0.15, HW - 0.4, 0.62), m['steel'])
    ob_ch = ch.finish(col)
    wheels = []
    for x, t in ((1.15, "F"), (-1.15, "R")):
        for s, u in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"BL_Wheel_{t}{u}", (x, s * (HW - 0.2), 0.52), 0.52, 0.38, col, m))
    SLEW_Z = 1.0
    tt = pb.Part("BL_Turntable", pivot=(0, 0, SLEW_Z))
    tt.cyl(0.75, 0.08, (0, 0, SLEW_Z + 0.04), m['grey'], seg=32)
    tt.box_mm((-1.95, -1.1, SLEW_Z + 0.08), (-0.6, 1.1, SLEW_Z + 1.30), paint)   # engine + counterweight
    tt.box_mm((-0.6, -0.4, SLEW_Z + 0.08), (0.4, 0.4, SLEW_Z + 1.05), paint)      # boom riser
    tt.box_mm((-1.85, 1.0, SLEW_Z + 0.4), (-1.3, 1.11, SLEW_Z + 1.0), m['steel'])  # ground controls
    ob_tt = tt.finish(col)
    PIV = Vector((-0.40, 0, SLEW_Z + 1.30))      # boom foot pin
    BL0 = 6.4                                    # base section length (estimated)
    bb = pb.Part("BL_Boom_Base", pivot=PIV)
    bb.box_mm((PIV.x - 0.2, -0.27, PIV.z - 0.22), (PIV.x + BL0, 0.27, PIV.z + 0.22), paint)
    bb.box_mm((PIV.x + 1.0, -0.12, PIV.z - 0.36), (PIV.x + 1.5, 0.12, PIV.z - 0.22), m['steel'])
    ob_bb = bb.finish(col)
    tele = []
    for i, (w, h, c) in enumerate(((0.21, 0.16, m['white']), (0.16, 0.12, m['grey']))):
        x1 = PIV.x + BL0 + 0.15 * (i + 1) + (0.2 if i == 1 else 0.0)
        tl = pb.Part(f"BL_Boom_Tele{i + 1}", pivot=PIV)
        tl.box_mm((PIV.x + 0.6 + 0.3 * i, -w, PIV.z - h), (x1, w, PIV.z + h), c)
        if i == 1:
            tl.cyl(0.06, 0.40, (x1, 0, PIV.z), m['grey'], rot=(90, 0, 0), seg=12)
        tele.append(tl.finish(col))
    J = Vector((PIV.x + BL0 + 0.5, 0, PIV.z))   # jib pin (retracted)
    jb = pb.Part("BL_Jib", pivot=J)
    jb.box_mm((J.x, -0.10, J.z - 0.10), (J.x + 1.2, 0.10, J.z + 0.10), paint)
    jb.cyl(0.05, 0.30, (J.x + 1.2, 0, J.z), m['grey'], rot=(90, 0, 0), seg=10)
    ob_jb = jb.finish(col)
    P = Vector((J.x + 1.2, 0, J.z))              # platform levelling pin
    pf = pb.Part("BL_Platform", pivot=P)
    pz = P.z - 0.45
    pf.box_mm((P.x + 0.05, -1.22, pz - 0.1), (P.x + 0.95, 1.22, pz), m['steel'])
    pf.box_mm((P.x - 0.05, -0.15, pz), (P.x + 0.1, 0.15, P.z + 0.1), m['steel'])
    pm.guard_box(pf, P.x + 0.08, -1.19, P.x + 0.92, 1.19, pz, m['yellow'])
    pf.box_mm((P.x + 0.75, -0.25, pz + 0.85), (P.x + 0.95, 0.25, pz + 1.15), m['steel'])
    ob_pf = pf.finish(col)
    pm.hyd_cyl("BL_LiftCyl", (0.25, 0, SLEW_Z + 0.5), (PIV.x + 1.25, 0, PIV.z - 0.3), 0.11,
               col, m, ob_tt, ob_bb)
    for w in wheels:
        pm.parent(w, ob_ch)
    pm.parent(ob_tt, ob_ch)
    pm.parent(ob_bb, ob_tt)
    pm.parent(tele[0], ob_bb)
    pm.parent(tele[1], tele[0])
    pm.parent(ob_jb, tele[1])
    pm.parent(ob_pf, ob_jb)
    pb.ref_human(ref, (1.0, -2.2, 0))

    def pose():
        """Boom 60 deg up, both tele sections out 5 m, jib 45 deg down, platform level."""
        ob_tt.rotation_euler.z = math.radians(20)
        ob_bb.rotation_euler.y = math.radians(-60)
        for t in tele:
            t.location.x += 5.0
        ob_jb.rotation_euler.y = math.radians(45)
        ob_pf.rotation_euler.y = math.radians(15)   # -(-60 + 45)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_BoomLift.png", (9, -9, 4), (1.5, 0, 1.2), 35),
        ("Preview_BoomLift_Raised.png", (24, -30, 11), (5, 0, 9), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_BoomLift.png (stowed), Preview_BoomLift_Raised.png",
                about="""
Diesel 4x4 telescopic boom lift, 20 m platform class (Genie S-65 size, no branding). Origin is the
ground point under the slewing centre. +X is the platform end when stowed.
""",
                moving="""
| Part | Motion |
|---|---|
| BL_Turntable | Slews about local Z |
| BL_Boom_Base | Rotates about local Y at the foot pin; negative Y raises (0 to about -75°) |
| BL_Boom_Tele1, BL_Boom_Tele2 | Each slides along the boom's local +X, up to about 5.3 m (Tele2 rides on Tele1) |
| BL_Jib | Rotates about local Y at the jib pin (about ±70°) |
| BL_Platform | Rotates about local Y to stay level: platform Y = -(boom Y + jib Y) |
| BL_LiftCyl_Barrel / _Rod | Look-at pair |
| BL_Wheel_FL..RR | Spin about local Y; tyre circumference 3.27 m. Front pair steers |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Stowed length × width × height | 9.42 × 2.49 × 2.72 m | Sourced, but listings vary (9.42-10.57 m long depending on jib position) |
| Platform height / horizontal reach | 19.8 / 17.1 m | Sourced (dealer listings citing Genie data) |
| Platform 2.44 × 0.91 m, boom split, tyre size | | Estimated |
""",
                sources="Boom & Bucket and Construction Equipment Guide Genie S-65 listings; Truck1 S-65 listing (metric)")


# ===========================================================================
# Scaffold tower and kit
# ===========================================================================

SC_BAY_L, SC_BAY_W, SC_LIFT, SC_N = 2.5, 1.3, 2.0, 4


def _standard(p, x, y, z0, h, m):
    p.cyl_between((x, y, z0), (x, y, z0 + h), 0.0242, m['galv'], seg=10)    # 48.3 mm tube
    z = z0 + 0.5
    while z < z0 + h - 0.01:   # cup nodes every 0.5 m
        p.cyl(0.045, 0.06, (x, y, z), m['galv'], seg=10, r2=0.03)
        z += 0.5


def _board(p, x0, x1, y0, y1, z, m):
    """Steel/timber boards, 225 mm wide, laid along X."""
    y = y0
    while y + 0.225 <= y1 + 1e-3:
        p.box_mm((x0, y + 0.005, z), (x1, y + 0.22, z + 0.038), m['wood'])
        y += 0.225


def build_scaffold_tower():
    name = "SM_ScaffoldTower"
    col, ref, m = pm.start(name)
    H = SC_LIFT * SC_N
    xs, ys = (0.0, SC_BAY_L), (0.0, SC_BAY_W)
    st = pb.Part("SC_Standards")
    for x in xs:
        for y in ys:
            st.box((0.15, 0.15, 0.006), (x, y, 0.003), m['steel'])          # base plate
            st.cyl(0.018, 0.30, (x, y, 0.15), m['steel'], seg=8)           # adjustable jack
            _standard(st, x, y, 0.15, H + 1.1, m)                          # top lift carries guardrails
    st.finish(col)
    lg = pb.Part("SC_LedgersTransoms")
    zs = [0.35] + [SC_LIFT * k for k in range(1, SC_N + 1)]
    for z in zs:
        for y in ys:
            lg.cyl_between((0, y, z), (SC_BAY_L, y, z), 0.0242, m['galv'], seg=8)
        for x in xs:
            lg.cyl_between((x, 0, z), (x, SC_BAY_W, z), 0.0242, m['galv'], seg=8)
    for y in ys:   # guardrails on the top lift
        for dz in (0.5, 1.0):
            lg.cyl_between((0, y, H + dz), (SC_BAY_L, y, H + dz), 0.0242, m['galv'], seg=8)
    for x in xs:
        for dz in (0.5, 1.0):
            lg.cyl_between((x, 0, H + dz), (x, SC_BAY_W, H + dz), 0.0242, m['galv'], seg=8)
    for k in range(SC_N):   # face braces alternating direction
        z0, z1 = 0.35 if k == 0 else SC_LIFT * k, SC_LIFT * (k + 1)
        for y in ys:
            a, b = ((0, y, z0), (SC_BAY_L, y, z1)) if k % 2 == 0 else ((SC_BAY_L, y, z0), (0, y, z1))
            lg.cyl_between(a, b, 0.0242, m['galv'], seg=8)
    lg.finish(col)
    bd = pb.Part("SC_Boards")
    for k in range(1, SC_N + 1):
        z = SC_LIFT * k + 0.025
        if k < SC_N:   # intermediate lifts: half boarded, ladder hatch side open
            _board(bd, 0.02, SC_BAY_L - 0.02, 0.02, 0.70, z, m)
        else:
            _board(bd, 0.02, SC_BAY_L - 0.02, 0.02, SC_BAY_W - 0.02, z, m)
            for y in (0.0, SC_BAY_W - 0.03):   # toe boards
                bd.box_mm((0, y, z + 0.04), (SC_BAY_L, y + 0.03, z + 0.19), m['yellow'])
            for x in (0.0, SC_BAY_L - 0.03):
                bd.box_mm((x, 0, z + 0.04), (x + 0.03, SC_BAY_W, z + 0.19), m['yellow'])
    bd.finish(col)
    ld = pb.Part("SC_Ladder")
    for k in range(SC_N):   # internal ladder in the open half, leaning
        z0 = 0.0 if k == 0 else SC_LIFT * k + 0.06
        a = Vector((0.4 + (k % 2) * 1.2, 1.0, z0))
        b = Vector((a.x + 0.5, 1.0, SC_LIFT * (k + 1) + 1.0))
        for s in (-0.22, 0.22):
            ld.cyl_between(a + Vector((s, 0, 0)), b + Vector((s, 0, 0)), 0.02, m['galv'], seg=6)
        n = int((b - a).length / 0.3)
        for i in range(1, n):
            q = a.lerp(b, i / n)
            ld.cyl_between(q - Vector((0.22, 0, 0)), q + Vector((0.22, 0, 0)), 0.014, m['galv'], seg=6)
    ld.finish(col)
    pb.ref_human(ref, (1.25, 0.65, H + 0.06))
    pb.ref_human(ref, (3.5, -1.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_ScaffoldTower.png", (11, -13, 8), (1.25, 0.65, 4.4), 30),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_ScaffoldTower.png",
                about=f"""
Cup-lock style access tower, one {SC_BAY_L} × {SC_BAY_W} m bay, {SC_N} lifts of {SC_LIFT} m
(working deck at {SC_LIFT * SC_N:.1f} m) with guardrails, toe boards and an internal ladder. Origin is
the base of the standard at the -X/-Y corner; the tower extends along +X and +Y. Static.
""",
                moving="Static. SC_Standards, SC_LedgersTransoms, SC_Boards and SC_Ladder are separate so boards or the ladder can be hidden.",
                dims="""
| Item | Value | Status |
|---|---|---|
| Bay length 2.5 m, ledger 2452 mm actual | | Sourced (cup-lock supplier data: 2.5 m is the basic access bay) |
| Cup nodes every 0.5 m | | Sourced (standards with cups at 500 mm intervals) |
| 48.3 mm tube | | Sourced (EN 12810/BS 1139 standard scaffold tube) |
| Transom 1.3 m, lift height 2.0 m, 225 mm boards, internal ladder | | Estimated (common practice, not checked against one manual) |
""",
                sources="scaffolding-direct.co.uk cup-lock ledger pages; bfs-industries.com cup-lock pages")


def build_scaffold_kit():
    name = "SM_ScaffoldKit"
    col, ref, m = pm.start(name)
    y = 0.0
    items = []

    def part(nm, fn):
        nonlocal y
        p = pb.Part(nm, pivot=(0, y, 0))
        fn(p, y)
        items.append(p.finish(col))
        y += 0.5

    part("SCK_Standard_3m", lambda p, y: _standard(p, 0, y, 0, 3.0, m))
    part("SCK_Standard_2m", lambda p, y: _standard(p, 0, y, 0, 2.0, m))
    part("SCK_Ledger_2p5m", lambda p, y: p.cyl_between((0, y, 0), (SC_BAY_L, y, 0), 0.0242, m['galv'], seg=8))
    part("SCK_Ledger_1p3m", lambda p, y: p.cyl_between((0, y, 0), (SC_BAY_W, y, 0), 0.0242, m['galv'], seg=8))
    part("SCK_Brace_2p5x2m", lambda p, y: p.cyl_between((0, y, 0), (SC_BAY_L, y, SC_LIFT), 0.0242, m['galv'], seg=8))
    part("SCK_Board_2p5m", lambda p, y: p.box_mm((0, y, 0), (SC_BAY_L, y + 0.225, 0.038), m['wood']))
    part("SCK_ToeBoard_2p5m", lambda p, y: p.box_mm((0, y, 0), (SC_BAY_L, y + 0.03, 0.15), m['yellow']))

    def jack(p, y):
        p.box((0.15, 0.15, 0.006), (0, y, 0.003), m['steel'])
        p.cyl(0.018, 0.60, (0, y, 0.3), m['steel'], seg=8)
        p.cyl(0.05, 0.04, (0, y, 0.25), m['grey'], seg=8)
    part("SCK_BaseJack", jack)
    pb.ref_human(ref, (-1.0, -1.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_ScaffoldKit.png", (6.0, -5.5, 4.5), (1.2, 1.75, 0.8), 28),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_ScaffoldKit.png",
                about="""
Loose cup-lock components for building other scaffold shapes in Unreal. Each part's pivot is its
lower or -X end on the floor/tube centreline; they are laid out 0.5 m apart along +Y.
Snap rule: standards on a 2.5 × 1.3 m grid, ledgers at multiples of 0.5 m height.
""",
                moving="Static props.",
                dims="Same sources and estimates as SM_ScaffoldTower.",
                sources="As SM_ScaffoldTower")


# ===========================================================================
# Vacuum loader truck
# ===========================================================================

def build_vacuum_truck():
    name = "SM_VacuumTruck"
    col, ref, m = pm.start(name)
    paint = m['white']
    body_paint = m['orange']
    # Sourced: ~10.67 x 2.44 x 3.91 m (Super Products Supersucker). Body ~12 m3 (estimated).
    HW, TR, TW = 1.22, 0.53, 0.30
    AX = [3.55, -1.95, -3.30]
    ch = pb.Part("VT_Chassis")
    ch.box_mm((-5.0, -0.5, 0.75), (4.9, 0.5, 1.05), m['steel'])
    cab(ch, 3.4, 5.34, -HW, HW, 1.05, 3.05, m, paint)
    ch.box_mm((-0.4, -HW, 1.05), (3.3, HW, 3.10), m['grey'])         # blower + filter module
    for i in range(3):   # louvres
        ch.box_mm((0.0 + i * 1.0, -HW - 0.01, 1.6), (0.8 + i * 1.0, -HW, 2.6), m['steel'])
    ch.cyl(0.45, 2.0, (1.5, 0.7, 2.2), m['steel'], rot=(0, 90, 0), seg=20)     # cyclone/filter drum
    ch.box_mm((-5.3, -0.45, 0.85), (-5.0, 0.45, 1.0), m['steel'])            # rear bumper
    ob_ch = ch.finish(col)
    wheels = []
    for i, x in enumerate(AX):
        for s, t in ((1, "L"), (-1, "R")):
            wheels.append(pm.wheel(f"VT_Wheel_A{i + 1}{t}", (x, s * (HW - TW / 2), TR), TR, TW, col, m))
    HX, HZ = -5.05, 1.15      # body tipping hinge at the rear
    bd = pb.Part("VT_DebrisBody", pivot=(HX, 0, HZ))
    bd.cyl(1.05, 4.5, (-2.75, 0, 2.25), body_paint, rot=(0, 90, 0), seg=32)   # ~13 m3 gross
    bd.box_mm((-4.9, -0.9, HZ), (-0.6, 0.9, 1.6), m['steel'])                  # subframe
    for x in (-4.4, -3.0, -1.6):
        bd.cyl(1.09, 0.08, (x, 0, 2.25), m['steel'], rot=(0, 90, 0), seg=32)   # hoops
    bd.box_mm((-1.2, -0.25, 3.25), (-0.5, 0.25, 3.91 - 0.45), m['steel'])     # boom mount
    ob_bd = bd.finish(col)
    dr = pb.Part("VT_RearDoor", pivot=(-5.05, 0, 3.30))
    dr.cyl(1.05, 0.12, (-5.06, 0, 2.25), m['steel'], rot=(0, 90, 0), seg=32)
    dr.box_mm((-5.15, -0.3, 1.25), (-5.10, 0.3, 1.45), m['grey'])               # dump valve
    ob_dr = dr.finish(col)
    BP = Vector((-0.85, 0, 3.46))      # boom slew/luff pin
    bm = pb.Part("VT_Boom", pivot=BP)
    bm.cyl_between(BP, BP + Vector((4.6, 0, 0.0)), 0.11, body_paint, seg=16)   # 8 in boom tube
    bm.cyl_between(BP + Vector((4.6, 0, 0)), BP + Vector((5.0, 0, -0.5)), 0.11, body_paint, seg=16)
    ob_bm = bm.finish(col)
    hs = pb.Part("VT_SuctionHose", pivot=BP + Vector((5.0, 0, -0.5)))
    hs.cyl_between(BP + Vector((5.0, 0, -0.5)), BP + Vector((5.0, 0, -2.4)), 0.12, m['rubber'], seg=16)
    ob_hs = hs.finish(col)
    pm.hyd_cyl("VT_TipCyl", (-0.5, 0, 1.05), (-1.2, 0, 1.6), 0.10, col, m, ob_ch, ob_bd)
    for w in wheels:
        pm.parent(w, ob_ch)
    pm.parent(ob_bd, ob_ch)
    pm.parent(ob_dr, ob_bd)
    pm.parent(ob_bm, ob_bd)
    pm.parent(ob_hs, ob_bm)
    pb.ref_human(ref, (1.0, -2.2, 0))

    def pose():
        """Dump: body tipped 40 deg (sourced dump angle), rear door open 80 deg, boom swung."""
        ob_bd.rotation_euler.y = math.radians(-40)
        ob_dr.rotation_euler.y = math.radians(80)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_VacuumTruck.png", (11, -10, 4.5), (0, 0, 1.8), 35),
        ("Preview_VacuumTruck_Dump.png", (-13, -10, 5), (-4, 0, 2.2), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_VacuumTruck.png, Preview_VacuumTruck_Dump.png",
                about="""
Three-axle industrial vacuum loader (Supersucker / Vacall AllVac size, no branding) for dust,
spill and baghouse clean-up. Origin is the ground point at the chassis middle. +X is the cab end.
""",
                moving="""
| Part | Motion |
|---|---|
| VT_DebrisBody | Tips about local Y at the rear hinge; dump is about -40° |
| VT_RearDoor | Swings up about local Y at its top hinge (+80° open); child of the body |
| VT_Boom | Slews about local Z and luffs about local Y at its pin on the body |
| VT_SuctionHose | Hangs from the boom tip; rotate about X/Y to swing |
| VT_TipCyl_Barrel / _Rod | Look-at pair |
| VT_Wheel_A1L..A3R | Spin about local Y; circumference 3.33 m. A1 steers |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Length × width × height | 10.67 × 2.44 × 3.91 m | Sourced (Super Products Supersucker data) |
| Debris body | ≈13 m³ gross in the model | Estimated; real 9-14 m³ (DISAB SDC 100 9 m³, AllVac 18 yd³ ≈ 13.8 m³) |
| Dump angle 40° | | Sourced (Vacall AllVac) |
| 8 in (≈200 mm) boom and hose, module layout | | Estimated |
""",
                sources="Super Products Supersucker spec sheet (directindustry PDF); Southeastern Equipment Vacall AllVac page; DISAB SDC 100 data")


# ===========================================================================
# Ride-on sweeper
# ===========================================================================

def build_sweeper():
    name = "SM_Sweeper"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    # Sourced: 2.36 x 1.59 x 2.095 m (with overhead guard); hopper 395 L, dump height 1.525 m.
    ch = pb.Part("SW_Chassis")
    ch.box_mm((-1.18, -0.70, 0.12), (0.95, 0.70, 0.95), paint)
    ch.box_mm((-1.18, -0.55, 0.95), (-0.45, 0.55, 1.15), m['steel'])        # engine cover
    ch.box_mm((-0.55, -0.35, 0.95), (-0.15, 0.35, 1.35), m['steel'])        # seat
    ch.box_mm((0.05, -0.15, 0.95), (0.20, 0.15, 1.35), m['steel'])          # steering column
    for x in (0.25, -1.10):   # overhead guard posts
        for s in (1, -1):
            ch.cyl_between((x, s * 0.65, 0.95), (x, s * 0.65, 2.075), 0.03, m['steel'], seg=8)
    ch.box_mm((-1.12, -0.70, 2.055), (0.30, 0.70, 2.095), m['steel'])
    ch.box_mm((-0.4, -0.4, 0.1), (0.4, 0.4, 0.12), m['steel'])              # main broom housing lip
    ob_ch = ch.finish(col)
    wheels = []
    for x, y, t in ((0.70, 0.62, "FL"), (0.70, -0.62, "FR")):
        wheels.append(pm.wheel(f"SW_Wheel_{t}", (x, y, 0.22), 0.22, 0.14, col, m))
    wheels.append(pm.wheel("SW_Wheel_Rear", (-0.95, 0, 0.22), 0.22, 0.16, col, m))
    br = pb.Part("SW_MainBroom", pivot=(0, 0, 0.18))
    br.cyl(0.18, 1.10, (0, 0, 0.18), m['rubber'], rot=(90, 0, 0), seg=20)
    ob_br = br.finish(col)
    sbs = []
    for s, t in ((1, "L"), (-1, "R")):
        c = (1.00, s * 0.55, 0.06)
        sb = pb.Part(f"SW_SideBrush_{t}", pivot=c)
        sb.cyl(0.25, 0.05, (c[0], c[1], 0.05), m['rubber'], seg=20)
        sb.cyl(0.06, 0.25, (c[0], c[1], 0.2), m['steel'], seg=8)
        sbs.append(sb.finish(col))
    HP = Vector((0.95, 0, 0.95))     # hopper lift-arm pivot (estimated)
    ha = pb.Part("SW_HopperArm", pivot=HP)
    for s in (1, -1):
        ha.beam_between(HP + Vector((0, s * 0.65, 0)), HP + Vector((0.25, s * 0.65, -0.55)), 0.08, 0.08, m['steel'])
    ob_ha = ha.finish(col)
    HD = HP + Vector((0.25, 0, -0.55))
    hp = pb.Part("SW_Hopper", pivot=HD)
    hp.box_mm((0.95, -0.62, 0.20), (1.18, 0.62, 0.80), paint)
    hp.box_mm((1.18, -0.62, 0.20), (1.20, 0.62, 0.80), m['steel'])
    ob_hp = hp.finish(col)
    for w in wheels + [ob_br] + sbs + [ob_ha]:
        pm.parent(w, ob_ch)
    pm.parent(ob_hp, ob_ha)
    pb.ref_human(ref, (-0.3, 1.3, 0))

    def pose():
        """High dump: arm raised so the hopper lip is at ~1.5 m, hopper tipped forward."""
        ob_ha.rotation_euler.y = math.radians(-115)
        ob_hp.rotation_euler.y = math.radians(150)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_Sweeper.png", (2.5, -4.5, 2.4), (0, 0, 0.8), 35),
        ("Preview_Sweeper_Dump.png", (4.0, -5.0, 2.6), (0.5, 0, 1.2), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_Sweeper.png, Preview_Sweeper_Dump.png",
                about="""
Ride-on industrial sweeper with a high-dump hopper (Tennant S30 size, no branding). Origin is the
ground point under the main broom. +X is forward (hopper end).
""",
                moving="""
| Part | Motion |
|---|---|
| SW_MainBroom | Spins about local Y |
| SW_SideBrush_L/R | Spin about local Z (L clockwise seen from above, R anticlockwise) |
| SW_HopperArm | Rotates about local Y; about -115° raises the hopper to dump height |
| SW_Hopper | Child of the arm; rotate about local Y to tip (preview +150° with the arm raised) |
| SW_Wheel_FL/FR/Rear | Spin about local Y; the rear wheel steers about Z |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Length × width × height (guard) | 2.36 × 1.59 × 2.095 m | Sourced (Tennant S30 dealer data). Width here is the single side-brush path; the model body is 1.40 m |
| Hopper 395 L, dump height up to 1.525 m | | Sourced |
| Three-wheel layout, arm geometry, broom size | | Estimated (not checked against an S30 drawing) |
""",
                sources="clemas.co.uk and hughcrane.co.uk Tennant S30 pages")


# ===========================================================================
# README
# ===========================================================================

BUILDERS = dict(MobileCrane=build_mobile_crane, ScissorLift=build_scissor_lift, BoomLift=build_boom_lift,
                ScaffoldTower=build_scaffold_tower, ScaffoldKit=build_scaffold_kit,
                VacuumTruck=build_vacuum_truck, Sweeper=build_sweeper)


INTRO = """
Shutdown and clean-up vehicles. Each asset is a standalone prop at its own origin (not tied to the
plant layout). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_mobile_equipment.py`. Brand names are size references only; the
models carry no logos. In the .blend the moving parts are parented for posing; hydraulic cylinder
halves use Damped Track constraints to non-exported empties.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
