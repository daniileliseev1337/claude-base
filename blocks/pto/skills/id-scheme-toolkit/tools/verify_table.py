# -*- coding: utf-8 -*-
"""
Verify a built ACAD_TABLE against its xlsx source (graphics reviewer, value axis).
Pairs (position : last-column value) are dumped from AutoCAD by (c7:verify-dump)
into C:/temp/acad_pairs.txt; this script reparses the SAME xlsx table (reusing
parse_table from xlsx2acadtable) and cross-checks every position's last column
("Всего"/"Объём"). renumber must match what generation used.

Usage:
  python verify_table.py <xlsx> <sheet> <table_index> <renumber> [acad_pairs.txt]
Exit 0 = PASSED, 1 = FAILED.
"""
import sys, io
from xlsx2acadtable import parse_table


def main():
    a = sys.argv
    xlsx, sheet, tidx, renum = a[1], a[2], int(a[3]), a[4]
    ncols = int(a[5]) if len(a) > 5 else 4
    pairs_path = a[6] if len(a) > 6 else r"C:\temp\acad_pairs.txt"
    renumber = (renum == "1")

    rows, _, _, _, _, qty_col = parse_table(xlsx, sheet, tidx, renumber, ncols)
    expected, pos = {}, 0
    for rtype, cells in rows:
        if rtype == "data":
            pos += 1
            expected[pos] = cells[qty_col - 1]   # quantity column ('Всего'/'Объём')

    acad = {}
    # AutoCAD writes acad_pairs.txt in cp1251 (qty may be non-ASCII, e.g. swapped 'м')
    for tok in io.open(pairs_path, encoding="cp1251").read().split():
        k, v = tok.split(":")
        acad[int(k)] = v

    mism = [("pos%d xlsx=%s acad=%s" % (p, expected[p], acad.get(p, "<MISSING>")))
            for p in sorted(expected) if expected[p] != acad.get(p)]
    extra = sorted(p for p in acad if p not in expected)

    print("xlsx positions: %d | acad positions: %d" % (len(expected), len(acad)))
    print("mismatches: %d" % len(mism))
    for m in mism:
        print("  ", m)
    if extra:
        print("extra in acad:", extra)
    ok = (not mism and not extra and len(expected) == len(acad))
    print("RESULT:", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
