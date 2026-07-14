# -*- coding: utf-8 -*-
"""Смоук рукопожатия MCP-сервера БЕЗ клиента: initialize по stdio → ответ.
Проверяет и CRLF-чистоту сырых байт (Codex/rmcp строг к \n — суть эпика 3).

Запуск: python mcp_handshake_smoke.py <команда> [аргументы...]
Пример: python mcp_handshake_smoke.py C:/.../.venv/Scripts/python.exe C:/.../main.py
Exit: 0 = ответ получен и LF-чистый; 1 = нет ответа / CRLF / ошибка initialize.
"""
import json
import subprocess
import sys

def main(cmd: list) -> int:
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
           "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                      "clientInfo": {"name": "handshake-smoke", "version": "0"}}}
    try:
        proc.stdin.write((json.dumps(req) + "\n").encode("utf-8"))
        proc.stdin.flush()
        line = proc.stdout.readline()          # сырые байты — переводы строк видны
    finally:
        proc.kill()
    if not line:
        print("FAIL: сервер не ответил на initialize")
        return 1
    if line.endswith(b"\r\n"):
        print("FAIL: ответ с CRLF — патч mcp_crlf_patch не применён (Codex не примет)")
        return 1
    try:
        resp = json.loads(line.decode("utf-8"))
    except ValueError:
        print(f"FAIL: не-JSON ответ: {line[:120]!r}")
        return 1
    if "result" not in resp:
        print(f"FAIL: initialize отклонён: {resp}")
        return 1
    print("OK: initialize принят, ответ LF-чистый")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: mcp_handshake_smoke.py <команда> [аргументы...]"); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
