#!/usr/bin/env python3
"""bootstrap.py — разворот нейтрального ядра памяти проекта в <Проект>/Claude/.

Часть скилла project-memory. Идемпотентен: существующие файлы НЕ перезаписывает
(перезапись — только явный --force). Ссылки в шаблонах — относительные.

Использование:
    python bootstrap.py "Имя проекта" [--target <корень>] [--profile core]
                        [--force <имя-или-относительный-путь>] ...
"""
import argparse
import socket
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates" / "core"

JOURNAL_NAME = "ЖУРНАЛ СЕССИЙ.md"

# (имя шаблона, относительный путь результата от корня проекта)
CORE_FILES = [
    ("CLAUDE.md.tmpl", Path("Claude") / "CLAUDE.md"),
    ("README.md.tmpl", Path("Claude") / "README.md"),
    ("ЖУРНАЛ СЕССИЙ.md.tmpl", Path("Claude") / JOURNAL_NAME),
    ("STATUS.md.tmpl", Path("Claude") / "STATUS.md"),
    ("КОНТЕКСТ.md.tmpl", Path("Claude") / "КОНТЕКСТ.md"),
    ("root-CLAUDE.md.tmpl", Path("CLAUDE.md")),
]

# Мостик роли к 16 доменным агентам: домен проекта → ведущий агент (по подстроке,
# регистр-независимо, первый матч). Неизвестный домен → "" (НЕ выдумывать агента).
# Специфичные домены проверяются РАНЬШЕ общего designer (ВОР≠проектирование).
_DOMAIN_AGENT = [
    (("вор", "объём", "объем", "спецификац", "ведомост", "пто", "подсчёт", "подсчет"), "pto-engineer"),
    (("ид", "аоср", "аомр", "исполнит", "освидетельств", "журнал работ"), "id-engineer"),
    (("смет", "гэсн", "фер", "кс-2", "кс-3", "расценк", "нр/сп"), "сметчик"),
    (("снабж", "упд", "накладн", "поставщик", "закупк", "тторг-12"), "снабженец"),
    (("замечан", "экспертиз"), "expertiza-responder"),
    (("коммерческ", " кп", "кп ", "тендер"), "kp-writer"),
    (("письм", "исходящ", "претензи", "сопроводит"), "letter-writer"),
    (("revit", "ревит", "pyrevit", "семейств"), "pyrevit-engineer"),
    (("норм", "гост", "снип", "пуэ", "цитат"), "norm-lookup"),
    (("ов", "вент", "кондиц", "отопл", "вк", "водоснаб", "канализ", "эо",
      "электр", "сс", "слаботоч", "скс", "скуд", "видеонабл", "иос", "проект"), "designer"),
]


def domain_to_agent(domain: str) -> str:
    """Домен проекта → имя ведущего доменного агента (или '' если неизвестен)."""
    d = (domain or "").lower()
    for subs, agent in _DOMAIN_AGENT:
        if any(s in d for s in subs):
            return agent
    return ""


def render(template_path: Path, project: str, today: str, host: str,
           role: str = "", domain: str = "") -> str:
    text = template_path.read_text(encoding="utf-8")
    agent = domain_to_agent(domain)
    return (text.replace("[ПРОЕКТ]", project)
                .replace("[ДАТА]", today)
                .replace("[УСТРОЙСТВО]", host)
                .replace("[РОЛЬ]", role or "_заполнить роль_")
                .replace("[ДОМЕН]", domain or "_заполнить домен_")
                .replace("[АГЕНТ]", agent or "_выбрать из 16 агентов_"))


def _forced(rel_out: Path, force: list[str]) -> bool:
    """--force матчит осознанный путь со слэшем (Claude/CLAUDE.md, ./CLAUDE.md)
    либо голое имя, если оно уникально среди CORE_FILES. Голое CLAUDE.md
    неоднозначно (корневой указатель и Claude/CLAUDE.md) — не матчится."""
    rel_posix = rel_out.as_posix()
    for f in force:
        fp = f.replace("\\", "/")
        if "/" in fp:
            if fp.startswith("./"):
                fp = fp[2:]
            if fp == rel_posix:
                return True
        elif rel_out.name == fp:
            if sum(1 for _, r in CORE_FILES if r.name == fp) == 1:
                return True
    return False


def bootstrap(project: str, target: Path, profile: str = "core",
              force: list[str] | None = None,
              role: str = "", domain: str = "") -> list[tuple[str, str]]:
    """Разворачивает ядро. Возвращает [("+"|"=", относительный_путь_posix)]."""
    if profile != "core":
        raise SystemExit(
            f"профиль '{profile}' не поддерживается в v1 (только core; "
            f"templates/profiles/ — точка расширения)")
    force = force or []
    today = date.today().isoformat()
    host = socket.gethostname().upper()
    report: list[tuple[str, str]] = []
    for tmpl_name, rel_out in CORE_FILES:
        out = Path(target) / rel_out
        if out.exists() and not _forced(rel_out, force):
            report.append(("=", rel_out.as_posix()))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(TEMPLATES / tmpl_name, project, today, host, role, domain),
                       encoding="utf-8", newline="\n")
        report.append(("+", rel_out.as_posix()))
    return report


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(
        description="Разворот памяти проекта (skill project-memory)")
    p.add_argument("project", help="имя проекта — подставится в [ПРОЕКТ]")
    p.add_argument("--target", default=".", help="корень проекта (default: cwd)")
    p.add_argument("--profile", default="core",
                   help="зарезервировано (v1: только core)")
    p.add_argument("--force", action="append", default=[], metavar="ФАЙЛ",
                   help="перезаписать существующий файл (можно повторять); "
                        "для CLAUDE.md указывать путь: ./CLAUDE.md (корневой) "
                        "или Claude/CLAUDE.md")
    p.add_argument("--role", default="", help="роль в КОНТЕКСТ.md (напр. 'инженер ОВ')")
    p.add_argument("--domain", default="",
                   help="домен проекта → ведущий агент (ОВ/ВК/ЭО/СС/ИД/ВОР/смета/снабжение/Revit...)")
    args = p.parse_args(argv)
    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"целевая папка не существует: {target}", file=sys.stderr)
        return 1
    report = bootstrap(args.project, target, args.profile, args.force,
                       args.role, args.domain)
    for mark, rel in report:
        label = "создан" if mark == "+" else "уже есть, не тронут"
        print(f"{mark} {rel}  ({label})")
    created = sum(1 for m, _ in report if m == "+")
    print(f"Итого: создано {created}, пропущено {len(report) - created}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
