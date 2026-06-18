# -*- coding: utf-8 -*-
"""
Find the largest empty rectangle on a layout render to place a table.
Raster approach: occupied = dark pixels on the PNG (= any visible graphics:
plan, leaders, stamps, "Приложение к АОСР", frame). Free = white.

Pixel<->model mapping uses AutoCAD view params at PNGOUT time:
  VIEWCTR (ctrx,ctry) = view center in current-space coords,
  VIEWSIZE (vsize)    = view height in model units.
  model_w = vsize * px_w/px_h ;  mm-per-pixel = vsize/px_h.

Usage:
  find_free_zone.py PNG CTRX CTRY VSIZE [COLW] [GAP] [CLEAR_MM] [MINW_MM] [MINH_MM] [THRESH] [K]
Prints zone + writes C:/temp/free_zone.txt (TAB key/value) for the pipeline.
"""
import sys
import numpy as np
from PIL import Image


def max_empty_rect(occ, min_w_cells, min_h_cells):
    """Largest-area rectangle of False (free) cells meeting min dims.
    occ: bool HxW (True=occupied). Returns (area, top, left, bottom, right) inclusive grid coords."""
    R, C = occ.shape
    heights = np.zeros(C, dtype=int)
    best = (0, 0, 0, 0, 0)
    for r in range(R):
        heights = np.where(occ[r], 0, heights + 1)
        st = []  # (start_col, height)
        for c in range(C + 1):
            h = int(heights[c]) if c < C else 0
            start = c
            while st and st[-1][1] > h:
                s_col, s_h = st.pop()
                w_cells = c - s_col
                if s_h >= min_h_cells and w_cells >= min_w_cells:
                    area = s_h * w_cells
                    if area > best[0]:
                        best = (area, r - s_h + 1, s_col, r, c - 1)
                start = s_col
            st.append((start, h))
    return best


def main():
    a = sys.argv
    png = a[1]
    ctrx, ctry, vsize = float(a[2]), float(a[3]), float(a[4])
    colw = float(a[5]) if len(a) > 5 else 126.0
    gap = float(a[6]) if len(a) > 6 else 4.0
    clear_mm = float(a[7]) if len(a) > 7 else 4.0
    minw_mm = float(a[8]) if len(a) > 8 else 60.0
    minh_mm = float(a[9]) if len(a) > 9 else 60.0
    thresh = int(a[10]) if len(a) > 10 else 180
    K = int(a[11]) if len(a) > 11 else 5

    img = Image.open(png).convert("L")
    arr = np.asarray(img)
    px_h, px_w = arr.shape
    mmpp = vsize / px_h                       # mm per pixel
    model_w = vsize * px_w / px_h
    x_min = ctrx - model_w / 2.0
    y_max = ctry + vsize / 2.0

    occ_full = arr < thresh                   # dark = occupied

    # downsample to K-pixel grid: cell occupied if ANY dark pixel inside (built-in clearance)
    Hc, Wc = px_h // K, px_w // K
    occ = occ_full[:Hc * K, :Wc * K].reshape(Hc, K, Wc, K).any(axis=(1, 3))

    # extra clearance: dilate occupied by clear cells
    clear_cells = max(0, int(round(clear_mm / (K * mmpp))))
    if clear_cells:
        d = occ.copy()
        for dr in range(-clear_cells, clear_cells + 1):
            for dc in range(-clear_cells, clear_cells + 1):
                d |= np.roll(np.roll(occ, dr, axis=0), dc, axis=1)
        occ = d

    min_w_cells = max(1, int(round(minw_mm / (K * mmpp))))
    min_h_cells = max(1, int(round(minh_mm / (K * mmpp))))
    area, top, left, bottom, right = max_empty_rect(occ, min_w_cells, min_h_cells)

    if area == 0:
        print("NO FREE ZONE meeting mins (minw=%.0f minh=%.0f mm)" % (minw_mm, minh_mm))
        sys.exit(2)

    # grid cells -> pixels -> model
    left_px, right_px = left * K, (right + 1) * K
    top_px, bottom_px = top * K, (bottom + 1) * K
    x_left = x_min + left_px * mmpp
    x_right = x_min + right_px * mmpp
    y_top = y_max - top_px * mmpp
    y_bottom = y_max - bottom_px * mmpp

    inset = clear_mm
    zx_right = x_right - inset
    zy_top = y_top - inset
    zw = (x_right - x_left) - 2 * inset
    zh = (y_top - y_bottom) - 2 * inset
    maxcols = max(1, int((zw + gap) // (colw + gap)))

    print("PNG %dx%d  mmpp=%.3f  model_w=%.1f" % (px_w, px_h, mmpp, model_w))
    print("free rect model: x[%.1f..%.1f] y[%.1f..%.1f]  w=%.1f h=%.1f" %
          (x_left, x_right, y_bottom, y_top, x_right - x_left, y_top - y_bottom))
    print("ZONE xright=%.1f ytop=%.1f width=%.1f height=%.1f maxcols=%d" %
          (zx_right, zy_top, zw, zh, maxcols))
    with open(r"C:/temp/free_zone.txt", "w", encoding="utf-8") as f:
        f.write("XRIGHT\t%.2f\nYTOP\t%.2f\nWIDTH\t%.2f\nHEIGHT\t%.2f\nMAXCOLS\t%d\n"
                % (zx_right, zy_top, zw, zh, maxcols))


if __name__ == "__main__":
    main()
