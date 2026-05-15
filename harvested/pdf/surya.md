# surya (datalab-to/surya)
- URL: https://github.com/datalab-to/surya
- Stars: 19739
- Last commit: 2026-05-06 (v0.17.1, 2026-01-31)
- License: **GPL-3.0** (флаг — вирусная лицензия)
- Описание: OCR, layout analysis, reading order, table recognition на 90+ языках (включая русский).

## Зачем смотрели
Современный transformer-based OCR с reading-order detection и layout-analysis в одном пакете.

## Оценка
- Подходит для нашей проблемы? **Под условием** (лицензия GPL — флаг).
- Сильные стороны:
  - 90+ языков включая русский.
  - Layout analysis + reading order + table recognition + OCR — всё в одном.
  - CPU-режим работает (auto-detect torch device).
  - pip install surya-ocr.
  - Используется внутри Marker (35к ★).
- Слабые стороны / риски:
  - **GPL-3.0** — вирусная лицензия. Согласно нашим правилам (CLAUDE.md → Harvest-workflow): «GPL — флаг для согласования», в скиллы/агенты НЕ берём. Можно использовать как отдельный CLI-инструмент в нашей среде.
  - Рекомендованный max width — 2048 px. Для A2 в высоком dpi нужен tiling.
  - Тяжёлый install (transformers + torch).
- Решение: **держим в уме** как отдельный standalone-инструмент. В нашу базу (`skills/agents`) не интегрируем из-за GPL.
