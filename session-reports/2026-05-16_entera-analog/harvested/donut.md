# donut

- **URL:** https://github.com/clovaai/donut
- **Категория:** Invoice/Receipt parsing (OCR-free document understanding)
- **Stars:** ~6.9k
- **Last commit:** 2022-07-20 (последний релиз 1.0.9 — ноябрь 2022)
- **License:** MIT
- **Описание:** OCR-free document understanding transformer от Naver/Clova. CORD-receipt: 91.3% точности. ECCV 2022.

## Зачем смотрели
Образец «invoice-specific» подхода через VLM. CORD-датасет — стандарт для receipt parsing.

## Оценка
- **Подходит?** Нет
- **Сильные стороны:**
  - MIT
  - OCR-free — модель сразу выдаёт JSON, без отдельного OCR-шага
  - Хорошая точность на receipts (CORD 91.3%)
- **Слабые стороны / риски:**
  - **3+ года без обновлений** (последний релиз ноябрь 2022)
  - Архитектура устарела по сравнению с Qwen2.5-VL/InternVL — современные VLM лучше zero-shot
  - Требует fine-tune под формат каждого типа документа — не подходит для разнообразия УПД
  - Не оптимизирован под inference (нет квантования)
- **Решение:** **Отбросили.** Концепция «OCR-free через VLM» жива, но реализация устарела — лучше брать современную Qwen2.5-VL и промптить, чем fine-tune'ить Donut.
