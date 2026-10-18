"""
build_permanent_cathode.py - SM_PermanentCathode (IsaKidd-type stainless steel cathode).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_permanent_cathode.py

Origin = underside centre of the hanger bar, which is the contact/seat point on the cell's
intercell bar. Blade in the local XZ plane (thickness along Y), hanger bar along X.
In a cell: location = (cell centre x, cathode_y(k), SEAT_Z), no rotation.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_PermanentCathode"
OUT = os.path.join(L.MESHES, "PermanentCathode")

DEPOSIT_T = 0.008          # one copper sheet at harvest (7-day crop, estimated)
DEPOSIT_TOP = -0.13        # just under the electrolyte level (seat - 0.12)
STRIP_W = 0.018            # PP edge strip, outside width across the blade edge


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    ref = pb.collection("REF")

    hw, t = L.BLADE_W / 2, L.BLADE_T
    z_bot = -L.BLADE_H

    # --- plate: blade with two lifting windows, plated hanger bar, edge strips ---
    p = pb.Part("CA_Plate")
    p.box_mm((-hw, -t / 2, z_bot), (hw, t / 2, L.WINDOW_Z0), m["stainless"])
    p.box_mm((-hw, -t / 2, L.WINDOW_Z1), (hw, t / 2, -0.015), m["stainless"])
    wx0, wx1 = L.WINDOW_X - L.WINDOW_W / 2, L.WINDOW_X + L.WINDOW_W / 2
    for x0, x1 in ((-hw, -wx1), (-wx0, wx0), (wx1, hw)):
        p.box_mm((x0, -t / 2, L.WINDOW_Z0), (x1, t / 2, L.WINDOW_Z1), m["stainless"])
    # copper plating 15 mm down the blade (original Isa design) and the plated hanger bar
    p.box_mm((-hw, -t / 2 - 0.0006, -0.015), (hw, t / 2 + 0.0006, 0.0), m["copper"])
    p.box_mm((-L.HANGER_L / 2, -L.HANGER_W / 2, 0.0),
             (L.HANGER_L / 2, L.HANGER_W / 2, L.HANGER_H), m["copper"])
    # polypropylene edge strips on both vertical edges, from the bottom to the deposit top
    for s in (-1, 1):
        x0, x1 = sorted((s * (hw - 0.008), s * (hw - 0.008 + STRIP_W)))
        p.box_mm((x0, -0.006, z_bot), (x1, 0.006, DEPOSIT_TOP + 0.01), m["pp"])
    plate = p.finish(col)

    # --- copper deposit: one sheet per face, pivot on its top edge (peel hinge) ---
    dw = hw - 0.008
    deposits = []
    for nm, s in (("CA_DepositFront", -1), ("CA_DepositBack", 1)):
        y0 = s * t / 2
        y1 = s * (t / 2 + DEPOSIT_T)
        d = pb.Part(nm, pivot=(0.0, y0, DEPOSIT_TOP))
        d.box_mm((-dw, min(y0, y1), z_bot + 0.005), (dw, max(y0, y1), DEPOSIT_TOP), m["cathode_cu"])
        deposits.append(d.finish(col))

    pb.ref_human(ref, (1.2, 0.6, -1.85))
    return col, plate, deposits


def write_readme(col, mass_dep):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_PermanentCathode

Permanent stainless steel cathode of the IsaKidd type, for SM_ElectrolyticCell. Copper plates
onto both faces of the blade during a 7-day crop, and the cathode stripping machine peels the two
sheets off. The blank goes back into a cell.
- **Blade:** 316L stainless, 3.25 mm, with two lifting windows under the hanger bar (real plates
  are lifted by these; SM_TankhouseCrane hooks under the hanger bar instead, see its README).
- **Hanger bar:** rectangular bar, copper plated, resting on the intercell bar at one end and on
  the capping board at the other.
- **Edge strips:** polypropylene strips on both vertical edges stop the copper growing around them.
  The bottom edge is left bare (the V-groove of the Isa 2000 design is too small to model).
- **Deposit:** two separate copper sheets (front and back), so they can be hidden while the cathode
  is a bare blank, or peeled off by the stripping machine.

Built in Blender 5.2.2, metres, Z up. Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE, mesh only).
Previews: `Preview_Cathode.png`, `Preview_Detail.png`.

## Origin and placement

- The origin is the **underside centre of the hanger bar**: the point that sits on the cell's
  seat line (SEAT_Z = {L.SEAT_Z} in tankhouse coordinates).
- The blade lies in the local XZ plane, thickness along Y. The hanger bar runs along X.
- In cell *k* (0 to 45): location = (cell centre x, cathode_y(k), {L.SEAT_Z}), no rotation.
  cathode_y(k) = -2.25 + 0.10·k for even cells, 0.05 less for odd cells (see
  Meshes/Tankhouse/README.md).

## Parts and pivots

| Object | Use | Pivot (X, Y, Z) |
|---|---|---|
| CA_Plate (blade, plating, hanger bar, edge strips) | the blank, moves as a whole | (0, 0, 0) |
| CA_DepositFront / CA_DepositBack | copper sheet on the -Y / +Y face. Rotate about local X at the top edge to peel. Scale Y from 0 to 1 to show growth | on the top edge of each sheet |

Exact pivots (world):

| Object | Pivot |
|---|---|
{rows}

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off, so the deposit pivots are kept.
Instance this mesh 46 times per cell (Instanced Static Mesh or HISM). With 160 cells this is
7,360 cathodes, so instancing is required.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Blade 316L stainless, 3.25 mm thick; hanger bar 304 stainless, copper plated | | Sourced (IsaKidd patents and Mount Isa patent summary) |
| Plating 15 mm down the blade (original Isa design; the BR design extends it to about 55 mm) | | Sourced (Wikipedia, IsaKidd refining technology) |
| PP edge strips on the side edges; bottom edge bare (V-groove) | | Sourced (patent summaries) |
| Harvested cathode about 1 × 1 m, 130–165 kg, 7-day crop common | | Sourced (research file, Wikipedia) |
| Blade {L.BLADE_W:.2f} × {L.BLADE_H:.2f} m below the bar | | Estimated to give about 1 × 1 m of deposit |
| Hanger bar {L.HANGER_L:.2f} × {L.HANGER_W:.3f} × {L.HANGER_H:.3f} m | | Estimated. The length makes the bar end meet the anode lug tips of the next cell on the shared intercell bar |
| Lifting windows {L.WINDOW_W:.2f} m wide at x ±{L.WINDOW_X:.2f}, from {abs(L.WINDOW_Z1):.2f} to {abs(L.WINDOW_Z0):.2f} m below the bar | | Own design (real plates have windows; no dimensions found) |
| Deposit per sheet {DEPOSIT_T*1000:.0f} mm, {2*dw_for_readme():.3f} × {abs(-L.BLADE_H + 0.005 - DEPOSIT_TOP):.3f} m, both sheets about {mass_dep:.0f} kg | | Estimated to land in the sourced 130–165 kg range |

Sources: /mnt/project-files/research/copper-refinery/copper-refinery-equipment.md (§8);
https://en.wikipedia.org/wiki/IsaKidd_refining_technology; US8133366B2 / US7807028 (stainless
electrolytic plates); US20050126906 (hanger bar, Mount Isa Mines).
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def dw_for_readme():
    return L.BLADE_W / 2 - 0.008


def main():
    os.makedirs(OUT, exist_ok=True)
    col, plate, deposits = build()
    dw = dw_for_readme()
    mass = 2 * (2 * dw) * (abs(-L.BLADE_H + 0.005 - DEPOSIT_TOP)) * DEPOSIT_T * 8960
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, mass)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render(res=(1280, 960), samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Cathode.png"), (1.6, -2.4, 0.2), (0, 0, -0.5), lens=40)
    deposits[0].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_Detail.png"), (1.15, -0.95, 0.35), (0.40, 0, -0.10), lens=45)
    deposits[0].hide_render = False


main()
