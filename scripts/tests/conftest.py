# -*- coding: utf-8 -*-
"""Фикстура мини-канона для тестов codex_sync: минимальный ~/.claude + ~/.codex во временной папке."""
import json
import pytest


@pytest.fixture
def make_canon(tmp_path):
    def _make(home=None):
        home = home or tmp_path
        claude = home / ".claude"
        for d in ("core", "codex-layer", "agents", "skills"):
            (claude / d).mkdir(parents=True, exist_ok=True)
        (home / ".codex").mkdir(exist_ok=True)
        (claude / "core" / "AGENTS.core.md").write_text(
            "# Ядро\nПравило 1: думай, прежде чем действовать.\n", encoding="utf-8")
        (claude / "codex-layer" / "AGENTS.codex.md").write_text(
            "# Слой Codex\nОперационка Codex.\n", encoding="utf-8")
        (claude / "codex-layer" / "mcp-whitelist.json").write_text(
            json.dumps({"allow": ["time"]}), encoding="utf-8")
        (claude / "codex-layer" / "skills-manifest.json").write_text(
            json.dumps({"enable": []}), encoding="utf-8")
        (claude / "codex-layer" / "targets.json").write_text(
            json.dumps({"enable": ["codex"]}), encoding="utf-8")
        (claude / "codex-layer" / "base.toml").write_text(
            "[agents]\nmax_threads = 6\n", encoding="utf-8")
        (home / ".claude.json").write_text(json.dumps({"mcpServers": {
            "time": {"command": "uvx", "args": ["mcp-server-time"]},
            "excel": {"command": "uvx", "args": ["excel-mcp-server"]},  # вне whitelist
        }}), encoding="utf-8")
        (claude / "agents" / "тест-агент.md").write_text(
            "---\nname: тест-агент\ndescription: тестовый ревьюер\nmodel: sonnet\ntools: Read\n---\nТело агента.\n",
            encoding="utf-8")
        (home / ".codex" / "config.toml").write_text("x = 1\n", encoding="utf-8")
        prof = claude / "codex-layer" / "profiles"
        prof.mkdir(exist_ok=True)
        (prof / "plus.toml").write_text('model = "gpt-5.6-luna"\n', encoding="utf-8")
        (prof / "pro.toml").write_text('model = "gpt-5.6-sol"\n', encoding="utf-8")
        return home
    return _make
