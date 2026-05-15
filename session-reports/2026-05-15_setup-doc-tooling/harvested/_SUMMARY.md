# Harvest: инструменты для редактирования PDF (MCP / Python)

**Дата:** 2026-05-15
**Контекст:** уже подключён `pdf-mcp` (uvx, read-only). Нужны инструменты для **редактирования** PDF (merge/split/forms/annotations/watermarks).

## Сравнительная таблица

| Кандидат | Stars | Last commit | License | Тип | Cloud? | Покрытие задач | Вердикт |
|---|---|---|---|---|---|---|---|
| **rsp2k/mcp-pdf** | 7 | 2026-05-05 | MIT | MCP Python | нет | merge/split/forms/annotations/watermark — всё | ✅ Брать первым (с тестом) |
| **gufao/mcp-server-stirling-pdf** | 1 | 2025-12-18 | **GPL-3.0** | MCP TS + Stirling Docker | нет (но Docker) | merge/split/watermark/OCR, без AcroForm | ⚠️ Только если уже есть Docker |
| **alejandroBallesterosC/document-edit-mcp** | 49 | 2025-11-10 | MIT | MCP Python | нет | только PDF generation, не edit | ❌ Не подходит по задаче |
| **pdfdotco/pdfco-mcp** | 9 | 2025-06-19 | MIT | MCP Python + cloud API | **да, платно** | merge/split/forms/annotations — всё | ⚠️ Запасной для OCR/подписи, не для рутины |
| **pikepdf/pikepdf** | 2 719 | 2026-05-15 | MPL-2.0 | Python lib (не MCP) | нет | merge/split/forms/annotations низкоуровнево | ✅ Fallback: написать свой MCP на нём |

## Отсеянные кандидаты (с причиной)

| Репо | Причина |
|---|---|
| `Sohaib-2/pdf-mcp-server` (14★) | **Нет LICENSE** — код не копировать, как MCP подключить можно но без копирования |
| `Wildebeest/mcp_pdf_forms` (9★) | Last commit 2025-04-01 — на грани 12-месячного фильтра, и читает только |
| `hanweg/mcp-pdf-tools` (74★) | Last commit 2024-12-22 — **17 месяцев тишины**, "WORK IN PROGRESS" в README |
| `knportal/formfill-mcp` (2★) | Stripe + Cloudflare integration — это коммерческий SaaS-врапер, не локальный тул |
| `matsengrp/pdf-navigator-mcp` (8★) | Только form-fill + навигация, без merge/split/annotations |
| `eiceblue/spire-pdf-mcp-server` (2★) | Обёртка над Spire.PDF (коммерческая лицензия с водяными знаками в free версии) |
| `R09722akaBennett/nano-pdf-mcp` (1★) | Требует Gemini 3 Pro API ключ (другой LLM-вендор), отсутствует LICENSE |
| `songminkyu/pdf-filler-recursive-simple-mcp` (1★) | 1 star, нет репутации, узкая задача |

## Честная оценка по фильтру

**Жёсткий фильтр CORE-секции (≥50 stars + last commit <12 мес + ясная лицензия)** проходит **только один** MCP-кандидат — `document-edit-mcp` (49★, MIT), и тот **не подходит по задаче** (только generation).

Поэтому пришлось ослабить «50 stars» до «явная репутация автора / зрелость кодовой базы»:
- **rsp2k/mcp-pdf** прошёл по свежести (10 дней назад) + лицензии + полноте функционала, при низкой популярности
- **pikepdf** прошёл сходу как зрелая библиотека-стандарт

## Рекомендация: что подключить первым

### Путь 1 (быстрая проверка готового MCP) — **rsp2k/mcp-pdf**

```powershell
# 1. Прогрев кэша uvx
uvx mcp-pdf --help

# 2. Если запускается без падений — подключить
claude mcp add pdf-edit uvx mcp-pdf

# 3. Тестовый прогон в Claude Code:
#    - merge двух одностраничных PDF из ~/test/
#    - fill_form на простой AcroForm с одним TextField
#    - add_watermark
#    Если хотя бы 2 из 3 работают — оставить.
```

**Если упадёт** (нет Tesseract/Ghostscript/Java и хардкорные импорты на старте) — переходим к пути 2.

### Путь 2 (свой MCP на pikepdf) — fallback по Karpathy-простоте

Если рынок MCP-серверов для PDF-edit ещё незрелый (что и видим — лучший кандидат 7★), правильнее написать **свой минимальный MCP** на ~150 строк FastMCP + pikepdf под наши 5 реальных операций:

1. `pdf_merge(input_paths, output_path)`
2. `pdf_split(input_path, ranges, output_dir)`
3. `pdf_delete_pages(input_path, pages, output_path)`
4. `pdf_fill_form(input_path, fields_dict, output_path, flatten=False)`
5. `pdf_add_watermark(input_path, watermark_text, output_path)`

Хранить в `~/.claude/mcp-local/pdf-edit/`, подключать через `claude mcp add pdf-edit python -m pdf_edit_server`. Это решение полностью под нашим контролем, лицензионно чистое, без облака и Docker.

### Итог

**1-й приоритет:** протестировать `rsp2k/mcp-pdf` в Sandbox/изолированном venv (1 час работы).
**2-й приоритет** (если 1-й не зашёл): свой 150-строчный MCP на pikepdf + опционально reportlab для оверлеев.
**Запасной:** `pdfco-mcp` держим в уме для разовых задач OCR/подписи, где локальные средства слабы.

`gufao/mcp-server-stirling-pdf` и `document-edit-mcp` — **не рекомендуются** (Docker overhead / нет функционала редактирования соответственно).
