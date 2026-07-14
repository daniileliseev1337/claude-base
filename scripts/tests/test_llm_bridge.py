import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path.home() / ".claude" / "skills" / "llm-interop" / "scripts" / "llm_bridge.py"
SPEC = importlib.util.spec_from_file_location("llm_bridge", SCRIPT)
bridge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bridge)


def make_task(tmp_path, *, partner="codex", permissions="read-only", hop_count=0):
    (tmp_path / "source.txt").write_text("проверяемый источник", encoding="utf-8")
    return {
        "schema_version": "1.0",
        "task_id": "unicode-review",
        "source": "claude" if partner == "codex" else "codex",
        "target": partner,
        "hop_count": hop_count,
        "mode": "review",
        "permissions": permissions,
        "goal": "Проверь кириллицу и контракт.",
        "context": {
            "files": ["source.txt"],
            "facts": ["Источник прочитан."],
            "prior_decisions": [],
        },
        "constraints": ["Не меняй файлы."],
        "done_when": ["Верни проверку с evidence."],
        "deliverables": [],
    }


def make_result(task, *, changes=None):
    return {
        "schema_version": "1.0",
        "task_id": task["task_id"],
        "status": "completed",
        "summary": "Кириллица сохранена.",
        "checks": [{"name": "encoding", "status": "pass", "evidence": "Текст прочитан."}],
        "changes": [] if changes is None else changes,
        "assumptions": [],
        "risks": [],
        "questions": [],
        "next_step": "Передать результат оркестратору.",
    }


def test_task_and_result_schemas_are_valid(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    task = make_task(tmp_path)
    task_schema = json.loads((bridge.SKILL_ROOT / "references" / "task.schema.json").read_text(encoding="utf-8"))
    result_schema = json.loads(bridge.RESULT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(task_schema)
    jsonschema.Draft202012Validator.check_schema(result_schema)
    jsonschema.validate(task, task_schema)
    jsonschema.validate(make_result(task), result_schema)


def test_validate_task_rejects_sensitive_and_traversal_paths(tmp_path):
    task = make_task(tmp_path)
    task["context"]["files"] = ["../.claude.json"]
    with pytest.raises(bridge.BridgeError, match="относительным"):
        bridge.validate_task(task, tmp_path, "codex", False)

    task["context"]["files"] = [".git/config"]
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("token", encoding="utf-8")
    with pytest.raises(bridge.BridgeError, match="чувствительный"):
        bridge.validate_task(task, tmp_path, "codex", False)


def test_validate_task_stops_recursion_and_requires_write_opt_in(tmp_path):
    task = make_task(tmp_path, hop_count=1)
    with pytest.raises(bridge.BridgeError, match="рекурсивная"):
        bridge.validate_task(task, tmp_path, "codex", False)

    task = make_task(tmp_path, permissions="workspace-write")
    with pytest.raises(bridge.BridgeError, match="--allow-write"):
        bridge.validate_task(task, tmp_path, "codex", False)
    bridge.validate_task(task, tmp_path, "codex", True)


def test_validate_result_enforces_read_only(tmp_path):
    task = make_task(tmp_path)
    with pytest.raises(bridge.BridgeError, match="read-only"):
        bridge.validate_result(make_result(task, changes=["changed.txt"]), task)


def test_commands_use_stdin_and_structured_output(tmp_path):
    codex_out = tmp_path / "codex.json"
    codex = bridge.build_command("codex", Path("codex.exe"), tmp_path, codex_out, "read-only", None)
    assert codex[-1] == "-"
    assert "--ignore-user-config" in codex
    assert codex[codex.index("--sandbox") + 1] == "read-only"
    assert codex[codex.index("--output-schema") + 1] == str(bridge.RESULT_SCHEMA)

    claude = bridge.build_command("claude", Path("claude.exe"), tmp_path, codex_out, "read-only", None)
    assert "--json-schema" in claude and "--no-session-persistence" in claude
    assert claude[claude.index("--permission-mode") + 1] == "plan"
    assert "Read,Glob,Grep" in claude


def test_codex_roundtrip_preserves_utf8(monkeypatch, tmp_path):
    task = make_task(tmp_path)
    task_path = tmp_path / "task.json"
    output = tmp_path / "result.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(bridge, "find_binary", lambda *a, **k: Path(sys.executable))

    def fake_run(command, prompt, cwd, timeout, temp_dir):
        assert "Проверь кириллицу" in prompt
        runner_output = Path(command[command.index("--output-last-message") + 1])
        runner_output.write_text(json.dumps(make_result(task), ensure_ascii=False), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(bridge, "_run_process", fake_run)
    args = argparse.Namespace(
        partner="codex", task=str(task_path), cwd=str(tmp_path), output=str(output),
        model=None, binary=None, allow_write=False, dry_run=False, timeout=10,
    )
    assert bridge.run(args) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["summary"] == "Кириллица сохранена."


def test_claude_structured_output_roundtrip(monkeypatch, tmp_path):
    task = make_task(tmp_path, partner="claude")
    task_path = tmp_path / "task.json"
    output = tmp_path / "result.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(bridge, "find_binary", lambda *a, **k: Path(sys.executable))

    def fake_run(command, prompt, cwd, timeout, temp_dir):
        outer = {"structured_output": make_result(task)}
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(outer, ensure_ascii=False), stderr="")

    monkeypatch.setattr(bridge, "_run_process", fake_run)
    args = argparse.Namespace(
        partner="claude", task=str(task_path), cwd=str(tmp_path), output=str(output),
        model=None, binary=None, allow_write=False, dry_run=False, timeout=10,
    )
    assert bridge.run(args) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["task_id"] == task["task_id"]


def test_runner_failure_and_timeout_are_explicit(monkeypatch, tmp_path):
    task = make_task(tmp_path)
    task_path = tmp_path / "task.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(bridge, "find_binary", lambda *a, **k: Path(sys.executable))
    args = argparse.Namespace(
        partner="codex", task=str(task_path), cwd=str(tmp_path), output=str(tmp_path / "out.json"),
        model=None, binary=None, allow_write=False, dry_run=False, timeout=1,
    )

    monkeypatch.setattr(
        bridge, "_run_process",
        lambda command, *a, **k: subprocess.CompletedProcess(command, 7, stdout="", stderr="runner failed"),
    )
    with pytest.raises(bridge.BridgeError, match="кодом 7"):
        bridge.run(args)

    monkeypatch.setattr(
        bridge, "_run_process",
        lambda *a, **k: (_ for _ in ()).throw(bridge.BridgeError("таймаут партнёра после 1 с")),
    )
    with pytest.raises(bridge.BridgeError, match="таймаут"):
        bridge.run(args)


def test_process_timeout_terminates_without_pipe_hang(tmp_path):
    with pytest.raises(bridge.BridgeError, match="таймаут"):
        bridge._run_process(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            "", tmp_path, 0.1, tmp_path,
        )
