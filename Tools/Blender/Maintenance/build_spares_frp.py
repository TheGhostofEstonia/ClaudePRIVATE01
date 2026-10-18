"""
build_spares_frp.py - acid-resistant spares, baghouse spares and an FRP repair station.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_spares_frp.py
      (add  -- AcidPump  to build one asset only)

Assets (Meshes/SparesAndFRP/), each a standalone prop at its own origin:
    SM_AcidPumpSpare      lined end-suction pump on a skid, spare impeller on a stand
    SM_PipeSpoolRack      cantilever rack of FRP, lined-steel and HDPE spools + fittings
    SM_BaghouseSpares     rack of filter cages and bag boxes, plus loose single bag and cage
    SM_FRPRepairStation   bench, resin drums, glass-mat stand, extraction arm, pipe on trestles
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

FOLDER = "SparesAndFRP"


def pallet(p, x0, y0, x1, y1, m):
    """Timber pallet 0.144 m high under the given footprint."""
    p.box_mm((x0, y0, 0.122), (x1, y1, 0.144), m['wood'])
    for y in (y0, (y0 + y1) / 2 - 0.05, y1 - 0.1):
        p.box_mm((x0, y, 0.022), (x1, y + 0.1, 0.122), m['wood'])
    p.box_mm((x0, y0, 0), (x1, y1, 0.022), m['wood'])


def flanged_pipe(p, a, b, r, body, flange_m, flange_face=None):
    """Pipe spool from a to b with a flange at each end (optional lining colour on the faces)."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    p.cyl_between(a, b, r, body, seg=20)
    for q in (a, b):
        p.cyl_between(q - d * 0.03, q + d * 0.03, r * 1.55, flange_m, seg=20)
        if flange_face:
            p.cyl_between(q - d * 0.035, q + d * 0.035, r * 0.95, flange_face, seg=20)


# ===========================================================================
# Acid pump spare
# ===========================================================================

def build_acid_pump():
    name = "SM_AcidPumpSpare"
    col, ref, m = pm.start(name)
    lining = pb.mat("M_PTFE_Lining", (0.9, 0.9, 0.88), 0.0, 0.5)
    ap = pb.Part("AP_Pump")
    pallet(ap, -0.9, -0.5, 0.9, 0.5, m)
    ap.box_mm((-0.8, -0.35, 0.144), (0.8, 0.35, 0.24), m['steel'])          # baseplate
    ap.cyl(0.30, 0.25, (0.45, 0, 0.62), m['blue'], rot=(0, 90, 0), seg=28)  # volute (axis along X)
    ap.cyl_between((0.58, 0, 0.62), (0.80, 0, 0.62), 0.10, m['blue'], seg=16)   # end suction nozzle
    ap.cyl(0.16, 0.04, (0.81, 0, 0.62), lining, rot=(0, 90, 0), seg=20)          # lined flange face
    ap.cyl_between((0.45, 0, 0.92), (0.45, 0, 1.02), 0.08, m['blue'], seg=16)   # top discharge
    ap.cyl(0.13, 0.04, (0.45, 0, 1.03), lining, seg=20)
    ap.box_mm((-0.2, -0.18, 0.24), (0.3, 0.18, 0.62), m['blue'])                 # bearing frame
    ap.box_mm((0.25, -0.15, 0.24), (0.35, 0.15, 0.36), m['blue'])                # foot
    ap.box_mm((-0.7, -0.18, 0.24), (-0.2, 0.18, 0.4), m['steel'])                # empty motor position
    ap.finish(col)
    sh = pb.Part("AP_Shaft", pivot=(0, 0, 0.62))
    sh.cyl_between((-0.45, 0, 0.62), (0.32, 0, 0.62), 0.03, m['grey'], seg=12)
    sh.cyl(0.08, 0.06, (-0.42, 0, 0.62), m['steel'], rot=(0, 90, 0), seg=14)   # coupling half
    sh.finish(col)
    # spare impeller on a stand beside the pallet
    st = pb.Part("AP_ImpellerStand")
    st.box_mm((1.2, -0.25, 0), (1.7, 0.25, 0.05), m['steel'])
    st.cyl(0.03, 0.55, (1.45, 0, 0.3), m['steel'], seg=10)
    st.finish(col)
    c = Vector((1.45, 0, 0.64))
    im = pb.Part("AP_SpareImpeller", pivot=c)
    im.cyl(0.25, 0.03, c - Vector((0, 0, 0.05)), lining, seg=32)            # back shroud
    im.cyl(0.25, 0.03, c + Vector((0, 0, 0.05)), lining, seg=32, r2=0.10)   # front shroud
    for k in range(6):                                                      # curved vanes as two straight bits
        a0 = math.radians(60 * k)
        p0 = c + Vector((0.07 * math.cos(a0), 0.07 * math.sin(a0), 0))
        p1 = c + Vector((0.16 * math.cos(a0 + 0.35), 0.16 * math.sin(a0 + 0.35), 0))
        p2 = c + Vector((0.24 * math.cos(a0 + 0.8), 0.24 * math.sin(a0 + 0.8), 0))
        im.beam_between(p0, p1, 0.02, 0.08, lining)
        im.beam_between(p1, p2, 0.02, 0.08, lining)
    im.cyl(0.05, 0.14, c, m['grey'], seg=12)                                # hub
    im.finish(col)
    # crate of seals and liners
    cr = pb.Part("AP_SealCrate")
    cr.box_mm((-0.6, 0.7, 0), (0.0, 1.2, 0.45), m['wood'])
    cr.finish(col)
    pb.ref_human(ref, (-0.6, 1.6, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_AcidPumpSpare.png", (3.0, -3.0, 2.0), (0.4, 0, 0.5), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_AcidPumpSpare.png",
                about="""
Spare acid-service pump, ready to swap in: a lined end-suction centrifugal pump (PTFE-lined
casing, white flange faces) on its baseplate on a pallet, without motor; a spare impeller on a
stand; and a crate for mechanical seals and liners. Origin is the floor under the pallet centre.
""",
                moving="""
| Part | Motion |
|---|---|
| AP_Shaft | Spins about local X (once the pump is installed) |
| AP_SpareImpeller | Loose prop; pivot at its hub |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Pump about 1.6 m baseplate, Ø0.6 m volute, 200/160 mm nozzles | | Estimated (mid-size acid transfer pump) |
""",
                sources="research file (tankhouse and acid plant are very corrosive; acid-resistant pump spares)")


# ===========================================================================
# Pipe spool rack
# ===========================================================================

def build_pipe_rack():
    name = "SM_PipeSpoolRack"
    col, ref, m = pm.start(name)
    hdpe = pb.mat("M_HDPE_Black", (0.04, 0.04, 0.04), 0.0, 0.5)
    lining = pb.mat("M_PTFE_Lining", (0.9, 0.9, 0.88), 0.0, 0.5)
    L = 6.0
    rk = pb.Part("PSR_Rack")
    for x in (0.0, L / 2, L):                                               # cantilever columns
        rk.box_mm((x - 0.1, -0.1, 0), (x + 0.1, 0.1, 3.6), m['orange'])
        rk.box_mm((x - 0.1, -0.8, 0), (x + 0.1, 0.8, 0.12), m['orange'])  # base
        for z in (0.6, 1.5, 2.4, 3.3):                                      # arms toward +Y (one side)
            rk.box_mm((x - 0.06, 0.1, z - 0.08), (x + 0.06, 1.3, z), m['orange'])
            rk.box_mm((x - 0.06, 1.25, z), (x + 0.06, 1.3, z + 0.12), m['orange'])   # end stop
    rk.box_mm((0, -0.06, 1.0), (L, 0.06, 1.1), m['orange'])                 # bracing
    rk.finish(col)
    sp = pb.Part("PSR_Spools")
    # level 1: FRP spools (green)
    for i, (r, y) in enumerate(((0.16, 0.35), (0.16, 0.75), (0.11, 1.08))):
        flanged_pipe(sp, (0.3, y, 0.6 + r * 1.55), (L - 0.3, y, 0.6 + r * 1.55), r, m['frp'], m['frp'])
    # level 2: PTFE-lined steel spools (black body, white lining at the faces)
    for y in (0.35, 0.8):
        flanged_pipe(sp, (0.4, y, 1.5 + 0.12 * 1.55), (3.4, y, 1.5 + 0.12 * 1.55), 0.12, m['steel'], m['steel'], lining)
        flanged_pipe(sp, (3.6, y, 1.5 + 0.12 * 1.55), (5.6, y, 1.5 + 0.12 * 1.55), 0.12, m['steel'], m['steel'], lining)
    # level 3: HDPE lengths
    for y in (0.3, 0.55, 0.8, 1.05):
        sp.cyl_between((0.2, y, 2.4 + 0.1), (L - 0.2, y, 2.4 + 0.1), 0.1, hdpe, seg=16)
    # level 4: fittings (elbows as two segments, tees)
    for k in range(5):
        x = 0.6 + k * 1.1
        c = Vector((x, 0.6, 3.3 + 0.125))
        sp.cyl_between(c, c + Vector((0.35, 0, 0)), 0.12, m['frp'], seg=16)
        sp.cyl_between(c, c + Vector((0, 0.35, 0)), 0.12, m['frp'], seg=16)
        sp.sphere(0.125, c, m['frp'], seg=12)
    sp.finish(col)
    pb.ref_human(ref, (L / 2, 2.2, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_PipeSpoolRack.png", (8.5, 7.5, 3.5), (3.0, 0.6, 1.8), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_PipeSpoolRack.png",
                about=f"""
Single-sided cantilever rack ({L:.0f} m) holding spare pipe for the acid plant and tankhouse:
FRP spools (green) on the bottom level, PTFE-lined steel spools with white liner faces on the
second, HDPE lengths on the third and FRP elbows/tees on the top. Origin is the floor at the
first column; arms point +Y.
""",
                moving="Static. PSR_Spools is one part; split it in Unreal if single spools must be picked up.",
                dims="""
| Item | Value | Status |
|---|---|---|
| Rack 6 m, 4 levels, 1.2 m arms; pipe DN200-DN300 | | Estimated |
""",
                sources="research file (acid-resistant pipe spares)")


# ===========================================================================
# Baghouse spares
# ===========================================================================

BAG_R, CAGE_R, BAG_L = 0.0762, 0.073, 3.05     # 6 in bag, 5.75 in cage, 120 in long


def cage(p, base, m, wires=12, ring_step=0.203):
    """Pulse-jet filter cage lying along +X from base (wires, rings, venturi collar)."""
    b = Vector(base)
    for k in range(wires):
        a = 2 * math.pi * k / wires
        o = Vector((0, CAGE_R * math.cos(a), CAGE_R * math.sin(a)))
        p.cyl_between(b + o, b + o + Vector((BAG_L, 0, 0)), 0.0025, m['galv'], seg=4)
    x = 0.0
    while x <= BAG_L + 1e-3:
        pts = [b + Vector((x, CAGE_R * math.cos(2 * math.pi * k / 12), CAGE_R * math.sin(2 * math.pi * k / 12)))
               for k in range(13)]
        for q0, q1 in zip(pts, pts[1:]):
            p.cyl_between(q0, q1, 0.003, m['galv'], seg=4)
        x += ring_step
    p.cyl(CAGE_R + 0.008, 0.06, b - Vector((0.03, 0, 0)), m['galv'], rot=(0, 90, 0), seg=16)   # top collar
    p.cyl(CAGE_R, 0.01, b + Vector((BAG_L, 0, 0)), m['galv'], rot=(0, 90, 0), seg=16)          # bottom pan


def build_baghouse_spares():
    name = "SM_BaghouseSpares"
    col, ref, m = pm.start(name)
    felt = pb.mat("M_FilterFelt", (0.85, 0.83, 0.75), 0.0, 0.95)
    card = pb.mat("M_Cardboard", (0.6, 0.45, 0.28), 0.0, 0.9)
    RL = 3.4
    rk = pb.Part("BH_Rack")
    for x in (-0.1, RL / 2, RL + 0.1):
        rk.box_mm((x - 0.05, -0.05, 0), (x + 0.05, 0.05, 2.2), m['yellow'])
        rk.box_mm((x - 0.05, 1.05, 0), (x + 0.05, 1.15, 2.2), m['yellow'])
    for z in (0.15, 0.9, 1.6):
        for y in (0.0, 1.1):
            rk.box_mm((-0.1, y - 0.05, z - 0.06), (RL + 0.1, y + 0.05, z), m['yellow'])
        for x in (0.3, 1.0, 1.7, 2.4, 3.1):
            rk.box_mm((x - 0.03, 0.0, z - 0.06), (x + 0.03, 1.1, z), m['yellow'])   # cradle bars
    rk.finish(col)
    cg = pb.Part("BH_Cages_Stack")
    for j in range(2):                     # two layers of six cages on the middle level
        for i in range(6):
            cage(cg, (0.15, 0.12 + i * 0.16 + (0.08 if j else 0), 0.9 + CAGE_R + j * 0.14), m)
    cg.finish(col)
    bx = pb.Part("BH_BagBoxes")
    for i in range(3):                     # boxed bags (10 per box) on the bottom and top levels
        for z in (0.15, 1.6):
            bx.box_mm((0.1 + i * 1.1, 0.1, z), (1.0 + i * 1.1, 1.0, z + 0.35), card)
    bx.finish(col)
    # loose single bag and cage on the floor in front of the rack, as handheld props
    sb = pb.Part("BH_FilterBag_Single", pivot=(0.1, -0.6, BAG_R))
    sb.cyl_between((0.1, -0.6, BAG_R), (0.1 + BAG_L, -0.6, BAG_R), BAG_R, felt, seg=16)
    sb.cyl(BAG_R + 0.01, 0.03, (0.1, -0.6, BAG_R), m['steel'], rot=(0, 90, 0), seg=16)   # snap band
    sb.finish(col)
    sc = pb.Part("BH_FilterCage_Single", pivot=(0.1, -1.0, CAGE_R + 0.01))
    cage(sc, (0.1, -1.0, CAGE_R + 0.01), m)
    sc.finish(col)
    pb.ref_human(ref, (RL + 0.8, -0.6, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_BaghouseSpares.png", (5.0, -4.5, 2.8), (1.7, 0.3, 1.0), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_BaghouseSpares.png",
                about=f"""
Storage rack for pulse-jet baghouse spares: twelve wire cages on the middle level, boxed filter
bags above and below, and one loose bag and one loose cage on the floor in front for handheld
or install animations. Origin is the floor at the rack's -X/-Y corner. Bags and cages lie along
+X; the collar/snap-band end is at -X.
""",
                moving="""
| Part | Motion |
|---|---|
| BH_FilterBag_Single, BH_FilterCage_Single | Loose props; pivot at the collar end. Stand upright (rotate Y = -90°) to drop into a tube sheet |
""",
                dims=f"""
| Item | Value | Status |
|---|---|---|
| Bag Ø6 in (152 mm) × 120 in (3.05 m), cage Ø5.75 in | | Sourced (common 6 in bag / 5.75 in cage pairing, 96/120/144 in standard lengths) |
| 12 cage wires, rings every 8 in | | Sourced range (10/12/14 wires for most felts); ring spacing estimated |
| Rack 3.4 × 1.1 × 2.2 m | | Estimated |
""",
                sources="https://www.baghouse.com/how-to-measure-your-baghouse-filters-cages/ ; mpparts.com 6 in × 120 in bag listing")


# ===========================================================================
# FRP repair station
# ===========================================================================

def build_frp_station():
    name = "SM_FRPRepairStation"
    col, ref, m = pm.start(name)
    drum_m = pb.mat("M_Drum_Blue", (0.05, 0.2, 0.5), 0.3, 0.5)
    mat_m = pb.mat("M_GlassMat", (0.92, 0.92, 0.88), 0.0, 0.9)
    st = pb.Part("FRP_Station")
    # workbench
    st.box_mm((0, 0, 0.9), (2.4, 0.8, 0.95), m['steel'])
    for x in (0.05, 2.3):
        for y in (0.05, 0.7):
            st.box_mm((x, y, 0), (x + 0.05, y + 0.05, 0.9), m['steel'])
    st.box_mm((0.05, 0.05, 0.2), (2.35, 0.75, 0.23), m['steel'])
    st.cyl(0.15, 0.25, (0.4, 0.4, 1.07), m['white'], seg=16)                 # mixing bucket
    st.box_mm((1.0, 0.2, 0.95), (1.6, 0.6, 0.98), m['white'])                # cutting board
    # resin and hardener drums on a spill pallet
    st.box_mm((2.8, 0.0, 0), (4.1, 1.3, 0.3), m['yellow'])
    for x, y in ((3.12, 0.33), (3.78, 0.33), (3.12, 0.97)):
        st.cyl(0.29, 0.88, (x, y, 0.74), drum_m, seg=24)
    st.cyl(0.15, 0.4, (3.78, 0.97, 0.5), m['white'], seg=16)                 # hardener can
    # glass mat roll stand
    st.box_mm((4.6, 0.0, 0), (5.6, 0.1, 1.1), m['steel'])
    st.box_mm((4.6, 0.9, 0), (5.6, 1.0, 1.1), m['steel'])
    st.cyl(0.25, 0.85, (5.1, 0.5, 1.0), mat_m, rot=(90, 0, 0), seg=24)
    # flammables cabinet
    st.box_mm((-1.0, 0.0, 0), (-0.1, 0.5, 1.8), m['yellow'])
    # trestles with an FRP pipe section under repair (patch wrap in the middle)
    for x in (0.4, 2.6):
        for s in (1, -1):
            st.beam_between((x - 0.3, 2.0 + s * 0.3, 0), (x, 2.0, 0.75), 0.05, 0.05, m['steel'])
            st.beam_between((x + 0.3, 2.0 + s * 0.3, 0), (x, 2.0, 0.75), 0.05, 0.05, m['steel'])
        st.box_mm((x - 0.05, 1.7, 0.72), (x + 0.05, 2.3, 0.78), m['steel'])
    st.cyl_between((-0.3, 2.0, 1.08), (3.3, 2.0, 1.08), 0.3, m['frp'], seg=24)
    st.cyl_between((1.25, 2.0, 1.08), (1.75, 2.0, 1.08), 0.31, mat_m, seg=24)   # wet patch
    st.finish(col)
    # fume extraction arm on a wall post, separate parts so it can be swung over the work
    P = Vector((-0.4, 1.2, 2.6))
    ps = pb.Part("FRP_ExtractPost")
    ps.cyl(0.08, 2.6, (P.x, P.y, 1.3), m['grey'], seg=12)
    ps.box_mm((P.x - 0.25, P.y - 0.25, 0), (P.x + 0.25, P.y + 0.25, 0.05), m['steel'])
    ps.finish(col)
    a1 = pb.Part("FRP_ExtractArm1", pivot=P)
    a1.cyl_between(P, P + Vector((1.4, 0.0, 0.0)), 0.075, m['yellow'], seg=12)
    ob_a1 = a1.finish(col)
    Q = P + Vector((1.4, 0, 0))
    a2 = pb.Part("FRP_ExtractArm2", pivot=Q)
    a2.cyl_between(Q, Q + Vector((1.2, 0.0, -0.9)), 0.075, m['yellow'], seg=12)
    a2.cyl(0.2, 0.25, Q + Vector((1.25, 0, -1.0)), m['yellow'], seg=16, r2=0.08)   # hood
    ob_a2 = a2.finish(col)
    pm.parent(ob_a2, ob_a1)
    pb.ref_human(ref, (1.5, 1.2, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_FRPRepairStation.png", (5.5, -6.5, 4.2), (2.3, 0.8, 0.9), 30),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_FRPRepairStation.png",
                about="""
Workshop corner for repairing FRP pipe, ducts and tank parts from the acid plant and tankhouse:
a steel bench with mixing bucket and cutting board, resin and hardener drums on a spill pallet,
a glass-mat roll stand, a flammables cabinet, an FRP pipe on trestles with a wet patch wrap, and
a two-joint fume extraction arm over the job. Origin is the floor at the bench's -X/-Y corner.
""",
                moving="""
| Part | Motion |
|---|---|
| FRP_ExtractArm1 | Rotates about local Z on the post |
| FRP_ExtractArm2 | Child of Arm1; rotates about local Y and Z at the elbow |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| 205 L drums (Ø0.58 × 0.88 m) | | Standard drum size |
| Everything else | | Estimated |
""",
                sources="research file (FRP repair for corrosive areas)")


BUILDERS = dict(AcidPump=build_acid_pump, PipeRack=build_pipe_rack, Baghouse=build_baghouse_spares,
                FRPStation=build_frp_station)

INTRO = """
Spares and repair gear for the corrosive areas (acid plant, tankhouse) and the dust-collection
baghouses. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_spares_frp.py`. Each asset is a standalone prop at its own origin.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
