# -*- coding: utf-8 -*-
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from gen_project_agents import render_project_agents, main, MARKER

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
