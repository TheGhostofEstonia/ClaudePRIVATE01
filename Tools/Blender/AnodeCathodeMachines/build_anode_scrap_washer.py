"""
build_anode_scrap_washer.py - SM_AnodeScrapWasher (spent anode washing and stacking).

Run:  blender -b --factory-startup --python Tools/Blender/AnodeCathodeMachines/build_anode_scrap_washer.py

Spent anodes (13-20 % of the anode left) come out of the cells on the crane with
slimes stuck to them. The line washes them, tips them flat and stacks them for the
forklift, which takes them back to the anode furnace. Wash water and slimes drain
to a settling tank; the underflow is pumped to the slimes plant.
Layout and sizes are my own design; the research only names "spray wash line and stacker".
"""
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import acm_common as ac  # noqa: E402
from acm_common import pb  # noqa: E402

ASSET, NAME = "AnodeScrapWasher", "SM_AnodeScrapWasher"

# ---------------------------------------------------------------------------
# Layout parameters (metres). Own design unless stated.
# ---------------------------------------------------------------------------
Z = ac.HANG_Z                 # lug seat height (same as the anode prep machine)
CHAIN_Y = 0.56
LUG_Y = 0.585
WB_Y = 0.50
RECEIVE = (0.0, 6.0)          # crane drop zone
WASH = (6.4, 11.4)            # wash chains inside the hood
PICK, TILT = 11.9, 13.4       # walking-beam pick (end of wash) and tilter station
LOAD = 45                     # scrap anodes per cell load
SCRAP_H = ac.ANODE_H * 0.82   # spent anode body height (eaten from the bottom too)
BODY_BOT = Z + ac.ANODE_LUG_H - 0.03 - SCRAP_H
HINGE = (TILT + 0.03, 0.0, BODY_BOT - 0.02)   # tilter axis (along Y)
STACK_Z = 0.45                # roller top of the stack conveyor
STACK_N = 20                  # scrap anodes per forklift stack
OUT_X = 21.5                  # stack conveyor end (forklift pickup)


def build(col, ref, M):
    # --- chains and hood ---
    ac.chain_conveyor("SW_Receive", RECEIVE[0], RECEIVE[1], CHAIN_Y, Z, col, M)
    ac.chain_conveyor("SW_Wash", WASH[0], WASH[1], CHAIN_Y, Z, col, M)
    ac.wash_hood("SW_WashHood", WASH[0] + 0.2, WASH[1] - 0.2, Z, BODY_BOT, col, M)

    # --- station frame: lug rails from the wash exit to the tilter ---
    st = pb.Part("SW_StationFrame", pivot=(WASH[1], 0, 0))
    x0, x1 = WASH[1] + 0.1, TILT - 0.25
    for s in (-1, 1):
        st.box_mm((x0, s * LUG_Y - 0.04, Z - 0.08), (x1, s * LUG_Y + 0.04, Z), M['grey'])
        st.box_mm((x0, s * LUG_Y - 0.04, Z - 0.22), (x1, s * 0.9 + 0.08, Z - 0.08), M['frame'])
        for x in (x0 + 0.1, x1 - 0.1):
            st.box_mm((x - 0.08, s * 0.9 - 0.08, 0), (x + 0.08, s * 0.9 + 0.08, Z - 0.22), M['frame'])
    st.finish(col)

    # --- walking beam: one 1.5 m step from the wash exit into the tilter hooks ---
    wb_x0, wb_x1 = PICK - 0.4, TILT + 0.3
    wb = pb.Part("SW_WalkingBeam", pivot=(wb_x0, 0, 0.30))
    for s in (-1, 1):
        wb.box_mm((wb_x0, s * WB_Y - 0.02, Z - 0.16), (wb_x1, s * WB_Y + 0.02, Z - 0.04), M['grey'])
        for x in (PICK, TILT):
            wb.box((0.08, 0.04, 0.03), (x, s * WB_Y, Z - 0.025), M['steel'])
        wb.box_mm((wb_x0 - 0.05, s * WB_Y - 0.02, 0.30), (wb_x0 + 0.05, s * WB_Y + 0.02, Z - 0.16), M['grey'])
    wb.box_mm((wb_x0 - 0.08, -WB_Y - 0.02, 0.20), (wb_x0 + 0.08, WB_Y + 0.02, 0.30), M['frame'])
    wb.finish(col)
    ac.hyd_cylinder("SW_WalkingBeam_TravelCyl", (wb_x0 - 1.6, 0, 0.12), (wb_x0 - 0.08, 0, 0.12), col, M, r=0.05)

    # --- tilter: cradle with lug hooks, rotates +90 deg about Y so the anode lies flat (lugs toward +X) ---
    hx, _, hz = HINGE
    tl = pb.Part("SW_Tilter", pivot=HINGE)
    tl.cyl(0.06, 1.7, HINGE, M['grey'], rot=(90, 0, 0), seg=14)
    for s in (-1, 1):
        tl.box_mm((hx - 0.04, s * 0.72 - 0.04, hz), (hx + 0.04, s * 0.72 + 0.04, Z + 0.12), M['frame'])   # arm
        tl.box_mm((hx - 0.08, min(s * LUG_Y, s * 0.72), Z - 0.06), (hx + 0.08, max(s * LUG_Y, s * 0.72), Z), M['yellow'])  # lug hook
    for z in (hz + 0.15, hz + 0.45, Z - 0.25):    # back bars that carry the face when tipped
        tl.box_mm((hx + 0.01, -0.72, z - 0.03), (hx + 0.05, 0.72, z + 0.03), M['frame'])
    tl.finish(col)
    tf = pb.Part("SW_TilterFrame", pivot=(hx, 0, 0))
    for s in (-1, 1):
        tf.box_mm((hx - 0.15, s * 0.95 - 0.12, 0), (hx + 0.15, s * 0.95 + 0.12, hz + 0.1), M['frame'])
        tf.box((0.25, 0.2, 0.2), (hx, s * 0.95, hz), M['steel'])     # bearing block
    tf.box((0.5, 0.35, 0.35), (hx, -1.25, hz), M['frame'])             # rotary actuator
    tf.finish(col)

    # --- stack conveyor, lift forks under the tipped anode, end stop for the forklift ---
    xs = ac.roller_conveyor("SW_StackConv", hx - 0.3, OUT_X, 0.0, STACK_Z, 1.40, col, M, pitch=0.30)
    cx = hx + 0.48
    fk = pb.Part("SW_StackForks", pivot=(cx, -1.15, hz - 0.03))
    for gx in [(a + b) / 2 for a, b in zip(xs, xs[1:]) if 0.05 < (a + b) / 2 - hx < 0.95]:
        fk.box_mm((gx - 0.025, -0.80, hz - 0.07), (gx + 0.025, 0.80, hz - 0.03), M['grey'])
    fk.box_mm((hx + 0.05, -1.25, hz - 0.20), (hx + 0.95, -0.95, hz), M['frame'])
    fk.finish(col)
    sk = pb.Part("SW_StackerFrame", pivot=(cx, -1.4, 0))
    sk.box_mm((cx - 0.25, -1.55, 0), (cx + 0.25, -1.30, hz + 0.6), M['frame'])          # fork mast
    sk.box_mm((OUT_X + 0.2, -0.9, 0), (OUT_X + 0.4, 0.9, STACK_Z + 0.5), M['yellow'])    # end stop
    for x in (cx + 1.6, OUT_X - 2.0):                                                    # side guides
        for s in (-1, 1):
            sk.box_mm((x - 0.6, s * 0.78 - 0.02, STACK_Z), (x + 0.6, s * 0.78 + 0.02, STACK_Z + 0.25), M['grey'])
    sk.finish(col)

    # --- slimes: settling tank with cone bottom, slurry pump, pipe from the hood drain ---
    sl = pb.Part("SW_SlimesTank", pivot=(8.9, -3.2, 0))
    tx, ty = 8.9, -3.2
    sl.cyl(1.1, 1.6, (tx, ty, 2.6), M['stainless'], seg=24)
    sl.cyl(1.1, 0.9, (tx, ty, 1.35), M['stainless'], r2=0.15, seg=24)
    for a in (45, 135, 225, 315):
        dx, dy = math.cos(math.radians(a)) * 1.0, math.sin(math.radians(a)) * 1.0
        sl.box((0.12, 0.12, 2.0), (tx + dx, ty + dy, 1.0), M['frame'])
    sl.box((1.0, 0.6, 0.5), (tx + 1.8, ty, 0.25), M['frame'])            # slurry pump skid
    sl.cyl(0.18, 0.5, (tx + 1.6, ty, 0.6), M['frame'], rot=(0, 90, 0), seg=14)
    sl.cyl_between((tx, ty, 0.85), (tx + 1.4, ty, 0.55), 0.06, M['grey'])
    sl.cyl_between((tx + 2.2, ty, 0.6), (tx + 2.2, ty, 3.6), 0.05, M['grey'])          # to slimes plant
    sl.cyl_between((tx + 2.2, ty, 3.6), (tx + 2.2, ty - 1.5, 3.6), 0.05, M['grey'])
    sl.cyl_between((tx - 0.9, -1.2, 0.15), (tx - 0.9, ty + 0.5, 3.4), 0.07, M['grey'])  # hood drain line
    sl.finish(col)

    # --- guards and dressing ---
    gd = pb.Part("SW_Guards", pivot=(0, 0, 0))
    ac.guard_fence(gd, (WASH[1], 1.6, 0), (hx + 2.0, 1.6, 0), M)
    ac.guard_fence(gd, (WASH[1], -1.9, 0), (hx + 2.0, -1.9, 0), M)
    gd.finish(col)
    dr = pb.Part("SW_Dressing", pivot=(0, 0, 0))
    ac.hpu(dr, (13.6, 3.0, 0), M)
    ac.cabinet(dr, (9.0, 2.2, 0), M, size=(2.0, 0.6, 2.1))
    ac.platform(dr, 6.6, 11.2, 1.25, 2.0, 1.5, M, ladder_at=(6.9, 1.6, 0))
    dr.finish(col)

    # --- REF: cell load of spent anodes, anodes in the wash, one in the hooks, two stacks ---
    r = pb.Part("REF_ScrapAnodes", pivot=(0, 0, 0))
    for i in range(LOAD):
        ac.add_anode(r, 0.4 + i * ac.PITCH, Z, M, scrap=True)
    for i in range(10):
        ac.add_anode(r, WASH[0] + 0.5 + i * 0.45, Z, M, scrap=True)
    ac.add_anode(r, PICK, Z, M, scrap=True)
    ac.add_anode(r, TILT, Z, M, scrap=True)
    for sx in (hx + 2.4, OUT_X - 1.0):
        for k in range(STACK_N):
            z = STACK_Z + k * (ac.SCRAP_T + 0.004)
            r.box((SCRAP_H, ac.ANODE_W, ac.SCRAP_T), (sx - 0.1, 0, z + ac.SCRAP_T / 2), M['anode'])
            r.box((0.10, ac.ANODE_LUG_SPAN, ac.SCRAP_T), (sx + SCRAP_H / 2 - 0.05, 0, z + ac.SCRAP_T / 2), M['anode'])
    r.finish(ref)
    ac.floor_ref(ref, -2, 23, -5, 4.5)


def readme(col):
    rows = pb.pivot_table([col.name])
    return f"""# SM_AnodeScrapWasher - anode scrap washing and stacking machine

Spent anodes come out of the cells on the tankhouse crane with slimes on them. The line washes
them, tips them flat and builds stacks for the forklift, which takes them back to the anode furnace.
Wash water carries the slimes to a cone-bottom settling tank; its underflow is pumped toward the
anode slimes plant.

**Own design.** The research only gives "spray wash line and stacker" and the scrap fraction
(80-87 % of each anode is consumed, so 13-20 % comes back). No drawings were found.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Anodes move along +X.
- Footprint: x -0.5 to 21.9, y -4.4 to 3.6 (about 22.4 x 8.0 m).
- Infeed: crane drop zone on the receiving chains, x 0 to 6, lug seat z = {Z:.2f} m, chains at y = +-{CHAIN_Y}.
  Same seat height and lug span as SM_AnodePrepMachine.
- Outfeed: stacks of {STACK_N} flat scrap anodes on the roller conveyor, roller top z = {STACK_Z} m,
  forklift pickup at the end stop x = {OUT_X + 0.2:.1f}. Stack width {ac.ANODE_LUG_SPAN} m across the lugs.
- Slimes pipe stub to the slimes plant at (11.1, -4.7, 3.6), pointing -Y.

## Moving parts

| Part | Motion | Pivot |
|---|---|---|
| SW_Receive / SW_Wash _L/R_Chain, sprockets | Chain loops along +X, sprockets spin about Y | see table |
| SW_WalkingBeam | Up 0.05 m, +X 1.5 m, down, back | ({PICK - 0.4:.2f}, 0, 0.30) |
| SW_Tilter | Rotates about Y; Blender rotation Y = +90° lays the anode flat with the lugs toward +X and the back bars underneath | hinge {tuple(round(v, 2) for v in HINGE)} |
| SW_StackForks | Lifts the flat anode off the tilter, then lowers one anode thickness per anode; at the bottom the stack sits on the rollers | ({HINGE[0] + 0.48:.2f}, -1.15, {HINGE[2] - 0.03:.2f}) |
| SW_StackConv_Roller_NN | Spin about Y | roller axes |

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

{ac.UNREAL_NOTE}
## Dimensions

| Item | Value | Status |
|---|---|---|
| Scrap fraction | 13-20 % of the anode | Sourced (80-87 % consumed, BCcampus Aqueous Pathways) |
| Scrap anode proxy | {ac.ANODE_W} x {SCRAP_H:.2f} x {ac.SCRAP_T} m body, full lugs (~80 kg) | Estimated |
| Cell load | {LOAD} anodes | Inside the sourced 30-50 range |
| Stack of {STACK_N}, wash hood 4.6 m, settling tank Ø2.2 m | | Own design |

## Files

- SM_AnodeScrapWasher.blend / .fbx (REF scrap anodes, floor and figure not exported)
- Preview_Overview.png, Preview_Tilter.png
"""


VIEWS = [
    ("Preview_Overview.png", (-3, 13, 9), (11, 0, 0.0), 24),
    ("Preview_Tilter.png", (10.5, -5.0, 3.2), (14.2, 0, 1.0), 28, ("Guards", "Dressing", "SlimesTank")),
]

if __name__ == "__main__":
    ac.run(ASSET, NAME, build, readme, VIEWS)
