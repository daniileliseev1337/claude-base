"""Тесты project_context.ps1 (UserPromptSubmit-хук доставки ядра проекта,
инжекция раз на сессию+проект). Windows/PowerShell 5.1 — переносимы между
машинами; на не-Windows скипаются.

Отдельный файл от test_hooks.py (тот параллельно правит другая задача) -
намеренно НЕ импортирует из него, копирует паттерн helper'а (subprocess +
stdin JSON), чтобы файлы были независимы."""
import json
import os
import subprocess
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


def make_project(base, name="proj"):
    """Проект с полным ядром (ЖУРНАЛ + КОНТЕКСТ + STATUS), с уникальными
    маркерными строками в каждом файле, чтобы тесты могли отличить источник."""
    proj = base / name
    (proj / "Claude").mkdir(parents=True)
    (proj / "Claude" / JOURNAL).write_text(
        "## 2026-07-01 * TEST * тема\n**Сделано:** x\n", encoding="utf-8")
    (proj / "Claude" / "КОНТЕКСТ.md").write_text(
        "# Тест КОНТЕКСТ маркер kontekst-marker-xyz123\n"
        "## ТВОЯ РОЛЬ\nроль тестовая\n", encoding="utf-8")
    (proj / "Claude" / "STATUS.md").write_text(
        "# Статус\nСтрока статуса status-marker-abc789\n", encoding="utf-8")
    return proj


def test_context_noop_no_path_no_project_cwd(tmp_path):
    outside = tmp_path / "empty_no_project"
    outside.mkdir()
    r = run_hook("project_context.ps1",
                 {"session_id": "c1", "cwd": str(outside), "prompt": "привет, как дела?"},
                 tmp_path / "st")
    assert r.returncode == 0
    assert r.stdout.strip() == b""


def test_context_injects_kontekst_and_stop_from_prompt_path(tmp_path):
    proj = make_project(tmp_path)
    outside_cwd = tmp_path / "elsewhere"
    outside_cwd.mkdir()
    prompt = 'глянь проект "{}\\sub\\file.txt" и почини баг'.format(proj)
    r = run_hook("project_context.ps1",
                 {"session_id": "c2", "cwd": str(outside_cwd), "prompt": prompt},
                 tmp_path / "st")
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace")
    assert "СТОП" in out
    assert "kontekst-marker-xyz123" in out          # текст из КОНТЕКСТ.md


def test_context_second_call_same_session_is_silent(tmp_path):
    proj = make_project(tmp_path)
    state = tmp_path / "st"
    prompt = 'открой "{}\\sub\\file.txt"'.format(proj)
    r1 = run_hook("project_context.ps1",
                  {"session_id": "c3", "cwd": str(tmp_path), "prompt": prompt}, state)
    assert r1.returncode == 0
    out1 = r1.stdout.decode("utf-8", "replace")
    assert "СТОП" in out1
    r2 = run_hook("project_context.ps1",
                  {"session_id": "c3", "cwd": str(tmp_path), "prompt": prompt}, state)
    assert r2.returncode == 0
    assert r2.stdout.strip() == b""                  # маркер сработал - тихо


def test_context_cwd_fallback_when_prompt_has_no_path(tmp_path):
    proj = make_project(tmp_path, "proj2")
    r = run_hook("project_context.ps1",
                 {"session_id": "c4", "cwd": str(proj), "prompt": "продолжи работу, пожалуйста"},
                 tmp_path / "st")
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace")
    assert "СТОП" in out
    assert "kontekst-marker-xyz123" in out


def test_context_cyrillic_project_path(tmp_path):
    proj = make_project(tmp_path, "Объект Тест")
    outside_cwd = tmp_path / "elsewhere2"
    outside_cwd.mkdir()
    prompt = 'работаем по "{}\\подпапка\\файл.txt"'.format(proj)
    r = run_hook("project_context.ps1",
                 {"session_id": "c5", "cwd": str(outside_cwd), "prompt": prompt},
                 tmp_path / "st")
    assert r.returncode == 0
    out = r.stdout.decode("utf-8", "replace")
    assert "СТОП" in out
    assert "kontekst-marker-xyz123" in out


def test_context_exit_code_always_zero_on_garbage_input(tmp_path):
    r = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(HOOKS / "project_context.ps1")],
        input=b"not valid json {{{ garbage",
        capture_output=True,
        env=dict(os.environ, PROJECT_MEMORY_STATE_DIR=str(tmp_path / "st")),
        timeout=90)
    assert r.returncode == 0


def test_context_exit_code_zero_with_no_stdin(tmp_path):
    r = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(HOOKS / "project_context.ps1")],
        input=b"",
        capture_output=True,
        env=dict(os.environ, PROJECT_MEMORY_STATE_DIR=str(tmp_path / "st")),
        timeout=90)
    assert r.returncode == 0
