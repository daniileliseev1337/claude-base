# DocTR / PaddleOCR — benchmark не зашёл (2026-05-20)

**Контекст.** Дополнение к `scan-text-replace-alternatives.md`. Harvest
рекомендовал DocTR (#1) и PaddleOCR PP-Structure (#2). Прогнали оба на
эталоне КП ЛС АХП. Не зашли.

## EasyOCR baseline

`page3.png` (2482×3511, 250 dpi скан КП ЛС АХП).
12 numeric Regular cells, строки 63-67, y < 1100:

- heights `[18, 18, 19, 18, 17, 18, 18, 18, 17, 17, 19, 20]`
- median **18**, std **0.90**, range **3**

## DocTR (Mindee, 6088 stars, Apache-2.0)

Install: `pip install python-doctr[torch]` (1.0.1, без конфликтов).

Models: `doctr-static.mindee.com` — **скачался** через bypass-proxy
(не baidu). 65 MB.

API: `DocumentFile.from_images(path)` — **cv2.imread не читает
Cyrillic-пути**. Workaround: копировать в ASCII path (`C:/tmp/doctr_bench/`).

**Результат:**
- 29 numeric matches вместо 12 (false positives, шум в фильтре `^[\d\s,.-]+$`)
- DocTR агрессивно делит `1 679,11` → `1679,11` + `492,61` как отдельные
  слова. EasyOCR держал как одну ячейку.
- cap_heights через smart_cap_height_detect:
  `[17,16,17,16,8,17,15,15,16,16,13,16,18,16,18,17,4,18,9,16,16,16,17,15,17,16,12,17,12]`
- median **16**, std **3.23**, range **14**

**Вердикт:** в **3.6× хуже** EasyOCR по std. **Не подходит** для
табличных скан-документов с пробелами в числах.

## PaddleOCR PP-StructureV3 (78228 stars, Apache-2.0)

Install:
- `paddleocr 3.5.0` уже стояло из v0.2 setup-extras.
- `paddlex[ocr]==3.5.2` доставлен сейчас (+ side effect: numpy 2.4.6 → 2.3.5).

**Проблема при load модели:**
- `RuntimeError: [json.exception.parse_error.101] parse error at line 1,
  column 1: attempting to parse an empty input`

**Расследование:**
1. **Прокси НЕ виноват.** `urlopen("https://paddlepaddle.org.cn/")`
   возвращает status=200 без прокси-env. Корп-firewall пропускает baidu.
2. Старый URL `paddleocr.bj.bcebos.com/dygraph_v2.0/...` → **404**
   (paddleocr 3.x сменил источники моделей).
3. После `rm -rf ~/.paddlex/official_models/` и retry — скачалось
   только **6.6 MB** (одна модель PP-LCNet_x1_0_doc_ori из ожидаемых
   ~200 MB всего пайплайна).
4. Каждый retry качает разные кусочки, ни разу не до конца. Silent
   network failures где-то в paddle installer/downloader.

**Вердикт:** **infrastructure issue**, не fixable без deep paddle debug.
В нашей среде paddleocr — ненадёжен. Если когда-то возьмём — пробовать
**RapidOCR** (ONNX-обёртка тех же весов с GitHub releases hosting).

## Главный вывод

**OCR не был корнем боли.** EasyOCR std=0.90 — устойчивый bbox.
Корень — per-cell font_size в нашем коде, починен в `unify_font_size_for_batch()`
(см. LESSONS-LEARNED §6).

Урок про эту проверку — LESSONS-LEARNED.md скилла, §7.

## Что не пробовали (backlog)

- **RapidOCR** — потенциально решает paddleocr install issue (ONNX + GitHub).
- **Tesseract 5** + tesserocr — font-attribute hints (bold/italic), но C++ engine MSI.
- **AnyText** (Category C, end-to-end editing) — conda-only, cyrillic не подтверждён.
- **CNN style transfer** (наш ROADMAP-heavy-options Option 1) — нужен dataset 50+ пар clean+scan.

Все четыре — только при появлении **новой** task где v7 unified не справится.
