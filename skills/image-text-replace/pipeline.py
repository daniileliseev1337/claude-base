#!/usr/bin/env python
"""
image-text-replace pipeline.

Заменяет указанный текст на растровом изображении (скан, JPEG, PNG):
1. OCR через PaddleOCR -> текст + bbox координаты
2. Фильтр по запросу пользователя (literal / regex)
3. Mask из bbox с расширением (dilate)
4. Inpaint: LaMa (default) либо cv2.inpaint TELEA (fast mode)
5. Render нового текста через Pillow в том же месте
6. Сохранение result рядом с оригиналом

CLI usage:
    python pipeline.py --input scan.png \
        --find "Шифр Ф.2024.123456789" \
        --replace "Шифр Ф.2026.987654321" \
        --font "C:/Windows/Fonts/arial.ttf" \
        --mode lama

Python lib:
    from pipeline import replace_text_in_image
    replace_text_in_image(
        input_path="scan.png",
        replacements=[("old", "new")],
        font_path="C:/Windows/Fonts/arial.ttf",
        mode="lama",
    )

Зависимости (лениво устанавливаются):
    paddleocr, paddlepaddle, iopaint (для mode=lama), Pillow, opencv-python, numpy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


# ----------------------------------------------------------------------
# Lazy deps installer
# ----------------------------------------------------------------------

def _ensure_deps(mode: str) -> None:
    """Install missing pip packages on first run. Idempotent."""
    required = ["paddleocr", "Pillow", "opencv-python", "numpy"]
    if mode == "lama":
        required.append("iopaint")

    missing: list[str] = []
    for pkg in required:
        try:
            __import__(pkg.split("-")[0].replace("Pillow", "PIL").replace("opencv", "cv2"))
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[ensure-deps] Installing: {missing}", flush=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", *missing],
            check=True,
        )


# ----------------------------------------------------------------------
# Core types
# ----------------------------------------------------------------------

@dataclass
class OcrMatch:
    """One text region recognized by OCR."""
    text: str
    bbox: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]
    confidence: float

    def bbox_rect(self) -> tuple[int, int, int, int]:
        """Return axis-aligned bounding rectangle: (x, y, w, h)."""
        xs = [p[0] for p in self.bbox]
        ys = [p[1] for p in self.bbox]
        x, y = min(xs), min(ys)
        return x, y, max(xs) - x, max(ys) - y

    def height_px(self) -> int:
        x, y, w, h = self.bbox_rect()
        return h


# ----------------------------------------------------------------------
# OCR
# ----------------------------------------------------------------------

def run_ocr(image_path: str, langs: str = "ru,en") -> list[OcrMatch]:
    """Run PaddleOCR on image, return list of OcrMatch."""
    from paddleocr import PaddleOCR
    primary_lang = langs.split(",")[0].strip()
    ocr = PaddleOCR(use_angle_cls=True, lang=primary_lang, show_log=False)
    raw = ocr.ocr(image_path, cls=True)
    matches: list[OcrMatch] = []
    if not raw or not raw[0]:
        return matches
    for region in raw[0]:
        bbox_pts, (text, conf) = region
        bbox_tuple = tuple((int(p[0]), int(p[1])) for p in bbox_pts)
        matches.append(OcrMatch(text=text, bbox=bbox_tuple, confidence=float(conf)))
    return matches


def filter_matches(
    matches: Sequence[OcrMatch],
    find_pattern: str,
    use_regex: bool,
    min_confidence: float = 0.7,
) -> list[OcrMatch]:
    """Pick matches whose text matches user's pattern."""
    if use_regex:
        rx = re.compile(find_pattern)
        return [m for m in matches if rx.search(m.text) and m.confidence >= min_confidence]
    return [m for m in matches if find_pattern in m.text and m.confidence >= min_confidence]


# ----------------------------------------------------------------------
# Mask building
# ----------------------------------------------------------------------

def build_mask(image_shape: tuple[int, int], matches: Iterable[OcrMatch], dilate_px: int = 4):
    """Return binary mask (0/255) of size (H, W) covering match bboxes + dilation."""
    import cv2
    import numpy as np

    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    for m in matches:
        pts = np.array(m.bbox, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
    if dilate_px > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_px * 2 + 1, dilate_px * 2 + 1))
        mask = cv2.dilate(mask, kernel)
    return mask


# ----------------------------------------------------------------------
# Inpainting backends
# ----------------------------------------------------------------------

def inpaint_lama(image_path: str, mask, output_path: str) -> None:
    """Use IOPaint CLI with LaMa model."""
    import cv2

    with tempfile.TemporaryDirectory() as td:
        img_dir = Path(td) / "img"
        mask_dir = Path(td) / "mask"
        out_dir = Path(td) / "out"
        img_dir.mkdir()
        mask_dir.mkdir()
        out_dir.mkdir()

        src_name = Path(image_path).name
        shutil_copy = Path(image_path).read_bytes()
        (img_dir / src_name).write_bytes(shutil_copy)
        cv2.imwrite(str(mask_dir / src_name), mask)

        cmd = [
            sys.executable, "-m", "iopaint", "run",
            "--model=lama",
            "--device=cpu",
            f"--image={img_dir}",
            f"--mask={mask_dir}",
            f"--output={out_dir}",
        ]
        print(f"[lama] {' '.join(cmd)}", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"iopaint failed:\n{result.stderr}")

        # iopaint outputs <src>.png in out_dir
        out_files = list(out_dir.glob(f"{Path(src_name).stem}.*"))
        if not out_files:
            raise RuntimeError(f"iopaint produced no output in {out_dir}")
        Path(output_path).write_bytes(out_files[0].read_bytes())


def inpaint_fast(image_path: str, mask, output_path: str) -> None:
    """Use cv2.inpaint with TELEA algorithm — fast for uniform backgrounds."""
    import cv2
    img = cv2.imread(image_path)
    result = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, result)


# ----------------------------------------------------------------------
# Rendering new text
# ----------------------------------------------------------------------

def render_text(
    cleaned_path: str,
    matches: Sequence[OcrMatch],
    replacements: Sequence[tuple[str, str]],
    font_path: str,
    font_size: int | None,
    color: tuple[int, int, int] | None,
    output_path: str,
) -> None:
    """Render new text at original bbox positions."""
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np

    img = Image.open(cleaned_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Build text-replacement map (find -> replace)
    repl_map = dict(replacements)
    original_img_arr = np.array(Image.open(cleaned_path).convert("RGB"))

    for m in matches:
        # Find which replacement applies to this match
        new_text = None
        for find, repl in repl_map.items():
            if find in m.text:
                new_text = m.text.replace(find, repl)
                break
        if new_text is None:
            continue

        x, y, w, h = m.bbox_rect()

        # Auto font size from height of original
        size = font_size or max(8, int(h * 0.85))
        font = ImageFont.truetype(font_path, size)

        # Auto color: median color of dark pixels within bbox (assume text = dark)
        if color is None:
            region = original_img_arr[max(y, 0):y + h, max(x, 0):x + w]
            if region.size > 0:
                gray = np.mean(region, axis=2)
                dark_mask = gray < np.percentile(gray, 30)
                if dark_mask.any():
                    median_color = tuple(int(c) for c in np.median(region[dark_mask], axis=0))
                else:
                    median_color = (0, 0, 0)
            else:
                median_color = (0, 0, 0)
            text_color = median_color
        else:
            text_color = color

        draw.text((x, y), new_text, font=font, fill=text_color)

    img.save(output_path)


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def replace_text_in_image(
    input_path: str,
    replacements: Sequence[tuple[str, str]],
    font_path: str = "C:/Windows/Fonts/arial.ttf",
    mode: str = "lama",
    output_path: str | None = None,
    use_regex: bool = False,
    font_size: int | None = None,
    color: tuple[int, int, int] | None = None,
    dilate_px: int = 4,
    ocr_lang: str = "ru,en",
    min_confidence: float = 0.7,
    dry_run: bool = False,
) -> dict:
    """Main public entry. Returns dict with summary."""
    import cv2

    _ensure_deps(mode)

    input_path = str(Path(input_path).resolve())
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.with_name(f"{p.stem}.replaced{p.suffix}"))

    print(f"[1/5] OCR {input_path}...", flush=True)
    all_matches = run_ocr(input_path, langs=ocr_lang)
    print(f"      → {len(all_matches)} text regions found", flush=True)

    # Collect matches for each find pattern
    selected: list[OcrMatch] = []
    summary_per_find = []
    for find, repl in replacements:
        hits = filter_matches(all_matches, find, use_regex=use_regex, min_confidence=min_confidence)
        summary_per_find.append({
            "find": find,
            "replace": repl,
            "matches": len(hits),
            "details": [{"text": h.text, "conf": round(h.confidence, 3), "bbox": h.bbox_rect()} for h in hits],
        })
        selected.extend(hits)

    if not selected:
        return {
            "status": "no_matches",
            "input": input_path,
            "output": None,
            "summary": summary_per_find,
            "message": "Ни один из find-паттернов не сматчился. Проверь OCR результат с --dry-run без фильтра.",
        }

    if dry_run:
        return {
            "status": "dry_run",
            "input": input_path,
            "output": None,
            "summary": summary_per_find,
            "message": f"Dry run: найдено {len(selected)} регионов. Запустить без --dry-run чтобы применить.",
        }

    print(f"[2/5] Building mask ({len(selected)} regions, dilate={dilate_px}px)...", flush=True)
    img = cv2.imread(input_path)
    if img is None:
        raise RuntimeError(f"OpenCV cannot read {input_path}")
    mask = build_mask(img.shape, selected, dilate_px=dilate_px)

    cleaned_path = str(Path(output_path).with_name(f"{Path(output_path).stem}.cleaned{Path(output_path).suffix}"))

    if mode == "lama":
        print(f"[3/5] Inpainting with LaMa (CPU, может занять 5-30 сек)...", flush=True)
        inpaint_lama(input_path, mask, cleaned_path)
    elif mode == "fast":
        print(f"[3/5] Inpainting with cv2 TELEA (fast)...", flush=True)
        inpaint_fast(input_path, mask, cleaned_path)
    else:
        raise ValueError(f"Unknown mode: {mode}. Expected 'lama' or 'fast'.")

    print(f"[4/5] Rendering new text with Pillow (font: {font_path})...", flush=True)
    if not Path(font_path).exists():
        raise FileNotFoundError(f"Font not found: {font_path}")
    render_text(
        cleaned_path=cleaned_path,
        matches=selected,
        replacements=replacements,
        font_path=font_path,
        font_size=font_size,
        color=color,
        output_path=output_path,
    )

    print(f"[5/5] Saved: {output_path}", flush=True)
    Path(cleaned_path).unlink(missing_ok=True)

    return {
        "status": "ok",
        "input": input_path,
        "output": output_path,
        "summary": summary_per_find,
        "message": f"Replaced {len(selected)} regions, saved to {output_path}",
    }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Replace text on raster image via OCR + inpaint.")
    p.add_argument("--input", required=True, help="Path to source image (.png/.jpg/.tiff)")
    p.add_argument("--find", action="append", required=True, help="Text to find. Can repeat for batch.")
    p.add_argument("--replace", action="append", required=True, help="Replacement text. Match --find by position.")
    p.add_argument("--regex", action="store_true", help="Treat --find as regex")
    p.add_argument("--font", default="C:/Windows/Fonts/arial.ttf", help="TTF font path (must support Cyrillic)")
    p.add_argument("--font-size", type=int, default=None, help="Font size in px (auto from bbox height if not set)")
    p.add_argument("--color", default=None, help="Hex color #RRGGBB for new text (auto from bbox median if not set)")
    p.add_argument("--mode", choices=["lama", "fast"], default="lama", help="Inpaint backend")
    p.add_argument("--ocr-lang", default="ru,en", help="PaddleOCR languages")
    p.add_argument("--dilate", type=int, default=4, help="Pixels to dilate mask around bbox")
    p.add_argument("--output", default=None, help="Output path (default: <input>.replaced.<ext>)")
    p.add_argument("--dry-run", action="store_true", help="Only show OCR matches, no inpaint/render")
    p.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    args = p.parse_args()
    if len(args.find) != len(args.replace):
        p.error("--find and --replace must come in pairs")
    return args


def main() -> int:
    args = _parse_args()
    color = None
    if args.color:
        c = args.color.lstrip("#")
        color = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

    result = replace_text_in_image(
        input_path=args.input,
        replacements=list(zip(args.find, args.replace)),
        font_path=args.font,
        mode=args.mode,
        output_path=args.output,
        use_regex=args.regex,
        font_size=args.font_size,
        color=color,
        dilate_px=args.dilate,
        ocr_lang=args.ocr_lang,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result["status"] in ("ok", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
