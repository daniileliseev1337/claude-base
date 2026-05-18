# Harvest summary — 2026-05-18 PDF→Excel pipeline

## Сравнительная таблица

| # | Источник | Имя | Stars | Last commit | License | Краткое описание | Решение |
|---|----------|-----|-------|-------------|---------|------------------|---------|
| 1 | GitHub | [0xabu/pdfannots](https://github.com/0xabu/pdfannots) | ~700 | активный | MIT | Извлекает PDF-аннотации (Acrobat-комментарии) в md/json с координатами | Держим в уме для PDF с реальными аннотациями |
| 2 | GitHub | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | ~7k | активный | MIT | Plumb-уровень доступ к PDF: chars/lines/rects/annots/tables | Держим как fallback к pdf-mcp |
| 3 | PyPI | [xls2xlsx](https://pypi.org/project/xls2xlsx/) | ~30 | 2022 | MIT | Pure-Python xls→xlsx без Excel/LibreOffice | Fallback если нет Excel |

## Рекомендация по этой задаче

**Своими средствами справились** — `pdf-mcp` (pdf_read_all + pdf_render_pages) + `openpyxl` + `pywin32` дали полный pipeline:
1. PDF → текст + визуал (определили какие пометки к каким позициям).
2. .xls → .xlsx (Excel COM).
3. xlsx → точечная правка ячеек (openpyxl).

Harvest-кандидаты не подключали потому что:
- pdfannots — наш PDF имеет text-layer пометки, не Acrobat-аннотации.
- pdfplumber — pdf-mcp справился, координаты не нужны были (визуальный рендер достаточен).
- xls2xlsx — Excel COM работал.

## Что взять в общую базу (`~/.claude/harvested/`)

- **pdfplumber.md** — пригодится для следующих PDF-задач с таблицами / annotations с координатами.
- **xls2xlsx.md** — пригодится если попадёт `.xls` на ПК без Excel.

Переношу обе после согласования с пользователем (по правилу — копировать в общую базу только осознанно).
