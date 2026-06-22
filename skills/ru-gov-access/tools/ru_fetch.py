#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ru_fetch.py — достучаться до российских госреестров (pub.fsa / egrul / fgis-АРШИН и т.п.)
из ЛЮБОГО окружения Claude Code, включая машины с иностранным egress (VPN/Дубай или
форс через иностранный корп-прокси).

Логика (детерминированная, 0 галлюцинаций в маршрутизации):
  1. Определить РЕАЛЬНОЕ гео egress (ipinfo, мимо прокси).
  2. egress = RU            -> качать напрямую (curl --noproxy), RU-IP уже есть.
  3. egress != RU:
       a) если задан $RU_PROXY (надёжный платный RU-прокси) -> через него;
       b) иначе авто-источник: свежий список бесплатных RU-SOCKS5 (proxifly),
          health-check каждого через ipinfo (country==RU), гнать запрос через живой.
  Блок росс. госсайтов — ЧИСТО ГЕО (проверено 2026-06-22: RU-IP -> pub.fsa/fgis = 200,
  антибота нет), поэтому хватает RU-exit + curl, без браузерных антибот-сервисов.

Использование:
  python ru_fetch.py <URL> [-o out.html|out.pdf] [--timeout 20] [--tries 8]
  RU_PROXY=socks5h://user:pass@host:port python ru_fetch.py <URL>   # надёжный путь

Требуется: curl (есть на всех машинах) + python3. Никаких pip-зависимостей.
"""
import json, os, re, subprocess, sys, argparse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
PROXIFLY_RU = ("https://raw.githubusercontent.com/proxifly/free-proxy-list/"
               "main/proxies/countries/RU/data.txt")
IPINFO = "https://ipinfo.io/json"


def run(args, timeout):
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 28, b"", b"timeout"
    except Exception as e:  # noqa
        return 1, b"", str(e).encode()


def egress_country():
    # ipinfo напрямую, мимо любых прокси
    rc, out, _ = run(["curl", "--noproxy", "*", "-s", "--max-time", "12", IPINFO], 15)
    if rc == 0 and out:
        try:
            return json.loads(out.decode("utf-8", "replace")).get("country")
        except Exception:  # noqa
            pass
    return None


def fetch_direct(url, outfile, timeout):
    args = ["curl", "--noproxy", "*", "-sSL", "-A", UA,
            "-w", "\n__HTTP__%{http_code}", "--max-time", str(timeout)]
    if outfile:
        args += ["-o", outfile]
    args += [url]
    return run(args, timeout + 5)


def fetch_via(url, proxy, outfile, timeout):
    # ВАЖНО: без --noproxy (иначе curl проигнорирует -x)
    args = ["curl", "-sSL", "-A", UA, "-x", proxy,
            "-w", "\n__HTTP__%{http_code}", "--max-time", str(timeout)]
    if outfile:
        args += ["-o", outfile]
    args += [url]
    return run(args, timeout + 5)


def proxy_alive_ru(proxy):
    rc, out, _ = run(["curl", "-s", "--max-time", "7", "-x", proxy, IPINFO], 9)
    if rc == 0 and out:
        m = re.search(r'"country"\s*:\s*"([^"]+)"', out.decode("utf-8", "replace"))
        if m:
            return m.group(1)
    return None


def live_ru_proxies(max_check):
    rc, out, _ = run(["curl", "--noproxy", "*", "-s", "--max-time", "25", PROXIFLY_RU], 30)
    if rc != 0 or not out:
        return []
    cand = []
    for line in out.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("socks5://"):
            cand.append("socks5h://" + line[len("socks5://"):])
        elif line.startswith("socks4://"):
            cand.append("socks4a://" + line[len("socks4://"):])
        # http(s)-прокси для https через CONNECT у бесплатных почти всегда дохлые — пропускаем
    live = []
    for px in cand[:max_check]:
        if proxy_alive_ru(px) == "RU":
            live.append(px)
            if len(live) >= 3:        # хватит пары рабочих
                break
    return live


def http_code(stdout):
    if not stdout:
        return None
    m = re.search(rb"__HTTP__(\d{3})", stdout)
    return m.group(1).decode() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-o", "--out")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--tries", type=int, default=10, help="сколько прокси проверить")
    a = ap.parse_args()

    country = egress_country()
    print(f"[egress] country={country}")

    # 1. Уже в РФ -> напрямую
    if country == "RU":
        print("[route] egress=RU -> direct (--noproxy)")
        rc, out, err = fetch_direct(a.url, a.out, a.timeout)
        code = http_code(out)
        print(f"[result] HTTP {code} rc={rc}")
        if not a.out and out:
            sys.stdout.buffer.write(out)
        return 0 if code and code[0] in "23" else 2

    # 2/3. Иностранный egress -> через RU-прокси
    proxies = []
    env_px = os.environ.get("RU_PROXY")
    if env_px:
        print("[route] using $RU_PROXY")
        proxies = [env_px]
    else:
        print("[route] egress!=RU, no $RU_PROXY -> auto free RU-SOCKS5 (proxifly)")
        proxies = live_ru_proxies(a.tries)
        print(f"[proxies] live RU found: {len(proxies)} -> {proxies}")
        if not proxies:
            print("[FAIL] no live free RU proxy. "
                  "Set a reliable one: RU_PROXY=socks5h://host:port (see SKILL.md).")
            return 3

    for px in proxies:
        rc, out, err = fetch_via(a.url, px, a.out, a.timeout)
        code = http_code(out)
        print(f"[try] {px} -> HTTP {code} rc={rc}")
        if code and code[0] in "23":
            print(f"[OK] fetched via {px}")
            if not a.out and out:
                sys.stdout.buffer.write(out)
            return 0
    print("[FAIL] no RU proxy returned 2xx/3xx. Retry "
          "(list is refreshed each run) or set RU_PROXY.")
    return 4


if __name__ == "__main__":
    sys.exit(main())
