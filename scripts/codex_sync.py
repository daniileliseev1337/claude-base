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
    (r"mcp__excel__\w+", "инструменты плагина spreadsheets"),
    (r"mcp__word__\w+", "инструменты плагина documents"),
    (r"mcp__pdf-mcp__\w+", "инструменты плагина pdf"),
    (r"mcp__playwright__\w+", "инструменты плагина browser"),
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
