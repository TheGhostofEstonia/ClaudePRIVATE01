"""
build_safety_equipment.py - SafetyEquipment set: emergency shower/eyewash, gas detection (fixed,
pole-mounted, portable, extractive), alarm panel and beacon, SCBA and respirator cabinets, a
portable-detector charging rack and a small PPE store building.

Run:  blender -b --factory-startup --python Tools/Blender/WorkshopsSafetyLab/build_safety_equipment.py
      (add -- --no-render to skip the previews)

Every prop is built at its own origin and exported to its own FBX, so it can be scattered around
the plant. Afterwards the props are moved into a display row for the .blend and the previews.

Origins:
  floor props  - floor level, centre of the footprint (shower, pole detector, PPE store)
  wall props   - on the wall face; the prop sticks out along local -Y (front faces -Y).
                 Eyewash and SCBA cabinet origins are at floor level, the others at the
                 centre of the back face (set z to the mounting height in Unreal).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import wsl_common as wc  # noqa: E402
from wsl_common import F  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Meshes", "SafetyEquipment")
NAME = "SM_SafetyEquipment"

# ANSI/ISEA Z358.1 figures used for the shower and eyewash (see README)
SHOWER_HEAD_Z = 2.20       # showerhead face 2.083-2.438 m above floor
EYEWASH_FLOW_Z = 1.05      # eye/face wash flow 0.838-1.346 m above floor
EYEWASH_WALL_GAP = 0.25    # nozzles at least 0.153 m from the wall


# ---------------------------------------------------------------------------
# Emergency shower and eyewash
# ---------------------------------------------------------------------------

def emergency_shower(col, m):
    """Floor-standing combination shower + eye/face wash. Arm and bowl point along +X."""
    p = pb.Part("ES_Shower_Body")
    p.cyl(0.13, 0.02, (0, 0, 0.01), m['yellow'], seg=24)                        # floor flange
    p.cyl(0.021, 2.38, (0, 0, 1.19), m['yellow'], seg=16)                       # 1-1/4" riser
    p.cyl_between((0, 0, 2.38), (0.6, 0, 2.38), 0.021, m['yellow'], seg=16)     # shower arm
    p.sphere(0.03, (0, 0, 2.38), m['yellow'], seg=12)
    p.box((0.1, 0.07, 0.07), (0.16, 0, 2.38), m['bright'])                      # stay-open valve
    p.cyl(0.13, 0.1, (0.6, 0, SHOWER_HEAD_Z + 0.05), m['yellow'], seg=32, r2=0.04)  # head bowl
    p.cyl(0.12, 0.01, (0.6, 0, SHOWER_HEAD_Z + 0.005), m['bright'], seg=32)     # spray face
    # eye/face wash: supply branch, bowl, drain back into the riser foot
    bowl = Vector((0.38, 0, EYEWASH_FLOW_Z - 0.1))
    p.cyl_between((0, 0, bowl.z - 0.12), (bowl.x - 0.05, 0, bowl.z - 0.12), 0.016, m['yellow'], seg=12)
    p.box((0.08, 0.06, 0.06), (0.12, 0, bowl.z - 0.12), m['bright'])            # eyewash valve
    p.cyl(0.15, 0.1, (bowl.x, 0, bowl.z), m['yellow'], seg=32, r2=0.05)
    p.cyl(0.14, 0.01, (bowl.x, 0, bowl.z + 0.045), m['stainless'], seg=32)
    p.cyl_between((bowl.x, 0, bowl.z - 0.05), (bowl.x, 0, 0.35), 0.02, m['yellow'], seg=12)
    p.cyl_between((bowl.x, 0, 0.35), (0.02, 0, 0.2), 0.02, m['yellow'], seg=12)
    for dy in (-0.05, 0.05):                                                     # spray heads
        p.cyl(0.018, 0.05, (bowl.x, dy, bowl.z + 0.08), m['bright'], seg=12)
    # sign panel (blank green, add a decal in Unreal) and activation beacon on top
    p.box((0.4, 0.01, 0.4), (0, -0.05, 2.0), m['green'])
    p.box((0.05, 0.04, 0.05), (0, -0.03, 2.0), m['bright'])
    p.cyl(0.05, 0.06, (0, 0, 2.44), m['steel'], seg=16)
    p.cyl(0.045, 0.1, (0, 0, 2.52), m['beacon'], seg=16)
    p.sphere(0.045, (0, 0, 2.57), m['beacon'], seg=12)
    p.finish(col)
    # pull rod with triangle handle hanging from the valve lever
    top = (0.3, 0, 2.38)
    r = pb.Part("ES_Shower_PullRod", pivot=top)
    r.cyl_between(top, (0.3, 0, 1.85), 0.006, m['bright'], seg=6)
    tri = [(0.3, 0, 1.85), (0.22, 0, 1.68), (0.38, 0, 1.68)]
    for a, b in zip(tri, tri[1:] + tri[:1]):
        r.cyl_between(a, b, 0.008, m['yellow'], seg=6)
    r.finish(col)
    # push flag in front of the bowl, turns about the valve stem (vertical)
    piv = (0.12, 0, bowl.z - 0.12)
    f = pb.Part("ES_Eyewash_PushFlag", pivot=piv)
    f.cyl_between(piv, (0.12, -0.22, bowl.z - 0.12), 0.008, m['bright'], seg=6)
    f.box((0.02, 0.18, 0.12), (0.12, -0.3, bowl.z - 0.06), m['green'])
    f.finish(col)
    # dust caps over the spray heads, flip open about the Y axis
    piv = (bowl.x - 0.04, 0, bowl.z + 0.105)
    c = pb.Part("ES_Eyewash_Caps", pivot=piv)
    for dy in (-0.05, 0.05):
        c.cyl(0.03, 0.025, (bowl.x, dy, bowl.z + 0.12), m['yellow'], seg=16)
    c.box((0.06, 0.12, 0.01), (bowl.x - 0.02, 0, bowl.z + 0.13), m['yellow'])
    c.finish(col)


def wall_eyewash(col, m):
    """Wall-mounted eye/face wash. Origin on the wall face at floor level; bowl sticks out along -Y."""
    p = pb.Part("EW_Body")
    y = -EYEWASH_WALL_GAP
    bz = EYEWASH_FLOW_Z - 0.1
    p.box((0.25, 0.02, 0.35), (0, -0.01, bz - 0.05), m['steel'])                # wall bracket
    p.cyl_between((0, -0.02, bz - 0.12), (0, y, bz - 0.12), 0.016, m['yellow'], seg=12)
    p.cyl_between((0, -0.02, bz - 0.12), (0, -0.02, 1.8), 0.016, m['yellow'], seg=12)   # supply up
    p.cyl(0.15, 0.1, (0, y, bz), m['yellow'], seg=32, r2=0.05)
    p.cyl(0.14, 0.01, (0, y, bz + 0.045), m['stainless'], seg=32)
    p.cyl_between((0, y, bz - 0.05), (0, y, 0.45), 0.02, m['yellow'], seg=12)  # drain with trap
    p.cyl_between((0, y, 0.45), (0, -0.02, 0.35), 0.02, m['yellow'], seg=12)
    for dx in (-0.05, 0.05):
        p.cyl(0.018, 0.05, (dx, y, bz + 0.08), m['bright'], seg=12)
    p.box((0.3, 0.01, 0.3), (0, -0.005, 1.55), m['green'])                      # sign panel
    p.finish(col)
    piv = (0.12, y + 0.1, bz - 0.12)
    f = pb.Part("EW_PushFlag", pivot=piv)
    f.cyl_between(piv, (0.2, y - 0.1, bz - 0.12), 0.008, m['bright'], seg=6)
    f.box((0.18, 0.02, 0.12), (0.22, y - 0.2, bz - 0.06), m['green'])
    f.finish(col)
    piv = (0, y + 0.04, bz + 0.105)
    c = pb.Part("EW_Caps", pivot=piv)
    for dx in (-0.05, 0.05):
        c.cyl(0.03, 0.025, (dx, y, bz + 0.12), m['yellow'], seg=16)
    c.box((0.12, 0.06, 0.01), (0, y + 0.02, bz + 0.13), m['yellow'])
    c.finish(col)


# ---------------------------------------------------------------------------
# Gas detection
# ---------------------------------------------------------------------------

def transmitter(p, fr, m):
    """Fixed toxic-gas transmitter, 280 x 150 x 130 mm housing, sensor head pointing down."""
    fr.bmm(p, (-0.16, -0.01, -0.12), (0.16, 0.0, 0.12), m['steel'])              # mounting plate
    fr.bmm(p, (-0.14, -0.14, -0.075), (0.14, -0.01, 0.075), m['red'])           # housing
    fr.cyl(p, 0.045, 0.01, (-0.05, -0.145, 0.01), m['glass'], rot=(90, 0, 0), seg=24)  # display window
    fr.bmm(p, (0.03, -0.146, -0.03), (0.11, -0.14, 0.04), m['screen'])
    fr.cyl(p, 0.032, 0.09, (0.06, -0.075, -0.12), m['steel'], seg=20)          # sensor head
    fr.cyl(p, 0.036, 0.02, (0.06, -0.075, -0.17), m['rubber'], seg=20)         # splash guard
    fr.cyl(p, 0.012, 0.04, (-0.08, -0.075, -0.095), m['bright'], seg=10)       # cable gland
    fr.cyl_between(p, (-0.08, -0.075, -0.115), (-0.08, -0.03, -0.4), 0.01, m['rubber'], seg=8)


def gas_detector_fixed(col, m):
    p = pb.Part("GD_Fixed")
    transmitter(p, F(), m)
    p.finish(col)


def gas_alarm_beacon(col, m):
    """Combined sounder and beacon. Origin centre of the back face."""
    p = pb.Part("GD_AlarmBeacon")
    p.box((0.12, 0.01, 0.16), (0, -0.005, 0), m['steel'])
    p.box((0.11, 0.09, 0.11), (0, -0.055, -0.02), m['red'])
    p.cyl(0.035, 0.03, (0, -0.115, -0.03), m['steel'], rot=(90, 0, 0), seg=20)  # sounder horn
    p.cyl(0.045, 0.08, (0, -0.055, 0.075), m['beacon'], seg=20)
    p.sphere(0.045, (0, -0.055, 0.115), m['beacon'], seg=16)
    p.finish(col)


def gas_detector_pole(col, m):
    """Outdoor area / fence-line monitor on a 3 m pole with sunshade, junction box and beacon."""
    p = pb.Part("GD_Pole")
    p.box((0.5, 0.5, 0.2), (0, 0, 0.1), m['dado'])
    p.box((0.25, 0.25, 0.015), (0, 0, 0.207), m['steel'])
    p.cyl(0.038, 3.0, (0, 0, 1.7), m['bright'], seg=16)
    f = F((0, -0.04, 1.6))                                                        # transmitter on the pole face
    transmitter(p, f, m)
    p.box((0.38, 0.22, 0.01), (0, -0.12, 1.75), m['stainless'], rot=(8, 0, 0))   # sunshade
    p.box((0.25, 0.15, 0.3), (0, -0.115, 1.0), m['machine2'])                    # junction box
    p.cyl(0.05, 0.06, (0, 0, 3.23), m['steel'], seg=16)
    p.cyl(0.055, 0.14, (0, 0, 3.33), m['beacon'], seg=20)
    p.sphere(0.055, (0, 0, 3.4), m['beacon'], seg=16)
    p.cyl(0.04, 0.05, (0.1, 0, 3.0), m['steel'], rot=(0, 90, 0), seg=16)        # sounder
    p.finish(col)


def portable_detector(p, fr, m):
    """Handheld multi-gas monitor, about 70 x 35 x 125 mm, standing on its base."""
    fr.bmm(p, (-0.035, -0.018, 0.0), (0.035, 0.018, 0.125), m['yellow'])
    fr.bmm(p, (-0.037, -0.02, 0.0), (0.037, 0.02, 0.02), m['rubber'])           # bumper
    fr.bmm(p, (-0.025, -0.0185, 0.06), (0.025, -0.018, 0.1), m['screen'])       # display
    fr.bmm(p, (-0.03, -0.012, 0.125), (0.03, 0.012, 0.135), m['beacon'])        # alarm bar
    for k in range(3):
        fr.bmm(p, (-0.02 + k * 0.016, -0.0185, 0.03), (-0.012 + k * 0.016, -0.018, 0.045), m['rubber'])
    fr.bmm(p, (-0.01, 0.018, 0.04), (0.01, 0.024, 0.11), m['bright'])           # belt clip


def gas_detector_portable(col, m):
    p = pb.Part("GD_Portable")
    portable_detector(p, F(), m)
    p.finish(col)


def charging_rack(col, m):
    """Wall rack charging six portable detectors. Origin centre of the back face."""
    p = pb.Part("GD_ChargingRack")
    p.box((0.75, 0.02, 0.3), (0, -0.01, 0), m['machine2'])
    p.box((0.75, 0.1, 0.03), (0, -0.07, -0.12), m['machine2'])
    for i in range(6):
        x = -0.31 + i * 0.124
        p.box((0.09, 0.06, 0.04), (x, -0.07, -0.085), m['rubber'])
        portable_detector(p, F((x, -0.07, -0.065)), m)
        p.box((0.01, 0.005, 0.01), (x, -0.101, -0.085), m['lamp'])
    p.finish(col)


def extractive_monitor(col, m):
    """
    Multipoint extractive (sample-draw) toxic gas monitor cabinet, the type used for arsine at
    hooded cells. Sample tubes enter from below. Origin centre of the back face.
    """
    p = pb.Part("GD_Extractive")
    p.box((0.6, 0.25, 0.75), (0, -0.125, 0), m['lab'])
    p.box((0.5, 0.01, 0.3), (0, -0.255, 0.15), m['glass'])
    p.box((0.2, 0.012, 0.12), (-0.1, -0.256, 0.15), m['screen'])
    for k in range(4):
        p.box((0.03, 0.01, 0.015), (0.12 + k * 0.035, -0.256, -0.1), m['lamp'] if k else m['red'])
    for k in range(8):                                                           # sample tubes
        x = -0.25 + k * 0.07
        p.cyl_between((x, -0.12, -0.375), (x, -0.12, -0.9), 0.004, m['white'], seg=6)
    p.cyl_between((0.27, -0.12, 0.375), (0.27, -0.12, 0.7), 0.012, m['rubber'], seg=8)  # exhaust
    p.finish(col)


def alarm_panel(col, m):
    """Gas detection control panel with channel indicator lamps. Origin centre of the back face."""
    p = pb.Part("GD_AlarmPanel")
    p.box((0.5, 0.2, 0.6), (0, -0.1, 0), m['machine2'])
    p.box((0.48, 0.01, 0.58), (0, -0.205, 0), m['machine2'])
    p.box((0.22, 0.012, 0.12), (0, -0.21, 0.17), m['screen'])
    for r in range(2):
        for k in range(8):
            mm = m['green'] if (r + k) % 5 else m['beacon']
            p.cyl(0.01, 0.01, (-0.175 + k * 0.05, -0.212, 0.02 - r * 0.07), mm, rot=(90, 0, 0), seg=10)
    p.cyl(0.03, 0.02, (0.17, -0.215, -0.2), m['red'], rot=(90, 0, 0), seg=16)   # silence/reset
    p.finish(col)


# ---------------------------------------------------------------------------
# Breathing apparatus cabinets
# ---------------------------------------------------------------------------

def scba_cabinet(col, m, prefix="SCBA", fr=None):
    """
    Floor-standing SCBA cabinet on legs with a glazed door (hinge on the left, local -X).
    Origin at floor level, centre of the back face.
    """
    fr = fr or F()
    p = pb.Part(prefix + "_Cabinet", pivot=fr.o)
    W, D, H, z0 = 0.7, 0.4, 1.0, 0.3
    for x in (-0.3, 0.3):
        fr.bmm(p, (x - 0.02, -D + 0.05, 0), (x + 0.02, -D + 0.09, z0), m['steel'])
        fr.bmm(p, (x - 0.02, -0.06, 0), (x + 0.02, -0.02, z0), m['steel'])
    fr.bmm(p, (-W / 2, -D, z0), (W / 2, -D + 0.02, z0 + H), m['red'])             # front frame
    fr.bmm(p, (-W / 2, -D, z0), (W / 2, 0, z0 + 0.03), m['red'])                  # floor
    fr.bmm(p, (-W / 2, -D, z0 + H - 0.03), (W / 2, 0, z0 + H), m['red'])
    fr.bmm(p, (-W / 2, -0.03, z0), (W / 2, 0, z0 + H), m['red'])                  # back
    for x in (-W / 2, W / 2 - 0.03):
        fr.bmm(p, (x, -D, z0), (x + 0.03, 0, z0 + H), m['red'])
    # set inside: cylinder, harness backplate, mask
    fr.cyl(p, 0.09, 0.6, (0.0, -0.15, z0 + 0.4), m['bright'], seg=20)
    fr.sphere(p, 0.09, (0.0, -0.15, z0 + 0.7), m['bright'], seg=16)
    fr.bmm(p, (-0.15, -0.28, z0 + 0.1), (0.15, -0.25, z0 + 0.7), m['rubber'])
    fr.sphere(p, 0.09, (0.0, -0.3, z0 + 0.8), m['rubber'], seg=16)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (-W / 2, -D - 0.01, z0)
    d = pb.Part(prefix + "_Door", pivot=fr.w(hinge))
    fr.bmm(d, (-W / 2, -D - 0.03, z0), (W / 2, -D - 0.01, z0 + H), m['red'])
    fr.bmm(d, (-W / 2 + 0.07, -D - 0.035, z0 + 0.15), (W / 2 - 0.07, -D - 0.025, z0 + H - 0.1), m['glass'])
    fr.bmm(d, (W / 2 - 0.06, -D - 0.06, z0 + 0.45), (W / 2 - 0.04, -D - 0.03, z0 + 0.6), m['bright'])
    d.finish(col, x_toward=fr.xdir(hinge))


def respirator_cabinet(col, m, prefix="RESP", fr=None):
    """Wall cabinet holding half-face respirators. Glazed door hinged on the left. Origin back centre."""
    fr = fr or F()
    p = pb.Part(prefix + "_Cabinet", pivot=fr.o)
    W, D, H = 0.9, 0.3, 0.8
    fr.bmm(p, (-W / 2, -D, -H / 2), (W / 2, -D + 0.02, H / 2), m['white'])
    fr.bmm(p, (-W / 2, -0.02, -H / 2), (W / 2, 0, H / 2), m['white'])
    for z in (-H / 2, H / 2 - 0.02, 0.0):
        fr.bmm(p, (-W / 2, -D, z), (W / 2, 0, z + 0.02), m['white'])
    for x in (-W / 2, W / 2 - 0.02):
        fr.bmm(p, (x, -D, -H / 2), (x + 0.02, 0, H / 2), m['white'])
    for z in (-0.2, 0.2):                                                        # respirators on hooks
        for k in range(4):
            x = -0.3 + k * 0.2
            fr.sphere(p, 0.06, (x, -0.12, z), m['rubber'], seg=12)
            fr.cyl(p, 0.035, 0.03, (x - 0.05, -0.17, z - 0.03), m['machine'], rot=(90, 0, 0), seg=12)
            fr.cyl(p, 0.035, 0.03, (x + 0.05, -0.17, z - 0.03), m['machine'], rot=(90, 0, 0), seg=12)
    p.finish(col, x_toward=fr.xdir((0, 0, 0)))
    hinge = (-W / 2, -D - 0.01, -H / 2)
    d = pb.Part(prefix + "_Door", pivot=fr.w(hinge))
    fr.bmm(d, (-W / 2, -D - 0.03, -H / 2), (W / 2, -D - 0.01, H / 2), m['white'])
    fr.bmm(d, (-W / 2 + 0.05, -D - 0.035, -H / 2 + 0.05), (W / 2 - 0.05, -D - 0.025, H / 2 - 0.05), m['glass'])
    fr.bmm(d, (W / 2 - 0.06, -D - 0.06, -0.08), (W / 2 - 0.04, -D - 0.03, 0.08), m['bright'])
    d.finish(col, x_toward=fr.xdir(hinge))


# ---------------------------------------------------------------------------
# PPE store building
# ---------------------------------------------------------------------------

PPE_X, PPE_Y, PPE_H = 5.0, 3.0, 3.3     # 10 x 6 m, 3.3 m to the roof slab


def ppe_store(col, m):
    """
    Small block-built PPE store: issue hatch with counter and roller grille, door, shelving,
    lockers, SCBA and respirator cabinets, detector charging rack. Front (hatch, door) on -Y.
    """
    fl = pb.Part("PPE_Floor")
    fl.box_mm((-PPE_X - 0.2, -PPE_Y - 0.2, -0.2), (PPE_X + 0.2, PPE_Y + 0.2, 0.0), m['concrete'])
    fl.box_mm((-PPE_X - 0.2, -PPE_Y - 1.5, -0.2), (PPE_X + 0.2, -PPE_Y - 0.2, -0.05), m['concrete'])  # apron
    fl.finish(col)
    w = pb.Part("PPE_Walls")
    t, h = 0.2, PPE_H
    xs, ys = PPE_X - t / 2, PPE_Y - t / 2
    # front wall: hatch 1.6 x 1.0 (sill 1.0) centred x=-1.5, door 1.0 x 2.1 centred x=3.0
    wc.wall(w, (-xs - t / 2, -ys), (xs + t / 2, -ys), h, t, m['white'],
            openings=[(2.7, 4.3, 1.0, 2.0), (7.5, 8.5, 0.0, 2.1)])
    wc.wall(w, (-xs - t / 2, ys), (xs + t / 2, ys), h, t, m['white'],
            windows=[(1.5, 3.5, 1.6, 2.4), (6.5, 8.5, 1.6, 2.4)], glass=m['glass'])
    for x in (-xs, xs):
        wc.wall(w, (x, -ys), (x, ys), h, t, m['white'])
    w.box_mm((-PPE_X, -PPE_Y - 0.3, 2.3), (-PPE_X + 4.3, -PPE_Y, 2.4), m['steel'])  # canopy over hatch
    w.box_mm((-PPE_X, -PPE_Y - 1.0, 2.4), (-PPE_X + 4.3, -PPE_Y, 2.45), m['steel'])
    w.box((1.2, 0.02, 0.4), (-1.5, -PPE_Y - 0.01, 2.75), m['blue'])              # blank sign board
    w.finish(col)
    r = pb.Part("PPE_Roof")
    r.box_mm((-PPE_X, -PPE_Y, h), (PPE_X, PPE_Y, h + 0.2), m['dado'])
    # parapet: 0.15 m thick upstand on all four edges
    r.box_mm((-PPE_X, PPE_Y - 0.15, h + 0.2), (PPE_X, PPE_Y, h + 0.5), m['dado'])
    r.box_mm((-PPE_X, -PPE_Y, h + 0.2), (PPE_X, -PPE_Y + 0.15, h + 0.5), m['dado'])
    r.box_mm((PPE_X - 0.15, -PPE_Y, h + 0.2), (PPE_X, PPE_Y, h + 0.5), m['dado'])
    r.box_mm((-PPE_X, -PPE_Y, h + 0.2), (-PPE_X + 0.15, PPE_Y, h + 0.5), m['dado'])
    r.finish(col)
    rs = pb.Part("PPE_HatchFrame")
    wc.roller_shutter("PPE_HatchShutter", col, rs, (-1.5, -PPE_Y - 0.01, 1.0), 1.6, 1.0, 0, m['bright'], m['steel'])
    rs.box_mm((-2.4, -PPE_Y - 0.35, 0.95), (-0.6, -PPE_Y, 1.0), m['stainless'])  # outside sill
    rs.finish(col)
    wc.door_leaf("PPE_Door", col, (2.5, -ys, 0), 1.0, 2.1, 0, m['blue'], m['bright'], glazed=m['glass'])

    p = pb.Part("PPE_Interior")
    wc.workbench(p, F((-1.5, -2.35, 0)), 2.4, 0.7, 1.0, m['wood'], m['blue'], drawers_m=m['blue'])
    for x in (-3.3, -1.0, 1.3):                                                  # issue shelving, north wall
        wc.shelving(p, F((x, 2.45, 0)), 2.1, 0.6, 2.4, 5, m['blue'], load_m=m['orange'], seed=int(x * 3))
    # hard hats on the top shelf of the middle unit
    for k in range(6):
        x = -1.85 + k * 0.33
        p.sphere(0.13, (x, 2.45, 2.4), m['white'] if k % 3 else m['yellow'], seg=16)
    wc.locker_bank(p, F((-4.5, -1.2, 0), 90), 6, m['machine2'], m['steel'])
    wc.cabinet(p, F((3.0, 2.5, 0)), 1.6, 0.5, 2.0, m['blue'], m['bright'])     # glove / boot store
    p.finish(col)
    scba_cabinet(col, m, prefix="PPE_SCBA", fr=F((PPE_X - 0.2, -0.4, 0), -90))
    respirator_cabinet(col, m, prefix="PPE_Resp", fr=F((PPE_X - 0.2, 1.3, 1.55), -90))
    ppe_vending(col, m)


def ppe_vending(col, m):
    """PPE vending machine outside next to the door (consumables: gloves, earplugs, glasses)."""
    p = pb.Part("PPE_Vending")
    f = F((4.2, -PPE_Y - 0.5, 0))
    f.bmm(p, (-0.45, -0.4, 0), (0.45, 0.4, 1.9), m['blue'])
    f.bmm(p, (-0.38, -0.41, 0.55), (0.18, -0.4, 1.75), m['glass'])
    f.bmm(p, (0.24, -0.41, 1.3), (0.4, -0.4, 1.5), m['screen'])
    f.bmm(p, (-0.38, -0.42, 0.25), (0.18, -0.4, 0.45), m['steel'])
    for r in range(5):
        for k in range(4):
            f.bmm(p, (-0.34 + k * 0.13, -0.35, 0.62 + r * 0.22), (-0.26 + k * 0.13, -0.2, 0.72 + r * 0.22),
                  m['orange'] if (r + k) % 2 else m['yellow'])
    p.finish(col)


# ---------------------------------------------------------------------------
# Build, export each prop, then lay out the display row
# ---------------------------------------------------------------------------

# (asset name, builder, display location)
PROPS = [
    ("SM_EmergencyShower", emergency_shower, (-8.0, -1.0, 0.0)),
    ("SM_EyewashStation", wall_eyewash, (-5.5, 0.0, 0.0)),
    ("SM_GasDetector_Fixed", gas_detector_fixed, (-3.8, 0.0, 1.5)),
    ("SM_GasAlarmBeacon", gas_alarm_beacon, (-3.0, 0.0, 2.3)),
    ("SM_GasMonitor_Extractive", extractive_monitor, (-1.6, 0.0, 1.4)),
    ("SM_GasAlarmPanel", alarm_panel, (0.0, 0.0, 1.5)),
    ("SM_DetectorChargingRack", charging_rack, (1.6, 0.0, 1.3)),
    ("SM_GasDetector_Portable", gas_detector_portable, (1.6, -0.25, 0.9)),
    ("SM_RespiratorCabinet", respirator_cabinet, (3.4, 0.0, 1.5)),
    ("SM_SCBACabinet", scba_cabinet, (5.2, 0.0, 0.0)),
    ("SM_GasDetector_Pole", gas_detector_pole, (7.5, -1.0, 0.0)),
    ("SM_PPEStore", ppe_store, (0.0, 7.0, 0.0)),
]


def write_readme(prop_info):
    rows = []
    for name, objs, loc in prop_info:
        rows.append(f"| {name} | {', '.join(o for o in objs)} | ({loc[0]:.1f}, {loc[1]:.1f}, {loc[2]:.1f}) |")
    table = "\n".join(rows)
    txt = f"""# SafetyEquipment

Safety props for the plant: emergency shower and eyewash, gas detection (SO₂ and arsine), alarm
devices, breathing-apparatus cabinets, a portable-detector charging rack and a small PPE store.
Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/WorkshopsSafetyLab/build_safety_equipment.py`; re-run it to rebuild.

Each prop has its own FBX built at its own origin, so it can be placed many times around the
plant. `SM_SafetyEquipment.blend` holds all of them in a display row (the locations below) in front
of a REF display wall. No logos or brand markings; sign panels are blank green or blue boards for
decals.

## Origins and placement

- Floor props (shower, pole detector, PPE store): origin at floor level, centre of the base.
- Wall props: origin on the wall face, the prop sticks out along local -Y. SM_EyewashStation and
  SM_SCBACabinet have the origin at floor level (their heights are built in). The others have the
  origin at the centre of the back face, so set Z to the mounting height.
- Suggested mounting heights (centre of the back face): fixed detector 1.5 m in the breathing
  zone, or 0.3-0.5 m where gas pools (see the note below); alarm beacon 2.3-2.5 m; extractive
  monitor and alarm panel 1.4-1.5 m; charging rack 1.3 m; respirator cabinet 1.5 m.
- Emergency showers and eyewashes are normally placed within 10 seconds' walk of the hazard
  (ANSI Z358.1). The shower needs about 1 m of clear floor around the spray.

## Files and parts

| FBX | Parts | Display location in the .blend |
|---|---|---|
{table}

## Moving parts

| Part | Motion |
|---|---|
| ES_Shower_PullRod | Pull = translate local -Z by about 0.08 m (pivot at the valve lever). |
| ES_Eyewash_PushFlag, EW_PushFlag | Turn about local Z at the valve stem, about 60°, to start the eyewash. |
| ES_Eyewash_Caps, EW_Caps | Flip open about local Y (ES) / local X (EW) by about 110° when the water starts. |
| SCBA_Door, PPE_SCBA_Door, RESP_Door, PPE_Resp_Door | Hinge on the left edge, rotate about local Z, up to about -110°. |
| PPE_Door | Hinge at floor level on the west edge of the door, rotate about local Z. |
| PPE_HatchShutter | Pivot at the top of the curtain; roll up = scale local Z from 1 to about 0.05. |

For a running shower or eyewash, spawn a Niagara water effect at the showerhead face
(0.60, 0, {SHOWER_HEAD_Z:.2f}) or the bowl spray heads (shower: (0.38, ±0.05, 1.03); wall eyewash: (±0.05, -0.25, 1.03)).
The amber beacon on top of the shower is the flow-switch alarm many plants fit; light it when the
shower runs.

## PPE store

- Footprint 10 × 6 m outside (x -5 … 5, y -3 … 3), 3.3 m to the roof slab, 0.3 m parapet.
  Origin at floor level in the centre. Front faces -Y.
- Openings: issue hatch 1.6 × 1.0 m, sill 1.0 m, centred at x = -1.5 on the front wall, with a
  canopy and roller grille. Door 1.0 × 2.1 m centred at x = 3.0 on the front wall. Two windows on
  the back wall.
- Inside: issue counter behind the hatch, three shelving units with stock and hard hats, six
  lockers on the west wall, SCBA and respirator cabinets on the east wall, glove/boot cabinet.
  Outside: PPE vending machine next to the door.
- PPE_Roof is separate so it can be hidden for interior views.

## Gas detection notes

- SO₂ (molar mass 64) and arsine, AsH₃ (molar mass 78), are both heavier than air (29). Mounting
  guides put sensors for heavier-than-air gases low, about 0.15-0.3 m above the floor, but other
  guides say toxic-gas sensors go in the breathing zone at 1.2-1.8 m. The sources disagree; real
  plants decide per area from a hazard study. For gameplay, the breathing-zone height reads better.
- SO₂ is the main risk around the furnaces, converters and acid plant. Arsine is a risk at the
  liberator (decopperizing) cells in the tankhouse. Arsine is often monitored with extractive
  multipoint analysers that draw samples through tubes to one cabinet (SM_GasMonitor_Extractive).
  That last point is from general knowledge; I did not check it against a datasheet.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Showerhead face height | {SHOWER_HEAD_Z:.2f} m (standard: 2.083-2.438 m) | Sourced: ANSI/ISEA Z358.1-2014 summaries |
| Shower spray pattern | Ø0.51 m at 1.52 m above floor (for the effect) | Sourced: same |
| Eye/face wash flow height | ~1.03-1.05 m (standard: 0.838-1.346 m) | Sourced: same |
| Eyewash nozzles from wall | 0.25 m (standard: at least 0.153 m) | Sourced: same |
| Shower flow 76 L/min for 15 min, tepid water 16-38 °C | for gameplay/effects | Sourced: same |
| Fixed transmitter housing | 280 × 150 × 130 mm | Sourced: Dräger Polytron 8100 product page. Which axis is which is my guess |
| Pole detector: 3.0 m pole, transmitter at 1.6 m, sunshade, beacon | | Estimated |
| Portable multi-gas monitor | 70 × 35 × 125 mm | Estimated (typical handheld size) |
| Extractive monitor cabinet | 0.6 × 0.25 × 0.75 m | Estimated |
| Alarm panel 0.5 × 0.2 × 0.6 m, beacon/sounder | | Estimated |
| SCBA cabinet 0.7 × 0.4 × 1.0 m on 0.3 m legs, respirator cabinet 0.9 × 0.3 × 0.8 m | | Estimated |
| PPE store building and layout | | Own design |

Sources:
- ANSI/ISEA Z358.1-2014 summaries: Broen-Lab (https://safetywheel.broen-lab.com/wp-content/uploads/2024/07/ANSI-Z358.1_250624.pdf),
  Hughes Safety (https://www.hughes-safety.com/media/mageworx/downloads/attachment/file/a/n/ansi_summary_huk_26042021.pdf),
  CCOHS (https://ccohs.gc.ca/oshanswers/safety_haz/emer_showers.html). I used summaries, not the
  standard's own text.
- Dräger Polytron 8100 (https://www.draeger.com/en-us_us/Products/Draeger-Polytron-8100).
- Detector mounting heights: PK Safety (https://pksafety.com/blog/best-practices-for-fixed-gas-detector-installation-placement-location-and-maintenance/),
  gasdetection.com (https://gasdetection.com/articles/where-to-mount-a-fixed-toxic-gas-detector/).

## Unreal import

Combine Meshes off. Import each FBX with Transform Vertex to Absolute off so every part keeps its
own pivot; for one-part props it makes no difference. The Blender Y axis appears as -Y in Unreal
with the default FBX settings, so check rotation signs after import.

## Previews

Preview_Overview.png (display row), Preview_ShowerEyewash.png, Preview_GasDetection.png,
Preview_PPEStore.png (roof hidden).
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    pb.reset_scene()
    pb.clear_material_cache()
    m = wc.palette()
    top = pb.collection(NAME)
    info = []
    for name, builder, loc in PROPS:
        col = pb.collection(name, top)
        builder(col, m)
        pb.export_fbx(os.path.join(OUT, name + ".fbx"), [col.name])
        objs = sorted(o.name for o in col.objects)
        for o in col.objects:
            o.location += Vector(loc)
        info.append((name, objs, loc))
    write_readme(info)

    ref = pb.collection("REF")
    wall = pb.Part("REF_DisplayWall")
    wall.box_mm((-6.5, 0.0, 0.0), (6.3, 0.2, 2.8), pb.mat("M_REF_Wall", (0.6, 0.6, 0.58), 0, 0.9))
    wall.box_mm((1.2, -0.6, 0.0), (2.0, -0.2, 0.9), pb.mat("M_REF_Table", (0.4, 0.3, 0.2), 0, 0.7))
    wall.finish(ref)
    pb.ref_human(ref, (-8.6, -2.2, 0.0))
    pb.ref_ground(ref, (-15, -12, 15, 15), [(-5.3, 3.8, 5.3, 10.3)], z=-0.01)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render(samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (0, -14, 6), (0, 2, 1.2), lens=30)
    pb.render_view(os.path.join(OUT, "Preview_ShowerEyewash.png"), (-5.2, -3.8, 2.2), (-7.0, 0.0, 1.2), lens=35)
    pb.render_view(os.path.join(OUT, "Preview_GasDetection.png"), (-0.8, -3.5, 1.9), (-0.8, 0.0, 1.4), lens=24)
    bpy.data.objects["PPE_Roof"].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_PPEStore.png"), (-6, -4, 11), (0, 7, 0.5), lens=30)
    bpy.data.objects["PPE_Roof"].hide_render = False


main()
