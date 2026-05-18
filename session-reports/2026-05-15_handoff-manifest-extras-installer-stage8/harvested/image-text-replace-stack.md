# Harvest — image text replace stack (2026-05-18)

**Запрос:** «можем ли мы найти инструменты для работы с изображениями
их корректировкой например замена текста». Уточнено: типично **сканы
документов**, объём окупает автоматизацию, у пользователя есть **Adobe
аккаунт**.

## Источник 1 — Adobe Firefly MCP (уже подключён)

**Ссылка:** `mcp__59c626be-4e80-4c40-9a49-ff47f6a2da1f__*` в нашем
deferred-tools списке.

**Что есть:** 40+ image-tools (crop, brightness/contrast, HSL, blur,
selection by prompt, vectorize, generative_expand, fill_text для Adobe
Express templates).

**Решение — НЕ ПОДХОДИТ для нашего use-case.** Цитата из ответа
`adobe_mandatory_init`:

> Object/element removal from images («remove text from photo») —
> **not available**. Alternative: Adobe Photoshop or Adobe Firefly
> [desktop apps].
>
> OCR / text extraction — **not available**. Alternative: Adobe Acrobat
> or dedicated OCR tools.

`fill_text` — только для Adobe Express templates (флаеры, посты), не
для сканов. Также MCP не принимает локальные пути — требует
file picker или egress upload.

Adobe-аккаунт пользователю реально нужен для **настольных** Photoshop
/ Acrobat, не для MCP-канала.

---

## Источник 2 — Appt-OCR (архитектурное вдохновение)

- **URL:** https://github.com/aarontzeng/Appt-OCR
- **Stars:** небольшие (~20-50, точное число на 2026-05 не уточняли)
- **Last commit:** активный (2026)
- **License:** MIT
- **Описание:** «Batch OCR tool for PPTX/PDF files — extracts text from
  images, reconstructs editable text boxes, and optionally erases
  original text using AI inpainting (LaMa).»

**Зачем смотрели:** прямо под наш сценарий — нашёл «батч + OCR + LaMa
inpaint». Можем взять архитектуру (PaddleOCR → bbox → mask → LaMa →
render).

**Решение:** НЕ клонировать целиком (он заточен под PPTX/PDF, а нам
самостоятельные изображения), **скопировать архитектуру** в наш скилл.
Получили `~/.claude/skills/image-text-replace/pipeline.py`.

---

## Источник 3 — IOPaint (главный движок)

- **URL:** https://github.com/Sanster/IOPaint
- **Stars:** ~17k (на 2026-05)
- **Last commit:** активный
- **License:** Apache-2.0
- **Описание:** «Image inpainting tool powered by SOTA AI Model.» Был
  переименован из `lama-cleaner` в `IOPaint`. Поддерживает LaMa, Stable
  Diffusion, MAT, FCFLama и др. модели.

**Зачем смотрели:** sane Python-обёртка над LaMa с CLI batch mode
(`iopaint run --image=<folder> --mask=<folder> --output=<dir>`).
Установка `pip install iopaint`.

**Решение:** **ВЗЯТО ВНУТРЬ.** Используется в нашем pipeline.py через
subprocess CLI (`iopaint run --model=lama ...`). Модель LaMa скачивается
автоматически в `~/.cache/iopaint/` при первом запуске (~174 MB).

---

## Источник 4 — PaddleOCR (уже стоит)

- **URL:** https://github.com/PaddlePaddle/PaddleOCR
- **Stars:** 40k+
- **License:** Apache-2.0
- **Status:** уже у нас в `mcp-manifest.json`, ставится через
  `setup-extras.ps1`.

**Зачем:** OCR с координатами bbox. Поддерживает русский + английский.
Точнее Tesseract'а на сложных сканах.

**Решение:** **ВЗЯТО ВНУТРЬ.** В pipeline.py через `from paddleocr
import PaddleOCR`.

---

## Источник 5 — PERO-Enhance (запасной)

- **URL:** https://github.com/DCGM/pero-enhance
- **License:** MIT
- **Описание:** Text-guided document scan quality enhancement. Методы
  `repair_line` (улучшить читаемость строки) и `inpaint_line`
  (заинпейнтить строку текста через PAGE XML).

**Зачем смотрели:** нишевый инструмент специально для **сканов
документов**, не general-purpose AI. Может работать быстрее LaMa
для line-level замен.

**Решение:** **НЕ ВЗЯТО**, но **отмечено** как fallback. Если LaMa
будет плохо работать на конкретных типах сканов — попробовать
PERO-Enhance. Зависимости тяжелее (требует Caffe-стек), поэтому не
default.

---

## Сравнительная таблица

| # | Инструмент | Stars | Лицензия | Решение |
|---|------------|-------|----------|---------|
| 1 | Adobe Firefly MCP | — | проприетарь | ❌ Не подходит (нет «remove text from photo» в API) |
| 2 | Appt-OCR | ~30 | MIT | ⚠ Архитектура взята, код не копировали |
| 3 | IOPaint (LaMa) | 17k | Apache-2.0 | ✅ Primary inpainting engine |
| 4 | PaddleOCR | 40k+ | Apache-2.0 | ✅ OCR engine (уже стоит) |
| 5 | PERO-Enhance | <100 | MIT | ⏸ В запасе, не подключено |

## Что добавили в общую базу

- **Skill:** `~/.claude/skills/image-text-replace/` (SKILL.md, pipeline.py, README.md)
- **Заметка про IOPaint:** TODO копировать в `~/.claude/harvested/pdf/IOPaint.md`
  (пока в pdf/ нет, хотя категория не очень подходит — IOPaint про image
  не PDF; может стоит завести `harvested/image/`).

## Связанные

- [[../report]] — этот session report
- [[../../../skills/image-text-replace/SKILL]] — methodology
- [[../../../skills/image-text-replace/pipeline]] — реализация
- [[../../../memory/2026-05-13_harvest-workflow]] — методика harvest

## Альтернативы которые НЕ исследовали (для будущих сессий)

- **TextDiffuser** (Microsoft) — генерация изображений с точным
  контролем над текстом. Overkill для нашей задачи (нам не нужно
  генерить, нам нужно заменять).
- **AnyText** — text-aware editing с диффузионными моделями. Сложнее
  чем нужно.
- **MAT inpainting** — альтернатива LaMa, IOPaint умеет его как опцию.
- **Stable Diffusion XL inpaint** — IOPaint умеет, но overkill для
  сканов документов.
