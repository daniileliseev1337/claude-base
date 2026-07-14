# -*- coding: utf-8 -*-
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from codex_sync import apply_managed_block, BEGIN, END

def test_block_appended_preserves_foreign_content():
    src = 'model = "gpt-5.6-sol"\n\n[plugins."visualize@openai-bundled"]\nenabled = true\n'
    out = apply_managed_block(src, "[mcp_servers.time]\ncommand = 'uvx'\n")
    assert src.rstrip("\n") in out          # чужое сохранено байт-в-байт
    assert BEGIN in out and END in out
    assert "[mcp_servers.time]" in out

def test_idempotent_and_replaces_old_block():
    src = "x = 1\n"
    once = apply_managed_block(src, "a = 1\n")
    twice = apply_managed_block(once, "a = 1\n")
    assert once == twice                     # идемпотентность
    updated = apply_managed_block(once, "a = 2\n")
    assert "a = 2" in updated and "a = 1" not in updated

def test_backslash_payload_survives_reapply():
    payload = "command = 'C:\\Users\\Daniil\\.claude\\x.exe'\nref = 'a\\1b'\n"
    once = apply_managed_block("x = 1\n", payload)
    twice = apply_managed_block(once, payload)   # раньше падало re.error
    assert once == twice
    assert "C:\\Users\\Daniil" in twice

def test_two_blocks_consolidated_to_one():
    src = f"a = 1\n{BEGIN}\nold1\n{END}\nb = 2\n{BEGIN}\nold2\n{END}\n"
    out = apply_managed_block(src, "new\n")
    assert out.count(BEGIN) == 1 and out.count(END) == 1
    assert "a = 1" in out and "b = 2" in out      # чужое между блоками сохранено
    assert "old1" not in out and "old2" not in out

def test_empty_file():
    assert apply_managed_block("", "a = 1\n").startswith(BEGIN)

def test_render_mcp_toml_whitelist_and_env():
    from codex_sync import render_mcp_toml
    servers = {
        "time": {"command": "uvx", "args": ["mcp-server-time"]},
        "excel": {"command": "uvx", "args": ["excel-mcp-server"], "env": {"X": "a\\b"}},
    }
    out = render_mcp_toml(servers, allow=["excel"])
    assert "[mcp_servers.excel]" in out
    assert "mcp_servers.time" not in out            # вне белого списка
    assert "args = ['excel-mcp-server']" in out
    assert "[mcp_servers.excel.env]" in out and "X = 'a\\b'" in out

def test_t_values_parse_as_real_toml():
    import tomllib
    from codex_sync import render_mcp_toml
    servers = {
        "s1": {"command": "run", "args": ["it's arg", "line1\nline2", "C:\\x\\y"]},
    }
    out = render_mcp_toml(servers, allow=["s1"])
    parsed = tomllib.loads(out)
    assert parsed["mcp_servers"]["s1"]["args"] == ["it's arg", "line1\nline2", "C:\\x\\y"]

def test_render_skills_toml(tmp_path):
    (tmp_path / "excel-helper").mkdir()
    (tmp_path / "excel-helper" / "SKILL.md").write_text("---\nname: excel-helper\n---\n", encoding="utf-8")
    from codex_sync import render_skills_toml
    manifest = {"enable": ["excel-helper", "ghost-skill"]}
    out = render_skills_toml(manifest, tmp_path)
    assert out.count("[[skills.config]]") == 1      # ghost-skill пропущен
    assert "excel-helper" in out and "enabled = true" in out

def test_render_hooks_json_structure(tmp_path):
    from codex_sync import render_hooks_json
    hooks = render_hooks_json(tmp_path)
    assert set(hooks["hooks"].keys()) == {"SessionStart", "Stop", "PostToolUse"}

    start = hooks["hooks"]["SessionStart"][0]["hooks"]
    assert "auto-pull.ps1" in start[0]["commandWindows"]          # pull строго первым
    assert "graph-staleness-check.ps1" in start[1]["commandWindows"]
    assert "session_start.ps1" in start[2]["commandWindows"]
    assert [h["timeout"] for h in start] == [30, 15, 10]

    stop = hooks["hooks"]["Stop"][0]["hooks"]
    assert "session_end.ps1" in stop[0]["commandWindows"]         # журнал до пуша
    assert "auto-push.ps1" in stop[1]["commandWindows"]
    assert [h["timeout"] for h in stop] == [20, 60]

    ptu = hooks["hooks"]["PostToolUse"][0]
    assert ptu["matcher"] == ".*"
    assert "log-tool-usage.ps1" in ptu["hooks"][0]["commandWindows"]
    assert ptu["hooks"][0]["timeout"] == 10

    for group in hooks["hooks"].values():
        for m in group:
            for h in m["hooks"]:
                assert h["type"] == "command"
                assert h["commandWindows"].count('"') == 2        # путь в кавычках

    import json
    json.loads(json.dumps(hooks, ensure_ascii=False))             # сериализуемость round-trip

def test_convert_agent_md():
    from codex_sync import convert_agent_md
    text = (pathlib.Path(__file__).parent / "fixtures" / "agent_sample.md").read_text(encoding="utf-8")
    fname, toml_text = convert_agent_md(text)
    assert fname == "sample-auditor.toml"
    assert "model = 'gpt-5.6-terra'" in toml_text            # sonnet → terra
    assert "mcp__excel__" not in toml_text                    # инструменты заменены
    assert "spreadsheets" in toml_text
    assert "name = 'sample-auditor'" in toml_text
    import tomllib
    assert tomllib.loads(toml_text)["description"] == "Тестовый ревьюер"

def test_convert_agent_md_crlf_and_block_description():
    from codex_sync import convert_agent_md
    import tomllib
    md = ("---\r\nname: crlf-agent\r\ndescription: |\r\n  Первая строка.\r\n  Вторая строка (Ф\\.\\d{4}).\r\nmodel: haiku\r\n---\r\n"
          "Тело с путём C:\\Users\\x и регекспом \\{\\{placeholder\\}\\}.\r\n")
    fname, toml_text = convert_agent_md(md)
    parsed = tomllib.loads(toml_text)
    assert fname == "crlf-agent.toml"
    assert parsed["model"] == "gpt-5.6-luna"
    assert "Вторая строка" in parsed["description"] and parsed["description"].strip() != "|"
    assert "C:\\Users\\x" in parsed["developer_instructions"]

def test_convert_agent_md_triple_quote_fallback():
    from codex_sync import convert_agent_md
    import tomllib
    md = "---\nname: tq\ndescription: d\nmodel: sonnet\n---\ncode: '''docstring''' и \\ бэкслэш\n"
    _, toml_text = convert_agent_md(md)
    parsed = tomllib.loads(toml_text)
    assert "'''docstring'''" in parsed["developer_instructions"]
    assert "\\ бэкслэш" in parsed["developer_instructions"]

def test_convert_agent_md_wildcard_tools():
    from codex_sync import convert_agent_md
    text = ("---\nname: w\ndescription: d\nmodel: haiku\n---\n"
            "Инструменты: mcp__excel__* и mcp__word__\\* и mcp__pdf-mcp__*.\n")
    _, toml_text = convert_agent_md(text)
    assert "mcp__" not in toml_text
    assert "spreadsheets" in toml_text and "documents" in toml_text
