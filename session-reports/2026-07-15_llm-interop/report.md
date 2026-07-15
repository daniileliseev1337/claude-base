# Эпик 4a — LLM interop

## Итог

Создана рабочая вертикаль Claude↔Codex через общий task/result-контракт. Канон
остаётся в `~/.claude`; Codex получает skill через управляемый junction.

## Реализация

- Добавлен skill `llm-interop`: строгие task/result JSON Schema, direct-exec bridge,
  read-only по умолчанию, UTF-8, hop-limit, secret/path gates.
- Codex запускается без пользовательского runtime-конфига; Claude read-only — в
  `plan` с инструментами чтения.
- Timeout завершает дерево дочернего процесса на Windows и POSIX.
- Успех сохраняется как JSON + Markdown; ошибка — failure JSON + Markdown с
  редактированной диагностикой.
- `handoff-to-new-chat` связан с машинным контрактом; vendor-транскрипты не
  переносятся.
- Исправлен `hooks.json`: `commandWindows` → `command`.
- Skill-манифест классифицирует каждый канонический skill как enabled или skipped
  с причиной; drift-check проверяет цель junction, а не только имя каталога.
- Тяжёлый Revit/AutoCAD MCP-оверлей выключен после доменной задачи.

## Верификация

- Skill validator: PASS с `PYTHONUTF8=1`; без переменной Windows-версия валидатора
  ошибочно читает UTF-8 как системную кодировку.
- Unit/golden: 79 PASS; project-memory: 4 PASS.
- `codex_sync.py check`: clean; dry-run: 0 writes, 0 drift, 11 junctions.
- Codex live smoke: completed, 4/4 checks PASS, `changes=[]`; результат рядом.
- Claude live smoke: внешний 403 доступа организации; bridge сохранил redacted
  failure JSON + Markdown, ложный result не создавал.
- Forward-test отдельным агентом: transport PASS; task read-only, относительные
  пути, hop_count=0, explicit done_when, без secret/config refs.
- Независимый auditor: PASSED после двух fix-wave; остаточных findings нет.

## Инвентаризация базы

- Правила/core/skills: 165 отслеживаемых файлов, 36 исходных skill-каталогов;
  после Эпика 4 — 37.
- Runtime: 16 агентов, 78 файлов scripts, 15 MCP registrations; локальные CAD MCP
  содержат крупные venv и не входят в переносимый слой.
- Подтверждены открытые риски: один активный PowerShell hook не парсится в Windows
  PowerShell; PAT может сохраниться в git remote URL; remote installer исполняется
  без checksum; MCP env ранее мог копироваться буквально; CAD MCP допускают
  arbitrary code. Эти дефекты не исправлялись попутно.

## Следующий инкремент

Отдельно выполнить semantic adapter ролей и оставшихся skills, тест-заезд
documents/spreadsheets/pdf, generic capability registry и исправление активных
security/runtime findings. Не включать всё массово до forward-test.

## Уточнения после приёмки

- Роль Codex зафиксирована как полноценный партнёр по строительным задачам, а не
  временная замена Claude. Паритет Revit/AutoCAD считать подтверждённым только
  после одинаковых живых задач и сравнения результата.
- Текущий проектный `AGENTS.md` принадлежит `gen_project_agents`, совпадает с
  рендером `CLAUDE.md` + `Claude/CLAUDE.md`; повторная генерация не нужна.
- Обнаружен пробел bootstrap: Codex умеет определить, нужен ли генератор, но
  текущий Codex-side хук только предупреждает. Для гарантированного первого входа
  нужен fallback на `CLAUDE.md` и безопасная content-based автогенерация.
- Чужой `AGENTS.md` без маркера генератора не перезаписывать; читать как канон и
  отдельно предлагать согласование с Claude-инструкциями.
- Официально подтверждено: локальные сообщения и cloud tasks делят пятичасовое
  окно, дополнительные недельные ограничения могут применяться. Индикатор
  `217k / 258k` относится к контексту задачи, а не к квоте аккаунта.

## Handoff 2026-07-15 11:34 · DANIILPC

### Цель новой задачи

Продолжить Эпик 4b с закрытия project bootstrap, затем собрать общий capability
registry, semantic adapters 16 ролей и TOOL_MAP. Сохранять функциональный паритет,
а не механически переносить все навыки и агенты, переживающие реворк.

### Стартовые источники

- `Claude/STATUS.md` и верх `Claude/ЖУРНАЛ СЕССИЙ.md` текущего проекта.
- `0_СТАТУС_программы.md` — детальная истина программы.
- `docs/superpowers/specs/2026-07-14-codex-phase3-roadmap.md` — порядок эпиков.
- Этот отчёт: сначала `rg -n "^##|^###"`, затем читать только нужные секции.

### Done when ближайшего инкремента

- Codex сам различает актуальный, устаревший, отсутствующий и чужой `AGENTS.md`.
- Генератор обновляет только собственный файл по сравнению содержимого и не
  затирает ручные инструкции.
- Проект с одним `CLAUDE.md` получает рабочий bootstrap без команды от владельца.
- Поведение покрыто тестами и независимым аудитом; глобальный sync остаётся clean.
- После bootstrap оформлены границы следующей части Эпика 4b: capability registry,
  adapters ролей/skills и TOOL_MAP.

### Известные блокеры и риски

- Живой Codex→Claude smoke остаётся заблокирован внешним `403 organization access`.
- Нейтральное правило межмодельного партнёрства и полная классификация 37 skills
  зафиксированы в `6a77406`; после push `main` совпадал с `origin/main`.
