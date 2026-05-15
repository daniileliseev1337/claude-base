# mingrammer/diagrams

- **URL:** https://github.com/mingrammer/diagrams
- **Stars:** 42.3k
- **Last commit / release:** v0.25.1 — 22 Nov 2025 (актив)
- **License:** MIT (зелёный)
- **Lang:** Python 95%
- **Описание:** Diagram-as-code для прототипирования cloud-архитектур (AWS/Azure/GCP/K8s/On-Premise/SaaS). Поверх Graphviz.

## Применимость к нашей задаче (xlsx 200 шкафов → СКС-схема)

- **Плюсы:**
  - Готовый набор `Cluster`-группировок — идеально ложится на «по объектам / по этажам».
  - Иконки для networking: `Switch`, `Router`, `Firewall`, `Server`, `Storage`, `Rack` — есть в `diagrams.onprem.network`, `diagrams.generic.network`.
  - Прямоугольники с подписями = нативное поведение (`Node(label="Шкаф-12, пом.305")`).
  - Линии связи с метками: `node1 >> Edge(label="VLAN 100") >> node2`.
  - Из xlsx → Python loop → diagram: легко, мы уже на Python.
- **Минусы:**
  - Layout полностью на Graphviz — для 200 узлов на одном листе будет каша; нужно бить на под-диаграммы по объектам/этажам.
  - **Нет** штампа ГОСТ и форматной рамки — это потом в Visio/draw.io вручную или постпроцессингом.
  - Экспорт: PNG, SVG, PDF, JPG. Visio/drawio — нет.
- **Сценарий:** генерим PNG/SVG per-object/per-floor, склеиваем в PDF-альбом, штамп ГОСТ накладываем отдельно (например, через reportlab или Visio-шаблон).

## Безопасность

- Open-source, MIT, 42k stars, активный. Можно использовать. Зависимость — `graphviz` бинарь (`dot`).
