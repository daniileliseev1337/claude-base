# Разведка 5: хуки Codex — CLI vs десктоп

Дата: 2026-07-14 · Агент: sonnet · Статус: завершено

## Официальная механика
- **`hooks.json` — официальный формат** (learn.chatgpt.com/docs/hooks); схема нашего генератора совпадает дословно (`type/command/commandWindows/statusMessage/timeout`). Альтернатива — инлайн `[[hooks.<Event>]]` в config.toml.
- Хронология: `[features].codex_hooks` → переименован в `hooks`; 2026-05-08 in-app trust review в десктопе; **2026-05-14 hooks GA (stable)**; 2026-07-09 десктоп влит в единый ChatGPT.exe.
- События (10): SessionStart, SubagentStart, PreToolUse, PermissionRequest, PostToolUse, UserPromptSubmit, SubagentStop, Stop, PreCompact, PostCompact. `notify` в config.toml — отдельный старый механизм (только agent-turn-complete; у нас уже работает для computer-use).
- Локальный факт: `codex features list` → `hooks stable true`; версия codex-cli 0.144.2 (бандл внутри десктопа, standalone не установлен).

## CLI vs десктоп
| Аспект | CLI | Десктоп |
|---|---|---|
| Схема hooks.json | поддерживается | тот же движок |
| Trust хуков | `/hooks` в TUI | in-app trust review (с 2026-05-08) |
| Известные баги | #17478/#15252/#17268 — Windows-гейт снимали/возвращали | **#21639 открыт: hooks вообще не исполняются после апдейта десктопа** (SessionStart и PreToolUse, и локальные и глобальные) |
| notify | работает | подтверждено рабочим у нас |

## Наш hooks.json — валиден, но не исполняется
Следов исполнения ноль: `~/.codex/log/` пуст (только codex-login.log), state-файлы без упоминаний hook/trust, при этом сессии в session_index есть (SessionStart должен был сработать). Две причины (не взаимоискл.):
1. **Хуки не прошли trust review** — non-managed command hooks обязаны быть explicitly trusted, иначе молча пропускаются («pending review»).
2. **Десктоп-регрессия #21639** (открыта, без воркэраунда).
Различить без живого запуска нельзя — пункт тест-заезда.

## Рекомендация автосинка (Эпик 1), ранжированно
1. **Хук Claude Code** (PostToolUse/Stop → codex_sync.py) — основной: инфраструктура auto-pull/auto-push подтверждённо работает, задержка мгновенная, сложность минимальная. Риск конкурентной записи config.toml при открытом Codex → писать во временный файл + atomic rename.
2. **Windows FileSystemWatcher / Планировщик** на ~/.claude/{core,codex-layer,agents,skills} — страховочный канал: ловит правки ЛЮБЫМ редактором, не только Claude. Сложнее (lifecycle процесса).
3. Хуки Codex — НЕ как единственный канал, пока #21639 открыт и trust не подтверждён (плюс trust — ручной шаг).
4. AGENTS.md-инструкция «прогони синк» — только fallback-подсказка, не гарантия.

## Дрейф-детектор
Событий/API на ручную правку ~/.codex нет; **mtime/hash-скан достаточен** (сравнение с последним снапшотом генератора; бэкапы `.bak-codex-sync` уже есть).

## Источники
learn.chatgpt.com/docs/hooks, /docs/config-file/config-advanced, /docs/changelog; openai/codex#21639, #17478, #24093, #11808; PR #15252, #17268. Локально: ~/.codex/{hooks.json,config.toml,log/,.codex-global-state.json,session_index.jsonl}, `codex features list`, `codex --version`.
