"""
build_electrolytic_cell.py - SM_ElectrolyticCell (polymer concrete electrorefining cell).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_electrolytic_cell.py
Needs Meshes/PermanentCathode/SM_PermanentCathode.blend for the previews.

Origin = cell centre at operating floor level (z 0). Long axis along Y, electrodes span X.
Place cell i of a row at (cell_x(i), ROW_Y[row], 0) in tankhouse coordinates, no rotation.
Each cell owns the capping board and intercell bar on its +X wall pair; the neighbour on the
+X side rests its -X electrode ends on them.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_ElectrolyticCell"
OUT = os.path.join(L.MESHES, "ElectrolyticCell")

HX_IN = L.CELL_IN_W / 2                    # 0.56
HX_OUT = HX_IN + L.CELL_WALL               # 0.64
HY_IN = L.CELL_IN_L / 2                    # 2.45
HY_OUT = L.CELL_OUT_L / 2                  # 2.55
BAR_X, BAR_W = L.CELL_PITCH / 2, 0.05      # intercell bar on the gap centre
PIPE_FLANGE_Z = -1.00                      # feed / drain flanges below the cell, in the basement
FEED_FLANGE = (0.0, -(HY_OUT + 0.10), PIPE_FLANGE_Z)
DRAIN_FLANGE = (0.0, HY_OUT + 0.10, PIPE_FLANGE_Z)


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")

    zb, zf, zr = L.CELL_BOTTOM_Z, L.CELL_FLOOR_Z, L.RIM_Z

    # --- monoblock body: floor, two side walls, two end walls, bearing pads ---
    b = pb.Part("EC_Body")
    b.box_mm((-HX_OUT, -HY_OUT, zb), (HX_OUT, HY_OUT, zf), m["polymer"])
    for s in (-1, 1):
        x0, x1 = sorted((s * HX_IN, s * HX_OUT))
        b.box_mm((x0, -HY_OUT, zf), (x1, HY_OUT, zr), m["polymer"])
        y0, y1 = sorted((s * HY_IN, s * HY_OUT))
        b.box_mm((-HX_IN, y0, zf), (HX_IN, y1, zr), m["polymer"])
    # vinyl ester liner seen on the inside floor
    b.box_mm((-HX_IN, -HY_IN, zf), (HX_IN, HY_IN, zf + 0.005), m["liner"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box((0.3, 0.3, 0.03), (sx * 0.42, sy * 2.2, zb - 0.015), m["rubber"])
    body = b.finish(col)

    # --- feed box (-Y end) and overflow weir box (+Y end), with pipes to basement flanges ---
    pf = pb.Part("EC_FeedOverflow")
    for s, flange, r in ((-1, FEED_FLANGE, 0.03), (1, DRAIN_FLANGE, 0.045)):
        y0, y1 = sorted((s * HY_OUT, s * (HY_OUT + 0.20)))
        pf.box_mm((-0.16, y0, zb + 0.10), (0.16, y1, zr), m["frp"])
        pf.box_mm((-0.17, y0 - 0.01, zr), (0.17, y1 + 0.01, zr + 0.02), m["frp"])
        pf.cyl_between((0, flange[1], zb + 0.10), (0, flange[1], flange[2]), r, m["frp"], seg=12)
        pb.flange(pf, flange, (0, 0, 0), r, m["frp"])
    # inside: feed distributor pipe along the floor, perforated (shown plain)
    pf.cyl_between((-0.40, -HY_IN, zf + 0.06), (-0.40, HY_IN - 0.2, zf + 0.06), 0.025, m["frp"], seg=10)
    pf.box_mm((-0.42, -HY_OUT, zf + 0.035), (-0.38, -HY_IN, zf + 0.085), m["frp"])
    feed = pf.finish(col)

    # --- capping boards: +X wall pair (own and neighbour's) plus the end walls ---
    c = pb.Part("EC_Capping")
    c.box_mm((HX_IN, -HY_OUT, zr), (L.CELL_PITCH - HX_IN, HY_OUT, L.CAP_TOP), m["capping"])
    for s in (-1, 1):
        y0, y1 = sorted((s * HY_IN, s * HY_OUT))
        c.box_mm((-HX_IN, y0, zr), (HX_IN, y1, L.CAP_TOP), m["capping"])
    cap = c.finish(col)

    # --- intercell bar (Walker double contact) on the gap centre of the +X wall pair ---
    ib = pb.Part("EC_IntercellBar")
    ib.box_mm((BAR_X - BAR_W / 2, -HY_OUT + 0.03, L.CAP_TOP), (BAR_X + BAR_W / 2, HY_OUT - 0.03, L.SEAT_Z),
              m["copper"])
    bar = ib.finish(col)

    # --- electrolyte, separate so it can be hidden or given a translucent material ---
    e = pb.Part("EC_Electrolyte")
    e.box_mm((-HX_IN + 0.002, -HY_IN + 0.002, L.LIQUID_Z - 0.01), (HX_IN - 0.002, HY_IN - 0.002, L.LIQUID_Z),
             m["electrolyte"])
    liquid = e.finish(col)

    return col, [body, feed, cap, bar, liquid], liquid


def write_readme(col):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_ElectrolyticCell

One copper electrorefining cell, for instancing along the four cell rows of SM_TankhouseBuilding.
- **Body:** polymer concrete monoblock with a vinyl ester liner, standing on four elastomer
  bearing pads on the building's cell support beams.
- **Electrodes:** {L.ANODES_PER_CELL} anodes (ATC_Anode / CW_Anode from the anode set) and
  {L.CATHODES_PER_CELL} permanent cathodes (SM_PermanentCathode) at a 100 mm anode pitch. The
  electrodes are not part of this mesh.
- **Contacts:** Walker-type double contact. Each cell owns the capping board and copper intercell
  bar on its +X wall pair. On that bar, the cathodes of this cell and the anodes of the next cell
  (+X) make contact. Their other ends rest on the capping boards.
- **Electrolyte:** enters at the -Y end through a feed box and a distributor pipe along the floor,
  and leaves over a weir in the +Y overflow box. Both boxes drain to flanges in the basement.

Built in Blender 5.2.2, metres, Z up. Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE, 5 objects).
Previews: `Preview_Cell.png` (one loaded cell, electrolyte hidden),
`Preview_Row.png` (six cells showing the electrode stagger).

## Origin and placement

- Origin: cell centre at operating floor level. Tankhouse z 0 is the walkway level, so cell i of
  a row goes at **(0.66 + 1.32·i, ROW_Y, 0)** with no rotation. Rows: A y -9.45, B -3.15,
  C 3.15, D 9.45. 40 cells per row.
- All cells face the same way: feed at -Y, overflow at +Y, own intercell bar at +X.
- Seat line (top of the intercell bar and capping boards under the electrode ends) z {L.SEAT_Z}.
- Electrode positions (cell-local Y), with the Walker stagger:

| | even cell (i = 0, 2, …) | odd cell |
|---|---|---|
| anode j (0–44) | -2.20 + 0.10·j | -2.25 + 0.10·j |
| cathode k (0–45) | -2.25 + 0.10·k | -2.30 + 0.10·k |

  With this stagger, each cathode of cell i and an anode of cell i+1 sit at the same Y and meet
  end to end on the intercell bar between them.
- Anode instance: ATC_Anode at (x, y_j + 0.0225, {L.ANODE_ORIGIN_Z:.2f}), rotation Euler XYZ
  (0°, -90°, 90°). Its lugs then point along ±X and their undersides sit on z {L.SEAT_Z}.
- Cathode instance: SM_PermanentCathode at (x, y_k, {L.SEAT_Z}), no rotation.
- Use the same orientation in all four rows. Current runs +X in rows A and C and -X in rows B and
  D (see RectifierBusbar/README.md). Because the insulator saddles are not modelled, the cell looks
  the same either way; in rows B and D read "anodes contact the +X bar, cathodes the -X bar".
  SM_RectifierBusbar supplies the end bar at the west end of each row (cell 0's -X side) and the
  end supports.

## Connection points (cell-local)

| Point | Position | Size |
|---|---|---|
| Electrolyte feed flange (from the row feed header) | {FEED_FLANGE} | DN60 |
| Overflow drain flange (to the row return launder) | {DRAIN_FLANGE} | DN90 |

## Parts and pivots

| Object | Use |
|---|---|
| EC_Body | static |
| EC_FeedOverflow | static |
| EC_Capping | static. Insulating boards, also covers the next cell's -X wall |
| EC_IntercellBar | static. Swap material to show hot spots |
| EC_Electrolyte | static. Hide when a cell is drained |

| Object | Pivot (cell-local) |
|---|---|
{rows}

## Unreal import

Combine Meshes off. Place one Blueprint per cell with these five meshes, and two HISMs per cell
(or one HISM per row) for the anodes and cathodes. 160 cells × 91 electrodes = 14,560 instances.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Inside 4.9 × 1.12 × 1.25 m (length × width × depth from the seat) | | Sourced range 4–5 m × 1.1 m × 1.2 m; exact values estimated to fit the anode |
| 45 anodes, 46 cathodes | | Sourced: 30–50 anodes per cell, one more cathode than anodes |
| Electrode pitch 100 mm (anode to anode); anode face to cathode face about 25 mm | | Sourced: 10 cm, at least 2.5 cm gap |
| Polymer concrete cell with vinyl ester lining | | Sourced: US6572741B1 |
| Electrolyte 60–65 °C in, 0.015–0.02 m³/min per cell | | Sourced (research file §8) |
| Wall 80 mm at the top, 120 mm floor, 40 mm gap between cells, 1.32 m cell pitch | | Estimated |
| Electrolyte level {L.SEAT_Z - L.LIQUID_Z:.2f} m below the seat. The anode body is then about 0.76 m immersed | | Estimated. The fixed anode (lugs flush with its top edge) sets this |
| Feed box, distributor pipe, overflow box | | Estimated layout |
| Insulator saddles under the non-contact electrode ends | | Not modelled. Real Walker cells hold those ends a few mm above the bar on insulating saddles; here every end rests on the capping board or bar at the same height |

Sources: /mnt/project-files/research/copper-refinery/copper-refinery-equipment.md (§8 table:
cell size, electrodes per cell, pitch, flow); US6572741B1 (polymer concrete cell); US6045669
(cell contact system); WO2012114176A1 (busbar).
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(cell_obs, liquid):
    """Load the cathode, build REF anodes, and render a loaded cell and a short row."""
    m = L.materials()
    ref = pb.collection("REF")
    anode = L.ref_anode(ref, m["anode_cu"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"),
                          ["CA_Plate", "CA_DepositFront", "CA_DepositBack"])
    src = L.instance_collection("SRC_Electrodes", [anode] + cath)
    loaded = [L.loaded_cell_collection(cell_obs, anode, cath, odd, f"LoadedCell_{odd}") for odd in (0, 1)]
    for i in range(1, 6):
        L.place_instance(ref, loaded[i % 2], (L.CELL_PITCH * i, 0, 0), name=f"REF_Cell{i}")
    # the exported cell (i = 0) gets its electrodes as plain objects so parts can be hidden
    for o in loaded[0].objects:
        if o.name.startswith(("A", "CA_")):
            ref.objects.link(o)
    _ = src
    pb.setup_render(res=(1600, 900), samples=32)
    floor = pb.Part("REF_Floor")
    gm = pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95)
    floor.box_mm((-3, -4, -0.62), (9, 4, -0.55), gm)
    floor.box_mm((-1.0, -4.0, -0.05), (8.5, -2.80, 0.0), m["grating"])   # walkway at z 0
    floor.finish(ref)
    pb.ref_human(ref, (1.6, -3.4, 0.0))
    pb.render_view(os.path.join(OUT, "Preview_Row.png"), (-3.5, -7.5, 3.6), (3.0, 0.0, 0.3), lens=32)
    liquid.hide_render = True
    hide = [o for o in ref.all_objects if o.name.startswith("REF_Cell")]
    for o in hide:
        o.hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Cell.png"), (-2.2, -5.6, 2.6), (0.0, -0.4, 0.2), lens=30)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, parts, liquid = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview(parts, liquid)


main()
