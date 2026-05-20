"""
Regression-тесты для skills/image-text-replace.

Покрывают функции которые ломались в реальных итерациях (см.
~/.claude/skills/image-text-replace/LESSONS-LEARNED.md):

- smart_cap_height_detect — без неё font_size +30% от реальной cap height
  (Урок 2: «Размер из full OCR bbox»).
- find_neighbor_cell_reference — reference = ячейка-сосед, не сам label
  (Урок 5: «reference = ячейка-сосед, не сам label»).
- compute_midline_paste_y — midline alignment
  (Урок 4: «position via midline»).
- _find_font_size_for_height — calibration size discovery.

Все тесты детерминированы, без LLM, без OCR/SD моделей.
Зависимости: numpy + Pillow (уже стоят на любой машине с
image-text-replace в production).
"""
from pathlib import Path

import numpy as np
import pytest

# pipeline и calibration уже доступны через conftest.py (sys.path)
from pipeline import (
    OcrMatch,
    compute_midline_paste_y,
    find_neighbor_cell_reference,
    smart_cap_height_detect,
    unify_font_size_for_batch,
)
from calibration import _find_font_size_for_height


# ---------- Helpers ----------

def make_ocr_match(text: str, x: int, y: int, w: int, h: int,
                    conf: float = 0.95) -> OcrMatch:
    """Build OcrMatch with axis-aligned bbox at (x, y, w, h)."""
    bbox = (
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
    )
    return OcrMatch(text=text, bbox=bbox, confidence=conf)


# ---------- TEST CLASS: smart_cap_height_detect ----------

class TestSmartCapHeightDetect:
    """LESSONS-LEARNED §3: detect cap height ignoring descenders."""

    def test_simple_dark_band(self):
        """Rows 5..15 with 50% dark pixels → cap_top=5, cap_bottom=15."""
        arr = np.full((30, 100, 3), 255, dtype=np.uint8)
        arr[5:16, :50, :] = 0  # rows 5..15 inclusive, 50% width dark
        result = smart_cap_height_detect(arr, 0, 0, 100, 30,
                                          core_ratio=0.3)
        assert result["cap_top"] == 5
        assert result["cap_bottom"] == 15
        assert result["cap_height"] == 11

    def test_ignores_thin_descender(self):
        """Descender row (10% dark, below 30% core_ratio) must be ignored.

        Это ключевой урок про '16 877,50' с запятой descender —
        запятая дает 1-row thin descender, его нужно отбрасывать.
        """
        arr = np.full((40, 100, 3), 255, dtype=np.uint8)
        # core rows: 5..15 with 50% dark
        arr[5:16, :50, :] = 0
        # descender row: 20 with 10% dark
        arr[20, :10, :] = 0
        result = smart_cap_height_detect(arr, 0, 0, 100, 40,
                                          core_ratio=0.3)
        assert result["cap_top"] == 5
        assert result["cap_bottom"] == 15  # 20-я строка отброшена

    def test_fallback_when_no_core_rows(self):
        """Тhin pattern below core_ratio everywhere → return bbox as-is."""
        arr = np.full((30, 100, 3), 255, dtype=np.uint8)
        # 10% dark everywhere — below 30% threshold
        arr[5:25, :10, :] = 0
        result = smart_cap_height_detect(arr, 0, 0, 100, 30,
                                          core_ratio=0.3)
        # Fallback: full bbox returned
        assert result["cap_top"] == 0
        assert result["cap_bottom"] == 30
        assert result["cap_height"] == 30

    def test_empty_region(self):
        """No dark pixels at all → fallback to bbox dimensions."""
        arr = np.full((30, 100, 3), 255, dtype=np.uint8)
        result = smart_cap_height_detect(arr, 0, 0, 100, 30)
        assert result["cap_height"] == 30


# ---------- TEST CLASS: find_neighbor_cell_reference ----------

class TestFindNeighborCellReference:
    """LESSONS-LEARNED §5: reference = digit-cell sibling, not label itself."""

    def test_finds_digit_cell_to_the_right(self):
        label = make_ocr_match("Итоговая сумма (вкл. НДС)",
                                x=100, y=200, w=200, h=30)
        digit = make_ocr_match("16 877,50", x=400, y=200, w=100, h=30)
        text_only = make_ocr_match("Примечание", x=600, y=200, w=80, h=30)

        result = find_neighbor_cell_reference(
            [label, digit, text_only], label,
            side="right", row_tolerance_px=15,
        )
        assert result is digit

    def test_skips_non_digit_text(self):
        """Если справа только не-числовой текст — вернёт None."""
        label = make_ocr_match("Итоговая сумма", x=100, y=200, w=200, h=30)
        text_only = make_ocr_match("текст справа", x=400, y=200, w=100, h=30)

        result = find_neighbor_cell_reference(
            [label, text_only], label, side="right",
        )
        assert result is None

    def test_respects_row_tolerance(self):
        """Digit на другой строке (y слишком далеко) — пропускается."""
        label = make_ocr_match("сумма", x=100, y=200, w=100, h=30)
        far_digit = make_ocr_match("12345", x=400, y=400, w=100, h=30)

        result = find_neighbor_cell_reference(
            [label, far_digit], label,
            side="right", row_tolerance_px=15,
        )
        assert result is None

    def test_picks_closest_when_multiple_digits(self):
        """Несколько digit-кандидатов справа — берём ближайший к label."""
        label = make_ocr_match("сумма", x=100, y=200, w=100, h=30)
        near = make_ocr_match("100", x=220, y=200, w=50, h=30)
        far = make_ocr_match("999", x=500, y=200, w=50, h=30)

        result = find_neighbor_cell_reference(
            [label, near, far], label, side="right",
        )
        assert result is near

    def test_side_left(self):
        """side='left' ищет на левой стороне от label."""
        label = make_ocr_match("сумма", x=400, y=200, w=100, h=30)
        digit_left = make_ocr_match("250", x=200, y=200, w=80, h=30)

        result = find_neighbor_cell_reference(
            [label, digit_left], label, side="left",
        )
        assert result is digit_left


# ---------- TEST CLASS: compute_midline_paste_y ----------

class TestComputeMidlinePasteY:
    """LESSONS-LEARNED §4: chiefly midline alignment (pure arithmetic)."""

    def test_perfect_alignment(self):
        """Label и cell midline совпадают → paste at midline minus canvas mid."""
        label = {"top_y": 100, "bottom_y": 200}        # midline 150
        cell = {"cap_top": 100, "cap_bottom": 200}     # midline 150
        canvas = {"top_y": 0, "bottom_y": 40}          # canvas midline 20

        paste_y = compute_midline_paste_y(
            label, cell, text_canvas_height=40,
            text_anchors_in_canvas=canvas,
        )
        # target_midline = (150+150)/2 = 150; paste_y = 150 - 20 = 130
        assert paste_y == 130

    def test_averaged_when_misaligned(self):
        """Если label и cell midline разные — target = их среднее."""
        label = {"top_y": 100, "bottom_y": 200}    # midline 150
        cell = {"cap_top": 110, "cap_bottom": 230}  # midline 170
        canvas = {"top_y": 0, "bottom_y": 40}       # canvas midline 20

        paste_y = compute_midline_paste_y(
            label, cell, text_canvas_height=40,
            text_anchors_in_canvas=canvas,
        )
        # target = (150+170)/2 = 160; paste_y = 160 - 20 = 140
        assert paste_y == 140

    def test_negative_paste_y_allowed(self):
        """Возможен отрицательный paste_y если canvas выше target."""
        label = {"top_y": 0, "bottom_y": 20}        # midline 10
        cell = {"cap_top": 0, "cap_bottom": 20}     # midline 10
        canvas = {"top_y": 0, "bottom_y": 100}      # canvas midline 50

        paste_y = compute_midline_paste_y(
            label, cell, text_canvas_height=100,
            text_anchors_in_canvas=canvas,
        )
        # target = 10; paste_y = 10 - 50 = -40
        assert paste_y == -40


# ---------- TEST CLASS: _find_font_size_for_height ----------

class TestFindFontSizeForHeight:
    """calibration.py — font-size search for target cap height."""

    def test_arial_returns_plausible_size(self):
        """Arial Regular на target_h=20 → размер в plausible range."""
        font_path = "C:/Windows/Fonts/arial.ttf"
        if not Path(font_path).exists():
            pytest.skip("Arial not on this Windows install")

        size = _find_font_size_for_height(font_path, target_h=20)
        assert 15 <= size <= 50, f"Size {size} outside plausible range"

    def test_times_bold_returns_plausible_size(self):
        """Times Bold на target_h=20 → размер в plausible range."""
        font_path = "C:/Windows/Fonts/timesbd.ttf"
        if not Path(font_path).exists():
            pytest.skip("Times Bold not on this Windows install")

        size = _find_font_size_for_height(font_path, target_h=20)
        assert 15 <= size <= 50, f"Size {size} outside plausible range"

    def test_fallback_on_missing_font(self):
        """Несуществующий font path → fallback 24."""
        size = _find_font_size_for_height("C:/nonexistent/no.ttf",
                                            target_h=20)
        assert size == 24

    def test_increasing_target_h_increases_size(self):
        """Чем больше target_h, тем больше font_size (monotonicity)."""
        font_path = "C:/Windows/Fonts/arial.ttf"
        if not Path(font_path).exists():
            pytest.skip("Arial not on this Windows install")

        s10 = _find_font_size_for_height(font_path, target_h=10)
        s30 = _find_font_size_for_height(font_path, target_h=30)
        assert s30 >= s10, f"s10={s10}, s30={s30} — monotonicity broken"


# ---------- TEST CLASS: unify_font_size_for_batch ----------

def _make_strip_image(strips: list[tuple[int, int, int, int]]):
    """Build synthetic image with N non-overlapping horizontal text-like strips.

    Each strip described as (y_top, height, x_start, dark_width).
    BBox of each OcrMatch tightly fits its strip (no padding) — это даёт
    smart_cap_height_detect возможность вернуть height точно равный height
    strip-а, без overshoot от перекрывающих соседей.

    Returns: (image, list[OcrMatch])
    """
    max_y = max(y_top + height for y_top, height, _, _ in strips) + 10
    arr = np.full((max_y, 200, 3), 255, dtype=np.uint8)
    matches = []
    for i, (y_top, height, x_start, dark_w) in enumerate(strips):
        y_bot = y_top + height - 1
        arr[y_top:y_bot + 1, x_start:x_start + dark_w, :] = 0
        bx, by, bw, bh = x_start, y_top, dark_w, height
        bbox = ((bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh))
        matches.append(OcrMatch(text=f"row{i}", bbox=bbox, confidence=0.95))
    return arr, matches


class TestUnifyFontSizeForBatch:
    """LESSONS-LEARNED §6: unified font_size for batch text replacement."""

    def test_median_simple(self):
        """5 strips height=10, non-overlapping → median=10 → font_size=15."""
        strips = [(20 + i * 20, 10, 10, 100) for i in range(5)]
        arr, matches = _make_strip_image(strips)
        font_size, diag = unify_font_size_for_batch(arr, matches, cap_ratio=0.66)

        assert diag["n"] == 5
        assert diag["median"] == 10
        assert font_size == int(10 / 0.66)  # 15

    def test_median_ignores_outlier(self):
        """4 strips height=10 + 1 outlier height=30 → median=10 (not 30, not mean=14)."""
        strips = [
            (20, 10, 10, 100),
            (50, 10, 10, 100),
            (80, 10, 10, 100),
            (110, 10, 10, 100),
            (140, 30, 10, 100),  # outlier
        ]
        arr, matches = _make_strip_image(strips)
        font_size, diag = unify_font_size_for_batch(arr, matches, cap_ratio=0.66)

        assert diag["n"] == 5
        assert diag["median"] == 10  # outlier doesn't pull median
        assert diag["mean"] > diag["median"]
        assert diag["std"] > 0

    def test_empty_returns_safe_fallback(self):
        """Empty matches → font_size=24 (safe default), n=0."""
        arr = np.zeros((10, 10, 3), dtype=np.uint8)
        font_size, diag = unify_font_size_for_batch(arr, [], cap_ratio=0.66)
        assert font_size == 24
        assert diag["n"] == 0
        assert diag["heights"] == []

    def test_cap_ratio_affects_size(self):
        """Same heights, different cap_ratio → different font_size.

        Regular (0.66) даёт БОЛЬШИЙ font_size чем Bold (0.70)
        для одной cap_height (font_size = cap_height / cap_ratio).
        """
        strips = [(20 + i * 20, 10, 10, 100) for i in range(3)]
        arr, matches = _make_strip_image(strips)
        fs_reg, _ = unify_font_size_for_batch(arr, matches, cap_ratio=0.66)
        fs_bold, _ = unify_font_size_for_batch(arr, matches, cap_ratio=0.70)
        assert fs_reg > fs_bold

    def test_real_kp_ls_ahp_heights(self):
        """Воспроизведение КП ЛС АХП v7: 12 Regular cells heights
        [18,18,19,18,17,18,18,18,17,17,19,20] → median=18 → font_size=27.
        """
        observed = [18, 18, 19, 18, 17, 18, 18, 18, 17, 17, 19, 20]
        # Non-overlapping strips with gap between
        y_cursor = 20
        strips = []
        for h in observed:
            strips.append((y_cursor, h, 10, 100))
            y_cursor += h + 5  # 5px gap
        arr, matches = _make_strip_image(strips)
        font_size, diag = unify_font_size_for_batch(arr, matches, cap_ratio=0.66)
        assert diag["median"] == 18
        assert font_size == 27
