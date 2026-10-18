"""
psh_build.py - shared helpers for the Project Safe Haven mesh build scripts.

(Copy of Tools/Blender/psh_build.py from the slag handling branch, kept here so the
workshop, safety equipment and laboratory scripts run on their own.)

Every asset script imports this module. Geometry is built with bmesh directly
in world coordinates (metres), so no operator context is needed and the
scripts run headless:

    blender -b --factory-startup --python Tools/Blender/build_<asset>.py

A Part collects primitives into one mesh. When finished, its vertices are
shifted so the object origin sits on the chosen pivot, which is what Unreal
and Blender rotate the part around.
"""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

# --------------------------------------------------------------------------
# Scene and collections
# --------------------------------------------------------------------------

def reset_scene():
    """Empty the scene and purge all data blocks (the 'wipe' step of the pipeline)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    return scene


def collection(name, parent=None):
    """Return a collection with this name, creating and linking it if needed."""
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

_MATS = {}


def mat(name, color, metal=0.0, rough=0.6, emit=None):
    """Simple Principled BSDF material. Unreal gets the name and base colour slot."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit[0], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit[1]
    _MATS[name] = m
    return m


def clear_material_cache():
    _MATS.clear()


# --------------------------------------------------------------------------
# Matrix helpers
# --------------------------------------------------------------------------

def _mtx(loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    """Location (m), Euler XYZ rotation (degrees), scale -> 4x4 matrix."""
    r = [math.radians(a) for a in rot]
    from mathutils import Euler
    m = Euler(r, 'XYZ').to_matrix().to_4x4()
    s = Matrix.Diagonal((*scale, 1.0))
    return Matrix.Translation(loc) @ m @ s


def _align_z(p1, p2):
    """Matrix that puts local +Z along p1->p2, origin at the midpoint. Returns (matrix, length)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    length = d.length
    rot = d.normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return Matrix.Translation((p1 + p2) / 2) @ rot, length


# --------------------------------------------------------------------------
# Part: one output mesh object
# --------------------------------------------------------------------------

class Part:
    """Accumulates primitives (world coordinates) into one mesh with a pivot."""

    def __init__(self, name, pivot=(0, 0, 0)):
        self.name = name
        self.pivot = Vector(pivot)
        self.bm = bmesh.new()
        self.mats = []
        self.uv_faces = {}   # face -> list of (u, v) per loop, for belts

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, verts, m):
        """Give all faces touching the new verts the material index of m."""
        idx = self._mi(m)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = idx

    def box(self, size, loc, m, rot=(0, 0, 0)):
        """Axis box of size (x, y, z) centred on loc, optional rotation in degrees."""
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=_mtx(loc, rot, size))
        self._tag(res['verts'], m)
        return self

    def box_mm(self, mn, mx, m):
        """Box from min corner to max corner (no rotation)."""
        size = [b - a for a, b in zip(mn, mx)]
        loc = [(a + b) / 2 for a, b in zip(mn, mx)]
        return self.box(size, loc, m)

    def cyl(self, r, depth, loc, m, rot=(0, 0, 0), seg=24, r2=None, cap=True):
        """Cylinder (or cone when r2 is given) along local Z, centred on loc."""
        res = bmesh.ops.create_cone(self.bm, cap_ends=cap, cap_tris=False, segments=seg,
                                    radius1=r, radius2=r if r2 is None else r2,
                                    depth=depth, matrix=_mtx(loc, rot))
        self._tag(res['verts'], m)
        return self

    def cyl_between(self, p1, p2, r, m, seg=16, r2=None):
        """Cylinder (pipe, rod, column) from point p1 to point p2."""
        mtx, length = _align_z(p1, p2)
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                                    radius1=r, radius2=r if r2 is None else r2,
                                    depth=length, matrix=mtx)
        self._tag(res['verts'], m)
        return self

    def beam_between(self, p1, p2, w, h, m, roll=0.0):
        """Rectangular member from p1 to p2, cross section w x h."""
        mtx, length = _align_z(p1, p2)
        mtx = mtx @ Matrix.Rotation(math.radians(roll), 4, 'Z')
        res = bmesh.ops.create_cube(self.bm, size=1.0,
                                    matrix=mtx @ Matrix.Diagonal((w, h, length, 1.0)))
        self._tag(res['verts'], m)
        return self

    def sphere(self, r, loc, m, seg=16):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=seg // 2,
                                        radius=r, matrix=Matrix.Translation(loc))
        self._tag(res['verts'], m)
        return self

    def poly_prism(self, pts2d, z0, z1, m, plane='XY', offset=0.0):
        """Extruded polygon. pts2d are in the given plane; extrusion along the third axis."""
        verts_lo, verts_hi = [], []
        for a, b in pts2d:
            if plane == 'XY':
                lo, hi = (a, b, z0), (a, b, z1)
            elif plane == 'XZ':
                lo, hi = (a, z0, b), (a, z1, b)
            else:  # 'YZ'
                lo, hi = (z0, a, b), (z1, a, b)
            verts_lo.append(self.bm.verts.new(lo))
            verts_hi.append(self.bm.verts.new(hi))
        n = len(pts2d)
        faces = [self.bm.faces.new(verts_lo[::-1]), self.bm.faces.new(verts_hi)]
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((verts_lo[i], verts_lo[j], verts_hi[j], verts_hi[i])))
        idx = self._mi(m)
        for f in faces:
            f.material_index = idx
        return self

    def quad_strip(self, rows, m, closed=False):
        """Grid surface from rows of points (list of lists); closed joins last row to first."""
        vrows = [[self.bm.verts.new(p) for p in row] for row in rows]
        idx = self._mi(m)
        n = len(vrows) if closed else len(vrows) - 1
        for i in range(n):
            a, b = vrows[i], vrows[(i + 1) % len(vrows)]
            for j in range(len(a) - 1):
                f = self.bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
                f.material_index = idx
        return self

    def finish(self, col, smooth_angle=35.0, x_toward=None):
        """
        Create the object, origin at pivot, and link it into collection col.
        x_toward: optional world point; the object's local +X is turned to face it
        (used for hydraulic cylinders so a Damped Track constraint keeps them aligned).
        """
        me = bpy.data.meshes.new(self.name)
        if self.uv_faces:
            uv = self.bm.loops.layers.uv.new("UVMap")
            for f, coords in self.uv_faces.items():
                for loop, c in zip(f.loops, coords):
                    loop[uv].uv = c
        basis = Matrix.Translation(self.pivot)
        if x_toward is not None:
            x = (Vector(x_toward) - self.pivot).normalized()
            y = Vector((0, 0, 1)).cross(x)
            y = y.normalized() if y.length > 1e-6 else Vector((0, 1, 0))
            z = x.cross(y)
            basis = basis @ Matrix((x, y, z)).transposed().to_4x4()
        bmesh.ops.transform(self.bm, matrix=basis.inverted(), verts=self.bm.verts)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
        ob = bpy.data.objects.new(self.name, me)
        ob.matrix_world = basis
        col.objects.link(ob)
        return ob


# --------------------------------------------------------------------------
# Common sub-assemblies
# --------------------------------------------------------------------------

def handrail(p, a, b, m, h=1.1, post_step=1.8):
    """Two-rail handrail with posts along the floor line a->b (z of a, b is walking level)."""
    a, b = Vector(a), Vector(b)
    n = max(1, int((b - a).length / post_step))
    for i in range(n + 1):
        q = a.lerp(b, i / n)
        p.cyl_between(q, q + Vector((0, 0, h)), 0.025, m, seg=8)
    for z in (h, h * 0.5):
        p.cyl_between(a + Vector((0, 0, z)), b + Vector((0, 0, z)), 0.022, m, seg=8)
    p.beam_between(a + Vector((0, 0, 0.05)), b + Vector((0, 0, 0.05)), 0.006, 0.1, m)


def ladder(p, base, top_z, m, facing=0.0, width=0.5):
    """Vertical ladder from base point up to top_z, rungs every 0.3 m."""
    base = Vector(base)
    ang = math.radians(facing)
    side = Vector((-math.sin(ang), math.cos(ang), 0)) * (width / 2)
    for s in (side, -side):
        p.cyl_between(base + s, Vector((base.x, base.y, top_z)) + s, 0.025, m, seg=8)
    z = base.z + 0.3
    while z < top_z:
        p.cyl_between(Vector((base.x, base.y, z)) + side, Vector((base.x, base.y, z)) - side,
                      0.016, m, seg=6)
        z += 0.3


def flange(p, centre, axis_deg, r_pipe, m, label_list=None, name=None):
    """Stub flange disc, axis given as Euler rotation that turns local Z onto the pipe axis."""
    p.cyl(r_pipe * 1.6, 0.05, centre, m, rot=axis_deg, seg=24)
    if label_list is not None:
        label_list.append((name, tuple(round(c, 2) for c in centre)))


# --------------------------------------------------------------------------
# Conveyor with troughed belt and continuous UVs
# --------------------------------------------------------------------------

def conveyor(prefix, tail, head, width, col, mats, ground_z=0.0, walkway=True,
             trough=30.0, pulley_r=0.32, uv_m=1.2, legs=True):
    """
    Straight inclined belt conveyor from tail point to head point (belt top line at pulley tops).

    Builds:  <prefix>_Structure (stringers, idlers, legs, walkway)
             <prefix>_Belt      (closed loop, U along the belt = length / uv_m, V across = width / uv_m)
             <prefix>_HeadPulley, <prefix>_TailPulley (pivot on axis, spin about the axis)
    Returns dict with objects and the belt loop length.
    """
    tail, head = Vector(tail), Vector(head)
    d = head - tail
    horiz = Vector((d.x, d.y, 0)).normalized()
    side = Vector((-horiz.y, horiz.x, 0))           # left-hand side of travel
    run = d.normalized()
    up = run.cross(side).normalized() * -1          # normal to belt, pointing up
    if up.z < 0:
        up = -up
    L = d.length
    steel, rubber, grey, yellow = mats['steel'], mats['rubber'], mats['grey'], mats['yellow']

    # Pulley centres sit one radius below the belt top line
    c_tail = tail - up * pulley_r
    c_head = head - up * pulley_r
    yaw = math.degrees(math.atan2(horiz.y, horiz.x))

    # --- belt loop: carry run (troughed), head wrap, return run, tail wrap ---
    half = width / 2
    flat = width * 0.38 / 2                         # half width of the flat centre roll
    t_rad = math.radians(trough)

    def cross(s_frac, carry):
        """Return 4 cross-section offsets (side, up) for a station along the run."""
        if not carry:
            return [(-half, 0), (-flat, 0), (flat, 0), (half, 0)]
        # trough angle fades to flat within 2.5 m of each pulley
        dist = min(s_frac * L, (1 - s_frac) * L)
        k = min(1.0, dist / 2.5)
        a = t_rad * k
        w = half - flat
        return [(-(flat + w * math.cos(a)), w * math.sin(a)), (-flat, 0),
                (flat, 0), (flat + w * math.cos(a), w * math.sin(a))]

    rows, uvs, s_acc = [], [], 0.0
    prev = None

    def add_row(centre, normal, offs):
        nonlocal s_acc, prev
        if prev is not None:
            s_acc += (centre - prev).length
        prev = centre.copy()
        rows.append([centre + side * o + normal * h for o, h in offs])
        v0 = [(o + half) / uv_m for o, h in offs]
        uvs.append([(s_acc / uv_m, v) for v in v0])

    n_carry = max(8, int(L / 0.6))
    for i in range(n_carry + 1):
        f = i / n_carry
        add_row(tail.lerp(head, f), up, cross(f, True))
    # head wrap: 12 steps around the head pulley (from top to bottom)
    for i in range(1, 12):
        a = math.pi * i / 12
        nrm = up * math.cos(a) + run * math.sin(a)
        add_row(c_head + nrm * pulley_r, nrm, cross(0, False))
    # return run under the structure
    n_ret = max(4, int(L / 1.5))
    for i in range(n_ret + 1):
        f = i / n_ret
        add_row((c_head - up * pulley_r).lerp(c_tail - up * pulley_r, f), -up, cross(0, False))
    for i in range(1, 12):
        a = math.pi * i / 12
        nrm = -up * math.cos(a) - run * math.sin(a)
        add_row(c_tail + nrm * pulley_r, nrm, cross(0, False))
    # close loop: last row joins first row; U continues to total length
    s_total = s_acc + (rows[0][1] - rows[-1][1]).length
    belt = Part(prefix + "_Belt")
    vrows = [[belt.bm.verts.new(p) for p in r] for r in rows]
    idx = belt._mi(rubber)
    for i in range(len(vrows)):
        a, b = vrows[i], vrows[(i + 1) % len(vrows)]
        ua = uvs[i]
        ub = uvs[i + 1] if i + 1 < len(uvs) else [(s_total / uv_m, v) for (_, v) in uvs[0]]
        for j in range(3):
            f = belt.bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
            f.material_index = idx
            belt.uv_faces[f] = [ua[j], ub[j], ub[j + 1], ua[j + 1]]
    belt_ob = belt.finish(col, smooth_angle=60)

    # --- pulleys (separate, pivot on axis) ---
    out = {"Belt": belt_ob, "loop_length": s_total}
    for nm, c in (("HeadPulley", c_head), ("TailPulley", c_tail)):
        pp = Part(f"{prefix}_{nm}", pivot=c)
        pp.cyl(pulley_r - 0.01, width + 0.15, c, steel, rot=(90, 0, yaw), seg=24)
        pp.cyl(0.06, width + 0.6, c, grey, rot=(90, 0, yaw), seg=12)
        out[nm] = pp.finish(col)

    # --- structure: stringers, idler sets, legs, walkway ---
    st = Part(prefix + "_Structure", pivot=tail)
    sw = half + 0.25
    for s in (side * sw, -side * sw):
        st.beam_between(c_tail + s - run * 0.3, c_head + s + run * 0.1, 0.1, 0.3, steel)
        # pulley bearing blocks
        for c in (c_tail, c_head):
            st.box((0.3, 0.3, 0.25), c + s * 1.08, grey, rot=(0, 0, yaw))
    step = 1.2
    n_id = int((L - 1.0) / step)
    for i in range(1, n_id):
        f = (i * step) / L
        base = tail.lerp(head, f) - up * 0.18
        offs = cross(f, True)
        # three carry rolls following the trough profile
        for (o1, h1), (o2, h2) in ((offs[0], offs[1]), (offs[1], offs[2]), (offs[2], offs[3])):
            p1 = base + side * o1 + up * h1 - up * 0.07
            p2 = base + side * o2 + up * h2 - up * 0.07
            st.cyl_between(p1, p2, 0.064, grey, seg=10)
        st.beam_between(base - up * 0.2 + side * sw, base - up * 0.2 - side * sw, 0.08, 0.08, steel)
        if i % 3 == 0:  # return roll
            rb = tail.lerp(head, f) - up * (2 * pulley_r + 0.1)
            st.cyl_between(rb + side * half, rb - side * half, 0.064, grey, seg=10)
    if legs:
        n_leg = max(2, int(L / 6) + 1)
        for i in range(n_leg):
            f = 0.04 + 0.92 * i / (n_leg - 1)
            q = tail.lerp(head, f) - up * 0.45
            if q.z - ground_z < 0.6:
                continue
            for s in (side * sw, -side * sw):
                st.beam_between(q + s, Vector((q.x, q.y, ground_z)) + s, 0.15, 0.15, steel)
                st.box((0.4, 0.4, 0.05), Vector((q.x, q.y, ground_z + 0.025)) + s, grey)
            st.beam_between(Vector((q.x, q.y, (q.z + ground_z) / 2)) + side * sw,
                            Vector((q.x, q.y, (q.z + ground_z) / 2)) - side * sw, 0.1, 0.1, steel)
    if walkway:
        wo = side * (sw + 0.45)
        a = tail - up * 0.5 + wo
        b = head - up * 0.5 + wo
        st.beam_between(a, b, 0.8, 0.04, grey)
        handrail(st, a + side * 0.4, b + side * 0.4, yellow)
    out["Structure"] = st.finish(col)
    return out


# --------------------------------------------------------------------------
# Export, save, render
# --------------------------------------------------------------------------

def export_fbx(path, col_names):
    """Export the mesh objects of the named collections only (REF is never passed)."""
    bpy.ops.object.select_all(action='DESELECT')
    for cn in col_names:
        for ob in bpy.data.collections[cn].all_objects:
            if ob.type == 'MESH':
                ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True,
                             add_leaf_bones=False, bake_anim=False, axis_forward='-Z', axis_up='Y')


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


def setup_render(res=(1600, 900), samples=48):
    """Cycles CPU with denoising, plain sky colour and a sun."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'AgX'
    world = bpy.data.worlds.new("PreviewWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.55, 0.65, 0.8, 1)
    bg.inputs["Strength"].default_value = 0.6
    sc.world = world
    if "PreviewSun" not in bpy.data.objects:
        sun = bpy.data.lights.new("PreviewSun", 'SUN')
        sun.energy = 4.0
        sun.angle = math.radians(2)
        so = bpy.data.objects.new("PreviewSun", sun)
        so.rotation_euler = (math.radians(50), math.radians(10), math.radians(140))
        collection("REF").objects.link(so)


def render_view(path, cam_loc, target, lens=35.0, ortho=None):
    """Place the preview camera at cam_loc looking at target and render a PNG."""
    sc = bpy.context.scene
    cam = bpy.data.objects.get("PreviewCam")
    if cam is None:
        cd = bpy.data.cameras.new("PreviewCam")
        cam = bpy.data.objects.new("PreviewCam", cd)
        collection("REF").objects.link(cam)
    cam.data.clip_end = 5000
    cam.data.lens = lens
    if ortho:
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = 'PERSP'
    cam.location = cam_loc
    direction = Vector(target) - Vector(cam_loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def ref_human(col, loc):
    """1.8 m scale figure for the non-exported REF collection."""
    p = Part("REF_Human_1p8m", pivot=loc)
    x, y, z = loc
    m = mat("M_REF_Human", (0.9, 0.35, 0.1))
    p.box((0.35, 0.22, 0.85), (x, y, z + 0.425), m)
    p.box((0.42, 0.25, 0.65), (x, y, z + 1.17), m)
    p.sphere(0.12, (x, y, z + 1.66), m)
    return p.finish(col)


def pivot_table(cols):
    """Markdown rows: object name, pivot location, for README generation."""
    rows = []
    for cn in cols:
        for ob in sorted(bpy.data.collections[cn].all_objects, key=lambda o: o.name):
            if ob.type == 'MESH':
                l = ob.matrix_world.translation
                rows.append(f"| {ob.name} | ({l.x:.2f}, {l.y:.2f}, {l.z:.2f}) |")
    return "\n".join(rows)


def ref_ground(col, extent, holes, z=-0.01, name="REF_Ground"):
    """
    Flat REF ground at z with rectangular holes (x0, y0, x1, y1) left open for pits and ramps.
    The plane is split on every hole edge and only cells outside all holes are kept.
    """
    ex0, ey0, ex1, ey1 = extent
    xs = sorted({ex0, ex1, *[h[0] for h in holes], *[h[2] for h in holes]})
    ys = sorted({ey0, ey1, *[h[1] for h in holes], *[h[3] for h in holes]})
    xs = [x for x in xs if ex0 <= x <= ex1]
    ys = [y for y in ys if ey0 <= y <= ey1]
    p = Part(name)
    m = mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95)
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if any(h[0] < cx < h[2] and h[1] < cy < h[3] for h in holes):
                continue
            p.box_mm((xs[i], ys[j], z - 0.3), (xs[i + 1], ys[j + 1], z), m)
    return p.finish(col)


def append_asset(blend_path, col, loc, yaw_deg, prefix_filter=None):
    """
    Append the mesh objects of another asset's .blend into col (preview only) under one empty
    placed at loc with yaw. Existing parent links inside the asset are kept.
    """
    with bpy.data.libraries.load(blend_path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if prefix_filter is None or n.startswith(tuple(prefix_filter))]
    root = bpy.data.objects.new("REF_Root_" + os.path.basename(blend_path).split(".")[0], None)
    col.objects.link(root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    loaded = [o for o in dst.objects if o is not None]
    for o in loaded:
        col.objects.link(o)
        if o.parent is None or o.parent not in loaded:
            o.parent = root
    return {o.name: o for o in loaded}
