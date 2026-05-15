# redlines (houfu/redlines)

**URL:** https://github.com/houfu/redlines
**Stars:** 156
**Last commit:** 2025-11-24 (v0.6.1)
**License:** MIT
**Поддерживает форматы:** text напрямую; pdf через `redlines[pdf]`; docx — нет (нужен внешний extract)
**Тип:** Python library

## Что делает
Сравнивает две строки/текста и выдаёт diff в виде JSON / Markdown / HTML /
rich-терминала с форматированием «как Track Changes в Word» (вычеркнутый
старый, подчёркнутый новый). Лёгкий, без тяжёлых зависимостей.

## Какой именно diff
- **Текстовый**, paragraph-level по умолчанию; sentence-level через
  опциональный NupunktProcessor.
- Для **docx** работает только в паре с экстрактором (mammoth / python-docx /
  word MCP → передать plain-text сюда).
- Для **pdf** есть опциональный экстра `redlines[pdf]` — встроенный извлекатель
  текста.
- Output Markdown/HTML удобно отправлять обратно пользователю или вставлять
  в отчёт.

## Как подключить
```
pip install redlines
# опционально:
pip install "redlines[pdf]"
pip install "redlines[nupunkt]"
```
Пример:
```python
from redlines import Redlines
diff = Redlines(text_v1, text_v2, markdown_style="red_green")
print(diff.output_markdown)
```

## Подводные камни
- НЕ работает с docx напрямую — только текст. Для docx-сравнения нужно сначала
  достать текст через `word` MCP или mammoth. Это означает потерю
  форматирования и track changes.
- Python 3.10+.
- Не различает удаление абзаца от перестановки — простая diff-логика на основе
  difflib.

## Вердикт
ВЗЯТЬ как лёгкий fallback для текстового diff любого формата
(docx-извлечённый-текст, pdf, plain). Дополняет `adeu` (структурный docx)
и `diff-pdf` (визуальный pdf). MIT, активный, 156 stars.
