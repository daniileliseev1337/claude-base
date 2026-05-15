# pypdfium2
- URL: https://github.com/pypdfium2-team/pypdfium2
- Stars: 767
- Last commit: 2026-05-04 (v5.8.0)
- License: Apache-2.0 / BSD-3-Clause (двойная)
- Описание: ABI-level Python bindings для PDFium (Google) — рендеринг, инспекция, манипуляция, создание PDF.

## Зачем смотрели
Альтернативный движок рендеринга на случай если PyMuPDF не справится; либеральная лицензия (vs AGPL у PyMuPDF).

## Оценка
- Подходит для нашей проблемы? **Да** (особенно для region rendering и лицензионно чистого решения).
- Сильные стороны:
  - **Apache 2.0 / BSD-3** — без AGPL-проблем.
  - PDFium = тот же движок, что в Chrome → высокое качество рендеринга.
  - Поддержка region rendering (clip rect при render).
  - Region text extraction (left/bottom/right/top).
  - Кросс-платформенный (Windows, без админ-прав через pip wheels).
  - Нет жёсткого лимита dimensions.
- Слабые стороны / риски:
  - Низкоуровневая обёртка — без table extraction и layout-analysis из коробки.
  - Меньше «батареек» чем PyMuPDF.
  - Меньше комьюнити (767 ★ vs 9.7к).
- Решение: **используем** как лицензионно чистую замену PyMuPDF для render-региона, если AGPL станет блокером. Иначе — держим в уме как fallback.
