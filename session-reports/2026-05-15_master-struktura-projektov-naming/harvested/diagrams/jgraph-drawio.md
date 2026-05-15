# jgraph/drawio + drawio-desktop + headless экспорт

- **drawio (web):** https://github.com/jgraph/drawio — 5.4k stars, Apache 2.0, JS.
- **drawio-desktop:** https://github.com/jgraph/drawio-desktop — **61.1k stars**, Apache 2.0, последняя версия 30.0.1 (May 2026). Electron-app + CLI.
- **rlespinasse/drawio-export:** https://github.com/rlespinasse/drawio-export — Docker CLI, MIT, 92 stars. Экспорт recursively в jpg/pdf/png/svg/xml/asciidoc/md.
- **rlespinasse/docker-drawio-desktop-headless:** https://github.com/rlespinasse/docker-drawio-desktop-headless — 65 stars, MIT, актив (v1.60.0 — May 2026). Headless drawio в Docker.
- **jgraph/drawio-tools:** https://github.com/jgraph/drawio-tools — 176 stars, Apache, веб-утилиты в т.ч. **CSV→диаграмма** (важно!).

## Применимость к нашей задаче

- **Плюсы:**
  - **Финальный формат** проектной документации в РФ — часто .vsdx или .drawio (открывают и заказчик, и проектировщик).
  - `drawio-desktop --export` — headless CLI: `drawio -x -f png file.drawio`.
  - **CSV-import** (drawio-tools и сам drawio): из xlsx можно сделать CSV с колонками `id,label,parent,connections` — drawio построит диаграмму. **Самый прямой путь от наших табличных данных.**
  - Огромная библиотека иконок — Cisco, AWS, networking — встроена.
  - Поддерживает группировку (containers/swimlanes) — этажи/объекты.
  - Штамп ГОСТ — можно подложить как фон-картинку или нарисовать в GUI один раз шаблон.
- **Минусы:**
  - Layout без авторазмещения — CSV-import даёт грубое размещение, потом надо допиливать в GUI. Для 200 узлов — час-два ручной работы.
  - Не «pure code» — гибрид: генерим скелет, дорисовываем в GUI.

## Сценарий рекомендованный

1. xlsx → CSV (id, label, parent=объект/этаж, edge to=шкаф-сосед, edge_label=сеть).
2. drawio.com → Extras → Edit Diagram → CSV import (или drawio-tools).
3. Полировка в drawio GUI: автолейаут, штамп ГОСТ из шаблона.
4. Экспорт в SVG/PDF через `drawio-export` (Docker) или drawio-desktop CLI.

## Лицензия

Apache-2.0 — зелёный.
