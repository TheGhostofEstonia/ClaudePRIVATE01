# SM_ElectrolyticCell

One copper electrorefining cell, for instancing along the four cell rows of SM_TankhouseBuilding.
- **Body:** polymer concrete monoblock with a vinyl ester liner, standing on four elastomer
  bearing pads on the building's cell support beams.
- **Electrodes:** 45 anodes (ATC_Anode / CW_Anode from the anode set) and
  46 permanent cathodes (SM_PermanentCathode) at a 100 mm anode pitch. The
  electrodes are not part of this mesh.
- **Contacts:** Walker-type double contact. Each cell owns the capping board and copper intercell
  bar on its +X wall pair. On that bar, the cathodes of this cell and the anodes of the next cell
  (+X) make contact. Their other ends rest on the capping boards.
- **Electrolyte:** enters at the -Y end through a feed box and a distributor pipe along the floor,
  and leaves over a weir in the +Y overflow box. Both boxes drain to flanges in the basement.

Built in Blender 5.2.2, metres, Z up. Files: `SM_ElectrolyticCell.blend`, `SM_ElectrolyticCell.fbx` (FBX_SCALE_NONE, 5 objects).
Previews: `Preview_Cell.png` (one loaded cell, electrolyte hidden),
`Preview_Row.png` (six cells showing the electrode stagger).

## Origin and placement

- Origin: cell centre at operating floor level. Tankhouse z 0 is the walkway level, so cell i of
  a row goes at **(0.66 + 1.32·i, ROW_Y, 0)** with no rotation. Rows: A y -9.45, B -3.15,
  C 3.15, D 9.45. 40 cells per row.
- All cells face the same way: feed at -Y, overflow at +Y, own intercell bar at +X.
- Seat line (top of the intercell bar and capping boards under the electrode ends) z 0.85.
- Electrode positions (cell-local Y), with the Walker stagger:

| | even cell (i = 0, 2, …) | odd cell |
|---|---|---|
| anode j (0–44) | -2.20 + 0.10·j | -2.25 + 0.10·j |
| cathode k (0–45) | -2.25 + 0.10·k | -2.30 + 0.10·k |

  With this stagger, each cathode of cell i and an anode of cell i+1 sit at the same Y and meet
  end to end on the intercell bar between them.
- Anode instance: ATC_Anode at (x, y_j + 0.0225, 0.47), rotation Euler XYZ
  (0°, -90°, 90°). Its lugs then point along ±X and their undersides sit on z 0.85.
- Cathode instance: SM_PermanentCathode at (x, y_k, 0.85), no rotation.
- Use the same orientation in all four rows. Current runs +X in rows A and C and -X in rows B and
  D (see RectifierBusbar/README.md). Because the insulator saddles are not modelled, the cell looks
  the same either way; in rows B and D read "anodes contact the +X bar, cathodes the -X bar".
  SM_RectifierBusbar supplies the end bar at the west end of each row (cell 0's -X side) and the
  end supports.

## Connection points (cell-local)

| Point | Position | Size |
|---|---|---|
| Electrolyte feed flange (from the row feed header) | (0.0, -2.6500000000000004, -1.0) | DN60 |
| Overflow drain flange (to the row return launder) | (0.0, 2.6500000000000004, -1.0) | DN90 |

## Parts and pivots

| Object | Use |
|---|---|
| EC_Body | static |
| EC_FeedOverflow | static |
| EC_Capping | static. Insulating boards, also covers the next cell's -X wall |
| EC_IntercellBar | static. Swap material to show hot spots |
| EC_Electrolyte | static. Hide when a cell is drained |

| Object | Pivot (cell-local) |
|---|---|
| EC_Body | (0.00, 0.00, 0.00) |
| EC_Capping | (0.00, 0.00, 0.00) |
| EC_Electrolyte | (0.00, 0.00, 0.00) |
| EC_FeedOverflow | (0.00, 0.00, 0.00) |
| EC_IntercellBar | (0.00, 0.00, 0.00) |

## Unreal import

Combine Meshes off. Place one Blueprint per cell with these five meshes, and two HISMs per cell
(or one HISM per row) for the anodes and cathodes. 160 cells × 91 electrodes = 14,560 instances.

## Dimensions

| Item | Value | Status |
|---|---|---|
| Inside 4.9 × 1.12 × 1.25 m (length × width × depth from the seat) | | Sourced range 4–5 m × 1.1 m × 1.2 m; exact values estimated to fit the anode |
| 45 anodes, 46 cathodes | | Sourced: 30–50 anodes per cell, one more cathode than anodes |
| Electrode pitch 100 mm (anode to anode); anode face to cathode face about 25 mm | | Sourced: 10 cm, at least 2.5 cm gap |
| Polymer concrete cell with vinyl ester lining | | Sourced: US6572741B1 |
| Electrolyte 60–65 °C in, 0.015–0.02 m³/min per cell | | Sourced (research file §8) |
| Wall 80 mm at the top, 120 mm floor, 40 mm gap between cells, 1.32 m cell pitch | | Estimated |
| Electrolyte level 0.12 m below the seat. The anode body is then about 0.76 m immersed | | Estimated. The fixed anode (lugs flush with its top edge) sets this |
| Feed box, distributor pipe, overflow box | | Estimated layout |
| Insulator saddles under the non-contact electrode ends | | Not modelled. Real Walker cells hold those ends a few mm above the bar on insulating saddles; here every end rests on the capping board or bar at the same height |

Sources: /mnt/project-files/research/copper-refinery/copper-refinery-equipment.md (§8 table:
cell size, electrodes per cell, pitch, flow); US6572741B1 (polymer concrete cell); US6045669
(cell contact system); WO2012114176A1 (busbar).
