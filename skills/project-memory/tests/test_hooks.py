"""Smoke-тесты хуков (Windows/PowerShell 5.1). Переносимы между Windows-машинами;
на не-Windows скипаются."""
import json
import os
import subprocess
import time
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / "tools" / "hooks"
JOURNAL = "ЖУРНАЛ СЕССИЙ.md"

pytestmark = pytest.mark.skipif(os.name != "nt",
                                reason="хуки PowerShell — Windows-only")


def run_hook(script, payload, state_dir):
    env = dict(os.environ, PROJECT_MEMORY_STATE_DIR=str(state_dir))
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(HOOKS / script)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True, env=env, timeout=90)


def run_find_project(start_path):
    """find_project.ps1 берёт вход через параметр -StartPath, не через
    JSON-stdin (это переиспользуемый скрипт для будущих хуков, не сам хук)."""
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(HOOKS / "find_project.ps1"),
         "-StartPath", str(start_path)],
        capture_output=True, timeout=90)


def _norm(p):
    """Нормализация пути для сравнения (регистр диска/кейс/трейлинг-слеш)."""
    return str(Path(p).resolve()).rstrip("\\/").lower()


def make_project(base):
    """Проект — в подпапке proj; state-папка тестов живёт РЯДОМ (вне корня
    проекта, как и в проде ~/.claude/.local-state), иначе маркер сам
    триггерил бы скан изменений."""
    proj = base / "proj"
    (proj / "Claude").mkdir(parents=True)
    j = proj / "Claude" / JOURNAL
    # шапка — как в живых журналах: правила + шаблон записи в fenced-блоке;
    # строка "## ГГГГ-ММ-ДД…" внутри код-блока НЕ должна считаться записью
    j.write_text("# Журнал\n\n"
                 "> Правила: запись сверху.\n\n"
                 "**Шаблон записи:**\n\n"
                 "```\n"
                 "## ГГГГ-ММ-ДД · УСТРОЙСТВО · тема\n"
                 "**Сделано:** …\n"
                 "```\n\n"
                 "---\n\n"
                 "## 2026-07-01 · TEST · тема A\n**Сделано:** x\n\n"
                 "## 2026-06-20 · TEST · тема B\n**Сделано:** y\n\n"
                 "## 2026-06-10 · TEST · тема C\n**Сделано:** z\n",
                 encoding="utf-8")
    return proj, j


def test_start_noop_outside_project(tmp_path):
    r = run_hook("session_start.ps1",
                 {"session_id": "s1", "cwd": str(tmp_path)}, tmp_path / "st")
    assert r.returncode == 0
    assert r.stdout.strip() == b""


def test_start_bootstraps_project_with_only_claude_md(tmp_path):
    proj = tmp_path / "plain-project"
    proj.mkdir()
    (proj / "CLAUDE.md").write_text("# Только CLAUDE\n", encoding="utf-8")

    r = run_hook("session_start.ps1",
                 {"session_id": "single", "cwd": str(proj)}, tmp_path / "st")

    assert r.returncode == 0
    agents = proj / "AGENTS.md"
    assert agents.exists()
    assert "Только CLAUDE" in agents.read_text(encoding="utf-8")


def test_start_bootstraps_plain_project_from_subfolder(tmp_path):
    proj = tmp_path / "plain-project"
    sub = proj / "docs" / "nested"
    sub.mkdir(parents=True)
    (proj / "CLAUDE.md").write_text("# Корень найден\n", encoding="utf-8")

    r = run_hook("session_start.ps1",
                 {"session_id": "nested", "cwd": str(sub)}, tmp_path / "st")

    assert r.returncode == 0
    assert (proj / "AGENTS.md").exists()
    assert not (sub / "AGENTS.md").exists()


def test_start_allows_project_root_named_claude(tmp_path):
    proj = tmp_path / "Claude"
    proj.mkdir()
    (proj / "CLAUDE.md").write_text("# Проект с таким именем\n", encoding="utf-8")

    r = run_hook("session_start.ps1",
                 {"session_id": "named-claude", "cwd": str(proj)}, tmp_path / "st")

    assert r.returncode == 0
    assert (proj / "AGENTS.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_start_preserves_foreign_agents_md(tmp_path):
    proj = tmp_path / "foreign-project"
    proj.mkdir()
    (proj / "CLAUDE.md").write_text("# Claude source\n", encoding="utf-8")
    agents = proj / "AGENTS.md"
    agents.write_text("# Ручной AGENTS\n", encoding="utf-8")

    r = run_hook("session_start.ps1",
                 {"session_id": "foreign", "cwd": str(proj)}, tmp_path / "st")

    assert r.returncode == 0
    assert agents.read_text(encoding="utf-8") == "# Ручной AGENTS\n"


def test_start_updates_stale_generated_agents_md(tmp_path):
    proj = tmp_path / "stale-project"
    proj.mkdir()
    source = proj / "CLAUDE.md"
    source.write_text("# Первая версия\n", encoding="utf-8")
    state = tmp_path / "st"
    run_hook("session_start.ps1",
             {"session_id": "stale-1", "cwd": str(proj)}, state)

    source.write_text("# Вторая версия\n", encoding="utf-8")
    r = run_hook("session_start.ps1",
                 {"session_id": "stale-2", "cwd": str(proj)}, state)

    assert r.returncode == 0
    assert "Вторая версия" in (proj / "AGENTS.md").read_text(encoding="utf-8")


def test_start_prints_journal_top_and_writes_marker(tmp_path):
    proj, _ = make_project(tmp_path)
    state = tmp_path / "st"
    r = run_hook("session_start.ps1",
                 {"session_id": "s2", "cwd": str(proj)}, state)
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace")
    assert "[project-memory]" in out
    assert "2026-07-01" in out and "2026-06-20" in out   # верхние 2 записи
    assert "2026-06-10" not in out                        # третья не печатается
    marker = state / "session_s2.json"
    assert marker.exists()
    data = json.loads(marker.read_text(encoding="utf-8-sig"))
    assert data["reminded"] is False and data["start_epoch"] > 0


def test_start_from_subfolder_finds_root(tmp_path):
    proj, _ = make_project(tmp_path)
    sub = proj / "docs" / "razdel"
    sub.mkdir(parents=True)
    r = run_hook("session_start.ps1",
                 {"session_id": "s3", "cwd": str(sub)}, tmp_path / "st")
    assert r.returncode == 0
    assert b"project-memory" in r.stdout


def test_end_noop_without_marker(tmp_path):
    r = run_hook("session_end.ps1",
                 {"session_id": "none", "stop_hook_active": False},
                 tmp_path / "st")
    assert r.returncode == 0


def test_end_full_cycle_reminds_once(tmp_path):
    proj, _ = make_project(tmp_path)
    state = tmp_path / "st"
    run_hook("session_start.ps1",
             {"session_id": "s5", "cwd": str(proj)}, state)
    time.sleep(1.2)                       # запас к точности mtime
    (proj / "работа.md").write_text("x", encoding="utf-8")
    r1 = run_hook("session_end.ps1",
                  {"session_id": "s5", "stop_hook_active": False}, state)
    assert r1.returncode == 2
    assert b"journal" in r1.stderr.lower()
    r2 = run_hook("session_end.ps1",
                  {"session_id": "s5", "stop_hook_active": False}, state)
    assert r2.returncode == 0             # напоминание строго один раз


def test_end_quiet_when_journal_updated(tmp_path):
    proj, j = make_project(tmp_path)
    state = tmp_path / "st"
    run_hook("session_start.ps1",
             {"session_id": "s6", "cwd": str(proj)}, state)
    time.sleep(1.2)
    (proj / "работа.md").write_text("x", encoding="utf-8")
    j.write_text("## 2026-07-06 · TEST · новая\n"
                 + j.read_text(encoding="utf-8"), encoding="utf-8")
    r = run_hook("session_end.ps1",
                 {"session_id": "s6", "stop_hook_active": False}, state)
    assert r.returncode == 0


def test_end_quiet_when_nothing_changed(tmp_path):
    proj, _ = make_project(tmp_path)
    state = tmp_path / "st"
    run_hook("session_start.ps1",
             {"session_id": "s7", "cwd": str(proj)}, state)
    time.sleep(1.2)
    r = run_hook("session_end.ps1",
                 {"session_id": "s7", "stop_hook_active": False}, state)
    assert r.returncode == 0


def test_end_respects_stop_hook_active(tmp_path):
    proj, _ = make_project(tmp_path)
    state = tmp_path / "st"
    run_hook("session_start.ps1",
             {"session_id": "s8", "cwd": str(proj)}, state)
    time.sleep(1.2)
    (proj / "работа.md").write_text("x", encoding="utf-8")
    r = run_hook("session_end.ps1",
                 {"session_id": "s8", "stop_hook_active": True}, state)
    assert r.returncode == 0              # анти-луп guard


# --- find_project.ps1: общий walk-up (путь ИЛИ cwd -> проект памяти) ---

def test_find_project_from_nested_nonexistent_file_path(tmp_path):
    """StartPath - файл ВНУТРИ несуществующих подпапок (sub/deep не создаются);
    walk-up должен идти строковыми операциями, не требовать существования
    промежуточных уровней."""
    proj, j = make_project(tmp_path)
    deep_file = proj / "sub" / "deep" / "file.txt"
    r = run_find_project(deep_file)
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace").strip()
    assert out, f"expected JSON on stdout, got empty; stderr={r.stderr!r}"
    data = json.loads(out)
    assert _norm(data["root"]) == _norm(proj)
    assert _norm(data["journal"]) == _norm(j)


def test_find_project_kontekst_field_present_and_absent(tmp_path):
    proj, _ = make_project(tmp_path)
    deep_file = proj / "sub" / "deep" / "file.txt"

    r_no = run_find_project(deep_file)
    data_no = json.loads(r_no.stdout.decode("utf-8", "replace").strip())
    assert data_no["kontekst"] == ""

    kontekst = proj / "Claude" / "КОНТЕКСТ.md"
    kontekst.write_text("# Контекст\n", encoding="utf-8")
    r_yes = run_find_project(deep_file)
    data_yes = json.loads(r_yes.stdout.decode("utf-8", "replace").strip())
    assert data_yes["kontekst"] != ""
    assert _norm(data_yes["kontekst"]) == _norm(kontekst)


def test_find_project_directory_start_path(tmp_path):
    """StartPath указывает прямо на существующую директорию проекта (не файл)."""
    proj, j = make_project(tmp_path)
    r = run_find_project(proj)
    assert r.returncode == 0
    data = json.loads(r.stdout.decode("utf-8", "replace").strip())
    assert _norm(data["root"]) == _norm(proj)
    assert _norm(data["journal"]) == _norm(j)


def test_find_project_no_project_found(tmp_path):
    outside = tmp_path / "empty_no_project"
    outside.mkdir()
    r = run_find_project(outside)
    assert r.returncode == 0
    assert r.stdout.decode("utf-8", "replace").strip() == ""


def test_find_project_cyrillic_path(tmp_path):
    """Кириллица и в имени папки проекта, и в промежуточных подпапках -
    проверка UTF-8 обвязки скрипта."""
    proj = tmp_path / "Проект Тест"
    (proj / "Claude").mkdir(parents=True)
    j = proj / "Claude" / JOURNAL
    j.write_text("## 2026-07-01 · TEST · тема\n**Сделано:** x\n",
                 encoding="utf-8")
    start = proj / "подпапка" / "файл.txt"
    r = run_find_project(start)
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace").strip()
    assert out, f"expected JSON on stdout, got empty; stderr={r.stderr!r}"
    data = json.loads(out)
    assert _norm(data["root"]) == _norm(proj)
    assert _norm(data["journal"]) == _norm(j)
