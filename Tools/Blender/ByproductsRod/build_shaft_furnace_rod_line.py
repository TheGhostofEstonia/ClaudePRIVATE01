"""
build_shaft_furnace_rod_line.py - SM_ShaftFurnaceRodLine (cathode melting and continuous rod line).

Run:  blender -b --factory-startup --python Tools/Blender/ByproductsRod/build_shaft_furnace_rod_line.py

Own local origin (0, 0, 0) at grade, +X = direction of flow. Flow: cathode bundles -> skip hoist ->
shaft furnace -> launder -> drum holding furnace -> launder -> tundish -> casting wheel with steel
band (Southwire SCR style) -> pinch rolls, shear, bar preparation -> 13-stand rolling mill ->
pickling/cooling tube -> wax -> laying head and coil forming -> coil car -> strapping -> coil conveyor.
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
OUT = os.path.join(REPO, "Meshes", "ShaftFurnaceRodLine")
NAME = "SM_ShaftFurnaceRodLine"
P = "SFR_"

# ---------------------------------------------------------------------------
# Layout (local metres). Sourced values are marked; the rest are estimates.
# ---------------------------------------------------------------------------
SF_C = (-14.0, 0.0)            # shaft furnace centre
SF_Z0, SF_Z1 = 6.0, 17.0       # shell bottom (top of plinth) and top
SF_R = 1.2                     # shell outer radius (2.4 m OD, estimated)
DOOR_Z = 14.5                  # charge door centre height
SKIP_BOT = Vector((-25.0, 0.0, 0.9))
SKIP_TOP = Vector((-17.0, 0.0, 15.2))
HF_A, HF_B, HF_Z, HF_R = -6.5, -2.5, 4.6, 1.4  # holding furnace drum x ends, axis height, radius
WHEEL_C = Vector((2.0, 0.0, 2.2))
WHEEL_R = 1.525                # 10 ft wheel (sourced, used SCR listing)
BAR_Z = 0.9                    # pass line through the mill
MILL_X0 = 11.0
STANDS = ([0.457] + [0.305] * 4 + [0.203] * 8)   # roll diameters, 18"/12"/8" (sourced listing)
STAND_STEP = 2.0
COIL_X = 66.0                  # laying head / coil forming centre
COIL_OD, COIL_ID, COIL_H = 1.8, 1.0, 1.0
BLDG = (-8.0, -10.0, 82.0, 12.0)
EAVE = 10.0


def build_charging(col, M, log):
    """Cathode bundle staging, skip hoist track and skip car."""
    # bundle staging pad with three cathode bundles (props)
    pad = pb.Part(P + "Charging_Pad", pivot=(SKIP_BOT.x - 6, 0, 0))
    pad.box_mm((SKIP_BOT.x - 10, -4, 0), (SKIP_BOT.x + 1, 4, 0.15), M['conc'])
    # roller conveyor from staging pad to the skip loading point
    for i in range(14):
        x = SKIP_BOT.x - 8.0 + i * 0.5
        pad.cyl_between((x, -0.7, 0.75), (x, 0.7, 0.75), 0.06, M['grey'], seg=10)
    for y in (-0.8, 0.8):
        pad.beam_between((SKIP_BOT.x - 8.3, y, 0.7), (SKIP_BOT.x - 1.2, y, 0.7), 0.1, 0.2, M['steel'])
        for x in (SKIP_BOT.x - 8.0, SKIP_BOT.x - 4.6, SKIP_BOT.x - 1.4):
            pad.beam_between((x, y, 0.15), (x, y, 0.6), 0.1, 0.1, M['steel'])
    pad.finish(col)
    for i, (x, y) in enumerate(((SKIP_BOT.x - 6.5, 0.0), (SKIP_BOT.x - 8.0, -2.6), (SKIP_BOT.x - 6.0, -2.6))):
        z = 0.82 if i == 0 else 0.15
        b = pb.Part(f"{P}CathodeBundle_{i + 1}", pivot=(x, y, z))
        b.box((1.05, 1.05, 0.25), (x, y, z + 0.125), M['copper'])       # ~2 t of 1 x 1 m sheets
        for yy in (y - 0.3, y + 0.3):
            b.box((1.07, 0.03, 0.27), (x, yy, z + 0.125), M['grey'])     # straps
        b.finish(col)

    # skip track (static) at 60 degrees from loading pit to the charge door
    tr = pb.Part(P + "Skip_Track", pivot=SKIP_BOT)
    d = (SKIP_TOP - SKIP_BOT).normalized()
    for y in (-0.9, 0.9):
        tr.beam_between(SKIP_BOT + Vector((0, y, 0)), SKIP_TOP + Vector((0, y, 0.6)), 0.25, 0.3, M['steel'])
    n = 6
    for i in range(n + 1):
        q = SKIP_BOT.lerp(SKIP_TOP, i / n)
        tr.beam_between(q + Vector((0, -1.0, -0.3)), q + Vector((0, 1.0, -0.3)), 0.2, 0.2, M['steel'])
        if 0 < i < n:
            for y in (-1.0, 1.0):
                tr.beam_between(q + Vector((0, y, -0.3)), Vector((q.x, y, 0)), 0.25, 0.25, M['steel'])
    # tipping chute into the charge door and hoist house on top
    tr.beam_between(SKIP_TOP + Vector((0.2, 0, 0.0)), (SF_C[0] - SF_R - 0.1, 0, DOOR_Z), 1.4, 0.08, M['steel'])
    tr.box((2.6, 2.6, 2.2), SKIP_TOP + Vector((-0.8, 0, 2.2)), M['clad'])
    tr.cyl(0.6, 2.2, SKIP_TOP + Vector((-0.8, 0, 2.2)), M['grey'], rot=(90, 0, 0), seg=20)  # winch drum
    tr.finish(col)

    sk = pb.Part(P + "Skip_Car", pivot=SKIP_BOT)
    # bucket body built square to the track: open box tilted 30 deg back from vertical
    c = SKIP_BOT + d * 1.0 + Vector((0, 0, 0.4))
    sk.box((1.4, 1.5, 0.08), c + Vector((0, 0, -0.55)), M['yellow'], rot=(0, -30, 0))
    for y in (-0.75, 0.75):
        sk.box((1.4, 0.06, 1.1), c + Vector((0, y, 0)), M['yellow'], rot=(0, -30, 0))
    sk.box((0.08, 1.5, 1.1), c + Vector((-0.6, 0, 0.3)), M['yellow'], rot=(0, -30, 0))
    for off in (0.0, 1.8):
        q = SKIP_BOT + d * off
        sk.cyl_between(q + Vector((0, -1.0, 0)), q + Vector((0, 1.0, 0)), 0.18, M['grey'], seg=12)
    sk.finish(col)
    log.append(("Cathode bundle feed (roller conveyor head)",
                tuple(round(c, 2) for c in (SKIP_BOT.x - 8.0, 0.0, 0.81))))


def build_shaft_furnace(col, M, log):
    """Concrete plinth, shaft furnace with three burner rows, charge door, hood and stack."""
    x, y = SF_C
    pl = pb.Part(P + "Furnace_Plinth", pivot=(x, y, 0))
    pl.box_mm((x - 4.0, y - 4.0, 0), (x + 4.0, y + 4.0, SF_Z0), M['conc'])
    pl.box_mm((x + 4.0, y - 2.5, 0), (HF_B + 1.0, y + 2.5, 2.6), M['conc'])    # holding furnace base
    for ang in range(0, 360, 90):
        a = math.radians(ang)
        pl.box((0.4, 0.4, 0.3), (x + 3.8 * math.cos(a), y + 3.8 * math.sin(a), SF_Z0 + 0.15), M['steel'])
    pb.handrail(pl, (x - 4.0, y - 4.0, SF_Z0), (x + 4.0, y - 4.0, SF_Z0), M['yellow'])
    pb.handrail(pl, (x - 4.0, y + 4.0, SF_Z0), (x + 4.0, y + 4.0, SF_Z0), M['yellow'])
    bh.stair(pl, (x + 2.0, y - 6.8, 0.0), (x + 2.0, y - 4.05, SF_Z0), M)
    pl.finish(col)

    sf = pb.Part(P + "ShaftFurnace", pivot=(x, y, SF_Z0))
    sf.cyl(SF_R, SF_Z1 - SF_Z0, (x, y, (SF_Z0 + SF_Z1) / 2), M['steel'], seg=32)
    sf.cyl(SF_R + 0.15, 0.6, (x, y, SF_Z0 + 0.3), M['refr'], seg=32)          # hearth band
    for z in (SF_Z0 + 3.5, SF_Z0 + 6.5, SF_Z1 - 0.3):
        sf.cyl(SF_R + 0.08, 0.2, (x, y, z), M['grey'], seg=32)                 # stiffener rings
    # three burner rows: 7 / 8 / 8 burners (US4301997 claim 18), with ring manifolds
    for row, (z, nb) in enumerate(((SF_Z0 + 0.9, 7), (SF_Z0 + 1.6, 8), (SF_Z0 + 2.3, 8))):
        for i in range(nb):
            a = 2 * math.pi * (i + 0.5 * row) / nb
            if abs(math.cos(a) - 1) < 0.2 and row == 0:
                continue  # keep the tap hole side clear on the lowest row
            p0 = Vector((x + math.cos(a) * SF_R, y + math.sin(a) * SF_R, z))
            p1 = Vector((x + math.cos(a) * (SF_R + 0.55), y + math.sin(a) * (SF_R + 0.55), z))
            sf.cyl_between(p0, p1, 0.11, M['grey'], seg=12)
            sf.cyl_between(p1, p1 + Vector((0, 0, 0.35)), 0.04, M['pipe'], seg=8)
        sf.cyl(SF_R + 0.6, 0.08, (x, y, z + 0.35), M['pipe'], seg=40)           # visual ring
    # tap hole block and spout toward +X
    sf.box((0.5, 0.6, 0.5), (x + SF_R + 0.15, y, SF_Z0 + 0.35), M['refr'])
    # charge door frame on -X side
    sf.box((0.25, 1.8, 1.8), (x - SF_R - 0.05, y, DOOR_Z), M['grey'])
    # hood and flue
    sf.cyl(SF_R, 1.2, (x, y, SF_Z1 + 0.6), M['steel'], seg=32, r2=0.6)
    bh.pipe_run(sf, [(x, y, SF_Z1 + 1.2), (x, y, SF_Z1 + 2.5), (x, y - 6.0, SF_Z1 + 2.5),
                     (x, y - 6.0, SF_Z1 + 1.0)], 0.5, M['steel'])
    # charging platform at the door
    sf.box_mm((x - 4.0, y - 2.5, DOOR_Z - 1.3), (x - SF_R, y + 2.5, DOOR_Z - 1.25), M['grate'])
    pb.handrail(sf, (x - 4.0, y + 2.5, DOOR_Z - 1.25), (x - SF_R, y + 2.5, DOOR_Z - 1.25), M['yellow'])
    pb.handrail(sf, (x - 4.0, y - 2.5, DOOR_Z - 1.25), (x - SF_R, y - 2.5, DOOR_Z - 1.25), M['yellow'])
    pb.ladder(sf, (x - 3.6, y + 2.3, SF_Z0), DOOR_Z - 1.25, M['yellow'], facing=90)
    sf.finish(col)

    door = pb.Part(P + "ChargeDoor", pivot=(x - SF_R - 0.2, y, DOOR_Z))
    door.box((0.12, 1.6, 1.4), (x - SF_R - 0.2, y, DOOR_Z), M['refr'])
    door.box((0.06, 1.7, 1.5), (x - SF_R - 0.28, y, DOOR_Z), M['steel'])
    door.finish(col)

    # exhaust fan and stack (static)
    st = pb.Part(P + "Stack", pivot=(x, y - 6.0, 0))
    st.box_mm((x - 1.5, y - 7.5, 0), (x + 1.5, y - 4.5, 0.4), M['conc'])
    st.cyl(0.55, SF_Z1 + 1.0, (x, y - 6.0, (SF_Z1 + 1.0) / 2 + 0.4), M['steel'], seg=24)   # down-comer
    st.box((1.6, 1.4, 1.6), (x + 1.4, y - 6.0, 1.2), M['motor'])               # induced draught fan
    st.cyl(0.7, 26.0, (x + 3.2, y - 6.0, 13.4), M['steel'], seg=24)            # 26 m stack
    st.cyl_between((x + 2.2, y - 6.0, 1.2), (x + 3.2, y - 6.0, 1.2), 0.45, M['steel'])
    st.finish(col)
    log.append(("Off-gas stack top", (round(x + 3.2, 2), round(y - 6.0, 2), 26.4)))

    # combustion air blower and gas train beside the plinth
    bl = pb.Part(P + "CombustionAir", pivot=(x, y + 5.5, 0))
    bl.box_mm((x - 1.8, y + 4.4, 0), (x + 1.8, y + 6.6, 0.3), M['conc'])
    bl.box((1.8, 1.6, 1.6), (x - 0.6, y + 5.5, 1.1), M['motor'])
    bl.cyl(0.35, 1.2, (x + 0.9, y + 5.5, 1.1), M['motor'], rot=(0, 90, 0), seg=16)
    bh.pipe_run(bl, [(x - 0.6, y + 5.5, 1.9), (x - 0.6, y + 5.5, SF_Z0 + 1.6),
                     (x - 0.6, y + SF_R + 0.6, SF_Z0 + 1.6)], 0.25, M['pipe'])
    bh.pipe_run(bl, [(x + 2.8, y + 6.5, 0.6), (x + 2.8, y + 4.2, 0.6), (x + 2.8, y + 4.2, SF_Z0 + 0.5),
                     (x + 0.8, y + SF_R + 0.6, SF_Z0 + 0.5)], 0.08, M['yellow'])  # natural gas
    bh.flange_y(bl, (x + 2.8, y + 6.5, 0.6), 0.08, M['yellow'], log, "Natural gas supply")
    bl.finish(col)


def build_holding_and_launders(col, M, log):
    """Drum holding furnace (tilts about its axis), two covered launders and the tundish."""
    hx, hz = (HF_A + HF_B) / 2, HF_Z
    st = pb.Part(P + "HoldingFurnace_Supports", pivot=(hx, 0, 2.6))
    for xr in (HF_A + 0.7, HF_B - 0.7):
        for s in (-1, 1):
            q = (xr, s * HF_R * 0.7, hz - HF_R * 0.72)
            st.cyl(0.32, 0.3, q, M['grey'], rot=(0, 90, 0), seg=16)           # trunnion rollers
            st.box((0.6, 0.6, q[2] - 2.6), (xr, s * HF_R * 0.7, (q[2] + 2.6) / 2 - 0.15), M['steel'])
    st.finish(col)
    hf = pb.Part(P + "HoldingFurnace", pivot=(hx, 0, hz))
    hf.cyl_between((HF_A, 0, hz), (HF_B, 0, hz), HF_R, M['steel'], seg=32)
    for xr in (HF_A + 0.7, HF_B - 0.7):
        hf.cyl_between((xr - 0.15, 0, hz), (xr + 0.15, 0, hz), HF_R + 0.12, M['grey'], seg=32)  # tyres
    hf.box((0.8, 0.8, 0.35), (HF_A + 1.2, 0, hz + HF_R + 0.1), M['refr'])       # inlet port
    hf.cyl_between((HF_A - 0.6, 0, hz), (HF_A, 0, hz), 0.3, M['grey'], seg=12)   # end burner
    hf.box((0.5, 0.5, 0.4), (HF_B + 0.2, 0, hz + 0.3), M['refr'])               # pouring spout
    hf.finish(col)

    def launder(name, a, b):
        """Covered refractory launder from a to b (top surface z, slight fall)."""
        p = pb.Part(name, pivot=a)
        a, b = Vector(a), Vector(b)
        p.beam_between(a, b, 0.45, 0.35, M['refr'])
        p.beam_between(a + Vector((0, 0, 0.25)), b + Vector((0, 0, 0.25)), 0.55, 0.08, M['steel'])
        return p.finish(col)

    launder(P + "Launder_ShaftToHolding",
            (SF_C[0] + SF_R + 0.4, 0, SF_Z0 + 0.35), (HF_A + 1.2, 0, hz + HF_R + 0.3))
    pour = WHEEL_C + Vector((math.cos(math.radians(150)), 0, math.sin(math.radians(150)))) * WHEEL_R
    tun_c = Vector((pour.x - 0.3, 0, pour.z + 0.9))
    launder(P + "Launder_HoldingToTundish", (HF_B + 0.45, 0, hz + 0.3), (tun_c.x - 0.5, 0, tun_c.z + 0.2))
    tu = pb.Part(P + "Tundish", pivot=tun_c)
    tu.box((1.0, 0.7, 0.5), tun_c, M['refr'])
    tu.box((1.04, 0.74, 0.06), tun_c + Vector((0, 0, 0.28)), M['steel'])
    tu.cyl_between(tun_c + Vector((0.3, 0, -0.25)), pour + Vector((0, 0, 0.05)), 0.05, M['refr'], seg=10)
    tu.box((0.12, 0.12, 0.6), tun_c + Vector((0.3, 0, 0.55)), M['grey'])        # stopper rod
    tu.finish(col)
    # tundish stand
    ts = pb.Part(P + "Tundish_Stand", pivot=(tun_c.x, 0, 0))
    for yy in (-0.7, 0.7):
        ts.beam_between((tun_c.x - 0.6, yy, 0), (tun_c.x - 0.6, yy, tun_c.z - 0.3), 0.15, 0.15, M['steel'])
    ts.beam_between((tun_c.x - 0.6, -0.7, tun_c.z - 0.3), (tun_c.x - 0.6, 0.7, tun_c.z - 0.3), 0.15, 0.15, M['steel'])
    ts.box((0.6, 1.6, 0.1), (tun_c.x - 0.4, 0, tun_c.z - 0.25), M['steel'])
    ts.finish(col)
    return pour


def hull_points(circles, n=96):
    """Convex hull (in X-Z) of a set of circles (cx, cz, r): the path a band wrapped round them takes."""
    pts = []
    for cx, cz, r in circles:
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    pts = sorted(set((round(a, 5), round(b, 5)) for a, b in pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]   # counter-clockwise loop


def build_caster(col, M, log):
    """Casting wheel, idler band wheels, steel band (continuous UVs), sprays and frame."""
    cx, cz = WHEEL_C.x, WHEEL_C.z
    idlers = [(cx + 2.6, cz - 1.0, 0.45, "BandWheel_Exit"),
              (cx + 1.4, cz + 2.5, 0.45, "BandWheel_Tension"),
              (cx - 1.9, cz + 2.3, 0.45, "BandWheel_Pour")]
    fr = pb.Part(P + "Caster_Frame", pivot=(cx, 0, 0))
    fr.box_mm((cx - 3.0, -1.6, 0), (cx + 3.6, 1.6, 0.3), M['conc'])
    # open side frames (one each side of the wheel) carrying the wheel and band wheel bearings
    for yy in (-0.75, 0.75):
        corners = [(cx - 2.6, 0.3), (cx + 3.2, 0.3), (cx + 3.2, cz + 0.6), (cx + 1.4, cz + 2.5),
                   (cx - 1.9, cz + 2.3)]
        for (ax, az), (bx, bz) in zip(corners, corners[1:] + corners[:1]):
            fr.beam_between((ax, yy, az), (bx, yy, bz), 0.2, 0.2, M['green'])
        for bx, bz in ((cx, cz), (cx + 2.6, cz - 1.0), (cx + 1.4, cz + 2.5), (cx - 1.9, cz + 2.3)):
            fr.beam_between((bx, yy, 0.3), (bx, yy, bz), 0.18, 0.18, M['green'])
            fr.box((0.45, 0.25, 0.45), (bx, yy, bz), M['grey'])               # bearing block
    # spray headers inside and outside the band arc
    for k in range(9):
        a = math.radians(165 + k * 18)
        for rr in (WHEEL_R + 0.35, WHEEL_R - 0.45):
            q = Vector((cx + rr * math.cos(a), 0, cz + rr * math.sin(a)))
            fr.cyl_between(q + Vector((0, -0.55, 0)), q + Vector((0, 0.55, 0)), 0.04, M['pipe'], seg=8)
    bh.pipe_run(fr, [(cx - 2.8, 1.4, 0.6), (cx - 2.8, 1.4, 2.0)], 0.1, M['pipe'])
    bh.flange_z(fr, (cx - 2.8, 1.4, 0.6), 0.1, M['pipe'], log, "Caster cooling water supply")
    bh.flange_z(fr, (cx + 3.4, -1.4, 0.3), 0.15, M['pipe'], log, "Caster cooling water return (drain)")
    fr.box((1.2, 1.0, 1.0), (cx, 1.35, cz), M['motor'])                        # wheel drive (+Y side)
    fr.finish(col)

    wh = pb.Part(P + "CastWheel", pivot=WHEEL_C)
    wh.cyl(WHEEL_R, 0.3, WHEEL_C, M['copper'], rot=(90, 0, 0), seg=64)          # Cu-Cr-Zr rim
    for yy in (-0.12, 0.12):
        wh.cyl(WHEEL_R + 0.04, 0.06, WHEEL_C + Vector((0, yy, 0)), M['copper'], rot=(90, 0, 0), seg=64)
    wh.cyl(WHEEL_R - 0.25, 0.32, WHEEL_C, M['grey'], rot=(90, 0, 0), seg=48)
    for k in range(6):
        a = math.radians(k * 60)
        wh.box((WHEEL_R * 1.4, 0.12, 0.16), WHEEL_C + Vector((math.cos(a), 0, math.sin(a))) * WHEEL_R * 0.3,
               M['steel'], rot=(0, -k * 60, 0))
    wh.cyl(0.18, 1.6, WHEEL_C, M['grey'], rot=(90, 0, 0), seg=16)
    wh.finish(col)
    for (ix, iz, ir, nm) in idlers:
        c = Vector((ix, 0, iz))
        iw = pb.Part(P + nm, pivot=c)
        iw.cyl(ir, 0.26, c, M['grey'], rot=(90, 0, 0), seg=32)
        iw.cyl(0.08, 1.5, c, M['grey'], rot=(90, 0, 0), seg=12)
        iw.finish(col)

    # band loop: hull of the wheel + idlers, offset out by half the band thickness
    loop = hull_points([(cx, cz, WHEEL_R + 0.01)] + [(a, b, r + 0.01) for a, b, r, _ in idlers])
    band = pb.Part(P + "CastBand")
    hw, t = 0.11, 0.012
    sec = [(-hw, 0.0), (hw, 0.0), (hw, t), (-hw, t)]   # (y, outward offset)
    rows, s_acc, us = [], 0.0, []
    n = len(loop)
    for i in range(n):
        a, b0, c = Vector(loop[i - 1]), Vector(loop[i]), Vector(loop[(i + 1) % n])
        tang = (c - a).normalized()
        nrm = Vector((tang.y, -tang.x))          # outward for a counter-clockwise loop
        if i:
            s_acc += (b0 - Vector(loop[i - 1])).length
        us.append(s_acc / 1.2)
        rows.append([band.bm.verts.new((b0.x + nrm.x * o, yv, b0.y + nrm.y * o)) for yv, o in sec])
    total = (s_acc + (Vector(loop[0]) - Vector(loop[-1])).length)
    for i in range(n):
        ra, rb = rows[i], rows[(i + 1) % n]
        ua, ub = us[i], (us[i + 1] if i + 1 < n else total / 1.2)
        for j in range(4):
            k = (j + 1) % 4
            f = band.bm.faces.new((ra[j], rb[j], rb[k], ra[k]))
            f.material_index = band._mi(M['stainless'])
            band.uv_faces[f] = [(ua, j / 4), (ub, j / 4), (ub, (j + 1) / 4), (ua, (j + 1) / 4)]
    band.finish(col, smooth_angle=60)
    return total, idlers


def build_bar_and_mill(col, M, log, idlers):
    """Cast bar, pinch rolls, shear, bar prep, 13 roll stands with separate rolls and drives."""
    ex, ez, er = idlers[0][:3]
    bar = pb.Part(P + "CastBar", pivot=(WHEEL_C.x, 0, BAR_Z))
    # bar leaves the band at the exit wheel and bends down to the pass line
    pts = [Vector((ex, 0, ez - er - 0.05)), Vector((ex + 0.8, 0, BAR_Z + 0.25)),
           Vector((ex + 1.8, 0, BAR_Z)), Vector((MILL_X0 - 0.5, 0, BAR_Z))]
    for a, b in zip(pts[:-1], pts[1:]):
        bar.beam_between(a, b, 0.065, 0.1, M['copper'], roll=90)
    bar.finish(col)
    # rod from mill exit to the laying head (round)
    rod = pb.Part(P + "Rod", pivot=(MILL_X0, 0, BAR_Z))
    mill_end = MILL_X0 + STAND_STEP * len(STANDS)
    rod.cyl_between((MILL_X0, 0, BAR_Z), (mill_end, 0, BAR_Z), 0.012, M['copper'], seg=8)
    rod.cyl_between((mill_end, 0, BAR_Z), (COIL_X - 3.0, 0, BAR_Z), 0.006, M['copper'], seg=6)
    rod.cyl_between((COIL_X - 3.0, 0, BAR_Z), (COIL_X - 0.5, 0, 4.3), 0.006, M['copper'], seg=6)
    rod.finish(col)

    eq = pb.Part(P + "BarPrep", pivot=(ex + 2.5, 0, 0))
    for x, w in ((ex + 2.6, 0.9), (ex + 4.0, 1.2), (ex + 5.6, 1.6)):
        eq.box_mm((x - w / 2, -0.9, 0), (x + w / 2, 0.9, BAR_Z - 0.15), M['green'])
    eq.box((1.2, 1.6, 1.0), (ex + 4.0, 0, BAR_Z + 0.65), M['green'])            # flying shear housing
    eq.box((1.6, 1.4, 0.7), (ex + 5.6, 0, BAR_Z + 0.5), M['grey'])              # edge trimmer / descaler
    eq.finish(col)
    for k, x in enumerate((ex + 2.6, ex + 3.0)):
        for s, nm in ((1, "Top"), (-1, "Bot")):
            c = Vector((x, 0, BAR_Z + s * 0.2))
            pr = pb.Part(f"{P}PinchRoll_{k + 1}_{nm}", pivot=c)
            pr.cyl(0.15, 0.4, c, M['grey'], rot=(90, 0, 0), seg=20)
            pr.finish(col)
    sh = pb.Part(P + "Shear_Blade", pivot=(ex + 4.0, 0, BAR_Z + 0.4))
    sh.box((0.08, 0.5, 0.35), (ex + 4.0, 0, BAR_Z + 0.25), M['grey'])
    sh.finish(col)

    ms = pb.Part(P + "Mill_Stands", pivot=(MILL_X0, 0, 0))
    ms.box_mm((MILL_X0 - 0.8, -1.4, 0), (mill_end, 1.4, 0.35), M['conc'])
    ms.box_mm((MILL_X0 - 0.8, -3.6, 0), (mill_end, -1.6, 0.25), M['conc'])     # drive line plinth
    ms.box_mm((MILL_X0 - 0.8, 1.2, BAR_Z + 1.3), (mill_end, 1.3, BAR_Z + 1.4), M['steel'])  # hood rail
    for i, d in enumerate(STANDS):
        x = MILL_X0 + STAND_STEP * i + STAND_STEP / 2
        horiz = (i % 2 == 0)                                    # alternate horizontal / vertical rolls
        hs = 0.9 + d * 1.6
        ms.box_mm((x - 0.35, -hs / 2, 0.35), (x + 0.35, -hs / 2 + 0.25, BAR_Z + hs / 2), M['green'])
        ms.box_mm((x - 0.35, hs / 2 - 0.25, 0.35), (x + 0.35, hs / 2, BAR_Z + hs / 2), M['green'])
        ms.box_mm((x - 0.37, -hs / 2 - 0.02, BAR_Z + hs / 2 - 0.2), (x + 0.37, hs / 2 + 0.02, BAR_Z + hs / 2 + 0.03),
                  M['green'])
        # independent drive: motor + gearbox on the -Y side, spindle to the stand
        mz = 0.25 + 0.55
        ms.box((0.9, 1.0, 1.1), (x, -3.0, mz), M['motor'])
        ms.box((0.7, 0.6, 0.9), (x, -2.1, mz - 0.1), M['grey'])
        ms.cyl_between((x, -1.8, BAR_Z), (x, -hs / 2, BAR_Z), 0.06, M['grey'], seg=10)
        r = d / 2
        g = r + 0.006 if i else r + 0.03
        for s, nm in ((1, "A"), (-1, "B")):
            if horiz:
                c = Vector((x, 0, BAR_Z + s * g))
                rot = (90, 0, 0)
            else:
                c = Vector((x, s * g, BAR_Z))
                rot = (0, 0, 0)
            rl = pb.Part(f"{P}Stand{i + 1:02d}_Roll{nm}", pivot=c)
            rl.cyl(r, 0.25 + d * 0.3, c, M['grey'], rot=rot, seg=24)
            rl.finish(col)
    ms.finish(col)
    return mill_end


def build_finishing(col, M, log, mill_end):
    """Pickling / cooling tube, dryer, wax, laying head, coil forming, coil car, strapping, conveyor."""
    pk = pb.Part(P + "Pickling_Cooling", pivot=(mill_end + 1.0, 0, 0))
    x0, x1 = mill_end + 1.0, COIL_X - 6.0
    pk.cyl_between((x0, 0, BAR_Z), (x1, 0, BAR_Z), 0.16, M['stainless'], seg=16)
    n = int((x1 - x0) / 3.0)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pk.beam_between((x, 0, 0), (x, 0, BAR_Z - 0.17), 0.12, 0.12, M['steel'])
        pk.box((0.2, 0.5, 0.06), (x, 0, BAR_Z - 0.18), M['steel'])
    # alcohol (IPA) make-up tank, recirculation pumps and drying blower
    bh.vtank(pk, (x0 + 4.0, 3.5), 0.3, 0.9, 2.2, M['stainless'], top='dish')
    pk.box_mm((x0 + 2.0, 2.0, 0), (x0 + 8.0, 5.0, 0.3), M['conc'])
    bh.pipe_run(pk, [(x0 + 4.0, 2.6, 1.2), (x0 + 4.0, 0.0, 1.2), (x0 + 4.0, 0.0, BAR_Z + 0.16)], 0.05, M['pipe'])
    pk.box((1.2, 1.0, 1.0), (x1 + 1.2, 0, BAR_Z + 0.1), M['grey'])             # air wipe / dryer
    pk.box((0.9, 0.8, 0.8), (x1 + 2.6, 0, BAR_Z + 0.1), M['yellow'])           # wax applicator
    bh.flange_y(pk, (x0 + 6.5, 5.0, 0.6), 0.05, M['pipe'], log, "Alcohol (IPA) make-up")
    pk.finish(col)

    # laying head tower: rod rises to the head on a guide trough
    lt = pb.Part(P + "Coiler_Tower", pivot=(COIL_X, 0, 0))
    lt.box_mm((COIL_X - 2.5, -2.5, 0), (COIL_X + 2.5, 2.5, 0.3), M['conc'])
    for sx in (-1.8, 1.8):
        for sy in (-1.8, 1.8):
            lt.beam_between((COIL_X + sx, sy, 0.3), (COIL_X + sx, sy, 5.4), 0.25, 0.25, M['steel'])
    lt.box_mm((COIL_X - 2.0, -2.0, 5.2), (COIL_X + 2.0, 2.0, 5.5), M['steel'])
    lt.box((0.8, 0.8, 0.8), (COIL_X, 0, 5.9), M['motor'])
    lt.beam_between((COIL_X - 3.0, 0, BAR_Z + 0.1), (COIL_X - 0.5, 0, 4.4), 0.2, 0.2, M['grey'])
    lt.finish(col)
    lh = pb.Part(P + "LayingHead", pivot=(COIL_X, 0, 4.6))
    lh.cyl(0.55, 0.5, (COIL_X, 0, 4.6), M['grey'], seg=32, r2=0.35)
    lh.cyl_between((COIL_X, 0, 4.5), (COIL_X + 0.75, 0, 4.0), 0.06, M['grey'], seg=8)   # laying pipe
    lh.finish(col)
    tub = pb.Part(P + "CoilForming_Tub", pivot=(COIL_X, 0, 0.3))
    for k in range(12):
        a = 2 * math.pi * k / 12
        q = (COIL_X + 1.15 * math.cos(a), 1.15 * math.sin(a))
        tub.cyl_between((q[0], q[1], 0.3), (q[0], q[1], 3.6), 0.05, M['grey'], seg=8)
    tub.cyl(1.2, 0.1, (COIL_X, 0, 3.6), M['grey'], seg=32)
    tub.finish(col)

    def coil(name, c, col):
        """Rod coil (estimated 1.8 m OD x 1.0 m ID x 1.0 m, ~5 t) as a ring with ribbed rings."""
        p = pb.Part(name, pivot=c)
        x, y, z = c
        p.cyl(COIL_OD / 2, COIL_H, (x, y, z + COIL_H / 2), M['copper'], seg=40, cap=False)
        p.cyl(COIL_ID / 2, COIL_H, (x, y, z + COIL_H / 2), M['copper'], seg=32, cap=False)
        for zz in (z + 0.002, z + COIL_H - 0.002):
            bm = p.bm
            import bmesh
            r = bmesh.ops.create_circle(bm, segments=40, radius=COIL_OD / 2)
            r2 = bmesh.ops.create_circle(bm, segments=40, radius=COIL_ID / 2)
            for v in r['verts'] + r2['verts']:
                v.co.x += x
                v.co.y += y
                v.co.z = zz
            e1 = [e for e in bm.edges if e.verts[0] in r['verts']]
            e2 = [e for e in bm.edges if e.verts[0] in r2['verts']]
            res = bmesh.ops.bridge_loops(bm, edges=e1 + e2)
            for f in res['faces']:
                f.material_index = p._mi(M['copper'])
        return p.finish(col)

    tt = pb.Part(P + "CoilTurntable", pivot=(COIL_X, 0, 0.3))
    tt.cyl(1.1, 0.25, (COIL_X, 0, 0.43), M['steel'], seg=32)
    tt.cyl(0.45, 0.6, (COIL_X, 0, 0.85), M['grey'], seg=24)                     # centre mandrel stub
    tt.finish(col)
    coil(P + "Coil_Forming", (COIL_X, 0.0, 0.56), col)

    # coil car on rails to the strapping station at -Y
    rails = pb.Part(P + "CoilCar_Rails", pivot=(COIL_X, 0, 0))
    for xx in (COIL_X - 0.8, COIL_X + 0.8):
        rails.box_mm((xx - 0.04, -9.5, 0.0), (xx + 0.04, -2.55, 0.15), M['grey'])
    rails.finish(col)
    cy = -3.7                                     # parked at the coiler pad edge
    car = pb.Part(P + "CoilCar", pivot=(COIL_X, cy, 0.15))
    car.box_mm((COIL_X - 1.1, cy - 1.1, 0.15), (COIL_X + 1.1, cy + 1.1, 0.34), M['yellow'])
    for xx in (COIL_X - 0.8, COIL_X + 0.8):
        for yy in (-0.8, 0.8):
            car.cyl_between((xx - 0.1, cy + yy, 0.15), (xx + 0.1, cy + yy, 0.15), 0.12, M['grey'], seg=10)
    car.finish(col)

    sx, sy = COIL_X, -7.0
    sp = pb.Part(P + "StrappingPress", pivot=(sx, sy, 0))
    sp.box_mm((sx - 2.0, sy - 2.0, 0), (sx + 2.0, sy + 2.0, 0.3), M['conc'])
    for xx in (sx - 1.6, sx + 1.6):
        sp.box_mm((xx - 0.2, sy - 0.4, 0.3), (xx + 0.2, sy + 0.4, 4.2), M['green'])
    sp.box_mm((sx - 1.8, sy - 0.5, 4.2), (sx + 1.8, sy + 0.5, 4.8), M['green'])
    sp.cyl(0.25, 1.2, (sx, sy, 5.4), M['grey'], seg=16)
    sp.box((0.9, 0.6, 1.2), (sx + 2.6, sy, 0.9), M['yellow'])                   # strapping head
    sp.finish(col)
    ram = pb.Part(P + "StrappingPress_Ram", pivot=(sx, sy, 3.6))
    ram.cyl(1.0, 0.2, (sx, sy, 3.5), M['grey'], seg=32)
    ram.cyl(0.12, 0.8, (sx, sy, 3.9), M['grey'], seg=12)
    ram.finish(col)

    # roller conveyor to the coil pickup bay at +X, three finished coils on pallets
    cv = pb.Part(P + "CoilConveyor", pivot=(sx + 2.0, sy, 0))
    for i in range(int((80.0 - (sx + 2.5)) / 0.6)):
        x = sx + 2.5 + i * 0.6
        cv.cyl_between((x, sy - 1.0, 0.6), (x, sy + 1.0, 0.6), 0.07, M['grey'], seg=10)
    for yy in (sy - 1.1, sy + 1.1):
        cv.beam_between((sx + 2.3, yy, 0.55), (80.0, yy, 0.55), 0.1, 0.25, M['steel'])
        for x in range(int(sx + 3), 80, 3):
            cv.beam_between((x, yy, 0), (x, yy, 0.45), 0.1, 0.1, M['steel'])
    cv.finish(col)
    for k, x in enumerate((71.0, 74.5, 78.0)):
        pal = pb.Part(f"{P}CoilPallet_{k + 1}", pivot=(x, sy, 0.67))
        pal.box((1.9, 1.9, 0.14), (x, sy, 0.74), M['steel'])
        pal.finish(col)
        coil(f"{P}Coil_Finished_{k + 1}", (x, sy, 0.81), col)
    log.append(("Finished coil pickup (end of coil conveyor)", (80.0, sy, 0.6)))


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    M = bh.std_mats()
    log = []
    build_charging(col, M, log)
    build_shaft_furnace(col, M, log)
    pour = build_holding_and_launders(col, M, log)
    band_len, idlers = build_caster(col, M, log)
    mill_end = build_bar_and_mill(col, M, log, idlers)
    build_finishing(col, M, log, mill_end)
    bh.portal_building(P + "Hall", *BLDG, EAVE, col, M, walls='NSE', crane_rail=8.0)
    pb.ref_human(ref, (WHEEL_C.x - 1.0, -2.2, 0.0))
    pb.ref_human(ref, (SF_C[0] + 2.0, -3.0, SF_Z0))
    pb.ref_ground(ref, (-40, -25, 95, 25), [], z=-0.02)
    return col, log, band_len, pour, mill_end


def write_readme(col, log, band_len, pour, mill_end):
    rows = pb.pivot_table([col.name])
    conn = "\n".join(f"| {a} | {b} |" for a, b in log)
    stands = ", ".join(f"{d * 1000:.0f}" for d in STANDS)
    txt = f"""# SM_ShaftFurnaceRodLine

Cathode melting shaft furnace and continuous copper rod line: skip hoist, shaft furnace, drum
holding furnace, launders and tundish, casting wheel with steel band (Southwire SCR type), bar
preparation, 13-stand rolling mill, alcohol pickling and cooling, waxing, laying head and coil
handling. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/ByproductsRod/build_shaft_furnace_rod_line.py`.

## Placement

Own local origin at (0, 0, 0) on grade, +X is the direction of flow. Not tied to the tankhouse
layout; place it wherever the cathode store is. Footprint about x -35 to 82, y -10 to 12
(hall {BLDG[2] - BLDG[0]:.0f} × {BLDG[3] - BLDG[1]:.0f} m, {EAVE:.0f} m eaves; the shaft furnace, skip hoist
and stack stand outside the west gable).

## Flow and heights

| Step | Where |
|---|---|
| Cathode bundles arrive on the roller conveyor and drop into the skip | x {SKIP_BOT.x - 8:.1f} to {SKIP_BOT.x:.1f} |
| Skip hoist, 60° track, tips into the charge door | door centre ({SF_C[0] - SF_R:.1f}, 0, {DOOR_Z:.1f}) |
| Shaft furnace on a {SF_Z0:.1f} m plinth, shell {SF_Z0:.1f} to {SF_Z1:.1f} m | centre ({SF_C[0]:.1f}, {SF_C[1]:.1f}) |
| Tap hole → launder → drum holding furnace (axis z {HF_Z:.1f}) | x {HF_A:.1f} to {HF_B:.1f} |
| Launder → tundish → pour point on the wheel at the 10 o'clock position | ({pour.x:.2f}, 0, {pour.z:.2f}) |
| Bar leaves the band at the exit band wheel, pass line z {BAR_Z:.2f} | x ≈ {WHEEL_C.x + 2.6:.1f} |
| Pinch rolls, flying shear, edge trimmer | x ≈ {WHEEL_C.x + 4.6:.1f} to {WHEEL_C.x + 8.4:.1f} |
| Rolling mill, 13 stands at {STAND_STEP:.1f} m pitch | x {MILL_X0:.1f} to {mill_end:.1f} |
| Pickling / cooling tube, air wipe, wax | x {mill_end + 1:.1f} to {COIL_X - 3:.1f} |
| Laying head and coil forming | ({COIL_X:.1f}, 0) |
| Coil car (−Y) → strapping press → coil conveyor → pickup | ({COIL_X:.1f}, −7.0) to (80, −7.0) |

## Moving parts

| Part | Motion |
|---|---|
| SFR_Skip_Car | Translate along the track, direction ({(SKIP_TOP - SKIP_BOT).normalized().x:.3f}, 0, {(SKIP_TOP - SKIP_BOT).normalized().z:.3f}), {(SKIP_TOP - SKIP_BOT).length:.1f} m travel |
| SFR_ChargeDoor | Slide up along Z (~1.6 m) |
| SFR_HoldingFurnace | Rotate about local X to tilt for draining (pivot on the drum axis) |
| SFR_CastWheel | Spin about local Y; top of the wheel moves toward −X (pour side down). Rim speed ≈ bar speed 0.20-0.28 m/s (sourced, Palabora) → ≈ 1.3-1.8 rpm |
| SFR_BandWheel_Exit / _Tension / _Pour | Spin about local Y at the same rim speed |
| SFR_CastBand | Static loop with continuous UVs (1 UV = 1.2 m along the band); pan U at band speed / 1.2. Loop length {band_len:.2f} m |
| SFR_PinchRoll_n_Top / _Bot | Spin about Y, opposite directions |
| SFR_Shear_Blade | Rotate about Y at its pivot (flying shear, used at start-up) |
| SFR_StandNN_RollA / _RollB | Spin about their own axis (odd stands horizontal rolls about Y, even stands vertical rolls about Z), A and B opposite. Speed rises down the mill |
| SFR_LayingHead | Spin about Z |
| SFR_CoilTurntable | Spin about Z, slowly, while the coil forms |
| SFR_Coil_Forming | Static; scale Z from 0 to 1 to show the coil building up |
| SFR_CoilCar | Translate along −Y from its park position at the coiler pad (y −3.7) to the strapping press (y −7); the coil is lifted off the turntable onto it (own design) |
| SFR_StrappingPress_Ram | Translate along Z (compresses the coil) |
| SFR_Coil_Finished_n, SFR_CoilPallet_n | Translate along +X on the coil conveyor |

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
each part at the pivot listed above (with it on, every pivot moves to the asset origin). The hall
roof and walls are separate objects so they can be hidden for cutaways. Copper surfaces use one
M_Copper slot; a separate emissive material for hot metal (launders, pour, bar) can be applied in
Unreal on SFR_CastBar and the launder interiors.

## Dimensions

No general-arrangement drawing of a shaft furnace rod line was found. The figures below come from
public product pages, a used-equipment listing and patents; the layout and all other sizes are mine.

| Item | Value | Status |
|---|---|---|
| Shaft furnace melting rate (design basis) | ≈ 25 t/h | Estimated; shaft furnaces for copper are built from 5 to 70 t/h (ABM paper) |
| Shaft furnace shell | Ø2.4 m × 11 m, hearth on a 6 m plinth | Estimated |
| Burner arrangement | 3 rows: 7 / 8 / 8 burners, each row fed from manifolds | Sourced (US4301997 claim 18) |
| Charging by skip hoist | | Sourced (SMS group); 60° track and heights estimated |
| Cylindrical holding furnace between shaft furnace and caster, covered heated launders, tundish with automatic pouring | | Sourced (Palabora) |
| Drum holding furnace Ø2.8 × 4.0 m | | Estimated |
| Casting wheel Ø3.05 m (10 ft), Cu-Cr-Zr rim | | Sourced (used SCR system listing) |
| Cast bar | ≈ 100 × 65 mm (≈ 6,000-6,500 mm²) | Sourced range: 6,000 mm² trapezoid (Primetals) and 10 in² (listing); modelled as a rectangle |
| Bar speed out of the caster | 0.20-0.28 m/s | Sourced (Palabora) |
| Rolling mill: 13 stands, roll Ø {stands} mm | | Sourced (used SCR listing: 1 × 18 in, 4 × 12 in, 8 × 8 in; Jinchuan SCR 7000 also 13 stands) |
| Stand pitch 2.0 m, housings, drives | | Estimated |
| Product rod Ø8 mm (7.9-14 mm range) | | Sourced (Palabora, Aurubis) |
| In-line alcohol pickling, wax coating, continuous coiling | | Sourced (Palabora, SMS Contirod) |
| Coil 1.8 m OD × 1.0 m ID × 1.0 m | ≈ 5 t | Estimated; sourced coil masses 2.3-2.7 t (listing), 2-4 t (Jinchuan), 4.6 t average (Palabora), 3.5-8 t (Aurubis) |
| Hall 90 × 22 m, 10 m eaves, crane rail at 8 m | | Own design |
| Coil car, strapping press, coil conveyor layout | | Own design |

The modelled caster is the wheel-and-band type (Southwire SCR). Contirod plants use a twin-belt
(Hazelett) caster in the same position instead.

Sources: US4301997A (https://patents.google.com/patent/US4301997); US5240494A (Asarco, cathode
melting burners, https://patents.google.com/patent/US5240494); ABM proceedings, innovations in
copper processing (https://abmproceedings.com.br/en/article/download-pdf/innovations-in-the-field-of-copper-processing);
SMS group melting furnaces (https://sms-group.com/plants/melting-and-refining-furnaces) and Contirod
fact sheet; Palabora copper rod (https://palabora.com/Our-Activities/Our-products/Copper-rod);
Aurubis Olen rod production (https://www.aurubis.com/en/olen/products/wire-rod/Productionprocess);
used SCR system listing (https://www.exapro.com/southwire-scr-system-2500-p250903031/); Primetals
SCR upgrade (https://www.primetals.com/press-media/news/primetals-technologies-awarded-project-to-increase-capacity-of-southwire-scr-copper-rod-mill);
Jinchuan SCR 7000 (https://umformtechnik.net/wire/Content/Business/New-SCR-copper-rod-mill-for-Jinchuan-Group).

## Files

- SM_ShaftFurnaceRodLine.blend / .fbx (REF not exported)
- Preview_Overview.png, Preview_FurnaceCaster.png, Preview_Mill.png, Preview_Coiler.png (hall roof and south wall hidden)
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, log, band_len, pour, mill_end = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, log, band_len, pour, mill_end)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render()
    hide = [P + "Hall_Roof", P + "Hall_Wall_S"]
    for n in hide:
        bpy.data.objects[n].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (-48, -55, 38), (18, 0, 2), lens=28)
    pb.render_view(os.path.join(OUT, "Preview_FurnaceCaster.png"), (5, -9.0, 6.5), (-4, 0, 3.8), lens=20)
    pb.render_view(os.path.join(OUT, "Preview_Mill.png"), (14, -8.5, 4.5), (26, 0, 1.0), lens=22)
    pb.render_view(os.path.join(OUT, "Preview_Coiler.png"), (58, -14, 7), (67, -3, 1.5), lens=24)
    for n in hide:
        bpy.data.objects[n].hide_render = False


main()
