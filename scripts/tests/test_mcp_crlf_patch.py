# -*- coding: utf-8 -*-
"""Тесты патчера CRLF-бага Python MCP SDK (python-sdk#2433)."""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from mcp_crlf_patch import (BUGGY, FIXED, classify, main, process_venv,
                            run, stdio_path, venv_from_command)

STDIO_BUGGY = (
    'import sys\nfrom io import TextIOWrapper\n\n'
    'async def stdio_server(stdin=None, stdout=None):\n'
    '    if not stdin:\n'
    '        stdin = anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, encoding="utf-8"))\n'
    '    if not stdout:\n'
    '        stdout = anyio.wrap_file(TextIOWrapper(sys.stdout.buffer, encoding="utf-8"))\n'
)

def _make_venv(tmp_path, text):
    venv = tmp_path / "v"
    p = venv / "Lib" / "site-packages" / "mcp" / "server" / "stdio.py"
    p.parent.mkdir(parents=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return venv

def test_classify_three_states():
    assert classify(STDIO_BUGGY) == "unpatched"
    assert classify(STDIO_BUGGY.replace(BUGGY, FIXED)) == "already-ok"
    assert classify("совсем другой код") == "unknown-pattern"

def test_patch_is_applied_and_idempotent(tmp_path):
    venv = _make_venv(tmp_path, STDIO_BUGGY)
    assert process_venv(venv, check_only=False) == "patched"
    text = stdio_path(venv).read_text(encoding="utf-8")
    assert FIXED in text and classify(text) == "already-ok"
    # stdin-обёртка НЕ тронута
    assert 'TextIOWrapper(sys.stdin.buffer, encoding="utf-8")' in text
    assert process_venv(venv, check_only=False) == "already-ok"   # идемпотентность

def test_unknown_pattern_untouched(tmp_path):
    venv = _make_venv(tmp_path, "def stdio_server(): pass\n")
    before = stdio_path(venv).read_bytes()
    assert process_venv(venv, check_only=False) == "unknown-pattern"
    assert stdio_path(venv).read_bytes() == before               # файл не изменён

def test_check_only_does_not_write(tmp_path):
    venv = _make_venv(tmp_path, STDIO_BUGGY)
    assert process_venv(venv, check_only=True) == "unpatched"
    assert BUGGY in stdio_path(venv).read_text(encoding="utf-8")  # не запатчен

def test_not_found(tmp_path):
    assert process_venv(tmp_path / "нет-такого", check_only=True) == "not-found"

def test_crlf_line_endings_preserved(tmp_path):
    venv = _make_venv(tmp_path, STDIO_BUGGY.replace("\n", "\r\n"))
    assert process_venv(venv, check_only=False) == "patched"
    raw = stdio_path(venv).read_bytes()
    assert b"\r\n" in raw and FIXED.encode() in raw               # переводы строк файла целы

def test_venv_from_command():
    assert venv_from_command(
        "C:/Users/Даниил/.claude/mcp-servers/autocad-mcp/.venv/Scripts/python.exe"
    ) == pathlib.Path("C:/Users/Даниил/.claude/mcp-servers/autocad-mcp/.venv")
    assert venv_from_command("uvx") is None
    assert venv_from_command("uv") is None
    assert venv_from_command("C:/Python312/python.exe") is None   # не venv-раскладка

def test_run_exit_codes(tmp_path, capsys):
    good = _make_venv(tmp_path, STDIO_BUGGY)
    assert run([str(good)], check_only=False) == 0
    assert run([str(good), str(tmp_path / "ghost")], check_only=False) == 1
    out = capsys.readouterr().out
    assert "not-found" in out and "already-ok" in out


def test_from_overlay_uses_shared_parser_and_classifies_invalid_input(tmp_path, capsys):
    from codex_mcp_overlay import overlay_path

    p = overlay_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text('{"enable": "pyserv"}', encoding="utf-8")

    assert main(["--from-overlay", "--check"], home=tmp_path) == 2
    assert "input-error" in capsys.readouterr().err


@pytest.mark.parametrize("config", ["[]", '{"mcpServers": null}', '{"mcpServers": []}',
                                      '{"mcpServers": {"pyserv": []}}'])
def test_from_overlay_classifies_malformed_mcp_configuration(tmp_path, capsys, config):
    from codex_mcp_overlay import overlay_path

    p = overlay_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text('{"enable": ["pyserv"]}', encoding="utf-8")
    (tmp_path / ".claude.json").write_text(config, encoding="utf-8")

    assert main(["--from-overlay", "--check"], home=tmp_path) == 2
    assert "input-error" in capsys.readouterr().err


def test_from_overlay_checks_and_patches_python_venv(tmp_path):
    import json
    from codex_mcp_overlay import overlay_path

    venv = _make_venv(tmp_path, STDIO_BUGGY)
    (tmp_path / ".claude.json").write_text(json.dumps({"mcpServers": {
        "pyserv": {"command": str(venv / "Scripts" / "python.exe")}
    }}), encoding="utf-8")
    p = overlay_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text('{"enable": ["pyserv"]}', encoding="utf-8")

    assert main(["--from-overlay", "--check"], home=tmp_path) == 1
    assert main(["--from-overlay"], home=tmp_path) == 0
    assert main(["--from-overlay", "--check"], home=tmp_path) == 0
