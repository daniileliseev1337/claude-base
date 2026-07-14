# -*- coding: utf-8 -*-
"""Плоский AGENTS.md проекта из CLAUDE.md (П9, Эпик 1 мульти-LLM).
Запуск: python gen_project_agents.py <project_root>. Чужой AGENTS.md (без маркера) не трогает."""
import re
import sys
from pathlib import Path

MARKER = "generated-by: gen_project_agents"
SOURCES = ("CLAUDE.md", "Claude/CLAUDE.md")

def render_project_agents(root: Path):
    parts = []
    for rel in SOURCES:
        p = root / rel
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"^@.*$", "", t, flags=re.M)              # @import — Claude-специфика, в плоском файле не работает
        t = t.replace("Claude Code", "агентная среда")        # vendor-нейтрализация
        parts.append(f"<!-- источник: {rel} -->\n\n" + t.strip())
    if not parts:
        return None
    head = (f"<!-- {MARKER} -->\n"
            "<!-- НЕ править руками: источник — CLAUDE.md проекта; перегенерация:\n"
            "     python ~/.claude/skills/project-memory/tools/gen_project_agents.py . -->\n\n")
    return head + "\n\n---\n\n".join(parts) + "\n"

def main(root: Path) -> int:
    out = render_project_agents(root)
    if out is None:
        print("[gen_project_agents] CLAUDE.md не найден — проект без ядра, выходим")
        return 1
    dst = root / "AGENTS.md"
    if dst.exists() and MARKER not in dst.read_text(encoding="utf-8").splitlines()[0]:
        print(f"[gen_project_agents] {dst} существует и создан не нами — не трогаю "
              "(если он и есть канон проекта, наш рендер не нужен)")
        return 2
    dst.write_text(out, encoding="utf-8", newline="\n")
    print(f"[gen_project_agents] записан {dst}")
    return 0

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()))
