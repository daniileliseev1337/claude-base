# Graph Report - .  (2026-06-08)

## Corpus Check
- 1 files · ~1,257 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 46 nodes · 89 edges · 7 communities
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Ведомости, схемы, инвариант ПВ-ВСО-ВОР-ИС|Ведомости, схемы, инвариант ПВ-ВСО-ВОР-ИС]]
- [[_COMMUNITY_Акты и состав тома|Акты и состав тома]]
- [[_COMMUNITY_Документы качества|Документы качества]]
- [[_COMMUNITY_Каркас тома и нумерация листов|Каркас тома и нумерация листов]]
- [[_COMMUNITY_Замечания ТН и нормы|Замечания ТН и нормы]]
- [[_COMMUNITY_Орг.часть приказы и СРО|Орг.часть: приказы и СРО]]
- [[_COMMUNITY_Сообщество 6|Сообщество 6]]

## God Nodes (most connected - your core abstractions)
1. `Документ качества` - 13 edges
2. `Акт (общий)` - 11 edges
3. `Исполнительная схема (ИС)` - 9 edges
4. `Позиция (оборуд./материал)` - 9 edges
5. `ВСО (вед. смонтир. оборудования)` - 8 edges
6. `Замечание ТН` - 8 edges
7. `Требования заказчика (! Требования к ИД)` - 8 edges
8. `Том ИД` - 7 edges
9. `Предъявительская ведомость (ПВ)` - 7 edges
10. `Каскад изменений` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Комплект акта` --содержит--> `ВСО (вед. смонтир. оборудования)`  [INFERRED]
  Обучение составления ИД.md → Обучение составления ИД.md  _Bridges community 2 → community 0_
- `Каскад изменений` --охватывает--> `Акт (общий)`  [INFERRED]
  Обучение составления ИД.md → Обучение составления ИД.md  _Bridges community 1 → community 0_
- `Инвариант: ПВ ≡ ВСО ≡ ВОР ≡ ИС` --связывает--> `Исполнительная схема (ИС)`  [INFERRED]
  Обучение составления ИД.md → Обучение составления ИД.md  _Bridges community 3 → community 0_
- `Не выдумывать; артикул по каталогу` --применяется_к--> `Позиция (оборуд./материал)`  [INFERRED]
  Обучение составления ИД.md → Обучение составления ИД.md  _Bridges community 0 → community 6_
- `Унификация по строениям` --применяется_к--> `Документ качества`  [INFERRED]
  Обучение составления ИД.md → Обучение составления ИД.md  _Bridges community 4 → community 0_

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Цепочка доказательства** — zhurnal_rabot, akt, is_detail, reestr_n, dok_kachestva, pv, vso [EXTRACTED 1.00]
- **Каскад изменений** — akt, reestr_n, vor, vso, pv, reestr_opis, is_detail [EXTRACTED 1.00]
- **Инвариант согласованности ПВ-ВСО-ВОР-ИС** — pv, vso, vor, is_detail [EXTRACTED 1.00]
- **Состав комплекта акта** — akt, vso, reestr_n, is_detail, dok_kachestva [EXTRACTED 1.00]
- **Порядок монтажа (п.7 разрешает следующий)** — akt_aosr, akt_aomr, akt_aousito [EXTRACTED 1.00]

## Communities (7 total, 0 thin omitted)

### Community 0 - "Ведомости, схемы, инвариант ПВ-ВСО-ВОР-ИС"
Cohesion: 0.44
Nodes (9): Инвариант: ПВ ≡ ВСО ≡ ВОР ≡ ИС, Каскад изменений, Позиция (оборуд./материал), Предъявительская ведомость (ПВ), Разрыв: неполная ВСО/схема, Спецификация РД/СО, Унификация по строениям, ВОР (вед. объёмов работ) (+1 more)

### Community 1 - "Акты и состав тома"
Cohesion: 0.43
Nodes (8): Акт (общий), АОМР (монтаж оборудования), АОСР (скрытые работы), АОУСИТО (главный акт), Грунтовка на оцинковке не нужна, Общие схемы (АОУСИТО), Протоколы испытаний, Требования заказчика (! Требования к ИД)

### Community 2 - "Документы качества"
Cohesion: 0.32
Nodes (8): Двусторонняя печать / нумерация листов, Комплект акта, Пересборка PDF в конце, Реестр №X (приложение к акту), Общий Реестр-опись, Титульный лист, Том ИД, Общий журнал работ

### Community 3 - "Каркас тома и нумерация листов"
Cohesion: 0.33
Nodes (7): Data Link (ушли от него), Факт первичен, Исполнительная схема (ИС), Разрыв: документ не соответствует факту, Разрыв: нет акта/документа, Разрыв: схема без длин/арматуры, Замечание ТН

### Community 4 - "Замечания ТН и нормы"
Cohesion: 0.38
Nodes (7): Декларация ЕАЭС, Документ качества, Гарантийный талон, Информационное письмо, Отказное письмо, Паспорт / РЭ / инструкция, Сертификат соответствия (СС)

### Community 5 - "Орг.часть: приказы и СРО"
Cohesion: 0.50
Nodes (4): Орг.часть (приказы + СРО), Приказ о назначении, Разрыв: реквизиты, Выписка СРО

### Community 6 - "Сообщество 6"
Cohesion: 0.67
Nodes (3): Не выдумывать; артикул по каталогу, Норма (СП/ГОСТ/Постановление), Разрыв: нормативная ссылка в акте

## Knowledge Gaps
- **6 isolated node(s):** `Выписка СРО`, `Титульный лист`, `Общие схемы (АОУСИТО)`, `Паспорт / РЭ / инструкция`, `Отказное письмо` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Документ качества` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.320) - this node is a cross-community bridge._
- **Why does `Акт (общий)` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **Why does `Требования заказчика (! Требования к ИД)` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Исполнительная схема (ИС)` (e.g. with `Data Link (ушли от него)` and `Факт первичен`) actually correct?**
  _`Исполнительная схема (ИС)` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Позиция (оборуд./материал)` (e.g. with `Не выдумывать; артикул по каталогу` and `Унификация по строениям`) actually correct?**
  _`Позиция (оборуд./материал)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ВСО (вед. смонтир. оборудования)` (e.g. with `Инвариант: ПВ ≡ ВСО ≡ ВОР ≡ ИС` and `Каскад изменений`) actually correct?**
  _`ВСО (вед. смонтир. оборудования)` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Выписка СРО`, `Титульный лист`, `Общие схемы (АОУСИТО)` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._