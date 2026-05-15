---
name: reference-pdf-ocr-pipeline
description: "Пайплайн извлечения текста из PDF где текст в кривых (наш pdf-mcp возвращает 0 символов). pypdfium2 рендерит региoнно без лимита 2000×2000, PaddleOCR извлекает RU+EN."
metadata: 
  node_type: memory
  type: reference
  originSessionId: fb892ce7-0051-4258-b832-c80cab5ecb76
---

**Когда применять:** PDF файл, `pdf-mcp.pdf_read_pages` возвращает 0 символов
(текст векторизован в кривые шрифтов), `markitdown` тоже пустой. Tesseract на
Windows-машине пользователя не установлен.

**Стек:**
- **pypdfium2** (Apache/BSD) — рендер PDF в PIL Image. Не имеет лимита 2000×2000
  как наш `pdf-mcp.pdf_render_pages`. Подхватывает любой dpi (тестировал 200 на
  A2×3 → 9928×4678 px).
- **PaddleOCR** (Apache 2.0) — OCR русского+английского без Tesseract. Pip-only,
  без админ-прав.

**Скрипт-эталон:** `C:\Users\Deliseev\Desktop\Здадчака\test_paddleocr_pdf.py`
показал 331 уникальную строку из `Приложение к ЧТЗ_27_02_2026 Model (1).pdf` за ~4 мин.

**Минимальный пример:**
```python
import pypdfium2 as pdfium
from paddleocr import PaddleOCR
import numpy as np

pdf = pdfium.PdfDocument("input.pdf")
img = pdf[0].render(scale=100/72).to_pil()   # 100 dpi
img.save("page.png")

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang='ru',
    enable_mkldnn=False,   # КРИТИЧНО на Windows для больших картинок
)
results = ocr.predict(np.array(img))
for r in results:
    for txt in r['rec_texts']:
        print(txt)
```

**Ловушки:**
- `enable_mkldnn=False` обязательно на Windows. Иначе при больших картинках
  падает с `NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support
  [pir::ArrayAttribute<pir::DoubleAttribute>]` (oneDNN runtime баг).
- Большое изображение PaddleOCR сам resize'нет до max 4000 длинной стороны.
  Если нужна максимальная точность — тайлить вручную и склеивать.
- При первом запуске качает модели (~30s+, в т.ч. `eslav_PP-OCRv5_mobile_rec`
  для русского) в `C:\Users\<...>\.paddlex\official_models\`.
- PowerShell cp1251: при `print('×')` падает UnicodeEncodeError.
  Лекарство: `$env:PYTHONIOENCODING = "utf-8"` перед запуском или замена символов.

**Связанные:** [[reference-autocad-mcp]], [[reference-harvest-tools-2026-05]]
