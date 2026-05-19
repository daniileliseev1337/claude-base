---
name: image-text-replace
description: |
  Замена текста на растровых изображениях (сканы, JPEG/PNG): найти текст
  через OCR, стереть AI-инпейнтингом (LaMa), отрендерить новый текст в
  том же месте.

  Pipeline: EasyOCR (RU+EN) → mask из bbox → IOPaint (LaMa) → Pillow render →
  сохранение. Primary режим — LaMa (работает на любом фоне). Opt-in
  fast-fill режим (cv2 + bg-color) для batch'а из идентичных белых сканов.

  Status: 2026-05-19 v0.2 — end-to-end протестирован на реальном
  сканированном КП (4 страницы PDF, замена грандтотала +20% на стр.4).

  Триггеры (подключается автоматически):
  - "замени текст на картинке", "замена текста на изображении", "замена текста в скане"
  - "исправь шифр на скане", "поменяй число на картинке", "затри текст на изображении"
  - "remove text from image", "inpaint text", "OCR + inpaint"
  - "перепечатать текст в скане", "replace text in scan"
  - "увеличь сумму в скане на N%", "поменяй цифру на N в скане"
  - после работы с PDF где из страницы извлекли картинку и нужно её
    подправить перед обратной вставкой
tools: Read, Write, Edit, Bash, Glob, Grep
---

# image-text-replace

Скилл для **программной** замены текста на растровых изображениях. Если
нужен один-два скана и есть Photoshop / Acrobat — **открой их руками,
скилл не нужен**. Скилл окупается когда:

- Batch из 10+ файлов с одинаковой правкой
- Voice/chat workflow (правка через Claude, не открывая GUI)
- Скан внутри PDF где нужно поправить и вставить обратно (`pdf-edit` + этот скилл)

## Pipeline в одном экране

```
input.png (или .jpg, .tiff)
    │
    ├── EasyOCR.readtext(input)  — RU+EN, через PIL (Unicode paths!)
    │       └→ [(text, bbox, conf), ...]
    │
    ├── фильтр по запросу пользователя
    │   (literal substring / regex / find_value_near_label для "Label: value")
    │       └→ список bbox'ов на замазку
    │
    ├── build_mask(bboxes, dilate=4px)
    │       └→ numpy mask (бинарная: белое = замазать)
    │
    ├── mode=lama (default):
    │       iopaint run --model=lama --model-dir=C:\iopaint-cache\torch → cleaned.png
    │   mode=fast:
    │       cv2.inpaint(image, mask, method=TELEA) → cleaned.png
    │       (для batch'а из идентичных белых сканов, в 50x быстрее)
    │
    ├── render_text() — Pillow ImageDraw.text() с цветом из ОРИГИНАЛА
    │       (важно: семплировать цвет из original, не cleaned —
    │        иначе получишь near-white на near-white = invisible)
    │       └→ result.png
    │
    └── сохранить рядом с input как input.replaced.png
```

## Когда подключать (для Claude)

Автоматически по триггерам в `description`. Также по контексту:

- Пользователь приложил скан и сказал «здесь должно быть X вместо Y»
- В рамках pdf-edit / word-helper / excel-helper случилось «картинка
  внутри документа с нерелевантным текстом»

**Не подключать** если:
- Векторное изображение (SVG, EMF) — там текст редактируемый, скилл не нужен
- Текст в самой странице PDF (не как картинка) — это `pdf-edit` / Acrobat
- Просто извлечь текст для копирования — это PaddleOCR без замены

## Зависимости

Лениво устанавливаются скиллом при первом запуске:

| Пакет | Размер | Назначение |
|-------|--------|------------|
| `paddleocr` | уже стоит (setup-extras) | OCR с bbox |
| `paddlepaddle` | уже стоит | backend для paddle |
| `iopaint` | ~200 MB + 174 MB модель LaMa | inpainting (primary mode) |
| `Pillow` | ~3 MB | render нового текста |
| `opencv-python` | ~30 MB | fast-fill mode + mask ops |

Установка по требованию:
```python
try:
    import iopaint
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "iopaint", "Pillow", "opencv-python"], check=True)
    import iopaint
```

Первый запуск iopaint скачает LaMa модель из HuggingFace в
`~/.cache/iopaint/` (~174 MB). На корп-прокси может потребовать
`HTTPS_PROXY` env-vars.

## Контракт API скилла

Pipeline доступен как:

```bash
# CLI mode (одной командой):
python ~/.claude/skills/image-text-replace/pipeline.py \
    --input scan.png \
    --find "Шифр Ф.2024.123456789" \
    --replace "Шифр Ф.2026.987654321" \
    --font "C:/Windows/Fonts/arial.ttf" \
    --mode lama
```

или

```python
# Python lib mode:
from pipeline import replace_text_in_image
result = replace_text_in_image(
    input_path="scan.png",
    replacements=[
        ("Шифр Ф.2024.123456789", "Шифр Ф.2026.987654321"),
        ("ВКР-12", "ВКР-13"),
    ],
    font_path="C:/Windows/Fonts/arial.ttf",
    mode="lama",  # or "fast"
    output_path="scan.replaced.png",
)
```

## Параметры

| Параметр | Default | Описание |
|----------|---------|----------|
| `--input` | — | Путь к исходной картинке (.png/.jpg/.tiff/.bmp) |
| `--find` / `--replace` | — | Пара «найти → заменить». Можно повторять для batch замен. |
| `--regex` | False | Интерпретировать `--find` как regex |
| `--font` | `arial.ttf` | TTF с поддержкой кириллицы. Windows: `C:/Windows/Fonts/arial.ttf`. |
| `--font-size` | auto | Подобрать по высоте оригинала автоматически или задать в пикселях |
| `--color` | auto | Цвет нового текста. По умолчанию — медиана цвета в bbox оригинала. |
| `--mode` | `lama` | `lama` (AI inpaint, primary) или `fast` (cv2/bg-fill) |
| `--ocr-lang` | `ru,en` | PaddleOCR языки |
| `--dilate` | `4` | Пиксели расширения mask вокруг bbox (захватить subpixel'ы) |
| `--output` | `<input>.replaced.<ext>` | Куда сохранять |
| `--dry-run` | False | Только показать что найдено (без замены) |

## Failure-mode

Скилл **никогда не должен молча** замазать не-то:

1. **Перед заменой** — show найденные регионы (bbox + текст + confidence)
   пользователю, попросить подтверждение (если `--yes` не передан).
2. **OCR confidence < 0.7** — пометить как WARN, не замазывать без явного
   одобрения. Часто это «казалось буквы Ф, а на самом деле дефект скана».
3. **Несколько матчей** — спросить какие конкретно (`--all` для batch
   или интерактивный выбор).
4. **Текст не найден** — exit с понятным сообщением, не fallback на
   regex или fuzzy без явного `--fuzzy` флага.

## Тестирование на первом реальном скане

Перед production-использованием:

1. Положить тестовый скан в `~/.claude/_sandbox/test-scan.png`.
2. `python pipeline.py --input ... --find "..." --replace "..." --dry-run`
3. Проверить что bbox'ы попали в нужные слова, OCR корректен.
4. Запустить без `--dry-run` на тестовом, открыть result.png глазами.
5. Если шов виден / текст съехал — крутить `--dilate`, `--font-size`,
   `--color`.

## Связанные

- [[skills/skills|skills]] — каталог скиллов
- [[pdf-helper]] — частая связка (PDF страница → картинка → этот скилл → вставка обратно)
- [[2026-05-13_harvest-workflow]] — harvest, в рамках которого нашли этот стек
- harvest note: `session-reports/2026-05-15_handoff-manifest-extras-installer-stage8/harvested/image-text-replace-stack.md`

## Источники (harvest)

- [Appt-OCR](https://github.com/aarontzeng/Appt-OCR) — архитектурное вдохновение (PPTX/PDF batch OCR + LaMa)
- [IOPaint](https://github.com/Sanster/IOPaint) — sane wrapper над LaMa (бывший lama-cleaner)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) — наш установленный OCR
- [PERO-Enhance](https://github.com/DCGM/pero-enhance) — нишевый инструмент для line-level inpaint в сканах
