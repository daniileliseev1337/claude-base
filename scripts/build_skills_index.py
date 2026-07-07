# -*- coding: utf-8 -*-
"""Генератор skills/skills.md из frontmatter самих скиллов (Блок 4 реворка, 2026-07-07).

Ручной вики-индекс устаревал при каждом новом скилле (решение владельца: генератор).
Источник истины — description в SKILL.md каждого скилла; индекс детерминированный,
править руками БЕСПОЛЕЗНО (перезапишется).

Запуск:  python ~/.claude/scripts/build_skills_index.py
Когда:   после добавления/переименования скилла (или хвостом /sync-base).
"""
import re
from datetime import date
from pathlib import Path

BASE = Path.home() / ".claude" / "skills"
OUT = BASE / "skills.md"


def first_paragraph(desc: str, limit: int = 200) -> str:
    """Первый абзац description (склейка строк до пустой), ужатый до limit по слову."""
    para = []
    for line in desc.splitlines():
        line = line.strip()
        if not line:
            if para:
                break
            continue
        para.append(line)
    text = " ".join(para).strip()
    if not text:
        return "(без описания)"
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"
    return text


def read_frontmatter(skill_md: Path):
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fm = m.group(1)
    name, desc = None, ""
    try:  # PyYAML понимает все стили (|, |-, >, >-, однострочный)
        import yaml
        data = yaml.safe_load(fm) or {}
        name = str(data.get("name") or "").strip() or None
        desc = str(data.get("description") or "")
    except Exception:  # fallback без yaml: блок = строки с отступом после description:
        nm = re.search(r"^name:\s*(.+)$", fm, re.M)
        if nm:
            name = nm.group(1).strip().strip("\"'")
        dm = re.search(r"^description:[ \t]*(.*)$", fm, re.M)
        if dm:
            inline = dm.group(1).strip()
            if inline and inline not in ("|", "|-", ">", ">-"):
                desc = inline
            else:
                block = []
                seen = False
                for line in fm.splitlines():
                    if re.match(r"^description:", line):
                        seen = True
                        continue
                    if seen:
                        if line.startswith((" ", "\t")) or not line.strip():
                            block.append(line)
                        else:
                            break
                desc = "\n".join(block)
    return name or skill_md.parent.name, first_paragraph(desc)


def main():
    rows = []
    for d in sorted(BASE.iterdir(), key=lambda p: p.name.lower()):
        sm = d / "SKILL.md"
        if not d.is_dir() or not sm.exists():
            continue
        fm = read_frontmatter(sm)
        if fm:
            rows.append(fm)

    lines = [
        "---",
        "generated: " + date.today().isoformat(),
        "generator: scripts/build_skills_index.py",
        "---",
        "",
        "# Скиллы — индекс (ГЕНЕРИРУЕТСЯ, руками не править)",
        "",
        "Источник истины — frontmatter `description` каждого `skills/<name>/SKILL.md`.",
        "Пересборка: `python ~/.claude/scripts/build_skills_index.py`.",
        "",
        f"Всего скиллов: {len(rows)}",
        "",
    ]
    for name, desc in rows:
        lines.append(f"- [[{name}]] — {desc}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"OK: {OUT} ({len(rows)} скиллов)")


if __name__ == "__main__":
    main()
