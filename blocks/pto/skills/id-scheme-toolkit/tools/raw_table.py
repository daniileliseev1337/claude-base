# -*- coding: utf-8 -*-
"""
Build table_data.txt (cp1251) for gen_table.lsp from an EXPLICIT JSON spec —
for non-VOR tables that have no xlsx source (reference tables, specs, etc.).
Reuses sanitize() so ∅/⌀ etc. survive cp1251.

JSON: {"tables":[ {
    "layout": "...", "ins": [x, y], "cols": [w1, w2, ...],
    "style": "ГОСТ", "thmax": 2.0, "margin": 0.2, "target_h": 60, "qtycol": 0,
    "rows": [ ["title","..."], ["header","c1","c2",...], ["section","..."],
              ["data","c1","c2",...], ... ]
}, ... ] }

Usage:  python raw_table.py spec.json <table_index>   -> C:/temp/table_data.txt
"""
import sys, io, json
from xlsx2acadtable import sanitize


def main():
    spec = json.load(io.open(sys.argv[1], encoding="utf-8"))
    t = spec["tables"][int(sys.argv[2])]
    cols = [str(c) for c in t["cols"]]
    T = "\t"
    out = io.open(r"C:\temp\table_data.txt", "w", encoding="cp1251", errors="replace")
    out.write("LAYOUT" + T + t["layout"] + "\n")
    out.write("INS" + T + str(t["ins"][0]) + T + str(t["ins"][1]) + "\n")
    out.write("COLS" + T + T.join(cols) + "\n")
    out.write("NROWS" + T + str(len(t["rows"])) + "\n")
    out.write("STYLE" + T + t.get("style", "ГОСТ") + "\n")
    out.write("THMAX" + T + str(t.get("thmax", 2.0)) + "\n")
    out.write("MARGIN" + T + str(t.get("margin", 0.2)) + "\n")
    out.write("TARGETH" + T + str(t["target_h"]) + "\n")
    out.write("QTYCOL" + T + str(t.get("qtycol", len(cols))) + "\n")
    for idx, row in enumerate(t["rows"]):
        rtype, cells = row[0], row[1:]
        out.write("ROW" + T + str(idx) + T + rtype + T + T.join(sanitize(c) for c in cells) + "\n")
    out.close()
    print("OK raw table %s -> C:/temp/table_data.txt (rows=%d cols=%d)"
          % (sys.argv[2], len(t["rows"]), len(cols)))


if __name__ == "__main__":
    main()
