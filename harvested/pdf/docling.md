# docling (DS4SD/docling)
- URL: https://github.com/DS4SD/docling
- Stars: 59800
- Last commit: 2026-05-07 (v2.93.0)
- License: MIT
- Описание: IBM Research-проект для подготовки документов под gen-AI: PDF, DOCX, PPTX → structured + markdown с layout/tables/reading-order.

## Зачем смотрели
Современный layout-aware extractor (60к ★, MIT), потенциальная замена markitdown для PDF.

## Оценка
- Подходит для нашей проблемы? **Да** для нормальных текстовых PDF / **Нет** для текста в кривых без OCR.
- Сильные стороны:
  - **MIT**.
  - Поддержка PDF layout-analysis: чтение по столбцам, reading order, table structure.
  - Extensive OCR для сканов.
  - От IBM Research — продакшен качество.
  - Активная разработка (172 релиза).
  - 60к ★ — топ в нише.
- Слабые стороны / риски:
  - Russian OCR не явно задокументирован — нужен тест.
  - Engineering drawings — не упомянуты явно.
  - Тяжёлая зависимость (PyTorch + models).
- Решение: **используем** как современную замену markitdown для PDF пояснительных записок и многоколоночных текстовых документов. Для нашего проблемного PDF со схемой ЛВС — попробуем в OCR-режиме (render → docling.ocr).
