# -*- coding: utf-8 -*-
"""Генератор среды Codex из канона ~/.claude. Запуск: python codex_sync.py [--dry-run]"""
import hashlib
import json
import re
import sys
import tomllib
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

def render_mcp_toml(mcp_servers: dict, allow: list, bridge=frozenset()) -> str:
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
        if name in bridge:              # мост по требованию: не ронять десктоп и ждать тяжёлый старт
            out.append("required = false")
            out.append("startup_timeout_sec = 60")
        env = cfg.get("env") or {}
        if env:
            out.append(f"[mcp_servers.{name}.env]")
            for k in sorted(env):
                out.append(f"{k} = {_t(env[k])}")
        out.append("")
    return "\n".join(out)

def render_base_tables(home: Path) -> str:
    """Эталонные секции base.toml для managed-блока. Только таблицы; секции,
    заданные пользователем вне блока, пропускаются с предупреждением
    (дубль таблицы = невалидный TOML)."""
    p = home / ".claude" / "codex-layer" / "base.toml"
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    parsed = tomllib.loads(text)
    toplevel = [k for k, v in parsed.items() if not isinstance(v, dict)]
    if toplevel:
        raise ValueError(f"base.toml: top-level ключи запрещены (уедут в чужую таблицу): {toplevel}")
    cfg = home / ".codex" / "config.toml"
    outside = cfg.read_text(encoding="utf-8") if cfg.exists() else ""
    outside = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S).sub("", outside)
    try:
        user_tables = {k for k, v in tomllib.loads(outside).items() if isinstance(v, dict)}
    except tomllib.TOMLDecodeError as e:
        print(f"[codex_sync] warn: config.toml вне managed-блока не парсится ({e}) — фильтр коллизий пропущен",
              file=sys.stderr)
        user_tables = set()
    blocks, name, current = [], None, []
    for line in text.splitlines():
        m = re.match(r"\[([A-Za-z0-9_.-]+)\]", line.strip())
        if m:
            if name is not None:
                blocks.append((name, current))
            name, current = m.group(1).split(".")[0], [line]
        elif name is not None:
            current.append(line)
    if name is not None:
        blocks.append((name, current))
    kept = []
    for tname, lines in blocks:
        if tname in user_tables:
            print(f"[codex_sync] warn: секция [{tname}] задана вне managed-блока — эталон пропущен",
                  file=sys.stderr)
            continue
        kept.append("\n".join(lines).rstrip())
    return "\n\n".join(kept)

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
        return {"type": "command", "command": _pwsh(script), "timeout": timeout}
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

PROFILE_HEADER = ("# generated-by: codex_sync (канон: codex-layer/profiles/{name}.toml) — "
                  "править канон, не этот файл\n")

def render_profiles(home: Path) -> dict:
    """Профили Codex: файл канона → ~/.codex/<name>.config.toml целиком (файл наш)."""
    d = home / ".claude" / "codex-layer" / "profiles"
    out = {}
    if not d.exists():
        return out
    for f in sorted(d.glob("*.toml")):
        text = f.read_text(encoding="utf-8")
        tomllib.loads(text)      # невалидный канон профиля — падаем с понятной ошибкой
        out[f"{f.stem}.config.toml"] = PROFILE_HEADER.format(name=f.stem) + text
    return out

def render_target_codex(home: Path) -> dict:
    """Чистый рендер всех артефактов таргета codex: ключ → содержимое. Ничего не пишет."""
    claude = home / ".claude"
    core, layer, _, _, mcp, allow = _read_canon(home)
    overlay = load_overlay(home)
    eff_allow = sorted(set(allow) | set(overlay))
    out = {
        "AGENTS.md": render_agents_md(core, layer),
        "config.toml#managed": (render_base_tables(home) + "\n\n"
                                + render_mcp_toml(mcp, eff_allow, bridge=set(overlay))).strip(),
        "hooks.json": json.dumps(render_hooks_json(home), ensure_ascii=False, indent=2),
    }
    for fname, toml_text in collect_agent_tomls(claude / "agents").items():
        out[f"agents/{fname}"] = toml_text
    out.update(render_profiles(home))
    return out

def collect_inputs(home: Path) -> dict:
    """sha256 входов канона; mcp-срез — только whitelisted (посторонние правки .claude.json не дёргают синк)."""
    claude = home / ".claude"
    core, layer, wl_text, sm_text, mcp, allow = _read_canon(home)
    overlay = load_overlay(home)
    eff = sorted(set(allow) | set(overlay))
    inputs = {
        "core/AGENTS.core.md": _sha(core),
        "codex-layer/AGENTS.codex.md": _sha(layer),
        "codex-layer/mcp-whitelist.json": _sha(wl_text),
        "codex-layer/skills-manifest.json": _sha(sm_text),
        ".claude.json#mcpServers": _sha(json.dumps(
            {k: mcp[k] for k in eff if k in mcp}, sort_keys=True, ensure_ascii=False)),
        "codex-mcp-overlay": _sha(json.dumps(sorted(overlay), ensure_ascii=False)),
    }
    for f in sorted((claude / "agents").glob("*.md")):
        inputs[f"agents/{f.name}"] = _sha(f.read_text(encoding="utf-8"))
    tj = claude / "codex-layer" / "targets.json"
    if tj.exists():
        inputs["codex-layer/targets.json"] = _sha(tj.read_text(encoding="utf-8"))
    bt = claude / "codex-layer" / "base.toml"
    if bt.exists():
        inputs["codex-layer/base.toml"] = _sha(bt.read_text(encoding="utf-8"))
    prof = claude / "codex-layer" / "profiles"
    if prof.exists():
        for f in sorted(prof.glob("*.toml")):
            inputs[f"codex-layer/profiles/{f.name}"] = _sha(f.read_text(encoding="utf-8"))
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

def overlay_path(home: Path) -> Path:
    return home / ".claude" / ".local-state" / "codex-mcp-overlay.json"

def load_overlay(home: Path) -> list:
    """Оверлей доменного моста. Битый файл → warn + [] (fail-safe: SessionStart-хук
    не должен падать; render без моста → check покажет canon-newer/drift, не молчание)."""
    p = overlay_path(home)
    if not p.exists():
        return []
    try:
        names = json.loads(p.read_text(encoding="utf-8"))["enable"]
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise ValueError("enable должен быть списком строк")
        return names
    except (ValueError, KeyError, TypeError) as e:
        print(f"[codex_sync] warn: оверлей {p} битый ({e}) — мост считается выключенным", file=sys.stderr)
        return []

def save_overlay(home: Path, names: list) -> None:
    p = overlay_path(home)
    if not names:
        p.unlink(missing_ok=True)
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"enable": sorted(names)}, ensure_ascii=False, indent=2),
                 encoding="utf-8", newline="\n")

def _output_path_codex(home: Path, key: str) -> Path:
    """Путь артефакта таргета codex на диске по ключу рендера."""
    codex = home / ".codex"
    if key == "config.toml#managed":
        return codex / "config.toml"
    if key.startswith("agents/"):
        return codex / "agents" / key.split("/", 1)[1]
    return codex / key          # AGENTS.md, hooks.json

# Реестр таргетов: имя среды → рендер артефактов и резолвер путей.
# Новая среда = новая пара функций + строка здесь; ядро (check/sync/manifest) не трогается.
TARGETS = {
    "codex": {"render": render_target_codex, "path": _output_path_codex},
}

def _enabled_targets(home: Path) -> list:
    p = home / ".claude" / "codex-layer" / "targets.json"
    if not p.exists():
        return ["codex"]                       # обратная совместимость со старым каноном
    names = json.loads(p.read_text(encoding="utf-8"))["enable"]
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        raise ValueError(f"targets.json: неизвестные таргеты {unknown}; доступны {sorted(TARGETS)}")
    return names

def render_all(home: Path) -> dict:
    """Объединённый рендер включённых таргетов. Ключи уникальны между таргетами."""
    out = {}
    for name in _enabled_targets(home):
        part = TARGETS[name]["render"](home)
        dup = sorted(set(part) & set(out))
        if dup:
            raise ValueError(f"коллизия ключей между таргетами: {dup}")
        out.update(part)
    return out

def _output_path(home: Path, key: str) -> Path:
    for name in _enabled_targets(home):
        p = TARGETS[name]["path"](home, key)
        if p is not None:
            return p
    raise KeyError(key)

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
    # junctions скиллов сверяются по факту существования на диске (не по манифесту синка) —
    # снятый вручную junction иначе невидим для check() между запусками sync
    claude = home / ".claude"
    sm_path = claude / "codex-layer" / "skills-manifest.json"
    if sm_path.exists():
        manifest = json.loads(sm_path.read_text(encoding="utf-8"))
        skills_dir = claude / "skills"
        agents_skills_dir = home / ".agents" / "skills"
        for name in manifest.get("enable", []):
            if (skills_dir / name / "SKILL.md").exists() and not (agents_skills_dir / name).is_dir():
                res["canon-newer"].append(f"skills/{name}#junction")
    return res

def _backup_once(p: Path) -> None:
    """[I3] Бэкап файла перед перезаписью — однократно (не затирает более старую копию)."""
    bak = p.with_suffix(p.suffix + ".bak-codex-sync")
    if p.exists() and not bak.exists():
        bak.write_bytes(p.read_bytes())

def _write_atomic(p: Path, text: str) -> None:
    """Атомарная запись: tmp-файл рядом + os.replace (без «половинчатого» файла при сбое)."""
    import os
    tmp = p.with_name(p.name + ".tmp-codex-sync")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, p)

def sync(home: Path, force=None, dry_run: bool = False) -> int:
    """Drift-aware сборка ~/.codex из канона ~/.claude. Возврат: 0 ок, 3 — ручной дрейф пропущен
    (записан не весь рендер — часть ключей с ручными правками на диске сохранена как есть)."""
    force = set(force or ())
    claude, codex = home / ".claude", home / ".codex"
    if not codex.exists():
        print("[codex_sync] ~/.codex отсутствует — синк пропущен")
        return 0
    rendered = render_all(home)
    st = check(home)
    forced = set(rendered) if "all" in force else force
    to_write = [k for k in sorted(rendered)
                if k in st["canon-newer"] or (k in st["manual-drift"] and k in forced)]
    skipped = [k for k in st["manual-drift"] if k not in forced]
    manifest = json.loads((claude / "codex-layer" / "skills-manifest.json").read_text(encoding="utf-8"))
    enabled_skills = [n for n in manifest.get("enable", []) if (claude / "skills" / n / "SKILL.md").exists()]
    if dry_run:
        print(f"AGENTS.md: {len(rendered['AGENTS.md'].encode('utf-8'))} байт; "
              f"писать: {len(to_write)}; дрейф-скип: {len(skipped)}; junctions: {len(enabled_skills)}")
        return 3 if skipped else 0
    build_error = False
    for key in to_write:
        p = _output_path(home, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        _backup_once(p)
        if key == "config.toml#managed":
            existing = p.read_text(encoding="utf-8") if p.exists() else ""
            new_cfg = apply_managed_block(existing, rendered[key])
            try:
                tomllib.loads(new_cfg)
            except tomllib.TOMLDecodeError as e:
                print(f"[codex_sync] error: итоговый config.toml невалиден — запись отменена: {e}",
                      file=sys.stderr)
                build_error = True
                continue
            _write_atomic(p, new_cfg)
        else:
            _write_atomic(p, rendered[key])
    ensure_skill_junctions(manifest, claude / "skills", home / ".agents" / "skills")
    # манифест: записанное/чистое = ожидаемый хеш; пропущенный дрейф (ручной или гейт-ошибка) = прежнее значение
    old = (load_manifest(home) or {}).get("outputs", {})
    unwritten = set(skipped) | ({"config.toml#managed"} if build_error else set())
    outputs = {k: (_sha(rendered[k]) if k not in unwritten else old.get(k, ""))
               for k in rendered}
    save_manifest(home, collect_inputs(home), outputs)
    for k in skipped:
        print(f"[codex_sync] manual-drift пропущен: {k} (занеси в канон или sync --force-overwrite {k})")
    return 4 if build_error else (3 if skipped else 0)

def diff_cmd(home: Path) -> int:
    """Unified diff всех manual-drift ключей: ожидание из канона vs факт на диске. Всегда 0."""
    import difflib
    expected = render_all(home)
    st = check(home)
    for key in st["manual-drift"]:
        disk = read_disk_output(home, key) or ""
        for line in difflib.unified_diff(expected[key].splitlines(), disk.splitlines(),
                                         fromfile=f"{key} (ожидаемо из канона)",
                                         tofile=f"{key} (факт на диске)", lineterm=""):
            print(line)
        print()
    return 0

def mcp_cmd(home: Path, action: str, names: list) -> int:
    """Доменный MCP-мост по требованию: on = патч CRLF + оверлей + sync;
    off = снять оверлей + sync; status = whitelist/оверлей/патч-статус."""
    import mcp_crlf_patch as patcher
    mcp = json.loads((home / ".claude.json").read_text(encoding="utf-8")).get("mcpServers", {})
    overlay = load_overlay(home)
    if action == "status":
        allow = json.loads((home / ".claude" / "codex-layer" / "mcp-whitelist.json")
                           .read_text(encoding="utf-8"))["allow"]
        print(f"whitelist: {', '.join(sorted(allow))}")
        print(f"мост: {', '.join(overlay) if overlay else '(выключен)'}")
        for n in overlay:
            venv = patcher.venv_from_command(mcp.get(n, {}).get("command", ""))
            st = patcher.process_venv(venv, check_only=True) if venv else "не python-venv"
            print(f"  {n}: патч {st}")
        return 0
    if action == "on":
        if not names:
            print("[codex_sync] error: укажи сервер: mcp on <имя> [...]", file=sys.stderr)
            return 1
        unknown = [n for n in names if n not in mcp]
        if unknown:
            print(f"[codex_sync] error: нет в ~/.claude.json: {', '.join(unknown)}; "
                  f"доступны: {', '.join(sorted(mcp))}", file=sys.stderr)
            return 1
        for n in names:                       # патч ДО включения; провал → конфиг не тронут
            venv = patcher.venv_from_command(mcp[n].get("command", ""))
            if venv is None:
                print(f"[codex_sync] {n}: не python-venv — CRLF-патч не требуется")
                continue
            st = patcher.process_venv(venv, check_only=False)
            print(f"[codex_sync] {n}: патч {st}")
            if st not in patcher.OK:
                print(f"[codex_sync] error: {n}: патч не применён ({st}) — "
                      f"мост не включён, конфиг не тронут", file=sys.stderr)
                return 1
        save_overlay(home, sorted(set(overlay) | set(names)))
        rc = sync(home)
        print(f"[codex_sync] мост включён: {', '.join(load_overlay(home))} — рестартни Codex")
        return rc
    # off: без имён = выключить всё
    remove = set(names) if names else set(overlay)
    save_overlay(home, [n for n in overlay if n not in remove])
    rc = sync(home)
    print("[codex_sync] мост выключен — рестартни Codex")
    return rc

if __name__ == "__main__":
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # кириллица при захвате из PowerShell
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Синк канона ~/.claude в ~/.codex")
    ap.add_argument("cmd", nargs="?", default="sync", choices=["sync", "check", "diff", "mcp"])
    ap.add_argument("rest", nargs="*", metavar="on|off|status [имя ...]",
                    help="для mcp: действие и имена серверов")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-overwrite", action="append", default=[], metavar="KEY|all",
                     help="перезаписать ключ (или all) поверх ручного дрейфа")
    args = ap.parse_args()
    home = Path.home()
    if args.cmd == "check":
        res = check(home)
        for cat in ("canon-newer", "manual-drift"):
            for key in res[cat]:
                print(f"{cat}\t{key}")
        sys.exit(3 if res["manual-drift"] else (2 if res["canon-newer"] else 0))
    elif args.cmd == "diff":
        sys.exit(diff_cmd(home))
    elif args.cmd == "mcp":
        action = args.rest[0] if args.rest else "status"
        if action not in ("on", "off", "status"):
            ap.error(f"mcp: неизвестное действие {action} (on|off|status)")
        sys.exit(mcp_cmd(home, action, args.rest[1:]))
    else:
        sys.exit(sync(home, force=set(args.force_overwrite), dry_run=args.dry_run))
