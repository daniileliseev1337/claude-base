# Harvest: инструменты для физического удаления штампов из PDF

**Дата:** 2026-05-27
**Контекст:** АХП Балашиха — перезамена 53+ штампов в томе ПД. Текущий
стек (PyMuPDF redact + pdfcpu stamp) оставляет линии таблицы старого
штампа и не очищает поля «Нов. 44-26» — пользователь матерился
повторно. Нужен инструмент с **физическим удалением vector graphics**.

## Сравнительная таблица

| # | Источник | Имя | Stars | License | Подходит |
|---|----------|-----|-------|---------|----------|
| 1 | GitHub | **pikepdf/pikepdf** | 2.6k | MPL-2.0 | ✅ ИДЕАЛЬНО (на базе qpdf) |
| 2 | GitHub | qpdf/qpdf (Berkenbilt) | 4k+ | Apache 2.0 | ✅ хорошо |
| 3 | mupdf.com | mutool clean | — | AGPL | ⚠ AGPL риск installer |
| 4 | GitHub | pymupdf/PyMuPDF | 6k+ | AGPL | ❌ **НЕ УМЕЕТ удалять shapes** (подтв. разработчиком) |
| 5 | GitHub | Profhameed/pdf-object-remover | 2 | MIT | ❌ desktop GUI only |
| 6 | sourceforge | pdf2svg + Inkscape | — | LGPL | ⚠ растеризация vector |
| 7 | ghostscript.com | Ghostscript | — | AGPL | ⚠ переписывает структуру |

## Ключевое открытие

В sample_p14_LogicalScheme.pdf (AutoCAD pdfplot15.hdi) **штамп лежит
как отдельный XObject Form `/Fm0`** с BBox = ГОСТ форма 3
(518×157pt = 183×55мм). Это значит:

- НЕ нужно сложное content stream surgery
- НЕ нужен redact (PyMuPDF не умеет)
- Достаточно: `del page.Resources.XObject['/Fm0']` + убрать
  `/Fm0 Do` из content stream

## Рекомендация

**pikepdf XObject removal** — самый простой и надёжный путь для
АутоКАД-PDF, где штамп = Form XObject.

Fallback (если на других страницах штамп не отдельный XObject) —
qpdf --qdf + Python content stream surgery.

## Связано

- [[2026-05-22_ahp-stamp-overlay-session-failure]] — Claude v6-v11 fails
- [[feedback-stamp-no-white-fill]] — hard rule запрет на заливки

## Ссылки

- https://github.com/pikepdf/pikepdf
- https://qpdf.readthedocs.io/en/stable/qdf.html
- https://github.com/pymupdf/PyMuPDF/discussions/2308 (PyMuPDF не умеет)
- https://github.com/Profhameed/pdf-object-remover (GUI only)
