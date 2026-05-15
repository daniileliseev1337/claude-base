# diff-pdf-visually (bgeron)

**URL:** https://github.com/bgeron/diff-pdf-visually
**Stars:** 73
**Last commit:** 2025-04-01 (v1.8.1)
**License:** Apache-2.0 / MIT (dual)
**Поддерживает форматы:** pdf (только)
**Тип:** Python library + CLI

## Что делает
Лёгкая Python-обёртка: растеризует обе PDF (pdftocairo) и сравнивает картинки
через ImageMagick `compare`. Не делает попиксельную карту diff — отвечает
на вопрос «есть ли видимая разница» и насколько большая (similarity score),
плюс выдаёт PNG страниц с подсвеченными отличиями.

## Какой именно diff
- **Визуальный**, page-by-page, с порогом чувствительности (PSNR threshold).
- Хорошо подходит для **regression-проверки** («ничего не должно было
  поменяться»), не для глубокого ревью.
- Python API позволяет встроить проверку в наши скрипты:
  ```python
  from diff_pdf_visually import pdf_similar
  is_same = pdf_similar("v1.pdf", "v2.pdf")
  ```

## Как подключить
```
pip install diff-pdf-visually
```
Зависимости (Windows — поставить отдельно):
- ImageMagick (с `compare.exe` в PATH)
- Poppler (`pdftocairo.exe` в PATH)

## Подводные камни
- Внешние бинари **ImageMagick + Poppler** обязательны. На Windows без
  админ-прав — установка через `winget` или portable-сборки, рабочее но
  boilerplate.
- Обе PDF должны иметь одинаковое число страниц и совпадающие размеры.
- Менее детальный вывод, чем у `diff-pdf`: «отличается / нет» + PNG, не
  готовый diff-PDF.
- Apache-2.0 / MIT — лицензионных проблем нет, можно встраивать.

## Вердикт
ЗАПАСНОЙ вариант. Брать если нужен **Python API** (а не CLI как diff-pdf),
например для встраивания в наш agent-проверяльщик `pdf-reviewer`.
Лицензия удобнее чем у diff-pdf (Apache/MIT vs GPL), но 73 stars и
требование внешних бинарей.
