"""
build_cathode_stripping_machine.py - SM_CathodeStrippingMachine (permanent stainless cathodes).

Run:  blender -b --factory-startup --python Tools/Blender/AnodeCathodeMachines/build_cathode_stripping_machine.py

Sequence (Glencore IsaKidd semi-automatic machine): receive -> wash -> transfer ->
flex -> chisel -> stack -> discharge, with a reject line.
Here: crane load on the receiving chains -> wash hood -> walking beam -> flexing
rollers crack the deposit edge -> two knives wedge in from the top -> tilters lay
the two sheets flat -> pushers slide them onto stacking forks -> forks lower full
stacks onto a roller conveyor (to the bundling line) -> blanks go on to the
discharge chains for the crane, rejects to a rack on +Y.
Station layout and sizes are my own design; the patents give the sequence, not sizes.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import acm_common as ac  # noqa: E402
from acm_common import pb  # noqa: E402

ASSET, NAME = "CathodeStrippingMachine", "SM_CathodeStrippingMachine"

# ---------------------------------------------------------------------------
# Layout parameters (metres). Own design unless stated.
# ---------------------------------------------------------------------------
Z = 1.80                      # hanger-bar seat height (raised so the sheets tip flat at 0.70 m)
CHAIN_Y = 0.62                # chains under the hanger-bar ends
WB_Y = 0.57                   # walking-beam bars under the hanger bar, outside the blade edge strips
RECEIVE = (0.0, 7.0)          # receiving chains (crane drop zone)
WASH = (7.4, 11.4)            # wash chains inside the hood
STATIONS = {'pick': 11.9, 'flex': 13.9, 'strip': 15.9, 'exit': 17.9}   # 2.0 m walking-beam step
DISCHARGE = (17.6, 24.5)      # blank discharge chains, crane pickup zone at the end
LOAD = 46                     # cathodes per cell load (one more than the anodes)
STACK_Y = -2.30               # copper stack conveyor centre line
STACK_Z = 0.45                # roller top of the stack conveyor
STACK_N = 30                  # sheets per stack, ~2.0 t (one bundle)
TILT_Z = 0.70                 # tilter hinge height (sheets lie flat here)
BLADE_BOT = Z - ac.BLADE_H
DEP_TOP = Z - ac.DEPOSIT_TOP_GAP
PICK_X0 = DISCHARGE[1] - 0.35 - (LOAD - 1) * ac.PITCH


def build(col, ref, M):
    sx = STATIONS['strip']

    # --- chain conveyors ---
    ac.chain_conveyor("CS_Receive", RECEIVE[0], RECEIVE[1], CHAIN_Y, Z, col, M)
    ac.chain_conveyor("CS_Wash", WASH[0], WASH[1], CHAIN_Y, Z, col, M)
    ac.chain_conveyor("CS_Discharge", DISCHARGE[0], DISCHARGE[1], CHAIN_Y, Z, col, M)

    # --- wash hood over the wash chains ---
    ac.wash_hood("CS_WashHood", WASH[0] + 0.2, WASH[1] - 0.2, Z, BLADE_BOT, col, M)

    # --- station frame between wash and discharge (left open around the strip station) ---
    st = pb.Part("CS_StationFrame", pivot=(WASH[1], 0, 0))
    x0, x1 = WASH[1] + 0.1, DISCHARGE[0] - 0.1
    for s in (-1, 1):
        st.box_mm((x0, s * CHAIN_Y - 0.04, Z - 0.08), (x1, s * CHAIN_Y + 0.04, Z), M['grey'])
        st.box_mm((x0, s * CHAIN_Y - 0.04, Z - 0.30), (x1, s * 1.00 + 0.08, Z - 0.08), M['frame'])
        for x in (x0 + 0.1, 12.9, 14.85, 16.95, x1 - 0.1):
            st.box_mm((x - 0.08, s * 1.0 - 0.08, 0), (x + 0.08, s * 1.0 + 0.08, Z - 0.30), M['frame'])
    st.finish(col)

    # --- walking beam (2.0 m step) ---
    wb_x0, wb_x1 = STATIONS['pick'] - 0.4, STATIONS['exit'] + 0.4
    tie_z = 0.20
    wb = pb.Part("CS_WalkingBeam", pivot=(wb_x0, 0, tie_z))
    for s in (-1, 1):
        wb.box_mm((wb_x0, s * WB_Y - 0.015, Z - 0.16), (wb_x1, s * WB_Y + 0.015, Z - 0.04), M['grey'])
        for x in STATIONS.values():
            wb.box((0.08, 0.03, 0.03), (x, s * WB_Y, Z - 0.025), M['steel'])
        for x in (wb_x0, wb_x1):
            wb.box_mm((x - 0.05, s * WB_Y - 0.02, tie_z), (x + 0.05, s * WB_Y + 0.02, Z - 0.16), M['grey'])
    for x in (wb_x0, wb_x1):
        wb.box_mm((x - 0.08, -WB_Y - 0.02, tie_z - 0.1), (x + 0.08, WB_Y + 0.02, tie_z), M['frame'])
    wb.finish(col)
    ac.hyd_cylinder("CS_WalkingBeam_TravelCyl", (wb_x0 - 2.1, 0, 0.12), (wb_x0 - 0.08, 0, 0.12), col, M, r=0.05)

    # --- flex station: hanger-bar clamp + flexing rollers on both faces ---
    fx = STATIONS['flex']
    fr = pb.Part("CS_FlexFrame", pivot=(fx, 0, 0))
    for dx in (-0.65, 0.65):
        ac.portal(fr, fx + dx, 1.05, Z + 0.9, M, depth=0.25, beam=0.25)
    for s in (-1, 1):
        fr.box_mm((fx - 0.78, s * 1.05 - 0.12, Z + 0.9), (fx + 0.78, s * 1.05 + 0.12, Z + 1.15), M['frame'])
    fr.finish(col)
    clamp = pb.Part("CS_FlexClamp", pivot=(fx, 0, Z + 0.25))
    clamp.box((0.12, ac.HBAR_L - 0.1, 0.08), (fx, 0, Z + 0.10), M['grey'])
    clamp.finish(col)
    ac.hyd_cylinder("CS_FlexClampCyl", (fx, 0, Z + 0.9), (fx, 0, Z + 0.14), col, M, r=0.07)
    fz = BLADE_BOT + 0.45      # flex line below the deposit top
    for nm, sgn in (("Up", -1), ("Down", 1)):
        rc = pb.Part(f"CS_FlexRoller_{nm}", pivot=(fx + sgn * 0.12, 0, fz))
        rc.cyl(0.07, 0.92, (fx + sgn * 0.12, 0, fz), M['grey'], rot=(90, 0, 0), seg=16)
        for s in (-1, 1):
            rc.box((0.20, 0.05, 0.16), (fx + sgn * 0.18, s * 0.49, fz), M['frame'])
        rc.finish(col)
        ac.hyd_cylinder(f"CS_FlexCyl_{nm}", (fx + sgn * 0.62, 0.0, fz), (fx + sgn * 0.27, 0.0, fz), col, M, r=0.08)

    # --- strip station: portal with two knife arms hinged above the plate ---
    sf = pb.Part("CS_StripFrame", pivot=(sx, 0, 0))
    for dx in (-1.15, 1.15):
        for s in (-1, 1):
            sf.box_mm((sx + dx - 0.12, s * 1.15 - 0.12, 0), (sx + dx + 0.12, s * 1.15 + 0.12, Z + 1.1), M['frame'])
    for s in (-1, 1):
        sf.box_mm((sx - 1.27, s * 1.15 - 0.12, Z + 1.1), (sx + 1.27, s * 1.15 + 0.12, Z + 1.35), M['frame'])
    for dx in (-0.75, 0.75):
        sf.box_mm((sx + dx - 0.12, -1.27, Z + 1.1), (sx + dx + 0.12, 1.27, Z + 1.35), M['frame'])
    sf.finish(col)
    for nm, sgn in (("Up", -1), ("Down", 1)):
        hinge = (sx + sgn * 0.75, 0, Z + 0.95)
        tip = (sx + sgn * 0.02, 0, DEP_TOP + 0.02)
        kn = pb.Part(f"CS_StripKnife_{nm}", pivot=hinge)
        kn.cyl(0.06, 1.0, hinge, M['grey'], rot=(90, 0, 0), seg=12)
        for s in (-1, 1):
            kn.beam_between((hinge[0], s * 0.40, hinge[2]), (tip[0] + sgn * 0.06, s * 0.40, tip[2] + 0.08), 0.08, 0.10, M['frame'])
        kn.box((0.12, 0.90, 0.025), (tip[0] + sgn * 0.06, 0, tip[2] + 0.02), M['yellow'], rot=(0, -sgn * 20, 0))
        kn.finish(col)
        ac.hyd_cylinder(f"CS_KnifeCyl_{nm}", (sx + sgn * 1.1, 0.7, Z + 1.05),
                        (sx + sgn * 0.42, 0.42, Z + 0.25), col, M, r=0.06)

    # --- sheet tilters: paddles hinged at TILT_Z, swing 90 deg outward to lay sheets flat ---
    for nm, sgn in (("Up", -1), ("Down", 1)):
        hx = sx + sgn * 0.06
        tl = pb.Part(f"CS_SheetTilter_{nm}", pivot=(hx, 0, TILT_Z))
        tl.cyl(0.04, 1.1, (hx, 0, TILT_Z), M['grey'], rot=(90, 0, 0), seg=10)
        for y in (-0.35, 0.0, 0.35):
            tl.box_mm((hx + sgn * 0.0, y - 0.03, TILT_Z), (hx + sgn * 0.05, y + 0.03, TILT_Z + 0.95), M['frame'])
        tl.box_mm((hx - 0.02, -0.45, TILT_Z), (hx + 0.02, 0.45, TILT_Z + 0.06), M['frame'])
        tl.finish(col)
        ac.hyd_cylinder(f"CS_TilterCyl_{nm}", (hx + sgn * 0.6, 0.55, 0.15), (hx + sgn * 0.02, 0.55, TILT_Z + 0.35), col, M, r=0.05)

    # --- stack conveyor (to bundling), stacking forks, sheet pushers ---
    xs = ac.roller_conveyor("CS_StackConv", sx - 1.3, 24.5, STACK_Y, STACK_Z, 1.10, col, M, pitch=0.30)
    for nm, sgn in (("Up", -1), ("Down", 1)):
        cx = sx + sgn * 0.56          # flat sheet centre after tilting
        fk = pb.Part(f"CS_StackForks_{nm}", pivot=(cx, STACK_Y - 0.70, TILT_Z))
        gaps = [(a + b) / 2 for a, b in zip(xs, xs[1:]) if abs((a + b) / 2 - cx) < 0.5]
        for gx in gaps:               # tines along Y between the rollers
            fk.box_mm((gx - 0.025, STACK_Y - 0.55, TILT_Z - 0.04), (gx + 0.025, STACK_Y + 0.55, TILT_Z), M['grey'])
        fk.box_mm((cx - 0.55, STACK_Y - 0.75, TILT_Z - 0.15), (cx + 0.55, STACK_Y - 0.55, TILT_Z + 0.05), M['frame'])
        fk.finish(col)
        # pusher: bar behind the flat sheet on a rodless carriage, travels -Y onto the forks
        ps = pb.Part(f"CS_SheetPusher_{nm}", pivot=(cx, 0.62, TILT_Z + 0.08))
        ps.box((0.9, 0.06, 0.10), (cx, 0.58, TILT_Z + 0.10), M['yellow'])
        ps.box((0.2, 0.15, 0.25), (cx, 0.68, TILT_Z + 0.20), M['frame'])
        ps.finish(col)
    sk = pb.Part("CS_StackerFrame", pivot=(sx, STACK_Y, 0))
    for nm, sgn in (("Up", -1), ("Down", 1)):
        cx = sx + sgn * 0.56
        sk.box_mm((cx - 0.12, STACK_Y - 1.0, 0), (cx + 0.12, STACK_Y - 0.8, TILT_Z + 0.6), M['frame'])   # fork mast
        sk.box_mm((cx - 0.6, 0.72, TILT_Z + 0.25), (cx + 0.6, 0.82, TILT_Z + 0.35), M['frame'])           # pusher beam
        for x in (cx - 0.55, cx + 0.55):
            sk.box_mm((x - 0.05, 0.72, 0), (x + 0.05, 0.82, TILT_Z + 0.25), M['frame'])
    sk.finish(col)

    # --- reject hoist to a rack on +Y at the exit station ---
    ex = STATIONS['exit']
    rr = pb.Part("CS_RejectRack", pivot=(ex, 2.6, 0))
    rr.box_mm((ex - 0.12, -1.0, Z + 1.4), (ex + 0.12, 3.5, Z + 1.7), M['frame'])
    for y in (-1.0, 3.4):
        rr.box_mm((ex - 0.12, y - 0.12, 0), (ex + 0.12, y + 0.12, Z + 1.4), M['frame'])
    for s in (-1, 1):
        rr.box_mm((ex - 0.6, 2.6 + s * CHAIN_Y - 0.04, Z - 0.10), (ex + 0.6, 2.6 + s * CHAIN_Y + 0.04, Z), M['grey'])
        for dx in (-0.55, 0.55):
            rr.box_mm((ex + dx - 0.05, 2.6 + s * CHAIN_Y - 0.05, 0), (ex + dx + 0.05, 2.6 + s * CHAIN_Y + 0.05, Z - 0.10), M['yellow'])
    rr.finish(col)
    tr = pb.Part("CS_RejectTrolley", pivot=(ex, 0, Z + 1.4))
    tr.box((0.5, 0.4, 0.25), (ex, 0, Z + 1.27), M['yellow'])
    tr.finish(col)
    tg = pb.Part("CS_RejectTongs", pivot=(ex, 0, Z + 0.7))
    tg.cyl_between((ex, 0, Z + 0.7), (ex, 0, Z + 1.15), 0.03, M['steel'], seg=8)
    tg.box((0.2, 1.50, 0.10), (ex, 0, Z + 0.65), M['yellow'])
    for s in (-1, 1):
        tg.box((0.08, 0.05, 0.6), (ex, s * 0.73, Z + 0.33), M['yellow'])
        tg.box((0.08, 0.06, 0.04), (ex, s * 0.70, Z + 0.05), M['yellow'])
    tg.finish(col)

    # --- pickup guides and end stop on the discharge chains ---
    cg = pb.Part("CS_PickupGuides", pivot=(PICK_X0, 0, 0))
    for s in (-1, 1):
        cg.box_mm((PICK_X0 - 0.1, s * 0.74 - 0.02, Z - 0.02), (DISCHARGE[1], s * 0.74 + 0.02, Z + 0.14), M['grey'])
        for i in range(LOAD):
            cg.box((0.012, 0.04, 0.10), (PICK_X0 + i * ac.PITCH + 0.05, s * 0.74, Z + 0.15), M['steel'])
    cg.box_mm((DISCHARGE[1] + 0.25, -0.9, 0), (DISCHARGE[1] + 0.45, 0.9, Z + 0.25), M['yellow'])
    cg.finish(col)

    # --- guards, dressing ---
    gd = pb.Part("CS_Guards", pivot=(0, 0, 0))
    ac.guard_fence(gd, (WASH[1], 1.45, 0), (DISCHARGE[0] - 0.2, 1.45, 0), M)
    ac.guard_fence(gd, (WASH[1], -1.45, 0), (sx - 1.45, -1.45, 0), M)
    ac.guard_fence(gd, (sx - 1.45, -3.1, 0), (sx + 1.45, -3.1, 0), M, h=1.2)
    gd.finish(col)
    dr = pb.Part("CS_Dressing", pivot=(0, 0, 0))
    ac.hpu(dr, (13.5, 3.2, 0), M)
    ac.cabinet(dr, (9.4, 2.4, 0), M, size=(2.4, 0.6, 2.1))
    dr.box_mm((19.5, -5.2, 0), (22.5, -3.4, 2.6), M['cabinet'])        # control pulpit
    dr.box_mm((19.7, -3.41, 1.2), (22.3, -3.39, 2.3), M['steel'])
    dr.box_mm((19.4, -5.3, 2.6), (22.6, -3.3, 2.75), M['frame'])
    ac.platform(dr, 7.6, 11.2, 1.3, 2.0, 1.5, M, ladder_at=(7.9, 1.65, 0))
    dr.finish(col)

    # --- REF: loads, plates in process, flat sheets, stacks, blanks in pickup ---
    r = pb.Part("REF_Cathodes", pivot=(0, 0, 0))
    for i in range(LOAD):
        ac.add_cathode(r, 0.4 + i * ac.PITCH, Z, M)
    for i in range(10):
        ac.add_cathode(r, WASH[0] + 0.5 + i * 0.33, Z, M)
    ac.add_cathode(r, STATIONS['pick'], Z, M)
    ac.add_cathode(r, STATIONS['flex'], Z, M)
    ac.add_cathode(r, sx, Z, M, deposit=False)
    for sgn in (-1, 1):
        ac.add_sheet(r, sx + sgn * 0.56, TILT_Z + 0.05, M, upright=False)                 # just tilted
        for k in range(STACK_N):                                                           # stack on the roller
            ac.add_sheet(r, sx + sgn * 0.56 + 3.0, STACK_Z + k * ac.DEPOSIT_T, M, upright=False, y=STACK_Y)
    for i in range(LOAD):
        ac.add_cathode(r, PICK_X0 + i * ac.PITCH, Z, M, deposit=False)
    r.finish(ref)
    ac.floor_ref(ref, -2, 26, -6.5, 5)


def readme(col):
    rows = pb.pivot_table([col.name])
    return f"""# SM_CathodeStrippingMachine - stripping machine for permanent stainless cathodes

Takes a crane load of harvested IsaKidd-type cathodes, washes them, flexes each plate to crack the
deposit edge, wedges two knives in from the top, lays the two copper sheets flat, stacks them and
sends the stacks to the bundling line. Clean blanks go to the discharge chains for the crane.

**Own design.** The sequence (receive, wash, transfer, flex, chisel, stack, discharge, reject)
follows Glencore's IsaKidd semi-automatic machine. US20070144894A1, WO2017144740A1 and
EP0482258A1 show stripping machines, but none gives dimensions. All sizes here are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Plates move along +X.
- Footprint: x -0.5 to 25.0, y -5.3 to 3.6 (about 25.5 x 8.9 m).
- Infeed: crane drop zone on the receiving chains, x 0 to 7, hanger-bar seat z = {Z:.2f} m,
  chains at y = +-{CHAIN_Y:.2f}. The seat is higher than the anode machine ({ac.HANG_Z:.2f} m) so the
  sheets can tip flat at z = {TILT_Z:.2f} m above the stacking forks.
- Blank outfeed: crane pickup zone on the discharge chains, x {PICK_X0:.2f} to {DISCHARGE[1] - 0.25:.2f},
  {LOAD} blanks at {ac.PITCH * 1000:.0f} mm pitch, seat z = {Z:.2f} m.
- Copper outfeed: stack roller conveyor along +X at y = {STACK_Y:.2f}, roller top z = {STACK_Z:.2f} m,
  open end at x = 24.5. Feeds SM_CathodeBundlingLine (its infeed is at the same height).
- Tankhouse link: the crane carries a cell load between this machine and the tankhouse transfer stand CathodeOut at (-12, 8) for harvested cathodes in, and CathodeBlankIn at (-22, 8) for blanks out (tankhouse coordinates, seat z 1.20, electrodes stacked along Y, so this machine's X runs along the tankhouse Y there). See Meshes/Tankhouse/README.md.
- Reject rack (hanger-bar rails, seat z = {Z:.2f}) on +Y at ({STATIONS['exit']:.1f}, 2.6).

## Stations and moving parts

| Station | x (m) | Moving parts |
|---|---|---|
| Receive chains | 0 to 7 | CS_Receive_L/R_Chain, sprockets |
| Wash | 7.4 to 11.4 | CS_Wash_L/R_Chain (hood is static) |
| Walking beam | {STATIONS['pick']} to {STATIONS['exit']} | CS_WalkingBeam: up 0.05 m, +X 2.0 m, down, back |
| Flex | {STATIONS['flex']} | CS_FlexClamp down 0.15 m onto the hanger bar; CS_FlexRoller_Up/Down slide 0.1 m along X against the blade, alternately |
| Strip | {STATIONS['strip']} | CS_StripKnife_Up/Down rotate about Y at their hinges (drawn closed at the deposit edge; open = about 25° outward); CS_SheetTilter_Up/Down rotate 90° outward about Y to lay the sheets flat |
| Stack | {STATIONS['strip']} ± 0.56 | CS_SheetPusher_Up/Down travel -Y {0.62 - STACK_Y:.2f} m; CS_StackForks_Up/Down lower {TILT_Z - STACK_Z + 0.05:.2f} m in steps of one sheet and leave the stack on the rollers |
| Stack conveyor | {STATIONS['strip'] - 1.3:.1f} to 24.5 | CS_StackConv_Roller_NN spin about Y |
| Exit / reject | {STATIONS['exit']} | CS_RejectTongs lift, CS_RejectTrolley travels +2.6 m along Y |
| Discharge | {DISCHARGE[0]} to {DISCHARGE[1]} | CS_Discharge_L/R_Chain, sprockets |

Cylinders: _Barrel pivot at the base end, _Rod pivot at the rod end, local +X along the axis.

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

{ac.UNREAL_NOTE}
## Dimensions

| Item | Value | Status |
|---|---|---|
| Blade | {ac.BLADE_W} x {ac.BLADE_H} m below the bar, {ac.BLADE_T * 1000:.2f} mm 316L | Thickness sourced (patents); size matches SM_PermanentCathode (tankhouse thread) |
| Hanger bar | {ac.HBAR_L} m, 25 x 35 mm, copper plated | Construction sourced (patents), size matches SM_PermanentCathode |
| Copper sheet | {ac.DEPOSIT_W} x {ac.DEPOSIT_H} m x {ac.DEPOSIT_T * 1000:.0f} mm, ~67 kg, top edge {ac.DEPOSIT_TOP_GAP} m below the bar | Matches SM_PermanentCathode (estimated there) |
| Throughput | ~250 plates/h (early machines); ~500/h needs two strip stations; >600/h reported | Sourced: Wikipedia IsaKidd, Glencore patent background, CIM paper |
| Cell load | {LOAD} cathodes | Estimated (anodes + 1, sourced rule) |
| Stack of {STACK_N} sheets, ~2.0 t | One stack = one bundle | Sourced bundle mass 1-4 t, ~2,000 kg at one producer; sheet count estimated |
| Walking-beam step 2.0 m, seat height {Z} m | | Own design |

Sources: Glencore IsaKidd electrode handling equipment
(https://www.glencoretechnology.com/en/technologies/isakidd/electrode-handling-equipment);
US20070144894A1, WO2017144740A1, EP0482258A1, US7306706B2 (patents.google.com).

## Files

- SM_CathodeStrippingMachine.blend / .fbx (REF cathodes, sheets, floor and figure not exported)
- Preview_Overview.png, Preview_Strip.png, Preview_Wash.png
"""


VIEWS = [
    ("Preview_Overview.png", (-2, -13, 9), (12.5, -0.5, 0.0), 24),
    ("Preview_Strip.png", (12.4, -6.0, 3.6), (15.6, -0.8, 1.2), 28, ("Guards", "Dressing")),
    ("Preview_Wash.png", (4.0, 5.5, 4.5), (9.5, 0, 1.4), 30),
]

if __name__ == "__main__":
    ac.run(ASSET, NAME, build, readme, VIEWS)
