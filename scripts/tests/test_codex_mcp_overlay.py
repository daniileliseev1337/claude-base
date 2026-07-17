# -*- coding: utf-8 -*-
"""Контракт единственного parser-а overlay доменного MCP-моста."""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))


def test_overlay_parser_normalizes_names(tmp_path):
    from codex_mcp_overlay import load_overlay_names, overlay_path

    p = overlay_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"enable": ["excel", "time", "excel"]}), encoding="utf-8")

    assert load_overlay_names(tmp_path) == ["excel", "time"]


def test_overlay_parser_rejects_invalid_payload(tmp_path):
    from codex_mcp_overlay import OverlayError, load_overlay_names, overlay_path

    p = overlay_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text('{"enable": "excel"}', encoding="utf-8")

    with pytest.raises(OverlayError, match="списком строк"):
        load_overlay_names(tmp_path)
