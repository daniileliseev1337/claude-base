"""Identify which PIL operation crashes."""
import sys, traceback

print("step 1: import")
from PIL import Image, ImageDraw, ImageFont
import numpy as np
print("step 1 ok")

print("step 2: open PNG")
src = sys.argv[1]
scan = Image.open(src).convert("RGB")
print(f"step 2 ok size={scan.size}")

print("step 3: crop")
crop = scan.crop((1981, 674, 2078, 706))
print(f"step 3 ok size={crop.size}")

print("step 4: numpy convert")
arr = np.array(crop)
print(f"step 4 ok shape={arr.shape}")

print("step 5: mean")
gray = arr.mean(axis=2)
print(f"step 5 ok shape={gray.shape}")

print("step 6: load font calibri")
f = ImageFont.truetype(r"C:\Windows\Fonts\calibri.ttf", 26)
print("step 6 ok")

print("step 7: small new image")
im = Image.new("RGB", (200, 60), "white")
ImageDraw.Draw(im).text((5, 5), "1 679,11", font=f, fill=(5, 5, 5))
print("step 7 ok")

print("step 8: small save")
out_dir = sys.argv[2]
im.save(f"{out_dir}/dbg_step8.png")
print("step 8 ok")

print("step 9: large combined")
combined = Image.new("RGB", (400, 600), "white")
combined.paste(crop, (0, 0))
combined.paste(im, (0, 100))
combined.save(f"{out_dir}/dbg_step9.png")
print("step 9 ok")

print("step 10: resize large")
big = combined.resize((1200, 1800), Image.LANCZOS)
big.save(f"{out_dir}/dbg_step10.png")
print("step 10 ok")

print("ALL OK")
