---
name: image-text-replace
description: |
  Замена/вставка текста на сканированных изображениях (JPEG/PNG/scan-PDF):
  OCR обнаружение → smart cap detection → font calibration → render с
  matching стилем → optional SD inpaint scan-ification.

  Pipeline v3.0 (production-ready, проверен на КП К7 АХП 2026-05-19):
  EasyOCR → smart_cap_height_detect → find_neighbor_cell → Times Bold
  render at cell_h × 1.42 → minimal degradation → midline alignment →
  SD img2img strength=0.10 polish.

  Status v3.0: production-ready после 16 итераций. Финальный результат
  принят пользователем как "именно то чего мы хотели". См.
  LESSONS-LEARNED.md для retrospective и anti-patterns.

  Триггеры:
  - "замени текст на картинке", "замена текста в скане"
  - "исправь шифр на скане", "затри текст на изображении"
  - "вставь текст в ячейку скана", "добавь % в строку"
  - "OCR + inpaint", "scan text replacement"
  - "увеличь сумму в скане на N%", "поменяй цифру в скане"
  - после работы с PDF где из страницы извлекли scan-картинку
tools: Read, Write, Edit, Bash, Glob, Grep
---

# image-text-replace v3.0

Скилл для **программной замены/вставки текста** на сканированных
растровых изображениях. Финансовые документы (КП, акты, счета),
техническая документация, отсканированные таблицы.

> **CRITICAL FIRST STEP для нового документа:** font calibration через
> `calibration.py` — определи реальный шрифт скана. Это #1 урок —
> 8 итераций потеряны на tuning Arial когда scan был Times Bold.

## Когда подключать

- Пользователь приложил скан/PDF и сказал «здесь должно быть X вместо Y»
- В рамках pdf-edit/word-helper нужно поменять текст в **картинке**
  внутри документа
- Batch-замена однотипного текста в 10+ сканах (например, шифры,
  даты, проценты)

**Не подключать:**
- Векторный PDF где текст редактируется напрямую → используй `pdf-edit`
- Просто извлечь текст → `paddleocr`/`easyocr` напрямую
- Один-два файла с Photoshop/Acrobat под рукой → user делает руками

## Workflow v3.0 (для нового типа документа)

### Шаг 1 — Font calibration (5 минут, делается ОДИН раз для типа документа)

```powershell
# Render same digits в 12 fonts рядом со scan → визуально подобрать matching
python ~/.claude/skills/image-text-replace/calibration.py `
    --input scan.png `
    --bbox 1114,686,96,26 `        # OCR bbox любого числа на скане
    --text "16 877,50" `             # сам text для render
    --output font-sheet.png

# Открой font-sheet.png → выбери row которая LOOKS наиболее похожа на REAL SCAN
# Запомни font path (e.g. "C:/Windows/Fonts/timesbd.ttf")
```

Без этого шага можно потратить часы на render param tuning неправильного
шрифта.

### Шаг 2 — Замена/вставка через pipeline

```powershell
python ~/.claude/skills/image-text-replace/pipeline.py `
    --input scan.png `
    --find "Ф.2024.123456789" `
    --replace "Ф.2026.987654321" `
    --font "C:/Windows/Fonts/timesbd.ttf"  ` # ← из calibration!
    --mode lama `
    --sd-refine `                          # ← v3.0 финальный SD pass
    --sd-strength 0.10
```

Pipeline автоматически:
1. OCR → bbox целевого text
2. `find_neighbor_cell_reference()` → берём ref color/PSF/size с ячейки рядом
3. `smart_cap_height_detect()` → font_size без descender ошибок
4. Render с matching font + minimal degradation
5. `compute_midline_paste_y()` → centered alignment
6. LaMa inpaint → erase old text
7. Blend rendered new text
8. **SD img2img strength=0.10** → final scan-ification

### Шаг 3 — Verification

```powershell
# Render result region, eyeball compare к surrounding text
python -c "from PIL import Image; Image.open('scan.replaced.png').crop((x,y,x+w,y+h)).resize((W*3,H*3)).save('result-zoom.png')"
```

Если **не матч** — see LESSONS-LEARNED.md перед next iteration.
**Не tune blindly.** Diagnose: font / size / weight / color / position / sharpness.

## Pipeline в одном экране

```
input.png (scan)
    │
    ├── EasyOCR.readtext(input)
    │       └→ [(text, bbox, conf), ...]
    │
    ├── filter_matches → label OCR bbox
    │
    ├── find_neighbor_cell_reference(matches, label, side='right', digits_only=True)
    │       └→ cell_ref OCR match (для color/PSF/font matching)
    │
    ├── smart_cap_height_detect(cell_ref.bbox) → cell_cap_height
    │       (игнорирует descenders запятой "16 877,50")
    │
    ├── sample text_color, noise_std, psf_sigma из cell_ref region
    │
    ├── _render_scan_realistic(font=TIMES BOLD, size=cap_h × 1.42,
    │                          psf_sigma=measured × 0.5)
    │       └→ rgb_text, alpha, canvas anchors
    │
    ├── compute_midline_paste_y(label_anchors, cell_anchors, ...)
    │       └→ paste_x, paste_y
    │
    ├── LaMa inpaint (mode=lama) erase old text → cleaned.png
    │
    ├── Blend rendered text onto cleaned at paste position
    │
    └── [v3.0] refine_text_region_with_diffusion(crop_bbox,
                                                    strength=0.10)
            → final scan-style polish via SD
```

## Зависимости

| Пакет | Размер | Required for |
|-------|--------|-------------|
| `easyocr` | ~140 MB + 100 MB models | OCR с bbox |
| `Pillow` | ~3 MB | render |
| `opencv-python` | ~30 MB | mask ops |
| `iopaint` (LaMa) | ~200 MB + 174 MB model | inpaint backend |
| `diffusers` + `transformers` + `accelerate` | ~500 MB + **3.4 GB SD model** | v3.0 SD refine |

Базовые (без SD) — лениво ставятся при первом запуске. SD требует
явной установки + HF auth + ASCII-safe cache dir `C:/sd-cache`.

## SD setup (только для v3.0 финального pass)

```powershell
# 1. Создать HF token (https://huggingface.co/settings/tokens, Read access)
$env:HF_TOKEN = "hf_..."
$env:HF_HOME = "C:/sd-cache"

# 2. Скачать model (3.4 GB, на корп-сети может занять ~30-60 min):
python -c "
import os
os.environ['HF_HOME'] = 'C:/sd-cache'
from huggingface_hub import snapshot_download, login
login(token=os.environ['HF_TOKEN'])
snapshot_download(
    repo_id='runwayml/stable-diffusion-inpainting',
    cache_dir='C:/sd-cache',
    allow_patterns=['*.json', '*.txt', '*.safetensors', '*.bin'],
)
"

# 3. Revoke token после первой загрузки (cache сохранится локально)
```

## Failure modes

1. **Hallucinated characters в SD pass** — strength > 0.20 на digits.
   Mitigation: держать `--sd-strength <= 0.15` для финансовых documents.
2. **OCR confidence < 0.7** — skill ОСТАНАВЛИВАЕТСЯ, не fall back на
   regex/fuzzy без явного `--fuzzy`.
3. **Несколько матчей find pattern** — show OCR results + ask user.
4. **No neighbor cell found** — fall back к label own bbox (lower quality).

## Связанные

- [[LESSONS-LEARNED]] — 16-итераций retrospective + anti-patterns
- [[ROADMAP-heavy-options]] — 4 heavy techniques (PSF, Borrow, SD, CNN)
- [[skills/skills|skills]] — каталог
- [[pdf-helper]] — связка PDF → image → этот скилл → PDF
- harvest: [[Appt-OCR]], [[IOPaint]], [[PaddleOCR]]

## Источники (harvest)

- [Appt-OCR](https://github.com/aarontzeng/Appt-OCR) — архитектурное вдохновение
- [IOPaint](https://github.com/Sanster/IOPaint) — LaMa backend
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — OCR engine (заменил PaddleOCR из-за CDN issues)
- [runwayml/stable-diffusion-inpainting](https://huggingface.co/runwayml/stable-diffusion-inpainting) — SD model (v3.0)
- [PERO-Enhance](https://github.com/DCGM/pero-enhance) — fallback option

## Versioning

- v0.1-v0.3: crisp digital — deprecated
- v0.5: PSF estimation (Option 3) — kept as helper
- v0.6: glyph borrowing (Option 4) — opt-in helper
- v1.4: cap-height font sizing — integrated
- v2.3: Times Bold default — integrated
- **v3.0**: SD scan-ification — production stack
