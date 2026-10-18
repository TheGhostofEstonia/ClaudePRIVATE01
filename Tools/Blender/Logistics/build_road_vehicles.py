"""
build_road_vehicles.py - road vehicles and trailers for plant logistics, each a prop at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_road_vehicles.py
      (add  -- TipperTrailer  to build one asset only; partial runs leave the README alone)

Assets (Meshes/RoadVehicles/):
    SM_TractorUnit       6x4 semi-trailer tractor
    SM_TipperTrailer     3-axle tipping semi-trailer (concentrate, flux, granulated slag)
    SM_FlatbedTrailer    13.6 m 3-axle flatbed with container twistlocks (cathode bundles, containers)
    SM_AcidTankTrailer   sulphuric acid tank semi-trailer, ~15 m3
    SM_Container20ft     ISO 668 20 ft dry container
    SM_FlatbedTruck      rigid 6x2 drop-side truck for in-plant transport
    SM_SecureVan         armoured cash-in-transit style truck (slimes / dore under security)

All: +X = front / forward travel, origin on the ground. The tractor and every semi-trailer share
one convention: origin = ground point under the kingpin / fifth-wheel centre, so a trailer coupled
to the tractor sits at the same origin as the tractor (straight ahead).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm
FOLDER = "RoadVehicles"

_box_mm = pb.Part.box_mm


def _box_mm_sorted(self, mn, mx, m):
    """box_mm that accepts the two corners in any order (avoids inverted boxes on mirrored sides)."""
    return _box_mm(self, [min(a, b) for a, b in zip(mn, mx)], [max(a, b) for a, b in zip(mn, mx)], m)


pb.Part.box_mm = _box_mm_sorted   # this process only

# Shared road-vehicle numbers
HALF_W = 1.275          # EU max width 2.55 m (Directive 96/53/EC), half
FIFTH_Z = 1.20          # fifth-wheel top / trailer rubbing-plate underside (estimated, typical 1.15-1.25)
TRUCK_R, TRUCK_W = 0.538, 0.315     # 315/80R22.5: 22.5 in rim + 2 x 0.80 x 315 mm = 1.076 m dia
TRAILER_R, TRAILER_W = 0.536, 0.385  # 385/65R22.5: 1.072 m dia
KINGPIN_R = 0.0254      # 2 in kingpin (ISO 337), 50.8 mm diameter


def extra_mats(m):
    """Materials this script adds to the common maintenance set."""
    m['stainless'] = pb.mat("M_Steel_Stainless", (0.7, 0.7, 0.72), 1.0, 0.25)
    m['container'] = pb.mat("M_Paint_ContainerRust", (0.42, 0.12, 0.06), 0.3, 0.6)
    m['armour'] = pb.mat("M_Paint_ArmourGrey", (0.22, 0.24, 0.25), 0.4, 0.5)
    m['taillamp'] = pb.mat("M_Lamp_Tail", (0.6, 0.02, 0.02), 0, 0.3, emit=((1, 0.05, 0.02), 2.0))
    return m


# ===========================================================================
# Shared pieces
# ===========================================================================

def cab_body(p, x0, x1, y0, y1, z0, z1, m, paint, side_glass=True):
    """Cab box from (x0, y0, z0) to (x1, y1, z1): windscreen on +X, headlamps, grille, optional side glass."""
    p.box_mm((x0, y0, z0), (x1, y1, z1), paint)
    p.box_mm((x1 - 0.02, y0 + 0.08, z0 + (z1 - z0) * 0.48), (x1 + 0.01, y1 - 0.08, z1 - 0.12), m['glass'])
    p.box_mm((x1, y0 + 0.4, z0 + 0.25), (x1 + 0.02, y1 - 0.4, z0 + (z1 - z0) * 0.4), m['steel'])  # grille
    for y in (y0 + 0.1, y1 - 0.4):
        p.box_mm((x1 - 0.05, y, z0 + 0.1), (x1 + 0.02, y + 0.3, z0 + 0.25), m['lamp'])
    if side_glass:
        for y in (y0 - 0.01, y1):
            p.box_mm((x1 - 0.95, y, z0 + (z1 - z0) * 0.48), (x1 - 0.2, y + 0.01, z1 - 0.15), m['glass'])
    for s in (1, -1):                                                     # mirror arms + heads
        y = y1 if s > 0 else y0
        p.cyl_between((x1 - 0.1, y, z1 - 0.3), (x1 - 0.1, y + s * 0.3, z1 - 0.3), 0.02, m['steel'], seg=6)
        p.box_mm((x1 - 0.15, y + s * 0.3 - 0.05, z1 - 0.9), (x1 - 0.05, y + s * 0.3 + 0.05, z1 - 0.3), m['steel'])


def cab_door(name, x_rear, x_hinge, y, z0, z1, side, col, m, paint):
    """
    Cab door leaf on the side at y (side +1 = left/+Y, -1 = right/-Y), hinge on the front edge.
    Pivot at (x_hinge, y, z0); opens by rotating about local Z (left door negative, right positive).
    """
    p = pb.Part(name, pivot=(x_hinge, y, z0))
    yo = y + side * 0.03
    p.box_mm((x_rear, min(y, yo), z0), (x_hinge, max(y, yo), z1), paint)
    p.box_mm((x_rear + 0.1, min(yo, yo + side * 0.005), z0 + (z1 - z0) * 0.55),
             (x_hinge - 0.1, max(yo, yo + side * 0.005), z1 - 0.08), m['glass'])
    p.box_mm((x_rear + 0.08, min(yo, yo + side * 0.03), z0 + (z1 - z0) * 0.42),
             (x_rear + 0.25, max(yo, yo + side * 0.03), z0 + (z1 - z0) * 0.46), m['grey'])   # handle
    return p.finish(col)


def trailer_rear(p, x_rear, z_beam, m):
    """Rear underrun bar, light bar with tail lamps and a number-plate panel."""
    p.box_mm((x_rear - 0.05, -1.2, 0.40), (x_rear + 0.10, 1.2, 0.52), m['steel'])        # underrun bar
    for s in (1, -1):
        p.box_mm((x_rear + 0.05, s * 0.85 - 0.06, 0.52), (x_rear + 0.12, s * 0.85 + 0.06, z_beam), m['steel'])
        p.box_mm((x_rear - 0.02, s * 1.0 - 0.15, z_beam - 0.25), (x_rear + 0.02, s * 1.0 + 0.15, z_beam - 0.12),
                 m['taillamp'])
    p.box_mm((x_rear - 0.02, -0.25, z_beam - 0.3), (x_rear + 0.02, 0.25, z_beam - 0.1), m['white'])


def trailer_chassis(p, x_front, x_rear, z_bot, z_top, axles_x, m, paint, side_guard=True):
    """
    Semi-trailer frame: two I-beams x_rear..x_front (z_bot..z_top), cross members, kingpin plate
    and kingpin at x = 0, landing-leg sleeves at x = -2.3, axle hangers and side underrun guards.
    """
    for s in (1, -1):
        p.box_mm((x_rear, s * 0.5 - 0.06, z_bot), (x_front, s * 0.5 + 0.06, z_top), paint)
    n = max(2, int((x_front - x_rear) / 1.0))
    for i in range(n + 1):
        x = x_rear + (x_front - x_rear) * i / n
        p.box((0.08, 2.3, 0.12), (x, 0, z_top - 0.08), m['steel'])
    p.box_mm((min(x_front, 1.2) - 1.6, -0.6, FIFTH_Z), (min(x_front, 1.2), 0.6, FIFTH_Z + 0.02), m['grey'])  # rubbing plate
    p.cyl(KINGPIN_R, 0.084, (0, 0, FIFTH_Z - 0.042), m['grey'], seg=12)                  # kingpin
    p.cyl(0.037, 0.012, (0, 0, FIFTH_Z - 0.078), m['grey'], seg=12)                      # kingpin collar
    for s in (1, -1):                                                                    # landing-leg sleeves
        p.box_mm((-2.38, s * 0.85 - 0.08, 0.75), (-2.22, s * 0.85 + 0.08, z_bot), m['steel'])
        p.cyl_between((-2.3, s * 0.85, 0.95), (-2.3, s * 0.5, z_bot), 0.03, m['steel'], seg=6)
    p.box_mm((-2.34, 0.93, 0.95), (-2.26, 1.15, 1.0), m['grey'])                         # crank handle
    for x in axles_x:
        for s in (1, -1):
            p.box_mm((x - 0.55, s * 0.5 - 0.05, z_bot - 0.35), (x + 0.15, s * 0.5 + 0.05, z_bot), m['steel'])  # hanger
            p.cyl(0.13, 0.28, (x - 0.45, s * 0.5, TRAILER_R + 0.3), m['rubber'], seg=14)   # air bellows
        p.cyl(0.075, 2.05, (x, 0, TRAILER_R), m['grey'], rot=(90, 0, 0), seg=12)           # axle beam
        for s in (1, -1):                                                                  # mudguards
            p.box_mm((x - 0.6, s * 1.065 - 0.22, TRAILER_R + 0.6), (x + 0.6, s * 1.065 + 0.22, TRAILER_R + 0.63),
                     m['rubber'])
    if side_guard:
        for s in (1, -1):
            for z in (0.55, 0.85):
                p.box_mm((max(axles_x) + 0.7, s * 1.22 - 0.02, z), (-2.6, s * 1.22 + 0.02, z + 0.1), m['grey'])
            p.box_mm((max(axles_x) + 0.70, s * 1.22, 0.55), (max(axles_x) + 0.75, s * 0.55, 0.95), m['steel'])
    trailer_rear(p, x_rear, z_bot, m)


def landing_legs(prefix, col, m, z_top):
    """Inner landing legs + sand shoes; pivot at the feet. Slide up along local Z by ~0.30 m when coupled."""
    p = pb.Part(prefix + "_LandingLegs", pivot=(-2.3, 0, 0))
    for s in (1, -1):
        p.box_mm((-2.35, s * 0.85 - 0.055, 0.08), (-2.25, s * 0.85 + 0.055, 0.95), m['grey'])
        p.box_mm((-2.48, s * 0.85 - 0.13, 0.0), (-2.12, s * 0.85 + 0.13, 0.08), m['steel'])
    p.cyl_between((-2.3, 0.85, 0.5), (-2.3, -0.85, 0.5), 0.025, m['steel'], seg=6)          # cross brace
    return p.finish(col)


def trailer_wheels(prefix, axles_x, col, m):
    """Single wide-base 385/65R22.5 tyres on each trailer axle."""
    wheels = []
    for i, x in enumerate(axles_x):
        wheels += pl.road_axle(prefix, x, 1.065, TRAILER_R, TRAILER_W, col, m, label=f"A{i + 1}")
    return wheels


def ref_tractor(ref):
    """Append the saved tractor (if built) into REF for coupled previews. Origins coincide."""
    path = os.path.join(pm.out_dir(FOLDER), "SM_TractorUnit.blend")
    if os.path.exists(path):
        objs = pb.append_asset(path, ref, (0, 0, 0), 0.0, prefix_filter=["TU_"])
        for o in objs.values():           # move into REF so the FBX export of the trailer skips them
            for c in list(o.users_collection):
                if c != ref:
                    c.objects.unlink(o)


def wheel_rows(prefix, axles, extra=""):
    """Markdown motion row for wheels."""
    return f"| {prefix}_Wheel_* | Spin about local Y; {pl.deg_per_metre(TRAILER_R):.1f}°/m travelled{extra} |"


# ===========================================================================
# Tractor unit
# ===========================================================================

def build_tractor_unit():
    name = "SM_TractorUnit"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint = m['blue']
    AX = [3.525, 0.225, -1.125]           # front, drive 1, drive 2 (estimated: 3.30 m + 1.35 m)
    ch = pb.Part("TU_Chassis")
    for s in (1, -1):                                                        # frame rails
        ch.box_mm((-1.95, s * 0.43 - 0.045, 0.75), (4.75, s * 0.43 + 0.045, 1.05), m['steel'])
    for x in (-1.9, -0.5, 1.0, 2.5, 4.0):
        ch.box((0.08, 0.86, 0.2), (x, 0, 0.9), m['steel'])
    ch.box_mm((-0.55, -0.45, 1.05), (0.55, 0.45, FIFTH_Z - 0.08), m['steel'])  # fifth-wheel mount
    ch.box_mm((-0.45, -0.45, FIFTH_Z - 0.08), (0.45, 0.45, FIFTH_Z), m['grey'])  # fifth-wheel plate
    ch.box_mm((-0.46, -0.08, FIFTH_Z - 0.081), (0.0, 0.08, FIFTH_Z + 0.001), m['steel'])  # throat (open rear)
    cab_body(ch, 2.55, 4.85, -1.245, 1.245, 1.15, 3.55, m, paint, side_glass=False)
    ch.poly_prism([(2.55, 3.55), (4.2, 3.55), (2.7, 3.9), (2.55, 3.9)], -1.2, 1.2, paint, plane='XZ')  # roof deflector
    ch.box_mm((4.85, -1.2, 0.45), (5.0, 1.2, 0.85), m['steel'])              # bumper
    for s in (1, -1):                                                        # front arches + steps
        ch.box_mm((AX[0] - 0.65, s * 1.245 - (0.25 if s > 0 else -0.25), 1.15),
                  (AX[0] + 0.65, s * 1.245, 1.25), paint)
        ch.box_mm((2.65, s * 1.17 - 0.07, 0.55), (3.05, s * 1.17 + 0.07, 0.6), m['grey'])
        ch.box_mm((2.65, s * 1.17 - 0.07, 0.85), (3.05, s * 1.17 + 0.07, 0.9), m['grey'])
    ch.cyl(0.33, 1.3, (1.45, 0.82, 0.78), m['galv'], rot=(0, 90, 0), seg=20)  # fuel tank, left
    ch.box_mm((1.0, -1.08, 0.5), (2.3, -0.5, 1.0), m['steel'])               # battery / AdBlue box, right
    ch.cyl(0.13, 0.9, (1.6, -0.8, 1.15), m['grey'], rot=(0, 90, 0), seg=12)  # air tank
    for x in AX[1:]:                                                         # drive axle housings
        ch.cyl(0.12, 1.9, (x, 0, TRUCK_R), m['steel'], rot=(90, 0, 0), seg=14)
        ch.sphere(0.25, (x, 0, TRUCK_R), m['steel'], seg=12)
    ch.cyl(0.09, 2.1, (AX[0], 0, TRUCK_R), m['steel'], rot=(90, 0, 0), seg=12)  # front beam axle
    ch.cyl_between((AX[2], 0, TRUCK_R), (2.4, 0, 0.75), 0.06, m['grey'], seg=10)  # prop shaft
    for s in (1, -1):                                                        # rear mudguards
        ch.box_mm((AX[2] - 0.6, s * 0.87 - 0.38 * 0 - 0.36, 1.13), (AX[1] + 0.6, s * 0.87 + 0.36, 1.16), m['rubber'])
    ch.box_mm((-1.98, -1.1, 0.75), (-1.92, 1.1, 0.95), m['steel'])           # rear light bar
    for s in (1, -1):
        ch.box_mm((-1.99, s * 0.95 - 0.12, 0.8), (-1.97, s * 0.95 + 0.12, 0.9), m['taillamp'])
    ch.cyl_between((2.45, -0.9, 1.2), (2.45, -0.9, 3.6), 0.06, m['grey'], seg=10)  # air intake stack
    ob_ch = ch.finish(col)

    doors = [cab_door("TU_Door_L", 3.35, 4.6, 1.245, 1.35, 3.05, 1, col, m, paint),
             cab_door("TU_Door_R", 3.35, 4.6, -1.245, 1.35, 3.05, -1, col, m, paint)]
    wheels = pl.road_axle("TU", AX[0], 1.04, TRUCK_R, TRUCK_W, col, m, label="A1")
    wheels += pl.road_axle("TU", AX[1], 0.87, TRUCK_R, TRUCK_W, col, m, dual=True, label="A2")
    wheels += pl.road_axle("TU", AX[2], 0.87, TRUCK_R, TRUCK_W, col, m, dual=True, label="A3")
    for o in wheels + doors:
        pm.parent(o, ob_ch)
    pb.ref_human(ref, (3.8, -2.0, 0))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_TractorUnit.png", (10.5, -8.5, 4.0), (1.5, 0, 1.8), 35)])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_TractorUnit.png",
                about="""
Three-axle 6x4 semi-trailer tractor (European cab-over-engine, no branding). Origin is the ground
point under the fifth-wheel centre (kingpin lock). +X is the cab end. Every semi-trailer in this
folder uses the same origin rule, so a coupled trailer is placed at the tractor's origin with the
same rotation; when articulating, rotate the trailer about the vertical line through
(0, 0, 1.20).
""",
                moving=f"""
| Part | Motion |
|---|---|
| TU_Wheel_A1L/R | Spin about local Y and steer about local Z (front axle) |
| TU_Wheel_A2*, A3* | Spin about local Y (twin tyres, drive axles) |
| All wheels | Tyre circumference {2 * math.pi * TRUCK_R:.2f} m: {pl.deg_per_metre(TRUCK_R):.1f}°/m travelled |
| TU_Door_L | Hinge on the front edge: rotate about local Z, negative opens (about -70°) |
| TU_Door_R | Same hinge, positive opens (about +70°) |

Coupling: fifth-wheel top at (0, 0, {FIFTH_Z:.2f}); the throat opens to the rear (-X).
""",
                dims=f"""
| Item | Value | Status |
|---|---|---|
| Width 2.49 m cab, 2.50 m over tyres | EU limit 2.55 m | Limit sourced (Directive 96/53/EC); body estimated |
| Height 3.90 m over roof deflector | EU limit 4.00 m | Limit sourced; model estimated |
| Length 6.95 m, wheelbase 3.30 m + 1.35 m tandem | | Estimated (typical 6x4 tractor) |
| Fifth-wheel height {FIFTH_Z:.2f} m, lead 0.45 m ahead of bogie centre | | Estimated (typical 1.15-1.25 m) |
| Cab back to kingpin 2.55 m | ≥ 2.04 m trailer front swing radius | Radius sourced (96/53/EC); clearance follows |
| Tyres 315/80R22.5, 1.076 m diameter | | Sourced from the tyre size code |
""",
                sources="Council Directive 96/53/EC (maximum dimensions); ISO tyre size designation")


# ===========================================================================
# Tipper trailer
# ===========================================================================

def _aim_matrix(origin, target):
    """World matrix at origin with local +X pointing at target (Z kept up where possible)."""
    origin, target = Vector(origin), Vector(target)
    x = (target - origin).normalized()
    y = Vector((0, 0, 1)).cross(x)
    y = y.normalized() if y.length > 1e-6 else Vector((0, 1, 0))
    z = x.cross(y)
    return Matrix.Translation(origin) @ Matrix((x, y, z)).transposed().to_4x4()


def build_tipper_trailer():
    name = "SM_TipperTrailer"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint, body_paint = m['steel'], m['orange']
    AX = [-4.99, -6.30, -7.61]            # 1.31 m axle spacing (typical air suspension)
    XF, XR = 1.30, -8.00                  # chassis ends
    BX0, BX1 = -7.95, 0.95                # body rear / front
    ZF, ZT = 1.45, 2.75                   # body floor top / side top (1.30 m sides)
    HINGE = Vector((BX0, 0, 1.45))        # rear tipping hinge
    ch = pb.Part("TT_Chassis")
    trailer_chassis(ch, XF, XR, FIFTH_Z, 1.42, AX, m, paint)
    for s in (1, -1):                                                       # hinge brackets
        ch.box_mm((XR, s * 0.9 - 0.06, 1.25), (XR + 0.35, s * 0.9 + 0.06, 1.45), m['grey'])
    ch.box_mm((0.95, -0.3, 1.25), (1.30, 0.3, 1.42), m['grey'])              # hoist cradle
    ob_ch = ch.finish(col)
    legs = landing_legs("TT", col, m, FIFTH_Z)

    bd = pb.Part("TT_Body", pivot=HINGE)
    bd.box_mm((BX0, -1.25, ZF - 0.05), (BX1, 1.25, ZF), body_paint)            # floor
    for s in (1, -1):                                                         # sides + top rail + ribs
        bd.box_mm((BX0, s * 1.25 - (0.03 if s > 0 else 0), ZF), (BX1, s * 1.25 + (0 if s > 0 else 0.03), ZT), body_paint)
        bd.box_mm((BX0, s * 1.245 - 0.04, ZT - 0.08), (BX1, s * 1.245 + 0.04, ZT), m['steel'])
        x = BX0 + 0.5
        while x < BX1:
            bd.box_mm((x - 0.04, s * 1.25 - 0.02, ZF), (x + 0.04, s * 1.25 + 0.02, ZT), body_paint)
            x += 1.1
    bd.box_mm((BX1 - 0.04, -1.25, ZF), (BX1, 1.25, ZT + 0.25), body_paint)     # front wall (raised)
    bd.box_mm((BX1 - 0.04, -1.25, ZT + 0.2), (BX1 + 0.5, 1.25, ZT + 0.25), body_paint)  # anti-spill canopy
    bd.box_mm((BX1, -0.18, ZF), (BX1 + 0.32, 0.18, 3.05), m['steel'])        # hoist doghouse
    for s in (1, -1):
        bd.box_mm((BX0, s * 0.5 - 0.08, ZF - 0.25), (BX1, s * 0.5 + 0.08, ZF - 0.05), m['steel'])  # sub-frame
    bd.box_mm((BX0 + 0.3, -1.3, ZF - 0.1), (BX0 + 0.5, 1.3, ZF), m['steel'])  # rear cross member
    ob_bd = bd.finish(col)

    tg = pb.Part("TT_Tailgate", pivot=(BX0 - 0.04, 0, ZT))
    tg.box_mm((BX0 - 0.06, -1.24, ZF + 0.02), (BX0, 1.24, ZT), body_paint)
    for z in (ZF + 0.35, ZF + 0.85):
        tg.box_mm((BX0 - 0.1, -1.24, z), (BX0 - 0.06, 1.24, z + 0.08), m['steel'])
    for s in (1, -1):
        tg.cyl(0.05, 0.12, (BX0 - 0.04, s * 1.18, ZT), m['grey'], rot=(90, 0, 0), seg=10)  # hinges
    ob_tg = tg.finish(col)

    # Telescopic hoist: 6 stages, retracted 1.65 m from the cradle pin to the body pin
    BASE = Vector((1.15, 0, 1.35))
    TIP = Vector((1.15, 0, 3.00))
    stages = []
    n_st, st_len = 6, 1.55
    for i in range(n_st):
        r = 0.13 - i * 0.012
        p = pb.Part(f"TT_Hoist_Stage{i + 1}", pivot=BASE)
        p.cyl_between(BASE, BASE + Vector((0, 0, st_len)), r, m['grey'] if i else m['steel'], seg=16)
        stages.append(p.finish(col, x_toward=TIP))
    for o in [legs, ob_bd] + trailer_wheels("TT", AX, col, m):
        pm.parent(o, ob_ch)
    pm.parent(ob_tg, ob_bd)
    pb.ref_human(ref, (-3.0, -2.0, 0))

    TIP_ANGLE = -45.0
    def pose():
        """Tipped: body -45° about the rear hinge, tailgate swung +60°, hoist stages re-aimed and extended."""
        ob_bd.rotation_euler.y = math.radians(TIP_ANGLE)
        ob_tg.rotation_euler.y = math.radians(60)
        bpy.context.view_layer.update()
        rel = TIP - HINGE
        a = math.radians(TIP_ANGLE)
        tip = HINGE + Vector((rel.x * math.cos(a) + rel.z * math.sin(a), 0,
                              -rel.x * math.sin(a) + rel.z * math.cos(a)))
        L = (tip - BASE).length
        e = (L - (TIP - BASE).length) / (n_st - 1)
        d = (tip - BASE).normalized()
        for i, ob in enumerate(stages):
            ob.matrix_world = _aim_matrix(BASE + d * (e * i), tip + d * 5)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_TipperTrailer.png", (9, -15, 6), (-4, 0, 1.6), 35),
        ("Preview_TipperTrailer_Tipped.png", (-19, -15, 8), (-3, 0, 3.5), 35, True)], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_TipperTrailer.png, Preview_TipperTrailer_Tipped.png",
                about="""
Three-axle steel tipping semi-trailer, front-tip telescopic hoist, for concentrate, silica flux,
limestone and granulated slag. Origin is the ground point under the kingpin (see SM_TractorUnit);
kingpin at (0, 0, 1.20). +X is the front. The preview stands on its landing legs.
""",
                moving=f"""
| Part | Motion |
|---|---|
| TT_Body | Tips about local Y at the rear hinge (-7.95, 0, 1.45); negative raises the front, about -45° to empty |
| TT_Tailgate | Child of the body, hinge at the top: positive swings the bottom out (+60° in the preview; keep it near vertical in world while tipping) |
| TT_Hoist_Stage1..6 | Telescopic cylinder from (1.15, 0, 1.35) to the body pin (1.15, 0, 3.00) when lowered. Aim each stage's local +X at the body pin's world position; stage i (1-6) slides (i-1)/5 of the extension along +X. Fully tipped the cylinder is about 8.5 m long |
| TT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
{wheel_rows("TT", AX)}
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Kingpin height 1.20 m, 2 in (50.8 mm) kingpin | | Kingpin size sourced (ISO 337); height estimated |
| Kingpin to rear 9.30 m, width 2.50 m, height 3.05 m | EU limits 12.0 m / 2.55 m / 4.0 m | Limits sourced (96/53/EC); model estimated |
| Body 8.9 × 2.5 × 1.3 m, ~27 m³ struck | | Estimated. At 2.0-2.4 t/m³ (concentrate) a ~27 t payload fills only about half of it; flux and slag are lighter |
| Axles 3 × 1.31 m spacing, 385/65R22.5 tyres | | Spacing typical (estimated); tyre size sourced |
| Tip angle 45°, six-stage front hoist | | Estimated |
""",
                sources="Directive 96/53/EC; ISO 337 (kingpin); tyre size code")


# ===========================================================================
# Flatbed trailer
# ===========================================================================

def twistlock_positions():
    """
    Container corner-casting centres on the deck: one 40 ft or two 20 ft (76 mm apart) sharing the
    outer locks. ISO 1161 casting centres: 20 ft 5.853 m, 40 ft 11.985 m, both 2.259 m across.
    """
    xr = -11.98                                   # rear face of the load
    xs = [xr + 0.1025, xr + 6.058 - 0.1025, xr + 6.058 + 0.076 + 0.1025, xr + 12.192 - 0.1025]
    return [(round(x, 4), s * 1.1295) for x in xs for s in (1, -1)]


BUNDLE_X = [-1.95, -3.25, -4.55, -5.85, -7.15, -8.45]
BUNDLE_Y = [0.6, -0.6]


def build_flatbed_trailer():
    name = "SM_FlatbedTrailer"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint = m['steel']
    AX = [-6.39, -7.70, -9.01]
    XF, XR, ZD = 1.60, -12.00, 1.55
    ch = pb.Part("FT_Chassis")
    trailer_chassis(ch, XF, XR, FIFTH_Z, ZD - 0.07, AX, m, paint)
    ch.box_mm((XR, -1.25, ZD - 0.07), (XF, 1.25, ZD), m['wood'])              # timber deck
    for s in (1, -1):                                                        # side raves + stake pockets
        ch.box_mm((XR, s * 1.25 - (0.05 if s > 0 else 0), ZD - 0.3), (XF, s * 1.25 + (0 if s > 0 else 0.05), ZD), paint)
        x = XR + 0.5
        while x < XF:
            ch.box_mm((x - 0.05, s * 1.25 - (0 if s > 0 else 0.06), ZD - 0.25),
                      (x + 0.05, s * 1.25 + (0.06 if s > 0 else 0), ZD - 0.02), m['grey'])
            x += 1.0
    ch.box_mm((XF - 0.05, -1.25, ZD), (XF, 1.25, ZD + 0.12), paint)          # front lip
    tl = twistlock_positions()
    for x, y in tl:
        ch.box((0.14, 0.12, 0.04), (x, y, ZD + 0.02), m['yellow'])
        ch.box((0.08, 0.05, 0.05), (x, y, ZD + 0.065), m['yellow'])
    ob_ch = ch.finish(col)
    legs = landing_legs("FT", col, m, FIFTH_Z)
    for o in [legs] + trailer_wheels("FT", AX, col, m):
        pm.parent(o, ob_ch)
    # REF load: 12 cathode bundles of 30 sheets (1.016 x 0.915 m sheets, ~2 t) on timber runners
    bmat = pb.mat("M_REF_Cathode", (0.75, 0.38, 0.22), 1.0, 0.35)
    for x in BUNDLE_X:
        for y in BUNDLE_Y:
            b = pb.Part(f"REF_CathodeBundle_{x:.2f}_{y:.1f}", pivot=(x, y, ZD))
            b.box((0.915, 1.016, 0.25), (x, y, ZD + 0.08 + 0.125), bmat)
            for dx in (-0.3, 0.3):
                b.box((0.08, 1.0, 0.08), (x + dx, y, ZD + 0.04), m['wood'])
            b.finish(ref)
    pb.ref_human(ref, (-1.0, -2.2, 0))
    ref_tractor(ref)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_FlatbedTrailer.png", (8, -16, 7), (-5, 0, 1.4), 35)])
    tl_rows = "\n".join(f"| ({x:.3f}, {y:.3f}, {ZD:.2f}) |" for x, y in tl)
    grid = ", ".join(f"({x:.2f}, {y:.1f})" for x in BUNDLE_X for y in BUNDLE_Y)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_FlatbedTrailer.png",
                about="""
13.6 m three-axle flatbed semi-trailer with a timber deck, stake pockets and fixed container
twistlocks, for cathode bundles, rod coils, spares and containers. Origin is the ground point under
the kingpin (0, 0, 1.20 kingpin height). +X is the front. The preview shows the tractor
(SM_TractorUnit, REF copy) coupled and twelve REF cathode bundles.
""",
                moving=f"""
| Part | Motion |
|---|---|
| FT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
{wheel_rows("FT", AX)}

Deck top z = {ZD:.2f}. Twistlock centres (one 40 ft, or two 20 ft 76 mm apart; the outer four serve both):

| Twistlock (X, Y, Z) |
|---|
{tl_rows}

Suggested cathode-bundle grid, 2 across × 6 rows (12 bundles ≈ 24 t), bundle centres (X, Y) on the
deck: {grid}. The rows sit between the kingpin and the axles so the load is shared. Bundles are
strapped down through the stake pockets.
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Length 13.60 m, kingpin to rear 12.00 m, front radius 1.60 m | EU limits 12.0 m and 2.04 m | Limits sourced (96/53/EC); model at the limit |
| Width 2.50 m, deck height 1.55 m | | Estimated (typical 1.45-1.60 m) |
| Twistlock layout | ISO 1161 casting centres 5.853 / 11.985 × 2.259 m | Sourced |
| Cathode bundle 1.016 × 0.915 m sheets, 30 per bundle ≈ 2.0 t | | From the project's cathode size (Meshes/CathodeBundlingLine) |
| Payload ~24-28 t | | Estimated (40-44 t gross combination) |
""",
                sources="Directive 96/53/EC; ISO 1161 / ISO 668 (container fittings); tyre size code")


# ===========================================================================
# Acid tank trailer
# ===========================================================================

def build_acid_tank_trailer():
    name = "SM_AcidTankTrailer"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint, tank_m = m['steel'], m['stainless']
    AX = [-5.70, -7.01, -8.32]
    XF, XR = 1.30, -8.90
    TR, TZ = 0.80, 2.35                    # tank radius, axis height
    TX0, TX1 = -7.90, 0.60                 # tank cylinder ends (heads extend 0.25 m beyond)
    ch = pb.Part("AT_Chassis")
    trailer_chassis(ch, XF, XR, FIFTH_Z, 1.45, AX, m, paint)
    for x in (0.2, -2.5, -5.0, -7.6):                                        # tank saddles
        ch.box_mm((x - 0.15, -0.75, 1.45), (x + 0.15, 0.75, TZ - TR + 0.2), paint)
    ob_ch = ch.finish(col)
    legs = landing_legs("AT", col, m, FIFTH_Z)

    tk = pb.Part("AT_Tank")
    tk.cyl(TR, TX1 - TX0, ((TX0 + TX1) / 2, 0, TZ), tank_m, rot=(0, 90, 0), seg=36)
    tk.cyl(TR, 0.25, (TX1 + 0.125, 0, TZ), tank_m, rot=(0, 90, 0), seg=36, r2=TR * 0.55)   # dished heads
    tk.cyl(TR * 0.55, 0.25, (TX0 - 0.125, 0, TZ), tank_m, rot=(0, 90, 0), seg=36, r2=TR)
    for x in (TX0 + 0.3, -3.65, TX1 - 0.3):                                  # stiffening rings
        tk.cyl(TR + 0.02, 0.08, (x, 0, TZ), m['grey'], rot=(0, 90, 0), seg=36)
    MX = -3.65                                                               # manway
    tk.cyl(0.28, 0.15, (MX, 0, TZ + TR + 0.04), tank_m, seg=24)
    tk.cyl(0.07, 0.25, (MX - 0.6, 0, TZ + TR + 0.1), m['grey'], seg=12)      # top loading valve
    tk.cyl(0.05, 0.3, (MX + 0.6, 0, TZ + TR + 0.12), m['grey'], seg=10)      # vent / relief valve
    tk.box_mm((-6.2, -0.22, TZ + TR - 0.02), (-1.1, 0.22, TZ + TR + 0.02), m['galv'])   # walkway grating
    tk.cyl_between((TX0 + 1.0, 0, TZ - TR - 0.05), (TX0 - 0.15, 0, TZ - TR - 0.05), 0.05, m['grey'], seg=10)  # bottom outlet
    for z in [0.6 + 0.3 * i for i in range(int((TZ + TR - 0.6) / 0.3) + 1)]:  # rear ladder
        tk.cyl_between((TX0 - 0.4, -0.2, z), (TX0 - 0.4, 0.2, z), 0.016, m['galv'], seg=6)
    for s in (1, -1):
        tk.cyl_between((TX0 - 0.4, s * 0.2, 0.6), (TX0 - 0.4, s * 0.2, TZ + TR + 0.05), 0.025, m['galv'], seg=8)
    ob_tk = tk.finish(col)

    ml = pb.Part("AT_ManwayLid", pivot=(MX - 0.28, 0, TZ + TR + 0.115))
    ml.cyl(0.29, 0.04, (MX, 0, TZ + TR + 0.135), tank_m, seg=24)
    for a in range(0, 360, 60):
        ml.cyl(0.02, 0.08, (MX + 0.25 * math.cos(math.radians(a)), 0.25 * math.sin(math.radians(a)), TZ + TR + 0.16),
               m['grey'], seg=6)
    ob_ml = ml.finish(col)
    hr = pb.Part("AT_Handrail", pivot=(-3.65, 0.24, TZ + TR + 0.02))
    for y in (0.24, -0.24):
        hr.cyl_between((-6.1, y, TZ + TR + 1.0), (-1.2, y, TZ + TR + 1.0), 0.022, m['yellow'], seg=8)
        for x in (-6.1, -4.5, -2.8, -1.2):
            hr.cyl_between((x, y, TZ + TR + 0.02), (x, y, TZ + TR + 1.0), 0.022, m['yellow'], seg=8)
    ob_hr = hr.finish(col)
    vc = pb.Part("AT_ValveCabinet")
    vc.box_mm((XR + 0.1, -0.6, 0.85), (XR + 0.7, 0.6, 1.4), m['white'])
    ob_vc = vc.finish(col)
    vd = pb.Part("AT_ValveCabinetDoor", pivot=(XR + 0.1, 0.6, 0.85))
    vd.box_mm((XR + 0.07, -0.58, 0.87), (XR + 0.1, 0.6, 1.38), m['white'])
    ob_vd = vd.finish(col)
    for o in [legs, ob_tk, ob_vc] + trailer_wheels("AT", AX, col, m):
        pm.parent(o, ob_ch)
    for o in (ob_ml, ob_hr):
        pm.parent(o, ob_tk)
    pm.parent(ob_vd, ob_vc)
    pb.ref_human(ref, (-2.5, -2.2, 0))
    vol = math.pi * TR ** 2 * (TX1 - TX0) + 2 * math.pi * 0.25 / 3 * (TR ** 2 + TR * TR * 0.55 + (TR * 0.55) ** 2)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_AcidTankTrailer.png", (8, -14, 6), (-3.5, 0, 1.8), 35)])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_AcidTankTrailer.png",
                about="""
Three-axle sulphuric acid tank semi-trailer: a small-diameter stainless (or rubber-lined steel)
barrel because concentrated acid is dense, top manway with loading and vent valves, top walkway
with a fold-down handrail, rear ladder and a rear valve cabinet over the bottom outlet. Origin is
the ground point under the kingpin (kingpin at (0, 0, 1.20)). +X is the front.
""",
                moving=f"""
| Part | Motion |
|---|---|
| AT_ManwayLid | Hinge on its -X edge: rotate about local Y, negative opens (about -110°) |
| AT_Handrail | Raised in the model; fold flat by rotating about local X by about 90° (road travel) |
| AT_ValveCabinetDoor | Hinge on the left (+Y) edge: rotate about local Z, positive opens |
| AT_LandingLegs | Slide up along local Z about 0.30 m when coupled |
{wheel_rows("AT", AX)}

Loading point: manway / top loading valve at ({MX:.2f}, 0, {TZ + TR + 0.15:.2f}). Unloading point:
bottom outlet in the valve cabinet, ({TX0 - 0.15:.2f}, 0, {TZ - TR - 0.05:.2f}).
""",
                dims=f"""
| Item | Value | Status |
|---|---|---|
| Tank 1.60 m diameter × 8.5 m over heads, ≈{vol:.1f} m³ gross | | Estimated |
| Payload check: 98 % H2SO4 is about 1.84 t/m³, so {vol:.1f} m³ ≈ {vol * 1.84:.0f} t | | Density sourced (standard value); payload estimated, near a 40-44 t combination limit |
| Height 3.95 m over the raised handrail (3.15 m folded at the tank top) | EU limit 4.0 m | Estimated |
| Kingpin to rear 8.9 m | | Estimated |
""",
                sources="Directive 96/53/EC; sulphuric acid density (CRC Handbook value, 98 % ≈ 1.84 g/cm³)")


# ===========================================================================
# ISO 20 ft container
# ===========================================================================

def build_container_20ft():
    name = "SM_Container20ft"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint = m['container']
    L, W, H = 6.058, 2.438, 2.591          # ISO 668 1CC external
    hx, hy = L / 2, W / 2
    bd = pb.Part("C20_Body")
    bd.box_mm((-hx, -hy, 0.0), (hx, hy, 0.16), paint)                        # bottom side rails + floor
    bd.box_mm((-hx + 0.05, -hy + 0.05, 0.16), (hx - 0.05, hy - 0.05, 0.19), m['wood'])
    bd.box_mm((-hx, -hy, H - 0.1), (hx, hy, H - 0.02), paint)                # top rails + roof
    bd.box_mm((-hx + 0.1, -hy + 0.05, H - 0.02), (hx - 0.1, hy - 0.05, H - 0.005), paint)
    for x in (-hx, hx - 0.12):                                               # corner posts
        for y in (-hy, hy - 0.12):
            bd.box_mm((x, y, 0.1), (x + 0.12, y + 0.12, H - 0.1), paint)
    for s in (1, -1):                                                        # corrugated side walls
        y = s * (hy - 0.03)
        bd.box_mm((-hx + 0.12, y - 0.01, 0.16), (hx - 0.12, y + 0.01, H - 0.1), paint)
        x = -hx + 0.2
        while x < hx - 0.2:
            bd.box_mm((x, y + s * 0.01, 0.16), (x + 0.14, y + s * 0.036, H - 0.1), paint)
            x += 0.278
    bd.box_mm((hx - 0.04, -hy + 0.12, 0.16), (hx - 0.02, hy - 0.12, H - 0.1), paint)  # front end wall
    for y in (-0.9, -0.45, 0.0, 0.45, 0.9):
        bd.box_mm((hx - 0.02, y - 0.07, 0.16), (hx, y + 0.07, H - 0.1), paint)
    bd.box_mm((-hx, -hy, H - 0.26), (-hx + 0.12, hy, H - 0.1), paint)          # door header
    bd.box_mm((-hx, -hy, 0.0), (-hx + 0.12, hy, 0.25), paint)                # door sill
    for x in (-hx + 0.089, hx - 0.089):                                      # corner castings (ISO 1161)
        for y in (-hy + 0.081, hy - 0.081):
            for z in (0.059, H - 0.059):
                bd.box((0.178, 0.162, 0.118), (x, y, z), m['steel'])
    for x in (-1.03, 1.03):                                                  # forklift pockets
        for s in (1, -1):
            bd.box_mm((x - 0.18, s * hy - (0.01 if s > 0 else -0.01) - 0.005, 0.02), (x + 0.18, s * hy + 0.005, 0.12), m['steel'])
    ob_bd = bd.finish(col)

    doors = []
    for side, t in ((1, "L"), (-1, "R")):
        hy_d = side * (hy - 0.06)
        p = pb.Part(f"C20_Door_{t}", pivot=(-hx - 0.02, hy_d, 0.25))
        yo, yi = hy_d, side * 0.005
        p.box_mm((-hx - 0.04, min(yo, yi), 0.25), (-hx, max(yo, yi), H - 0.26), paint)
        for z in (0.6, 1.3, 2.0):
            p.box_mm((-hx - 0.06, min(yo, yi), z), (-hx - 0.04, max(yo, yi), z + 0.06), paint)
        for fy in (0.3, 0.75):                                               # locking bars + cams
            y = side * (hy - 0.06 - fy * (hy - 0.06))
            p.cyl_between((-hx - 0.07, y, 0.2), (-hx - 0.07, y, H - 0.2), 0.016, m['grey'], seg=8)
            p.box_mm((-hx - 0.12, y - 0.02, 1.15), (-hx - 0.07, y + 0.02, 1.4), m['grey'])
        for z in (0.45, 1.3, 2.15):                                          # hinges
            p.cyl(0.03, 0.1, (-hx - 0.02, hy_d, z), m['steel'], seg=8)
        doors.append(p.finish(col))
        pm.parent(doors[-1], ob_bd)
    pb.ref_human(ref, (-4.0, -1.8, 0))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_Container20ft.png", (-7.0, -6.0, 3.8), (0, 0, 1.2), 35)])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_Container20ft.png",
                about="""
ISO 668 type 1CC 20 ft dry freight container with corrugated walls, corner castings, forklift
pockets and two hinged doors at the -X end. Origin is the ground point under the centre of the
container (bottom of the corner castings at z = 0). It fits the twistlocks of SM_FlatbedTrailer
(corner castings at ±2.9265 m along X, ±1.1295 m along Y from the origin).
""",
                moving="""
| Part | Motion |
|---|---|
| C20_Door_L (+Y leaf) | Hinge on the outer edge: rotate about local Z, negative opens, up to -270° flat against the side |
| C20_Door_R (-Y leaf) | Same, positive opens, up to +270° |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| External 6.058 × 2.438 × 2.591 m | | Sourced (ISO 668, 1CC) |
| Corner castings 178 × 162 × 118 mm, centres 5.853 × 2.259 m | | Sourced (ISO 1161) |
| Max gross 30.48 t (newer ratings 36 t), tare ≈2.2 t | | Sourced (ISO 668 rating); tare typical |
| Corrugation pitch 0.278 m, forklift pockets at ±1.03 m | | Estimated |
""",
                sources="ISO 668 (series 1 freight containers); ISO 1161 (corner fittings)")


# ===========================================================================
# Rigid flatbed truck
# ===========================================================================

def build_flatbed_truck():
    name = "SM_FlatbedTruck"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint = m['white']
    AX = [3.50, -1.60, -2.95]             # steer, drive (twin), tag (single)
    ZD, SH = 1.40, 0.60                   # deck top, drop-side height
    DX0, DX1 = -4.70, 2.70                # deck rear / front
    ch = pb.Part("FB_Chassis")
    for s in (1, -1):
        ch.box_mm((-4.8, s * 0.43 - 0.045, 0.75), (4.75, s * 0.43 + 0.045, 1.05), m['steel'])
    cab_body(ch, 2.85, 4.85, -1.245, 1.245, 1.15, 3.20, m, paint)
    ch.box_mm((4.85, -1.2, 0.45), (5.0, 1.2, 0.85), m['steel'])
    ch.box_mm((DX0, -1.25, 1.05), (DX1, 1.25, ZD - 0.04), m['steel'])        # deck frame
    ch.box_mm((DX0, -1.24, ZD - 0.04), (DX1, 1.24, ZD), m['wood'])
    ch.box_mm((DX1 - 0.08, -1.25, ZD), (DX1, 1.25, ZD + 1.2), m['steel'])    # headboard
    ch.cyl(0.3, 1.1, (0.8, 0.85, 0.75), m['galv'], rot=(0, 90, 0), seg=20)   # fuel tank
    ch.box_mm((0.3, -1.05, 0.5), (1.6, -0.5, 1.0), m['steel'])
    ch.cyl(0.12, 1.9, (AX[1], 0, TRUCK_R), m['steel'], rot=(90, 0, 0), seg=14)
    ch.sphere(0.25, (AX[1], 0, TRUCK_R), m['steel'], seg=12)
    ch.cyl(0.08, 2.0, (AX[2], 0, TRUCK_R), m['steel'], rot=(90, 0, 0), seg=12)
    ch.cyl(0.09, 2.1, (AX[0], 0, TRUCK_R), m['steel'], rot=(90, 0, 0), seg=12)
    ch.cyl_between((AX[1], 0, TRUCK_R), (2.7, 0, 0.75), 0.06, m['grey'], seg=10)
    ch.box_mm((-4.85, -1.2, 0.45), (-4.75, 1.2, 0.55), m['steel'])           # rear underrun
    for s in (1, -1):
        ch.box_mm((-4.86, s * 1.0 - 0.15, 0.85), (-4.8, s * 1.0 + 0.15, 0.95), m['taillamp'])
    ob_ch = ch.finish(col)

    sides = []
    for s, t in ((1, "L"), (-1, "R")):                                       # drop sides, 2 panels each
        y = s * 1.24
        for k, (x0, x1) in enumerate(((-1.0, DX1 - 0.08), (DX0, -1.0))):
            p = pb.Part(f"FB_DropSide_{t}{k + 1}", pivot=((x0 + x1) / 2, y, ZD))
            p.box_mm((x0 + 0.01, min(y, y - s * 0.04), ZD), (x1 - 0.01, max(y, y - s * 0.04), ZD + SH), m['galv'])
            p.box_mm((x0 + 0.01, min(y, y + s * 0.02), ZD + SH - 0.06), (x1 - 0.01, max(y, y + s * 0.02), ZD + SH), m['grey'])
            sides.append(p.finish(col))
    tg = pb.Part("FB_Tailgate", pivot=(DX0, 0, ZD))
    tg.box_mm((DX0 - 0.04, -1.24, ZD), (DX0, 1.24, ZD + SH), m['galv'])
    ob_tg = tg.finish(col)
    doors = [cab_door("FB_Door_L", 3.35, 4.6, 1.245, 1.35, 2.85, 1, col, m, paint),
             cab_door("FB_Door_R", 3.35, 4.6, -1.245, 1.35, 2.85, -1, col, m, paint)]
    wheels = pl.road_axle("FB", AX[0], 1.04, TRUCK_R, TRUCK_W, col, m, label="A1")
    wheels += pl.road_axle("FB", AX[1], 0.87, TRUCK_R, TRUCK_W, col, m, dual=True, label="A2")
    wheels += pl.road_axle("FB", AX[2], 1.04, TRUCK_R, TRUCK_W, col, m, label="A3")
    for o in sides + [ob_tg] + doors + wheels:
        pm.parent(o, ob_ch)
    pb.ref_human(ref, (-5.6, -1.2, 0))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_FlatbedTruck.png", (-9, -10, 5), (-0.5, 0, 1.5), 35)])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_FlatbedTruck.png",
                about="""
Rigid 6x2 drop-side flatbed truck (day cab, rear tag axle) for in-plant moves of spares, cathode
bundles and pallets. Origin is the ground point at the middle of the chassis. +X is the cab end.
Deck 7.4 × 2.48 m, top at z = 1.40; room for 2 × 6 cathode bundles by area, but the payload
(about 14 t) limits it to about 6-7 bundles.
""",
                moving=f"""
| Part | Motion |
|---|---|
| FB_DropSide_L1/L2 | Hinge on the bottom edge: rotate about local X, negative drops the side outward (about -100°) |
| FB_DropSide_R1/R2 | Same, positive drops outward |
| FB_Tailgate | Hinge on the bottom edge: rotate about local Y, negative drops it rearward |
| FB_Door_L / _R | Cab doors, hinge at the front edge: rotate about local Z, L negative, R positive |
| FB_Wheel_A1L/R | Spin and steer (local Z) |
| All wheels | Spin about local Y, {pl.deg_per_metre(TRUCK_R):.1f}°/m. A3 (tag) can be lifted 0.15 m along Z when empty |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Length 9.85 m, width 2.50 m, cab height 3.20 m | | Estimated (typical 26 t 6x2 rigid) |
| Deck 7.4 × 2.48 m at 1.40 m, drop sides 0.60 m | | Estimated |
| Gross 26 t, payload ≈14 t | EU 3-axle rigid 26 t (with drive-axle conditions) | Limit sourced (96/53/EC); payload estimated |
| Tyres 315/80R22.5 | | Sourced from the size code |
""",
                sources="Directive 96/53/EC")


# ===========================================================================
# Armoured secure van
# ===========================================================================

def build_secure_van():
    name = "SM_SecureVan"
    col, ref, m = pm.start(name)
    extra_mats(m)
    paint = m['armour']
    R, W = 0.433, 0.265                    # 265/70R19.5
    AX = [2.50, -1.40]
    BX0, BX1, BZ0, BZ1, HY = -3.80, 1.85, 0.95, 3.25, 1.20
    ch = pb.Part("SV_Chassis")
    for s in (1, -1):
        ch.box_mm((-3.9, s * 0.4 - 0.04, 0.6), (3.7, s * 0.4 + 0.04, 0.9), m['steel'])
    cab_body(ch, 1.90, 3.70, -1.13, 1.13, 0.85, 2.95, m, paint)
    ch.box_mm((3.7, -1.05, 0.4), (3.95, 1.05, 0.8), m['steel'])              # bull bar / bumper
    for z in (0.95, 1.25):
        ch.cyl_between((3.95, -1.0, z), (3.95, 1.0, z), 0.04, m['steel'], seg=8)
    ch.box_mm((BX0, -HY, BZ0), (BX1, HY, BZ1), paint)                        # armoured body
    ch.box_mm((BX0 - 0.02, -HY - 0.02, BZ1 - 0.05), (BX1 + 0.02, HY + 0.02, BZ1 + 0.03), m['steel'])  # roof edge
    ch.sphere(0.18, (-0.5, 0, BZ1 + 0.02), m['glass'], seg=12)               # roof camera dome
    ch.box_mm((0.6, -0.3, BZ1), (1.2, 0.3, BZ1 + 0.12), m['steel'])         # roof hatch
    for s in (1, -1):                                                        # small armoured windows + gun ports
        y = s * (HY + 0.005)
        ch.box_mm((0.4, min(y, y + s * 0.01), 2.2), (0.9, max(y, y + s * 0.01), 2.5), m['glass'])
        for x in (-2.8, -1.0):
            ch.cyl(0.06, 0.03, (x, s * (HY + 0.012), 1.9), m['steel'], rot=(90, 0, 0), seg=12)
        ch.box_mm((-3.6, s * HY - (0.03 if s > 0 else -0.03), 0.6), (1.6, s * HY + (0 if s > 0 else 0), 0.95), m['steel'])  # skirt
    ch.cyl(0.12, 1.9, (AX[1], 0, R), m['steel'], rot=(90, 0, 0), seg=14)
    ch.cyl(0.08, 1.9, (AX[0], 0, R), m['steel'], rot=(90, 0, 0), seg=12)
    ch.box_mm((-4.0, -0.8, 0.5), (-3.8, 0.8, 0.6), m['grey'])                # rear step
    for s in (1, -1):
        ch.box_mm((-3.82, s * 1.0 - 0.1, 1.0), (-3.8, s * 1.0 + 0.1, 1.15), m['taillamp'])
    ob_ch = ch.finish(col)

    parts = []
    for side, t in ((1, "L"), (-1, "R")):                                    # rear double doors
        yh = side * (HY - 0.02)
        p = pb.Part(f"SV_RearDoor_{t}", pivot=(BX0, yh, 1.05))
        p.box_mm((BX0 - 0.06, min(yh, 0.005 * side), 1.05), (BX0, max(yh, 0.005 * side), BZ1 - 0.1), paint)
        p.cyl(0.05, 0.03, (BX0 - 0.07, side * 0.55, 2.0), m['steel'], rot=(0, 90, 0), seg=12)   # gun port
        p.box_mm((BX0 - 0.1, side * 0.1 - 0.03, 1.8), (BX0 - 0.06, side * 0.1 + 0.03, 2.0), m['grey'])  # handle
        parts.append(p.finish(col))
    sd = pb.Part("SV_SideDoor", pivot=(1.20, -HY, 1.05))                     # right-hand crew door
    sd.box_mm((0.30, -HY - 0.05, 1.05), (1.20, -HY, 2.95), paint)
    sd.box_mm((0.45, -HY - 0.06, 2.3), (1.05, -HY - 0.05, 2.6), m['glass'])
    sd.cyl(0.05, 0.03, (0.75, -HY - 0.06, 1.9), m['steel'], rot=(90, 0, 0), seg=12)
    parts.append(sd.finish(col))
    wheels = pl.road_axle("SV", AX[0], 0.95, R, W, col, m, label="A1")
    wheels += pl.road_axle("SV", AX[1], 0.80, R, W, col, m, dual=True, label="A2")
    for o in parts + wheels:
        pm.parent(o, ob_ch)
    pb.ref_human(ref, (-4.6, -1.5, 0))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_SecureVan.png", (-8.5, -8.5, 4.0), (-0.3, 0, 1.6), 35)])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_SecureVan.png",
                about="""
Armoured cash-in-transit style truck on a two-axle 7.5-12 t chassis, for moving anode slimes,
doré bars and precious-metal samples under security. Plain armour grey, no branding. Armoured
body with small windows, gun ports, roof camera dome and hatch, rear double doors and a crew door
on the right. Origin is the ground point at the middle of the vehicle. +X is the cab end.
""",
                moving=f"""
| Part | Motion |
|---|---|
| SV_RearDoor_L (+Y leaf) | Hinge on the outer edge: rotate about local Z, negative opens (up to about -180°) |
| SV_RearDoor_R (-Y leaf) | Same, positive opens |
| SV_SideDoor | Hinge on the front edge: rotate about local Z, positive opens outward (about +90°) |
| SV_Wheel_A1L/R | Spin and steer (local Z) |
| All wheels | 265/70R19.5, spin about local Y, {pl.deg_per_metre(R):.1f}°/m |

Cab doors are modelled closed (part of SV_Chassis).
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Length 7.75 m, width 2.40 m, height 3.25 m (3.45 m over the dome) | | Estimated (typical 12 t CIT truck) |
| Wheelbase 3.90 m, 265/70R19.5 tyres | | Estimated; tyre diameter from the size code |
| Gun ports, window sizes, door layout | | Own design |
""",
                sources="no specific vehicle; general CIT truck proportions")


# ===========================================================================
# README
# ===========================================================================

BUILDERS = dict(TractorUnit=build_tractor_unit, TipperTrailer=build_tipper_trailer,
                FlatbedTrailer=build_flatbed_trailer, AcidTankTrailer=build_acid_tank_trailer,
                Container20ft=build_container_20ft, FlatbedTruck=build_flatbed_truck,
                SecureVan=build_secure_van)

INTRO = """
Road vehicles for plant logistics: inbound concentrate, flux and reagents, outbound cathode,
acid and slimes. Each asset is a standalone prop at its own origin (not tied to the plant
layout). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_road_vehicles.py`. Brand names are size references only; the models
carry no logos. In the .blend the moving parts are parented for posing.

Coupling rule: the tractor's origin is the ground point under its fifth-wheel centre, and each
semi-trailer's origin is the ground point under its kingpin. Placing a trailer at the tractor's
origin couples it (fifth-wheel top and kingpin rubbing plate both at z = 1.20 m). For a turning
combination, rotate the trailer about the vertical axis through that point.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
