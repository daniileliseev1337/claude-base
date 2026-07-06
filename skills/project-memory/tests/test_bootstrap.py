"""Тесты bootstrap.py — переносимые (tmp_path, без привязки к машине)."""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import bootstrap  # noqa: E402

JOURNAL = "ЖУРНАЛ СЕССИЙ.md"
CORE = ["Claude/CLAUDE.md", "Claude/README.md", f"Claude/{JOURNAL}",
        "Claude/STATUS.md", "CLAUDE.md"]


def test_creates_all_files(tmp_path):
    report = bootstrap.bootstrap("Тестовый объект", tmp_path)
    assert sorted(p for _, p in report) == sorted(CORE)
    assert all(m == "+" for m, _ in report)
    for c in CORE:
        assert (tmp_path / c).exists(), c


def test_placeholders_substituted(tmp_path):
    bootstrap.bootstrap("Тестовый объект", tmp_path)
    for c in CORE:
        text = (tmp_path / c).read_text(encoding="utf-8")
        for ph in ("[ПРОЕКТ]", "[ДАТА]", "[УСТРОЙСТВО]"):
            assert ph not in text, f"{ph} остался в {c}"
        assert "Тестовый объект" in text, c
    status = (tmp_path / "Claude" / "STATUS.md").read_text(encoding="utf-8")
    assert date.today().isoformat() in status


def test_idempotent_no_clobber(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    status = tmp_path / "Claude" / "STATUS.md"
    status.write_text("МОИ ПРАВКИ", encoding="utf-8")
    report = bootstrap.bootstrap("П", tmp_path)
    assert status.read_text(encoding="utf-8") == "МОИ ПРАВКИ"
    assert all(m == "=" for m, _ in report)


def test_recreates_missing_only(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    (tmp_path / "Claude" / "README.md").unlink()
    keeper = tmp_path / "Claude" / "STATUS.md"
    keeper.write_text("keep", encoding="utf-8")
    marks = {p: m for m, p in bootstrap.bootstrap("П", tmp_path)}
    assert marks["Claude/README.md"] == "+"
    assert keeper.read_text(encoding="utf-8") == "keep"


def test_force_single_file(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    status = tmp_path / "Claude" / "STATUS.md"
    readme = tmp_path / "Claude" / "README.md"
    status.write_text("st", encoding="utf-8")
    readme.write_text("rd", encoding="utf-8")
    bootstrap.bootstrap("П", tmp_path, force=["STATUS.md"])
    assert status.read_text(encoding="utf-8") != "st"   # перезаписан
    assert readme.read_text(encoding="utf-8") == "rd"   # не тронут


def test_force_bare_claude_md_ambiguous_touches_nothing(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    root_c = tmp_path / "CLAUDE.md"
    inner_c = tmp_path / "Claude" / "CLAUDE.md"
    root_c.write_text("r", encoding="utf-8")
    inner_c.write_text("i", encoding="utf-8")
    bootstrap.bootstrap("П", tmp_path, force=["CLAUDE.md"])  # имя неоднозначно
    assert root_c.read_text(encoding="utf-8") == "r"
    assert inner_c.read_text(encoding="utf-8") == "i"


def test_force_by_relpath(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    inner_c = tmp_path / "Claude" / "CLAUDE.md"
    inner_c.write_text("i", encoding="utf-8")
    bootstrap.bootstrap("П", tmp_path, force=["Claude/CLAUDE.md"])
    assert inner_c.read_text(encoding="utf-8") != "i"


def test_force_root_pointer_via_dot_slash(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    root_c = tmp_path / "CLAUDE.md"
    inner_c = tmp_path / "Claude" / "CLAUDE.md"
    root_c.write_text("r", encoding="utf-8")
    inner_c.write_text("i", encoding="utf-8")
    bootstrap.bootstrap("П", tmp_path, force=["./CLAUDE.md"])
    assert root_c.read_text(encoding="utf-8") != "r"    # корневой перезаписан
    assert inner_c.read_text(encoding="utf-8") == "i"   # внутренний не тронут


def test_no_absolute_paths_in_output(tmp_path):
    bootstrap.bootstrap("П", tmp_path)
    for c in CORE:
        text = (tmp_path / c).read_text(encoding="utf-8")
        assert not re.search(r"[A-Za-z]:[\\/]", text), c


def test_unknown_profile_rejected(tmp_path):
    import pytest
    with pytest.raises(SystemExit):
        bootstrap.bootstrap("П", tmp_path, profile="id-tom")


def test_cli_smoke(tmp_path):
    r = subprocess.run(
        [sys.executable, str(TOOLS / "bootstrap.py"), "Объект",
         "--target", str(tmp_path)],
        capture_output=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "Claude" / JOURNAL).exists()
