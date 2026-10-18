"""
render_tankhouse_overview.py - places every tankhouse asset at the shared origin and renders
Meshes/Tankhouse/Preview_PlantOverview.png. Run after all build_*.py scripts.

Run:  blender -b --factory-startup --python Tools/Blender/Tankhouse/render_tankhouse_overview.py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import th_layout as L  # noqa: E402
from th_layout import pb  # noqa: E402

ASSETS = {   # folder: (blend name, objects hidden for the cutaway)
    "Tankhouse": ("SM_TankhouseBuilding", {"TH_Walls", "TH_Roof"}),
    "TankhouseCrane": ("SM_TankhouseCrane", set()),
    "RectifierBusbar": ("SM_RectifierBusbar", {"RB_RectifierHouse"}),
    "ElectrolyteCirculation": ("SM_ElectrolyteCirculation", {"EL_AnnexShell"}),
    "LiberatorCells": ("SM_LiberatorCells", {"LC_AnnexShell"}),
}


def main():
    pb.reset_scene()
    pb.clear_material_cache()
    m = L.materials()
    ref = pb.collection("REF")
    hidden = []
    lead = None
    for folder, (blend, hide) in ASSETS.items():
        obs = L.load_objects(L.asset_path(folder, blend))
        for o in obs:
            if o.name.startswith("REF_"):
                continue
            ref.objects.link(o)
            if o.name in hide:
                hidden.append(o)
            if o.name == "LC_LeadAnode":
                lead = o
    anode = L.ref_anode(ref, m["anode_cu"])
    cath = L.load_objects(L.asset_path("PermanentCathode", "SM_PermanentCathode"),
                          ["CA_Plate", "CA_DepositFront", "CA_DepositBack"])
    cell = L.load_objects(L.asset_path("ElectrolyticCell", "SM_ElectrolyticCell"),
                          ["EC_Body", "EC_FeedOverflow", "EC_Capping", "EC_IntercellBar", "EC_Electrolyte"])
    L.instance_collection("SRC_Parts", [anode] + cath + cell)
    loaded = [L.loaded_cell_collection(cell, anode, cath, odd, f"LoadedCell_{odd}") for odd in (0, 1)]
    for r, ry in L.ROW_Y.items():
        for i in range(L.CELLS_PER_ROW):
            L.place_instance(ref, loaded[i % 2], (L.cell_x(i), ry, 0), name=f"REF_Cell{r}{i}")
    # liberator row: cell shells only (hoods cover the electrodes)
    shells = L.instance_collection("SRC_Shell", [])
    for o in cell:
        lo = L.linked_copy(o, ref, (0, 0, 0))
        ref.objects.unlink(lo)
        shells.objects.link(lo)
    for n in range(8):
        L.place_instance(ref, shells, (66.2 + 0.66 + 1.32 * n, -3.0, 0), name=f"REF_LibCell{n}")
    if lead is not None:
        lead.hide_render = True
    pb.ref_ground(ref, (-90, -70, 130, 70), [(L.BLD_X0, -L.BLD_Y, L.BLD_X1, L.BLD_Y), (-32, -27, 0, -15),
                  (64, -10, 82, 4), (44, 15.3, 60, 27)], z=-0.31)
    pb.setup_render(res=(1920, 1080), samples=32)
    out = os.path.join(L.MESHES, "Tankhouse")
    pb.render_view(os.path.join(out, "Preview_PlantOverview.png"), (-62, -78, 58), (22, -2, 0), lens=30)
    for o in hidden:
        o.hide_render = True
    pb.render_view(os.path.join(out, "Preview_PlantCutaway.png"), (-50, -62, 40), (22, -2, -1), lens=30)


main()
