"""
build_workshops.py - SM_Workshops: maintenance workshop building with machine shop, welding /
fabrication bay, electrical shop, instrument shop and tool store.

Run:  blender -b --factory-startup --python Tools/Blender/WorkshopsSafetyLab/build_workshops.py
      (add -- --no-render to skip the previews)

Layout (own design, no real drawings used): a 48 x 18 m crane-served high bay
(machine shop west, welding/fabrication east) with an 8 m lean-to along the north side
holding the electrical shop, instrument shop and tool store.
Origin = finished floor level at the centre of the high bay. +X east, +Y north.
"""
import math
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402
import wsl_common as wc  # noqa: E402
from wsl_common import F  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Meshes", "Workshops")
NAME = "SM_Workshops"

# ---------------------------------------------------------------------------
# Building parameters (all estimated)
# ---------------------------------------------------------------------------
HB_X = 24.0            # high bay half length (48 m)
HB_Y = 9.0             # high bay half span (18 m)
EAVES = 9.0            # high bay eaves height
PITCH = 6.0            # roof pitch, degrees
RIDGE = EAVES + HB_Y * math.tan(math.radians(PITCH))
LT_Y = 17.0            # lean-to outer wall line (8 m deep)
LT_LOW, LT_HIGH = 5.0, 5.8   # lean-to eaves at the outer wall / at the high bay wall
DADO = 1.2             # concrete upstand under the cladding
RAIL_Z = 7.0           # crane rail top
RAIL_Y = 8.4           # crane rail centre line (+/-)
FRAMES = [-24 + 6 * i for i in range(9)]


def shell_wall(walls, m, a, b, h, openings=(), windows=()):
    """External wall: 1.2 m concrete upstand, then cladding up to h. Openings in floor coords."""
    wc.wall(walls, a, b, min(DADO, h), 0.2, m['dado'],
            openings=[o for o in openings if o[2] < DADO] + [w for w in windows if w[2] < DADO],
            glass=m['glass'])
    if h > DADO:
        shift = lambda lst: [(o[0], o[1], max(0.0, o[2] - DADO), o[3] - DADO) for o in lst if o[3] > DADO]
        wc.wall(walls, a, b, h - DADO, 0.08, m['clad'], openings=shift(openings),
                windows=shift(windows), z0=DADO, glass=m['glass'])


# ---------------------------------------------------------------------------
# Building shell
# ---------------------------------------------------------------------------

def build_shell(col, m):
    floor = pb.Part("WS_Floor")
    floor.box_mm((-HB_X - 0.3, -HB_Y - 0.3, -0.3), (HB_X + 0.3, LT_Y + 0.3, 0.0), m['concrete'])
    # yellow aisle lines along the central east-west aisle
    for y in (-2.6, 2.6):
        floor.box_mm((-HB_X + 0.5, y - 0.05, 0.0), (HB_X - 0.5, y + 0.05, 0.004), m['yellow'])
    floor.finish(col)

    walls = pb.Part("WS_Walls")
    clere = [(6 * i + 0.8, 6 * i + 5.2, 6.2, 7.6) for i in range(8)]
    # south wall: personnel doors at x=-15 and x=20, roller door 5x5 at x=-3
    shell_wall(walls, m, (-HB_X, -HB_Y), (HB_X, -HB_Y), EAVES,
               openings=[(8.5, 9.5, 0, 2.1), (43.5, 44.5, 0, 2.1), (18.5, 23.5, 0, 5.0)],
               windows=clere)
    # north wall of the high bay (lean-to side): electrical roller 3x3.5 at x=-15,
    # instrument door x=-2, tool store hatch x=10 and door x=13; clerestory above the lean-to roof
    shell_wall(walls, m, (-HB_X, HB_Y), (HB_X, HB_Y), EAVES,
               openings=[(7.5, 10.5, 0, 3.5), (21.5, 22.5, 0, 2.1), (33.0, 35.0, 0.95, 2.25),
                         (36.5, 37.5, 0, 2.1)],
               windows=[(6 * i + 0.8, 6 * i + 5.2, 6.6, 7.6) for i in range(8)])
    # gable ends: east roller 6x6, west roller 5x5, both on the centre line
    shell_wall(walls, m, (HB_X, -HB_Y), (HB_X, HB_Y), EAVES, openings=[(6.0, 12.0, 0, 6.0)])
    shell_wall(walls, m, (-HB_X, -HB_Y), (-HB_X, HB_Y), EAVES, openings=[(6.5, 11.5, 0, 5.0)])
    for x in (-HB_X, HB_X):
        walls.poly_prism([(-HB_Y, EAVES), (HB_Y, EAVES), (0, RIDGE)], x - 0.04, x + 0.04, m['clad'],
                         plane='YZ')
    # lean-to north wall: electrical roller 3x3.5 at x=-15, doors at x=-9, 0, 20, windows
    shell_wall(walls, m, (-HB_X, LT_Y), (HB_X, LT_Y), LT_LOW,
               openings=[(7.5, 10.5, 0, 3.5), (14.5, 15.5, 0, 2.1), (23.5, 24.5, 0, 2.1),
                         (43.5, 44.5, 0, 2.1)],
               windows=[(3.0, 6.0, 1.2, 2.4), (11.5, 13.5, 1.2, 2.4), (19.0, 22.5, 1.2, 2.4),
                        (26.0, 30.5, 1.2, 2.4)])
    # lean-to end walls with the sloping top
    for x in (-HB_X, HB_X):
        shell_wall(walls, m, (x, HB_Y), (x, LT_Y), LT_LOW)
        walls.poly_prism([(HB_Y, LT_LOW), (LT_Y, LT_LOW), (HB_Y, LT_HIGH)], x - 0.04, x + 0.04,
                         m['clad'], plane='YZ')
    # block partitions between the lean-to rooms
    for x in (-6.0, 8.0):
        wc.wall(walls, (x, HB_Y), (x, LT_Y), LT_LOW, 0.2, m['dado'])
    walls.finish(col)

    # steel frame: portal columns and rafters, lean-to columns, crane runway
    st = pb.Part("WS_Structure")
    for x in FRAMES:
        for y in (-HB_Y + 0.3, HB_Y - 0.3):
            wc.i_column(st, x, y, EAVES, m['struct'], d=0.6, bf=0.3, yaw=90)
            # crane corbel
            st.box_mm((x - 0.15, min(y, math.copysign(RAIL_Y - 0.2, y)), RAIL_Z - 1.1),
                      (x + 0.15, max(y, math.copysign(RAIL_Y - 0.2, y)), RAIL_Z - 0.75), m['struct'])
        for s in (1, -1):
            st.beam_between((x, s * (HB_Y - 0.3), EAVES - 0.35), (x, 0, RIDGE - 0.35), 0.2, 0.55,
                            m['struct'])
        wc.i_column(st, x, LT_Y - 0.2, LT_LOW, m['struct'], d=0.3, bf=0.15, yaw=90)
        st.beam_between((x, LT_Y - 0.2, LT_LOW - 0.2), (x, HB_Y, LT_HIGH - 0.2), 0.12, 0.3, m['struct'])
    for s in (1, -1):
        y = s * RAIL_Y
        st.box_mm((-HB_X, y - 0.15, RAIL_Z - 0.75), (HB_X, y + 0.15, RAIL_Z - 0.07), m['struct'])
        st.box_mm((-HB_X, y - 0.035, RAIL_Z - 0.07), (HB_X, y + 0.035, RAIL_Z), m['bright'])
        st.box_mm((-HB_X + 0.1, y - 0.2, RAIL_Z), (-HB_X + 0.4, y + 0.2, RAIL_Z + 0.5), m['yellow'])
        st.box_mm((HB_X - 0.4, y - 0.2, RAIL_Z), (HB_X - 0.1, y + 0.2, RAIL_Z + 0.5), m['yellow'])
    wc.ceiling_lights(st, [-18, -9, 0, 9, 18], [-4.5, 4.5], EAVES - 0.2, m['lamp'], m['steel'])
    wc.ceiling_lights(st, [-19, -11, -2, 4, 12, 20], [13.0], LT_LOW - 0.25, m['lamp'], m['steel'])
    st.finish(col)

    roof = pb.Part("WS_Roof")
    run = HB_Y / math.cos(math.radians(PITCH)) + 0.3
    for s in (1, -1):
        roof.box((2 * HB_X + 0.6, run, 0.1),
                 (0, s * HB_Y / 2, (EAVES + RIDGE) / 2 + 0.05), m['roof'], rot=(s * -PITCH, 0, 0))
    lt_ang = math.degrees(math.atan2(LT_HIGH - LT_LOW, LT_Y - HB_Y))
    roof.box((2 * HB_X + 0.6, (LT_Y - HB_Y) / math.cos(math.radians(lt_ang)) + 0.3, 0.1),
             (0, (HB_Y + LT_Y) / 2, (LT_LOW + LT_HIGH) / 2 + 0.05), m['roof'], rot=(-lt_ang, 0, 0))
    roof.finish(col)

    # doors: roller shutters (pivot at the top of the curtain) and hinged leaves
    rs = pb.Part("WS_DoorFrames")
    wc.roller_shutter("WS_Shutter_East", col, rs, (HB_X + 0.1, 0, 0), 6.0, 6.0, 90, m['clad'], m['steel'])
    wc.roller_shutter("WS_Shutter_West", col, rs, (-HB_X - 0.1, 0, 0), 5.0, 5.0, -90, m['clad'], m['steel'])
    wc.roller_shutter("WS_Shutter_South", col, rs, (-3.0, -HB_Y - 0.1, 0), 5.0, 5.0, 0, m['clad'], m['steel'])
    wc.roller_shutter("WS_Shutter_ElecInner", col, rs, (-15.0, HB_Y - 0.1, 0), 3.0, 3.5, 0, m['clad'], m['steel'])
    wc.roller_shutter("WS_Shutter_ElecOuter", col, rs, (-15.0, LT_Y + 0.1, 0), 3.0, 3.5, 180, m['clad'], m['steel'])
    wc.roller_shutter("WS_Shutter_StoreHatch", col, rs, (10.0, HB_Y - 0.1, 0.95), 2.0, 1.3, 0, m['bright'], m['steel'])
    rs.finish(col)
    doors = [("WS_Door_South_Machine", (-15.5, -HB_Y, 0), 0),
             ("WS_Door_South_Weld", (19.5, -HB_Y, 0), 0),
             ("WS_Door_Instrument_Inner", (-2.5, HB_Y, 0), 0),
             ("WS_Door_Store_Inner", (12.5, HB_Y, 0), 0),
             ("WS_Door_Elec_Outer", (-9.5, LT_Y, 0), 0),
             ("WS_Door_Instrument_Outer", (-0.5, LT_Y, 0), 0),
             ("WS_Door_Store_Outer", (19.5, LT_Y, 0), 0)]
    for nm, hinge, yaw in doors:
        wc.door_leaf(nm, col, hinge, 1.0, 2.1, yaw, m['blue'], m['bright'], glazed=m['glass'])
    return doors


# ---------------------------------------------------------------------------
# Machine shop equipment
# ---------------------------------------------------------------------------

def lathe(col, prefix, fr, L, W, H, swing, bed_top, m):
    """
    Engine lathe in local frame: bed along X, headstock at -X, operator side -Y, origin = floor
    centre. Separate parts: _Bed (static), _Chuck (spins about local X), _Carriage and
    _Tailstock (slide along local X).
    """
    hc = bed_top + swing / 2 + 0.05          # spindle centre height
    head_len = 0.28 * min(L, 4.0)
    x0 = -L / 2
    bed = pb.Part(prefix + "_Bed", pivot=fr.o)
    fr.bmm(bed, (x0, -W * 0.3, 0), (x0 + head_len, W * 0.3, bed_top - 0.25), m['machine'])  # pedestals
    fr.bmm(bed, (L / 2 - 0.6, -W * 0.3, 0), (L / 2, W * 0.3, bed_top - 0.25), m['machine'])
    if L > 5:
        fr.bmm(bed, (-0.4, -W * 0.3, 0), (0.4, W * 0.3, bed_top - 0.25), m['machine'])
    fr.bmm(bed, (x0, -W / 2, 0.45), (L / 2, W / 2, 0.5), m['steel'])                         # chip tray
    fr.bmm(bed, (x0 + head_len, -W * 0.22, bed_top - 0.25), (L / 2, W * 0.22, bed_top), m['machine'])
    for y in (-W * 0.17, W * 0.17):                                                           # ways
        fr.bmm(bed, (x0 + head_len, y - 0.04, bed_top), (L / 2 - 0.05, y + 0.04, bed_top + 0.02), m['bright'])
    fr.bmm(bed, (x0, -W * 0.28, bed_top - 0.25), (x0 + head_len, W * 0.3, H), m['machine'])   # headstock
    fr.bmm(bed, (x0, -W * 0.36, bed_top - 0.55), (x0 + head_len, -W * 0.28, bed_top - 0.05),
           m['machine2'])                                                                      # gearbox
    for k in range(4):
        fr.cyl(bed, 0.03, 0.08, (x0 + 0.1 + k * head_len / 4, -W * 0.3, H - 0.25), m['bright'],
               rot=(90, 0, 0), seg=10)
    for z in (bed_top - 0.35, bed_top - 0.45):                                                 # leadscrew, rod
        fr.cyl_between(bed, (x0 + head_len, -W * 0.27, z), (L / 2 - 0.1, -W * 0.27, z), 0.02,
                       m['bright'], seg=8)
    fr.bmm(bed, (x0 + 0.1, W * 0.3, 0), (x0 + head_len - 0.1, W * 0.5, bed_top - 0.3), m['machine2'])
    bed.finish(col, x_toward=fr.xdir((0, 0, 0)))

    piv = (x0 + head_len, 0, hc)
    ch = pb.Part(prefix + "_Chuck", pivot=fr.w(piv))
    r = swing * 0.32
    fr.cyl(ch, r, 0.14, (x0 + head_len + 0.07, 0, hc), m['bright'], rot=(0, 90, 0), seg=32)
    for a in (90, 210, 330):
        ya, za = math.cos(math.radians(a)) * r * 0.6, math.sin(math.radians(a)) * r * 0.6
        fr.box(ch, (0.06, 0.05, r * 0.5), (x0 + head_len + 0.17, ya, hc + za), m['steel'],
               rot=(a - 90, 0, 0))
    ch.finish(col, x_toward=fr.xdir(piv))

    xc = x0 + head_len + 0.35 * (L - head_len)
    piv = (xc, 0, bed_top)
    ca = pb.Part(prefix + "_Carriage", pivot=fr.w(piv))
    fr.bmm(ca, (xc - 0.3, -W * 0.25, bed_top + 0.02), (xc + 0.3, W * 0.25, bed_top + 0.12), m['machine'])
    fr.bmm(ca, (xc - 0.3, -W * 0.36, bed_top - 0.5), (xc + 0.3, -W * 0.25, bed_top + 0.1), m['machine'])
    fr.bmm(ca, (xc - 0.15, -W * 0.25, bed_top + 0.12), (xc + 0.15, W * 0.1, bed_top + 0.2), m['machine2'])
    fr.bmm(ca, (xc - 0.07, -W * 0.12, bed_top + 0.2), (xc + 0.07, 0.0, hc - 0.02), m['steel'])
    fr.cyl(ca, 0.09, 0.03, (xc, -W * 0.37, bed_top - 0.2), m['bright'], rot=(90, 0, 0), seg=16)
    ca.finish(col, x_toward=fr.xdir(piv))

    xt = L / 2 - 0.45
    piv = (xt, 0, bed_top)
    ta = pb.Part(prefix + "_Tailstock", pivot=fr.w(piv))
    fr.bmm(ta, (xt - 0.2, -W * 0.2, bed_top + 0.02), (xt + 0.2, W * 0.2, hc + 0.08), m['machine'])
    fr.cyl(ta, 0.05, 0.25, (xt - 0.3, 0, hc), m['bright'], rot=(0, 90, 0), seg=12)
    fr.cyl(ta, 0.02, 0.06, (xt - 0.45, 0, hc), m['bright'], rot=(0, 90, 0), seg=8, r2=0.002)
    fr.cyl(ta, 0.08, 0.03, (xt + 0.21, 0, hc), m['bright'], rot=(0, 90, 0), seg=12)
    ta.finish(col, x_toward=fr.xdir(piv))


def milling_machine(col, fr, m):
    """Turret (knee-type) milling machine. _Table slides along local X."""
    p = pb.Part("WS_Mill_Body", pivot=fr.o)
    fr.bmm(p, (-0.4, -0.2, 0), (0.4, 0.75, 0.08), m['machine'])                 # base
    fr.bmm(p, (-0.3, 0.15, 0.08), (0.3, 0.75, 1.6), m['machine'])               # column
    fr.bmm(p, (-0.3, -0.35, 0.5), (0.3, 0.15, 0.85), m['machine'])              # knee
    fr.bmm(p, (-0.25, -0.35, 0.85), (0.25, 0.1, 0.95), m['machine2'])           # saddle
    fr.cyl(p, 0.22, 0.12, (0, 0.45, 1.66), m['machine'], seg=24)               # turret
    fr.bmm(p, (-0.15, -0.55, 1.65), (0.15, 0.9, 1.9), m['machine'])             # ram
    fr.bmm(p, (-0.18, -0.75, 1.3), (0.18, -0.35, 1.9), m['machine'])            # head
    fr.cyl(p, 0.12, 0.35, (0, -0.55, 2.07), m['machine2'], seg=16)             # motor
    fr.cyl(p, 0.035, 0.15, (0, -0.55, 1.22), m['bright'], seg=12)              # quill
    fr.cyl_between(p, (-0.05, -0.36, 0.3), (-0.05, -0.36, 0.55), 0.03, m['bright'], seg=8)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (0, -0.12, 0.95)
    t = pb.Part("WS_Mill_Table", pivot=fr.w(piv))
    fr.bmm(t, (-0.7, -0.27, 0.95), (0.7, 0.03, 1.05), m['bright'])
    fr.bmm(t, (-0.15, -0.2, 1.05), (0.15, -0.04, 1.15), m['steel'])             # vice
    for x in (-0.75, 0.75):
        fr.cyl(t, 0.07, 0.03, (x, -0.12, 1.0), m['bright'], rot=(0, 90, 0), seg=12)
    t.finish(col, x_toward=fr.xdir(piv))


def radial_drill(col, fr, m):
    """Radial arm drill. _Arm swings about the column axis (local Z) and can travel up/down it."""
    p = pb.Part("WS_RadialDrill_Base", pivot=fr.o)
    fr.bmm(p, (-1.3, -0.55, 0), (1.3, 0.55, 0.25), m['machine'])
    fr.bmm(p, (-0.2, -0.45, 0.25), (1.1, 0.45, 0.85), m['machine2'])            # box table
    fr.cyl(p, 0.2, 2.5, (-1.0, 0, 1.5), m['machine'], seg=24)
    fr.cyl(p, 0.18, 0.4, (-1.0, 0, 2.95), m['machine2'], seg=24)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (-1.0, 0, 2.0)
    a = pb.Part("WS_RadialDrill_Arm", pivot=fr.w(piv))
    fr.cyl(a, 0.28, 0.6, (-1.0, 0, 2.0), m['machine'], seg=24)
    fr.bmm(a, (-0.8, -0.2, 1.8), (1.0, 0.2, 2.25), m['machine'])
    fr.bmm(a, (0.35, -0.35, 1.45), (0.75, 0.25, 2.35), m['machine'])             # drill head
    fr.cyl(a, 0.05, 0.4, (0.55, -0.1, 1.25), m['bright'], seg=12)               # spindle
    fr.cyl(a, 0.13, 0.35, (0.55, 0.0, 2.5), m['machine2'], seg=16)              # motor
    a.finish(col, x_toward=fr.xdir(piv))


def pedestal_drill(col, fr, m):
    p = pb.Part("WS_PedestalDrill", pivot=fr.o)
    fr.bmm(p, (-0.25, -0.35, 0), (0.25, 0.25, 0.06), m['machine'])
    fr.cyl(p, 0.05, 1.85, (0, 0.15, 0.97), m['bright'], seg=12)
    fr.bmm(p, (-0.18, -0.25, 0.7), (0.18, 0.1, 0.76), m['machine'])              # table
    fr.bmm(p, (-0.15, -0.3, 1.55), (0.15, 0.25, 1.85), m['machine'])            # head
    fr.cyl(p, 0.1, 0.25, (0, 0.2, 2.0), m['machine2'], seg=16)
    fr.cyl(p, 0.025, 0.15, (0, -0.2, 1.47), m['bright'], seg=8)
    for a in (0, 120, 240):
        fr.cyl_between(p, (0.16, -0.05, 1.65),
                       (0.16 + 0.0, -0.05 + 0.25 * math.cos(math.radians(a)),
                        1.65 + 0.25 * math.sin(math.radians(a))), 0.01, m['bright'], seg=6)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))


def bandsaw(col, fr, m):
    """Horizontal bandsaw. _Bow is hinged at the rear (pivot on local X axis line, rotate about local X)."""
    p = pb.Part("WS_Bandsaw_Base", pivot=fr.o)
    fr.bmm(p, (-0.9, -0.3, 0), (0.9, 0.3, 0.65), m['machine'])
    fr.bmm(p, (-0.3, -0.25, 0.65), (0.3, 0.15, 0.72), m['bright'])
    fr.bmm(p, (-0.15, -0.28, 0.72), (-0.1, 0.15, 0.85), m['steel'])              # vice jaws
    fr.bmm(p, (0.1, -0.28, 0.72), (0.15, 0.15, 0.85), m['steel'])
    for x in (-1.8, -1.4):                                                       # roller stand
        fr.cyl_between(p, (x, -0.2, 0.72), (x, 0.2, 0.72), 0.04, m['bright'], seg=10)
    fr.bmm(p, (-1.9, -0.2, 0), (-1.3, 0.2, 0.68), m['steel'])
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (0, 0.28, 0.85)
    b = pb.Part("WS_Bandsaw_Bow", pivot=fr.w(piv))
    fr.bmm(b, (-0.75, 0.15, 0.85), (0.75, 0.3, 1.25), m['machine'])
    for x in (-0.65, 0.65):
        fr.cyl(b, 0.22, 0.08, (x, 0.05, 1.02), m['machine'], rot=(90, 0, 0), seg=24)
    fr.bmm(b, (-0.65, -0.06, 0.8), (0.65, -0.04, 0.82), m['bright'])            # blade
    fr.bmm(b, (0.55, 0.15, 1.25), (0.85, 0.35, 1.45), m['machine2'])            # motor
    b.finish(col, x_toward=fr.xdir(piv))


def hydraulic_press(col, fr, m):
    """100 t H-frame workshop press. _Ram slides along local Z."""
    p = pb.Part("WS_Press_Frame", pivot=fr.o)
    for x in (-0.75, 0.75):
        fr.bmm(p, (x - 0.08, -0.12, 0), (x + 0.08, 0.12, 2.6), m['red'])
        fr.bmm(p, (x - 0.25, -0.5, 0), (x + 0.25, 0.5, 0.08), m['red'])          # feet
    fr.bmm(p, (-0.83, -0.15, 2.3), (0.83, 0.15, 2.6), m['red'])                 # top beam
    for z in (0.8, 0.95):                                                        # bed channels
        fr.bmm(p, (-0.67, -0.15, z), (0.67, -0.03, z + 0.12), m['red'])
        fr.bmm(p, (-0.67, 0.03, z), (0.67, 0.15, z + 0.12), m['red'])
    fr.cyl(p, 0.14, 0.5, (0, 0, 2.05), m['bright'], seg=24)                    # cylinder
    fr.bmm(p, (0.85, -0.3, 0), (1.35, 0.3, 0.7), m['red'])                      # power pack
    fr.cyl(p, 0.08, 0.04, (1.1, -0.31, 0.95), m['white'], rot=(90, 0, 0), seg=16)  # gauge
    fr.cyl_between(p, (1.1, -0.3, 0.7), (1.1, -0.3, 0.92), 0.01, m['bright'], seg=6)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (0, 0, 1.8)
    r = pb.Part("WS_Press_Ram", pivot=fr.w(piv))
    fr.cyl(r, 0.09, 0.4, (0, 0, 1.6), m['bright'], seg=16)
    fr.cyl(r, 0.12, 0.08, (0, 0, 1.36), m['steel'], seg=16)
    r.finish(col)


def crane(col, m, x0=-10.0, yt=0.0, hook_z=4.0):
    """10 t double-girder overhead crane. Bridge moves on X, trolley on Y, hook block on Z."""
    gz = RAIL_Z + 0.25
    br = pb.Part("WS_Crane_Bridge", pivot=(x0, 0, RAIL_Z))
    for dx in (-0.8, 0.8):
        br.box_mm((x0 + dx - 0.2, -RAIL_Y, gz), (x0 + dx + 0.2, RAIL_Y, gz + 0.9), m['yellow'])
        br.box_mm((x0 + dx - 0.03, -RAIL_Y + 0.3, gz + 0.9), (x0 + dx + 0.03, RAIL_Y - 0.3, gz + 0.96),
                  m['bright'])
    for s in (1, -1):
        y = s * RAIL_Y
        br.box_mm((x0 - 1.6, y - 0.25, RAIL_Z + 0.2), (x0 + 1.6, y + 0.25, gz + 0.6), m['yellow'])
        for dx in (-1.2, 1.2):
            br.cyl(0.2, 0.12, (x0 + dx, y, RAIL_Z + 0.2), m['steel'], rot=(90, 0, 0), seg=16)
    br.box_mm((x0 - 0.8, RAIL_Y - 1.4, gz + 0.1), (x0 - 0.2, RAIL_Y - 0.5, gz + 0.7), m['steel'])  # panel
    br.finish(col)
    tz = gz + 0.96
    tr = pb.Part("WS_Crane_Trolley", pivot=(x0, yt, tz))
    tr.box_mm((x0 - 1.0, yt - 0.9, tz), (x0 + 1.0, yt + 0.9, tz + 0.25), m['yellow'])
    tr.cyl(0.3, 1.2, (x0, yt - 0.2, tz + 0.55), m['steel'], rot=(0, 90, 0), seg=24)   # drum
    tr.box_mm((x0 - 0.9, yt + 0.3, tz + 0.25), (x0 - 0.3, yt + 0.8, tz + 0.75), m['yellow'])  # motor
    tr.box_mm((x0 + 0.3, yt + 0.3, tz + 0.25), (x0 + 0.9, yt + 0.8, tz + 0.65), m['steel'])   # gearbox
    tr.finish(col)
    rope_top = tz
    ro = pb.Part("WS_Crane_Ropes", pivot=(x0, yt - 0.2, rope_top))
    for dx in (-0.12, 0.12):
        ro.cyl_between((x0 + dx, yt - 0.2, rope_top), (x0 + dx, yt - 0.2, hook_z + 0.45), 0.012, m['steel'], seg=6)
    ro.finish(col)
    hk = pb.Part("WS_Crane_Hook", pivot=(x0, yt - 0.2, hook_z + 0.45))
    hk.box_mm((x0 - 0.25, yt - 0.35, hook_z), (x0 + 0.25, yt - 0.05, hook_z + 0.45), m['yellow'])
    hk.cyl(0.04, 0.2, (x0, yt - 0.2, hook_z - 0.1), m['bright'], seg=10)
    hk.cyl(0.15, 0.07, (x0, yt - 0.2, hook_z - 0.32), m['bright'], rot=(90, 0, 0), seg=16)
    hk.finish(col)


def machine_shop(col, m):
    lathe(col, "WS_Lathe1", F((-12.5, -6.0, 0)), 9.5, 1.9, 1.8, 1.0, 0.95, m)    # 1000 x 6000 class
    lathe(col, "WS_Lathe2", F((-21.0, -6.0, 0)), 3.63, 1.2, 1.52, 0.66, 0.85, m)  # 660 x 2000
    milling_machine(col, F((-19.0, 4.5, 0)), m)
    radial_drill(col, F((-13.5, 4.5, 0)), m)
    pedestal_drill(col, F((-9.0, 4.5, 0)), m)
    bandsaw(col, F((-5.5, 4.5, 0)), m)
    hydraulic_press(col, F((-1.0, 4.5, 0)), m)

    p = pb.Part("WS_MachineShop_Furniture")
    for x in (-22.0, -19.8, -17.6):
        wc.workbench(p, F((x, 8.25, 0)), 2.0, 0.75, 0.9, m['wood'], m['blue'], vice_m=m['steel'],
                     drawers_m=m['blue'])
    for x in (-11.0, -9.9, -8.8):
        wc.cabinet(p, F((x, 8.45, 0)), 1.0, 0.5, 1.95, m['blue'], m['bright'])
    wc.shelving(p, F((3.6, 7.9, 0)), 2.7, 1.0, 3.0, 4, m['orange'], load_m=m['machine2'])
    # bench grinder on pedestal
    g = F((-6.5, 7.6, 0))
    g.cyl(p, 0.12, 0.9, (0, 0, 0.45), m['machine'], seg=12)
    g.bmm(p, (-0.2, -0.2, 0), (0.2, 0.2, 0.03), m['machine'])
    g.cyl(p, 0.09, 0.3, (0, 0, 1.0), m['machine'], rot=(0, 90, 0), seg=16)
    for x in (-0.22, 0.22):
        g.cyl(p, 0.1, 0.04, (x, 0, 1.0), m['machine2'], rot=(0, 90, 0), seg=20)
    p.finish(col)


# ---------------------------------------------------------------------------
# Welding / fabrication bay
# ---------------------------------------------------------------------------

def welding_bay(col, m):
    p = pb.Part("WS_WeldBay_Static")
    booth_x = (9.0, 13.0, 17.0)
    for x in (7.0, 11.0, 15.0, 19.0):
        # side screens between and beside the booths (one per line, no overlapping faces)
        p.box_mm((x - 0.03, -HB_Y + 0.3, 0.0), (x + 0.03, -5.0, 2.0), m['machine2'])
    for i, cx in enumerate(booth_x):
        # curtain rail and a partly drawn curtain
        p.box_mm((cx - 2.0, -5.03, 2.05), (cx + 2.0, -4.97, 2.1), m['bright'])
        p.box_mm((cx - 2.0, -5.02, 0.15), (cx + 0.4, -4.98, 2.0), m['orange'])
        # welding table (slotted top) on legs
        f = F((cx, -7.0, 0))
        f.bmm(p, (-0.75, -0.5, 0.82), (0.75, 0.5, 0.86), m['steel'])
        for x in (-0.65, 0.65):
            for y in (-0.4, 0.4):
                f.bmm(p, (x - 0.03, y - 0.03, 0), (x + 0.03, y + 0.03, 0.82), m['steel'])
        # inverter welder on a trolley with a shielding gas bottle
        f = F((cx + 1.35, -8.25, 0))
        f.bmm(p, (-0.3, -0.25, 0.1), (0.3, 0.25, 0.15), m['steel'])
        f.bmm(p, (-0.28, -0.2, 0.15), (0.12, 0.2, 0.65), m['blue'])
        f.cyl(p, 0.11, 1.3, (0.2, 0.0, 0.8), m['green'], seg=16)
        for x in (-0.25, 0.25):
            f.cyl(p, 0.06, 0.03, (x, -0.26, 0.06), m['rubber'], rot=(90, 0, 0), seg=10)
        # extraction fan on the wall above the arm bracket
        p.box_mm((cx - 1.9, -HB_Y + 0.12, 2.9), (cx - 1.3, -HB_Y + 0.5, 3.4), m['white'])
        p.cyl_between((cx - 1.6, -HB_Y + 0.3, 3.4), (cx - 1.6, -HB_Y + 0.3, EAVES - 1.0), 0.1, m['bright'])
        fume_arm(col, f"WS_FumeArm_{i + 1}", (cx - 1.6, -HB_Y + 0.3, 2.6), m)
    # gas cylinder cage near the south door
    cage = F((22.5, -4.2, 0))
    cage.bmm(p, (-1.3, -0.6, 0), (1.3, 0.6, 0.05), m['steel'])
    cage.bmm(p, (-1.3, -0.6, 2.0), (1.3, 0.6, 2.05), m['steel'])
    for x in (-1.3, -0.65, 0.0, 0.65, 1.3):
        for y in (-0.6, 0.6):
            cage.cyl_between(p, (x, y, 0), (x, y, 2.0), 0.015, m['yellow'], seg=6)
    for y in (-0.6, 0.6):
        for z in (0.5, 1.0, 1.5):
            cage.cyl_between(p, (-1.3, y, z), (1.3, y, z), 0.01, m['yellow'], seg=6)
    for i in range(8):
        x = -1.1 + i * 0.31
        cage.cyl(p, 0.115, 1.5, (x, 0.25 if i % 2 else -0.15, 0.8), m['green'] if i < 4 else m['red'], seg=16)
        cage.sphere(p, 0.115, (x, 0.25 if i % 2 else -0.15, 1.55), m['green'] if i < 4 else m['red'], seg=12)
    # cast welding platen and a vertical plate rack
    pl = F((21.0, 4.5, 0))
    pl.bmm(p, (-1.5, -0.75, 0.65), (1.5, 0.75, 0.85), m['steel'])
    for x in (-1.3, 1.3):
        pl.bmm(p, (x - 0.1, -0.6, 0), (x + 0.1, 0.6, 0.65), m['steel'])
    pr = F((19.0, 7.7, 0))
    pr.bmm(p, (-2.5, -0.6, 0), (2.5, 0.6, 0.15), m['steel'])
    for i in range(6):
        x = -2.5 + i
        for y in (-0.35, 0.0, 0.35):
            pr.bmm(p, (x - 0.04, y - 0.04, 0.15), (x + 0.04, y + 0.04, 2.0), m['orange'])
    for k, y in enumerate((-0.18, 0.17)):
        pr.bmm(p, (-2.4, y - 0.01, 0.15), (0.6 + k, y + 0.01, 1.4 + 0.2 * k), m['bright'])
    p.finish(col)
    plasma_table(col, F((12.0, 4.5, 0)), m)


def fume_arm(col, name, bracket, m):
    """Articulated fume extraction arm. Pivot at the wall bracket, swings about Z."""
    x, y, z = bracket
    a = pb.Part(name, pivot=bracket)
    a.cyl(0.08, 0.3, (x, y, z), m['bright'], seg=12)
    mid = (x + 0.3, y + 1.2, z + 0.1)
    hood = (x + 0.9, y + 1.9, 1.5)
    a.cyl_between((x, y, z), mid, 0.08, m['white'], seg=12)
    a.cyl_between(mid, hood, 0.08, m['white'], seg=12)
    a.sphere(0.1, mid, m['steel'], seg=12)
    a.cyl(0.18, 0.25, (hood[0], hood[1], hood[2] - 0.1), m['yellow'], seg=20, r2=0.08)
    a.finish(col)


def plasma_table(col, fr, m):
    """CNC plasma cutting table. _Gantry slides along local X."""
    p = pb.Part("WS_Plasma_Table", pivot=fr.o)
    fr.bmm(p, (-3.25, -1.25, 0), (3.25, 1.25, 0.7), m['steel'])                  # water table
    for i in range(16):
        x = -3.1 + i * 0.41
        fr.bmm(p, (x - 0.004, -1.2, 0.7), (x + 0.004, 1.2, 0.75), m['bright'])  # slats
    for y in (-1.45, 1.45):
        fr.bmm(p, (-3.4, y - 0.1, 0), (3.4, y + 0.1, 0.85), m['machine2'])        # rail beds
        fr.bmm(p, (-3.4, y - 0.03, 0.85), (3.4, y + 0.03, 0.9), m['bright'])
    fr.bmm(p, (3.6, -2.2, 0), (4.3, -1.6, 1.1), m['machine2'])                    # console
    fr.bmm(p, (3.62, -2.21, 0.75), (4.28, -2.2, 1.05), m['screen'])
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (-1.0, 0, 0.9)
    g = pb.Part("WS_Plasma_Gantry", pivot=fr.w(piv))
    for y in (-1.45, 1.45):
        fr.bmm(g, (-1.25, y - 0.15, 0.9), (-0.75, y + 0.15, 1.35), m['yellow'])
    fr.bmm(g, (-1.1, -1.6, 1.35), (-0.9, 1.6, 1.6), m['yellow'])
    fr.bmm(g, (-1.25, -0.2, 1.05), (-1.08, 0.1, 1.65), m['steel'])                # torch carriage
    fr.cyl(g, 0.025, 0.25, (-1.17, -0.05, 0.95), m['bright'], seg=10)
    g.finish(col, x_toward=fr.xdir(piv))


# ---------------------------------------------------------------------------
# Lean-to rooms
# ---------------------------------------------------------------------------

def electrical_shop(col, m):
    p = pb.Part("WS_Electrical_Static")
    # motor test bench with a motor and the test panel
    f = F((-20.5, 11.6, 0))
    f.bmm(p, (-1.5, -0.75, 0.62), (1.5, 0.75, 0.7), m['steel'])
    for x in (-1.4, 1.4):
        for y in (-0.65, 0.65):
            f.bmm(p, (x - 0.05, y - 0.05, 0), (x + 0.05, y + 0.05, 0.62), m['steel'])
    f.cyl(p, 0.35, 0.8, (0, 0, 1.08), m['blue'], rot=(0, 90, 0), seg=24)
    f.bmm(p, (-0.3, -0.3, 0.7), (0.3, 0.3, 0.78), m['blue'])
    f.bmm(p, (-0.15, -0.15, 1.43), (0.15, 0.15, 1.58), m['blue'])                  # terminal box
    f.cyl(p, 0.05, 0.25, (0.52, 0, 1.08), m['bright'], rot=(0, 90, 0), seg=12)   # shaft
    t = F((-23.4, 11.6, 0), 90)
    wc.cabinet(p, t, 1.2, 0.5, 2.0, m['machine2'], m['bright'], doors=1)
    t.bmm(p, (-0.4, -0.26, 1.3), (0.4, -0.25, 1.7), m['screen'])
    # varnish dip tank and baking oven
    f = F((-19.0, 15.6, 0))
    f.cyl(p, 0.6, 1.0, (0, 0, 0.5), m['machine2'], seg=24)
    f.cyl(p, 0.62, 0.05, (0, 0, 1.02), m['steel'], seg=24)
    oven(col, F((-22.4, 15.4, 0), 0), m)
    # coil winding machine
    f = F((-11.0, 12.0, 0))
    f.bmm(p, (-0.75, -0.35, 0), (0.75, 0.35, 0.85), m['machine2'])
    f.bmm(p, (-0.7, -0.2, 0.85), (-0.4, 0.2, 1.2), m['machine'])
    f.cyl(p, 0.03, 1.1, (0.15, 0, 1.03), m['bright'], rot=(0, 90, 0), seg=10)
    f.cyl(p, 0.25, 0.25, (0.2, 0, 1.03), m['orange'], rot=(0, 90, 0), seg=24)   # coil former
    # benches along the partition, shelving on the west end wall
    for y in (11.0, 13.4):
        wc.workbench(p, F((-6.55, y, 0), -90), 2.2, 0.75, 0.9, m['epoxy'], m['blue'], drawers_m=m['blue'])
    wc.shelving(p, F((-23.5, 14.0, 0), 90), 2.0, 0.6, 2.4, 5, m['blue'], load_m=m['machine2'], seed=2)
    p.finish(col)


def oven(col, fr, m):
    """Motor-winding baking oven, door on local -Y with hinge on the left (-X) edge."""
    p = pb.Part("WS_Oven_Body", pivot=fr.o)
    fr.bmm(p, (-1.0, -0.9, 0), (1.0, 1.0, 2.2), m['white'])
    fr.bmm(p, (0.6, 1.0, 1.6), (0.9, 1.3, 2.4), m['bright'])                       # fan box
    fr.cyl(p, 0.1, 0.6, (0.75, 1.15, 2.6), m['bright'], seg=12)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (-0.95, -0.95, 0.05)
    d = pb.Part("WS_Oven_Door", pivot=fr.w(hinge))
    fr.bmm(d, (-0.95, -1.0, 0.05), (0.95, -0.9, 2.15), m['white'])
    fr.bmm(d, (0.75, -1.08, 0.9), (0.8, -1.0, 1.4), m['bright'])
    d.finish(col, x_toward=fr.xdir(hinge))


def instrument_shop(col, m):
    p = pb.Part("WS_Instrument_Static")
    for x in (-4.6, -2.4, 2.4, 4.6, 6.8):
        f = F((x, 16.4, 0))
        wc.workbench(p, f, 2.1, 0.75, 0.9, m['epoxy'], m['lab'])
        f.bmm(p, (-1.05, 0.25, 0.9), (1.05, 0.37, 1.6), m['lab'])                  # riser
        f.bmm(p, (-1.05, 0.05, 1.6), (1.05, 0.37, 1.63), m['lab'])                 # shelf
        f.bmm(p, (-0.3, 0.1, 0.95), (0.25, 0.14, 1.3), m['screen'])                # monitor
        f.bmm(p, (0.4, -0.05, 0.9), (0.8, 0.25, 1.05), m['machine2'])              # calibrator box
    # calibration bench: deadweight tester, gauge stand
    f = F((3.5, 12.5, 0))
    wc.workbench(p, f, 2.4, 0.9, 0.9, m['epoxy'], m['lab'], drawers_m=m['lab'])
    f.bmm(p, (-0.9, -0.3, 0.9), (-0.3, 0.3, 1.0), m['machine'])
    f.cyl(p, 0.03, 0.15, (-0.6, 0.0, 1.07), m['bright'], seg=12)
    for k in range(5):
        f.cyl(p, 0.11, 0.03, (-0.6, 0.0, 1.16 + k * 0.032), m['bright'], seg=24)
    f.cyl_between(p, (-0.3, 0.0, 0.98), (0.3, 0.0, 0.98), 0.006, m['bright'], seg=6)
    f.cyl_between(p, (0.3, 0.0, 0.98), (0.3, 0.0, 1.25), 0.01, m['bright'], seg=6)
    f.cyl(p, 0.08, 0.04, (0.3, -0.02, 1.3), m['white'], rot=(90, 0, 0), seg=20)
    # glazed instrument cabinets on the east partition and a test rack on the west partition
    for y in (10.5, 11.6):
        t = F((7.6, y, 0), -90)
        wc.cabinet(p, t, 1.0, 0.45, 2.0, m['lab'], m['bright'])
        t.bmm(p, (-0.45, -0.24, 1.0), (0.45, -0.23, 1.9), m['glass'])
    wc.shelving(p, F((-5.6, 13.0, 0), 90), 2.4, 0.6, 2.2, 5, m['lab'], load_m=m['machine'], seed=4)
    p.finish(col)


def tool_store(col, m):
    p = pb.Part("WS_ToolStore_Static")
    wc.workbench(p, F((10.0, 9.55, 0)), 2.6, 0.7, 0.95, m['wood'], m['blue'])
    for i, x in enumerate((15.0, 17.5, 20.0, 22.5)):
        wc.shelving(p, F((x, 13.0, 0), 90), 5.0, 0.9, 2.5, 5, m['blue'], load_m=m['orange'] if i % 2 else m['machine2'],
                    seed=i)
    wc.cabinet(p, F((9.5, 16.5, 0)), 1.8, 0.6, 2.0, m['blue'], m['bright'])
    p.finish(col)


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

def write_readme(col):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_Workshops

Plant maintenance workshop: crane-served high bay (machine shop + welding/fabrication) with a
lean-to holding the electrical shop, instrument shop and tool store. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/WorkshopsSafetyLab/build_workshops.py`; re-run it to rebuild.

The layout is my own design. I found no public drawings of a smelter maintenance workshop, so the
building, room sizes and machine placement are estimates. Machine sizes are taken from real
machine classes where noted below.

## Placement and footprint

- Origin: finished floor level (z = 0) at the centre of the high bay. +X east, +Y north.
- Footprint: x -24 … +24 m, y -9 … +17 m (48 × 26 m). Slab extends 0.3 m beyond the walls.
- High bay: 48 × 18 m (y -9 … +9), eaves 9.0 m, ridge {RIDGE:.2f} m, 6° roof.
- Lean-to: 48 × 8 m (y +9 … +17), roof falls from 5.8 m to 5.0 m.
- Rooms: machine shop x -24 … 6, welding/fabrication x 6 … 24 (both in the high bay, no wall
  between them; the three welding booths are screened). Lean-to: electrical shop x -24 … -6,
  instrument shop x -6 … 8, tool store x 8 … 24.
- Central aisle y -2.6 … +2.6 is kept clear, marked by yellow floor lines, from the west door to
  the east door.

### Doors

| Door | Centre (x, y) | Size W × H | Part |
|---|---|---|---|
| East roller shutter (main vehicle door) | (24.0, 0.0) | 6.0 × 6.0 | WS_Shutter_East |
| West roller shutter | (-24.0, 0.0) | 5.0 × 5.0 | WS_Shutter_West |
| South roller shutter, machine shop | (-3.0, -9.0) | 5.0 × 5.0 | WS_Shutter_South |
| Electrical shop, from high bay | (-15.0, 9.0) | 3.0 × 3.5 | WS_Shutter_ElecInner |
| Electrical shop, outside (drive-through for motors) | (-15.0, 17.0) | 3.0 × 3.5 | WS_Shutter_ElecOuter |
| Tool store serving hatch (sill 0.95 m) | (10.0, 9.0) | 2.0 × 1.3 | WS_Shutter_StoreHatch |
| Personnel door, machine shop south | (-15.0, -9.0) | 1.0 × 2.1 | WS_Door_South_Machine |
| Personnel door, welding bay south | (20.0, -9.0) | 1.0 × 2.1 | WS_Door_South_Weld |
| Instrument shop, from high bay | (-2.0, 9.0) | 1.0 × 2.1 | WS_Door_Instrument_Inner |
| Tool store, from high bay | (13.0, 9.0) | 1.0 × 2.1 | WS_Door_Store_Inner |
| Electrical shop, outside | (-9.0, 17.0) | 1.0 × 2.1 | WS_Door_Elec_Outer |
| Instrument shop, outside | (0.0, 17.0) | 1.0 × 2.1 | WS_Door_Instrument_Outer |
| Tool store, outside | (20.0, 17.0) | 1.0 × 2.1 | WS_Door_Store_Outer |

## Moving parts

| Part | Motion |
|---|---|
| WS_Shutter_* | Pivot at the top of the curtain under the coil box. Roll up = scale local Z from 1 to about 0.05. |
| WS_Door_* | Pivot on the hinge edge at floor level, leaf along local +X. Open = rotate about local Z, ±90° (pick the sign for the swing side you want). |
| WS_Crane_Bridge | Travels along X on the rails at z = 7.0 (y = ±8.4). Limits about x = -22 … +22. |
| WS_Crane_Trolley | Attach to the bridge. Travels along Y, about ±7 m. |
| WS_Crane_Hook | Attach to the trolley. Moves along Z (hook built at z = 4.0; floor clearance down to about 0.6 m). |
| WS_Crane_Ropes | Attach to the trolley. Pivot at the drum; scale local Z = (pivot z - hook block top z) / {RAIL_Z + 1.21 - 4.45:.2f} to keep the ropes reaching the hook. |
| WS_Lathe1/2_Chuck | Spins about local X (spindle axis). |
| WS_Lathe1/2_Carriage, _Tailstock | Slide along local X (bed axis). |
| WS_Mill_Table | Slides along local X, about ±0.35 m. |
| WS_RadialDrill_Arm | Swings about local Z at the column axis (about ±150°), rises along Z up to about +0.4 m. |
| WS_Bandsaw_Bow | Hinge along local X at the rear; raise = rotate about local X by up to about -40°. |
| WS_Press_Ram | Slides along local Z, down to about -0.4 m. |
| WS_FumeArm_1/2/3 | Swing about Z at the wall bracket (about ±80°). |
| WS_Plasma_Gantry | Slides along local X, about -2.0 … +4.5 m from its built position. |
| WS_Oven_Door | Hinge on the left edge, rotate about local Z by up to -100°. |

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

## Unreal import

Combine Meshes off. With Transform Vertex to Absolute on, every part keeps the building origin as
its pivot, which suits the static parts. For the moving parts, import with it off and place each
part at the pivot above. The Blender Y axis appears as -Y in Unreal with the default FBX settings,
so check rotation signs after import. WS_Roof is a separate part so it can be hidden for interior
views; it has no underside lining.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Large lathe (WS_Lathe1), 1000 mm swing × 6 m between centres class | 9.5 × 1.9 × 1.8 m | Estimated (scaled up from the 660 × 2000 class) |
| Medium lathe (WS_Lathe2), 660 mm swing × 2000 mm between centres | 3.63 × 1.20 × 1.52 m | Sourced: Bernardo Titan 660 × 2000 and Cormak 660 × 2000 listings (3630 × 1200 × 1520-1700 mm, 2.9-3.8 t) |
| Turret milling machine | ~1.5 × 1.7 × 2.2 m | Estimated |
| Radial arm drill (1.6 m arm) | base 2.6 × 1.1 m, 3.2 m tall | Estimated |
| Horizontal bandsaw, pedestal drill, bench grinder | | Estimated |
| 100 t H-frame press | 1.7 × 1.0 × 2.6 m | Estimated |
| 10 t double-girder crane, 16.8 m span, rail at 7.0 m | | Estimated |
| Welding booths | 4 × 3.7 m, 2.0 m screens, curtain on the aisle side | Own design |
| CNC plasma table | 6.5 × 2.5 m water table | Estimated (common 6 × 2 m cutting area) |
| Benches 0.9 m high, shelving, cabinets, gas cylinders Ø0.23 × 1.5 m | | Estimated |
| Building, room sizes, door positions | | Own design |

Sources: Bernardo Titan 660 × 2000 (https://www.machineseeker.com/bernardo-titan+660+-+2000/i-19924365),
Cormak 660 × 2000 (https://www.cormak.pl/gb/product/1429-660x2000-industrial-lathe.html).

## Files

- SM_Workshops.blend / .fbx (the REF collection is not exported)
- Preview_Exterior.png, Preview_Cutaway.png, Preview_MachineShop.png, Preview_WeldBay.png,
  Preview_LeanTo.png (all but the exterior are rendered with WS_Roof hidden)
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    m = wc.palette()
    build_shell(col, m)
    crane(col, m)
    machine_shop(col, m)
    welding_bay(col, m)
    electrical_shop(col, m)
    instrument_shop(col, m)
    tool_store(col, m)
    pb.ref_human(ref, (-2.0, -1.5, 0.0))
    pb.ref_ground(ref, (-60, -45, 60, 50), [(-24.3, -9.3, 24.3, 17.3)], z=-0.01)

    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render(samples=32)
    roof = bpy.data.objects["WS_Roof"]
    pb.render_view(os.path.join(OUT, "Preview_Exterior.png"), (44, -46, 24), (0, 3, 4))
    roof.hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Cutaway.png"), (-36, -40, 36), (0, 3, 0))
    pb.render_view(os.path.join(OUT, "Preview_MachineShop.png"), (-1, 1.0, 7.5), (-15, -3, 0.5), lens=24)
    pb.render_view(os.path.join(OUT, "Preview_WeldBay.png"), (5, 3, 7), (15, -5, 0.5), lens=24)
    pb.render_view(os.path.join(OUT, "Preview_LeanTo.png"), (0, 4, 16), (-3, 13.5, 0), lens=22)
    roof.hide_render = False


main()
