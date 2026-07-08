#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_get.py — ЕДИНЫЙ вход веб-доступа Claude Code: одна команда вместо ручного
перебора curl/exa/firecrawl/playwright/WebFetch/r.jina по памяти.

Боль, которую чиним: лестница веб-доступа жила ТЕКСТОМ (правило в CLAUDE.md).
Модель каждый раз должна была её вспоминать и вручную дёргать 3-6 инструментов
по очереди — ступени забывались, падение одной читалось как «в интернете нет».
Здесь детерминированная часть лестницы вынесена в КОД: скрипт сам определяет
egress, перебирает ступени до первого ВЕРИФИЦИРОВАННОГО успеха и печатает, что
сработало. Если кодовые ступени исчерпаны — печатает next_hint: какую MCP-ступень
взять Claude (exa/firecrawl/playwright). 0 «забыл ступень», 0 токенов на логику.

Честная граница (см. SKILL.md): код покрывает curl-семейство + r.jina (облачный
reader). MCP-ступени (exa http, firecrawl, playwright-браузер) из питона не
дёргаются — они инструменты Claude; скрипт лишь маршрутизирует к ним явно.

RU-слой НЕ дублируется: российский exit-IP делегируется соседнему скиллу
ru-gov-access (tools/ru_fetch.py) — один дом на RU-SOCKS5-логику.

Usage:
  python web_get.py <URL> [--kind page|file|auto] [-o out] [--timeout 20] [--json]
  # --kind auto (дефолт): file если задан -o или URL кончается на .pdf/.zip/...
  # --json: только машиночитаемый JSON в stdout (для парсинга Claude), без лога

Needs: curl + python3. No pip deps. ru-слой требует соседний ru_fetch.py.
"""
import argparse
import json
import os
import re
import subprocess
import sys

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
IPINFO = "https://ipinfo.io/json"
RU_FETCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "ru-gov-access", "tools", "ru_fetch.py")

# Маркеры HTML-заглушки/челленджа: тело с ними = НЕ настоящий контент, ступень провалена.
CHALLENGE_MARKERS = (
    "ddos-guard", "cf-browser-verification", "cf_chl_", "just a moment",
    "checking your browser", "attention required", "enable javascript and cookies",
    "проверка браузера", "доступ ограничен",
)
FILE_EXT = (".pdf", ".zip", ".xlsx", ".xls", ".docx", ".doc", ".rar",
            ".dwg", ".dxf", ".png", ".jpg", ".jpeg", ".rtf", ".7z")
# Сигнатуры бинарных файлов (первые байты) для верификации скачанного.
MAGIC = {
    b"%PDF": "pdf", b"PK\x03\x04": "zip/office", b"Rar!": "rar",
    b"\x89PNG": "png", b"\xff\xd8\xff": "jpeg", b"{\\rt": "rtf",
    b"AC10": "dwg", b"7z\xbc\xaf": "7z",
}


def run(args, timeout):
    """Запуск процесса. Возвращает (returncode, stdout_bytes, stderr_bytes)."""
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 28, b"", b"timeout"
    except Exception as e:  # noqa: BLE001
        return 1, b"", str(e).encode()


def egress_country():
    """РЕАЛЬНОЕ гео egress (мимо прокси окна). None если не пробилось."""
    rc, out, _ = run(["curl", "--noproxy", "*", "-s", "--max-time", "12", IPINFO], 15)
    if rc != 0 or not out:
        return None
    m = re.search(rb'"country"\s*:\s*"([^"]+)"', out)
    return m.group(1).decode() if m else None


def is_ru_host(url):
    """RU-цель по TLD: .ru/.su/.рф(xn--p1ai). Грубо, но покрывает наш словарь сайтов."""
    m = re.match(r"https?://([^/:]+)", url.strip(), re.I)
    host = (m.group(1) if m else url).lower()
    return bool(re.search(r"\.(ru|su)$", host) or host.endswith(".xn--p1ai"))


def classify_kind(url, kind, out):
    """auto → file, если задан -o или расширение файловое; иначе page."""
    if kind in ("page", "file"):
        return kind
    low = url.lower().split("?")[0]
    if out or any(low.endswith(e) for e in FILE_EXT):
        return "file"
    return "page"


def _http_code(stdout):
    m = re.search(rb"__HTTP__(\d{3})", stdout or b"")
    return m.group(1).decode() if m else None


def verify_page(body_bytes, http):
    """Страница валидна: 2xx, непустая, без challenge-маркеров."""
    if not http or http[0] not in "23":
        return False, f"http={http}"
    if not body_bytes or len(body_bytes) < 64:
        return False, "empty/too-short"
    head = body_bytes[:4000].decode("utf-8", "replace").lower()
    for mk in CHALLENGE_MARKERS:
        if mk in head:
            return False, f"challenge:{mk}"
    return True, "ok"


def verify_file(path, http, expect_pdf):
    """Файл валиден: скачан, не HTML-заглушка, магическая сигнатура известна."""
    if not http or http[0] not in "23":
        return False, f"http={http}"
    if not path or not os.path.exists(path) or os.path.getsize(path) < 64:
        return False, "missing/too-short"
    with open(path, "rb") as f:
        head = f.read(8)
    if head[:5].lower() in (b"<!doc", b"<html"):
        return False, "html-stub (not a file)"
    sig = next((name for magic, name in MAGIC.items() if head.startswith(magic)), None)
    if sig is None:
        return False, f"unknown-magic:{head[:4]!r}"
    if expect_pdf and sig != "pdf":
        return False, f"expected pdf, got {sig}"
    return True, sig


def curl_page(url, direct, timeout):
    """curl страницы. direct=True → --noproxy (обход корп-прокси окна)."""
    args = ["curl", "-sSL", "-A", UA, "-w", "\n__HTTP__%{http_code}",
            "--max-time", str(timeout)]
    if direct:
        args += ["--noproxy", "*"]
    args += [url]
    rc, out, _ = run(args, timeout + 6)
    http = _http_code(out)
    body = re.sub(rb"\n__HTTP__\d{3}$", b"", out or b"")
    return http, body


def curl_file(url, out_path, direct, timeout):
    args = ["curl", "-sSL", "-A", UA, "-w", "__HTTP__%{http_code}",
            "--max-time", str(timeout), "-o", out_path]
    if direct:
        args += ["--noproxy", "*"]
    args += [url]
    rc, tail, _ = run(args, timeout + 6)
    return _http_code(tail)


def jina_page(url, timeout):
    """r.jina.ai — облачный reader: берёт антибот/JS-сайты, отдаёт текст. Без ключа."""
    jurl = "https://r.jina.ai/" + url
    args = ["curl", "-sSL", "-A", UA, "-w", "\n__HTTP__%{http_code}",
            "--max-time", str(timeout + 15), jurl]
    rc, out, _ = run(args, timeout + 22)
    http = _http_code(out)
    body = re.sub(rb"\n__HTTP__\d{3}$", b"", out or b"")
    return http, body


def ru_fetch_page(url, out_path, timeout):
    """Делегируем RU exit-IP соседнему скиллу ru-gov-access (один дом на RU-SOCKS5)."""
    if not os.path.exists(RU_FETCH):
        return None, b"", "ru_fetch.py not found"
    args = [sys.executable, RU_FETCH, url, "--timeout", str(timeout)]
    if out_path:
        args += ["-o", out_path]
    rc, out, err = run(args, timeout + 40)
    # ru_fetch печатает лог в stdout + тело (если без -o). Код успеха: rc==0.
    return (0 if rc == 0 else 1), out, err.decode("utf-8", "replace")[-200:]


def build_ladder(kind, ru_host, egress):
    """
    Порядок ступеней = f(тип, RU-цель, egress). Возвращает список имён ступеней.
    Принципы: дешёвое-и-стабильное раньше; RU-цель с иностранного egress не берётся
    прямым curl (гео) → облако/RU-канал; для ЧТЕНИЯ облачная jina быстрее и надёжнее
    эфемерного бесплатного RU-прокси (эмпирика 2026-07-08) → jina перед ru; jina умеет
    только ТЕКСТ, поэтому для FILE её нет — сырой файл берёт только curl/ru_fetch.
    """
    if egress == "RU":
        # RU-egress выходит и в РФ, и в мир напрямую.
        return ["noproxy", "direct", "jina"] if kind == "page" else ["noproxy", "direct"]
    if ru_host:
        # RU-цель, egress не-RU. ВАЖНО (боевой урок 2026-07-08, palerom.png взялся
        # прямым curl с NL-egress): НЕ все RU-сайты гео-блокированы — RU-коммерч B2B
        # часто отдаёт напрямую. Поэтому СНАЧАЛА быстрый прямой (noproxy/direct, 1-2с),
        # облако jina — на гео-блок (consultant-класс), медленный ru_fetch — последним
        # fallback (бесплатный RU-прокси ищется долго, нужен лишь реально блокированным).
        return ["noproxy", "direct", "jina", "ru"] if kind == "page" else ["noproxy", "direct", "ru"]
    # Зарубежная цель, egress не-RU: прямой работает.
    return ["direct", "noproxy", "jina"] if kind == "page" else ["direct", "noproxy"]


def next_hint(kind, ru_host, tried):
    """Что взять Claude, когда кодовые ступени исчерпаны. MCP — не из питона."""
    if kind == "file":
        return ("Кодовые ступени пали. Для файла: (1) playwright browser_navigate на "
                "КАРТОЧКУ товара → снять cookies → curl -b (Метод 2 feedback_web_direct_access); "
                "(2) если RU-госсайт по прямому URL — уже пробовал ru_fetch. "
                "Скриншот карточки глазами ДО вывода «документа нет».")
    if ru_host:
        return ("Кодовые ступени пали для RU-страницы. Claude: (1) exa/firecrawl "
                "(облачный канал, читают RU-коммерч сайты); (2) SPA-данные реестра → "
                "playwright с RU-proxy (ru-gov-access, data-слой). Скриншот перед выводом «нет».")
    return ("Кодовые ступени пали для зарубежной страницы. Claude: (1) exa web_search/"
            "web_fetch (semantic, антибот); (2) firecrawl_scrape; (3) playwright для JS/SPA. "
            "Сделай browser_take_screenshot ДО вывода «сайта/данных нет».")


def attempt(stage, url, kind, out_path, timeout, expect_pdf):
    """Одна ступень: выполнить + верифицировать. Возвращает dict-результат."""
    r = {"stage": stage}
    if kind == "page":
        if stage == "direct":
            http, body = curl_page(url, direct=False, timeout=timeout)
        elif stage == "noproxy":
            http, body = curl_page(url, direct=True, timeout=timeout)
        elif stage == "jina":
            http, body = jina_page(url, timeout=timeout)
        elif stage == "ru":
            rc, body, err = ru_fetch_page(url, None, timeout)
            http = "200" if rc == 0 else None
            if rc != 0:
                r.update(ok=False, http=http, reason=err or "ru_fetch fail")
                return r
        else:
            r.update(ok=False, reason="unknown stage")
            return r
        ok, reason = verify_page(body, http)
        r.update(ok=ok, http=http, bytes=len(body or b""), reason=reason)
        if ok:
            r["preview"] = body[:600].decode("utf-8", "replace")
        return r
    # file
    if stage == "ru":
        rc, _out, err = ru_fetch_page(url, out_path, timeout)
        http = "200" if rc == 0 else None
    elif stage in ("direct", "noproxy"):
        http = curl_file(url, out_path, direct=(stage == "noproxy"), timeout=timeout)
    else:
        r.update(ok=False, reason="unknown stage")
        return r
    ok, reason = verify_file(out_path, http, expect_pdf)
    r.update(ok=ok, http=http, reason=reason)
    if ok:
        r["out"] = out_path
        r["bytes"] = os.path.getsize(out_path)
    return r


def fetch(url, kind="auto", out=None, timeout=20, egress=None):
    """Главная лестница. Возвращает единый dict-результат (для --json и как API)."""
    kind = classify_kind(url, kind, out)
    ru_host = is_ru_host(url)
    if egress is None:
        egress = egress_country()
    expect_pdf = bool(out and out.lower().endswith(".pdf")) or url.lower().split("?")[0].endswith(".pdf")
    ladder = build_ladder(kind, ru_host, egress)

    tried = []
    for stage in ladder:
        res = attempt(stage, url, kind, out, timeout, expect_pdf)
        tried.append({k: res[k] for k in ("stage", "ok", "http", "reason", "bytes")
                      if k in res})
        if res.get("ok"):
            return {"ok": True, "url": url, "kind": kind, "ru_host": ru_host,
                    "egress": egress, "stage": stage, "http": res.get("http"),
                    "bytes": res.get("bytes"), "out": res.get("out"),
                    "preview": res.get("preview"), "tried": tried}
    return {"ok": False, "url": url, "kind": kind, "ru_host": ru_host,
            "egress": egress, "stage": None, "tried": tried,
            "next": next_hint(kind, ru_host, tried)}


def force_utf8_stdio():
    """
    БОЕВОЙ ФИКС 2026-07-08: web_get печатает preview/reason с юникодом (китайские
    бренды оборудования, спецтире, emoji). Windows-консоль без PYTHONIOENCODING = cp1251,
    и print() ловит UnicodeEncodeError → «упал на выводе» (репорт владельца на palerom/
    tincraft). Инструмент обязан быть устойчив САМ, не полагаться на env пользователя.
    reconfigure есть у TextIOWrapper (Py 3.7+); при перенаправлении/отсутствии — тихо мимо.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


def render_human(res):
    """Человекочитаемый отчёт как СТРОКА (тестируемо отдельно от печати)."""
    lines = [f"[egress] {res['egress']}  [kind] {res['kind']}  [ru_host] {res['ru_host']}"]
    for t in res["tried"]:
        mark = "OK " if t.get("ok") else "-- "
        size = f"({t['bytes']}b)" if t.get("bytes") else ""
        lines.append(f"  {mark}{t['stage']:8} http={t.get('http')} {t.get('reason','')} {size}")
    if res["ok"]:
        where = res.get("out") or f"{res.get('bytes')}b (preview ниже)"
        lines.append(f"[OK] via '{res['stage']}' -> {where}")
        if res.get("preview") and not res.get("out"):
            lines.append("---8<--- preview ---")
            lines.append(res["preview"])
    else:
        lines.append(f"[FAIL] все кодовые ступени пали.\n[next] {res['next']}")
    return "\n".join(lines)


def main():
    force_utf8_stdio()
    ap = argparse.ArgumentParser(description="Единый вход веб-доступа (лестница в коде).")
    ap.add_argument("url")
    ap.add_argument("--kind", choices=["page", "file", "auto"], default="auto")
    ap.add_argument("-o", "--out")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--json", action="store_true", help="только JSON в stdout")
    a = ap.parse_args()

    res = fetch(a.url, kind=a.kind, out=a.out, timeout=a.timeout)

    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(render_human(res))
    return 0 if res["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
