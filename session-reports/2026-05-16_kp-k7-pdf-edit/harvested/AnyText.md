# AnyText (tyxsspa/AnyText)

- **URL:** https://github.com/tyxsspa/AnyText
- **Stars:** 4 900
- **License:** Apache-2.0
- **Last commit:** активен (нет точной даты в README, но 31 коммит на main, FP16 inference добавлен относительно недавно)
- **Описание:** Diffusion-based multilingual visual text generation/editing (paper ICLR 2024). Поддерживает китайский/английский/японский. Cyrillic — НЕ заявлен.

## Зачем смотрели

Альтернатива vector overlay для замены текста в сканированных PDF (КП К-7, 24 файла). Цель — визуально неотличимая вставка «-20%» в строку «Итоговая сумма (вкл. НДС)» без ручного подбора baseline/кегля.

## Оценка

- **Подходит?** Условно нет (для текущей задачи overkill)
- **Сильные стороны:** Diffusion-модель учитывает font/style/scale контекста; визуальное совпадение лучше чем у любого vector overlay
- **Слабые стороны:**
  - Требует GPU ≥8 GB VRAM (FP16). На моей машине нет CUDA — нужно либо облако, либо CPU inference (минуты на изображение)
  - Cyrillic поддержка не подтверждена; маловероятна для тонких manipulations типа «-20%»
  - Inference ~10 сек/изображение на A100 → 24 файла ≥ 4 минут на сервере (на consumer GPU — десятки минут)
  - Setup overhead: PyTorch + CUDA + ~5 GB модели + Python env
  - Не reproducible (стохастика diffusion)
- **Решение:** Держим в уме для задач "scene text editing с сохранением стиля" общего вида. Для текущей задачи (одна и та же фраза в 24 однотипных файла) проще auto-calibrated vector overlay.
