"""
Тест: извлечь текст из PDF с текстом в кривых через pypdfium2 + PaddleOCR.
Решаем блокер: pdf-mcp возвращал 0 символов, Tesseract не установлен.
"""
from pathlib import Path
import sys
import time

import pypdfium2 as pdfium
from PIL import Image
import numpy as np

BASE = Path(r"C:\Users\Deliseev\Desktop\Здадчака")
PDF = BASE / "Приложение к ЧТЗ_27_02_2026 Model (1).pdf"
OUT_TXT = BASE / "ChTZ_OCR_paddleocr.txt"
OUT_PNG = BASE / "ChTZ_region_render.png"

print(f"[1/4] Открываю PDF: {PDF.name}")
pdf = pdfium.PdfDocument(PDF)
page = pdf[0]
w_pt, h_pt = page.get_size()
print(f"      Размер страницы: {w_pt:.0f}x{h_pt:.0f} pt (A2x3 ~ 5040x707 mm)")

# Рендерим страницу на высоком DPI (без лимита 2000x2000 как у нашего pdf-mcp)
# Возьмём 200 dpi — баланс качества/размера
SCALE = 100 / 72  # 100 dpi — достаточно для текста, меньше нагрузка на OCR
print(f"[2/4] Рендерю страницу на 200 dpi (scale={SCALE:.2f})...")
t0 = time.time()
bitmap = page.render(scale=SCALE, rotation=0)
img = bitmap.to_pil()
print(f"      Размер изображения: {img.size} ({(time.time()-t0):.1f}s)")
img.save(OUT_PNG)
print(f"      Сохранён рендер: {OUT_PNG.name}")

# OCR через PaddleOCR
print("[3/4] Инициализирую PaddleOCR (RU+EN)... (~30s на первый запуск)")
t0 = time.time()
from paddleocr import PaddleOCR
# По API 3.x используется параметр lang. Для русского нужен 'ru' или 'eslav'
# Пробуем сначала 'ru'.
# Отключаем mkldnn — известный баг на Windows с большими картинками
ocr = PaddleOCR(use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='ru',
                enable_mkldnn=False)
print(f"      OCR инициализирован ({(time.time()-t0):.1f}s)")

print("[4/4] Запускаю OCR на изображении...")
t0 = time.time()
img_array = np.array(img)
results = ocr.predict(img_array)
print(f"      OCR выполнен ({(time.time()-t0):.1f}s)")

# Извлекаем текст
lines = []
total_items = 0
for result in results:
    if result is None:
        continue
    # API 3.x: результаты в result.json или result['rec_texts']
    try:
        texts = result['rec_texts']
        scores = result.get('rec_scores', [1.0] * len(texts))
        boxes = result.get('rec_polys', None)
        for i, txt in enumerate(texts):
            if txt and txt.strip():
                lines.append(txt.strip())
                total_items += 1
    except (KeyError, TypeError):
        try:
            # старое API
            for line in result:
                if line and len(line) >= 2:
                    box, (text, score) = line[0], line[1]
                    if text:
                        lines.append(text.strip())
                        total_items += 1
        except Exception as e:
            print(f"      Не смог распарсить result: {e}")
            print(f"      Тип результата: {type(result)}")
            if hasattr(result, '__dict__'):
                print(f"      Атрибуты: {list(result.__dict__.keys())[:10]}")

print(f"\n=== РЕЗУЛЬТАТ ===")
print(f"Распознано фрагментов текста: {total_items}")
print(f"Уникальных строк: {len(set(lines))}")

# Сохраняем результат
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write(f"# OCR извлечение из {PDF.name}\n")
    f.write(f"# Через pypdfium2 + PaddleOCR, dpi=200\n")
    f.write(f"# Всего фрагментов: {total_items}\n\n")
    for line in lines:
        f.write(line + "\n")
print(f"\nСохранено: {OUT_TXT}")

# Покажем первые 30 строк
print("\nПервые 30 строк:")
for line in lines[:30]:
    print(f"  {line}")
