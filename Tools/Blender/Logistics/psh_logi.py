"""
psh_logi.py - extra helpers for the logistics build scripts (rail, road, yard vehicles, facilities).

Builds on the shared Tools/Blender/psh_build.py and reuses the maintenance helpers in
Tools/Blender/Maintenance/psh_maint.py (start, wheel, hyd_cyl, parent, finish_asset, run ...).
Importing this module puts both folders on sys.path, so a build script only needs:

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import psh_logi as pl
    pb, pm = pl.pb, pl.pm

Rail conventions used by every rail asset:
    standard gauge 1.435 m, origin on the track centre line at top of rail (z = 0), +X = A end.
    UIC buffers: centres 1.75 m apart, centre height 1.06 m above top of rail (UIC 527 / EN 15551
    range is 0.94-1.065 m; 1.06 m is the new-vehicle value).
"""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(_HERE, "..")))                 # psh_build.py
sys.path.append(os.path.abspath(os.path.join(_HERE, "..", "Maintenance")))  # psh_maint.py

import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

GAUGE = 1.435          # track gauge, inner rail faces (m)
RAIL_HEAD = 0.072      # UIC 60 rail head width (m)
WHEEL_Y = GAUGE / 2 + RAIL_HEAD / 2   # wheel tread centre line from track centre (~0.754)
BUFFER_Z = 1.06        # buffer centre height above top of rail
BUFFER_Y = 0.875       # half of the 1.75 m buffer spacing


# --------------------------------------------------------------------------
# Rail running gear
# --------------------------------------------------------------------------

def wheelset(name, x, col, m, r=0.46):
    """
    Two flanged wheels on one axle. Pivot on the axle centre at (x, 0, r); spin about local Y.
    Default r = 0.46 m (920 mm freight wheel, new). Wheel circumference 2*pi*r.
    """
    p = pb.Part(name, pivot=(x, 0, r))
    for s in (1, -1):
        y = s * WHEEL_Y
        p.cyl(r, 0.135, (x, y, r), m['steel'], rot=(90, 0, 0), seg=28)              # tread + rim
        p.cyl(r + 0.028, 0.03, (x, y - s * 0.06, r), m['steel'], rot=(90, 0, 0), seg=28)  # flange (inside)
        p.cyl(r * 0.3, 0.16, (x, y, r), m['grey'], rot=(90, 0, 0), seg=14)            # hub
        p.cyl(0.11, 0.22, (x, s * (WHEEL_Y + 0.15), r), m['grey'], rot=(90, 0, 0), seg=14)  # axle box
    p.cyl(0.085, GAUGE + 0.2, (x, 0, r), m['grey'], rot=(90, 0, 0), seg=14)          # axle
    return p.finish(col)


def bogie(prefix, x, col, m, wheelbase=1.8, r=0.46, paint=None):
    """
    Freight bogie (Y25 size class): side frames, bolster and two wheelsets.
    <prefix>_Frame pivot at the centre pivot (x, 0, r + 0.25) - yaw about local Z in curves.
    <prefix>_WS1/_WS2 are separate wheelsets (spin about local Y), parented to the frame in the .blend.
    Returns (frame, [ws1, ws2]).
    """
    paint = paint or m['steel']
    zc = r + 0.25
    f = pb.Part(prefix + "_Frame", pivot=(x, 0, zc))
    for s in (1, -1):
        y = s * (WHEEL_Y + 0.15)
        f.box((wheelbase + 0.7, 0.18, 0.32), (x, y, r + 0.05), paint)                 # side frame
        for dx in (-wheelbase / 2, wheelbase / 2):
            f.box((0.34, 0.24, 0.12), (x + dx, y, r + 0.18), m['grey'])               # axle box cap
        for dx in (-0.25, 0.25):                                                      # springs
            f.cyl(0.08, 0.25, (x + dx, y, r + 0.33), m['grey'], seg=10)
    f.box((0.4, GAUGE + 0.5, 0.3), (x, 0, zc), paint)                                 # bolster
    f.cyl(0.22, 0.06, (x, 0, zc + 0.17), m['grey'], seg=20)                           # centre bowl
    frame = f.finish(col)
    ws = []
    for i, dx in enumerate((-wheelbase / 2, wheelbase / 2)):
        w = wheelset(f"{prefix}_WS{i + 1}", x + dx, col, m, r=r)
        pm.parent(w, frame)
        ws.append(w)
    return frame, ws


def buffers_and_coupling(p, x_end, direction, m, beam_paint):
    """
    Headstock beam, two UIC side buffers and a screw coupling hook at one vehicle end.
    x_end: x of the buffer faces; direction +1 for the +X end, -1 for the -X end.
    """
    d = direction
    p.box((0.25, 2.9, 0.4), (x_end - d * 0.75, 0, BUFFER_Z), beam_paint)               # headstock
    for s in (1, -1):
        y = s * BUFFER_Y
        p.cyl(0.11, 0.45, (x_end - d * 0.42, y, BUFFER_Z), m['steel'], rot=(0, 90, 0), seg=14)  # casing
        p.cyl(0.07, 0.2, (x_end - d * 0.12, y, BUFFER_Z), m['grey'], rot=(0, 90, 0), seg=12)    # plunger
        p.cyl(0.22, 0.04, (x_end - d * 0.02, y, BUFFER_Z), m['grey'], rot=(0, 90, 0), seg=20)   # head
    p.box((0.35, 0.08, 0.12), (x_end - d * 0.45, 0, BUFFER_Z), m['steel'])           # draw hook
    p.cyl_between((x_end - d * 0.3, 0, BUFFER_Z - 0.05), (x_end + d * 0.1, 0, BUFFER_Z - 0.25),
                  0.025, m['steel'], seg=8)                                          # hanging link


def underframe(p, x0, x1, z_top, m, paint, width=2.6):
    """Two sole bars and cross members from x0 to x1, top of frame at z_top."""
    for s in (1, -1):
        y = s * (width / 2 - 0.12)
        p.box_mm((x0, y - 0.06, z_top - 0.35), (x1, y + 0.06, z_top), paint)          # sole bar
    p.box_mm((x0, -0.15, z_top - 0.35), (x1, 0.15, z_top), paint)                    # centre sill
    n = max(2, int((x1 - x0) / 1.6))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        p.box((0.12, width - 0.2, 0.2), (x, 0, z_top - 0.1), m['steel'])


# --------------------------------------------------------------------------
# Road vehicles
# --------------------------------------------------------------------------

def road_axle(prefix, x, y_half, r, w, col, m, dual=False, label="A"):
    """
    Wheels for one road axle at x. Single tyres at +/-y_half, or twin tyres (dual=True) centred on
    +/-y_half with 0.35 m between twin centres. Each wheel spins about local Y.
    Returns list of wheel objects named <prefix>_Wheel_<label>L/R (and L2/R2 for the inner twins).
    """
    out = []
    for s, t in ((1, "L"), (-1, "R")):
        if dual:
            out.append(pm.wheel(f"{prefix}_Wheel_{label}{t}", (x, s * (y_half + 0.175), r), r, w, col, m))
            out.append(pm.wheel(f"{prefix}_Wheel_{label}{t}2", (x, s * (y_half - 0.175), r), r, w, col, m))
        else:
            out.append(pm.wheel(f"{prefix}_Wheel_{label}{t}", (x, s * y_half, r), r, w, col, m))
    return out


def deg_per_metre(r):
    """Wheel spin rate in degrees per metre travelled, for the README motion tables."""
    return 360.0 / (2 * math.pi * r)
