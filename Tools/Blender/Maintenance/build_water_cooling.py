"""
build_water_cooling.py - furnace / process cooling-water circuit.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_water_cooling.py
      (add  -- Tower  to build one asset only)

Assets (Meshes/WaterCoolingCircuit/):
    SM_FurnaceCoolingTower       3-cell induced-draft concrete cooling tower (open circuit)
    SM_CoolingWaterPumpStation   3 pumps, 2 plate heat exchangers, headers, shelter
    SM_EmergencyWaterTank        elevated gravity tank for jacket cooling if pumps fail
    SM_LeakDetectionManifold     return-water manifold with per-circuit flow meters and alarm panel

Circuit (own layout): the closed jacket loop (treated water) runs furnace jackets -> leak
detection manifold -> plate heat exchangers -> pumps -> jackets. The open tower loop cools the
other side of the plate heat exchangers. The emergency tank feeds the jacket loop by gravity.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

FOLDER = "WaterCoolingCircuit"


def pipe_run(p, pts, r, m, seg=14):
    """Straight pipe segments through the points, with a sphere at each bend."""
    for a, b in zip(pts, pts[1:]):
        p.cyl_between(a, b, r, m, seg=seg)
    for q in pts[1:-1]:
        p.sphere(r * 1.02, q, m, seg=seg)


def valve(p, c, r, m, axis='X'):
    """Gate valve body with handwheel on top."""
    rot = (0, 90, 0) if axis == 'X' else (90, 0, 0)
    p.cyl(r * 1.5, r * 2.2, c, m['steel'], rot=rot, seg=16)
    p.cyl_between(c, Vector(c) + Vector((0, 0, r * 3.5)), r * 0.25, m['grey'], seg=8)
    p.cyl(r * 1.3, 0.04, Vector(c) + Vector((0, 0, r * 3.5)), m['red'], seg=16)


# ===========================================================================
# Cooling tower
# ===========================================================================

def build_tower():
    name = "SM_FurnaceCoolingTower"
    col, ref, m = pm.start(name)
    N, CELL, DECK, BASIN = 3, 9.0, 10.0, 1.5      # cells, cell size, fan deck height, basin depth
    STACK_R, STACK_H, FAN_R = 3.9, 3.0, 3.65
    LX, LY = N * CELL, CELL
    conc = m['concrete']
    louvre = pb.mat("M_Louvre_PVC", (0.55, 0.6, 0.58), 0.0, 0.6)
    fill = pb.mat("M_Fill_Dark", (0.1, 0.12, 0.12), 0.0, 0.8)
    st = pb.Part("CT_Structure")
    st.box_mm((-0.4, -0.4, -BASIN), (LX + 0.4, LY + 0.4, 0.4), conc)       # basin walls (outer block)
    st.box_mm((0, 0, -BASIN + 0.3), (LX, LY, 0.25), pb.mat("M_Water", (0.05, 0.12, 0.13), 0.0, 0.05))
    for i in range(N + 1):                                                  # cell partition walls
        x = i * CELL
        st.box_mm((x - 0.15, 0, 0.4), (x + 0.15, LY, DECK), conc)
    for y in (0.0, LY):                                                     # columns on the louvre faces
        for k in range(N * 3 + 1):
            x = k * CELL / 3
            st.box_mm((x - 0.2, y - 0.2, 0.4), (x + 0.2, y + 0.2, DECK), conc)
        st.box_mm((0, y - 0.25, 4.4), (LX, y + 0.25, DECK), conc)            # casing above the air inlet
    for y, s in ((0.0, -1), (LY, 1)):                                       # inlet louvres (0.4-4.4 m)
        for z in [0.6 + 0.35 * k for k in range(11)]:
            st.box((LX, 0.04, 0.3), (LX / 2, y + s * 0.12, z), louvre, rot=(s * 40, 0, 0))
    st.box_mm((0, 0, 4.4), (LX, LY, 6.2), fill)                               # fill pack (seen through louvres)
    st.box_mm((-0.3, -0.3, DECK), (LX + 0.3, LY + 0.3, DECK + 0.3), conc)    # fan deck
    pm.guard_box(st, -0.25, -0.25, LX + 0.25, LY + 0.25, DECK + 0.3, m['yellow'])
    for i in range(N):                                                      # fan stacks (FRP)
        cx = (i + 0.5) * CELL
        n = 40
        rows = []
        for z, r in ((DECK + 0.3, STACK_R), (DECK + 0.3 + STACK_H * 0.4, STACK_R * 0.95),
                     (DECK + 0.3 + STACK_H, STACK_R * 1.05)):
            rows.append([(cx + r * math.cos(2 * math.pi * k / n), LY / 2 + r * math.sin(2 * math.pi * k / n), z)
                         for k in range(n + 1)])
        st.quad_strip([list(x) for x in zip(*rows)], m['frp'])
        st.box_mm((cx + 4.2, LY / 2 - 0.4, DECK + 0.3), (cx + 4.4, LY / 2 + 0.4, DECK + 1.4), m['steel'])  # motor stand
    # hot water inlet risers up the -Y face to a distribution header
    pipe_run(st, [Vector((-2.5, -1.5, 0.0)), Vector((-2.5, -1.5, 7.0)), Vector((LX - 1.0, -1.5, 7.0))],
             0.35, m['blue'])
    for i in range(N):
        cx = (i + 0.5) * CELL
        st.cyl_between((cx, -1.5, 7.0), (cx, 0.5, 7.0), 0.25, m['blue'], seg=12)
    st.cyl_between((LX + 0.4, LY / 2, -0.9), (LX + 3.0, LY / 2, -0.9), 0.45, m['blue'], seg=16)   # cold water outlet
    pb.flange(st, Vector((-2.5, -1.5, 0.0)), (0, 0, 0), 0.35, m['steel'])
    pb.flange(st, Vector((LX + 3.0, LY / 2, -0.9)), (0, 90, 0), 0.45, m['steel'])
    pm.stair(st, (LX + 1.2, -6.0, 0.0), (LX + 1.2, -0.4, DECK + 0.3), 1.0, m['steel'], m['yellow'])
    st.finish(col)
    fans = []
    for i in range(N):
        cx = (i + 0.5) * CELL
        c = Vector((cx, LY / 2, DECK + 1.3))
        f = pb.Part(f"CT_Fan{i + 1}", pivot=c)
        f.cyl(0.45, 0.6, c, m['grey'], seg=16)
        for k in range(8):
            a = 360 * k / 8
            f.box((FAN_R - 0.5, 0.45, 0.04), c + Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0)) * (FAN_R / 2 + 0.2),
                  m['steel'], rot=(12, 0, a))
        fans.append(f.finish(col))
    pb.ref_human(ref, (LX / 2, -1.0, DECK + 0.3))
    pb.ref_human(ref, (-1.0, -4.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_FurnaceCoolingTower.png", (LX + 22, -26, 22), (LX / 2, LY / 2, 4.5), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_FurnaceCoolingTower.png",
                about=f"""
Three-cell induced-draft counterflow cooling tower in cast concrete for the furnace and process
water. It is built to look different from the acid plant's two-cell gas-cleaning tower: concrete
casing and cell walls, inlet louvres along both long faces, FRP fan stacks, an external hot-water
riser and a stair to the fan deck. Origin is the -X/-Y outer corner of the cells at basin rim
level (0.0); cells run along +X ({LX:.0f} × {LY:.0f} m in plan, fan deck at {DECK:.0f} m).
""",
                moving=f"""
| Part | Motion |
|---|---|
| CT_Fan1..3 | Spin about local Z (about 120-150 rpm is typical for this fan size; game value) |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Cell plan 9 × 9 m, fan Ø7.3 m, fan deck 10 m, basin 1.5 m deep | | Estimated (field-erected tower proportions; packaged towers like the Marley NC have 2.1-3.7 m fans) |
| Hot water inlet Ø0.7 m at (-2.5, -1.5, 0.0); cold water outlet Ø0.9 m at (30.0, 4.5, -0.9) | | Connection points (stub flanges) |
""",
                sources="Marley NC listings (fan sizes, cell sizes for packaged towers) via equipt.com/genemco.com; research file")


# ===========================================================================
# Pump station
# ===========================================================================

def build_pump_station():
    name = "SM_CoolingWaterPumpStation"
    col, ref, m = pm.start(name)
    sh = pb.Part("WCP_Station")
    sh.box_mm((-1.0, -1.0, -0.3), (17.0, 9.0, 0.0), m['concrete'])          # slab
    for x in (-0.8, 5.2, 11.2, 16.8):                                       # shelter portal frames
        for y in (-0.8, 8.8):
            sh.beam_between((x, y, 0), (x, y, 6.5), 0.3, 0.3, m['blue'])
        sh.beam_between((x, -0.8, 6.5), (x, 8.8, 6.5), 0.3, 0.5, m['blue'])
    sh.box_mm((-1.0, -1.0, 6.75), (17.0, 9.0, 6.85), m['galv'])              # roof sheet
    sh.box_mm((-0.8, 8.6, 4.6), (16.8, 8.8, 6.5), m['blue'])                 # crane rail beam / runway
    # suction header (from the tower basin) along y = 1.0, discharge header along y = 6.5
    pipe_run(sh, [Vector((-1.0, 1.0, 0.8)), Vector((10.5, 1.0, 0.8))], 0.35, m['blue'])
    pipe_run(sh, [Vector((0.5, 6.5, 2.6)), Vector((16.5, 6.5, 2.6))], 0.30, m['green'])
    pb.flange(sh, Vector((-1.0, 1.0, 0.8)), (0, 90, 0), 0.35, m['steel'])
    pb.flange(sh, Vector((16.5, 6.5, 2.6)), (0, 90, 0), 0.30, m['steel'])
    pumps = []
    for i in range(3):
        x = 1.5 + i * 3.2
        sh.box_mm((x - 0.6, 1.8, 0), (x + 0.6, 5.2, 0.35), m['concrete'])    # plinth
        sh.cyl(0.55, 1.0, (x, 2.6, 0.95), m['blue'], rot=(90, 0, 0), seg=24)  # split-case pump casing
        sh.cyl_between((x, 1.0, 0.8), (x, 2.1, 0.8), 0.22, m['blue'], seg=14)  # suction branch
        sh.cyl_between((x, 2.6, 1.5), (x, 2.6, 2.6), 0.2, m['green'], seg=14)  # discharge riser
        pipe_run(sh, [Vector((x, 2.6, 2.6)), Vector((x, 6.5, 2.6))], 0.2, m['green'])
        valve(sh, Vector((x, 4.2, 2.6)), 0.2, m, axis='Y')                   # isolation valve
        sh.cyl(0.25, 0.4, (x, 5.3, 2.6), m['steel'], rot=(90, 0, 0), seg=14)  # check valve
        sh.box_mm((x - 0.45, 3.8, 0.35), (x + 0.45, 5.1, 1.35), m['green'])   # motor
        sh.box_mm((x - 0.5, 3.3, 0.35), (x + 0.5, 3.5, 0.6), m['steel'])     # coupling guard base
        c = Vector((x, 3.45, 0.95))
        sp = pb.Part(f"WCP_Pump{i + 1}_Shaft", pivot=c)
        sp.cyl(0.1, 0.9, c, m['grey'], rot=(90, 0, 0), seg=12)
        sp.cyl(0.18, 0.12, c, m['steel'], rot=(90, 0, 0), seg=16)             # coupling hub
        pumps.append(sp)
    # plate heat exchangers (closed jacket loop <-> open tower loop)
    for j in range(2):
        x = 11.5 + j * 2.6
        sh.box_mm((x - 0.4, 1.6, 0), (x + 0.4, 1.9, 3.2), m['blue'])         # fixed frame plate
        sh.box_mm((x - 0.4, 4.4, 0), (x + 0.4, 4.7, 3.2), m['blue'])         # pressure plate
        sh.box_mm((x - 0.35, 1.9, 0.3), (x + 0.35, 4.0, 2.9), m['grey'])     # plate pack
        sh.box_mm((x - 0.05, 1.6, 3.2), (x + 0.05, 6.0, 3.35), m['steel'])   # carrying bar
        sh.box_mm((x - 0.15, 5.8, 0), (x + 0.15, 6.0, 3.35), m['steel'])     # support column
        for z, mm in ((2.6, m['green']), (0.8, m['blue'])):
            sh.cyl_between((x - 0.2, 1.6, z), (x - 0.2, 1.0, z), 0.18, mm, seg=12)
            sh.cyl_between((x + 0.2, 1.6, z + 0.2), (x + 0.2, 0.2, z + 0.2), 0.18, m['red'], seg=12)
    for sp in pumps:
        sp.finish(col)
    sh.box_mm((14.5, 7.0, 0), (16.5, 8.2, 2.2), m['grey'])                   # MCC / VSD panel
    sh.finish(col)
    pb.ref_human(ref, (8.0, 0.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_CoolingWaterPumpStation.png", (21, -13, 6.5), (8.0, 4.0, 1.6), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_CoolingWaterPumpStation.png",
                about="""
Open-sided pump shelter on a slab: three horizontal split-case pumps (two duty, one standby)
with motors, isolation and check valves, a suction header from the tower basin, a discharge
header, and two plate heat exchangers that separate the closed furnace-jacket loop from the
open tower loop. Origin is the slab corner at floor level; the station runs along +X.
Pipe colours: blue = cold/suction, green = pumped supply, red = warm return from the jackets.
Own layout.
""",
                moving="""
| Part | Motion |
|---|---|
| WCP_Pump1..3_Shaft | Spin about local Y (coupling hub visible between pump and motor; impellers are inside the casings and not modelled) |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Station 18 × 10 m, pumps, exchangers, headers (Ø0.6-0.7 m) | | Own design; sizes are estimates for a flash furnace jacket circuit |
| Suction header inlet Ø0.7 m at (-1.0, 1.0, 0.8); discharge header outlet Ø0.6 m at (16.5, 6.5, 2.6) | | Connection points (stub flanges) |
""",
                sources="Hatch, 'Monitoring of Copper Cooling Components in Furnaces Using Leak Detection and NDT Methods' (closed cooling circuits on smelting furnaces)")


# ===========================================================================
# Emergency elevated water tank
# ===========================================================================

def build_emergency_tank():
    name = "SM_EmergencyWaterTank"
    col, ref, m = pm.start(name)
    H, R, TH = 22.0, 4.0, 6.0          # tank bottom height, radius, shell height
    tk = pb.Part("EWT_Tank")
    for a in (45, 135, 225, 315):      # four legs, slightly battered
        top = Vector((R * 0.8 * math.cos(math.radians(a)), R * 0.8 * math.sin(math.radians(a)), H))
        bot = Vector((R * 1.1 * math.cos(math.radians(a)), R * 1.1 * math.sin(math.radians(a)), 0))
        tk.beam_between(bot, top, 0.45, 0.45, m['white'])
        tk.box((1.2, 1.2, 0.6), bot + Vector((0, 0, 0.3)), m['concrete'])
    for z in (6.0, 12.0, 18.0):        # ring girts and X bracing
        f = z / H
        pts = []
        for a in (45, 135, 225, 315):
            r = R * (1.1 - 0.3 * f)
            pts.append(Vector((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)))
        for i in range(4):
            tk.beam_between(pts[i], pts[(i + 1) % 4], 0.2, 0.2, m['white'])
    tk.cyl(R, TH, (0, 0, H + TH / 2), m['white'], seg=40)
    tk.cyl(R, 1.2, (0, 0, H + TH + 0.6), m['white'], seg=40, r2=0.6)        # conical roof
    tk.cyl(R + 0.05, 0.3, (0, 0, H + 0.15), m['steel'], seg=40)              # balcony ring
    pm.guard_box(tk, -R - 0.9, -R - 0.9, R + 0.9, R + 0.9, H, m['yellow'])   # square balcony rail
    tk.box_mm((-R - 0.9, -R - 0.9, H - 0.1), (R + 0.9, R + 0.9, H), m['galv'])
    pb.ladder(tk, Vector((R * 1.1 * 0.707 + 0.3, 0, 0)), H, m['yellow'], facing=90)
    pipe_run(tk, [Vector((0, 0, H)), Vector((0, 0, 1.0)), Vector((3.5, 0, 1.0)), Vector((6.0, 0, 1.0))], 0.25, m['blue'])
    valve(tk, Vector((4.5, 0, 1.0)), 0.25, m, axis='X')                      # fail-open valve
    pb.flange(tk, Vector((6.0, 0, 1.0)), (0, 90, 0), 0.25, m['steel'])
    tk.cyl_between((0.8, 0, H + TH), (0.8, 0, 1.2), 0.1, m['blue'], seg=10)  # overflow
    tk.finish(col)
    pb.ref_human(ref, (3.0, -3.0, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_EmergencyWaterTank.png", (40, -46, 24), (0, 0, 14), 35),
    ])
    vol = math.pi * R * R * TH
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_EmergencyWaterTank.png",
                about=f"""
Elevated steel tank (about {vol:.0f} m³) on a four-leg tower, bottom at {H:.0f} m. If the cooling pumps
stop, a fail-open valve lets it feed the furnace jackets by gravity long enough to drain or
freeze the bath safely. Origin is the ground at the tower centre. Outlet stub Ø0.5 m at
(6.0, 0.0, 1.0).
Common practice for smelter jacket cooling, but not sourced to a specific plant; size is a
guess. The research file notes that loss of jacket water risks a steam explosion, which makes
this tank a good game hazard hook.
""",
                moving="Static. The valve handwheel is part of the tank mesh.",
                dims="""
| Item | Value | Status |
|---|---|---|
| Ø8 × 6 m tank, 22 m tower | | Estimated |
""",
                sources="research file (jacket water loss -> steam explosion hazard)")


# ===========================================================================
# Leak detection manifold
# ===========================================================================

def build_leak_manifold():
    name = "SM_LeakDetectionManifold"
    col, ref, m = pm.start(name)
    NC = 8                       # circuits
    PITCH = 0.9
    LX = NC * PITCH + 1.0
    rk = pb.Part("LDM_Rack")
    for x in (0.0, LX):
        for y in (0.0, 1.2):
            rk.beam_between((x, y, 0), (x, y, 3.2), 0.15, 0.15, m['steel'])
    for z in (0.2, 3.2):
        rk.box_mm((0, -0.05, z - 0.1), (LX, 1.25, z), m['steel'])
    rk.box_mm((0, 0.0, 0.25), (LX, 1.2, 0.29), m['galv'])                   # drip tray floor
    pipe_run(rk, [Vector((-0.5, 0.9, 0.7)), Vector((LX + 0.5, 0.9, 0.7))], 0.2, m['red'])      # return header
    pipe_run(rk, [Vector((-0.5, 0.3, 2.8)), Vector((LX + 0.5, 0.3, 2.8))], 0.2, m['green'])    # supply header
    pb.flange(rk, Vector((LX + 0.5, 0.9, 0.7)), (0, 90, 0), 0.2, m['steel'])
    pb.flange(rk, Vector((-0.5, 0.3, 2.8)), (0, 90, 0), 0.2, m['steel'])
    for i in range(NC):
        x = 0.9 + i * PITCH
        # supply branch out to a jacket (down from the supply header, out the back)
        rk.cyl_between((x, 0.3, 2.8), (x, -0.8, 2.8), 0.05, m['green'], seg=10)
        rk.cyl(0.08, 0.2, (x, -0.2, 2.8), m['steel'], rot=(90, 0, 0), seg=12)     # supply flow meter
        # return from the jacket: in from the back, down through a flow meter and sight glass to the header
        pipe_run(rk, [Vector((x, -0.8, 2.2)), Vector((x, 0.9, 2.2)), Vector((x, 0.9, 0.7))], 0.05, m['red'], seg=10)
        rk.cyl(0.085, 0.25, (x, 0.9, 1.75), m['steel'], seg=12)                    # return flow meter
        rk.cyl(0.065, 0.18, (x, 0.9, 1.35), m['glass'], seg=12)                    # sight glass
        rk.cyl(0.03, 0.12, (x + 0.08, 0.9, 1.95), m['grey'], rot=(0, 90, 0), seg=8)  # temperature probe
        valve(rk, Vector((x, 0.9, 1.05)), 0.05, m, axis='Y')
    # alarm panel at the +X end
    rk.box_mm((LX + 0.8, 0.0, 0.0), (LX + 1.6, 1.2, 2.1), m['grey'])
    rk.box_mm((LX + 1.6, 0.1, 1.0), (LX + 1.62, 1.1, 1.9), m['glass'])
    rk.finish(col)
    lamps = []
    for i in range(NC):     # one status lamp per circuit, separate so Unreal can switch it
        y = 0.15 + i * (0.9 / (NC - 1))
        lp = pb.Part(f"LDM_Lamp{i + 1}", pivot=(LX + 1.63, y, 0.8))
        lp.cyl(0.035, 0.04, (LX + 1.63, y, 0.8), m['lamp'], rot=(0, 90, 0), seg=12)
        lamps.append(lp.finish(col))
    bc = pb.Part("LDM_Beacon", pivot=(LX + 1.2, 0.6, 2.1))
    bc.cyl(0.03, 0.4, (LX + 1.2, 0.6, 2.3), m['steel'], seg=8)
    bc.cyl(0.09, 0.2, (LX + 1.2, 0.6, 2.6), pb.mat("M_Beacon_Red", (1, 0.05, 0.02), 0, 0.3, emit=((1, 0.05, 0.02), 8.0)), seg=16)
    bc.finish(col)
    pb.ref_human(ref, (LX / 2, 2.2, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_LeakDetectionManifold.png", (LX + 5, 7, 4.5), (LX / 2 + 0.5, 0.6, 1.4), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_LeakDetectionManifold.png",
                about=f"""
Distribution and return manifold for {NC} furnace cooling-jacket circuits. Each circuit has a
supply flow meter and a return flow meter, a sight glass, a temperature probe and an isolation
valve. The panel compares supply and return flow per circuit; a shortfall means water is leaking
into the furnace, and that circuit's lamp and the beacon go red. Origin is the rack corner at
floor level; circuits run along +X at {PITCH} m pitch; jacket pipes leave the back (-Y).
Own layout. Sourced: smelters run automatic leak detection systems on furnace cooling circuits,
including pressure-based systems sensitive to a few drips per minute.
""",
                moving="""
| Part | Motion |
|---|---|
| LDM_Lamp1..8 | Static; swap material (green / red) per circuit state |
| LDM_Beacon | Static; drive emissive strength or rotate a light for the alarm |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Rack, pipe sizes, meter sizes | | Own design |
| Supply header inlet at (-0.5, 0.3, 2.8); return header outlet at (8.7, 0.9, 0.7) | | Connection points |
""",
                sources="https://hatch.com/About-Us/Publications/Technical-Papers/2014/05/Monitoring-of-Copper-Cooling-Components-in-Furnaces-Using-Leak-Detection-and-NDT-Methods")


BUILDERS = dict(Tower=build_tower, PumpStation=build_pump_station, EmergencyTank=build_emergency_tank,
                LeakManifold=build_leak_manifold)

INTRO = """
Cooling-water circuit for the furnace and converter cooling jackets. Built in Blender 5.2.2 LTS
(headless, cloud) with `Tools/Blender/Maintenance/build_water_cooling.py`. Each asset sits at its
own origin; the stub flanges listed per asset are where they connect, so lay pipe between them
in Unreal once the plant layout fixes their positions. The cooling tower is deliberately
different from the acid plant's gas-cleaning tower (GasCleaning folder, on T's computer).
Loop: jackets -> leak detection manifold -> plate heat exchangers -> pumps -> jackets (closed,
treated water); tower basin -> pumps -> exchangers -> tower (open); emergency tank -> jackets by
gravity.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
