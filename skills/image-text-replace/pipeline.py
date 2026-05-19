#!/usr/bin/env python
"""
image-text-replace pipeline v0.2.

Заменяет указанный текст на растровом изображении (скан, JPEG, PNG):
1. OCR через EasyOCR (RU+EN) -> текст + bbox координаты
2. Фильтр по запросу пользователя (literal / regex)
3. Mask из bbox с расширением (dilate)
4. Inpaint: IOPaint LaMa (default) либо cv2.inpaint TELEA (fast mode)
5. Render нового текста через Pillow в том же месте
6. Сохранение result рядом с оригиналом

v0.2 changelog:
- Switch OCR engine PaddleOCR -> EasyOCR. Причина: paddleocr 3.x
  тянет модели с baidu CDN, на корп-сети не работает.
- PIL-loaded image для обхода cv2.imread ANSI-path issue (папки с
  кириллицей в пути).
- Singleton OCR reader (cache) для batch-обработки.
- Helper `find_value_near_label()` для кейса "Метка: значение".
- find/replace теперь поддерживает мульти-OCR-результаты (join
  соседних bbox'ов в одну строку).

CLI usage:
    python pipeline.py --input scan.png \\
        --find "Ф.2024.123456789" \\
        --replace "Ф.2026.987654321" \\
        --font "C:/Windows/Fonts/arial.ttf" \\
        --mode lama

Python lib:
    from pipeline import replace_text_in_image, run_ocr, find_value_near_label
    matches = run_ocr("scan.png")
    label_bbox, value_match = find_value_near_label(matches, r"Итоговая сумма")
    # ... compute new value ...
    replace_text_in_image("scan.png",
        replacements=[(value_match.text, "new value")],
        font_path="C:/Windows/Fonts/arial.ttf")

Зависимости (ставятся через setup-extras.ps1):
    easyocr, iopaint, Pillow, opencv-python, numpy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence


# ----------------------------------------------------------------------
# Lazy deps installer
# ----------------------------------------------------------------------

_IMPORT_MAP = {
    "easyocr": "easyocr",
    "Pillow": "PIL",
    "opencv-python": "cv2",
    "numpy": "numpy",
    "iopaint": "iopaint",
}


def _ensure_deps(mode: str) -> None:
    required = ["easyocr", "Pillow", "opencv-python", "numpy"]
    if mode == "lama":
        required.append("iopaint")
    missing: list[str] = []
    for pkg in required:
        import_name = _IMPORT_MAP[pkg]
        try:
            __import__(import_name)
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
        """Axis-aligned bounding rectangle: (x, y, w, h)."""
        xs = [p[0] for p in self.bbox]
        ys = [p[1] for p in self.bbox]
        x, y = min(xs), min(ys)
        return x, y, max(xs) - x, max(ys) - y

    def center_y(self) -> int:
        ys = [p[1] for p in self.bbox]
        return (min(ys) + max(ys)) // 2

    def height_px(self) -> int:
        return self.bbox_rect()[3]


# ----------------------------------------------------------------------
# OCR (EasyOCR with PIL-load workaround)
# ----------------------------------------------------------------------

_READER_CACHE: dict[tuple[str, ...], object] = {}


def _get_reader(langs: Sequence[str]):
    import easyocr
    key = tuple(sorted(langs))
    if key not in _READER_CACHE:
        _READER_CACHE[key] = easyocr.Reader(list(langs), gpu=False, verbose=False)
    return _READER_CACHE[key]


def _load_image_as_array(image_path: str):
    """Read image via Pillow (handles Unicode paths) → numpy RGB array."""
    from PIL import Image
    import numpy as np
    return np.array(Image.open(image_path).convert("RGB"))


def run_ocr(image_path: str, langs: Sequence[str] = ("ru", "en")) -> list[OcrMatch]:
    """Run EasyOCR on image, return list of OcrMatch."""
    reader = _get_reader(langs)
    img = _load_image_as_array(image_path)
    raw = reader.readtext(img)
    matches: list[OcrMatch] = []
    for region in raw:
        bbox_pts, text, conf = region
        bbox_tuple = tuple((int(p[0]), int(p[1])) for p in bbox_pts)
        matches.append(OcrMatch(text=text, bbox=bbox_tuple, confidence=float(conf)))
    return matches


def filter_matches(
    matches: Sequence[OcrMatch],
    find_pattern: str,
    use_regex: bool,
    min_confidence: float = 0.5,
) -> list[OcrMatch]:
    """Pick matches whose text matches user's pattern."""
    if use_regex:
        rx = re.compile(find_pattern)
        return [m for m in matches if rx.search(m.text) and m.confidence >= min_confidence]
    return [m for m in matches if find_pattern in m.text and m.confidence >= min_confidence]


def find_value_near_label(
    matches: Sequence[OcrMatch],
    label_pattern: str,
    side: str = "right",
    row_tolerance_px: int = 20,
    use_regex: bool = True,
) -> Optional[tuple[OcrMatch, OcrMatch]]:
    """For 'Label: value' patterns. Find label match, then the nearest
    OcrMatch on the same row (right side by default).

    Returns (label_match, value_match) or None.
    """
    label_hits = filter_matches(matches, label_pattern, use_regex=use_regex)
    if not label_hits:
        return None
    label_match = max(label_hits, key=lambda m: m.confidence)
    lx, ly, lw, lh = label_match.bbox_rect()
    label_right = lx + lw
    label_left = lx
    label_cy = label_match.center_y()
    candidates = [
        m for m in matches
        if m is not label_match
        and abs(m.center_y() - label_cy) <= row_tolerance_px
    ]
    if side == "right":
        candidates = [m for m in candidates if m.bbox_rect()[0] >= label_right - 10]
        candidates.sort(key=lambda m: m.bbox_rect()[0])
    elif side == "left":
        candidates = [m for m in candidates if (m.bbox_rect()[0] + m.bbox_rect()[2]) <= label_left + 10]
        candidates.sort(key=lambda m: -(m.bbox_rect()[0] + m.bbox_rect()[2]))
    else:
        raise ValueError(f"side must be 'left' or 'right', got {side!r}")
    if not candidates:
        return None
    return label_match, candidates[0]


# ----------------------------------------------------------------------
# Mask building
# ----------------------------------------------------------------------

def build_mask(image_shape: tuple[int, int, ...], matches: Iterable[OcrMatch], dilate_px: int = 4):
    """Binary mask (0/255) covering match bboxes + dilation."""
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

def _ascii_safe_cache_dir() -> Path:
    """Return an ASCII-only cache directory for torch/iopaint models.

    Windows + Python + Cyrillic username breaks model loading
    (`~/.cache/torch/...` resolves to garbled bytes for usernames like
    'Даниил'). Use C:\\iopaint-cache as a stable fallback.
    """
    if os.name == "nt":
        candidate = Path(r"C:\iopaint-cache")
    else:
        candidate = Path.home() / ".cache" / "iopaint-pipeline"
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def inpaint_lama(image_path: str, mask, output_path: str) -> None:
    """Use IOPaint CLI with LaMa model. Sets TORCH_HOME to ASCII-safe path."""
    from PIL import Image

    cache_root = _ascii_safe_cache_dir()
    env = os.environ.copy()
    env["TORCH_HOME"] = str(cache_root / "torch")
    env["XDG_CACHE_HOME"] = str(cache_root / "xdg")
    env["HF_HOME"] = str(cache_root / "hf")
    (cache_root / "torch").mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        img_dir = Path(td) / "img"
        mask_dir = Path(td) / "mask"
        out_dir = Path(td) / "out"
        img_dir.mkdir()
        mask_dir.mkdir()
        out_dir.mkdir()

        ascii_name = "input.png"
        Image.open(image_path).convert("RGB").save(img_dir / ascii_name)
        Image.fromarray(mask).save(mask_dir / ascii_name)

        cmd = [
            sys.executable, "-m", "iopaint", "run",
            "--model=lama",
            "--device=cpu",
            f"--model-dir={cache_root / 'torch'}",
            f"--image={img_dir}",
            f"--mask={mask_dir}",
            f"--output={out_dir}",
        ]
        print(f"[lama] cache={cache_root}", flush=True)
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"iopaint failed (rc={result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

        out_files = list(out_dir.glob("input.*"))
        if not out_files:
            raise RuntimeError(f"iopaint produced no output in {out_dir}")
        Image.open(out_files[0]).save(output_path)


def inpaint_fast(image_path: str, mask, output_path: str) -> None:
    """cv2.inpaint with TELEA — fast for uniform backgrounds."""
    import cv2
    from PIL import Image
    import numpy as np
    img = np.array(Image.open(image_path).convert("RGB"))
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    result = cv2.inpaint(bgr, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)).save(output_path)


# ----------------------------------------------------------------------
# Rendering new text
# ----------------------------------------------------------------------

def render_text(
    cleaned_path: str,
    original_path: str,
    matches: Sequence[OcrMatch],
    replacements: Sequence[tuple[str, str]],
    font_path: str,
    font_size: Optional[int],
    color: Optional[tuple[int, int, int]],
    output_path: str,
) -> None:
    """Draw `replacements` text onto the inpainted image at original bbox positions.

    Color auto-sampling reads dark pixels from `original_path` (BEFORE
    inpainting) — otherwise we'd sample from the inpainted region which
    no longer contains text and gives near-white = invisible result.
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    img = Image.open(cleaned_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    # Sample colors from ORIGINAL (pre-inpaint), not cleaned.
    original_arr = np.array(Image.open(original_path).convert("RGB"))

    for m in matches:
        new_text = None
        for find, repl in replacements:
            if find in m.text:
                new_text = m.text.replace(find, repl)
                break
        if new_text is None:
            continue

        x, y, w, h = m.bbox_rect()

        size = font_size or max(8, int(h * 0.85))
        font = ImageFont.truetype(font_path, size)

        if color is None:
            region = original_arr[max(y, 0):y + h, max(x, 0):x + w]
            if region.size > 0:
                gray = np.mean(region, axis=2)
                # Берём только САМЫЕ тёмные 10% — это ядро штрихов букв.
                # 30 percentile захватывал anti-aliased edge-pixels → median
                # получался серым (~rgb 98) вместо чёрного. Bug пойман на
                # КП К7 АХП 2026-05-19, user noted "20% сероватое".
                dark_mask = gray < np.percentile(gray, 10)
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
    output_path: Optional[str] = None,
    use_regex: bool = False,
    font_size: Optional[int] = None,
    color: Optional[tuple[int, int, int]] = None,
    dilate_px: int = 4,
    ocr_langs: Sequence[str] = ("ru", "en"),
    min_confidence: float = 0.5,
    dry_run: bool = False,
    preloaded_matches: Optional[Sequence[OcrMatch]] = None,
) -> dict:
    """Main public entry. Returns dict with summary.

    `preloaded_matches` — если уже сделали OCR заранее (например, для
    нескольких find/replace на одном изображении в разных шагах),
    можно передать готовый список и не делать OCR повторно.
    """
    from PIL import Image

    _ensure_deps(mode)

    input_path = str(Path(input_path).resolve())
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.with_name(f"{p.stem}.replaced{p.suffix}"))

    if preloaded_matches is None:
        print(f"[1/5] OCR {input_path}...", flush=True)
        all_matches = run_ocr(input_path, langs=ocr_langs)
        print(f"      -> {len(all_matches)} text regions found", flush=True)
    else:
        all_matches = list(preloaded_matches)
        print(f"[1/5] Using {len(all_matches)} preloaded OCR matches", flush=True)

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
            "message": "Ни один из find-паттернов не сматчился. Запусти с --dry-run и проверь OCR результаты.",
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
    pil_img = Image.open(input_path).convert("RGB")
    img_shape = (pil_img.height, pil_img.width, 3)
    mask = build_mask(img_shape, selected, dilate_px=dilate_px)

    cleaned_path = str(Path(output_path).with_name(f"{Path(output_path).stem}.cleaned{Path(output_path).suffix}"))

    if mode == "lama":
        print(f"[3/5] Inpainting with LaMa (CPU, ~5-30 сек)...", flush=True)
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
        original_path=input_path,
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
    p.add_argument("--input", required=True)
    p.add_argument("--find", action="append", required=True, help="Text to find. Can repeat.")
    p.add_argument("--replace", action="append", required=True, help="Replacement. Pairs with --find by position.")
    p.add_argument("--regex", action="store_true")
    p.add_argument("--font", default="C:/Windows/Fonts/arial.ttf")
    p.add_argument("--font-size", type=int, default=None)
    p.add_argument("--color", default=None, help="Hex #RRGGBB or omit for auto")
    p.add_argument("--mode", choices=["lama", "fast"], default="lama")
    p.add_argument("--ocr-lang", default="ru,en")
    p.add_argument("--dilate", type=int, default=4)
    p.add_argument("--output", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--min-conf", type=float, default=0.5)
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
        ocr_langs=tuple(s.strip() for s in args.ocr_lang.split(",")),
        min_confidence=args.min_conf,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result["status"] in ("ok", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
