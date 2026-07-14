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
        if "url" in cfg:                # [I1] remote (http/sse) — без command/args
            out.append(f"[mcp_servers.{name}]")
            out.append(f"url = {_t(cfg['url'])}")
            out.append("")
            continue
        if "command" not in cfg:        # [I1] ни command, ни url — пропуск с предупреждением
            print(f"[codex_sync] warn: MCP-сервер {name} без command и без url (type={cfg.get('type', '?')}) — пропущен", file=sys.stderr)
            continue
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
    """не используется main() с 2026-07-14 — skills.config не работает в десктоп-сборке,
    оставлена для будущих версий"""
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

def _is_junction(p: Path) -> bool:
    """Проверить, является ли путь Windows directory junction или symlink."""
    import os
    try:
        if not p.is_dir():
            return False
        # Windows symlink (os.path.islink работает, но может не ловить все junction'ы)
        # Альтернативный способ: проверить атрибут файла FILE_ATTRIBUTE_REPARSE_POINT (0x400)
        stat_result = os.stat(p, follow_symlinks=False)
        return bool(stat_result.st_file_attributes & 0x400) or os.path.islink(str(p))
    except (OSError, AttributeError):
        return False

def ensure_skill_junctions(manifest: dict, skills_dir: Path, agents_skills_dir: Path) -> list:
    """Junction на каждый скилл из манифеста в ~/.agents/skills (стандартный путь Codex).
    Возвращает список созданных. Чужие папки (не junction на skills_dir) не трогает."""
    import subprocess
    agents_skills_dir.mkdir(parents=True, exist_ok=True)
    enabled = [n for n in manifest.get("enable", []) if (skills_dir / n / "SKILL.md").exists()]
    for n in manifest.get("enable", []):
        if n not in enabled:
            print(f"[codex_sync] warn: скилл {n} не найден в {skills_dir}", file=sys.stderr)
    made = []
    for n in enabled:
        dst = agents_skills_dir / n
        if dst.exists():
            continue
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(skills_dir / n)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            made.append(n)
        else:
            print(f"[codex_sync] warn: junction {n} не создан: {r.stderr.strip()}", file=sys.stderr)
    # cleanup: junction'ы, указывающие в skills_dir, но выпавшие из манифеста
    for child in agents_skills_dir.iterdir():
        if child.name in enabled or not child.is_dir():
            continue
        if _is_junction(child) and (skills_dir / child.name).exists():
            try:
                child.rmdir()   # junction снимается rmdir, содержимое источника не трогается
            except OSError:
                print(f"[codex_sync] warn: не удалось удалить junction {child.name}", file=sys.stderr)
    return made

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

def collect_agent_tomls(agents_dir: Path) -> dict:
    """[I2] Обходит agents/*.md; пропускает не-агентские файлы (без фронтматтера
    или без name: в фронтматтере) с предупреждением вместо мусорного '.toml'."""
    out = {}
    for f in sorted(agents_dir.glob("*.md")):
        try:
            fname, toml_text = convert_agent_md(f.read_text(encoding="utf-8"))
        except ValueError as e:
            print(f"[codex_sync] warn: {f.name} пропущен: {e}", file=sys.stderr)
            continue
        if fname == ".toml":
            print(f"[codex_sync] warn: {f.name} пропущен: пустое имя (нет name: в фронтматтере)", file=sys.stderr)
            continue
        out[fname] = toml_text
    return out

LANG_LINE = ("Отвечай пользователю по-русски. Код, имена файлов и идентификаторы — "
             "латиницей; комментарии в коде — по-русски.\n\n")

def render_agents_md(core: str, layer: str) -> str:
    out = LANG_LINE + core.strip() + "\n\n---\n\n" + layer.strip() + "\n"
    if len(out.encode("utf-8")) > 32768:
        raise ValueError("AGENTS.md превышает 32 KiB — сокращай ядро/слой")
    return out

def _backup_once(p: Path) -> None:
    """[I3] Бэкап файла перед перезаписью — однократно (не затирает более старую копию)."""
    bak = p.with_suffix(p.suffix + ".bak-codex-sync")
    if p.exists() and not bak.exists():
        bak.write_bytes(p.read_bytes())

def main(home: Path, dry_run: bool = False):
    import json
    claude, codex = home / ".claude", home / ".codex"
    core = (claude / "core" / "AGENTS.core.md").read_text(encoding="utf-8")
    layer = (claude / "codex-layer" / "AGENTS.codex.md").read_text(encoding="utf-8")
    agents_md = render_agents_md(core, layer)
    mcp = json.loads((home / ".claude.json").read_text(encoding="utf-8")).get("mcpServers", {})
    allow = json.loads((claude / "codex-layer" / "mcp-whitelist.json").read_text(encoding="utf-8"))["allow"]
    manifest = json.loads((claude / "codex-layer" / "skills-manifest.json").read_text(encoding="utf-8"))
    payload = render_mcp_toml(mcp, allow)
    cfg_path = codex / "config.toml"
    new_cfg = apply_managed_block(cfg_path.read_text(encoding="utf-8"), payload)
    hooks = render_hooks_json(home)
    agents_out = collect_agent_tomls(claude / "agents")
    # Прогноз junction'ов для dry_run
    enabled_skills = [n for n in manifest.get("enable", []) if (claude / "skills" / n / "SKILL.md").exists()]
    if dry_run:
        print(f"AGENTS.md: {len(agents_md.encode('utf-8'))} байт; config.toml payload: {len(payload)}; "
              f"hooks: {sum(len(v) for v in hooks['hooks'].values())} групп; agents: {len(agents_out)}; "
              f"junctions: {len(enabled_skills)}")
        return
    for p in (cfg_path, codex / "AGENTS.md", codex / "hooks.json"):
        _backup_once(p)
    (codex / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    cfg_path.write_text(new_cfg, encoding="utf-8")
    (codex / "hooks.json").write_text(json.dumps(hooks, ensure_ascii=False, indent=2), encoding="utf-8")
    (codex / "agents").mkdir(exist_ok=True)
    for fname, toml_text in agents_out.items():
        agent_path = codex / "agents" / fname
        _backup_once(agent_path)
        agent_path.write_text(toml_text, encoding="utf-8")
    ensure_skill_junctions(manifest, claude / "skills", home / ".agents" / "skills")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    main(Path.home(), ap.parse_args().dry_run)
