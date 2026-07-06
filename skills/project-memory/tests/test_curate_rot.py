"""Тесты curate_rot.py — переносимые: синтетический STATUS + смоделированная
реальность (несуществующий файл, прошедшая дата, отставание от журнала)."""
import json
import re
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import curate_rot  # noqa: E402

JOURNAL = "ЖУРНАЛ СЕССИЙ.md"


@pytest.fixture
def project(tmp_path):
    cl = tmp_path / "Claude"
    cl.mkdir()
    (cl / "STATUS.md").write_text(
        "# Объект — статус\n\n"
        "**Последнее обновление:** 2026-05-01\n\n"
        "## Сейчас в работе\n"
        "- ведомость: см. `docs/план.md`\n"
        "- ждём ответ поставщика до 2026-06-01\n"
        "- отчёт собран: `docs/отчёт.md`\n",
        encoding="utf-8")
    (cl / JOURNAL).write_text(
        "# Журнал\n\n"
        "## 2026-07-01 · DEV1 · вторая сессия\n**Сделано:** x\n\n"
        "## 2026-06-20 · DEV2 · первая сессия\n**Сделано:** y\n",
        encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "отчёт.md").write_text("готово", encoding="utf-8")
    # docs/план.md сознательно НЕ создаём — протухшая ссылка
    return tmp_path


def run_propose(root):
    out_dir = curate_rot.propose(root)
    data = json.loads((out_dir / "proposals.json").read_text(encoding="utf-8"))
    return out_dir, data


def test_find_project_root_walks_up(project):
    sub = project / "docs"
    assert curate_rot.find_project_root(sub) == project
    assert curate_rot.find_project_root(project / "Claude") == project


def test_find_project_root_none_outside(tmp_path):
    assert curate_rot.find_project_root(tmp_path) is None


def test_propose_finds_missing_file(project):
    _, data = run_propose(project)
    hits = [p for p in data["proposals"] if p["signal"] == "file-missing"]
    assert hits and any("план.md" in " ".join(p["evidence"]) for p in hits)


def test_propose_finds_passed_date(project):
    _, data = run_propose(project)
    hits = [p for p in data["proposals"] if p["signal"] == "date-passed"]
    assert hits and any("2026-06-01" in " ".join(p["evidence"]) for p in hits)


def test_propose_finds_status_behind_journal(project):
    _, data = run_propose(project)
    hits = [p for p in data["proposals"]
            if p["signal"] == "status-behind-journal"]
    assert hits
    ev = " ".join(hits[0]["evidence"])
    assert "2026-05-01" in ev and "2026-07-01" in ev


def test_propose_finds_done_file_changed(project):
    _, data = run_propose(project)
    assert any(p["signal"] == "done-file-changed" for p in data["proposals"])


def test_all_proposals_valid(project):
    _, data = run_propose(project)
    assert data["proposals"], "на явной синтетике должны быть предложения"
    ids = [p["id"] for p in data["proposals"]]
    assert len(ids) == len(set(ids))
    for p in data["proposals"]:
        assert p["evidence"], p["id"]                     # непустой evidence
        assert p["target"].startswith("Claude/"), p["id"]
        assert p["action"] in ("modify", "flag", "archive")
        assert p["confidence"] in ("high", "medium", "low")
        assert p["source"] == "script"


def test_propose_readonly_inputs(project):
    status = project / "Claude" / "STATUS.md"
    journal = project / "Claude" / JOURNAL
    before = (status.read_text(encoding="utf-8"),
              journal.read_text(encoding="utf-8"))
    run_propose(project)
    after = (status.read_text(encoding="utf-8"),
             journal.read_text(encoding="utf-8"))
    assert before == after


def test_report_written_and_relative(project):
    out_dir, _ = run_propose(project)
    blob = ((out_dir / "REPORT.md").read_text(encoding="utf-8")
            + (out_dir / "proposals.json").read_text(encoding="utf-8"))
    assert not re.search(r"[A-Za-z]:[\\/]", blob), "абсолютные пути запрещены"
