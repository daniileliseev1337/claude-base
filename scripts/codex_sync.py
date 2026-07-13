# -*- coding: utf-8 -*-
"""Генератор среды Codex из канона ~/.claude. Запуск: python codex_sync.py [--dry-run]"""
import re

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
