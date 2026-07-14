# -*- coding: utf-8 -*-
"""Генератор среды Codex из канона ~/.claude. Запуск: python codex_sync.py [--dry-run]"""
import hashlib
import json
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

# [I2] маркеры записи в tools: фронтматтера — есть хотя бы один → агент пишет файлы,
# sandbox_mode не сужаем; нет ни одного (и tools вообще заданы) → read-only ревьюер.
WRITE_TOOL_MARKERS = ("Write", "Edit", "search_and_replace", "add_paragraph")

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
    tools = _yaml_value(front, "tools")
    for pat, repl in TOOL_MAP:
        body = re.sub(pat, repl, body)
        desc = re.sub(pat, repl, desc)
    toml_text = f"name = {_t(name)}\ndescription = {_t(desc)}\nmodel = {_t(model)}\n"
    if tools and not any(marker in tools for marker in WRITE_TOOL_MARKERS):
        toml_text += 'sandbox_mode = "read-only"\n'   # [I2] ревьюер без Write/Edit — сузить sandbox в Codex
    toml_text += f"developer_instructions = {_toml_block(body.strip())}\n"
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

def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _read_canon(home: Path):
    """Общие входы: контенты канона + mcp-срез. Одна точка чтения для render_all и collect_inputs."""
    claude = home / ".claude"
    core = (claude / "core" / "AGENTS.core.md").read_text(encoding="utf-8")
    layer = (claude / "codex-layer" / "AGENTS.codex.md").read_text(encoding="utf-8")
    wl_text = (claude / "codex-layer" / "mcp-whitelist.json").read_text(encoding="utf-8")
    sm_text = (claude / "codex-layer" / "skills-manifest.json").read_text(encoding="utf-8")
    mcp = json.loads((home / ".claude.json").read_text(encoding="utf-8")).get("mcpServers", {})
    allow = json.loads(wl_text)["allow"]
    return core, layer, wl_text, sm_text, mcp, allow

def render_all(home: Path) -> dict:
    """Чистый рендер всех артефактов Codex: ключ → содержимое. Ничего не пишет."""
    claude = home / ".claude"
    core, layer, _, _, mcp, allow = _read_canon(home)
    out = {
        "AGENTS.md": render_agents_md(core, layer),
        "config.toml#managed": render_mcp_toml(mcp, allow).rstrip(),
        "hooks.json": json.dumps(render_hooks_json(home), ensure_ascii=False, indent=2),
    }
    for fname, toml_text in collect_agent_tomls(claude / "agents").items():
        out[f"agents/{fname}"] = toml_text
    return out

def collect_inputs(home: Path) -> dict:
    """sha256 входов канона; mcp-срез — только whitelisted (посторонние правки .claude.json не дёргают синк)."""
    claude = home / ".claude"
    core, layer, wl_text, sm_text, mcp, allow = _read_canon(home)
    inputs = {
        "core/AGENTS.core.md": _sha(core),
        "codex-layer/AGENTS.codex.md": _sha(layer),
        "codex-layer/mcp-whitelist.json": _sha(wl_text),
        "codex-layer/skills-manifest.json": _sha(sm_text),
        ".claude.json#mcpServers": _sha(json.dumps(
            {k: mcp[k] for k in sorted(allow) if k in mcp}, sort_keys=True, ensure_ascii=False)),
    }
    for f in sorted((claude / "agents").glob("*.md")):
        inputs[f"agents/{f.name}"] = _sha(f.read_text(encoding="utf-8"))
    return inputs

def manifest_path(home: Path) -> Path:
    return home / ".claude" / ".local-state" / "codex-sync-manifest.json"

def save_manifest(home: Path, inputs: dict, outputs: dict) -> None:
    p = manifest_path(home)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": 1, "inputs": inputs, "outputs": outputs},
                            ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

def load_manifest(home: Path):
    p = manifest_path(home)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None    # битый манифест = отсутствующий (безопасный режим: дрейф не перезапишем)

def _output_path(home: Path, key: str) -> Path:
    """Путь артефакта на диске по ключу рендера."""
    codex = home / ".codex"
    if key == "config.toml#managed":
        return codex / "config.toml"
    if key.startswith("agents/"):
        return codex / "agents" / key.split("/", 1)[1]
    return codex / key          # AGENTS.md, hooks.json

def read_disk_output(home: Path, key: str):
    p = _output_path(home, key)
    if not p.exists():
        return None
    if key == "config.toml#managed":
        m = re.search(re.escape(BEGIN) + r"\n(.*?)\n?" + re.escape(END), p.read_text(encoding="utf-8"), re.S)
        return m.group(1).rstrip() if m else None
    return p.read_text(encoding="utf-8")

def check(home: Path) -> dict:
    """Трёхсторонняя сверка канон ↔ манифест ↔ диск. Категория на каждый ключ рендера."""
    res = {"clean": [], "canon-newer": [], "manual-drift": []}
    if not (home / ".codex").exists():
        return res
    expected = render_all(home)
    man = load_manifest(home) or {}
    base_outputs = man.get("outputs", {})
    for key in sorted(expected):
        disk = read_disk_output(home, key)
        if disk is not None and disk == expected[key]:
            res["clean"].append(key)          # диск совпал с ожиданием — чисто в любом случае
        elif disk is None or base_outputs.get(key) == _sha(disk):
            res["canon-newer"].append(key)    # диск = то, что синк писал в прошлый раз → безопасно перегенерить
        else:
            res["manual-drift"].append(key)   # диск отличается и от ожидания, и от последней записи синка
    return res

def _backup_once(p: Path) -> None:
    """[I3] Бэкап файла перед перезаписью — однократно (не затирает более старую копию)."""
    bak = p.with_suffix(p.suffix + ".bak-codex-sync")
    if p.exists() and not bak.exists():
        bak.write_bytes(p.read_bytes())

def main(home: Path, dry_run: bool = False):
    claude, codex = home / ".claude", home / ".codex"
    rendered = render_all(home)
    manifest = json.loads((claude / "codex-layer" / "skills-manifest.json").read_text(encoding="utf-8"))
    cfg_path = codex / "config.toml"
    new_cfg = apply_managed_block(cfg_path.read_text(encoding="utf-8"), rendered["config.toml#managed"])
    agent_keys = [k for k in rendered if k.startswith("agents/")]
    enabled_skills = [n for n in manifest.get("enable", []) if (claude / "skills" / n / "SKILL.md").exists()]
    if dry_run:
        print(f"AGENTS.md: {len(rendered['AGENTS.md'].encode('utf-8'))} байт; "
              f"config.toml payload: {len(rendered['config.toml#managed'])}; "
              f"agents: {len(agent_keys)}; junctions: {len(enabled_skills)}")
        return
    for p in (cfg_path, codex / "AGENTS.md", codex / "hooks.json"):
        _backup_once(p)
    # [I4] newline="\n" — на Windows write_text() иначе разворачивает \n в \r\n
    (codex / "AGENTS.md").write_text(rendered["AGENTS.md"], encoding="utf-8", newline="\n")
    cfg_path.write_text(new_cfg, encoding="utf-8", newline="\n")
    (codex / "hooks.json").write_text(rendered["hooks.json"], encoding="utf-8", newline="\n")
    (codex / "agents").mkdir(exist_ok=True)
    for key in agent_keys:
        agent_path = codex / "agents" / key.split("/", 1)[1]
        _backup_once(agent_path)
        agent_path.write_text(rendered[key], encoding="utf-8", newline="\n")
    ensure_skill_junctions(manifest, claude / "skills", home / ".agents" / "skills")

if __name__ == "__main__":
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # кириллица при захвате из PowerShell
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Синк канона ~/.claude в ~/.codex")
    ap.add_argument("cmd", nargs="?", default="sync", choices=["sync", "check"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    home = Path.home()
    if args.cmd == "check":
        res = check(home)
        for cat in ("canon-newer", "manual-drift"):
            for key in res[cat]:
                print(f"{cat}\t{key}")
        sys.exit(3 if res["manual-drift"] else (2 if res["canon-newer"] else 0))
    else:
        main(home, args.dry_run)
