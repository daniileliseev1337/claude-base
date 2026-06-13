# 2026-06-10 — /sync-base: полная актуализация + установка всех per-machine инструментов

## Что сделал
- `/sync-base` по новому алгоритму (Шаги 0–6): git актуален (BEHIND=0, AHEAD=0),
  создан отсутствовавший `CLAUDE.user.md` (Шаг 0).
- Самопроверка `verify-claude-base.ps1`: **23/23 PASS**.
- Инвентарь по `mcp-manifest.json` (12 MCP, 15 Python-пакетов): всё стояло,
  кроме playwright.
- **Поставлено в этой сессии:**
  - playwright MCP — через `setup-extras.ps1 -Yes`, зарегистрирован, ✓ Connected
    без перезапуска Claude Code; `extras-pending.flag` снят.
  - graphify CLI — `uv tool install graphifyy` (0.8.36), exe в `~/.local/bin/`.
  - Ollama 0.30.6 + модель qwen2.5:7b (4.7 ГБ).
- Inkscape 1.4.4 оказался уже установлен (winget «existing package»).
- Блок `pto` (experimental, pilot_machines=[DANIIL]) не активирован: hostname
  этого ПК — DaniilPC, точного совпадения нет.

## Где сломался / уроки
1. **setup-extras.ps1 в фоне самоотменяется**: внутри `Read-Host "Proceed? (y/N)"` —
   в неинтерактивном запуске даёт `[WARN] Cancelled by user` с exit 0 (!).
   Лечится флагом `-Yes`. Урок: фоновый запуск setup-extras — только с `-Yes`.
2. **winget не качает с github.com**: системный WinINET-прокси выключен
   (ProxyEnable=0), env-прокси winget игнорирует → `InternetOpenUrl() 0x80072f19`.
   Обход: скачать установщик через `Invoke-WebRequest -Proxy <corp> -ProxyCredential`
   (прокси пропускает обычный HTTPS к github, в отличие от git-CONNECT),
   затем silent-установка (`/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`).
3. **Inkscape ложно «не установлен»** при проверке через `command -v`/PATH —
   winget не добавляет его в PATH. Проверять `Test-Path 'C:\Program Files\Inkscape\bin\inkscape.exe'`
   (в новой версии /sync-base это уже учтено).
4. **Sandbox-классификатор блокирует `uv tool install graphifyy`** как typosquat
   (двойная «y» выглядит опечаткой «graphify»). Разблокировалось только после
   проверки пакета на PyPI (0.8.36, MIT, реальный) и явного подтверждения
   пользователем точного написания через AskUserQuestion.
5. **graphify skill version lag**: CLI 0.8.36 предупреждает, что скилл в базе
   от 0.8.35. На consumer-ПК `graphify install` запускать нельзя (перезапись
   файлов базы) → записан feedback `feedback-pending/graphify-skill-version-lag.md`.

## Источники
- `~/.claude/mcp-manifest.json`, `~/.claude/scripts/setup-extras.ps1`,
  `~/.claude/scripts/verify-claude-base.ps1`, `~/.claude/blocks/pto/BLOCK.md`
- PyPI: страница пакета graphifyy (проверка подлинности)
- github releases: OllamaSetup.exe v0.30.6 (скачан через прокси)
