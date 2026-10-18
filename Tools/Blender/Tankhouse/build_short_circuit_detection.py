"""
build_short_circuit_detection.py - SM_ShortCircuitDetection (crane IR camera, cell voltage
sensors, row display boards, handheld gaussmeter).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_short_circuit_detection.py
Needs the cell, cathode and crane .blend files for the preview.

Every part is built at its own origin (its mount point) so it can be instanced; the README lists
where each goes in tankhouse coordinates.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_ShortCircuitDetection"
OUT = os.path.join(L.MESHES, "ShortCircuitDetection")

# Crane trolley camera bracket (from build_tankhouse_crane.py: bracket under the trolley frame)
CRANE_BX, CRANE_TY = L.cell_x(10), L.ROW_Y["A"]
CAM_MOUNT = (CRANE_BX, CRANE_TY - 1.4, 10.005)
ARM_LEN = 0.9
SENSOR_DX, SENSOR_Z = 0.35, 0.45                 # on the cell's -Y end wall, beside the feed box
DISPLAY_X = -2.6                                 # row display boards at the west end of each row


def ir_camera(m, col):
    """Boom (fixed to the trolley) and pan/tilt head with a thermal camera in a housing."""
    b = pb.Part("SCD_IRBoom")
    b.box((0.25, 0.25, 0.04), (0, 0, -0.02), m["steel"])
    b.box_mm((-0.05, -0.05, -ARM_LEN), (0.05, 0.05, -0.04), m["yellow"])
    b.box((0.2, 0.2, 0.05), (0, 0, -ARM_LEN - 0.025), m["steel"])
    b.box((0.3, 0.12, 0.25), (0.12, 0.0, -0.25), m["cabinet"])               # junction / power box
    boom = b.finish(col)
    h = pb.Part("SCD_IRHead", pivot=(0, 0, -ARM_LEN - 0.05))
    z = -ARM_LEN - 0.05
    h.cyl(0.08, 0.1, (0, 0, z - 0.05), m["grey"], seg=16)                     # pan unit
    h.box((0.06, 0.32, 0.22), (0, 0, z - 0.21), m["grey"])                    # tilt yoke
    h.box((0.20, 0.26, 0.36), (0, 0, z - 0.32), m["cabinet"])                  # camera housing
    h.box((0.24, 0.30, 0.02), (0, 0, z - 0.13), m["cabinet"])                  # sunshield
    h.cyl(0.06, 0.04, (0, 0, z - 0.52), m["black"], seg=16)                    # germanium window
    head = h.finish(col)
    return boom, head


def cell_sensor(m, col):
    """Cell voltage / temperature sensor box with two leads to the intercell bars."""
    s = pb.Part("SCD_CellSensor")
    s.box((0.22, 0.10, 0.18), (0, -0.05, 0), m["cabinet"])
    s.box((0.08, 0.02, 0.04), (-0.05, -0.105, 0.03), m["green"])               # status LED strip
    for x in (-0.06, 0.06):
        s.cyl_between((x, -0.05, 0.09), (x, -0.05, 0.25), 0.008, m["red"] if x < 0 else m["black"], seg=6)
    s.cyl_between((-0.06, -0.05, 0.25), (-0.66 - SENSOR_DX, 0.06, L.SEAT_Z - SENSOR_Z - 0.01), 0.008,
                  m["red"], seg=6)
    s.cyl_between((0.06, -0.05, 0.25), (0.66 - SENSOR_DX, 0.06, L.SEAT_Z - SENSOR_Z - 0.01), 0.008,
                  m["black"], seg=6)
    return s.finish(col)


def row_display(m, col):
    """Post-mounted display board showing cell voltages and short alarms for one row."""
    d = pb.Part("SCD_RowDisplay")
    d.box_mm((-0.06, -0.06, 0.0), (0.06, 0.06, 2.6), m["steel"])
    d.box_mm((-0.05, -0.9, 2.0), (0.05, 0.9, 3.0), m["black"])
    d.box_mm((-0.06, -0.85, 2.05), (-0.05, 0.85, 2.95), m["screen"])
    d.box((0.3, 0.3, 0.6), (0.0, 0.25, 0.8), m["cabinet"])                    # row data concentrator
    d.box((0.06, 0.12, 0.12), (-0.1, 0.0, 3.08), m["red"])                     # alarm beacon
    return d.finish(col)


def gaussmeter(m, col):
    """Handheld gaussmeter: probe on a fibreglass pole with a readout. Origin at the grip."""
    g = pb.Part("SCD_Gaussmeter")
    g.cyl_between((0, 0, -0.4), (0, 0, 1.3), 0.015, m["yellow"], seg=8)        # pole
    g.box((0.04, 0.02, 0.12), (0, 0, -0.46), m["black"])                       # Hall probe head
    g.box((0.10, 0.05, 0.16), (0.0, 0.035, 0.2), m["cabinet"])                 # readout
    g.box((0.07, 0.005, 0.06), (0.0, 0.061, 0.23), m["screen"])
    g.cyl(0.022, 0.18, (0, 0, 0), m["rubber"], seg=10)                         # grip
    return g.finish(col)


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")
    parts = {}
    parts["boom"], parts["head"] = ir_camera(m, col)
    parts["sensor"] = cell_sensor(m, col)
    parts["display"] = row_display(m, col)
    parts["gauss"] = gaussmeter(m, col)
    return col, parts


def write_readme(col):
    rows = pb.pivot_table([col.name])
    disp = "\n".join(f"| SCD_RowDisplay, row {r} | ({DISPLAY_X}, {y + 3.2:.2f}, 0), rotation 0 (screen faces -X) |"
                     for r, y in L.ROW_Y.items())
    txt = f"""# SM_ShortCircuitDetection

Short-circuit detection for the tankhouse. A short (a bent cathode or a nodule touching an anode)
pulls current through one electrode pair; the hot contacts show up on a thermal camera, the cell
voltage drops, and the magnetic field around the shorted hanger bar rises. This set covers the
three methods the research notes list:
- **Crane IR camera:** a thermal camera on a pan/tilt head under the tankhouse crane's trolley,
  scanning the cell tops as the crane travels.
- **Cell voltage sensors:** one sensor box per cell on the -Y end wall, wired to the intercell bars
  on both sides of the cell, reporting to a display board at the west end of each row.
- **Handheld gaussmeter:** a Hall probe on a fibreglass pole that an operator runs along the
  hanger bars to find the shorted cathode.

Built in Blender 5.2.2, metres, Z up. Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE, 6 objects).
Preview: `Preview_Overview.png`.

## Placement (tankhouse coordinates)

| Part | Location |
|---|---|
| SCD_IRBoom | on the crane trolley's camera bracket. With SM_TankhouseCrane in its modelled pose: {CAM_MOUNT}. Attach it to TC_Trolley |
| SCD_IRHead | at the boom's pivot ({CAM_MOUNT[0]:.2f}, {CAM_MOUNT[1]:.2f}, {CAM_MOUNT[2] - ARM_LEN - 0.05:.3f}); attach to SCD_IRBoom. Pan = rotate local Z, tilt = rotate the housing about local X (single object here; split if you need both axes) |
| SCD_CellSensor | one per cell at (cell x + {SENSOR_DX}, row y − 2.56, {SENSOR_Z}), no rotation: on the cell's end wall at the feed end, beside the feed box. The two leads end on the intercell bars on both sides of the cell (cell x ± 0.66) |
{disp}
| SCD_Gaussmeter | prop, carried by an operator. Origin at the grip, probe down (local −Z) |

## Parts and pivots

| Object | Pivot (local) |
|---|---|
{rows}

## Sources and status

| Item | Status |
|---|---|
| IR detection of shorts, published methods | Sourced (research companion §8 [S30][S31]) |
| Cell voltage and short monitors (ShortMeter, CellView) | Sourced (Mipac, research companion [S24]) |
| Handheld gaussmeters and IR cameras on the crane | Sourced (research file §8) |
| Shorts cost 1–3 % of current | Sourced (research companion [S6][S23]) |
| All shapes and sizes, the sensor and display positions | Own design / estimated. No brand styling or logos |
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(parts):
    m = L.materials()
    ref = pb.collection("REF")
    for o in parts.values():
        o.hide_render = True
    anode = L.ref_anode(ref, m["anode_cu"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"),
                          ["CA_Plate", "CA_DepositFront", "CA_DepositBack"])
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    L.instance_collection("SRC_Parts", [anode] + cath + cell)
    loaded = [L.loaded_cell_collection(cell, anode, cath, odd, f"LoadedCell_{odd}") for odd in (0, 1)]
    crane = [o for o in L.load_objects(L.asset_path("TankhouseCrane", "SM_TankhouseCrane")) if o.name.startswith("TC_")]
    for o in crane:
        ref.objects.link(o)
    for r in ("A", "B"):
        ry = L.ROW_Y[r]
        for i in range(0, 14):
            L.place_instance(ref, loaded[i % 2], (L.cell_x(i), ry, 0), name=f"REF_Cell{r}{i}")
            L.linked_copy(parts["sensor"], ref, (L.cell_x(i) + SENSOR_DX, ry - 2.56, SENSOR_Z), name=f"REF_Sensor{r}{i}")
        L.linked_copy(parts["display"], ref, (DISPLAY_X, ry + 3.2, 0), name=f"REF_Display{r}")
    L.linked_copy(parts["boom"], ref, CAM_MOUNT, name="REF_Boom")
    L.linked_copy(parts["head"], ref, (CAM_MOUNT[0], CAM_MOUNT[1], CAM_MOUNT[2] - ARM_LEN - 0.05), name="REF_Head")
    pb.ref_human(ref, (5.0, -6.3, 0.0))
    L.linked_copy(parts["gauss"], ref, (5.25, -6.0, 0.95), (35, 0, 0), name="REF_Gauss")
    fl = pb.Part("REF_Floor")
    fl.box_mm((-4, -14, -0.62), (20, 0, -0.55), pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
    fl.box_mm((-4, -6.68, -0.05), (20, -5.92, 0.0), m["grating"])
    fl.box_mm((-4, -14, -0.05), (20, -12.22, 0.0), m["floor"])
    fl.box_mm((-4, -14, -0.05), (-0.6, 0, 0.0), m["floor"])
    fl.finish(ref)
    pb.setup_render(res=(1600, 900), samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (-3.0, -16.0, 6.5), (6.0, -6.5, 1.5), lens=26)


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
