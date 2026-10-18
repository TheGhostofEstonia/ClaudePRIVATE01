"""
build_warehouse.py - spares warehouse with high racks, a reusable pallet-rack bay, and the
palletised consumables that arrive at the plant (one FBX per prop).

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_warehouse.py
      (add  -- Warehouse  /  -- Rack  /  -- Consumables  to build one set only)

Assets:
    Meshes/Warehouse/SM_Warehouse          60 x 30 m portal-frame store, eave 12 m, 3 truck docks,
                                           drive-in door, office/counter, 8 pallet-rack lines,
                                           cantilever rack for pipe and bar
    Meshes/Warehouse/SM_PalletRackBay      one 2.7 m clear bay, 5 storage levels (frame + beams)
    Meshes/Warehouse/SM_PalletRackFrame    the end frame that closes a run of bays
    Meshes/Consumables/SM_<Prop>.fbx       pallets, refractory bricks, castable and reagent sacks,
                                           bulk bag, IBC, drum, cathode blank crate, spares crate,
                                           gas cylinder cage

Origins are at floor level, centre of the footprint (the rack props use the front-left upright).
"""
import math
import os
import random
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
        clad=pb.mat("M_Cladding_Grey", (0.62, 0.65, 0.66), 0.5, 0.45),
        roof=pb.mat("M_Cladding_Roof", (0.45, 0.47, 0.48), 0.5, 0.5),
        struct=pb.mat("M_Steel_Structure", (0.16, 0.24, 0.36), 0.3, 0.5),
        rack=pb.mat("M_Rack_Frame_Blue", (0.05, 0.2, 0.55), 0.3, 0.45),
        beam=pb.mat("M_Rack_Beam_Orange", (0.85, 0.3, 0.02), 0.3, 0.45),
        carton=pb.mat("M_Carton", (0.55, 0.4, 0.22), 0.0, 0.85),
        crate=pb.mat("M_Crate_Grey", (0.35, 0.37, 0.38), 0.2, 0.6),
        wrap=pb.mat("M_ShrinkWrap", (0.75, 0.8, 0.82), 0.0, 0.15),
        bag=pb.mat("M_Bag_WovenPP", (0.82, 0.8, 0.72), 0.0, 0.8),
        sack=pb.mat("M_Sack_Paper", (0.62, 0.5, 0.36), 0.0, 0.9),
        fibc=pb.mat("M_FIBC_White", (0.85, 0.85, 0.8), 0.0, 0.75),
        hdpe=pb.mat("M_HDPE_Natural", (0.88, 0.88, 0.84), 0.0, 0.35),
        stainless=pb.mat("M_Stainless", (0.7, 0.7, 0.72), 1.0, 0.25),
        copper=pb.mat("M_Copper", (0.8, 0.42, 0.25), 1.0, 0.3),
        edge=pb.mat("M_EdgeStrip_Plastic", (0.85, 0.85, 0.8), 0.0, 0.5),
        maroon=pb.mat("M_Paint_Maroon", (0.35, 0.03, 0.05), 0.2, 0.45),
        black=pb.mat("M_Paint_Black", (0.03, 0.03, 0.03), 0.2, 0.45),
        seal=pb.mat("M_DockSeal_Black", (0.04, 0.04, 0.04), 0.0, 0.9),
        lamp=pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0)),
    )


def fix_normals(p):
    """poly_prism winding depends on the point order; make every face point outward."""
    bmesh.ops.recalc_face_normals(p.bm, faces=p.bm.faces)


def wall(p, axis, c, a0, a1, z0, z1, t, m, openings=(), dado=None):
    """
    Wall panel of thickness t on the plane x = c (axis 'y', wall runs along Y) or y = c
    (axis 'x', wall runs along X), from a0 to a1 along the wall and z0 to z1 high.
    openings: (a_start, a_end, z_bottom, z_top) holes. dado: (height, material) concrete upstand.
    """
    def piece(b0, b1, za, zb, mm):
        if b1 - b0 < 1e-3 or zb - za < 1e-3:
            return
        if axis == 'x':
            p.box_mm((b0, c - t / 2, za), (b1, c + t / 2, zb), mm)
        else:
            p.box_mm((c - t / 2, b0, za), (c + t / 2, b1, zb), mm)

    def run(za, zb, mm, ops):
        cur = a0
        for oa, ob, oz0, oz1 in sorted(ops):
            piece(cur, oa, za, zb, mm)
            piece(oa, ob, max(za, oz1), zb, mm)       # above the opening
            piece(oa, ob, za, min(zb, oz0), mm)       # below the opening
            cur = ob
        piece(cur, a1, za, zb, mm)

    if dado:
        h, dm = dado
        run(z0, z0 + h, dm, openings)
        z0 = z0 + h
    run(z0, z1, m, openings)


# ===========================================================================
# Pallet racking (shared by the warehouse and the rack props)
# ===========================================================================

RACK_PITCH = 2.8          # frame centre to frame centre: 2.7 m clear beam + upright
RACK_DEPTH = 1.1          # frame depth for 1.2 m deep EUR pallets (50 mm overhang each side)
RACK_H = 8.5              # frame height
BEAM_Z = (1.8, 3.6, 5.4, 7.2)   # beam tops; with the floor that is 5 storage levels


def rack_frame(p, x, ya, yb, mx, h=RACK_H):
    """Upright frame at x across the rack depth ya..yb (two uprights, horizontal + diagonal bracing)."""
    for y in (ya + 0.045, yb - 0.045):
        p.box_mm((x - 0.045, y - 0.035, 0), (x + 0.045, y + 0.035, h), mx['rack'])
        p.box_mm((x - 0.08, y - 0.08, 0), (x + 0.08, y + 0.08, 0.008), mx['rack'])     # base plate
    z, up = 0.15, True
    while z < h - 0.1:
        p.beam_between((x, ya + 0.08, z), (x, yb - 0.08, z), 0.03, 0.03, mx['rack'])
        z2 = min(z + 1.2, h - 0.1)
        a, b = (ya + 0.08, yb - 0.08) if up else (yb - 0.08, ya + 0.08)
        p.beam_between((x, a, z), (x, b, z2), 0.025, 0.025, mx['rack'])
        z, up = z2, not up
    p.beam_between((x, ya + 0.08, h - 0.1), (x, yb - 0.08, h - 0.1), 0.03, 0.03, mx['rack'])


def rack_beams(p, x, ya, yb, mx, pitch=RACK_PITCH):
    """Front and back box beams at every level between the frame at x and the next one."""
    for z in BEAM_Z:
        for y in (ya + 0.045 - 0.035 - 0.025, yb - 0.045 + 0.035 + 0.025):
            p.box_mm((x + 0.045, y - 0.025, z - 0.12), (x + pitch - 0.045, y + 0.025, z), mx['beam'])
        # two pallet support bars front to back (deck support)
        for dx in (0.6, pitch - 0.6):
            p.box_mm((x + dx - 0.02, ya + 0.02, z - 0.03), (x + dx + 0.02, yb - 0.02, z), mx['rack'])


# ===========================================================================
# Warehouse
# ===========================================================================

L, W, EAVE, RIDGE = 60.0, 30.0, 12.0, 13.3     # building outline (m), roof pitch about 5°
HX, HY = L / 2, W / 2
DOCK_X = (10.0, 15.0, 20.0)                     # dock door centres on the south wall (y -15)
DOCK_W, DOCK_H = 3.0, 3.2
DRIVE_W, DRIVE_H = 5.0, 5.0                     # drive-in door, west wall, centred on y 0
WELL_Z = -1.2                                   # dock well floor; truck bed meets the 0.0 floor
OFFICE = (-HX + 0.25, 7.0, -22.0, HY - 0.25)    # x0, y0, x1, y1
RACK_X0, RACK_BAYS = -20.0, 16
RACK_LINES = [(13.5, 14.6), (8.9, 10.0), (7.6, 8.7), (3.0, 4.1), (1.7, 2.8),
              (-2.9, -1.8), (-4.2, -3.1), (-8.8, -7.7)]   # (y front/back) of each single-depth line
CANT_X, CANT_Y = 29.25, (-6.0, 12.0)            # cantilever rack column line, along the east wall


def roof_z(y):
    """Underside of the roof sheet at distance y from the ridge line."""
    return EAVE - 0.05 + (RIDGE - EAVE) * (1 - abs(y) / (HY + 0.4))


def build_warehouse():
    name = "SM_Warehouse"
    col, ref, m = pm.start(name)
    mx = extra_mats()
    rng = random.Random(7)

    # --- floor slab and dock well with its ramp ---
    sl = pb.Part("WH_Slab")
    sl.box_mm((-HX - 0.3, -HY - 0.3, -0.25), (HX + 0.3, HY + 0.3, 0.0), m['concrete'])
    for x in DOCK_X:   # leveller decks flush with the floor
        sl.box_mm((x - 1.0, -HY + 0.12, 0.0), (x + 1.0, -HY + 2.6, 0.015), m['steel'])
    for x0, y0, x1, y1 in ((-HX + 0.5, -HY + 0.5, HX - 0.5, -HY + 0.6), (-HX + 0.5, -2.1, -20.5, -2.0)):
        sl.box_mm((x0, y0, 0.0), (x1, y1, 0.004), m['yellow'])                  # floor lines
    sl.finish(col)

    ap = pb.Part("WH_DockApron")
    wx0, wx1 = DOCK_X[0] - 3.0, DOCK_X[-1] + 3.0
    ap.box_mm((wx0, -HY - 12.0, WELL_Z - 0.2), (wx1, -HY - 0.3, WELL_Z), m['concrete'])   # well floor
    ap.poly_prism([(-HY - 12.0, WELL_Z - 0.2), (-HY - 22.0, -0.2), (-HY - 22.0, 0.0), (-HY - 12.0, WELL_Z)],
                  wx0, wx1, m['concrete'], plane='YZ')                                   # 12 % ramp
    for x in (wx0 - 0.15, wx1 + 0.15):      # retaining walls, top at ground level
        ap.poly_prism([(-HY - 0.3, WELL_Z - 0.2), (-HY - 12.0, WELL_Z - 0.2), (-HY - 22.0, -0.2),
                       (-HY - 22.0, 0.1), (-HY - 0.3, 0.1)], x - 0.15, x + 0.15, m['concrete'], plane='YZ')
    ap.box_mm((wx0, -HY - 0.3, WELL_Z), (wx1, -HY + 0.0, 0.0), m['concrete'])          # dock face
    fix_normals(ap)
    ap.finish(col)

    # --- portal frames, purlins, eaves beams, bracing ---
    fr = pb.Part("WH_Frame")
    xs = [-HX + 6.0 * i for i in range(11)]
    for i, x in enumerate(xs):
        xc = min(max(x, -HX + 0.2), HX - 0.2)
        for s in (1, -1):
            fr.box_mm((xc - 0.15, s * (HY - 0.2) - 0.2, 0), (xc + 0.15, s * (HY - 0.2) + 0.2, roof_z(HY - 0.2)), mx['struct'])
        for s in (1, -1):    # rafter halves (convex quads), 0.55 m deep
            ye = s * (HY - 0.05)
            fr.poly_prism([(ye, roof_z(ye) - 0.55), (0, roof_z(0) - 0.55), (0, roof_z(0)), (ye, roof_z(ye))],
                          xc - 0.1, xc + 0.1, mx['struct'], plane='YZ')
    for y in (-13.5, -10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5, 13.5):
        fr.box_mm((-HX, y - 0.04, roof_z(y) - 0.2), (HX, y + 0.04, roof_z(y) - 0.005), mx['struct'])
    for s in (1, -1):
        fr.box_mm((-HX, s * (HY - 0.2) - 0.1, EAVE - 0.35), (HX, s * (HY - 0.2) + 0.1, EAVE - 0.05), mx['struct'])
        for xa, xb in ((xs[0] + 0.2, xs[1]), (xs[-2], xs[-1] - 0.2)):          # wall bracing, end bays
            fr.cyl_between((xa, s * (HY - 0.25), 0.3), (xb, s * (HY - 0.25), EAVE - 0.4), 0.02, m['steel'], seg=6)
            fr.cyl_between((xb, s * (HY - 0.25), 0.3), (xa, s * (HY - 0.25), EAVE - 0.4), 0.02, m['steel'], seg=6)
    fix_normals(fr)
    fr.finish(col)

    # --- cladding: south wall with dock doors, west wall with drive-in and office doors ---
    t = 0.12
    cs = pb.Part("WH_Cladding_South")
    wall(cs, 'x', -HY - t / 2, -HX, HX, 0.0, EAVE, t, mx['clad'],
         [(x - DOCK_W / 2, x + DOCK_W / 2, 0.0, DOCK_H) for x in DOCK_X], dado=(1.2, m['concrete']))
    cs.finish(col)
    cn = pb.Part("WH_Cladding_North")
    wall(cn, 'x', HY + t / 2, -HX, HX, 0.0, EAVE, t, mx['clad'], [], dado=(1.2, m['concrete']))
    cn.finish(col)
    cw = pb.Part("WH_Cladding_West")
    wall(cw, 'y', -HX - t / 2, -HY - t, HY + t, 0.0, EAVE, t, mx['clad'],
         [(-DRIVE_W / 2, DRIVE_W / 2, 0.0, DRIVE_H), (10.0, 11.0, 0.0, 2.1)], dado=(1.2, m['concrete']))
    cw.poly_prism([(-HY - t, EAVE), (HY + t, EAVE), (0.0, RIDGE + 0.05)], -HX - t, -HX, mx['clad'], plane='YZ')
    cw.box_mm((-HX - t - 0.01, 10.0, 0.0), (-HX - t, 11.0, 2.1), m['grey'])              # office door leaf
    fix_normals(cw)
    cw.finish(col)
    ce = pb.Part("WH_Cladding_East")
    wall(ce, 'y', HX + t / 2, -HY - t, HY + t, 0.0, EAVE, t, mx['clad'], [(-12.0, -11.0, 0.0, 2.1)],
         dado=(1.2, m['concrete']))
    ce.poly_prism([(-HY - t, EAVE), (HY + t, EAVE), (0.0, RIDGE + 0.05)], HX, HX + t, mx['clad'], plane='YZ')
    ce.box_mm((HX + t, -12.0, 0.0), (HX + t + 0.01, -11.0, 2.1), m['grey'])              # fire exit leaf
    fix_normals(ce)
    ce.finish(col)

    rf = pb.Part("WH_Roof")
    rf.poly_prism([(-HY - 0.4, EAVE - 0.05), (0.0, RIDGE - 0.05), (0.0, RIDGE + 0.05), (-HY - 0.4, EAVE + 0.05)],
                  -HX - 0.3, HX + 0.3, mx['roof'], plane='YZ')
    rf.poly_prism([(0.0, RIDGE - 0.05), (HY + 0.4, EAVE - 0.05), (HY + 0.4, EAVE + 0.05), (0.0, RIDGE + 0.05)],
                  -HX - 0.3, HX + 0.3, mx['roof'], plane='YZ')
    for x in (-21.0, -9.0, 3.0, 15.0):   # rooflight strips, just above the roof sheet
        for a, b in ((-11.0, -3.0), (3.0, 11.0)):
            rf.poly_prism([(a, roof_z(a) + 0.11), (b, roof_z(b) + 0.11), (b, roof_z(b) + 0.13), (a, roof_z(a) + 0.13)],
                          x - 1.0, x + 1.0, m['glass'], plane='YZ')
    fix_normals(rf)
    rf.finish(col)

    # --- dock equipment: seals, bumpers, coil boxes, leveller lips; roller doors separately ---
    de = pb.Part("WH_DockEquipment")
    for x in DOCK_X:
        for s in (1, -1):
            de.box_mm((x + s * (DOCK_W / 2 + 0.15) - 0.15, -HY - 0.6, 0.0), (x + s * (DOCK_W / 2 + 0.15) + 0.15, -HY - 0.12, DOCK_H + 0.3), mx['seal'])
            de.box_mm((x + s * 1.1 - 0.12, -HY - 0.45, -0.55), (x + s * 1.1 + 0.12, -HY - 0.3, -0.1), m['rubber'])  # bumper
        de.box_mm((x - DOCK_W / 2 - 0.3, -HY - 0.6, DOCK_H), (x + DOCK_W / 2 + 0.3, -HY - 0.12, DOCK_H + 0.55), mx['seal'])  # head curtain
        de.box_mm((x - DOCK_W / 2 - 0.1, -HY + 0.0, DOCK_H), (x + DOCK_W / 2 + 0.1, -HY + 0.55, DOCK_H + 0.55), m['grey'])  # coil box
        de.box((0.3, 0.12, 0.2), (x + DOCK_W / 2 + 0.5, -HY + 0.12, 1.4), m['yellow'])     # control box
        de.box((0.2, 0.08, 0.4), (x - DOCK_W / 2 - 0.5, -HY - 0.15, 2.4), m['steel'])     # dock light
    de.box_mm((-HX + 0.0, -DRIVE_W / 2 - 0.1, DRIVE_H), (-HX + 0.65, DRIVE_W / 2 + 0.1, DRIVE_H + 0.65), m['grey'])
    de.finish(col)

    doors, lips = [], []
    for i, x in enumerate(DOCK_X):
        piv = (x, -HY + 0.1, 0.0)
        d = pb.Part(f"WH_Door_Dock{i + 1}", pivot=piv)
        d.box_mm((x - DOCK_W / 2 + 0.02, -HY + 0.07, 0.0), (x + DOCK_W / 2 - 0.02, -HY + 0.13, DOCK_H), m['white'])
        for z in [0.3 + 0.3 * k for k in range(10)]:
            d.box_mm((x - DOCK_W / 2 + 0.02, -HY + 0.13, z - 0.01), (x + DOCK_W / 2 - 0.02, -HY + 0.145, z + 0.01), m['grey'])
        d.box_mm((x - 0.2, -HY + 0.13, 0.9), (x + 0.2, -HY + 0.16, 0.95), m['steel'])     # handle
        doors.append(d.finish(col))
        lp = pb.Part(f"WH_LevellerLip_{i + 1}", pivot=(x, -HY + 0.12, 0.0))
        lp.box_mm((x - 1.0, -HY + 0.1, -0.4), (x + 1.0, -HY + 0.12, 0.0), m['steel'])
        lips.append(lp.finish(col))
    dpiv = (-HX + 0.1, 0.0, 0.0)
    dd = pb.Part("WH_Door_DriveIn", pivot=dpiv)
    dd.box_mm((-HX + 0.07, -DRIVE_W / 2 + 0.02, 0.0), (-HX + 0.13, DRIVE_W / 2 - 0.02, DRIVE_H), m['white'])
    for z in [0.3 + 0.3 * k for k in range(16)]:
        dd.box_mm((-HX + 0.13, -DRIVE_W / 2 + 0.02, z - 0.01), (-HX + 0.145, DRIVE_W / 2 - 0.02, z + 0.01), m['grey'])
    doors.append(dd.finish(col))

    # --- office / counter block in the north-west corner ---
    ox0, oy0, ox1, oy1 = OFFICE
    of = pb.Part("WH_Office")
    wall(of, 'y', ox1, oy0, oy1, 0.0, 3.5, 0.15, m['white'], [(8.0, 9.0, 0.0, 2.1), (10.5, 13.5, 1.0, 2.2)])
    wall(of, 'x', oy0, ox0, ox1 + 0.075, 0.0, 3.5, 0.15, m['white'], [(-27.0, -24.0, 1.0, 2.2)])
    of.box_mm((ox0, oy0 - 0.075, 3.5), (ox1 + 0.075, oy1, 3.65), m['white'])            # roof / storage deck
    of.box_mm((ox1 - 0.02, 10.5, 1.0), (ox1 + 0.02, 13.5, 2.2), m['glass'])            # counter window glass
    of.box_mm((ox1 + 0.075, 10.4, 0.95), (ox1 + 0.45, 13.6, 1.0), m['wood'])           # counter shelf
    of.box_mm((-27.0, oy0 - 0.02, 1.0), (-24.0, oy0 + 0.02, 2.2), m['glass'])
    of.box_mm((ox1 + 0.075, 7.98, 0.0), (ox1 + 0.1, 9.0, 2.1), m['grey'])              # door leaf
    pm.guard_box(of, ox0, oy0 - 0.075, ox1 + 0.075, oy1, 3.65, m['yellow'], h=1.1, open_side='y1')
    for x, y in ((-26.0, 12.5), (-24.0, 9.5)):                                         # desks inside
        of.box((1.6, 0.8, 0.75), (x, y, 0.375), m['wood'])
    of.finish(col)

    # --- pallet racking and its load ---
    rk = pb.Part("WH_Racking")
    ld = pb.Part("WH_RackLoad")
    load_mats = (mx['carton'], mx['crate'], m['blue'], mx['wrap'])
    for ya, yb in RACK_LINES:
        for i in range(RACK_BAYS + 1):
            rack_frame(rk, RACK_X0 + i * RACK_PITCH, ya, yb, mx)
        for i in range(RACK_BAYS):
            x = RACK_X0 + i * RACK_PITCH
            rack_beams(rk, x, ya, yb, mx)
            for z in (0.0,) + BEAM_Z:
                for k in range(3):
                    if rng.random() > 0.68:
                        continue
                    cx = x + 0.15 + 0.45 + k * 0.9
                    cy = (ya + yb) / 2
                    ld.box_mm((cx - 0.4, cy - 0.6, z), (cx + 0.4, cy + 0.6, z + 0.144), m['wood'])
                    h = rng.uniform(0.5, 1.3)
                    ld.box_mm((cx - 0.38, cy - 0.58, z + 0.144), (cx + 0.38, cy + 0.58, z + 0.144 + h),
                              rng.choice(load_mats))
        for x in (RACK_X0 - 0.2, RACK_X0 + RACK_BAYS * RACK_PITCH + 0.2):           # end-of-run guards
            rk.box_mm((x - 0.05, ya - 0.05, 0.0), (x + 0.05, yb + 0.05, 0.4), m['yellow'])
    rk.finish(col)
    ld.finish(col)

    # --- cantilever rack for pipe, bar and long spares (arms point -X) ---
    ct = pb.Part("WH_CantileverRack")
    ys = [CANT_Y[0] + 1.5 * k for k in range(int((CANT_Y[1] - CANT_Y[0]) / 1.5) + 1)]
    for y in ys:
        ct.box_mm((CANT_X - 0.15, y - 0.1, 0.0), (CANT_X + 0.15, y + 0.1, 4.5), mx['rack'])
        ct.box_mm((CANT_X - 1.4, y - 0.1, 0.0), (CANT_X + 0.15, y + 0.1, 0.25), mx['rack'])   # base leg
        for z in (1.0, 2.0, 3.0, 4.0):
            ct.beam_between((CANT_X - 0.15, y, z), (CANT_X - 1.35, y, z + 0.04), 0.1, 0.16, mx['beam'])
            ct.box((0.06, 0.12, 0.08), (CANT_X - 1.33, y, z + 0.1), mx['beam'])          # end stop
    ct.beam_between((CANT_X + 0.1, ys[0], 1.5), (CANT_X + 0.1, ys[-1], 3.5), 0.05, 0.05, m['steel'])   # back bracing
    ct.beam_between((CANT_X + 0.1, ys[0], 3.5), (CANT_X + 0.1, ys[-1], 1.5), 0.05, 0.05, m['steel'])
    ct.finish(col)
    cl = pb.Part("WH_CantileverLoad")
    for z, r, n in ((1.0, 0.11, 5), (2.0, 0.08, 6), (3.0, 0.16, 3), (4.0, 0.05, 10)):
        for k in range(n):
            x = CANT_X - 0.35 - k * (2 * r + 0.02)
            if x - r < CANT_X - 1.3:
                break
            cl.cyl_between((x, ys[0] - 0.3, z + 0.08 + r), (x, ys[-1] + 0.3, z + 0.08 + r), r, m['galv'] if k % 2 else m['grey'], seg=12)
    cl.finish(col)

    # --- high-bay lights ---
    lt = pb.Part("WH_Lights")
    for x in [-27.0 + 6.0 * i for i in range(10)]:
        for y in (-11.5, -6.0, 0.0, 5.85, 11.75):
            lt.cyl_between((x, y, roof_z(y) - 0.2), (x, y, 10.6), 0.008, m['steel'], seg=4)
            lt.cyl(0.25, 0.2, (x, y, 10.5), m['grey'], seg=16)
            lt.cyl(0.22, 0.02, (x, y, 10.39), mx['lamp'], seg=16)
    lt.finish(col)

    # --- REF ---
    pb.ref_human(ref, (0.0, -12.0, 0.0))
    pb.ref_human(ref, (DOCK_X[1], -HY - 6.0, WELL_Z))
    pb.ref_ground(ref, (-60, -55, 60, 45), [(-HX - 0.3, -HY - 0.3, HX + 0.3, HY + 0.3),
                                              (wx0 - 0.3, -HY - 22.0, wx1 + 0.3, -HY - 0.3)], z=-0.01)
    fk = pb.Part("REF_Forklift_3t")
    fm = pb.mat("M_REF_Forklift", (0.85, 0.55, 0.05), 0, 0.5)
    fk.box_mm((-1.5, -0.55, 0.0), (1.2, 0.55, 2.2), fm)
    fk.box_mm((1.2, -0.45, 0.0), (1.3, 0.45, 3.5), fm)
    fk.finish(ref)
    bpy.data.objects["REF_Forklift_3t"].location = (2.0, 0.0, 0.0)

    def pose():   # interior view: roof and north cladding hidden, dock 1 open, lip out
        bpy.data.objects["WH_Roof"].hide_render = True
        bpy.data.objects["WH_Cladding_North"].hide_render = True
        bpy.data.objects["WH_Lights"].hide_render = True
        doors[0].location.z += DOCK_H - 0.05
        lips[0].rotation_euler = (math.radians(-90), 0, 0)

    table = pm.finish_asset(name, "Warehouse", [
        ("Preview_Exterior.png", (45, -70, 32), (5, -5, 3), 30),
        ("Preview_Interior.png", (-12, 45, 42), (2, -1, 0), 26, True),
    ], pose=pose, ground=None)
    n_obj, n_tri = pm.counts(name)
    positions = RACK_BAYS * len(RACK_LINES) * (1 + len(BEAM_Z)) * 3
    readme_warehouse(table, n_obj, n_tri, positions, wx0, wx1)
    return name


def readme_warehouse(table, n_obj, n_tri, positions, wx0, wx1):
    """README for the Warehouse folder (warehouse section; the rack props are appended by build_rack)."""
    text = f"""
Spares and consumables warehouse with high pallet racking, three truck docks and a drive-in door.
Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_warehouse.py`.
The layout is an own design.

Origin: finished floor level (z 0) at the centre of the building. +X east, the docks face south (-Y).

{n_obj} parts, about {n_tri:,} triangles. Previews: Preview_Exterior.png, Preview_Interior.png (roof,
north wall and lights hidden, dock 1 open with its lip out). REF holds a 3 t forklift block, two
1.8 m figures and a ground slab with the building and dock well left open.

### Layout

| Zone | Extent |
|---|---|
| Building (outside of cladding) | x {-HX - 0.12:.2f} to {HX + 0.12:.2f}, y {-HY - 0.12:.2f} to {HY + 0.12:.2f}, eave {EAVE:.1f} m, ridge {RIDGE:.1f} m |
| Portal frames | 11 frames at 6.0 m centres, x -30 to 30 |
| Marshalling / dispatch area behind the docks | y -14.75 to -8.8 |
| Pallet racking | {len(RACK_LINES)} single-depth lines (2 single, 3 back-to-back pairs), {RACK_BAYS} bays each, x {RACK_X0:.1f} to {RACK_X0 + RACK_BAYS * RACK_PITCH:.1f}. Aisles 3.5 m (y -7.7..-4.2, -1.8..1.7, 4.1..7.6, 10.0..13.5) |
| Storage positions | {positions:,} EUR-pallet positions (3 per beam level, 5 levels including the floor); about 68 % are filled in WH_RackLoad |
| Cantilever rack | Column line x {CANT_X:.2f}, y {CANT_Y[0]:.1f} to {CANT_Y[1]:.1f}, 1.2 m arms toward -X at z 1, 2, 3, 4 |
| Office / counter | x {OFFICE[0]:.2f} to {OFFICE[2]:.1f}, y {OFFICE[1]:.1f} to {OFFICE[3]:.2f}, 3.5 m high, counter window on the east face at y 10.5 to 13.5, flat roof used as a storage deck with handrail |

### Moving parts

| Part | Motion |
|---|---|
| WH_Door_Dock1..3 | Roller shutter. Slide +Z by {DOCK_H - 0.05:.2f} m to open (rolls into the coil box) |
| WH_Door_DriveIn | Roller shutter. Slide +Z by {DRIVE_H - 0.05:.2f} m to open |
| WH_LevellerLip_1..3 | Hinged lip. Rotate about local X: 0° hangs down (stowed), -90° rests on the truck bed |
| WH_Roof, WH_Cladding_* | Static, separate so they can be hidden for cutaway views |
| WH_RackLoad, WH_CantileverLoad | Static stock, separate so it can be hidden or replaced with the Consumables props |

### Pivots

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{table}

### Footprint and connection points

| Item | Value |
|---|---|
| Dock doors (south wall) | Centres x {', '.join(f'{x:.1f}' for x in DOCK_X)}, y {-HY:.1f}; {DOCK_W:.1f} x {DOCK_H:.1f} m, sill at floor level 0.0 |
| Dock well | x {wx0:.1f} to {wx1:.1f}, y {-HY - 12.0:.1f} to {-HY - 0.3:.1f}, floor z {WELL_Z:.1f} (truck bed about level with the warehouse floor) |
| Dock well ramp top (road joins here) | x {wx0:.1f} to {wx1:.1f} at y {-HY - 22.0:.1f}, z 0.0, 12 % down toward the docks |
| Drive-in door (west wall) | Centre ({-HX:.1f}, 0.0, 0.0), {DRIVE_W:.1f} x {DRIVE_H:.1f} m, leads into the aisle at y -1.8..1.7 |
| Office personnel door (west wall) | ({-HX:.1f}, 10.5, 0.0), 1.0 x 2.1 m |
| Fire exit (east wall) | ({HX:.1f}, -11.5, 0.0), 1.0 x 2.1 m |

### Dimensions

| Item | Value | Status |
|---|---|---|
| Building {L:.0f} x {W:.0f} m, eave {EAVE:.0f} m | | Estimated (sizes given in the brief) |
| Rack beam clear span 2.7 m, frame depth {RACK_DEPTH} m, 3 EUR pallets per level | | Typical industry values for 1200 x 800 mm pallets, estimated |
| Beam levels z {', '.join(f'{z:.1f}' for z in BEAM_Z)} (frame {RACK_H} m) | | Estimated |
| Aisle 3.5 m | | Estimated for a 3 t counterbalance forklift (right-angle stacking aisle about 3.5-4.0 m) |
| Dock door {DOCK_W:.1f} x {DOCK_H:.1f} m, leveller 2.0 x 2.5 m, dock well 1.2 m deep | | Estimated, common European dock sizes |
| Cantilever arms 1.2 m, 4 levels | | Estimated |
"""
    pm.write_readme("Warehouse", "Warehouse", "Spares warehouse for the plant, plus the pallet-rack props it is built from.",
                    [("SM_Warehouse", text)])


# ===========================================================================
# Pallet rack props
# ===========================================================================

def build_rack():
    """SM_PalletRackBay (frame at x 0 + beams to x 2.8) and SM_PalletRackFrame (end frame)."""
    name = "SM_PalletRack"
    m = pm.start(name)[2]
    mx = extra_mats()
    out = pm.out_dir("Warehouse")
    top = pb.collection(name)
    info = []
    for prop, fn in (("SM_PalletRackBay", lambda p: (rack_frame(p, 0.0, 0.0, RACK_DEPTH, mx),
                                                      rack_beams(p, 0.0, 0.0, RACK_DEPTH, mx))),
                     ("SM_PalletRackFrame", lambda p: rack_frame(p, 0.0, 0.0, RACK_DEPTH, mx))):
        c = pb.collection(prop, top)
        p = pb.Part(prop.replace("SM_", "PR_"))
        fn(p)
        ob = p.finish(c)
        pb.export_fbx(os.path.join(out, prop + ".fbx"), [c.name])
        ob.data.calc_loop_triangles()
        info.append((prop, len(ob.data.loop_triangles)))
    # preview: three bays and an end frame, partly loaded
    ref = pb.collection("REF")
    bay = bpy.data.objects["PR_PalletRackBay"]
    for i in (1, 2):
        dup = bay.copy()
        dup.location.x = i * RACK_PITCH
        ref.objects.link(dup)
    endf = bpy.data.objects["PR_PalletRackFrame"]
    endf.location.x = 3 * RACK_PITCH
    pb.ref_human(ref, (-1.2, -1.0, 0))
    pb.save_blend(os.path.join(out, name + ".blend"))
    endf.location.x = 3 * RACK_PITCH
    pb.setup_render(res=(1280, 720), samples=32)
    g = pb.Part("REF_Ground")
    g.box_mm((-20, -20, -0.05), (20, 20, -0.002), pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
    g.finish(ref)
    pb.render_view(os.path.join(out, "Preview_PalletRack.png"), (-6.0, -13.0, 5.0), (4.2, 0.5, 4.0), 28)
    endf.location.x = 0.0
    return info


def readme_rack(info):
    """Append the rack props section to Meshes/Warehouse/README.md."""
    tri = {k: v for k, v in info}
    text = f"""
## SM_PalletRackBay and SM_PalletRackFrame

Reusable selective pallet racking, the same geometry the warehouse uses. Both live in
SM_PalletRack.blend and export as separate FBX files. Each is one static part (PR_PalletRackBay,
PR_PalletRackFrame), pivot at its origin. Preview: Preview_PalletRack.png (three bays plus the end
frame). About {tri['SM_PalletRackBay']:,} and {tri['SM_PalletRackFrame']:,} triangles.

Origin: floor level at the front upright of the frame, on the frame centre line. The rack runs
toward +X and its depth toward +Y (aisle on the -Y side).

To build a run of n bays, place SM_PalletRackBay at x = 0, {RACK_PITCH}, 2 × {RACK_PITCH}, ... (n copies)
and one SM_PalletRackFrame at x = n × {RACK_PITCH}. Back-to-back runs: second run rotated 180°
with 0.2 m between the backs.

| Item | Value | Status |
|---|---|---|
| Bay pitch {RACK_PITCH} m (2.7 m clear between uprights), depth {RACK_DEPTH} m | | Estimated, typical for 3 EUR pallets per level |
| Frame height {RACK_H} m, uprights 90 x 70 mm, bracing every 1.2 m | | Estimated |
| Beam levels (tops) z {', '.join(f'{z:.1f}' for z in BEAM_Z)}, 120 mm box beams, 2 deck support bars per level | | Estimated |
| Load per level | 3 EUR pallets, about 1 t each | Estimated |

## Unreal import

{pm.UNREAL_NOTE.strip()}
"""
    with open(os.path.join(pm.out_dir("Warehouse"), "README.md"), "a") as f:
        f.write(text)


# ===========================================================================
# Consumables
# ===========================================================================

EPAL = (1.2, 0.8, 0.144)   # EUR pallet (EPAL 1)


def euro_pallet(p, cx, cy, z0, m):
    """EPAL 1 pallet, 1200 x 800 x 144 mm, long side along X: bottom boards, 9 blocks, 3 cross
    boards, 5 top boards. Returns the deck top height."""
    w = m['wood']
    for y, bw in ((-0.35, 0.1), (0.0, 0.145), (0.35, 0.1)):              # 3 bottom boards
        p.box_mm((cx - 0.6, cy + y - bw / 2, z0), (cx + 0.6, cy + y + bw / 2, z0 + 0.022), w)
    for x in (-0.5275, 0.0, 0.5275):
        for y in (-0.3275, 0.0, 0.3275):                                   # 9 blocks
            bx = 0.145
            p.box_mm((cx + x - bx / 2, cy + y - 0.0725, z0 + 0.022), (cx + x + bx / 2, cy + y + 0.0725, z0 + 0.1), w)
        p.box_mm((cx + x - 0.0725, cy - 0.4, z0 + 0.1), (cx + x + 0.0725, cy + 0.4, z0 + 0.122), w)  # cross boards
    for y, bw in ((-0.3275, 0.145), (-0.1575, 0.1), (0.0, 0.145), (0.1575, 0.1), (0.3275, 0.145)):
        p.box_mm((cx - 0.6, cy + y - bw / 2, z0 + 0.122), (cx + 0.6, cy + y + bw / 2, z0 + 0.144), w)
    return z0 + 0.144


def loft(p, rings, m, cap=True):
    """Closed surface through rings of points (each ring a closed loop, same count), with end caps."""
    vr = [[p.bm.verts.new(v) for v in r] for r in rings]
    idx = p._mi(m)
    n = len(vr[0])
    for a, b in zip(vr[:-1], vr[1:]):
        for j in range(n):
            f = p.bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
            f.material_index = idx
    if cap:
        for r in (vr[0], vr[-1]):
            f = p.bm.faces.new(r)
            f.material_index = idx
    bmesh.ops.recalc_face_normals(p.bm, faces=[f for f in p.bm.faces if f.material_index == idx])


def rsquare(cx, cy, z, ax, ay, n=24, k=6.0):
    """Rounded-square ring (superellipse, exponent k) of half sizes ax, ay at height z."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        pts.append(Vector((cx + ax * math.copysign(abs(c) ** (2 / k), c),
                           cy + ay * math.copysign(abs(s) ** (2 / k), s), z)))
    return pts


def p_euro_pallet(col, m, mx):
    p = pb.Part("CS_EuroPallet")
    euro_pallet(p, 0, 0, 0, m)
    p.finish(col)


def p_brick_pallet(col, m, mx):
    """175 magnesia-chrome bricks (230 x 114 x 76 mm), 5 layers of 5 x 7, on a EUR pallet; wrap separate."""
    p = pb.Part("BP_PalletBricks")
    z = euro_pallet(p, 0, 0, 0, m)
    bl, bw, bh, g = 0.23, 0.114, 0.076, 0.003
    for layer in range(5):
        for i in range(5):
            for j in range(7):
                x = -0.575 + bl / 2 + i * bl
                y = -0.399 + bw / 2 + j * bw
                p.box((bl - g, bw - g, bh - g), (x, y, z + bh / 2 + layer * bh), m['refr'])
    p.finish(col)
    w = pb.Part("BP_Wrap")
    w.box_mm((-0.585, -0.41, 0.15), (0.585, 0.41, z + 5 * bh + 0.01), mx['wrap'])
    w.finish(col)


def p_sack_pallet(col, m, mx, name, prefix, layers, bag_h, mat):
    """Sacks 0.6 x 0.4 m on a EUR pallet, 4 per layer in alternating orientation; wrap separate."""
    p = pb.Part(prefix + "_PalletSacks")
    z = euro_pallet(p, 0, 0, 0, m)
    for layer in range(layers):
        zc = z + bag_h / 2 + layer * bag_h
        if layer % 2 == 0:
            spots = [(-0.3, -0.2, 0.6, 0.4), (0.3, -0.2, 0.6, 0.4), (-0.3, 0.2, 0.6, 0.4), (0.3, 0.2, 0.6, 0.4)]
        else:
            spots = [(-0.4, 0.1, 0.4, 0.6), (0.0, 0.1, 0.4, 0.6), (0.4, 0.1, 0.4, 0.6), (0.0, -0.3, 1.2, 0.2)]
            spots = spots[:3] + [(-0.3, -0.3, 0.6, 0.2), (0.3, -0.3, 0.6, 0.2)]
        for x, y, sx, sy in spots:
            # pillow shape: lofted rounded rectangle, fuller in the middle
            rings = [rsquare(x, y, zc - bag_h / 2 + 0.005, sx / 2 - 0.03, sy / 2 - 0.03, 16),
                     rsquare(x, y, zc, sx / 2 - 0.005, sy / 2 - 0.005, 16),
                     rsquare(x, y, zc + bag_h / 2 - 0.005, sx / 2 - 0.03, sy / 2 - 0.03, 16)]
            loft(p, rings, mat)
    p.finish(col)
    w = pb.Part(prefix + "_Wrap")
    w.box_mm((-0.61, -0.41, 0.15), (0.61, 0.41, z + layers * bag_h + 0.01), mx['wrap'])
    w.finish(col)


def p_castable(col, m, mx):
    p_sack_pallet(col, m, mx, "SM_CastableBagPallet", "CB", 10, 0.11, mx['bag'])


def p_reagent(col, m, mx):
    p_sack_pallet(col, m, mx, "SM_ReagentSackPallet", "RS", 8, 0.13, mx['sack'])


def p_bulk_bag(col, m, mx):
    """FIBC about 0.9 x 0.9 x 1.1 m body (about 0.9 m3 filled), 4 corner loops, tied top spout."""
    p = pb.Part("BB_BulkBag")
    H = 1.1
    rings = []
    for k, z in enumerate((0.0, 0.05, 0.3, 0.6, 0.9, H - 0.04, H)):
        bulge = (0.0, 0.03, 0.05, 0.055, 0.04, 0.0, -0.06)[k]
        rings.append(rsquare(0, 0, z, 0.45 + bulge, 0.45 + bulge, 24, 8.0))
    loft(p, rings, mx['fibc'])
    p.cyl(0.2, 0.06, (0, 0, H + 0.03), mx['fibc'], seg=16, r2=0.14)
    p.cyl(0.12, 0.25, (0, 0, H + 0.18), mx['fibc'], seg=12, r2=0.09)               # spout
    p.cyl(0.095, 0.03, (0, 0, H + 0.2), m['white'], seg=12)                       # tie
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):                            # lifting loops
        c = Vector((sx * 0.42, sy * 0.42, H - 0.02))
        d = Vector((-sy, sx, 0)).normalized() * 0.07
        top = c + Vector((0, 0, 0.28))
        p.beam_between(c - d, top - d * 0.4, 0.05, 0.006, m['blue'])
        p.beam_between(top - d * 0.4, top + d * 0.4, 0.05, 0.006, m['blue'])
        p.beam_between(top + d * 0.4, c + d, 0.05, 0.006, m['blue'])
    p.finish(col)


def p_ibc(col, m, mx):
    """1000 L IBC: 1.2 x 1.0 x 1.16 m, steel/plastic pallet, HDPE bottle, tubular cage, DN50 valve at +X."""
    p = pb.Part("IBC_Tote")
    p.box_mm((-0.6, -0.5, 0.0), (0.6, 0.5, 0.03), m['steel'])
    for y in (-0.42, 0.0, 0.42):
        p.box_mm((-0.6, y - 0.06, 0.0), (0.6, y + 0.06, 0.13), m['steel'])
    p.box_mm((-0.6, -0.5, 0.13), (0.6, 0.5, 0.15), m['galv'])
    loft(p, [rsquare(0, 0, 0.155, 0.55, 0.46, 24, 8), rsquare(0, 0, 1.12, 0.55, 0.46, 24, 8)], mx['hdpe'])
    p.cyl(0.075, 0.04, (0.0, 0.0, 1.14), m['white'], seg=16)                        # filler cap
    cage = m['galv']
    for z in (0.16, 0.48, 0.8, 1.13):                                              # horizontal ring tubes
        for a, b in (((-0.57, -0.48), (0.57, -0.48)), ((0.57, -0.48), (0.57, 0.48)),
                     ((0.57, 0.48), (-0.57, 0.48)), ((-0.57, 0.48), (-0.57, -0.48))):
            p.cyl_between((a[0], a[1], z), (b[0], b[1], z), 0.009, cage, seg=6)
    for t in [i / 7 for i in range(8)]:                                            # vertical tubes
        for pa, pb_ in (((-0.57 + 1.14 * t, -0.48), None), ((-0.57 + 1.14 * t, 0.48), None),
                        ((-0.57, -0.48 + 0.96 * t), None), ((0.57, -0.48 + 0.96 * t), None)):
            p.cyl_between((pa[0], pa[1], 0.15), (pa[0], pa[1], 1.13), 0.009, cage, seg=6)
    p.cyl(0.06, 0.12, (0.6, 0.0, 0.22), m['grey'], rot=(0, 90, 0), seg=14)         # outlet valve
    p.box((0.04, 0.2, 0.03), (0.63, 0.0, 0.3), m['orange'])                          # valve lever
    p.finish(col)


def p_drum(col, m, mx):
    """200 L steel drum, 0.585 m outside diameter x 0.88 m, two rolling hoops, two bungs."""
    p = pb.Part("DR_Drum200L")
    R, H = 0.2925, 0.88
    p.cyl(R - 0.008, H - 0.02, (0, 0, H / 2), m['blue'], seg=32)
    for z in (0.012, H - 0.012):                                                  # chimes
        p.cyl(R, 0.024, (0, 0, z), m['blue'], seg=32)
    for z in (H / 3, 2 * H / 3):                                                   # rolling hoops
        p.cyl(R, 0.03, (0, 0, z), m['blue'], seg=32)
    p.cyl(0.035, 0.012, (0.18, 0, H), m['grey'], seg=12)                            # 2" bung
    p.cyl(0.02, 0.012, (-0.18, 0, H), m['grey'], seg=10)                            # 3/4" bung
    p.finish(col)


BLANK_W, BLANK_H, BLANK_T = 1.040, 1.050, 0.00325   # 316L blade, matches acm_common.py
HBAR_L, HBAR_W, HBAR_H = 1.32, 0.025, 0.035
CRATE_N, CRATE_PITCH = 20, 0.05


def p_blank_crate(col, m, mx):
    """Steel transport crate holding 20 new permanent-cathode blanks hanging by their bars."""
    f = pb.Part("CBC_Frame")
    X, Y, Hc = 0.74, 0.58, 1.38          # half length (bar direction), half width, height
    seat = 1.26                          # hanger-bar underside on the top rails
    for y in (-Y + 0.08, Y - 0.08):                                                # fork channels
        f.box_mm((-X, y - 0.1, 0.0), (X, y + 0.1, 0.12), m['steel'])
    f.box_mm((-X, -Y, 0.12), (X, Y, 0.15), m['steel'])                              # deck plate
    for sx in (1, -1):
        for sy in (1, -1):
            f.box_mm((sx * X - (0.06 if sx > 0 else -0.06) - 0.03, sy * Y - (0.03 if sy > 0 else -0.03) - 0.03, 0.0),
                     (sx * X - (0.06 if sx > 0 else -0.06) + 0.03, sy * Y - (0.03 if sy > 0 else -0.03) + 0.03, Hc), m['yellow'])
        f.box_mm((sx * 0.62 - 0.04, -Y, seat - 0.06), (sx * 0.62 + 0.04, Y, seat), m['yellow'])    # bar rails
        for k in range(CRATE_N + 1):                                                # comb teeth between bars
            y = -CRATE_N * CRATE_PITCH / 2 + k * CRATE_PITCH
            f.box((0.06, 0.008, 0.04), (sx * 0.62, y, seat + 0.02), m['rubber'])
        f.box_mm((sx * X - 0.06, -Y, 0.5), (sx * X, Y, 0.56), m['yellow'])           # side rails
    for sy in (1, -1):
        f.box_mm((-X, sy * Y - 0.03, Hc - 0.06), (X, sy * Y + 0.03, Hc), m['yellow'])
        f.box_mm((-X, sy * Y - 0.03, 0.5), (X, sy * Y + 0.03, 0.56), m['yellow'])
    for sx in (1, -1):                                                              # lifting eyes
        for sy in (1, -1):
            f.cyl(0.04, 0.02, (sx * (X - 0.09), sy * (Y - 0.06), Hc + 0.04), m['steel'], rot=(90, 0, 0), seg=10)
    f.finish(col)
    b = pb.Part("CBC_Blanks")
    for k in range(CRATE_N):
        y = -CRATE_N * CRATE_PITCH / 2 + CRATE_PITCH / 2 + k * CRATE_PITCH
        b.box((HBAR_L, HBAR_W, HBAR_H), (0, y, seat + HBAR_H / 2), mx['copper'])
        b.box((BLANK_W, BLANK_T, BLANK_H), (0, y, seat - BLANK_H / 2), mx['stainless'])
        for sx in (1, -1):                                                          # edge strips
            b.box((0.02, 0.01, BLANK_H - 0.03), (sx * (BLANK_W / 2 + 0.004), y, seat - 0.03 - (BLANK_H - 0.03) / 2), mx['edge'])
    b.finish(col)


def p_spares_crate(col, m, mx):
    """Open timber crate 1.6 x 1.0 x 0.8 m with machine spares; the lid is a separate part."""
    c = pb.Part("SSC_Crate")
    w = m['wood']
    for y in (-0.4, 0.0, 0.4):
        c.box_mm((-0.8, y - 0.05, 0.0), (0.8, y + 0.05, 0.1), w)                     # skids
    c.box_mm((-0.8, -0.5, 0.1), (0.8, 0.5, 0.125), w)                                # floor
    for z in (0.15, 0.32, 0.49, 0.66):                                              # side slats
        for sy in (1, -1):
            c.box_mm((-0.8, sy * 0.5 - 0.0125, z), (0.8, sy * 0.5 + 0.0125, z + 0.12), w)
        for sx in (1, -1):
            c.box_mm((sx * 0.8 - 0.0125, -0.49, z), (sx * 0.8 + 0.0125, 0.49, z + 0.12), w)
    for sx in (1, -1):
        for sy in (1, -1):
            c.box_mm((sx * 0.76 - 0.04, sy * 0.46 - 0.04, 0.1), (sx * 0.76 + 0.04, sy * 0.46 + 0.04, 0.8), w)
    c.finish(col)
    s = pb.Part("SSC_Contents")
    s.cyl_between((-0.65, -0.2, 0.25), (0.65, -0.2, 0.25), 0.08, m['grey'], seg=16)    # pump shaft
    for k in range(4):                                                              # flange stack
        s.cyl(0.18, 0.03, (0.35, 0.2, 0.14 + k * 0.032), m['grey'], seg=20)
    s.cyl(0.2, 0.25, (-0.35, 0.2, 0.25), m['blue'], seg=20)                          # bearing housing
    s.box((0.3, 0.2, 0.15), (0.0, 0.25, 0.2), m['red'])                              # bolt box
    s.finish(col)
    lid = pb.Part("SSC_Lid", pivot=(0, 0, 0.8))
    for y in [-0.45 + 0.15 * k for k in range(7)]:
        lid.box_mm((-0.8, y - 0.07, 0.8), (0.8, y + 0.07, 0.825), w)
    for x in (-0.6, 0.0, 0.6):
        lid.box_mm((x - 0.05, -0.48, 0.825), (x + 0.05, 0.48, 0.85), w)
    lid.finish(col)


def p_gas_cage(col, m, mx):
    """Gas cylinder storage cage 1.6 x 0.9 x 2.0 m, mesh panels, two hinged front gates (front -Y),
    10 x 50 L cylinders in two rows with a restraint bar."""
    X, Y, H = 0.8, 0.45, 2.0
    g = m['galv']
    c = pb.Part("GCC_Cage")
    for sx in (1, -1):
        for sy in (1, -1):
            c.box_mm((sx * X - 0.025, sy * Y - 0.025, 0), (sx * X + 0.025, sy * Y + 0.025, H), g)
    c.box_mm((-X, -Y, 0.0), (X, Y, 0.05), m['concrete'])                              # plinth
    c.poly_prism([(-Y - 0.1, H), (Y + 0.1, H + 0.12), (Y + 0.1, H + 0.14), (-Y - 0.1, H + 0.02)],
                 -X - 0.1, X + 0.1, m['galv'], plane='YZ')                            # mono-pitch roof
    fix_normals(c)
    for z in (0.1, H - 0.05):
        for a, b in (((-X, Y), (X, Y)), ((X, -Y), (X, Y)), ((-X, -Y), (-X, Y)), ((-X, -Y), (X, -Y))):
            c.beam_between((a[0], a[1], z), (b[0], b[1], z), 0.04, 0.04, g)
    for k in range(1, 16):                                                          # back mesh rods
        x = -X + 2 * X * k / 16
        c.box_mm((x - 0.004, Y - 0.004, 0.1), (x + 0.004, Y + 0.004, H - 0.05), g)
    for sx in (1, -1):                                                              # side mesh rods
        for k in range(1, 9):
            y = -Y + 2 * Y * k / 9
            c.box_mm((sx * X - 0.004, y - 0.004, 0.1), (sx * X + 0.004, y + 0.004, H - 0.05), g)
    for z in [0.1 + 0.15 * k for k in range(13)]:
        c.box_mm((-X, Y - 0.004, z - 0.004), (X, Y + 0.004, z + 0.004), g)
        for sx in (1, -1):
            c.box_mm((sx * X - 0.004, -Y, z - 0.004), (sx * X + 0.004, Y, z + 0.004), g)
    for row_y in (-0.15, 0.22):                                                     # restraint bars
        c.cyl_between((-X, row_y + 0.13, 1.1), (X, row_y + 0.13, 1.1), 0.012, m['yellow'], seg=8)
    c.box((0.3, 0.02, 0.2), (0.0, -Y - 0.02, 1.6), m['yellow'])                       # hazard sign
    c.finish(col)
    gates = []
    for side, sx in (("L", -1), ("R", 1)):
        hinge = Vector((sx * X, -Y, 0.0))
        gt = pb.Part(f"GCC_Gate{side}", pivot=hinge)
        x_in = sx * X - sx * (X - 0.02)          # gate leaf runs from the hinge to the centre line
        x0, x1 = min(sx * X, x_in), max(sx * X, x_in)
        for z in (0.12, 1.0, H - 0.08):
            gt.box_mm((x0, -Y - 0.02, z - 0.02), (x1, -Y + 0.02, z + 0.02), g)
        for x in (x0 + 0.02, x1 - 0.02):
            gt.box_mm((x - 0.02, -Y - 0.02, 0.1), (x + 0.02, -Y + 0.02, H - 0.06), g)
        for k in range(1, 6):
            x = x0 + (x1 - x0) * k / 6
            gt.box_mm((x - 0.004, -Y - 0.004, 0.12), (x + 0.004, -Y + 0.004, H - 0.08), g)
        gates.append(gt.finish(col))
    cy = pb.Part("GCC_Cylinders")
    colours = (m['white'], mx['maroon'], m['green'], mx['black'], m['white'])
    for r, row_y in enumerate((-0.15, 0.22)):
        for k in range(5):
            x = -0.6 + 0.3 * k
            body = colours[(k + r) % len(colours)]
            cy.cyl(0.115, 1.3, (x, row_y, 0.7), m['grey'], seg=16)                     # 230 mm body
            cy.cyl(0.115, 0.18, (x, row_y, 1.44), body, seg=16, r2=0.05)               # coloured shoulder
            cy.cyl(0.04, 0.12, (x, row_y, 1.58), m['grey'], seg=10)                    # valve guard cap
    cy.finish(col)


PROPS = [
    ("SM_EuroPallet", p_euro_pallet),
    ("SM_BrickPallet", p_brick_pallet),
    ("SM_CastableBagPallet", p_castable),
    ("SM_ReagentSackPallet", p_reagent),
    ("SM_BulkBag", p_bulk_bag),
    ("SM_IBC", p_ibc),
    ("SM_Drum200L", p_drum),
    ("SM_CathodeBlankCrate", p_blank_crate),
    ("SM_SteelSparesCrate", p_spares_crate),
    ("SM_GasCylinderCage", p_gas_cage),
]


def build_consumables():
    name = "SM_Consumables"
    top, ref, m = pm.start(name)
    mx = extra_mats()
    out = pm.out_dir("Consumables")
    info = []
    x = 0.0
    for prop, fn in PROPS:
        c = pb.collection(prop, top)
        fn(c, m, mx)
        pb.export_fbx(os.path.join(out, prop + ".fbx"), [c.name])
        obs = sorted(c.objects, key=lambda o: o.name)
        tris = 0
        for o in obs:
            o.data.calc_loop_triangles()
            tris += len(o.data.loop_triangles)
        info.append((prop, [(o.name, tuple(o.matrix_world.translation)) for o in obs], tris))
        # move into a display row (spacing by the prop's own width)
        xs = [(o.matrix_world @ Vector(v)).x for o in obs for v in o.bound_box]
        w0, w1 = min(xs), max(xs)
        x += -w0
        for o in obs:
            o.location.x += x
        x += w1 + 0.6
    # spares crate lid leaning against its crate in the display
    lid = bpy.data.objects["SSC_Lid"]
    lid.location.y -= 0.62
    lid.location.z -= 0.35
    lid.rotation_euler = (math.radians(-75), 0, 0)
    pb.ref_human(ref, (x + 0.4, 0.0, 0.0))
    pb.save_blend(os.path.join(out, name + ".blend"))
    pb.setup_render(res=(1280, 720), samples=32)
    g = pb.Part("REF_Ground")
    g.box_mm((-10, -15, -0.05), (x + 10, 15, -0.002), pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
    g.finish(ref)
    mid = x / 2
    for wn in ("BP_Wrap", "CB_Wrap", "RS_Wrap"):   # show the bricks and sacks in the preview
        bpy.data.objects[wn].hide_render = True
    pb.render_view(os.path.join(out, "Preview_ContactSheet.png"), (mid, -17.0, 5.5), (mid, 0, 0.6), 30)
    readme_consumables(info)
    return name


def readme_consumables(info):
    rows = []
    for prop, obs, tris in info:
        parts = ", ".join(o for o, _ in obs)
        rows.append(f"| {prop} | {parts} | {tris:,} |")
    text = f"""
# Consumables

Palletised and packaged goods that arrive at the plant (section 12 of the equipment reference:
refractory bricks and castables, electrolyte additives and reagents, acid and oils, steel spares,
cathode blanks). Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_warehouse.py`. Each prop is exported to its own FBX at its own
origin; SM_Consumables.blend holds them all in a display row. Preview: Preview_ContactSheet.png.

Origins: floor level, centre of the footprint. Long sides run along X. IBC valve and cathode-crate
lifting points as described below; the gas cage front (gates) faces -Y.

## Props

| FBX | Parts | Triangles |
|---|---|---|
{chr(10).join(rows)}

All parts are static and pivot at the prop origin (0, 0, 0), except SSC_Lid (pivot (0, 0, 0.80),
the top of the crate) and the gas cage gates below.

## Moving parts

| Part | Motion |
|---|---|
| GCC_GateL / GCC_GateR | Swing about local Z at the hinge posts (-0.80, -0.45, 0) and (0.80, -0.45, 0). Open outward: GateL -100°, GateR +100° |
| SSC_Lid | Lift off; in the display it leans against the crate |
| BP_Wrap, CB_Wrap, RS_Wrap | Shrink wrap shells: hide them to show the bricks or sacks, or give them a translucent material in Unreal |
| CBC_Blanks | Separate from CBC_Frame, so the empty crate can be reused |

## Dimensions

| Item | Value | Status |
|---|---|---|
| EUR pallet | 1200 x 800 x 144 mm, 5 top boards, 3 cross boards, 9 blocks, 3 bottom boards | Sourced (EPAL 1 / EN 13698-1 standard sizes, from memory of the standard; board widths approximate) |
| Refractory brick | 230 x 114 x 76 mm "9-inch straight", 175 per pallet | Brick size is the standard straight size (sourced from general refractory practice, not a specific supplier). Mass about 6 kg each in magnesia-chrome (about 3.0 t/m³, estimated), about 1.05 t per pallet |
| Castable sacks | 25 kg, 0.6 x 0.4 x 0.11 m, 40 per pallet (1.0 t) | Estimated |
| Reagent sacks | 25 kg paper sacks, 0.6 x 0.4 x 0.13 m, 32 per pallet (0.8 t), for glue, thiourea, flocculant | Estimated |
| Bulk bag (FIBC) | 0.9 x 0.9 x 1.1 m body, 4 loops, tied filling spout | Estimated, typical 1 m³ bag |
| IBC | 1200 x 1000 x 1160 mm, 1000 L, DN50 outlet valve on the +X short side | Sourced as the common industry size (from memory, typical of composite IBCs) |
| 200 L drum | 585 mm outside diameter, 880 mm high, 2 rolling hoops | Typical tight-head drum size (from memory, ISO 15750 range), not checked against a supplier |
| Cathode blank crate | 1.48 x 1.16 x 1.38 m, 20 blanks at 50 mm pitch, hanger bars rest on comb rails at z 1.26 | Blank: 1.040 x 1.050 m, 3.25 mm 316L blade, 1.32 m bar 25 x 35 mm, matches the tankhouse assets (Tools/Blender/AnodeCathodeMachines/acm_common.py). Crate is an own design |
| Steel spares crate | 1.6 x 1.0 x 0.8 m timber, lid separate | Estimated |
| Gas cylinder cage | 1.6 x 0.9 x 2.0 m, 10 x 50 L cylinders (230 mm diameter, about 1.6 m with cap) | Cylinder size typical (from memory); cage estimated. Shoulder colours follow EN 1089-3 (white oxygen, maroon acetylene, dark green argon, black nitrogen) |

## Unreal import

{pm.UNREAL_NOTE.strip()}
"""
    with open(os.path.join(pm.out_dir("Consumables"), "README.md"), "w") as f:
        f.write(text.strip() + "\n")


# ===========================================================================

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    keys = argv or ["Warehouse", "Rack", "Consumables"]
    if "Warehouse" in keys:
        build_warehouse()
    if "Rack" in keys:
        readme_rack(build_rack()) if "Warehouse" in keys else build_rack()
    if "Consumables" in keys:
        build_consumables()


main()
