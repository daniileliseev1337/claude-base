"""Тесты блокирующего гейта мутаций project-memory (Windows/PowerShell 5.1):
- log-tool-usage.ps1 (PostToolUse) - регистрация чтения Claude\\КОНТЕКСТ.md,
- project_gate.ps1 (PreToolUse) - блокировка Write/Edit/MultiEdit/NotebookEdit/Task
  в проекте памяти, пока КОНТЕКСТ.md этой сессией не прочитан.

Переносимы между Windows-машинами; на не-Windows скипаются. Файл НЕЗАВИСИМ от
test_hooks.py (его параллельно правит другая задача) - своя копия make_project.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.name != "nt",
                                 reason="хуки PowerShell - Windows-only")

CLAUDE_HOME = Path(__file__).resolve().parents[3]     # .../.claude (skills/project-memory/tests -> up 3)
HOOKS = CLAUDE_HOME / "skills" / "project-memory" / "tools" / "hooks"
PROJECT_GATE = HOOKS / "project_gate.ps1"
LOG_TOOL_USAGE = CLAUDE_HOME / "scripts" / "log-tool-usage.ps1"

JOURNAL = "ЖУРНАЛ СЕССИЙ.md"
KONTEKST = "КОНТЕКСТ.md"


def run_project_gate(payload, state_dir):
    env = dict(os.environ, PROJECT_MEMORY_STATE_DIR=str(state_dir))
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(PROJECT_GATE)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True, env=env, timeout=90)


def run_log_tool_usage(payload, state_dir, userprofile_dir):
    """userprofile_dir isolates the UNRELATED tool-usage.jsonl/toolgate telemetry
    (log-tool-usage.ps1's own dir is $env:USERPROFILE\\.claude\\.local-state, see
    scripts/tests/test-toolgate.ps1) so this test never touches the real machine's
    ~/.claude/.local-state/tool-usage.jsonl. The ctxread marker itself is keyed
    ONLY by PROJECT_MEMORY_STATE_DIR (matches project_gate.ps1's own lookup)."""
    env = dict(os.environ, PROJECT_MEMORY_STATE_DIR=str(state_dir),
               USERPROFILE=str(userprofile_dir))
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(LOG_TOOL_USAGE)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True, env=env, timeout=90)


def _norm(p):
    """Нормализация пути для сравнения (регистр диска/кейс/трейлинг-слеш)."""
    return str(Path(p).resolve()).rstrip("\\/").lower()


def make_project(base, name="proj"):
    """Проект с журналом И КОНТЕКСТ.md: журнал - то, что find_project.ps1 считает
    признаком проекта памяти; КОНТЕКСТ.md - файл, чтение которого регистрируется."""
    proj = base / name
    (proj / "Claude").mkdir(parents=True)
    j = proj / "Claude" / JOURNAL
    j.write_text("## 2026-07-01 · TEST · тема\n**Сделано:** x\n", encoding="utf-8")
    k = proj / "Claude" / KONTEKST
    k.write_text("# Контекст\n\nРоль, критерии, грабли.\n", encoding="utf-8")
    return proj, j, k


def find_ctxread_markers(state_dir, session_id):
    return list(Path(state_dir).glob(f"ctxread_{session_id}_*.json"))


def read_json_sig(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


# === (a) log-tool-usage.ps1: Read(Claude\КОНТЕКСТ.md) -> marker appears =====

def test_a_registers_marker_on_kontekst_read(tmp_path):
    proj, _, k = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-a1"

    r = run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)

    assert r.returncode == 0, f"stderr={r.stderr!r}"
    markers = find_ctxread_markers(state, sid)
    assert len(markers) == 1, f"expected exactly one marker, got {markers}"
    data = read_json_sig(markers[0])
    assert _norm(data["root"]) == _norm(proj)


def test_a_no_marker_on_read_of_other_file(tmp_path):
    """Read любого другого файла (не КОНТЕКСТ.md) маркер не создаёт - точность
    суффиксной проверки, не 'любой Read в проекте засчитывается'."""
    proj, _, _ = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-a2"
    other = proj / "Claude" / "STATUS.md"
    other.write_text("status\n", encoding="utf-8")

    r = run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(other)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)

    assert r.returncode == 0
    assert find_ctxread_markers(state, sid) == []


def test_a_existing_telemetry_and_gate_logic_untouched(tmp_path):
    """Бонус-проверка локально (авторитетная - отдельный прогон test-toolgate.ps1,
    п.5 задачи): новый блок не ломает существующую строку телеметрии."""
    proj, _, k = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-a3"

    r = run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": "",
         "tool_response": {"content": "hello"}},
        state, up)

    assert r.returncode == 0
    tele_file = up / ".claude" / ".local-state" / "tool-usage.jsonl"
    assert tele_file.exists()
    # PS 5.1 "-Encoding UTF8" prepends a BOM on the first write to a new file
    last_line = tele_file.read_text(encoding="utf-8-sig").strip().splitlines()[-1]
    entry = json.loads(last_line)
    assert entry["tool"] == "Read" and entry["session"] == sid
    assert entry["bytes"] > 0


# === (b) project_gate.ps1: Write без маркера -> exit 2 ======================

def test_b_gate_blocks_write_without_marker(tmp_path):
    proj, _, _ = make_project(tmp_path)
    state = tmp_path / "st"
    target = proj / "file.py"

    r = run_project_gate(
        {"session_id": "sess-b1", "tool_name": "Write",
         "tool_input": {"file_path": str(target), "content": "x"},
         "cwd": str(proj)},
        state)

    assert r.returncode == 2, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    stderr = r.stderr.decode("utf-8", "replace")
    assert "КОНТЕКСТ" in stderr, f"stderr={stderr!r}"


def test_b_gate_blocks_edit_and_multiedit_without_marker(tmp_path):
    proj, _, _ = make_project(tmp_path)
    state = tmp_path / "st"
    target = proj / "file.py"
    target.write_text("x = 1\n", encoding="utf-8")

    r_edit = run_project_gate(
        {"session_id": "sess-b2", "tool_name": "Edit",
         "tool_input": {"file_path": str(target), "old_string": "x = 1", "new_string": "x = 2"},
         "cwd": str(proj)},
        state)
    assert r_edit.returncode == 2

    r_multi = run_project_gate(
        {"session_id": "sess-b3", "tool_name": "MultiEdit",
         "tool_input": {"file_path": str(target), "edits": [{"old_string": "x = 1", "new_string": "x = 2"}]},
         "cwd": str(proj)},
        state)
    assert r_multi.returncode == 2


def test_b_gate_blocks_notebook_edit_via_notebook_path_field(tmp_path):
    """NotebookEdit несёт путь в tool_input.notebook_path, не file_path (сверено
    с реальной схемой инструмента) - гейт обязан распознавать именно это поле."""
    proj, _, _ = make_project(tmp_path)
    state = tmp_path / "st"
    target = proj / "nb.ipynb"

    r = run_project_gate(
        {"session_id": "sess-b4", "tool_name": "NotebookEdit",
         "tool_input": {"notebook_path": str(target), "new_source": "print(1)"},
         "cwd": str(proj)},
        state)

    assert r.returncode == 2, f"stdout={r.stdout!r} stderr={r.stderr!r}"


# === (c) marker from (a) -> project_gate allows same project+session =======

def test_c_gate_allows_write_after_kontekst_read_same_session(tmp_path):
    proj, _, k = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-c1"

    r1 = run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)
    assert r1.returncode == 0
    assert len(find_ctxread_markers(state, sid)) == 1

    target = proj / "file.py"
    r2 = run_project_gate(
        {"session_id": sid, "tool_name": "Write",
         "tool_input": {"file_path": str(target), "content": "x"},
         "cwd": str(proj)},
        state)
    assert r2.returncode == 0, f"stderr={r2.stderr!r}"


def test_c_gate_still_blocks_different_session_after_read(tmp_path):
    """Маркер ключуется session_id - чтение в ОДНОЙ сессии не открывает мутации
    в ДРУГОЙ сессии того же проекта."""
    proj, _, k = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"

    run_log_tool_usage(
        {"session_id": "sess-c2-reader", "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)

    target = proj / "file.py"
    r = run_project_gate(
        {"session_id": "sess-c2-other", "tool_name": "Write",
         "tool_input": {"file_path": str(target), "content": "x"},
         "cwd": str(proj)},
        state)
    assert r.returncode == 2


def test_c_gate_allows_task_by_cwd_after_read(tmp_path):
    """tool_name==Task берёт путь из top-level cwd, не tool_input (у Task нет
    file_path) - отдельная проверка обеих веток: до и после чтения."""
    proj, _, k = make_project(tmp_path)
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-c3"

    r_before = run_project_gate(
        {"session_id": sid, "tool_name": "Task",
         "tool_input": {"description": "d", "prompt": "p", "subagent_type": "general-purpose"},
         "cwd": str(proj)},
        state)
    assert r_before.returncode == 2

    run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)

    r_after = run_project_gate(
        {"session_id": sid, "tool_name": "Task",
         "tool_input": {"description": "d", "prompt": "p", "subagent_type": "general-purpose"},
         "cwd": str(proj)},
        state)
    assert r_after.returncode == 0, f"stderr={r_after.stderr!r}"


# === (d) project_gate вне проекта -> exit 0 ==================================

def test_d_gate_noop_outside_project(tmp_path):
    outside = tmp_path / "not_a_project"
    outside.mkdir()
    state = tmp_path / "st"

    r = run_project_gate(
        {"session_id": "sess-d1", "tool_name": "Write",
         "tool_input": {"file_path": str(outside / "f.py"), "content": "x"},
         "cwd": str(outside)},
        state)
    assert r.returncode == 0, f"stderr={r.stderr!r}"


# === (e) project_gate на Read/прочие read-only тулы -> exit 0 ================

def test_e_gate_noop_on_read(tmp_path):
    proj, _, k = make_project(tmp_path)
    state = tmp_path / "st"

    r = run_project_gate(
        {"session_id": "sess-e1", "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj)},
        state)
    assert r.returncode == 0


def test_e_gate_noop_on_other_readonly_tools(tmp_path):
    proj, _, _ = make_project(tmp_path)
    state = tmp_path / "st"
    cases = [
        ("Bash", {"command": "echo hi"}),
        ("Grep", {"pattern": "x"}),
        ("Glob", {"pattern": "*.py"}),
    ]
    for tool_name, tool_input in cases:
        r = run_project_gate(
            {"session_id": "sess-e2", "tool_name": tool_name,
             "tool_input": tool_input, "cwd": str(proj)},
            state)
        assert r.returncode == 0, f"{tool_name}: stderr={r.stderr!r}"


# === Кириллица в пути проекта - end-to-end block -> read -> allow ============

def test_cyrillic_project_path_end_to_end(tmp_path):
    proj, _, k = make_project(tmp_path, name="Проект Тест")
    state, up = tmp_path / "st", tmp_path / "up"
    sid = "sess-cyr1"
    target = proj / "подпапка" / "файл.py"

    r0 = run_project_gate(
        {"session_id": sid, "tool_name": "Write",
         "tool_input": {"file_path": str(target), "content": "x"},
         "cwd": str(proj)},
        state)
    assert r0.returncode == 2, f"stdout={r0.stdout!r} stderr={r0.stderr!r}"

    r1 = run_log_tool_usage(
        {"session_id": sid, "tool_name": "Read",
         "tool_input": {"file_path": str(k)},
         "cwd": str(proj), "transcript_path": ""},
        state, up)
    assert r1.returncode == 0, f"stderr={r1.stderr!r}"
    markers = find_ctxread_markers(state, sid)
    assert len(markers) == 1
    assert _norm(read_json_sig(markers[0])["root"]) == _norm(proj)

    r2 = run_project_gate(
        {"session_id": sid, "tool_name": "Write",
         "tool_input": {"file_path": str(target), "content": "x"},
         "cwd": str(proj)},
        state)
    assert r2.returncode == 0, f"stdout={r2.stdout!r} stderr={r2.stderr!r}"
