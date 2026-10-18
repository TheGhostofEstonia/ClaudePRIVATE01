"""
build_skulling_mouth_cleaning.py - skull removal stations and the converter mouth cleaner.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_skulling_mouth_cleaning.py
      (add  -- LadleSkulling  to build one asset only)

Assets:
    Meshes/SkullingStations/SM_LadleSkullingStation   tipping cradle + pedestal breaker + skull bunker
    Meshes/SkullingStations/SM_PotSkullingStation     portal "pot knock" frame with a drop ram
    Meshes/ConverterMouthCleaner/SM_ConverterMouthCleaner  rail-mounted boom with ram and blade

All three are own designs built around sourced practice (see each README).
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

LADLE_R, LADLE_H, LADLE_TRUN_Z = 1.75, 3.8, 2.6   # REF ladle (same proxy as the relining tower)


def ref_ladle(ref, centre, inverted_deg=0.0):
    """REF ladle proxy with trunnions along Y; centre = trunnion axis point."""
    p = pb.Part("REF_Ladle", pivot=centre)
    lm = pb.mat("M_REF_LadleShell", (0.2, 0.2, 0.2), 0.6, 0.6)
    sk = pb.mat("M_REF_Skull", (0.25, 0.2, 0.15), 0.3, 0.9)
    c = Vector(centre)
    base = c - Vector((0, 0, LADLE_TRUN_Z))
    p.cyl(LADLE_R, LADLE_H, base + Vector((0, 0, LADLE_H / 2)), lm, seg=32, r2=LADLE_R)
    p.cyl(LADLE_R - 0.25, 0.3, base + Vector((0, 0, LADLE_H - 0.1)), sk, seg=32)   # skull at the rim
    for s in (1, -1):
        p.cyl(0.25, 0.5, c + Vector((0, s * (LADLE_R + 0.25), 0)), lm, rot=(90, 0, 0), seg=16)
    ob = p.finish(ref)
    ob.rotation_euler.y = math.radians(inverted_deg)
    return ob


# ===========================================================================
# Ladle skulling station
# ===========================================================================

def build_ladle_skulling():
    name = "SM_LadleSkullingStation"
    folder = "SkullingStations"
    col, ref, m = pm.start(name)
    PIV = Vector((0, 0, 4.4))           # cradle tipping axis (along Y)
    PIT = -1.2                          # skull bunker floor
    ba = pb.Part("LSS_Base")
    for s in (1, -1):                   # cradle pedestals, bearing blocks, tilt drive (motor + gearbox)
        ba.box_mm((-1.6, s * 3.05 - 0.45, 0), (1.0, s * 3.05 + 0.45, PIV.z - 0.5), m['concrete'])
        ba.box_mm((-0.45, s * 3.05 - 0.3, PIV.z - 0.5), (0.45, s * 3.05 + 0.3, PIV.z + 0.3), m['steel'])
        ba.box_mm((-1.5, s * 3.05 - 0.4, PIV.z - 1.7), (-0.9, s * 3.05 + 0.4, PIV.z - 0.5), m['blue'])
        ba.cyl(0.2, 0.5, (-1.2, s * 3.6, PIV.z - 1.3), m['blue'], rot=(90, 0, 0), seg=14)
    ba.box_mm((-5.0, -1.9, PIT - 0.3), (-1.0, 1.9, PIT), m['concrete'])     # bunker floor (-X side)
    ba.box_mm((-1.0, -1.9, PIT - 0.3), (2.2, 1.9, PIT), m['concrete'])
    for y0, y1 in ((-2.2, -1.9), (1.9, 2.2)):                              # bunker side walls, steel lined
        ba.box_mm((-5.0, y0, PIT), (2.2, y1, 1.2), m['concrete'])
    ba.box_mm((2.2, -2.2, PIT), (2.5, 2.2, 1.2), m['concrete'])             # back wall
    ba.box_mm((-5.0, -1.9, PIT), (-4.7, 1.9, -0.0), m['steel'])             # loader kerb at the open end
    ba.box_mm((2.0, -1.9, PIT), (2.2, 1.9, 1.2), m['steel'])               # impact liner
    ob_ba = ba.finish(col)
    # cradle: U-frame holding the ladle trunnions, rotates about Y at PIV
    cr = pb.Part("LSS_Cradle", pivot=PIV)
    for s in (1, -1):
        y = s * (LADLE_R + 0.55)
        cr.box_mm((-0.35, y - 0.18, PIV.z - 3.0), (0.35, y + 0.18, PIV.z + 0.35), m['yellow'])
        cr.cyl(0.32, 0.6, (0, s * 2.75, PIV.z), m['grey'], rot=(90, 0, 0), seg=20)      # journal
        cr.cyl(1.3, 0.12, (0, s * 2.62, PIV.z), m['steel'], rot=(90, 0, 0), seg=48)     # drive ring gear
    cr.box_mm((-0.35, -(LADLE_R + 0.55), PIV.z - 3.0), (0.35, LADLE_R + 0.55, PIV.z - 2.7), m['yellow'])  # bottom bar
    ob_cr = cr.finish(col)
    # pedestal breaker on a plinth beside the bunker (-X, +Y corner), reaching into the inverted ladle
    PB = Vector((-3.0, 3.6, 0))
    ped = pb.Part("LSS_BreakerPedestal")
    ped.box_mm((PB.x - 1.0, PB.y - 1.0, 0), (PB.x + 1.0, PB.y + 1.0, 2.0), m['concrete'])
    ped.cyl(0.5, 1.2, PB + Vector((0, 0, 2.6)), m['yellow'], seg=24)
    ob_ped = ped.finish(col)
    SZ = 3.2
    tu = pb.Part("LSS_BreakerTurret", pivot=(PB.x, PB.y, SZ))
    tu.cyl(0.6, 0.2, (PB.x, PB.y, SZ + 0.1), m['grey'], seg=24)
    tu.box_mm((PB.x - 0.5, PB.y - 0.35, SZ + 0.2), (PB.x + 0.5, PB.y + 0.35, SZ + 1.0), m['yellow'])
    tu.box_mm((PB.x - 1.4, PB.y - 0.5, SZ + 0.2), (PB.x - 0.5, PB.y + 0.5, SZ + 1.2), m['steel'])   # power pack
    ob_tu = tu.finish(col)
    # boom laid along +X from the pin in rest pose
    BP = Vector((PB.x + 0.3, PB.y, SZ + 0.8))
    L1, L2 = 4.2, 3.4
    bo = pb.Part("LSS_BreakerBoom", pivot=BP)
    bo.box_mm((BP.x - 0.2, BP.y - 0.18, BP.z - 0.22), (BP.x + L1, BP.y + 0.18, BP.z + 0.22), m['yellow'])
    bo.box_mm((BP.x + 1.2, BP.y - 0.1, BP.z - 0.42), (BP.x + 1.6, BP.y + 0.1, BP.z - 0.22), m['steel'])
    bo.box_mm((BP.x + 0.6, BP.y - 0.1, BP.z + 0.22), (BP.x + 1.0, BP.y + 0.1, BP.z + 0.4), m['steel'])
    ob_bo = bo.finish(col)
    J = BP + Vector((L1, 0, 0))
    st = pb.Part("LSS_BreakerStick", pivot=J)
    st.box_mm((J.x - 0.3, J.y - 0.15, J.z - 0.18), (J.x + L2, J.y + 0.15, J.z + 0.18), m['yellow'])
    st.box_mm((J.x - 0.3, J.y - 0.08, J.z + 0.18), (J.x, J.y + 0.08, J.z + 0.45), m['steel'])
    ob_st = st.finish(col)
    K = J + Vector((L2, 0, 0))
    hm = pb.Part("LSS_BreakerHammer", pivot=K)
    hm.box_mm((K.x, K.y - 0.22, K.z - 0.25), (K.x + 1.5, K.y + 0.22, K.z + 0.25), m['steel'])
    hm.cyl_between(K + Vector((1.5, 0, 0)), K + Vector((2.1, 0, 0)), 0.07, m['grey'], seg=12, r2=0.02)
    ob_hm = hm.finish(col)
    pm.hyd_cyl("LSS_BoomCyl", (PB.x + 0.4, PB.y, SZ + 0.25), (BP.x + 1.4, BP.y, BP.z - 0.42), 0.12, col, m, ob_tu, ob_bo)
    pm.hyd_cyl("LSS_StickCyl", (BP.x + 0.8, BP.y, BP.z + 0.4), (J.x - 0.15, J.y, J.z + 0.45), 0.1, col, m, ob_bo, ob_st)
    pm.parent(ob_tu, ob_ped)
    pm.parent(ob_bo, ob_tu)
    pm.parent(ob_st, ob_bo)
    pm.parent(ob_hm, ob_st)
    lad = ref_ladle(ref, PIV)
    pm.parent(lad, ob_cr)
    pb.ref_human(ref, (-2.0, -3.5, 0))

    def pose():
        """Ladle inverted 150 deg over the bunker, breaker reaching into it."""
        ob_cr.rotation_euler.y = math.radians(-150)
        ob_tu.rotation_euler.z = math.radians(-60)    # aim at the ladle mouth
        ob_bo.rotation_euler.y = math.radians(-40)
        ob_st.rotation_euler.y = math.radians(130)    # stick hangs straight down
        ob_hm.rotation_euler.y = math.radians(-90)    # hammer level, pointing into the mouth

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, folder, [
        ("Preview_LadleSkulling.png", (12, -13, 9), (-0.5, 0, 2.0), 35),
        ("Preview_LadleSkulling_Working.png", (-13, -11, 9), (-1.0, 0.5, 2.8), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, folder=folder,
                previews="Preview_LadleSkulling.png (upright), Preview_LadleSkulling_Working.png (inverted, breaker in)",
                about=f"""
The crane sets a ladle into the cradle by its trunnions. A geared drive on each pedestal (ring gear
on the cradle journal, motor and gearbox on the pedestal) tips the cradle about
{abs(150)}° so the mouth faces down over a steel-lined skull bunker ({PIT} m floor), and a
pedestal-mounted hydraulic breaker on a plinth knocks the skull and lip build-up loose. A loader
clears the bunker from the open -X end. Origin is the floor under the tipping axis; the tipping
axis runs along Y at {PIV.z} m. The REF ladle (Ø3.5 × 3.8 m, trunnions {LADLE_TRUN_Z} m above its
base) is not exported.
Own design. Sourced practice: skull is knocked out with hydraulic or pneumatic hammers, and
hydraulic pushers were used on ladles (see Sources).
""",
                moving="""
| Part | Motion |
|---|---|
| LSS_Cradle | Rotates about local Y; tip is negative Y (preview -150°). Carry the ladle with it |
| LSS_BreakerTurret | Slews about local Z |
| LSS_BreakerBoom | Rotates about local Y (negative raises) |
| LSS_BreakerStick, LSS_BreakerHammer | Rotate about local Y (positive folds down) |
| LSS_BoomCyl, LSS_StickCyl | Look-at pairs |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Whole station | | Own design, sized to the REF ladle |
| Breaker reach about 9 m from the pedestal | | Estimated (pedestal breakers for grizzlies cover 6-12 m) |
""",
                sources="onemine.org 'A New Method of Removing Skulls from Direct-Metal Ladles' (hydraulic push-out); US4047708 background (jack hammers for skull); research file (Mount Isa 'pot knock' for slag pots)")


# ===========================================================================
# Pot skulling station (pot knock)
# ===========================================================================

POT_RIM_R, POT_BASE_R, POT_H = 1.80, 1.20, 2.60       # same proxy as SM_SlagPotCarrier
POT_TRUN_Z, POT_TRUN_HALF = 1.80, 2.02


def build_pot_skulling():
    name = "SM_PotSkullingStation"
    folder = "SkullingStations"
    col, ref, m = pm.start(name)
    SAD_Z = 3.0                       # trunnion saddle height (pot hangs inverted)
    TOP = 6.8
    fr = pb.Part("PSS_Frame")
    for x in (-2.2, 2.2):
        for y in (-2.6, 2.6):
            fr.beam_between((x, y, 0), (x, y, TOP), 0.4, 0.4, m['yellow'])
            fr.box((0.8, 0.8, 0.04), (x, y, 0.02), m['steel'])
    for y in (-2.6, 2.6):             # side beams carrying the saddles
        fr.beam_between((-2.2, y, SAD_Z - 0.3), (2.2, y, SAD_Z - 0.3), 0.35, 0.5, m['yellow'])
        fr.box_mm((-0.35, y - (0.2 if y > 0 else -0.2) - 0.2, SAD_Z - 0.55),
                  (0.35, y - (0.2 if y > 0 else -0.2) + 0.2, SAD_Z - 0.25), m['steel'])
        for x in (-0.35, 0.35):       # V-saddle cheeks
            fr.box_mm((x - 0.06, y - 0.6 if y > 0 else y + 0.2, SAD_Z - 0.25),
                      (x + 0.06, y - 0.2 if y > 0 else y + 0.6, SAD_Z + 0.2), m['steel'])
    for x in (-2.2, 2.2):
        fr.beam_between((x, -2.6, TOP - 0.3), (x, 2.6, TOP - 0.3), 0.4, 0.6, m['yellow'])
    fr.beam_between((0, -2.6, TOP - 0.3), (0, 2.6, TOP - 0.3), 0.5, 0.7, m['yellow'])   # ram beam
    fr.box_mm((-0.6, -0.6, TOP - 0.65), (0.6, 0.6, TOP + 0.9), m['steel'])                # ram housing
    fr.box_mm((-2.5, -2.9, -0.02), (2.5, 2.9, 0.0), m['steel'])                          # wear plate
    for x in (-2.2, 2.2):             # skull deflectors between the -X legs (open +X for the loader)
        if x < 0:
            fr.box_mm((x - 0.1, -2.4, 0), (x + 0.1, 2.4, 1.5), m['steel'])
    ob_fr = fr.finish(col)
    RZ = TOP - 0.65
    ram = pb.Part("PSS_Ram", pivot=(0, 0, RZ))
    ram.cyl(0.22, 1.4, (0, 0, RZ - 0.7), m['grey'], seg=20)
    ram.cyl(0.45, 0.35, (0, 0, RZ - 1.55), m['steel'], seg=20)                            # striker head
    ob_ram = ram.finish(col)
    # REF pot hung upside down in the saddles
    pp = pb.Part("REF_SlagPot_Inverted")
    pm_ = pb.mat("M_REF_Pot", (0.2, 0.2, 0.22), 0.6, 0.6)
    base_z = SAD_Z + POT_TRUN_Z
    pp.cyl(POT_RIM_R, POT_H, (0, 0, base_z - POT_H / 2), pm_, seg=32, r2=POT_BASE_R)   # mouth down
    for s in (1, -1):
        pp.cyl(0.18, 0.3, (0, s * (POT_TRUN_HALF - 0.15), SAD_Z), pm_, rot=(90, 0, 0), seg=12)
    pp.finish(ref)
    sk = pb.Part("REF_SkullHeap")
    sk.cyl(1.3, 0.6, (0.4, 0, 0.3), pb.mat("M_REF_Skull", (0.25, 0.2, 0.15), 0.3, 0.9), seg=12, r2=0.3)
    sk.finish(ref)
    pb.ref_human(ref, (3.5, -3.5, 0))

    def pose():
        ob_ram.location.z -= 0.25     # striker touching the pot base

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, folder, [
        ("Preview_PotSkulling.png", (14, -12, 8), (0, 0, 3.2), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, folder=folder,
                previews="Preview_PotSkulling.png (ram down on an inverted pot)",
                about=f"""
"Pot knock" station for slag pots that come back from the cooling yard with skull stuck inside.
The crane (or a pot carrier with a crane assist) hangs the pot upside down by its trunnions in
two V-saddles at {SAD_Z} m. A hydraulic ram in the top beam strikes the pot base, the skull drops
onto a wear plate, and a loader clears it from the open +X side. Origin is the floor under the
pot centre. Trunnions lie along Y, matching SM_SlagPotCarrier's assumed pot (trunnion
{POT_TRUN_Z} m above the base, tips at ±{POT_TRUN_HALF} m).
Own design. Mount Isa runs a "pot knock" deskulling system on its pot route (sourced), but I
found no drawing of it.
""",
                moving=f"""
| Part | Motion |
|---|---|
| PSS_Ram | Moves along -Z; 0.25 m down touches the base of the REF pot (preview pose) |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Pot proxy rim Ø3.6, base Ø2.4, 2.6 m tall | | Assumed (same as SM_SlagPotCarrier) |
| Frame 4.4 × 5.2 × 6.8 m, saddles at 3.0 m | | Own design |
""",
                sources="research file [S8]: Mount Isa slag pot route with a 'pot knock' deskulling system")


# ===========================================================================
# Converter mouth cleaner
# ===========================================================================

def build_mouth_cleaner():
    name = "SM_ConverterMouthCleaner"
    folder = "ConverterMouthCleaner"
    col, ref, m = pm.start(name)
    GAUGE = 3.0
    WR = 0.40
    ca = pb.Part("CMC_Carriage")
    ca.box_mm((-2.4, -GAUGE / 2 - 0.25, 0.55), (2.4, GAUGE / 2 + 0.25, 1.35), m['yellow'])
    for s in (1, -1):   # bogie sides
        ca.box_mm((-2.6, s * GAUGE / 2 - 0.2, 0.25), (2.6, s * GAUGE / 2 + 0.2, 0.75), m['steel'])
    ca.box_mm((-2.4, -1.9, 1.35), (-0.8, -0.2, 3.4), m['white'])          # operator cab
    ca.box_mm((-0.81, -1.8, 2.4), (-0.79, -0.3, 3.2), m['glass'])
    ca.box_mm((-0.75, -2.0, 1.35), (-0.65, -0.1, 3.6), m['steel'])        # heat shield in front of cab
    ca.box_mm((-2.4, 0.4, 1.35), (-1.0, 1.7, 2.6), m['grey'])             # hydraulic power pack
    ca.box_mm((2.4, -0.8, 0.6), (2.6, 0.8, 1.1), m['steel'])              # buffer
    ca.box_mm((-2.6, -0.8, 0.6), (-2.4, 0.8, 1.1), m['steel'])
    ob_ca = ca.finish(col)
    wheels = []
    for x, t in ((1.8, "F"), (-1.8, "R")):
        for s, u in ((1, "L"), (-1, "R")):
            w = pb.Part(f"CMC_RailWheel_{t}{u}", pivot=(x, s * GAUGE / 2, WR))
            w.cyl(WR, 0.12, (x, s * GAUGE / 2, WR), m['steel'], rot=(90, 0, 0), seg=24)
            w.cyl(WR + 0.04, 0.03, (x, s * (GAUGE / 2 - 0.07), WR), m['steel'], rot=(90, 0, 0), seg=24)   # flange
            wheels.append(w.finish(col))
    SZ = 1.35
    tu = pb.Part("CMC_Turret", pivot=(0.8, 0.6, SZ))
    tu.cyl(0.8, 0.3, (0.8, 0.6, SZ + 0.15), m['grey'], seg=28)
    for s in (1, -1):
        tu.box_mm((0.2, 0.6 + s * 0.35 - 0.08, SZ + 0.3), (1.2, 0.6 + s * 0.35 + 0.08, SZ + 1.6), m['yellow'])
    ob_tu = tu.finish(col)
    P = Vector((0.6, 0.6, SZ + 1.4))
    bo = pb.Part("CMC_Boom", pivot=P)
    bo.box_mm((P.x - 0.4, P.y - 0.26, P.z - 0.3), (P.x + 5.0, P.y + 0.26, P.z + 0.3), m['yellow'])
    bo.box_mm((P.x + 1.5, P.y - 0.12, P.z - 0.55), (P.x + 2.0, P.y + 0.12, P.z - 0.3), m['steel'])
    ob_bo = bo.finish(col)
    ra = pb.Part("CMC_Ram", pivot=P)
    ra.box_mm((P.x + 1.0, P.y - 0.18, P.z - 0.2), (P.x + 6.2, P.y + 0.18, P.z + 0.2), m['grey'])
    ob_ra = ra.finish(col)
    BL = Vector((P.x + 6.2, P.y, P.z))
    bl = pb.Part("CMC_Blade", pivot=BL)
    bl.box_mm((BL.x, BL.y - 0.25, BL.z - 0.25), (BL.x + 0.5, BL.y + 0.25, BL.z + 0.25), m['steel'])
    bl.poly_prism([(BL.x + 0.5, BL.z - 0.35), (BL.x + 1.1, BL.z - 0.05), (BL.x + 1.1, BL.z + 0.05),
                   (BL.x + 0.5, BL.z + 0.35)], BL.y - 0.6, BL.y + 0.6, m['grey'], plane='XZ')   # chisel blade
    ob_bl = bl.finish(col)
    pm.hyd_cyl("CMC_LuffCyl", (1.6, 0.6, SZ + 0.3), (P.x + 1.75, P.y, P.z - 0.55), 0.14, col, m, ob_tu, ob_bo)
    for w in wheels + [ob_tu]:
        pm.parent(w, ob_ca)
    pm.parent(ob_bo, ob_tu)
    pm.parent(ob_ra, ob_bo)
    pm.parent(ob_bl, ob_ra)
    # REF rails and converter shell with the mouth turned toward the machine
    rl = pb.Part("REF_Rails")
    rm = pb.mat("M_REF_Rail", (0.4, 0.4, 0.4), 0.9, 0.4)
    for s in (1, -1):
        rl.box_mm((-12, s * GAUGE / 2 - 0.04, 0), (12, s * GAUGE / 2 + 0.04, 0.15), rm)
    rl.finish(ref)
    cv = pb.Part("REF_ConverterShell")
    cm = pb.mat("M_REF_Converter", (0.18, 0.18, 0.2), 0.6, 0.6)
    CX, CZ, CR = 11.0, 4.5, 2.2
    cv.cyl(CR, 10.0, (CX, 0.6, CZ), cm, rot=(90, 0, 0), seg=40)
    cv.box_mm((CX - CR - 0.5, 0.6 - 1.0, CZ - 0.75), (CX - CR + 0.4, 0.6 + 1.0, CZ + 0.75),
              pb.mat("M_REF_Accretion", (0.3, 0.25, 0.18), 0.2, 0.9))   # mouth lip with build-up
    cv.finish(ref)
    pb.ref_human(ref, (-1.0, -3.2, 0))

    def pose():
        """Boom raised toward the converter mouth, ram extended 1.2 m, blade tilted."""
        ob_bo.rotation_euler.y = math.radians(-12)
        ob_ra.location.x += 1.2
        ob_bl.rotation_euler.y = math.radians(10)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, folder, [
        ("Preview_MouthCleaner.png", (6, -12, 6), (2.0, 0, 2.0), 35),
        ("Preview_MouthCleaner_Working.png", (5, -15, 8), (5.0, 0, 3.2), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, folder=folder,
                previews="Preview_MouthCleaner.png, Preview_MouthCleaner_Working.png",
                about=f"""
Rail-mounted converter mouth cleaner ("mouth breaker"). It runs on a {GAUGE} m gauge track along
the converter aisle. With a converter rolled so its mouth faces the aisle, the luffing boom
pushes a hydraulic ram with a chisel blade into the mouth and shears off the accretions
(frozen slag and metal) that build up on the lip. A heat shield protects the cab. Origin is the
rail-level point at the carriage centre; the boom points +X. The REF converter shell (Ø4.4 m) and
rails are not exported.
Own design. Sourced: mouth build-up must be scraped off and this damages mouth refractory, which
then needs hot gunning; C21C5/4693 "Skull removal; Cleaning of the converter mouth" is a patent
class of its own. I found no drawing of a specific machine.
""",
                moving="""
| Part | Motion |
|---|---|
| CMC_Carriage | Travels along X on the rails |
| CMC_RailWheel_* | Spin about local Y; circumference 2.51 m |
| CMC_Turret | Slews about local Z (±30° is enough to square up to a mouth) |
| CMC_Boom | Luffs about local Y (negative raises) |
| CMC_Ram | Slides along the boom's local +X (stroke about 2 m) |
| CMC_Blade | Tilts about local Y |
| CMC_LuffCyl_Barrel / _Rod | Look-at pair |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Converter shell Ø4.4 m | | Typical 4-4.5 m from the research file (not sourced to one plant) |
| Machine 5.2 × 3.5 m, boom + ram ≈ 7 m reach, 3.0 m gauge | | Own design |
""",
                sources="https://onemine.org/documents/peirce-smith-converter-mouth-redesign-overview ; https://patents.google.com/patent/US4591134 (classification C21C5/4693)")


BUILDERS = dict(LadleSkulling=build_ladle_skulling, PotSkulling=build_pot_skulling,
                MouthCleaner=build_mouth_cleaner)

INTROS = {
    "SkullingStations": """
Stations for knocking solidified skull out of ladles and slag pots. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_skulling_mouth_cleaning.py`. Both are fixed
installations at their own origin; place them beside the converter aisle (ladles) and on the slag
pot route between the cooling yard and the furnace (pots).
""",
    "ConverterMouthCleaner": """
Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_skulling_mouth_cleaning.py`. Standalone at its own origin; lay the
rails along the converter aisle in front of the converter row.
""",
}


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    results = [BUILDERS[k]() for k in (argv or BUILDERS)]
    if not argv:
        for folder, intro in INTROS.items():
            pm.write_group_readme(folder, intro, [r for r in results if r['folder'] == folder])
