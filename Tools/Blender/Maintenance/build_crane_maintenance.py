"""
build_crane_maintenance.py - overhead crane maintenance gear.

Run:  blender -b --factory-startup --python Tools/Blender/Maintenance/build_crane_maintenance.py
      (add  -- Walkway  to build one asset only)

Assets (Meshes/CraneMaintenance/):
    SM_CraneRunwayWalkway   tiling 6 m runway walkway section + caged access ladder
    SM_RopeChangingRig      rope reel stand, pulling winch and guide rollers
    SM_SpareHookBlocks      50 t and 16 t spare hook blocks on a storage stand
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_build as pb  # noqa: E402
import psh_maint as pm  # noqa: E402

FOLDER = "CraneMaintenance"


# ===========================================================================
# Runway walkway
# ===========================================================================

def build_walkway():
    name = "SM_CraneRunwayWalkway"
    col, ref, m = pm.start(name)
    L, W = 6.0, 0.8
    sec = pb.Part("CRW_Section")
    sec.box_mm((0, 0, -0.04), (L, W, 0.0), m['galv'])                     # grating
    sec.box_mm((0, -0.05, -0.20), (0.1, W, -0.04), m['steel'])           # cross bearer (one per tile)
    sec.box_mm((0, W - 0.05, -0.20), (L, W, -0.04), m['steel'])           # outer stringer
    sec.box_mm((0, -0.05, -0.20), (L, 0.0, -0.04), m['steel'])            # inner stringer (on the girder side)
    for x in (0.0, L / 2):                                                # knee brackets back to the girder web
        sec.beam_between((x + 0.05, W - 0.05, -0.20), (x + 0.05, -0.05, -0.9), 0.08, 0.08, m['steel'])
    sec.box_mm((0, W - 0.03, 0.0), (L, W, 0.15), m['yellow'])             # toe board
    # outer handrail: posts every 2 m (last post belongs to the next tile)
    for x in (0.0, 2.0, 4.0):
        sec.cyl_between((x + 0.03, W - 0.05, 0), (x + 0.03, W - 0.05, 1.1), 0.025, m['yellow'], seg=8)
    for z in (0.55, 1.1):
        sec.cyl_between((0, W - 0.05, z), (L, W - 0.05, z), 0.022, m['yellow'], seg=8)
    sec.box_mm((0.4, W - 0.06, 0.95), (0.6, W - 0.04, 1.05), m['lamp'])  # walkway light
    sec.finish(col)
    # caged access ladder from the floor up to the walkway, placed at x = -0.6 behind the section start
    lad = pb.Part("CRW_CageLadder", pivot=(-0.6, W / 2, -12.0))
    base = Vector((-0.6, W / 2, -12.0))
    pb.ladder(lad, base, 1.1, m['yellow'], facing=0.0, width=0.45)
    z = base.z + 2.5
    while z < 1.1:                                                        # cage hoops
        for a0 in range(0, 180, 15):
            a1 = a0 + 15
            r = 0.38
            c = Vector((-0.6 - 0.38, W / 2, z))
            q0 = c + Vector((-r * math.sin(math.radians(a0)), r * math.cos(math.radians(a0)), 0))
            q1 = c + Vector((-r * math.sin(math.radians(a1)), r * math.cos(math.radians(a1)), 0))
            lad.cyl_between(q0, q1, 0.015, m['yellow'], seg=6)
        z += 0.9
    for a in (30, 90, 150):                                               # vertical cage straps
        c = Vector((-0.6 - 0.38, W / 2, 0))
        o = Vector((-0.38 * math.sin(math.radians(a)), 0.38 * math.cos(math.radians(a)), 0))
        lad.cyl_between(c + o + Vector((0, 0, base.z + 2.5)), c + o + Vector((0, 0, 1.1)), 0.012, m['yellow'], seg=6)
    lad.finish(col)
    # REF runway girder and crane rail beside the walkway (not exported)
    g = pb.Part("REF_RunwayGirder")
    gm = pb.mat("M_REF_Girder", (0.35, 0.35, 0.38), 0.6, 0.5)
    g.box_mm((-1.0, -0.65, -1.6), (L + 1.0, -0.05, -1.55), gm)
    g.box_mm((-1.0, -0.37, -1.55), (L + 1.0, -0.33, -0.05), gm)
    g.box_mm((-1.0, -0.65, -0.05), (L + 1.0, -0.05, 0.0), gm)
    g.box_mm((-1.0, -0.40, 0.0), (L + 1.0, -0.30, 0.15), gm)               # crane rail
    g.finish(ref)
    pb.ref_human(ref, (2.5, 0.4, 0.0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_CraneRunwayWalkway.png", (7.5, 5.0, 2.8), (2.5, 0.0, -0.8), 35),
    ], ground=None)
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_CraneRunwayWalkway.png",
                about=f"""
Walkway along an overhead crane runway girder for inspecting rails, end stops and the crane's
long-travel wheels. CRW_Section is a {L:.0f} m tile: place copies every {L:.0f} m along +X. Origin is
the inner edge of the walkway floor at the section start; the girder side is -Y, the open side
+Y. The floor is at the girder top flange (rail base). CRW_CageLadder climbs 12 m from the floor
below to the walkway and sits just before the section start; move it to suit (its pivot is the
ladder foot). The REF girder (1.6 m deep with a crane rail) is not exported.
""",
                moving="Static.",
                dims="""
| Item | Value | Status |
|---|---|---|
| Walkway 0.8 m clear, guardrail 1.1 m with mid rail, 150 mm toe board | | Common industrial practice (e.g. ISO 14122-2/-3 ranges); not sourced to one plant |
| Ladder cage from 2.5 m above the floor, hoops every 0.9 m | | Common practice, estimated |
| Girder depth 1.6 m, 12 m ladder | | Estimated |
""",
                sources="research file (crane maintenance list); ISO 14122 is the governing standard family (not checked line by line)")


# ===========================================================================
# Rope changing rig
# ===========================================================================

def build_rope_rig():
    name = "SM_RopeChangingRig"
    col, ref, m = pm.start(name)
    RZ, FR, CR, RW = 1.15, 1.0, 0.45, 1.0      # reel axle height, flange r, core r, width
    st = pb.Part("RCR_ReelStand")
    for s in (1, -1):
        y = s * (RW / 2 + 0.25)
        st.beam_between((-0.8, y, 0), (0, y, RZ + 0.1), 0.12, 0.12, m['red'])
        st.beam_between((0.8, y, 0), (0, y, RZ + 0.1), 0.12, 0.12, m['red'])
        st.beam_between((-0.8, y, 0.06), (0.8, y, 0.06), 0.12, 0.12, m['red'])
        st.box((0.18, 0.12, 0.18), (0, y, RZ), m['steel'])                 # bearing / jack head
    st.cyl(0.05, RW + 0.8, (0, 0, RZ), m['grey'], rot=(90, 0, 0), seg=12)  # axle
    st.box((0.25, 0.1, 0.4), (0.35, -(RW / 2 + 0.25), RZ - 0.2), m['steel'])   # band brake lever
    st.finish(col)
    re = pb.Part("RCR_Reel", pivot=(0, 0, RZ))
    for s in (1, -1):
        re.cyl(FR, 0.05, (0, s * RW / 2, RZ), m['wood'], rot=(90, 0, 0), seg=40)
    re.cyl(CR + 0.38, RW - 0.05, (0, 0, RZ), m['rope'], rot=(90, 0, 0), seg=40)   # wound rope
    ob_re = re.finish(col)
    # winch skid 9 m away along +X
    WX = 9.0
    wi = pb.Part("RCR_Winch")
    wi.box_mm((WX - 0.9, -0.7, 0), (WX + 0.9, 0.7, 0.18), m['steel'])
    for s in (1, -1):
        wi.box_mm((WX - 0.4, s * 0.55 - 0.05, 0.18), (WX + 0.4, s * 0.55 + 0.05, 1.05), m['blue'])
    wi.box_mm((WX + 0.45, -0.5, 0.18), (WX + 0.9, 0.5, 0.75), m['blue'])        # motor + gearbox
    wi.box_mm((WX - 1.3, -0.15, 0.0), (WX - 0.9, 0.15, 0.4), m['steel'])         # anchor lug
    wi.finish(col)
    dr = pb.Part("RCR_WinchDrum", pivot=(WX, 0, 0.75))
    dr.cyl(0.32, 0.95, (WX, 0, 0.75), m['steel'], rot=(90, 0, 0), seg=28)
    for s in (1, -1):
        dr.cyl(0.45, 0.04, (WX, s * 0.47, 0.75), m['steel'], rot=(90, 0, 0), seg=28)
    ob_dr = dr.finish(col)
    gr = pb.Part("RCR_GuideRollers")
    for x in (3.0, 6.0):
        gr.box_mm((x - 0.3, -0.35, 0), (x + 0.3, 0.35, 0.1), m['steel'])
        for s in (1, -1):
            gr.box_mm((x - 0.05, s * 0.25 - 0.03, 0.1), (x + 0.05, s * 0.25 + 0.03, 0.5), m['steel'])
        gr.cyl(0.1, 0.44, (x, 0, 0.35), m['grey'], rot=(90, 0, 0), seg=14)
    gr.finish(col)
    rp = pb.Part("RCR_Rope")   # paying out from the reel bottom, over the rollers, onto the drum
    pts = [(0, 0, RZ - CR - 0.38), (3.0, 0, 0.45), (6.0, 0, 0.45), (WX, 0, 0.75 - 0.32)]
    for a, b in zip(pts, pts[1:]):
        rp.cyl_between(a, b, 0.012, m['rope'], seg=6)
    rp.finish(col)
    pb.ref_human(ref, (4.5, -1.2, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_RopeChangingRig.png", (4.5, -12.0, 5.0), (4.5, 0, 0.6), 30),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_RopeChangingRig.png",
                about="""
Ground rig for reeving a new hoist rope into an overhead crane. The new rope pays off a reel on a
jack stand with a band brake, runs over floor guide rollers, and a pulling winch draws it (with
the old rope as a messenger) through the crane's sheaves. Origin is the floor under the reel
axle; the winch is 9 m along +X. RCR_Rope is a static straight-line run; replace it with a
spline in Unreal if the rope must follow the crane.
""",
                moving="""
| Part | Motion |
|---|---|
| RCR_Reel | Spins about local Y |
| RCR_WinchDrum | Spins about local Y. Rope speed = drum r (0.32 m) × ω |
| RCR_ReelStand, RCR_Winch, RCR_GuideRollers, RCR_Rope | Static |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| Reel Ø2.0 × 1.0 m, winch, roller spacing | | Estimated (typical wire-rope reel sizes, no one source) |
""",
                sources="research file (crane maintenance: rope-changing gear)")


# ===========================================================================
# Spare hook blocks
# ===========================================================================

def hook_block(prefix, centre, n_sheave, sheave_r, plate, hook_h, col, m, paint):
    """
    Hook block: side plates with sheaves on a cross pin (axis along Y) and a hook below on a
    swivel. Returns (frame, [sheaves], hook) objects. centre = sheave pin centre.
    """
    c = Vector(centre)
    pw, pd, ph = plate                          # plate width (X), stack depth (Y), height (Z)
    fr = pb.Part(prefix + "_Frame", pivot=c)
    for s in (1, -1):
        fr.box_mm((c.x - pw / 2, c.y + s * pd / 2 - 0.03, c.z - ph * 0.55), (c.x + pw / 2, c.y + s * pd / 2 + 0.03, c.z + ph * 0.45), paint)
    fr.cyl(0.06, pd + 0.1, c, m['grey'], rot=(90, 0, 0), seg=12)
    fr.box_mm((c.x - pw / 2, c.y - pd / 2, c.z - ph * 0.55 - 0.15), (c.x + pw / 2, c.y + pd / 2, c.z - ph * 0.55), m['steel'])   # crosshead
    for x in (-1, 1):   # yellow/black hazard faces stand in for the guard stripes
        fr.box_mm((c.x + x * pw / 2 - 0.01, c.y - pd / 2, c.z), (c.x + x * pw / 2 + 0.01, c.y + pd / 2, c.z + 0.1), m['yellow'])
    ob_fr = fr.finish(col)
    sheaves = []
    gap = (pd - 0.08) / n_sheave
    for i in range(n_sheave):
        y = c.y - pd / 2 + 0.04 + gap * (i + 0.5)
        sh = pb.Part(f"{prefix}_Sheave{i + 1}", pivot=(c.x, y, c.z))
        sh.cyl(sheave_r, gap * 0.7, (c.x, y, c.z), m['grey'], rot=(90, 0, 0), seg=32)
        sh.cyl(sheave_r * 0.92, gap * 0.85, (c.x, y, c.z), m['steel'], rot=(90, 0, 0), seg=32)
        sheaves.append(sh.finish(col))
    hz = c.z - ph * 0.55 - 0.15
    hk = pb.Part(prefix + "_Hook", pivot=(c.x, c.y, hz))
    hk.cyl(0.08 * hook_h, 0.25 * hook_h, (c.x, c.y, hz - 0.125 * hook_h), m['grey'], seg=14)   # shank / swivel
    # hook body: a bent tube sweep in the XZ plane
    r_in = 0.22 * hook_h
    t = 0.09 * hook_h
    cz = hz - 0.25 * hook_h - r_in - t
    pts = [Vector((c.x, c.y, hz - 0.25 * hook_h))]
    for a in range(0, 271, 15):
        ang = math.radians(a + 90)
        pts.append(Vector((c.x + (r_in + t / 2) * math.cos(ang) * -1, c.y, cz + (r_in + t / 2) * math.sin(ang))))
    for a, b in zip(pts, pts[1:]):
        hk.cyl_between(a, b, t * 0.55, m['steel'], seg=12)
    hk.box_mm((c.x - 0.02, c.y - 0.06, hz - 0.3 * hook_h), (c.x + r_in + t, c.y + 0.06, hz - 0.27 * hook_h), m['yellow'])   # safety latch
    ob_hk = hk.finish(col)
    pm.parent(ob_hk, ob_fr)
    for sh in sheaves:
        pm.parent(sh, ob_fr)
    return ob_fr, sheaves, ob_hk


def build_hook_blocks():
    name = "SM_SpareHookBlocks"
    col, ref, m = pm.start(name)
    st = pb.Part("SHB_Stand")
    st.box_mm((-2.0, -1.0, 0), (2.0, 1.7, 0.12), m['steel'])                # skid base
    for x in (-1.0, 1.0):                                                   # timber cradles
        for y in (-0.6, 0.0, 0.8):
            st.box_mm((x - 0.6, y - 0.1, 0.12), (x + 0.6, y + 0.1, 0.30), m['wood'])
    for x in (-2.0, 1.94):                                                  # end posts with lifting eyes
        st.box_mm((x, -1.0, 0.12), (x + 0.06, 1.7, 0.6), m['red'])
    st.finish(col)
    # blocks are built upright, then laid on their side plates (root rotated X = +90, hook toward +Y)
    for nm, x, n, sr, plate, hh in (("SHB_Block50t", -1.0, 4, 0.36, (0.95, 0.55, 1.05), 1.1),
                                    ("SHB_Block16t", 1.0, 2, 0.25, (0.65, 0.30, 0.70), 0.75)):
        fr, _, _ = hook_block(nm, (x, 0.0, 2.0), n, sr, plate, hh, col, m, m['yellow'])
        fr.rotation_euler.x = math.radians(90)
        fr.location = (x, -0.35, 0.30 + plate[1] / 2 + 0.03)
    pb.ref_human(ref, (2.6, 0.3, 0))
    n_obj, n_tri = pm.counts(name)
    table = pm.finish_asset(name, FOLDER, [
        ("Preview_SpareHookBlocks.png", (3.0, -4.5, 3.2), (0, 0.3, 0.5), 35),
    ])
    return dict(name=name, table=table, n_obj=n_obj, n_tri=n_tri, previews="Preview_SpareHookBlocks.png",
                about="""
Two spare hook blocks laid on their side plates on timber cradles on a skid: a 4-sheave 50 t
block and a 2-sheave 16 t block, each with a hook on a swivel and a safety latch. Each block is a
set of parts so it can be picked up by a crane in game. Origin is the floor at the stand centre.
The block frames carry a rotation of X = +90° (hook pointing +Y); set rotation X = 0 to hang a
block upright from a crane.
""",
                moving="""
| Part | Motion |
|---|---|
| SHB_Block50t_Frame, SHB_Block16t_Frame | Root of each block: move as a whole when lifted (sheave pin centre is the pivot) |
| SHB_Block*_SheaveN | Spin about local Y |
| SHB_Block*_Hook | Swivels about local Z |
""",
                dims="""
| Item | Value | Status |
|---|---|---|
| 50 t, 5-sheave block for 16 mm rope weighs about 475 kg (mobile crane type) | | Sourced (Tadano listing) but overhead-crane blocks are heavier; Mennens 5-sheave blocks run about 1.8-3.6 t |
| Sheave Ø0.72 m (50 t) / Ø0.50 m (16 t), plate sizes, hook size | | Estimated (sheave Ø ≈ 25-30 × rope Ø for 22-28 mm rope) |
""",
                sources="cranetrader.com Tadano 50 t block listing; mennens.nl 5-sheave block product sheet")


BUILDERS = dict(Walkway=build_walkway, RopeRig=build_rope_rig, HookBlocks=build_hook_blocks)

INTRO = """
Gear for keeping the overhead cranes running: runway walkway sections, rope-changing equipment
and spare hook blocks. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Maintenance/build_crane_maintenance.py`. Each asset sits at its own origin. The
research file notes that cranes are single points of failure in a smelter, which is why spares
are kept ready.
"""


if __name__ == "__main__":
    pm.run(BUILDERS, FOLDER, INTRO)
