# SM_RectifierBusbar

DC supply for the tankhouse cells: rectifier transformers, a rectifier house, the main DC bus,
row end bars and the crossovers that link the four rows into one series circuit. Also a cell
shorting (bypass) frame that the crane sets over a cell to take it out of the circuit.

**Current path:** rectifier (+) → row D east end → west along D → crossover D–C (west end) →
east along C → crossover C–B (east end) → west along B → crossover B–A (west end) → east along A →
rectifier (−).

Built in Blender 5.2.2, metres, Z up, tankhouse coordinates (lines up with SM_TankhouseBuilding).
Files: `SM_RectifierBusbar.blend`, `SM_RectifierBusbar.fbx` (FBX_SCALE_NONE). Previews: `Preview_Yard.png`,
`Preview_RowEnds.png`, `Preview_House.png` (house shell hidden).

## Layout

| Part | Position |
|---|---|
| Rectifier house | x 44.0 to 60.0, y 15.3 to 20.5, 6.0 m high, against the hall's north wall |
| Rectifier transformers (2) | centres (48.5, 23.5) and (55.5, 23.5), in a bund with a firewall between them |
| Main DC bus (+) | x 57.0, z 3.0: from the house through the north wall, south along the east aisle to y 9.45, west to the row D end bus at x 53.00 |
| Main DC bus (−) | x 58.0, z 3.0: same route to y -9.45 (row A end) |
| West end bars | x 0.0 on an end support block, one per row |
| East end | cell 39's own intercell bar at x 52.80, with an end support block under its capping board overhang |
| Row end bus (under each row end) | x -0.20 (west) and 53.00 (east), centre z 0.24, fed by 5 flexible connectors from the end bar |
| Crossovers | D–C and B–A at x -0.20; C–B at x 53.00; on insulator stands from the basement floor |

## Connection points

| Point | Position |
|---|---|
| HV cable entry, transformer at x 48.5 | (49.55, 24.80, 0.10) |
| HV cable entry, transformer at x 55.5 | (56.55, 24.80, 0.10) |

## Parts and pivots

| Object | Use |
|---|---|
| RB_RowEnds | end supports, end bars, flexible connectors, end bus, crossovers |
| RB_MainBus | overhead DC bus, supports, wall sleeves |
| RB_RectifierHouse | shell; hide for interior views |
| RB_Rectifiers | 2 × 6 thyristor cubicles, cooler skids, DC isolators and shunt, control panel |
| RB_Transformers | transformers, bund, firewall, HV cable boxes, LV bus ducts |
| RB_ShortingFrame | movable (crane). Modelled over cell B20. Place over cell i at (cell x, row y, 0.85). Its copper bars clamp onto the intercell bars on both sides of the cell |

| Object | Pivot |
|---|---|
| RB_MainBus | (0.00, 0.00, 0.00) |
| RB_RectifierHouse | (0.00, 0.00, 0.00) |
| RB_Rectifiers | (0.00, 0.00, 0.00) |
| RB_RowEnds | (0.00, 0.00, 0.00) |
| RB_ShortingFrame | (27.06, -3.15, 0.85) |
| RB_Transformers | (0.00, 0.00, 0.00) |

## Electrical sizing (my estimates)

| Item | Value | Status |
|---|---|---|
| Cell current | about 30 kA | Inference in the research file: 45 cathodes × 2 faces × about 1 m² × 300 A/m² |
| Cell voltage | 0.25–0.3 V | Sourced |
| Circuit voltage | 160 cells × 0.30 V = 48 V, plus bus losses → about 55 V DC | Calculated |
| Rectifier rating | 2 units × 15–18 kA, about 1.7 MW in total | Estimated (no kA ratings found for real units) |
| Bus section | 4 copper bars 250 × 25 mm per pole (25,000 mm², about 1.2 A/mm²) | Estimated (common design current density for copper bus) |
| Transformer size, house size, bus height | | Estimated |
| Shorting frame | | Own design (real refineries use bypass frames/switches; no drawing found) |

Sources: research companion §8 (cell voltage, current density, rectifier references: ABB and GE
Vernova brochures, no ratings); WO2012114176A1 (busbar).
