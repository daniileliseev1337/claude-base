---
name: pdf-stamp-pipeline
description: |
  Массовая замена основной надписи (штампа) в PDF проектной документации — batch
  overlay через pdfcpu + pikepdf на томе из десятков/сотен листов. Один штамп
  заменить другим во всём томе (новый шифр/подписи/изменения). НЕ для удаления
  отдельного объекта (→ Inkscape) и НЕ для перерисовки нанесённой разметки (→ SVG).

  Триггеры:
  - «обновить штампы в томе», «поменять основную надпись», «массовая замена штампа»
  - «прошить шифр по всем листам», «единый штамп на том», «штамп на N листов»
  - «pdfcpu», «overlay PDF», «batch stamp PDF»
  - «убрать старый штамп из text-слоя pypdf-сборки»
---

# pdf-stamp-pipeline

## Когда подключаться

Том PDF собран (часто через pypdf) → нужно заменить основную надпись (ГОСТ Р 21.101
форма 3/5) на актуальную **во всём томе** (десятки-сотни листов). Текущая боль:
5 скриптов + Acrobat на лист = нерабочий процесс для тома. Этот скилл — 1 команда,
~1.3 сек/лист.

**⚠ Сначала выбери метод — таблица в `tools/method_decision.md`.** Этот скилл —
только для МАССОВОЙ ЗАМЕНЫ ШТАМПА (overlay). Для других задач правки PDF — другие методы.

## Decision: какой метод правки PDF (короткая версия)

| Задача | Метод | Где |
|---|---|---|
| **Массовая замена штампа на томе** (новый поверх старого) | **pdfcpu + pikepdf** | ← этот скилл |
| Удалить/подвинуть ОДИН объект в вектор-PDF (1 файл) | Inkscape (GUI, verified) | [[reference_inkscape_pdf_editing]] |
| Физически вырезать старое содержимое (clip-path) | pikepdf clip-path | [[anti-patterns]] §A3.5 |
| Перерисовать нанесённую разметку (CCTV/СС/ЭО) | SVG-PyMuPDF / autocad-mcp | [[reference_autocad_pdf_svg_markup]] |
| Перекрасить аннотации (облачка) | pikepdf `/Annots` | [[pdf-helper]] |

Полная таблица с критериями выбора — `tools/method_decision.md`.

## Зависимости (per-machine)

- **pdfcpu** (Apache-2.0, single-binary 20 MB) в `~/.claude/bin/pdfcpu/` — ставится
  вручную (release-zip с GitHub, bypass proxy). **Backlog: добавить в setup-extras manifest.**
- **pikepdf** (pip, стандартный).
- **PyMuPDF** (fitz, pip).
- **MS Word / LibreOffice** (опц.) — docx-шаблон штампа → PDF.

```powershell
# Установка pdfcpu (один раз на ПК):
$bin = "$HOME\.claude\bin\pdfcpu"
$url = "https://github.com/pdfcpu/pdfcpu/releases/download/v0.12.1/pdfcpu_0.12.1_Windows_x86_64.zip"
$env:HTTPS_PROXY=""  # bypass (см. anti-patterns A4.5)
# Invoke-WebRequest $url -OutFile "$env:TEMP\pdfcpu.zip"; Expand-Archive ... -Dest $bin
```

## Pipeline — 3 стадии (см. `tools/Replace-TitleBlock.ps1`)

Порядок критичен (выстрадан Acrobat-инцидентом 2026-05-25):

**Стадия 1 — pikepdf: collapse content streams в Form XObject.**
pypdf-сборка оставляет N content streams со всеми историческими штампами. Оставляем
`stream[0]` (схемы + боковая шкала), оборачиваем в Form XObject (изолирует graphics
state по PDF 1.7 §8.10 — несбалансированные `q` не утекают, нет stack underflow в
Acrobat). Удаляем legacy XObject'ы (`/fzFrm0`, `/fullpage`).

**Стадия 2 — pdfcpu overlay нового штампа.**
```
pdfcpu stamp add --mode pdf "stamp.pdf" "pos:full, scale:1.0 abs, rot:0" cleaned.pdf stamped.pdf
```
Параметры критичны: `pos:full` (full-page, не badge в углу), `scale:1.0 abs`
(absolute, без масштабирования), `rot:0` (иначе дефолт 25° для image-stamps).

**Стадия 3 — PyMuPDF clean: фикс Type1-шрифтов для Acrobat.**
```python
fitz.open(stamped).save(out, garbage=4, clean=True, deflate=True, deflate_fonts=True)
```
pypdf-сборки тащат Type1-шрифты без `/FirstChar`/`/Widths`/`/FontDescriptor` →
`pdfcpu validate --mode relaxed` прощает, но **Acrobat бросает «Ошибка на этой странице»**.
PyMuPDF garbage=4+clean нормализует font dictionaries (strict-validate проходит).

## Верификация (обязательно, на ВСЕХ листах — A9.4)

- `pdfcpu validate --mode strict` — проходит.
- **text-слой**: старый шифр/ФИО НЕ ищутся (`pdf_search`), новые — есть.
- **Рендер всех листов** (не 3 удобных) — штамп на месте, имена не обрезаны, рамка цела.
- Размер не взлетел; Acrobat открывает без диалога ошибки.
- Спавнить агента [[pdf-reviewer]] на итоговый том.

## Ограничения / backlog

- pdfcpu **не удаляет** старый штамп — это стадия 1 (pikepdf), неизбежна.
- Дорисовка рамки штампа — пока ручной этап (или PyMuPDF `draw_rect` как 4-я стадия).
- **Генератор `stamp.pdf` по параметрам** (шифр/лист/дата) — TODO (`tools/stamp_generator.py`,
  заготовка). Альтернатива — AcroForm-маршрут (PyPDFForm `fill({...})`), разовая работа.
- Шаблоны ГОСТ форм (`templates/form3_full.docx`, `form5_short.docx`) — добавить при наличии.

## Связанные методы (НЕ дублировать — выбор по decision-таблице)

- [[reference_inkscape_pdf_editing]] — удалить/подвинуть объект (verified).
- [[reference_autocad_pdf_svg_markup]] / [[reference_autocad_pdf_overlay_mcp]] — разметка.
- [[anti-patterns]] §A3.5/A3.6 — почему redaction/content-stream surgery провальны.
- [[pdf-helper]] — общая методология PDF (содержит триггеры массовой замены штампа).

## Источник

feedback `2026-05-25_pdf-stamp-pipeline` (R-090226727A) — harvest (pdfcpu 8650★ Apache
выбран из 6 кандидатов) + рабочий прототип. Эволюция: `2026-05-22_ahp-stamp-overlay`
(провал ручного подхода) → harvest → этот pipeline (~1.3 сек/лист vs ~10 мин с Acrobat).
