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

def test_convert_agent_readonly_sandbox():
    from codex_sync import convert_agent_md
    ro = "---\nname: r\ndescription: d\nmodel: sonnet\ntools: Read, Grep, mcp__excel__read_data_from_excel\n---\nТело.\n"
    _, t = convert_agent_md(ro)
    assert 'sandbox_mode = "read-only"' in t
    rw = "---\nname: w\ndescription: d\nmodel: sonnet\ntools: Read, Write, Edit\n---\nТело.\n"
    _, t2 = convert_agent_md(rw)
    assert "sandbox_mode" not in t2

def test_render_agents_md_limit():
    from codex_sync import render_agents_md
    out = render_agents_md("ядро", "слой")
    assert out.startswith("Отвечай пользователю по-русски")
    assert "ядро" in out and "слой" in out
    import pytest
    with pytest.raises(ValueError):
        render_agents_md("x" * 33000, "y")

def test_agents_md_written_lf(tmp_path, monkeypatch):
    # мини-проверка: render_agents_md не содержит \r, а гейт меряет то, что пишется
    from codex_sync import render_agents_md
    out = render_agents_md("ядро", "слой")
    assert "\r" not in out

def test_render_mcp_toml_http_server():
    from codex_sync import render_mcp_toml
    servers = {"exa": {"type": "http", "url": "https://mcp.exa.ai/mcp"},
               "bad": {"type": "http"}}
    out = render_mcp_toml(servers, allow=["exa", "bad"])
    assert "[mcp_servers.exa]" in out and "url = 'https://mcp.exa.ai/mcp'" in out
    assert "command" not in out.split("[mcp_servers.exa]")[1].split("[")[0]
    assert "mcp_servers.bad" not in out

def test_collect_agent_tomls_skips_nameless(tmp_path):
    from codex_sync import collect_agent_tomls
    (tmp_path / "good.md").write_text("---\nname: good\ndescription: d\nmodel: haiku\n---\nТело.\n", encoding="utf-8")
    (tmp_path / "agents.md").write_text("# Индекс агентов\nпросто текст без фронтматтером\n", encoding="utf-8")
    result = collect_agent_tomls(tmp_path)
    assert list(result) == ["good.toml"]

def test_ensure_skill_junctions(tmp_path):
    from codex_sync import ensure_skill_junctions
    src = tmp_path / "claude_skills"; dst = tmp_path / "agents_skills"
    (src / "excel-helper").mkdir(parents=True)
    (src / "excel-helper" / "SKILL.md").write_text("---\nname: excel-helper\n---\n", encoding="utf-8")
    (src / "old-skill").mkdir()
    (src / "old-skill" / "SKILL.md").write_text("---\nname: old-skill\n---\n", encoding="utf-8")
    manifest = {"enable": ["excel-helper", "ghost"]}
    made = ensure_skill_junctions(manifest, src, dst)
    assert (dst / "excel-helper" / "SKILL.md").exists()      # junction работает
    assert made == ["excel-helper"]                           # ghost пропущен с warn
    # идемпотентность
    assert ensure_skill_junctions(manifest, src, dst) == []
    # cleanup: скилл выпал из манифеста -> junction снимается
    import subprocess
    subprocess.run(["cmd", "/c", "mklink", "/J", str(dst / "old-skill"), str(src / "old-skill")], capture_output=True)
    ensure_skill_junctions(manifest, src, dst)
    assert not (dst / "old-skill").exists()
    assert (src / "old-skill" / "SKILL.md").exists()          # источник цел

def test_render_all_keys_and_purity(make_canon):
    from codex_sync import render_all
    home = make_canon()
    out = render_all(home)
    assert set(out) == {"AGENTS.md", "config.toml#managed", "hooks.json", "agents/тест-агент.toml"}
    assert "[mcp_servers.time]" in out["config.toml#managed"]
    assert "excel" not in out["config.toml#managed"]          # whitelist работает
    assert out["config.toml#managed"] == out["config.toml#managed"].rstrip()
    # чистота: на диск ничего не записано
    assert (home / ".codex" / "config.toml").read_text(encoding="utf-8") == "x = 1\n"
    assert not (home / ".codex" / "AGENTS.md").exists()

def test_collect_inputs_tracks_canon_and_mcp_slice(make_canon):
    from codex_sync import collect_inputs
    home = make_canon()
    h1 = collect_inputs(home)
    assert "core/AGENTS.core.md" in h1 and "agents/тест-агент.md" in h1
    assert ".claude.json#mcpServers" in h1
    # правка канона меняет хеш
    (home / ".claude" / "core" / "AGENTS.core.md").write_text("# Ядро v2\n", encoding="utf-8")
    h2 = collect_inputs(home)
    assert h1["core/AGENTS.core.md"] != h2["core/AGENTS.core.md"]
    # правка НЕ-whitelisted сервера в .claude.json срез не трогает
    import json
    cj = home / ".claude.json"
    data = json.loads(cj.read_text(encoding="utf-8"))
    data["mcpServers"]["excel"]["args"] = ["other"]
    cj.write_text(json.dumps(data), encoding="utf-8")
    h3 = collect_inputs(home)
    assert h2[".claude.json#mcpServers"] == h3[".claude.json#mcpServers"]

def _seed_manifest(home):
    """Синк-состояние 'всё чисто': диск = ожидаемое, манифест записан."""
    from codex_sync import render_all, collect_inputs, save_manifest, _sha, apply_managed_block
    rendered = render_all(home)
    codex = home / ".codex"
    (codex / "AGENTS.md").write_text(rendered["AGENTS.md"], encoding="utf-8", newline="\n")
    cfg = codex / "config.toml"
    cfg.write_text(apply_managed_block(cfg.read_text(encoding="utf-8"), rendered["config.toml#managed"]),
                   encoding="utf-8", newline="\n")
    (codex / "hooks.json").write_text(rendered["hooks.json"], encoding="utf-8", newline="\n")
    (codex / "agents").mkdir(exist_ok=True)
    for k in rendered:
        if k.startswith("agents/"):
            (codex / "agents" / k.split("/", 1)[1]).write_text(rendered[k], encoding="utf-8", newline="\n")
    save_manifest(home, collect_inputs(home), {k: _sha(v) for k, v in rendered.items()})

def test_check_clean(make_canon):
    from codex_sync import check
    home = make_canon(); _seed_manifest(home)
    res = check(home)
    assert res["canon-newer"] == [] and res["manual-drift"] == []
    assert "AGENTS.md" in res["clean"]

def test_check_canon_newer_after_core_edit(make_canon):
    from codex_sync import check
    home = make_canon(); _seed_manifest(home)
    (home / ".claude" / "core" / "AGENTS.core.md").write_text("# Ядро v2\n", encoding="utf-8")
    res = check(home)
    assert "AGENTS.md" in res["canon-newer"] and res["manual-drift"] == []

def test_check_manual_drift_after_disk_edit(make_canon):
    from codex_sync import check
    home = make_canon(); _seed_manifest(home)
    agents_md = home / ".codex" / "AGENTS.md"
    agents_md.write_text(agents_md.read_text(encoding="utf-8") + "\nручная правка\n",
                         encoding="utf-8", newline="\n")
    res = check(home)
    assert res["manual-drift"] == ["AGENTS.md"] and res["canon-newer"] == []

def test_check_both_categories_and_managed_block_extraction(make_canon):
    from codex_sync import check, read_disk_output
    home = make_canon(); _seed_manifest(home)
    # ручная правка ВНУТРИ managed-блока + правка канона
    cfg = home / ".codex" / "config.toml"
    cfg.write_text(cfg.read_text(encoding="utf-8").replace("[mcp_servers.time]", "[mcp_servers.time2]"),
                   encoding="utf-8", newline="\n")
    (home / ".claude" / "core" / "AGENTS.core.md").write_text("# Ядро v3\n", encoding="utf-8")
    res = check(home)
    assert "config.toml#managed" in res["manual-drift"]
    assert "AGENTS.md" in res["canon-newer"]
    assert "time2" in read_disk_output(home, "config.toml#managed")

def test_check_missing_codex_dir_is_quiet(make_canon, tmp_path):
    from codex_sync import check
    home = make_canon()
    import shutil; shutil.rmtree(home / ".codex")
    res = check(home)
    assert res == {"clean": [], "canon-newer": [], "manual-drift": []}

def test_sync_writes_manifest_and_regenerates_on_canon_change(make_canon):
    from codex_sync import sync, check, manifest_path
    home = make_canon()
    assert sync(home) == 0                                   # первый прогон: сборка + манифест
    assert manifest_path(home).exists()
    assert check(home)["manual-drift"] == [] and check(home)["canon-newer"] == []
    (home / ".claude" / "core" / "AGENTS.core.md").write_text("# Ядро v2\n", encoding="utf-8")
    assert sync(home) == 0                                   # canon-newer → перегенерено
    assert "Ядро v2" in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")

def test_sync_skips_manual_drift_and_returns_3(make_canon):
    from codex_sync import sync
    home = make_canon(); sync(home)
    agents_md = home / ".codex" / "AGENTS.md"
    agents_md.write_text("ручная правка\n", encoding="utf-8", newline="\n")
    (home / ".claude" / "core" / "AGENTS.core.md").write_text("# Ядро v2\n", encoding="utf-8")
    assert sync(home) == 3                                   # дрейф скипнут
    assert agents_md.read_text(encoding="utf-8") == "ручная правка\n"   # НЕ перезаписан
    assert "Ядро v2" not in agents_md.read_text(encoding="utf-8")

def test_sync_force_overwrite_resets_drift(make_canon):
    from codex_sync import sync, check
    home = make_canon(); sync(home)
    (home / ".codex" / "AGENTS.md").write_text("ручная правка\n", encoding="utf-8", newline="\n")
    assert sync(home, force={"all"}) == 0
    res = check(home)
    assert res["manual-drift"] == [] and res["canon-newer"] == []

def test_sync_preserves_foreign_config_and_is_atomic_style(make_canon):
    from codex_sync import sync
    home = make_canon(); sync(home)
    cfg = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert cfg.startswith("x = 1")                            # чужое цело
    assert "[mcp_servers.time]" in cfg
    assert not list((home / ".codex").glob("*.tmp-codex-sync"))   # tmp-файлы подчистились

def test_check_reports_missing_skill_junction_and_sync_heals(make_canon):
    import json as _json
    from codex_sync import sync, check
    home = make_canon()
    claude = home / ".claude"
    skill = claude / "skills" / "тест-скилл"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: тест-скилл\n---\n", encoding="utf-8")
    (claude / "codex-layer" / "skills-manifest.json").write_text(
        _json.dumps({"enable": ["тест-скилл"]}), encoding="utf-8")
    assert sync(home) == 0                                    # junction создан
    j = home / ".agents" / "skills" / "тест-скилл"
    assert j.exists()
    import subprocess; subprocess.run(["cmd", "/c", "rmdir", str(j)], capture_output=True)  # junction снят
    res = check(home)
    assert "skills/тест-скилл#junction" in res["canon-newer"]
    assert sync(home) == 0                                    # sync вылечил
    assert j.exists() and check(home)["canon-newer"] == []

def test_diff_cmd_shows_unified_diff(make_canon, capsys):
    from codex_sync import sync, diff_cmd
    home = make_canon(); sync(home)
    (home / ".codex" / "AGENTS.md").write_text("ручная правка\n", encoding="utf-8", newline="\n")
    diff_cmd(home)
    out = capsys.readouterr().out
    assert "AGENTS.md" in out and "+ручная правка" in out.replace("+ ручная", "+ручная")
