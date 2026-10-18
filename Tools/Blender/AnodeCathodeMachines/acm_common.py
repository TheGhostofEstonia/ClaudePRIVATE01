"""
acm_common.py - shared pieces for the anode/cathode machine build scripts.

Imports the shared Tools/Blender/psh_build.py and adds:
  - electrode sizes (one place to change them for all five machines)
  - anode, permanent cathode and copper sheet geometry
  - chain strands with continuous UVs and separate sprockets
  - roller conveyors with one object per roller
  - hydraulic cylinders, guard panels and platforms
  - a small jointed robot arm (parented links)

Machine convention used by every script in this folder:
  origin (0, 0, 0) on the floor at the infeed end, product flows along +X,
  electrodes hang with their faces normal to X (plate in the YZ plane),
  hanger bars / anode lugs run along Y.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# ---------------------------------------------------------------------------
# Electrode sizes, matched to the tankhouse core meshes (Tools/Blender/Tankhouse/
# th_layout.py: SM_PermanentCathode and the anode set's ATC_Anode).
# Blade thickness and pitch sourced, the rest estimated by those threads.
# ---------------------------------------------------------------------------
BLADE_W, BLADE_H, BLADE_T = 1.040, 1.050, 0.00325   # 316L blade below the bar, 3.25 mm (sourced)
EDGE_STRIP_W = 0.018                                # PP edge strip on both side edges
HBAR_L, HBAR_W, HBAR_H = 1.32, 0.025, 0.035         # hanger bar along Y, 25 thick x 35 tall
DEPOSIT_W, DEPOSIT_H, DEPOSIT_T = 1.016, 0.915, 0.008  # copper on each face (~67 kg per sheet)
DEPOSIT_TOP_GAP = 0.13                              # deposit top edge below the hanger-bar underside
ANODE_W, ANODE_H, ANODE_T = 1.000, 1.000, 0.045     # anode body (same as ATC_Anode)
ANODE_LUG_SPAN = 1.32                               # lug tip to lug tip (lugs from |y| 0.50 to 0.66)
ANODE_LUG_H, ANODE_LUG_T = 0.12, 0.040              # lug height (top flush with body) and thickness
SCRAP_T = 0.012                                     # spent anode body thickness (13-20 % left)
PITCH = 0.100                                       # same-type electrode pitch in a cell (sourced)
HANG_Z = 1.60                                       # lug / hanger-bar seat height on the machines

# ---------------------------------------------------------------------------
# Materials (created once per scene through pb.mat's cache)
# ---------------------------------------------------------------------------

def materials():
    """Material set shared by all machines."""
    m = _material_dict()
    # guard mesh: see-through in previews; use a masked mesh material in Unreal
    m['guard'].node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    return m


def _material_dict():
    return {
        'frame': pb.mat("M_Machine_Paint", (0.10, 0.28, 0.55), 0.2, 0.45),
        'yellow': pb.mat("M_Safety_Yellow", (0.85, 0.62, 0.05), 0.1, 0.45),
        'steel': pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5),
        'grey': pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
        'stainless': pb.mat("M_Stainless", (0.62, 0.62, 0.64), 1.0, 0.25),
        'copper': pb.mat("M_Copper", (0.80, 0.38, 0.22), 1.0, 0.3),
        'anode': pb.mat("M_Copper_Anode", (0.45, 0.20, 0.12), 0.9, 0.55),
        'plastic': pb.mat("M_Edge_Strip", (0.08, 0.08, 0.09), 0.0, 0.6),
        'chain': pb.mat("M_Chain", (0.15, 0.15, 0.16), 0.9, 0.45),
        'rubber': pb.mat("M_Rubber", (0.03, 0.03, 0.03), 0.0, 0.85),
        'guard': pb.mat("M_Guard_Mesh", (0.75, 0.62, 0.10), 0.3, 0.5),
        'hydraulic': pb.mat("M_Hydraulic_Rod", (0.80, 0.80, 0.82), 1.0, 0.15),
        'grating': pb.mat("M_Grating", (0.30, 0.30, 0.31), 0.7, 0.6),
        'cabinet': pb.mat("M_Cabinet_Grey", (0.70, 0.71, 0.70), 0.1, 0.5),
        'red': pb.mat("M_Stop_Red", (0.6, 0.03, 0.02), 0.1, 0.4),
        'water': pb.mat("M_Water_Spray", (0.55, 0.70, 0.80), 0.0, 0.1),
        'brush': pb.mat("M_Brush_Nylon", (0.12, 0.25, 0.12), 0.0, 0.8),
        'strap': pb.mat("M_Steel_Strap", (0.35, 0.37, 0.40), 0.9, 0.35),
        'label': pb.mat("M_Label_White", (0.9, 0.9, 0.88), 0.0, 0.7),
        'lamp': pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0)),
        'green': pb.mat("M_Lamp_Green", (0.1, 0.8, 0.2), 0, 0.3, emit=((0.1, 1.0, 0.2), 3.0)),
    }


# ---------------------------------------------------------------------------
# Electrodes. Each function adds to an existing Part so they can be used as
# props (own Part) or merged into REF proxies.
# ---------------------------------------------------------------------------

def add_anode(p, x, seat_z, M, scrap=False):
    """Anode hanging at x with its lug undersides at seat_z (plate in YZ, faces normal X)."""
    t = SCRAP_T if scrap else ANODE_T
    top = seat_z + ANODE_LUG_H                 # body top is flush with the lug tops
    body_h = ANODE_H * (0.82 if scrap else 1.0)  # spent anodes are also eaten from the bottom
    p.box((t, ANODE_W, body_h), (x, 0, top - body_h / 2), M['anode'])
    # lugs stick out sideways from the top corners, from the body edge to the lug span
    lug_len = (ANODE_LUG_SPAN - ANODE_W) / 2
    for s in (-1, 1):
        y = s * (ANODE_W / 2 + lug_len / 2)
        p.box((ANODE_LUG_T, lug_len, ANODE_LUG_H), (x, y, seat_z + ANODE_LUG_H / 2), M['anode'])
    return p


def add_cathode(p, x, seat_z, M, deposit=True):
    """Permanent cathode at x, hanger-bar underside at seat_z. deposit adds the two copper sheets."""
    p.box((HBAR_W, HBAR_L, HBAR_H), (x, 0, seat_z + HBAR_H / 2), M['copper'])
    p.box((BLADE_T, BLADE_W, BLADE_H), (x, 0, seat_z - BLADE_H / 2), M['stainless'])
    for s in (-1, 1):
        p.box((0.010, EDGE_STRIP_W, BLADE_H - 0.03),
              (x, s * (BLADE_W / 2 + EDGE_STRIP_W / 2 - 0.006), seat_z - 0.03 - (BLADE_H - 0.03) / 2),
              M['plastic'])
    if deposit:
        bottom = seat_z - DEPOSIT_TOP_GAP - DEPOSIT_H
        for s in (-1, 1):
            add_sheet(p, x + s * (BLADE_T / 2 + DEPOSIT_T / 2), bottom, M, upright=True)
    return p


def add_sheet(p, x, bottom_z, M, upright=True, y=0.0):
    """One copper cathode sheet. upright: hanging in YZ with bottom at bottom_z; else lying flat."""
    if upright:
        p.box((DEPOSIT_T, DEPOSIT_W, DEPOSIT_H), (x, y, bottom_z + DEPOSIT_H / 2), M['copper'])
    else:
        p.box((DEPOSIT_H, DEPOSIT_W, DEPOSIT_T), (x, y, bottom_z + DEPOSIT_T / 2), M['copper'])
    return p


# ---------------------------------------------------------------------------
# Chain strand: closed loop in the XZ plane with continuous UVs + sprockets
# ---------------------------------------------------------------------------

def chain_strand(prefix, x0, x1, y, z_top, col, M, r=0.16, w=0.05, t=0.03, uv_m=0.5):
    """
    One chain strand running along +X at height z_top (top of the carrying run).
    Builds <prefix>_Chain (loop mesh, U = distance / uv_m) and two sprocket parts
    <prefix>_Sprocket_Head (x1) and _Tail (x0) with pivots on their shafts (spin about Y).
    Returns the loop length in metres.
    """
    cz = z_top - r                     # sprocket centre
    path = []                          # (point, outward normal in XZ)
    n_run = max(4, int((x1 - x0) / 0.25))
    for i in range(n_run + 1):         # top run, tail -> head
        path.append((Vector((x0 + (x1 - x0) * i / n_run, y, z_top)), Vector((0, 0, 1))))
    for i in range(1, 12):             # head wrap
        a = math.pi * i / 12
        nrm = Vector((math.sin(a), 0, math.cos(a)))
        path.append((Vector((x1, y, cz)) + nrm * r, nrm))
    for i in range(n_run + 1):         # bottom return, head -> tail
        path.append((Vector((x1 - (x1 - x0) * i / n_run, y, cz - r)), Vector((0, 0, -1))))
    for i in range(1, 12):             # tail wrap
        a = math.pi * i / 12
        nrm = Vector((-math.sin(a), 0, -math.cos(a)))
        path.append((Vector((x0, y, cz)) + nrm * r, nrm))

    # Rectangular section: (side offset along Y, offset along the normal)
    sec = [(-w / 2, 0), (w / 2, 0), (w / 2, -t), (-w / 2, -t)]
    part = pb.Part(prefix + "_Chain", pivot=(x0, y, cz))
    rows, us, s = [], [], 0.0
    for i, (pt, nrm) in enumerate(path):
        if i:
            s += (pt - path[i - 1][0]).length
        rows.append([part.bm.verts.new(pt + Vector((0, oy, 0)) + nrm * on) for oy, on in sec])
        us.append(s / uv_m)
    total = s + (path[0][0] - path[-1][0]).length
    idx = part._mi(M['chain'])
    vs = [0.0, 0.25, 0.5, 0.75, 1.0]
    for i in range(len(rows)):
        a, b = rows[i], rows[(i + 1) % len(rows)]
        ua, ub = us[i], (us[i + 1] if i + 1 < len(us) else total / uv_m)
        for j in range(4):
            f = part.bm.faces.new((a[j], b[j], b[(j + 1) % 4], a[(j + 1) % 4]))
            f.material_index = idx
            part.uv_faces[f] = [(ua, vs[j]), (ub, vs[j]), (ub, vs[j + 1]), (ua, vs[j + 1])]
    part.finish(col, smooth_angle=30)
    for nm, x in (("Head", x1), ("Tail", x0)):
        sp = pb.Part(f"{prefix}_Sprocket_{nm}", pivot=(x, y, cz))
        sp.cyl(r - 0.01, 0.025, (x, y, cz), M['grey'], rot=(90, 0, 0), seg=20)
        sp.cyl(0.04, 0.12, (x, y, cz), M['steel'], rot=(90, 0, 0), seg=10)
        sp.finish(col)
    return total


def chain_conveyor(prefix, x0, x1, y_half, z_top, col, M, legs=True, r=0.16):
    """Two strands at +-y_half on a steel frame, plus a drive motor at the head end."""
    length = 0.0
    for side, s in (("L", 1), ("R", -1)):
        length = chain_strand(f"{prefix}_{side}", x0, x1, s * y_half, z_top, col, M, r=r)
    fr = pb.Part(prefix + "_Frame", pivot=(x0, 0, 0))
    for s in (-1, 1):
        y = s * (y_half + 0.08)
        fr.box_mm((x0 - 0.1, y - 0.06, z_top - 2 * r - 0.12), (x1 + 0.1, y + 0.06, z_top - 0.04), M['frame'])
        fr.box_mm((x0 - 0.1, s * y_half - 0.04, z_top - 2 * r + 0.02), (x1 + 0.1, s * y_half + 0.04, z_top - 2 * r + 0.05), M['steel'])
        if legs:
            n = max(2, int((x1 - x0) / 2.5) + 1)
            for i in range(n):
                x = x0 + (x1 - x0) * i / (n - 1)
                fr.box_mm((x - 0.08, y - 0.08, 0), (x + 0.08, y + 0.08, z_top - 2 * r - 0.12), M['frame'])
                fr.box((0.3, 0.3, 0.02), (x, y, 0.01), M['steel'])
    # cross ties and the head shaft drive (gearmotor on the -Y side)
    for x in (x0, x1):
        fr.box_mm((x - 0.06, -y_half - 0.1, z_top - 2 * r - 0.25), (x + 0.06, y_half + 0.1, z_top - 2 * r - 0.13), M['frame'])
    fr.cyl(0.03, 2 * y_half + 0.3, (x1, 0, z_top - r), M['grey'], rot=(90, 0, 0), seg=10)
    fr.box((0.35, 0.3, 0.3), (x1, -y_half - 0.35, z_top - r), M['frame'])
    fr.cyl(0.13, 0.4, (x1, -y_half - 0.7, z_top - r), M['frame'], rot=(90, 0, 0), seg=16)
    fr.finish(col)
    return length


# ---------------------------------------------------------------------------
# Roller conveyor: one object per roller so each can spin
# ---------------------------------------------------------------------------

def roller_conveyor(prefix, x0, x1, y_c, z_top, width, col, M, pitch=0.30, r=0.0635,
                    legs=True, base_z=0.0):
    """Driven roller conveyor along X. Rollers <prefix>_Roller_NN spin about Y on their axes."""
    n = int((x1 - x0) / pitch)
    xs = [x0 + pitch / 2 + i * (x1 - x0 - pitch) / max(1, n - 1) for i in range(n)]
    for i, x in enumerate(xs):
        c = (x, y_c, z_top - r)
        rp = pb.Part(f"{prefix}_Roller_{i:02d}", pivot=c)
        rp.cyl(r, width, c, M['grey'], rot=(90, 0, 0), seg=16)
        rp.cyl(0.02, width + 0.14, c, M['steel'], rot=(90, 0, 0), seg=8)
        rp.finish(col)
    fr = pb.Part(prefix + "_Frame", pivot=(x0, y_c, base_z))
    for s in (-1, 1):
        y = y_c + s * (width / 2 + 0.07)
        fr.box_mm((x0, y - 0.05, z_top - r - 0.12), (x1, y + 0.05, z_top - r + 0.06), M['frame'])
        if legs:
            m = max(2, int((x1 - x0) / 2.0) + 1)
            for i in range(m):
                x = x0 + 0.1 + (x1 - x0 - 0.2) * i / (m - 1)
                fr.box_mm((x - 0.06, y - 0.06, base_z), (x + 0.06, y + 0.06, z_top - r - 0.12), M['frame'])
    # chain guard / drive box on the -Y side
    fr.box_mm((x0, y_c - width / 2 - 0.25, z_top - r - 0.10), (x1, y_c - width / 2 - 0.13, z_top - r + 0.04), M['yellow'])
    fr.box((0.4, 0.3, 0.3), (x0 + 0.4, y_c - width / 2 - 0.45, z_top - r - 0.25), M['frame'])
    fr.finish(col)
    return xs


# ---------------------------------------------------------------------------
# Hydraulic cylinder: barrel and rod as separate parts
# ---------------------------------------------------------------------------

def hyd_cylinder(prefix, base, tip, col, M, r=0.07, stroke_frac=0.5):
    """
    Cylinder from base (barrel end) to tip (rod end) at the drawn extension.
    <prefix>_Barrel pivot = base, <prefix>_Rod pivot = tip; both local +X point along the axis,
    so the rod slides along its local -X/+X.
    """
    base, tip = Vector(base), Vector(tip)
    mid = base.lerp(tip, stroke_frac)
    b = pb.Part(prefix + "_Barrel", pivot=base)
    b.cyl_between(base, mid + (tip - base).normalized() * 0.05, r, M['frame'], seg=16)
    b.cyl_between(base - (tip - base).normalized() * 0.05, base + (tip - base).normalized() * 0.05,
                  r * 1.25, M['steel'], seg=16)
    b.finish(col, x_toward=tip)
    rd = pb.Part(prefix + "_Rod", pivot=tip)
    rd.cyl_between(mid - (tip - base).normalized() * 0.15, tip, r * 0.5, M['hydraulic'], seg=12)
    rd.finish(col, x_toward=tip + (tip - base))
    return b, rd


# ---------------------------------------------------------------------------
# Static dressing: guards, platforms, cabinets, HPU
# ---------------------------------------------------------------------------

def guard_fence(p, a, b, M, h=2.0, post=2.0):
    """Mesh guard fence along the floor from a to b (posts + infill panel)."""
    a, b = Vector(a), Vector(b)
    n = max(1, int((b - a).length / post))
    d = (b - a)
    for i in range(n + 1):
        q = a.lerp(b, i / n)
        p.box((0.06, 0.06, h), (q.x, q.y, h / 2), M['yellow'])
    yaw = math.degrees(math.atan2(d.y, d.x))
    c = (a + b) / 2
    p.box((d.length, 0.01, h - 0.25), (c.x, c.y, (h - 0.25) / 2 + 0.15), M['guard'], rot=(0, 0, yaw))


def platform(p, x0, x1, y0, y1, z, M, rails=True, ladder_at=None):
    """Grated platform with legs, handrails on the long sides and an optional ladder."""
    p.box_mm((x0, y0, z - 0.05), (x1, y1, z), M['grating'])
    for x in (x0 + 0.1, x1 - 0.1):
        for y in (y0 + 0.1, y1 - 0.1):
            p.box_mm((x - 0.05, y - 0.05, 0), (x + 0.05, y + 0.05, z - 0.05), M['frame'])
    if rails:
        for y in (y0, y1):
            pb.handrail(p, (x0, y, z), (x1, y, z), M['yellow'])
    if ladder_at:
        pb.ladder(p, (ladder_at[0], ladder_at[1], 0), z + 1.0, M['yellow'], facing=ladder_at[2])


def cabinet(p, loc, M, size=(1.2, 0.5, 2.0), yaw=0):
    """Electrical / control cabinet standing on the floor with a lamp on top."""
    x, y, _ = loc
    p.box(size, (x, y, size[2] / 2), M['cabinet'], rot=(0, 0, yaw))
    p.cyl(0.04, 0.25, (x, y, size[2] + 0.125), M['green'], seg=10)


def hpu(p, loc, M):
    """Hydraulic power unit: tank, two motor-pump sets, filter housing, cooler."""
    x, y, _ = loc
    p.box((2.2, 1.2, 1.0), (x, y, 0.5), M['frame'])
    for dx in (-0.5, 0.5):
        p.cyl(0.18, 0.6, (x + dx, y, 1.32), M['frame'], rot=(0, 90, 0), seg=16)
        p.cyl(0.10, 0.3, (x + dx + 0.42, y, 1.32), M['grey'], rot=(0, 90, 0), seg=12)
    p.cyl(0.08, 0.5, (x - 0.9, y + 0.35, 1.25), M['grey'], seg=12)
    p.box((0.1, 0.9, 0.7), (x + 1.15, y, 1.4), M['steel'])


def portal(p, x, y_half, h, M, depth=0.3, beam=0.3):
    """Two-post portal frame across the line at x (columns at +-y_half, beam on top)."""
    for s in (-1, 1):
        p.box_mm((x - depth / 2, s * y_half - 0.15, 0), (x + depth / 2, s * y_half + 0.15, h), M['frame'])
        p.box((0.6, 0.6, 0.03), (x, s * y_half, 0.015), M['steel'])
    p.box_mm((x - depth / 2, -y_half - 0.15, h), (x + depth / 2, y_half + 0.15, h + beam), M['frame'])


def wash_hood(name, x0, x1, z_seat, plate_bottom, col, M, half_w=1.05):
    """
    Stainless spray hood over a chain conveyor, open at both ends for the hanging
    electrodes: side walls, roof, end walls with a plate-shaped opening, drain tank,
    vertical spray headers either side of the plates and an exhaust stack.
    """
    hd = pb.Part(name, pivot=(x0, 0, 0))
    top = z_seat + 0.6
    for s in (-1, 1):
        hd.box_mm((x0, s * half_w - 0.03, 0.3), (x1, s * half_w + 0.03, top), M['stainless'])
    hd.box_mm((x0, -half_w - 0.03, top), (x1, half_w + 0.03, top + 0.06), M['stainless'])
    for x in (x0, x1):
        for s in (-1, 1):
            hd.box_mm((x - 0.03, min(s * 0.75, s * half_w), 0.3), (x + 0.03, max(s * 0.75, s * half_w), top), M['stainless'])
        hd.box_mm((x - 0.03, -0.75, z_seat + 0.15), (x + 0.03, 0.75, top), M['stainless'])
    hd.box_mm((x0, -half_w - 0.05, 0), (x1, half_w + 0.05, 0.3), M['stainless'])      # drain tank
    hd.cyl(0.25, 1.6, ((x0 + x1) / 2, 0, top + 0.85), M['stainless'], seg=16)         # exhaust stack
    h = z_seat - plate_bottom
    for i in range(6):
        x = x0 + 0.35 + i * (x1 - x0 - 0.7) / 5
        for s in (-1, 1):
            hd.cyl(0.03, h, (x, s * 0.80, plate_bottom + h / 2), M['grey'], seg=8)
    hd.cyl(0.05, x1 - x0, ((x0 + x1) / 2, 0.95, z_seat + 0.45), M['grey'], rot=(0, 90, 0), seg=10)
    return hd.finish(col)


# ---------------------------------------------------------------------------
# Jointed robot arm (six-axis style) as a parented chain of parts
# ---------------------------------------------------------------------------

def robot_arm(prefix, base, col, M, yaw=0.0, reach=1.6, tool=None):
    """
    Floor or pedestal robot with links <prefix>_J1Base .. _J6Flange.
    Each link's origin is its joint; links are parented so rotating a joint moves the rest.
    J1 turns about Z, J2/J3/J5 bend about local Y, J4/J6 roll about the forearm axis (local X).
    tool(part, flange_point) may add a gripper/tool to the flange part.
    """
    bx, by, bz = base
    a = math.radians(yaw)
    fwd = Vector((math.cos(a), math.sin(a), 0))
    upper, fore = reach * 0.45, reach * 0.45
    j2 = Vector((bx, by, bz + 0.65)) + fwd * 0.18
    j3 = j2 + Vector((0, 0, upper))
    j5 = j3 + fwd * fore
    j6 = j5 + fwd * 0.18
    orange = M['yellow']
    parts = []
    p = pb.Part(prefix + "_J0Pedestal", pivot=(bx, by, bz))
    p.cyl(0.32, 0.12, (bx, by, bz + 0.06), M['steel'], seg=20)
    parts.append(p.finish(col))
    p = pb.Part(prefix + "_J1Base", pivot=(bx, by, bz + 0.12))
    p.cyl(0.26, 0.35, (bx, by, bz + 0.30), orange, seg=20)
    p.box((0.42, 0.36, 0.30), (j2.x - fwd.x * 0.05, j2.y - fwd.y * 0.05, j2.z - 0.05), orange, rot=(0, 0, yaw))
    parts.append(p.finish(col))
    p = pb.Part(prefix + "_J2Upper", pivot=j2)
    p.cyl(0.17, 0.42, j2, M['steel'], rot=(90, 0, yaw), seg=16)
    p.beam_between(j2, j3, 0.22, 0.18, orange, roll=yaw)
    parts.append(p.finish(col, x_toward=j2 + fwd))
    p = pb.Part(prefix + "_J3Fore", pivot=j3)
    p.cyl(0.14, 0.34, j3, M['steel'], rot=(90, 0, yaw), seg=16)
    p.cyl_between(j3 - fwd * 0.2, j3 + fwd * (fore * 0.55), 0.10, orange, seg=14)
    parts.append(p.finish(col, x_toward=j3 + fwd))
    p = pb.Part(prefix + "_J4Roll", pivot=j3 + fwd * (fore * 0.55))
    p.cyl_between(j3 + fwd * (fore * 0.55), j5, 0.08, orange, seg=14)
    parts.append(p.finish(col, x_toward=j5))
    p = pb.Part(prefix + "_J5Wrist", pivot=j5)
    p.cyl(0.075, 0.18, j5, M['steel'], rot=(90, 0, yaw), seg=14)
    p.cyl_between(j5, j6 - fwd * 0.03, 0.06, orange, seg=12)
    parts.append(p.finish(col, x_toward=j6))
    p = pb.Part(prefix + "_J6Flange", pivot=j6)
    p.cyl_between(j6 - fwd * 0.03, j6, 0.07, M['grey'], seg=14)
    if tool:
        tool(p, j6, fwd)
    parts.append(p.finish(col, x_toward=j6 + fwd))
    for child, parent in zip(parts[1:], parts[:-1]):
        mw = child.matrix_world.copy()
        child.parent = parent
        child.matrix_world = mw
    return parts


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def out_dir(asset):
    d = os.path.join(REPO, "Meshes", asset)
    os.makedirs(d, exist_ok=True)
    return d


def floor_ref(col, x0, x1, y0, y1):
    """REF floor slab and a 1.8 m figure at the infeed corner."""
    pb.ref_ground(col, (x0, y0, x1, y1), [])
    pb.ref_human(col, (x0 + 1.0, y0 + 1.0, 0))


def moving_rows(col_name, keys):
    """README table rows for objects whose names contain any of keys."""
    import bpy
    rows = []
    for ob in sorted(bpy.data.collections[col_name].all_objects, key=lambda o: o.name):
        if ob.type == 'MESH' and any(k in ob.name for k in keys):
            l = ob.matrix_world.translation
            rows.append(f"| {ob.name} | ({l.x:.3f}, {l.y:.3f}, {l.z:.3f}) |")
    return "\n".join(rows)


UNREAL_NOTE = """## Unreal import

Combine Meshes off. Transform Vertex to Absolute puts every part at the asset origin with its
pivot at the origin too, which is right for static parts. For the moving parts, import a second
time with it off (or use the pivots above) so each part rotates or slides about its own pivot.
Blender +Y becomes Unreal -Y with the default FBX axis settings, so check rotation signs.
Parented robot links keep their hierarchy only with Transform Vertex to Absolute off.

Chains: 1 UV unit = 0.5 m along the chain, so panner speed (U per second) = chain speed (m/s) / 0.5.
The chain mesh is a closed loop with continuous U, like the belt conveyors.
"""


def run(asset, name, build_fn, readme_fn, views, samples=32):
    """
    Pipeline for one asset: wipe scene, build, export FBX (asset collection only),
    write README, save .blend, render previews. views = [(file, cam_loc, target, lens), ...].
    Pass --no-render after "--" on the command line to skip the previews.
    """
    pb.reset_scene()
    pb.clear_material_cache()
    out = out_dir(asset)
    col = pb.collection(name)
    ref = pb.collection("REF")
    build_fn(col, ref, materials())
    pb.export_fbx(os.path.join(out, name + ".fbx"), [col.name])
    with open(os.path.join(out, "README.md"), "w") as f:
        f.write(readme_fn(col))
    pb.save_blend(os.path.join(out, name + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render(samples=samples)
    import bpy
    for view in views:
        fn, cam, tgt, lens = view[:4]
        hide = view[4] if len(view) > 4 else ()   # name parts hidden in this view (e.g. guards)
        for ob in bpy.data.objects:
            ob.hide_render = any(h in ob.name for h in hide)
        pb.render_view(os.path.join(out, fn), cam, tgt, lens=lens)
    for ob in bpy.data.objects:
        ob.hide_render = False
