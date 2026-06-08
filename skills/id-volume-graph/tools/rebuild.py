# -*- coding: utf-8 -*-
"""Пересобрать graph.json из id_volume_extract.json после ручной правки модели.

Запускать ПОД интерпретатором, где установлен graphify, портативно:
    uv tool run --from graphifyy python tools/rebuild.py
(или напрямую python из venv graphifyy). Затем для визуала из папки скилла:
    graphify export html
"""
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
OUT = SKILL / "graphify-out"
OUT.mkdir(parents=True, exist_ok=True)

from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.export import to_json

extraction = json.loads((SKILL / "id_volume_extract.json").read_text(encoding="utf-8"))
G = build_from_json(extraction)
communities = cluster(G)
cohesion = score_all(G, communities)
to_json(G, communities, str(OUT / "graph.json"))

# Метки сообществ + анализ для отчёта (best-effort; метки можно дополнить вручную)
labels_path = OUT / ".graphify_labels.json"
labels = {}
if labels_path.exists():
    labels = {int(k): v for k, v in json.loads(labels_path.read_text(encoding="utf-8")).items()}
for cid in communities:
    labels.setdefault(cid, "Сообщество " + str(cid))
labels_path.write_text(json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8")

print(f"rebuilt: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
print("далее (из папки скилла): graphify export html")
