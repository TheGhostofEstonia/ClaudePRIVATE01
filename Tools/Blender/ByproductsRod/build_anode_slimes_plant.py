"""
build_anode_slimes_plant.py - SM_AnodeSlimesPlant (anode slimes treatment and precious metals refinery).

Run:  blender -b --factory-startup --python Tools/Blender/ByproductsRod/build_anode_slimes_plant.py

Own local origin (0, 0, 0) at grade, +X = direction of flow. North bay (y > 0): slimes receiving
tank -> decopperizing autoclave (acid pressure leach) -> flash tank -> filter press -> rotary dryer
-> Kaldo (top blown rotary converter) furnace with off-gas hood -> selenium scrubbers; doré anode
casting. South bay (y < 0): Moebius silver cells, Wohlwill gold cells, induction furnace, bar
casting and the vault.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402
import byp_helpers as bh  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Meshes", "AnodeSlimesPlant")
NAME = "SM_AnodeSlimesPlant"
P = "ASP_"

# ---------------------------------------------------------------------------
# Layout (local metres). All sizes estimated / own design unless the README says otherwise.
# ---------------------------------------------------------------------------
NY = 6.0                               # centre line of the north (process) bay
RECV = (3.5, NY)                       # slimes receiving tank
AC_X, AC_Z, AC_R = (7.0, 15.0), 2.8, 1.1   # autoclave ends, axis height, radius
FLASH = (17.5, NY)
FP_X0, FP_Z = 20.0, 1.6                # filter press fixed head x, plate centre height
N_PLATES, PLATE = 24, 1.2
DRYER = (29.0, 34.0, NY, 1.6)          # rotary dryer x0, x1, y, axis z
KALDO_C = Vector((39.0, NY, 3.6))      # trunnion centre
KALDO_TILT = 25.0                      # mouth up, degrees above horizontal (working position)
SCRUB = ((46.0, 11.0), (49.0, 11.0))   # selenium scrubber towers
DORE = (44.0, 1.5)                     # doré anode casting table
SY = -6.0                              # centre line of the south (refinery) bay
VAULT = (44.0, -12.0, 50.0, -7.0)      # vault x0, y0, x1, y1
BLDG = (0.0, -13.0, 52.0, 14.0)
EAVE = 14.0


def build_hydro(col, M, log):
    """Receiving tank, autoclave with 4 agitated compartments, flash tank, filter press, dryer."""
    rt = pb.Part(P + "ReceivingTank", pivot=(RECV[0], RECV[1], 0))
    rt.cyl(1.8, 0.3, (RECV[0], RECV[1], 0.15), M['conc'], seg=32)
    bh.vtank(rt, RECV, 0.3, 1.5, 3.2, M['frp'], top='flat')
    rt.box((3.4, 0.25, 0.25), (RECV[0], RECV[1], 3.65), M['steel'])
    bh.drive(rt, (RECV[0], RECV[1], 3.78), M, r=0.22, length=0.6)
    bh.pipe_run(rt, [(RECV[0] - 1.5, RECV[1], 3.2), (0.3, RECV[1], 3.2)], 0.06, M['frp'])
    bh.flange_x(rt, (0.3, RECV[1], 3.2), 0.06, M['frp'], log, "Anode slimes slurry in (from the tankhouse)")
    rt.box((0.8, 0.5, 0.6), (RECV[0] + 2.1, RECV[1] - 1.2, 0.6), M['motor'])        # autoclave feed pump
    bh.pipe_run(rt, [(RECV[0] + 2.5, RECV[1] - 1.2, 0.6), (AC_X[0] + 0.5, RECV[1] - 1.2, 0.6),
                     (AC_X[0] + 0.5, RECV[1] - 1.2, AC_Z + AC_R + 0.4), (AC_X[0] + 0.5, NY, AC_Z + AC_R + 0.4)],
                0.05, M['stainless'])
    rt.finish(col)
    bh.agitator(P + "ReceivingTank_Agitator", RECV, 3.78, 0.8, 1.0, col, M)

    ac = pb.Part(P + "Autoclave", pivot=(AC_X[0], NY, AC_Z))
    ac.box_mm((AC_X[0] - 0.8, NY - 1.8, 0), (AC_X[1] + 0.8, NY + 1.8, 0.3), M['conc'])
    bh.htank(ac, (AC_X[0], NY, AC_Z), (AC_X[1], NY, AC_Z), AC_R, M['grey'], saddles=2,
             saddle_m=M['steel'], ground_z=0.3)
    comp = [AC_X[0] + (AC_X[1] - AC_X[0]) * (i + 0.5) / 4 for i in range(4)]
    for x in comp:
        ac.cyl(0.3, 0.3, (x, NY, AC_Z + AC_R + 0.1), M['grey'], seg=16)              # agitator nozzle
        bh.drive(ac, (x, NY, AC_Z + AC_R + 0.25), M, r=0.22, length=0.7)
    for x in (AC_X[0] + 0.4, AC_X[1] - 0.4):
        ac.cyl(0.25, 0.4, (x, NY + 0.5, AC_Z + AC_R), M['grey'], seg=12)             # manways / PSV
    # oxygen and steam injection lines along the bottom
    bh.pipe_run(ac, [(AC_X[0], NY - AC_R - 0.3, 0.8), (AC_X[1], NY - AC_R - 0.3, 0.8)], 0.05, M['yellow'])
    for x in comp:
        bh.pipe_run(ac, [(x, NY - AC_R - 0.3, 0.8), (x, NY - AC_R * 0.6, AC_Z - AC_R * 0.8)], 0.03, M['yellow'])
    bh.pipe_run(ac, [(AC_X[0], NY - AC_R - 0.3, 0.8), (AC_X[0] - 1.5, NY - AC_R - 0.3, 0.8),
                     (AC_X[0] - 1.5, NY - AC_R - 0.3, 6.0)], 0.05, M['yellow'])
    bh.flange_z(ac, (AC_X[0] - 1.5, NY - AC_R - 0.3, 6.0), 0.05, M['yellow'], log, "Oxygen supply")
    bh.pipe_run(ac, [(AC_X[1] - 0.4, NY - AC_R - 0.5, 0.5), (AC_X[1] - 0.4, NY - 3.5, 0.5),
                     (AC_X[1] - 0.4, NY - 3.5, 6.0)], 0.06, M['insul'])
    bh.flange_z(ac, (AC_X[1] - 0.4, NY - 3.5, 6.0), 0.06, M['insul'], log, "Steam supply (autoclave heating)")
    # top platform with stair
    bh.platform(ac, AC_X[0] - 0.3, NY - 1.8, AC_X[1] + 0.3, NY + 1.8, AC_Z + AC_R + 0.15, M, rails='NSEW',
                hole=(AC_X[0], NY - AC_R, AC_X[1], NY + AC_R))
    bh.stair(ac, (AC_X[1] + 0.3 + 3.5, NY + 2.4, 0.0), (AC_X[1] + 0.35, NY + 2.4, AC_Z + AC_R + 0.15), M)
    ac.finish(col)
    for i, x in enumerate(comp):
        bh.agitator(f"{P}Autoclave_Agitator_{i + 1}", (x, NY), AC_Z + AC_R + 0.25, AC_Z - AC_R * 0.6, 0.7, col, M)

    ft = pb.Part(P + "FlashTank", pivot=(FLASH[0], FLASH[1], 0))
    bh.vtank(ft, FLASH, 2.0, 0.8, 2.0, M['grey'], bottom='cone', top='dish', legs=3, leg_m=M['steel'])
    bh.pipe_run(ft, [(AC_X[1] + 0.25, NY, AC_Z - 0.6), (FLASH[0] - 0.8, NY, AC_Z - 0.6)], 0.06, M['grey'])
    bh.pipe_run(ft, [(FLASH[0], FLASH[1], 4.3), (FLASH[0], FLASH[1], EAVE + 2.0)], 0.15, M['grey'])
    bh.flange_z(ft, (FLASH[0], FLASH[1], EAVE + 2.0), 0.15, M['grey'], log, "Flash vent (above roof, to scrubber)")
    bh.pipe_run(ft, [(FLASH[0], FLASH[1], 0.95), (FLASH[0], FLASH[1], 0.6), (FP_X0 - 0.4, FLASH[1], 0.6),
                     (FP_X0 - 0.4, FLASH[1], FP_Z)], 0.06, M['stainless'])
    ft.finish(col)

    # filter press: fixed head, side bars, separate plates and moving head (all translate along X)
    pitch = 0.075
    x_end = FP_X0 + 0.4 + N_PLATES * pitch
    fp = pb.Part(P + "FilterPress_Frame", pivot=(FP_X0, NY, 0))
    fp.box_mm((FP_X0 - 0.3, NY - 1.0, 0), (FP_X0 + 0.3, NY + 1.0, FP_Z + 0.9), M['green'])     # fixed head
    tail = FP_X0 + 6.0
    fp.box_mm((tail - 0.3, NY - 0.9, 0), (tail + 0.6, NY + 0.9, FP_Z + 0.8), M['green'])         # cylinder end
    for s in (-1, 1):
        fp.beam_between((FP_X0, NY + s * 0.75, FP_Z + 0.55), (tail, NY + s * 0.75, FP_Z + 0.55), 0.12, 0.2, M['steel'])
    fp.cyl_between((tail - 0.3, NY, FP_Z), (tail - 1.4, NY, FP_Z), 0.18, M['grey'], seg=16)       # hydraulic ram
    fp.box_mm((FP_X0 - 0.2, NY - 1.4, 0), (tail + 0.4, NY + 1.4, 0.15), M['conc'])
    fp.box_mm((FP_X0 + 0.3, NY - 0.7, 0.15), (tail - 0.3, NY + 0.7, 0.6), M['stainless'])       # cake trough
    fp.finish(col)
    for i in range(N_PLATES):
        x = FP_X0 + 0.35 + i * pitch
        pl = pb.Part(f"{P}FilterPress_Plate{i + 1:02d}", pivot=(x, NY, FP_Z))
        pl.box((0.065, PLATE, PLATE), (x, NY, FP_Z), M['grey'] if i % 2 else M['frp'])
        for s in (-1, 1):
            pl.box((0.08, 0.18, 0.12), (x, NY + s * 0.7, FP_Z + 0.55), M['grey'])             # handles on bars
        pl.finish(col)
    mh = pb.Part(P + "FilterPress_MovingHead", pivot=(x_end + 0.1, NY, FP_Z))
    mh.box((0.25, 1.4, 1.4), (x_end + 0.1, NY, FP_Z), M['green'])
    mh.cyl_between((x_end + 0.22, NY, FP_Z), (tail - 1.4, NY, FP_Z), 0.09, M['grey'], seg=12)  # ram rod
    mh.finish(col)
    fl = pb.Part(P + "FilterPress_FiltrateLine", pivot=(FP_X0 + 0.5, NY + 1.0, 0))
    yn = BLDG[3] - 0.2
    bh.pipe_run(fl, [(FP_X0 + 0.5, NY + 1.0, 0.4), (FP_X0 + 0.5, yn, 0.4)], 0.05, M['frp'])
    bh.flange_y(fl, (FP_X0 + 0.5, yn, 0.4), 0.05, M['frp'], log, "Filtrate (copper-bearing) out, back to the tankhouse")
    fl.finish(col)

    # cake conveyor to the rotary dryer
    x0, x1, dy, dz = DRYER
    cv = pb.Part(P + "CakeConveyor", pivot=(tail - 1.0, NY, 0))
    cv.beam_between((FP_X0 + 1.0, NY + 1.0, 0.3), (x0 - 0.4, NY + 1.0, dz + 0.6), 0.5, 0.12, M['grey'])
    cv.box((0.6, 0.6, 0.5), (x0 - 0.5, NY + 0.5, dz + 0.6), M['stainless'])
    cv.finish(col)
    dr = pb.Part(P + "RotaryDryer_Base", pivot=(x0, dy, 0))
    dr.box_mm((x0 - 0.8, dy - 1.2, 0), (x1 + 1.5, dy + 1.2, 0.25), M['conc'])
    for x in (x0 + 0.8, x1 - 0.8):
        for s in (-0.45, 0.45):
            dr.cyl_between((x - 0.15, dy + s, dz - 0.75), (x + 0.15, dy + s, dz - 0.75), 0.18, M['grey'], seg=12)
            dr.box((0.3, 0.3, dz - 0.95), (x, dy + s, 0.25 + (dz - 0.95) / 2), M['steel'])
    dr.box((0.9, 0.9, 1.4), (x0 - 0.4, dy, dz), M['stainless'])                      # feed breeching
    dr.box((1.0, 1.0, 2.0), (x1 + 0.6, dy, dz + 0.2), M['stainless'])                # discharge hood
    dr.box((0.6, 0.5, 0.5), (x0 + 2.5, dy - 1.0, 0.5), M['motor'])                    # drive
    bh.pipe_run(dr, [(x1 + 0.6, dy, dz + 1.2), (x1 + 0.6, dy, EAVE + 2.0)], 0.2, M['grey'])
    dr.finish(col)
    rd = pb.Part(P + "RotaryDryer_Drum", pivot=(x0, dy, dz))
    rd.cyl_between((x0, dy, dz), (x1, dy, dz), 0.6, M['grey'], seg=24)
    for x in (x0 + 0.8, x1 - 0.8):
        rd.cyl_between((x - 0.12, dy, dz), (x + 0.12, dy, dz), 0.68, M['steel'], seg=24)
    rd.finish(col)


def rot_y(v, deg, c):
    """Rotate point v about the Y axis through c by deg (positive tilts +X toward +Z)."""
    a = math.radians(deg)
    d = Vector(v) - c
    return c + Vector((d.x * math.cos(a) - d.z * math.sin(a), d.y, d.x * math.sin(a) + d.z * math.cos(a)))


def build_kaldo(col, M, log):
    """Kaldo / TBRC furnace: base with trunnion stands, tilting cradle, rotating vessel, hood, lance."""
    c = KALDO_C
    t = KALDO_TILT
    ax = rot_y(c + Vector((1, 0, 0)), t, c) - c          # vessel axis unit vector (toward the mouth)
    R = 1.25

    base = pb.Part(P + "Kaldo_Base", pivot=(c.x, c.y, 0))
    base.box_mm((c.x - 3.0, c.y - 3.2, 0), (c.x + 3.5, c.y + 3.2, 0.3), M['conc'])
    for s in (-1, 1):
        y = c.y + s * 2.3
        base.box_mm((c.x - 0.5, y - 0.4, 0.3), (c.x + 0.5, y + 0.4, c.z - 0.3), M['steel'])
        base.box((0.9, 0.9, 0.5), (c.x, y, c.z), M['grey'])                          # trunnion bearing
    base.box((1.2, 1.0, 1.0), (c.x, c.y + 3.0, c.z), M['motor'])                       # tilt drive
    base.finish(col)

    cr = pb.Part(P + "Kaldo_Cradle", pivot=c)
    for s in (-1, 1):
        cr.cyl_between(c + Vector((0, s * 1.6, 0)), c + Vector((0, s * 2.2, 0)), 0.25, M['grey'], seg=16)
        # side frame members of the cradle, parallel to the vessel axis
        cr.beam_between(c + Vector((0, s * 1.6, 0)) - ax * 1.4, c + Vector((0, s * 1.6, 0)) + ax * 1.0,
                        0.3, 0.5, M['steel'])
    for off in (-1.1, 0.7):
        q = c + ax * off
        for s in (-1, 1):
            cr.cyl_between(q + Vector((0, s * (R + 0.15), 0)), q + Vector((0, s * 1.6, 0)), 0.12, M['steel'], seg=10)
            cr.cyl_between(q + Vector((0, s * (R + 0.3), -0.0)) - ax * 0.12,
                           q + Vector((0, s * (R + 0.3), 0)) + ax * 0.12, 0.17, M['grey'], seg=12)  # support rollers
    # rotation drive on the cradle bottom
    cr.box((0.9, 0.8, 0.8), c - ax * 1.9 + Vector((0, 0, -0.2)), M['motor'])
    cr.finish(col)

    ve = pb.Part(P + "Kaldo_Vessel", pivot=c)
    back = c - ax * 1.7
    body_end = c + ax * 1.1
    mouth = c + ax * 2.0
    ve.cyl_between(back, body_end, R, M['steel'], seg=40)
    ve.cyl_between(body_end, mouth, R, M['steel'], seg=40, r2=0.6)
    ve.cyl_between(mouth, mouth + ax * 0.12, 0.62, M['refr'], seg=32, r2=0.62)
    ve.cyl_between(back - ax * 0.25, back, R * 0.6, M['steel'], seg=32, r2=R)
    for off in (-1.1, 0.7):
        q = c + ax * off
        ve.cyl_between(q - ax * 0.1, q + ax * 0.1, R + 0.15, M['grey'], seg=40)       # riding rings
    ve.cyl_between(back - ax * 0.25, back - ax * 0.45, 0.6, M['grey'], seg=24)        # girth gear hub
    ve.finish(col, x_toward=mouth)

    # hood, off-gas duct to the scrubbers, lance on its carriage (all static)
    hd = pb.Part(P + "Kaldo_Hood", pivot=(mouth.x + 0.8, c.y, mouth.z + 1.0))
    hc = Vector((mouth.x + 0.9, c.y, mouth.z + 1.0))
    hd.box((2.0, 2.8, 2.6), hc + Vector((0.3, 0, 0.6)), M['steel'])
    hd.cyl(0.6, 1.8, hc + Vector((0.3, 0, 2.8)), M['steel'], seg=24)
    duct_top = 11.0
    sx0 = SCRUB[0]
    bh.pipe_run(hd, [hc + Vector((0.3, 0, 3.6)), (hc.x + 0.3, c.y, duct_top), (sx0[0] - 1.6, c.y, duct_top),
                     (sx0[0] - 1.6, sx0[1], duct_top), (sx0[0] - 1.6, sx0[1], 3.0), (sx0[0] - 1.0, sx0[1], 3.0)],
                0.5, M['steel'])
    # lance: water-cooled pipe from a carriage above the hood into the mouth
    lt = hc + Vector((1.6, 0, 4.4))
    hd.cyl_between(lt, mouth + ax * 0.3 + Vector((0, 0, 0.3)), 0.08, M['grey'], seg=10)
    hd.box((0.8, 0.6, 0.6), lt, M['yellow'])
    hd.beam_between(lt + Vector((0, 0.4, 0.3)), hc + Vector((2.6, 0.4, 6.0)), 0.15, 0.15, M['steel'])
    hd.beam_between(hc + Vector((2.6, 0.4, 0)), hc + Vector((2.6, 0.4, 6.0)), 0.25, 0.25, M['steel'])
    hd.beam_between(hc + Vector((2.6, 0.4, -hc.z)), hc + Vector((2.6, 0.4, 0)), 0.25, 0.25, M['steel'])
    hd.finish(col)

    # ladle car under the mouth (rails along Y toward the doré casting table)
    lr = pb.Part(P + "LadleCar_Rails", pivot=(mouth.x + 1.6, c.y, 0))
    for dx in (-0.6, 0.6):
        lr.box_mm((mouth.x + 1.6 + dx - 0.04, DORE[1] - 0.8, 0), (mouth.x + 1.6 + dx + 0.04, c.y + 1.0, 0.12), M['grey'])
    lr.finish(col)
    lc = Vector((mouth.x + 1.6, c.y, 0.12))
    ld = pb.Part(P + "LadleCar", pivot=lc)
    ld.box((1.6, 1.6, 0.3), lc + Vector((0, 0, 0.25)), M['yellow'])
    ld.cyl(0.55, 0.8, lc + Vector((0, 0, 0.8)), M['steel'], seg=24, r2=0.65)
    ld.cyl(0.5, 0.05, lc + Vector((0, 0, 1.18)), M['refr'], seg=24)
    ld.finish(col)

    # selenium scrubbing: two packed towers, circulation tanks, fan and stack
    sc = pb.Part(P + "SeleniumScrubbers", pivot=(sx0[0], sx0[1], 0))
    for i, (x, y) in enumerate(SCRUB):
        sc.cyl(1.1, 0.3, (x, y, 0.15), M['conc'], seg=24)
        bh.vtank(sc, (x, y), 0.3, 0.9, 8.0, M['frp'], top='dish')
        bh.vtank(sc, (x, y - 2.3), 0.0, 0.7, 1.6, M['frp'], top='flat')                  # liquor tank
        sc.box((0.6, 0.4, 0.5), (x + 0.9, y - 2.3, 0.4), M['motor'])
        bh.pipe_run(sc, [(x + 0.9, y - 2.1, 0.6), (x + 0.9, y - 0.2, 0.6), (x + 0.9, y - 0.2, 7.6),
                         (x + 0.3, y, 7.6)], 0.05, M['frp'])
    bh.pipe_run(sc, [(SCRUB[0][0], SCRUB[0][1], 8.6), (SCRUB[0][0], SCRUB[0][1], 9.4),
                     (SCRUB[1][0], SCRUB[1][1], 9.4), (SCRUB[1][0], SCRUB[1][1], 8.6)], 0.4, M['frp'])
    bh.pipe_run(sc, [(SCRUB[1][0] + 0.9, SCRUB[1][1], 1.0), (SCRUB[1][0] + 1.8, SCRUB[1][1], 1.0)], 0.4, M['frp'])
    sc.box((1.2, 1.2, 1.4), (SCRUB[1][0] + 2.4, SCRUB[1][1], 0.9), M['motor'])
    sc.cyl(0.4, EAVE + 4.0, (SCRUB[1][0] + 2.4, SCRUB[1][1] + 1.4, (EAVE + 4.0) / 2), M['frp'], seg=20)
    sc.cyl_between((SCRUB[1][0] + 2.4, SCRUB[1][1] + 0.6, 1.0), (SCRUB[1][0] + 2.4, SCRUB[1][1] + 1.1, 1.0),
                   0.35, M['frp'])
    sc.finish(col)
    log.append(("Scrubber stack top", (SCRUB[1][0] + 2.4, SCRUB[1][1] + 1.4, EAVE + 4.0)))
    log.append(("Selenium sludge drain (liquor tank 2)", (SCRUB[1][0], SCRUB[1][1] - 3.0, 0.3)))

    # doré anode casting table: turntable with 8 moulds, rotates about Z
    dx, dy = DORE
    dt = pb.Part(P + "DoreCasting_Table", pivot=(dx, dy, 0.9))
    dt.cyl(1.6, 0.15, (dx, dy, 0.9), M['steel'], seg=40)
    for k in range(8):
        a = 2 * math.pi * k / 8
        q = (dx + 1.2 * math.cos(a), dy + 1.2 * math.sin(a), 1.02)
        dt.box((0.5, 0.35, 0.1), q, M['grey'], rot=(0, 0, math.degrees(a)))
    dt.finish(col)
    dtb = pb.Part(P + "DoreCasting_Base", pivot=(dx, dy, 0))
    dtb.cyl(0.4, 0.82, (dx, dy, 0.41), M['grey'], seg=20)
    dtb.box((0.6, 0.6, 0.6), (dx + 0.9, dy - 1.4, 0.3), M['motor'])
    dtb.finish(col)


def build_refinery(col, M, log):
    """Moebius silver cells, Wohlwill gold cells, induction furnace, bar casting, vault."""
    cells = pb.Part(P + "MoebiusCells", pivot=(6.0, SY, 0))
    cells.box_mm((5.0, SY - 2.6, 0), (27.0, SY + 2.6, 0.15), M['conc'])
    # two rows of 8 cells, 1.2 x 0.9 x 0.8 m, each with 5 anode baskets and 6 cathode plates
    for row, yc in enumerate((SY - 1.2, SY + 1.2)):
        for i in range(8):
            x = 6.5 + i * 2.4
            cells.box_mm((x - 0.15, yc - 0.6, 0.15), (x + 1.35, yc + 0.6, 0.8), M['steel'])        # stand
            cells.box_mm((x, yc - 0.45, 0.8), (x + 1.2, yc + 0.45, 1.6), M['frp'])                 # tank
            cells.box_mm((x + 0.03, yc - 0.42, 1.4), (x + 1.17, yc + 0.42, 1.45), M['liquid'])
            for k in range(11):
                px = x + 0.1 + k * 0.1
                if k % 2:
                    cells.box((0.03, 0.75, 0.15), (px, yc, 1.48), M['clad'])                         # anode bag top
                else:
                    cells.box((0.01, 0.8, 0.7), (px, yc, 1.35), M['stainless'])                     # cathode plate
            cells.box((1.3, 0.06, 0.06), (x + 0.6, yc - 0.5, 1.65), M['copper'])                     # busbars
            cells.box((1.3, 0.06, 0.06), (x + 0.6, yc + 0.5, 1.65), M['copper'])
    cells.box((1.6, 1.2, 2.0), (26.0, SY, 1.15), M['grey'])                                            # cell rectifier
    bh.vtank(cells, (5.8, SY + 3.6), 0.0, 0.8, 1.8, M['frp'], top='flat')                              # electrolyte tank
    bh.pipe_run(cells, [(5.8, SY + 2.8, 1.7), (5.8, SY + 2.0, 1.7), (27.0, SY + 2.0, 1.7)], 0.04, M['frp'])
    cells.finish(col)

    ww = pb.Part(P + "WohlwillCells", pivot=(29.0, SY, 0))
    for i in range(3):
        x = 29.0 + i * 1.2
        ww.box_mm((x - 0.1, SY - 0.5, 0), (x + 0.9, SY + 0.5, 0.8), M['steel'])
        ww.box_mm((x, SY - 0.35, 0.8), (x + 0.8, SY + 0.35, 1.3), M['frp'])                           # porcelain-type cell
        for k in range(5):
            ww.box((0.01, 0.55, 0.45), (x + 0.15 + k * 0.125, SY, 1.15), M['copper'] if k % 2 else M['grey'])
    ww.box((1.0, 0.8, 1.6), (29.4, SY + 1.6, 0.8), M['grey'])                                          # rectifier
    ww.finish(col)

    # induction furnace (tilts about Y on its trunnions) and bar casting line
    ic = Vector((36.0, SY, 1.4))
    ib = pb.Part(P + "InductionFurnace_Frame", pivot=(ic.x, ic.y, 0))
    ib.box_mm((ic.x - 1.0, ic.y - 1.2, 0), (ic.x + 1.0, ic.y + 1.2, 0.2), M['conc'])
    for s in (-1, 1):
        ib.box_mm((ic.x - 0.25, ic.y + s * 0.95 - 0.15, 0.2), (ic.x + 0.25, ic.y + s * 0.95 + 0.15, ic.z), M['green'])
    ib.box((1.2, 0.9, 1.6), (ic.x - 1.8, ic.y, 0.8), M['grey'])                                        # power supply
    ib.finish(col)
    inf = pb.Part(P + "InductionFurnace", pivot=ic)
    inf.cyl(0.55, 1.1, ic + Vector((0, 0, 0.1)), M['green'], seg=24)
    inf.cyl(0.35, 0.05, ic + Vector((0, 0, 0.66)), M['refr'], seg=24)
    inf.box((0.3, 0.2, 0.15), ic + Vector((0.6, 0, 0.55)), M['refr'])                                  # spout
    for s in (-1, 1):
        inf.cyl_between(ic + Vector((0, s * 0.55, 0)), ic + Vector((0, s * 0.85, 0)), 0.1, M['grey'], seg=12)
    inf.finish(col)
    bc = pb.Part(P + "BarCasting", pivot=(38.5, SY, 0))
    bc.box_mm((37.5, SY - 0.6, 0), (42.0, SY + 0.6, 0.8), M['steel'])
    for k in range(8):
        bc.box((0.36, 0.16, 0.08), (38.0 + k * 0.5, SY, 0.84), M['grey'])                                 # bar moulds
    bc.finish(col)

    # vault: reinforced concrete room with a swing door, shelves with silver and gold bars
    x0, y0, x1, y1 = VAULT
    vt = pb.Part(P + "Vault", pivot=(x0, y0, 0))
    t, h = 0.4, 3.2
    vt.box_mm((x0, y0, 0), (x1, y0 + t, h), M['conc'])
    vt.box_mm((x0, y0 + t, 0), (x0 + t, y1 - t, h), M['conc'])          # side walls between front and back
    vt.box_mm((x1 - t, y0 + t, 0), (x1, y1 - t, h), M['conc'])
    vt.box_mm((x0, y0, h), (x1, y1, h + t), M['conc'])
    door_x0, door_x1 = x0 + 2.0, x0 + 3.4
    vt.box_mm((x0, y1 - t, 0), (door_x0, y1, h), M['conc'])
    vt.box_mm((door_x1, y1 - t, 0), (x1, y1, h), M['conc'])
    vt.box_mm((door_x0, y1 - t, 2.2), (door_x1, y1, h), M['conc'])
    vt.box_mm((door_x0 - 0.1, y1, 0), (door_x1 + 0.1, y1 + 0.1, 2.3), M['grey'])                         # door frame
    for k in range(3):
        sy0 = y0 + t + 0.1
        vt.box_mm((x0 + t + 0.2 + k * 1.7, sy0, 0), (x0 + t + 0.3 + k * 1.7, sy0 + 0.6, 2.0), M['steel'])
        for z in (0.5, 1.1, 1.7):
            vt.box_mm((x0 + t + 0.2 + k * 1.7, sy0, z), (x0 + t + 1.7 + k * 1.7, sy0 + 0.6, z + 0.03), M['steel'])
    vt.finish(col)
    dr = pb.Part(P + "Vault_Door", pivot=(door_x0, y1 + 0.05, 0))
    dr.box_mm((door_x0, y1 + 0.1, 0.02), (door_x1, y1 + 0.35, 2.2), M['grey'])
    dr.cyl_between((door_x0 + 0.7, y1 + 0.35, 1.1), (door_x0 + 0.7, y1 + 0.45, 1.1), 0.25, M['stainless'], seg=24)
    for z in (0.4, 1.1, 1.8):
        dr.cyl_between((door_x0 - 0.02, y1 + 0.2, z - 0.15), (door_x0 - 0.02, y1 + 0.2, z + 0.15), 0.06, M['grey'], seg=8)
    dr.finish(col)
    gold = pb.mat("M_Gold", (1.0, 0.76, 0.3), 1.0, 0.2)
    silver = pb.mat("M_Silver", (0.9, 0.9, 0.92), 1.0, 0.2)
    bars = pb.Part(P + "Vault_Bars", pivot=(x0 + 1.0, y0 + 0.8, 0.53))
    for k in range(3):
        for zi, z in enumerate((0.53, 1.13, 1.73)):
            m = gold if (k == 0 and zi == 2) else silver
            n = 6 if m is silver else 10
            w, d, hh = (0.3, 0.13, 0.1) if m is silver else (0.25, 0.07, 0.04)   # ~30 kg Ag / ~12.5 kg Au
            for j in range(n):
                bars.box((w, d, hh), (x0 + t + 0.45 + (j % 5) * 0.27 + k * 1.7,
                                      y0 + t + 0.25 + (j // 5) * 0.25, z + hh / 2), m)
    bars.finish(col)
    log.append(("Vault door (security perimeter boundary)", (door_x0 + 0.7, y1 + 0.3, 0.0)))


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    M = bh.std_mats()
    log = []
    build_hydro(col, M, log)
    build_kaldo(col, M, log)
    build_refinery(col, M, log)
    bh.portal_building(P + "Building", *BLDG, EAVE, col, M, walls='NSEW', crane_rail=11.5)
    pb.ref_human(ref, (KALDO_C.x - 2.0, KALDO_C.y - 3.0, 0.3))
    pb.ref_human(ref, (12.0, SY, 0.15))
    pb.ref_human(ref, (VAULT[0] + 3.0, VAULT[3] + 1.2, 0.0))
    pb.ref_ground(ref, (-10, -25, 62, 25), [], z=-0.02)
    return col, log


def write_readme(col, log):
    rows = pb.pivot_table([col.name])
    conn = "\n".join(f"| {a} | {b} |" for a, b in log)
    txt = f"""# SM_AnodeSlimesPlant

Anode slimes plant and precious metals refinery: decopperizing autoclave, filter press, dryer,
Kaldo furnace with selenium scrubbing, doré anode casting, Moebius silver cells, Wohlwill gold
cells, induction furnace, bar casting and a vault, in one building. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/ByproductsRod/build_anode_slimes_plant.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Building
{BLDG[2] - BLDG[0]:.0f} × {BLDG[3] - BLDG[1]:.0f} m (x {BLDG[0]:.0f} to {BLDG[2]:.0f}, y {BLDG[1]:.0f} to {BLDG[3]:.0f}),
{EAVE:.0f} m eaves, crane runway at 11.5 m. North bay (y > 0) is the process bay, south bay
(y < 0) the precious metals refinery with the vault in its south-east corner. The slimes
come from the tankhouse as slurry through the inlet flange below.

## Flowsheet (simplified)

Slimes slurry → agitated receiving tank → acid pressure leach in a 4-compartment autoclave with
oxygen (decopperizing; copper and part of the tellurium go into solution) → flash tank → filter
press (filtrate back to the tankhouse) → rotary dryer → Kaldo / top blown rotary converter:
smelting and converting to doré, selenium leaves as SeO2 in the off-gas and is caught in the wet
scrubbers → doré poured to the ladle car and cast into doré anodes on the turntable → Moebius
cells (silver crystals on stainless cathodes) → silver crystals melted in the induction furnace
and cast into bars. Gold-bearing anode slime from the silver cells goes to the Wohlwill cells;
the gold cathodes are melted and cast the same way. Bars go to the vault.

## Moving parts

| Part | Motion |
|---|---|
| ASP_ReceivingTank_Agitator, ASP_Autoclave_Agitator_1..4 | Spin about Z |
| ASP_FilterPress_Plate01..24 | Translate along +X one at a time to open the press and drop the cake |
| ASP_FilterPress_MovingHead | Translate along +X (≈ 1.5 m stroke) |
| ASP_RotaryDryer_Drum | Spin about X (a few rpm) |
| ASP_Kaldo_Cradle | Rotate about Y on the trunnions: working position as built (mouth {KALDO_TILT:.0f}° up); about −{KALDO_TILT + 35:.0f}° to pour, +{90 - KALDO_TILT:.0f}° to stand upright for charging. Parent ASP_Kaldo_Vessel to it |
| ASP_Kaldo_Vessel | Spin about its local X (the vessel axis, origin on the trunnion centre); Kaldo vessels rotate at up to a few tens of rpm (estimate) |
| ASP_LadleCar | Translate along −Y from under the mouth to the doré casting table |
| ASP_DoreCasting_Table | Rotate about Z in 45° steps (8 moulds) |
| ASP_InductionFurnace | Rotate about Y on its trunnions to pour (spout on +X) |
| ASP_Vault_Door | Rotate about Z at the hinge (pivot), opens outward to +Y |

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
each part at the pivot listed above. Attach ASP_Kaldo_Vessel to ASP_Kaldo_Cradle so it tilts with
it. The building roof and walls are separate objects (ASP_Building_Roof, _Wall_N/S/E/W). The
vault walls, roof and door are solid, so the vault works as a closed room for gameplay.

## Dimensions

No general-arrangement drawing of an anode slimes plant was found. The process route is sourced;
every size and the layout are mine.

| Item | Value | Status |
|---|---|---|
| Route: pressure leach decopperization → TBRC (Kaldo) smelting to doré, selenium off as SeO2 | | Sourced (US4581064 TBRC patent; Metso slimes scope via the research notes) |
| Acid pressure leach conditions 80-120 °C, 2-8 bar O2 | | Sourced (2017 Physicochemical Problems of Mineral Processing paper) |
| Moebius cells for silver, Wohlwill cells for gold | | Sourced from a secondary review (Indonesian Mining Journal 2013); standard practice, not verified against a plant |
| Throughput basis | ≈ 500-1,000 t/a slimes | Estimated; Aurubis Hamburg's central plant takes ~8,000 t/a, a single-refinery plant is much smaller |
| Autoclave Ø2.2 × 8 m, 4 compartments | | Estimated |
| Filter press 1.2 m plates, 24 plates | | Estimated |
| Rotary dryer Ø1.2 × 5 m | | Estimated |
| Kaldo vessel Ø2.5 m, 3.6 m long | | Estimated (small-batch class) |
| Moebius cells 1.2 × 0.9 × 0.8 m, 16 cells | | Estimated |
| Silver bar ~30 kg (300 × 130 × 100 mm, rounded), gold bar ~12.5 kg (250 × 70 × 40 mm, rounded) | | Typical market bar masses; shapes simplified |
| Vault 6 × 5 m, 0.4 m walls | | Own design |

Sources: US4581064A TBRC slimes treatment (https://patents.google.com/patent/US4581064);
US4163046 recovery of selenium (https://patents.justia.com/patent/4163046); Physicochemical
Problems of Mineral Processing, pressure leaching of decopperized slimes (https://dlibra.kdm.wcss.pl/Content/38198/download);
Indonesian Mining Journal review (https://jurnal.tekmira.esdm.go.id/index.php/imj/article/view/382/255);
Aurubis Hamburg slimes plant (https://recyclinginternational.com/?p=6097).

## Files

- SM_AnodeSlimesPlant.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Kaldo.png, Preview_Hydro.png, Preview_Refinery.png (roof and south wall hidden)
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, log = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, log)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render()
    hide = [P + "Building_Roof", P + "Building_Wall_S"]
    for n in hide:
        bpy.data.objects[n].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (0, -50, 36), (26, 1, 0), lens=28)
    pb.render_view(os.path.join(OUT, "Preview_Kaldo.png"), (32, -1.0, 7.5), (41, 6, 3.5), lens=22)
    pb.render_view(os.path.join(OUT, "Preview_Hydro.png"), (4, -1.0, 8), (16, 7, 2), lens=22)
    pb.render_view(os.path.join(OUT, "Preview_Refinery.png"), (20, -12.0, 6), (38, -6, 1), lens=22)
    for n in hide:
        bpy.data.objects[n].hide_render = False


main()
