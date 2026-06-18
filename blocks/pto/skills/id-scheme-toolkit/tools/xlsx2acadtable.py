# -*- coding: utf-8 -*-
"""
GCH W-layer: xlsx VOR sheet -> table_data.txt (cp1251) for gen_table.lsp.
Splits a sheet into VOR tables (by "Ведомость объёмов работ" rows),
classifies rows (title/header/section/data), optionally renumbers, writes data file.

Usage:
  python xlsx2acadtable.py <xlsx> <sheet> <table_index> <layout> <ins_x> <ins_y>
                           <cols_csv> <style> <thmax> <margin> <target_h> <renumber>
                           [gap xstart ytop maxcols]   # multi-column mode
  renumber: 1 = header№ -> "№", data positions -> 1..N ; 0 = verbatim

parse_table() is importable (used by verify_table.py) so verification reuses the
exact same slicing/classification/renumbering as generation.
"""
import sys, io, openpyxl

# symbols absent from cp1251 -> AutoCAD control codes / ASCII (so they survive the data file)
_SUBS = {"∅": "%%c", "⌀": "%%c", "Ø": "%%c", "ø": "%%c",  # diameter -> %%c
" ": " ", " ": " "}


def sanitize(s):
    for k, v in _SUBS.items():
        s = s.replace(k, v)
    return s


def cellstr(v):
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip()


def find_tables(ws):
    """Return [(start_row, end_row), ...] for each VOR table on the sheet."""
    starts = []
    for r in range(1, ws.max_row + 1):
        if cellstr(ws.cell(row=r, column=1).value).startswith("Ведомость объ"):
            starts.append(r)
    return [(s, (starts[i + 1] - 1) if i + 1 < len(starts) else ws.max_row)
            for i, s in enumerate(starts)]


def detect_qty_col(header_cells):
    """1-based index of the quantity column ('Всего'/'Объём'/'Кол-во'); default = last."""
    for i, h in enumerate(header_cells):
        hl = h.strip().lower()
        if ("всего" in hl) or ("объ" in hl) or ("кол" in hl):
            return i + 1
    return len(header_cells)


def parse_table(xlsx, sheet, tidx, renumber, ncols=4):
    """Slice + classify one VOR table into ncols columns.
    Returns (rows, bounds, s, e, npos, qty_col). rows: (type, cells[]).
    section = first cell non-empty and all the rest empty."""
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb[sheet]
    maxc = ws.max_column
    bounds = find_tables(ws)
    if not bounds:
        return [], [], None, None, 0, ncols
    s, e = bounds[tidx]
    rows, pos, qty_col = [], 0, ncols
    for r in range(s, e + 1):
        vals = [cellstr(ws.cell(row=r, column=c).value) for c in range(1, maxc + 1)]
        cells = (vals + [""] * ncols)[:ncols]
        if not any(x.strip() for x in vals):
            continue
        if r == s:
            rows.append(("title", [cells[0]]))
        elif r == s + 1:
            head = cells[:]
            qty_col = detect_qty_col(head)
            if renumber:
                head[0] = "№"
            rows.append(("header", head))
        elif cells[0] and not any(c.strip() for c in cells[1:]):
            rows.append(("section", [cells[0]]))
        else:
            if renumber:
                pos += 1
                cells[0] = str(pos)
            rows.append(("data", cells))
    return rows, bounds, s, e, pos, qty_col


def main():
    a = sys.argv
    (xlsx, sheet, tidx, layout, insx, insy, cols_csv, style, thmax, margin, target_h, renum) = (
        a[1], a[2], int(a[3]), a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12])
    cols = cols_csv.split(",")
    ncols = len(cols)
    renumber = (renum == "1")
    multi = (len(a) >= 17)
    if multi:
        gap, xstart, ytop, maxcols = a[13], a[14], a[15], a[16]

    rows, bounds, s, e, pos, qty_col = parse_table(xlsx, sheet, tidx, renumber, ncols)
    print("tables:", bounds)
    if not rows:
        print("NO TABLES FOUND"); return

    out = io.open(r"C:\temp\table_data.txt", "w", encoding="cp1251", errors="replace")
    T = "\t"
    out.write("LAYOUT" + T + layout + "\n")
    out.write("INS" + T + insx + T + insy + "\n")
    out.write("COLS" + T + T.join(cols) + "\n")
    out.write("NROWS" + T + str(len(rows)) + "\n")
    out.write("STYLE" + T + style + "\n")
    out.write("THMAX" + T + thmax + "\n")
    out.write("MARGIN" + T + margin + "\n")
    out.write("TARGETH" + T + target_h + "\n")
    out.write("QTYCOL" + T + str(qty_col) + "\n")
    if multi:
        out.write("GAP" + T + gap + "\n")
        out.write("XSTART" + T + xstart + "\n")
        out.write("YTOP" + T + ytop + "\n")
        out.write("MAXCOLS" + T + maxcols + "\n")
    for idx, (rtype, cells) in enumerate(rows):
        out.write("ROW" + T + str(idx) + T + rtype + T + T.join(sanitize(c) for c in cells) + "\n")
    out.close()
    print("OK wrote C:\\temp\\table_data.txt | rows=%d cols=%d positions=%d table=%d (xlsx %d-%d) renumber=%s"
          % (len(rows), ncols, pos, tidx, s, e, renumber))


if __name__ == "__main__":
    main()
