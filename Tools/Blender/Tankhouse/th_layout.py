"""
th_layout.py - shared layout constants and helpers for the electrorefining tankhouse assets.

Every tankhouse build script imports this module, so the cell pitch, row positions, crane
rail height and transfer points are defined once. Meshes/Tankhouse/README.md lists the same
numbers for the other threads.

Coordinates: tankhouse local frame, metres, Z up.
  +X = along the building (west -> east), +Y = across the building (south -> north).
  Origin = west end of the cell area, on the building centreline, at operating floor level.
  Place the tankhouse origin at flash-furnace world (0, -150, 0) with no rotation.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import psh_build as pb  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MESHES = os.path.join(REPO, "Meshes")

# ---------------------------------------------------------------------------
# Plant placement (flash furnace coordinates)
# ---------------------------------------------------------------------------
WORLD_ORIGIN = (0.0, -150.0, 0.0)

# ---------------------------------------------------------------------------
# Electrodes. Anode = ATC_Anode / CW_Anode from the anode set (measured from the .blend).
# ---------------------------------------------------------------------------
ANODE_W, ANODE_H, ANODE_T = 1.00, 1.00, 0.045      # body
ANODE_LUG_TIP = 0.66                               # lug tip at |x| from the anode centre
ANODE_LUG_H, ANODE_LUG_T = 0.12, 0.040             # lug height (top flush with body), thickness
ANODES_PER_CELL = 45
CATHODES_PER_CELL = 46
ELECTRODE_PITCH = 0.10                             # anode to anode, centre to centre

# Permanent cathode (estimated, see PermanentCathode/README.md)
BLADE_W, BLADE_H, BLADE_T = 1.04, 1.05, 0.00325
HANGER_L, HANGER_W, HANGER_H = 1.32, 0.025, 0.035
WINDOW_X, WINDOW_W, WINDOW_Z0, WINDOW_Z1 = 0.30, 0.12, -0.10, -0.03   # relative to the seat

# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------
SEAT_Z = 0.85                  # top of the intercell bar = underside of anode lugs and hanger bars
CAP_TOP = SEAT_Z - 0.025       # capping board top
RIM_Z = SEAT_Z - 0.05          # top of the polymer concrete walls
LIQUID_Z = SEAT_Z - 0.12       # electrolyte level
CELL_FLOOR_Z = SEAT_Z - 1.25   # inside floor
CELL_BOTTOM_Z = CELL_FLOOR_Z - 0.12
CELL_IN_W, CELL_IN_L = 1.12, 4.90      # inside, X (electrode width) x Y (row of electrodes)
CELL_WALL = 0.08
CELL_PITCH = 1.32              # cell centre to cell centre along a row (X)
CELLS_PER_ROW = 40
ROW_Y = {"A": -9.45, "B": -3.15, "C": 3.15, "D": 9.45}
CELL_OUT_L = CELL_IN_L + 2 * 0.10      # 5.10 m along Y

# Current runs D (west) -> C (east) -> B (west) -> A (east), see RectifierBusbar/README.md
ROW_FLOW = {"D": -1, "C": +1, "B": -1, "A": +1}


def cell_x(i):
    """Centre X of cell i (0..39) in any row."""
    return CELL_PITCH / 2 + CELL_PITCH * i


def anode_y(j, odd):
    """Cell-local Y of anode j (0..44). Odd cells are shifted -0.05 m (Walker stagger)."""
    return -2.20 + ELECTRODE_PITCH * j - (0.05 if odd else 0.0)


def cathode_y(k, odd):
    """Cell-local Y of cathode k (0..45)."""
    return -2.25 + ELECTRODE_PITCH * k - (0.05 if odd else 0.0)


# Anode instance transform inside a cell: ATC_Anode hanging, lugs along X.
ANODE_ROT = (0.0, -90.0, 90.0)     # Euler XYZ degrees
ANODE_ORIGIN_Z = SEAT_Z - 0.38     # lug underside is 0.38 above the anode origin when hanging
ANODE_ORIGIN_DY = ANODE_T / 2      # origin sits on the +Y face of the hanging anode

# ---------------------------------------------------------------------------
# Building and crane
# ---------------------------------------------------------------------------
BLD_X0, BLD_X1 = -32.0, 64.0
BLD_Y = 15.0                   # walls at y = +-15
COL_STEP = 6.0
BASEMENT_Z = -3.0
EAVES_Z, RIDGE_Z = 12.5, 14.5
SERVICE_BAY_X1 = -4.0          # service bay x -32 .. -4 at grade
CRANE_RAIL_Z = 8.0
CRANE_RAIL_Y = 14.4            # span 28.8 m
CRANE_X_MIN, CRANE_X_MAX = -28.0, 60.0

# Transfer stands in the service bay (electrode lug seat height 1.20)
TRANSFER_SEAT_Z = 1.20
TRANSFER = {
    "AnodeIn": (-12.0, -8.0),      # prepared anodes from the anode preparation machine
    "AnodeScrapOut": (-22.0, -8.0),  # spent anodes to the scrap washing machine
    "CathodeOut": (-12.0, 8.0),    # loaded cathodes to the stripping machine
    "CathodeBlankIn": (-22.0, 8.0),  # stripped blanks back from the stripping machine
}


# ---------------------------------------------------------------------------
# Shared materials
# ---------------------------------------------------------------------------
def materials():
    return {
        "steel": pb.mat("M_Steel_Dark", (0.12, 0.12, 0.13), 0.8, 0.5),
        "grey": pb.mat("M_Steel_Machined", (0.55, 0.55, 0.57), 0.9, 0.3),
        "stainless": pb.mat("M_Stainless", (0.62, 0.63, 0.64), 1.0, 0.25),
        "copper": pb.mat("M_Copper_Bus", (0.80, 0.42, 0.25), 1.0, 0.3),
        "cathode_cu": pb.mat("M_Copper_Cathode", (0.75, 0.38, 0.28), 1.0, 0.45),
        "anode_cu": pb.mat("M_AnodeCopper", (0.45, 0.22, 0.14), 0.9, 0.6),
        "polymer": pb.mat("M_PolymerConcrete", (0.25, 0.27, 0.28), 0.0, 0.7),
        "liner": pb.mat("M_CellLiner_Vinylester", (0.18, 0.22, 0.20), 0.0, 0.35),
        "capping": pb.mat("M_CappingBoard", (0.85, 0.85, 0.80), 0.0, 0.5),
        "frp": pb.mat("M_FRP", (0.55, 0.62, 0.55), 0.0, 0.4),
        "pp": pb.mat("M_Polypropylene", (0.9, 0.9, 0.85), 0.0, 0.5),
        "electrolyte": pb.mat("M_Electrolyte", (0.12, 0.35, 0.55), 0.0, 0.05),
        "concrete": pb.mat("M_Concrete", (0.55, 0.54, 0.52), 0.0, 0.9),
        "floor": pb.mat("M_AcidProofFloor", (0.35, 0.40, 0.38), 0.0, 0.6),
        "grating": pb.mat("M_Grating_FRP", (0.65, 0.5, 0.15), 0.0, 0.6),
        "yellow": pb.mat("M_Safety_Yellow", (0.85, 0.65, 0.05), 0.2, 0.45),
        "crane": pb.mat("M_Crane_Paint", (0.85, 0.55, 0.05), 0.2, 0.45),
        "blue": pb.mat("M_Equipment_Blue", (0.08, 0.22, 0.45), 0.2, 0.5),
        "cabinet": pb.mat("M_Cabinet_Grey", (0.70, 0.72, 0.72), 0.3, 0.45),
        "rubber": pb.mat("M_Rubber", (0.03, 0.03, 0.03), 0.0, 0.85),
        "cladding": pb.mat("M_Cladding", (0.62, 0.66, 0.68), 0.5, 0.45),
        "roof": pb.mat("M_Roof", (0.45, 0.48, 0.50), 0.5, 0.5),
        "glass": pb.mat("M_Glass", (0.05, 0.08, 0.1), 0.0, 0.05),
        "lead": pb.mat("M_Lead_Anode", (0.32, 0.33, 0.35), 0.7, 0.55),
        "red": pb.mat("M_Signal_Red", (0.6, 0.03, 0.02), 0.1, 0.4),
        "green": pb.mat("M_Signal_Green", (0.05, 0.45, 0.1), 0.1, 0.4),
        "black": pb.mat("M_Black", (0.02, 0.02, 0.02), 0.2, 0.5),
        "lamp": pb.mat("M_Lamp", (1, 1, 0.9), 0, 0.2, emit=((1, 0.95, 0.85), 5.0)),
        "screen": pb.mat("M_Screen", (0.05, 0.1, 0.2), 0, 0.2, emit=((0.2, 0.5, 1.0), 2.0)),
    }


# ---------------------------------------------------------------------------
# REF electrodes and instancing (previews only, never exported)
# ---------------------------------------------------------------------------
def ref_anode(col, m):
    """
    Copy of ATC_Anode: origin at the underside centre of the flat anode, lugs toward local +X
    (body 1.0 x 1.0 x 0.045, lugs x 0.38..0.50, |y| 0.50..0.66, z 0..0.04).
    """
    p = pb.Part("REF_Anode")
    p.box_mm((-0.5, -0.5, 0.0), (0.5, 0.5, ANODE_T), m)
    for s in (-1, 1):
        y0, y1 = sorted((s * 0.5, s * ANODE_LUG_TIP))
        p.box_mm((0.38, y0, 0.0), (0.50, y1, ANODE_LUG_T), m)
    return p.finish(col)


def instance_collection(name, objects):
    """Collection outside the scene that holds source objects for collection instances."""
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    for o in objects:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
    return c


def place_instance(col, src, loc, rot_deg=(0, 0, 0), name=None):
    """Empty in col that instances collection src at loc / rot."""
    e = bpy.data.objects.new(name or ("INST_" + src.name), None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = src
    e.location = loc
    e.rotation_euler = [math.radians(a) for a in rot_deg]
    col.objects.link(e)
    return e


def linked_copy(src_ob, col, loc, rot_deg=(0, 0, 0), name=None):
    """Object sharing src_ob's mesh, placed at loc / rot (degrees)."""
    o = bpy.data.objects.new(name or src_ob.name + "_i", src_ob.data)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    col.objects.link(o)
    return o


def load_objects(blend_path, names=None):
    """Append mesh objects (all, or the named ones) from another asset's .blend, unlinked."""
    with bpy.data.libraries.load(blend_path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if names is None or n in names]
    return [o for o in dst.objects if o is not None and o.type == 'MESH']


def asset_path(folder, name):
    return os.path.join(MESHES, folder, name + ".blend")


def loaded_cell_collection(cell_obs, anode_ob, cathode_obs, odd, name):
    """
    Collection with one cell (its exported parts) plus 45 anodes and 46 cathodes in their
    working positions, for instancing in previews.
    """
    c = bpy.data.collections.new(name)
    for o in cell_obs:
        lo = bpy.data.objects.new(o.name + "_" + name, o.data)
        lo.matrix_world = o.matrix_world.copy()
        c.objects.link(lo)
    for j in range(ANODES_PER_CELL):
        lo = bpy.data.objects.new(f"A{j}_{name}", anode_ob.data)
        lo.location = (0.0, anode_y(j, odd) + ANODE_ORIGIN_DY, ANODE_ORIGIN_Z)
        lo.rotation_euler = [math.radians(a) for a in ANODE_ROT]
        c.objects.link(lo)
    for k in range(CATHODES_PER_CELL):
        for co in cathode_obs:
            lo = bpy.data.objects.new(f"{co.name}{k}_{name}", co.data)
            lo.location = Vector(co.matrix_world.translation) + Vector((0.0, cathode_y(k, odd), SEAT_Z))
            c.objects.link(lo)
    return c


def write(path, text):
    with open(path, "w") as f:
        f.write(text)


def ref_lights(col, points, energy=400.0, name="REF_Lamp"):
    """Point lights for preview renders of enclosed spaces (basement, pump room)."""
    for i, p in enumerate(points):
        ld = bpy.data.lights.new(f"{name}{i}", 'POINT')
        ld.energy = energy
        ld.shadow_soft_size = 0.5
        o = bpy.data.objects.new(f"{name}{i}", ld)
        o.location = p
        col.objects.link(o)
