# Сессия 2026-07-06 — реализация скилла project-memory (v1)

## Что сделано

Скилл `~/.claude/skills/project-memory/` реализован по спеке
`docs/superpowers/specs/2026-07-06-project-memory-skill-design.md` (проектная папка
сессии) через superpowers:writing-plans → executing-plans (inline, без воркеров).
План: `docs/superpowers/plans/2026-07-06-project-memory-skill.md` (там же).

Состав (спека §3 — 1:1):
- `templates/core/` — 5 обезличенных шаблонов (CLAUDE.md, README, ЖУРНАЛ СЕССИЙ.md,
  STATUS.md, root-CLAUDE.md) с плейсхолдерами [ПРОЕКТ]/[ДАТА]/[УСТРОЙСТВО];
  `templates/profiles/` — пустая точка расширения (первый профиль — блок ПТО).
- `tools/bootstrap.py` — идемпотентный разворот ядра; `--force` только явный
  (голое неоднозначное имя CLAUDE.md не матчится: `./CLAUDE.md` / `Claude/CLAUDE.md`).
- `tools/curate_rot.py` — propose (read-only, 5 детерминированных сигналов:
  file-missing, absolute-path, date-passed, status-behind-journal,
  done-file-changed; все action=flag) → review (Claude + AskUserQuestion) →
  apply (бэкап `Claude/_backup_<дата>/` ДО записи; только `--accept id,…`;
  пустой evidence отклоняется в обеих фазах; target вне Claude/ запрещён;
  modify/archive применяются, flag — только вручную).
- `tools/hooks/session_start.ps1` (SessionStart: верх журнала в контекст + маркер
  сессии) и `session_end.ps1` (Stop: «файлы менялись, журнал нет» → exit 2
  максимум один раз за сессию). ASCII-only исходники (PS 5.1/no-BOM), кириллическое
  имя журнала — из codepoints; state в `~/.claude/.local-state/project-memory/`
  (ключ session_id, вне синка облака).
- `prompts/rot.md` — семантический слой куратора (Claude дописывает c*-пункты в тот
  же proposals.json). `SKILL.md` + `README.md` (сниппет settings.json). Строка в
  индексе `skills/skills.md`.
- Тесты: 40 passed (11 bootstrap + 21 curate + 8 hooks-smoke Windows-only),
  переносимые (tmp, синтетика).

## Решения открытых вопросов спеки §10 (зафиксированы в плане)

1. Хуки подключаются по месту из папки скилла (обновляются с auto-pull), установка —
   сниппет из README через update-config, включает пользователь.
2. AskUserQuestion из Python не зовётся: скрипт готовит proposals/REPORT, Claude ведёт
   апрув, apply применяет только `--accept`-список.
3. Отдельный commands/-файл не нужен — скилл и есть slash-команда.
4. session_end = событие **Stop** (SessionEnd никто не видит; Stop c exit 2 возвращает
   stderr Клоду) + маркер start_epoch_ms от session_start; анти-шум: stop_hook_active,
   «напомнил один раз», журнал-обновлён, скан с short-circuit и исключениями
   (.curate/_backup_/сам журнал).

## Где ломалось (поймано тестами/e2e — ценность TDD)

1. `--force CLAUDE.md`: голое имя совпадало с точным rel-путём корневого указателя →
   перезапись неоднозначной цели. Фикс: путь со слэшем = осознанный, голое имя —
   только при уникальности.
2. Усечение start_epoch до секунд: журнал, созданный в ту же секунду, что и старт,
   выглядел «обновлённым после старта» → напоминание глохло. Фикс: миллисекунды.
3. Тестовая state-папка лежала внутри корня проекта → свежий маркер сам триггерил
   скан изменений. Фикс фикстуры: проект в подпапке, state — сосед (как в проде).
4. Ложняк propose на собственном шаблоне STATUS: `_backup_<дата>/` в бэктиках
   счёлся путём. Фикс: плейсхолдеры `<...>` — не пути + инвариант-тест
   «свежий bootstrap → 0 предложений».

## Приёмка

`auditor` (sonnet): **PASSED** по всем 6 пунктам (обезличивание grep'ом; структура
1:1 со спекой; pytest сам прогнал — 40 passed; решения владельца соблюдены — без git
на памяти, без порогов в днях в логике напоминаний, profiles/ пуст, бэкап до записи,
пустой evidence отклоняется; JSON-сниппет README распарсен). WARN: кэши pytest в
папке скилла — вычищены, в git не попадали (whitelist-.gitignore базы).

## Открыто / следующие шаги

- Хуки НЕ включены: ждут решения владельца (добавить сниппет из README скилла в
  settings.json через update-config на его машинах).
- Обкатка на реальном объекте (bootstrap поверх существующей ручной папки — файлы
  не затрёт, досоздаст недостающие).
- Профиль id-tom — за блоком ПТО (точка расширения готова, `--profile` зарезервирован).

## Уроки

- Событийный enforcement журнала возможен ТОЛЬКО через Stop-хук с exit 2 — вывод
  SessionEnd не доходит ни до модели, ни до пользователя.
- PS 5.1-хуки: [Console]::InputEncoding = UTF8 обязателен для чтения stdin-JSON
  с не-ASCII путями; кириллические имена файлов в ASCII-only исходнике — сборкой
  из codepoints.
- Сравнения mtime в хуках — только в миллисекундах (секунды дают гонку в пределах
  одной секунды).
