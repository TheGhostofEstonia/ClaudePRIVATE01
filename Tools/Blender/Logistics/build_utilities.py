"""
build_utilities.py - fixed inbound-utility facilities for the plant, each at its own origin.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_utilities.py
      (add  -- Substation  to build one asset only; the README of that folder is still written)

Assets (each in its own folder under Meshes/):
    Substation/SM_Substation          HV substation: 2 incoming bays, 2 x 40 MVA transformers, MV switch house
    OxygenPlant/SM_OxygenPlant        cryogenic air separation unit (ASU) with LOX/LIN storage
    FuelStorage/SM_FuelOilTankFarm    bunded fuel oil tanks, pump bay, truck unloading stand
    FuelStorage/SM_GasMeteringStation natural gas pressure reducing and metering station
    FluxStorage/SM_FluxStorage        covered flux / limestone / reverts bays with loader hopper and belt

All: origin on the ground at the footprint centre, +X east, +Y north, metres. Not placed in the
plant layout; each README lists footprint and connection points.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm


# ===========================================================================
# Shared helpers
# ===========================================================================

def extra_mats(m):
    """Materials used by these facilities on top of the psh_maint set."""
    m['porcelain'] = pb.mat("M_Porcelain_Brown", (0.32, 0.14, 0.06), 0.0, 0.25)
    m['alu'] = pb.mat("M_Aluminium", (0.75, 0.76, 0.77), 0.9, 0.35)
    m['tank'] = pb.mat("M_Paint_TankWhite", (0.78, 0.79, 0.77), 0.1, 0.5)
    m['clad'] = pb.mat("M_Cladding_Grey", (0.42, 0.45, 0.47), 0.4, 0.5)
    m['roof'] = pb.mat("M_Cladding_Roof", (0.3, 0.32, 0.33), 0.4, 0.55)
    m['gravel'] = pb.mat("M_Gravel", (0.45, 0.43, 0.4), 0.0, 1.0)
    m['tx'] = pb.mat("M_Paint_TransformerGrey", (0.36, 0.4, 0.38), 0.3, 0.5)
    m['gas'] = pb.mat("M_Paint_GasYellow", (0.9, 0.7, 0.05), 0.2, 0.45)
    m['flux'] = pb.mat("M_Silica_Flux", (0.75, 0.7, 0.6), 0.0, 0.95)
    m['lime'] = pb.mat("M_Limestone", (0.82, 0.82, 0.78), 0.0, 0.95)
    m['revert'] = pb.mat("M_Reverts", (0.25, 0.2, 0.18), 0.2, 0.8)
    m['fence'] = pb.mat("M_Fence_Mesh", (0.5, 0.52, 0.5), 0.8, 0.5)
    # chain-link panels: see-through in the previews; in Unreal give this slot a masked material
    m['fence'].node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    return m


def insulator(p, base, h, r, m, sheds=None):
    """Porcelain insulator or bushing column standing on base: core plus sheds every ~0.12 m."""
    x, y, z = base
    p.cyl(r * 0.55, h, (x, y, z + h / 2), m['porcelain'], seg=12)
    n = sheds or max(3, int(h / 0.12))
    for i in range(n):
        p.cyl(r, 0.03, (x, y, z + 0.1 + (h - 0.2) * i / max(1, n - 1)), m['porcelain'], seg=14)
    p.cyl(r * 0.7, 0.06, (x, y, z + h), m['alu'], seg=12)


def building(p, x0, y0, x1, y1, h, m, wall='clad', roof='roof', z0=0.0):
    """Closed cladded box building with a 0.3 m roof slab overhang."""
    p.box_mm((x0, y0, z0), (x1, y1, z0 + h), m[wall])
    p.box_mm((x0 - 0.3, y0 - 0.3, z0 + h), (x1 + 0.3, y1 + 0.3, z0 + h + 0.25), m[roof])


def fence(p, x0, y0, x1, y1, m, h=2.4, gap=None):
    """Mesh security fence round a rectangle. gap = (side, a, b): leave side ('y0', 'y1', 'x0', 'x1') open from a to b."""
    sides = {'y0': ((x0, y0), (x1, y0)), 'y1': ((x0, y1), (x1, y1)),
             'x0': ((x0, y0), (x0, y1)), 'x1': ((x1, y0), (x1, y1))}
    for k, (a, b) in sides.items():
        segs = [(a, b)]
        if gap and gap[0] == k:
            horiz = k in ('y0', 'y1')
            c = a[1] if horiz else a[0]
            g0, g1 = gap[1], gap[2]
            lo = (g0, c) if horiz else (c, g0)
            hi = (g1, c) if horiz else (c, g1)
            segs = [(a, lo), (hi, b)]
        for s0, s1 in segs:
            v0, v1 = Vector((*s0, 0)), Vector((*s1, 0))
            L = (v1 - v0).length
            if L < 0.1:
                continue
            n = max(1, int(L / 3.0))
            for i in range(n + 1):
                q = v0.lerp(v1, i / n)
                p.cyl_between(q, q + Vector((0, 0, h + 0.3)), 0.04, m['galv'], seg=8)
            mid = (v0 + v1) / 2
            ang = math.degrees(math.atan2(v1.y - v0.y, v1.x - v0.x))
            p.box((L, 0.01, h - 0.1), mid + Vector((0, 0, 0.05 + h / 2)), m['fence'], rot=(0, 0, ang))


def vtank(p, c, r, h, m, paint, roof_rise=0.6, stair=True):
    """Vertical fixed-roof storage tank: shell, cone roof, roof rail and a straight external stair."""
    x, y = c
    p.cyl(r, h, (x, y, h / 2), m[paint], seg=48)
    p.cyl(r, roof_rise, (x, y, h + roof_rise / 2), m[paint], seg=48, r2=0.6)
    p.cyl(0.4, 0.8, (x, y, h + roof_rise + 0.2), m['steel'], seg=12)            # vent
    for i in range(24):                                                       # roof edge rail posts
        a = 2 * math.pi * i / 24
        q = Vector((x + (r - 0.3) * math.cos(a), y + (r - 0.3) * math.sin(a), h + 0.1))
        p.cyl_between(q, q + Vector((0, 0, 1.1)), 0.025, m['yellow'], seg=6)
    p.cyl(r - 0.3, 0.05, (x, y, h + 1.2), m['yellow'], seg=48, cap=False)    # rail ring (open)
    if stair:   # straight stair climbing the south-east face, tangent to the shell
        a = Vector((x + r + 0.6, y - r * 0.9, 0.0))
        b = Vector((x + r + 0.6, y + r * 0.6, h))
        pm.stair(p, a, b, 0.9, m['galv'], m['yellow'])


def pipe(p, pts, r, m, seg=12):
    """Pipe along a polyline with a ball at every bend."""
    for a, b in zip(pts, pts[1:]):
        p.cyl_between(a, b, r, m, seg=seg)
    for q in pts[1:-1]:
        p.sphere(r * 1.05, q, m, seg=seg)


def finish_one(name, folder, about, moving, dims, sources, views, ground):
    """Save/export/render one asset and write its folder README (one asset per call)."""
    table = pm.finish_asset(name, folder, views, ground=ground)
    n_obj, n_tri = pm.counts(name)
    return dict(name=name, about=about, n_obj=n_obj, n_tri=n_tri,
                previews=", ".join(v[0] for v in views), moving=moving, table=table,
                dims=dims, sources=sources)


# ===========================================================================
# Substation
# ===========================================================================

def build_substation():
    name = "SM_Substation"
    col, ref, m = pm.start(name)
    extra_mats(m)
    PH = (-2.2, 0.0, 2.2)          # phase offsets across a bay (110 kV class, estimated)
    BAYS = (-9.0, 9.0)             # bay centre lines (y)
    GANTRY_Z = 14.0                # line gantry beam height (estimated)
    EQ_Z = 2.5                     # equipment support height (live parts above 2.5 m, estimated)

    yard = pb.Part("SS_Yard")
    yard.box_mm((-30, -20, -0.15), (30, 20, 0.0), m['gravel'])                    # gravel yard
    yard.box_mm((-28, -1.0, 0.0), (28, 1.0, 0.02), m['concrete'])                 # centre access road
    fence(yard, -30, -20, 30, 20, m, gap=('x1', -4.0, 4.0))
    ob_yard = yard.finish(col)

    st = pb.Part("SS_Structures")
    for yb in BAYS:
        # incoming line gantry: two lattice-ish legs and a beam, strain insulators per phase
        for s in (-1, 1):
            st.box((0.6, 0.6, GANTRY_Z), (-26, yb + s * 4.0, GANTRY_Z / 2), m['galv'])
        st.box((0.6, 8.6, 0.8), (-26, yb, GANTRY_Z), m['galv'])
        for dy in PH:
            y = yb + dy
            st.cyl_between((-26, y, GANTRY_Z - 0.4), (-24.4, y, GANTRY_Z - 0.9), 0.09, m['porcelain'], seg=10)
            # down-lead to the surge arrester, then along the equipment row
            pipe(st, [Vector((-24.4, y, GANTRY_Z - 0.9)), Vector((-22, y, EQ_Z + 2.6)),
                      Vector((-6.5, y, EQ_Z + 2.6))], 0.05, m['alu'], seg=8)
            for x, hh in ((-22, 2.2), (-18, 1.6), (-14, 2.4), (-10, 2.0)):
                # support column + insulator: arrester, disconnector, breaker pole, current transformer
                st.box((0.35, 0.35, EQ_Z), (x, y, EQ_Z / 2), m['galv'])
                insulator(st, (x, y, EQ_Z), hh if x != -18 else 1.6, 0.16 if x != -14 else 0.22, m)
            st.box((0.9, 0.6, 0.9), (-14, y, EQ_Z - 0.6), m['grey'])             # breaker mechanism box
            st.box((0.5, 0.5, 0.7), (-10, y, EQ_Z + 2.35), m['tx'])               # CT head
        # transformer foundation and oil bund with gravel
        st.box_mm((-6.0, yb - 4.5, -0.05), (10.0, yb + 4.5, 0.35), m['concrete'])
        st.box_mm((-5.6, yb - 4.1, 0.35), (9.6, yb + 4.1, 0.4), m['gravel'])
        # LV bus duct to the switch house
        pipe(st, [Vector((5.5, yb, 5.2)), Vector((12, yb, 5.2)), Vector((14, yb * 0.5, 5.2))], 0.35, m['tx'], seg=4)
    st.box_mm((-6, -0.3, 0.0), (10, 0.3, 7.5), m['concrete'])                     # fire wall between transformers
    building(st, 14, -15, 28, 15, 5.5, m, wall='clad')                             # MV switch / control house
    for y in (-10, 0, 10):
        st.box_mm((27.98, y - 0.6, 0.0), (28.05, y + 0.6, 2.3), m['steel'])       # personnel doors (east)
    st.box_mm((26, -0.8, -1.0), (30.5, 0.8, 0.0), m['concrete'])                  # cable trench outlet
    ob_st = st.finish(col)

    # Transformers (static, one part each so they can be swapped or highlighted)
    txs = []
    for i, yb in enumerate(BAYS):
        t = pb.Part(f"SS_Transformer_T{i + 1}", pivot=(2.0, yb, 0.4))
        t.box_mm((-1.5, yb - 1.8, 0.4), (5.5, yb + 1.8, 4.4), m['tx'])            # main tank
        for s in (-1, 1):                                                         # radiator banks
            for k in range(8):
                t.box((0.08, 1.2, 3.0), (-1.0 + k * 0.85, yb + s * 2.45, 2.4), m['tx'])
            t.box_mm((-1.2, yb + s * 1.8 - (0.05 if s > 0 else -0.05), 3.8), (5.2, yb + s * 3.1, 3.95), m['tx'])
        t.cyl(0.55, 4.5, (1.5, yb, 5.4), m['tx'], rot=(0, 90, 0), seg=16)        # conservator
        for k in range(2):
            t.box((0.15, 0.15, 1.0), (0.0 + k * 3.0, yb, 4.9), m['steel'])
        for dy in PH:                                                             # HV bushings (west)
            insulator(t, (-0.6, yb + dy * 0.55, 4.4), 2.4, 0.2, m)
            pipe(t, [Vector((-0.6, yb + dy * 0.55, 6.8)), Vector((-6.5, yb + dy, EQ_Z + 2.6))], 0.05, m['alu'], seg=8)
        for dy in (-0.8, 0, 0.8):                                                  # LV bushings (east)
            insulator(t, (4.8, yb + dy, 4.4), 0.8, 0.15, m)
        t.box_mm((5.2, yb - 0.6, 4.4), (5.8, yb + 0.6, 5.6), m['tx'])            # LV bus duct start
        t.box_mm((-1.6, yb + 1.8, 1.0), (-0.6, yb + 2.2, 2.6), m['grey'])         # tap changer cabinet
        txs.append(t.finish(col))

    # Disconnector blades: rotate about the near post (vertical axis)
    blades = []
    for yb in BAYS:
        for j, dy in enumerate(PH):
            y = yb + dy
            b = pb.Part(f"SS_Disconnector_{'S' if yb < 0 else 'N'}{j + 1}", pivot=(-18.7, y, EQ_Z + 1.65))
            b.beam_between((-18.7, y, EQ_Z + 1.65), (-17.3, y, EQ_Z + 1.65), 0.08, 0.06, m['alu'])
            blades.append(b.finish(col))

    # Gate leaves (east side, two 4 m leaves)
    gates = []
    for s, t in ((-1, "S"), (1, "N")):
        g = pb.Part(f"SS_Gate_{t}", pivot=(30, s * 4.0, 0))
        g.box_mm((29.95, min(s * 4.0, 0) + 0.05, 0.05), (30.05, max(s * 4.0, 0) - 0.05, 2.4), m['fence'])
        for z in (0.1, 2.35):
            g.cyl_between((30, s * 4.0, z), (30, 0, z), 0.03, m['galv'], seg=8)
        gates.append(g.finish(col))

    pb.ref_human(ref, (24, -18, 0))
    views = [("Preview_Substation.png", (-52, -48, 30), (2, 0, 4), 35)]
    r = finish_one(
        name, "Substation",
        about="""
HV substation feeding the plant: two incoming line bays (110 kV class, phases 2.2 m apart), each
with surge arresters, a three-pole disconnector, a live-tank circuit breaker and current
transformers, then a 40 MVA class oil transformer stepping down to medium voltage. A fire wall
separates the transformers. LV bus ducts run east into the MV switch / control house, whose cable
trench leads on to the plant (the tankhouse rectifier house and the rest of the plant load). Own
layout design. Origin: ground centre of the fenced yard, 60 x 40 m.
""",
        moving="""
| Part | Motion |
|---|---|
| SS_Disconnector_S1..S3 / N1..N3 | Rotate about local Z at the near post: 0° closed, +90° open |
| SS_Gate_S / SS_Gate_N | Swing about local Z at the gate post: S leaf -90° (opens outward, +X), N leaf +90° |
| SS_Transformer_T1 / T2 | Static, separate so they can be replaced or highlighted (fire, failure) |
""",
        dims="""
| Item | Value | Basis |
|---|---|---|
| Yard (fenced) | 60 x 40 m, fence 2.4 m | Estimated |
| Line gantry beam | 14 m | Estimated, 110 kV class |
| Phase spacing | 2.2 m | Estimated, 110 kV class |
| Live part support height | 2.5 m to the insulator base | Estimated (usual minimum to live parts ~2.5 m above walkways) |
| Transformer tank | 7.0 x 3.6 x 4.0 m, radiators each side, top of conservator 5.95 m | Estimated, 40 MVA class |
| MV switch / control house | 14 x 30 x 5.5 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Incoming line, south bay (3 phases at gantry) | (-26.0, -9.0 ± 2.2, 13.6) |
| Incoming line, north bay | (-26.0, 9.0 ± 2.2, 13.6) |
| MV cable trench outlet to the plant | (30.5, 0.0, -1.0), 1.6 m wide |
| Road gate (east) | x 30, y -4 to 4 |

Plant load is not sized here. The tankhouse rectifiers are about 30 kA at 55 V per circuit
(Meshes/Tankhouse); a smelter and refinery site also carries oxygen plant compressors, blowers and
pumps, so two 40 MVA units is a plausible order of magnitude, not a design figure.
""",
        sources="own design; no plant-specific substation data used.",
        views=views, ground=45.0)
    return r


# ===========================================================================
# Oxygen plant (cryogenic ASU)
# ===========================================================================

def build_oxygen_plant():
    name = "SM_OxygenPlant"
    col, ref, m = pm.start(name)
    extra_mats(m)
    RACK_Z = 6.0      # pipe rack top (estimated)

    s = pb.Part("OX_Site")
    s.box_mm((-42, -26, -0.2), (42, 26, 0.0), m['concrete'])
    # Main air compressor (MAC) house with air intake filter house on the west end
    building(s, -36, 4, -6, 20, 12.0, m)
    s.box_mm((-41, 6, 6.0), (-36, 18, 13.0), m['clad'])                            # intake filter house
    for k in range(10):                                                           # louvres
        s.box((0.05, 11.6, 0.25), (-41.03, 12, 6.5 + k * 0.62), m['steel'])
    s.box_mm((-41, 6, 0.0), (-38, 18, 6.0), m['steel'])                            # filter house supports
    # Direct contact aftercooler column (air pre-cooling) and chiller skid
    s.cyl(1.6, 22.0, (2.0, 12.0, 11.0), m['tank'], seg=32)
    s.cyl(1.6, 0.5, (2.0, 12.0, 22.25), m['tank'], seg=32, r2=0.3)
    s.box_mm((-1.5, 16.0, 0.0), (5.5, 20.0, 2.6), m['blue'])
    # Two molecular sieve adsorbers, horizontal on saddles
    for y in (9.0, 15.5):
        s.cyl(1.75, 10.0, (14.0, y, 3.2), m['tank'], rot=(0, 90, 0), seg=32)
        for xs in (9.5, 18.5):
            s.sphere(1.75, (xs, y, 3.2), m['tank'], seg=24)
        for xs in (11.0, 17.0):
            s.box((0.6, 2.6, 1.6), (xs, y, 0.8), m['concrete'])
    # Cold box (rectification columns) and main heat exchanger box
    CB = (30.0, 8.0)
    s.box_mm((CB[0] - 2.25, CB[1] - 3.0, 0.0), (CB[0] + 2.25, CB[1] + 3.0, 38.0), m['white'])
    s.box_mm((CB[0] - 2.4, CB[1] - 3.15, 38.0), (CB[0] + 2.4, CB[1] + 3.15, 38.3), m['steel'])
    pm.guard_box(s, CB[0] - 2.4, CB[1] - 3.15, CB[0] + 2.4, CB[1] + 3.15, 38.3, m['yellow'])
    s.box_mm((23.0, 4.5, 0.0), (26.5, 8.0, 22.0), m['white'])                      # heat exchanger box
    # stair tower beside the cold box: landings every 4 m
    tw = (35.5, 8.0)
    for zz in range(0, 39, 4):
        s.box_mm((tw[0] - 1.5, tw[1] - 2.5, zz), (tw[0] + 1.5, tw[1] + 2.5, zz + 0.08), m['galv'])
    for (dx, dy) in ((-1.5, -2.5), (1.5, -2.5), (-1.5, 2.5), (1.5, 2.5)):
        s.box((0.2, 0.2, 38.4), (tw[0] + dx, tw[1] + dy, 19.2), m['galv'])
    for zz in range(0, 36, 4):
        pm.stair(s, Vector((tw[0], tw[1] - 2.3, zz + 0.08)), Vector((tw[0], tw[1] + 1.0, zz + 4.0)),
                 1.0, m['galv'], m['yellow'])
    # Expander / booster compressor skid
    s.box_mm((18.0, -4.0, 0.0), (24.0, 0.0, 2.8), m['blue'])
    # Liquid storage: LOX and LIN vertical vacuum-insulated tanks, ambient vaporiser banks
    for (x, y, lbl) in ((24.0, -14.0, 'lox'), (32.0, -14.0, 'lin')):
        s.cyl(2.2, 16.0, (x, y, 8.4), m['white'], seg=32)
        s.sphere(2.2, (x, y, 16.4), m['white'], seg=24)
        for a in range(4):                                                        # legs
            ang = math.pi / 4 + a * math.pi / 2
            s.box((0.3, 0.3, 0.8), (x + 1.8 * math.cos(ang), y + 1.8 * math.sin(ang), 0.4), m['steel'])
    for k in range(3):                                                            # finned vaporisers
        x0 = 4.0 + k * 3.5
        for i in range(6):
            for j in range(6):
                s.box((0.06, 0.32, 7.0), (x0 + i * 0.4, -16.0 + j * 0.4, 3.9), m['alu'], rot=(0, 0, 45))
        s.box_mm((x0 - 0.3, -16.3, 0.0), (x0 + 2.3, -13.7, 0.4), m['steel'])
    # Small 2-cell cooling tower for the MAC intercoolers
    s.box_mm((-34, -22, 0.0), (-22, -14, 8.0), m['frp'])
    for x in (-31, -25):
        s.cyl(2.6, 2.5, (x, -18, 9.25), m['frp'], seg=24)
    # Pipe rack along y = 0 from the MAC house to the east site edge, with three pipes
    for x in range(-34, 42, 6):
        for y in (-1.5, 1.5):
            s.box((0.3, 0.3, RACK_Z), (x, y, RACK_Z / 2), m['steel'])
        s.box((0.3, 3.4, 0.3), (x, 0, RACK_Z), m['steel'])
    for y, r_, mm in ((-0.9, 0.35, m['blue']), (0.0, 0.25, m['white']), (0.9, 0.3, m['green'])):
        s.cyl_between((-34, y, RACK_Z + 0.15 + r_), (41.5, y, RACK_Z + 0.15 + r_), r_, mm, seg=14)
    for y, r_ in ((-0.9, 0.35), (0.0, 0.25), (0.9, 0.3)):                          # outlet flanges
        s.cyl(r_ * 1.6, 0.05, (41.6, y, RACK_Z + 0.15 + r_), m['grey'], rot=(0, 90, 0), seg=20)
    # air duct MAC -> aftercooler -> adsorbers -> cold box at rack level
    pipe(s, [Vector((-6, 12, 8)), Vector((0.2, 12, 8)), Vector((0.2, 12, 20)), Vector((2.0, 12, 21.5))], 0.5, m['grey'])
    pipe(s, [Vector((2.0, 10.4, 3.0)), Vector((9.0, 10.4, 3.0)), Vector((9.0, 9.0, 3.2))], 0.4, m['grey'])
    pipe(s, [Vector((19.0, 12.0, 3.2)), Vector((23.0, 12.0, 3.2)), Vector((23.0, 6.0, 3.2)), Vector((27.8, 6.0, 3.2))], 0.4, m['grey'])
    s.finish(col)

    # MAC house roller door (slides up along +Z), south wall
    door = pb.Part("OX_MACDoor", pivot=(-21, 4.0, 0.0))
    door.box_mm((-24, 3.9, 0.0), (-18, 3.98, 5.0), m['steel'])
    door.finish(col)

    pb.ref_human(ref, (16, -6, 0))
    views = [("Preview_OxygenPlant.png", (-62, -60, 40), (6, 2, 10), 35)]
    return finish_one(
        name, "OxygenPlant",
        about="""
On-site cryogenic oxygen plant (air separation unit) for oxygen-enriched flash smelting and
converting. Process order, west to east: air intake filter house, main air compressor house,
direct contact aftercooler column with chiller skid, two horizontal molecular sieve adsorbers,
expander/booster skid, main heat exchanger box and the rectification cold box with a stair tower.
Liquid oxygen and liquid nitrogen backup tanks with finned ambient vaporisers stand south, and a
2-cell cooling tower serves the compressor coolers. Product leaves on the pipe rack at the east
edge. Own layout design. Origin: ground centre of the 84 x 52 m pad.
""",
        moving="""
| Part | Motion |
|---|---|
| OX_MACDoor | Roller door, slide along local +Z by 5.0 m to open |
""",
        dims="""
| Item | Value | Basis |
|---|---|---|
| Cold box | 4.5 x 6.0 m plan, 38 m high | Inside Linde's stated coldbox range (up to 5 x 7 m section, up to 40 m long); exact size for a given capacity estimated |
| Heat exchanger box | 3.5 x 3.5 x 22 m | Estimated |
| Aftercooler column | 3.2 m dia x 22 m | Estimated |
| Adsorbers | 3.5 m dia x 13.5 m over heads | Estimated |
| LOX / LIN tanks | 4.4 m dia, ~18.6 m tall | Estimated |
| MAC house | 30 x 16 x 12 m | Estimated |
| Pipe rack | top z 6.0 m, along y 0 | Estimated |

Capacity is not designed. A flash smelter of a few hundred kt/y concentrate uses oxygen in the
order of 1,000 t/d (estimated, unsourced here); Linde quotes one project at 6 x 3,600 t/d
oxygen, so this single-train size is plausible for a smelter.

**Connection points**

| Point | Position |
|---|---|
| Gaseous oxygen out (blue, DN700) | (41.6, -0.9, 6.50) |
| Nitrogen out (white, DN500) | (41.6, 0.0, 6.40) |
| Cooling water (green, DN600) | (41.6, 0.9, 6.45) |
| Road access to LOX/LIN tanker fill | south edge, x 20 to 36 |
""",
        sources="[Linde coldboxes](https://www.linde-engineering.com/products-and-services/plant-components/coldboxes-packaged-units-and-cryogenic-columns) for the cold box size range and the 6 x 3,600 t/d project; everything else own design.",
        views=views, ground=60.0)


# ===========================================================================
# Fuel oil tank farm and gas metering station
# ===========================================================================

def build_fuel_tank_farm():
    name = "SM_FuelOilTankFarm"
    col, ref, m = pm.start(name)
    extra_mats(m)
    R, H = 6.0, 12.0          # tank radius and shell height: ~1,350 m3 gross each (estimated)

    s = pb.Part("FT_Site")
    s.box_mm((-22, -32, -0.2), (22, 13, 0.0), m['concrete'])
    for (a, b) in (((-20, -12), (20, -12)), ((-20, 12), (20, 12)), ((-20, -12), (-20, 12)), ((20, -12), (20, 12))):
        s.box_mm((min(a[0], b[0]) - 0.15, min(a[1], b[1]) - 0.15, 0.0),
                 (max(a[0], b[0]) + 0.15, max(a[1], b[1]) + 0.15, 1.5), m['concrete'])  # bund wall 1.5 m
    pm.stair(s, Vector((0, -14.5, 0.0)), Vector((0, -12.2, 1.5)), 1.0, m['galv'], m['yellow'])  # bund step-over
    for x in (-9.0, 9.0):
        vtank(s, (x, 0.0), R, H, m, 'tank')
        s.cyl(R + 0.4, 0.3, (x, 0.0, 0.15), m['concrete'], seg=48)                  # ring foundation
    # Manifold: tank outlets to the pump bay south of the bund
    for x in (-9.0, 9.0):
        pipe(s, [Vector((x, -R, 0.6)), Vector((x, -10.5, 0.6)), Vector((x * 0.2, -10.5, 0.6)),
                 Vector((x * 0.2, -10.5, 2.2)), Vector((x * 0.2, -15.0, 2.2)), Vector((x * 0.2, -15.0, 0.8))],
             0.12, m['steel'])
    s.box_mm((-5.0, -19.0, 0.0), (5.0, -15.0, 0.2), m['concrete'])                 # pump slab
    for x in (-1.8, 1.8):
        s.box_mm((x - 0.6, -18.2, 0.2), (x + 0.6, -16.0, 1.0), m['green'])          # pump + motor
        s.cyl(0.3, 1.0, (x, -17.0, 1.3), m['green'], rot=(90, 0, 0), seg=14)
    # Truck unloading stand: canopy, gantry platform and drain grating
    s.box_mm((-10.0, -30.0, 0.0), (10.0, -24.0, 0.05), m['grey'])                   # drained slab
    for x in (-9.5, 9.5):
        for y in (-29.5, -24.5):
            s.box((0.3, 0.3, 6.0), (x, y, 3.0), m['steel'])
    s.box_mm((-10.5, -30.5, 6.0), (10.5, -23.5, 6.3), m['roof'])
    s.box_mm((-6.0, -23.9, 0.0), (6.0, -22.4, 3.6), m['galv'])                      # gantry tower block
    s.box_mm((-6.0, -24.4, 3.6), (6.0, -22.4, 3.7), m['galv'])                      # gantry walkway
    pb.handrail(s, (-6.0, -24.4, 3.7), (6.0, -24.4, 3.7), m['yellow'])
    pm.stair(s, Vector((7.5, -23.2, 0.0)), Vector((6.1, -23.2, 3.7)), 0.9, m['galv'], m['yellow'])
    pipe(s, [Vector((0, -22.6, 0.4)), Vector((0, -19.0, 0.4))], 0.1, m['steel'])
    s.finish(col)

    # Bottom-loading/unloading arm: inner arm swings about the riser, outer arm about the elbow
    riser = Vector((-4.0, -23.0, 1.2))
    a1 = pb.Part("FT_UnloadArm_Inner", pivot=riser)
    a1.cyl(0.08, 2.4, riser - Vector((0, 0, 0.6)), m['steel'], seg=12)
    a1.cyl_between(riser, riser + Vector((0, -2.2, 0)), 0.07, m['steel'], seg=12)
    a1.cyl(0.12, 0.4, riser + Vector((0, -2.2, 0)), m['grey'], seg=12)
    ob_a1 = a1.finish(col)
    elbow = riser + Vector((0, -2.2, 0))
    a2 = pb.Part("FT_UnloadArm_Outer", pivot=elbow)
    a2.cyl_between(elbow, elbow + Vector((2.0, 0, -0.4)), 0.07, m['steel'], seg=12)
    a2.cyl(0.12, 0.15, elbow + Vector((2.0, 0, -0.45)), m['grey'], rot=(0, 90, 0), seg=12)
    ob_a2 = a2.finish(col)
    pm.parent(ob_a2, ob_a1)

    pb.ref_human(ref, (3, -27, 0))
    views = [("Preview_FuelOilTankFarm.png", (-40, -60, 26), (0, -8, 4), 35)]
    return finish_one(
        name, "FuelStorage",
        about="""
Fuel oil storage for burners (anode furnace, converters, ladle preheat, dryer backup). Two
vertical fixed-roof tanks inside a 40 x 24 m concrete bund, a manifold to a two-pump transfer bay
south of the bund, and a covered road tanker unloading stand with a gantry walkway and a swinging
unloading arm. Own layout design. Origin: ground centre of the bund. The research file lists
"natural gas / fuel oil, coke or coal (some processes)"; coke storage is not modelled because the
flash smelting route here uses little or none.
""",
        moving="""
| Part | Motion |
|---|---|
| FT_UnloadArm_Inner | Swing about local Z at the riser, ±90° |
| FT_UnloadArm_Outer | Swing about local Z at the elbow (child of the inner arm), ±150° |
""",
        dims="""
| Item | Value | Basis |
|---|---|---|
| Tanks | 12 m dia x 12 m shell, ~1,350 m3 gross each | Estimated |
| Bund | 40 x 24 m inside, wall 1.5 m: ~1,440 m3 gross less tank footprints ~1,100 m3, about 80 % of one tank | Estimated. Many codes ask for 110 % of the largest tank; raise the wall to ~2.0 m for that |
| Unloading stand | 20 x 6 m slab, canopy 6.0 m, gantry deck 3.7 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Transfer pump discharge (to burners, DN150) | pump bay (±1.8, -17.0, 1.3), take off east |
| Tanker hose coupling (outer arm tip, stowed) | (-2.0, -25.2, 0.75) |
| Road lane through the unloading stand | along X at y -27, 6 m wide |
""",
        sources="own design.",
        views=views, ground=45.0)


def build_gas_metering_station():
    name = "SM_GasMeteringStation"
    col, ref, m = pm.start(name)
    extra_mats(m)
    Z = 1.0        # pipe centre height (estimated)

    s = pb.Part("GM_Station")
    s.box_mm((-7.0, -5.0, -0.2), (7.0, 5.0, 0.0), m['gravel'])
    s.box_mm((-5.5, -2.5, 0.0), (4.5, 2.5, 0.25), m['concrete'])                   # skid plinth
    fence(s, -7.0, -5.0, 7.0, 5.0, m, gap=('y0', -1.5, 1.5))
    # inlet riser from below ground, then two parallel runs (duty / standby)
    pipe(s, [Vector((-7.5, 0, -0.5)), Vector((-6.0, 0, -0.5)), Vector((-6.0, 0, Z)), Vector((-5.0, 0, Z))], 0.12, m['gas'])
    for y in (-1.2, 1.2):
        pipe(s, [Vector((-5.0, 0, Z)), Vector((-4.5, y, Z)), Vector((3.5, y, Z)), Vector((4.0, 0, Z))], 0.1, m['gas'])
        s.cyl(0.35, 1.2, (-3.5, y, Z + 0.3), m['gas'], seg=16)                      # filter
        s.box((0.6, 0.45, 0.45), (-1.5, y, Z), m['grey'])                           # meter
        s.cyl(0.25, 0.5, (0.5, y, Z + 0.35), m['gas'], seg=14)                      # regulator body
        s.cyl(0.32, 0.2, (0.5, y, Z + 0.7), m['grey'], seg=14)                      # actuator head
        s.cyl(0.16, 0.4, (2.3, y, Z + 0.3), m['red'], seg=12)                       # slam-shut valve
        for x in (-4.2, 3.2):
            s.box((0.15, 0.15, Z), (x, y, Z / 2 + 0.25), m['steel'])                # pipe supports
    s.cyl_between((4.0, 0, Z), (7.5, 0, Z), 0.15, m['gas'], seg=12)                 # outlet
    s.cyl(0.24, 0.05, (7.5, 0, Z), m['grey'], rot=(0, 90, 0), seg=16)
    s.cyl_between((1.0, 2.2, 0.25), (1.0, 2.2, 4.5), 0.05, m['gas'], seg=8)         # relief vent stack
    building(s, 3.2, -4.6, 6.6, -2.6, 2.5, m, wall='white')                          # metering kiosk
    s.finish(col)

    gate = pb.Part("GM_Gate", pivot=(-1.5, -5.0, 0.0))
    gate.box_mm((-1.45, -5.04, 0.05), (1.45, -4.96, 2.4), m['fence'])
    gate.finish(col)

    pb.ref_human(ref, (-2, -4, 0))
    views = [("Preview_GasMeteringStation.png", (-14, -16, 8), (0, 0, 1), 35)]
    return finish_one(
        name, "FuelStorage",
        about="""
Natural gas pressure reducing and metering station at the site boundary: buried inlet riser,
two parallel streams (duty and standby) each with filter, meter, pressure regulator and slam-shut
valve, a relief vent stack, a small kiosk for the flow computer, gravel yard and fence. Own layout
design. Origin: ground centre of the 14 x 10 m yard.
""",
        moving="""
| Part | Motion |
|---|---|
| GM_Gate | Swing about local Z at the west post, -90° opens outward |
""",
        dims="""
| Item | Value | Basis |
|---|---|---|
| Yard | 14 x 10 m, fence 2.4 m | Estimated |
| Stream pipe | DN200, centre 1.0 m | Estimated |
| Vent stack top | 4.5 m | Estimated |

**Connection points**

| Point | Position |
|---|---|
| Gas inlet (buried, from the supplier) | (-7.5, 0.0, -0.5) |
| Gas outlet to the plant ring main (DN300 flange) | (7.5, 0.0, 1.0) |
""",
        sources="own design.",
        views=views, ground=20.0)


# ===========================================================================
# Flux storage
# ===========================================================================

def build_flux_storage():
    name = "SM_FluxStorage"
    col, ref, m = pm.start(name)
    extra_mats(m)
    BAY_W, BAY_D, WALL_H, EAVE = 15.0, 20.0, 4.0, 12.0     # estimated
    X0 = -30.0                                            # west wall of bay 1
    belt_mats = dict(steel=m['steel'], rubber=m['rubber'], grey=m['grey'], yellow=m['yellow'])

    s = pb.Part("FX_Building")
    s.box_mm((X0 - 1, -12, -0.2), (X0 + 3 * BAY_W + 1, 12, 0.0), m['concrete'])   # floor slab (x -31..16)
    # concrete push walls: back wall (north) and the side / divider walls, front (south) open
    s.box_mm((X0, BAY_D / 2 - 0.5, 0.0), (X0 + 3 * BAY_W, BAY_D / 2, WALL_H), m['concrete'])
    for i in range(4):
        x = X0 + i * BAY_W
        s.box_mm((x - 0.25, -BAY_D / 2 + 2.0, 0.0), (x + 0.25, BAY_D / 2, WALL_H), m['concrete'])
    # steel portal frames every 7.5 m, monopitch roof sloping to the north, cladding above the walls
    for i in range(7):
        x = X0 + i * 7.5
        for y in (-BAY_D / 2 + 0.2, BAY_D / 2 - 0.2):
            s.box((0.4, 0.4, EAVE + 1.0), (x, y, (EAVE + 1.0) / 2), m['steel'])
        s.beam_between((x, -BAY_D / 2 - 1.0, EAVE + 1.4), (x, BAY_D / 2 + 1.0, EAVE - 0.2), 0.3, 0.6, m['steel'])
    roof = [(-BAY_D / 2 - 1.2, EAVE + 1.8), (BAY_D / 2 + 1.2, EAVE + 0.2), (BAY_D / 2 + 1.2, EAVE + 0.35), (-BAY_D / 2 - 1.2, EAVE + 1.95)]
    s.poly_prism(roof, X0 - 0.5, X0 + 3 * BAY_W + 0.5, m['roof'], plane='YZ')
    s.box_mm((X0, BAY_D / 2 - 0.1, WALL_H), (X0 + 3 * BAY_W, BAY_D / 2, EAVE), m['clad'])
    for x in (X0, X0 + 3 * BAY_W):                                                # gable cladding
        s.box_mm((x - 0.05, -BAY_D / 2, WALL_H), (x + 0.05, BAY_D / 2, EAVE + 0.6), m['clad'])
    # material piles (static, part of the building mesh): flux, limestone, reverts
    for i, mm in enumerate((m['flux'], m['lime'], m['revert'])):
        cx = X0 + BAY_W * (i + 0.5)
        pts = [(-6.0, 0.0), (6.0, 0.0), (3.5, 3.6), (-3.5, 3.6)]
        s.poly_prism([(cx + a, b) for a, b in pts], -BAY_D / 2 + 3.0, BAY_D / 2 - 1.0, mm, plane='XZ')
    # loader-fed ground hopper east of the bays with grizzly and a belt up to the transfer tower
    HX = 22.0
    s.box_mm((HX - 3.0, -3.0, 0.0), (HX + 3.0, 3.0, 0.6), m['concrete'])             # hopper kerb
    s.poly_prism([(HX - 2.7, 0.6), (HX + 2.7, 0.6), (HX + 0.6, -2.8), (HX - 0.6, -2.8)], -2.7, 2.7, m['steel'], plane='XZ')
    for k in range(9):
        s.box((0.08, 5.4, 0.12), (HX - 2.4 + k * 0.6, 0, 0.66), m['grey'])         # grizzly bars
    s.box_mm((HX - 3.5, -3.5, -3.5), (HX + 3.5, 3.5, -3.2), m['concrete'])          # pit floor (under hopper)
    pm.guard_box(s, HX - 3.0, -3.0, HX + 3.0, 3.0, 0.6, m['yellow'], open_side='x0')
    # transfer tower at the belt head
    TX, TZ = 52.0, 14.0
    for (dx, dy) in ((-2.5, -2.5), (2.5, -2.5), (-2.5, 2.5), (2.5, 2.5)):
        s.box((0.4, 0.4, TZ + 3.0), (TX + dx, dy, (TZ + 3.0) / 2), m['steel'])
    s.box_mm((TX - 3.0, -3.0, TZ - 0.6), (TX + 3.0, 3.0, TZ + 3.0), m['clad'])
    s.finish(col)

    # Inclined belt: tail under the hopper (feeder discharge), head into the transfer tower
    conv = pb.conveyor("FX_Belt", tail=(HX, 0.0, -2.2), head=(TX - 0.5, 0.0, TZ + 0.4), width=1.0,
                       col=col, mats=belt_mats, ground_z=0.0)

    pb.ref_human(ref, (-8, -13, 0))
    views = [("Preview_FluxStorage.png", (75, -60, 34), (12, 0, 4), 35)]
    r = finish_one(
        name, "FluxStorage",
        about=f"""
Covered storage for smelter flux and other bought-in solids: three loader bays (silica flux,
limestone, reverts) with 4 m concrete push walls under a steel monopitch roof, open to the south
for front-end loaders and trucks. A loader tips into a ground hopper with a grizzly east of the
bays; an inclined 1.0 m belt (troughed, continuous UVs, 1 UV = 1.2 m, belt loop
{conv['loop_length']:.1f} m) lifts it to a transfer tower, where it can join the plant's
blending conveyors. Own layout design. Origin: floor level at the hopper side of the building,
22 m west of the hopper centre (footprint below).
""",
        moving="""
| Part | Motion |
|---|---|
| FX_Belt_Belt | Panner along U: U speed = belt speed (m/s) / 1.2. Loop length in the about text |
| FX_Belt_HeadPulley / TailPulley | Spin about the pulley axis (local Y): deg/s = belt speed / 0.32 m x 57.3 |
""",
        dims="""
| Item | Value | Basis |
|---|---|---|
| Bays | 3 x 15 m wide, 20 m deep, push walls 4 m | Estimated |
| Roof | eave 12 m north, ~13.6 m south (open side, loader + tipping truck clearance) | Estimated |
| Pile per bay | ~12 m base, 3.6 m high, ~17 m long: ~430 m3 (about 650 t of silica flux at ~1.5 t/m3 bulk) | Estimated |
| Hopper | 6 x 6 m grizzly top at z 0.6, pit floor -3.5 | Estimated |
| Belt | 1.0 m wide, tail (22, 0, -2.2), head (51.5, 0, 14.4) | Estimated |

Footprint: building x -31 to 16, y -12 to 12; hopper x 19 to 25; transfer tower x 49 to 55.

**Connection points**

| Point | Position |
|---|---|
| Belt head discharge in the transfer tower (to the blending conveyors) | (51.5, 0.0, 14.4) |
| Loader tipping edge (hopper west side, open) | x 19, y -3 to 3, z 0.6 |
| Bay fronts (loader / truck access, south) | y -10, x -30 to 15 |
""",
        sources="own design; bulk density of silica sand ~1.5 t/m3 is a general handbook value (estimated, not checked against a plant).",
        views=views, ground=70.0)
    return r


# ===========================================================================
# Run: build everything (or the named assets) and write one README per folder
# ===========================================================================

BUILDERS = {
    "Substation": build_substation,
    "OxygenPlant": build_oxygen_plant,
    "FuelOilTankFarm": build_fuel_tank_farm,
    "GasMeteringStation": build_gas_metering_station,
    "FluxStorage": build_flux_storage,
}

INTROS = {
    "Substation": "High-voltage substation for the plant.",
    "OxygenPlant": "On-site cryogenic oxygen plant (air separation unit).",
    "FuelStorage": "Fuel receiving and storage: fuel oil tank farm and natural gas metering station.",
    "FluxStorage": "Covered flux, limestone and reverts storage with loader hopper and belt.",
}

COMMON_INTRO = """
Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_utilities.py`.
Fixed facility at its own origin (ground at the footprint centre, +X east, +Y north), not placed
in the plant layout. All layouts are Claude's own designs; dimensions are estimated unless the
table says otherwise.
"""


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    keys = argv or list(BUILDERS)
    by_folder = {}
    for k in keys:
        r = BUILDERS[k]()
        folder = {"FuelOilTankFarm": "FuelStorage", "GasMeteringStation": "FuelStorage"}.get(k, k)
        by_folder.setdefault(folder, []).append(r)
    if argv:           # partial runs leave the READMEs alone
        return
    for folder, results in by_folder.items():
        pm.write_group_readme(folder, INTROS[folder] + "\n" + COMMON_INTRO, results)


main()
