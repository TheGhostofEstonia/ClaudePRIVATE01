"""
build_rectifier_busbar.py - SM_RectifierBusbar (rectifier yard, DC bus, row end bars, crossovers).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_rectifier_busbar.py

Tankhouse coordinates. One DC circuit through all 160 cells in series:
  rectifier (+) -> row D east end, west along D -> crossover to C at the west end,
  east along C -> crossover to B at the east end, west along B -> crossover to A at the
  west end, east along A -> rectifier (-).
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_RectifierBusbar"
OUT = os.path.join(L.MESHES, "RectifierBusbar")

ROW_END_W = 0.0                                     # x of the west end bars
ROW_END_E = L.cell_x(L.CELLS_PER_ROW - 1) + L.CELL_PITCH / 2   # x of cell 39's own bar
BUS_W, BUS_H = 0.175, 0.25                          # 4 bars 250 x 25 mm with 25 mm gaps
OVERHEAD_Z = 3.0                                    # main DC bus height inside the hall
POS_X, NEG_X = 57.0, 58.0                           # main bus runs along the east aisle
HOUSE = (44.0, 60.0, 15.3, 20.5)                    # rectifier house x0, x1, y0, y1
HOUSE_H = 6.0
TRAFO_X = (48.5, 55.5)
TRAFO_Y = 23.5


def bus_run(p, a, b, m, w=BUS_W, h=BUS_H, vertical=False):
    """Bundle of four copper bars between points a and b (axis-aligned run)."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    d = b - a
    if vertical or abs(d.z) > max(abs(d.x), abs(d.y)):
        for i in range(4):
            off = -w / 2 + 0.0125 + i * 0.05
            p.box_mm((a.x - h / 2, a.y + off - 0.0125, min(a.z, b.z)),
                     (a.x + h / 2, a.y + off + 0.0125, max(a.z, b.z)), m)
        return
    along_x = abs(d.x) >= abs(d.y)
    for i in range(4):
        off = -w / 2 + 0.0125 + i * 0.05
        if along_x:
            p.box_mm((min(a.x, b.x), a.y + off - 0.0125, a.z - h / 2), (max(a.x, b.x), a.y + off + 0.0125, a.z + h / 2), m)
        else:
            p.box_mm((a.x + off - 0.0125, min(a.y, b.y), a.z - h / 2), (a.x + off + 0.0125, max(a.y, b.y), a.z + h / 2), m)


def insulator_stand(p, x, y, z_top, z_floor, m):
    """Steel post with a porcelain/polymer insulator under a bus run."""
    p.box_mm((x - 0.06, y - 0.06, z_floor), (x + 0.06, y + 0.06, z_top - 0.25), m["steel"])
    p.cyl(0.07, 0.12, (x, y, z_top - 0.19), m["capping"], seg=12)
    p.box_mm((x - 0.15, y - 0.15, z_top - 0.13), (x + 0.15, y + 0.15, z_top - 0.125), m["steel"])


def row_ends(m, col):
    """End supports, end bars and flexible connectors at both ends of every row; crossovers."""
    p = pb.Part("RB_RowEnds")
    zb = L.SEAT_Z - 0.03                      # end bar centre height
    hy = L.CELL_OUT_L / 2 - 0.03
    for ry in L.ROW_Y.values():
        # west end: support block, capping, end bar
        p.box_mm((-0.30, ry - hy, L.CELL_BOTTOM_Z), (0.02, ry + hy, L.RIM_Z), m["polymer"])
        p.box_mm((-0.30, ry - hy, L.RIM_Z), (0.10, ry + hy, L.CAP_TOP), m["capping"])
        p.box_mm((ROW_END_W - 0.025, ry - hy, L.CAP_TOP), (ROW_END_W + 0.025, ry + hy, L.SEAT_Z), m["copper"])
        # east end: support block under the overhang of cell 39's capping board
        p.box_mm((ROW_END_E - 0.02, ry - hy, L.CELL_BOTTOM_Z), (ROW_END_E + 0.30, ry + hy, L.RIM_Z), m["polymer"])
        p.box_mm((ROW_END_E + 0.10, ry - hy, L.RIM_Z), (ROW_END_E + 0.30, ry + hy, L.CAP_TOP), m["capping"])
        # flexible laminated connectors from the end bars down to the end bus (5 per end)
        for x_bar, sgn in ((ROW_END_W, -1), (ROW_END_E, 1)):
            for k in range(5):
                y = ry - 2.0 + k
                p.box_mm((x_bar + sgn * 0.03 - 0.02, y - 0.06, zb - 0.45), (x_bar + sgn * 0.03 + 0.02, y + 0.06,
                         L.SEAT_Z), m["copper"])
    # end bus under each row end, along Y at the connector feet
    z_end = L.SEAT_Z - 0.03 - 0.45 - BUS_H / 2
    for ry in L.ROW_Y.values():
        for x in (ROW_END_W - 0.20, ROW_END_E + 0.20):
            bus_run(p, (x, ry - 2.2, z_end), (x, ry + 2.2, z_end), m["copper"])
    # crossovers: D-C and B-A at the west end, C-B at the east end
    for x, y0, y1 in ((ROW_END_W - 0.20, L.ROW_Y["D"], L.ROW_Y["C"]),
                      (ROW_END_W - 0.20, L.ROW_Y["B"], L.ROW_Y["A"]),
                      (ROW_END_E + 0.20, L.ROW_Y["C"], L.ROW_Y["B"])):
        bus_run(p, (x, min(y0, y1) + 2.2, z_end), (x, max(y0, y1) - 2.2, z_end), m["copper"])
        for k in range(3):
            y = min(y0, y1) + 2.6 + k * ((abs(y1 - y0) - 5.2) / 2)
            insulator_stand(p, x, y, z_end - BUS_H / 2, L.BASEMENT_Z, m)
    for ry in L.ROW_Y.values():
        for x in (ROW_END_W - 0.20, ROW_END_E + 0.20):
            for dy in (-1.6, 1.6):
                insulator_stand(p, x, ry + dy, z_end - BUS_H / 2, L.BASEMENT_Z, m)
    return p.finish(col), z_end


def main_bus(m, col, z_end):
    """Overhead DC bus from the rectifier house to the row D (+) and row A (-) east ends."""
    p = pb.Part("RB_MainBus")
    zo = OVERHEAD_Z
    for x, ry in ((POS_X, L.ROW_Y["D"]), (NEG_X, L.ROW_Y["A"])):
        y_wall = L.BLD_Y + 0.5
        bus_run(p, (x, y_wall, zo), (x, ry, zo), m["copper"])                # along the east aisle
        bus_run(p, (x, ry, zo), (ROW_END_E + 0.20, ry, zo), m["copper"])     # across to the row end
        bus_run(p, (ROW_END_E + 0.20, ry, z_end + BUS_H / 2), (ROW_END_E + 0.20, ry, zo + BUS_H / 2),
                m["copper"], vertical=True)
        # portal supports every ~4 m along the east aisle
        y = ry
        step = 4.0 if y_wall > ry else -4.0
        ys = []
        while (y_wall - y) * step > 0:
            ys.append(y)
            y += step
        for yy in ys + [ry]:
            p.box_mm((x - 0.08, yy - 0.08, 0.0), (x + 0.08, yy + 0.08, zo - BUS_H / 2 - 0.15), m["steel"])
            p.cyl(0.07, 0.12, (x, yy, zo - BUS_H / 2 - 0.08), m["capping"], seg=12)
        for xx in ((x + ROW_END_E) / 2,):
            p.box_mm((xx - 0.08, ry - 0.08, 0.0), (xx + 0.08, ry + 0.08, zo - BUS_H / 2 - 0.15), m["steel"])
            p.cyl(0.07, 0.12, (xx, ry, zo - BUS_H / 2 - 0.08), m["capping"], seg=12)
        # wall penetration sleeve
        p.box_mm((x - 0.25, L.BLD_Y - 0.2, zo - 0.25), (x + 0.25, L.BLD_Y + 0.6, zo + 0.25), m["frp"])
        # into the rectifier house
        bus_run(p, (x, L.BLD_Y + 0.5, zo), (x, HOUSE[2] + 1.6, zo), m["copper"])
    # +/- signs on the supports
    p.box((0.4, 0.02, 0.4), (POS_X, 13.0, zo + 0.5), m["red"])
    p.box((0.4, 0.02, 0.4), (NEG_X, 13.0, zo + 0.5), m["blue"])
    return p.finish(col)


def rectifier_house(m, col):
    """House shell (hide for interior views) and the rectifier equipment inside."""
    x0, x1, y0, y1 = HOUSE
    h = pb.Part("RB_RectifierHouse")
    h.box_mm((x0, y0, -0.3), (x1, y1, 0.0), m["concrete"])
    for xa, xb, ya, yb in ((x0, x1, y0, y0 + 0.2), (x0, x1, y1 - 0.2, y1), (x0, x0 + 0.2, y0, y1), (x1 - 0.2, x1, y0, y1)):
        h.box_mm((xa, ya, 0.0), (xb, yb, HOUSE_H), m["cladding"])
    h.box_mm((x0 - 0.3, y0 - 0.3, HOUSE_H), (x1 + 0.3, y1 + 0.3, HOUSE_H + 0.3), m["roof"])
    for xx in (x0 + 3, x1 - 3):   # roof ventilation fans
        h.cyl(0.6, 0.6, (xx, (y0 + y1) / 2, HOUSE_H + 0.6), m["grey"], seg=16)
    h.box_mm((x0 + 1.0, y1 - 0.25, 0.0), (x0 + 3.0, y1 + 0.02, 2.6), m["blue"])   # door
    house = h.finish(col)

    r = pb.Part("RB_Rectifiers")
    yc = (y0 + y1) / 2 + 0.3
    for k, xs in enumerate((x0 + 2.0, x0 + 8.5)):
        for i in range(6):   # thyristor cubicles
            x = xs + i * 0.95
            r.box_mm((x, yc - 0.7, 0.0), (x + 0.9, yc + 0.7, 2.3), m["cabinet"])
            r.box_mm((x + 0.1, yc - 0.71, 1.4), (x + 0.4, yc - 0.70, 2.0), m["screen"] if i == 0 else m["grey"])
        # water/water cooler skid for the thyristor stacks
        r.box_mm((xs, yc + 1.2, 0.0), (xs + 2.2, yc + 2.2, 1.6), m["blue"])
        r.cyl_between((xs + 0.5, yc + 0.7, 2.0), (xs + 0.5, yc + 1.4, 2.0), 0.05, m["grey"], seg=10)
    # DC isolators and current shunt on the bus inside the house
    for x in (POS_X, NEG_X):
        r.box_mm((x - 0.4, y0 + 0.4, 2.0), (x + 0.4, y0 + 1.4, 3.6), m["cabinet"])
    r.box_mm((x0 + 0.6, y0 + 0.5, 0.0), (x0 + 1.6, y0 + 2.5, 2.2), m["cabinet"])  # control panel
    rect = r.finish(col)
    return house, rect


def transformers(m, col):
    """Two oil-filled rectifier transformers in bunded bays with a firewall, LV bus ducts."""
    t = pb.Part("RB_Transformers")
    flanges = []
    t.box_mm((HOUSE[0], HOUSE[3] + 0.5, -0.2), (HOUSE[1], HOUSE[3] + 6.5, 0.1), m["concrete"])   # bund floor
    for xa in (HOUSE[0], HOUSE[1] - 0.3, (TRAFO_X[0] + TRAFO_X[1]) / 2 - 0.15):  # bund / firewalls
        t.box_mm((xa, HOUSE[3] + 0.5, 0.1), (xa + 0.3, HOUSE[3] + 6.5, 4.5 if xa > HOUSE[0] + 1 and xa < HOUSE[1] - 1 else 0.6),
                 m["concrete"])
    for x in TRAFO_X:
        y = TRAFO_Y
        t.box_mm((x - 2.0, y - 1.3, 0.1), (x + 2.0, y + 1.3, 3.3), m["grey"])           # tank
        for s in (-1, 1):                                                              # radiators
            for i in range(6):
                xx = x - 1.5 + i * 0.6
                t.box_mm((xx - 0.04, y + s * 1.3, 0.6), (xx + 0.04, y + s * 2.1, 3.0), m["grey"])
        t.cyl(0.35, 1.8, (x - 1.0, y, 3.9), m["grey"], rot=(0, 90, 0), seg=16)           # conservator
        t.box((0.2, 0.2, 0.6), (x - 1.0, y, 3.5), m["grey"])
        for i in range(3):                                                             # HV bushings
            t.cyl(0.08, 0.9, (x + 0.6 + i * 0.45, y + 0.6, 3.75), m["capping"], seg=10)
        flanges.append((f"HV cable entry, transformer at x {x}", (x + 1.05, y + 1.3, 0.1)))
        t.box_mm((x + 0.5, y + 1.3, 0.1), (x + 1.6, y + 1.8, 2.0), m["grey"])            # HV cable box
        # LV bus duct from the tank to the rectifier house wall
        t.box_mm((x - 0.4, HOUSE[3], 3.0), (x + 0.4, y - 1.3, 3.6), m["grey"])
        t.box_mm((x - 0.4, y - 1.4, 3.0), (x + 0.4, y - 1.3, 3.6), m["grey"])
    return t.finish(col), flanges


def shorting_frame(m, col):
    """Cell bypass (shorting) frame: clamps across one cell to take it out of the circuit."""
    x, y = L.cell_x(20), L.ROW_Y["B"]                         # modelled over cell B20 (preview)
    p = pb.Part("RB_ShortingFrame", pivot=(x, y, L.SEAT_Z))
    for sy in (-1, 1):
        yy = y + sy * 2.75
        p.box_mm((x - 0.75, yy - 0.06, L.SEAT_Z + 0.25), (x + 0.75, yy + 0.06, L.SEAT_Z + 0.45), m["steel"])
        for sx in (-1, 1):
            p.box_mm((x + sx * 0.66 - 0.05, yy - 0.05, L.SEAT_Z - 0.10), (x + sx * 0.66 + 0.05, yy + 0.05,
                     L.SEAT_Z + 0.25), m["copper"])
    for sx in (-1, 1):
        p.box_mm((x + sx * 0.66 - 0.04, y - 2.8, L.SEAT_Z + 0.15), (x + sx * 0.66 + 0.04, y + 2.8, L.SEAT_Z + 0.25),
                 m["copper"])
    p.box_mm((x - 0.70, y - 0.15, L.SEAT_Z + 0.15), (x + 0.70, y + 0.15, L.SEAT_Z + 0.25), m["copper"])
    p.box((0.3, 0.3, 0.15), (x, y, L.SEAT_Z + 0.55), m["yellow"])     # crane lifting eye block
    return p.finish(col)


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")
    ends, z_end = row_ends(m, col)
    bus = main_bus(m, col, z_end)
    house, rect = rectifier_house(m, col)
    trafo, flanges = transformers(m, col)
    sf = shorting_frame(m, col)
    return col, {"house": house, "bus": bus, "ends": ends, "trafo": trafo, "rect": rect, "sf": sf}, flanges, z_end


def write_readme(col, flanges, z_end):
    rows = pb.pivot_table([col.name])
    fl = "\n".join(f"| {n} | ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}) |" for n, p in flanges)
    cur, cells = 30.0, 4 * L.CELLS_PER_ROW
    v_cells = cells * 0.30
    txt = f"""# SM_RectifierBusbar

DC supply for the tankhouse cells: rectifier transformers, a rectifier house, the main DC bus,
row end bars and the crossovers that link the four rows into one series circuit. Also a cell
shorting (bypass) frame that the crane sets over a cell to take it out of the circuit.

**Current path:** rectifier (+) → row D east end → west along D → crossover D–C (west end) →
east along C → crossover C–B (east end) → west along B → crossover B–A (west end) → east along A →
rectifier (−).

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates (lines up with SM_TankhouseBuilding).
Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE). Previews: `Preview_Yard.png`,
`Preview_RowEnds.png`, `Preview_House.png` (house shell hidden).

## Layout

| Part | Position |
|---|---|
| Rectifier house | x {HOUSE[0]} to {HOUSE[1]}, y {HOUSE[2]} to {HOUSE[3]}, {HOUSE_H} m high, against the hall's north wall |
| Rectifier transformers (2) | centres ({TRAFO_X[0]}, {TRAFO_Y}) and ({TRAFO_X[1]}, {TRAFO_Y}), in a bund with a firewall between them |
| Main DC bus (+) | x {POS_X}, z {OVERHEAD_Z}: from the house through the north wall, south along the east aisle to y {L.ROW_Y['D']}, west to the row D end bus at x {ROW_END_E + 0.2:.2f} |
| Main DC bus (−) | x {NEG_X}, z {OVERHEAD_Z}: same route to y {L.ROW_Y['A']} (row A end) |
| West end bars | x {ROW_END_W} on an end support block, one per row |
| East end | cell 39's own intercell bar at x {ROW_END_E:.2f}, with an end support block under its capping board overhang |
| Row end bus (under each row end) | x {ROW_END_W - 0.2:.2f} (west) and {ROW_END_E + 0.2:.2f} (east), centre z {z_end:.2f}, fed by 5 flexible connectors from the end bar |
| Crossovers | D–C and B–A at x {ROW_END_W - 0.2:.2f}; C–B at x {ROW_END_E + 0.2:.2f}; on insulator stands from the basement floor |

## Connection points

| Point | Position |
|---|---|
{fl}

## Parts and pivots

| Object | Use |
|---|---|
| RB_RowEnds | end supports, end bars, flexible connectors, end bus, crossovers |
| RB_MainBus | overhead DC bus, supports, wall sleeves |
| RB_RectifierHouse | shell; hide for interior views |
| RB_Rectifiers | 2 × 6 thyristor cubicles, cooler skids, DC isolators and shunt, control panel |
| RB_Transformers | transformers, bund, firewall, HV cable boxes, LV bus ducts |
| RB_ShortingFrame | movable (crane). Modelled over cell B20. Place over cell i at (cell x, row y, {L.SEAT_Z}). Its copper bars clamp onto the intercell bars on both sides of the cell |

| Object | Pivot |
|---|---|
{rows}

## Electrical sizing (my estimates)

| Item | Value | Status |
|---|---|---|
| Cell current | about {cur:.0f} kA | Inference in the research file: 45 cathodes × 2 faces × about 1 m² × 300 A/m² |
| Cell voltage | 0.25–0.3 V | Sourced |
| Circuit voltage | {cells} cells × 0.30 V = {v_cells:.0f} V, plus bus losses → about 55 V DC | Calculated |
| Rectifier rating | 2 units × 15–18 kA, about 1.7 MW in total | Estimated (no kA ratings found for real units) |
| Bus section | 4 copper bars 250 × 25 mm per pole (25,000 mm², about 1.2 A/mm²) | Estimated (common design current density for copper bus) |
| Transformer size, house size, bus height | | Estimated |
| Shorting frame | | Own design (real refineries use bypass frames/switches; no drawing found) |

Sources: research companion §8 (cell voltage, current density, rectifier references: ABB and GE
Vernova brochures, no ratings); WO2012114176A1 (busbar).
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(parts):
    m = L.materials()
    ref = pb.collection("REF")
    bld = L.load_objects(L.asset_path("Tankhouse", "SM_TankhouseBuilding"),
                         ["TH_Frame", "TH_OperatingFloor", "TH_Basement", "TH_CraneRunway", "TH_Walls", "TH_Roof"])
    for o in bld:
        ref.objects.link(o)
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    src = L.instance_collection("SRC_Cell", cell)
    for r, ry in L.ROW_Y.items():
        for i in list(range(0, 4)) + list(range(L.CELLS_PER_ROW - 4, L.CELLS_PER_ROW)):
            L.place_instance(ref, src, (L.cell_x(i), ry, 0), name=f"REF_Cell{r}{i}")
    pb.ref_ground(ref, (-60, -50, 100, 60), [(L.BLD_X0, -L.BLD_Y, L.BLD_X1, L.BLD_Y), (HOUSE[0], HOUSE[2], HOUSE[1],
                  HOUSE[3] + 6.5)], z=-0.31)
    pb.ref_human(ref, (50.0, 12.5, 0.0))
    pb.setup_render(res=(1600, 900), samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Yard.png"), (78, 48, 18), (52, 18, 2), lens=30)
    by = {o.name: o for o in bld}
    by["TH_Walls"].hide_render = True
    by["TH_Roof"].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_RowEnds.png"), (62, -16, 7), (52, 0, 0.5), lens=28)
    parts["house"].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_House.png"), (48, 9, 9), (52, 18, 1.0), lens=28)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, parts, flanges, z_end = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, flanges, z_end)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview(parts)


main()
