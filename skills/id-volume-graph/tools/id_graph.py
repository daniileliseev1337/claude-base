#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Обёртка query/path/explain по графу устройства тома ИД — независимо от cwd вызывающего.

Граф лежит рядом со скиллом (graphify-out/graph.json). graphify CLI ищет graphify-out
относительно cwd, поэтому запускаем его с cwd = папка скилла.

Примеры:
  python id_graph.py query "АОСР документ качества реестр"
  python id_graph.py path "Позиция (оборуд./материал)" "Документ качества"
  python id_graph.py explain "Каскад изменений"
"""
import subprocess, sys, os, shutil

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
if not args or args[0] not in ("query", "path", "explain"):
    print('usage: python id_graph.py query|path|explain ARGS...')
    print('  query "<слова из меток узлов>"   — BFS-обход (что связано)')
    print('  path "Узел A" "Узел B"            — кратчайший путь зависимостей')
    print('  explain "Узел"                    — все связи узла')
    sys.exit(1)

gf = shutil.which("graphify") or "graphify"
env = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.exit(subprocess.run([gf] + args, cwd=SKILL_DIR, env=env).returncode)
