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


def parse_table(xlsx, sheet, tidx, renumber):
    """Slice + classify one VOR table. Returns (rows, bounds, s, e, npos).
    rows: list of (type, cells[]) where type in title|header|section|data."""
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb[sheet]
    maxc = ws.max_column
    bounds = find_tables(ws)
    if not bounds:
        return [], [], None, None, 0
    s, e = bounds[tidx]
    rows, pos = [], 0
    for r in range(s, e + 1):
        vals = [cellstr(ws.cell(row=r, column=c).value) for c in range(1, maxc + 1)]
        av, bv, cv, dv = (vals + ["", "", "", ""])[:4]
        if not any(x.strip() for x in vals):
            continue
        if r == s:
            rows.append(("title", [av]))
        elif r == s + 1:
            rows.append(("header", [("№" if renumber else av), bv, cv, dv]))
        elif av and not bv and not cv and not dv:
            rows.append(("section", [av]))
        else:
            if renumber:
                pos += 1
                av = str(pos)
            rows.append(("data", [av, bv, cv, dv]))
    return rows, bounds, s, e, pos


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

    rows, bounds, s, e, pos = parse_table(xlsx, sheet, tidx, renumber)
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
    if multi:
        out.write("GAP" + T + gap + "\n")
        out.write("XSTART" + T + xstart + "\n")
        out.write("YTOP" + T + ytop + "\n")
        out.write("MAXCOLS" + T + maxcols + "\n")
    for idx, (rtype, cells) in enumerate(rows):
        out.write("ROW" + T + str(idx) + T + rtype + T + T.join(cells) + "\n")
    out.close()
    print("OK wrote C:\\temp\\table_data.txt | rows=%d cols=%d positions=%d table=%d (xlsx %d-%d) renumber=%s"
          % (len(rows), ncols, pos, tidx, s, e, renumber))


if __name__ == "__main__":
    main()
