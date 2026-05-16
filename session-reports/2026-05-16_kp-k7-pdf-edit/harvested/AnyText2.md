# AnyText2 (tyxsspa/AnyText2)

- **URL:** https://github.com/tyxsspa/AnyText2
- **Stars:** 194
- **License:** Apache-2.0
- **Last commit:** 2025-03-01 (release code+checkpoint+dataset)
- **Описание:** Развитие AnyText: customizable per-line text attributes (font/color/size). Extract font+color from scene image и применять к новому тексту.

## Зачем смотрели

Тот же сценарий что AnyText — визуально совпадающая вставка «-20%» в скан КП.

## Оценка

- **Подходит?** Под условием (если бы у нас был CUDA-GPU и подтверждена Cyrillic поддержка)
- **Сильные стороны:**
  - +9.3% text accuracy для English vs AnyText
  - "Per-line attribute customization" — теоретически можно задать тот же шрифт что в скане
  - Apache 2.0 — можно интегрировать
- **Слабые стороны:**
  - Те же GPU/setup требования что AnyText
  - 194 stars — нишевый, mainstream ещё не подтвердил
  - Cyrillic-evaluation отсутствует в paper
- **Решение:** Отложен. При появлении задачи "много разных правок текста на разных сканах" можно вернуться.
