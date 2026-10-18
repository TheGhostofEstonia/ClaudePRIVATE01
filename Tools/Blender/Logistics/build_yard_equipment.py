"""
build_yard_equipment.py - on-site mobile plant for the logistics set, each a standalone prop at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_yard_equipment.py
      (add  -- WheelLoader  to build one asset only)

Assets (Meshes/YardEquipment/):
    SM_WheelLoader       articulated wheel loader, ~5.4 m3 bucket (Cat 980 size)
    SM_SkidSteer         skid steer loader (Cat 262 size)
    SM_HeavyForklift16t  16 t counterbalance forklift, duplex mast (anode / cathode bundles)
    SM_Forklift3t        3 t counterbalance forklift, triplex mast (warehouse)
    SM_TuggerTrain       electric tow tractor + 3 platform carts

All: +X = forward travel, origin on the ground (see each README section).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm
FOLDER = "YardEquipment"


# ===========================================================================
# Local helpers
# ===========================================================================

def fin(p, col, **kw):
    """Recalculate outward normals (poly prisms are wound either way), then finish the part."""
    bmesh.ops.recalc_face_normals(p.bm, faces=p.bm.faces[:])
    return p.finish(col, **kw)


def xz(x, z):
    """Point in the side (XZ) plane at y = 0."""
    return Vector((x, 0.0, z))


def rot_xz(v, a_deg):
    """Rotate a vector in the XZ plane, counter-clockwise (raises +X) by a_deg.
    In Blender this equals rotation_euler.y = -a."""
    a = math.radians(a_deg)
    return Vector((v.x * math.cos(a) - v.z * math.sin(a), v.y, v.x * math.sin(a) + v.z * math.cos(a)))


def ang_xz(v):
    """Angle of a vector in the XZ plane (degrees, CCW from +X)."""
    return math.degrees(math.atan2(v.z, v.x))


def plate_xz(p, a, b, t, y0, y1, m):
    """Flat plate whose section is the line a->b (XZ) thickened by t to the left, spanning y0..y1."""
    d = (b - a).normalized()
    n = Vector((-d.z, 0, d.x)) * t
    pts = [(a.x, a.z), (b.x, b.z), (b.x + n.x, b.z + n.z), (a.x + n.x, a.z + n.z)]
    p.poly_prism(pts, y0, y1, m, plane='XZ')


def bucket(p, hinge, prof, width, t, m, side_m=None):
    """
    Loader bucket: shell plates along the profile points (relative to the hinge pin, XZ) and two
    side plates filling the outline. prof runs from the top-back over the heel to the cutting edge.
    """
    pts = [hinge + xz(*q) for q in prof]
    hw = width / 2
    for a, b in zip(pts, pts[1:]):
        plate_xz(p, b, a, t, -hw, hw, m)
    outline = [(q.x, q.z) for q in pts]
    for s in (1, -1):
        y0 = s * hw - (0.03 if s > 0 else -0.03)
        p.poly_prism(outline, min(y0, s * hw), max(y0, s * hw), side_m or m, plane='XZ')


def circle_meet(c1, r1, c2, r2, lower=True):
    """Intersection of two circles in the XZ plane; returns the lower (or upper) point."""
    d = (c2 - c1).length
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    u = (c2 - c1) / d
    n = Vector((-u.z, 0, u.x))
    p1, p2 = c1 + u * a + n * h, c1 + u * a - n * h
    return (min if lower else max)((p1, p2), key=lambda q: q.z)


def solve_lever(C, u0, D, link_len, guess_deg):
    """
    Bell-crank angle (world delta, degrees) that puts the link end U = C + rot(u0, a) at link_len
    from D. Scans +/-90 deg around the guess and returns the closest solution.
    """
    best, best_e = guess_deg, 1e9
    for i in range(-900, 901):
        a = guess_deg + i * 0.1
        e = abs(((C + rot_xz(u0, a)) - D).length - link_len) + abs(i) * 1e-5
        if e < best_e:
            best, best_e = a, e
    return best


def overhead_guard(p, x_front, x_rear, hw, z0, z_top, m, roof_m=None):
    """Four-post overhead guard with a slatted roof."""
    for x in (x_front, x_rear):
        for s in (1, -1):
            p.box_mm((x - 0.04, s * hw - 0.04, z0), (x + 0.04, s * hw + 0.04, z_top), m)
    p.box_mm((x_rear - 0.05, -hw - 0.05, z_top), (x_front + 0.05, hw + 0.05, z_top + 0.06), m)
    n = max(3, int((x_front - x_rear) / 0.12))
    for i in range(1, n):
        x = x_rear + (x_front - x_rear) * i / n
        p.box_mm((x - 0.015, -hw, z_top + 0.06), (x + 0.015, hw, z_top + 0.09), roof_m or m)


def cab_glass(p, x0, x1, hw, z0, z1, m, paint):
    """Glazed cab: corner posts in paint, glass panes on all four faces, roof."""
    for x in (x0, x1):
        for s in (1, -1):
            p.box_mm((x - 0.04, s * hw - 0.04, z0), (x + 0.04, s * hw + 0.04, z1), paint)
    p.box_mm((x0 + 0.04, -hw + 0.02, z0), (x1 - 0.04, hw - 0.02, z1), m['glass'])
    p.box_mm((x0 - 0.06, -hw - 0.06, z1), (x1 + 0.06, hw + 0.06, z1 + 0.12), paint)


# ===========================================================================
# Wheel loader
# ===========================================================================

def build_wheel_loader():
    name = "SM_WheelLoader"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    # Sourced (Cat 980 spec): wheelbase 3.80, tread 2.44, length w/o bucket 8.155, hood 3.064,
    # ROPS 3.829, hinge pin carry 0.68 / max lift 4.554, 5.4 m3 bucket, 29.5R25 tyres.
    WB, TREAD = 3.80, 2.44
    TR, TW = 0.935, 0.75                 # 29.5R25: ~1.87 m diameter, 0.75 m wide
    HZ = 1.15                            # articulation hinge height (estimated)
    A = xz(1.50, 2.30)                   # lift arm pivot on the front frame (estimated)
    B0 = xz(3.905, 0.68)                 # bucket hinge pin at carry (height sourced)
    L_ARM = (B0 - A).length
    th0 = ang_xz(B0 - A)
    dirv = (B0 - A).normalized()
    perp = Vector((-dirv.z, 0, dirv.x))
    C_ARM = A + dirv * 1.80              # arm point under the cross tube
    C0 = C_ARM + perp * 0.50             # bell-crank pivot on the arm cross tube
    T0 = C0 + xz(-0.30, 0.65)            # bell-crank top: tilt cylinder rod end
    D0 = B0 + xz(-0.05, 0.75)            # bucket top (link) pin
    LINK, R_U = 0.75, 0.45               # link length, bell-crank lower arm
    U0 = circle_meet(C0, R_U, D0, LINK)  # bell-crank bottom: tilt link pin
    F0 = xz(0.75, 1.95)                  # tilt cylinder base on the front frame
    BW = 3.25                            # bucket width (estimated, ~ over tyres)
    PROF = [(-0.12, 0.95), (-0.12, 0.45), (-0.10, -0.40), (0.15, -0.66), (1.55, -0.68)]

    # --- rear frame (root): engine, counterweight, cab ---
    rf = pb.Part("WL_RearFrame", pivot=(0, 0, HZ))
    rf.box_mm((-3.60, -0.55, 0.75), (-0.25, 0.55, 1.45), m['steel'])
    rf.cyl(0.22, 2.0, (-WB / 2, 0, TR), m['grey'], rot=(90, 0, 0), seg=16)        # rear axle
    rf.box_mm((-4.00, -0.85, 1.45), (-1.75, 0.85, 3.064), paint)                  # engine hood
    rf.box_mm((-4.03, -0.70, 1.70), (-3.99, 0.70, 2.90), m['steel'])              # radiator grille
    rf.box_mm((-4.155, -1.15, 0.55), (-3.70, 1.15, 1.90), paint)                  # counterweight
    rf.box_mm((-1.70, -0.85, 1.45), (0.15, 0.85, 1.85), paint)                    # cab base
    cab_glass(rf, -1.60, 0.10, 0.80, 1.85, 3.70, m, paint)                        # ROPS top 3.82
    rf.box_mm((0.08, -0.6, 3.55), (0.14, 0.6, 3.65), m['lamp'])                   # work lights
    for s in (1, -1):                                                             # rear fenders
        rf.box_mm((-2.65, min(s * 0.86, s * 1.65), 1.95), (-1.15, max(s * 0.86, s * 1.65), 2.05), paint)
    rf.cyl_between((-2.60, 0.45, 3.06), (-2.60, 0.45, 3.76), 0.07, m['steel'], seg=12)  # exhaust
    rf.box_mm((-0.35, -0.42, 0.60), (-0.05, 0.42, 1.70), m['steel'])              # hinge yoke
    rf.box_mm((-1.60, 0.56, 0.80), (-0.70, 0.95, 1.40), m['steel'])               # fuel tank
    pb.ladder(rf, (-1.10, 1.00, 0.45), 1.45, m['steel'], facing=90, width=0.45)
    ob_rf = fin(rf, col)

    # --- front frame: towers, front axle ---
    ff = pb.Part("WL_FrontFrame", pivot=(0, 0, HZ))
    ff.box_mm((-0.05, -0.30, 0.65), (0.35, 0.30, 1.65), m['steel'])               # hinge tongue
    ff.box_mm((0.30, -0.42, 0.75), (2.60, 0.42, 1.50), paint)
    ff.cyl(0.24, 2.0, (WB / 2, 0, TR), m['grey'], rot=(90, 0, 0), seg=16)         # front axle
    for s in (1, -1):
        ff.box_mm((1.05, min(s * 0.38, s * 0.50), 0.95), (1.85, max(s * 0.38, s * 0.50), 2.45), paint)
        ff.cyl(0.13, 0.40, (A.x, s * 0.57, A.z), m['grey'], rot=(90, 0, 0), seg=14)   # arm pivot pin
        ff.box_mm((0.80, min(s * 0.45, s * 0.65), 0.95), (1.05, max(s * 0.45, s * 0.65), 1.20), m['steel'])
        ff.box_mm((1.15, min(s * 0.86, s * 1.65), 2.00), (2.65, max(s * 0.86, s * 1.65), 2.08), paint)
    ff.box_mm((0.55, -0.18, 1.50), (0.95, 0.18, 2.05), m['steel'])                # tilt cyl bracket
    ff.box_mm((2.55, -0.9, 1.30), (2.62, -0.6, 1.45), m['lamp'])
    ff.box_mm((2.55, 0.6, 1.30), (2.62, 0.9, 1.45), m['lamp'])
    ob_ff = fin(ff, col)
    pm.parent(ob_ff, ob_rf)

    wheels = []
    for x, par, t in ((WB / 2, ob_ff, "F"), (-WB / 2, ob_rf, "R")):
        for s, side in ((1, "L"), (-1, "R")):
            w = pm.wheel(f"WL_Wheel_{t}{side}", (x, s * TREAD / 2, TR), TR, TW, col, m, rim_r=0.42)
            pm.parent(w, par)
            wheels.append(w)

    # --- lift arms with cross tube ---
    ar = pb.Part("WL_LiftArms", pivot=A)
    for s in (1, -1):
        y = s * 0.70
        ar.beam_between(A + Vector((0, y, 0)), B0 + Vector((0, y, 0)), 0.12, 0.42, paint)
        ar.cyl(0.12, 0.16, B0 + Vector((0, y, 0)), m['grey'], rot=(90, 0, 0), seg=14)
        lug = A + dirv * 1.05 - perp * 0.22 + Vector((0, s * 0.62, 0))
        ar.box((0.25, 0.08, 0.25), lug, m['steel'])
        ar.beam_between(C_ARM + Vector((0, y, 0)), C0 + Vector((0, y, 0)), 0.10, 0.30, paint)  # tube bracket
    ar.cyl_between(C0 + Vector((0, -0.70, 0)), C0 + Vector((0, 0.70, 0)), 0.14, paint, seg=16)
    ob_ar = fin(ar, col)
    pm.parent(ob_ar, ob_ff)

    # --- bell-crank (tilt lever) and link ---
    lv = pb.Part("WL_TiltLever", pivot=C0)
    for s in (1, -1):
        y = s * 0.12
        lv.beam_between(T0 + Vector((0, y, 0)), C0 + Vector((0, y, 0)), 0.06, 0.26, paint)
        lv.beam_between(C0 + Vector((0, y, 0)), U0 + Vector((0, y, 0)), 0.06, 0.26, paint)
    for q in (T0, C0, U0):
        lv.cyl(0.08, 0.34, q, m['grey'], rot=(90, 0, 0), seg=12)
    ob_lv = fin(lv, col)
    pm.parent(ob_lv, ob_ar)

    lk = pb.Part("WL_TiltLink", pivot=U0)
    lk.beam_between(U0, D0, 0.12, 0.18, m['steel'])
    ob_lk = fin(lk, col, x_toward=D0)
    pm.parent(ob_lk, ob_lv)

    # --- bucket ---
    bk = pb.Part("WL_Bucket", pivot=B0)
    bucket(bk, B0, PROF, BW, 0.04, m['steel'], side_m=paint)
    bk.box((0.08, BW, 0.06), B0 + xz(1.56, -0.65), m['grey'])                     # cutting edge
    for s in (1, -1):
        bk.box((0.30, 0.10, 0.30), B0 + Vector((-0.06, s * 0.70, 0)), m['steel'])  # hinge ears
    bk.box((0.28, 0.24, 0.28), D0 + xz(0.02, 0), m['steel'])                      # link ear
    ob_bk = fin(bk, col)
    pm.parent(ob_bk, ob_ar)

    # link aims at the bucket pin through an empty carried by the bucket
    e = bpy.data.objects.new("WL_TiltLink_Aim", None)
    e.empty_display_size = 0.05
    e.location = D0
    col.objects.link(e)
    pm.parent(e, ob_bk)
    c = ob_lk.constraints.new('DAMPED_TRACK')
    c.target, c.track_axis = e, 'TRACK_X'

    # --- cylinders ---
    pm.hyd_cyl("WL_TiltCyl", F0, T0, 0.11, col, m, base_par=ob_ff, tip_par=ob_lv)
    for s, t in ((1, "L"), (-1, "R")):
        base = Vector((0.92, s * 0.55, 1.08))
        tip = A + dirv * 1.05 - perp * 0.22 + Vector((0, s * 0.55, 0))
        pm.hyd_cyl(f"WL_LiftCyl_{t}", base, tip, 0.10, col, m, base_par=ob_ff, tip_par=ob_ar)
        pm.hyd_cyl(f"WL_SteerCyl_{t}", (-0.95, s * 0.48, 1.05), (0.55, s * 0.48, 1.05), 0.07, col, m,
                   base_par=ob_rf, tip_par=ob_ff)
    pb.ref_human(ref, (-1.0, 2.6, 0))

    TH_MAX = math.degrees(math.asin((4.554 - A.z) / L_ARM))

    def pose():
        """Arms at maximum lift (hinge pin 4.55 m), bucket racked back 45 deg (holding a load), slight articulation."""
        d_th = TH_MAX - th0
        beta = 45.0
        ob_ar.rotation_euler.y = -math.radians(d_th)
        ob_bk.rotation_euler.y = -math.radians(beta - d_th)
        C1 = A + rot_xz(C0 - A, d_th)
        B1 = A + rot_xz(B0 - A, d_th)
        D1 = B1 + rot_xz(D0 - B0, beta)
        phi = solve_lever(C1, U0 - C0, D1, LINK, d_th)
        ob_lv.rotation_euler.y = -math.radians(phi - d_th)
        ob_ff.rotation_euler.z = math.radians(12)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_WheelLoader.png", (10.5, -9.5, 4.5), (0.5, 0, 1.6), 35),
        ("Preview_WheelLoader_Raised.png", (11.0, -10.0, 5.0), (1.0, 0, 2.6), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_WheelLoader.png, Preview_WheelLoader_Raised.png",
                about=f"""
Articulated wheel loader with a Z-bar linkage and a 5.4 m³ general-purpose bucket (Cat 980 size,
no branding). Moves flux, limestone and reverts in the receiving area and clears slag and spillage.
Origin is the ground point under the articulation hinge. +X is the bucket end.
""",
                moving=f"""
| Part | Motion |
|---|---|
| WL_FrontFrame | Articulates (yaw) about local Z at the hinge, about ±40° (estimated). Child of WL_RearFrame |
| WL_LiftArms | Rotate about local Y at the arm pivot. 0° = carry; about -{TH_MAX - th0:.1f}° (negative Y raises) = maximum lift, hinge pin 4.55 m |
| WL_Bucket | Rotates about local Y at the hinge pin, relative to the arms. The linkage reaches about -40° (rack back, negative Y) to +45° (dump). At full lift the preview uses arms -{TH_MAX - th0:.1f}° and bucket +{TH_MAX - th0 - 45:.1f}°, i.e. racked back 45° in world |
| WL_TiltLever | Bell-crank on the arm cross tube; rotates about local Y. Follows the bucket: solve it so the link ({LINK} m, lower lever arm {R_U} m) closes between the lever pin and the bucket top pin (the script's solve_lever does this) |
| WL_TiltLink | Look-at: pivot on the lever, local +X aims at the bucket top pin (Damped Track in the .blend) |
| WL_TiltCyl / WL_LiftCyl_L/R / WL_SteerCyl_L/R _Barrel / _Rod | Look-at pairs: each half aims local +X at the other's pivot |
| WL_Wheel_FL..RR | Spin about local Y, {pl.deg_per_metre(TR):.1f}° per metre travelled (r {TR} m) |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Wheelbase, tread | 3.80 m, 2.44 m | Sourced (Cat 980 spec sheet) |
| Length without bucket, hood height, ROPS height | 8.155 m, 3.064 m, 3.83 m | Sourced |
| Hinge pin height at carry / maximum lift | 0.68 m / 4.55 m | Sourced (configuration-dependent; 0.63 m and 4.78 m are also published) |
| Bucket 5.4 m³ | Width 3.25 m, profile | Capacity sourced; width and profile estimated |
| Tyres 29.5R25 | r 0.935, 0.75 wide | Size sourced, model dimensions approximate |
| Arm pivot, linkage geometry, articulation hinge height 1.15 m | | Estimated (own layout, not from a Cat drawing) |
""",
                sources="Cat 980 product and dealer spec pages (cat.com, zieglercat.com, ringpower.com)")


# ===========================================================================
# Skid steer
# ===========================================================================

def build_skid_steer():
    name = "SM_SkidSteer"
    col, ref, m = pm.start(name)
    paint = m['yellow']
    # Sourced (Cat 262D3): wheelbase 1.249, width over tyres 1.676, cab top 2.11, length 2.995 /
    # 3.714 with bucket, bucket pin 0.20 carry / 3.172 max lift, 1.73 m bucket, 12x16.5 tyres.
    WB, TR, TW = 1.249, 0.42, 0.31
    WY = 1.676 / 2 - TW / 2
    P = xz(-1.15, 1.65)                  # lift arm pivot at the rear towers (estimated)
    K = xz(0.55, 1.62)                   # arm knee in front of the cab
    B0 = xz(1.40, 0.20)                  # bucket pin at carry (height sourced)
    AY = 0.80                            # arm centre line (outside the cab)
    PROF = [(-0.05, 0.50), (-0.06, 0.05), (0.08, -0.19), (0.72, -0.20)]

    bd = pb.Part("SS_Body")
    bd.box_mm((-1.55, -0.50, 0.25), (0.85, 0.50, 1.05), paint)                    # main frame / chaincases
    for s in (1, -1):
        bd.box_mm((-0.85, min(s * 0.50, s * 0.68), 0.30), (0.85, max(s * 0.50, s * 0.68), 0.55), m['steel'])
        bd.box_mm((-1.55, min(s * 0.62, s * 0.74), 0.55), (-0.90, max(s * 0.62, s * 0.74), 1.75), paint)  # towers
        bd.cyl(0.07, 0.20, (P.x, s * 0.74, P.z), m['grey'], rot=(90, 0, 0), seg=12)
        bd.box_mm((-0.75, min(s * 0.80, s * 0.86), 0.45), (0.75, max(s * 0.80, s * 0.86), 0.50), m['steel'])  # step
    bd.box_mm((-1.55, -0.62, 1.05), (-0.85, 0.62, 1.35), paint)                   # engine cover
    bd.box_mm((-1.58, -0.45, 0.45), (-1.54, 0.45, 1.00), m['steel'])              # rear door grille
    cab_glass(bd, -0.80, 0.55, 0.52, 1.05, 2.00, m, paint)                        # cab top 2.11
    bd.box_mm((-0.70, -0.25, 1.05), (-0.25, 0.25, 1.40), m['steel'])              # seat
    ob_bd = fin(bd, col)

    wheels = []
    for x, t in ((WB / 2, "F"), (-WB / 2, "R")):
        for s, side in ((1, "L"), (-1, "R")):
            w = pm.wheel(f"SS_Wheel_{t}{side}", (x, s * WY, TR), TR, TW, col, m, rim_r=0.24)
            pm.parent(w, ob_bd)
            wheels.append(w)

    dr = pb.Part("SS_CabDoor", pivot=(0.57, 0.50, 1.10))
    dr.box_mm((0.55, -0.50, 1.10), (0.59, 0.50, 1.95), m['glass'])
    dr.box_mm((0.54, -0.50, 1.08), (0.60, 0.50, 1.12), m['steel'])
    dr.box_mm((0.54, -0.50, 1.93), (0.60, 0.50, 1.97), m['steel'])
    ob_dr = fin(dr, col)
    pm.parent(ob_dr, ob_bd)

    ar = pb.Part("SS_LiftArms", pivot=P)
    for s in (1, -1):
        y = Vector((0, s * AY, 0))
        ar.beam_between(P + y, K + y, 0.08, 0.22, paint)
        ar.beam_between(K + y, B0 + y + xz(0, 0.10), 0.08, 0.22, paint)
        ar.cyl(0.08, 0.12, B0 + y, m['grey'], rot=(90, 0, 0), seg=12)
    ar.cyl_between(K + xz(0.12, -0.25) + Vector((0, -AY, 0)), K + xz(0.12, -0.25) + Vector((0, AY, 0)),
                   0.07, paint, seg=12)                                           # cross tube
    ob_ar = fin(ar, col)
    pm.parent(ob_ar, ob_bd)

    bk = pb.Part("SS_Bucket", pivot=B0)
    bucket(bk, B0, PROF, 1.73, 0.02, m['steel'], side_m=paint)
    bk.box_mm((B0.x - 0.10, -0.80, B0.z - 0.15), (B0.x - 0.04, 0.80, B0.z + 0.55), m['steel'])  # coupler plate
    ob_bk = fin(bk, col)
    pm.parent(ob_bk, ob_ar)

    for s, t in ((1, "L"), (-1, "R")):
        pm.hyd_cyl(f"SS_LiftCyl_{t}", (-1.05, s * 0.70, 0.62), (-0.25, s * 0.70, 1.62), 0.045, col, m,
                   base_par=ob_bd, tip_par=ob_ar)
        pm.hyd_cyl(f"SS_TiltCyl_{t}", K + xz(0.12, -0.20) + Vector((0, s * 0.45, 0)),
                   B0 + xz(-0.07, 0.45) + Vector((0, s * 0.45, 0)), 0.04, col, m,
                   base_par=ob_ar, tip_par=ob_bk)
    pb.ref_human(ref, (0.0, 1.6, 0))

    TH0 = ang_xz(B0 - P)
    TH_MAX = math.degrees(math.asin((3.172 - P.z) / (B0 - P).length))

    def pose():
        """Arms at full height (bucket pin 3.17 m), bucket kept level, door open."""
        d = TH_MAX - TH0
        ob_ar.rotation_euler.y = -math.radians(d)
        ob_bk.rotation_euler.y = math.radians(d)
        ob_dr.rotation_euler.z = math.radians(80)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_SkidSteer.png", (4.6, -4.4, 2.3), (0.1, 0, 0.9), 35),
        ("Preview_SkidSteer_Raised.png", (5.0, -4.8, 2.8), (0.3, 0, 1.6), 35, True),
    ], pose=pose)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri,
                previews="Preview_SkidSteer.png, Preview_SkidSteer_Raised.png",
                about="""
Skid steer loader with radial lift arms and a 1.73 m low-profile bucket (Cat 262 size, no
branding), for clean-up under conveyors and in the shed. Origin is the ground point midway between
the axles. +X is the bucket end. Skid steering: left and right wheels turn independently.
""",
                moving=f"""
| Part | Motion |
|---|---|
| SS_LiftArms | Rotate about local Y at the rear tower pivot; 0° carry, about -{TH_MAX - TH0:.1f}° = full height (bucket pin 3.17 m) |
| SS_Bucket | Rotates about local Y at the pin. +{TH_MAX - TH0:.1f}° keeps it level at full height; about -30° racks back, +50° dumps |
| SS_CabDoor | Front door, hinged on its left vertical edge: rotate about local Z, 0 to +80° (opens outward) |
| SS_LiftCyl_L/R, SS_TiltCyl_L/R _Barrel / _Rod | Look-at pairs |
| SS_Wheel_FL..RR | Spin about local Y, {pl.deg_per_metre(TR):.1f}° per metre (r {TR} m). Left pair and right pair at independent speeds |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Wheelbase, width over tyres, cab top | 1.249 m, 1.676 m, 2.11 m | Sourced (Cat 262D3 spec) |
| Length without / with bucket | 2.995 m / 3.71 m | Sourced; the model is 2.95 / 3.67 m |
| Bucket pin carry / max lift | 0.20 m / 3.17 m | Sourced |
| Bucket width 1.73 m | | Sourced; depth and profile estimated |
| Tyres 12x16.5 (r 0.42 m) | | Size sourced, radius approximate |
| Arm pivot, knee, cylinder pins | | Estimated |
""",
                sources="Cat 262D3 spec pages (cat.com, ringpower.com, miltoncat.com)")


# ===========================================================================
# Counterbalance forklifts (shared builder)
# ===========================================================================

def forklift(name, pre, P, m):
    """
    Build a counterbalance forklift from the parameter dict P. Origin: ground under the front
    axle centre, +X toward the forks. Returns dict of key objects and derived numbers.
    Mast stages slide along local Z, child of the previous stage; the outer mast tilts about Y.
    """
    col = bpy_col(name)
    paint, dark = m['orange'] if P['paint'] == 'orange' else m['yellow'], m['steel']
    hw = P['width'] / 2
    WB = P['wheelbase']
    FR, FW, RR, RW = P['f_r'], P['f_w'], P['r_r'], P['r_w']
    XM = P['mast_x']                      # tilt pin x
    ZT = P['tilt_z']                      # tilt pin height
    MW = P['mast_w']                      # outer upright centre spacing
    ch = P['channel']                     # upright section (x, y)

    # --- body ---
    bd = pb.Part(pre + "_Body")
    xr = P['rear_x']
    ci = hw - P['fender_w'] - 0.03                                                        # chassis half width between wheels
    bd.box_mm((-WB - RR, -ci, 0.18), (XM - 0.12, ci, P['deck_z']), paint)                 # chassis
    zw = 2 * max(FR, RR) + 0.08                                                           # underside of full-width deck
    bd.box_mm((-WB + RR + 0.05, -hw, zw), (XM - 0.12, hw, P['deck_z']), paint)            # side pods over the wheels
    x_cw = -WB - RR - 0.05
    bd.box_mm((xr, -hw, 0.20), (x_cw, hw, P['cw_top']), dark)                             # counterweight, behind wheels
    bd.box_mm((x_cw, -hw, 2 * RR + 0.08), (xr + P['cw_len'], hw, P['cw_top']), dark)      # counterweight over wheels
    bd.box_mm((xr + P['cw_len'], -hw, P['deck_z'] - 0.1), (-WB * 0.3, hw, P['deck_z']), paint)  # hood
    for x in (0.0, -WB):
        for s in (1, -1):
            r = FR if x == 0 else RR
            bd.box_mm((x - r - 0.05, min(s * (hw - 0.02), s * (hw - P['fender_w'])), 2 * r + 0.03),
                      (x + r + 0.05, max(s * (hw - 0.02), s * (hw - P['fender_w'])), 2 * r + 0.08), dark)
    bd.cyl(FR * 0.5, P['width'] - 0.3, (0, 0, FR), m['grey'], rot=(90, 0, 0), seg=14)      # drive axle
    bd.box_mm((-WB - 0.15, -hw + 0.35, RR * 0.6), (-WB + 0.15, hw - 0.35, RR * 1.2), m['grey'])  # steer axle
    sx = P['seat_x']
    bd.box_mm((sx - 0.25, -0.25, P['deck_z']), (sx + 0.25, 0.25, P['deck_z'] + 0.45), dark)  # seat
    bd.box_mm((sx - 0.30, -0.25, P['deck_z'] + 0.45), (sx - 0.22, 0.25, P['deck_z'] + 0.95), dark)
    sw = Vector((sx + 0.55, 0, P['deck_z'] + 0.7))
    bd.cyl_between((sx + 0.70, 0, P['deck_z']), sw, 0.04, dark, seg=8)                     # steering column
    bd.cyl(0.18, 0.04, sw + Vector((0, 0, 0.03)), dark, rot=(0, -30, 0), seg=16)          # steering wheel
    gz = P['guard_z']
    if P['cab']:
        cab_glass(bd, P['guard_xr'], P['guard_xf'], P['guard_hw'], P['deck_z'], gz - 0.12, m, paint)
    else:
        overhead_guard(bd, P['guard_xf'], P['guard_xr'], P['guard_hw'], P['deck_z'], gz - 0.09, dark)
    bd.box_mm((XM - 0.5, -0.12, ZT - 0.25), (XM - 0.12, 0.12, ZT + 0.15), m['grey'])       # tilt bracket
    bd.box_mm((xr - 0.02, -hw + 0.2, P['cw_top'] - 0.3), (xr + 0.02, -hw + 0.4, P['cw_top'] - 0.15), m['red'])
    bd.box_mm((xr - 0.02, hw - 0.4, P['cw_top'] - 0.3), (xr + 0.02, hw - 0.2, P['cw_top'] - 0.15), m['red'])
    ob_bd = fin(bd, col)

    wheels = []
    fy = hw - P['fender_w'] / 2
    for s, t in ((1, "L"), (-1, "R")):
        if P['dual']:
            for k, dy in (("", 0.0), ("2", -FW - 0.03)):
                c = (0.0, s * (fy + (dy if k else 0.0)), FR)
                w = pm.wheel(f"{pre}_Wheel_F{t}{k}", c, FR, FW, col, m)
                pm.parent(w, ob_bd)
                wheels.append(w)
        else:
            w = pm.wheel(f"{pre}_Wheel_F{t}", (0.0, s * fy, FR), FR, FW, col, m)
            pm.parent(w, ob_bd)
            wheels.append(w)
        w = pm.wheel(f"{pre}_Wheel_R{t}", (-WB, s * (hw - RW / 2 - 0.08), RR), RR, RW, col, m)
        pm.parent(w, ob_bd)
        wheels.append(w)

    # --- mast stages ---
    stages = []
    par = None
    z0 = P['mast_z0']
    for i, (nm, h, inset) in enumerate(P['stages']):
        st = pb.Part(f"{pre}_{nm}", pivot=(XM, 0, ZT) if i == 0 else (XM, 0, z0))
        x = XM + i * (ch[0] + 0.01)
        yy = MW / 2 - inset
        for s in (1, -1):
            st.box_mm((x, s * yy - ch[1] / 2, z0), (x + ch[0], s * yy + ch[1] / 2, z0 + h), dark)
        for zz in (z0 + 0.05, z0 + h - 0.08, z0 + h * 0.5):
            st.box_mm((x, -yy, zz), (x + ch[0] * 0.6, yy, zz + 0.08), dark)
        if i == 0:   # lift cylinder barrels behind the outer mast + tilt lugs
            for s in (1, -1):
                st.cyl(P['lift_r'], h * 0.92, (XM - 0.07, s * (yy - 0.15), z0 + h * 0.46), m['grey'], seg=14)
                st.box((0.15, 0.08, 0.15), (XM - 0.06, s * 0.22, P['tilt_tip_z']), m['grey'])
        else:        # rods / chain sheaves on the inner stages
            for s in (1, -1):
                st.cyl(P['lift_r'] * 0.5, h * 0.95, (XM - 0.07, s * (MW / 2 - P['stages'][0][2] - 0.15),
                                                     z0 + h * 0.5), m['grey'], seg=10)
            st.cyl(ch[0] * 0.55, MW - 2 * inset - 0.1, (x + ch[0] / 2, 0, z0 + h - 0.05), m['grey'],
                   rot=(90, 0, 0), seg=14)
        ob = fin(st, col)
        if par is not None:
            pm.parent(ob, par)
        else:
            pm.parent(ob, ob_bd)
        stages.append(ob)
        par = ob

    # --- carriage, side shift, forks ---
    n_st = len(P['stages'])
    xc = XM + n_st * (ch[0] + 0.01) + 0.02
    cw2 = P['carr_w'] / 2
    zc0, zc1 = 0.10, 0.10 + P['carr_h']
    ca = pb.Part(f"{pre}_Carriage", pivot=(xc, 0, zc0))
    ca.box_mm((xc, -cw2, zc0), (xc + 0.06, cw2, zc0 + 0.12), dark)
    ca.box_mm((xc, -cw2, zc1 - 0.12), (xc + 0.06, cw2, zc1), dark)
    for s in (1, -1):
        ca.box_mm((xc, s * 0.25 - 0.04, zc0), (xc + 0.05, s * 0.25 + 0.04, zc1), dark)
    br_top = zc1 + P['backrest_h']                                                     # load backrest
    for i in range(7):
        y = -cw2 + 0.04 + (P['carr_w'] - 0.08) * i / 6
        ca.box_mm((xc + 0.01, y - 0.02, zc1), (xc + 0.05, y + 0.02, br_top), dark)
    ca.box_mm((xc + 0.01, -cw2, br_top - 0.05), (xc + 0.05, cw2, br_top), dark)
    ob_ca = fin(ca, col)
    pm.parent(ob_ca, stages[-1])

    xs = xc + 0.07
    ss = pb.Part(f"{pre}_SideShift", pivot=(xs, 0, zc0))
    ss.box_mm((xs, -cw2 + 0.05, zc0 + 0.02), (xs + 0.05, cw2 - 0.05, zc0 + 0.13), m['grey'])
    ss.box_mm((xs, -cw2 + 0.05, zc1 - 0.13), (xs + 0.05, cw2 - 0.05, zc1 - 0.02), m['grey'])
    ob_ss = fin(ss, col)
    pm.parent(ob_ss, ob_ca)

    forks = []
    ft, fwid, fl = P['fork']                       # thickness, width, length
    xf = xs + 0.05
    for s, t in ((1, "L"), (-1, "R")):
        y = s * P['fork_y']
        fk = pb.Part(f"{pre}_Fork_{t}", pivot=(xf, y, zc1 - 0.08))
        fk.box_mm((xf, y - fwid / 2, 0.02), (xf + ft, y + fwid / 2, zc1), dark)       # shank
        fk.box_mm((xf, y - fwid / 2, 0.02), (xf + fl, y + fwid / 2, 0.02 + ft), dark)  # blade
        fk.box_mm((xf - 0.03, y - fwid / 2, zc1 - 0.12), (xf, y + fwid / 2, zc1 - 0.04), dark)  # hook
        ob = fin(fk, col)
        pm.parent(ob, ob_ss)
        forks.append(ob)

    # --- tilt cylinders ---
    for s, t in ((1, "L"), (-1, "R")):
        pm.hyd_cyl(f"{pre}_TiltCyl_{t}", (XM - P['tilt_len'], s * 0.22, ZT + 0.05),
                   (XM - 0.06, s * 0.22, P['tilt_tip_z']), 0.05 * P['cyl_k'], col, m,
                   base_par=ob_bd, tip_par=stages[0])
    return dict(body=ob_bd, stages=stages, carriage=ob_ca, sideshift=ob_ss, forks=forks,
                wheels=wheels, fork_x=xf, zc1=zc1)


def bpy_col(name):
    """Asset collection created by pm.start."""
    return bpy.data.collections[name]


def mast_offsets(h, free_lift, n_stages):
    """
    Model convention for the mast stages at fork lift h (fork top above the lowered position):
    the carriage first rises inside the innermost stage up to the free lift, then the moving stages
    share the rest equally. Returns (carriage offset, [offset of each moving stage relative to its parent]).
    """
    c = min(h, free_lift)
    rest = max(0.0, h - free_lift)
    k = n_stages - 1
    return c, [rest / k] * k


def forklift_result(name, pre, P, objs, about, dims, sources, previews):
    """README entry for a forklift."""
    names = [o.name for o in objs['stages']]
    k = len(names) - 1
    moving = f"""
| Part | Motion |
|---|---|
| {names[0]} | Tilts about local Y at the tilt pins: forward {P['tilt_f']}° (positive Y), back {P['tilt_b']}° (negative Y). Child of {pre}_Body |
| {', '.join(names[1:])} | Slide along local +Z, each child of the stage before. Model convention for fork lift h: carriage rises inside the innermost stage first up to the free lift ({P['free_lift']} m), then the {k} moving stage{'s share' if k > 1 else ' takes'} the rest{' equally' if k > 1 else ''}. Max lift {P['max_lift']} m |
| {pre}_Carriage | Slides along local +Z inside the innermost stage, 0 to {P['free_lift']} m |
| {pre}_SideShift | Slides along local Y, ±{P['side_shift']} m |
| {pre}_Fork_L/R | Slide along local Y on the carriage bars to set the fork spread (centres ±{P['fork_y']} m as modelled) |
| {pre}_TiltCyl_L/R _Barrel / _Rod | Look-at pairs |
| {pre}_Wheel_F* | Spin about local Y, {pl.deg_per_metre(P['f_r']):.1f}° per metre (r {P['f_r']} m) |
| {pre}_Wheel_RL/RR | Spin about local Y, {pl.deg_per_metre(P['r_r']):.1f}° per metre (r {P['r_r']} m), and steer about local Z (about ±75°; rear-wheel steering) |
"""
    return dict(name=name, previews=previews, about=about, moving=moving, dims=dims, sources=sources)


def pose_forklift(objs, P, h, tilt_back=3.0):
    """Raise the forks to lift h and tilt the mast back slightly (preview pose)."""
    c, offs = mast_offsets(h, P['free_lift'], len(objs['stages']))
    objs['stages'][0].rotation_euler.y = -math.radians(tilt_back)
    for st, o in zip(objs['stages'][1:], offs):
        st.location.z += o
    objs['carriage'].location.z += c


# ===========================================================================
# 16 t heavy forklift
# ===========================================================================

P16 = dict(
    paint='yellow', width=2.54, wheelbase=3.40, f_r=0.62, f_w=0.30, r_r=0.62, r_w=0.30, dual=True,
    fender_w=0.66, rear_x=-4.75, cw_len=1.05, cw_top=2.05, deck_z=1.45, seat_x=-1.80,
    guard_xf=-0.75, guard_xr=-2.55, guard_hw=0.75, guard_z=2.92, cab=True,
    mast_x=0.75, tilt_z=0.70, tilt_tip_z=1.85, tilt_len=1.10, mast_w=1.55, channel=(0.20, 0.16),
    mast_z0=0.30, stages=[("MastOuter", 3.645, 0.0), ("MastInner", 3.45, 0.18)], lift_r=0.11,
    carr_w=2.30, carr_h=1.05, backrest_h=0.90, fork=(0.10, 0.25, 2.40), fork_y=0.75,
    free_lift=1.50, max_lift=4.50, side_shift=0.15, tilt_f=6, tilt_b=10, cyl_k=2.0,
)


def build_heavy_forklift():
    name = "SM_HeavyForklift16t"
    col, ref, m = pm.start(name)
    objs = forklift(name, "HF", P16, m)
    pb.ref_human(ref, (-1.5, 2.2, 0))
    # REF load: a cathode bundle stack (two 2 t bundles) on the forks, non-exported
    ld = pb.Part("REF_Load_CathodeBundles", pivot=(objs['fork_x'] + 0.6, 0, 0.2))
    ld.box_mm((objs['fork_x'] + 0.05, -0.53, 0.14), (objs['fork_x'] + 1.10, 0.53, 0.50),
              pb.mat("M_REF_Copper", (0.7, 0.35, 0.2), 0.9, 0.35))
    ld.box_mm((objs['fork_x'] + 1.20, -0.53, 0.14), (objs['fork_x'] + 2.25, 0.53, 0.50),
              pb.mat("M_REF_Copper", (0.7, 0.35, 0.2), 0.9, 0.35))
    ob_ld = ld.finish(ref)
    pm.parent(ob_ld, objs['forks'][0])
    ob_ld.hide_render = True

    def pose():
        ob_ld.hide_render = False
        pose_forklift(objs, P16, 3.0)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_HeavyForklift16t.png", (8.5, -8.0, 3.8), (-0.8, 0, 1.6), 35),
        ("Preview_HeavyForklift16t_Raised.png", (9.0, -8.5, 4.5), (-0.3, 0, 2.6), 35, True),
    ], pose=pose)
    r = forklift_result(name, "HF", P16, objs, about="""
Heavy counterbalance forklift, 16 t at 1.2 m load centre (Kalmar DCG160-12 size, no branding), for
anode stacks and cathode bundles between the casting wheel, tankhouse service bay, stripping line
and dispatch. Enclosed cab, twin front tyres, duplex mast with free lift and hydraulic side shift.
Origin is the ground point under the front (drive) axle centre. +X is the fork end. The Raised
preview carries two 2 t cathode bundles from the REF collection (not exported).
""", dims="""
| Item | Value | Status |
|---|---|---|
| Rated capacity 16 t at 1.2 m load centre | | Sourced (model designation) |
| Overall width 2.54 m, cab (construction) height 2.92 m, turning radius 5.175 m | | Sourced (Lectura specs for DCG160-12) |
| Overall height lowered 3.945 m, fork length 2.40 m, lift 4.5 m (duplex free-lift mast) | | Sourced (dealer listing, one configuration) |
| Length to fork face ~5.7 m (8.1 m with 2.4 m forks) | | Sourced loosely (dealer listing); model is 5.65 m |
| Wheelbase 3.40 m, tyres r 0.62 m, free lift 1.50 m, fork section 250 × 100 mm, carriage 2.30 m | | Estimated |
""", sources="lectura-specs.com DCG160-12, krommenhoek.nl and forkliftcenter.com listings",
        previews="Preview_HeavyForklift16t.png, Preview_HeavyForklift16t_Raised.png")
    r.update(table=table, n_obj=n_obj, n_tri=n_tri)
    return r


# ===========================================================================
# 3 t warehouse forklift
# ===========================================================================

P3 = dict(
    paint='orange', width=1.256, wheelbase=1.65, f_r=0.335, f_w=0.18, r_r=0.29, r_w=0.16, dual=False,
    fender_w=0.20, rear_x=-2.14, cw_len=0.45, cw_top=1.15, deck_z=0.95, seat_x=-0.85,
    guard_xf=-0.20, guard_xr=-1.45, guard_hw=0.52, guard_z=2.165, cab=False,
    mast_x=0.32, tilt_z=0.36, tilt_tip_z=1.05, tilt_len=0.55, mast_w=0.90, channel=(0.10, 0.08),
    mast_z0=0.10, stages=[("MastOuter", 2.05, 0.0), ("MastMiddle", 1.95, 0.09), ("MastInner", 1.85, 0.18)],
    lift_r=0.05, carr_w=1.10, carr_h=0.50, backrest_h=0.70, fork=(0.045, 0.10, 1.20), fork_y=0.35,
    free_lift=1.39, max_lift=4.68, side_shift=0.10, tilt_f=6, tilt_b=8, cyl_k=1.0,
)


def build_forklift_3t():
    name = "SM_Forklift3t"
    col, ref, m = pm.start(name)
    objs = forklift(name, "FL", P3, m)
    pb.ref_human(ref, (-0.8, 1.2, 0))
    ld = pb.Part("REF_Load_Pallet", pivot=(objs['fork_x'] + 0.6, 0, 0.1))
    ld.box_mm((objs['fork_x'] + 0.02, -0.40, 0.0), (objs['fork_x'] + 1.22, 0.40, 0.144),
              pb.mat("M_REF_Pallet", (0.55, 0.42, 0.25), 0, 0.8))
    ld.box_mm((objs['fork_x'] + 0.05, -0.38, 0.144), (objs['fork_x'] + 1.19, 0.38, 1.0),
              pb.mat("M_REF_Crate", (0.35, 0.4, 0.45), 0.5, 0.5))
    ob_ld = ld.finish(ref)
    ob_ld.location.z += 0.02
    pm.parent(ob_ld, objs['forks'][0])
    ob_ld.hide_render = True

    def pose():
        ob_ld.hide_render = False
        pose_forklift(objs, P3, 4.0)

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_Forklift3t.png", (4.5, -4.4, 2.2), (-0.5, 0, 1.0), 35),
        ("Preview_Forklift3t_Raised.png", (6.5, -6.2, 4.2), (0.2, 0, 2.9), 32, True),
    ], pose=pose)
    r = forklift_result(name, "FL", P3, objs, about="""
Standard 3 t counterbalance forklift with a triplex full-free-lift mast and side shift (Linde
H30 size, no branding), for the spares warehouse racks, pallets, drums and IBCs. Open overhead
guard. Origin is the ground point under the front axle centre. +X is the fork end. The Raised
preview carries a REF pallet and crate (not exported).
""", dims="""
| Item | Value | Status |
|---|---|---|
| Rated capacity 3 t at 0.5 m load centre | | Sourced (model class) |
| Length to fork face 2.756 m, width 1.256 m, overall height 2.165 m | | Sourced (dealer listing, Linde H 30 T); model length 2.62 m |
| Triplex mast: max lift 4.68 m, free lift 1.39 m | | Sourced (same listing) |
| Wheelbase 1.65 m, tyres r 0.335 / 0.29 m, forks 1.20 m × 100 × 45 mm | | Estimated |
""", sources="exapro.com Linde H 30 T listings",
        previews="Preview_Forklift3t.png, Preview_Forklift3t_Raised.png")
    r.update(table=table, n_obj=n_obj, n_tri=n_tri)
    return r


# ===========================================================================
# Tugger train
# ===========================================================================

def build_tugger_train():
    name = "SM_TuggerTrain"
    col, ref, m = pm.start(name)
    paint = m['blue']
    # Tractor: 1.73 x 0.996 x 1.96 m with roof (Linde P60 class, sourced listing), wheelbase 1.28 m
    # (Hyster T6.0UT brochure). Carts are own design.
    WB = 1.28
    tr = pb.Part("TT_Tractor")
    tr.box_mm((-0.45, -0.49, 0.18), (1.25, 0.49, 0.75), paint)                   # chassis / battery
    tr.box_mm((0.85, -0.49, 0.75), (1.28, 0.49, 1.05), paint)                    # front cowl
    tr.box_mm((-0.30, -0.25, 0.75), (0.20, 0.25, 1.15), m['steel'])              # seat
    tr.box_mm((-0.32, -0.25, 1.15), (-0.24, 0.25, 1.55), m['steel'])
    tr.cyl_between((0.75, 0, 0.75), (0.55, 0, 1.25), 0.03, m['steel'], seg=8)
    tr.cyl(0.16, 0.03, (0.55, 0, 1.27), m['steel'], rot=(0, -35, 0), seg=16)
    overhead_guard(tr, 0.90, -0.40, 0.45, 0.75, 1.90, m['steel'])               # roof top 1.96
    tr.box_mm((-0.48, -0.15, 0.30), (-0.45, 0.15, 0.50), m['steel'])             # hitch plate
    tr.cyl(0.03, 0.18, (-0.55, 0, 0.40), m['grey'], seg=8)                       # hitch pin
    tr.box_mm((1.26, -0.40, 0.85), (1.29, -0.25, 0.95), m['lamp'])
    tr.box_mm((1.26, 0.25, 0.85), (1.29, 0.40, 0.95), m['lamp'])
    ob_tr = fin(tr, col)
    for x, r, t in ((WB - 0.10, 0.20, "F"), (-0.10, 0.25, "R")):
        for s, side in ((1, "L"), (-1, "R")):
            w = pm.wheel(f"TT_Tractor_Wheel_{t}{side}", (x, s * 0.40, r), r, 0.16, col, m)
            pm.parent(w, ob_tr)

    # Carts: 2.0 x 1.0 m deck at 0.55 m, front swivel castors, fixed rear wheels, hinged tow bar.
    hitch = Vector((-0.55, 0, 0.40))
    CL, BAR = 2.0, 0.80
    carts = []
    for i in range(1, 4):
        xf = hitch.x - BAR                      # cart front end
        xb = xf - CL
        pre = f"TT_Cart{i}"
        fr = pb.Part(pre + "_Frame", pivot=(xf - CL / 2, 0, 0))
        fr.box_mm((xb, -0.50, 0.48), (xf, 0.50, 0.55), m['galv'])                # deck
        for s in (1, -1):
            fr.box_mm((xb, s * 0.45 - 0.04, 0.30), (xf, s * 0.45 + 0.04, 0.48), m['steel'])
            for x in (xb + 0.05, xf - 0.05):
                fr.box_mm((x - 0.025, s * 0.48 - 0.025, 0.55), (x + 0.025, s * 0.48 + 0.025, 1.05), m['yellow'])
            fr.box_mm((xb + 0.02, s * 0.48 - 0.02, 1.02), (xf - 0.02, s * 0.48 + 0.02, 1.05), m['yellow'])
        fr.box_mm((xb - 0.08, -0.12, 0.33), (xb, 0.12, 0.47), m['steel'])        # rear hitch
        fr.box_mm((xf, -0.12, 0.33), (xf + 0.08, 0.12, 0.47), m['steel'])        # tow bar bracket
        ob_fr = fin(fr, col)
        tb = pb.Part(pre + "_TowBar", pivot=(xf + 0.06, 0, 0.40))
        tb.beam_between((xf + 0.06, -0.10, 0.40), (hitch.x, 0, 0.40), 0.04, 0.05, m['steel'])
        tb.beam_between((xf + 0.06, 0.10, 0.40), (hitch.x, 0, 0.40), 0.04, 0.05, m['steel'])
        tb.cyl(0.06, 0.04, (hitch.x, 0, 0.40), m['grey'], seg=14)               # eye
        ob_tb = fin(tb, col)
        pm.parent(ob_tb, ob_fr)
        for s, side in ((1, "L"), (-1, "R")):
            ax = Vector((xf - 0.20, s * 0.38, 0.30))
            cs = pb.Part(f"{pre}_Castor_F{side}", pivot=ax)
            cs.box((0.14, 0.14, 0.02), ax, m['steel'])
            for dy in (-0.05, 0.05):
                cs.box((0.04, 0.012, 0.18), ax + Vector((-0.06, s * 0 + dy, -0.09)), m['steel'])
            ob_cs = fin(cs, col)
            pm.parent(ob_cs, ob_fr)
            w = pm.wheel(f"{pre}_Wheel_F{side}", (ax.x - 0.06, ax.y, 0.15), 0.15, 0.08, col, m)
            pm.parent(w, ob_cs)
            w2 = pm.wheel(f"{pre}_Wheel_R{side}", (xb + 0.25, s * 0.38, 0.15), 0.15, 0.08, col, m)
            pm.parent(w2, ob_fr)
        carts.append(ob_fr)
        hitch = Vector((xb - 0.05, 0, 0.40))
    pb.ref_human(ref, (0.3, 1.1, 0))

    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_TuggerTrain.png", (4.0, -6.5, 3.2), (-3.5, 0, 0.6), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_TuggerTrain.png",
                about="""
Electric seated tow tractor (6 t towing class, Linde P60 / Hyster T6.0UT size, no branding) with
three 2.0 × 1.0 m platform carts for spares, reagents and drums between the warehouse, workshops
and the plant. Origin is the ground point under the tractor's rear axle line (x = 0 at 0.10 m in
front of it). +X is forward. Each cart's tow bar eye sits on the hitch pin of the vehicle ahead.
""",
                moving=f"""
| Part | Motion |
|---|---|
| TT_Tractor_Wheel_FL/FR | Spin about local Y, {pl.deg_per_metre(0.20):.1f}° per metre (r 0.20 m); steer about local Z ±60° |
| TT_Tractor_Wheel_RL/RR | Drive wheels, spin about local Y, {pl.deg_per_metre(0.25):.1f}° per metre (r 0.25 m) |
| TT_CartN_Frame | Free body; follows the hitch ahead. Pivot at the cart centre on the ground |
| TT_CartN_TowBar | Yaws about local Z (±70°) and lifts about local Y (±15°) at the cart bracket; the eye drops on the hitch pin ahead |
| TT_CartN_Castor_FL/FR | Swivel about local Z (trailing castor, wheel axle 0.06 m behind the swivel) |
| TT_CartN_Wheel_* | Spin about local Y, {pl.deg_per_metre(0.15):.1f}° per metre (r 0.15 m). Front wheels are children of the castors |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Tractor 1.73 × 0.996 × 1.96 m (roof) | | Sourced (Linde P 60 Z dealer listing); model 1.77 × 0.98 × 1.96 m |
| Tractor wheelbase 1.28 m, 6 t towing capacity | | Sourced (Hyster T6.0UT brochure) |
| Wheel sizes, hitch height 0.40 m | | Estimated |
| Carts 2.0 × 1.0 m, deck 0.55 m, side stakes 1.05 m, tow bar 0.8 m | | Estimated (own design) |
""",
                sources="exapro.com Linde P 60 Z listing; Hyster T6.0UT brochure (hyster.com)")


# ===========================================================================
# README
# ===========================================================================

BUILDERS = dict(WheelLoader=build_wheel_loader, SkidSteer=build_skid_steer,
                HeavyForklift16t=build_heavy_forklift, Forklift3t=build_forklift_3t,
                TuggerTrain=build_tugger_train)

INTRO = """
On-site mobile plant for logistics: loaders for flux, reverts and clean-up, forklifts for anode and
cathode bundles and for the spares warehouse, and a tugger train for parts. Each asset is a
standalone prop at its own origin (not tied to the plant layout). Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Logistics/build_yard_equipment.py`. Brand names are size
references only; the models carry no logos. In the .blend the moving parts are parented for
posing; hydraulic cylinder halves and the loader tilt link use Damped Track constraints to
non-exported empties. REF objects (scale figure, loads, camera, sun, ground) are not exported.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
