"""
build_electrolyte_circulation.py - SM_ElectrolyteCirculation (tanks, pumps, filters, heat
exchangers, additive dosing, feed headers and return launders).

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/build_electrolyte_circulation.py

Tankhouse coordinates. The pump room is an annex south of the west end of the hall
(x -32..0, y -27..-15) with its floor at z -5.0, below the hall basement (-3.0), so the
overflow from every cell returns to the circulation tanks by gravity.

Flow: cell overflow -> row return launders (basement) -> return main -> circulation tanks
-> pumps -> filters -> plate heat exchangers (steam heated) -> feed main -> row feed headers
-> cell feed boxes.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

NAME = "SM_ElectrolyteCirculation"
OUT = os.path.join(L.MESHES, "ElectrolyteCirculation")

ANNEX = (-32.0, 0.0, -27.0, -15.0)       # x0, x1, y0, y1
PIT_Z = -5.0
TANKS = [(-27.0, -21.0), (-20.5, -21.0)]
TANK_R, TANK_H = 3.0, 4.0
PUMPS_X = [-15.0, -13.0, -11.0]
PUMP_Y = -19.2                           # casing centre
PUMP_AXIS_Z = PIT_Z + 0.75
FILTERS = [(-8.5, -24.5), (-5.0, -24.5)]
PHE = [(-8.5, -18.0), (-5.0, -18.0)]
HEADER_Z = -1.30                         # row feed headers
LAUNDER_Z = -1.50                        # launder floor
FEED_DY, DRAIN_DY = -2.65, 2.65          # cell flange offsets from the row centreline
MANIFOLD_X, RETURN_X = -1.2, -1.8
X_END = L.cell_x(L.CELLS_PER_ROW - 1) + 0.4


def pipe(p, pts, r, m, seg=12):
    """Polyline pipe through the points, with a sphere at each bend."""
    for a, b in zip(pts[:-1], pts[1:]):
        p.cyl_between(a, b, r, m, seg=seg)
    for q in pts[1:-1]:
        p.sphere(r, q, m, seg=seg)


def annex_shell(m, col):
    x0, x1, y0, y1 = ANNEX
    s = pb.Part("EL_AnnexShell")
    for xa, xb, ya, yb in ((x0, x1, y0, y0 + 0.3), (x0, x1, y1 - 0.3, y1), (x0, x0 + 0.3, y0, y1), (x1 - 0.3, x1, y0, y1)):
        s.box_mm((xa, ya, 0.0), (xb, yb, 5.0), m["cladding"])            # walls above grade
    s.box_mm((x0 - 0.3, y0 - 0.3, 5.0), (x1 + 0.3, y1 + 0.3, 5.3), m["roof"])
    shell_ob = s.finish(col)

    s = pb.Part("EL_AnnexPit")
    s.box_mm((x0, y0, PIT_Z - 0.4), (x1, y1, PIT_Z), m["floor"])
    for xa, xb, ya, yb in ((x0, x1, y0, y0 + 0.3), (x0, x1, y1 - 0.3, y1), (x0, x0 + 0.3, y0, y1), (x1 - 0.3, x1, y0, y1)):
        s.box_mm((xa, ya, PIT_Z), (xb, yb, 0.0), m["concrete"])          # retaining walls
    # bund kerbs around the tanks and acid-proof floor channel to a sump
    s.box_mm((x0 + 0.6, y0 + 0.6, PIT_Z), (-16.8, y0 + 0.8, PIT_Z + 0.4), m["concrete"])
    s.box_mm((-17.0, y0 + 0.6, PIT_Z), (-16.8, y1 - 0.6, PIT_Z + 0.4), m["concrete"])
    s.box((1.2, 1.2, 0.02), (-2.0, -16.2, PIT_Z + 0.005), m["liner"])     # sump grate
    s.finish(col)
    return shell_ob


def stairs_and_crane(m, col):
    """Stair from grade down the west wall, and a monorail beam over the pumps."""
    p = pb.Part("EL_Access")
    x0, _, y0, y1 = ANNEX
    n = 25
    for i in range(n):
        y = y1 - 0.8 - i * (6.0 / n)
        z = -0.2 * (i + 1)
        p.box_mm((x0 + 0.4, y - 0.13, z - 0.05), (x0 + 1.4, y + 0.13, z), m["grating"])
    p.box_mm((x0 + 0.4, y1 - 0.8 - 6.2, PIT_Z - 0.05), (x0 + 1.4, y1 - 0.8 - 6.0 + 0.1, PIT_Z), m["grating"])
    pb.handrail(p, (x0 + 1.4, y1 - 0.8, 0.0), (x0 + 1.4, y1 - 6.8, PIT_Z), m["yellow"], post_step=1.5)
    p.box_mm((x0 + 0.4, y1 - 0.8, -0.05), (x0 + 1.4, y1 - 0.3, 0.0), m["grating"])
    # pump maintenance monorail
    p.box_mm((-16.5, PUMP_Y - 0.1, 3.6), (-9.5, PUMP_Y + 0.1, 3.9), m["yellow"])
    for x in (-16.5, -9.5):
        p.box_mm((x - 0.1, PUMP_Y - 0.1, 3.9), (x + 0.1, PUMP_Y + 0.1, 5.0), m["yellow"])
    return p.finish(col)


def tanks(m, col):
    t = pb.Part("EL_Tanks")
    for i, (x, y) in enumerate(TANKS):
        zc = PIT_Z + 0.3 + TANK_H / 2
        t.cyl(TANK_R, TANK_H, (x, y, zc), m["frp"], seg=40)
        t.cyl(TANK_R + 0.05, 0.1, (x, y, PIT_Z + 0.3 + TANK_H + 0.05), m["frp"], seg=40)   # lid
        t.cyl(TANK_R + 0.2, 0.3, (x, y, PIT_Z + 0.15), m["concrete"], seg=40)               # plinth
        for k in range(4):                                                                 # hoop bands
            t.cyl(TANK_R + 0.02, 0.06, (x, y, PIT_Z + 0.8 + k * 1.0), m["frp"], seg=40)
        t.cyl(0.35, 0.2, (x + 1.5, y, PIT_Z + 0.3 + TANK_H + 0.2), m["frp"], seg=16)        # manway
        t.cyl_between((x - 1.0, y, PIT_Z + 0.3 + TANK_H), (x - 1.0, y, PIT_Z + 0.3 + TANK_H + 1.2), 0.1,
                      m["frp"], seg=10)                                                      # vent
        # outlet nozzle toward the pumps (+X side, low)
        t.cyl_between((x + TANK_R, y + 1.2, PIT_Z + 0.7), (x + TANK_R + 0.5, y + 1.2, PIT_Z + 0.7), 0.15,
                      m["frp"], seg=12)
        # level gauge
        t.box_mm((x - 0.05, y - TANK_R - 0.15, PIT_Z + 0.6), (x + 0.05, y - TANK_R - 0.05, PIT_Z + 0.3 + TANK_H),
                 m["glass"])
        pb.ladder(t, (x - 0.9, y - TANK_R - 0.25, PIT_Z), PIT_Z + 0.3 + TANK_H + 1.0, m["yellow"], facing=0)
    # return main inlets (side nozzles under the liquid level)
    for x, y in TANKS:
        t.cyl_between((x, y + TANK_R - 0.1, -2.6), (x, y + TANK_R + 0.6, -2.6), 0.2, m["frp"], seg=12)
    return t.finish(col)


def pumps(m, col):
    """Three horizontal centrifugal pumps (2 duty, 1 standby). Rotors are separate objects."""
    body = pb.Part("EL_Pumps")
    rotors = []
    for i, x in enumerate(PUMPS_X):
        y, z = PUMP_Y, PUMP_AXIS_Z
        body.box_mm((x - 0.5, y - 0.8, PIT_Z), (x + 0.5, y + 2.4, PIT_Z + 0.25), m["concrete"])   # plinth
        body.box_mm((x - 0.4, y - 0.7, PIT_Z + 0.25), (x + 0.4, y + 2.3, PIT_Z + 0.32), m["steel"])  # baseplate
        body.cyl(0.42, 0.3, (x, y, z), m["blue"], rot=(90, 0, 0), seg=24)                         # volute
        body.cyl_between((x, y - 0.15, z), (x, y - 0.75, z), 0.15, m["blue"], seg=12)             # suction
        body.cyl_between((x, y, z + 0.42), (x, y, z + 0.9), 0.12, m["blue"], seg=12)              # discharge
        body.box((0.3, 0.6, 0.25), (x, y + 0.45, z - 0.25), m["blue"])                           # bearing frame
        body.cyl(0.32, 0.9, (x, y + 1.6, z), m["blue"], rot=(90, 0, 0), seg=20)                   # motor
        body.box((0.5, 0.9, 0.12), (x, y + 1.6, PIT_Z + 0.38), m["steel"])
        body.box_mm((x - 0.18, y + 0.75, z - 0.18), (x + 0.18, y + 1.12, z + 0.18), m["yellow"])  # coupling guard
        r = pb.Part(f"EL_PumpRotor_{i + 1}", pivot=(x, y, z))
        r.cyl(0.33, 0.08, (x, y, z), m["grey"], rot=(90, 0, 0), seg=16)                           # impeller
        for k in range(6):
            a = math.radians(60 * k)
            r.box((0.04, 0.1, 0.26), (x + 0.2 * math.cos(a), y - 0.06, z + 0.2 * math.sin(a)), m["grey"],
                  rot=(0, -60 * k, 0))
        r.cyl_between((x, y, z), (x, y + 1.15, z), 0.04, m["grey"], seg=10)                         # shaft
        rotors.append(r.finish(col))
    return body.finish(col), rotors


def filters_phe_dosing(m, col):
    p = pb.Part("EL_FiltersExchangers")
    flanges = []
    for x, y in FILTERS:      # vertical pressure filters on legs
        p.cyl(1.0, 2.6, (x, y, PIT_Z + 1.0 + 1.3), m["frp"], seg=28)
        p.sphere(1.0, (x, y, PIT_Z + 3.6), m["frp"], seg=24)
        p.cyl(1.0, 0.2, (x, y, PIT_Z + 1.0), m["frp"], seg=28, r2=0.6)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            p.cyl_between((x + 0.8 * math.cos(a), y + 0.8 * math.sin(a), PIT_Z),
                          (x + 0.8 * math.cos(a), y + 0.8 * math.sin(a), PIT_Z + 1.4), 0.06, m["steel"], seg=8)
        p.cyl(0.25, 0.15, (x, y, PIT_Z + 4.65), m["frp"], seg=12)
    for i, (x, y) in enumerate(PHE):   # plate-and-frame heat exchangers (titanium plates)
        p.box_mm((x - 0.5, y - 1.3, PIT_Z), (x + 0.5, y - 1.15, PIT_Z + 2.4), m["blue"])        # fixed frame
        p.box_mm((x - 0.5, y + 1.15, PIT_Z), (x + 0.5, y + 1.3, PIT_Z + 2.4), m["blue"])        # support column
        p.box_mm((x - 0.45, y - 1.15, PIT_Z + 0.3), (x + 0.45, y + 0.4, PIT_Z + 2.2), m["stainless"])  # plate pack
        p.box_mm((x - 0.5, y + 0.4, PIT_Z + 0.2), (x + 0.5, y + 0.55, PIT_Z + 2.3), m["blue"])   # pressure plate
        p.box_mm((x - 0.05, y - 1.15, PIT_Z + 2.3), (x + 0.05, y + 1.15, PIT_Z + 2.45), m["grey"])  # carry bar
        p.box_mm((x - 0.05, y - 1.15, PIT_Z + 0.1), (x + 0.05, y + 1.15, PIT_Z + 0.2), m["grey"])   # guide bar
        for zz in (PIT_Z + 0.6, PIT_Z + 1.9):
            for xx in (x - 0.25, x + 0.25):
                p.cyl_between((xx, y - 1.3, zz), (xx, y - 1.7, zz), 0.08, m["stainless"], seg=10)
        for nm, xx, zz in (("Steam in", x + 0.25, PIT_Z + 1.9), ("Condensate out", x + 0.25, PIT_Z + 0.6)):
            pb.flange(p, (xx, y - 1.7, zz), (90, 0, 0), 0.08, m["steel"], flanges, f"PHE {i + 1} {nm}")
    # additive dosing skid: glue and thiourea tanks with dosing pumps
    sx, sy = -2.0, -25.6
    p.box_mm((sx - 1.4, sy - 0.8, PIT_Z), (sx + 1.4, sy + 0.8, PIT_Z + 0.15), m["steel"])
    for k, xx in enumerate((sx - 0.7, sx + 0.7)):
        p.cyl(0.55, 1.5, (xx, sy, PIT_Z + 0.95), m["pp"], seg=20)
        p.box((0.3, 0.2, 0.25), (xx, sy + 0.65, PIT_Z + 0.3), m["blue"])
        p.cyl(0.2, 0.3, (xx, sy, PIT_Z + 1.85), m["blue"], seg=12)                             # mixer
    p.box_mm((-0.9, -26.6, PIT_Z), (-0.35, -25.4, PIT_Z + 2.0), m["cabinet"])                 # dosing panel
    return p.finish(col), flanges


def annex_piping(m, col):
    """Suction header, discharge header, filter and PHE piping, feed main up into the basement."""
    p = pb.Part("EL_AnnexPiping")
    flanges = []
    zs = PIT_Z + 0.7
    ys = PUMP_Y - 0.75
    # suction header from both tank outlets along the pumps
    p.cyl_between((TANKS[0][0] + TANK_R + 0.5, TANKS[0][1] + 1.2, zs), (TANKS[1][0] + TANK_R + 0.5, TANKS[0][1] + 1.2, zs),
                  0.15, m["frp"])
    pipe(p, [(TANKS[1][0] + TANK_R + 0.5, TANKS[1][1] + 1.2, zs), (TANKS[1][0] + TANK_R + 0.5, ys, zs),
             (PUMPS_X[-1], ys, zs)], 0.15, m["frp"])
    for x in PUMPS_X:
        p.cyl(0.2, 0.25, (x, ys + 0.08, zs), m["grey"], rot=(90, 0, 0), seg=12)   # suction valve
    # discharge header at z PIT+2.2 to the filters, then to the PHEs, then the feed main
    zd = PIT_Z + 2.2
    for x in PUMPS_X:
        p.cyl_between((x, PUMP_Y, PUMP_AXIS_Z + 0.9), (x, PUMP_Y, zd), 0.12, m["frp"], seg=12)
        p.cyl(0.17, 0.2, (x, PUMP_Y, PUMP_AXIS_Z + 1.2), m["grey"], seg=12)        # discharge valve
    pipe(p, [(PUMPS_X[0], PUMP_Y, zd), (FILTERS[0][0], PUMP_Y, zd), (FILTERS[0][0], FILTERS[0][1] + 1.0, zd)],
         0.14, m["frp"])
    p.cyl_between((FILTERS[0][0], FILTERS[0][1] + 1.0, zd), (FILTERS[1][0], FILTERS[1][1] + 1.0, zd), 0.14, m["frp"])
    # filter outlets (bottom) to the PHE inlets
    zo = PIT_Z + 0.6
    for (fx, fy), (hx, hy) in zip(FILTERS, PHE):
        pipe(p, [(fx, fy, PIT_Z + 0.9), (fx, fy, zo - 0.2), (fx + 1.3, fy, zo - 0.2), (fx + 1.3, hy - 1.7, zo - 0.2),
                 (hx - 0.25, hy - 1.7, zo - 0.2), (hx - 0.25, hy - 1.7, zo)], 0.1, m["frp"])
    # PHE outlets join the feed main, which rises and runs north into the hall basement
    for hx, hy in PHE:
        pipe(p, [(hx - 0.25, hy - 1.7, PIT_Z + 1.9), (hx - 0.25, hy - 1.7, PIT_Z + 3.2),
                 (hx - 0.25, -16.0, PIT_Z + 3.2)], 0.1, m["frp"])
    pipe(p, [(PHE[0][0] - 0.25, -16.0, PIT_Z + 3.2), (MANIFOLD_X, -16.0, PIT_Z + 3.2), (MANIFOLD_X, -16.0, HEADER_Z),
             (MANIFOLD_X, -12.6, HEADER_Z)], 0.16, m["frp"])
    # bleed take-off to the liberator cells (stub)
    pipe(p, [(PHE[1][0] - 0.25, -16.6, PIT_Z + 3.2), (-0.6, -16.6, PIT_Z + 3.2)], 0.05, m["frp"], seg=10)
    pb.flange(p, (-0.6, -16.6, PIT_Z + 3.2), (0, 90, 0), 0.05, m["frp"], flanges, "Bleed to liberator cells")
    return p.finish(col), flanges


def basement_piping(m, col):
    """Feed manifold and row headers with cell risers; return launders and return main."""
    p = pb.Part("EL_FeedHeaders")
    ys = [ry + FEED_DY for ry in L.ROW_Y.values()]
    p.cyl_between((MANIFOLD_X, -12.6, HEADER_Z), (MANIFOLD_X, max(ys), HEADER_Z), 0.16, m["frp"])
    for y in ys:
        p.cyl_between((MANIFOLD_X, y, HEADER_Z), (X_END, y, HEADER_Z), 0.10, m["frp"], seg=12)
        p.cyl(0.14, 0.2, (MANIFOLD_X + 0.4, y, HEADER_Z), m["grey"], rot=(0, 90, 0), seg=12)   # row valve
        for i in range(L.CELLS_PER_ROW):
            x = L.cell_x(i)
            p.cyl_between((x, y, HEADER_Z), (x, y, -1.025), 0.03, m["frp"], seg=8)
            p.cyl(0.05, 0.04, (x, y, -1.12), m["grey"], seg=8)                                  # flow valve
        # hangers every 4 cells from the cell support beams' level
        for i in range(0, L.CELLS_PER_ROW, 4):
            x = L.cell_x(i) + 0.66
            p.box_mm((x - 0.03, y - 0.15, HEADER_Z - 0.14), (x + 0.03, y + 0.15, HEADER_Z - 0.10), m["steel"])
            p.box_mm((x - 0.03, y - 0.02, HEADER_Z - 0.10), (x + 0.03, y + 0.02, -0.62), m["steel"])
    feed = p.finish(col)

    r = pb.Part("EL_ReturnLaunders")
    for ry in L.ROW_Y.values():
        y = ry + DRAIN_DY
        r.box_mm((RETURN_X - 0.2, y - 0.25, LAUNDER_Z - 0.05), (X_END, y + 0.25, LAUNDER_Z), m["frp"])
        for s in (-1, 1):
            r.box_mm((RETURN_X - 0.2, y + s * 0.25 - 0.02, LAUNDER_Z), (X_END, y + s * 0.25 + 0.02, -1.15), m["frp"])
        r.box_mm((X_END - 0.02, y - 0.25, LAUNDER_Z), (X_END + 0.02, y + 0.25, -1.15), m["frp"])
        for i in range(0, L.CELLS_PER_ROW, 4):
            x = L.cell_x(i) + 0.66
            r.box_mm((x - 0.03, y - 0.3, LAUNDER_Z - 0.09), (x + 0.03, y + 0.3, LAUNDER_Z - 0.05), m["steel"])
            r.box_mm((x - 0.03, y + 0.28, LAUNDER_Z - 0.09), (x + 0.03, y + 0.32, -0.62), m["steel"])
        # drop from the launder's west end into the return main
        r.cyl_between((RETURN_X, y, LAUNDER_Z), (RETURN_X, y, -2.0), 0.15, m["frp"], seg=12)
    yhi = max(ry + DRAIN_DY for ry in L.ROW_Y.values())
    pipe(r, [(RETURN_X, yhi, -2.0), (RETURN_X, -16.5, -2.0), (RETURN_X, -16.5, -2.6),
             (TANKS[0][0], -16.5, -2.6), (TANKS[0][0], TANKS[0][1] + TANK_R + 0.6, -2.6)], 0.2, m["frp"])
    r.cyl_between((TANKS[1][0], -16.5, -2.6), (TANKS[1][0], TANKS[1][1] + TANK_R + 0.6, -2.6), 0.2, m["frp"])
    ret = r.finish(col)
    return feed, ret


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    col = pb.collection(NAME)
    pb.collection("REF")
    shell = annex_shell(m, col)
    stairs_and_crane(m, col)
    tanks(m, col)
    pumps(m, col)
    _, fl1 = filters_phe_dosing(m, col)
    _, fl2 = annex_piping(m, col)
    basement_piping(m, col)
    return col, shell, fl1 + fl2


def write_readme(col, flanges):
    rows = pb.pivot_table([col.name])
    fl = "\n".join(f"| {n} | {p} |" for n, p in flanges)
    cells = 4 * L.CELLS_PER_ROW
    vol = 2 * 3.14159 * TANK_R ** 2 * (TANK_H - 1.2)
    txt = f"""# SM_ElectrolyteCirculation

Electrolyte circulation for the tankhouse. The electrolyte is kept at 60–65 °C, filtered and dosed
with additives, and fed to every cell.
- **Pump room annex:** south of the hall's west end, x {ANNEX[0]} to {ANNEX[1]}, y {ANNEX[2]} to {ANNEX[3]},
  floor z {PIT_Z} (below the hall basement, so the cell overflow returns by gravity). Stair down
  from grade at the west wall; monorail over the pumps.
- **Circulation tanks:** 2 FRP tanks Ø{2 * TANK_R:.0f} × {TANK_H:.0f} m, about {vol:.0f} m³ working volume in total.
- **Pumps:** 3 horizontal centrifugal pumps (2 duty, 1 standby). Each rotor (impeller, shaft,
  coupling hub) is a separate object that spins about its local Y axis.
- **Filters:** 2 vertical pressure filters.
- **Heat exchangers:** 2 plate-and-frame exchangers with titanium plates, steam heated.
- **Additive dosing:** glue and thiourea tanks with dosing pumps on one skid.
- **Basement:** a feed manifold at x {MANIFOLD_X} supplies four row feed headers (one under the feed
  flanges of each row, z {HEADER_Z}), each with a riser and flow valve to every cell. The cells
  overflow into four open return launders (floor z {LAUNDER_Z}), which drain at the west end into the
  return main back to the tanks.

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates (lines up with SM_TankhouseBuilding and
SM_ElectrolyticCell). Files: `{NAME}.blend`, `{NAME}.fbx` (FBX_SCALE_NONE). Previews:
`Preview_PumpRoom.png` (shell hidden), `Preview_Basement.png` (hall basement with headers and
launders, cells shown).

## Connection points

| Point | Position (tankhouse) |
|---|---|
| Cell feed risers end at each cell's feed flange | (0.66 + 1.32·i, row y {FEED_DY}, -1.025) |
| Cell drain flanges discharge into the launders | (0.66 + 1.32·i, row y +{DRAIN_DY}, -1.0) |
{fl}

The bleed line to SM_LiberatorCells is left as a stub at the annex's east wall. The route to the
liberator annex at the far east end of the hall is open; run it along the south wall of the hall.

## Parts and pivots

| Object | Use |
|---|---|
| EL_AnnexShell | walls above grade and roof; hide for cutaways |
| EL_AnnexPit | pit floor, retaining walls, bund kerbs, sump |
| EL_Access | stair, monorail |
| EL_Tanks, EL_Pumps, EL_FiltersExchangers, EL_AnnexPiping | static |
| EL_PumpRotor_1..3 | rotate about local Y (the pump shaft). About 1,480 rpm (4-pole motor, estimated) |
| EL_FeedHeaders, EL_ReturnLaunders | static, basement |

| Object | Pivot |
|---|---|
{rows}

## Dimensions and design

| Item | Value | Status |
|---|---|---|
| Electrolyte 60–65 °C in, 55–60 °C out; 40–50 g/L Cu, 180–200 g/L H2SO4; glue 1–10 mg/L | | Sourced (research companion §8) |
| Flow 0.015–0.02 m³/min per cell → {cells} cells × 0.02 = {cells * 0.02 * 60:.0f} m³/h | | Sourced rate, my total |
| Pump room under the cell floor; titanium plate heat exchangers | | Sourced (research file §8) |
| Tanks, pumps, filters, heat exchanger sizes and the annex layout | | Estimated |
| Gravity return with a pump room below the hall basement | | Own design |

Sources: /mnt/project-files/copper_refinery_equipment.md §8; research companion §8 ([S5], [S6]).
"""
    L.write(os.path.join(OUT, "README.md"), txt)


def preview(shell):
    ref = pb.collection("REF")
    bld = L.load_objects(L.asset_path("Tankhouse", "SM_TankhouseBuilding"),
                         ["TH_Frame", "TH_OperatingFloor", "TH_Basement", "TH_Walls"])
    for o in bld:
        ref.objects.link(o)
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar"])
    src = L.instance_collection("SRC_Cell", cell)
    for r, ry in L.ROW_Y.items():
        for i in range(0, 12):
            L.place_instance(ref, src, (L.cell_x(i), ry, 0), name=f"REF_Cell{r}{i}")
    pb.ref_human(ref, (-13.0, -21.5, PIT_Z))
    pb.setup_render(res=(1600, 900), samples=32)
    shell.hide_render = True
    by = {o.name: o for o in bld}
    by["TH_Walls"].hide_render = True
    pb.render_view(os.path.join(OUT, "Preview_PumpRoom.png"), (-2.0, -36.0, 6.0), (-15.0, -20.0, -3.5), lens=24)
    L.ref_lights(ref, [(x, y, -0.9) for x in (4, 12, 20, 28) for y in (-11.5, -6.3, 0.0)], 600.0)
    pb.render_view(os.path.join(OUT, "Preview_Basement.png"), (-0.5, -12.3, -2.2), (25.0, -4.0, -1.3), lens=20)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, shell, flanges = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, flanges)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    preview(shell)


main()
