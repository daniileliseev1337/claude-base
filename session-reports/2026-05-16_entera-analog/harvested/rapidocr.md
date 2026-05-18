# RapidOCR

- **URL:** https://github.com/RapidAI/RapidOCR
- **Категория:** OCR / Document Understanding (легковесный CPU-only)
- **Stars:** ~6.6k
- **Last commit:** 2026-04-11 (v3.8.1)
- **License:** Apache-2.0
- **Описание:** Лёгкий OCR на ONNX Runtime / OpenVINO / MNN / TensorRT — модели от PaddleOCR, портированные для inference без зависимости от PaddlePaddle.

## Зачем смотрели
Хороший fallback на CPU-only машинах. Если бухгалтер обрабатывает 1С на обычном офисном ПК без GPU, MinerU/Surya будут тормозить, а RapidOCR — терпимо.

## Оценка
- **Подходит?** Под условием (как fallback, не основной)
- **Сильные стороны:**
  - **Apache-2.0**
  - Без PaddlePaddle (на ONNX) — намного проще деплой
  - Очень быстрый на CPU
  - Поддержка PP-OCRv5 моделей — те же что у PaddleOCR
- **Слабые стороны / риски:**
  - **Русский явно не указан** в README — поддержка только китайский+английский по умолчанию (другие модели надо отдельно искать в model list); надо проверять качество на кириллице
  - Только OCR (текст из картинки), без layout/table parsing — нужна обвязка
  - Меньше документации, чем у материнского PaddleOCR
- **Решение:** Держим в уме как fallback для CPU-only сценариев. Не основной выбор.
