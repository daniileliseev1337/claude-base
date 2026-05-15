# PlantUML + nwdiag + C4-PlantUML + Cisco-sprites

- **plantuml/plantuml:** https://github.com/plantuml/plantuml — 13k stars, GPL-3/LGPL-3/Apache/EPL/MIT (multi-license), v1.2026.3 от 8 May 2026 (актив).
- **PlantUML nwdiag:** встроено в PlantUML — https://plantuml.com/nwdiag — сетевые диаграммы из текста.
- **plantuml-stdlib/C4-PlantUML:** https://github.com/plantuml-stdlib/C4-PlantUML — 7.3k stars, MIT, актив.
- **plantuml-stdlib (Cisco):** https://github.com/plantuml/plantuml-stdlib — официальная stdlib, есть AWS/Azure/K8s; **Cisco-sprites не в core**, но есть community sprites через `<$sprite>` синтаксис.

## Применимость к нашей задаче

- **Плюсы:**
  - Декларативный текст — компактно, версионируется в git.
  - `nwdiag`-синтаксис специально для network: `network N1 { switch1; pc1; pc2; }` — рисует «шину» с подключёнными узлами.
  - Можно генерить .puml из xlsx (Python — простой шаблонизатор).
  - SVG/PNG/PDF.
  - Лицензии: для использования как инструмента — без проблем (Java-бинарь LGPL).
- **Минусы:**
  - **nwdiag в PlantUML не такой богатый** как отдельный nwdiag (см. отдельную заметку) — но интегрирован.
  - Cisco-иконки — нужно подгружать sprites из community-репо отдельно.
  - **Group layout** есть (через `cloud`/`rectangle`/`frame`), но для 200 узлов выйдет каша без ручного позиционирования.
  - Штампа ГОСТ нет.

## Лицензия

PlantUML использовать как утилиту — OK (multi-license, можно выбрать LGPL/MIT/Apache). **GPL остаётся флагом** — если будем брать исходники PlantUML и модифицировать, придётся выбирать совместимую лицензию.

## Сценарий

Для small/medium схем (до ~50 узлов) — отличный быстрый вариант. Для наших 200 шкафов — менее удобен, чем `mingrammer/diagrams` + Graphviz cluster или drawio CSV-import.
