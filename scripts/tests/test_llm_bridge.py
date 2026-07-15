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

    invalid_task = make_task(tmp_path)
    invalid_task["context"]["files"] = ["../.env"]
    assert list(jsonschema.Draft202012Validator(task_schema).iter_errors(invalid_task))
    invalid_result = make_result(task, changes=["C:/Users/example/.env"])
    invalid_result["summary"] = ""
    invalid_result["checks"] = []
    assert list(jsonschema.Draft202012Validator(result_schema).iter_errors(invalid_result))


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


def test_validate_task_rejects_empty_source_and_secret_values(tmp_path):
    task = make_task(tmp_path)
    task["source"] = ""
    with pytest.raises(bridge.BridgeError, match="source"):
        bridge.validate_task(task, tmp_path, "codex", False)

    task = make_task(tmp_path)
    task["goal"] = "Проверь token=supersecretvalue123"
    with pytest.raises(bridge.BridgeError, match="похожую на секрет"):
        bridge.validate_task(task, tmp_path, "codex", False)
    assert "supersecret" not in bridge._redact_text('{"token":"supersecretvalue123"}')
    assert "123e4567" not in bridge._redact_text('{"session_id":"123e4567-e89b-12d3-a456-426614174000"}')


def test_runtime_mirrors_schema_for_empty_items_and_duplicates(tmp_path):
    task = make_task(tmp_path)
    task["constraints"] = [""]
    with pytest.raises(bridge.BridgeError, match="пустые строки"):
        bridge.validate_task(task, tmp_path, "codex", False)

    task = make_task(tmp_path)
    task["context"]["files"] = ["source.txt", "source.txt"]
    with pytest.raises(bridge.BridgeError, match="дубли"):
        bridge.validate_task(task, tmp_path, "codex", False)

    task = make_task(tmp_path)
    result = make_result(task)
    result["checks"][0]["name"] = ""
    result["checks"][0]["evidence"] = ""
    with pytest.raises(bridge.BridgeError, match="не должны быть пустыми"):
        bridge.validate_result(result, task)


def test_secret_scan_covers_private_keys_and_large_files(tmp_path):
    task = make_task(tmp_path)
    private = tmp_path / "private.txt"
    private.write_text("-----BEGIN PRIVATE KEY-----\nabc", encoding="utf-8")
    task["context"]["files"] = ["private.txt"]
    with pytest.raises(bridge.BridgeError, match="содержащий секрет"):
        bridge.validate_task(task, tmp_path, "codex", False)

    private.write_text("-----BEGIN ENCRYPTED PRIVATE KEY-----\nabc", encoding="utf-8")
    with pytest.raises(bridge.BridgeError, match="содержащий секрет"):
        bridge.validate_task(task, tmp_path, "codex", False)

    large = tmp_path / "large.txt"
    large.write_text("x" * (2 * 1024 * 1024 + 32) + "\ntoken=supersecretvalue123", encoding="utf-8")
    task["context"]["files"] = ["large.txt"]
    with pytest.raises(bridge.BridgeError, match="содержащий секрет"):
        bridge.validate_task(task, tmp_path, "codex", False)


def test_validate_result_enforces_read_only(tmp_path):
    task = make_task(tmp_path)
    with pytest.raises(bridge.BridgeError, match="read-only"):
        bridge.validate_result(make_result(task, changes=["changed.txt"]), task)

    failed = make_result(task)
    failed["checks"][0]["status"] = "fail"
    with pytest.raises(bridge.BridgeError, match="completed требует"):
        bridge.validate_result(failed, task)


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

    runner = bridge._runner_schema(json.loads(bridge.RESULT_SCHEMA.read_text(encoding="utf-8")))
    serialized = json.dumps(runner)
    assert "pattern" not in serialized and "minLength" not in serialized


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
    assert output.with_suffix(".md").is_file()


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
    failure = (tmp_path / "out.failure.json")
    assert failure.is_file()
    assert json.loads(failure.read_text(encoding="utf-8"))["kind"] == "nonzero_exit"
    assert failure.with_suffix(".md").is_file()

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
