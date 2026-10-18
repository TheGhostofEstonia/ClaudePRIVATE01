"""
byp_helpers.py - extra sub-assemblies for the byproducts and rod line build scripts.

Builds on psh_build.Part (world coordinates in metres). Kept separate from psh_build.py so the
shared module stays identical to the copy on the slag handling branch.
"""
import math

from mathutils import Vector

import psh_build as pb


# --------------------------------------------------------------------------
# Standard material set
# --------------------------------------------------------------------------

def std_mats():
    """Materials shared by all three plants (same names as the earlier assets)."""
    return dict(
        conc=pb.mat("M_Concrete", (0.55, 0.54, 0.52), 0.0, 0.85),
        steel=pb.mat("M_Steel_Structural", (0.25, 0.32, 0.4), 0.6, 0.5),
        grey=pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
        stainless=pb.mat("M_Steel_Stainless", (0.7, 0.71, 0.72), 0.95, 0.25),
        yellow=pb.mat("M_Safety_Yellow", (0.9, 0.7, 0.05), 0.1, 0.5),
        grate=pb.mat("M_Grating", (0.3, 0.3, 0.3), 0.7, 0.6),
        motor=pb.mat("M_Motor_Blue", (0.1, 0.2, 0.45), 0.4, 0.4),
        green=pb.mat("M_Equipment_Green", (0.15, 0.35, 0.2), 0.3, 0.45),
        frp=pb.mat("M_FRP_Tan", (0.62, 0.52, 0.36), 0.0, 0.5),
        rubber=pb.mat("M_Belt_Rubber", (0.04, 0.04, 0.04), 0.0, 0.8),
        clad=pb.mat("M_Cladding_Grey", (0.55, 0.58, 0.6), 0.5, 0.45),
        roof=pb.mat("M_Roof_Sheeting", (0.4, 0.42, 0.45), 0.6, 0.4),
        pipe=pb.mat("M_Pipe_Grey", (0.35, 0.36, 0.36), 0.3, 0.5),
        insul=pb.mat("M_Insulation_Cladding", (0.78, 0.78, 0.76), 0.6, 0.35),
        refr=pb.mat("M_Refractory", (0.6, 0.35, 0.25), 0.0, 0.9),
        copper=pb.mat("M_Copper", (0.85, 0.42, 0.25), 1.0, 0.3),
        liquid=pb.mat("M_Liquid_Green", (0.12, 0.35, 0.3), 0.0, 0.1),
    )


# --------------------------------------------------------------------------
# Vessels
# --------------------------------------------------------------------------

def dished_head(p, c, r, z, m, up=True, seg=32):
    """Shallow torispherical head approximated by two cone frusta; base ring at height z."""
    x, y = c
    h1, h2 = 0.12 * r, 0.1 * r
    if up:
        p.cyl(r, h1, (x, y, z + h1 / 2), m, seg=seg, r2=0.75 * r)
        p.cyl(0.75 * r, h2, (x, y, z + h1 + h2 / 2), m, seg=seg, r2=0.3 * r)
    else:   # create_cone puts radius1 at the bottom
        p.cyl(0.75 * r, h1, (x, y, z - h1 / 2), m, seg=seg, r2=r)
        p.cyl(0.3 * r, h2, (x, y, z - h1 - h2 / 2), m, seg=seg, r2=0.75 * r)


def vtank(p, c, z0, r, h, m, bottom='flat', top='dish', legs=0, leg_m=None, seg=32):
    """
    Vertical vessel. z0 is the bottom of the straight shell.
    bottom: 'flat', 'dish' or 'cone' (60 deg cone). top: 'flat', 'dish' or 'open'.
    legs: number of legs down to grade (z = 0), used with a raised z0.
    """
    x, y = c
    p.cyl(r, h, (x, y, z0 + h / 2), m, seg=seg, cap=(top != 'open'))
    if top == 'dish':
        dished_head(p, c, r, z0 + h, m, up=True, seg=seg)
    if bottom == 'dish':
        dished_head(p, c, r, z0, m, up=False, seg=seg)
    elif bottom == 'cone':
        hc = r * math.tan(math.radians(30)) * 1.7
        p.cyl(0.12 * r, hc, (x, y, z0 - hc / 2), m, seg=seg, r2=r)
        p.cyl(0.12 * r, 0.3, (x, y, z0 - hc - 0.15), m, seg=12)
    if legs:
        lm = leg_m or m
        for i in range(legs):
            a = 2 * math.pi * (i + 0.5) / legs
            q = (x + math.cos(a) * r * 0.95, y + math.sin(a) * r * 0.95)
            p.box((0.2, 0.2, z0 + h * 0.3), (q[0], q[1], (z0 + h * 0.3) / 2), lm)
            p.box((0.4, 0.4, 0.04), (q[0], q[1], 0.02), lm)
    return p


def htank(p, a, b, r, m, saddles=2, saddle_m=None, ground_z=0.0):
    """Horizontal vessel with dished ends between end points a and b (axis along a->b)."""
    a, b = Vector(a), Vector(b)
    p.cyl_between(a, b, r, m, seg=32)
    d = (b - a).normalized()
    for e, s in ((a, -1), (b, 1)):
        p.cyl_between(e, e + d * s * 0.12 * r, r, m, seg=32, r2=0.75 * r)
        p.cyl_between(e + d * s * 0.12 * r, e + d * s * 0.22 * r, 0.75 * r, m, seg=32, r2=0.3 * r)
    sm = saddle_m or m
    for i in range(saddles):
        q = a.lerp(b, 0.2 + 0.6 * i / max(1, saddles - 1))
        side = Vector((-d.y, d.x, 0))
        h = q.z - ground_z
        p.box((0.3, 2 * r * 0.9, h), (q.x, q.y, ground_z + h / 2), sm,
              rot=(0, 0, math.degrees(math.atan2(side.y, side.x)) - 90))


def agitator(name, c, top_z, bot_z, r_imp, col, mats, blades=4):
    """Agitator shaft with pitched blade impeller; separate part, pivot on the shaft top, spins about Z."""
    x, y = c
    a = pb.Part(name, pivot=(x, y, top_z))
    a.cyl(0.05, top_z - bot_z, (x, y, (top_z + bot_z) / 2), mats['stainless'], seg=10)
    a.cyl(0.12, 0.2, (x, y, bot_z + 0.1), mats['stainless'], seg=12)
    for i in range(blades):
        ang = 360.0 * i / blades
        rad = math.radians(ang)
        q = (x + math.cos(rad) * r_imp / 2, y + math.sin(rad) * r_imp / 2, bot_z + 0.1)
        a.box((r_imp, 0.03, r_imp * 0.25), q, mats['stainless'], rot=(35, 0, ang))
    return a.finish(col)


def drive(p, loc, mats, r=0.25, length=0.8, rot=(0, 0, 0)):
    """Motor + gearbox block standing on loc (vertical drive for agitators by default)."""
    x, y, z = loc
    p.box((0.6, 0.6, 0.45), (x, y, z + 0.225), mats['grey'])
    p.cyl(r, length, (x, y, z + 0.45 + length / 2), mats['motor'], rot=rot, seg=16)


# --------------------------------------------------------------------------
# Pipes, platforms, stairs
# --------------------------------------------------------------------------

def pipe_run(p, pts, r, m, elbow=True):
    """Pipe along a polyline of points, with a ball at each bend."""
    pts = [Vector(q) for q in pts]
    for q1, q2 in zip(pts[:-1], pts[1:]):
        p.cyl_between(q1, q2, r, m, seg=12)
    if elbow:
        for q in pts[1:-1]:
            p.sphere(r * 1.05, q, m, seg=12)


def platform(p, x0, y0, x1, y1, z, mats, rails='NSEW', posts=True, post_step=4.0, hole=None):
    """
    Grated deck on columns with handrails on the named sides (N=+y, S=-y, E=+x, W=-x).
    hole: optional (hx0, hy0, hx1, hy1) opening left in the deck for a vessel passing through.
    """
    if hole is None:
        p.box_mm((x0, y0, z - 0.05), (x1, y1, z), mats['grate'])
    else:
        hx0, hy0, hx1, hy1 = hole
        for a, b in (((x0, y0), (hx0, y1)), ((hx1, y0), (x1, y1)),
                     ((hx0, y0), (hx1, hy0)), ((hx0, hy1), (hx1, y1))):
            p.box_mm((a[0], a[1], z - 0.05), (b[0], b[1], z), mats['grate'])
    for (xa, ya, xb, yb) in ((x0, y0, x1, y0), (x0, y1, x1, y1)):
        p.beam_between((xa, ya, z - 0.2), (xb, yb, z - 0.2), 0.15, 0.3, mats['steel'])
    if posts:
        nx = max(1, int((x1 - x0) / post_step))
        ny = max(1, int((y1 - y0) / post_step))
        for i in range(nx + 1):
            for j in (0, ny):
                q = (x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny)
                p.beam_between((q[0], q[1], 0), (q[0], q[1], z - 0.35), 0.2, 0.2, mats['steel'])
    sides = dict(S=((x0, y0, z), (x1, y0, z)), N=((x0, y1, z), (x1, y1, z)),
                 W=((x0, y0, z), (x0, y1, z)), E=((x1, y0, z), (x1, y1, z)))
    for k in rails:
        pb.handrail(p, sides[k][0], sides[k][1], mats['yellow'])


def stair(p, a, b, mats, width=0.9):
    """Straight stair from floor point a to landing point b (b higher), treads every 0.2 m rise."""
    a, b = Vector(a), Vector(b)
    d = b - a
    horiz = Vector((d.x, d.y, 0)).normalized()
    side = Vector((-horiz.y, horiz.x, 0)) * (width / 2)
    for s in (side, -side):
        p.beam_between(a + s, b + s, 0.05, 0.25, mats['steel'])
    n = max(2, int(d.z / 0.2))
    for i in range(1, n):
        q = a.lerp(b, i / n)
        p.box((0.25, width, 0.03), q, mats['grate'],
              rot=(0, 0, math.degrees(math.atan2(horiz.y, horiz.x))))
    pb.handrail(p, a + side * 1.05, b + side * 1.05, mats['yellow'], post_step=2.5)


def portal_building(prefix, x0, y0, x1, y1, eave, col, mats, bay=6.0, walls='NSEW', crane_rail=None):
    """
    Simple steel portal-frame building. Frame, roof and each wall are separate objects so the
    roof and any wall can be hidden for cutaways. crane_rail: rail height for a runway beam.
    """
    fr = pb.Part(prefix + "_Frame", pivot=(x0, y0, 0))
    nb = max(1, int(round((x1 - x0) / bay)))
    ridge = eave + (y1 - y0) * 0.1
    ym = (y0 + y1) / 2
    for i in range(nb + 1):
        x = x0 + (x1 - x0) * i / nb
        for y in (y0, y1):
            fr.beam_between((x, y, 0), (x, y, eave), 0.4, 0.3, mats['steel'])
            fr.box((0.7, 0.7, 0.3), (x, y, 0.15), mats['conc'])
        fr.beam_between((x, y0, eave), (x, ym, ridge), 0.3, 0.5, mats['steel'])
        fr.beam_between((x, ym, ridge), (x, y1, eave), 0.3, 0.5, mats['steel'])
    if crane_rail:
        for y in (y0 + 0.6, y1 - 0.6):
            fr.beam_between((x0, y, crane_rail), (x1, y, crane_rail), 0.4, 0.8, mats['steel'])
    fr.finish(col)
    rf = pb.Part(prefix + "_Roof", pivot=(x0, y0, eave))
    for ya, za, yb, zb in ((y0, eave, ym, ridge), (ym, ridge, y1, eave)):
        rf.quad_strip([[(x0 - 0.3, ya, za + 0.3), (x1 + 0.3, ya, za + 0.3)],
                       [(x0 - 0.3, yb, zb + 0.3), (x1 + 0.3, yb, zb + 0.3)]], mats['roof'])
        rf.quad_strip([[(x1 + 0.3, ya, za + 0.22), (x0 - 0.3, ya, za + 0.22)],
                       [(x1 + 0.3, yb, zb + 0.22), (x0 - 0.3, yb, zb + 0.22)]], mats['roof'])
    rf.finish(col)
    out = {}
    for k in walls:
        if k in 'NS':
            y = y1 if k == 'N' else y0
            w = pb.Part(f"{prefix}_Wall_{k}", pivot=(x0, y, 0))
            w.box_mm((x0, y - 0.05, 0.0), (x1, y + 0.05, eave), mats['clad'])
        else:
            x = x1 if k == 'E' else x0
            w = pb.Part(f"{prefix}_Wall_{k}", pivot=(x, y0, 0))
            w.poly_prism([(y0, 0), (y1, 0), (y1, eave), (ym, ridge), (y0, eave)],
                         x - 0.05, x + 0.05, mats['clad'], plane='YZ')
        out[k] = w.finish(col)
    return out


def flange_x(p, centre, r, m, log, name):
    """Stub flange on a pipe running along X."""
    pb.flange(p, centre, (0, 90, 0), r, m, log, name)


def flange_y(p, centre, r, m, log, name):
    """Stub flange on a pipe running along Y."""
    pb.flange(p, centre, (90, 0, 0), r, m, log, name)


def flange_z(p, centre, r, m, log, name):
    """Stub flange on a vertical pipe."""
    pb.flange(p, centre, (0, 0, 0), r, m, log, name)
