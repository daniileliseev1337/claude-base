#!/usr/bin/env python3
"""curate_rot.py — rot-куратор памяти проекта (propose → review → apply).

propose: read-only сверка STATUS.md с журналом и реальностью файлов →
         Claude/.curate/<stamp>/{proposals.json, REPORT.md}
apply:   бэкап затрагиваемых файлов в Claude/_backup_<дата_время>/ →
         применение ТОЛЬКО явно принятых предложений (--accept id1,id2).
         Скрипт сам никогда не решает, что применять: апрув ведёт
         человек/Claude (см. SKILL.md и prompts/rot.md).

Правила: пути в выходных артефактах — относительные от корня проекта
(мультидевайс, Я.Диск); пустой evidence → предложение невалидно; куратор
не пишет вне Claude/. git log сознательно не используется: папки объектов
живут вне git (решение владельца); при необходимости — точка расширения.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

JOURNAL_NAME = "ЖУРНАЛ СЕССИЙ.md"
STATUS_NAME = "STATUS.md"
ARCHIVE_REL = Path("Claude") / "_АРХИВ" / "из-курирования.md"

WAIT_RE = re.compile(r"(ждём|ждем|дедлайн|срок)", re.IGNORECASE)
WAIT_DO_RE = re.compile(r"\bдо\s+\d{2,4}[.\-]")
DONE_RE = re.compile(r"(готов|сдан|собран|выполнен)", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
RU_DATE_RE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
ABS_PATH_RE = re.compile(r"\b[A-Za-z]:[\\/]")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
LAST_UPD_RE = re.compile(r"Последнее обновление:\**\s*([0-9.\-]+)")
JOURNAL_HEAD_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def find_project_root(start: Path) -> Path | None:
    """Идёт вверх от start (≤12 уровней) до папки с Claude/ЖУРНАЛ СЕССИЙ.md."""
    d = Path(start).resolve()
    for _ in range(12):
        if (d / "Claude" / JOURNAL_NAME).exists():
            return d
        if d.name == "Claude" and (d / JOURNAL_NAME).exists():
            return d.parent
        if d.parent == d:
            return None
        d = d.parent
    return None


def _parse_date(token: str) -> date | None:
    m = ISO_DATE_RE.search(token)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = RU_DATE_RE.search(token)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def _path_candidates(line: str) -> list[str]:
    """Упоминания путей в строке: `бэктики` и markdown-ссылки. URL и
    абсолютные пути отбрасываются (абсолютные ловит отдельный сигнал)."""
    cands = BACKTICK_RE.findall(line) + MDLINK_RE.findall(line)
    out = []
    for c in cands:
        c = c.strip()
        if not c or c.startswith(("http://", "https://", "#")):
            continue
        if ABS_PATH_RE.search(c):
            continue
        if " " in c:
            continue
        if "/" in c or "\\" in c or re.search(r"\.\w{1,6}$", c):
            out.append(c.replace("\\", "/"))
    return out


class _Collector:
    def __init__(self):
        self.items = []
        self.dropped = 0

    def add(self, target, excerpt, proposed, evidence, confidence, action,
            signal):
        if not evidence:            # пустой evidence → предложение невалидно
            self.dropped += 1
            return
        self.items.append({
            "id": f"p{len(self.items) + 1}",
            "target": target,
            "current_excerpt": excerpt,
            "proposed_excerpt": proposed,
            "evidence": evidence,
            "confidence": confidence,
            "action": action,
            "source": "script",
            "signal": signal,
        })


def _scan_status(root: Path, col: "_Collector", today: date) -> None:
    status_path = root / "Claude" / STATUS_NAME
    if not status_path.exists():
        return
    target = "Claude/" + STATUS_NAME
    text = status_path.read_text(encoding="utf-8")

    last_upd = None
    m = LAST_UPD_RE.search(text)
    if m:
        last_upd = _parse_date(m.group(1))

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # 1) абсолютные пути запрещены правилами папки
        if ABS_PATH_RE.search(stripped):
            col.add(target, line.rstrip(), "",
                    ["в строке абсолютный путь — запрещён правилами папки "
                     "(корни устройств разные), заменить на относительный"],
                    "high", "flag", "absolute-path")

        # 2) упомянутый файл не существует
        for cand in _path_candidates(stripped):
            if not (root / cand).exists():
                col.add(target, line.rstrip(), "",
                        [f"файл не найден: {cand} (проверено от корня проекта)"],
                        "high", "flag", "file-missing")

        # 3) прошедшая дата в строке ожидания
        if WAIT_RE.search(stripped) or WAIT_DO_RE.search(stripped):
            if "Последнее обновление" not in stripped:
                d = _parse_date(stripped)
                if d and d < today:
                    col.add(target, line.rstrip(), "",
                            [f"дата {d.isoformat()} прошла (сегодня "
                             f"{today.isoformat()}), а строка всё ещё в статусе"],
                            "medium", "flag", "date-passed")

        # 4) «готово/сдано», но файл менялся после последнего обновления статуса
        if last_upd and DONE_RE.search(stripped):
            for cand in _path_candidates(stripped):
                f = root / cand
                if f.exists():
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
                    if mtime > last_upd:
                        col.add(target, line.rstrip(), "",
                                [f"{cand} менялся {mtime.isoformat()} — после "
                                 f"последнего обновления статуса "
                                 f"({last_upd.isoformat()}); «готово» могло устареть"],
                                "low", "flag", "done-file-changed")

    # 5) STATUS отстал от журнала
    journal = root / "Claude" / JOURNAL_NAME
    if last_upd and journal.exists():
        jtext = journal.read_text(encoding="utf-8")
        jdates = [_parse_date(d) for d in JOURNAL_HEAD_RE.findall(jtext)]
        jdates = [d for d in jdates if d]
        newer = [d for d in jdates if d > last_upd]
        if newer:
            col.add(target,
                    m.group(0) if m else "Последнее обновление",
                    "",
                    [f"последнее обновление STATUS — {last_upd.isoformat()}, "
                     f"после него {len(newer)} записей журнала "
                     f"(верхняя {max(newer).isoformat()}); прогнать обновление STATUS"],
                    "high", "flag", "status-behind-journal")


def propose(start: Path) -> Path:
    """Read-only анализ. Возвращает папку Claude/.curate/<stamp>/."""
    root = find_project_root(Path(start))
    if root is None:
        raise SystemExit(
            f"память проекта не найдена (нет Claude/{JOURNAL_NAME} вверх от {start})")
    today = date.today()
    col = _Collector()
    _scan_status(root, col, today)

    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = root / "Claude" / ".curate" / stamp
    n = 2
    while out_dir.exists():
        out_dir = root / "Claude" / ".curate" / f"{stamp}-{n}"
        n += 1
    out_dir.mkdir(parents=True)

    payload = {"created": stamp, "project": root.name,
               "dropped_no_evidence": col.dropped, "proposals": col.items}
    (out_dir / "proposals.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "REPORT.md").write_text(_render_report(payload),
                                       encoding="utf-8", newline="\n")
    return out_dir


def _render_report(payload: dict) -> str:
    props = payload["proposals"]
    by_conf = {c: sum(1 for p in props if p["confidence"] == c)
               for c in ("high", "medium", "low")}
    lines = [
        f"# Rot-курирование {payload['created']}",
        "",
        f"Проект: {payload['project']} (все пути — от корня проекта)",
        f"Предложений: {len(props)} (high: {by_conf['high']}, "
        f"medium: {by_conf['medium']}, low: {by_conf['low']}); "
        f"отброшено без evidence: {payload['dropped_no_evidence']}",
        "",
        "Дальше: review по пунктам → `curate_rot.py apply <stamp> --accept id,…`",
        "(бэкап в `Claude/_backup_<дата>/` создаётся автоматически; "
        "flag-пункты правятся вручную).",
        "",
    ]
    for p in props:
        lines += [
            f"## {p['id']} · {p['action']} · {p['confidence']} · "
            f"{p['target']} · {p['signal']}",
            "",
            f"> {p['current_excerpt']}",
            "",
            "Evidence:",
        ]
        lines += [f"- {e}" for e in p["evidence"]]
        if p["proposed_excerpt"]:
            lines += ["", "Предлагаемая замена:", f"> {p['proposed_excerpt']}"]
        lines.append("")
    if not props:
        lines.append("Протухания не найдены — статус согласован с реальностью.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Rot-куратор памяти проекта")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("propose",
                        help="read-only анализ → proposals.json + REPORT.md")
    pp.add_argument("--project", default=".", help="корень проекта или подпапка")
    ap = sub.add_parser("apply",
                        help="применить принятые предложения (после review)")
    ap.add_argument("stamp", help="метка прогона propose (папка в Claude/.curate/)")
    ap.add_argument("--accept", default="", help="id принятых через запятую: p1,p3")
    ap.add_argument("--project", default=".", help="корень проекта или подпапка")
    args = p.parse_args(argv)

    if args.cmd == "propose":
        out_dir = propose(Path(args.project))
        root = find_project_root(Path(args.project))
        rel = out_dir.relative_to(root).as_posix()
        data = json.loads((out_dir / "proposals.json").read_text(encoding="utf-8"))
        print(f"propose: {len(data['proposals'])} предложений → {rel}/")
        print(f"дальше: прочитать {rel}/REPORT.md, затем apply --accept id,…")
        return 0

    accepted = [a.strip() for a in args.accept.split(",") if a.strip()]
    res = apply(Path(args.project), args.stamp, accepted)
    for line in res["log"]:
        print(line)
    return 0 if not res["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
