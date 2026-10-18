"""
build_liberator_cells.py - SM_LiberatorCells (decopperizing cells with hoods, arsine exhaust,
lead anodes, feed/product tanks, own rectifier and a small overhead crane).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_liberator_cells.py

Tankhouse coordinates. Annex east of the hall: x 64..82, y -10..4. One row of 8 cells (the
same SM_ElectrolyticCell shells as the main tankhouse) in a pit, each under an FRP hood that
exhausts to a scrubber, fan and stack outside the east wall.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_LiberatorCells"
OUT = os.path.join(L.MESHES, "LiberatorCells")

ANNEX = (64.0, 82.0, -10.0, 4.0)
ANNEX_H = 9.0
N_CELLS = 8
ROW_Y = -3.0
ROW_X0 = 66.2                                   # west end of the row
PIT = (65.6, 77.6, -6.0, 0.0, -1.8)            # x0, x1, y0, y1, floor z
HOOD_TOP = 2.0
DUCT_Z, DUCT_R = 3.2, 0.30
SCRUB = (85.5, -3.0)
FAN = (85.5, 0.8)
STACK = (85.5, 3.2)
STACK_TOP = 20.0
CRANE_RAIL_Z = 6.5
CRANE_RAIL_Y = (-9.0, 3.0)
TANKS = [(67.5, 2.0), (71.0, 2.0)]
LEAD_W, LEAD_H, LEAD_T = 0.96, 0.98, 0.012


def cell_x(n):
    return ROW_X0 + L.CELL_PITCH / 2 + L.CELL_PITCH * n


def shell(m, col):
    x0, x1, y0, y1 = ANNEX
    s = pb.Part("LC_AnnexShell")
    for xa, xb, ya, yb in ((x0, x1, y0, y0 + 0.2), (x0, x1, y1 - 0.2, y1), (x1 - 0.2, x1, y0, y1)):
        s.box_mm((xa, ya, 0.0), (xb, yb, ANNEX_H), m["cladding"])
    # west wall is the hall's east wall; only close the strip above the hall eaves line
    s.box_mm((x0 - 0.3, y0 - 0.3, ANNEX_H), (x1 + 0.3, y1 + 0.3, ANNEX_H + 0.3), m["roof"])
    s.box_mm((x1 - 0.25, -1.5, 0.0), (x1 + 0.02, 1.5, 4.0), m["blue"])           # roller door (closed)
    return s.finish(col)


def floor_pit(m, col):
    """Annex floor with the cell pit, cell support beams and a drain launder."""
    px0, px1, py0, py1, pz = PIT
    x0, x1, y0, y1 = ANNEX
    f = pb.Part("LC_FloorPit")
    t = 0.3
    f.box_mm((x0, y0, -t), (x1, py0, 0.0), m["floor"])
    f.box_mm((x0, py1, -t), (x1, y1, 0.0), m["floor"])
    f.box_mm((x0, py0, -t), (px0, py1, 0.0), m["floor"])
    f.box_mm((px1, py0, -t), (x1, py1, 0.0), m["floor"])
    f.box_mm((px0, py0, pz - 0.3), (px1, py1, pz), m["floor"])
    for xa, xb, ya, yb in ((px0, px1, py0, py0 + 0.25), (px0, px1, py1 - 0.25, py1),
                           (px0, px0 + 0.25, py0, py1), (px1 - 0.25, px1, py0, py1)):
        f.box_mm((xa, ya, pz), (xb, yb, -t), m["concrete"])
    beam_top = L.CELL_BOTTOM_Z - 0.03
    for s in (-1, 1):
        y = ROW_Y + s * 2.2
        f.box_mm((ROW_X0 - 0.3, y - 0.25, beam_top - 0.5), (ROW_X0 + N_CELLS * L.CELL_PITCH + 0.3, y + 0.25, beam_top),
                 m["concrete"])
        for k in range(4):
            x = ROW_X0 + k * N_CELLS * L.CELL_PITCH / 3
            f.box_mm((x - 0.2, y - 0.2, pz), (x + 0.2, y + 0.2, beam_top - 0.5), m["concrete"])
    # overflow launder along the row's +Y side (under the cells' drain flanges)
    yl = ROW_Y + 2.65
    f.box_mm((ROW_X0, yl - 0.25, -1.55), (ROW_X0 + N_CELLS * L.CELL_PITCH, yl + 0.25, -1.50), m["frp"])
    for s in (-1, 1):
        f.box_mm((ROW_X0, yl + s * 0.25 - 0.02, -1.50), (ROW_X0 + N_CELLS * L.CELL_PITCH, yl + s * 0.25 + 0.02, -1.15),
                 m["frp"])
    # feed header under the feed flanges
    yf = ROW_Y - 2.65
    f.cyl_between((ROW_X0 - 0.5, yf, -1.3), (ROW_X0 + N_CELLS * L.CELL_PITCH, yf, -1.3), 0.06, m["frp"], seg=12)
    for n in range(N_CELLS):
        f.cyl_between((cell_x(n), yf, -1.3), (cell_x(n), yf, -1.025), 0.03, m["frp"], seg=8)
    # end supports and end bars at both row ends
    hy = L.CELL_OUT_L / 2 - 0.03
    xe = ROW_X0 + N_CELLS * L.CELL_PITCH
    for xa, xb, xbar in ((ROW_X0 - 0.30, ROW_X0 + 0.02, ROW_X0), (xe - 0.02, xe + 0.30, None)):
        f.box_mm((xa, ROW_Y - hy, L.CELL_BOTTOM_Z), (xb, ROW_Y + hy, L.RIM_Z), m["polymer"])
        f.box_mm((xa, ROW_Y - hy, L.RIM_Z), (xb + (0.08 if xbar else 0.0), ROW_Y + hy, L.CAP_TOP), m["capping"])
        if xbar is not None:
            f.box_mm((xbar - 0.025, ROW_Y - hy, L.CAP_TOP), (xbar + 0.025, ROW_Y + hy, L.SEAT_Z), m["copper"])
    # handrail around the pit edge where no cell stands
    pb.handrail(f, (px0, py0, 0.0), (px1, py0, 0.0), m["yellow"])
    pb.handrail(f, (px0, py1, 0.0), (px1, py1, 0.0), m["yellow"])
    return f.finish(col)


def hoods(m, col):
    """One removable FRP hood per cell, pivot at the lifting lug on top."""
    obs = []
    hx, hy = L.CELL_PITCH / 2 - 0.02, L.CELL_OUT_L / 2 + 0.05
    for n in range(N_CELLS):
        x = cell_x(n)
        h = pb.Part(f"LC_Hood_{n + 1}", pivot=(x, ROW_Y, HOOD_TOP + 0.25))
        z0 = L.RIM_Z
        for s in (-1, 1):   # long sides
            y0, y1 = sorted((ROW_Y + s * hy, ROW_Y + s * (hy - 0.02)))
            h.box_mm((x - hx, y0, z0), (x + hx, y1, HOOD_TOP - 0.3), m["frp"])
        for s in (-1, 1):   # ends (over the capping boards)
            x0, x1 = sorted((x + s * hx, x + s * (hx - 0.02)))
            h.box_mm((x0, ROW_Y - hy, L.SEAT_Z + 0.15), (x1, ROW_Y + hy, HOOD_TOP - 0.3), m["frp"])
        # pitched top
        h.poly_prism([(ROW_Y - hy, HOOD_TOP - 0.3), (ROW_Y + hy, HOOD_TOP - 0.3), (ROW_Y + 0.3, HOOD_TOP),
                      (ROW_Y - 0.3, HOOD_TOP)], x - hx, x + hx, m["frp"], plane='YZ')
        h.cyl_between((x, ROW_Y, HOOD_TOP - 0.05), (x, ROW_Y, DUCT_Z - DUCT_R), 0.1, m["frp"], seg=12)  # branch
        h.box((0.12, 0.3, 0.2), (x, ROW_Y + 0.6, HOOD_TOP), m["yellow"])                                 # lifting lug
        h.box((0.12, 0.3, 0.2), (x, ROW_Y - 0.6, HOOD_TOP), m["yellow"])
        obs.append(h.finish(col))
    return obs


def exhaust(m, col):
    """Exhaust header over the row, scrubber tower, fan and stack outside the east wall."""
    p = pb.Part("LC_Exhaust")
    flanges = []
    xa, xb = ROW_X0 - 0.4, ANNEX[1] + 0.5
    p.cyl_between((xa, ROW_Y, DUCT_Z), (xb, ROW_Y, DUCT_Z), DUCT_R, m["frp"], seg=20)
    p.sphere(DUCT_R, (xa, ROW_Y, DUCT_Z), m["frp"], seg=16)
    p.cyl_between((xb, ROW_Y, DUCT_Z), (SCRUB[0] - 1.0, ROW_Y, DUCT_Z), DUCT_R, m["frp"], seg=20)
    for n in range(0, N_CELLS, 2):    # hangers
        x = cell_x(n) + 0.66
        p.box_mm((x - 0.03, ROW_Y - 0.03, DUCT_Z + DUCT_R), (x + 0.03, ROW_Y + 0.03, ANNEX_H), m["steel"])
    sx, sy = SCRUB
    p.cyl(1.0, 6.0, (sx, sy, 3.3), m["frp"], seg=28)
    p.sphere(1.0, (sx, sy, 6.3), m["frp"], seg=20)
    p.cyl(1.2, 0.3, (sx, sy, 0.15), m["concrete"], seg=28)
    p.cyl_between((sx, sy, 6.8), (sx, sy, 7.4), 0.3, m["frp"], seg=16)
    pipe = [(sx, sy, 7.4), (sx, FAN[1], 7.4), (FAN[0], FAN[1], 2.0)]
    p.cyl_between(pipe[0], pipe[1], 0.3, m["frp"], seg=16)
    p.sphere(0.3, pipe[1], m["frp"], seg=12)
    p.cyl_between(pipe[1], (FAN[0], FAN[1], 2.3), 0.3, m["frp"], seg=16)
    p.cyl(0.9, 0.6, (FAN[0], FAN[1], 1.6), m["frp"], rot=(90, 0, 0), seg=24)                  # fan casing
    p.box_mm((FAN[0] - 0.8, FAN[1] - 1.0, 0.0), (FAN[0] + 0.8, FAN[1] + 1.4, 0.7), m["concrete"])
    p.cyl(0.35, 0.7, (FAN[0], FAN[1] - 0.8, 1.6), m["blue"], rot=(90, 0, 0), seg=16)           # motor
    p.cyl_between((FAN[0], FAN[1] + 0.3, 1.6), (STACK[0], STACK[1], 1.6), 0.3, m["frp"], seg=16)
    p.cyl(0.35, STACK_TOP, (STACK[0], STACK[1], STACK_TOP / 2), m["frp"], seg=20)
    for k in range(3):   # stack guy brackets
        p.cyl(0.42, 0.1, (STACK[0], STACK[1], 6.0 + 5.0 * k), m["steel"], seg=20)
    # scrubber liquor recirculation pump
    p.box_mm((sx - 1.8, sy - 0.4, 0.0), (sx - 1.2, sy + 0.4, 0.6), m["blue"])
    pb.flange(p, (sx, sy - 1.0, 0.8), (90, 0, 0), 0.05, m["frp"], flanges, "Scrubber bleed (to effluent treatment)")
    pb.ladder(p, (sx + 1.1, sy, 0.0), 6.5, m["yellow"], facing=90)
    return p.finish(col), flanges


def tanks_rectifier(m, col):
    """Feed and product tanks with pumps, liberator rectifier and DC bus."""
    p = pb.Part("LC_TanksRectifier")
    flanges = []
    for x, y in TANKS:
        p.cyl(1.1, 2.6, (x, y, 1.3 + 0.15), m["frp"], seg=28)
        p.cyl(1.25, 0.15, (x, y, 0.075), m["concrete"], seg=28)
        p.cyl(1.12, 0.06, (x, y, 2.78), m["frp"], seg=28)
        p.box((0.4, 0.6, 0.5), (x + 1.6, y, 0.4), m["blue"])                                     # pump
        p.cyl_between((x + 1.1, y, 0.35), (x + 1.4, y, 0.35), 0.06, m["frp"], seg=10)
    pb.flange(p, (ANNEX[0] + 0.3, TANKS[0][1], 2.2), (0, 90, 0), 0.05, m["frp"], flanges,
              "Bleed electrolyte in (from SM_ElectrolyteCirculation)")
    p.cyl_between((ANNEX[0] + 0.3, TANKS[0][1], 2.2), (TANKS[0][0] - 1.1, TANKS[0][1], 2.2), 0.05, m["frp"], seg=10)
    # feed pump to the cell feed header
    pipe_pts = [(TANKS[0][0] + 1.8, TANKS[0][1], 0.4), (TANKS[0][0] + 1.8, 0.4, 0.4), (ROW_X0 - 0.5, 0.4, 0.4),
                (ROW_X0 - 0.5, 0.4, -1.3), (ROW_X0 - 0.5, ROW_Y - 2.65, -1.3)]
    for a, b in zip(pipe_pts[:-1], pipe_pts[1:]):
        p.cyl_between(a, b, 0.06, m["frp"], seg=10)
    # launder outlet back to the product tank (pumped from the pit sump)
    p.box_mm((ROW_X0 + N_CELLS * L.CELL_PITCH - 0.6, -0.6, PIT[4]), (ROW_X0 + N_CELLS * L.CELL_PITCH, 0.0, PIT[4] + 0.8),
             m["blue"])
    pb.flange(p, (TANKS[1][0] + 1.8, TANKS[1][1] + 1.2, 0.8), (90, 0, 0), 0.05, m["frp"], flanges,
              "Decopperized solution out (to the nickel sulfate / evaporator plant)")
    # rectifier cubicles, small transformer and DC bus to both row ends
    rx, ry = 77.0, 2.6
    for k in range(3):
        p.box_mm((rx + k * 0.95, ry - 0.6, 0.0), (rx + k * 0.95 + 0.9, ry + 0.6, 2.3), m["cabinet"])
    p.box_mm((rx + 3.1, ry - 0.9, 0.0), (rx + 4.6, ry + 0.9, 2.2), m["grey"])
    xe = ROW_X0 + N_CELLS * L.CELL_PITCH
    zb = 2.6
    for x_end, xx in ((ROW_X0 - 0.2, rx + 0.4), (xe + 0.2, rx + 1.4)):
        p.box_mm((min(x_end, xx) - 0.05, 1.0 - 0.05, zb - 0.1), (max(x_end, xx) + 0.05, 1.0 + 0.05, zb + 0.1),
                 m["copper"])
        p.box_mm((xx - 0.05, 1.0 - 0.05, 2.3), (xx + 0.05, 1.0 + 0.05, zb + 0.1), m["copper"])
        p.box_mm((x_end - 0.05, 1.0 - 0.05, zb - 0.1), (x_end + 0.05, ROW_Y + 2.4, zb + 0.1), m["copper"])
        p.box_mm((x_end - 0.05, ROW_Y + 2.3, L.SEAT_Z - 0.4), (x_end + 0.05, ROW_Y + 2.4, zb + 0.1), m["copper"])
    return p.finish(col), flanges


def crane(m, col):
    """Single-girder 5 t crane over the liberator row, with a lifting beam for hoods and loads."""
    obs = []
    xb = cell_x(3)
    ya, yb = CRANE_RAIL_Y
    rails = pb.Part("LC_CraneRunway")
    for y in (ya, yb):
        rails.box_mm((ANNEX[0] + 0.3, y - 0.15, CRANE_RAIL_Z - 0.6), (ANNEX[1] - 0.3, y + 0.15, CRANE_RAIL_Z), m["steel"])
        for k in range(4):
            x = ANNEX[0] + 0.5 + k * (ANNEX[1] - ANNEX[0] - 1.0) / 3
            rails.box_mm((x - 0.15, y - 0.15, 0.0), (x + 0.15, y + 0.15, CRANE_RAIL_Z - 0.6), m["steel"])
    obs.append(rails.finish(col))
    b = pb.Part("LC_CraneBridge", pivot=(xb, (ya + yb) / 2, CRANE_RAIL_Z))
    b.box_mm((xb - 0.3, ya - 0.2, CRANE_RAIL_Z + 0.25), (xb + 0.3, yb + 0.2, CRANE_RAIL_Z + 1.05), m["crane"])
    for y in (ya, yb):
        b.box_mm((xb - 1.2, y - 0.2, CRANE_RAIL_Z), (xb + 1.2, y + 0.2, CRANE_RAIL_Z + 0.45), m["crane"])
    obs.append(b.finish(col))
    h = pb.Part("LC_CraneHoist", pivot=(xb, ROW_Y, CRANE_RAIL_Z + 0.25))
    h.box_mm((xb - 0.4, ROW_Y - 0.6, CRANE_RAIL_Z - 0.55), (xb + 0.4, ROW_Y + 0.6, CRANE_RAIL_Z + 0.2), m["blue"])
    h.cyl_between((xb, ROW_Y, CRANE_RAIL_Z - 0.55), (xb, ROW_Y, 3.9), 0.012, m["steel"], seg=6)
    h.box_mm((xb - 0.08, ROW_Y - 2.6, 3.7), (xb + 0.08, ROW_Y + 2.6, 3.9), m["yellow"])      # lifting beam
    for s in (-1, 1):
        h.cyl_between((xb, ROW_Y + s * 2.5, 3.7), (xb, ROW_Y + s * 2.5, 3.3), 0.012, m["steel"], seg=6)
    obs.append(h.finish(col))
    return obs


def lead_anode(m, col):
    """Insoluble lead alloy anode, origin at the header bar underside centre (= seat point)."""
    p = pb.Part("LC_LeadAnode", pivot=(0.0, 0.0, 0.0))
    p.box_mm((-LEAD_W / 2, -LEAD_T / 2, -LEAD_H), (LEAD_W / 2, LEAD_T / 2, -0.02), m["lead"])
    p.box_mm((-L.HANGER_L / 2, -0.015, 0.0), (L.HANGER_L / 2, 0.015, 0.04), m["copper"])        # header bar
    p.box_mm((-LEAD_W / 2, -0.02, -0.06), (LEAD_W / 2, 0.02, 0.0), m["lead"])                     # lead-encased joint
    for s in (-1, 1):   # insulator spacers on the side edges
        p.box((0.02, 0.05, 0.08), (s * (LEAD_W / 2 + 0.005), 0.0, -0.5), m["pp"])
    ob = p.finish(col)
    ob.location = (0.0, 0.0, 0.0)
    return ob


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")
    sh = shell(m, col)
    floor_pit(m, col)
    hds = hoods(m, col)
    _, f1 = exhaust(m, col)
    _, f2 = tanks_rectifier(m, col)
    crane(m, col)
    anode = lead_anode(m, col)
    return col, sh, hds, anode, f1 + f2


def write_readme(col, flanges):
    rows = pb.pivot_table([col.name])
    fl = "\n".join(f"| {n} | {p} |" for n, p in flanges)
    cells = "\n".join(f"| {n} | ({cell_x(n):.2f}, {ROW_Y}, 0) |" for n in range(N_CELLS))
    txt = f"""# SM_LiberatorCells

Liberator (decopperizing) cells. A bleed stream of tankhouse electrolyte is electrowon here with
insoluble lead anodes to take out copper, and then arsenic, antimony and bismuth before the
solution goes to the nickel sulfate plant. The last stage can release **arsine** gas, so every
cell has an FRP hood that exhausts through a scrubber, fan and stack.

- **Annex:** east of the hall, x {ANNEX[0]} to {ANNEX[1]}, y {ANNEX[2]} to {ANNEX[3]}, {ANNEX_H} m high, sharing
  the hall's east wall. Scrubber, fan and 20 m stack stand outside the east wall (x about 84–87).
- **Cells:** one row of {N_CELLS} cells. The shells are SM_ElectrolyticCell instances (not repeated
  in this FBX). They stand in a pit (floor z {PIT[4]}) on support beams, so their rims are 0.8 m above
  the annex floor like in the main hall.
- **Electrodes:** 45 lead anodes (LC_LeadAnode, exported here) and 46 permanent cathodes
  (SM_PermanentCathode) per cell, same positions as in the main cells.
- **Hoods:** 8 separate hoods (LC_Hood_1..8), each lifted off by the annex crane for harvesting.
- **Supply:** feed tank (bleed in), product tank (decopperized solution out), pumps, a small
  rectifier on its own DC circuit, and a 5 t single-girder crane with a lifting beam.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates. Files: `{NAME}.blend`, `{NAME}.fbx`
(FBX_SCALE_NONE). Previews: `Preview_Exterior.png`, `Preview_Cells.png` (shell hidden, one hood
lifted).

## Cell placement (SM_ElectrolyticCell instances)

| Cell | Location (tankhouse), no rotation |
|---|---|
{cells}

Lead anode j: LC_LeadAnode at (cell x, anode_y(j), {L.SEAT_Z}) with no rotation (header bar along X).
Cathode k: SM_PermanentCathode at (cell x, cathode_y(k), {L.SEAT_Z}). anode_y / cathode_y as in
ElectrolyticCell/README.md; use the even pattern for cells 0, 2, 4, 6.

## Connection points

| Point | Position (tankhouse) |
|---|---|
{fl}

## Parts and pivots

| Object | Use |
|---|---|
| LC_AnnexShell | walls and roof; hide for cutaways |
| LC_FloorPit | floor, pit, beams, launder, feed header, end supports and end bar |
| LC_Hood_1..8 | lift +Z at the pivot (lifting lugs) to remove |
| LC_Exhaust | header, branch ducts (on the hoods), scrubber, fan, stack |
| LC_TanksRectifier | tanks, pumps, rectifier, DC bus |
| LC_CraneRunway | static |
| LC_CraneBridge | translate X, x {ANNEX[0] + 2:.0f} to {ANNEX[1] - 2:.0f} |
| LC_CraneHoist | child of the bridge, translate Y between the rails; hook block and lifting beam are part of it (scale the rope in Unreal or split if needed) |
| LC_LeadAnode | instance per anode position, origin at the header bar underside centre |

| Object | Pivot |
|---|---|
{rows}

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Liberator cells look like the main cells and have hoods for arsine | | Sourced (research file §9, WO2017191458A1; arsine risk in research companion §9) |
| 8 cells, same shells as the main cells, lead anodes 0.96 × 0.98 m × 12 mm | | Estimated |
| Hood, duct, scrubber, fan and stack sizes, annex layout, 5 t crane | | Estimated / own design |
| Bleed 0.1–0.5 m³ per t Cu | | Sourced (research companion §8) |

Sources: /mnt/project-files/copper_refinery_equipment.md §9; research companion §9 ([S5]);
WO2017191458A1, WO2017144912A1.
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(sh, hds, anode):
    ref = pb.collection("REF")
    bld = L.load_objects(L.asset_path("Tankhouse", "SM_TankhouseBuilding"),
                         ["TH_Frame", "TH_Walls", "TH_Roof", "TH_OperatingFloor"])
    for o in bld:
        ref.objects.link(o)
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"), ["CA_Plate"])
    L.instance_collection("SRC_Parts", cell + cath)
    loaded = []
    for odd in (0, 1):
        c = L.loaded_cell_collection(cell, anode, cath, odd, f"LibCell_{odd}")
        for o in c.objects:   # lead anodes hang from their header bar: no lug rotation/offset
            if o.data == anode.data:
                o.rotation_euler = (0, 0, 0)
                o.location = (0.0, o.location.y - L.ANODE_ORIGIN_DY, L.SEAT_Z)
        loaded.append(c)
    for n in range(N_CELLS):
        L.place_instance(ref, loaded[n % 2], (cell_x(n), ROW_Y, 0), name=f"REF_LibCell{n}")
    pb.ref_ground(ref, (40, -40, 110, 40), [(L.BLD_X0, -L.BLD_Y, ANNEX[0], L.BLD_Y), (ANNEX[0], ANNEX[2], ANNEX[1], ANNEX[3])], z=-0.31)
    pb.ref_human(ref, (72.0, 1.0, 0.0))
    pb.setup_render(res=(1600, 900), samples=32)
    anode.hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Exterior.png"), (104, -28, 16), (78, -2, 4), lens=30)
    sh.hide_render = True
    by = {o.name: o for o in bld}
    by["TH_Walls"].hide_render = True
    by["TH_Roof"].hide_render = True
    hds[3].location.z += 1.4
    pb.render_view(os.path.join(OUT, "Preview_Cells.png"), (66.0, -12.5, 6.0), (72.0, -2.5, 0.5), lens=26)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, sh, hds, anode, flanges = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, flanges)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview(sh, hds, anode)


main()
