"""
wsl_common.py - helpers shared by the workshop, safety equipment and laboratory build scripts.

Builds on psh_build.py (a copy of the project helper module, kept in this folder so these
scripts do not depend on another branch). Adds:
  - F: a local frame (origin + yaw) so equipment can be written in its own coordinates
  - building shell pieces: walls with openings, steel columns, door leaves, roller shutters
  - furniture used in several buildings: benches, shelving, cabinets, fume hoods
  - a shared material palette
"""
import math

from mathutils import Vector

import psh_build as pb


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

def palette():
    """Materials used across the three assets (names are what Unreal sees)."""
    return dict(
        concrete=pb.mat("M_Concrete_Floor", (0.42, 0.41, 0.39), 0.0, 0.85),
        dado=pb.mat("M_Concrete_Wall", (0.55, 0.54, 0.51), 0.0, 0.9),
        clad=pb.mat("M_Cladding_Grey", (0.62, 0.65, 0.66), 0.5, 0.45),
        roof=pb.mat("M_Cladding_Roof", (0.45, 0.47, 0.48), 0.5, 0.5),
        struct=pb.mat("M_Steel_Structure", (0.16, 0.24, 0.36), 0.3, 0.5),
        steel=pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5),
        bright=pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
        stainless=pb.mat("M_Stainless", (0.7, 0.7, 0.72), 1.0, 0.25),
        machine=pb.mat("M_Machine_Paint", (0.32, 0.42, 0.38), 0.2, 0.45),
        machine2=pb.mat("M_Machine_Paint_Grey", (0.5, 0.52, 0.55), 0.2, 0.45),
        yellow=pb.mat("M_Safety_Yellow", (0.85, 0.6, 0.02), 0.2, 0.45),
        red=pb.mat("M_Safety_Red", (0.6, 0.04, 0.03), 0.1, 0.45),
        green=pb.mat("M_Safety_Green", (0.02, 0.38, 0.12), 0.1, 0.45),
        blue=pb.mat("M_Paint_Blue", (0.05, 0.18, 0.45), 0.2, 0.45),
        orange=pb.mat("M_Curtain_Orange", (0.75, 0.25, 0.02), 0.0, 0.7),
        rubber=pb.mat("M_Rubber_Black", (0.03, 0.03, 0.03), 0.0, 0.85),
        wood=pb.mat("M_Bench_Wood", (0.45, 0.3, 0.16), 0.0, 0.7),
        epoxy=pb.mat("M_Bench_Epoxy", (0.06, 0.06, 0.07), 0.0, 0.3),
        white=pb.mat("M_Enamel_White", (0.85, 0.86, 0.86), 0.1, 0.35),
        lab=pb.mat("M_Instrument_Casing", (0.78, 0.8, 0.82), 0.1, 0.4),
        glass=pb.mat("M_Glass", (0.1, 0.14, 0.16), 0.0, 0.05),
        screen=pb.mat("M_Screen", (0.02, 0.03, 0.05), 0.0, 0.2, emit=((0.25, 0.45, 0.7), 1.5)),
        refract=pb.mat("M_Refractory", (0.62, 0.52, 0.42), 0.0, 0.9),
        hot=pb.mat("M_Glow_Hot", (1.0, 0.4, 0.1), 0.0, 0.5, emit=((1.0, 0.45, 0.1), 6.0)),
        lamp=pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 4.0)),
        beacon=pb.mat("M_Beacon_Amber", (1.0, 0.5, 0.0), 0.0, 0.2, emit=((1.0, 0.5, 0.0), 3.0)),
    )


# --------------------------------------------------------------------------
# Local frame
# --------------------------------------------------------------------------

class F:
    """Local frame: origin (x, y, z) plus a yaw in degrees. Methods take local coordinates."""

    def __init__(self, origin=(0, 0, 0), yaw=0.0):
        self.o = Vector(origin)
        self.yaw = yaw
        a = math.radians(yaw)
        self.c, self.s = math.cos(a), math.sin(a)

    def w(self, p):
        """Local point -> world point."""
        x, y, z = p
        return self.o + Vector((x * self.c - y * self.s, x * self.s + y * self.c, z))

    def sub(self, origin, yaw=0.0):
        """Child frame placed at a local point, yaw added."""
        return F(self.w(origin), self.yaw + yaw)

    def box(self, part, size, loc, m, rot=(0, 0, 0)):
        part.box(size, self.w(loc), m, rot=(rot[0], rot[1], rot[2] + self.yaw))

    def bmm(self, part, mn, mx, m):
        """Box from local min to max corner."""
        size = [b - a for a, b in zip(mn, mx)]
        loc = [(a + b) / 2 for a, b in zip(mn, mx)]
        self.box(part, size, loc, m)

    def cyl(self, part, r, depth, loc, m, rot=(0, 0, 0), seg=24, r2=None):
        part.cyl(r, depth, self.w(loc), m, rot=(rot[0], rot[1], rot[2] + self.yaw), seg=seg, r2=r2)

    def cyl_between(self, part, a, b, r, m, seg=16, r2=None):
        part.cyl_between(self.w(a), self.w(b), r, m, seg=seg, r2=r2)

    def beam(self, part, a, b, w, h, m):
        part.beam_between(self.w(a), self.w(b), w, h, m, roll=self.yaw)

    def sphere(self, part, r, loc, m, seg=16):
        part.sphere(r, self.w(loc), m, seg=seg)

    def xdir(self, pivot_local):
        """World point one metre along local +X from a local pivot (for Part.finish x_toward)."""
        return self.w((pivot_local[0] + 1.0, pivot_local[1], pivot_local[2]))


# --------------------------------------------------------------------------
# Building shell
# --------------------------------------------------------------------------

def wall(part, a, b, h, t, m, openings=(), z0=0.0, glass=None, windows=()):
    """
    Straight wall from plan point a to b (centre line), height h above z0, thickness t.
    openings: (u0, u1, zb, zt) along the wall measured from a, cut through the wall.
    windows:  same tuples; cut and filled with a glass pane (needs glass material).
    """
    a, b = Vector((*a, 0)), Vector((*b, 0))
    L = (b - a).length
    fr = F((a.x, a.y, z0), math.degrees(math.atan2(b.y - a.y, b.x - a.x)))
    holes = list(openings) + list(windows)
    us = sorted({0.0, L, *[o[0] for o in holes], *[o[1] for o in holes]})
    us = [u for u in us if 0.0 <= u <= L]
    for u0, u1 in zip(us[:-1], us[1:]):
        if u1 - u0 < 1e-4:
            continue
        um = (u0 + u1) / 2
        cuts = sorted((o[2], o[3]) for o in holes if o[0] < um < o[1])
        z = 0.0
        for zb, zt in cuts + [(h, h)]:
            if zb - z > 1e-4:
                fr.bmm(part, (u0, -t / 2, z), (u1, t / 2, zb), m)
            z = max(z, zt)
    for u0, u1, zb, zt in windows:
        fr.bmm(part, (u0, -0.01, zb), (u1, 0.01, zt), glass)
        # mullion frame
        fr.bmm(part, (u0, -t / 2, zb - 0.05), (u1, t / 2, zb), m)


def i_column(part, x, y, h, m, d=0.4, bf=0.2, yaw=0.0):
    """I-section column standing on the floor; web along local X (depth d, flange width bf)."""
    fr = F((x, y, 0), yaw)
    tf, tw = 0.018, 0.012
    fr.bmm(part, (d / 2 - tf, -bf / 2, 0), (d / 2, bf / 2, h), m)      # flanges
    fr.bmm(part, (-d / 2, -bf / 2, 0), (-d / 2 + tf, bf / 2, h), m)
    fr.bmm(part, (-d / 2, -tw / 2, 0), (d / 2, tw / 2, h), m)          # web
    fr.bmm(part, (-0.3, -0.3, 0), (0.3, 0.3, 0.02), m)   # base plate


def door_leaf(name, col, hinge, width, height, yaw, m, frame_m=None, glazed=None):
    """
    Hinged door leaf. Pivot on the hinge edge at floor level; the leaf extends along local +X.
    Opening = rotate about local Z (sign depends on swing side; listed in the README).
    """
    fr = F(hinge, yaw)
    p = pb.Part(name, pivot=hinge)
    fr.bmm(p, (0.0, -0.025, 0.0), (width, 0.025, height), m)
    if glazed is not None:
        fr.bmm(p, (width * 0.25, -0.03, height * 0.55), (width * 0.75, 0.03, height * 0.85), glazed)
    # lever handles both sides
    for s in (1, -1):
        fr.box(p, (0.14, 0.03, 0.03), (width - 0.12, s * 0.06, 1.05), frame_m or m)
    return p.finish(col, x_toward=fr.xdir((0, 0, 0)))


def roller_shutter(name, col, frame_part, centre, width, height, yaw, m, box_m):
    """
    Roller shutter in an opening. centre = floor point at the middle of the opening, on the
    outer wall face. The curtain pivot is at its top centre: scale local Z towards 0 to roll it
    up into the coil box. The coil box and guides go into frame_part (static).
    """
    fr = F(centre, yaw)
    # static: coil box above the opening and side guides
    fr.bmm(frame_part, (-width / 2 - 0.15, -0.35, height), (width / 2 + 0.15, 0.05, height + 0.6), box_m)
    fr.bmm(frame_part, (width / 2, -0.12, 0), (width / 2 + 0.1, -0.02, height), box_m)
    fr.bmm(frame_part, (-width / 2 - 0.1, -0.12, 0), (-width / 2, -0.02, height), box_m)
    top = fr.w((0, -0.07, height))
    p = pb.Part(name, pivot=top)
    fr.bmm(p, (-width / 2, -0.09, 0), (width / 2, -0.05, height), m)
    n = max(4, int(height / 0.4))
    for i in range(1, n):
        z = height * i / n
        fr.bmm(p, (-width / 2, -0.1, z - 0.02), (width / 2, -0.09, z + 0.02), m)
    fr.bmm(p, (-width / 2, -0.11, 0), (width / 2, -0.03, 0.08), box_m)   # bottom rail
    return p.finish(col, x_toward=fr.xdir((0, -0.07, height)))


def ceiling_lights(part, xs, ys, z, m_lamp, m_body):
    """Grid of high-bay light fittings (static, emissive underside)."""
    for x in xs:
        for y in ys:
            part.cyl(0.25, 0.25, (x, y, z), m_body, seg=16, r2=0.12)
            part.cyl(0.24, 0.02, (x, y, z - 0.13), m_lamp, seg=16)


# --------------------------------------------------------------------------
# Furniture
# --------------------------------------------------------------------------

def workbench(part, fr, L, D, H, top_m, frame_m, vice_m=None, drawers_m=None):
    """Bench centred on the frame origin, length along local X, front edge on local -Y."""
    fr.bmm(part, (-L / 2, -D / 2, H - 0.05), (L / 2, D / 2, H), top_m)
    for x in (-L / 2 + 0.05, L / 2 - 0.05):
        for y in (-D / 2 + 0.05, D / 2 - 0.05):
            fr.bmm(part, (x - 0.03, y - 0.03, 0), (x + 0.03, y + 0.03, H - 0.05), frame_m)
    fr.bmm(part, (-L / 2 + 0.05, -D / 2 + 0.05, 0.15), (L / 2 - 0.05, D / 2 - 0.05, 0.18), frame_m)
    if drawers_m is not None:
        fr.bmm(part, (L / 2 - 0.55, -D / 2 + 0.02, 0.2), (L / 2 - 0.08, D / 2 - 0.05, H - 0.07), drawers_m)
        for i in range(4):
            z = 0.25 + i * (H - 0.35) / 4
            fr.bmm(part, (L / 2 - 0.4, -D / 2, z + 0.12), (L / 2 - 0.22, -D / 2 + 0.03, z + 0.14), frame_m)
    if vice_m is not None:
        x = -L / 2 + 0.35
        fr.bmm(part, (x - 0.1, -D / 2 - 0.05, H), (x + 0.1, -D / 2 + 0.2, H + 0.12), vice_m)
        fr.bmm(part, (x - 0.1, -D / 2 - 0.12, H + 0.02), (x + 0.1, -D / 2 - 0.05, H + 0.14), vice_m)
        fr.cyl_between(part, (x, -D / 2 - 0.12, H + 0.07), (x, -D / 2 - 0.35, H + 0.07), 0.012, frame_m, seg=8)


def shelving(part, fr, L, D, H, levels, m, load_m=None, seed=0):
    """Open steel shelving, length along local X; optional boxes on the shelves."""
    for x in (-L / 2, L / 2):
        for y in (-D / 2, D / 2):
            fr.bmm(part, (x - 0.025, y - 0.025, 0), (x + 0.025, y + 0.025, H), m)
    for i in range(levels):
        z = 0.15 + i * (H - 0.2) / max(1, levels - 1)
        fr.bmm(part, (-L / 2, -D / 2, z - 0.02), (L / 2, D / 2, z), m)
        if load_m is not None and i < levels - 1:
            k = (seed + i * 7) % 5
            x = -L / 2 + 0.1
            while x < L / 2 - 0.4:
                w = 0.25 + 0.1 * ((k + int(x * 10)) % 3)
                h = 0.15 + 0.05 * ((k + int(x * 7)) % 4)
                fr.bmm(part, (x, -D / 2 + 0.05, z), (x + w, D / 2 - 0.05, z + h), load_m)
                x += w + 0.08


def cabinet(part, fr, W, D, H, body_m, handle_m, doors=2):
    """Closed steel cabinet, front on local -Y."""
    fr.bmm(part, (-W / 2, -D / 2, 0), (W / 2, D / 2, H), body_m)
    for i in range(doors):
        x0 = -W / 2 + W * i / doors
        fr.bmm(part, (x0 + 0.01, -D / 2 - 0.01, 0.05), (x0 + W / doors - 0.01, -D / 2, H - 0.02), body_m)
        hx = x0 + (W / doors - 0.06 if i % 2 == 0 else 0.06)
        fr.bmm(part, (hx - 0.01, -D / 2 - 0.04, H * 0.45), (hx + 0.01, -D / 2 - 0.01, H * 0.6), handle_m)


def locker_bank(part, fr, n, body_m, line_m, W=0.4, D=0.5, H=1.85):
    """Row of n lockers along local X starting at the frame origin, front on local -Y."""
    for i in range(n):
        x0 = i * W
        fr.bmm(part, (x0 + 0.005, -D / 2, 0.1), (x0 + W - 0.005, D / 2, 0.1 + H), body_m)
        for z in (0.1 + H - 0.15, 0.1 + H - 0.2, 0.1 + H - 0.25):
            fr.bmm(part, (x0 + 0.1, -D / 2 - 0.005, z), (x0 + W - 0.1, -D / 2, z + 0.02), line_m)
    fr.bmm(part, (0, -D / 2 - 0.3, 0), (n * W, -D / 2 - 0.05, 0.42), line_m)   # bench seat


def fume_hood(name_prefix, col, part, fr, W, body_m, glass_m, top_m, duct_to_z=None, duct_m=None):
    """
    Bench fume hood (W wide, 0.9 deep, 2.4 tall) on a base cabinet, front on local -Y.
    The sash is a separate part <prefix>_Sash: pivot at its bottom centre, slides along local Z
    (closed = 0, fully open = +0.75 m).
    """
    D = 0.9
    cabinet(part, fr, W, D, 0.85, body_m, top_m, doors=2)
    fr.bmm(part, (-W / 2, -D / 2, 0.85), (W / 2, D / 2, 0.9), top_m)          # work surface
    for s in (-1, 1):                                                              # side posts
        fr.bmm(part, (s * W / 2 - (0.1 if s > 0 else 0), -D / 2, 0.9),
               (s * W / 2 + (0.1 if s < 0 else 0), D / 2, 2.4), body_m)
    fr.bmm(part, (-W / 2, D / 2 - 0.05, 0.9), (W / 2, D / 2, 2.4), body_m)        # back
    fr.bmm(part, (-W / 2, -D / 2, 1.85), (W / 2, D / 2, 2.4), body_m)            # top/fascia
    fr.bmm(part, (-W / 2 + 0.1, -D / 2 + 0.04, 0.92), (W / 2 - 0.1, -D / 2 + 0.08, 0.98), body_m)  # aerofoil
    if duct_to_z is not None:
        fr.cyl(part, 0.15, duct_to_z - 2.4, (0, 0.1, (2.4 + duct_to_z) / 2), duct_m, seg=16)
    piv = (0, -D / 2 + 0.02, 1.15)
    sash = pb.Part(name_prefix + "_Sash", pivot=fr.w(piv))
    fr.bmm(sash, (-W / 2 + 0.1, -D / 2 + 0.0, 1.15), (W / 2 - 0.1, -D / 2 + 0.03, 1.85), glass_m)
    fr.bmm(sash, (-W / 2 + 0.1, -D / 2 - 0.02, 1.15), (W / 2 - 0.1, -D / 2 + 0.03, 1.2), body_m)
    return sash.finish(col, x_toward=fr.xdir(piv))
