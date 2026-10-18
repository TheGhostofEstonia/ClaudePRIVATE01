"""
build_anode_prep_machine.py - SM_AnodePrepMachine (anode preparation machine).

Run:  blender -b --factory-startup --python Tools/Blender/AnodeCathodeMachines/build_anode_prep_machine.py

Sequence (after US4903519, US5799529, US8227345 and Metso's brochure):
forklift load of anodes onto the infeed chains -> walking beam singles them out ->
weigh -> flatten press (platens squeeze the faces) -> lug straightening press ->
lug underside milling -> inspection / reject hoist -> spacing chain sets the anodes
at cell pitch -> crane pickup zone (one cell load).
Station layout and sizes are my own design from the patent sequence; no drawings with
dimensions were found.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import acm_common as ac  # noqa: E402
from acm_common import pb  # noqa: E402

ASSET, NAME = "AnodePrepMachine", "SM_AnodePrepMachine"

# ---------------------------------------------------------------------------
# Layout parameters (metres). Estimated / own design unless stated.
# ---------------------------------------------------------------------------
Z = ac.HANG_Z                 # lug seat height on chains, rails and rack
CHAIN_Y = 0.56                # chain strands under the lugs
LUG_Y = 0.60                  # lug contact face centre (rails, lug press, mills)
WB_Y = 0.525                  # walking-beam bars, under the inner lug area
INFEED = (0.0, 7.0)           # infeed chain conveyor
STATIONS = {                  # walking-beam stations, 1.5 m step
    'pick': 7.5, 'weigh': 9.0, 'press': 10.5, 'lugpress': 12.0, 'mill': 13.5, 'reject': 15.0}
SPACER = (16.0, 28.5)         # spacing chain, pickup zone at its end
LOAD = 45                     # anodes per cell load (30-50 sourced range)
PICK_X0 = SPACER[1] - 0.35 - (LOAD - 1) * ac.PITCH


def build(col, ref, M):
    """All exported parts go to col, preview proxies to ref."""
    # --- chain conveyors (strands, sprockets, frames) ---
    ac.chain_conveyor("AP_Infeed", INFEED[0], INFEED[1], CHAIN_Y, Z, col, M)
    ac.chain_conveyor("AP_Spacer", SPACER[0], SPACER[1], CHAIN_Y, Z, col, M)

    # --- station frame: lug rails on posts between the conveyors (open so the anodes show) ---
    st = pb.Part("AP_StationFrame", pivot=(INFEED[1], 0, 0))
    x0, x1 = INFEED[1] + 0.1, SPACER[0] - 0.1
    for s in (-1, 1):
        st.box_mm((x0, s * LUG_Y - 0.04, Z - 0.08), (x1, s * LUG_Y + 0.04, Z), M['grey'])        # lug rail
        st.box_mm((x0, s * LUG_Y - 0.04, Z - 0.22), (x1, s * 0.80 + 0.08, Z - 0.08), M['frame'])  # rail girder
        n = int((x1 - x0) / 1.5) + 1
        for i in range(n):                    # posts between stations (x = station - 0.75)
            x = x0 + 0.05 + (x1 - x0 - 0.1) * i / (n - 1)
            st.box_mm((x - 0.08, s * 0.80 - 0.08, 0), (x + 0.08, s * 0.80 + 0.08, Z - 0.22), M['frame'])
            st.box((0.35, 0.35, 0.02), (x, s * 0.80, 0.01), M['steel'])
    # weigh station: rail section on four load cells, indicator on a post
    wx = STATIONS['weigh']
    for s in (-1, 1):
        for dx in (-0.25, 0.25):
            st.cyl(0.05, 0.06, (wx + dx, s * LUG_Y, Z - 0.11), M['grey'], seg=12)
    st.box((0.08, 0.08, 2.0), (wx, -1.4, 1.0), M['frame'])
    st.box((0.5, 0.12, 0.35), (wx, -1.4, 2.1), M['cabinet'])
    st.box((0.38, 0.01, 0.12), (wx, -1.465, 2.12), M['green'])
    st.finish(col)

    # --- walking beam: two bars lift the anode under the inner lug area and step it 1.5 m.
    #     Bars drop at both ends to cross ties below the anode bottoms. ---
    wb_x0, wb_x1 = STATIONS['pick'] - 0.5, STATIONS['reject'] + 0.6
    tie_z = 0.40
    wb = pb.Part("AP_WalkingBeam", pivot=(wb_x0, 0, tie_z))
    for s in (-1, 1):
        wb.box_mm((wb_x0, s * WB_Y - 0.02, Z - 0.16), (wb_x1, s * WB_Y + 0.02, Z - 0.04), M['grey'])
        for x in STATIONS.values():           # saddle blocks under each lug position
            wb.box((0.10, 0.04, 0.03), (x, s * WB_Y, Z - 0.025), M['steel'])
        for x in (wb_x0, wb_x1):
            wb.box_mm((x - 0.05, s * WB_Y - 0.02, tie_z), (x + 0.05, s * WB_Y + 0.02, Z - 0.16), M['grey'])
    for x in (wb_x0, wb_x1):
        wb.box_mm((x - 0.08, -WB_Y - 0.02, tie_z - 0.12), (x + 0.08, WB_Y + 0.02, tie_z), M['frame'])
    wb.finish(col)
    for i, x in enumerate((wb_x0, wb_x1)):
        ac.hyd_cylinder(f"AP_WalkingBeam_LiftCyl_{i}", (x, 0, 0.0), (x, 0, tie_z - 0.12), col, M, r=0.07)
    ac.hyd_cylinder("AP_WalkingBeam_TravelCyl", (wb_x0 - 1.4, 0, 0.18), (wb_x0 - 0.08, 0, 0.18), col, M, r=0.05)

    # --- flatten press: heavy portal, two platens squeezing along X ---
    px = STATIONS['press']
    pr = pb.Part("AP_PressFrame", pivot=(px, 0, 0))
    for dx in (-1.0, 1.0):
        for s in (-1, 1):
            pr.box_mm((px + dx - 0.15, s * 1.05 - 0.15, 0), (px + dx + 0.15, s * 1.05 + 0.15, 2.9), M['frame'])
        pr.box_mm((px + dx - 0.15, -1.2, 2.9), (px + dx + 0.15, 1.2, 3.3), M['frame'])
    for s in (-1, 1):
        pr.box_mm((px - 1.15, s * 1.05 - 0.15, 2.9), (px + 1.15, s * 1.05 + 0.15, 3.3), M['frame'])
        pr.box_mm((px - 1.15, s * 1.05 - 0.15, 0.0), (px + 1.15, s * 1.05 + 0.15, 0.3), M['frame'])
    pr.finish(col)
    zc = Z + ac.ANODE_LUG_H - ac.ANODE_H / 2
    for nm, sgn in (("Up", -1), ("Down", 1)):
        pl = pb.Part(f"AP_PressPlaten_{nm}", pivot=(px + sgn * 0.35, 0, zc))
        pl.box((0.08, 0.92, 0.90), (px + sgn * 0.35, 0, zc), M['grey'])
        pl.box((0.12, 0.6, 0.6), (px + sgn * 0.45, 0, zc), M['frame'])
        pl.finish(col)
        ac.hyd_cylinder(f"AP_PressCyl_{nm}", (px + sgn * 0.98, 0, zc), (px + sgn * 0.51, 0, zc), col, M, r=0.16)

    # --- lug straightening press: a C-frame press over the outer part of each lug ---
    lx = STATIONS['lugpress']
    lp = pb.Part("AP_LugPressFrame", pivot=(lx, 0, 0))
    for s in (-1, 1):
        lp.box_mm((lx - 0.35, s * LUG_Y - 0.05, 0), (lx + 0.35, s * LUG_Y + 0.05, Z - 0.10), M['frame'])  # anvil column
        lp.box_mm((lx - 0.35, s * 1.0 - 0.12, 0), (lx + 0.35, s * 1.0 + 0.12, Z + 1.05), M['frame'])      # C-frame back
        lp.box_mm((lx - 0.35, min(s * 0.50, s * 1.12), Z + 0.85), (lx + 0.35, max(s * 0.50, s * 1.12), Z + 1.05), M['frame'])
    lp.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        hd = pb.Part(f"AP_LugPressHead_{side}", pivot=(lx, s * LUG_Y, Z + 0.25))
        hd.box((0.30, 0.14, 0.10), (lx, s * LUG_Y, Z + 0.20), M['grey'])
        hd.finish(col)
        ac.hyd_cylinder(f"AP_LugPressCyl_{side}", (lx, s * LUG_Y, Z + 0.85), (lx, s * LUG_Y, Z + 0.25), col, M, r=0.09)

    # --- lug milling: a face mill under the contact face of each lug, spindle vertical ---
    mx = STATIONS['mill']
    mf = pb.Part("AP_MillFrame", pivot=(mx, 0, 0))
    for s in (-1, 1):
        y = s * LUG_Y
        mf.box_mm((mx - 0.45, y - 0.10, 0), (mx + 0.45, y + 0.10, 0.60), M['frame'])                 # base under the lug
        mf.box_mm((mx - 0.45, min(y, s * 1.0), 0), (mx + 0.45, max(y, s * 1.0), 0.60), M['frame'])  # base out to the column
        mf.box_mm((mx - 0.20, y - 0.08, 0.60), (mx + 0.20, y + 0.08, 0.80), M['steel'])             # slide
        mf.box_mm((mx - 0.35, s * 1.0 - 0.10, 0), (mx + 0.35, s * 1.0 + 0.10, Z + 0.55), M['frame'])  # clamp column
        mf.box_mm((mx - 0.35, min(s * 0.50, s * 1.1), Z + 0.45), (mx + 0.35, max(s * 0.50, s * 1.1), Z + 0.55), M['frame'])
        mf.box((0.2, 0.12, 0.30), (mx, y, Z + 0.28), M['grey'])                                     # top clamp pad
    mf.box((0.8, 0.7, 0.5), (mx, -1.9, 0.25), M['steel'])        # chip bin
    mf.finish(col)
    for side, s in (("L", 1), ("R", -1)):
        y = s * LUG_Y
        # head carriage moves up on the slide; cutter spins about Z
        car = pb.Part(f"AP_MillHead_{side}", pivot=(mx, y, 0.80))
        car.box((0.36, 0.16, 0.50), (mx, y, 1.05), M['frame'])
        car.cyl(0.14, 0.40, (mx, y + s * 0.28, 1.05), M['frame'], rot=(90, 0, 0), seg=16)   # spindle motor
        car.finish(col)
        cut = pb.Part(f"AP_MillCutter_{side}", pivot=(mx, y, Z - 0.05))
        cut.cyl(0.04, 0.30, (mx, y, Z - 0.25), M['grey'], seg=12)
        cut.cyl(0.05, 0.05, (mx, y, Z - 0.075), M['grey'], seg=20)
        for i in range(6):
            a = i * math.pi / 3
            cut.box((0.02, 0.015, 0.03), (mx + 0.045 * math.cos(a), y + 0.045 * math.sin(a), Z - 0.06), M['yellow'])
        cut.finish(col)

    # --- inspection arch with cameras, reject hoist on a runway to a reject rack on -Y ---
    rx = STATIONS['reject']
    ry = -2.6                                 # reject rack centre line
    rf = pb.Part("AP_InspectReject", pivot=(rx, 0, 0))
    ac.portal(rf, rx - 0.55, 1.15, 2.9, M, depth=0.2, beam=0.2)
    for s in (-1, 1):
        rf.box((0.25, 0.18, 0.18), (rx - 0.55, s * 0.95, 2.6), M['cabinet'])
        rf.cyl(0.05, 0.08, (rx - 0.40, s * 0.95, 2.6), M['steel'], rot=(0, 90, 0), seg=12)
    # runway beam along Y at 3.4 m, posts at both ends
    rf.box_mm((rx - 0.12, ry - 0.9, 3.40), (rx + 0.12, 1.0, 3.70), M['frame'])
    for y in (ry - 0.8, 0.9):
        rf.box_mm((rx - 0.12, y - 0.12, 0), (rx + 0.12, y + 0.12, 3.40), M['frame'])
    # reject rack: lug rails at seat height, holds ~8 anodes
    for s in (-1, 1):
        rf.box_mm((rx - 0.5, ry + s * LUG_Y - 0.04, Z - 0.10), (rx + 0.5, ry + s * LUG_Y + 0.04, Z), M['grey'])
        for dx in (-0.45, 0.45):
            rf.box_mm((rx + dx - 0.05, ry + s * LUG_Y - 0.05, 0), (rx + dx + 0.05, ry + s * LUG_Y + 0.05, Z - 0.10), M['yellow'])
    rf.finish(col)
    tr = pb.Part("AP_RejectTrolley", pivot=(rx, 0, 3.40))
    tr.box((0.5, 0.4, 0.25), (rx, 0, 3.27), M['yellow'])
    tr.box((0.3, 0.3, 0.35), (rx, 0.3, 3.2), M['frame'])           # hoist motor
    tr.finish(col)
    tg = pb.Part("AP_RejectTongs", pivot=(rx, 0, 2.6))
    tg.cyl_between((rx, 0, 2.6), (rx, 0, 3.15), 0.03, M['steel'], seg=8)
    tg.box((0.2, 1.40, 0.10), (rx, 0, 2.55), M['yellow'])
    for s in (-1, 1):
        tg.box((0.08, 0.05, 0.85), (rx, s * 0.68, 2.1), M['yellow'])
        tg.box((0.08, 0.06, 0.05), (rx, s * 0.64, Z + 0.05), M['yellow'])
    tg.finish(col)

    # --- spacer: comb guides over the pickup zone, end stop ---
    cg = pb.Part("AP_PickupGuides", pivot=(PICK_X0, 0, 0))
    for s in (-1, 1):
        cg.box_mm((PICK_X0 - 0.1, s * 0.70 - 0.02, Z - 0.02), (SPACER[1], s * 0.70 + 0.02, Z + 0.14), M['grey'])
        for i in range(LOAD):
            cg.box((0.012, 0.04, 0.10), (PICK_X0 + i * ac.PITCH + 0.05, s * 0.70, Z + 0.15), M['steel'])
    cg.box_mm((SPACER[1] + 0.25, -0.9, 0), (SPACER[1] + 0.45, 0.9, Z + 0.25), M['yellow'])
    cg.finish(col)
    dog = pb.Part("AP_SpacerDogs", pivot=(SPACER[0], 0, Z))
    for s in (-1, 1):
        dog.box((0.03, 0.05, 0.06), (SPACER[0] + 0.3, s * CHAIN_Y, Z + 0.03), M['yellow'])
    dog.finish(col)

    # --- dressing: guards, HPU, control pulpit, operator platform ---
    gd = pb.Part("AP_Guards", pivot=(0, 0, 0))
    for y in (-1.6, 1.6):
        ac.guard_fence(gd, (INFEED[1] - 0.2, y, 0), (SPACER[0] + 0.2, y, 0), M)
    gd.finish(col)
    dr = pb.Part("AP_Dressing", pivot=(0, 0, 0))
    ac.hpu(dr, (10.5, 3.0, 0), M)
    ac.cabinet(dr, (13.0, 2.6, 0), M, size=(2.4, 0.6, 2.1))
    # control pulpit with window facing the press and mill
    dr.box_mm((11.0, -4.6, 0), (14.0, -2.8, 2.6), M['cabinet'])
    dr.box_mm((11.2, -2.81, 1.2), (13.8, -2.79, 2.3), M['steel'])
    dr.box_mm((10.9, -4.7, 2.6), (14.1, -2.7, 2.75), M['frame'])
    dr.cyl(0.05, 0.4, (INFEED[1] - 0.2, -1.6, 2.2), M['red'], seg=10)
    ac.platform(dr, 17.0, 27.0, 1.0, 1.9, 1.2, M, ladder_at=(17.3, 1.45, 0))
    dr.finish(col)

    # --- REF: forklift load on the infeed, one anode at each station, cell load in pickup ---
    r = pb.Part("REF_Anodes", pivot=(0, 0, 0))
    for i in range(20):
        ac.add_anode(r, 0.6 + i * 0.06, Z, M)
    for x in STATIONS.values():
        ac.add_anode(r, x, Z, M)
    for i in range(LOAD):
        ac.add_anode(r, PICK_X0 + i * ac.PITCH, Z, M)
    for i in range(3):
        ac.add_anode(r, 19.0 + i * 0.6, Z, M)
    rk = pb.Part("REF_RejectAnode", pivot=(STATIONS['reject'], -2.6, 0))
    ac.add_anode(rk, STATIONS['reject'], Z, M)
    rk.finish(ref).location.y += -2.6
    r.finish(ref)
    ac.floor_ref(ref, -2, 30, -6, 5)


def readme(col):
    rows = pb.pivot_table([col.name])
    return f"""# SM_AnodePrepMachine - anode preparation machine

Takes cast anodes from the stacking area, weighs them, flattens them, straightens and mills the
lug undersides, rejects bad ones and sets the rest at cell pitch for the tankhouse crane.

**Own design.** The station sequence follows US4903519 (straightening press), US5799529 (lug
straightening and machining) and US8227345 (high-capacity anode preparation). I found no drawings
with dimensions, so the layout and every machine size here are estimates.

## Placement

- Origin (0, 0, 0): floor at the infeed end, on the line centre. Anodes move along +X.
- Footprint: x -0.5 to 28.9, y -4.7 to 3.6 (about 29.4 x 8.3 m including pulpit and HPU).
- Infeed: forklift sets a load of anodes (face to face) on the infeed chains, x 0 to 7, lug seat at
  z = {ac.HANG_Z:.2f} m. Chains at y = +-{CHAIN_Y:.2f}.
- Outfeed: crane pickup zone on the spacing chain, x {PICK_X0:.2f} to {SPACER[1] - 0.35 + 0.05:.2f},
  {LOAD} anodes at {ac.PITCH * 1000:.0f} mm pitch, lug seat z = {ac.HANG_Z:.2f} m. End stop at x = {SPACER[1] + 0.35:.2f}.
- Tankhouse link: the crane carries a cell load between this machine and the tankhouse transfer stand AnodeIn at (-12, -8) (tankhouse coordinates, seat z 1.20, electrodes stacked along Y, so this machine's X runs along the tankhouse Y there). See Meshes/Tankhouse/README.md.
- Reject rack (lug rails, seat z = {ac.HANG_Z:.2f}) on the -Y side, centred at ({STATIONS['reject']:.1f}, -2.6).
- Lug span {ac.ANODE_LUG_SPAN:.2f} m, same anode as the anode set and the tankhouse cells.

## Stations

| Station | x (m) | Moving parts |
|---|---|---|
| Infeed chains | 0 to 7 | AP_Infeed_L/R_Chain, sprockets |
| Walking beam pick | {STATIONS['pick']} | AP_WalkingBeam: up 0.05 m, +X 1.5 m, down, back (rectangular cycle); lift and travel cylinders follow |
| Weigh | {STATIONS['weigh']} | none (rail on load cells) |
| Flatten press | {STATIONS['press']} | AP_PressPlaten_Up/Down slide along X toward the anode, 0.3 m stroke |
| Lug straightening | {STATIONS['lugpress']} | AP_LugPressHead_L/R move down 0.17 m onto the lugs |
| Lug milling | {STATIONS['mill']} | AP_MillHead_L/R and AP_MillCutter_L/R rise 0.05 m together; cutters spin about Z |
| Inspection + reject | {STATIONS['reject']} | AP_RejectTongs lift 0.3 m (move along Z), AP_RejectTrolley travels -2.6 m along Y to the reject rack; tongs ride with the trolley |
| Spacing chain + pickup | {SPACER[0]} to {SPACER[1]} | AP_Spacer_L/R_Chain, AP_SpacerDogs (move with the chain) |

Hydraulic cylinders are split into _Barrel (pivot at the base end) and _Rod (pivot at the rod end),
both with local +X along the cylinder axis, so they can be aimed at each other.

### Pivots (all exported parts)

| Object | Pivot (Blender X, Y, Z) |
|---|---|
{rows}

{ac.UNREAL_NOTE}
## Dimensions

| Item | Value | Status |
|---|---|---|
| Capacity | up to 500 anodes/h | Sourced, Metso brochure (vendor claim) |
| Anode body | {ac.ANODE_W} x {ac.ANODE_H} x {ac.ANODE_T} m, lugs {ac.ANODE_LUG_H} x {ac.ANODE_LUG_T} m | Matches ATC_Anode from the anode set. By volume it is ~415 kg, above the sourced 300-380 kg range |
| Lug span | {ac.ANODE_LUG_SPAN} m | Matches ATC_Anode (estimated there) |
| Electrode pitch | {ac.PITCH} m | Sourced (same-type pitch in the cell) |
| Anodes per cell load | {LOAD} | Inside the sourced 30-50 range; change LOAD in the script |
| Lug seat height {ac.HANG_Z} m, chains 7 m and 12.5 m, 1.5 m station step | | Own design |
| Press frame 2.3 x 2.4 x 3.3 m, platens 0.92 x 0.90 m | | Estimated |

Sources: US4903519A, US5799529A, US8227345B2 (patents.google.com); Metso copper electrorefining
brochure (https://metso.com/globalassets/industry-pages/metals-refining/hydrometallurgy/mo_copper_electrorefining_brochure_final_lowres.pdf).

## Files

- SM_AnodePrepMachine.blend / .fbx (REF collection with anodes, floor and figure is not exported)
- Preview_Overview.png, Preview_PressMill.png, Preview_Pickup.png
"""


VIEWS = [
    ("Preview_Overview.png", (-5, -15, 11), (13.5, 0, 0.0), 24),
    ("Preview_PressMill.png", (8.2, 5.8, 3.8), (12.2, 0, 1.3), 28, ("Guards", "Dressing")),
    ("Preview_Pickup.png", (31, -6, 4.5), (24, 0, 1.3), 35),
]

if __name__ == "__main__":
    ac.run(ASSET, NAME, build, readme, VIEWS)
