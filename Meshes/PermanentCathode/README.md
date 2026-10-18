# SM_PermanentCathode

Permanent stainless steel cathode of the IsaKidd type, for SM_ElectrolyticCell. Copper plates
onto both faces of the blade during a 7-day crop, and the cathode stripping machine peels the two
sheets off. The blank goes back into a cell.
- **Blade:** 316L stainless, 3.25 mm, with two lifting windows under the hanger bar (real plates
  are lifted by these; SM_TankhouseCrane hooks under the hanger bar instead, see its README).
- **Hanger bar:** rectangular bar, copper plated, resting on the intercell bar at one end and on
  the capping board at the other.
- **Edge strips:** polypropylene strips on both vertical edges stop the copper growing around them.
  The bottom edge is left bare (the V-groove of the Isa 2000 design is too small to model).
- **Deposit:** two separate copper sheets (front and back), so they can be hidden while the cathode
  is a bare blank, or peeled off by the stripping machine.

Built in Blender 5.2.2, metres, Z up. Files: `SM_PermanentCathode.blend`, `SM_PermanentCathode.fbx` (FBX_SCALE_NONE, mesh only).
Previews: `Preview_Cathode.png`, `Preview_Detail.png`.

## Origin and placement

- The origin is the **underside centre of the hanger bar**: the point that sits on the cell's
  seat line (SEAT_Z = 0.85 in tankhouse coordinates).
- The blade lies in the local XZ plane, thickness along Y. The hanger bar runs along X.
- In cell *k* (0 to 45): location = (cell centre x, cathode_y(k), 0.85), no rotation.
  cathode_y(k) = -2.25 + 0.10·k for even cells, 0.05 less for odd cells (see
  Meshes/Tankhouse/README.md).

## Parts and pivots

| Object | Use | Pivot (X, Y, Z) |
|---|---|---|
| CA_Plate (blade, plating, hanger bar, edge strips) | the blank, moves as a whole | (0, 0, 0) |
| CA_DepositFront / CA_DepositBack | copper sheet on the -Y / +Y face. Rotate about local X at the top edge to peel. Scale Y from 0 to 1 to show growth | on the top edge of each sheet |

Exact pivots (world):

| Object | Pivot |
|---|---|
| CA_DepositBack | (0.00, 0.00, -0.13) |
| CA_DepositFront | (0.00, -0.00, -0.13) |
| CA_Plate | (0.00, 0.00, 0.00) |

## Unreal import

Combine Meshes off and Transform Vertex to Absolute off, so the deposit pivots are kept.
Instance this mesh 46 times per cell (Instanced Static Mesh or HISM). With 160 cells this is
7,360 cathodes, so instancing is required.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Blade 316L stainless, 3.25 mm thick; hanger bar 304 stainless, copper plated | | Sourced (IsaKidd patents and Mount Isa patent summary) |
| Plating 15 mm down the blade (original Isa design; the BR design extends it to about 55 mm) | | Sourced (Wikipedia, IsaKidd refining technology) |
| PP edge strips on the side edges; bottom edge bare (V-groove) | | Sourced (patent summaries) |
| Harvested cathode about 1 × 1 m, 130–165 kg, 7-day crop common | | Sourced (research file, Wikipedia) |
| Blade 1.04 × 1.05 m below the bar | | Estimated to give about 1 × 1 m of deposit |
| Hanger bar 1.32 × 0.025 × 0.035 m | | Estimated. The length makes the bar end meet the anode lug tips of the next cell on the shared intercell bar |
| Lifting windows 0.12 m wide at x ±0.30, from 0.03 to 0.10 m below the bar | | Own design (real plates have windows; no dimensions found) |
| Deposit per sheet 8 mm, 1.024 × 0.915 m, both sheets about 134 kg | | Estimated to land in the sourced 130–165 kg range |

Sources: /mnt/project-files/research/copper-refinery/copper-refinery-equipment.md (§8);
https://en.wikipedia.org/wiki/IsaKidd_refining_technology; US8133366B2 / US7807028 (stainless
electrolytic plates); US20050126906 (hanger bar, Mount Isa Mines).
