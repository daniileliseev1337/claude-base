# -*- coding: utf-8 -*-
"""Генератор среды Codex из канона ~/.claude. Запуск: python codex_sync.py [--dry-run]"""
import re
import sys
from pathlib import Path

BEGIN = "# >>> claude-base managed >>>"
END = "# <<< claude-base managed <<<"

def apply_managed_block(existing: str, payload: str) -> str:
    block = f"{BEGIN}\n{payload.rstrip()}\n{END}\n"
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    stripped = pattern.sub("", existing)          # убрать ВСЕ старые блоки
    if not stripped.strip():
        return block                              # [M1] пустой файл → только блок
    sep = "" if stripped.endswith("\n\n") else ("\n" if stripped.endswith("\n") else "\n\n")
    return stripped + sep + block

def _t(v: str) -> str:
    # TOML literal string для простых значений (Windows-пути без экранирования);
    # апостроф/перевод строки в literal невозможны — таким значениям basic string
    s = str(v)
    if "'" not in s and "\n" not in s:
        return "'" + s + "'"
    esc = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return '"' + esc + '"'

def render_mcp_toml(mcp_servers: dict, allow: list) -> str:
    out = []
    for name in sorted(mcp_servers):
        if name not in allow:
            continue
        cfg = mcp_servers[name]
        out.append(f"[mcp_servers.{name}]")
        out.append(f"command = {_t(cfg['command'])}")
        args = cfg.get("args", [])
        out.append("args = [" + ", ".join(_t(a) for a in args) + "]")
        env = cfg.get("env") or {}
        if env:
            out.append(f"[mcp_servers.{name}.env]")
            for k in sorted(env):
                out.append(f"{k} = {_t(env[k])}")
        out.append("")
    return "\n".join(out)

def render_skills_toml(manifest: dict, skills_dir: Path) -> str:
    out = []
    for name in manifest.get("enable", []):
        d = skills_dir / name
        if not (d / "SKILL.md").exists():
            print(f"[codex_sync] warn: скилл {name} не найден в {skills_dir}", file=sys.stderr)
            continue
        out.append("[[skills.config]]")
        out.append(f"path = {_t(str(d))}")
        out.append("enabled = true")
        out.append("")
    return "\n".join(out)

def _pwsh(script: Path) -> str:
    return f"powershell -NoProfile -ExecutionPolicy Bypass -File \"{script}\""

def render_hooks_json(home: Path) -> dict:
    s = home / ".claude" / "scripts"
    pm = home / ".claude" / "skills" / "project-memory" / "tools" / "hooks"
    def entry(script, timeout):
        return {"type": "command", "commandWindows": _pwsh(script), "timeout": timeout}
    return {"hooks": {
        "SessionStart": [{"hooks": [
            entry(s / "auto-pull.ps1", 30),
            entry(s / "graph-staleness-check.ps1", 15),
            entry(pm / "session_start.ps1", 10),
        ]}],
        "Stop": [{"hooks": [
            entry(pm / "session_end.ps1", 20),
            entry(s / "auto-push.ps1", 60),
        ]}],
        "PostToolUse": [{"matcher": ".*", "hooks": [entry(s / "log-tool-usage.ps1", 10)]}],
    }}

MODEL_MAP = {
    "opus": "gpt-5.6-sol",
    "fable": "gpt-5.6-sol",
    "sonnet": "gpt-5.6-terra",
    "haiku": "gpt-5.6-luna"
}

# TOOL_MAP переводит MCP-инструменты в описания плагинов.
TOOL_MAP = [
    (r"mcp__excel__(?:\w+|\\?\*)", "инструменты плагина spreadsheets"),
    (r"mcp__word__(?:\w+|\\?\*)", "инструменты плагина documents"),
    (r"mcp__pdf-mcp__(?:\w+|\\?\*)", "инструменты плагина pdf"),
    (r"mcp__playwright__(?:\w+|\\?\*)", "инструменты плагина browser"),
    (r"\bTask\b(?= tool| тул| \()", "spawn_agents"),
]

def _yaml_value(front: str, key: str) -> str:
    """Значение ключа фронтматтера; block-scalar (| и >) собирается целиком:
    | — с переводами строк, > — склейка пробелом."""
    m = re.search(rf"^{key}:[ \t]*(.*)$", front, re.M)
    if not m:
        return ""
    first = m.group(1).strip()
    if first not in ("|", "|-", ">", ">-"):
        return first
    lines = []
    for line in front[m.end():].split("\n"):
        if line.strip() == "":
            lines.append("")
        elif line.startswith((" ", "\t")):
            lines.append(line.strip())
        else:
            break
    joiner = "\n" if first.startswith("|") else " "
    return joiner.join(lines).strip()

def _toml_block(s: str) -> str:
    """Многострочный TOML: literal '''...''' (бэкслэши/кавычки сырыми);
    если внутри есть ''' — basic с экранированием."""
    if "'''" not in s:
        return "'''\n" + s + "\n'''"
    esc = s.replace("\\", "\\\\").replace('"""', '""\\"')
    return '"""\n' + esc + '\n"""'

def convert_agent_md(text: str):
    text = text.replace("\r\n", "\n")  # CRLF-агенты реальны (5/17 в базе)
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("Неверный формат: не найдена граница ---")
    front, body = m.group(1), m.group(2)
    name = _yaml_value(front, "name")
    model = MODEL_MAP.get(_yaml_value(front, "model"), "gpt-5.6-terra")
    desc = _yaml_value(front, "description")
    for pat, repl in TOOL_MAP:
        body = re.sub(pat, repl, body)
        desc = re.sub(pat, repl, desc)
    toml_text = (f"name = {_t(name)}\ndescription = {_t(desc)}\nmodel = {_t(model)}\n"
                 f"developer_instructions = {_toml_block(body.strip())}\n")
    return f"{name}.toml", toml_text

LANG_LINE = ("Отвечай пользователю по-русски. Код, имена файлов и идентификаторы — "
             "латиницей; комментарии в коде — по-русски.\n\n")

def render_agents_md(core: str, layer: str) -> str:
    out = LANG_LINE + core.strip() + "\n\n---\n\n" + layer.strip() + "\n"
    if len(out.encode("utf-8")) > 32768:
        raise ValueError("AGENTS.md превышает 32 KiB — сокращай ядро/слой")
    return out

def main(home: Path, dry_run: bool = False):
    import json
    claude, codex = home / ".claude", home / ".codex"
    core = (claude / "core" / "AGENTS.core.md").read_text(encoding="utf-8")
    layer = (claude / "codex-layer" / "AGENTS.codex.md").read_text(encoding="utf-8")
    agents_md = render_agents_md(core, layer)
    mcp_raw = json.loads((home / ".claude.json").read_text(encoding="utf-8")).get("mcpServers", {})
    mcp = {}
    for name, scfg in mcp_raw.items():
        if "command" not in scfg:       # remote (type=http/sse) — TOML-схема пока не реализована
            print(f"[codex_sync] warn: MCP-сервер {name} не stdio (type={scfg.get('type', '?')}) — пропущен", file=sys.stderr)
            continue
        mcp[name] = scfg
    allow = json.loads((claude / "codex-layer" / "mcp-whitelist.json").read_text(encoding="utf-8"))["allow"]
    manifest = json.loads((claude / "codex-layer" / "skills-manifest.json").read_text(encoding="utf-8"))
    payload = render_mcp_toml(mcp, allow) + "\n" + render_skills_toml(manifest, claude / "skills")
    cfg_path = codex / "config.toml"
    new_cfg = apply_managed_block(cfg_path.read_text(encoding="utf-8"), payload)
    hooks = render_hooks_json(home)
    agents_out = {}
    for f in sorted((claude / "agents").glob("*.md")):
        fname, toml_text = convert_agent_md(f.read_text(encoding="utf-8"))
        agents_out[fname] = toml_text
    if dry_run:
        print(f"AGENTS.md: {len(agents_md)} байт; config.toml payload: {len(payload)}; "
              f"hooks: {sum(len(v) for v in hooks['hooks'].values())} групп; agents: {len(agents_out)}")
        return
    for p in (cfg_path, codex / "AGENTS.md", codex / "hooks.json"):     # бэкап каждого существующего (однократно)
        bak = p.with_suffix(p.suffix + ".bak-codex-sync")
        if p.exists() and not bak.exists():
            bak.write_bytes(p.read_bytes())
    (codex / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    cfg_path.write_text(new_cfg, encoding="utf-8")
    (codex / "hooks.json").write_text(json.dumps(hooks, ensure_ascii=False, indent=2), encoding="utf-8")
    (codex / "agents").mkdir(exist_ok=True)
    for fname, toml_text in agents_out.items():
        (codex / "agents" / fname).write_text(toml_text, encoding="utf-8")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    main(Path.home(), ap.parse_args().dry_run)
