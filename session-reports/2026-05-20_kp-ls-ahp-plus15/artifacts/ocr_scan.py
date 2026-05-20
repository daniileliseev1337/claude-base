"""OCR страницы 3 и сохранение всех matches в JSON для последующего поиска целей."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/image-text-replace"))
from pipeline import run_ocr

img = sys.argv[1]
out = sys.argv[2]
matches = run_ocr(img)
data = []
for m in matches:
    x, y, w, h = m.bbox_rect()
    data.append({
        "text": m.text,
        "conf": round(m.confidence, 3),
        "bbox": [x, y, w, h],
        "cx": x + w // 2,
        "cy": y + h // 2,
    })
Path(out).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OCR done: {len(data)} matches → {out}")
