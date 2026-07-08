#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Юнит-тесты чистой логики web_get (без сети). Прогон: python -m pytest -q  ИЛИ  python test_web_get.py"""
import os
import sys
import tempfile

# Сам тест-раннер печатает юникод-имена — под cp1251-консолью (Windows без
# PYTHONIOENCODING) это упало бы так же, как боевой баг web_get. Устойчивость первой строкой.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import web_get as w  # noqa: E402

FAILS = []


def check(name, cond):
    print(("  ok  " if cond else " FAIL ") + name)
    if not cond:
        FAILS.append(name)


# --- is_ru_host ---
check("ru tld .ru", w.is_ru_host("https://ridan.ru/catalog") is True)
check("ru tld .su", w.is_ru_host("http://foo.su/") is True)
check("рф punycode", w.is_ru_host("https://сайт.xn--p1ai/x") is True)
check("com не RU", w.is_ru_host("https://example.com/ru") is False)
check("ru в пути ≠ RU-host", w.is_ru_host("https://cdn.io/ru/file") is False)

# --- classify_kind ---
check("auto+.pdf → file", w.classify_kind("http://x/y.pdf", "auto", None) == "file")
check("auto+-o → file", w.classify_kind("http://x/y", "auto", "z.pdf") == "file")
check("auto plain → page", w.classify_kind("http://x/y", "auto", None) == "page")
check("явный page переопределяет .pdf", w.classify_kind("http://x/y.pdf", "page", None) == "page")
check("?query после .pdf всё равно file", w.classify_kind("http://x/y.pdf?v=2", "auto", None) == "file")

# --- build_ladder ---
check("egress RU → noproxy первым", w.build_ladder("page", True, "RU")[0] == "noproxy")
check("RU-цель заграница page → jina первым (быстрее прокси)", w.build_ladder("page", True, "NL")[0] == "jina")
check("RU-цель заграница page → ru как fallback", "ru" in w.build_ladder("page", True, "NL"))
check("RU-цель заграница FILE → ru первым (jina бинарь не отдаёт)", w.build_ladder("file", True, "NL")[0] == "ru")
check("заграница-цель заграница → direct первым", w.build_ladder("page", False, "NL")[0] == "direct")
check("page включает jina", "jina" in w.build_ladder("page", False, "NL"))
check("file исключает jina везде", "jina" not in w.build_ladder("file", True, "NL")
      and "jina" not in w.build_ladder("file", False, "NL"))

# --- verify_page ---
ok, _ = w.verify_page(b"<html><body>" + b"x" * 200 + b"</body></html>", "200")
check("page 200 непустая → ok", ok is True)
ok, r = w.verify_page(b"x" * 200, "404")
check("page 404 → fail", ok is False and "http" in r)
ok, r = w.verify_page(b"<html>Just a moment... checking your browser. " + b" " * 100 + b"</html>", "200")
check("page challenge → fail", ok is False and r.startswith("challenge"))
ok, r = w.verify_page(b"tiny", "200")
check("page слишком короткая → fail", ok is False)

# --- verify_file ---
tmp = tempfile.mkdtemp()
pdf = os.path.join(tmp, "a.pdf")
with open(pdf, "wb") as f:
    f.write(b"%PDF-1.7\n" + b"0" * 200)
ok, sig = w.verify_file(pdf, "200", expect_pdf=True)
check("file %PDF ждём pdf → ok", ok is True and sig == "pdf")

stub = os.path.join(tmp, "b.pdf")
with open(stub, "wb") as f:
    f.write(b"<!DOCTYPE html><html><body>not a pdf, a 404 page</body></html>" + b" " * 80)
ok, r = w.verify_file(stub, "200", expect_pdf=True)
check("file html-заглушка → fail", ok is False and "html-stub" in r)

png = os.path.join(tmp, "c.pdf")
with open(png, "wb") as f:
    f.write(b"\x89PNG\r\n" + b"0" * 200)
ok, r = w.verify_file(png, "200", expect_pdf=True)
check("file png но ждём pdf → fail", ok is False and "expected pdf" in r)

zipf = os.path.join(tmp, "d.zip")
with open(zipf, "wb") as f:
    f.write(b"PK\x03\x04" + b"0" * 200)
ok, sig = w.verify_file(zipf, "200", expect_pdf=False)
check("file zip без ожидания pdf → ok", ok is True and sig == "zip/office")

# --- next_hint непустой и упоминает MCP-ступени ---
check("hint page-foreign упоминает exa", "exa" in w.next_hint("page", False, []))
check("hint file упоминает playwright", "playwright" in w.next_hint("file", True, []))

# --- render_human: собирает отчёт со ступенями и preview ---
sample = {"ok": True, "url": "http://x", "kind": "page", "ru_host": False, "egress": "NL",
          "stage": "jina", "http": "200", "bytes": 999, "out": None,
          "preview": "Жироулавливающий зонт 中文 — спецтире",
          "tried": [{"stage": "direct", "ok": False, "http": None, "reason": "timeout"},
                    {"stage": "jina", "ok": True, "http": "200", "reason": "ok", "bytes": 999}]}
rh = w.render_human(sample)
check("render_human показывает победившую ступень", "via 'jina'" in rh)
check("render_human показывает провал ступени", "-- direct" in rh)
check("render_human несёт preview-юникод", "中文" in rh)

# --- РЕГРЕСС боевого бага 08.07: печать юникода в cp1251-консоли НЕ валит процесс ---
import subprocess  # noqa: E402
_tool = os.path.join(os.path.dirname(__file__), "..", "tools", "web_get.py")
_probe = (
    "import sys,io,os;"
    "sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='cp1251');"  # эмулируем Windows-консоль
    "sys.path.insert(0,os.path.dirname(r'" + _tool + "'));"
    "import web_get as w; w.force_utf8_stdio();"
    "print(w.render_human({'ok':True,'kind':'page','ru_host':False,'egress':'NL','stage':'jina',"
    "'http':'200','bytes':9,'out':None,'preview':'зонт 中文 emoji😀 —тире','tried':[]}))"
)
_env = dict(os.environ); _env.pop("PYTHONIOENCODING", None)  # как у пользователя — без него
_r = subprocess.run([sys.executable, "-c", _probe], capture_output=True, env=_env)
check("cp1251-консоль + юникод-preview → НЕ падает (exit 0)", _r.returncode == 0)
check("cp1251: нет UnicodeEncodeError в stderr", b"UnicodeEncodeError" not in _r.stderr)

print()
if FAILS:
    print(f"FAILED {len(FAILS)}: {FAILS}")
    sys.exit(1)
print("ALL PASS")
