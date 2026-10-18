"""
check_tankhouse.py - clearance checks between the tankhouse assets. Prints PASS / FAIL lines.

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/check_tankhouse.py

Checks (all with a 1 mm shrink so touching faces do not count):
  1. electrodes vs cell body, capping boards, intercell bar and neighbour cells
  2. crane hooks (open, bale lowered into an even cell) vs electrodes and cells
  3. crane hooks engaged: anode hook toes under every lug, cathode toes through every window
  4. carried anode load at travel height vs the electrodes of the other cells
"""
import os
import sys

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

SHRINK = 0.001


def bvh(obj_mesh, mtx):
    """BVH of a mesh in world space, every vertex pulled 1 mm toward its face centre."""
    bm = bmesh.new()
    bm.from_mesh(obj_mesh)
    bm.transform(mtx)
    bm.verts.index_update()
    # shrink by scaling each loose part about its own bounding-box centre
    parts = []
    seen = set()
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, island = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop()
            island.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    stack.append(b)
        parts.append(island)
    for island in parts:
        lo = Vector([min(v.co[i] for v in island) for i in range(3)])
        hi = Vector([max(v.co[i] for v in island) for i in range(3)])
        c = (lo + hi) / 2
        for v in island:
            for i in range(3):
                h = (hi[i] - lo[i]) / 2
                if h > SHRINK:
                    v.co[i] = c[i] + (v.co[i] - c[i]) * (h - SHRINK) / h
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def tf(loc, rot=(0, 0, 0)):
    from mathutils import Euler
    import math
    return Matrix.Translation(loc) @ Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()


def report(name, hits):
    print(("PASS " if not hits else "FAIL ") + name + ("" if not hits else f": {hits[:6]}"))


def main():
    pb.reset_scene()
    m = L.materials()
    anode = L.ref_anode(pb.collection("REF"), m["anode_cu"])
    cath = {o.name: o for o in L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"))}
    cell = {o.name: o for o in L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"))}
    crane = {o.name: o for o in L.load_objects(L.asset_path("TankhouseCrane", "SM_TankhouseCrane"))}
    plate = cath["CA_Plate"]

    # two neighbouring cells: cell 10 (even) and cell 11 (odd) of row A
    ry = L.ROW_Y["A"]
    cells = []
    for i in (9, 10, 11):
        for n in ("EC_Body", "EC_Capping", "EC_IntercellBar", "EC_FeedOverflow"):
            o = cell[n]
            cells.append((f"cell{i}:{n}", bvh(o.data, tf((L.cell_x(i), ry, 0)) @ o.matrix_world)))
    electrodes = []
    for i in (10, 11):
        odd = i % 2 == 1
        for j in range(L.ANODES_PER_CELL):
            mt = tf((L.cell_x(i), ry + L.anode_y(j, odd) + L.ANODE_ORIGIN_DY, L.ANODE_ORIGIN_Z), L.ANODE_ROT)
            electrodes.append((f"c{i}A{j}", bvh(anode.data, mt), mt))
        for k in range(L.CATHODES_PER_CELL):
            mt = tf((L.cell_x(i), ry + L.cathode_y(k, odd), L.SEAT_Z)) @ plate.matrix_world
            electrodes.append((f"c{i}K{k}", bvh(plate.data, mt), mt))

    # 1. electrodes vs cells and each other (neighbours only)
    hits = [(en, cn) for en, eb, _ in electrodes for cn, cb in cells if eb.overlap(cb)]
    report("electrodes clear of cell bodies, capping, bars, feed boxes", hits)
    hits = []
    for a in range(len(electrodes) - 1):
        for b in range(a + 1, min(a + 3, len(electrodes))):
            if electrodes[a][1].overlap(electrodes[b][1]):
                hits.append((electrodes[a][0], electrodes[b][0]))
    report("electrodes clear of each other (same cell neighbours)", hits)

    # 2. hooks open with the bale lowered into cell 10 (even): dz moves the crane pose down
    bale_z = crane["TC_Bale"].matrix_world.translation.z
    bx = crane["TC_Bale"].matrix_world.translation.x
    by = crane["TC_Bale"].matrix_world.translation.y
    shift = Vector((L.cell_x(10) - bx, ry - by, L.SEAT_Z - bale_z))
    hooks = {}
    for n in ("TC_AnodeHooks", "TC_CathodeHooks", "TC_Bale"):
        o = crane[n]
        hooks[n] = (o, Matrix.Translation(shift) @ o.matrix_world)
    cell10 = [e for e in electrodes if e[0].startswith("c10")]
    for n, (o, mt) in hooks.items():
        hb = bvh(o.data, mt)
        hits = [en for en, eb, _ in cell10 if hb.overlap(eb)]
        hits += [cn for cn, cb in cells if hb.overlap(cb)]
        report(f"{n} open, lowered into an even cell: clear", hits)

    # 3. engaged: move hooks, then lift 15 mm; every electrode must now touch a hook
    for n, dy, kind in (("TC_AnodeHooks", -0.008, "A"), ("TC_CathodeHooks", 0.006, "K")):
        o, mt = hooks[n]
        eng = Matrix.Translation((0, dy, 0)) @ mt
        hb = bvh(o.data, eng)
        hits = [en for en, eb, _ in cell10 if en[3] == kind and hb.overlap(eb)]
        report(f"{n} engaged (before lift): clear of its electrodes", hits)
        lifted = Matrix.Translation((0, 0, 0.015)) @ eng
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(lifted)
        hb2 = BVHTree.FromBMesh(bm)
        bm.free()
        missing = [en for en, eb, _ in cell10 if en[3] == kind and not hb2.overlap(eb)]
        report(f"{n} engaged + 15 mm lift: catches every {'anode' if kind == 'A' else 'cathode'}", missing)

    # 4. anode load at travel height over a loaded even cell and a loaded odd cell
    travel = 1.60
    loads = [bvh(anode.data, Matrix.Translation((0, 0, travel)) @ mt) for en, _, mt in cell10 if en[3] == "A"]
    below = [bvh(eb_mesh, mt) for en, _, mt in electrodes
             for eb_mesh in [anode.data if en[3] == "A" else plate.data]]
    below += [bvh(anode.data if en[3] == "A" else plate.data, Matrix.Translation((-L.CELL_PITCH, 0, 0)) @ mt)
              for en, _, mt in electrodes if en.startswith("c11")]
    hits = [i for i, lb in enumerate(loads) if any(lb.overlap(b) for b in below)]
    report("carried anodes at travel height clear of electrodes in the cells below", hits)

main()
