"""
build_plant_rail_cars.py - self-propelled in-plant rail cars.

Run:  blender -b --factory-startup --python Tools/Blender/Logistics/build_plant_rail_cars.py
      (add  -- Ladle  or  -- Anode  to build one asset only)

Assets:
    Meshes/LadleTransferCar/SM_LadleTransferCar   electric ladle car with a 9 m3 matte / blister ladle
    Meshes/AnodeTransferCar/SM_AnodeTransferCar   battery car carrying three 20-anode stacks

Both: origin on the track centre line at top of rail (z = 0), +X = A end (the cable reel / cab end),
standard gauge, UIC buffers at the shared height in psh_logi.py.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import psh_logi as pl  # noqa: E402

pb, pm = pl.pb, pl.pm

WHEEL_R = 0.46
DECK_Z = 1.20           # top of the deck plate on both cars


def body_frame(p, half_len, m, paint, width=2.8):
    """Deck plate, underframe and buffers at both ends."""
    pl.underframe(p, -half_len, half_len, DECK_Z - 0.03, m, paint, width=width)
    p.box_mm((-half_len, -width / 2, DECK_Z - 0.03), (half_len, width / 2, DECK_Z), m['steel'])
    for d in (1, -1):
        pl.buffers_and_coupling(p, d * (half_len + 0.75), d, m, paint)


def beacon(p, loc, m):
    p.cyl(0.08, 0.12, loc, m['orange'], seg=12)
    p.cyl(0.06, 0.1, Vector(loc) + Vector((0, 0, 0.11)), m['lamp'], seg=12)


def common_result(name, about, moving, dims, sources, folder, previews):
    n_obj, n_tri = pm.counts(name)
    return dict(name=name, about=about, n_obj=n_obj, n_tri=n_tri, previews=previews,
                moving=moving, dims=dims, sources=sources)


# ===========================================================================
# Ladle transfer car
# ===========================================================================

# Ladle: conical bowl, inner 2.90 m top / 2.20 m bottom diameter, 1.90 m deep
# -> pi*h/3*(R^2 + R*r + r^2) = 9.8 m3 brim-full, 9.0 m3 working (0.15 m freeboard).
LADLE_IN_TOP_R, LADLE_IN_BOT_R, LADLE_IN_D = 1.45, 1.10, 1.90
LINING = 0.25            # steel shell + refractory
LADLE_BOT_Z = DECK_Z + 0.20                     # sits on a 0.2 m seat ring
LADLE_H = LADLE_IN_D + LINING
TRUNNION_Z = LADLE_BOT_Z + 1.45


def ladle_radius(z):
    """Outer shell radius at height z."""
    t = (z - LADLE_BOT_Z) / LADLE_H
    return (LADLE_IN_BOT_R + LINING) + (LADLE_IN_TOP_R - LADLE_IN_BOT_R) * t


def build_ladle_car():
    name = "SM_LadleTransferCar"
    folder = "LadleTransferCar"
    col, ref, m = pm.start(name)
    paint = m['blue']
    HL = 3.6                                    # half length of the frame
    refr = m['refr']

    # --- car body ---
    car = pb.Part("LTC_Body")
    body_frame(car, HL, m, paint, width=3.0)
    car.cyl(1.55, 0.20, (0, 0, DECK_Z + 0.10), m['grey'], seg=32)               # ladle seat ring
    for s in (1, -1):                                                         # trunnion saddles
        y = s * (ladle_radius(TRUNNION_Z) + 0.35)
        car.box((0.6, 0.35, TRUNNION_Z - DECK_Z - 0.18), (0, y, (DECK_Z + TRUNNION_Z - 0.18) / 2), paint)
        car.box((0.6, 0.45, 0.12), (0, y, TRUNNION_Z - 0.24), m['steel'])
        car.box((0.6, 0.08, 0.35), (0, y + s * 0.2, TRUNNION_Z - 0.05), m['steel'])  # outer cheek
        # heat shield plate between ladle and bogies / cable
    car.box_mm((-HL + 0.1, -1.5, DECK_Z), (-HL + 0.15, 1.5, DECK_Z + 1.2), m['steel'])
    # A end: cable reel drum on a frame, drive cabinet and beacon
    car.box_mm((HL - 1.4, -1.4, DECK_Z), (HL - 0.2, -0.4, DECK_Z + 1.4), m['grey'])     # drive cabinet
    for s in (0.25, 1.25):
        car.box_mm((HL - 0.75 - 0.05, s - 0.05, DECK_Z), (HL - 0.75 + 0.05, s + 0.05, DECK_Z + 1.5), paint)
    beacon(car, (HL - 0.8, -0.9, DECK_Z + 1.46), m)
    # traction motors on the inner axle of each bogie (body-mounted, simplified)
    for x in (2.0, -2.0):
        car.box((0.7, 0.9, 0.5), (x - math.copysign(0.4, x), 0, 0.85), m['steel'])
    ob_body = car.finish(col)

    reel = pb.Part("LTC_CableReel", pivot=(HL - 0.75, 0.75, DECK_Z + 1.3))
    reel.cyl(0.9, 0.08, (HL - 0.75, 0.42, DECK_Z + 1.3), m['yellow'], rot=(90, 0, 0), seg=32)
    reel.cyl(0.9, 0.08, (HL - 0.75, 1.08, DECK_Z + 1.3), m['yellow'], rot=(90, 0, 0), seg=32)
    reel.cyl(0.55, 0.62, (HL - 0.75, 0.75, DECK_Z + 1.3), m['rubber'], rot=(90, 0, 0), seg=32)
    reel.cyl(0.08, 0.95, (HL - 0.75, 0.75, DECK_Z + 1.3), m['grey'], rot=(90, 0, 0), seg=12)
    ob_reel = reel.finish(col)
    pm.parent(ob_reel, ob_body)

    bogies = []
    for i, x in enumerate((2.1, -2.1)):
        fr, ws = pl.bogie(f"LTC_Bogie{i + 1}", x, col, m, wheelbase=1.8, r=WHEEL_R)
        pm.parent(fr, ob_body)
        bogies.append(fr)

    # --- ladle (crane-liftable by the trunnions) ---
    la = pb.Part("LTC_Ladle", pivot=(0, 0, TRUNNION_Z))
    rb, rt = LADLE_IN_BOT_R + LINING, LADLE_IN_TOP_R + LINING
    la.cyl(rb, LADLE_H, (0, 0, LADLE_BOT_Z + LADLE_H / 2), m['steel'], r2=rt, seg=40)    # outer shell
    # visible refractory rim and inner lining top ring
    la.cyl(rt + 0.03, 0.12, (0, 0, LADLE_BOT_Z + LADLE_H - 0.06), m['steel'], seg=40)
    la.cyl(LADLE_IN_TOP_R, 0.02, (0, 0, LADLE_BOT_Z + LADLE_H + 0.005), refr, seg=40)
    for z in (LADLE_BOT_Z + 0.5, LADLE_BOT_Z + 1.2):                                     # stiffener bands
        r = ladle_radius(z)
        la.cyl(r + 0.04, 0.12, (0, 0, z), m['steel'], seg=40)
    for s in (1, -1):                                                                  # trunnions
        r = ladle_radius(TRUNNION_Z)
        la.box((0.7, 0.2, 0.7), (0, s * (r + 0.02), TRUNNION_Z), m['steel'])
        la.cyl(0.15, 0.45, (0, s * (r + 0.32), TRUNNION_Z), m['grey'], rot=(90, 0, 0), seg=20)
        la.cyl(0.24, 0.06, (0, s * (r + 0.57), TRUNNION_Z), m['grey'], rot=(90, 0, 0), seg=20)
    # pouring lip on +X, tipping lug low on -X (crane auxiliary hook lifts it to pour toward +X)
    lip_z = LADLE_BOT_Z + LADLE_H
    la.box((0.55, 0.7, 0.15), (rt + 0.18, 0, lip_z - 0.12), m['steel'], rot=(0, 15, 0))
    la.box((0.35, 0.25, 0.35), (-(rb + 0.15), 0, LADLE_BOT_Z + 0.3), m['steel'])
    la.cyl(0.1, 0.3, (-(rb + 0.15), 0, LADLE_BOT_Z + 0.3), m['grey'], rot=(90, 0, 0), seg=12)
    ob_ladle = la.finish(col)

    # lid, hinged on the -X rim (opens away from the pouring lip)
    hinge = Vector((-(rt + 0.12), 0, lip_z + 0.05))
    lid = pb.Part("LTC_Lid", pivot=hinge)
    lid.cyl(rt + 0.08, 0.10, (0, 0, lip_z + 0.07), m['steel'], seg=40)
    lid.cyl(rt - 0.3, 0.12, (0, 0, lip_z + 0.17), refr, seg=40, r2=rt - 0.5)
    for y in (-0.6, 0.6):
        lid.box((0.4, 0.08, 0.14), (-(rt + 0.02), y, lip_z + 0.08), m['steel'])
        lid.cyl(0.05, 0.2, (hinge.x, y, hinge.z), m['grey'], rot=(90, 0, 0), seg=10)
    lid.cyl_between((rt - 0.3, -0.3, lip_z + 0.15), (rt - 0.3, 0.3, lip_z + 0.15), 0.04, m['grey'])  # handle
    ob_lid = lid.finish(col)
    pm.parent(ob_lid, ob_ladle)
    pm.parent(ob_ladle, ob_body)

    pb.ref_human(ref, (1.0, -2.6, 0.0))
    table = pm.finish_asset(name, folder, [
        ("Preview_LadleTransferCar.png", (9.0, -9.5, 5.5), (0, 0, 2.0), 30),
        ("Preview_LadleTransferCar_LidOpen.png", (-8.5, -8.0, 7.0), (0, 0, 2.6), 30, True)],
        pose=lambda: setattr(ob_lid.rotation_euler, 'y', math.radians(-100)))

    vol_full = math.pi * LADLE_IN_D / 3 * (LADLE_IN_TOP_R ** 2 + LADLE_IN_TOP_R * LADLE_IN_BOT_R + LADLE_IN_BOT_R ** 2)
    res = common_result(
        name,
        "Self-propelled rail ladle car for the converter aisle: carries a matte or blister copper ladle "
        "between the furnace tapping launders and the converter-aisle crane. Electric drive fed from a "
        "cable reel at the A end (+X); two four-wheel bogies; UIC buffers so the plant locomotive can "
        "shunt it. The ladle is a separate part that the converter-aisle crane lifts by its two "
        "trunnions (along Y) and pours by lifting the tipping lug on the -X side with the auxiliary hook. "
        "Slag pots use the existing straddle carrier (Meshes/SlagPotCarrier), not this car.\n\n"
        f"Ladle: {vol_full:.1f} m3 brim-full, 9.0 m3 working. Loaded with 9.0 m3 of matte at about "
        "5 t/m3 that is about 45 t of matte (blister copper at about 7.8 t/m3 would be about 70 t, so "
        "fill blister ladles to about 6 m3). Own design. Origin: track centre, top of rail, under the "
        "ladle centre.",
        "| Part | Motion |\n|---|---|\n"
        "| LTC_Body | Travels along X. Parent of everything else in the .blend |\n"
        f"| LTC_Bogie1/2_Frame | Yaw about local Z in curves |\n"
        f"| LTC_Bogie*_WS1/WS2 | Spin about local Y: {pl.deg_per_metre(WHEEL_R):.1f} deg per metre travelled |\n"
        "| LTC_CableReel | Spins about local Y as the car travels (pays out / winds the trailing cable) |\n"
        f"| LTC_Ladle | Lifted off by the crane; pivot on the trunnion axis (z {TRUNNION_Z:.2f}), tilt about local Y to pour toward +X |\n"
        "| LTC_Lid | Hinge on the -X rim; rotate about local Y, -100 deg = open (preview 2) |",
        f"""| Item | Value | Source |
|---|---|---|
| Gauge, buffers | 1.435 m; buffers 1.75 m apart at z 1.06 | Standard / UIC |
| Wheels | 920 mm, two bogies at x +-2.1, wheelbase 1.8 m | Estimated |
| Length over buffers | {2 * (3.6 + 0.75):.2f} m; frame width 3.0 m | Estimated |
| Deck top | z {DECK_Z:.2f} | Estimated |
| Ladle | inner 2.90 / 2.20 m diameter, 1.90 m deep; outer 3.40 m top, {LADLE_H:.2f} m tall; {vol_full:.1f} m3 full | Estimated (own design) |
| Trunnion axis | z {TRUNNION_Z:.2f}, trunnion ends at y +-{ladle_radius(TRUNNION_Z) + 0.6:.2f} | Estimated |
| Top of ladle rim / lid | z {LADLE_BOT_Z + LADLE_H:.2f} / about z {LADLE_BOT_Z + LADLE_H + 0.23:.2f} | Estimated |
| Mass (estimated) | car about 25 t, empty lined ladle about 20 t, 45 t matte: about 90 t total, 22.5 t axle load | Estimated |
| Matte density | about 5 t/m3 | Typical (brief) |""",
        "no sourced ladle dimensions found; historical converter-aisle descriptions mention ladles of "
        "10 t and more (https://www.911metallurgist.com/blog/smelter-slags-mattes/). Everything here is "
        "an own design.", folder, "Preview_LadleTransferCar.png, Preview_LadleTransferCar_LidOpen.png")
    res['table'] = table
    pm.write_group_readme(folder, INTRO_LADLE, [res])
    return res


# ===========================================================================
# Anode transfer car
# ===========================================================================

# Anode from the anode set / tankhouse (Tools/Blender/Tankhouse/th_layout.py)
ANODE_W, ANODE_H, ANODE_T = 1.00, 1.00, 0.045
ANODE_LUG_TIP, ANODE_LUG_H, ANODE_LUG_T = 0.66, 0.12, 0.040
STACK_N, STACK_PITCH = 20, 0.05                 # face to face, 5 mm clearance
STACK_LEN = STACK_N * STACK_PITCH               # 1.00 m along X
SEAT_Z = DECK_Z + 0.95                          # lug undersides on the lug rails
STACK_X = (-1.75, 0.0, 1.75)


def build_anode_car():
    name = "SM_AnodeTransferCar"
    folder = "AnodeTransferCar"
    col, ref, m = pm.start(name)
    paint = m['green']
    HL = 3.0

    car = pb.Part("ATC2_Body")
    body_frame(car, HL, m, paint, width=2.8)
    # battery box and controller under the deck between the bogies
    car.box_mm((-0.9, -1.1, 0.55), (0.9, 1.1, DECK_Z - 0.35), m['grey'])
    car.box_mm((-0.85, 1.1, 0.75), (-0.25, 1.14, DECK_Z - 0.45), m['yellow'])        # charge socket panel
    # lug racks: two rails per stack at the lug line, posts and end guides
    for x in STACK_X:
        for s in (1, -1):
            y = s * 0.60
            car.box_mm((x - STACK_LEN / 2 - 0.15, y - 0.04, SEAT_Z - 0.08), (x + STACK_LEN / 2 + 0.15, y + 0.04, SEAT_Z),
                       m['grey'])                                                     # lug rail
            for dx in (-STACK_LEN / 2 - 0.08, STACK_LEN / 2 + 0.08):                  # posts clear of the end anodes
                car.box((0.1, 0.1, SEAT_Z - 0.08 - DECK_Z), (x + dx, y, (DECK_Z + SEAT_Z - 0.08) / 2), paint)
                # locating guides: posts at each stack end, above the lug rail
                car.box((0.06, 0.12, 0.35), (x + dx, y, SEAT_Z + 0.17), m['yellow'])
        car.box_mm((x - 0.55, -0.65, DECK_Z), (x + 0.55, 0.65, DECK_Z + 0.04), m['rubber'])  # wear pad
    # operator platform and control pedestal at the A end, handrails
    car.box_mm((HL - 0.3, -1.4, DECK_Z), (HL + 0.45, 1.4, DECK_Z + 0.05), m['steel'])
    car.box_mm((HL - 0.1, 0.6, DECK_Z), (HL + 0.3, 1.1, DECK_Z + 1.1), m['grey'])        # control pedestal
    car.box_mm((HL + 0.28, 0.65, DECK_Z + 0.8), (HL + 0.31, 1.05, DECK_Z + 1.05), m['glass'])
    pb.handrail(car, (HL + 0.4, -1.35, DECK_Z), (HL + 0.4, 1.35, DECK_Z), m['yellow'])
    beacon(car, (HL, 0.85, DECK_Z + 1.12), m)
    for x in (1.9, -1.9):                                                              # traction motors
        car.box((0.6, 0.8, 0.45), (x - math.copysign(0.35, x), 0, 0.85), m['steel'])
    ob_body = car.finish(col)
    for i, x in enumerate((1.9, -1.9)):
        fr, ws = pl.bogie(f"ATC2_Bogie{i + 1}", x, col, m, wheelbase=1.8, r=WHEEL_R)
        pm.parent(fr, ob_body)

    # REF anode stack (not exported) on the middle seat
    anode_m = pb.mat("M_REF_Anode", (0.55, 0.25, 0.12), 0.9, 0.45)
    st = pb.Part("REF_AnodeStack_20")
    x0 = STACK_X[1] - STACK_LEN / 2 + STACK_PITCH / 2
    lug_len = ANODE_LUG_TIP - ANODE_W / 2
    for i in range(STACK_N):
        x = x0 + i * STACK_PITCH
        top = SEAT_Z + ANODE_LUG_H
        st.box((ANODE_T, ANODE_W, ANODE_H), (x, 0, top - ANODE_H / 2), anode_m)
        for s in (1, -1):
            st.box((ANODE_LUG_T, lug_len, ANODE_LUG_H), (x, s * (ANODE_W / 2 + lug_len / 2), SEAT_Z + ANODE_LUG_H / 2), anode_m)
    st.finish(ref)
    pb.ref_human(ref, (0.5, -2.4, 0.0))

    table = pm.finish_asset(name, folder, [
        ("Preview_AnodeTransferCar.png", (7.5, -8.0, 5.0), (0, 0, 1.4), 30)])
    top_z = SEAT_Z + 0.35
    seats = "\n".join(f"| Stack {i + 1} | ({x:.2f}, 0.00, {SEAT_Z:.2f}) | x {x - STACK_LEN / 2:.2f} to {x + STACK_LEN / 2:.2f} |"
                      for i, x in enumerate(STACK_X))
    res = common_result(
        name,
        "Battery-electric rail transfer car that carries cast anodes from the casting wheel / anode "
        "stacking area to the tankhouse service bay. Three stack seats, each a pair of lug rails at the "
        "lug line (y +-0.60) with yellow end guides: a forklift or crane sets a stack of 20 anodes "
        "hanging face to face by their lugs, the same way the anode preparation machine infeed takes "
        "them. Anode as in the tankhouse set: 1.00 x 1.00 x 0.045 m body, lugs to a 1.32 m span (45 mm "
        "is still the working thickness; T has not decided on thinning). Operator platform and "
        "radio/pedestal control at the A end (+X). Own design. One REF stack (not exported) sits on "
        "the middle seat in the .blend.\n\n"
        "Stack seats (lug underside, stack centre):\n\n| Seat | Centre (x, y, z) | Stack extent along X |\n"
        "|---|---|---|\n" + seats + "\n\n"
        f"Load: 3 x 20 anodes x about 415 kg = about 25 t. Highest point loaded: z {top_z:.2f} (guides), "
        "width 2.9 m over the platform, well inside the 6 x 6 m tankhouse service bay doors.",
        "| Part | Motion |\n|---|---|\n"
        "| ATC2_Body | Travels along X; parent of the bogies in the .blend |\n"
        "| ATC2_Bogie1/2_Frame | Yaw about local Z in curves |\n"
        f"| ATC2_Bogie*_WS1/WS2 | Spin about local Y: {pl.deg_per_metre(WHEEL_R):.1f} deg per metre travelled |",
        f"""| Item | Value | Source |
|---|---|---|
| Gauge, buffers | 1.435 m; buffers 1.75 m apart at z 1.06 | Standard / UIC |
| Length over buffers | {2 * (HL + 0.75):.2f} m, frame 2.8 m wide | Estimated |
| Deck top / lug seat | z {DECK_Z:.2f} / z {SEAT_Z:.2f} (anode bottoms clear the deck by 0.07 m) | Estimated |
| Wheels | 920 mm, bogies at x +-1.9 | Estimated |
| Anode | 1.00 x 1.00 x 0.045 m, lug span 1.32 m, about 415 kg | From the tankhouse set (th_layout.py) |
| Stack | 20 anodes at 50 mm pitch = 1.00 m | Stack count from the anode set; pitch estimated |""",
        "own design; anode sizes from the project's tankhouse set.", folder, "Preview_AnodeTransferCar.png")
    res['table'] = table
    pm.write_group_readme(folder, INTRO_ANODE, [res])
    return res


INTRO_LADLE = """
Rail ladle transfer car for the converter aisle. Built in Blender 5.2.2 LTS (headless, cloud) with
`Tools/Blender/Logistics/build_plant_rail_cars.py`. Runs on the RailTrackKit track (standard gauge,
top of rail z = 0). Vehicle at its own origin, not placed in the plant layout. In the .blend the
moving parts are parented to LTC_Body for posing.
"""

INTRO_ANODE = """
Rail anode transfer car between the anode casting / stacking area and the tankhouse service bay.
Built in Blender 5.2.2 LTS (headless, cloud) with `Tools/Blender/Logistics/build_plant_rail_cars.py`.
Runs on the RailTrackKit track (standard gauge, top of rail z = 0). Vehicle at its own origin, not
placed in the plant layout; a track into the service bay (doors 6 x 6 m, Meshes/Tankhouse/README.md)
is needed to use it there.
"""


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    builders = {"Ladle": build_ladle_car, "Anode": build_anode_car}
    for k in (argv or list(builders)):
        builders[k]()
