"""
build_slag_cooling_yard.py - SM_SlagCoolingYard.

Run:  blender -b --factory-startup --python Tools/Blender/build_slag_cooling_yard.py

Shares the flash furnace origin (Blender +X = east, +Y = north, assumed).
Contents, in carrier travel order:
  pit apron (z -5.5, east of the slag pot pit) -> 8 % ramp north to grade ->
  cooling pad with rows of pot stations and water spray headers ->
  tipping station and breaking pit (z -3.5) -> loader exit ramp west toward the concentrator.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "Meshes", "SlagCoolingYard")
NAME = "SM_SlagCoolingYard"

# ---------------------------------------------------------------------------
# Layout (flash furnace coordinates, metres). All estimated / own design.
# ---------------------------------------------------------------------------
PIT_Z = -5.5                       # slag pot pit floor (from SM_SlagPots)
APRON = (50.0, -2.0, 70.0, 30.0)   # x0, y0, x1, y1 of the turning apron at pit level
RAMP_X = (56.0, 66.0)              # ramp lane, 10 m wide
RAMP_Y = (30.0, 99.0)              # 69 m run for 5.5 m rise = 8.0 %
PAD = (-20.0, 99.0, 66.0, 175.0)   # cooling pad at grade
ROWS_Y = (111.0, 141.0, 149.0)     # pot station rows A, B, C (pot centres)
ROW_FACING = (+1, -1, +1)          # carrier front direction (+1 north, -1 south) at each row
STATION_X0, STATION_PITCH, STATIONS = -12.0, 8.0, 9
HEADER_Z = 6.5                     # spray header height
HEADER_Y = (106.0, 145.0)          # behind row A, between rows B and C
TIP_Y = 175.0                      # tipping edge
CURB_W = 0.8                       # wheel stop curb width (on the pad side)
BREAK_Z = -3.5                     # breaking pit floor
BREAK = (-20.0, 175.0, 66.0, 203.0)
TIP_BAYS_X = (0.0, 20.0, 40.0)
EXIT_Y = (182.0, 192.0)            # loader exit ramp, 10 % up to grade going west
EXIT_X = (-55.0, -20.0)
POND = (-34.0, 110.0, -22.0, 150.0)  # settling pond for spray run-off
POND_Z = -3.0


def wall(p, x0, y0, x1, y1, z0, z1, m):
    """Straight retaining wall, axis aligned box."""
    p.box_mm((min(x0, x1), min(y0, y1), z0), (max(x0, x1), max(y0, y1), z1), m)


def build():
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(NAME)
    ref = pb.collection("REF")
    log = []                                   # connection points for the README

    conc = pb.mat("M_Concrete", (0.55, 0.54, 0.52), 0.0, 0.85)
    conc_dark = pb.mat("M_Concrete_Stained", (0.32, 0.3, 0.28), 0.0, 0.9)
    plate = pb.mat("M_Steel_WearPlate", (0.22, 0.2, 0.19), 0.8, 0.55)
    steel = pb.mat("M_Steel_Galv", (0.6, 0.62, 0.63), 0.9, 0.4)
    pipe = pb.mat("M_Pipe_Water_Blue", (0.08, 0.25, 0.6), 0.3, 0.4)
    yellow = pb.mat("M_Safety_Yellow", (0.9, 0.7, 0.05), 0.1, 0.5)
    grate = pb.mat("M_Grating", (0.25, 0.25, 0.26), 0.8, 0.5)
    water = pb.mat("M_Water_Settling", (0.12, 0.16, 0.12), 0.0, 0.05)
    lamp = pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0))
    clad = pb.mat("M_Cladding_Grey", (0.45, 0.47, 0.5), 0.5, 0.5)

    # =====================================================================
    # YARD_PitApronRamp: apron at pit level, 8 % ramp, retaining walls
    # =====================================================================
    g = pb.Part("YARD_PitApronRamp", pivot=(RAMP_X[0], RAMP_Y[0], PIT_Z))
    ax0, ay0, ax1, ay1 = APRON
    g.box_mm((ax0, ay0, PIT_Z - 0.5), (ax1, ay1, PIT_Z), conc_dark)
    wall(g, ax0, ay0 - 0.6, ax1 + 0.6, ay0, PIT_Z - 0.5, 1.0, conc)             # south wall
    wall(g, ax1, ay0, ax1 + 0.6, ay1 + 0.6, PIT_Z - 0.5, 1.0, conc)             # east wall
    wall(g, ax0, ay1, RAMP_X[0] - 0.6, ay1 + 0.6, PIT_Z - 0.5, 1.0, conc)      # north wall, west of ramp
    wall(g, RAMP_X[1] + 0.6, ay1, ax1 + 0.6, ay1 + 0.6, PIT_Z - 0.5, 1.0, conc)
    # ramp slab (sloped prism in the YZ plane, extruded along X)
    y0, y1 = RAMP_Y
    g.poly_prism([(y0, PIT_Z), (y1, 0.0), (y1, -0.5), (y0, PIT_Z - 0.5)],
                 RAMP_X[0], RAMP_X[1], conc_dark, plane='YZ')
    # side walls: bottom follows the ramp, top is a 1 m parapet above grade
    for xa, xb in ((RAMP_X[0] - 0.6, RAMP_X[0]), (RAMP_X[1], RAMP_X[1] + 0.6)):
        g.poly_prism([(ay1, PIT_Z - 0.5), (y1, -0.5), (y1, 1.0), (ay1, 1.0)], xa, xb, conc, plane='YZ')
    # yellow kerb lines along the walls
    for x in (RAMP_X[0] + 0.15, RAMP_X[1] - 0.15):
        g.poly_prism([(y0, PIT_Z + 0.01), (y1, 0.01), (y1, -0.01), (y0, PIT_Z - 0.01)],
                     x - 0.1, x + 0.1, yellow, plane='YZ')
    g.finish(col)
    log.append(("Pit apron west edge, joins the slag pot pit", f"x = {ax0}, y {ay0} to {ay1}, floor z = {PIT_Z}"))
    log.append(("Ramp foot / ramp top", f"({sum(RAMP_X)/2}, {y0}, {PIT_Z}) / ({sum(RAMP_X)/2}, {y1}, 0.0), 8.0 %"))

    # =====================================================================
    # YARD_Pad: cooling pad slab, drain trenches
    # =====================================================================
    px0, py0, px1, py1 = PAD
    pad = pb.Part("YARD_Pad", pivot=(px0, py0, 0))
    pad.box_mm((px0, py0, -0.4), (px1, py1 - CURB_W, 0.0), conc)
    # darker wheel paths / pot plate surrounds are separate below; trenches along the header lines
    for hy in HEADER_Y:
        pad.box_mm((px0, hy - 0.4, -0.02), (STATION_X0 + STATION_PITCH * STATIONS, hy + 0.4, 0.005), grate)
    pad.box_mm((px0, py0, -0.02), (px0 + 0.8, py1 - CURB_W, 0.005), grate)          # collector to pond
    pad.finish(col)

    # =====================================================================
    # YARD_PotStations: steel set-down plates, station posts with numbers
    # =====================================================================
    st = pb.Part("YARD_PotStations", pivot=(STATION_X0, ROWS_Y[0], 0))
    stations = []
    for r, (ry, face) in enumerate(zip(ROWS_Y, ROW_FACING)):
        for i in range(STATIONS):
            x = STATION_X0 + STATION_PITCH * i
            st.box((5.0, 5.0, 0.06), (x, ry, 0.03), plate)
            # painted straddle guide lines for the carrier wheels (5.7 m track)
            for s in (-1, 1):
                st.box((0.15, 9.0, 0.01), (x + s * 2.43, ry + face * 2.5, 0.005), yellow)
            stations.append((f"{'ABC'[r]}{i + 1}", x, ry, 90 if face > 0 else -90))
    st.finish(col)

    # =====================================================================
    # YARD_SprayHeaders: overhead water headers on posts, one nozzle drop per pot
    # =====================================================================
    sp = pb.Part("YARD_SprayHeaders", pivot=(STATION_X0, HEADER_Y[0], 0))
    xs = [STATION_X0 - STATION_PITCH / 2 + STATION_PITCH * i for i in range(STATIONS + 1)]
    nozzles = []
    for hy in HEADER_Y:
        for x in xs:
            sp.box((0.3, 0.3, HEADER_Z + 0.3), (x, hy, (HEADER_Z + 0.3) / 2), steel)
            sp.box((0.6, 0.6, 0.05), (x, hy, 0.025), steel)
            sp.box((0.25, 1.4, 0.2), (x, hy, HEADER_Z + 0.3), steel)          # cross arm
        sp.cyl_between((xs[0] - 1, hy, HEADER_Z + 0.5), (xs[-1], hy, HEADER_Z + 0.5), 0.1, pipe, seg=12)
        # nozzle drops toward each pot in the adjacent row(s)
        for ry in ROWS_Y:
            if abs(ry - hy) > 6:
                continue
            for i in range(STATIONS):
                x = STATION_X0 + STATION_PITCH * i
                tip = Vector((x, hy + (ry - hy) * 0.35, HEADER_Z - 0.6))
                sp.cyl_between((x, hy, HEADER_Z + 0.5), tip, 0.035, pipe, seg=8)
                sp.cyl(0.07, 0.15, tip, steel, seg=8)
                nozzles.append(tip)
    # supply main along the west edge from the pump house
    sp.cyl_between((xs[0] - 1, HEADER_Y[0], HEADER_Z + 0.5), (xs[0] - 1, HEADER_Y[1], HEADER_Z + 0.5),
                   0.12, pipe, seg=12)
    sp.cyl_between((xs[0] - 1, HEADER_Y[0], HEADER_Z + 0.5), (xs[0] - 1, HEADER_Y[0], 0.3), 0.12, pipe, seg=12)
    sp.cyl_between((xs[0] - 1, HEADER_Y[0], 0.3), (-24.0, HEADER_Y[0], 0.3), 0.12, pipe, seg=12)
    pb.flange(sp, (-24.0, HEADER_Y[0], 0.3), (0, 90, 0), 0.12, steel, log, "Spray water supply flange (from pump house)")
    sp.finish(col)

    # =====================================================================
    # YARD_TippingStation: wheel stop curb, armoured tipping wall, bay markers
    # =====================================================================
    bx0, by0, bx1, by1 = BREAK
    tp = pb.Part("YARD_TippingStation", pivot=(TIP_BAYS_X[1], TIP_Y, 0))
    tp.box_mm((bx0, TIP_Y - CURB_W, -0.4), (bx1, TIP_Y, 1.0), conc)                # wheel stop curb
    tp.box_mm((bx0, TIP_Y, BREAK_Z - 0.5), (bx1, TIP_Y + 0.8, 0.0), conc)          # tipping wall
    tp.box_mm((bx0, TIP_Y + 0.8, BREAK_Z), (bx1, TIP_Y + 0.88, 0.0), plate)        # wear plates
    for x in TIP_BAYS_X:
        tp.box_mm((x - 3.4, TIP_Y - CURB_W - 0.02, 0.2), (x - 2.9, TIP_Y + 0.02, 0.8), yellow)
        tp.box_mm((x + 2.9, TIP_Y - CURB_W - 0.02, 0.2), (x + 3.4, TIP_Y + 0.02, 0.8), yellow)
        tp.box_mm((x - 2.85, TIP_Y - 14, 0.0), (x - 2.0, TIP_Y - CURB_W, 0.01), yellow)  # approach lines
        tp.box_mm((x + 2.0, TIP_Y - 14, 0.0), (x + 2.85, TIP_Y - CURB_W, 0.01), yellow)
    tp.finish(col)

    # =====================================================================
    # YARD_BreakingPit: pit floor, walls, loader exit ramp (10 %) to the west
    # =====================================================================
    bp = pb.Part("YARD_BreakingPit", pivot=(bx0, by0, BREAK_Z))
    bp.box_mm((bx0, by0, BREAK_Z - 0.5), (bx1, by1, BREAK_Z), conc_dark)
    wall(bp, bx1, by0, bx1 + 0.6, by1 + 0.6, BREAK_Z - 0.5, 1.0, conc)        # east
    wall(bp, bx0 - 0.6, by1, bx1 + 0.6, by1 + 0.6, BREAK_Z - 0.5, 1.0, conc)  # north
    wall(bp, bx0 - 0.6, by0, bx0, EXIT_Y[0], BREAK_Z - 0.5, 1.0, conc)        # west, south of exit
    wall(bp, bx0 - 0.6, EXIT_Y[1], bx0, by1, BREAK_Z - 0.5, 1.0, conc)        # west, north of exit
    ex0, ex1 = EXIT_X
    bp.poly_prism([(ex1, BREAK_Z), (ex0, 0.0), (ex0, -0.5), (ex1, BREAK_Z - 0.5)],
                  EXIT_Y[0], EXIT_Y[1], conc_dark, plane='XZ')
    for ya, yb in ((EXIT_Y[0] - 0.6, EXIT_Y[0]), (EXIT_Y[1], EXIT_Y[1] + 0.6)):
        bp.poly_prism([(ex1, BREAK_Z - 0.5), (ex0, -0.5), (ex0, 1.0), (ex1, 1.0)], ya, yb, conc, plane='XZ')
    bp.finish(col)
    log.append(("Breaking pit floor", f"x {bx0} to {bx1}, y {by0} to {by1}, z = {BREAK_Z}"))
    log.append(("Loader exit ramp top (toward the concentrator ROM bin)",
                f"({ex0}, {sum(EXIT_Y)/2}, 0.0), 10 m wide, heading west"))

    # =====================================================================
    # YARD_SettlingPond + YARD_PondWater + YARD_PumpHouse
    # =====================================================================
    qx0, qy0, qx1, qy1 = POND
    pd = pb.Part("YARD_SettlingPond", pivot=(qx0, qy0, POND_Z))
    pd.box_mm((qx0, qy0, POND_Z - 0.4), (qx1, qy1, POND_Z), conc_dark)
    wall(pd, qx0 - 0.4, qy0 - 0.4, qx1 + 0.4, qy0, POND_Z - 0.4, 0.3, conc)
    wall(pd, qx0 - 0.4, qy1, qx1 + 0.4, qy1 + 0.4, POND_Z - 0.4, 0.3, conc)
    wall(pd, qx0 - 0.4, qy0, qx0, qy1, POND_Z - 0.4, 0.3, conc)
    wall(pd, qx1, qy0, qx1 + 0.4, qy1, POND_Z - 0.4, 0.3, conc)
    wall(pd, qx0, (qy0 + qy1) / 2 - 0.2, qx1, (qy0 + qy1) / 2 + 0.2, POND_Z, -0.6, conc)   # weir between cells
    # run-off inlet chute from the pad collector trench
    pd.box_mm((qx1, HEADER_Y[1] - 0.4, -0.6), (px0, HEADER_Y[1] + 0.4, 0.0), grate)
    pd.finish(col)
    pw = pb.Part("YARD_PondWater", pivot=(qx0, qy0, -0.8))
    pw.box_mm((qx0, qy0, -0.82), (qx1, qy1, -0.8), water)
    pw.finish(col)
    ph = pb.Part("YARD_PumpHouse", pivot=(-30.0, 100.0, 0))
    ph.box_mm((-34.0, 100.0, -0.3), (-26.0, 106.0, 0.0), conc)
    ph.box_mm((-33.8, 100.2, 0.0), (-26.2, 105.8, 3.5), clad)
    ph.poly_prism([(100.0, 3.5), (106.0, 3.5), (103.0, 4.3)], -34.0, -26.0, clad, plane='YZ')
    ph.box_mm((-26.25, 102.0, 0.0), (-26.15, 104.0, 2.4), steel)                  # door
    ph.cyl_between((-30.0, 106.0, 0.3), (-30.0, qy0 + 2, 0.3), 0.12, pipe, seg=12)  # suction from pond
    ph.cyl_between((-30.0, qy0 + 2, 0.3), (-30.0, qy0 + 2, POND_Z + 0.5), 0.12, pipe, seg=12)
    ph.cyl_between((-26.0, HEADER_Y[0], 0.3), (-24.0, HEADER_Y[0], 0.3), 0.12, pipe, seg=12)
    pb.flange(ph, (-34.2, 103.0, 0.5), (0, 90, 0), 0.08, steel, log, "Make-up water / power entry (pump house west wall)")
    ph.finish(col)

    # =====================================================================
    # YARD_LightMasts: 25 m masts with flood heads
    # =====================================================================
    lm = pb.Part("YARD_LightMasts", pivot=(px0, py0, 0))
    for x, y in ((px0 + 1.5, py0 + 1.5), (px1 + 2.0, py0 + 1.5), (px0 + 1.5, TIP_Y - 3),
                 (px1 + 2.0, TIP_Y - 3), (px1 + 2.0, 60.0), (sum(TIP_BAYS_X) / 3, by1 + 2.0)):
        lm.cyl(0.35, 0.8, (x, y, 0.4), conc, seg=12)
        lm.cyl_between((x, y, 0.8), (x, y, 25.0), 0.25, steel, seg=10, r2=0.12)
        lm.box((2.4, 1.2, 0.3), (x, y, 25.2), steel)
        for dx in (-0.7, 0.0, 0.7):
            lm.box((0.6, 0.5, 0.08), (x + dx, y, 25.0), lamp)
    lm.finish(col)

    # =====================================================================
    # REF: proxy pots on some stations, human, ground, slag heap in the pit
    # =====================================================================
    potm = pb.mat("M_REF_Pot", (0.25, 0.22, 0.2), 0.7, 0.6)
    hot = pb.mat("M_REF_Slag_Hot", (1.0, 0.3, 0.05), 0, 0.5, emit=((1, 0.3, 0.05), 4.0))
    cold = pb.mat("M_REF_Slag_Cold", (0.12, 0.11, 0.11), 0.1, 0.8)
    rp = pb.Part("REF_Pots")
    for k, (_, x, y, _) in enumerate(stations):
        if k % 3 == 2:
            continue
        rp.cyl(1.2, 2.6, (x, y, 1.3), potm, seg=24, r2=1.8)
        rp.cyl(1.65, 0.05, (x, y, 2.35), hot if k < 6 else cold, seg=24)
    rp.finish(ref)
    rh = pb.Part("REF_SlagHeap")
    import random
    random.seed(4)
    for i in range(40):
        x = random.uniform(-15, 60)
        y = random.uniform(179, 200)
        s = random.uniform(0.8, 2.2)
        rh.box((s, s * 0.8, s * 0.6), (x, y, BREAK_Z + s * 0.25), cold,
               rot=(random.uniform(0, 40), random.uniform(0, 40), random.uniform(0, 180)))
    rh.finish(ref)
    pb.ref_human(ref, (61.0, 100.0, 0.0))
    # grade at z=0 around the excavated areas, holes left for the pits, ramps and pond
    pb.ref_ground(ref, (-120, -20, 160, 260),
                  [(ax0 - 2, ay0 - 0.6, ax1 + 0.6, ay1 + 0.6),            # apron (west of x 50 is the pot pit)
                   (RAMP_X[0] - 0.6, ay1, RAMP_X[1] + 0.6, py0),         # ramp
                   (bx0 - 0.6, by0, bx1 + 0.6, by1 + 0.6),               # breaking pit
                   (EXIT_X[0], EXIT_Y[0] - 0.6, bx0, EXIT_Y[1] + 0.6),   # loader exit ramp
                   (qx0 - 0.4, qy0 - 0.4, qx1 + 0.4, qy1 + 0.4)])        # settling pond
    return col, log, stations, nozzles


def write_readme(col, log, stations, nozzles):
    rows = pb.pivot_table([col.name])
    conn = "\n".join(f"| {a} | {b} |" for a, b in log)
    st_rows = "\n".join(f"| {n} | ({x:.1f}, {y:.1f}, 0.0) | {yaw:+d}° |" for n, x, y, yaw in stations)
    txt = f"""# SM_SlagCoolingYard

Slag pot cooling yard with the carrier ramp out of the slag pot pit, pot cooling stations with
water sprays, a tipping station over a breaking pit, a settling pond and a pump house. Built in
Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/build_slag_cooling_yard.py`.

## Placement and layout

Shares the flash furnace origin: place at (0, 0, 0) with no rotation, like SM_SlagPots.
Blender +X is taken as east and +Y as north. The acid plant runs east from x = 69.6 with its
tank farm to the north, so everything here stays at x ≤ 70.6 (the apron's east wall). That
boundary is my assumption, since I could not see the acid plant layout from the cloud.

Carrier route: pit (pots at (46.0, 8.8) and (46.0, 15.3), z -5.5) → turning apron east of the
pit (x 50-70, y -2 to 30, z -5.5) → 10 m wide ramp at x 56-66 climbing north at 8.0 % to grade at
y = 99 → north-south haul lane x 56-66 along the east side of the pad → aisles between the rows →
tipping station at y = 175. The pit wall layout in SM_SlagPots is not known here; the apron
assumes the pit is open on its east side between y -2 and 30 at x = 50. Trim or move the apron to
match.

## Process (sourced practice, simplified)

Pots are set down at a station, left to cool in air and then under water sprays, carried to the
tipping station and inverted over the wall. The solid slag cake drops into the breaking pit, where
it is broken (impact hammer or mobile breaker) and loaded out to the concentrator's ROM bin.
Typical practice in the literature is about 24 h in air and 48 h under water sprays (Springer
2020 review); US4046323 describes 15 h or more to form a 0.25-0.38 m shell before dumping. With
27 stations and a 72 h cycle the yard handles about 9 pots/day (≈ 500 t of slag/day at
16 m³ × ~3.4 t/m³). A plant tapping more slag needs more stations, a shorter cycle, or early tipping
with cake cooling in the pit. The station count is a script parameter (`STATIONS`).

## Pot stations (pot centre at ground, carrier yaw to use)

Carrier yaw is the direction the carrier's front faces: +90° = north, -90° = south. The carrier
straddles the pot with its open end toward the station.

| Station | Pot centre | Carrier yaw |
|---|---|---|
{st_rows}

Tipping: carriers reverse north against the curb at y = {TIP_Y - CURB_W} with the front facing south
(yaw -90°). Bays are centred at x = {', '.join(str(x) for x in TIP_BAYS_X)}. With SM_SlagPotCarrier the origin
then sits at y ≈ {TIP_Y - CURB_W - 4.54:.1f}, and at 140° tip the pot is over the pit.

Spray nozzles: {len(nozzles)} nozzle tips at z = {HEADER_Z - 0.6} m, one per pot (row A from the south
header at y = {HEADER_Y[0]}, rows B and C from the shared header at y = {HEADER_Y[1]}), each offset 35 %
of the way toward its pot. Use them as Niagara spray emitter locations.

## Connection points

| Point | Location |
|---|---|
{conn}

## Objects and pivots

All parts are static; YARD_PondWater is a separate object for a water material.

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

## Unreal import

Combine Meshes off, Transform Vertex to Absolute on (no moving parts). No UVs are authored; use
world-aligned materials for concrete and steel, and let Unreal generate lightmap UVs if you use
baked lighting. With the default FBX settings Blender +Y appears as Unreal -Y, so the carrier yaws
in the table change sign in Unreal (+90° here = -90° there).

## Dimensions

| Item | Value | Status |
|---|---|---|
| Slag pot pit floor z, pot positions | -5.5; (46.0, 8.8), (46.0, 15.3) | From SM_SlagPots |
| Ramp grade 8.0 %, 10 m wide | | Estimated (typical haul road ramp for a 5.7 m wide carrier) |
| Station pitch 8 m, 5 × 5 m steel set-down plates, aisles 22 m | | Own design, sized to the 9.85 × 5.70 m carrier footprint |
| Air then water-spray cooling, cooling times | 24 h + 48 h | Sourced (Springer 2020 review; US4046323) |
| Spray header height 6.5 m | | Estimated, clears a carrier with a lifted pot (~4.5 m) |
| Tipping wall 3.5 m drop, wear-plated face, 1.0 m wheel stop curb | | Own design (Mount Isa uses steel tipping stations, [S8]) |
| Breaking pit 86 × 28 m, loader ramp 10 % | | Estimated |
| Settling pond 12 × 40 m, two cells | | Own design |
| Light masts 25 m | | Estimated |

Sources: US4046323A (https://patents.google.com/patent/US4046323A/en); "Recovery of copper from
slag" review, Mining, Metallurgy & Exploration 2020 (https://link.springer.com/doi/10.1007/s42461-020-00274-x);
Glencore Kress article [S8] in research/copper-refinery/copper-refinery-equipment.md.

## Files

- SM_SlagCoolingYard.blend / .fbx (REF collection, proxy pots and slag heap are not exported)
- Preview_Overview.png, Preview_Ramp.png, Preview_Tipping.png
"""
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(txt)


def main():
    os.makedirs(OUT, exist_ok=True)
    col, log, stations, nozzles = build()
    pb.export_fbx(os.path.join(OUT, NAME + ".fbx"), [col.name])
    write_readme(col, log, stations, nozzles)
    pb.save_blend(os.path.join(OUT, NAME + ".blend"))
    if "--no-render" in sys.argv:
        return
    pb.setup_render()
    # carriers from SM_SlagPotCarrier for scale: one tipping at the middle bay, one at station C6
    car = os.path.join(REPO, "Meshes", "SlagPotCarrier", "SM_SlagPotCarrier.blend")
    if os.path.exists(car):
        refc = pb.collection("REF_Carriers")
        tip = pb.append_asset(car, refc, (TIP_BAYS_X[1], TIP_Y - CURB_W - 4.54, 0.0), -90,
                               ("CAR_", "RIG_", "REF_SlagPot"))
        tip["CAR_Cradle"].rotation_euler.y = math.radians(-140)
        st = pb.append_asset(car, refc, (stations[23][1], stations[23][2], 0.0), stations[23][3],
                              ("CAR_", "RIG_", "REF_SlagPot"))
    pb.render_view(os.path.join(OUT, "Preview_Overview.png"), (150, -40, 120), (20, 110, -2), lens=30)
    pb.render_view(os.path.join(OUT, "Preview_Ramp.png"), (85, 15, 14), (58, 70, -3), lens=28)
    pb.render_view(os.path.join(OUT, "Preview_Tipping.png"), (-5, 140, 22), (22, 180, -1), lens=28)


main()
