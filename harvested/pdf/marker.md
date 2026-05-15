# marker (VikParuchuri/marker)
- URL: https://github.com/VikParuchuri/marker
- Stars: 35100
- Last commit: 2026-01-31 (v1.10.2)
- License: **GPL-3.0** (флаг)
- Описание: Конвертация PDF → Markdown + JSON с высокой точностью, multi-language (на базе Surya OCR).

## Зачем смотрели
Топ-инструмент по PDF→Markdown качеству на 2026. Заявлен 93.92% accuracy на категории «Engineering document».

## Оценка
- Подходит для нашей проблемы? **Под условием** (лицензия GPL).
- Сильные стороны:
  - 93.92% heuristic score на engineering-документах — заявленно лучше всех альтернатив.
  - Использует Surya внутри → 90+ языков, включая русский.
  - Markdown + JSON выход.
  - Активно поддерживается.
- Слабые стороны / риски:
  - **GPL-3.0** — те же ограничения, что у surya.
  - Region rendering / A2 — не описано явно.
  - Тяжёлая зависимость (Surya + transformers).
- Решение: **держим в уме** как standalone CLI вне нашей базы. В наши скиллы/агенты не интегрируем из-за GPL.
