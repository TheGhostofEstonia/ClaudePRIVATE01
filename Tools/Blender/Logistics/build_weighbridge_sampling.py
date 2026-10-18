"""
build_weighbridge_sampling.py - road weighbridge and truck concentrate sampling station.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_weighbridge_sampling.py
      (add  -- Weighbridge  or  -- SamplingStation  to build one asset only)

Assets:
    Meshes/Weighbridge/SM_Weighbridge          surface-mounted 18 x 3 m road weighbridge, booth,
                                               traffic lights, two boom barriers, RFID post
    Meshes/SamplingStation/SM_SamplingStation  pedestal auger sampler over a truck lane, with a
                                               sample preparation house

Both are fixed facilities at their own origin: ground level, centre of the truck lane.
Trucks drive in +X. Layouts are own designs; see the READMEs for sourced and estimated sizes.
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


def extra_mats():
    """Materials not in the psh_maint palette."""
    return dict(
        lamp_red=pb.mat("M_Lamp_Red", (1.0, 0.05, 0.02), 0, 0.3, emit=((1.0, 0.05, 0.02), 4.0)),
        lamp_green=pb.mat("M_Lamp_Green", (0.05, 1.0, 0.2), 0, 0.3, emit=((0.05, 1.0, 0.2), 4.0)),
        lamp_off=pb.mat("M_Lamp_Off", (0.08, 0.08, 0.08), 0, 0.3),
        clad=pb.mat("M_Cladding_Grey", (0.62, 0.65, 0.66), 0.5, 0.45),
        chequer=pb.mat("M_Steel_Chequer", (0.35, 0.35, 0.36), 0.9, 0.55),
    )


def striped_bar(p, a, b, w, h, m1, m2, step=0.5):
    """Box bar from a to b split into alternating m1/m2 stripes of length step (barrier arms, kerbs)."""
    a, b = Vector(a), Vector(b)
    n = max(1, round((b - a).length / step))
    for i in range(n):
        p.beam_between(a.lerp(b, i / n), a.lerp(b, (i + 1) / n), w, h, m1 if i % 2 == 0 else m2)


def booth(p, x0, y0, x1, y1, m, mx, window_side='y1', door_side='x0'):
    """Small cabin on a plinth: walls, flat roof, a window band on one side and a door on another."""
    h = 2.7
    p.box_mm((x0 - 0.1, y0 - 0.1, 0), (x1 + 0.1, y1 + 0.1, 0.15), m['concrete'])     # plinth
    p.box_mm((x0, y0, 0.15), (x1, y1, h), mx['clad'])
    p.box_mm((x0 - 0.15, y0 - 0.15, h), (x1 + 0.15, y1 + 0.15, h + 0.15), m['white'])  # roof slab
    if window_side == 'y1':
        p.box_mm((x0 + 0.3, y1, 1.1), (x1 - 0.3, y1 + 0.02, 2.3), m['glass'])
    elif window_side == 'y0':
        p.box_mm((x0 + 0.3, y0 - 0.02, 1.1), (x1 - 0.3, y0, 2.3), m['glass'])
    if door_side == 'x0':
        yc = (y0 + y1) / 2
        p.box_mm((x0 - 0.02, yc - 0.45, 0.15), (x0, yc + 0.45, 2.25), m['grey'])
        p.box_mm((x0 - 0.03, yc + 0.3, 1.0), (x0 - 0.02, yc + 0.38, 1.05), m['steel'])  # handle
    elif door_side == 'x1':
        yc = (y0 + y1) / 2
        p.box_mm((x1, yc - 0.45, 0.15), (x1 + 0.02, yc + 0.45, 2.25), m['grey'])
    p.box_mm((x1 - 0.9, y0 + 0.3, h + 0.15), (x1 - 0.2, y0 + 1.0, h + 0.55), m['grey'])  # AC unit


# ===========================================================================
# Weighbridge
# ===========================================================================

DECK_L, DECK_W, DECK_Z = 18.0, 3.0, 0.35   # deck 18 x 3 m (sourced size class), top 0.35 m (est.)
RAMP_L = 3.0                                # 1:8.6 approach, below the 1:8 maximum (sourced)
BARRIER_X = (-DECK_L / 2 - RAMP_L - 1.5, DECK_L / 2 + RAMP_L + 1.5)   # entry, exit barrier lines
BARRIER_Y = -2.4                            # housings on the driver's right (-Y when driving +X)
ARM_L = 4.2                                 # arm spans the 3 m lane plus margin


def build_weighbridge():
    name = "SM_Weighbridge"
    col, ref, m = pm.start(name)
    mx = extra_mats()
    hx = DECK_L / 2
    hy = DECK_W / 2

    # --- foundation, ramps, kerb guides ---
    fd = pb.Part("WB_Foundation")
    fd.box_mm((-hx - 0.3, -hy - 0.3, -0.3), (hx + 0.3, hy + 0.3, 0.05), m['concrete'])  # raft
    for s in (1, -1):    # concrete ramps, wedge in the XZ plane, extruded across the lane
        x_end = s * hx
        pts = [(x_end, 0.0), (x_end + s * RAMP_L, 0.0), (x_end, DECK_Z)]
        if s < 0:
            pts = pts[::-1]
        fd.poly_prism(pts, -hy, hy, m['concrete'], plane='XZ')
    for s in (1, -1):    # kerb guides along both deck edges, yellow/black
        striped_bar(fd, (-hx - RAMP_L + 0.5, s * (hy + 0.15), 0.15),
                    (hx + RAMP_L - 0.5, s * (hy + 0.15), 0.15), 0.25, 0.3, m['yellow'], m['steel'], 1.0)
    # load cells (8, at the module ends of a 3-module deck) on base plates
    cells = []
    for x in (-hx + 0.6, -3.0, 3.0, hx - 0.6):
        for s in (1, -1):
            c = (x, s * (hy - 0.35), 0.05)
            fd.box((0.4, 0.4, 0.03), (c[0], c[1], 0.065), m['grey'])
            fd.cyl(0.07, 0.12, (c[0], c[1], 0.14), m['grey'], seg=12)
            cells.append(c)
    bmesh.ops.recalc_face_normals(fd.bm, faces=fd.bm.faces)   # ramp wedges are wound inward
    fd.finish(col)

    # --- steel deck: 3 modules with chequer plate top and side channels ---
    dk = pb.Part("WB_Deck")
    for i, (a, b) in enumerate(((-hx, -3.0), (-3.0, 3.0), (3.0, hx))):
        dk.box_mm((a + 0.01, -hy, DECK_Z - 0.03), (b - 0.01, hy, DECK_Z), mx['chequer'])
        dk.box_mm((a + 0.01, -hy, 0.2), (b - 0.01, hy, DECK_Z - 0.03), m['blue'])
        for y in (-1.0, 0.0, 1.0):   # longitudinal girders under the plate
            dk.box_mm((a + 0.05, y - 0.08, 0.2), (b - 0.05, y + 0.08, DECK_Z - 0.03), m['steel'])
    dk.finish(col)

    # --- operator booth, beside the deck centre on the -Y side ---
    bt = pb.Part("WB_Booth")
    booth(bt, -1.5, -hy - 3.6, 1.5, -hy - 1.2, m, mx, window_side='y1', door_side='x0')
    bt.box_mm((-1.2, -hy - 1.6, 0.9), (1.2, -hy - 1.2, 0.95), m['grey'])   # inside desk (seen through glass)
    bt.finish(col)

    # --- traffic lights at both ends, facing the approaching and leaving truck ---
    tl = pb.Part("WB_TrafficLights")
    for s in (1, -1):
        x = s * (hx + 0.4)
        y = -hy - 0.7
        tl.cyl_between((x, y, 0), (x, y, 3.0), 0.05, m['galv'], seg=10)
        tl.box((0.2, 0.3, 0.7), (x, y, 3.2), m['steel'])
        face = -0.11                           # both heads face -X: the approaching truck and the truck on the deck
        tl.cyl(0.09, 0.04, (x + face, y, 3.38), mx['lamp_red'], rot=(0, 90, 0), seg=14)
        tl.cyl(0.09, 0.04, (x + face, y, 3.02), mx['lamp_green'], rot=(0, 90, 0), seg=14)
    tl.finish(col)

    # --- boom barriers: housing (static) + arm (rotates about its hinge) ---
    arms = []
    for label, xb in (("Entry", BARRIER_X[0]), ("Exit", BARRIER_X[1])):
        hs = pb.Part(f"WB_BarrierHousing_{label}")
        hs.box_mm((xb - 0.2, BARRIER_Y - 0.2, 0), (xb + 0.2, BARRIER_Y + 0.2, 1.0), m['yellow'])
        hs.box((0.6, 0.6, 0.1), (xb, BARRIER_Y, 0.05), m['concrete'])
        hs.finish(col)
        hinge = (xb, BARRIER_Y + 0.25, 0.9)
        ar = pb.Part(f"WB_BarrierArm_{label}", pivot=hinge)
        striped_bar(ar, (xb, BARRIER_Y + 0.25, 0.9), (xb, BARRIER_Y + 0.25 + ARM_L, 0.9),
                    0.06, 0.1, m['red'], m['white'], 0.5)
        ar.box((0.12, 0.3, 0.15), (xb, BARRIER_Y + 0.15, 0.9), m['steel'])   # hub
        arms.append(ar.finish(col))
        # support fork on the far side of the lane
        hs2 = pb.Part(f"WB_BarrierRest_{label}")
        yr = BARRIER_Y + 0.25 + ARM_L - 0.15
        hs2.cyl_between((xb, yr, 0), (xb, yr, 0.82), 0.04, m['galv'], seg=8)
        hs2.box((0.1, 0.12, 0.06), (xb, yr, 0.82), m['steel'])
        hs2.finish(col)

    # --- RFID reader / ticket post before the entry barrier, cab-window height ---
    rf = pb.Part("WB_RFIDPost")
    xr = BARRIER_X[0] + 1.2
    rf.cyl_between((xr, -hy - 0.9, 0), (xr, -hy - 0.9, 1.9), 0.05, m['galv'], seg=10)
    rf.box((0.3, 0.12, 0.45), (xr, -hy - 0.85, 1.95), m['grey'], rot=(20, 0, 0))
    rf.box((0.2, 0.01, 0.12), (xr, -hy - 0.78, 2.0), m['glass'], rot=(20, 0, 0))
    rf.cyl_between((xr, -hy - 0.9, 0), (xr, -hy - 0.9, 0.9), 0.2, m['yellow'], seg=12)  # bollard guard
    rf.finish(col)

    # --- REF: approach slabs, human, truck-size block ---
    pb.ref_human(ref, (0.0, -hy - 0.6, 0))
    pb.ref_ground(ref, (-35, -15, 35, 15), [(-hx - RAMP_L, -hy - 0.3, hx + RAMP_L, hy + 0.3)], z=-0.01)
    tr = pb.Part("REF_Truck_16p5m")
    tr.box_mm((-8.0, -1.25, 1.0), (8.5, 1.25, 4.0), pb.mat("M_REF_Truck", (0.3, 0.45, 0.6), 0, 0.6))
    tr.finish(ref)
    bpy.data.objects["REF_Truck_16p5m"].hide_render = True   # keeps the deck visible in the preview

    def pose():
        for a in arms:   # entry arm up for the second view
            if a.name.endswith("Entry"):
                a.rotation_euler = (math.radians(85), 0, 0)

    table = pm.finish_asset(name, "Weighbridge", [
        ("Preview_Overview.png", (-24, -20, 12), (0, 0, 0.5), 30),
        ("Preview_Entry.png", (-22, -7, 3.2), (-9, 0, 1.0), 35, True),
    ], pose=pose, ground=None)
    n_obj, n_tri = pm.counts(name)
    cell_rows = "\n".join(f"| Load cell {i + 1} | ({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}) |" for i, c in enumerate(cells))
    sections = [
        ("About", f"""
Surface-mounted (pitless) road weighbridge for inbound concentrate, flux and reagent trucks and
outbound cathode, acid and slag trucks. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_weighbridge_sampling.py`. The layout is an own design.

Origin: ground level (z 0) at the centre of the deck. Trucks drive in +X (entry at -X). The booth,
traffic lights, barriers and RFID post sit on the driver's side (-Y).

{n_obj} parts, about {n_tri:,} triangles. Previews: Preview_Overview.png, Preview_Entry.png
(entry barrier raised). REF holds a 16.5 m articulated-truck block (hidden in the renders), a
1.8 m figure and a ground slab with the weighbridge footprint left open.
"""),
        ("Moving parts", """
| Part | Motion |
|---|---|
| WB_BarrierArm_Entry / _Exit | Rotate about local X at the hinge. Closed = 0°, open = +85° (arm tips up). Arm spans +Y across the lane |
| WB_Deck | Static. Separate so a material or decal can mark it; the real deflection under load is a few mm |
| WB_TrafficLights | Static. Red and green lamps are separate material slots (M_Lamp_Red / M_Lamp_Green): swap the emissive strength in Unreal to switch |
"""),
        ("Pivots", "| Object | Pivot (Blender X, Y, Z) |\n|---|---|\n" + table + "\n\nLoad cells (inside WB_Foundation):\n\n| Item | Position |\n|---|---|\n" + cell_rows),
        ("Footprint and connection points", f"""
| Item | Value |
|---|---|
| Footprint incl. ramps and barriers | x {BARRIER_X[0] - 0.3:.1f} to {BARRIER_X[1] + 0.3:.1f}, y -5.3 to {BARRIER_Y + 0.25 + ARM_L:.1f} |
| Lane entry (road joins here, z 0) | ({BARRIER_X[0] - 1.0:.1f}, 0.0, 0.0), heading +X |
| Lane exit | ({BARRIER_X[1] + 1.0:.1f}, 0.0, 0.0), heading +X |
| Lane width on the deck | 3.0 m between kerb guides (3.3 m between kerb centres) |
| Deck top | z {DECK_Z:.2f}, x {-hx:.1f} to {hx:.1f} |
| Booth door | (-1.50, {-hy - 2.4:.2f}, 0.15), opens toward -X |
| Barrier hinge lines | x {BARRIER_X[0]:.1f} (entry), x {BARRIER_X[1]:.1f} (exit) |
"""),
        ("Dimensions", f"""
| Item | Value | Status |
|---|---|---|
| Deck | {DECK_L:.0f} x {DECK_W:.0f} m, 3 modules, 8 load cells | Sourced size class: 18 x 3 m, 3 modules with 8 weigh bars, about 100 t ([Avery Weigh-Tronix BMS spec](https://secure.averyweigh-tronix.com/en/wp-content/uploads/sites/5/2021/11/bridgemont-bms_spec_uk500291.pdf)); 18 x 3 m is listed at 80-120 t with 8 or 10 cells ([Sri Lanka Measurement Units dept.](https://measurementsdept.gov.lk/images/Pattern_Approval-Download/WEIGHBRIDGE_REQUIREMENTS/WEB_WEIGHBRIDGE_REQUIREMENTS.pdf)) |
| Ramp gradient | 1:{RAMP_L / DECK_Z:.1f} ({RAMP_L:.1f} m long) | Sourced limit: ramps no steeper than 1:8 (same Sri Lanka note); length estimated |
| Deck top height | {DECK_Z:.2f} m | Estimated; real height depends on the load-cell mounting |
| Booth 3.0 x 2.4 x 2.7 m, barrier arm {ARM_L:.1f} m at 0.9 m | | Estimated |
| Traffic light head 3.2 m | | Estimated |
"""),
        ("Unreal import", pm.UNREAL_NOTE),
    ]
    pm.write_readme("Weighbridge", "Weighbridge", "Road weighbridge for all trucks entering or leaving the plant.", sections)
    return name


# ===========================================================================
# Sampling station
# ===========================================================================

PED = Vector((0.0, -4.5, 0.0))   # pedestal centre, beside the lane on the -Y side
BOOM_Z = 8.6                     # boom centre line height
BOOM_L = 8.0                     # pivot to boom tip
CARR_Y = 4.5                     # drawn carriage position along the boom (from the pivot)
PROBE_L = 3.8                    # auger tube length
PROBE_TOP_UP = 7.9               # probe drive head z when fully raised
PLUNGE = 3.0                     # probe travel down
HOUSE = (-2.6, -13.0, 2.6, -8.6)  # sample house footprint x0, y0, x1, y1
HOPPER = Vector((0.0, -9.6, 3.4))  # receiving hopper inlet on the house roof (boom slewed 180°)


def auger(p, top, length, m, r=0.11, pitch=0.22):
    """Auger tube with an exposed helical flight on the lower 1.2 m (quad strips)."""
    top = Vector(top)
    tip = top - Vector((0, 0, length))
    p.cyl_between(top, tip + Vector((0, 0, 1.2)), r, m['grey'], seg=16)          # tube
    p.cyl_between(tip + Vector((0, 0, 1.2)), tip, 0.04, m['grey'], seg=10)       # flight shaft
    turns = 1.2 / pitch
    n = int(turns * 16)
    rows = []
    for i in range(n + 1):
        a = 2 * math.pi * i / 16
        z = tip.z + 1.2 * i / n
        inner = Vector((tip.x + 0.04 * math.cos(a), tip.y + 0.04 * math.sin(a), z))
        outer = Vector((tip.x + r * math.cos(a), tip.y + r * math.sin(a), z))
        rows.append([inner, outer])
    p.quad_strip(rows, m['steel'])
    p.cyl(0.05, 0.08, tip + Vector((0, 0, 0.04)), m['steel'], seg=10, r2=0.005)  # cutting tip


def build_sampling_station():
    name = "SM_SamplingStation"
    col, ref, m = pm.start(name)
    mx = extra_mats()

    # --- truck lane slab with kerbs ---
    ln = pb.Part("SS_Lane")
    ln.box_mm((-14, -2.0, -0.2), (14, 2.0, 0.0), m['concrete'])
    for s in (1, -1):
        striped_bar(ln, (-12, s * 2.1, 0.1), (12, s * 2.1, 0.1), 0.2, 0.2, m['yellow'], m['steel'], 1.0)
    ln.box_mm((-0.1, -2.0, 0.0), (0.1, 2.0, 0.005), m['white'])              # stop line under the probe
    ln.finish(col)

    # --- pedestal, slewing ring, top platform and caged ladder ---
    pd = pb.Part("SS_Pedestal")
    pd.box((1.6, 1.6, 0.4), (PED.x, PED.y, 0.2), m['concrete'])
    pd.cyl_between(PED + Vector((0, 0, 0.4)), PED + Vector((0, 0, BOOM_Z - 0.75)), 0.35, m['yellow'], seg=24)
    pd.cyl(0.55, 0.15, PED + Vector((0, 0, BOOM_Z - 0.68)), m['grey'], seg=32)   # slewing ring
    pz = BOOM_Z - 1.9                                                            # platform level
    pd.box((2.4, 2.4, 0.06), PED + Vector((0, 0, pz)), mx['chequer'])
    pm.guard_box(pd, PED.x - 1.2, PED.y - 1.2, PED.x + 1.2, PED.y + 1.2, pz + 0.03, m['yellow'], open_side='y0')
    for dx in (-1.1, 1.1):   # platform knee braces
        pd.cyl_between(PED + Vector((dx, 0, pz)), PED + Vector((0, 0, pz - 1.4)), 0.04, m['yellow'], seg=8)
    pb.ladder(pd, PED + Vector((0, -1.25, 0.4)), pz, m['galv'], facing=90.0)
    for k in range(int((pz - 2.5) / 0.9) + 1):   # safety cage hoops
        z = 2.5 + k * 0.9
        pd.cyl(0.36, 0.03, PED + Vector((0, -1.55, z)), m['galv'], seg=16, cap=False)
    pd.box((0.6, 0.4, 0.9), PED + Vector((0.7, 0.75, pz + 0.48)), m['grey'])   # control cabinet
    pd.finish(col)

    # --- slewing boom (slews about Z at the pedestal axis) ---
    piv = PED + Vector((0, 0, BOOM_Z))
    bm_ = pb.Part("SS_Boom", pivot=piv)
    bm_.cyl(0.5, 0.5, piv + Vector((0, 0, -0.35)), m['yellow'], seg=24)          # slew housing
    bm_.box((0.6, 0.5, 0.4), piv + Vector((0.55, 0, -0.35)), m['grey'])          # slew drive
    for s in (1, -1):   # two box girders, carriage runs underneath on their bottom flanges
        bm_.box_mm((piv.x + s * 0.28 - 0.07, piv.y - 1.2, BOOM_Z - 0.3),
                   (piv.x + s * 0.28 + 0.07, piv.y + BOOM_L, BOOM_Z + 0.35), m['yellow'])
    for y in (-1.2, BOOM_L):
        bm_.box_mm((piv.x - 0.35, piv.y + y - 0.1, BOOM_Z + 0.2), (piv.x + 0.35, piv.y + y, BOOM_Z + 0.35), m['yellow'])
    bm_.box_mm((piv.x - 0.3, piv.y - 2.0, BOOM_Z - 0.2), (piv.x + 0.3, piv.y - 1.2, BOOM_Z + 0.4), m['steel'])  # counterweight
    bm_.box_mm((piv.x - 0.4, piv.y + BOOM_L - 0.2, BOOM_Z - 0.35), (piv.x + 0.4, piv.y + BOOM_L, BOOM_Z + 0.4), m['red'])  # end stop
    boom = bm_.finish(col)

    # --- carriage (travels along the boom) with the vertical probe guide frame ---
    cpos = piv + Vector((0, CARR_Y, 0))
    cr = pb.Part("SS_Carriage", pivot=cpos)
    cr.box((0.9, 0.9, 0.35), cpos + Vector((0, 0, -0.5)), m['grey'])
    for s in (1, -1):
        for dy in (-0.3, 0.3):
            cr.cyl(0.08, 0.06, cpos + Vector((s * 0.28, dy, -0.28)), m['steel'], rot=(0, 90, 0), seg=12)
    gz_top, gz_bot = BOOM_Z - 0.7, PROBE_TOP_UP - PROBE_L + 0.6   # guide frame span
    for dx, dy in ((0.25, 0.25), (-0.25, 0.25), (0.25, -0.25), (-0.25, -0.25)):
        cr.cyl_between(cpos + Vector((dx, dy, gz_top - BOOM_Z)), Vector((cpos.x + dx, cpos.y + dy, gz_bot)),
                       0.035, m['yellow'], seg=8)
    cr.box((0.6, 0.6, 0.12), Vector((cpos.x, cpos.y, gz_bot)), m['yellow'])       # lower guide collar
    cr.box((0.45, 0.35, 0.3), cpos + Vector((0.6, 0, -0.5)), m['blue'])           # travel motor
    carriage = cr.finish(col)
    pm.parent(carriage, boom)

    # --- probe: drive head + auger, plunges along -Z ---
    ptop = Vector((cpos.x, cpos.y, PROBE_TOP_UP))
    pr = pb.Part("SS_Probe", pivot=ptop)
    pr.box((0.42, 0.42, 0.45), ptop + Vector((0, 0, 0.1)), m['blue'])              # hydraulic motor/gearbox
    pr.cyl(0.14, 0.2, ptop + Vector((0, 0, 0.45)), m['grey'], seg=14)
    pr.box((0.48, 0.16, 0.2), ptop + Vector((0, 0, -0.18)), m['steel'])            # guide shoes
    auger(pr, ptop + Vector((0, 0, -0.2)), PROBE_L - 0.2, m)
    probe = pr.finish(col)
    pm.parent(probe, carriage)

    # --- sample house with receiving hopper and divider inside ---
    x0, y0, x1, y1 = HOUSE
    hs = pb.Part("SS_SampleHouse")
    booth(hs, x0, y0, x1, y1, m, mx, window_side='y0', door_side='x1')
    hs.cyl(0.55, 0.6, HOPPER + Vector((0, 0, -0.05)), m['galv'], seg=20, r2=0.18)  # receiving hopper
    hs.cyl(0.6, 0.06, HOPPER + Vector((0, 0, 0.25)), m['grey'], seg=20)           # grid rim
    hs.box((0.8, 0.7, 1.2), (-1.4, -9.6, 0.75), m['green'])                       # jaw crusher
    hs.cyl(0.35, 0.9, (0.0, -9.6, 1.6), m['grey'], seg=20)                         # rotary sample divider
    hs.cyl(0.08, 0.6, (0.0, -9.6, 2.35), m['grey'], seg=10)                        # chute from hopper
    for k in range(8):   # divider sample jars around the base
        a = 2 * math.pi * k / 8
        hs.cyl(0.06, 0.18, (0.45 * math.cos(a), -9.6 + 0.45 * math.sin(a), 0.85), m['white'], seg=10)
    hs.box((1.6, 0.6, 0.85), (1.3, -12.5, 0.58), m['grey'])                       # bench / drawer cabinet
    hs.box((0.6, 0.6, 0.8), (-1.8, -12.4, 0.55), m['blue'])                       # drying oven
    hs.finish(col)

    # --- REF ---
    pb.ref_human(ref, (2.0, -3.0, 0))
    tr = pb.Part("REF_TipperTrailerBox")
    mt = pb.mat("M_REF_Truck", (0.3, 0.45, 0.6), 0, 0.6)
    tr.box_mm((-6.5, -1.25, 1.3), (6.5, 1.25, 1.4), mt)                       # open-top body, so the probe shows
    for s in (1, -1):
        tr.box_mm((-6.5, s * 1.25 - 0.04, 1.4), (6.5, s * 1.25 + 0.04, 3.6), mt)
        tr.box_mm((s * 6.5 - 0.04, -1.25, 1.4), (s * 6.5 + 0.04, 1.25, 3.6), mt)
    tr.box_mm((-6.4, -1.2, 1.4), (6.4, 1.2, 2.9), pb.mat("M_REF_Concentrate", (0.12, 0.1, 0.08), 0, 0.95))
    tr.finish(ref)
    pb.ref_ground(ref, (-40, -30, 40, 30), [(-14, -2.0, 14, 2.0)], z=-0.01)

    def pose():   # probe plunged into the trailer
        probe.location.z -= PLUNGE

    table = pm.finish_asset(name, "SamplingStation", [
        ("Preview_Overview.png", (14, -22, 12), (0, -3, 4), 30),
        ("Preview_Sampling.png", (8, 7, 9.5), (0, 0, 3.0), 30, True),
    ], pose=pose, ground=None)
    n_obj, n_tri = pm.counts(name)
    hopper_reach = (HOPPER - PED).length
    sections = [
        ("About", f"""
Automatic auger (probe) sampler for incoming concentrate trucks, with a sample preparation house.
The driver stops at the white line, the boom slews over the trailer, the carriage moves the
probe along the load and the auger drills down and lifts a core. The boom then slews round over
the receiving hopper on the house roof and the auger reverses to drop the sample, which falls
through a crusher and a rotary divider into sample jars for the laboratory. Built in Blender 5.2.2
LTS (headless, cloud) with `Tools/Blender/Logistics/build_weighbridge_sampling.py`. The layout is
an own design based on pedestal samplers with a slewing boom.

Origin: ground level (z 0) at the probe stop line on the lane centre. Trucks drive in +X.

{n_obj} parts, about {n_tri:,} triangles. Previews: Preview_Overview.png, Preview_Sampling.png
(probe plunged {PLUNGE:.1f} m). REF holds a 13 x 2.5 m tipper-trailer block (z 1.3 to 3.6) and a
1.8 m figure.

Rail option (not modelled): for concentrate arriving by rail the same pedestal and boom can stand
beside the track before the rotary car dumper, with the stop line replaced by a car-positioner
mark. The boom then needs about 1 m more reach because a wagon body sits further from the
pedestal than a truck trailer.
"""),
        ("Moving parts", f"""
| Part | Motion |
|---|---|
| SS_Boom | Slews about local Z at the pedestal axis. 0° = boom over the lane (+Y). 180° puts the carriage over the receiving hopper when the carriage is at {hopper_reach:.1f} m from the axis |
| SS_Carriage | Travels along the boom's local Y: {1.0:.1f} m to {BOOM_L - 0.6:.1f} m from the axis (drawn at {CARR_Y:.1f} m, which is the lane centre) |
| SS_Probe | Plunges along -Z by up to {PLUNGE:.1f} m. Raised, the tip is at z {PROBE_TOP_UP - PROBE_L:.2f}, above a 4.0 m trailer top. Auger spins about local Z while drilling |
"""),
        ("Pivots", "| Object | Pivot (Blender X, Y, Z) |\n|---|---|\n" + table),
        ("Footprint and connection points", f"""
| Item | Value |
|---|---|
| Footprint | x -14 to 14 (lane), y {HOUSE[1]:.1f} to 2.2 |
| Lane entry / exit (z 0) | (-14.0, 0.0, 0.0) / (14.0, 0.0, 0.0), 4.0 m wide |
| Probe stop line | x 0, under the probe when the boom is at 0° |
| Sample house door | ({HOUSE[2]:.2f}, {(HOUSE[1] + HOUSE[3]) / 2:.2f}, 0.15), facing +X |
| Receiving hopper inlet | ({HOPPER.x:.2f}, {HOPPER.y:.2f}, {HOPPER.z + 0.28:.2f}) |
| Pedestal ladder foot | ({PED.x:.2f}, {PED.y - 1.25:.2f}, 0.40) |
"""),
        ("Dimensions", f"""
| Item | Value | Status |
|---|---|---|
| Boom reach | {BOOM_L:.1f} m from the axis, carriage range about {BOOM_L - 1.6:.1f} m, 360° slew | Estimated, sized to cover a 2.5 m trailer 4.5 m from the axis. A commercial collector sampler lists 2.95-5.95 m horizontal reach and 0-5 m sampling height with 180° slew ([SAUR, DirectIndustry](https://www.directindustry.com/prod/saur/product-239378-2404099.html)) |
| Auger probe | {PROBE_L:.1f} m long, 0.22 m flight diameter, {PLUNGE:.1f} m stroke | Estimated |
| Pedestal | 0.7 m diameter column, boom at z {BOOM_Z:.1f} | Estimated |
| Sample house | {HOUSE[2] - HOUSE[0]:.1f} x {HOUSE[3] - HOUSE[1]:.1f} x 2.7 m | Estimated |
| Truck lane | 4.0 m wide | Estimated |
"""),
        ("Unreal import", pm.UNREAL_NOTE),
    ]
    pm.write_readme("SamplingStation", "SamplingStation", "Truck sampling station for incoming concentrate.", sections)
    return name


# ===========================================================================

BUILDERS = {"Weighbridge": build_weighbridge, "SamplingStation": build_sampling_station}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for k in (argv or list(BUILDERS)):
        BUILDERS[k]()


main()
