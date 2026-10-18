"""
psh_maint.py - extra helpers for the maintenance and mobile equipment scripts.

Builds on psh_build.py (copied unchanged from Tools/Blender/ on the slag handling branch so this
folder runs on its own). Adds wheels, crawler tracks, hydraulic cylinders, parenting, and one
call that saves, exports and renders a finished asset.

Every script in this folder runs headless:
    blender -b --factory-startup --python Tools/Blender/Maintenance/build_<group>.py
"""
import math
import os

import bpy
from mathutils import Vector

import psh_build as pb

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def out_dir(folder):
    """Meshes/<folder>, created if missing."""
    d = os.path.join(REPO, "Meshes", folder)
    os.makedirs(d, exist_ok=True)
    return d


def start(name):
    """Wipe the scene and return (asset collection, REF collection, common materials)."""
    pb.reset_scene()
    pb.clear_material_cache()
    col = pb.collection(name)
    ref = pb.collection("REF")
    m = dict(
        steel=pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5),
        grey=pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
        galv=pb.mat("M_Steel_Galvanised", (0.62, 0.63, 0.62), 0.9, 0.45),
        yellow=pb.mat("M_Paint_SafetyYellow", (0.85, 0.6, 0.05), 0.2, 0.45),
        orange=pb.mat("M_Paint_Orange", (0.9, 0.3, 0.03), 0.2, 0.45),
        blue=pb.mat("M_Paint_Blue", (0.05, 0.18, 0.45), 0.2, 0.45),
        green=pb.mat("M_Paint_Green", (0.08, 0.3, 0.12), 0.2, 0.5),
        red=pb.mat("M_Paint_Red", (0.6, 0.04, 0.03), 0.2, 0.45),
        white=pb.mat("M_Paint_White", (0.8, 0.8, 0.78), 0.1, 0.5),
        rubber=pb.mat("M_Rubber", (0.03, 0.03, 0.03), 0.0, 0.85),
        glass=pb.mat("M_Glass_Cab", (0.05, 0.08, 0.1), 0.0, 0.05),
        concrete=pb.mat("M_Concrete", (0.5, 0.49, 0.46), 0.0, 0.9),
        wood=pb.mat("M_Timber", (0.45, 0.3, 0.16), 0.0, 0.8),
        frp=pb.mat("M_FRP_Green", (0.35, 0.5, 0.35), 0.0, 0.4),
        refr=pb.mat("M_Refractory_Brick", (0.62, 0.36, 0.22), 0.0, 0.85),
        rope=pb.mat("M_WireRope", (0.3, 0.3, 0.3), 0.9, 0.55),
        lamp=pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0)),
    )
    return col, ref, m


# --------------------------------------------------------------------------
# Hierarchy
# --------------------------------------------------------------------------

def parent(child, par):
    """Parent keeping the child's world transform (preview posing in the .blend only)."""
    child.parent = par
    child.matrix_parent_inverse = par.matrix_world.inverted()


# --------------------------------------------------------------------------
# Wheels and tracks
# --------------------------------------------------------------------------

def wheel(name, centre, r, w, col, m, rim_r=None, seg=28):
    """Tyre + rim + hub on an axle along local Y. Pivot at the hub; spin about local Y."""
    p = pb.Part(name, pivot=centre)
    p.cyl(r, w, centre, m['rubber'], rot=(90, 0, 0), seg=seg)
    rr = rim_r or r * 0.62
    for s in (1, -1):   # rim faces slightly proud of the tread on both sides
        c = Vector(centre) + Vector((0, s * (w / 2 + 0.005), 0))
        p.cyl(rr, 0.02, c, m['grey'], rot=(90, 0, 0), seg=seg)
        p.cyl(rr * 0.35, 0.06, c + Vector((0, s * 0.02, 0)), m['steel'], rot=(90, 0, 0), seg=12)
    return p.finish(col)


def track(name, x_rear, x_front, y, r, w, col, m, ground=0.0):
    """
    Crawler track loop around two idlers of radius r, centred on line y, running along X.
    UV U runs along the loop (1 U = 1 m), so a panner at U speed = track speed (m/s) moves the
    shoes. Pivot at the loop centre. The idlers/rollers belong to the frame, not this part.
    """
    zc = ground + r
    rows, uvs, s = [], [], 0.0
    pts = []
    n_run = max(6, int((x_front - x_rear) / 0.15))
    for i in range(n_run + 1):                      # bottom run, rear -> front
        pts.append((x_rear + (x_front - x_rear) * i / n_run, zc - r, (0, -1)))
    for i in range(1, 16):                          # front wrap
        a = -math.pi / 2 + math.pi * i / 16
        pts.append((x_front + r * math.cos(a), zc + r * math.sin(a), (math.cos(a), math.sin(a))))
    for i in range(n_run + 1):                      # top run, front -> rear
        pts.append((x_front - (x_front - x_rear) * i / n_run, zc + r, (0, 1)))
    for i in range(1, 16):                          # rear wrap
        a = math.pi / 2 + math.pi * i / 16
        pts.append((x_rear + r * math.cos(a), zc + r * math.sin(a), (math.cos(a), math.sin(a))))
    t = 0.05                                        # shoe thickness
    prev = None
    for x, z, (nx, nz) in pts:
        if prev is not None:
            s += math.hypot(x - prev[0], z - prev[1])
        prev = (x, z)
        o = Vector((nx, 0, nz)) * t
        ring = [Vector((x, y - w / 2, z)) - o * 0.0, Vector((x, y - w / 2, z)) + o,
                Vector((x, y + w / 2, z)) + o, Vector((x, y + w / 2, z))]
        rows.append(ring)
        uvs.append([(s, 0.0), (s, 0.05), (s, 0.05 + w), (s, 0.1 + w)])
    total = s + math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
    p = pb.Part(name, pivot=((x_rear + x_front) / 2, y, zc))
    vrows = [[p.bm.verts.new(v) for v in r_] for r_ in rows]
    idx = p._mi(m['rubber'])
    for i in range(len(vrows)):
        a, b = vrows[i], vrows[(i + 1) % len(vrows)]
        ua = uvs[i]
        ub = uvs[i + 1] if i + 1 < len(uvs) else [(total, v) for (_, v) in uvs[0]]
        for j in range(3):
            f = p.bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
            f.material_index = idx
            p.uv_faces[f] = [ua[j], ub[j], ub[j + 1], ua[j + 1]]
    return p.finish(col, smooth_angle=50)


def track_frame(p, x_rear, x_front, y, r, w, m, ground=0.0):
    """Idlers, bottom rollers and side frame inside a track loop (added to an existing Part)."""
    zc = ground + r
    for x in (x_rear, x_front):
        p.cyl(r - 0.06, w * 0.8, (x, y, zc), m['steel'], rot=(90, 0, 0), seg=20)
    n = max(2, int((x_front - x_rear) / 0.35))
    for i in range(1, n):
        x = x_rear + (x_front - x_rear) * i / n
        p.cyl(0.07, w * 0.7, (x, y, ground + 0.12), m['grey'], rot=(90, 0, 0), seg=10)
    p.box_mm((x_rear, y - w * 0.35, zc - r * 0.55), (x_front, y + w * 0.35, zc + r * 0.55), m['steel'])


# --------------------------------------------------------------------------
# Hydraulic cylinder
# --------------------------------------------------------------------------

def hyd_cyl(prefix, base, tip, r, col, m, base_par=None, tip_par=None, frac=0.55):
    """
    Two parts aimed at each other: <prefix>_Barrel (pivot at base, local +X toward tip) and
    <prefix>_Rod (pivot at tip, local +X toward base). In Unreal give each a look-at to the
    other's pivot. In the .blend each half has a Damped Track to an empty at the other end's pin,
    and the empties ride on base_par / tip_par, so posing those parts poses the cylinder without
    a dependency cycle. Empties are not exported (FBX export takes meshes only).
    """
    base, tip = Vector(base), Vector(tip)
    L = (tip - base).length
    d = (tip - base).normalized()
    b = pb.Part(prefix + "_Barrel", pivot=base)
    b.cyl_between(base, base + d * L * frac, r, m['grey'], seg=14)
    b.cyl(r * 1.2, r * 1.6, base, m['steel'], rot=_rot_for_axis(d), seg=12)
    ob_b = b.finish(col, x_toward=tip)
    rd = pb.Part(prefix + "_Rod", pivot=tip)
    rd.cyl_between(tip, base + d * L * 0.1, r * 0.5, m['grey'], seg=12)
    rd.sphere(r * 0.7, tip, m['steel'], seg=10)
    ob_r = rd.finish(col, x_toward=base)
    for half, pin, par, other_par in ((ob_b, tip, tip_par, base_par), (ob_r, base, base_par, tip_par)):
        e = bpy.data.objects.new(half.name + "_Aim", None)
        e.empty_display_size = 0.05
        e.location = pin
        col.objects.link(e)
        if par is not None:
            parent(e, par)
        if other_par is not None:
            parent(half, other_par)
        c = half.constraints.new('DAMPED_TRACK')
        c.target = e
        c.track_axis = 'TRACK_X'
    return ob_b, ob_r


def _rot_for_axis(d):
    """Euler (deg) that turns local Z onto direction d (for cylinder end caps)."""
    e = Vector(d).to_track_quat('Z', 'Y').to_euler()
    return tuple(math.degrees(a) for a in e)


# --------------------------------------------------------------------------
# Railings and stairs
# --------------------------------------------------------------------------

def guard_box(p, x0, y0, x1, y1, z, m, h=1.1, open_side=None):
    """Handrails round a rectangle at floor level z. open_side: 'x0', 'x1', 'y0' or 'y1' left open."""
    edges = {'y0': ((x0, y0, z), (x1, y0, z)), 'y1': ((x0, y1, z), (x1, y1, z)),
             'x0': ((x0, y0, z), (x0, y1, z)), 'x1': ((x1, y0, z), (x1, y1, z))}
    for k, (a, b) in edges.items():
        if k != open_side:
            pb.handrail(p, a, b, m, h=h)


def stair(p, a, b, width, m, rail_m):
    """Straight stair from floor point a up to floor point b (both at walking level)."""
    a, b = Vector(a), Vector(b)
    run = Vector((b.x - a.x, b.y - a.y, 0))
    side = Vector((-run.y, run.x, 0)).normalized() * (width / 2)
    n = max(2, int((b.z - a.z) / 0.19))
    for s in (side, -side):
        p.beam_between(a + s, b + s, 0.03, 0.2, m)
    for i in range(1, n):
        q = a.lerp(b, i / n)
        p.beam_between(q + side * 0.95, q - side * 0.95, 0.25, 0.03, m)
    for s in (side, -side):
        pb.handrail(p, a + s, b + s, rail_m, h=1.0)


# --------------------------------------------------------------------------
# Finish an asset: save, export, render, pivot table
# --------------------------------------------------------------------------

def finish_asset(name, folder, views, pose=None, samples=32, res=(1280, 720), ground=60.0):
    """
    Save SM_<name>.blend and .fbx (asset collection only) into Meshes/<folder>/, then render
    each view (file, cam_loc, target, lens). pose(): optional callback run after saving and
    before the views flagged True in their 5th field, for working-pose previews. ground: half
    size of a REF ground slab added for the renders (None for no ground).
    Returns the markdown pivot table.
    """
    d = out_dir(folder)
    bpy.context.view_layer.update()          # children's world matrices after any re-placing
    table = pb.pivot_table([name])
    pb.save_blend(os.path.join(d, name + ".blend"))
    pb.export_fbx(os.path.join(d, name + ".fbx"), [name])
    pb.setup_render(res=res, samples=samples)
    if ground is not None and "REF_Ground" not in bpy.data.objects:
        g = pb.Part("REF_Ground")
        g.box_mm((-ground, -ground, -0.05), (ground, ground, -0.002),
                 pb.mat("M_REF_Ground", (0.33, 0.31, 0.27), 0, 0.95))
        g.finish(pb.collection("REF"))
    posed = False
    for v in views:
        fname, cam, tgt, lens = v[:4]
        if len(v) > 4 and v[4] and pose and not posed:
            pose()
            posed = True
        pb.render_view(os.path.join(d, fname), cam, tgt, lens)
    return table


def counts(name):
    """Object and triangle count of the asset collection (for the README)."""
    obs = [o for o in bpy.data.collections[name].all_objects if o.type == 'MESH']
    tris = 0
    for o in obs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    return len(obs), tris


def write_readme(folder, title, intro, sections):
    """sections: list of (heading, markdown body). Written to Meshes/<folder>/README.md."""
    lines = [f"# {title}", "", intro.strip(), ""]
    for h, body in sections:
        lines += [f"## {h}", "", body.strip(), ""]
    with open(os.path.join(out_dir(folder), "README.md"), "w") as f:
        f.write("\n".join(lines))


UNREAL_NOTE = """
Combine Meshes off. Transform Vertex to Absolute bakes each part's transform into its vertices,
which moves every pivot to the asset origin; for parts that move, import with it off and place
each part at the pivot listed in the table. With the default FBX settings Blender +Y appears as
-Y in Unreal, so check rotation signs after import. The REF collection (scale figure, preview
camera and sun) is not exported.
"""


def write_group_readme(folder, intro, results):
    """
    One README for a folder of assets. results: dicts with name, about, n_obj, n_tri, previews,
    moving, table, dims, sources (as returned by each builder).
    """
    sections = []
    for r in results:
        body = (r['about'].strip() + f"\n\n{r['n_obj']} parts, about {r['n_tri']:,} triangles. "
                f"Previews: {r['previews']}.\n\n### Moving parts\n\n" + r['moving'].strip() +
                "\n\n### Pivots\n\n| Object | Pivot (Blender X, Y, Z) |\n|---|---|\n" + r['table'] +
                "\n\n### Dimensions\n\n" + r['dims'].strip() + "\n\nSources: " + r['sources'])
        sections.append((r['name'], body))
    sections.append(("Unreal import", UNREAL_NOTE))
    write_readme(folder, folder, intro, sections)


def run(builders, folder, intro):
    """Build all assets (or those named after '--' on the command line) and write the README."""
    import sys
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    keys = argv or list(builders)
    results = [builders[k]() for k in keys]
    if not argv:   # partial runs leave the README alone
        write_group_readme(folder, intro, results)
