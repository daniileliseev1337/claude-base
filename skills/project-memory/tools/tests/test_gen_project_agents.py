# -*- coding: utf-8 -*-
import os
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from gen_project_agents import render_project_agents, main, project_agents_status, MARKER

def _proj(tmp_path):
    (tmp_path / "Claude").mkdir()
    (tmp_path / "CLAUDE.md").write_text(
        "@~/.claude/core/AGENTS.core.md\n# Проект X\nПамять — в Claude/.\nClaude Code читает этот файл.\n",
        encoding="utf-8")
    (tmp_path / "Claude" / "CLAUDE.md").write_text("# Память проекта\nПорядок сессии.\n", encoding="utf-8")
    return tmp_path

def test_render_flattens_and_neutralizes(tmp_path):
    out = render_project_agents(_proj(tmp_path))
    assert MARKER in out.splitlines()[0]
    assert "@~/" not in out                      # @import вырезан
    assert "Claude Code" not in out              # vendor-нейтрализация
    assert "Проект X" in out and "Порядок сессии" in out

def test_render_none_without_core(tmp_path):
    assert render_project_agents(tmp_path) is None

def test_main_writes_and_refuses_foreign(tmp_path):
    root = _proj(tmp_path)
    assert main(root) == 0
    agents = root / "AGENTS.md"
    assert MARKER in agents.read_text(encoding="utf-8").splitlines()[0]
    assert main(root) == 0                       # перегенерация своего — ок
    agents.write_text("# Чужой AGENTS.md (написан Codex)\n", encoding="utf-8")
    assert main(root) == 2                       # чужой файл не затираем
    assert "Чужой" in agents.read_text(encoding="utf-8")

def test_main_refuses_empty_foreign_agents_md(tmp_path):
    root = _proj(tmp_path)
    (root / "AGENTS.md").write_text("", encoding="utf-8")
    assert main(root) == 2                       # пустой файл — не наш, не трогаем и не падаем
    assert (root / "AGENTS.md").read_text(encoding="utf-8") == ""


def test_main_refuses_spoofed_ownership_marker(tmp_path):
    root = _proj(tmp_path)
    agents = root / "AGENTS.md"
    agents.write_text("<!-- not-generated-by: gen_project_agents -->\n# Ручной файл\n",
                      encoding="utf-8")

    assert main(root) == 2
    assert "Ручной файл" in agents.read_text(encoding="utf-8")


def test_main_refuses_dangling_symlink_before_missing_check(tmp_path, monkeypatch):
    root = _proj(tmp_path)
    agents = root / "AGENTS.md"
    original = pathlib.Path.is_symlink
    monkeypatch.setattr(pathlib.Path, "is_symlink",
                        lambda self: self == agents or original(self))

    assert project_agents_status(root) == "foreign"
    assert main(root) == 2
    assert not agents.exists()


def test_main_refuses_agents_md_directory(tmp_path):
    root = _proj(tmp_path)
    (root / "AGENTS.md").mkdir()

    assert project_agents_status(root) == "foreign"
    assert main(root) == 2
    assert (root / "AGENTS.md").is_dir()


def test_main_replaces_hardlink_without_changing_other_project(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    root_a = _proj(tmp_path / "a")
    root_b = _proj(tmp_path / "b")
    (root_a / "CLAUDE.md").write_text("# Проект A\n", encoding="utf-8")
    (root_b / "CLAUDE.md").write_text("# Проект B\n", encoding="utf-8")
    assert main(root_a) == 0
    os.link(root_a / "AGENTS.md", root_b / "AGENTS.md")
    before_a = (root_a / "AGENTS.md").read_text(encoding="utf-8")

    assert project_agents_status(root_b) == "stale"
    assert main(root_b) == 0

    assert (root_a / "AGENTS.md").read_text(encoding="utf-8") == before_a
    assert "Проект B" in (root_b / "AGENTS.md").read_text(encoding="utf-8")
    assert not os.path.samefile(root_a / "AGENTS.md", root_b / "AGENTS.md")


def test_status_distinguishes_missing_current_stale_and_foreign(tmp_path):
    root = _proj(tmp_path)
    assert project_agents_status(root) == "missing"

    assert main(root) == 0
    assert project_agents_status(root) == "current"

    (root / "CLAUDE.md").write_text("# Изменённый проект\n", encoding="utf-8")
    assert project_agents_status(root) == "stale"

    (root / "AGENTS.md").write_text("# Ручной канон\n", encoding="utf-8")
    assert project_agents_status(root) == "foreign"


def test_main_does_not_rewrite_current_generated_file(tmp_path):
    root = _proj(tmp_path)
    assert main(root) == 0
    agents = root / "AGENTS.md"
    old = 1_700_000_000
    agents.touch()
    os.utime(agents, (old, old))

    assert main(root) == 0
    assert agents.stat().st_mtime == old


def test_main_updates_stale_generated_file(tmp_path):
    root = _proj(tmp_path)
    assert main(root) == 0
    (root / "CLAUDE.md").write_text("# Новая инструкция\n", encoding="utf-8")

    assert main(root) == 0
    assert "Новая инструкция" in (root / "AGENTS.md").read_text(encoding="utf-8")


def test_main_bootstraps_project_with_only_root_claude_md(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Единственный источник\n", encoding="utf-8")

    assert main(tmp_path) == 0
    agents = tmp_path / "AGENTS.md"
    assert agents.exists()
    assert "Единственный источник" in agents.read_text(encoding="utf-8")
