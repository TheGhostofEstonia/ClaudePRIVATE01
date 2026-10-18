"""
build_cathode_bundling_line.py - SM_CathodeBundlingLine (squaring, weighing, strapping, labelling).

Run:  blender -b --factory-startup --python Tools/Blender/AnodeCathodeMachines/build_cathode_bundling_line.py

Takes stacks of stripped cathode sheets from SM_CathodeStrippingMachine and turns them
into shipping bundles: square the stack -> weigh -> strap lengthwise -> turn 90 deg ->
strap crosswise -> print and apply the label -> accumulate for the forklift.
Also exports BL_Prop_CathodeBundle, a finished strapped bundle as its own mesh.
Layout and machine sizes are my own design. Bundle mass and labelling content are sourced.
"""
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # shared psh_build.py
import acm_common as ac  # noqa: E402
from acm_common import pb  # noqa: E402

ASSET, NAME = "CathodeBundlingLine", "SM_CathodeBundlingLine"

# ---------------------------------------------------------------------------
# Layout parameters (metres). Own design unless stated.
# ---------------------------------------------------------------------------
RZ = 0.45                     # roller top, same as the stripping machine's stack conveyor
WIDTH = 1.30                  # roller length
SHEETS = 30                   # sheets per bundle (~2.0 t)
BH = SHEETS * ac.DEPOSIT_T + 0.01   # bundle height incl. air gaps
STRAP1_X, TURN_X, STRAP2_X, LABEL_X = 8.2, 10.2, 12.2, 14.5
OUT = (15.5, 21.5)            # outfeed accumulation, forklift pickup at the end


def strap_arch(prefix, x, col, M):
    """Strapping arch: portal, strap guide track around the bundle, head and press platen on top."""
    a = pb.Part(prefix + "_Arch", pivot=(x, 0, 0))
    ac.portal(a, x, 1.05, 1.75, M, depth=0.35, beam=0.35)
    # strap guide track: four channels round the window, the bottom one runs between rollers
    for z in (RZ - 0.10, 1.45):
        a.box_mm((x - 0.04, -0.85, z - 0.03), (x + 0.04, 0.85, z + 0.03), M['grey'])
    for s in (-1, 1):
        a.box_mm((x - 0.04, s * 0.85 - 0.03, RZ - 0.10), (x + 0.04, s * 0.85 + 0.03, 1.45), M['grey'])
    a.box((0.7, 0.6, 0.45), (x, 1.45, 0.6), M['cabinet'])         # strap dispenser (coil)
    a.cyl(0.35, 0.12, (x + 0.45, 1.45, 0.6), M['strap'], rot=(0, 90, 0), seg=20)
    a.box((0.6, 0.5, 0.35), (x, 0.0, 1.95), M['frame'])            # head housing on the beam
    a.finish(col)
    pr = pb.Part(prefix + "_PressPlaten", pivot=(x, 0, RZ + BH + 0.05))
    pr.box((0.30, 1.10, 0.06), (x, 0, RZ + BH + 0.05), M['grey'])
    pr.box((0.18, 0.40, 0.20), (x, 0, RZ + BH + 0.18), M['steel'])  # sealing head (rides on the platen)
    pr.finish(col)
    ac.hyd_cylinder(prefix + "_PressCyl", (x, 0.35, 1.75), (x, 0.35, RZ + BH + 0.10), col, M, r=0.05)


def add_bundle(p, x, M, straps=True, label=True):
    """Finished bundle: sheet stack, two straps each way, label on the -Y face."""
    L, W = ac.DEPOSIT_H, ac.DEPOSIT_W
    for k in range(SHEETS):
        p.box((L, W, ac.DEPOSIT_T * 0.98), (x, 0, RZ + k * ac.DEPOSIT_T + ac.DEPOSIT_T / 2), M['copper'])
    if straps:
        t, w = 0.004, 0.032
        top, bot = RZ + SHEETS * ac.DEPOSIT_T + t / 2, RZ - t / 2
        for dx in (-0.25, 0.25):          # crosswise straps (loop in the YZ plane)
            p.box((w, W + 2 * t, t), (x + dx, 0, top), M['strap'])
            p.box((w, W + 2 * t, t), (x + dx, 0, bot), M['strap'])
            for s in (-1, 1):
                p.box((w, t, top - bot), (x + dx, s * (W / 2 + t / 2), (top + bot) / 2), M['strap'])
        for dy in (-0.25, 0.25):          # lengthwise straps (loop in the XZ plane)
            p.box((L + 2 * t, w, t), (x, dy, top + t), M['strap'])
            p.box((L + 2 * t, w, t), (x, dy, bot - t), M['strap'])
            for s in (-1, 1):
                p.box((t, w, top - bot + 2 * t), (x + s * (L / 2 + t / 2), dy, (top + bot) / 2), M['strap'])
    if label:
        p.box((0.20, 0.003, 0.12), (x, -W / 2 - 0.006, RZ + BH / 2), M['label'])
    return p


def build(col, ref, M):
    # --- roller conveyors, split where strap tracks pass between rollers ---
    ac.roller_conveyor("BL_Infeed", 0.0, 5.0, 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BL_Weigh", 5.05, 7.0, 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BL_Strap1In", 7.05, STRAP1_X - 0.12, 0.0, RZ, WIDTH, col, M, pitch=0.25)
    ac.roller_conveyor("BL_Strap1Out", STRAP1_X + 0.12, 9.3, 0.0, RZ, WIDTH, col, M, pitch=0.25)
    ac.roller_conveyor("BL_Turntable", TURN_X - 0.7, TURN_X + 0.7, 0.0, RZ, WIDTH, col, M, legs=False, base_z=0.25)
    ac.roller_conveyor("BL_Strap2In", 11.1, STRAP2_X - 0.12, 0.0, RZ, WIDTH, col, M, pitch=0.25)
    ac.roller_conveyor("BL_Strap2Out", STRAP2_X + 0.12, 13.4, 0.0, RZ, WIDTH, col, M, pitch=0.25)
    ac.roller_conveyor("BL_Label", 13.45, OUT[0], 0.0, RZ, WIDTH, col, M)
    ac.roller_conveyor("BL_Outfeed", OUT[0] + 0.05, OUT[1], 0.0, RZ, WIDTH, col, M)

    # --- squaring station: side pushers and a pop-up end stop ---
    sq = pb.Part("BL_SquareFrame", pivot=(4.0, 0, 0))
    for s in (-1, 1):
        sq.box_mm((3.3, s * 1.05 - 0.15, 0), (4.7, s * 1.05 + 0.15, RZ + 0.5), M['frame'])
    sq.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        pu = pb.Part(f"BL_Squarer_{side}", pivot=(4.0, s * 0.62, RZ + 0.12))
        pu.box((1.10, 0.05, 0.22), (4.0, s * 0.62, RZ + 0.12), M['grey'])
        pu.box((0.3, 0.3, 0.12), (4.0, s * 0.75, RZ + 0.12), M['steel'])
        pu.finish(col)
        ac.hyd_cylinder(f"BL_SquarerCyl_{side}", (4.0, s * 1.0, RZ + 0.12), (4.0, s * 0.80, RZ + 0.12), col, M, r=0.05)
    stop = pb.Part("BL_SquareStop", pivot=(4.62, 0, RZ))
    stop.box((0.05, 1.0, 0.25), (4.62, 0, RZ + 0.08), M['yellow'])
    stop.finish(col)

    # --- weigh: the BL_Weigh conveyor frame sits on four load cells, big remote display ---
    wg = pb.Part("BL_ScaleBase", pivot=(6.0, 0, 0))
    wg.box_mm((5.05, -0.85, 0), (7.0, 0.85, 0.06), M['steel'])
    for x in (5.2, 6.85):
        for y in (-0.75, 0.75):
            wg.cyl(0.06, 0.08, (x, y, 0.10), M['grey'], seg=12)
    wg.box((0.08, 0.08, 2.4), (6.0, -1.5, 1.2), M['frame'])
    wg.box((0.9, 0.12, 0.45), (6.0, -1.5, 2.5), M['cabinet'])
    wg.box((0.75, 0.01, 0.25), (6.0, -1.565, 2.52), M['green'])
    wg.finish(col)

    # --- strapping: two arches with the turntable between them ---
    strap_arch("BL_Strap1", STRAP1_X, col, M)
    strap_arch("BL_Strap2", STRAP2_X, col, M)
    tt = pb.Part("BL_Turntable", pivot=(TURN_X, 0, 0.25))
    tt.cyl(0.95, 0.10, (TURN_X, 0, 0.30), M['frame'], seg=32)
    tt.finish(col)
    tb = pb.Part("BL_TurntableBase", pivot=(TURN_X, 0, 0))
    tb.cyl(1.0, 0.25, (TURN_X, 0, 0.125), M['steel'], seg=32)
    tb.finish(col)
    for ob in list(bpy.data.objects):     # rollers and frame turn with the table
        if ob.name.startswith("BL_Turntable_"):
            mw = ob.matrix_world.copy()
            ob.parent = bpy.data.objects["BL_Turntable"]
            ob.matrix_world = mw

    # --- labelling: printer cabinet and robot with a label applicator ---
    def applicator(p, flange, fwd):
        p.box((0.16, 0.16, 0.22), flange + fwd * 0.10, M['cabinet'])
        p.box((0.04, 0.24, 0.16), flange + fwd * 0.21, M['rubber'])
    ac.robot_arm("BL_LabelRobot", (LABEL_X, -1.35, 0.0), col, M, yaw=90, reach=1.3, tool=applicator)
    lb = pb.Part("BL_LabelStation", pivot=(LABEL_X, -1.35, 0))
    lb.box((0.8, 0.6, 1.3), (LABEL_X + 0.9, -1.55, 0.65), M['cabinet'])     # label printer
    lb.box((0.5, 0.02, 0.08), (LABEL_X + 0.9, -1.24, 1.0), M['steel'])     # label exit slot
    lb.box((1.2, 0.5, 2.0), (LABEL_X - 1.0, -1.8, 1.0), M['cabinet'])      # robot controller
    lb.finish(col)

    # --- outfeed: end stop, light curtain posts at the forklift side ---
    of = pb.Part("BL_OutfeedStop", pivot=(OUT[1], 0, 0))
    of.box_mm((OUT[1] + 0.15, -0.8, 0), (OUT[1] + 0.35, 0.8, RZ + 0.45), M['yellow'])
    for y in (-1.0, 1.0):
        of.box((0.08, 0.08, 1.8), (OUT[0] + 0.2, y, 0.9), M['yellow'])
    of.finish(col)

    # --- guards and dressing ---
    gd = pb.Part("BL_Guards", pivot=(0, 0, 0))
    ac.guard_fence(gd, (7.0, 1.9, 0), (OUT[0], 1.9, 0), M)
    ac.guard_fence(gd, (7.0, -2.4, 0), (OUT[0], -2.4, 0), M)
    gd.finish(col)
    dr = pb.Part("BL_Dressing", pivot=(0, 0, 0))
    ac.cabinet(dr, (10.2, 2.4, 0), M, size=(2.4, 0.6, 2.1))
    ac.hpu(dr, (2.0, 2.3, 0), M)
    dr.finish(col)

    # --- exported prop: one finished bundle, origin at its base centre ---
    bp = pb.Part("BL_Prop_CathodeBundle", pivot=(OUT[1] - 0.7, 0, RZ))
    add_bundle(bp, OUT[1] - 0.7, M)
    bp.finish(col)

    # --- REF: stacks and bundles moving through the line ---
    r = pb.Part("REF_Bundles", pivot=(0, 0, 0))
    add_bundle(r, 1.5, M, straps=False, label=False)
    add_bundle(r, 4.0, M, straps=False, label=False)
    add_bundle(r, 6.0, M, straps=False, label=False)
    add_bundle(r, STRAP1_X, M, straps=False, label=False)
    add_bundle(r, LABEL_X, M)
    add_bundle(r, OUT[1] - 2.0, M)
    r.finish(ref)
    ac.floor_ref(ref, -2, 23, -4, 4)


def readme(col):
    rows = pb.pivot_table([col.name])
    m = SHEETS * ac.DEPOSIT_W * ac.DEPOSIT_H * ac.DEPOSIT_T * 8940
    return f"""# SM_CathodeBundlingLine - cathode squaring, weighing, strapping and labelling

Turns each stack of stripped sheets into a shipping bundle. Stacks arrive on rollers from
SM_CathodeStrippingMachine, are squared, weighed, strapped lengthwise, turned 90°, strapped
crosswise, labelled by a robot and collected at the end for the forklift.

**Own design** for the layout and machine sizes. Sourced: bundle mass, steel strapping, labels
carrying product, bundle number and net weight.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Bundles move along +X.
- Footprint: x -0.2 to 21.9, y -2.5 to 2.9 (about 22.1 x 5.4 m).
- Infeed: roller top z = {RZ} m, roller length {WIDTH} m, at x = 0. Matches the stripping machine's stack
  conveyor (also z = {RZ}); place this line so x = 0 meets its open end.
- Outfeed: forklift pickup at the end stop, x = {OUT[1] + 0.15:.2f}, room for about three bundles.
- Bundle: {ac.DEPOSIT_H} x {ac.DEPOSIT_W} x {BH:.2f} m, {SHEETS} sheets, about {m / 1000:.1f} t.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| BL_*_Roller_NN | Spin about Y | roller axes |
| BL_Squarer_L/R | Slide along Y toward the stack, 0.10 m | see table |
| BL_SquareStop | Pops up 0.25 m between the rollers (drawn up) | (4.62, 0, {RZ}) |
| BL_Strap1/2_PressPlaten | Moves down onto the bundle while the strap is tensioned and sealed | see table |
| BL_Turntable | Rotates 90° about Z; its rollers and frame are parented to it | ({TURN_X}, 0, 0.25) |
| BL_LabelRobot_J1..J6 | Six-axis arm, links parented in order; J1 about Z, J2/J3/J5 about local Y, J4/J6 about local X | see table |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

{ac.UNREAL_NOTE}
BL_Prop_CathodeBundle is a finished bundle (straps and label included) to use as a prop or a
physics actor. Its pivot is its base centre.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Bundle mass | about {m / 1000:.1f} t | Sourced: 1-4 t per bundle (Tata AIG cargo note), ~2,000 kg at one producer |
| Strapping | Steel straps, 2 each way | Steel strapping sourced; strap count and 32 x 4 mm strap estimated |
| Label | Product, bundle number, net weight | Sourced (producer); 200 x 120 mm label size estimated |
| Sheet | {ac.DEPOSIT_W} x {ac.DEPOSIT_H} m x {ac.DEPOSIT_T * 1000:.0f} mm | Estimated, same as the stripping machine |
| Strapping arches 2.4 m wide x 2.1 m high, turntable Ø1.9 m, robot reach ~1.3 m | | Estimated |

Sources: research/copper-refinery/copper-refinery-equipment.md [S26] [S27].

## Files

- SM_CathodeBundlingLine.blend / .fbx (REF bundles, floor and figure not exported)
- Preview_Overview.png, Preview_Strapping.png, Preview_Label.png
"""


VIEWS = [
    ("Preview_Overview.png", (-3, -11, 7), (11, 0, 0.0), 24),
    ("Preview_Strapping.png", (6.6, -3.4, 2.3), (9.2, 0, 0.7), 28, ("Guards",)),
    ("Preview_Label.png", (12.8, 3.4, 2.6), (14.6, -0.9, 0.9), 30, ("Guards",)),
]

if __name__ == "__main__":
    ac.run(ASSET, NAME, build, readme, VIEWS)
