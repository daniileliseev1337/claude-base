---
date: 2026-05-25
topic: pdf-stamp-pipeline
status: working-prototype-ready
purpose: harvest + прототип для регулярных задач массовой замены штампа основной надписи в PDF проектной документации
---

# PDF Stamp Pipeline — harvest и прототип

## Контекст задачи

После сборки тома проектной документации К-7 через pypdf в PDF возникают две проблемы:
1. **Скрытые слои старых штампов** в text-слое (см. report 2026-05-22): pypdf оставляет N=8 content streams со всеми историческими версиями штампа.
2. **Массовая замена** штампа на актуальный вариант: тысячи листов одного тома, разные подразделы (СТМ.ЭТ, ИОС1.5, …) — нужно один штамп заменить другим **во всём томе**.

Текущий ad-hoc пайплайн в одной сессии:
- pikepdf — удалить старые content streams + Form XObject /fzFrm0+/fullpage
- Word COM — конвертация docx-шаблона в PDF
- PyMuPDF show_pdf_page — overlay нового штампа
- Иногда — ручная правка в Acrobat (ширины ячеек, обрезанные имена)

5 python-скриптов и Acrobat для одного листа. Для тома из 57 листов — нерабочий процесс.

## Harvest 2026-05-25

Запустил general-purpose subagent с ТЗ: 3-5 open-source инструментов для batch-overlay штампа в PDF, фильтр MIT/Apache, ≥50 stars, last commit ≤12мес.

### Кандидаты

| Инструмент | URL | Stars | Last commit | License | Вердикт |
|---|---|---|---|---|---|
| **pdfcpu** | [pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu) | 8650 | 2026-05-11 | Apache-2.0 | **ОСНОВНОЙ** |
| pyHanko | [MatthiasValvekens/pyHanko](https://github.com/MatthiasValvekens/pyHanko) | 726 | 2026-05-24 | MIT | Fallback (stamping primitive) |
| PyPDFForm | [chinapandaman/PyPDFForm](https://github.com/chinapandaman/PyPDFForm) | 1219 | 2026-05-25 | MIT | Долгосрочный (AcroForm route) |
| borb | [jorisschellekens/borb](https://github.com/jorisschellekens/borb) | 3566 | 2026-05-17 | NOASSERTION | Отсев — лицензия |
| Marisol, jodobear/pdf-stamper, pdf_text_overlay | — | <50 | >2 лет | mixed | Отсев — мёртвые |

### Главный вывод harvest

**Готового «движка штампов под ГОСТ Р 21.1101 форма 3» в open-source НЕТ.** Engineering title blocks автоматизируются внутри CAD (Revit/AutoCAD plug-ins), post-processing PDF — наш специфический ad-hoc кейс.

Но **pdfcpu** + **pikepdf** на 100% закрывают batch-overlay по факту тестов.

## Прототип pipeline

### Установка pdfcpu

```powershell
# Качается release-zip с GitHub (bypass proxy — настроен глобально в git config + $env:HTTPS_PROXY="")
$bin = "$HOME\.claude\bin\pdfcpu"
$url = "https://github.com/pdfcpu/pdfcpu/releases/download/v0.12.1/pdfcpu_0.12.1_Windows_x86_64.zip"
# Скачать, Expand-Archive в $bin
```

Артефакт: `~/.claude/bin/pdfcpu/pdfcpu_0.12.1_Windows_x86_64/pdfcpu.exe` (20 MB single-binary, без зависимостей).

### Скрипт-обёртка

`Replace-TitleBlock.ps1` (см. `artifacts/Replace-TitleBlock.ps1`) — **три стадии** (после Acrobat-инцидента 2026-05-25):

**Стадия 1: pikepdf — collapse content streams в Form XObject**

```python
# Если Page.Contents — массив N streams, оставляем только stream[0]
# (схемы + боковая шкала; остальные содержат legacy штампы pypdf-сборки).
# Оборачиваем stream[0] в Form XObject — это изолирует graphics state
# по спеке PDF 1.7 §8.10, поэтому несбалансированные q внутри не утекают.
# Старая попытка «5 Q компенсаций» давала stack underflow в Acrobat.
if isinstance(cs, pikepdf.Array) and len(cs) > 1:
    form = pikepdf.Stream(pdf, cs[0].read_bytes())
    form.Type = pikepdf.Name('/XObject')
    form.Subtype = pikepdf.Name('/Form')
    form.BBox = page.MediaBox
    form.Matrix = pikepdf.Array([1, 0, 0, 1, 0, 0])
    form.Resources = page.Resources
    page.Resources.XObject['/CleanBody'] = form
    page.Contents = pikepdf.Stream(pdf, b'q\n/CleanBody Do\nQ\n')
# Удаляем XObjects /fzFrm0 и /fullpage
```

**Стадия 2: pdfcpu overlay**

```
pdfcpu stamp add --mode pdf "stamp.pdf" "pos:full, scale:1.0 abs, rot:0" cleaned.pdf stamped.pdf
```

Параметры — критичны:
- `pos:full` — full-page overlay (не «small badge in bottom-right»)
- `scale:1.0 abs` — без масштабирования (`abs` = absolute, не proportional)
- `rot:0` — без поворота (default 25° для image-stamps!)

**Стадия 3: PyMuPDF clean — фикс Type1-шрифтов для Acrobat**

```python
doc = fitz.open(stamped)
doc.save(out, garbage=4, clean=True, deflate=True, deflate_fonts=True)
```

**Зачем:** в исходных PDF pypdf-сборки есть Type1 шрифты без обязательных
entry `/FirstChar`, `/Widths`, `/FontDescriptor`. `pdfcpu validate --mode relaxed`
прощает, но **Acrobat при открытии бросает диалог «Ошибка на этой странице».**
PyMuPDF при save с `garbage=4 + clean=True` перепаковывает PDF и нормализует
font dictionaries — strict-validate проходит, Acrobat больше не ругается.

### Использование

```powershell
# Один лист
Replace-TitleBlock.ps1 `
    -InputPdf "СТраница для проб.ORIG.pdf" `
    -StampPdf "etr_stamp.pdf" `
    -OutputPdf "out.pdf"

# Целый том на 57 листов
Replace-TitleBlock.ps1 -InputPdf "Том_5.1.5.pdf" -StampPdf "stamp.pdf" -OutputPdf "Том_stamped.pdf"

# Только страницы 5-50 (титульник, оглавление пропустить)
Replace-TitleBlock.ps1 -InputPdf "Том.pdf" -StampPdf "s.pdf" -OutputPdf "out.pdf" -Pages "5-50"
```

## Сравнение текущих подходов

Все прогоны на одном `СТраница для проб.ORIG.pdf` (985 KB, 1 page, A3 landscape):

| Метрика | Ручной (5 скриптов + Acrobat) | Прежний (PyMuPDF v4) | **Новый pipeline v3** |
|---|---|---|---|
| Кол-во шагов CLI | 5 + ручная правка | 4 python-скрипта | **1 ps1 команда** |
| Время на 1 лист | ~10 мин (с Acrobat) | ~30 сек | **~1.3 сек** |
| Размер вывода | 200 KB (после Acrobat) | 50 KB | **49 KB** |
| СТМ.ЭТ в text-слое | 0 | 0 | **0** ✓ |
| <исполнитель> в text-слое | 0 | 0 | **0** ✓ |
| <нормоконтроль>а не обрезана | требует правки | да | **да** ✓ |
| pdfcpu validate strict | n/a | OK | **OK** ✓ |
| **Acrobat открывает без ошибок** | да | да | **да** ✓ |
| Поддержка multi-page batch | нет | foreach в python | **`-Pages "1-100"`** |

**Acrobat-инцидент 2026-05-25** (исправлен 3-м шагом PyMuPDF clean):
v2 pipeline проходил `pdfcpu validate --mode relaxed`, но Acrobat показывал «Ошибка на этой странице. Возможно, страница будет отображаться неверно» при открытии. Root cause — Type1 шрифты без `/FirstChar` / `/Widths` / `/FontDescriptor`, унаследованные от pypdf-сборки. `pdfcpu validate --mode strict` это ловил, relaxed-mode прощал. PyMuPDF `garbage=4 + clean=True` нормализует font dictionaries без ручного восстановления отсутствующих entries.

## Ограничения и open questions

1. **pdfcpu не делает удаление старого штампа** — это pikepdf-первый-шаг, неизбежен. Готового CLI для surgery с legacy pypdf-сборками нет, и не появится — это слишком узкий кейс.

2. **Word footer как источник штампа** — текущий путь (docx → MS Word COM → PDF). Альтернатива: переделать штамп в **AcroForm** (PyPDFForm) — заполнение полей `PdfWrapper.fill({...})` вместо генерации PDF из Word. Это разовая работа, потом ускоряет всё. Кандидат на следующий этап.

3. **Дорисовка рамки штампа** — пока ручной этап (Acrobat, или PyMuPDF `draw_rect()`). pdfcpu сам не дорисовывает. Можно добавить третий шаг pipeline: post-process `draw_rect` поверх рамки штампа.

4. **Шифр в шаблоне** — пока я заменял через regex по `<w:t>` тегам в `footer2.xml`. На батч-обработку разных подразделов (СТМ.ЭТ, ИОС1.5, ПС, …) нужен **генератор stamp.pdf по параметрам** (шифр, лист/листов, дата подписи). Кандидат на следующий этап.

## Архитектура для разработки на основном ПК

Если переносить в скилл `pdf-stamp-pipeline`:

```
~/.claude/skills/pdf-stamp-pipeline/
├── SKILL.md           — методология и триггеры
├── Replace-TitleBlock.ps1   — основной скрипт
├── stamp_generator.py — генератор stamp.pdf по параметрам (TODO)
├── templates/
│   ├── form3_full.docx  — ГОСТ форма 3 (первый/единичный лист)
│   ├── form5_short.docx — ГОСТ форма 5 (последующие листы)
│   └── header_only.docx — упрощённая для ТЗ/ПЗ
└── examples/
    └── batch_tom.ps1   — обработка целого тома
```

Триггеры в SKILL.md:
- «обновить штампы в томе», «поменять основную надпись», «массовая замена штампа»
- «прошить шифр по всем листам», «единый штамп на том»
- «pdfcpu», «overlay PDF», «batch stamp PDF»

Зависимости:
- pdfcpu в `~/.claude/bin/` (через setup-extras.ps1 — добавить в manifest)
- pikepdf через pip (уже стандартный)
- MS Word или LibreOffice (опционально, для docx → PDF)

## Артефакты сессии

В `artifacts/`:
- `Replace-TitleBlock.ps1` — основной скрипт (рабочий прототип)
- `pdfcpu_install_notes.md` — инструкция по установке single-binary
- `test_pipeline2.pdf` — результат прогона на образце (можно сравнить с FINAL.pdf пользовательской ручной версией)
- `etr_stamp.pdf` — пример stamp template (Word footer → PDF)

В `harvested/`:
- `pdfcpu.md` — заметка по основному инструменту
- `pyHanko.md` — заметка по fallback'у
- `PyPDFForm.md` — заметка по AcroForm-маршруту

## Связанные

- [[2026-05-22_pdf-cleanup-stamp-replacement]] — первая сессия (ручной разбор pypdf-слоёв)
- [[feedback-upd-pdf-parsing]] — общие ловушки PDF в нашем стеке
- [[pdf-helper]] — методологический скилл (надо обновить с упоминанием pdfcpu)

## Recommendation

**На основной ПК (DANIILPC) передать:**

1. Скилл `pdf-stamp-pipeline` (создать) с тремя файлами выше
2. Добавить `pdfcpu` в `setup-extras.ps1` manifest как обязательный extra
3. Обновить `pdf-helper` SKILL.md — добавить триггеры «массовая замена штампа»
4. Создать chain `chain:replace-stamps-batch` для типового флоу: «выбор шаблона → генерация stamp.pdf → batch overlay → проверка text-слоя»

**Долгосрочно (отдельная задача):**
- AcroForm-маршрут через PyPDFForm — переписать stamp template как fillable form, тогда `stamp_generator.py` тривиальный.
- Дорисовка рамки автоматически через PyMuPDF `draw_rect` как третий шаг pipeline.
