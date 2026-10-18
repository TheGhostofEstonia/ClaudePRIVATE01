"""
build_cathode_blank_repair_line.py - SM_CathodeBlankRepairLine (permanent cathode maintenance).

Run:  blender -b --factory-startup --python Tools/Blender/AnodeCathodeMachines/build_cathode_blank_repair_line.py

Boliden Pori sends flagged stainless blanks in special racks to a workshop for polishing,
contact cleaning, straightening, flattening and edge-strip replacement (Metso case study).
This line does those steps in order:
transport rack -> hoist -> hanging chain through a flatness scanner -> tilt flat ->
straightening press -> brush polisher -> hanger-bar contact grinder -> edge-strip
station -> tilt upright -> hanging chain -> hoist -> transport rack.
Layout and machine sizes are my own design.
"""
import math
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import acm_common as ac  # noqa: E402
from acm_common import pb  # noqa: E402

ASSET, NAME = "CathodeBlankRepairLine", "SM_CathodeBlankRepairLine"

# ---------------------------------------------------------------------------
# Layout parameters (metres). Own design unless stated.
# ---------------------------------------------------------------------------
Z = 1.95                      # hanger-bar seat on the chains (blade bottom at work height)
RZ = Z - ac.BLADE_H           # roller top = blade bottom = 0.90
CHAIN_Y = 0.62
RACK_Z = 1.40                 # hanger-bar seat in the transport racks
RACK_N = 20                   # blanks per transport rack
RACK_IN_X, RACK_OUT_X = 1.2, 28.0
CHAIN_IN = (3.4, 8.0)
TILT_IN = 8.45                # tilt-in hinge x (plate lies toward +X)
PRESS = (11.6, 14.0)
BRUSH = (15.0, 17.0)
GRIND_X = 18.0                # hanger-bar position under the contact grinders
EDGE_X = 20.0                 # blade centre at the edge-strip station
TILT_UP = 21.6                # tilt-up hinge x
CHAIN_OUT = (21.6, 26.2)
WIDTH = 1.50                  # roller length


def add_flat_blank(p, x0, M):
    """Blank lying flat on the rollers, blade from x0 toward +X, hanger bar at the +X end."""
    p.box((ac.BLADE_H, ac.BLADE_W, ac.BLADE_T), (x0 + ac.BLADE_H / 2, 0, RZ + ac.BLADE_T / 2), M['stainless'])
    p.box((ac.HBAR_H, ac.HBAR_L, ac.HBAR_W), (x0 + ac.BLADE_H + ac.HBAR_H / 2, 0, RZ + ac.HBAR_W / 2), M['copper'])
    for s in (-1, 1):
        p.box((ac.BLADE_H - 0.03, ac.EDGE_STRIP_W, 0.010),
              (x0 + (ac.BLADE_H - 0.03) / 2, s * (ac.BLADE_W / 2 + ac.EDGE_STRIP_W / 2 - 0.006), RZ + 0.005), M['plastic'])
    return p


def transport_rack(name, x, col, M):
    """Forkliftable rack: hanger-bar rails at RACK_Z for RACK_N blanks at cell pitch."""
    p = pb.Part(name, pivot=(x, 0, 0))
    L = RACK_N * ac.PITCH + 0.3
    p.box_mm((x - L / 2, -0.85, 0.08), (x + L / 2, 0.85, 0.16), M['frame'])          # base deck
    for dy in (-0.45, 0.45):                                                        # fork pockets
        p.box_mm((x - L / 2, dy - 0.15, 0.0), (x + L / 2, dy - 0.11, 0.08), M['frame'])
        p.box_mm((x - L / 2, dy + 0.11, 0.0), (x + L / 2, dy + 0.15, 0.08), M['frame'])
    for s in (-1, 1):
        p.box_mm((x - L / 2, s * CHAIN_Y - 0.04, RACK_Z - 0.08), (x + L / 2, s * CHAIN_Y + 0.04, RACK_Z), M['grey'])
        for dx in (-L / 2 + 0.05, 0.0, L / 2 - 0.05):
            p.box_mm((x + dx - 0.05, s * 0.80 - 0.05, 0.16), (x + dx + 0.05, s * 0.80 + 0.05, RACK_Z + 0.25), M['frame'])
        p.box_mm((x - L / 2, s * 0.80 - 0.05, RACK_Z + 0.20), (x + L / 2, s * 0.80 + 0.05, RACK_Z + 0.25), M['frame'])
        p.box_mm((x - L / 2, min(s * CHAIN_Y, s * 0.80), RACK_Z - 0.12), (x + L / 2, max(s * CHAIN_Y, s * 0.80), RACK_Z - 0.08), M['frame'])
    return p.finish(col)


def monorail_hoist(prefix, x0, x1, col, M, park_x):
    """Monorail beam on two posts, trolley (moves X) and hanger-bar gripper (moves Z)."""
    top = 4.2
    b = pb.Part(prefix + "_Monorail", pivot=(x0, 0, top))
    b.box_mm((x0 - 0.3, -0.10, top), (x1 + 0.3, 0.10, top + 0.35), M['yellow'])
    for x in (x0 - 0.2, x1 + 0.2):
        b.box_mm((x - 0.1, 1.15, 0), (x + 0.1, 1.35, top + 0.35), M['frame'])
        b.box_mm((x - 0.1, -0.10, top + 0.35), (x + 0.1, 1.35, top + 0.55), M['frame'])
    b.finish(col)
    t = pb.Part(prefix + "_Trolley", pivot=(park_x, 0, top))
    t.box((0.5, 0.35, 0.30), (park_x, 0, top - 0.15), M['frame'])
    t.box((0.3, 0.3, 0.4), (park_x, 0.3, top - 0.2), M['frame'])      # hoist motor
    t.finish(col)
    gz = Z + 0.30
    g = pb.Part(prefix + "_Gripper", pivot=(park_x, 0, gz))
    g.cyl_between((park_x, 0, gz), (park_x, 0, top - 0.3), 0.025, M['steel'], seg=8)
    g.box((0.12, 1.60, 0.10), (park_x, 0, gz), M['yellow'])
    for s in (-1, 1):
        g.box((0.08, 0.04, 0.30), (park_x, s * 0.76, gz - 0.15), M['yellow'])
        g.box((0.08, 0.10, 0.03), (park_x, s * 0.72, gz - 0.29), M['yellow'])
    g.finish(col)


def tilter(name, hinge_x, gaps, col, M):
    """
    Tilting frame drawn upright: hanger-bar hooks at Z, arms outside the roller frame at
    y = +-0.95, back bars at heights that land between the rollers when it is turned
    flat (+90 deg about Y lays the plate toward +X). Pivot on the hinge axis.
    """
    hz = RZ
    p = pb.Part(name, pivot=(hinge_x, 0, hz))
    p.cyl(0.05, 2.1, (hinge_x, 0, hz), M['grey'], rot=(90, 0, 0), seg=12)
    for s in (-1, 1):
        p.box_mm((hinge_x - 0.04, s * 0.95 - 0.04, hz), (hinge_x + 0.04, s * 0.95 + 0.04, Z + 0.12), M['frame'])
        p.box_mm((hinge_x - 0.08, min(s * CHAIN_Y, s * 0.95), Z - 0.06), (hinge_x + 0.08, max(s * CHAIN_Y, s * 0.95), Z), M['yellow'])
    for gx in gaps:
        z = hz + (gx - hinge_x)
        if hz + 0.08 < z < Z - 0.15:
            p.box_mm((hinge_x + 0.01, -0.95, z - 0.02), (hinge_x + 0.04, 0.95, z + 0.02), M['frame'])
    return p.finish(col)


def build(col, ref, M):
    # --- racks, hoists, hanging chains ---
    transport_rack("BR_TransportRack_In", RACK_IN_X, col, M)
    transport_rack("BR_TransportRack_Out", RACK_OUT_X, col, M)
    monorail_hoist("BR_HoistIn", RACK_IN_X - 1.0, CHAIN_IN[0] + 0.4, col, M, park_x=CHAIN_IN[0] + 0.2)
    monorail_hoist("BR_HoistOut", CHAIN_OUT[1] - 0.4, RACK_OUT_X + 1.0, col, M, park_x=CHAIN_OUT[1] - 0.2)
    ac.chain_conveyor("BR_ChainIn", CHAIN_IN[0], CHAIN_IN[1], CHAIN_Y, Z, col, M)
    ac.chain_conveyor("BR_ChainOut", CHAIN_OUT[0], CHAIN_OUT[1], CHAIN_Y, Z, col, M)

    # --- flatness scanner arch over the in-chain (laser line scanners both faces) ---
    sc = pb.Part("BR_FlatnessScanner", pivot=(6.0, 0, 0))
    ac.portal(sc, 6.0, 1.2, Z + 0.7, M, depth=0.2, beam=0.2)
    for s in (-1, 1):
        for dx in (-0.5, 0.5):
            sc.box_mm((6.0 + dx - 0.04, s * 1.2 - 0.04, 0), (6.0 + dx + 0.04, s * 1.2 + 0.04, Z + 0.7), M['frame'])
            sc.box((0.18, 0.12, 0.12), (6.0 + dx, s * 1.05, RZ + 0.65), M['cabinet'])
            sc.box((0.02, 0.06, 0.06), (6.0 + dx - s * 0.0, s * 0.98, RZ + 0.65), M['green'])
    sc.box((0.6, 0.3, 0.4), (6.0, -1.6, 1.6), M['cabinet'])      # vision PC / screen
    sc.finish(col)

    # --- roller tables (flat process line at work height) ---
    xs_in = ac.roller_conveyor("BR_TableIn", TILT_IN + 0.05, PRESS[0], 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BR_TableMid", PRESS[1], BRUSH[0], 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BR_BrushRolls", BRUSH[0], BRUSH[1], 0.0, RZ, WIDTH, col, M, pitch=0.5)
    ac.roller_conveyor("BR_TableGrind", BRUSH[1], 18.6, 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BR_TableEdge", 18.6, TILT_UP - 0.05, 0.0, RZ, WIDTH, col, M)
    xs_up = ac.roller_conveyor("BR_TableUp", TILT_UP + 0.05, TILT_UP + 1.45, 0.0, RZ, WIDTH, col, M, legs=False)

    # --- tilters ---
    tilter("BR_TiltIn", TILT_IN, [(a + b) / 2 for a, b in zip(xs_in, xs_in[1:])], col, M)
    up = tilter("BR_TiltUp", TILT_UP, [(a + b) / 2 for a, b in zip(xs_up, xs_up[1:])], col, M)
    up.rotation_euler.y = math.radians(90)          # drawn flat, waiting for a plate
    for nm, hx in (("BR_TiltInBase", TILT_IN), ("BR_TiltUpBase", TILT_UP)):
        tb = pb.Part(nm, pivot=(hx, 0, 0))
        for s in (-1, 1):
            tb.box_mm((hx - 0.15, s * 1.1 - 0.1, 0), (hx + 0.15, s * 1.1 + 0.1, RZ + 0.08), M['frame'])
        tb.box((0.45, 0.35, 0.35), (hx, -1.45, RZ), M['frame'])           # rotary actuator
        if nm == "BR_TiltUpBase":                                         # legs for the short table
            for x in (hx + 0.3, hx + 1.3):
                for s in (-1, 1):
                    tb.box_mm((x - 0.05, s * 0.82 - 0.05, 0), (x + 0.05, s * 0.82 + 0.05, RZ - 0.18), M['frame'])
        tb.finish(col)

    # --- straightening press: bed, gantry on rails (X), carriage (Y), ram (Z) ---
    pc = sum(PRESS) / 2
    bed = pb.Part("BR_PressBed", pivot=(pc, 0, 0))
    bed.box_mm((PRESS[0], -0.85, 0), (PRESS[1], 0.85, RZ - 0.01), M['steel'])
    for s in (-1, 1):
        bed.box_mm((PRESS[0] - 0.4, s * 1.25 - 0.1, 0), (PRESS[1] + 0.4, s * 1.25 + 0.1, 0.35), M['grey'])  # gantry rails
    bed.finish(col)
    gx = pc - 0.4
    gt = pb.Part("BR_PressGantry", pivot=(gx, 0, 0.35))
    for s in (-1, 1):
        gt.box_mm((gx - 0.25, s * 1.25 - 0.15, 0.35), (gx + 0.25, s * 1.25 + 0.15, 2.6), M['frame'])
    gt.box_mm((gx - 0.25, -1.4, 2.6), (gx + 0.25, 1.4, 3.0), M['frame'])
    gt.finish(col)
    cy = 0.2
    cr = pb.Part("BR_PressCarriage", pivot=(gx, cy, 2.6))
    cr.box((0.6, 0.5, 0.6), (gx, cy, 2.5), M['yellow'])
    cr.finish(col)
    ram = pb.Part("BR_PressRam", pivot=(gx, cy, RZ + 0.25))
    ram.cyl_between((gx, cy, RZ + 0.25), (gx, cy, 2.2), 0.08, M['hydraulic'])
    ram.cyl(0.18, 0.08, (gx, cy, RZ + 0.25), M['grey'], seg=20)
    ram.finish(col)
    # carriage rides on the gantry, ram rides on the carriage
    for child, parent in (("BR_PressCarriage", "BR_PressGantry"), ("BR_PressRam", "BR_PressCarriage")):
        child = bpy.data.objects[child]
        mw = child.matrix_world.copy()
        child.parent = bpy.data.objects[parent]
        child.matrix_world = mw

    # --- brush polisher: housing, top and bottom brush rolls, motors ---
    bc = sum(BRUSH) / 2
    hs = pb.Part("BR_BrushHousing", pivot=(bc, 0, 0))
    hs.box_mm((BRUSH[0], -1.0, RZ + 0.12), (BRUSH[1], 1.0, 2.0), M['cabinet'])
    hs.box_mm((BRUSH[0], -1.0, 0), (BRUSH[1], -0.92, RZ - 0.1), M['cabinet'])
    hs.box_mm((BRUSH[0], 0.92, 0), (BRUSH[1], 1.0, RZ - 0.1), M['cabinet'])
    hs.cyl(0.2, 1.0, (bc, 0, 2.5), M['steel'], seg=16)                  # dust extraction
    hs.finish(col)
    for nm, x, z in (("Top", bc - 0.35, RZ + 0.004 + 0.16), ("Bottom", bc + 0.35, RZ - 0.16)):
        br = pb.Part(f"BR_BrushRoll_{nm}", pivot=(x, 0, z))
        br.cyl(0.16, 1.30, (x, 0, z), M['brush'], rot=(90, 0, 0), seg=20)
        br.cyl(0.04, 1.80, (x, 0, z), M['grey'], rot=(90, 0, 0), seg=10)
        br.finish(col)
    mt = pb.Part("BR_BrushMotors", pivot=(bc, -1.2, 0))
    for x, z in ((bc - 0.35, RZ + 0.164), (bc + 0.35, RZ - 0.16)):
        mt.cyl(0.15, 0.45, (x, -1.25, z), M['frame'], rot=(90, 0, 0), seg=16)
    mt.box_mm((bc - 0.6, -1.5, 0), (bc + 0.6, -1.0, RZ - 0.35), M['frame'])
    mt.finish(col)

    # --- contact grinders over both hanger-bar ends ---
    gf = pb.Part("BR_GrinderFrame", pivot=(GRIND_X, 0, 0))
    for s in (-1, 1):
        gf.box_mm((GRIND_X - 0.1, s * 1.05 - 0.1, 0), (GRIND_X + 0.1, s * 1.05 + 0.1, 1.85), M['frame'])
        gf.box_mm((GRIND_X - 0.1, min(s * 0.55, s * 1.15), 1.75), (GRIND_X + 0.1, max(s * 0.55, s * 1.15), 1.85), M['frame'])
    gf.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        y = s * 0.60
        gh = pb.Part(f"BR_ContactGrinder_{side}", pivot=(GRIND_X, y, RZ + 0.05))
        gh.cyl(0.10, 0.03, (GRIND_X, y, RZ + 0.06), M['grey'], seg=20)
        gh.cyl(0.07, 0.25, (GRIND_X, y, RZ + 0.22), M['frame'], seg=14)
        gh.finish(col)
        ac.hyd_cylinder(f"BR_GrinderCyl_{side}", (GRIND_X, y, 1.75), (GRIND_X, y, RZ + 0.35), col, M, r=0.04)

    # --- edge-strip station: press bars along both edges, strip reels, bench ---
    es = pb.Part("BR_EdgeStation", pivot=(EDGE_X, 0, 0))
    for s in (-1, 1):
        for dx in (-0.6, 0.6):
            es.box_mm((EDGE_X + dx - 0.08, s * 1.1 - 0.08, 0), (EDGE_X + dx + 0.08, s * 1.1 + 0.08, RZ + 0.55), M['frame'])
        es.box_mm((EDGE_X - 0.7, s * 1.1 - 0.08, RZ + 0.45), (EDGE_X + 0.7, s * 1.1 + 0.08, RZ + 0.55), M['frame'])
        es.cyl(0.30, 0.08, (EDGE_X - 1.0, s * 1.45, 1.2), M['plastic'], rot=(90, 0, 0), seg=24)   # edge-strip reel
        es.box((0.1, 0.1, 1.2), (EDGE_X - 1.0, s * 1.45, 0.6), M['frame'])
    es.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        eb = pb.Part(f"BR_EdgePress_{side}", pivot=(EDGE_X, s * 0.62, RZ + 0.02))
        eb.box((ac.BLADE_H - 0.1, 0.06, 0.08), (EDGE_X, s * 0.60, RZ + 0.03), M['grey'])
        for dx in (-0.45, 0.0, 0.45):
            eb.box((0.08, 0.40, 0.06), (EDGE_X + dx, s * 0.82, RZ + 0.10), M['steel'])
        eb.finish(col)

    # --- guards and dressing ---
    gd = pb.Part("BR_Guards", pivot=(0, 0, 0))
    ac.guard_fence(gd, (PRESS[0] - 0.6, -1.7, 0), (GRIND_X + 0.5, -1.7, 0), M)
    ac.guard_fence(gd, (PRESS[0] - 0.6, 1.7, 0), (GRIND_X + 0.5, 1.7, 0), M)
    gd.finish(col)
    dr = pb.Part("BR_Dressing", pivot=(0, 0, 0))
    ac.hpu(dr, (12.8, 2.6, 0), M)
    ac.cabinet(dr, (16.0, 2.3, 0), M, size=(2.4, 0.6, 2.1))
    dr.box_mm((19.0, -2.4, 0), (21.0, -1.6, 0.9), M['steel'])            # operator bench
    dr.box_mm((19.0, -2.4, 0.9), (21.0, -1.6, 0.94), M['grey'])
    dr.finish(col)

    # --- REF: rack loads, plates on the chains and at each flat station ---
    r = pb.Part("REF_Blanks", pivot=(0, 0, 0))
    L = RACK_N * ac.PITCH
    for i in range(RACK_N):
        ac.add_cathode(r, RACK_IN_X - L / 2 + 0.05 + i * ac.PITCH, RACK_Z, M, deposit=False)
        if i < 12:
            ac.add_cathode(r, RACK_OUT_X - L / 2 + 0.05 + i * ac.PITCH, RACK_Z, M, deposit=False)
    for x in (4.2, 5.2, 6.0, 7.0):
        ac.add_cathode(r, x, Z, M, deposit=False)
    add_flat_blank(r, PRESS[0] + 0.5, M)
    add_flat_blank(r, BRUSH[0] - 0.3, M)
    add_flat_blank(r, GRIND_X - ac.BLADE_H - 0.01, M)
    add_flat_blank(r, EDGE_X - ac.BLADE_H / 2, M)
    for x in (23.0, 24.5):
        ac.add_cathode(r, x, Z, M, deposit=False)
    r.finish(ref)
    ac.floor_ref(ref, -2, 30.5, -4, 4)


def readme(col):
    rows = pb.pivot_table([col.name])
    return f"""# SM_CathodeBlankRepairLine - permanent cathode blank repair and straightening line

Workshop line for stainless cathode blanks that the stripping machine's vision system flags.
Blanks arrive in transport racks, are scanned for flatness, laid flat, straightened in a gantry
press, brush-polished, have their hanger-bar contacts ground clean and their edge strips
replaced, then stand back up and go into an outgoing rack.

**Own design.** The work list (polishing, contact cleaning, straightening, flattening, edge-strip
replacement, machine vision, special racks) is sourced from Metso's Boliden Pori case study. The
layout and every size are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Blanks move along +X.
- Footprint: x -0.3 to 29.3, y -2.4 to 2.9 (about 29.6 x 5.3 m); monorails reach 4.75 m high.
- Infeed: forklift sets BR_TransportRack_In at x = {RACK_IN_X}, hanger-bar seat z = {RACK_Z} m,
  {RACK_N} blanks at {ac.PITCH * 1000:.0f} mm pitch.
- Outfeed: BR_TransportRack_Out at x = {RACK_OUT_X}, same rack. The racks are exported as their
  own parts, so they can also be used as props on a truck or in the tankhouse.
- Chains: hanger-bar seat z = {Z} m. Flat work height (roller top) z = {RZ:.3f} m.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| BR_HoistIn/Out_Trolley | Travels along X on the monorail | see table |
| BR_HoistIn/Out_Gripper | Moves along Z (down to the rack seat, up to clear) and rides with the trolley | see table |
| BR_ChainIn/Out _L/R_Chain, sprockets | Chain loops along +X | see table |
| BR_TiltIn | Rotation Y 0° (upright, drawn) to +90° lays the blank flat toward +X | hinge ({TILT_IN}, 0, {RZ:.3f}) |
| BR_TiltUp | Drawn flat (rotation Y = +90°); rotate to 0° to stand the blank up onto the out-chain | hinge ({TILT_UP}, 0, {RZ:.3f}) |
| BR_PressGantry | Travels along X on its rails | ({sum(PRESS) / 2 - 0.4:.2f}, 0, 0.35) |
| BR_PressCarriage | Travels along Y on the gantry beam; parented to the gantry | see table |
| BR_PressRam | Moves down onto the blade; parented to the carriage | see table |
| BR_BrushRoll_Top/Bottom | Spin about Y (counter-rotating) | roll axes |
| BR_BrushRolls_Roller_NN and other _Roller_NN | Spin about Y | roller axes |
| BR_ContactGrinder_L/R | Spin about Z and move down 0.05 m onto the hanger-bar contact | see table |
| BR_EdgePress_L/R | Slide inward along Y to press new edge strips on | see table |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

{ac.UNREAL_NOTE}
## Dimensions

| Item | Value | Status |
|---|---|---|
| Work list | polishing, contact cleaning, straightening, flattening, edge-strip replacement | Sourced (Metso, Boliden Pori) |
| Fleet | 28,000 plates; ~300/week sent for checks; plate life ≥10 years | Sourced (same) |
| Blade | {ac.BLADE_W} x {ac.BLADE_H} m x {ac.BLADE_T * 1000:.2f} mm | Thickness sourced, size matches SM_PermanentCathode |
| Rack of {RACK_N}, press gantry 2.8 m wide, brush rolls Ø0.32 m, work height {RZ:.2f} m | | Own design |

Source: Metso case study, "Maintained cathodes ensure refinery's cost-efficiency"
(https://www.metso.com/insights/case-studies/mining-and-metals/maintained-cathodes-ensure-refinerys-cost-efficiency/).

## Files

- SM_CathodeBlankRepairLine.blend / .fbx (REF blanks, floor and figure not exported)
- Preview_Overview.png, Preview_PressBrush.png, Preview_Racks.png
"""


VIEWS = [
    ("Preview_Overview.png", (-3, -12, 9), (14, 0, 0.0), 24),
    ("Preview_PressBrush.png", (10.0, -4.5, 3.2), (14.5, 0, 0.9), 28, ("Guards", "BrushHousing", "Dressing")),
    ("Preview_Racks.png", (-2.5, -5.0, 3.5), (3.0, 0, 1.6), 30),
]

if __name__ == "__main__":
    ac.run(ASSET, NAME, build, readme, VIEWS)
