"""
build_rail_track.py - modular standard-gauge plant railway track pieces.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_rail_track.py
      (add  -- Straight10  to build one piece only; the layout preview needs a full run)

Assets (Meshes/RailTrackKit/), each a separate .blend/.fbx:
    SM_Track_Straight_10m       straight 10 m
    SM_Track_Straight_2m5       straight 2.5 m filler
    SM_Track_Curve_R190_15deg   190 m radius curve, 15 degrees, turning to +Y
    SM_Turnout_1to9_Left        300 m radius 1:9 turnout, diverging to the left (+Y)
    SM_BufferStop               5 m of track with a fixed buffer stop
    SM_LevelCrossingPanel       10 m of track with concrete crossing panels for a road

All pieces: origin on the track centre line at top of rail (z = 0) at the start of the piece,
track runs along +X. Rail centres at y = +-0.754 (1.435 m gauge, UIC 60-like rail).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm
FOLDER = "RailTrackKit"

RAIL_Y = pl.WHEEL_Y          # rail centre line from track centre
RAIL_H = 0.172               # UIC 60 rail height
SLEEPER_TOP = -RAIL_H - 0.01 # 10 mm rail pad
SLEEPER = (0.26, 2.6, 0.22)  # along track, across, depth (B70 class, estimated)
SLEEPER_STEP = 0.6
FORMATION_Z = -0.65          # bottom of the ballast

# Simplified UIC 60 cross-section (y across, z up), closed loop, top of rail at z = 0
RAIL_PROFILE = [(-0.036, 0.0), (0.036, 0.0), (0.036, -0.05), (0.008, -0.062), (0.008, -0.15),
                (0.075, -0.16), (0.075, -RAIL_H), (-0.075, -RAIL_H), (-0.075, -0.16),
                (-0.008, -0.15), (-0.008, -0.062), (-0.036, -0.05)]
# Ballast top surface (y across, z): shoulder 0.4 m past the sleeper ends, 1:1.5 side slopes
BALLAST_PROFILE = [(-2.375, FORMATION_Z), (-1.7, -0.2), (1.7, -0.2), (2.375, FORMATION_Z)]


# ===========================================================================
# Path helpers: a path is a list of (point, heading_rad) samples along the centre line
# ===========================================================================

def straight_path(length, x0=0.0, y0=0.0, step=2.5):
    n = max(1, int(math.ceil(length / step)))
    return [(Vector((x0 + length * i / n, y0, 0)), 0.0) for i in range(n + 1)]


def arc_path(radius, angle_deg, step=1.0):
    """Arc starting at the origin heading +X, turning left (+Y), centre at (0, radius)."""
    a = math.radians(angle_deg)
    n = max(2, int(math.ceil(radius * a / step)))
    out = []
    for i in range(n + 1):
        t = a * i / n
        out.append((Vector((radius * math.sin(t), radius * (1 - math.cos(t)), 0)), t))
    return out


def offset(path, d):
    """Path shifted sideways by d (positive = left of travel)."""
    return [(p + Vector((-math.sin(h), math.cos(h), 0)) * d, h) for p, h in path]


def clip(path, s0, s1):
    """Part of a path between arc lengths s0 and s1 (approximate, keeps sample points)."""
    out, s = [], 0.0
    for i, (p, h) in enumerate(path):
        if i:
            s += (p - path[i - 1][0]).length
        if s0 - 1e-6 <= s <= s1 + 1e-6:
            out.append((p, h))
    return out


def path_length(path):
    return sum((path[i][0] - path[i - 1][0]).length for i in range(1, len(path)))


# ===========================================================================
# Track builders (add geometry to a Part)
# ===========================================================================

def extrude(p, path, profile, m, closed=True, uv=False):
    """Sweep a 2D (y, z) profile along a path. uv=True: U = metres along, V = metres across."""
    rows, uvs, s = [], [], 0.0
    for i, (c, h) in enumerate(path):
        if i:
            s += (c - path[i - 1][0]).length
        n = Vector((-math.sin(h), math.cos(h), 0))
        prof = profile(c) if callable(profile) else profile
        row = [c + n * y + Vector((0, 0, z)) for y, z in prof]
        if closed:
            row.append(row[0])
        rows.append(row)
        v, vv = 0.0, [0.0]
        for j in range(1, len(row)):
            v += (row[j] - row[j - 1]).length
            vv.append(v)
        uvs.append([(s, x) for x in vv])
    vrows = [[p.bm.verts.new(q) for q in r] for r in rows]
    idx = p._mi(m)
    for i in range(len(vrows) - 1):
        a, b = vrows[i], vrows[i + 1]
        for j in range(len(a) - 1):
            f = p.bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
            f.material_index = idx
            if uv:
                p.uv_faces[f] = [uvs[i][j], uvs[i + 1][j], uvs[i + 1][j + 1], uvs[i][j + 1]]
    return p


def rail(p, path, m):
    extrude(p, path, RAIL_PROFILE, m)


def sleepers(p, path, m, clip_m, length=None, y_shift=0.0):
    """Concrete sleepers every 0.6 m along a path (first one 0.3 m in), with rail clips."""
    L = path_length(path)
    s, i, acc = SLEEPER_STEP / 2, 1, 0.0
    while s < L:
        # walk to the segment holding arc length s
        while i < len(path) - 1 and acc + (path[i][0] - path[i - 1][0]).length < s:
            acc += (path[i][0] - path[i - 1][0]).length
            i += 1
        a, b = path[i - 1], path[i]
        seg = (b[0] - a[0]).length
        t = (s - acc) / seg if seg else 0
        c = a[0].lerp(b[0], t)
        h = a[1] + (b[1] - a[1]) * t
        n = Vector((-math.sin(h), math.cos(h), 0))
        ln = length(c) if callable(length) else SLEEPER[1]
        ys = y_shift(c) if callable(y_shift) else y_shift
        p.box((SLEEPER[0], ln, SLEEPER[2]), c + n * ys + Vector((0, 0, SLEEPER_TOP - SLEEPER[2] / 2)),
              m, rot=(0, 0, math.degrees(h)))
        for r in (RAIL_Y, -RAIL_Y):            # fastening clips both sides of each rail foot
            for d in (0.1, -0.1):
                p.box((0.12, 0.05, 0.04), c + n * (r + d) + Vector((0, 0, SLEEPER_TOP + 0.02)),
                      clip_m, rot=(0, 0, math.degrees(h)))
        s += SLEEPER_STEP


def plain_track(p, path, m, ballast=None):
    """Two rails, sleepers and the ballast bed along a path."""
    for d in (RAIL_Y, -RAIL_Y):
        rail(p, offset(path, d), m['rail'])
    sleepers(p, path, m['sleeper'], m['clip'])
    if ballast is not None:
        extrude(ballast, path, BALLAST_PROFILE, m['ballast'], closed=False, uv=True)


def track_mats():
    return dict(
        rail=pb.mat("M_Rail_Steel", (0.32, 0.29, 0.27), 0.9, 0.45),
        sleeper=pb.mat("M_Concrete_Sleeper", (0.55, 0.54, 0.5), 0.0, 0.85),
        clip=pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5),
        ballast=pb.mat("M_Ballast_Tiling", (0.17, 0.16, 0.15), 0.0, 0.95),
        panel=pb.mat("M_Concrete_Panel", (0.6, 0.59, 0.56), 0.0, 0.8),
        rubber=pb.mat("M_Rubber", (0.03, 0.03, 0.03), 0.0, 0.85),
        yellow=pb.mat("M_Paint_SafetyYellow", (0.85, 0.6, 0.05), 0.2, 0.45),
        red=pb.mat("M_Paint_Red", (0.6, 0.04, 0.03), 0.2, 0.45),
        white=pb.mat("M_Paint_White", (0.8, 0.8, 0.78), 0.1, 0.5),
        grey=pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
    )


def new_piece(name):
    col, ref, _ = pm.start(name)
    return col, ref, track_mats()


def result(name, about, moving, dims, sources, end):
    n_obj, n_tri = pm.counts(name)
    pm.finish_asset(name, FOLDER, [], ground=None)
    return dict(name=name, about=about + f"\n\nConnection: start (0, 0, 0) heading +X; end {end}.",
                n_obj=n_obj, n_tri=n_tri, previews="Preview_TrackKit.png",
                moving=moving, table=pb.pivot_table([name]), dims=dims, sources=sources)


COMMON_DIMS = """
| Item | Value | Source |
|---|---|---|
| Gauge | 1.435 m | Standard |
| Rail | UIC 60 outline simplified to 12 points: 172 mm high, 72 mm head, 150 mm foot | Sourced (UIC 60 / 60E1 nominal sizes) |
| Sleepers | 2.6 x 0.26 x 0.22 m concrete, 0.6 m spacing | Estimated (B70 class) |
| Ballast | Top 3.4 m wide at z -0.20, 1:1.5 slopes to z -0.65 (formation level) | Estimated |
"""


# ===========================================================================
# Pieces
# ===========================================================================

def build_straight(length, name):
    col, ref, m = new_piece(name)
    p, b = pb.Part(name + "_Track"), pb.Part(name + "_Ballast")
    path = straight_path(length)
    plain_track(p, path, m, b)
    p.finish(col)
    b.finish(col, smooth_angle=10)
    return result(name, f"Straight track, {length} m.", "None.", COMMON_DIMS,
                  "rail profile from UIC 60 nominal dimensions; everything else estimated.",
                  f"({length:.2f}, 0, 0) heading +X")


def build_straight10():
    return build_straight(10.0, "SM_Track_Straight_10m")


def build_straight2():
    return build_straight(2.5, "SM_Track_Straight_2m5")


def build_curve():
    name, R, A = "SM_Track_Curve_R190_15deg", 190.0, 15.0
    col, ref, m = new_piece(name)
    p, b = pb.Part(name + "_Track"), pb.Part(name + "_Ballast")
    path = arc_path(R, A)
    plain_track(p, path, m, b)
    p.finish(col)
    b.finish(col, smooth_angle=10)
    e = path[-1][0]
    return result(name, f"190 m radius curve through 15 degrees to the left (+Y), arc length "
                  f"{R * math.radians(A):.2f} m on the centre line. No cant (plant speeds). "
                  "Use it mirrored (scale Y -1) for a right-hand curve.",
                  "None.", COMMON_DIMS + "| Radius | 190 m (common minimum for standard-gauge sidings) | Estimated |\n",
                  "estimated.", f"({e.x:.3f}, {e.y:.3f}, 0) heading 15.0 deg (rotate the next piece by +15 deg about Z)")


# Turnout geometry: diverging centre line is a 300 m arc from the switch toe until it reaches 1:9
TO_R = 300.0
TO_ANGLE = math.degrees(math.atan(1 / 9))       # 6.34 deg
BLADE_L = 12.0                                  # switch blade length, toe to heel (estimated)
THROW = 0.16                                    # tip opening (estimated)
BLADE_ANG = math.degrees(math.asin(THROW / BLADE_L))


def build_turnout():
    name = "SM_Turnout_1to9_Left"
    col, ref, m = new_piece(name)
    p, b = pb.Part(name + "_Track"), pb.Part(name + "_Ballast")
    div = arc_path(TO_R, TO_ANGLE, step=1.0)
    L = div[-1][0].x                             # straight route ends level with the diverging end
    main = straight_path(L, step=1.0)
    # stock rails: right rail of the main route, left (outer) rail of the diverging route
    rail(p, offset(main, -RAIL_Y), m['rail'])
    rail(p, offset(div, RAIL_Y), m['rail'])
    # closure rails from the blade heels to the end: main-route left rail, diverging inner rail
    rail(p, clip(offset(main, RAIL_Y), BLADE_L, L + 1), m['rail'])
    rail(p, clip(offset(div, -RAIL_Y), BLADE_L, 99), m['rail'])
    # frog: where the diverging inner rail crosses the main left rail
    xf = math.sqrt(2 * TO_R * 2 * RAIL_Y)        # small-angle crossing point
    p.box((3.0, 0.32, 0.08), (xf, RAIL_Y, -RAIL_H + 0.04), m['grey'])
    # check (guard) rails opposite the frog, inside the other running rail of each route
    p.box((5.0, 0.07, 0.15), (xf, -RAIL_Y + 0.11, -0.08), m['rail'])
    xg = xf
    yg = TO_R * (1 - math.cos(math.asin(xg / TO_R))) + RAIL_Y - 0.11
    p.box((5.0, 0.07, 0.15), (xg, yg, -0.08), m['rail'], rot=(0, 0, math.degrees(math.asin(xg / TO_R))))
    # long bearers under both routes
    sleepers(p, main, m['sleeper'], m['clip'],
             length=lambda c: 2.6 + max(0.0, TO_R - math.sqrt(max(0, TO_R ** 2 - c.x ** 2))),
             y_shift=lambda c: max(0.0, TO_R - math.sqrt(max(0, TO_R ** 2 - c.x ** 2))) / 2)
    # point machine and drive rod beside the toe, on the right side
    p.box((1.2, 0.5, 0.35), (0.9, -1.75, -0.12), m['yellow'])
    p.cyl_between((0.9, -1.5, -0.12), (0.9, 0.8, -0.12), 0.025, m['clip'], seg=8)
    # one ballast bed under both routes: the left shoulder widens with the diverging offset
    def widened(c):
        w = max(0.0, TO_R - math.sqrt(max(0, TO_R ** 2 - c.x ** 2)))
        return [(-2.375, FORMATION_Z), (-1.7, -0.2), (1.7 + w, -0.2), (2.375 + w, FORMATION_Z)]
    extrude(b, main, widened, m['ballast'], closed=False, uv=True)
    p.finish(col)
    b.finish(col, smooth_angle=10)
    # switch blades, pivot at the heel. Each blade toe tucks one head width (0.072 m) inside its
    # stock rail and runs out to the closure rail line at the heel. Modelled closed, then the
    # right blade is opened for the straight route.
    def tapered(path, d_toe, d_heel):
        out, s = [], 0.0
        for i, (c, h) in enumerate(path):
            if i:
                s += (c - path[i - 1][0]).length
            d = d_toe + (d_heel - d_toe) * min(1.0, s / BLADE_L)
            out.append((c + Vector((-math.sin(h), math.cos(h), 0)) * d, h))
        return out

    bl = pb.Part(name + "_SwitchBlade_L", pivot=(BLADE_L, RAIL_Y, 0))
    rail(bl, tapered(straight_path(BLADE_L, step=1.0), RAIL_Y - 0.072, RAIL_Y), m['rail'])
    bl.finish(col)
    rblade = tapered(clip(div, 0, BLADE_L), -RAIL_Y + 0.072, -RAIL_Y)
    hx = rblade[-1][0]
    br = pb.Part(name + "_SwitchBlade_R", pivot=(hx.x, hx.y, 0))
    rail(br, rblade, m['rail'])
    ob_r = br.finish(col)
    ob_r.rotation_euler.z = math.radians(-BLADE_ANG)     # straight route set: right blade open
    e = div[-1][0]
    moving = (f"| Part | Motion |\n|---|---|\n"
              f"| {name}_SwitchBlade_L | Straight blade beside the left stock rail. Rotates about local Z at its heel. "
              f"Straight route: 0 deg (closed). Diverging route: +{BLADE_ANG:.3f} deg (toe moves {THROW} m toward -Y, open) |\n"
              f"| {name}_SwitchBlade_R | Curved blade beside the right stock rail. Straight route (as exported): "
              f"-{BLADE_ANG:.3f} deg (toe {THROW} m open toward +Y). Diverging route: 0 deg (closed) |\n\n"
              "Throw the two blades together; one is always closed. The exported file is set for the straight route.")
    dims = COMMON_DIMS + (
        "| Diverging radius | 300 m, held until the 1:9 angle (6.34 deg) | Estimated after the common EW 60-300-1:9 type |\n"
        f"| Length | {L:.2f} m (EW 60-300-1:9 is about 33.2 m long, from memory, unverified) | Estimated |\n"
        f"| Switch blades | {BLADE_L} m, throw {THROW} m at the toe | Estimated |\n"
        f"| Frog | crossing point at x = {xf:.2f} m; modelled as crossing rails on a cast block, no flangeway cut-outs | Simplified |\n")
    return result(name, "Left-hand 1:9 turnout. The diverging route leaves to +Y. Bearers lengthen to carry both "
                  "routes. A point machine sits on the right side at the toe. Mirror (scale Y -1) for a right-hand "
                  "turnout and swap the blade signs.", moving, dims, "estimated; see the dimensions table.",
                  f"straight route ({L:.2f}, 0, 0) heading 0 deg; diverging route ({e.x:.2f}, {e.y:.3f}, 0) heading {TO_ANGLE:.2f} deg")


def build_buffer_stop():
    name = "SM_BufferStop"
    col, ref, m = new_piece(name)
    p, b = pb.Part(name + "_Track"), pb.Part(name + "_Ballast")
    plain_track(p, straight_path(5.0), m, b)
    st = pb.Part(name + "_Stop")
    XF = 2.0                                        # buffer faces
    z = pl.BUFFER_Z
    st.box_mm((XF + 0.45, -1.3, z - 0.35), (XF + 0.75, 1.3, z + 0.35), m['red'])          # buffer beam
    for s in (1, -1):
        y = s * pl.BUFFER_Y
        st.cyl(0.13, 0.4, (XF + 0.25, y, z), m['clip'], rot=(0, 90, 0), seg=14)         # buffer casing
        st.cyl(0.22, 0.05, (XF + 0.025, y, z), m['grey'], rot=(0, 90, 0), seg=20)       # buffer head
        for yy in (RAIL_Y,):
            ry = s * yy
            # raking struts from the beam down to clamps on the rails behind
            st.beam_between((XF + 0.6, ry, z - 0.3), (XF + 2.6, ry, -0.05), 0.16, 0.2, m['red'])
            st.beam_between((XF + 0.6, ry, z - 0.3), (XF + 0.6, ry, -0.05), 0.16, 0.16, m['red'])
            st.box((2.4, 0.2, 0.12), (XF + 1.6, ry, -0.03), m['clip'])                   # rail clamp shoe
    for s in (1, -1):                                # yellow/black warning board
        st.box((0.05, 0.6, 0.6), (XF + 0.43, s * 0.35, z + 0.75), m['yellow'])
    st.box((0.04, 0.12, 0.6), (XF + 0.42, 0, z + 0.75), m['clip'])
    st.cyl(0.08, 0.1, (XF + 0.4, 0, z + 1.2), m['red'], rot=(0, 90, 0), seg=14)          # red end lamp
    p.finish(col)
    b.finish(col, smooth_angle=10)
    st.finish(col)
    return result(name, "5 m of track ending in a fixed friction-free buffer stop. Buffer faces at x = 2.0, "
                  f"centres at y +-{pl.BUFFER_Y}, z {pl.BUFFER_Z} (matches the UIC buffers on the rail vehicles).",
                  "None.", COMMON_DIMS + "| Stop frame | beam 2.6 m wide, struts to rail clamps 2.6 m long | Estimated |\n",
                  "estimated.", "none (dead end); track continues to x = 5.0 under the frame")


def build_level_crossing():
    name = "SM_LevelCrossingPanel"
    col, ref, m = new_piece(name)
    p, b = pb.Part(name + "_Track"), pb.Part(name + "_Ballast")
    plain_track(p, straight_path(10.0), m, b)
    pn = pb.Part(name + "_Panels")
    head = 0.036
    fw = 0.07                                       # flangeway on the inside of each rail
    top = -0.005
    for i in range(4):
        x0, x1 = i * 2.5 + 0.01, (i + 1) * 2.5 - 0.01
        # gauge panel between the rails (leaves the flangeways open)
        pn.box_mm((x0, -RAIL_Y + head + fw, SLEEPER_TOP), (x1, RAIL_Y - head - fw, top), m['panel'])
        for s in (1, -1):                           # outer panels 1.2 m wide
            y0 = s * (RAIL_Y + head + 0.01)
            y1 = s * (RAIL_Y + head + 1.21)
            pn.box_mm((x0, min(y0, y1), SLEEPER_TOP), (x1, max(y0, y1), top), m['panel'])
            # rubber flangeway filler strips against the rail web (outside face)
            pn.box_mm((x0, min(y0, s * (RAIL_Y + 0.08)) - 0.0, -0.17), (x1, max(y0, s * (RAIL_Y + 0.08)), -0.05),
                      m['rubber'])
    for s in (1, -1):                               # painted edge lines across the road
        pn.box_mm((0.0, -2.0, top), (0.15, 2.0, top + 0.004), m['white'])
        pn.box_mm((9.85, -2.0, top), (10.0, 2.0, top + 0.004), m['white'])
    p.finish(col)
    b.finish(col, smooth_angle=10)
    pn.finish(col)
    return result(name, "10 m of track (the road runs across it, along Y) with four 2.5 m bays of concrete panels "
                  "flush with the rail top: gauge panels between the rails and 1.2 m outer panels. Road surface "
                  "level z = -0.005; the road must meet the outer panel edges at y = +-2.0.",
                  "None.", COMMON_DIMS + "| Panels | 2.5 m bays, 70 mm flangeways, outer panels 1.2 m | Estimated |\n",
                  "estimated.", "(10.00, 0, 0) heading +X")


BUILDERS = {
    "Straight10": build_straight10,
    "Straight2": build_straight2,
    "Curve": build_curve,
    "Turnout": build_turnout,
    "BufferStop": build_buffer_stop,
    "LevelCrossing": build_level_crossing,
}


# ===========================================================================
# Layout preview: append every saved piece side by side and render once
# ===========================================================================

def layout_preview():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection("Layout")
    d = pm.out_dir(FOLDER)
    spots = [("SM_Track_Straight_10m", (0, 0, 0)), ("SM_Track_Straight_2m5", (12, 0, 0)),
             ("SM_BufferStop", (16, 0, 0)), ("SM_LevelCrossingPanel", (0, -7, 0)),
             ("SM_Track_Curve_R190_15deg", (12, -7, 0)), ("SM_Turnout_1to9_Left", (0, -18, 0))]
    for nm, loc in spots:
        pb.append_asset(os.path.join(d, nm + ".blend"), col, loc, 0)
    pb.ref_human(col, (4, 2.2, -0.2))
    pb.setup_render(res=(1280, 720), samples=32)
    g = pb.Part("REF_Ground")
    g.box_mm((-30, -50, -0.7), (90, 30, -0.65), pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
    g.finish(col)
    pb.render_view(os.path.join(d, "Preview_TrackKit.png"), (-14, 14, 16), (16, -9, 0), 24)


INTRO = """
Modular standard-gauge track for the plant railway (concentrate wagons, acid tank wagons, cathode
flat wagons, ladle and anode transfer cars). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_rail_track.py`. Each piece is its own .blend/.fbx.

Conventions for every piece: origin on the track centre line at top of rail (z = 0) at the start
of the piece; the piece runs along +X. Formation (bottom of ballast) is at z = -0.65, so place the
pieces with their origin 0.65 m above the ground surface, or sink the ground under the ballast.
Each piece has a `_Track` mesh (rails, sleepers, clips) and a `_Ballast` mesh. The ballast has
UVs in metres (U along the track, V across the ballast surface), so a tiling ballast material
with 1 UV = 1 m lines up across pieces. Rails have no UVs (use a triplanar or world-aligned steel
material). Ends are open; pieces join end to end without caps.
"""


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    pm.run(BUILDERS, FOLDER, INTRO)
    if not argv:
        layout_preview()
