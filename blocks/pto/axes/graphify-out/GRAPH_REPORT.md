# Graph Report - .  (2026-06-22)

## Corpus Check
- Corpus is ~2,175 words - fits in a single context window. You may not need a graph.

## Summary
- 15 nodes · 35 edges · 3 communities
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
- Token cost: 0 input · 72,629 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Рамка ТН и приёмка (Workflow)|Рамка ТН и приёмка (Workflow)]]
- [[_COMMUNITY_Содержательное ядро состав-документы-графика|Содержательное ядро: состав-документы-графика]]
- [[_COMMUNITY_Интеграция акты, пересборка, гейт G-5|Интеграция: акты, пересборка, гейт G-5]]

## God Nodes (most connected - your core abstractions)
1. `Ось Б — Независимый аудит оригинала` - 9 edges
2. `Протокол возврата (кросс-блокеры)` - 8 edges
3. `Ось 3 — Графика ГЧ (DWG)` - 7 edges
4. `Ось 1 — Состав` - 6 edges
5. `Ось 2 — Документы качества` - 6 edges
6. `Ось 4 — Акты (нормоконтроль)` - 6 edges
7. `Ось 5 — Пересборка PDF` - 5 edges
8. `Ось 6 — Финальная приёмка` - 5 edges
9. `Workflow (постраничный fan-out)` - 4 edges
10. `Ось Р — ТН-замечания` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Ось 4 — Акты (нормоконтроль)` --references--> `Гейт G-5 (жёсткий) перед пересборкой`  [EXTRACTED]
  osi_strategy.md → osi_graph_curated.md
- `Ось 5 — Пересборка PDF` --references--> `Гейт G-5 (жёсткий) перед пересборкой`  [EXTRACTED]
  osi_strategy.md → osi_graph_curated.md
- `Гейт G-5 (жёсткий) перед пересборкой` --references--> `Протокол возврата (кросс-блокеры)`  [EXTRACTED]
  osi_graph_curated.md → osi_strategy.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Содержательные оси держат инвариант ПВ≡ВСО≡ВОР≡ИС** — os_1, os_2, os_3, invariant_pv_vso_vor_is [EXTRACTED 1.00]
- **Оси с Workflow по умолчанию или как кандидаты** — os_b, os_4, os_6, workflow_fanout [EXTRACTED 1.00]
- **Конвергенция осей 1-4 до нуля блокеров — условие G-5** — os_1, os_2, os_3, os_4, gate_g5, protokol_vozvrata [EXTRACTED 1.00]

## Communities (3 total, 0 thin omitted)

### Community 0 - "Рамка ТН и приёмка (Workflow)"
Cohesion: 0.53
Nodes (6): Ось 6 — Финальная приёмка, Ось Б — Независимый аудит оригинала, Ось Р — ТН-замечания, Выдача / печать, Скилл id-tom-priemka, Workflow (постраничный fan-out)

### Community 1 - "Содержательное ядро: состав-документы-графика"
Cohesion: 0.80
Nodes (5): Инвариант ПВ ≡ ВСО ≡ ВОР ≡ ИС, Ось 1 — Состав, Ось 2 — Документы качества, Ось 3 — Графика ГЧ (DWG), СВОД факта закупки/монтажа

### Community 2 - "Интеграция: акты, пересборка, гейт G-5"
Cohesion: 1.00
Nodes (4): Гейт G-5 (жёсткий) перед пересборкой, Ось 4 — Акты (нормоконтроль), Ось 5 — Пересборка PDF, Протокол возврата (кросс-блокеры)

## Knowledge Gaps
- **2 isolated node(s):** `Выдача / печать`, `СВОД факта закупки/монтажа`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Ось 6 — Финальная приёмка` connect `Рамка ТН и приёмка (Workflow)` to `Интеграция: акты, пересборка, гейт G-5`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Why does `Ось Б — Независимый аудит оригинала` connect `Рамка ТН и приёмка (Workflow)` to `Содержательное ядро: состав-документы-графика`, `Интеграция: акты, пересборка, гейт G-5`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **What connects `Выдача / печать`, `СВОД факта закупки/монтажа` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._