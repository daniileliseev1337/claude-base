"""Minimal font calibration without segfault — render 4 candidates."""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

art = sys.argv[1]
src = f"{art}/p3_orig.png"
out = f"{art}/font_test.png"

# Use price 1 679,11 — well-OCR'd bbox
x, y, w, h = 1981, 674, 97, 32
scan = Image.open(src).convert("RGB")
crop = scan.crop((x, y, x + w, y + h))

# Detect cap height
arr = np.array(crop).mean(axis=2)
core_rows = np.where((arr < 150).sum(axis=1) > w * 0.3)[0]
cap_h = int(core_rows[-1] - core_rows[0]) if len(core_rows) > 0 else 20
print(f"cap_h={cap_h}")

candidates = [
    ("Calibri", r"C:\Windows\Fonts\calibri.ttf"),
    ("Calibri Bold", r"C:\Windows\Fonts\calibrib.ttf"),
    ("Arial", r"C:\Windows\Fonts\arial.ttf"),
    ("Open Sans", r"C:\Windows\Fonts\seguisb.ttf"),  # Segoe UI Semibold
]

# Find font_size so cap-height matches
def fit_size(path, target):
    for size in range(10, 50):
        f = ImageFont.truetype(path, size)
        im = Image.new("RGB", (60, 60), "white")
        ImageDraw.Draw(im).text((5, 5), "H", font=f, fill="black", anchor="lt")
        a = np.array(im).mean(axis=2)
        rows = np.where((a < 100).any(axis=1))[0]
        if len(rows) >= 2 and rows[-1] - rows[0] >= target:
            return size
    return 22

text = "1 679,11"
combined = Image.new("RGB", (w + 250, (h + 4) * (len(candidates) + 1)), "white")
combined.paste(crop, (0, 0))
ImageDraw.Draw(combined).text((w + 8, 2), "REAL", fill="red")
for i, (name, path) in enumerate(candidates):
    sz = fit_size(path, cap_h)
    f = ImageFont.truetype(path, sz)
    row = Image.new("RGB", (w, h + 4), "white")
    ImageDraw.Draw(row).text((1, 2), text, font=f, fill=(5, 5, 5), anchor="lt")
    combined.paste(row, (0, (h + 4) * (i + 1)))
    ImageDraw.Draw(combined).text((w + 8, (h + 4) * (i + 1) + 2), f"{name} sz={sz}", fill="red")

combined.resize((combined.width * 3, combined.height * 3), Image.LANCZOS).save(out)
print(f"saved {out}")
