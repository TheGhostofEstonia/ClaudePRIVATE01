"""
build_rail_vehicles.py - plant railway rolling stock, each a standalone asset at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_rail_vehicles.py
      (add  -- HopperWagon  to build one asset only)

Assets (Meshes/RailVehicles/):
    SM_ShuntingLocomotive  4-axle diesel-hydraulic road switcher, G1206 size class
    SM_HopperWagon         covered bottom-discharge hopper wagon for concentrate
    SM_SideTipWagon        air-operated side-tipping wagon (flux, reverts, slag)
    SM_FlatWagon           19.9 m bogie flat wagon (Res class) for cathode bundles / containers
    SM_AcidTankWagon       sulphuric acid tank wagon, top discharge

All: origin on the track centre line at top of rail (z = 0), +X = A end, standard gauge.
"""
import math
import os
import sys

import bmesh
import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm
FOLDER = "RailVehicles"


# ===========================================================================
# Shared helpers for this script
# ===========================================================================

def fix_normals(p):
    """Recalculate outward normals on a Part that uses poly_prism (winding varies)."""
    bmesh.ops.recalc_face_normals(p.bm, faces=p.bm.faces[:])


def ref_track(ref, half_len):
    """Non-exported REF track under the vehicle: two rails and sleepers at 0.6 m pitch."""
    p = pb.Part("REF_Track")
    rail = pb.mat("M_REF_Rail", (0.35, 0.33, 0.3), 0.8, 0.5)
    sleeper = pb.mat("M_REF_Sleeper", (0.45, 0.44, 0.42), 0.0, 0.9)
    for s in (1, -1):
        p.box_mm((-half_len, s * pl.WHEEL_Y - 0.036, -0.172), (half_len, s * pl.WHEEL_Y + 0.036, 0.0), rail)
    n = int(2 * half_len / 0.6)
    for i in range(n + 1):
        x = -half_len + i * 0.6
        p.box((0.26, 2.6, 0.2), (x, 0, -0.27), sleeper)
    return p.finish(ref)


def side_view(L, h=4.5):
    """Standard three-quarter view for a vehicle of length L."""
    return (L * 0.75, -L * 0.85, h), (0, 0, 1.8), 35.0


def result(name, about, previews, moving, dims, sources):
    n_obj, n_tri = pm.counts(name)
    return dict(name=name, about=about, previews=previews, moving=moving, dims=dims,
                sources=sources, n_obj=n_obj, n_tri=n_tri, table=_TABLE[name])


_TABLE = {}


def windows(p, x0, x1, y0, y1, z0, z1, m, faces):
    """Glass panes on the faces of a cab box. faces: subset of '+x', '-x', '+y', '-y'."""
    g = m['glass']
    if '+x' in faces:
        p.box_mm((x1 - 0.01, y0 + 0.15, z0), (x1 + 0.01, y1 - 0.15, z1), g)
    if '-x' in faces:
        p.box_mm((x0 - 0.01, y0 + 0.15, z0), (x0 + 0.01, y1 - 0.15, z1), g)
    if '+y' in faces:
        p.box_mm((x0 + 0.2, y1 - 0.01, z0), (x1 - 0.2, y1 + 0.01, z1), g)
    if '-y' in faces:
        p.box_mm((x0 + 0.2, y0 - 0.01, z0), (x1 - 0.2, y0 + 0.01, z1), g)


# ===========================================================================
# Shunting locomotive
# ===========================================================================

def build_shunting_locomotive():
    name = "SM_ShuntingLocomotive"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    LOB = 14.70                     # length over buffers (sourced)
    HW = 1.50                       # half deck width; 3.08 m over handrails (sourced)
    R = 0.50                        # wheel radius, 1,000 mm new (sourced)
    BOGIE_X = 3.60                  # bogie centres 7.20 m apart (sourced, single source)
    WB = 2.40                       # bogie wheelbase (sourced, single source)
    FZ = 1.45                       # top of frame / walkway (estimated)
    ROOF = 4.22                     # height over cab roof (sourced)

    b = pb.Part("SL_Body")
    pl.underframe(b, -7.05, 7.05, FZ, m, m['steel'], width=3.0)
    b.box_mm((-7.1, -HW, FZ), (7.1, HW, FZ + 0.05), m['steel'])                 # walkway plate
    for d in (1, -1):
        pl.buffers_and_coupling(b, d * LOB / 2, d, m, m['red'])
    # long hood (engine, transmission, cooling group)
    b.box_mm((-6.6, -1.1, FZ + 0.05), (1.3, 1.1, 3.55), paint)
    b.box_mm((-6.4, -1.11, 2.3), (-4.4, 1.11, 3.4), m['grey'])                  # radiator grilles
    b.box_mm((-6.3, -0.9, 3.55), (-4.6, 0.9, 3.75), m['grey'])                  # fan housing
    b.cyl(0.4, 0.05, (-5.45, 0, 3.77), m['steel'], seg=24)                      # fan grille
    b.cyl(0.14, 0.45, (-1.6, 0.0, 3.75), m['steel'], seg=14)                    # exhaust stack
    for x in (-3.8, -2.4, -1.0):                                                # hood doors
        for s in (1, -1):
            b.box_mm((x - 0.6, s * 1.1 - 0.01, 1.8), (x + 0.6, s * 1.1 + 0.01, 3.3), m['white'])
    # cab (estimated layout: off-centre, toward +X)
    b.box_mm((1.3, -HW, FZ + 0.05), (4.3, HW, ROOF - 0.12), paint)
    b.box_mm((1.25, -HW - 0.03, ROOF - 0.12), (4.35, HW + 0.03, ROOF), m['white'])   # roof
    windows(b, 1.3, 4.3, -HW, HW, 2.95, 3.9, m, ('+x',))
    b.box_mm((1.29, -1.45, 3.62), (1.31, -1.15, 3.95), m['glass'])               # rear windows over hood
    b.box_mm((1.29, 1.15, 3.62), (1.31, 1.45, 3.95), m['glass'])
    b.box_mm((1.29, -1.05, 3.62), (1.31, 1.05, 3.95), m['glass'])
    for s in (1, -1):                                                           # fixed side windows
        b.box_mm((2.4, s * HW - 0.01, 2.95), (4.1, s * HW + 0.01, 3.85), m['glass'])
    # short hood (batteries, compressor)
    b.box_mm((4.3, -1.0, FZ + 0.05), (6.7, 1.0, 2.9), paint)
    # fuel tank between the bogies
    b.box_mm((-2.0, -1.2, 0.62), (2.0, 1.2, FZ - 0.35), m['steel'])
    # handrails along both walkways and across the ends (gaps at the steps)
    for s in (1, -1):
        y = s * (HW - 0.05)
        pb.handrail(b, (-6.6, y, FZ + 0.05), (1.2, y, FZ + 0.05), paint)
        pb.handrail(b, (4.4, y, FZ + 0.05), (6.7, y, FZ + 0.05), paint)
    for d in (1, -1):
        pb.handrail(b, (d * 7.0, -0.9, FZ + 0.05), (d * 7.0, 0.9, FZ + 0.05), paint)
    # corner steps and lamps
    for d in (1, -1):
        for s in (1, -1):
            for k, z in enumerate((0.45, 0.85)):
                b.box((0.5, 0.25, 0.04), (d * 6.85, s * (HW - 0.15 + 0.05 * k), z), m['steel'])
            b.box((0.05, 0.4, 0.04), (d * 6.85, s * (HW - 0.2), 0.65), m['steel'])
            b.cyl(0.09, 0.05, (d * 7.12, s * 0.6, 1.75), m['lamp'], rot=(0, 90, 0), seg=14)
        b.cyl(0.09, 0.05, (d * (6.72 if d > 0 else 6.62), 0, 2.7), m['lamp'], rot=(0, 90, 0), seg=14)
    body = b.finish(col)

    bogies, wheelsets = [], []
    for i, x in enumerate((BOGIE_X, -BOGIE_X)):
        fr, ws = pl.bogie(f"SL_Bogie{i + 1}", x, col, m, wheelbase=WB, r=R)
        pm.parent(fr, body)
        bogies.append(fr)
        wheelsets += ws

    # cab side doors, hinged on a vertical axis at the rear edge (estimated)
    doors = []
    for s, t in ((1, "L"), (-1, "R")):
        hinge = (1.45, s * (HW + 0.02), FZ + 0.1)
        d = pb.Part(f"SL_CabDoor_{t}", pivot=hinge)
        d.box_mm((1.45, s * HW - 0.0 + (0 if s > 0 else -0.04), FZ + 0.1),
                 (2.25, s * HW + (0.04 if s > 0 else 0), 3.85), paint)
        d.box_mm((1.6, s * (HW + 0.04) - 0.01, 2.95), (2.1, s * (HW + 0.04) + 0.01, 3.7), m['glass'])
        do = d.finish(col)
        pm.parent(do, body)
        doors.append(do)

    pb.ref_human(ref, (5.5, -2.6, 0.0))
    ref_track(ref, 12.0)
    cam, tgt, lens = side_view(LOB)
    _TABLE[name] = pm.finish_asset(name, FOLDER, [("Preview_ShuntingLocomotive.png", cam, tgt, lens)])
    return result(
        name,
        "Four-axle diesel-hydraulic road switcher, Vossloh G1206 size class (no branding), for "
        "shunting concentrate, acid and cathode trains inside the plant. Origin on the track centre "
        "at top of rail under the middle of the locomotive. +X is the short-hood (cab) end.",
        "Preview_ShuntingLocomotive.png",
        f"""
| Part | Motion |
|---|---|
| SL_Body | Root. Moves along the track |
| SL_Bogie1_Frame / SL_Bogie2_Frame | Yaw about local Z in curves (a few degrees) |
| SL_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.50 m: {pl.deg_per_metre(0.5):.1f} degrees per metre travelled |
| SL_CabDoor_L / _R | Swing about local Z: L positive, R negative, about 95° open |
""",
        """
| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 14.70 m | Sourced |
| Width over handrails | 3.08 m (deck 3.00 m) | Sourced |
| Height over cab roof | 4.22 m | Sourced |
| Wheel diameter | 1.00 m new | Sourced |
| Bogie centres / bogie wheelbase | 7.20 m / 2.40 m | Sourced, single source |
| Frame top 1.45 m, hood heights 3.55 / 2.90 m, cab position | | Estimated |
| Buffer height 1.06 m, spacing 1.75 m | | UIC standard values |
""",
        "[Wikipedia: MaK/Vossloh G1206](https://en.wikipedia.org/wiki/MaK_/_Vossloh_G1206), "
        "[Spitzke G 1206 data](https://www.spitzke.com/en/machines/locomotives-railway-wagons/diesel-locomotives/g-1206-series/).")


# ===========================================================================
# Covered hopper wagon (bottom discharge)
# ===========================================================================

def build_hopper_wagon():
    name = "SM_HopperWagon"
    col, ref, m = pm.start(name)
    paint = m['blue']
    LOB = 12.79                     # length over buffers (estimated, Fals size class)
    BOGIE_X = 4.0
    FZ = 1.30                       # top of underframe (estimated)
    BODY = (-5.6, 5.6, -1.5, 1.5, 1.30, 3.95)    # x0, x1, y0, y1, z0, z1 (estimated)
    OUTLETS = (-1.25, 1.25)         # hopper outlet centres between the bogies
    OUT_HALF, TOP_HALF = 0.35, 1.2  # outlet / hopper top half length along X
    DOOR_Z = 0.72                   # underside of the closed doors

    b = pb.Part("HW_Body")
    pl.underframe(b, -5.95, 5.95, FZ, m, m['steel'])
    for d in (1, -1):
        pl.buffers_and_coupling(b, d * LOB / 2, d, m, m['steel'])
    x0, x1, y0, y1, z0, z1 = BODY
    b.box_mm((x0, y0, z0), (x1, y1, z1), paint)
    b.box_mm((x0 - 0.05, y0 - 0.05, z1), (x1 + 0.05, y1 + 0.05, z1 + 0.05), paint)    # roof edge
    x = x0 + 0.2
    while x < x1:                                                                    # side ribs
        for s in (1, -1):
            b.box((0.1, 0.06, z1 - z0), (x, s * (y1 + 0.03), (z0 + z1) / 2), paint)
        x += 1.4
    b.box_mm((x0 - 0.02, y0, z0), (x1 + 0.02, y1, z0 + 0.1), m['steel'])            # bottom chord
    # two discharge hoppers (sloped funnels) and their outlet frames
    for xc in OUTLETS:
        pts = [(xc - TOP_HALF, z0), (xc + TOP_HALF, z0), (xc + OUT_HALF, DOOR_Z + 0.05),
               (xc - OUT_HALF, DOOR_Z + 0.05)]
        b.poly_prism(pts, -1.2, 1.2, paint, plane='XZ')
        b.box_mm((xc - OUT_HALF - 0.05, -1.25, DOOR_Z + 0.03), (xc + OUT_HALF + 0.05, 1.25, DOOR_Z + 0.12), m['steel'])
    # roof hatch coamings
    for xc in (-3.5, 0.0, 3.5):
        b.box_mm((xc - 0.85, -0.55, z1 + 0.05), (xc + 0.85, 0.55, z1 + 0.12), m['steel'])
    # roof walkway, end platforms, ladders
    b.box_mm((x0, -0.25, z1 + 0.12), (x1, 0.25, z1 + 0.15), m['galv'])
    for d in (1, -1):
        b.box_mm((min(d * 5.62, d * 6.0), -1.3, FZ - 0.05), (max(d * 5.62, d * 6.0), 1.3, FZ), m['galv'])
        pb.ladder(b, (d * 5.68, 1.0, FZ), z1 + 0.1, m['galv'], facing=0)
        pb.handrail(b, (d * 5.95, -1.3, FZ), (d * 5.95, 0.4, FZ), m['yellow'])
    fix_normals(b)
    body = b.finish(col)

    for i, x in enumerate((BOGIE_X, -BOGIE_X)):
        fr, ws = pl.bogie(f"HW_Bogie{i + 1}", x, col, m)
        pm.parent(fr, body)

    # bottom doors: two flaps per outlet, hinged on lines along Y at the outlet edges
    doors = []
    for i, xc in enumerate(OUTLETS):
        for t, hx, sign in (("A", xc - OUT_HALF, 1), ("B", xc + OUT_HALF, -1)):
            d = pb.Part(f"HW_Door_{i + 1}{t}", pivot=(hx, 0, DOOR_Z + 0.015))
            d.box_mm((min(hx, xc), -1.15, DOOR_Z), (max(hx, xc), 1.15, DOOR_Z + 0.03), m['steel'])
            d.box_mm((min(hx, xc) + 0.05, -1.1, DOOR_Z - 0.06), (max(hx, xc) - 0.05, -1.0, DOOR_Z), m['steel'])
            d.box_mm((min(hx, xc) + 0.05, 1.0, DOOR_Z - 0.06), (max(hx, xc) - 0.05, 1.1, DOOR_Z), m['steel'])
            do = d.finish(col)
            pm.parent(do, body)
            doors.append((do, sign))
    # roof hatch lids, hinged along X on the +Y edge
    lids = []
    for i, xc in enumerate((-3.5, 0.0, 3.5)):
        hinge = (xc, 0.6, z1 + 0.15)
        lp = pb.Part(f"HW_HatchLid_{i + 1}", pivot=hinge)
        lp.box_mm((xc - 0.9, -0.6, z1 + 0.12), (xc + 0.9, 0.6, z1 + 0.18), paint)
        lo = lp.finish(col)
        pm.parent(lo, body)
        lids.append(lo)

    def pose():
        for do, sign in doors:
            do.rotation_euler.y = math.radians(60 * sign)
        for lo in lids:
            lo.rotation_euler.x = math.radians(-100)

    pb.ref_human(ref, (4.0, -2.8, 0.0))
    ref_track(ref, 10.0)
    cam, tgt, lens = side_view(LOB)
    _TABLE[name] = pm.finish_asset(name, FOLDER, [
        ("Preview_HopperWagon.png", cam, tgt, lens),
        ("Preview_HopperWagon_Open.png", (4.5, -7.5, 0.9), (0, 0, 1.2), 28.0, True)], pose=pose)
    return result(
        name,
        "Covered four-axle bottom-discharge hopper wagon for copper concentrate (Fals / Tadns size "
        "class, no branding). Two funnel hoppers between the bogies empty through flap doors into a "
        "track hopper; three roof hatches for loading. Origin on the track centre at top of rail.",
        "Preview_HopperWagon.png, Preview_HopperWagon_Open.png (doors and hatches open)",
        f"""
| Part | Motion |
|---|---|
| HW_Body | Root |
| HW_Bogie1_Frame / HW_Bogie2_Frame | Yaw about local Z |
| HW_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: {pl.deg_per_metre(0.46):.1f} degrees per metre |
| HW_Door_1A, HW_Door_2A | Rotate about local Y, +60° opens (downward) |
| HW_Door_1B, HW_Door_2B | Rotate about local Y, -60° opens |
| HW_HatchLid_1..3 | Rotate about local X, -100° opens |
""",
        """
| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 12.79 m | Estimated (Fals-class figure from memory, not checked) |
| Body 11.2 x 3.0 m, top 3.95 m above rail (lids 4.13 m); hoppers below the underframe | | Estimated |
| Bogie centres 8.0 m, freight bogie wheelbase 1.80 m | | Estimated |
| Wheel diameter 0.92 m | | Standard freight wheel |
| Volume about 75 m³ gross body; at 25 t axle load the payload is about 75 t | | Estimated |
| Outlets 0.70 x 2.30 m at x = ±1.25, door underside 0.72 m above rail | | Estimated, own design |
""",
        "no dimension source found in the time box; proportions follow European ore and mineral hopper wagons.")


# ===========================================================================
# Side-tipping wagon
# ===========================================================================

def build_side_tip_wagon():
    name = "SM_SideTipWagon"
    col, ref, m = pm.start(name)
    paint = m['red']
    LOB = 13.50                     # length over buffers (estimated)
    BOGIE_X = 4.5
    FZ = 1.25                       # top of underframe (estimated)
    PIV_Y, PIV_Z = -1.45, 1.40      # tipping hinge line on the -Y (dump) side
    BX = 6.0                        # body half length
    WALL_Z = 2.95                   # top of body sides

    fp = pb.Part("ST_Underframe")
    pl.underframe(fp, -6.3, 6.3, FZ, m, m['steel'])
    for d in (1, -1):
        pl.buffers_and_coupling(fp, d * LOB / 2, d, m, m['steel'])
    for x in (-5.0, -2.5, 0.0, 2.5, 5.0):                                        # hinge brackets
        fp.box((0.25, 0.2, 0.2), (x, PIV_Y, PIV_Z - 0.05), m['grey'])
        fp.cyl(0.06, 0.3, (x, PIV_Y, PIV_Z), m['grey'], rot=(0, 90, 0), seg=10)
    for x in (-2.0, 2.0):                                                        # cylinder mounts
        fp.box((0.3, 0.3, 0.4), (x, 0.6, FZ - 0.2), m['steel'])
    frame = fp.finish(col)

    bp = pb.Part("ST_Body", pivot=(0, PIV_Y, PIV_Z))
    bp.box_mm((-BX, -1.45, PIV_Z), (BX, 1.45, PIV_Z + 0.15), paint)               # floor
    bp.box_mm((-BX, 1.38, PIV_Z + 0.15), (BX, 1.45, WALL_Z), paint)               # fixed +Y side
    for d in (1, -1):                                                            # end walls
        bp.box_mm((min(d * BX, d * (BX - 0.08)), -1.45, PIV_Z + 0.15),
                  (max(d * BX, d * (BX - 0.08)), 1.45, WALL_Z + 0.25), paint)
    x = -BX + 0.5
    while x < BX:                                                                # ribs on fixed side
        bp.box((0.1, 0.08, WALL_Z - PIV_Z), (x, 1.49, (PIV_Z + WALL_Z) / 2), paint)
        x += 1.5
    for x in (-5.0, -2.5, 0.0, 2.5, 5.0):                                        # hinge eyes
        bp.box((0.2, 0.15, 0.15), (x + 0.2, PIV_Y + 0.05, PIV_Z + 0.02), m['grey'])
    body = bp.finish(col)
    pm.parent(body, frame)

    dp = pb.Part("ST_DropSide", pivot=(0, -1.45, PIV_Z + 0.07))
    dp.box_mm((-BX + 0.08, -1.53, PIV_Z + 0.15), (BX - 0.08, -1.45, WALL_Z), paint)
    x = -BX + 0.5
    while x < BX:
        dp.box((0.1, 0.06, WALL_Z - PIV_Z - 0.15), (x, -1.56, (PIV_Z + 0.15 + WALL_Z) / 2), paint)
        x += 1.5
    drop = dp.finish(col)
    pm.parent(drop, body)

    for i, x in enumerate((BOGIE_X, -BOGIE_X)):
        fr, ws = pl.bogie(f"ST_Bogie{i + 1}", x, col, m)
        pm.parent(fr, frame)
    for i, x in enumerate((-2.0, 2.0)):                                          # air tipping cylinders
        pm.hyd_cyl(f"ST_TipCyl{i + 1}", (x, 0.6, FZ - 0.3), (x, 0.75, PIV_Z), 0.13, col, m,
                   base_par=frame, tip_par=body)

    def pose():
        body.rotation_euler.x = math.radians(45)
        drop.rotation_euler.x = math.radians(75)

    pb.ref_human(ref, (4.5, -3.2, 0.0))
    ref_track(ref, 10.0)
    cam, tgt, lens = side_view(LOB)
    _TABLE[name] = pm.finish_asset(name, FOLDER, [
        ("Preview_SideTipWagon.png", cam, tgt, lens),
        ("Preview_SideTipWagon_Tipped.png", (9.0, -13.0, 5.0), (0, -1.5, 1.8), 35.0, True)], pose=pose)
    return result(
        name,
        "Four-axle air-operated side-tipping wagon for flux, limestone, reverts and broken slag "
        "(own design in the general form of European and US air-dump cars). The body tips to the "
        "-Y side about a hinge line along the solebar; the -Y side wall drops as it tips. Origin on "
        "the track centre at top of rail.",
        "Preview_SideTipWagon.png, Preview_SideTipWagon_Tipped.png (body at 45°)",
        f"""
| Part | Motion |
|---|---|
| ST_Underframe | Root |
| ST_Body | Rotate about local X, 0 to +45° tips to the -Y side |
| ST_DropSide | Child of the body; rotate about local X, 0 to about +75° swings it out and down. Tie it to the body angle (about 1.7 x body angle) |
| ST_TipCyl1/2_Barrel / _Rod | Look-at pair: each half aims local +X at the other's pivot |
| ST_Bogie1_Frame / ST_Bogie2_Frame | Yaw about local Z |
| ST_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: {pl.deg_per_metre(0.46):.1f} degrees per metre |
""",
        """
| Dimension | Value | Status |
|---|---|---|
| Length over buffers 13.5 m, body 12.0 x 2.9 x 1.55 m (about 50 m³ struck) | | Estimated, own design |
| Hinge line y = -1.45, z = 1.40 above rail | | Estimated |
| Bogie centres 9.0 m, wheel 0.92 m | | Estimated / standard |
""",
        "none; own design.")


# ===========================================================================
# Flat wagon (Res class)
# ===========================================================================

SPIGOTS_20FT = []   # filled by build_flat_wagon for the README


def build_flat_wagon():
    name = "SM_FlatWagon"
    col, ref, m = pm.start(name)
    paint = m['green']
    LOB = 19.90                     # length over buffers (sourced)
    BOGIE_X = 7.43                  # bogie centres 14.86 m (sourced)
    DECK = 1.235                    # deck height above rail (estimated, unconfirmed)
    DX, DY = 9.25, 1.385            # deck half length / half width (estimated)

    b = pb.Part("FW_Body")
    pl.underframe(b, -9.6, 9.6, DECK - 0.05, m, paint, width=2.8)
    for d in (1, -1):
        pl.buffers_and_coupling(b, d * LOB / 2, d, m, paint)
    b.box_mm((-DX, -DY, DECK - 0.06), (DX, DY, DECK), m['wood'])                 # timber deck
    for s in (1, -1):                                                            # side edge channels
        b.box_mm((-DX, s * DY - (0.06 if s > 0 else 0), DECK - 0.35),
                 (DX, s * DY + (0 if s > 0 else 0.06), DECK + 0.02), paint)
    # stanchion pockets
    xs = [-8.4 + 2.4 * i for i in range(8)]
    for x in xs:
        for s in (1, -1):
            b.box((0.16, 0.16, 0.3), (x, s * (DY + 0.08), DECK - 0.15), m['steel'])
    # container spigots for three 20 ft boxes (ISO corner fitting centres 5.853 x 2.259 m)
    SPIGOTS_20FT.clear()
    for c in (-6.1, 0.0, 6.1):
        for dx in (-2.9265, 2.9265):
            for dy in (-1.1295, 1.1295):
                b.box((0.12, 0.12, 0.06), (c + dx, dy, DECK + 0.03), m['grey'])
                SPIGOTS_20FT.append((round(c + dx, 3), dy, DECK))
    # hand brake wheel and steps at the ends
    for d in (1, -1):
        b.cyl(0.2, 0.03, (d * 9.5, 1.15, 1.5), m['steel'], rot=(0, 90, 0), seg=16)
        for s in (1, -1):
            b.box((0.4, 0.25, 0.04), (d * 9.3, s * 1.45, 0.55), m['steel'])
    body = b.finish(col)

    for i, x in enumerate((BOGIE_X, -BOGIE_X)):
        fr, ws = pl.bogie(f"FW_Bogie{i + 1}", x, col, m)
        pm.parent(fr, body)

    # removable stanchions, one part per side
    for s, t in ((1, "L"), (-1, "R")):
        sp = pb.Part(f"FW_Stanchions_{t}", pivot=(0, s * (DY + 0.08), DECK))
        for x in xs:
            sp.box((0.1, 0.1, 2.2), (x, s * (DY + 0.08), DECK + 0.8), m['steel'])
        so = sp.finish(col)
        pm.parent(so, body)
    # folding end walls, hinged along Y at the deck ends
    for d, t in ((1, "A"), (-1, "B")):
        ep = pb.Part(f"FW_EndWall_{t}", pivot=(d * DX, 0, DECK))
        ep.box_mm((min(d * DX, d * (DX - 0.06)), -1.3, DECK), (max(d * DX, d * (DX - 0.06)), 1.3, DECK + 0.6), paint)
        eo = ep.finish(col)
        pm.parent(eo, body)

    # REF load: three cathode bundles to show scale
    lm = pb.mat("M_REF_Copper", (0.72, 0.36, 0.2), 0.9, 0.35)
    for x in (-3.0, -1.5, 0.0, 1.5, 3.0):
        lp = pb.Part(f"REF_CathodeBundle_{x:+.1f}")
        lp.box((1.05, 1.02, 0.26), (x, 0, DECK + 0.13), lm)
        lp.finish(ref)
    pb.ref_human(ref, (6.0, -2.8, 0.0))
    ref_track(ref, 13.0)
    cam, tgt, lens = side_view(LOB, h=6.0)
    _TABLE[name] = pm.finish_asset(name, FOLDER, [("Preview_FlatWagon.png", cam, tgt, lens)])
    spig = "\n".join(f"| ({x:.3f}, {y:.4f}, {z:.3f}) |" for x, y, z in SPIGOTS_20FT)
    return result(
        name,
        "Four-axle bogie flat wagon, Res class size (no branding), for strapped cathode bundles, "
        "rod coils, spares and 20 ft containers. Timber deck, removable stanchions in side pockets, "
        "folding end walls, container spigots for three 20 ft boxes. The preview's cathode bundles "
        "are REF only. Origin on the track centre at top of rail.",
        "Preview_FlatWagon.png",
        f"""
| Part | Motion |
|---|---|
| FW_Body | Root |
| FW_Stanchions_L / _R | Remove (hide) for container loads; slide along local Z out of the pockets |
| FW_EndWall_A | Rotate about local Y, +90° folds it outward flat |
| FW_EndWall_B | Rotate about local Y, -90° folds it outward flat |
| FW_Bogie1_Frame / FW_Bogie2_Frame | Yaw about local Z |
| FW_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: {pl.deg_per_metre(0.46):.1f} degrees per metre |

Container spigot tops (corner-fitting centres of three 20 ft containers, deck height):

| Spigot (X, Y, Z) |
|---|
{spig}
""",
        """
| Dimension | Value | Status |
|---|---|---|
| Length over buffers | 19.90 m | Sourced |
| Bogie centres | 14.86 m | Sourced |
| Deck 18.5 x 2.77 m, deck height 1.235 m | | Estimated (common figures, not confirmed) |
| 20 ft corner fitting centres 5.853 x 2.259 m | | ISO 668 / 1161 values, from memory |
| Stanchions 2.2 m tall at 2.4 m pitch, end walls 0.6 m | | Estimated |
""",
        "[TrainsDepot Res-x 679.1](https://www.trainsdepot.org/en/vehicle/2787/res-x679-1), "
        "[Đuro Đaković Rens data](https://duro-dakovic.com/en/duro-dakovic-special-vehicles/transport/intermodal-wagons/rens/).")


# ===========================================================================
# Sulphuric acid tank wagon
# ===========================================================================

def build_acid_tank_wagon():
    name = "SM_AcidTankWagon"
    col, ref, m = pm.start(name)
    paint = m['white']
    LOB = 12.20                     # length over buffers (estimated)
    BOGIE_X = 3.5
    FZ = 1.25                       # top of underframe (estimated)
    TR, TL = 1.10, 8.6              # tank shell radius / cylindrical length (estimated)
    TZ = FZ + 0.12 + TR             # tank axis height
    TOP = TZ + TR

    b = pb.Part("AT_Body")
    pl.underframe(b, -5.6, 5.6, FZ, m, m['steel'], width=2.7)
    for d in (1, -1):
        pl.buffers_and_coupling(b, d * LOB / 2, d, m, m['steel'])
    b.cyl(TR, TL, (0, 0, TZ), paint, rot=(0, 90, 0), seg=40)                     # shell
    for d in (1, -1):                                                            # dished heads
        rot = (0, 90 * d, 0)
        b.cyl(TR, 0.25, (d * (TL / 2 + 0.125), 0, TZ), paint, rot=rot, seg=40, r2=0.78)
        b.cyl(0.78, 0.12, (d * (TL / 2 + 0.31), 0, TZ), paint, rot=rot, seg=40, r2=0.35)
    for x in (-3.5, 0.0, 3.5):                                                   # saddles
        b.box((0.3, 2.0, 0.35), (x, 0, FZ + 0.15), m['steel'])
    for x in (-2.0, 2.0):                                                        # tank bands
        b.cyl(TR + 0.02, 0.08, (x, 0, TZ), m['steel'], rot=(0, 90, 0), seg=40)
    for s in (1, -1):                                                            # orange hazard band
        b.box_mm((-3.0, s * (TR + 0.005) - 0.005, TZ - 0.2), (3.0, s * (TR + 0.005) + 0.005, TZ + 0.2), m['orange'])
        b.box_mm((-0.4, s * (TR + 0.02) - 0.005, TZ - 0.5), (0.4, s * (TR + 0.02) + 0.005, TZ - 0.25), m['orange'])
    # dome, valves and top platform
    b.cyl(0.32, 0.3, (0, 0, TOP + 0.1), paint, seg=24)
    b.cyl(0.38, 0.05, (0, 0, TOP + 0.25), m['steel'], seg=24)
    b.cyl(0.08, 0.35, (0.75, 0, TOP + 0.12), m['grey'], seg=12)                  # eductor (discharge) pipe
    b.cyl(0.13, 0.08, (0.75, 0, TOP + 0.3), m['steel'], seg=14)                  # discharge valve cap
    b.cyl(0.06, 0.3, (-0.75, 0, TOP + 0.1), m['grey'], seg=12)                   # air inlet valve
    b.cyl(0.1, 0.06, (-0.75, 0, TOP + 0.26), m['steel'], seg=14)
    b.cyl(0.07, 0.25, (0, 0.6, TOP + 0.05), m['red'], seg=12)                    # safety valve
    PZ = TOP + 0.02
    b.box_mm((-1.3, -1.45, PZ - 0.04), (1.3, 1.45, PZ), m['galv'])               # grating platform
    for s in (1, -1):
        for x in (-1.2, 1.2):
            b.cyl_between((x, s * 1.35, PZ - 0.04), (x, s * 0.6, TZ + 0.5), 0.03, m['galv'], seg=8)
    pm.guard_box(b, -1.3, -1.45, 1.3, 1.45, PZ, m['yellow'], open_side=None)
    for s in (1, -1):                                                            # ladders both sides
        pb.ladder(b, (1.0, s * 1.52, FZ - 0.4), PZ + 0.9, m['galv'], facing=90)
        b.box((0.6, 0.35, 0.04), (1.0, s * 1.45, FZ - 0.4), m['steel'])
    body = b.finish(col)

    for i, x in enumerate((BOGIE_X, -BOGIE_X)):
        fr, ws = pl.bogie(f"AT_Bogie{i + 1}", x, col, m)
        pm.parent(fr, body)

    # manway lid hinged along Y at its -X edge
    hz = TOP + 0.29
    lp = pb.Part("AT_ManwayLid", pivot=(-0.36, 0, hz))
    lp.cyl(0.36, 0.05, (0, 0, hz), m['steel'], seg=24)
    lp.box((0.12, 0.3, 0.06), (-0.33, 0, hz), m['grey'])
    lo = lp.finish(col)
    pm.parent(lo, body)

    pb.ref_human(ref, (3.5, -2.8, 0.0))
    ref_track(ref, 10.0)
    cam, tgt, lens = side_view(LOB)
    _TABLE[name] = pm.finish_asset(name, FOLDER, [("Preview_AcidTankWagon.png", cam, tgt, lens)])
    return result(
        name,
        "Four-axle tank wagon for 93-98 % sulphuric acid (own design in the general form of European "
        "acid tank wagons, no branding). Carbon-steel tank (concentrated acid does not need a lining), "
        "top loading and top discharge only: a dip (eductor) pipe and valve, an air inlet valve and a "
        "safety valve around the manway dome, reached by side ladders and a top platform. Origin on "
        "the track centre at top of rail.",
        "Preview_AcidTankWagon.png",
        f"""
| Part | Motion |
|---|---|
| AT_Body | Root |
| AT_ManwayLid | Rotate about local Y, -110° opens |
| AT_Bogie1_Frame / AT_Bogie2_Frame | Yaw about local Z |
| AT_BogieN_WS1 / _WS2 | Spin about local Y. Wheel radius 0.46 m: {pl.deg_per_metre(0.46):.1f} degrees per metre |

Connection points: discharge valve cap at (0.75, 0, {TOP + 0.3:.2f}), air inlet at (-0.75, 0, {TOP + 0.26:.2f}),
manway at (0, 0, {TOP + 0.25:.2f}).
""",
        f"""
| Dimension | Value | Status |
|---|---|---|
| Length over buffers 12.2 m, bogie centres 7.0 m | | Estimated |
| Tank 2.20 m diameter, 8.6 m cylindrical, about 35 m³ | | Estimated |
| Top of tank {TOP:.2f} m, top of handrail {TOP + 1.12:.2f} m above rail | | Estimated |

Volume note: concentrated acid weighs about 1.83 t/m³, so a 90 t (22.5 t axle load) wagon carries
about 60-65 t, which is only about 35 m³. Acid wagons are therefore small for their weight; the
60-80 m³ class is for lighter products and would be overloaded with acid.
""",
        "density of sulphuric acid (standard value); wagon dimensions estimated.")


# ===========================================================================

BUILDERS = {
    "ShuntingLocomotive": build_shunting_locomotive,
    "HopperWagon": build_hopper_wagon,
    "SideTipWagon": build_side_tip_wagon,
    "FlatWagon": build_flat_wagon,
    "AcidTankWagon": build_acid_tank_wagon,
}

INTRO = """
Rolling stock for the plant railway: a shunting locomotive and four wagon types for concentrate,
flux/reverts, cathode bundles and containers, and sulphuric acid. Each asset is a standalone prop
at its own origin (track centre line, top of rail z = 0, +X = A end), standard gauge 1.435 m, UIC
buffers at 1.06 m and 1.75 m spacing. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_rail_vehicles.py`. Brand names are size references only; the
models carry no logos. In the .blend the bogies, wheelsets, doors and lids are parented to the
body for posing. The REF collection (track, scale figure, sample load, camera, sun) is not exported.

Bogies are separate parts: <prefix>_BogieN_Frame yaws about its centre pivot and carries two
wheelsets. Bogie wheelbase 1.80 m (freight) or 2.40 m (locomotive).
"""

if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
