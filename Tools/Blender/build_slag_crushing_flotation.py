"""
build_slag_crushing_flotation.py - SM_SlagCrushingFlotation (slag concentrator).

Run:  blender -b --factory-startup --python Tools/Blender/build_slag_crushing_flotation.py

Shares the flash furnace origin (Blender +X = east, +Y = north, assumed).
Flow: loader ramp -> ROM hopper with static grizzly and rock breaker -> vibrating grizzly
feeder -> jaw crusher -> CV01 -> scalping screen -> cone crusher (oversize) -> CV02 ->
fine ore bin -> CV03 -> ball mill + cyclones -> rougher/scavenger and cleaner flotation
cells -> concentrate thickener. Tailings leave through a stub flange.
Sized for roughly 500-600 t/d of slow-cooled slag (the cooling yard output), all estimated.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "Meshes", "SlagCrushingFlotation")
NAME = "SM_SlagCrushingFlotation"

# ---------------------------------------------------------------------------
# Layout (flash furnace coordinates). All estimated / own design.
# ---------------------------------------------------------------------------
LINE_Y = 187.0                         # centre line of the loader ramp, hopper and jaw crusher
RAMP_X = (-58.0, -123.0)               # loader ramp, 10 % up to the tipping platform
PLAT_Z = 6.5                           # tipping platform / hopper rim
HOP_X = -134.0                         # ROM hopper centre
JAW_X = -140.0                         # jaw crusher centre
JAW_BASE_Z = 0.5
TOWER = (-140.0, 236.0)                # screen / cone crusher tower centre
FOB = (-140.0, 284.0)                  # fine ore bin centre
BLDG = (-205.0, 268.0, -160.0, 300.0)  # mill and flotation building x0, y0, x1, y1
EAVE_Z = 14.0
MILL_Y, MILL_Z = 290.0, 3.0            # ball mill axis
MILL_FEED_X = -165.0
MILL_R, MILL_L = 1.6, 4.5              # 3.2 m dia x 4.5 m ball mill
BELT_W = 0.8


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    log = []

    conc = pb.mat("M_Concrete", (0.55, 0.54, 0.52), 0.0, 0.85)
    earth = pb.mat("M_Fill_Gravel", (0.42, 0.37, 0.3), 0.0, 0.95)
    steel = pb.mat("M_Steel_Structural", (0.25, 0.32, 0.4), 0.6, 0.5)
    grey = pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3)
    green = pb.mat("M_Equipment_Green", (0.15, 0.35, 0.2), 0.3, 0.45)
    yellow = pb.mat("M_Safety_Yellow", (0.9, 0.7, 0.05), 0.1, 0.5)
    wear = pb.mat("M_Steel_WearPlate", (0.22, 0.2, 0.19), 0.8, 0.55)
    rubber = pb.mat("M_Belt_Rubber", (0.04, 0.04, 0.04), 0.0, 0.8)
    pipe = pb.mat("M_Pipe_Slurry_Grey", (0.35, 0.36, 0.36), 0.3, 0.5)
    froth = pb.mat("M_Froth", (0.35, 0.33, 0.28), 0.2, 0.3)
    pulp = pb.mat("M_Pulp", (0.12, 0.12, 0.13), 0.0, 0.2)
    clad = pb.mat("M_Cladding_Grey", (0.55, 0.58, 0.6), 0.5, 0.45)
    roof = pb.mat("M_Roof_Sheeting", (0.4, 0.42, 0.45), 0.6, 0.4)
    motor = pb.mat("M_Motor_Blue", (0.1, 0.2, 0.45), 0.4, 0.4)
    belt_mats = dict(steel=steel, rubber=rubber, grey=grey, yellow=yellow)

    # =====================================================================
    # CONC_LoaderRamp: fill ramp with retaining walls, tipping platform, wheel stop
    # =====================================================================
    lr = pb.Part("CONC_LoaderRamp", pivot=(RAMP_X[0], LINE_Y, 0))
    y0, y1 = LINE_Y - 5, LINE_Y + 5
    x_top = RAMP_X[1]
    lr.poly_prism([(RAMP_X[0], 0.0), (x_top, PLAT_Z), (x_top - 8.0, PLAT_Z), (x_top - 8.0, -0.3),
                   (RAMP_X[0], -0.3)], y0, y1, earth, plane='XZ')
    for ya, yb in ((y0 - 0.5, y0), (y1, y1 + 0.5)):
        lr.poly_prism([(RAMP_X[0], -0.3), (RAMP_X[0], 1.0), (x_top, PLAT_Z + 1.0),
                       (x_top - 8.0, PLAT_Z + 1.0), (x_top - 8.0, -0.3)], ya, yb, conc, plane='XZ')
    # retaining wall at the hopper face and wheel stop bund
    lr.box_mm((x_top - 8.6, y0 - 0.5, -0.3), (x_top - 8.0, y1 + 0.5, PLAT_Z), conc)
    lr.box_mm((x_top - 8.0, y0, PLAT_Z), (x_top - 7.2, y1, PLAT_Z + 0.9), conc)
    lr.finish(col)
    log.append(("Loader ramp foot (from the cooling yard exit ramp at (-55, 187, 0))",
                f"({RAMP_X[0]}, {LINE_Y}, 0.0), 10 % up to z {PLAT_Z} at x {x_top}"))

    # =====================================================================
    # CONC_ROMHopper: steel hopper, static grizzly, support steel
    # =====================================================================
    hx = HOP_X
    hp = pb.Part("CONC_ROMHopper", pivot=(hx, LINE_Y, PLAT_Z))
    top, bot, z_out = 3.0, 0.6, 3.8
    # four sloping sides as thin prisms (top 6 x 6 m to 1.2 x 1.2 m outlet)
    for s in (-1, 1):
        hp.quad_strip([[(hx - top, LINE_Y + s * top, PLAT_Z), (hx + top, LINE_Y + s * top, PLAT_Z)],
                       [(hx - bot, LINE_Y + s * bot, z_out), (hx + bot, LINE_Y + s * bot, z_out)]], wear)
        hp.quad_strip([[(hx + s * top, LINE_Y - top, PLAT_Z), (hx + s * top, LINE_Y + top, PLAT_Z)],
                       [(hx + s * bot, LINE_Y - bot, z_out), (hx + s * bot, LINE_Y + bot, z_out)]], wear)
    # rim beam and grizzly bars at 0.40 m spacing
    for s in (-1, 1):
        hp.box((2 * top + 0.3, 0.3, 0.4), (hx, LINE_Y + s * top, PLAT_Z + 0.2), steel)
        hp.box((0.3, 2 * top + 0.3, 0.4), (hx + s * top, LINE_Y, PLAT_Z + 0.2), steel)
    for i in range(-7, 8):
        hp.box((2 * top, 0.08, 0.25), (hx, LINE_Y + i * 0.4, PLAT_Z + 0.3), grey)
    # support columns to grade on the west side
    for dy in (-top, top):
        hp.box((0.4, 0.4, PLAT_Z), (hx - top, LINE_Y + dy, PLAT_Z / 2), steel)
        hp.beam_between((hx - top, LINE_Y + dy, 0.3), (hx - bot, LINE_Y + dy * 0.3, z_out), 0.25, 0.25, steel)
    hp.finish(col)

    # =====================================================================
    # CONC_RockBreaker: pedestal + slew + boom + stick with hammer (moving parts)
    # =====================================================================
    pz = PLAT_Z + 0.9
    ped = Vector((x_top - 6.0, LINE_Y + 6.2, PLAT_Z))
    rb = pb.Part("CONC_RockBreaker_Pedestal", pivot=ped)
    rb.cyl(0.6, 1.4, ped + Vector((0, 0, 0.7)), conc, seg=16)
    rb.cyl(0.45, 0.6, ped + Vector((0, 0, 1.7)), yellow, seg=16)
    rb.finish(col)
    slew_c = ped + Vector((0, 0, 2.0))
    sl = pb.Part("CONC_RockBreaker_Slew", pivot=slew_c)
    sl.cyl(0.55, 0.3, slew_c + Vector((0, 0, 0.15)), yellow, seg=16)
    sl.box((1.0, 0.8, 0.8), slew_c + Vector((0, 0, 0.7)), yellow)
    sl.finish(col)
    boom_c = slew_c + Vector((0, 0, 0.9))
    hop_pt = Vector((hx, LINE_Y, PLAT_Z + 1.0))
    yaw = math.atan2(hop_pt.y - boom_c.y, hop_pt.x - boom_c.x)
    dirv = Vector((math.cos(yaw), math.sin(yaw), 0))
    boom_tip = boom_c + dirv * 4.2 + Vector((0, 0, 1.8))
    bm_ = pb.Part("CONC_RockBreaker_Boom", pivot=boom_c)
    bm_.beam_between(boom_c, boom_tip, 0.35, 0.5, yellow)
    bm_.cyl_between(boom_c + Vector((0, 0, -0.4)), boom_c + dirv * 2.2 + Vector((0, 0, 0.6)), 0.09, grey, seg=10)
    bm_.finish(col)
    stick_tip = boom_tip + dirv * 2.0 + Vector((0, 0, -3.2))
    st = pb.Part("CONC_RockBreaker_Stick", pivot=boom_tip)
    st.beam_between(boom_tip, stick_tip, 0.3, 0.4, yellow)
    st.cyl_between(stick_tip, stick_tip + Vector((0, 0, -1.0)), 0.2, grey, seg=12)    # hammer body
    st.cyl_between(stick_tip + Vector((0, 0, -1.0)), stick_tip + Vector((0, 0, -1.5)), 0.07, grey, seg=8)
    st.finish(col)

    # =====================================================================
    # CONC_GrizzlyFeeder: frame (static) + deck (vibrates)
    # =====================================================================
    gf0 = Vector((hx + 0.6, LINE_Y, 3.55))
    gf1 = Vector((JAW_X + 1.05, LINE_Y, 3.25))
    gfs = pb.Part("CONC_GrizzlyFeeder_Frame", pivot=gf0)
    for s in (-1, 1):
        gfs.box_mm((gf1.x - 0.2, LINE_Y + s * 0.75 - 0.1, 2.6), (gf0.x, LINE_Y + s * 0.75 + 0.1, 2.9), steel)
        for x in (gf0.x - 0.3, gf1.x + 0.3):
            gfs.box((0.25, 0.25, 2.6), (x, LINE_Y + s * 0.75, 1.3), steel)
    gfs.finish(col)
    gd = pb.Part("CONC_GrizzlyFeeder_Deck", pivot=(gf0 + gf1) / 2)
    gd.beam_between(gf0 + Vector((0, 0, -0.3)), gf1 + Vector((0, 0, -0.3)), 1.1, 0.12, wear)
    for s in (-1, 1):
        gd.beam_between(gf0 + Vector((0, s * 0.6, 0)), gf1 + Vector((0, s * 0.6, 0)), 0.08, 0.7, green)
    for i in range(-3, 4):
        gd.beam_between(gf0 + Vector((-2.0, i * 0.15, -0.1)), gf1 + Vector((0, i * 0.15, -0.1)), 0.05, 0.12, grey)
    gd.box((0.6, 1.4, 0.4), (gf0 + gf1) / 2 + Vector((0.6, 0, -0.55)), motor)        # vibrator
    gd.finish(col)

    # =====================================================================
    # Jaw crusher (~900 x 600 mm class): frame, pitman (swing jaw), flywheels, motor
    # =====================================================================
    jx, jy, jz = JAW_X, LINE_Y, JAW_BASE_Z
    shaft = Vector((jx + 0.95, jy, jz + 2.15))
    jw = pb.Part("CONC_JawCrusher_Frame", pivot=(jx, jy, jz))
    jw.box_mm((jx - 2.2, jy - 1.6, -0.3), (jx + 2.2, jy + 1.6, jz), conc)              # plinth
    for s in (-1, 1):
        jw.poly_prism([(jx - 1.4, jz), (jx + 1.4, jz), (jx + 1.4, jz + 2.4), (jx - 1.1, jz + 2.4),
                       (jx - 1.4, jz + 1.4)], jy + s * 0.55, jy + s * 0.75, green, plane='XZ')
        jw.cyl(0.32, 0.3, (shaft.x, jy + s * 0.85, shaft.z), grey, rot=(90, 0, 0))     # bearing housings
    # fixed jaw (west side) sloping liner
    jw.poly_prism([(jx - 1.0, jz + 0.3), (jx - 0.75, jz + 0.3), (jx - 0.55, jz + 2.4), (jx - 1.05, jz + 2.4)],
                  jy - 0.55, jy + 0.55, wear, plane='XZ')
    # discharge chute to CV01 below the plinth
    jw.box_mm((jx - 0.9, jy - 0.5, -1.0), (jx + 0.2, jy + 0.5, -0.3), wear)
    jw.box_mm((jx + 1.6, jy - 2.6, -0.3), (jx + 3.0, jy - 1.7, 0.6), motor)           # drive motor
    jw.finish(col)
    pt = pb.Part("CONC_JawCrusher_Pitman", pivot=shaft)
    pt.poly_prism([(shaft.x - 0.45, shaft.z + 0.25), (shaft.x + 0.35, shaft.z + 0.25),
                   (shaft.x + 0.1, jz + 0.35), (jx - 0.5, jz + 0.35)], jy - 0.5, jy + 0.5, green, plane='XZ')
    pt.poly_prism([(shaft.x - 0.5, shaft.z + 0.2), (shaft.x - 0.4, shaft.z + 0.2),
                   (jx - 0.42, jz + 0.35), (jx - 0.55, jz + 0.35)], jy - 0.52, jy + 0.52, wear, plane='XZ')
    pt.box((0.25, 1.0, 0.25), (shaft.x + 0.35, jy, jz + 0.6), grey)                   # toggle seat
    pt.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        c = Vector((shaft.x, jy + s * 1.15, shaft.z))
        fw = pb.Part(f"CONC_JawCrusher_Flywheel_{side}", pivot=c)
        fw.cyl(0.8, 0.22, c, grey, rot=(90, 0, 0), seg=32)
        fw.cyl(0.65, 0.24, c, green, rot=(90, 0, 0), seg=32)
        for k in range(6):                                                           # spokes read as spin
            a = math.radians(60 * k)
            fw.box((0.12, 0.26, 1.2), c + Vector((math.cos(a), 0, math.sin(a))) * 0.3, grey,
                   rot=(0, -60 * k + 90, 0))
        fw.finish(col)
    # crusher pit for CV01 tail
    cp = pb.Part("CONC_CrusherPit", pivot=(jx, jy, -2.2))
    cp.box_mm((jx - 3.0, jy - 2.4, -2.6), (jx + 2.5, jy + 3.5, -2.2), conc)
    for xa, xb, ya, yb in ((jx - 3.4, jx + 2.9, jy - 2.8, jy - 2.4), (jx - 3.4, jx - 3.0, jy - 2.4, jy + 3.5),
                           (jx + 2.5, jx + 2.9, jy - 2.4, jy + 3.5)):
        cp.box_mm((xa, ya, -2.6), (xb, yb, -0.3), conc)
    cp.finish(col)

    # =====================================================================
    # Conveyors (0.8 m belts, 1 UV = 1.2 m like the conveyor kit)
    # =====================================================================
    tx, ty = TOWER
    cv = {}
    cv["CV01"] = pb.conveyor("CONC_CV01", (jx, jy - 1.4, -1.25), (tx, ty - 3.2, 11.6), BELT_W, col,
                             belt_mats, ground_z=0.0)
    cv["CV02"] = pb.conveyor("CONC_CV02", (tx, ty + 0.5, 1.4), (FOB[0], FOB[1] - 2.0, 15.2), BELT_W, col,
                             belt_mats, ground_z=0.0)
    cv["CV03"] = pb.conveyor("CONC_CV03", (FOB[0] - 1.0, FOB[1], 1.3), (MILL_FEED_X + 1.8, FOB[1], 6.4),
                             BELT_W, col, belt_mats, ground_z=0.0)

    # =====================================================================
    # Screen / cone tower: structure, screen deck (vibrates), cone crusher
    # =====================================================================
    tw = pb.Part("CONC_ScreenTower", pivot=(tx, ty, 0))
    for dx in (-3.5, 3.5):
        for dy in (-4.0, 4.0):
            tw.box((0.35, 0.35, 13.0), (tx + dx, ty + dy, 6.5), steel)
    for z in (4.5, 9.5):
        tw.box_mm((tx - 3.7, ty - 4.2, z - 0.15), (tx + 3.7, ty + 4.2, z), pb.mat("M_Grating", (0.25, 0.25, 0.26), 0.8, 0.5))
        pb.handrail(tw, (tx - 3.6, ty - 4.1, z), (tx + 3.6, ty - 4.1, z), yellow)
        pb.handrail(tw, (tx - 3.6, ty + 4.1, z), (tx + 3.6, ty + 4.1, z), yellow)
    tw.box_mm((tx - 3.7, ty - 4.2, 13.0), (tx + 3.7, ty + 4.2, 13.3), roof)
    # chutes: screen undersize and cone product down onto CV02
    tw.box_mm((tx - 0.6, ty - 1.0, 2.0), (tx + 0.6, ty + 0.2, 9.4), wear)
    tw.box_mm((tx - 0.5, ty + 0.6, 1.9), (tx + 0.5, ty + 1.6, 3.0), wear)
    pb.ladder(tw, (tx + 3.75, ty, 0.0), 9.5, yellow, facing=0)
    tw.finish(col)
    log.append(("Cone crusher / screen tower centre", f"({tx}, {ty}, 0.0)"))
    sc_c = Vector((tx, ty, 10.6))
    sd = pb.Part("CONC_Screen_Deck", pivot=sc_c)
    a = math.radians(20)
    p0 = sc_c + Vector((0, -1.8 * math.cos(a), 1.8 * math.sin(a)))
    p1 = sc_c + Vector((0, 1.8 * math.cos(a), -1.8 * math.sin(a)))
    for s in (-1, 1):
        sd.beam_between(p0 + Vector((s * 0.8, 0, 0)), p1 + Vector((s * 0.8, 0, 0)), 0.1, 0.9, green)
    for dz in (0.0, -0.35):
        sd.beam_between(p0 + Vector((0, 0, dz)), p1 + Vector((0, 0, dz)), 1.5, 0.04, grey)
    sd.cyl(0.25, 1.9, sc_c + Vector((0, 0, -0.55)), motor, rot=(0, 90, 0), seg=12)    # exciter
    sd.finish(col)
    cone_c = Vector((tx, ty + 1.2, 4.5))
    cc = pb.Part("CONC_ConeCrusher_Body", pivot=cone_c)
    cc.cyl(1.0, 1.1, cone_c + Vector((0, 0, 0.55)), green, seg=32)
    cc.cyl(1.05, 0.25, cone_c + Vector((0, 0, 1.2)), grey, seg=32)                    # adjustment ring
    cc.cyl(0.95, 0.6, cone_c + Vector((0, 0, 1.6)), green, seg=32, r2=0.6)            # bowl / hopper
    cc.box((1.4, 0.4, 0.4), cone_c + Vector((1.5, 0, 0.5)), green)                     # countershaft box
    cc.box((1.2, 0.8, 0.8), cone_c + Vector((3.0, 0, 0.4)), motor)
    cc.box_mm((tx - 0.4, ty + 1.8, 9.0), (tx + 0.4, ty + 2.6, 9.4), wear)            # oversize chute from screen
    cc.beam_between((tx, ty + 2.2, 9.0), cone_c + Vector((0, 0, 2.0)), 0.6, 0.6, wear)
    cc.finish(col)
    hd = pb.Part("CONC_ConeCrusher_Head", pivot=cone_c + Vector((0, 0, 1.9)))
    hd.cyl(0.25, 0.9, cone_c + Vector((0, 0, 1.45)), wear, seg=24, r2=0.55)
    hd.cyl(0.06, 0.2, cone_c + Vector((0, 0, 1.95)), grey, seg=8)
    hd.finish(col)
    pl_c = cone_c + Vector((2.3, 0, 0.5))
    pl = pb.Part("CONC_ConeCrusher_Pulley", pivot=pl_c)
    pl.cyl(0.45, 0.25, pl_c, grey, rot=(0, 90, 0), seg=24)
    pl.finish(col)

    # =====================================================================
    # CONC_FineOreBin: 7 m dia steel bin on legs, outlet gate onto CV03
    # =====================================================================
    fx, fy = FOB
    fb = pb.Part("CONC_FineOreBin", pivot=(fx, fy, 0))
    fb.cyl(3.5, 8.0, (fx, fy, 9.0), clad, seg=40)
    fb.cyl(3.5, 2.8, (fx, fy, 3.6), clad, seg=40, r2=0.4)
    fb.cyl(0.4, 0.3, (fx, fy, 2.05), wear, seg=40, r2=3.5)
    fb.cyl(3.6, 0.6, (fx, fy, 13.3), roof, seg=40, r2=0.8)
    for k in range(6):
        a = math.radians(60 * k + 30)
        p = Vector((fx + 3.3 * math.cos(a), fy + 3.3 * math.sin(a), 0))
        fb.box((0.4, 0.4, 6.0), p + Vector((0, 0, 3.0)), steel)
    fb.box((0.8, 0.8, 0.4), (fx, fy, 1.95), grey)                                    # slide gate
    pb.ladder(fb, (fx + 3.6, fy, 0.0), 13.2, yellow, facing=0)
    fb.finish(col)
    log.append(("Fine ore bin (≈260 m³, ≈450 t at 1.7 t/m³ bulk)", f"centre ({fx}, {fy}), roof z 13.6"))

    # =====================================================================
    # Mill and flotation building (frame, roof and walls separate for cutaways)
    # =====================================================================
    bx0, by0, bx1, by1 = BLDG
    fr = pb.Part("CONC_Building_Frame", pivot=(bx0, by0, 0))
    fr.box_mm((bx0, by0, -0.3), (bx1, by1, 0.0), conc)                               # floor slab
    xs = [bx0 + 7.5 * i for i in range(int((bx1 - bx0) / 7.5) + 1)]
    for x in xs:
        for y in (by0, by1):
            fr.box((0.5, 0.6, EAVE_Z), (x, y, EAVE_Z / 2), steel)
        fr.beam_between((x, by0, EAVE_Z), (x, (by0 + by1) / 2, EAVE_Z + 2.5), 0.3, 0.7, steel)
        fr.beam_between((x, by1, EAVE_Z), (x, (by0 + by1) / 2, EAVE_Z + 2.5), 0.3, 0.7, steel)
    for y in (by0 + 1.0, by1 - 1.0):                                                  # crane rails
        fr.box_mm((bx0, y - 0.25, 10.6), (bx1, y + 0.25, 11.0), steel)
        for x in xs:
            fr.box_mm((x - 0.2, min(y, (by0 if y < 284 else by1)), 10.4),
                      (x + 0.2, max(y, (by0 if y < 284 else by1)), 10.6), steel)
    fr.finish(col)
    rf = pb.Part("CONC_Building_Roof", pivot=(bx0, by0, EAVE_Z))
    mid = (by0 + by1) / 2
    rf.quad_strip([[(bx0 - 0.5, by0 - 0.5, EAVE_Z + 0.4), (bx1 + 0.5, by0 - 0.5, EAVE_Z + 0.4)],
                   [(bx0 - 0.5, mid, EAVE_Z + 2.9), (bx1 + 0.5, mid, EAVE_Z + 2.9)],
                   [(bx0 - 0.5, by1 + 0.5, EAVE_Z + 0.4), (bx1 + 0.5, by1 + 0.5, EAVE_Z + 0.4)]], roof)
    rf.quad_strip([[(bx1 + 0.5, by0 - 0.5, EAVE_Z + 0.4), (bx0 - 0.5, by0 - 0.5, EAVE_Z + 0.4)],
                   [(bx1 + 0.5, mid, EAVE_Z + 2.9), (bx0 - 0.5, mid, EAVE_Z + 2.9)],
                   [(bx1 + 0.5, by1 + 0.5, EAVE_Z + 0.4), (bx0 - 0.5, by1 + 0.5, EAVE_Z + 0.4)]], roof)
    rf.finish(col)
    t = 0.15
    w = pb.Part("CONC_Building_Wall_S", pivot=(bx0, by0, 0))
    w.box_mm((bx0, by0 - 0.4 - t, 0.0), (bx0 + 25.0, by0 - 0.4, EAVE_Z), clad)
    w.box_mm((bx0 + 31.0, by0 - 0.4 - t, 0.0), (bx1, by0 - 0.4, EAVE_Z), clad)
    w.box_mm((bx0 + 25.0, by0 - 0.4 - t, 7.0), (bx0 + 31.0, by0 - 0.4, EAVE_Z), clad)  # over roller door
    w.box_mm((bx0 + 25.0, by0 - 0.35 - t, 0.0), (bx0 + 31.0, by0 - 0.35, 7.0), grey)   # roller door
    w.finish(col)
    w = pb.Part("CONC_Building_Wall_N", pivot=(bx0, by1, 0))
    w.box_mm((bx0, by1 + 0.4, 0.0), (bx1, by1 + 0.4 + t, EAVE_Z), clad)
    w.finish(col)
    w = pb.Part("CONC_Building_Wall_E", pivot=(bx1, by0, 0))
    hole = (FOB[1] - 1.5, FOB[1] + 1.5, 3.5, 8.5)                                     # CV03 entry
    w.box_mm((bx1 + 0.3, by0, 0.0), (bx1 + 0.3 + t, hole[0], EAVE_Z), clad)
    w.box_mm((bx1 + 0.3, hole[1], 0.0), (bx1 + 0.3 + t, by1, EAVE_Z), clad)
    w.box_mm((bx1 + 0.3, hole[0], 0.0), (bx1 + 0.3 + t, hole[1], hole[2]), clad)
    w.box_mm((bx1 + 0.3, hole[0], hole[3]), (bx1 + 0.3 + t, hole[1], EAVE_Z), clad)
    w.finish(col)
    w = pb.Part("CONC_Building_Wall_W", pivot=(bx0, by0, 0))
    w.box_mm((bx0 - 0.3 - t, by0, 0.0), (bx0 - 0.3, by1, EAVE_Z), clad)
    w.finish(col)

    # =====================================================================
    # Ball mill: shell (rotates about X), pinion, static bearings / motor / feed
    # =====================================================================
    mz, my = MILL_Z, MILL_Y
    x_feed = MILL_FEED_X - 1.2                     # feed-end head
    x_dis = x_feed - MILL_L                        # discharge-end head
    axis_c = Vector(((x_feed + x_dis) / 2, my, mz))
    ms = pb.Part("CONC_BallMill_Shell", pivot=axis_c)
    ms.cyl(MILL_R, MILL_L, axis_c, green, rot=(0, 90, 0), seg=40)
    ms.cyl(MILL_R, 0.7, (x_feed + 0.35, my, mz), green, rot=(0, 90, 0), seg=40, r2=0.65)
    ms.cyl(0.65, 0.7, (x_dis - 0.35, my, mz), green, rot=(0, 90, 0), seg=40, r2=MILL_R)
    ms.cyl(0.55, 0.8, (x_feed + 1.1, my, mz), grey, rot=(0, 90, 0), seg=24)           # feed trunnion
    ms.cyl(0.55, 0.8, (x_dis - 1.1, my, mz), grey, rot=(0, 90, 0), seg=24)            # discharge trunnion
    ms.cyl(0.75, 1.4, (x_dis - 2.2, my, mz), wear, rot=(0, 90, 0), seg=24)            # trommel
    ms.cyl(1.95, 0.35, (x_dis + 0.9, my, mz), grey, rot=(0, 90, 0), seg=48)           # girth gear
    for k in range(8):                                                               # liner bolt rows
        a = math.radians(45 * k)
        ms.box((MILL_L - 0.2, 0.08, 0.04), axis_c + Vector((0, math.cos(a), math.sin(a))) * (MILL_R + 0.01),
               grey, rot=(45 * k, 0, 0))
    for k in range(2):                                                               # manholes
        ms.box((0.6, 0.6, 0.1), axis_c + Vector((0.8 - 1.6 * k, 0, MILL_R + 0.03)), grey)
    ms.finish(col)
    mb = pb.Part("CONC_BallMill_Base", pivot=axis_c)
    for x in (x_feed + 1.1, x_dis - 1.1):
        mb.box((1.4, 2.6, mz - 0.6), (x, my, (mz - 0.6) / 2), conc)
        mb.box((1.2, 1.6, 0.55), (x, my, mz - 0.35), grey)                             # bearing housing
    mb.box((1.2, 4.8, 2.4), (x_dis + 0.9, my, mz), steel)                             # gear guard (static)
    pin_c = Vector((x_dis + 0.9, my - 2.35, mz - 0.4))
    mb.box((1.0, 1.0, mz - 0.9), (pin_c.x, pin_c.y, (mz - 0.9) / 2), conc)
    mb.box((1.2, 1.2, 1.3), (pin_c.x + 0.0, my - 4.6, 0.65), conc)
    mb.cyl(0.65, 1.8, (pin_c.x, my - 4.6, 2.0), motor, rot=(90, 0, 0), seg=24)         # drive motor (axis Y)
    mb.box((2.6, 1.6, 1.6), (x_feed + 3.1, my, 4.6), wear)                            # feed chute / hopper
    mb.box((1.0, 1.0, 1.4), (x_feed + 1.9, my, mz + 0.4), wear)                        # feed spout
    mb.box((2.4, 3.0, 2.5), (x_dis - 2.4, my, 1.0), wear)                              # trommel hood
    mb.box((3.0, 3.0, 2.0), (x_dis - 4.2, my, 1.0), conc)                              # discharge sump
    for dy in (-1.0, 1.0):                                                            # cyclone feed pumps
        mb.box((1.0, 0.7, 0.8), (x_dis - 4.2, my + dy, 2.4), green)
        mb.cyl(0.25, 0.8, (x_dis - 3.4, my + dy, 2.4), motor, rot=(0, 90, 0), seg=12)
    mb.finish(col)
    log.append(("Ball mill axis (3.2 m × 4.5 m, shell rotates about X)", f"({axis_c.x:.2f}, {my}, {mz})"))
    pn = pb.Part("CONC_BallMill_Pinion", pivot=Vector((x_dis + 0.9, my - 1.9, mz - 0.4)))
    pn.cyl(0.3, 0.4, (x_dis + 0.9, my - 1.9, mz - 0.4), grey, rot=(0, 90, 0), seg=20)
    pn.cyl_between((x_dis + 0.9, my - 1.9, mz - 0.4), (x_dis + 0.9, my - 3.5, mz - 0.4), 0.12, grey, seg=12)
    pn.finish(col)

    # cyclone cluster on a platform over the mill feed end
    cyc_c = Vector((x_feed + 1.0, my, 9.5))
    cy = pb.Part("CONC_CycloneCluster", pivot=cyc_c)
    cy.box_mm((cyc_c.x - 2.5, my - 2.5, 7.8), (cyc_c.x + 2.5, my + 2.5, 8.0), pb.mat("M_Grating", (0.25, 0.25, 0.26), 0.8, 0.5))
    for dx in (-2.4, 2.4):
        for dy in (-2.4, 2.4):
            cy.box((0.25, 0.25, 7.8), (cyc_c.x + dx, my + dy, 3.9), steel)
    cy.cyl(0.35, 1.2, cyc_c, steel, seg=16)                                           # distributor
    for k in range(4):
        a = math.radians(90 * k + 45)
        p = cyc_c + Vector((math.cos(a), math.sin(a), 0)) * 1.1
        cy.cyl(0.13, 0.7, p + Vector((0, 0, 0.35)), pipe, seg=12)
        cy.cyl(0.13, 1.2, p + Vector((0, 0, -0.6)), pipe, seg=12, r2=0.04)
        cy.cyl_between(cyc_c + Vector((0, 0, 0.3)), p + Vector((0, 0, 0.5)), 0.06, pipe, seg=8)
    cy.cyl_between((x_dis - 3.4, my - 1.0, 2.4), (x_dis - 3.4, my - 1.0, 9.5), 0.1, pipe, seg=10)
    cy.cyl_between((x_dis - 3.4, my - 1.0, 9.5), cyc_c, 0.1, pipe, seg=10)
    cy.cyl_between(cyc_c + Vector((0, 0, -1.3)), (x_feed + 2.6, my, 5.3), 0.12, pipe, seg=10)  # underflow to feed
    pb.handrail(cy, (cyc_c.x - 2.5, my - 2.5, 8.0), (cyc_c.x + 2.5, my - 2.5, 8.0), yellow)
    pb.ladder(cy, (cyc_c.x + 2.6, my - 2.0, 0.0), 8.0, yellow, facing=0)
    cy.finish(col)

    # =====================================================================
    # Flotation: 4 x 10 m3 rougher/scavenger + 3 x 3 m3 cleaner tank cells
    # Each cell: tank (static, all cells joined), impeller+shaft (spins about Z)
    # =====================================================================
    tanks = pb.Part("CONC_Flot_Tanks", pivot=(-172.0, 276.0, 0))
    frothp = pb.Part("CONC_Flot_Froth", pivot=(-172.0, 276.0, 0))
    cells = [(f"R{i + 1}", -172.0 - 4.5 * i, 276.0, 1.25, 2.4, 1.2 - 0.3 * i) for i in range(4)]
    cells += [(f"C{i + 1}", -190.0 - 3.6 * i, 284.0, 0.85, 1.6, 1.6 - 0.3 * i) for i in range(3)]
    for tag, x, y, r, h, zb in cells:
        tanks.cyl(r + 0.3, zb, (x, y, zb / 2), conc, seg=24)                         # plinth
        tanks.cyl(r, h, (x, y, zb + h / 2), green, seg=32)
        tanks.cyl(r + 0.32, 0.35, (x, y, zb + h - 0.05), green, seg=32, r2=r + 0.32)  # froth launder
        tanks.cyl(0.1, 0.8, (x + r + 0.2, y, zb + h - 0.6), pipe, seg=8)              # launder outlet
        tanks.box((2 * r + 0.8, 0.35, 0.3), (x, y, zb + h + 0.35), steel)              # mechanism bridge
        tanks.cyl(0.32, 0.7, (x, y, zb + h + 0.85), motor, seg=16)                     # drive motor
        frothp.cyl(r - 0.02, 0.02, (x, y, zb + h - 0.08), froth, seg=32)
        sh_top = Vector((x, y, zb + h + 0.5))
        imp = pb.Part(f"CONC_Flot_{tag}_Impeller", pivot=sh_top)
        imp.cyl_between(sh_top, (x, y, zb + 0.45), 0.07, grey, seg=10)
        imp.cyl(r * 0.28, 0.35, (x, y, zb + 0.45), wear, seg=12)
        for k in range(6):
            a = math.radians(60 * k)
            imp.box((r * 0.3, 0.05, 0.35), (x + math.cos(a) * r * 0.18, y + math.sin(a) * r * 0.18, zb + 0.45),
                    wear, rot=(0, 0, 60 * k))
        imp.finish(col)
    # walkways along the rougher bank and connecting boxes between cells
    for i in range(3):
        _, xa, ya, ra, ha, za = cells[i]
        _, xb_, yb_, rb, hb, zb2 = cells[i + 1]
        tanks.box((4.5 - ra - rb + 0.2, 0.8, 0.9), ((xa + xb_) / 2, ya, zb2 + hb * 0.5), green)
    tanks.box_mm((-188.0, 277.8, 3.4), (-170.0, 279.0, 3.5), pb.mat("M_Grating", (0.25, 0.25, 0.26), 0.8, 0.5))
    pb.handrail(tanks, (-188.0, 279.0, 3.5), (-170.0, 279.0, 3.5), yellow)
    for x in (-187.5, -170.5):
        tanks.box((0.2, 0.2, 3.4), (x, 278.9, 1.7), steel)
    tanks.cyl_between((x_feed + 1.0, my - 1.4, 8.8), (-172.0, 276.0, 3.6 + 1.2), 0.12, pipe, seg=10)  # cyclone O/F
    tanks.finish(col)
    frothp.finish(col)

    # =====================================================================
    # Concentrate thickener outside the west wall: tank + rake (spins about Z)
    # =====================================================================
    th_c = Vector((bx0 - 9.0, 286.0, 0.0))
    th = pb.Part("CONC_Thickener_Tank", pivot=th_c)
    th.cyl(3.2, 3.0, th_c + Vector((0, 0, 1.9)), clad, seg=48)
    th.cyl(3.0, 0.02, th_c + Vector((0, 0, 3.2)), pulp, seg=48)
    th.cyl(3.0, 0.5, th_c + Vector((0, 0, 0.35)), clad, seg=48, r2=0.3)
    th.box((6.8, 0.8, 0.5), th_c + Vector((0, 0, 3.7)), steel)                         # access bridge
    th.cyl(0.4, 0.8, th_c + Vector((0, 0, 4.3)), motor, seg=16)                         # rake drive
    for k in range(6):
        a = math.radians(60 * k)
        th.box((0.3, 0.3, 0.4), th_c + Vector((math.cos(a) * 3.1, math.sin(a) * 3.1, 0.2)), conc)
    th.cyl_between((-197.0, 284.0, 2.0), (bx0 + 0.2, 284.0, 4.0), 0.08, pipe, seg=8)
    th.cyl_between((bx0 + 0.2, 284.0, 4.0), th_c + Vector((0, -2.0, 4.0)), 0.08, pipe, seg=8)
    pb.flange(th, th_c + Vector((-3.5, 0, 0.4)), (0, 90, 0), 0.08, grey, log,
              "Concentrate underflow flange (to filter / smelter return)")
    th.finish(col)
    rk = pb.Part("CONC_Thickener_Rake", pivot=th_c + Vector((0, 0, 4.0)))
    rk.cyl_between(th_c + Vector((0, 0, 4.0)), th_c + Vector((0, 0, 0.6)), 0.1, grey, seg=10)
    for s in (-1, 1):
        rk.beam_between(th_c + Vector((0, 0, 0.7)), th_c + Vector((s * 2.9, 0, 1.0)), 0.12, 0.2, grey)
    rk.finish(col)
    tl = pb.Part("CONC_TailingsStub", pivot=(bx0 - 0.5, 274.0, 1.0))
    tl.cyl_between((-185.5, 276.0, 0.6), (bx0 - 0.5, 274.0, 1.0), 0.15, pipe, seg=12)
    pb.flange(tl, (bx0 - 0.6, 274.0, 1.0), (0, 90, 0), 0.15, grey, log, "Tailings flange (to tailings thickener / dam)")
    tl.finish(col)

    # =====================================================================
    # Overhead crane in the building (bridge moves X, trolley moves Y, hook Z)
    # =====================================================================
    br_c = Vector((MILL_FEED_X - 4.0, (by0 + by1) / 2, 11.2))
    cb = pb.Part("CONC_Crane_Bridge", pivot=br_c)
    for dx in (-0.8, 0.8):
        cb.box((0.5, by1 - by0 - 1.0, 1.0), br_c + Vector((dx, 0, 0.3)), yellow)
    for s in (-1, 1):
        cb.box((2.4, 0.6, 0.6), br_c + Vector((0, s * ((by1 - by0) / 2 - 1.0), 0)), yellow)
    cb.finish(col)
    tr_c = br_c + Vector((0, 2.0, 1.0))
    ct = pb.Part("CONC_Crane_Trolley", pivot=tr_c)
    ct.box((2.4, 2.0, 0.8), tr_c + Vector((0, 0, 0.4)), yellow)
    ct.cyl(0.35, 1.6, tr_c + Vector((0, 0, 0.4)), grey, rot=(0, 90, 0), seg=16)
    ct.finish(col)
    hk_c = tr_c + Vector((0, 0, -3.0))
    ch = pb.Part("CONC_Crane_Hook", pivot=hk_c)
    ch.box((0.6, 0.4, 0.6), hk_c, yellow)
    ch.cyl_between(hk_c + Vector((0, 0, -0.3)), hk_c + Vector((0, 0, -0.8)), 0.08, grey, seg=8)
    ch.finish(col)

    # =====================================================================
    # REF: human, ground, slag lumps on the grizzly
    # =====================================================================
    pb.ref_human(ref, (x_top - 3.0, LINE_Y + 3.5, PLAT_Z))
    pb.ref_human(ref, (-176.0, 279.0, 3.5))
    pb.ref_ground(ref, (-240, 150, -50, 320),
                  [(JAW_X - 3.4, LINE_Y - 2.8, JAW_X + 2.9, LINE_Y + 3.5)], z=-0.02)    # crusher pit open
    return col, log, cv


def write_readme(col, log, cv):
    rows = pb.pivot_table([col.name])
    conn = "\n".join(f"| {a} | {b} |" for a, b in log)
    belts = "\n".join(f"| CONC_{k}_Belt | {v['loop_length']:.2f} m | {v['loop_length'] / 1.2:.3f} |" for k, v in cv.items())
    txt = f"""# SM_SlagCrushingFlotation

Slag concentrator: ROM hopper with rock breaker, jaw crusher, scalping screen and cone crusher,
fine ore bin, ball mill with cyclones, flotation cells and a concentrate thickener, in one folder
because the parts are small enough to share one asset. Built in Blender 5.2.2 LTS (headless,
cloud) with `Tools/Blender/build_slag_crushing_flotation.py`.

## Placement

Shares the flash furnace origin: place at (0, 0, 0), no rotation. Blender +X is taken as east,
+Y as north. It sits west and north of the cooling yard (x -240 to -55, y 180 to 300), away from
the acid plant east of x = 69.6. A loader carries broken slag from the yard's breaking pit
up the yard exit ramp (top at (-55, 187, 0)) straight onto this asset's loader ramp.

## Flowsheet (simplified)

ROM hopper (6 × 6 m, static grizzly at 400 mm, pedestal rock breaker) → vibrating grizzly feeder →
jaw crusher (~900 × 600 mm class) → CV01 → scalping screen (1.5 × 3.6 m, 20°) → oversize to the
cone crusher → screen undersize + cone product on CV02 → fine ore bin (Ø7 m) → CV03 → ball mill
(Ø3.2 × 4.5 m) in closed circuit with 4 cyclones → rougher/scavenger bank 4 × 10 m³ → cleaner bank
3 × 3 m³ → concentrate thickener (Ø6.4 m). Tailings leave through a stub flange.

Sizing basis (own estimate): ≈ 500 t/d of slag from the cooling yard; crushing ≈ 45 t/h on one or
two shifts, milling ≈ 22 t/h continuous, grind ~80 % passing 45 µm (Aurubis Pirdop runs its slag
flotation feed at P80 38 µm), flotation feed ≈ 50 m³/h pulp at ~35 % solids, ~30 min
rougher-scavenger residence. Slow-cooled slag is crushed and ground before flotation in the
sourced practice (US4046323: broken to ~300 mm, crushed to ~6 mm, then milled and floated).

## Moving parts

| Part | Motion |
|---|---|
| CONC_RockBreaker_Slew | Rotate about local Z |
| CONC_RockBreaker_Boom | Rotate about local Y at the boom foot (after slew yaw) |
| CONC_RockBreaker_Stick | Rotate about local Y at the boom tip; hammer is part of the stick |
| CONC_GrizzlyFeeder_Deck | Vibrate (small X/Z oscillation, ~15 Hz) |
| CONC_JawCrusher_Pitman | Swing about Y at the eccentric shaft, ±2° at ~4-5 Hz |
| CONC_JawCrusher_Flywheel_L/R | Spin about Y (~250-300 rpm) |
| CONC_Screen_Deck | Vibrate along its slope |
| CONC_ConeCrusher_Head | Gyrate: small tilt (1-2°) whose direction rotates about Z |
| CONC_ConeCrusher_Pulley | Spin about X |
| CONC_BallMill_Shell | Spin about X, ~16-17 rpm (≈75 % of critical speed for Ø3.2 m) |
| CONC_BallMill_Pinion | Spin about X, opposite direction, ~8× shell speed |
| CONC_Flot_R1..R4_Impeller, CONC_Flot_C1..C3_Impeller | Spin about Z (shaft + impeller) |
| CONC_Thickener_Rake | Spin about Z, very slow (~0.1-0.3 rpm) |
| CONC_Crane_Bridge / Trolley / Hook | Translate X / Y / Z |
| CONC_CV0x_HeadPulley, _TailPulley | Spin about the pulley axis |
| CONC_Flot_Froth | Static froth surfaces, for a panning froth material |

### Belts

0.8 m belts with continuous UVs at the conveyor kit's texel density (1 UV = 1.2 m in both
directions, so V spans 0 to 0.667 across the belt). Panner speed in U = belt speed / 1.2, same
material as the kit. Carry runs are troughed at 30°, flattening near the pulleys.

| Belt | Loop length | U at loop end |
|---|---|---|
{belts}

### Pivot coordinates

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

## Connection points

| Point | Location |
|---|---|
{conn}

## Unreal import

Combine Meshes off. For the moving parts, import with Transform Vertex to Absolute off and place
each part at the pivot listed above (with it on, every pivot moves to the asset origin). The
building roof and walls are separate objects so they can be hidden for cutaways.

## Dimensions

Everything here is an estimate of a typical machine class, not a specific vendor model. I found
no published general-arrangement drawings of a slag concentrator.

| Item | Value | Status |
|---|---|---|
| Jaw crusher, 900 × 600 mm class, ~2.8 × 2.6 × 2.4 m with flywheels Ø1.6 m | | Estimated (40 × 30 in class machines weigh ~21-23 t with feeder, dealer listings) |
| Cone crusher Ø2.0 m body, ~2.2 m tall | | Estimated |
| Screen 1.5 × 3.6 m double deck, 20° | | Estimated |
| Fine ore bin Ø7 m, 8 m straight side | ≈ 260 m³ | Estimated |
| Ball mill Ø3.2 × 4.5 m, ~700 kW | | Estimated from the sizing basis |
| Flotation cells 4 × 10 m³ (Ø2.5 m), 3 × 3 m³ (Ø1.7 m), 0.3 m steps | | Estimated |
| Concentrate thickener Ø6.4 m | | Estimated |
| Building 45 × 32 m, 14 m eaves, overhead crane | | Own design |
| ROM tipping platform 6.5 m, ramp 10 % | | Own design |

Sources: US4046323A (https://patents.google.com/patent/US4046323A/en); Pavez et al. 2021 Atacama
slag flotation case study (https://repositorioacademico.uda.cl/entities/publication/e63bb582-2389-49c5-be25-c5672acb5dca);
Sarcheshmeh converter slag flotation, ~200 t/d (https://onemine.org/documents/flotation-copper-recovery-from-converter-slag-of-the-sarcheshmeh-khatoonabad-smelter);
Metso Nordberg C Series (https://metso.com/portfolio/nordberg-c-series).

## Files

- SM_SlagCrushingFlotation.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Crushing.png, Preview_MillFlotation.png (roof and south wall hidden)
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, log, cv = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, log, cv)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render()
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (-30, 120, 90), (-150, 250, 0), lens=30)
    pb.render_view(os.path.join(OUT, "Preview_Crushing.png"), (-118, 172, 16), (-138, 200, 3), lens=26)
    for n in ("CONC_Building_Roof", "CONC_Building_Wall_S"):
        bpy.data.objects[n].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_MillFlotation.png"), (-168, 248, 26), (-182, 284, 2), lens=24)
    for n in ("CONC_Building_Roof", "CONC_Building_Wall_S"):
        bpy.data.objects[n].hide_render = False


main()
