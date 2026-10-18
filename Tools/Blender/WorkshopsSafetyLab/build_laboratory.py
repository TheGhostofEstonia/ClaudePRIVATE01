"""
build_laboratory.py - SM_Laboratory: plant assay / control laboratory with sample preparation,
fire assay, instrument room (WDXRF, spark OES, ICP-OES) and wet chemistry.

Run:  blender -b --factory-startup --python Tools/Blender/WorkshopsSafetyLab/build_laboratory.py
      (add -- --no-render to skip the previews)

Layout is my own design (no real lab drawings used). Single-storey block building,
36 x 18 m, 4.5 m ceiling, flat roof. Origin = finished floor level at the centre of the
building. +X east, +Y north.
"""
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import wsl_common as wc  # noqa: E402
from wsl_common import F  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Meshes", "Laboratory")
NAME = "SM_Laboratory"

LX, LY, LH = 18.0, 9.0, 4.5      # half length, half width, ceiling height
TW = 0.25                        # external wall thickness
IW = 0.15                        # internal wall thickness
INNER_Y = LY - TW / 2            # wall centre lines
INNER_X = LX - TW / 2

# Instrument sizes (W x D x H, metres) - see README for sources
XRF = (1.31, 0.89, 1.47)         # WDXRF, tube-above floor unit (Rigaku ZSX Primus IV class)
OES = (0.79, 0.625, 1.35)        # floor-standing spark OES (SPECTROMAXx class listing)
ICP = (0.625, 0.74, 0.887)       # benchtop ICP-OES (Agilent 5900)
FUSION_FURNACE = (1.45, 1.22, 2.16)   # floor fire-assay furnace (MSA listing)
CUPEL_FURNACE = (0.485, 0.75, 0.82)   # benchtop cupellation furnace (Delmer D-C)


# ---------------------------------------------------------------------------
# Building shell
# ---------------------------------------------------------------------------

def build_shell(col, m):
    fl = pb.Part("LB_Floor")
    fl.box_mm((-LX - 0.2, -LY - 0.2, -0.3), (LX + 0.2, LY + 0.2, 0.0), m['concrete'])
    # epoxy floor finish in the instrument and wet chemistry rooms
    fl.box_mm((6.0, -LY + TW / 2, 0.0), (LX - TW / 2, LY - TW / 2, 0.004), m['machine2'])
    fl.finish(col)

    w = pb.Part("LB_Walls")
    win = lambda u0, u1: (u0, u1, 1.1, 2.4)
    # South and north walls butt against the end walls so no faces overlap at the corners.
    # ux converts a plan x to the distance along these walls.
    ux = lambda x: x + LX - TW
    # south wall: fire assay door x=0, main double door x=12, windows
    wc.wall(w, (-LX + TW, -INNER_Y), (LX - TW, -INNER_Y), LH, TW, m['white'],
            openings=[(ux(-0.5), ux(0.5), 0, 2.1), (ux(11.0), ux(13.0), 0, 2.4)],
            windows=[win(ux(-16.0), ux(-13.0)), win(ux(-10.0), ux(-7.0)), win(ux(7.0), ux(10.0)),
                     win(ux(14.5), ux(17.0))], glass=m['glass'])
    # north wall: prep door x=-12, wet chem door x=12, window in the prep room
    wc.wall(w, (-LX + TW, INNER_Y), (LX - TW, INNER_Y), LH, TW, m['white'],
            openings=[(ux(-12.5), ux(-11.5), 0, 2.1), (ux(11.5), ux(12.5), 0, 2.1)],
            windows=[win(ux(-9.5), ux(-7.0))], glass=m['glass'])
    # west wall (u = y + 9): sample delivery roller shutter 4 x 4 centred y=0
    wc.wall(w, (-INNER_X, -LY), (-INNER_X, LY), LH, TW, m['white'], openings=[(7.0, 11.0, 0, 4.0)])
    # east wall: windows in the instrument and wet chemistry rooms
    wc.wall(w, (INNER_X, -LY), (INNER_X, LY), LH, TW, m['white'],
            windows=[win(2.0, 5.0), win(12.0, 13.5)], glass=m['glass'])
    # internal walls end on the external wall centre lines; uy converts a plan y to wall distance
    uy = lambda y: y + INNER_Y
    wc.wall(w, (-6.0, -INNER_Y), (-6.0, INNER_Y), LH, IW, m['white'], openings=[(uy(4.4), uy(6.4), 0, 2.4)])
    wc.wall(w, (6.0, -INNER_Y), (6.0, INNER_Y), LH, IW, m['white'],
            openings=[(uy(-5.4), uy(-4.4), 0, 2.1), (uy(4.6), uy(5.6), 0, 2.1)])
    wc.wall(w, (6.0, 0.0), (INNER_X, 0.0), LH, IW, m['white'], openings=[(5.5, 6.5, 0, 2.1)])
    w.finish(col)

    # balance room: glazed partitions in the north-east corner of the fire assay room
    g = pb.Part("LB_BalanceRoom")
    wc.wall(g, (2.0, 5.0), (2.0, INNER_Y), 3.0, 0.08, m['lab'], windows=[(0.2, 3.7, 0.9, 2.8)],
            glass=m['glass'])
    wc.wall(g, (2.0, 5.0), (6.0, 5.0), 3.0, 0.08, m['lab'], openings=[(0.3, 1.2, 0, 2.1)],
            windows=[(1.4, 3.8, 0.9, 2.8)], glass=m['glass'])
    g.box_mm((2.0, 5.0, 3.0), (6.0, INNER_Y, 3.05), m['lab'])                     # ceiling
    g.finish(col)

    r = pb.Part("LB_Roof")
    r.box_mm((-LX, -LY, LH), (LX, LY, LH + 0.25), m['dado'])
    r.box_mm((-LX, LY - 0.15, LH + 0.25), (LX, LY, LH + 0.7), m['dado'])
    r.box_mm((-LX, -LY, LH + 0.25), (LX, -LY + 0.15, LH + 0.7), m['dado'])
    r.box_mm((LX - 0.15, -LY, LH + 0.25), (LX, LY, LH + 0.7), m['dado'])
    r.box_mm((-LX, -LY, LH + 0.25), (-LX + 0.15, LY, LH + 0.7), m['dado'])
    r.finish(col)

    # roof plant: fire assay stacks, fume hood fans, ICP exhaust fan
    rp = pb.Part("LB_RoofPlant")
    for x in (-3.8, -0.9):
        rp.cyl(0.35, 4.0, (x, 7.6, LH + 2.25), m['bright'], seg=24)
        rp.cyl(0.42, 0.1, (x, 7.6, LH + 4.3), m['steel'], seg=24)
    for x in (8.2, 10.1, 14.0, 16.0):
        rp.box((0.8, 0.8, 0.7), (x, 8.0, LH + 0.6), m['lab'])
        rp.cyl(0.15, 1.2, (x, 8.0, LH + 1.55), m['bright'], seg=16)
    rp.box((0.7, 0.7, 0.6), (17.5, -3.7, LH + 0.55), m['lab'])
    rp.finish(col)

    lights = pb.Part("LB_Lights")
    for x in range(-15, 18, 3):
        for y in (-6.0, -2.0, 2.0, 6.0):
            lights.box((1.2, 0.3, 0.05), (x, y, LH - 0.03), m['lamp'])
    lights.finish(col)

    # doors
    rs = pb.Part("LB_DoorFrames")
    wc.roller_shutter("LB_Shutter_West", col, rs, (-LX - 0.01, 0.0, 0), 4.0, 4.0, -90, m['clad'], m['steel'])
    rs.finish(col)
    # (name, hinge point, yaw, leaf width, leaf height)
    doors = [("LB_Door_South_FireAssay", (-0.5, -INNER_Y, 0), 0, 1.0, 2.1),
             ("LB_Door_Main_L", (11.0, -INNER_Y, 0), 0, 1.0, 2.4),
             ("LB_Door_Main_R", (13.0, -INNER_Y, 0), 180, 1.0, 2.4),
             ("LB_Door_North_Prep", (-12.5, INNER_Y, 0), 0, 1.0, 2.1),
             ("LB_Door_North_WetChem", (11.5, INNER_Y, 0), 0, 1.0, 2.1),
             ("LB_Door_Prep_FireAssay_L", (-6.0, 4.4, 0), 90, 1.0, 2.4),
             ("LB_Door_Prep_FireAssay_R", (-6.0, 6.4, 0), -90, 1.0, 2.4),
             ("LB_Door_FireAssay_Instrument", (6.0, -5.4, 0), 90, 1.0, 2.1),
             ("LB_Door_FireAssay_WetChem", (6.0, 4.6, 0), 90, 1.0, 2.1),
             ("LB_Door_Instrument_WetChem", (11.5, 0.0, 0), 0, 1.0, 2.1),
             ("LB_Door_BalanceRoom", (2.3, 5.0, 0), 0, 0.9, 2.1)]
    for nm, hinge, yaw, wd, ht in doors:
        wc.door_leaf(nm, col, hinge, wd, ht, yaw, m['white'], m['bright'], glazed=m['glass'])


# ---------------------------------------------------------------------------
# Sample preparation
# ---------------------------------------------------------------------------

def drying_oven(col, fr, name, m):
    """Large sample drying oven. Door hinged on the left (-X) edge, front on local -Y."""
    p = pb.Part(name + "_Body", pivot=fr.o)
    fr.bmm(p, (-0.75, -0.5, 0), (0.75, 0.5, 2.0), m['white'])
    fr.bmm(p, (0.45, -0.52, 1.5), (0.7, -0.5, 1.85), m['machine2'])              # controller
    fr.bmm(p, (0.5, -0.53, 1.65), (0.65, -0.52, 1.75), m['screen'])
    fr.cyl(p, 0.08, 0.4, (0.4, 0.2, 2.2), m['bright'], seg=12)                   # vent
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (-0.72, -0.52, 0.05)
    d = pb.Part(name + "_Door", pivot=fr.w(hinge))
    fr.bmm(d, (-0.72, -0.57, 0.05), (0.4, -0.52, 1.95), m['white'])
    fr.bmm(d, (0.3, -0.62, 0.8), (0.35, -0.57, 1.3), m['bright'])
    d.finish(col, x_toward=fr.xdir(hinge))


def pulverizer(col, fr, name, m):
    """Ring-mill pulveriser in a sound-proof cabinet. Lid hinged at the back (rotate about local X)."""
    p = pb.Part(name + "_Body", pivot=fr.o)
    fr.bmm(p, (-0.4, -0.45, 0), (0.4, 0.45, 1.0), m['machine'])
    fr.bmm(p, (-0.3, -0.46, 0.75), (0.1, -0.45, 0.9), m['machine2'])
    fr.cyl(p, 0.03, 0.02, (0.25, -0.46, 0.85), m['red'], rot=(90, 0, 0), seg=12)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (0, 0.45, 1.0)
    lid = pb.Part(name + "_Lid", pivot=fr.w(hinge))
    fr.bmm(lid, (-0.4, -0.45, 1.0), (0.4, 0.45, 1.25), m['machine'])
    fr.bmm(lid, (-0.15, -0.5, 1.12), (0.15, -0.45, 1.16), m['bright'])
    lid.finish(col, x_toward=fr.xdir(hinge))


def jaw_crusher(p, fr, m):
    """Laboratory jaw crusher on a stand with feed hopper and catch pan."""
    fr.bmm(p, (-0.45, -0.4, 0), (0.45, 0.4, 0.6), m['machine2'])                  # stand
    fr.bmm(p, (-0.35, -0.3, 0.6), (0.35, 0.3, 1.15), m['machine'])                # crusher body
    fr.cyl(p, 0.3, 0.08, (0.42, 0.0, 0.95), m['steel'], rot=(0, 90, 0), seg=24)  # flywheel
    fr.cyl(p, 0.3, 0.08, (-0.42, 0.0, 0.95), m['steel'], rot=(0, 90, 0), seg=24)
    fr.bmm(p, (-0.25, -0.25, 1.15), (0.25, 0.25, 1.4), m['steel'])                # hopper
    fr.bmm(p, (-0.2, -0.45, 0.4), (0.2, -0.05, 0.55), m['stainless'])             # catch pan
    fr.bmm(p, (-0.3, 0.4, 0.2), (0.3, 0.7, 0.55), m['blue'])                      # motor


def sample_prep(col, m):
    for i, x in enumerate((-16.2, -14.4)):
        drying_oven(col, F((x, -8.2, 0), 180), f"LB_DryOven{i + 1}", m)
    for i, x in enumerate((-13.0, -11.6)):
        pulverizer(col, F((x, 8.3, 0)), f"LB_Pulverizer{i + 1}", m)
    p = pb.Part("LB_Prep_Static")
    jaw_crusher(p, F((-15.6, 7.9, 0)), m)
    # dust extraction hoods over the crusher and pulverisers, duct along the north wall
    for x in (-15.6, -13.0, -11.6):
        p.cyl(0.35, 0.3, (x, 8.2, 2.0), m['lab'], seg=20, r2=0.12)
        p.cyl_between((x, 8.2, 2.15), (x, 8.2, 3.6), 0.12, m['bright'], seg=12)
    p.cyl_between((-16.2, 8.2, 3.6), (-11.0, 8.2, 3.6), 0.2, m['bright'], seg=16)
    p.cyl_between((-12.0, 8.2, 3.6), (-12.0, 8.2, LH), 0.2, m['bright'], seg=16)
    # sample receipt and splitting benches, pellet press, sample racks
    wc.workbench(p, F((-12.0, -4.0, 0)), 3.0, 0.9, 0.9, m['epoxy'], m['lab'], drawers_m=m['lab'])
    wc.workbench(p, F((-9.0, -8.4, 0), 180), 2.4, 0.75, 0.9, m['epoxy'], m['lab'])
    f = F((-9.0, -8.4, 0), 180)
    f.bmm(p, (-0.8, -0.2, 0.9), (-0.3, 0.2, 1.15), m['stainless'])                # riffle splitter
    f.cyl(p, 0.18, 0.35, (0.4, 0.0, 1.08), m['machine2'], seg=24)                 # rotary splitter
    f = F((-8.5, 4.0, 0))
    f.bmm(p, (-0.3, -0.3, 0), (0.3, 0.3, 0.75), m['machine2'])                   # pellet press stand
    f.bmm(p, (-0.22, -0.22, 0.75), (0.22, 0.22, 1.35), m['blue'])
    f.cyl(p, 0.06, 0.15, (0, 0, 1.05), m['bright'], seg=16)
    for y in (-6.0, -4.4, 4.4, 6.0):
        wc.shelving(p, F((-17.4, y, 0), 90), 1.5, 0.6, 2.2, 5, m['lab'], load_m=m['white'], seed=int(y))
    p.finish(col)


# ---------------------------------------------------------------------------
# Fire assay
# ---------------------------------------------------------------------------

def fusion_furnace(col, fr, name, m):
    """
    Floor-standing fire assay (fusion) furnace, front on local -Y. Vertical-lift door
    <name>_Door slides along local Z (closed = 0, open = +0.35 m).
    """
    W, D, H = FUSION_FURNACE
    p = pb.Part(name + "_Body", pivot=fr.o)
    fr.bmm(p, (-W / 2, -D / 2, 0), (W / 2, D / 2, 0.75), m['machine2'])         # base / controls
    fr.bmm(p, (-W / 2 + 0.05, -D / 2, 0.75), (W / 2 - 0.05, D / 2, H - 0.25), m['refract'])
    fr.bmm(p, (-W / 2, -D / 2, 0.75), (W / 2, D / 2 - 0.2, 0.8), m['steel'])
    for x in (-W / 2, W / 2 - 0.06):
        fr.bmm(p, (x, -D / 2, 0.75), (x + 0.06, D / 2, H - 0.25), m['steel'])  # side frame
    fr.bmm(p, (-W / 2, -D / 2, H - 0.25), (W / 2, D / 2, H), m['steel'])       # exhaust hood
    fr.cyl(p, 0.15, 0.2, (0, 0.1, H + 0.1), m['bright'], seg=16)
    fr.bmm(p, (-0.3, -D / 2 - 0.01, 0.95), (0.3, -D / 2 + 0.01, 1.25), m['hot'])  # glowing muffle mouth
    fr.bmm(p, (0.35, -D / 2 - 0.02, 0.3), (0.65, -D / 2, 0.6), m['screen'])
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    piv = (0, -D / 2 - 0.05, 0.9)
    d = pb.Part(name + "_Door", pivot=fr.w(piv))
    fr.bmm(d, (-0.4, -D / 2 - 0.08, 0.9), (0.4, -D / 2 - 0.02, 1.35), m['refract'])
    fr.bmm(d, (-0.42, -D / 2 - 0.1, 0.9), (0.42, -D / 2 - 0.08, 1.37), m['steel'])
    fr.bmm(d, (-0.15, -D / 2 - 0.16, 1.15), (0.15, -D / 2 - 0.1, 1.18), m['bright'])
    d.finish(col, x_toward=fr.xdir(piv))


def cupel_furnace(col, fr, name, m):
    """Benchtop cupellation furnace on a steel stand. Door drops forward about local X (bottom hinge)."""
    W, D, H = CUPEL_FURNACE
    z0 = 0.75
    p = pb.Part(name + "_Body", pivot=fr.o)
    fr.bmm(p, (-0.32, -0.42, 0), (0.32, 0.42, z0), m['steel'])
    fr.bmm(p, (-W / 2, -D / 2, z0), (W / 2, D / 2, z0 + H), m['machine2'])
    fr.bmm(p, (-W / 2 - 0.02, -D / 2, z0 + H), (W / 2 + 0.02, D / 2, z0 + H + 0.12), m['steel'])  # hood
    fr.cyl(p, 0.07, 0.25, (0, 0.1, z0 + H + 0.24), m['bright'], seg=12)
    fr.bmm(p, (-0.115, -D / 2 - 0.005, z0 + 0.3), (0.115, -D / 2 + 0.01, z0 + 0.4), m['hot'])
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (0, -D / 2 - 0.01, z0 + 0.25)
    d = pb.Part(name + "_Door", pivot=fr.w(hinge))
    fr.bmm(d, (-0.17, -D / 2 - 0.06, z0 + 0.25), (0.17, -D / 2 - 0.01, z0 + 0.47), m['steel'])
    fr.bmm(d, (-0.08, -D / 2 - 0.1, z0 + 0.43), (0.08, -D / 2 - 0.06, z0 + 0.45), m['bright'])
    d.finish(col, x_toward=fr.xdir(hinge))


def fire_assay(col, m):
    fusion_furnace(col, F((-4.6, 8.12, 0)), "LB_FusionFurnace1", m)
    fusion_furnace(col, F((-2.9, 8.12, 0)), "LB_FusionFurnace2", m)
    cupel_furnace(col, F((-1.45, 8.3, 0)), "LB_CupelFurnace1", m)
    cupel_furnace(col, F((-0.65, 8.3, 0)), "LB_CupelFurnace2", m)
    p = pb.Part("LB_FireAssay_Static")
    # canopy hood over the furnace line, ducts to the two roof stacks
    p.box_mm((-5.6, 6.6, 2.7), (0.0, INNER_Y - 0.12, 3.2), m['stainless'])
    for x in (-3.8, -0.9):
        p.cyl_between((x, 7.6, 3.2), (x, 7.6, LH), 0.3, m['bright'], seg=20)
    # flux mixing bench and crucible racks on the west wall
    wc.workbench(p, F((-5.5, -3.0, 0), 90), 2.4, 0.75, 0.9, m['steel'], m['steel'])
    f = F((-5.5, -3.0, 0), 90)
    for k in range(3):                                                            # flux bins
        f.cyl(p, 0.14, 0.4, (-0.8 + k * 0.4, 0.05, 1.1), m['white'], seg=16)
    wc.shelving(p, F((-5.6, 1.0, 0), 90), 1.8, 0.5, 2.0, 5, m['steel'], load_m=m['refract'], seed=3)
    # pouring table with cast-iron conical moulds
    f = F((-2.0, 3.6, 0))
    f.bmm(p, (-0.8, -0.45, 0.8), (0.8, 0.45, 0.85), m['steel'])
    for x in (-0.7, 0.7):
        for y in (-0.35, 0.35):
            f.bmm(p, (x - 0.03, y - 0.03, 0), (x + 0.03, y + 0.03, 0.8), m['steel'])
    for i in range(2):
        f.bmm(p, (-0.7, -0.38 + i * 0.4, 0.85), (0.7, -0.02 + i * 0.4, 0.95), m['steel'])
        for k in range(6):
            f.cyl(p, 0.04, 0.012, (-0.55 + k * 0.22, -0.2 + i * 0.4, 0.955), m['rubber'], seg=12)
    # button cleaning bench with anvil, parting fume hood on the south wall
    wc.workbench(p, F((1.5, -8.4, 0), 180), 2.0, 0.75, 0.9, m['steel'], m['steel'])
    p.box((0.2, 0.2, 0.15), (1.0, -8.4, 0.975), m['steel'])
    # balance room: two anti-vibration balance tables
    for x in (3.4, 5.0):
        f = F((x, 8.45, 0))
        f.bmm(p, (-0.6, -0.35, 0), (0.6, 0.35, 0.75), m['lab'])
        f.bmm(p, (-0.6, -0.35, 0.75), (0.6, 0.35, 0.8), m['dado'])
        f.bmm(p, (-0.15, -0.15, 0.8), (0.15, 0.15, 1.05), m['glass'])
        f.bmm(p, (-0.16, -0.16, 0.8), (0.16, 0.16, 0.84), m['white'])
    p.finish(col)
    hood("LB_Hood_Parting", col, F((3.8, -8.42, 0), 180), m)


def hood(name, col, fr, m):
    """1.8 m fume hood: static body part <name>_Body plus the sliding sash <name>_Sash."""
    body = pb.Part(name + "_Body")
    wc.fume_hood(name, col, body, fr, 1.8, m['white'], m['glass'], m['epoxy'], duct_to_z=LH,
                 duct_m=m['bright'])
    body.finish(col)


# ---------------------------------------------------------------------------
# Instrument room
# ---------------------------------------------------------------------------

def xrf(col, fr, m):
    """Floor-standing WDXRF spectrometer, front on local -Y. Sample loader lid hinged at the back."""
    W, D, H = XRF
    p = pb.Part("LB_XRF_Body", pivot=fr.o)
    fr.bmm(p, (-W / 2, -D / 2, 0), (W / 2, D / 2, H - 0.12), m['lab'])
    fr.bmm(p, (-W / 2, -D / 2, 0), (W / 2, D / 2, 0.08), m['machine2'])
    fr.bmm(p, (-W / 2 + 0.05, -D / 2 - 0.005, 0.15), (-0.05, -D / 2, 0.9), m['white'])   # service panels
    fr.bmm(p, (0.05, -D / 2 - 0.005, 0.15), (W / 2 - 0.05, -D / 2, 0.9), m['white'])
    fr.bmm(p, (W / 2 - 0.4, -D / 2 + 0.05, H - 0.12), (W / 2 - 0.05, D / 2 - 0.05, H), m['lab'])
    for k in range(8):                                                            # sample tray positions
        fr.cyl(p, 0.025, 0.02, (-W / 2 + 0.15 + k * 0.09, -D / 2 + 0.15, H - 0.11), m['bright'], seg=12)
    fr.bmm(p, (W / 2 - 0.35, -D / 2 - 0.006, H - 0.45), (W / 2 - 0.1, -D / 2, H - 0.3), m['screen'])
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (0.0, D / 2 - 0.05, H - 0.12)
    lid = pb.Part("LB_XRF_Lid", pivot=fr.w(hinge))
    fr.bmm(lid, (-W / 2 + 0.05, -D / 2 + 0.05, H - 0.12), (W / 2 - 0.45, D / 2 - 0.05, H - 0.04), m['lab'])
    fr.bmm(lid, (-0.3, -D / 2 + 0.06, H - 0.11), (0.2, -D / 2 + 0.4, H - 0.035), m['glass'])
    lid.finish(col, x_toward=fr.xdir(hinge))


def spark_oes(p, fr, m):
    """Floor-standing spark OES, front on local -Y; spark stand on the top-left."""
    W, D, H = OES
    fr.bmm(p, (-W / 2, -D / 2, 0), (W / 2, D / 2, H - 0.25), m['lab'])
    fr.bmm(p, (-W / 2, -D / 2, H - 0.25), (0.05, D / 2, H - 0.2), m['lab'])
    fr.bmm(p, (-W / 2 + 0.05, -D / 2 + 0.05, H - 0.2), (-0.05, D / 2 - 0.15, H), m['white'])  # spark stand
    fr.cyl(p, 0.05, 0.1, (-0.2, -0.05, H + 0.05), m['bright'], seg=16)          # sample clamp
    fr.cyl_between(p, (-0.2, -0.05, H + 0.1), (-0.2, 0.15, H + 0.25), 0.012, m['bright'], seg=8)
    fr.bmm(p, (0.1, -D / 2 - 0.006, 0.7), (W / 2 - 0.05, -D / 2, 0.95), m['screen'])
    fr.cyl(p, 0.1, 1.5, (W / 2 + 0.25, 0.1, 0.75), m['machine2'], seg=16)       # argon cylinder
    fr.cyl_between(p, (W / 2 + 0.25, 0.1, 1.55), (W / 2, 0.1, 0.9), 0.006, m['bright'], seg=6)


def icp_bench(p, fr, m):
    """Bench with ICP-OES, autosampler and PC; recirculating chiller under the bench end."""
    W, D, H = ICP
    wc.workbench(p, fr, 3.0, 0.9, 0.9, m['epoxy'], m['lab'])
    fr.bmm(p, (-0.3 - W / 2, -D / 2, 0.9), (-0.3 + W / 2, D / 2, 0.9 + H), m['lab'])
    fr.bmm(p, (-0.3 - W / 2 + 0.05, -D / 2 - 0.005, 0.95), (-0.3 + W / 2 - 0.05, -D / 2, 1.35), m['glass'])
    fr.cyl(p, 0.12, 0.3, (-0.3, 0.1, 0.9 + H + 0.15), m['bright'], seg=16)      # torch exhaust
    fr.cyl(p, 0.12, LH - 0.9 - H - 0.3, (-0.3, 0.1, (LH + 0.9 + H + 0.3) / 2), m['bright'], seg=16)
    fr.bmm(p, (-1.4, -0.35, 0.9), (-0.7, 0.25, 1.25), m['white'])                 # autosampler
    for k in range(5):
        for j in range(3):
            fr.cyl(p, 0.012, 0.1, (-1.32 + k * 0.13, -0.25 + j * 0.15, 1.3), m['glass'], seg=8)
    fr.bmm(p, (0.6, -0.1, 0.9), (1.15, 0.0, 1.25), m['screen'])                   # PC monitor
    fr.bmm(p, (0.65, -0.35, 0.9), (1.1, -0.2, 0.92), m['rubber'])
    fr.bmm(p, (0.8, -0.3, 0), (1.3, 0.35, 0.65), m['white'])                      # chiller


def instrument_room(col, m):
    xrf(col, F((8.8, -7.2, 0), 180), m)
    p = pb.Part("LB_Instrument_Static")
    spark_oes(p, F((16.3, -8.42, 0), 180), m)
    icp_bench(p, F((17.4, -4.0, 0), -90), m)
    # fusion bead machine and balance bench on the west wall, PC desk beside the XRF
    f = F((6.55, -1.6, 0), 90)
    wc.workbench(p, f, 2.0, 0.8, 0.9, m['epoxy'], m['lab'])
    f.bmm(p, (-0.6, -0.3, 0.9), (0.1, 0.3, 1.45), m['white'])                     # fusion machine
    f.bmm(p, (-0.5, -0.31, 1.1), (0.0, -0.3, 1.3), m['glass'])
    f.bmm(p, (0.4, -0.15, 0.9), (0.7, 0.15, 1.05), m['lab'])                      # balance
    f = F((10.8, -8.45, 0), 180)
    wc.workbench(p, f, 1.6, 0.7, 0.75, m['wood'], m['lab'])
    f.bmm(p, (-0.3, 0.1, 0.75), (0.3, 0.14, 1.1), m['screen'])
    p.finish(col)


# ---------------------------------------------------------------------------
# Wet chemistry
# ---------------------------------------------------------------------------

def wet_chem(col, m):
    for i, x in enumerate((8.2, 10.1, 14.0, 16.0)):
        hood(f"LB_Hood_Wet{i + 1}", col, F((x, 8.42, 0)), m)
    p = pb.Part("LB_WetChem_Static")
    # island bench with reagent shelf and two sinks
    f = F((12.0, 4.0, 0))
    f.bmm(p, (-2.4, -0.75, 0), (2.4, 0.75, 0.85), m['lab'])
    f.bmm(p, (-2.4, -0.75, 0.85), (2.4, 0.75, 0.9), m['epoxy'])
    f.bmm(p, (-2.3, -0.1, 0.9), (2.3, 0.1, 1.7), m['lab'])
    for z in (1.3, 1.7):
        f.bmm(p, (-2.3, -0.2, z - 0.02), (2.3, 0.2, z), m['lab'])
    for x in (-2.0, 2.0):
        f.bmm(p, (x - 0.25, -0.65, 0.86), (x + 0.25, -0.3, 0.91), m['stainless'])
        f.cyl_between(p, (x, -0.2, 0.9), (x, -0.2, 1.2), 0.012, m['bright'], seg=8)
        f.cyl_between(p, (x, -0.2, 1.2), (x, -0.4, 1.2), 0.012, m['bright'], seg=8)
    for k in range(10):                                                           # reagent bottles
        f.cyl(p, 0.04, 0.2, (-2.1 + k * 0.45, -0.12, 1.4), m['glass'], seg=12)
    wc.workbench(p, F((17.45, 3.5, 0), -90), 3.0, 0.75, 0.9, m['epoxy'], m['lab'], drawers_m=m['lab'])
    wc.cabinet(p, F((17.5, 1.0, 0), -90), 1.2, 0.5, 1.9, m['yellow'], m['bright'])  # flammables cabinet
    p.finish(col)


# ---------------------------------------------------------------------------
# Dust collector outside the preparation room
# ---------------------------------------------------------------------------

def dust_collector(col, m):
    p = pb.Part("LB_DustCollector")
    f = F((-12.0, 11.0, 0))
    f.bmm(p, (-0.9, -0.9, 0), (0.9, 0.9, 0.2), m['dado'])
    for x in (-0.7, 0.7):
        for y in (-0.7, 0.7):
            f.bmm(p, (x - 0.05, y - 0.05, 0.2), (x + 0.05, y + 0.05, 1.5), m['steel'])
    f.bmm(p, (-0.75, -0.75, 2.2), (0.75, 0.75, 4.3), m['lab'])                     # bag housing
    f.cyl(p, 0.75, 0.7, (0, 0, 1.85), m['lab'], seg=4, r2=0.15)                     # hopper (square)
    f.cyl(p, 0.12, 0.3, (0, 0, 1.35), m['steel'], seg=12)                          # rotary valve
    f.bmm(p, (0.75, -0.3, 3.0), (1.3, 0.3, 3.6), m['blue'])                         # fan
    f.cyl_between(p, (0, -0.75, 3.6), (0, -2.2, 3.6), 0.2, m['bright'], seg=16)    # duct to the wall
    f.cyl(p, 0.15, 1.2, (1.0, 0, 4.2), m['bright'], seg=12)                        # clean air stack
    p.finish(col)


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

def write_readme(col):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_Laboratory

Plant assay and control laboratory: sample preparation, fire assay with balance room, instrument
room (WDXRF, spark OES, ICP-OES) and wet chemistry. Built in Blender 5.2.2 LTS (headless, cloud)
with `Tools/Blender/WorkshopsSafetyLab/build_laboratory.py`; re-run it to rebuild.

The building and room layout are my own design; I found no public drawings of a smelter lab.
Instrument sizes come from manufacturer pages or listings where noted below.

## Placement and footprint

- Origin: finished floor level (z = 0) at the centre of the building. +X east, +Y north.
- Footprint: x -18 … +18 m, y -9 … +9 m (36 × 18 m), walls 0.25 m, 4.5 m ceiling, flat roof
  with a 0.45 m parapet. Roof stacks reach z = {LH + 4.35:.1f} m.
- The dust collector stands outside the north wall at (-12, 11), so the overall footprint is
  y -9 … +12 m.
- Rooms: sample preparation x -18 … -6; fire assay x -6 … +6 with a glazed balance room at
  x 2 … 6, y 5 … 9; instrument room x 6 … 18, y -9 … 0; wet chemistry x 6 … 18, y 0 … 9.

### Doors

| Door | Centre (x, y) | Size W × H | Part |
|---|---|---|---|
| Sample delivery roller shutter (west) | (-18.0, 0.0) | 4.0 × 4.0 | LB_Shutter_West |
| Main entrance, double (south) | (12.0, -9.0) | 2.0 × 2.4 | LB_Door_Main_L / _R |
| Fire assay (south) | (0.0, -9.0) | 1.0 × 2.1 | LB_Door_South_FireAssay |
| Sample prep (north) | (-12.0, 9.0) | 1.0 × 2.1 | LB_Door_North_Prep |
| Wet chemistry (north) | (12.0, 9.0) | 1.0 × 2.1 | LB_Door_North_WetChem |
| Prep to fire assay, double | (-6.0, 5.4) | 2.0 × 2.4 | LB_Door_Prep_FireAssay_L / _R |
| Fire assay to instrument room | (6.0, -4.9) | 1.0 × 2.1 | LB_Door_FireAssay_Instrument |
| Fire assay to wet chemistry | (6.0, 5.1) | 1.0 × 2.1 | LB_Door_FireAssay_WetChem |
| Instrument room to wet chemistry | (12.0, 0.0) | 1.0 × 2.1 | LB_Door_Instrument_WetChem |
| Balance room | (2.75, 5.0) | 0.9 × 2.1 | LB_Door_BalanceRoom |

## Moving parts

| Part | Motion |
|---|---|
| LB_Shutter_West | Pivot at the top of the curtain; roll up = scale local Z from 1 to about 0.05. |
| LB_Door_* | Pivot on the hinge edge at floor level, leaf along local +X. Open = rotate about local Z by ±90°. |
| LB_FusionFurnace1/2_Door | Vertical-lift door: translate local +Z by 0.35 m to open. |
| LB_CupelFurnace1/2_Door | Bottom-hinged: rotate about local X by about -90° to drop it open. |
| LB_DryOven1/2_Door | Hinge on the left edge, rotate about local Z, up to about -110°. |
| LB_Pulverizer1/2_Lid | Hinged at the back, rotate about local X by about -75° to open. |
| LB_XRF_Lid | Sample-loader cover hinged at the back, rotate about local X by about -60°. |
| LB_Hood_*_Sash | Fume hood sash: translate local +Z, 0 (closed) to +0.75 m (open). |

The furnace mouths use an emissive material (M_Glow_Hot) so they read as hot in the previews.

### Pivot coordinates (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

## Unreal import

Combine Meshes off. With Transform Vertex to Absolute on, every part keeps the building origin as
its pivot, which suits the static parts. For the moving parts, import with it off and place each
part at the pivot above. The Blender Y axis appears as -Y in Unreal with the default FBX settings,
so check rotation signs after import. LB_Roof and LB_RoofPlant are separate so they can be hidden
for interior views. Suggested safety props from SafetyEquipment: an SM_EmergencyShower at
(7.0, 1.5, 0) in wet chemistry and at (-5.0, 0.0, 0) in fire assay; an SM_EyewashStation on the
wet chemistry island end.

## Dimensions

| Item | Value (W × D × H) | Status |
|---|---|---|
| WDXRF spectrometer (tube-above floor unit) | 1.31 × 0.89 × 1.47 m, ~620 kg | Sourced: Rigaku ZSX Primus IV product page |
| Spark OES, floor type | 0.79 × 0.625 × 1.35 m, 127 kg | Sourced: SPECTROMAXx listing on linkonbiz.com; the axis order is my guess |
| ICP-OES, benchtop | 0.625 × 0.74 × 0.887 m, ~90 kg | Sourced: Agilent 5800/5900 site preparation checklist |
| Fire assay (fusion) furnace, floor-standing | 1.45 × 1.22 × 2.16 m | Sourced: used MSA fire assay furnace listing (57 × 48 × 85 in) |
| Cupellation furnace, benchtop | 0.485 × 0.75 × 0.82 m on a 0.75 m stand | Sourced: Delmer D-C (18 cupels, 1150 °C) |
| Furnace canopy hood, stacks Ø0.7 to {LH + 4.35:.1f} m | | Estimated |
| Jaw crusher, ring-mill pulverisers, drying ovens, splitters, pellet press, fusion bead machine | | Estimated |
| Fume hoods 1.8 × 0.9 × 2.4 m | | Estimated (common size) |
| Building, rooms, door positions, dust collector | | Own design |

Sources: Rigaku ZSX Primus IV (https://rigaku.com/products/xrf-spectrometers/wdxrf/zsx-primus-iv);
SPECTROMAXx listing (https://linkonbiz.com/en/product/iframe-detail/1296); Agilent 5800/5900
site prep checklist (https://icpms.cz/paper/20842); MSA furnace (https://www.911metallurgist.com/fire-assay-furnace-for-sale);
Delmer cupellation furnaces (https://delmergroup.com/collections/cupellation-furnace).

## Files

- SM_Laboratory.blend / .fbx (the REF collection is not exported)
- Preview_Exterior.png, Preview_Cutaway.png, Preview_FireAssay.png, Preview_Instruments.png,
  Preview_SamplePrep.png (all but the exterior are rendered with the roof hidden)
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
    sample_prep(col, m)
    fire_assay(col, m)
    instrument_room(col, m)
    wet_chem(col, m)
    dust_collector(col, m)
    pb.ref_human(ref, (10.0, -4.0, 0.0))
    pb.ref_ground(ref, (-50, -40, 50, 40), [(-18.2, -9.2, 18.2, 9.2)], z=-0.01)

    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render(samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Exterior.png"), (30, -34, 18), (0, 0, 2))
    hide = [bpy.data.objects[n] for n in ("LB_Roof", "LB_RoofPlant", "LB_Lights")]
    for o in hide:
        o.hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Cutaway.png"), (-26, -30, 30), (0, 0, 0))
    pb.render_view(os.path.join(OUT, "Preview_FireAssay.png"), (1.5, -2.0, 4.2), (-2.5, 7.0, 1.0), lens=24)
    pb.render_view(os.path.join(OUT, "Preview_Instruments.png"), (10.5, -1.0, 4.0), (13.0, -7.5, 0.8), lens=22)
    pb.render_view(os.path.join(OUT, "Preview_SamplePrep.png"), (-9.0, 1.0, 4.2), (-14.0, 7.0, 0.8), lens=24)
    for o in hide:
        o.hide_render = False


main()
