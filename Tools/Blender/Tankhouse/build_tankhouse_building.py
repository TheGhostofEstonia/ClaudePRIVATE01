"""
build_tankhouse_building.py - SM_TankhouseBuilding (electrorefining hall, basement, crane runway).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_tankhouse_building.py
Needs the cell, cathode and crane .blend files for the previews.

Tankhouse coordinates (see th_layout.py). Hall x -32..64, y -15..15. Service bay at grade
x -32..-4; four cell rows (A-D) of 40 cells from x 0 to 52.8 over a basement at z -3.0.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_TankhouseBuilding"
OUT = os.path.join(L.MESHES, "Tankhouse")

X0, X1, HW = L.BLD_X0, L.BLD_X1, L.BLD_Y
BX0, BX1 = -2.0, 62.0                    # basement extent in X
BY = 12.6                                # basement half width
CELL_X0 = -0.6                           # west row end (row end bars)
CELL_X1 = L.CELL_PITCH * L.CELLS_PER_ROW + 0.8
ROW_HALF = L.CELL_OUT_L / 2 + 0.22       # cell plus feed / overflow boxes
STAIR = (55.0, 61.0, 10.0, 11.4)         # x0, x1, y0, y1 of the basement stair opening
DOORS = [  # (wall, centre along wall, width, height)
    ("S", -18.0, 6.0, 6.0), ("N", -18.0, 6.0, 6.0), ("W", 0.0, 6.0, 6.0), ("E", 0.0, 4.0, 4.5),
]


def frame(m, col):
    """Columns, roof rafters, purlins, ridge, bracing."""
    f = pb.Part("TH_Frame")
    xs = [X0 + L.COL_STEP * i for i in range(int((X1 - X0) / L.COL_STEP) + 1)]
    for x in xs:
        for s in (-1, 1):
            y = s * (HW - 0.25)
            f.box_mm((x - 0.15, y - 0.25, 0.0), (x + 0.15, y + 0.25, L.EAVES_Z), m["steel"])
            f.box((0.7, 0.7, 0.3), (x, y, -0.15), m["concrete"])        # base plinth
            # crane runway bracket
            f.box_mm((x - 0.15, s * L.CRANE_RAIL_Y - 0.35, L.CRANE_RAIL_Z - 1.45),
                     (x + 0.15, y, L.CRANE_RAIL_Z - 1.15), m["steel"])
        for s in (-1, 1):   # rafters
            f.beam_between((x, s * HW, L.EAVES_Z), (x, 0.0, L.RIDGE_Z), 0.25, 0.6, m["steel"])
        f.beam_between((x, -HW + 0.5, L.EAVES_Z - 0.3), (x, HW - 0.5, L.EAVES_Z - 0.3), 0.12, 0.12, m["steel"])
    # purlins every ~2.5 m up each slope, and eaves / ridge members
    for k in range(7):
        t = k / 6
        for s in (-1, 1):
            y = s * HW * (1 - t)
            z = L.EAVES_Z + (L.RIDGE_Z - L.EAVES_Z) * t + 0.35
            f.box_mm((X0, y - 0.08, z - 0.12), (X1, y + 0.08, z + 0.12), m["steel"])
    # X bracing in the end bays of both long walls
    for x0, x1 in ((xs[0], xs[1]), (xs[-2], xs[-1])):
        for s in (-1, 1):
            y = s * (HW - 0.25)
            f.beam_between((x0, y, 0.3), (x1, y, L.EAVES_Z - 0.3), 0.06, 0.06, m["steel"])
            f.beam_between((x1, y, 0.3), (x0, y, L.EAVES_Z - 0.3), 0.06, 0.06, m["steel"])
    return f.finish(col)


def runway(m, col):
    """Crane runway girders and rails."""
    r = pb.Part("TH_CraneRunway")
    for s in (-1, 1):
        y = s * L.CRANE_RAIL_Y
        r.box_mm((X0, y - 0.25, L.CRANE_RAIL_Z - 1.15), (X1, y + 0.25, L.CRANE_RAIL_Z - 0.10), m["steel"])
        r.box_mm((X0, y - 0.04, L.CRANE_RAIL_Z - 0.10), (X1, y + 0.04, L.CRANE_RAIL_Z), m["grey"])
        for x in (X0 + 0.3, X1 - 0.3):       # end stops
            r.box((0.4, 0.5, 0.6), (x, y, L.CRANE_RAIL_Z + 0.3), m["red"])
    return r.finish(col)


def floors(m, col):
    """Operating floor (z 0): service bay slab, aisles, walkways between rows, east slab."""
    f = pb.Part("TH_OperatingFloor")
    t = 0.30
    f.box_mm((X0, -HW, -t), (CELL_X0, HW, 0.0), m["floor"])                 # service bay + west landing
    f.box_mm((CELL_X1, -HW, -t), (X1, HW, 0.0), m["floor"])                 # east slab (stair cut below)
    for s in (-1, 1):                                                       # side aisles
        y0, y1 = sorted((s * (abs(L.ROW_Y["A"]) + ROW_HALF), s * HW))
        f.box_mm((CELL_X0, y0, -t), (CELL_X1, y1, 0.0), m["floor"])
    # FRP gratings on steel beams between the rows
    rows = sorted(L.ROW_Y.values())
    for a, b in zip(rows[:-1], rows[1:]):
        y0, y1 = a + ROW_HALF, b - ROW_HALF
        f.box_mm((CELL_X0, y0, -0.05), (CELL_X1, y1, 0.0), m["grating"])
        for yy in (y0 + 0.05, y1 - 0.05):
            f.box_mm((CELL_X0, yy - 0.05, -0.35), (CELL_X1, yy + 0.05, -0.05), m["steel"])
    # yellow kerb lines along the service bay / cell area edge
    f.box_mm((CELL_X0 - 0.15, -12.4, 0.0), (CELL_X0, 12.4, 0.02), m["yellow"])
    ob = f.finish(col)
    return ob


def basement(m, col):
    """Basement slab, retaining walls, cell support beams on columns, stair."""
    b = pb.Part("TH_Basement")
    z = L.BASEMENT_Z
    b.box_mm((BX0, -BY, z - 0.4), (BX1, BY, z), m["floor"])
    for s in (-1, 1):
        y0, y1 = sorted((s * BY, s * (BY + 0.4)))
        b.box_mm((BX0, y0, z), (BX1, y1, -0.3), m["concrete"])
    b.box_mm((BX0 - 0.4, -BY - 0.4, z), (BX0, BY + 0.4, -0.3), m["concrete"])
    b.box_mm((BX1, -BY - 0.4, z), (BX1 + 0.4, BY + 0.4, -0.3), m["concrete"])
    # cell support beams: two per row under the bearing pads, columns every 3 cells
    beam_top = L.CELL_BOTTOM_Z - 0.03
    for ry in L.ROW_Y.values():
        for s in (-1, 1):
            y = ry + s * 2.2
            b.box_mm((CELL_X0, y - 0.25, beam_top - 0.6), (CELL_X1, y + 0.25, beam_top), m["concrete"])
            n = int((CELL_X1 - CELL_X0) / 3.96) + 1
            for i in range(n + 1):
                x = CELL_X0 + 0.25 + (CELL_X1 - CELL_X0 - 0.5) * i / n
                b.box_mm((x - 0.25, y - 0.25, z), (x + 0.25, y + 0.25, beam_top - 0.6), m["concrete"])
    # sloped trench along each row centre (spill collection to a sump at the east end)
    for ry in L.ROW_Y.values():
        b.box_mm((BX0 + 0.5, ry - 0.3, z - 0.02), (BX1 - 0.5, ry + 0.3, z + 0.01), m["liner"])
    b.box_mm((BX1 - 2.5, -1.5, z - 0.02), (BX1 - 0.5, 1.5, z + 0.01), m["liner"])
    # stair from the east slab down to the basement
    sx0, sx1, sy0, sy1 = STAIR
    nst = 16
    for i in range(nst):
        x = sx0 + (sx1 - sx0) * (i + 0.5) / nst
        zt = -(i + 1) * (-z) / nst
        b.box_mm((x - 0.19, sy0, zt - 0.05), (x + 0.19, sy1, zt), m["grating"])
    for yy in (sy0, sy1):
        b.beam_between((sx0, yy, -0.1), (sx1, yy, z), 0.05, 0.25, m["steel"])
        pb.handrail(b, (sx0, yy, 0.0), (sx1, yy, z), m["yellow"], post_step=1.5)
    return b.finish(col)


def walls(m, col):
    """Cladding with door openings and a glazing band, as one object so it can be hidden."""
    w = pb.Part("TH_Walls")
    zg0, zg1 = 9.0, 11.0                      # glazing band

    def wall_x(y, sgn, doors):
        """Long wall at y, split around doors (list of (centre x, width, height))."""
        cuts = sorted(doors)
        x = X0
        for cx, wd, ht in cuts + [(X1 + 1e9, 0, 0)]:
            a = min(cx - wd / 2, X1)
            if a > x:
                w.box_mm((x, y - 0.05, 0.0), (a, y + 0.05, zg0), m["cladding"])
            if cx < X1:
                w.box_mm((cx - wd / 2, y - 0.05, ht), (cx + wd / 2, y + 0.05, zg0), m["cladding"])
                w.box_mm((cx - wd / 2, y - 0.15 * sgn, ht - 0.3), (cx + wd / 2, y, ht), m["yellow"])
            x = cx + wd / 2
        w.box_mm((X0, y - 0.03, zg0), (X1, y + 0.03, zg1), m["glass"])
        w.box_mm((X0, y - 0.05, zg1), (X1, y + 0.05, L.EAVES_Z), m["cladding"])

    for wall, sgn in (("S", -1), ("N", 1)):
        wall_x(sgn * HW, sgn, [(c, wd, ht) for wl, c, wd, ht in DOORS if wl == wall])
    for wall, x in (("W", X0), ("E", X1)):
        d = [(c, wd, ht) for wl, c, wd, ht in DOORS if wl == wall][0]
        c, wd, ht = d
        w.box_mm((x - 0.05, -HW, 0.0), (x + 0.05, c - wd / 2, L.EAVES_Z), m["cladding"])
        w.box_mm((x - 0.05, c + wd / 2, 0.0), (x + 0.05, HW, L.EAVES_Z), m["cladding"])
        w.box_mm((x - 0.05, c - wd / 2, ht), (x + 0.05, c + wd / 2, L.EAVES_Z), m["cladding"])
        # gable
        w.poly_prism([(-HW, L.EAVES_Z), (HW, L.EAVES_Z), (0.0, L.RIDGE_Z)], x - 0.05, x + 0.05,
                     m["cladding"], plane='YZ')
    return w.finish(col)


def roof(m, col):
    """Pitched roof sheeting and a continuous ridge ventilator (acid mist extraction)."""
    r = pb.Part("TH_Roof")
    vent = 1.6
    for s in (-1, 1):
        a = (s * (HW + 0.4), L.EAVES_Z + 0.5 - 0.4 * (L.RIDGE_Z - L.EAVES_Z) / HW)
        b = (s * vent, L.RIDGE_Z + 0.5 - vent * (L.RIDGE_Z - L.EAVES_Z) / HW)
        pts = [(a[0], a[1]), (b[0], b[1]), (b[0], b[1] + 0.08), (a[0], a[1] + 0.08)]
        r.poly_prism(pts, X0 - 0.4, X1 + 0.4, m["roof"], plane='YZ')
    zr = L.RIDGE_Z + 0.5
    for s in (-1, 1):   # vent side louvres
        r.box_mm((X0, s * vent - 0.04, zr - 0.2), (X1, s * vent + 0.04, zr + 1.2), m["grey"])
    r.poly_prism([(-vent - 0.4, zr + 1.2), (vent + 0.4, zr + 1.2), (0.0, zr + 1.7)], X0, X1, m["roof"],
                 plane='YZ')
    return r.finish(col)


def transfer_stands(m, col):
    """Four stands in the service bay where the crane sets down / picks up full cell loads."""
    obs = []
    for key, (x, y) in L.TRANSFER.items():
        s = pb.Part(f"TH_TransferStand_{key}", pivot=(x, y, 0.0))
        z = L.TRANSFER_SEAT_Z
        for sx in (-1, 1):
            s.box_mm((x + sx * 0.66 - 0.06, y - 2.55, z - 0.12), (x + sx * 0.66 + 0.06, y + 2.55, z), m["steel"])
            s.box_mm((x + sx * 0.60 - 0.035, y - 2.5, z - 0.005), (x + sx * 0.60 + 0.035, y + 2.5, z),
                     m["capping"])
            for yy in (-2.4, -0.8, 0.8, 2.4):
                s.box_mm((x + sx * 0.66 - 0.08, y + yy - 0.08, 0.0), (x + sx * 0.66 + 0.08, y + yy + 0.08, z - 0.12),
                         m["steel"])
        for yy in (-2.4, 2.4):
            s.box_mm((x - 0.72, y + yy - 0.05, 0.25), (x + 0.72, y + yy + 0.05, 0.35), m["steel"])
        s.box_mm((x - 0.9, y - 2.8, 0.0), (x + 0.9, y + 2.8, 0.01), m["yellow"])   # floor marking
        obs.append(s.finish(col))
    return obs


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")
    parts = {
        "frame": frame(m, col), "runway": runway(m, col), "floor": floors(m, col),
        "basement": basement(m, col), "walls": walls(m, col), "roof": roof(m, col),
    }
    transfer_stands(m, col)
    return col, parts


def write_readme(col):
    rows = pb.pivot_table([col.name])
    rx = {k: v for k, v in L.ROW_Y.items()}
    tr = "\n".join(f"| {k} | ({x:.1f}, {y:.1f}, {L.TRANSFER_SEAT_Z}) | ({x + L.WORLD_ORIGIN[0]:.1f}, "
                   f"{y + L.WORLD_ORIGIN[1]:.1f}) |" for k, (x, y) in L.TRANSFER.items())
    txt = f"""# Tankhouse (SM_TankhouseBuilding and layout reference)

Copper electrorefining tankhouse: hall, basement and crane runway. This README is also the
**layout reference** for every tankhouse asset (cells, cathodes, crane, rectifiers and busbars,
short-circuit detection, electrolyte circulation, liberator cells) and for the anode preparation
and cathode stripping machines built in other threads.

Built in Blender 5.2.2, metres, Z up. Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE, mesh only),
`Preview_Exterior.png`, `Preview_Interior.png` (walls and roof hidden), `Preview_Basement.png`,
`Preview_PlantOverview.png` and `Preview_PlantCutaway.png` (every tankhouse asset placed; made by render_tankhouse_overview.py). Rebuild scripts:
`Tools/Blender/Tankhouse/` (shared constants in `th_layout.py`).

## Tankhouse coordinates

- **Origin:** west end of the cell area, on the hall centreline, at operating floor level (z 0).
  +X runs along the hall (west to east), +Y across it (south to north).
- **Placement in the plant:** put the tankhouse origin at **flash-furnace world
  ({L.WORLD_ORIGIN[0]:.0f}, {L.WORLD_ORIGIN[1]:.0f}, {L.WORLD_ORIGIN[2]:.0f}) with no rotation**. All tankhouse
  assets use this one origin, so they line up when placed at the same transform. My choice: south
  of the smelter, clear of the slag concentrator (x -240 to -55, y 180 to 300) and the acid plant
  (east of x 69.6, tanks to the north). World extents including annexes: x -32 to 82,
  y -177 to -123.
- **Anode set:** SM_RotaryAnodeFurnace and its casting wheel / take-off / stacking machines are not
  tied to the flash furnace. Anode stacks reach the tankhouse by forklift through the service bay
  doors, so their placement is free.

## Key numbers

| Item | Value |
|---|---|
| Hall | x {X0} to {X1}, y ±{HW}; eaves {L.EAVES_Z}, ridge {L.RIDGE_Z} (+ ridge vent); columns every {L.COL_STEP} m |
| Service bay (at grade, forklifts) | x {X0} to {L.SERVICE_BAY_X1}. Doors: south and north walls at x -21 to -15 (6 × 6 m), west wall centre (6 × 6 m) |
| Operating floor / walkways | z 0. Cells stand 0.80 m above it |
| Basement (piping, launders, leak detection) | z {L.BASEMENT_Z}, x {BX0} to {BX1}, y ±{BY}. Stair at x {STAIR[0]} to {STAIR[1]}, y {STAIR[2]} to {STAIR[3]} |
| Cell rows | A y {rx['A']}, B y {rx['B']}, C y {rx['C']}, D y {rx['D']} (row centrelines) |
| Cells per row | {L.CELLS_PER_ROW}, total {4 * L.CELLS_PER_ROW} |
| Cell pitch along a row (X) | {L.CELL_PITCH} m; cell i centre x = 0.66 + 1.32·i (cells span x 0 to {L.CELL_PITCH * L.CELLS_PER_ROW:.1f}) |
| Cell outside | {L.CELL_PITCH - 0.04:.2f} (X) × {L.CELL_OUT_L:.2f} (Y) m, bottom z {L.CELL_BOTTOM_Z:.2f}, rim z {L.RIM_Z:.2f} |
| Electrode seat line (top of intercell bars) | z {L.SEAT_Z} |
| Electrolyte level | z {L.LIQUID_Z:.2f} |
| Electrodes per cell | {L.ANODES_PER_CELL} anodes, {L.CATHODES_PER_CELL} cathodes, 100 mm anode pitch (see ElectrolyticCell/README.md for positions) |
| Crane rails | y ±{L.CRANE_RAIL_Y} (span {2 * L.CRANE_RAIL_Y:.1f} m), rail top z {L.CRANE_RAIL_Z}, bridge travel x {L.CRANE_X_MIN} to {L.CRANE_X_MAX} |
| Crane hook seat | in a cell {L.SEAT_Z}; at the transfer stands {L.TRANSFER_SEAT_Z}; travel {L.SEAT_Z + 1.6:.2f} |
| Current path | rectifier (+) → row D east end, west along D → C, east along C → B, west along B → A, east along A → rectifier (−). See RectifierBusbar/README.md |

## Transfer points (crane ↔ machines)

Each transfer stand holds one full cell load: electrodes hanging along Y at the cell spacing, with
their lugs / hanger bar ends on two rails at x ±0.60 from the stand centre, seat z {L.TRANSFER_SEAT_Z}.
The crane picks or sets a load with the bale centred on the stand. The anode preparation and
cathode stripping machines (other thread) should deliver to / collect from these points, or replace
the stands with their own racks at the same position and seat height.

| Stand | Tankhouse (x, y, seat z) | World (x, y) |
|---|---|---|
{tr}

- **AnodeIn:** 45 prepared anodes from the anode preparation machine, spaced for the crane
  (anode pitch 0.10 m).
- **AnodeScrapOut:** 45 spent anodes (anode scrap) to the anode scrap washing machine.
- **CathodeOut:** 46 cathodes with copper deposit to the cathode stripping machine.
- **CathodeBlankIn:** 46 stripped blanks back from the stripping machine.

## Annexes (other tankhouse assets, same origin)

| Asset | Where |
|---|---|
| SM_RectifierBusbar | rectifier yard north of the east end (x 40 to 60, y 15 to 27), DC bus in the basement at the east end |
| SM_ElectrolyteCirculation | circulation annex south of the west end (x -32 to 0, y -27 to -15), headers in the basement |
| SM_LiberatorCells | liberator annex east of the hall (x 64 to 82, y -10 to 4) |
| SM_ShortCircuitDetection | crane-mounted IR camera, cell voltage boxes on the rows, handheld gaussmeter |

## Parts and pivots

| Object | Use |
|---|---|
| TH_Frame | static steel frame |
| TH_CraneRunway | runway girders and rails |
| TH_OperatingFloor | slabs, gratings between rows |
| TH_Basement | slab, walls, cell support beams, trench liners, stair |
| TH_Walls / TH_Roof | hide for cutaways |
| TH_TransferStand_* | separate so the machine thread can replace them |

| Object | Pivot |
|---|---|
{rows}

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off. The hall is large ({X1 - X0:.0f} × {2 * HW:.0f} m),
so consider splitting TH_Walls / TH_Roof into HLODs.

## Dimensions

| Item | Status |
|---|---|
| Cell size, electrodes per cell, electrode pitch | Sourced (see ElectrolyticCell/README.md) |
| Refineries have 800–2,400 cells | Sourced. This tankhouse has 160, a deliberately small game-scale refinery (about 45–50 kt/yr of cathode at 30 kA and 95 % current efficiency, my calculation) |
| Parallel cell rows with a crane bridge across them; crane rails parallel to the rows in US4392934, here the bridge runs along the hall and spans all four rows | Layout: own design based on US4392934 and photos |
| Hall size, eaves, basement depth, walkway widths, doors, ridge vent | Estimated |
| Rows on a basement with leak trenches | Estimated (common practice, no drawing found) |

Sources: /mnt/project-files/copper_refinery_equipment.md §8; research companion §8; US4392934.
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(parts):
    m = L.materials()
    ref = pb.collection("REF")
    anode = L.ref_anode(ref, m["anode_cu"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"),
                          ["CA_Plate", "CA_DepositFront", "CA_DepositBack"])
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    L.instance_collection("SRC_Parts", [anode] + cath + cell)
    loaded = [L.loaded_cell_collection(cell, anode, cath, odd, f"LoadedCell_{odd}") for odd in (0, 1)]
    cells = pb.collection("REF_Cells", ref)
    for r, ry in L.ROW_Y.items():
        for i in range(L.CELLS_PER_ROW):
            L.place_instance(cells, loaded[i % 2], (L.cell_x(i), ry, 0), name=f"REF_Cell{r}{i}")
    crane = L.load_objects(L.asset_path("TankhouseCrane", "SM_TankhouseCrane"))
    crane = [o for o in crane if o.name.startswith("TC_")]
    for o in crane:
        ref.objects.link(o)
    pb.ref_ground(ref, (-80, -60, 100, 60), [(X0, -HW, X1, HW)], z=-0.31)
    pb.ref_human(ref, (-14.0, -11.0, 0.0))
    pb.setup_render(res=(1600, 900), samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Exterior.png"), (-70, -60, 32), (16, 0, 4), lens=30)
    parts["walls"].hide_render = True
    parts["roof"].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Interior.png"), (-30, -11, 7.5), (20, 2, 0), lens=24)
    L.ref_lights(ref, [(x, y, -0.9) for x in (30, 40, 50, 58) for y in (-11.5, -6.3, 0.0, 6.3, 11.5)], 600.0)
    pb.render_view(os.path.join(OUT, "Preview_Basement.png"), (60.5, -11.0, -1.4), (30.0, 0.0, -2.2), lens=20)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, parts = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview(parts)


main()
