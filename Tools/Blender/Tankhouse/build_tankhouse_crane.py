"""
build_tankhouse_crane.py - SM_TankhouseCrane (electrode handling crane with a multi-hook bale).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_tankhouse_crane.py
Needs SM_ElectrolyticCell and SM_PermanentCathode .blend files for the previews.

Tankhouse coordinates. The bridge runs along X on rails at y = +-14.4 (top z 8.0), the trolley
runs along Y on the bridge, and the bale hangs on four ropes. The bale carries two hook sets:
anode hooks under the lugs (x +-0.53) and cathode hooks under the hanger bar (x +-0.30).
Modelled pose: bridge over cell 10, trolley over row A, bale at travel height, hooks open.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_TankhouseCrane"
OUT = os.path.join(L.MESHES, "TankhouseCrane")

BRIDGE_X = L.cell_x(10)                 # modelled bridge position
TROLLEY_Y = L.ROW_Y["A"]                # modelled trolley position
TRAVEL_DZ = 1.60                        # bale lift above the seat for travel
BALE_Z = L.SEAT_Z + TRAVEL_DZ           # bale pivot = hook seat (lug underside) level
GIRDER_DX = 1.6                         # girders at bridge_x +- 1.6 (trolley gauge 3.2 m)
GIRDER_TOP = L.CRANE_RAIL_Z + 0.55 + 1.40
TROLLEY_RAIL_Z = GIRDER_TOP + 0.10
DRUM_Z = TROLLEY_RAIL_Z + 0.85
ROPE_TOP_Z = TROLLEY_RAIL_Z + 0.25      # ropes leave the trolley frame here
HEAD_DZ = 1.10                          # sheave block centre above the bale pivot
ANODE_HOOK_X, CATH_HOOK_X = 0.53, 0.30
ANODE_ENGAGE_DY, CATH_ENGAGE_DY = -0.008, 0.006


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    bx, ty = BRIDGE_X, TROLLEY_Y
    rz = L.CRANE_RAIL_Z
    ry = L.CRANE_RAIL_Y

    # --- bridge: two box girders, end trucks with wheels, walkway, panels, buffers ---
    br = pb.Part("TC_Bridge", pivot=(bx, 0.0, rz))
    for s in (-1, 1):
        gx = bx + s * GIRDER_DX
        br.box_mm((gx - 0.35, -ry - 0.3, GIRDER_TOP - 1.40), (gx + 0.35, ry + 0.3, GIRDER_TOP), m["crane"])
        br.box_mm((gx - 0.04, -ry, GIRDER_TOP), (gx + 0.04, ry, TROLLEY_RAIL_Z), m["steel"])  # trolley rail
    for s in (-1, 1):
        y = s * ry
        br.box_mm((bx - 2.4, y - 0.35, rz + 0.30), (bx + 2.4, y + 0.35, rz + 1.10), m["crane"])  # end truck
        for wx in (-1.9, 1.9):
            br.cyl(0.30, 0.16, (bx + wx, y, rz + 0.30), m["grey"], rot=(90, 0, 0), seg=20)
            br.box((0.4, 0.12, 0.1), (bx + wx + 0.5, y, rz + 0.25), m["steel"])
        for ex in (-2.55, 2.55):
            br.cyl(0.12, 0.3, (bx + ex, y, rz + 0.7), m["rubber"], rot=(0, 90, 0), seg=12)  # buffers
        br.box((0.6, 0.5, 0.5), (bx - 1.0, y - s * 0.6, rz + 1.0), m["blue"])           # travel motor
    # walkway on the -X girder with handrail, and an electrical panel house
    wx0 = bx - GIRDER_DX - 1.35
    br.box_mm((wx0, -ry, GIRDER_TOP - 1.45), (bx - GIRDER_DX - 0.35, ry, GIRDER_TOP - 1.40), m["grating"])
    pb.handrail(br, (wx0, -ry, GIRDER_TOP - 1.40), (wx0, ry, GIRDER_TOP - 1.40), m["yellow"])
    br.box_mm((wx0 + 0.05, 4.0, GIRDER_TOP - 1.40), (wx0 + 0.95, 7.0, GIRDER_TOP + 0.6), m["cabinet"])
    # festoon cable rail along the +X girder
    br.box_mm((bx + GIRDER_DX + 0.35, -ry, GIRDER_TOP - 0.5), (bx + GIRDER_DX + 0.45, ry, GIRDER_TOP - 0.4),
              m["steel"])
    br.finish(col)

    # --- trolley: frame, wheels, hoist drum, motor, gearbox ---
    tr = pb.Part("TC_Trolley", pivot=(bx, ty, TROLLEY_RAIL_Z))
    z0 = TROLLEY_RAIL_Z + 0.20
    tr.box_mm((bx - 2.0, ty - 1.6, z0), (bx + 2.0, ty + 1.6, z0 + 0.35), m["crane"])
    for s in (-1, 1):
        for wy in (-1.2, 1.2):
            tr.cyl(0.2, 0.12, (bx + s * GIRDER_DX, ty + wy, TROLLEY_RAIL_Z + 0.2), m["grey"],
                   rot=(0, 90, 0), seg=16)
    for s in (-1, 1):  # drum bearing pedestals
        tr.box((0.3, 0.4, 0.55), (bx + s * 1.1, ty, z0 + 0.6), m["steel"])
    tr.box((0.9, 0.7, 0.7), (bx + 1.55, ty + 0.9, z0 + 0.7), m["blue"])      # hoist motor
    tr.box((0.7, 0.9, 0.8), (bx + 1.55, ty, z0 + 0.75), m["steel"])          # gearbox
    tr.box((0.7, 0.6, 0.6), (bx - 1.55, ty - 1.0, z0 + 0.65), m["blue"])     # trolley drive
    tr.box_mm((bx - 2.0, ty - 1.6, z0 + 1.35), (bx + 2.0, ty + 1.6, z0 + 1.40), m["crane"])  # rain cover
    for sx in (-1, 1):
        for sy in (-1, 1):
            tr.box((0.08, 0.08, 1.0), (bx + sx * 1.95, ty + sy * 1.55, z0 + 0.85), m["crane"])
    # IR camera bracket under the frame (SM_ShortCircuitDetection mounts here)
    tr.box((0.3, 0.3, 0.25), (bx, ty - 1.4, z0 - 0.12), m["steel"])
    tr.finish(col)

    drum = pb.Part("TC_HoistDrum", pivot=(bx, ty, DRUM_Z))
    drum.cyl(0.45, 1.9, (bx, ty, DRUM_Z), m["grey"], rot=(0, 90, 0), seg=32)
    for s in (-1, 1):
        drum.cyl(0.55, 0.05, (bx + s * 0.95, ty, DRUM_Z), m["steel"], rot=(0, 90, 0), seg=32)
    drum.finish(col)

    # --- ropes: four falls, pivot at the trolley; scale local Z with the hoist ---
    head_z = BALE_Z + HEAD_DZ
    rp = pb.Part("TC_Ropes", pivot=(bx, ty, ROPE_TOP_Z))
    for rx in (-0.45, 0.45):
        for rys in (-1.8, 1.8):
            rp.cyl_between((bx + rx, ty + rys, ROPE_TOP_Z), (bx + rx, ty + rys, head_z), 0.014, m["steel"], seg=6)
    rp.finish(col)

    # --- bale: frame, sheave blocks, guide rollers, hook carrier beams ---
    bl = pb.Part("TC_Bale", pivot=(bx, ty, BALE_Z))
    bz0 = BALE_Z + 0.40
    hy = 2.45
    for x in (-ANODE_HOOK_X, -CATH_HOOK_X, CATH_HOOK_X, ANODE_HOOK_X):
        bl.box_mm((bx + x - 0.05, ty - hy, bz0), (bx + x + 0.05, ty + hy, bz0 + 0.18), m["crane"])
    for y in (-hy, -1.2, 0.0, 1.2, hy):
        bl.box_mm((bx - 0.70, ty + y - 0.06, bz0 + 0.18), (bx + 0.70, ty + y + 0.06, bz0 + 0.40), m["crane"])
    bl.box_mm((bx - 0.20, ty - hy, bz0 + 0.40), (bx + 0.20, ty + hy, bz0 + 0.65), m["crane"])  # spine
    for rys in (-1.8, 1.8):
        bl.box((1.2, 0.3, 0.5), (bx, ty + rys, head_z - 0.15), m["crane"])        # sheave block
        for rx in (-0.45, 0.45):
            bl.cyl(0.28, 0.08, (bx + rx, ty + rys, head_z), m["grey"], rot=(0, 90, 0), seg=20)
        bl.box((0.3, 0.3, head_z - 0.4 - bz0 - 0.65), (bx, ty + rys, (head_z - 0.4 + bz0 + 0.65) / 2),
               m["crane"])
    # hook actuators (one per hook beam, at the beam ends)
    for x in (-ANODE_HOOK_X, -CATH_HOOK_X, CATH_HOOK_X, ANODE_HOOK_X):
        for s in (-1, 1):
            bl.cyl_between((bx + x, ty + s * (hy - 0.05), bz0 + 0.09), (bx + x, ty + s * (hy + 0.25), bz0 + 0.09),
                           0.04, m["grey"], seg=10)
    # end guide frames (locate the bale on the cell end walls)
    for s in (-1, 1):
        y = ty + s * (hy + 0.15)
        for x in (-0.55, 0.55):
            bl.box_mm((bx + x - 0.04, y - 0.04, BALE_Z - 0.35), (bx + x + 0.04, y + 0.04, bz0 + 0.4), m["crane"])
        bl.box_mm((bx - 0.60, y - 0.05, bz0 + 0.30), (bx + 0.60, y + 0.05, bz0 + 0.40), m["crane"])
    bl.finish(col)

    # --- hook sets (child of the bale), modelled open, for even cells ---
    ah = pb.Part("TC_AnodeHooks", pivot=(bx, ty, BALE_Z))
    for j in range(L.ANODES_PER_CELL):
        ya = ty + L.anode_y(j, False)
        for s in (-1, 1):
            x0, x1 = sorted((s * 0.505, s * 0.555))
            # plate in the gap on the +Y side of the lug, toe pointing -Y
            ah.box_mm((bx + x0, ya + 0.031, BALE_Z - 0.03), (bx + x1, ya + 0.036, bz0), m["stainless"])
            ah.box_mm((bx + x0, ya + 0.023, BALE_Z - 0.03), (bx + x1, ya + 0.031, BALE_Z - 0.012), m["stainless"])
    ah.finish(col)

    ch = pb.Part("TC_CathodeHooks", pivot=(bx, ty, BALE_Z))
    for k in range(L.CATHODES_PER_CELL):
        yc = ty + L.cathode_y(k, False)
        for s in (-1, 1):
            x0, x1 = s * CATH_HOOK_X - 0.04, s * CATH_HOOK_X + 0.04
            # plate in the gap between the hanger bar and the anode, toe pointing +Y under the bar
            ch.box_mm((bx + x0, yc - 0.0265, BALE_Z - 0.03), (bx + x1, yc - 0.0215, bz0), m["stainless"])
            ch.box_mm((bx + x0, yc - 0.0215, BALE_Z - 0.03), (bx + x1, yc - 0.0135, BALE_Z - 0.012), m["stainless"])
    ch.finish(col)

    pb.ref_human(ref, (BRIDGE_X - 3.0, TROLLEY_Y - 4.0, 0.0))
    return col


def write_readme(col):
    rows = pb.pivot_table([col.name])
    txt = f"""# SM_TankhouseCrane

Electrode handling crane for the electrorefining tankhouse (SM_TankhouseBuilding).
- **Bridge:** double box girder, {2*L.CRANE_RAIL_Y:.1f} m span, on rails along X at y = ±{L.CRANE_RAIL_Y}
  (rail top z {L.CRANE_RAIL_Z}). Travels the whole hall, x {L.CRANE_X_MIN} to {L.CRANE_X_MAX}, from the
  service bay transfer stands to the far end of the cell rows.
- **Trolley:** runs along Y on the girders. One hoist drum with four rope falls carries the bale.
- **Bale:** a 4.9 m frame that lines up with one cell. It carries two hook sets that can work
  separately, so the crane can lift a full anode load, a full cathode load, or both:
  - anode hooks: 2 × 45 hooks at x ±0.53 whose toes slide under the anode lugs (between the anode
    body edge and the capping board);
  - cathode hooks: 2 × 46 hooks at x ±0.30 whose toes slide under the hanger bar where it
    overhangs the blade (11 mm each side).
- **Short-circuit camera:** a bracket under the trolley frame takes the IR camera boom of
  SM_ShortCircuitDetection.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates. Files: `{NAME}.blend`, `{NAME}.fbx`
(FBX_SCALE_NONE, 8 objects). Previews: `Preview_Overview.png`, `Preview_Bale.png` (bale lowered
onto a loaded cell, hooks engaged).

## Origin and placement

- Tankhouse coordinates: the FBX lines up with SM_TankhouseBuilding with no offset.
- Modelled pose: bridge over cell 10 (x {BRIDGE_X:.2f}), trolley over row A (y {TROLLEY_Y}), bale at
  travel height (hook seat z {BALE_Z:.2f}), hooks open.

## Parts, pivots and motion

| Object | Motion | Range |
|---|---|---|
| TC_Bridge | translate X | x {L.CRANE_X_MIN} to {L.CRANE_X_MAX} (pivot x) |
| TC_Trolley | child of the bridge, translate Y | y -12.0 to 12.0 |
| TC_HoistDrum | child of the trolley, rotate about local X. Drum Ø0.9 m, 4-fall reeving on 2 drum grooves: drum turn (rad) = 2 × lift (m) / 0.45 | |
| TC_Ropes | child of the trolley, scale local Z = (rope top z {ROPE_TOP_Z:.2f} − head z) / {ROPE_TOP_Z - BALE_Z - HEAD_DZ:.2f}, where head z = bale pivot z + {HEAD_DZ} | |
| TC_Bale | child of the trolley, translate Z (pivot = hook seat level) | seat in cell {L.SEAT_Z}, transfer stands {L.TRANSFER_SEAT_Z}, travel {BALE_Z:.2f} (max {ROPE_TOP_Z - HEAD_DZ - 0.6:.1f}) |
| TC_AnodeHooks | child of the bale, translate Y: 0 = open, {ANODE_ENGAGE_DY} = toes under the lugs | |
| TC_CathodeHooks | child of the bale, translate Y: 0 = open, +{CATH_ENGAGE_DY} = toes under the hanger bar | |

Exact pivots (tankhouse coordinates):

| Object | Pivot |
|---|---|
{rows}

**Positioning over a cell.** For cell i in a row: bridge pivot x = 0.66 + 1.32·i, trolley pivot
y = row y. The hooks are laid out for the even-cell electrode pattern, so for an odd cell move the
trolley a further -0.05 m in Y.

**Pick sequence (anodes).** Lower the bale from travel height to z {L.SEAT_Z} with the hooks open
(the toes pass down beside the lugs), move TC_AnodeHooks {ANODE_ENGAGE_DY} m, then lift. The toes
reach 7.5 mm under each lug. The cathode hooks do the same under the hanger bars with +{CATH_ENGAGE_DY} m
(toes 6 mm under the bar). `check_tankhouse.py` tests both hook sets: clear while lowering and
engaging, and every electrode caught after a 15 mm lift.
At travel height a carried anode's bottom is {TRAVEL_DZ - 0.88:.2f} m above the seat line, clear of
the electrodes in the other cells.

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off. Attach the trolley to the bridge, the
drum, ropes and bale to the trolley, and the hook sets to the bale. Attach lifted electrodes to the
bale while carried.

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Semi-automatic crane with a multi-hook bale that lifts anodes and cathodes; double lifting bale | | Sourced (research file §8, US4392934, Glencore Technology) |
| Separate anode crane 10 t and cathode crane 3.5 t at Kyshtym | | Sourced (Kuenz press release, AJOT). This crane combines both duties |
| Safe working load about 20 t (45 anodes × 0.38 t = 17.1 t plus the hooks) | | Estimated |
| Span {2*L.CRANE_RAIL_Y:.1f} m, rail z {L.CRANE_RAIL_Z}, girder depth 1.4 m, trolley gauge 3.2 m | | Estimated to suit the building |
| Hook shapes, hook positions, end guide frames | | Own design. The toes are small (6–8 mm) because the gaps between anodes and cathodes are only 15–26 mm |
| Cathode hooks under the hanger bar instead of through the blade windows | | Own simplification. Real IsaKidd plates are lifted by their windows; with a 25 mm hanger bar a fixed window hook could not pass the bar inside the 15 mm gap, so it would need pivoting fingers |
| No operator cab: remote/automatic operation with a walkway and panel house for maintenance | | Sourced: Kuenz remote operating stations; layout estimated |

Sources: /mnt/project-files/copper_refinery_equipment.md §8 (US4392934); research companion §8
(double-lifting bale, automatic operation, [S2]/[S3]); https://www.ajot.com/news/kuenz-automated-anode-and-cathode-handling-cranes-with-remote-operating-stations-ros-for-kyshtym-russia
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview():
    m = L.materials()
    ref = pb.collection("REF")
    anode = L.ref_anode(ref, m["anode_cu"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"),
                          ["CA_Plate", "CA_DepositFront", "CA_DepositBack"])
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    L.instance_collection("SRC_Parts", [anode] + cath + cell)
    loaded = [L.loaded_cell_collection(cell, anode, cath, odd, f"LoadedCell_{odd}") for odd in (0, 1)]
    for i in range(6, 15):
        L.place_instance(ref, loaded[i % 2], (L.cell_x(i), L.ROW_Y["A"], 0), name=f"REF_CellA{i}")
    floor = pb.Part("REF_Floor")
    floor.box_mm((0, -15, -0.62), (30, -3, -0.55), pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
    floor.box_mm((0, -15, -0.05), (30, -12.0, 0.0), m["floor"])
    floor.finish(ref)
    for s in (-1, 1):
        rail = pb.Part(f"REF_Runway{s}")
        rail.box_mm((0, s * L.CRANE_RAIL_Y - 0.3, L.CRANE_RAIL_Z - 1.0), (30, s * L.CRANE_RAIL_Y + 0.3,
                    L.CRANE_RAIL_Z), m["steel"])
        rail.finish(ref)
    pb.setup_render(res=(1600, 900), samples=32)
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (-2.0, -26.0, 13.0), (BRIDGE_X, -4.0, 5.0), lens=26)
    # lower the bale onto cell 10 and engage the hooks
    dz = L.SEAT_Z - BALE_Z
    for n in ("TC_Bale", "TC_AnodeHooks", "TC_CathodeHooks"):
        bpy_obj(n).location.z += dz
    bpy_obj("TC_AnodeHooks").location.y += ANODE_ENGAGE_DY
    bpy_obj("TC_CathodeHooks").location.y += CATH_ENGAGE_DY
    r = bpy_obj("TC_Ropes")
    r.scale.z = (ROPE_TOP_Z - (L.SEAT_Z + HEAD_DZ)) / (ROPE_TOP_Z - BALE_Z - HEAD_DZ)
    pb.render_view(os.path.join(OUT, "Preview_Bale.png"), (BRIDGE_X - 3.2, TROLLEY_Y - 5.5, 3.6),
                   (BRIDGE_X, TROLLEY_Y - 1.0, 1.0), lens=28)


def bpy_obj(n):
    import bpy
    return bpy.data.objects[n]


def main():
    os.makedirs(OUT, exist_ok=True)
    col = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview()


main()
