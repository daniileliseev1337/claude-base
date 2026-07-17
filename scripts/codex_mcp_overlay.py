# -*- coding: utf-8 -*-
"""Единый parser overlay доменного MCP-моста для sync, патчера и hook-а."""
import json
from pathlib import Path


class OverlayError(ValueError):
    """Overlay нельзя безопасно прочитать или привести к контракту списка имён."""


def overlay_path(home: Path) -> Path:
    return home / ".claude" / ".local-state" / "codex-mcp-overlay.json"


def normalize_overlay_names(names: list) -> list:
    """Проверить и нормализовать имена overlay без знания MCP-конфигурации."""
    if not isinstance(names, list):
        raise OverlayError("enable должен быть списком строк")
    if not all(isinstance(name, str) and name.strip() for name in names):
        raise OverlayError("enable должен быть списком непустых строк")
    return sorted(set(names))


def load_overlay_names(home: Path) -> list:
    """Прочитать overlay; отсутствие файла означает выключенный мост."""
    p = overlay_path(home)
    if not p.exists():
        return []
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise OverlayError("корень должен быть объектом")
        return normalize_overlay_names(payload["enable"])
    except OverlayError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise OverlayError(str(error)) from error
