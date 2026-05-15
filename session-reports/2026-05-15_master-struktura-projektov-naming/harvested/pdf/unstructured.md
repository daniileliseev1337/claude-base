# unstructured (Unstructured-IO/unstructured)
- URL: https://github.com/Unstructured-IO/unstructured
- Stars: 14700
- Last commit: 2026-05-13
- License: Apache-2.0
- Описание: Open-source ETL — превращение документов любых форматов в structured данные для LLM.

## Зачем смотрели
Layout-aware PDF extraction, multi-format pipeline, продакшен-качество, MIT-семейство лицензий.

## Оценка
- Подходит для нашей проблемы? **Да** для общего пайплайна / **Под условием** для нашего конкретного кейса с кривыми.
- Сильные стороны:
  - **Apache-2.0**.
  - `partition_pdf` поддерживает strategy={fast, hi_res, ocr_only} — гибко.
  - hi_res использует layout detection model (yolox/detectron2).
  - Table enrichment в enterprise-версии.
  - Активный разработчик, 14.7к ★.
- Слабые стороны / риски:
  - Tesseract по умолчанию для OCR — наш текущий блокер (нет в системе).
  - Тяжёлые зависимости (detectron2 на Windows бывает проблемным).
  - Engineering drawings и текст в кривых не упомянуты.
- Решение: **держим в уме**. Для нашего pipeline есть более легковесные варианты (pdfplumber + PaddleOCR). Unstructured пригодится если будем строить enterprise document ingestion.
