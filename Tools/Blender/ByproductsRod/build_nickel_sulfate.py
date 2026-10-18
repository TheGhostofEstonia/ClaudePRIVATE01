"""
build_nickel_sulfate.py - SM_NickelSulfate (nickel sulfate crystallizer / evaporator plant).

Run:  blender -b --factory-startup --python Tools/Blender/ByproductsRod/build_nickel_sulfate.py

Own local origin (0, 0, 0) at grade, +X = direction of flow. Treats the decopperized electrolyte
bleed from the liberator cells. Flow: feed tank -> forced-circulation evaporative crystallizer
(heater + vapour body, vacuum from a surface condenser) -> slurry tank -> pusher centrifuge ->
crystals by screw conveyor to a fluid bed dryer -> rotary valve -> bucket elevator -> product bin
-> 25 kg bagging. Centrifuge mother liquor (black acid) goes to its own tank.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import byp_helpers as bh  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Meshes", "NickelSulfate")
NAME = "SM_NickelSulfate"
P = "NIS_"

# ---------------------------------------------------------------------------
# Layout (local metres). All sizes estimated / own design unless the README says otherwise.
# ---------------------------------------------------------------------------
FEED = (3.0, 4.0)                      # feed tank centre
HEATER = (8.0, 0.0)                    # vertical heater (calandria) centre
VB = (11.5, 0.0)                       # vapour body centre
VB_Z0, VB_H, VB_R = 4.5, 4.0, 1.25     # vapour body straight shell bottom, height, radius
COND = (14.0, 18.5, 3.5, 10.5)         # condenser x0, x1, y, z (horizontal)
DECK_Z = 4.0                           # centrifuge floor
DECK = (15.0, -7.5, 25.0, -1.0)        # centrifuge floor x0, y0, x1, y1
SLURRY = (17.0, -4.0)                  # slurry tank on the deck
CENT = (21.5, -4.0)                    # pusher centrifuge centre (axis along X)
DRYER = (27.0, 33.0, -4.0)             # fluid bed dryer x0, x1, y
ELEV = (35.0, -4.0)                    # bucket elevator
BIN = (38.0, -4.0, 5.0)                # product bin centre and bottom of straight shell
BLDG = (0.0, -10.0, 42.0, 8.0)
EAVE = 13.0


def build_feed_and_evaporator(col, M, log):
    """Feed tank, heater, vapour body, circulation loop, pump, platforms."""
    ft = pb.Part(P + "FeedTank", pivot=(FEED[0], FEED[1], 0))
    ft.cyl(1.8, 0.3, (FEED[0], FEED[1], 0.15), M['conc'], seg=32)
    bh.vtank(ft, FEED, 0.3, 1.5, 4.0, M['frp'], top='dish')
    bh.pipe_run(ft, [(FEED[0] - 1.5, FEED[1], 3.8), (0.4, FEED[1], 3.8)], 0.08, M['frp'])
    bh.flange_x(ft, (0.4, FEED[1], 3.8), 0.08, M['frp'], log, "Bleed feed in (decopperized electrolyte from the liberators)")
    # feed pump and line to the circulation loop
    ft.box((0.9, 0.5, 0.6), (FEED[0] + 2.2, FEED[1], 0.6), M['motor'])
    bh.pipe_run(ft, [(FEED[0] + 1.5, FEED[1], 0.6), (FEED[0] + 1.9, FEED[1], 0.6)], 0.06, M['frp'])
    bh.pipe_run(ft, [(FEED[0] + 2.6, FEED[1], 0.6), (HEATER[0], FEED[1], 0.6), (HEATER[0], 1.0, 0.6)],
                0.06, M['stainless'])
    ft.finish(col)

    hx = pb.Part(P + "Heater", pivot=(HEATER[0], HEATER[1], 0))
    hx.box_mm((HEATER[0] - 1.2, HEATER[1] - 1.2, 0), (HEATER[0] + 1.2, HEATER[1] + 1.2, 0.3), M['conc'])
    for sx in (-0.8, 0.8):
        hx.beam_between((HEATER[0] + sx, HEATER[1], 0.3), (HEATER[0] + sx, HEATER[1], 2.3), 0.2, 0.2, M['steel'])
    hx.cyl(0.6, 5.0, (HEATER[0], HEATER[1], 4.3), M['stainless'], seg=24)        # 1.2 m x 5 m shell
    for z in (1.8, 6.8):
        hx.cyl(0.75, 0.12, (HEATER[0], HEATER[1], z), M['grey'], seg=24)         # tube sheet flanges
    hx.cyl(0.6, 0.5, (HEATER[0], HEATER[1], 1.55), M['stainless'], seg=24, r2=0.6)
    hx.cyl(0.3, 0.6, (HEATER[0], HEATER[1], 1.0), M['stainless'], seg=16, r2=0.6)  # bottom channel
    # steam in near the top, condensate out near the bottom
    bh.pipe_run(hx, [(HEATER[0] - 0.6, 0, 6.2), (HEATER[0] - 2.5, 0, 6.2), (HEATER[0] - 2.5, 0, 12.0)],
                0.15, M['insul'])
    bh.flange_z(hx, (HEATER[0] - 2.5, 0, 12.0), 0.15, M['insul'], log, "Low-pressure steam in")
    bh.pipe_run(hx, [(HEATER[0] - 0.6, 0, 2.2), (HEATER[0] - 1.6, 0, 2.2), (HEATER[0] - 1.6, 0, 0.5),
                     (HEATER[0] - 1.6, -2.5, 0.5)], 0.06, M['pipe'])
    bh.flange_y(hx, (HEATER[0] - 1.6, -2.5, 0.5), 0.06, M['pipe'], log, "Steam condensate out")
    hx.finish(col)

    vb = pb.Part(P + "VapourBody", pivot=(VB[0], VB[1], 0))
    bh.vtank(vb, VB, VB_Z0, VB_R, VB_H, M['stainless'], bottom='cone', top='dish')
    vb.cyl(0.35, 1.0, (VB[0], VB[1], VB_Z0 + VB_H + 0.7), M['stainless'], seg=16)     # vapour outlet
    for k in range(4):                                                                # support lugs + legs
        a = math.radians(45 + 90 * k)
        q = (VB[0] + math.cos(a) * (VB_R + 0.25), VB[1] + math.sin(a) * (VB_R + 0.25))
        vb.box((0.5, 0.5, 0.3), (q[0], q[1], VB_Z0 + 0.8), M['steel'])
        vb.beam_between((q[0], q[1], 0), (q[0], q[1], VB_Z0 + 0.65), 0.25, 0.25, M['steel'])
    vb.cyl(0.25, 0.25, (VB[0] + VB_R + 0.05, 0, VB_Z0 + 2.4), M['grey'], rot=(0, 90, 0), seg=16)  # sight glass
    vb.finish(col)

    # circulation loop: vapour body bottom -> pump -> heater bottom; heater top -> vapour body side
    lp = pb.Part(P + "CirculationLoop", pivot=(HEATER[0], 0, 0))
    vb_bot = VB_Z0 - VB_R * math.tan(math.radians(30)) * 1.7 - 0.3
    pump = Vector((10.0, 0, 1.0))
    bh.pipe_run(lp, [(VB[0], 0, vb_bot), (VB[0], 0, pump.z), (pump.x + 0.6, 0, pump.z)], 0.25, M['stainless'])
    bh.pipe_run(lp, [(pump.x - 0.6, 0, pump.z), (HEATER[0] + 0.0, 0, pump.z), (HEATER[0], 0, 0.7)],
                0.25, M['stainless'])
    bh.pipe_run(lp, [(HEATER[0], 0, 6.86), (HEATER[0], 0, 7.6), (HEATER[0] + 1.0, 0, 7.6),
                     (VB[0] - VB_R - 0.05, 0, 7.0)], 0.25, M['stainless'])
    lp.box((1.2, 1.0, 0.9), pump, M['stainless'])                                    # axial pump casing
    lp.box((1.0, 0.9, 0.3), pump + Vector((0, 0, -0.6)), M['steel'])
    lp.cyl(0.35, 1.1, pump + Vector((0, -1.3, 0)), M['motor'], rot=(90, 0, 0), seg=16)
    lp.box((0.6, 0.4, 0.4), pump + Vector((0, -0.65, 0)), M['grey'])
    lp.box_mm((pump.x - 0.8, -2.0, 0), (pump.x + 0.8, 0.8, 0.15), M['conc'])
    # product slurry draw-off from the loop to the slurry tank on the centrifuge deck
    bh.pipe_run(lp, [(VB[0] + 0.3, 0, pump.z), (VB[0] + 0.3, -1.5, pump.z), (14.0, -1.5, pump.z),
                     (14.0, -1.5, DECK_Z + 3.0), (SLURRY[0], SLURRY[1] + 1.0, DECK_Z + 3.0)], 0.08, M['stainless'])
    lp.box((0.8, 0.5, 0.6), (14.0, -2.2, 0.45), M['motor'])                        # slurry transfer pump
    lp.finish(col)

    # condenser, vacuum pump and condensate tank
    x0, x1, cy, cz = COND
    cd = pb.Part(P + "Condenser", pivot=(x0, cy, 0))
    bh.htank(cd, (x0, cy, cz), (x1, cy, cz), 0.6, M['grey'], saddles=0)
    bh.pipe_run(cd, [(VB[0], 0, VB_Z0 + VB_H + 1.2), (VB[0], 0, cz + 1.3), (x0 + 0.8, cy, cz + 1.3),
                     (x0 + 0.8, cy, cz + 0.55)], 0.35, M['stainless'])
    for x in (x0 + 0.6, x1 - 0.6):
        cd.beam_between((x, cy - 0.5, 0), (x, cy - 0.5, cz - 0.55), 0.2, 0.2, M['steel'])
        cd.beam_between((x, cy + 0.5, 0), (x, cy + 0.5, cz - 0.55), 0.2, 0.2, M['steel'])
        cd.beam_between((x, cy - 0.5, cz - 0.6), (x, cy + 0.5, cz - 0.6), 0.2, 0.2, M['steel'])
    for dz, nm in ((0.25, "Cooling water in (condenser)"), (-0.25, "Cooling water out (condenser)")):
        bh.pipe_run(cd, [(x1 + 0.1, cy, cz + dz), (x1 + 1.4, cy, cz + dz)], 0.15, M['pipe'])
        bh.flange_x(cd, (x1 + 1.4, cy, cz + dz), 0.15, M['pipe'], log, nm)
    ct = (x1 - 1.0, cy + 2.3)
    bh.vtank(cd, ct, 0.3, 0.8, 2.0, M['stainless'], top='dish')                    # condensate receiver
    cd.box_mm((ct[0] - 1.0, ct[1] - 1.0, 0), (ct[0] + 1.0, ct[1] + 1.0, 0.3), M['conc'])
    bh.pipe_run(cd, [(x1 - 1.0, cy, cz - 0.6), (x1 - 1.0, cy, 3.0), (ct[0], ct[1], 3.0), (ct[0], ct[1], 2.5)],
                0.1, M['stainless'])                                               # barometric leg
    vp = (x1 + 2.5, cy + 2.3)
    cd.box_mm((vp[0] - 1.2, vp[1] - 0.8, 0), (vp[0] + 1.2, vp[1] + 0.8, 0.25), M['conc'])
    cd.cyl(0.45, 0.9, (vp[0] - 0.3, vp[1], 0.75), M['grey'], rot=(0, 90, 0), seg=20)   # liquid ring pump
    cd.cyl(0.3, 0.8, (vp[0] + 0.6, vp[1], 0.75), M['motor'], rot=(0, 90, 0), seg=16)
    bh.pipe_run(cd, [(x1 - 0.2, cy, cz + 0.6), (x1 - 0.2, cy, cz + 1.2), (vp[0] - 0.3, cy, cz + 1.2),
                     (vp[0] - 0.3, vp[1], 1.2)], 0.08, M['pipe'])
    bh.pipe_run(cd, [(ct[0] + 0.8, ct[1], 0.6), (ct[0] + 0.8, BLDG[3] - 0.2, 0.6)], 0.06, M['pipe'])
    bh.flange_y(cd, (ct[0] + 0.8, BLDG[3] - 0.2, 0.6), 0.06, M['pipe'], log, "Process condensate out (to electrolyte make-up)")
    cd.finish(col)

    # access platform round the vapour body top and heater
    pf = pb.Part(P + "Platform_Evaporator", pivot=(6.5, -2.0, 0))
    r = VB_R + 0.1
    bh.platform(pf, 6.5, -2.0, 13.5, 2.0, VB_Z0 + VB_H - 0.6, M, rails='NSEW',
                hole=(VB[0] - r, VB[1] - r, VB[0] + r, VB[1] + r))
    bh.stair(pf, (4.0, -2.9, 0.0), (6.45, -2.9, 3.0), M)
    bh.platform(pf, 3.0, -3.5, 6.5, -2.2, 3.0, M, rails='S')
    pb.ladder(pf, (6.2, -2.5, 3.0), VB_Z0 + VB_H - 0.6, M['yellow'], facing=0)
    pf.finish(col)


def build_centrifuge_area(col, M, log):
    """Deck, slurry tank with agitator, pusher centrifuge, mother liquor tank, screw conveyor."""
    x0, y0, x1, y1 = DECK
    dk = pb.Part(P + "Deck_Centrifuge", pivot=(x0, y0, 0))
    bh.platform(dk, x0, y0, x1, y1, DECK_Z, M, rails='NSE')
    bh.stair(dk, (x0 - 3.8, y1 - 0.6, 0.0), (x0 - 0.05, y1 - 0.6, DECK_Z), M)
    dk.finish(col)

    st = pb.Part(P + "SlurryTank", pivot=(SLURRY[0], SLURRY[1], DECK_Z))
    bh.vtank(st, SLURRY, DECK_Z + 0.1, 1.1, 2.4, M['stainless'], top='flat')
    st.box((2.6, 0.25, 0.25), (SLURRY[0], SLURRY[1], DECK_Z + 2.65), M['steel'])     # agitator bridge
    bh.drive(st, (SLURRY[0], SLURRY[1], DECK_Z + 2.78), M, r=0.2, length=0.6)
    bh.pipe_run(st, [(SLURRY[0] + 1.1, SLURRY[1], DECK_Z + 0.4), (CENT[0] - 1.6, CENT[1], DECK_Z + 0.4),
                     (CENT[0] - 1.6, CENT[1], DECK_Z + 1.2)], 0.07, M['stainless'])
    st.finish(col)
    bh.agitator(P + "SlurryTank_Agitator", SLURRY, DECK_Z + 2.78, DECK_Z + 0.6, 0.8, col, M)

    # pusher centrifuge: static casing and frame, rotating basket, reciprocating pusher plate
    cx, cy = CENT
    az = DECK_Z + 1.2
    cf = pb.Part(P + "Centrifuge", pivot=(cx, cy, DECK_Z))
    cf.box_mm((cx - 2.0, cy - 0.9, DECK_Z), (cx + 1.6, cy + 0.9, DECK_Z + 0.5), M['green'])   # base frame
    cf.box_mm((cx - 2.0, cy - 0.7, DECK_Z + 0.5), (cx - 0.6, cy + 0.7, az + 0.4), M['green'])  # bearing housing
    cf.cyl_between((cx - 0.6, cy, az), (cx + 1.0, cy, az), 0.75, M['stainless'], seg=32)       # casing
    cf.cyl_between((cx + 1.0, cy, az), (cx + 1.3, cy, az), 0.75, M['stainless'], seg=32, r2=0.5)
    cf.box((0.8, 0.8, 0.6), (cx + 0.9, cy, DECK_Z + 0.2), M['stainless'])                     # solids chute
    cf.box((0.7, 0.6, 0.6), (cx - 1.3, cy - 1.2, DECK_Z + 0.8), M['motor'])                   # main motor
    cf.box((0.6, 0.6, 0.5), (cx - 1.3, cy + 1.2, DECK_Z + 0.5), M['grey'])                    # hydraulic unit
    cf.finish(col)
    bk = pb.Part(P + "Centrifuge_Basket", pivot=(cx, cy, az))
    bk.cyl_between((cx - 0.5, cy, az), (cx + 0.9, cy, az), 0.6, M['grey'], seg=32)
    bk.cyl_between((cx - 0.55, cy, az), (cx - 0.5, cy, az), 0.68, M['grey'], seg=32)
    bk.finish(col)
    pu = pb.Part(P + "Centrifuge_Pusher", pivot=(cx - 0.4, cy, az))
    pu.cyl_between((cx - 0.45, cy, az), (cx - 0.35, cy, az), 0.55, M['stainless'], seg=24)
    pu.cyl_between((cx - 1.6, cy, az), (cx - 0.45, cy, az), 0.08, M['grey'], seg=12)
    pu.finish(col)

    # mother liquor (black acid) tank at grade under the deck
    mlc = (cx - 1.5, y0 - 2.2)
    ml = pb.Part(P + "MotherLiquorTank", pivot=(mlc[0], mlc[1], 0))
    ml.cyl(1.5, 0.3, (mlc[0], mlc[1], 0.15), M['conc'], seg=32)
    bh.vtank(ml, mlc, 0.3, 1.2, 3.0, M['frp'], top='dish')
    bh.pipe_run(ml, [(cx + 0.2, cy, DECK_Z + 0.5), (cx + 0.2, cy, DECK_Z - 0.2), (cx + 0.2, mlc[1] + 0.5, DECK_Z - 0.2),
                     (mlc[0], mlc[1] + 0.5, 3.6)], 0.08, M['frp'])
    ml.box((0.8, 0.5, 0.6), (mlc[0] + 1.9, mlc[1], 0.6), M['motor'])
    bh.pipe_run(ml, [(mlc[0] + 1.2, mlc[1], 0.6), (mlc[0] + 1.5, mlc[1], 0.6)], 0.06, M['frp'])
    bh.pipe_run(ml, [(mlc[0] + 2.3, mlc[1], 0.6), (mlc[0] + 2.3, BLDG[1] + 0.2, 0.6)], 0.06, M['frp'])
    bh.flange_y(ml, (mlc[0] + 2.3, BLDG[1] + 0.2, 0.6), 0.06, M['frp'], log,
                "Mother liquor (black acid) out, to acid return / electrolyte make-up")
    ml.finish(col)

    # screw conveyor: centrifuge solids chute -> dryer feed, with a separate rotating flight
    a = Vector((cx + 0.9, cy, DECK_Z - 0.3))
    b = Vector((DRYER[0] + 0.6, DRYER[2], 3.2))
    sc = pb.Part(P + "ScrewConveyor", pivot=a)
    sc.cyl_between(a, b, 0.25, M['stainless'], seg=16)
    sc.box((0.5, 0.5, 0.5), b + Vector((0.2, 0, -0.4)), M['stainless'])
    sc.cyl_between(b + Vector((0.2, 0, -0.65)), Vector((DRYER[0] + 0.8, DRYER[2], 2.3)), 0.15, M['stainless'])
    sc.box((0.6, 0.4, 0.4), a + Vector((-0.5, 0, 0)), M['motor'])
    sc.beam_between(a.lerp(b, 0.5) + Vector((0, 0, -0.25)), Vector((a.lerp(b, 0.5).x, cy, 0)), 0.15, 0.15, M['steel'])
    sc.finish(col)
    fl = pb.Part(P + "ScrewConveyor_Flight", pivot=a)
    d = (b - a)
    n = int(d.length / 0.25)
    side = Vector((0, 1, 0))
    up = d.normalized().cross(side).normalized()
    fl.cyl_between(a, b, 0.05, M['grey'], seg=8)
    for i in range(n):
        q = a + d * (i / n)
        ang = 2 * math.pi * i / 6
        tip = q + (side * math.cos(ang) + up * math.sin(ang)) * 0.2
        fl.cyl_between(q, tip, 0.02, M['grey'], seg=6)
    fl.finish(col)


def build_dryer_and_bagging(col, M, log):
    """Fluid bed dryer, cyclone, bag filter, fan, rotary valve, bucket elevator, product bin, bagging."""
    x0, x1, y = DRYER
    dr = pb.Part(P + "FluidBedDryer", pivot=(x0, y, 0))
    dr.box_mm((x0 - 0.5, y - 1.6, 0), (x1 + 0.5, y + 1.6, 0.25), M['conc'])
    dr.box_mm((x0, y - 0.9, 0.9), (x1, y + 0.9, 1.5), M['stainless'])            # air plenum
    dr.box_mm((x0, y - 0.8, 1.5), (x1, y + 0.8, 2.4), M['stainless'])            # bed
    dr.box_mm((x0 + 0.3, y - 0.8, 2.4), (x1 - 0.3, y + 0.8, 3.2), M['stainless'])  # freeboard hood
    for x in (x0 + 0.3, (x0 + x1) / 2, x1 - 0.3):
        for s in (-0.8, 0.8):
            dr.beam_between((x, y + s, 0.25), (x, y + s, 0.9), 0.15, 0.15, M['steel'])
    # hot air: fan + steam air heater feeding the plenum
    ah = Vector((x0 + 1.0, y + 3.0, 1.2))
    dr.box((1.2, 1.0, 1.4), ah, M['grey'])
    dr.box((1.0, 1.0, 1.0), ah + Vector((-1.4, 0, -0.2)), M['motor'])
    bh.pipe_run(dr, [ah + Vector((0, -0.5, 0)), (x0 + 1.0, y + 0.9, 1.2)], 0.3, M['stainless'])
    # exhaust to cyclone and bag filter
    cyc = (x1 - 1.0, y - 3.4)
    bh.vtank(dr, cyc, 2.8, 0.6, 1.6, M['stainless'], bottom='cone', top='flat', legs=3, leg_m=M['steel'])
    bh.pipe_run(dr, [((x0 + x1) / 2, y, 3.2), ((x0 + x1) / 2, y, 4.0), (cyc[0] - 0.6, cyc[1], 4.0)],
                0.3, M['stainless'])
    bf = (x1 + 2.0, y - 3.4)
    dr.box_mm((bf[0] - 1.0, bf[1] - 1.0, 2.0), (bf[0] + 1.0, bf[1] + 1.0, 5.0), M['grey'])  # bag filter
    dr.cyl(0.3, 1.8, (bf[0], bf[1], 1.1), M['grey'], seg=4, r2=1.2)
    for sx in (-0.9, 0.9):
        for sy in (-0.9, 0.9):
            dr.beam_between((bf[0] + sx, bf[1] + sy, 0), (bf[0] + sx, bf[1] + sy, 2.0), 0.15, 0.15, M['steel'])
    bh.pipe_run(dr, [(cyc[0], cyc[1], 4.4), (cyc[0], cyc[1], 5.4), (bf[0], bf[1], 5.4), (bf[0], bf[1], 5.0)],
                0.25, M['stainless'])
    ef = (bf[0] + 2.0, bf[1])
    dr.box((1.2, 1.0, 1.2), (ef[0], ef[1], 0.8), M['motor'])                       # exhaust fan
    bh.pipe_run(dr, [(bf[0] + 1.0, bf[1], 4.0), (ef[0], ef[1], 4.0), (ef[0], ef[1], 1.4)], 0.25, M['grey'])
    bh.pipe_run(dr, [(ef[0] + 0.6, ef[1], 0.8), (ef[0] + 1.0, ef[1], 0.8), (ef[0] + 1.0, ef[1], EAVE + 3.0)],
                0.25, M['grey'])
    bh.flange_z(dr, (ef[0] + 1.0, ef[1], EAVE + 3.0), 0.25, M['grey'], log, "Dryer exhaust vent (above roof)")
    dr.finish(col)

    rv = pb.Part(P + "RotaryValve", pivot=(x1 + 0.4, y, 1.2))
    rv.cyl_between((x1 + 0.2, y - 0.2, 1.2), (x1 + 0.2, y + 0.2, 1.2), 0.2, M['grey'], seg=8)
    rv.finish(col)
    rh = pb.Part(P + "RotaryValve_Housing", pivot=(x1, y, 1.2))
    rh.box((0.55, 0.55, 0.15), (x1 + 0.2, y, 1.5), M['stainless'])
    rh.box((0.55, 0.55, 0.15), (x1 + 0.2, y, 0.9), M['stainless'])
    rh.box((0.4, 0.3, 0.3), (x1 + 0.2, y + 0.45, 1.2), M['motor'])
    bh.pipe_run(rh, [(x1, y, 1.8), (x1 + 0.2, y, 1.8), (x1 + 0.2, y, 1.6)], 0.12, M['stainless'])
    bh.pipe_run(rh, [(x1 + 0.2, y, 0.8), (ELEV[0], y, 0.5)], 0.12, M['stainless'])
    rh.finish(col)

    ex, ey = ELEV
    top = BIN[2] + 4.5
    el = pb.Part(P + "BucketElevator", pivot=(ex, ey, 0))
    el.box_mm((ex - 0.8, ey - 0.6, 0), (ex + 0.8, ey + 0.6, 0.25), M['conc'])
    el.box_mm((ex - 0.6, ey - 0.4, 0.25), (ex + 0.6, ey + 0.4, 1.4), M['grey'])     # boot
    for sx in (-0.3, 0.3):
        el.box_mm((ex + sx - 0.2, ey - 0.3, 1.4), (ex + sx + 0.2, ey + 0.3, top), M['grey'])  # up / down legs
    el.box_mm((ex - 0.7, ey - 0.45, top), (ex + 0.7, ey + 0.45, top + 1.0), M['grey'])      # head
    el.box((0.6, 0.4, 0.4), (ex, ey + 0.7, top + 0.5), M['motor'])
    bh.pipe_run(el, [(ex + 0.6, ey, top + 0.4), (BIN[0], BIN[1], BIN[2] + 3.4)], 0.15, M['stainless'])
    el.finish(col)

    bx, by, bz = BIN
    pb_ = pb.Part(P + "ProductBin", pivot=(bx, by, 0))
    bh.vtank(pb_, (bx, by), bz, 1.3, 3.0, M['stainless'], bottom='cone', top='flat', legs=4, leg_m=M['steel'])
    pb_.box((0.4, 0.4, 0.3), (bx, by, bz - 1.9), M['grey'])                        # slide gate
    # bagging station: weigh hopper and filling spout, roller conveyor with 25 kg bags
    pb_.box_mm((bx - 0.5, by - 0.5, 1.6), (bx + 0.5, by + 0.5, 2.6), M['stainless'])
    pb_.cyl(0.12, 0.5, (bx, by, 1.35), M['stainless'], seg=12)
    pb_.box_mm((bx - 0.8, by - 0.8, 0), (bx + 0.8, by + 0.8, 0.5), M['green'])      # bag platform scale
    for i in range(10):
        x = bx + 1.0 + i * 0.4
        pb_.cyl_between((x, by - 0.4, 0.5), (x, by + 0.4, 0.5), 0.04, M['grey'], seg=8)
    pb_.beam_between((bx + 0.9, by - 0.45, 0.45), (bx + 4.9, by - 0.45, 0.45), 0.06, 0.12, M['steel'])
    pb_.beam_between((bx + 0.9, by + 0.45, 0.45), (bx + 4.9, by + 0.45, 0.45), 0.06, 0.12, M['steel'])
    pb_.finish(col)

    bags = pb.Part(P + "Bags_25kg", pivot=(bx, by + 3.5, 0))
    bags.box((0.4, 0.3, 0.6), (bx, by, 0.85), M['clad'])                            # bag on the filler
    pal = (bx + 0.5, by + 3.5)
    bags.box((1.2, 1.0, 0.14), (pal[0], pal[1], 0.07), M['frp'])
    # 25 kg bags (~0.58 x 0.48 x 0.13 m filled flat), 4 per layer, 10 layers = 1 t
    for layer in range(10):
        for k in range(4):
            q = (pal[0] - 0.3 + 0.6 * (k % 2), pal[1] - 0.25 + 0.5 * (k // 2))
            bags.box((0.57, 0.47, 0.13), (q[0], q[1], 0.14 + 0.065 + layer * 0.135), M['clad'])
    bags.finish(col)
    log.append(("Bagged NiSO4·6H2O pallet pickup", (round(pal[0], 2), round(pal[1], 2), 0.0)))


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    M = bh.std_mats()
    log = []
    build_feed_and_evaporator(col, M, log)
    build_centrifuge_area(col, M, log)
    build_dryer_and_bagging(col, M, log)
    bh.portal_building(P + "Building", *BLDG, EAVE, col, M, walls='NSEW', crane_rail=None)
    pb.ref_human(ref, (VB[0] - 2.2, -1.5, VB_Z0 + VB_H - 0.6))
    pb.ref_human(ref, (CENT[0] + 0.5, -2.0, DECK_Z))
    pb.ref_human(ref, (BIN[0] - 1.5, BIN[1] + 1.5, 0.0))
    pb.ref_ground(ref, (-10, -20, 52, 18), [], z=-0.02)
    return col, log


def write_readme(col, log):
    rows = pb.pivot_table([col.name])
    conn = "\n".join(f"| {a} | {b} |" for a, b in log)
    txt = f"""# SM_NickelSulfate

Nickel sulfate plant for the tankhouse electrolyte bleed: forced-circulation evaporative
crystallizer with vacuum condenser, pusher centrifuge, fluid bed dryer and 25 kg bagging, in one
building. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/ByproductsRod/build_nickel_sulfate.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Building
{BLDG[2] - BLDG[0]:.0f} × {BLDG[3] - BLDG[1]:.0f} m (x {BLDG[0]:.0f} to {BLDG[2]:.0f}, y {BLDG[1]:.0f} to {BLDG[3]:.0f}),
{EAVE:.0f} m eaves; the dryer vent stands above the roof. Place it next to the liberator cells
(Tankhouse thread); the only process feed is the decopperized bleed flange below.

## Flowsheet (simplified)

Decopperized bleed (copper already electrowon out in the liberator cells) → feed tank (FRP,
Ø3.0 × 4.0 m) → forced-circulation crystallizer: vertical heater (Ø1.2 × 5 m, LP steam) and
vapour body (Ø2.5 m, 4 m straight side, cone bottom), axial circulation pump, vacuum from a
surface condenser and liquid ring vacuum pump → NiSO4·6H2O slurry drawn off to the agitated slurry
tank → pusher centrifuge (wet crystals) → screw conveyor → fluid bed dryer (6 × 1.6 m bed, cyclone
and bag filter on the exhaust) → rotary valve → bucket elevator → product bin → 25 kg bags on 1 t
pallets. The centrifuge mother liquor (black acid, strong H2SO4 with residual Ni/As/Sb) goes to
its own tank and leaves through a flange.

Many refineries use an evaporation-and-cooling route with a separate cooling crystallizer, and
some newer ones replace evaporation with ion exchange / acid retardation (Palabora runs acid
retardation and three IX stages before its crystallizer). The IX stage is not modelled.

## Moving parts

| Part | Motion |
|---|---|
| NIS_SlurryTank_Agitator | Spin about Z |
| NIS_Centrifuge_Basket | Spin about X (pusher centrifuges run roughly 1,000-2,000 rpm; estimate) |
| NIS_Centrifuge_Pusher | Translate along X, short stroke (~50 mm) at ~1 Hz, while also spinning with the basket |
| NIS_ScrewConveyor_Flight | Spin about its own axis (the axis runs from its pivot toward the dryer feed) |
| NIS_RotaryValve | Spin about Y |

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
each part at the pivot listed above. The building roof and walls are separate objects
(NIS_Building_Roof, _Wall_N/S/E/W) so they can be hidden for cutaways.

## Dimensions

I found no published drawing of a copper-refinery nickel sulfate plant. The process chain
(evaporative crystallizer → centrifuge → fluid bed dryer → rotary valve → product bin → 25 kg
bags) is sourced from Palabora's description; all sizes and the layout are estimates.

| Item | Value | Status |
|---|---|---|
| Process chain and 25 kg bag product | | Sourced (Palabora) |
| Black acid (mother liquor) by-product | | Sourced (Aurubis Olen factsheet, as quoted in a search result; the PDF itself was not opened) |
| Throughput basis | ~1-2 t/d NiSO4·6H2O | Estimate for a mid-size refinery bleed |
| Feed tank Ø3.0 × 4.0 m FRP | ≈ 28 m³ | Estimated |
| Heater Ø1.2 × 5 m, vapour body Ø2.5 m × 4 m + cone | | Estimated |
| Condenser Ø1.2 × 4.5 m, condensate receiver Ø1.6 × 2 m | | Estimated |
| Slurry tank Ø2.2 × 2.4 m, centrifuge basket Ø1.2 × 1.4 m | | Estimated |
| Fluid bed dryer bed 6.0 × 1.6 m | | Estimated |
| Product bin Ø2.6 × 3 m + cone | ≈ 20 m³ | Estimated |
| Building 42 × 18 m, 13 m eaves | | Own design |

Sources: Palabora nickel sulphate production (https://palabora.co.za/Our-Activities/Our-products/Nickel-Sulphate-production);
Aurubis Olen factsheet (https://aurubis.com/dam/jcr:cd8a8481-e965-4fd8-a11e-de02ecfa7a91/2024_12_factsheet_BOB_EN.pdf);
emew on liberator cells and nickel recovery (https://emew.com/blog/liberating-copper-and-nickel-a-true-story).

## Files

- SM_NickelSulfate.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_Evaporator.png, Preview_CentrifugeDryer.png (roof and south wall hidden)
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
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (2, -42, 30), (22, 0, 3), lens=28)
    pb.render_view(os.path.join(OUT, "Preview_Evaporator.png"), (2, -9.5, 9), (11, 1, 5), lens=22)
    pb.render_view(os.path.join(OUT, "Preview_CentrifugeDryer.png"), (41, 6.5, 7.5), (31, -4, 1.5), lens=22)
    for n in hide:
        bpy.data.objects[n].hide_render = False


main()
