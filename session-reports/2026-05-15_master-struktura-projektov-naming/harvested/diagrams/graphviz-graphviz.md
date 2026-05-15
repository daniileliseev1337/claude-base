# graphviz (core) + xflr6/graphviz (Python bindings)

- **URL core:** https://gitlab.com/graphviz/graphviz (GitHub repo `graphviz/graphviz` — archived/empty stub)
- **URL python:** https://github.com/xflr6/graphviz
- **License:** EPL 2.0 (core), MIT (python wrapper)
- **Stars (python wrapper):** 1.8k
- **Описание:** Граф-визуализация на DOT-языке. Layouts: `dot` (иерархический), `neato` (spring), `fdp`, `sfdp`, `circo`, `twopi`.

## Применимость к нашей задаче

- **Плюсы:**
  - Golden standard, под капотом у `mingrammer/diagrams`, `pyvis`, `pydot`, `networkx`.
  - `subgraph cluster_*` — группировки = объект/этаж/сеть.
  - HTML-like labels — можно собрать «прямоугольник со списком оборудования внутри» (label-таблица).
  - SVG/PNG/PDF из коробки.
- **Минусы:**
  - DOT-язык низкоуровневый, для 200 узлов писать руками — нет; генерим из Python.
  - Сам по себе нет иконок Cisco/HP — нужны внешние PNG/SVG.
  - **GOST/штамп — нет**, постпроцессинг.
- **Сценарий:** база, если строим свой генератор. Но `mingrammer/diagrams` обёртка удобнее.

## Лицензия (EPL 2.0)

Бинарь Graphviz — EPL 2.0. Это не GPL, но и не MIT — copyleft слабого типа. Использование как утилиты (CLI) — без ограничений; модификация исходников требует публикации модификаций. Для нас — **зелёный свет** (юзаем как инструмент).
