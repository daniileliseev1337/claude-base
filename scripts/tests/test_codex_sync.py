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
