# -*- coding: utf-8 -*-
"""Патчер CRLF-бага Python MCP SDK на Windows (modelcontextprotocol/python-sdk#2433).

stdio.py SDK оборачивает sys.stdout.buffer в TextIOWrapper без newline="" —
JSON-RPC уходит с \r\n; Rust-клиент Codex (rmcp) строг к \n → рукопожатие падает.
Клиент Claude Code \r терпит, поэтому под Claude баг невидим.
Патч дописывает newline="" только в stdout-обёртку. Идемпотентен; при незнакомом
коде (другая версия SDK) файл не трогается. Когда апстрим-фикс вольют — станет no-op.

Запуск: python mcp_crlf_patch.py (--venv <venv> [--venv ...] | --scan | --from-overlay) [--check]
Standalone: codex_sync импортирует этот модуль, обратного импорта нет.
"""
import argparse
import json
import sys
from pathlib import Path

BUGGY = 'TextIOWrapper(sys.stdout.buffer, encoding="utf-8")'
FIXED = 'TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")'
OK = {"patched", "already-ok"}


def classify(text: str) -> str:
    if FIXED in text:
        return "already-ok"
    if BUGGY in text:
        return "unpatched"
    return "unknown-pattern"


def stdio_path(venv: Path) -> Path:
    return venv / "Lib" / "site-packages" / "mcp" / "server" / "stdio.py"


def process_venv(venv: Path, check_only: bool) -> str:
    p = stdio_path(venv)
    if not p.exists():
        return "not-found"
    with open(p, encoding="utf-8", newline="") as f:   # newline="" — переводы строк файла не трогаем
        text = f.read()
    st = classify(text)
    if check_only or st != "unpatched":
        return st
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace(BUGGY, FIXED))
    return "patched"


def venv_from_command(command: str):
    """venv из command MCP-сервера (~/.claude.json): <venv>/Scripts/python.exe → <venv>; иначе None."""
    p = Path(command)
    if p.name.lower() == "python.exe" and p.parent.name.lower() == "scripts":
        return p.parents[1]
    return None


def run(venvs: list, check_only: bool) -> int:
    worst = 0
    for v in venvs:
        st = process_venv(Path(v), check_only)
        print(f"{v}\t{st}")
        if st not in OK:
            worst = 1
    return worst


def _overlay_venvs(home: Path) -> list:
    """venv'ы python-серверов из активного оверлея моста (формат задачи 2:
    .local-state/codex-mcp-overlay.json = {"enable": [имена]})."""
    op = home / ".claude" / ".local-state" / "codex-mcp-overlay.json"
    if not op.exists():
        return []
    names = json.loads(op.read_text(encoding="utf-8")).get("enable", [])
    mcp = json.loads((home / ".claude.json").read_text(encoding="utf-8")).get("mcpServers", {})
    out = []
    for n in names:
        v = venv_from_command(mcp.get(n, {}).get("command", ""))
        if v is not None:
            out.append(str(v))
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Патч CRLF-бага mcp/server/stdio.py в venv")
    ap.add_argument("--venv", action="append", default=[], help="путь к venv (повторяемый)")
    ap.add_argument("--scan", action="store_true", help="просканировать ~/.claude/mcp-servers/*/.venv")
    ap.add_argument("--from-overlay", action="store_true",
                    help="venv'ы серверов активного оверлея моста (для дрейф-скана)")
    ap.add_argument("--check", action="store_true", help="только диагностика, без записи")
    args = ap.parse_args()
    venvs = list(args.venv)
    if args.scan:
        root = Path.home() / ".claude" / "mcp-servers"
        if root.exists():
            venvs += [str(d / ".venv") for d in sorted(root.iterdir()) if (d / ".venv").is_dir()]
    if args.from_overlay:
        venvs += _overlay_venvs(Path.home())
        if not venvs:
            sys.exit(0)        # мост выключен — проверять нечего
    if not venvs:
        ap.error("[mcp_crlf_patch] нужен --venv, --scan или --from-overlay")
    sys.exit(run(venvs, args.check))
