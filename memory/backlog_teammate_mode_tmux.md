---
created: 2026-05-20
status: backlog
priority: low
trigger: «появилась реальная многоразделовая задача (designer ОВ+ВК+ЭО+СС параллельно), И установлен tmux (Git Bash + tmux ИЛИ WSL), И пользователь явно разрешил трогать env-переменные»
related:
  - [[karpathy-guidelines]]
  - [[chains-pattern]]
  - [[project_designer_decomposition]]
tags: [backlog, R&D, teammates, tmux, settings]
---

# Backlog: teammateMode tmux + CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS

## Контекст

Источник идеи — аудит чужой базы Claude Code «К-7 (агенты)» от 2026-05-20
(см. отчёт `~/Desktop/K-7_audit_report.docx`, раздел 4.7). У них в
settings.json:

```json
"env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" },
"teammateMode": "tmux"
```

Это даёт параллельный запуск нескольких subagent'ов через tmux-сессии.

## Почему отложено

1. **`tmux` отсутствует в нашем окружении** (DANIILPC, Windows + Git Bash).
   `which tmux` → not found на 2026-05-20. На Windows без WSL установка
   tmux нетривиальна.
2. **`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` — env-переменная.** Правка
   `env` в settings.json требует явного указания пользователя
   (стандартное ограничение Claude Code instructions). Сейчас явного
   согласия нет.
3. **Реальной задачи под параллелизм пока нет.** `designer` — монолит
   (см. [[project_designer_decomposition]]). Без декомпозиции
   параллельный запуск Stage 3 невозможен.

## Альтернатива — `teammateMode: "in-process"`

schema settings.json допускает три значения:

- `"auto"` — Claude Code сам выберет (tmux если есть, иначе in-process)
- `"tmux"` — требует tmux
- `"in-process"` — параллельные агенты в том же процессе, без tmux

`in-process` не требует tmux и работает на Windows. Если триггер
сработает раньше чем мы поставим tmux — переключиться на in-process
(или auto).

## Когда триггер сработает

Включаем `teammateMode` если выполнено **всё**:

1. Активирован `chain:project-doc-pack` (см. [[project_designer_decomposition]])
   — появилась реальная многоразделовая задача (например, ПЗ + спецификация
   параллельно для ОВ, ВК, ЭО, СС).
2. Пользователь явно разрешил трогать env-переменные.
3. Один из вариантов:
   - tmux установлен → `teammateMode: "tmux"`
   - tmux нет → `teammateMode: "in-process"` или `"auto"`.

## Что делать когда триггер сработает

1. **Если выбран tmux**, поставить:
   - Git Bash: `pacman -S tmux` (если есть pacman) или вручную из репо
   - WSL: `apt install tmux`
2. **Правка settings.json:**
   ```json
   "env": {
     "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
   },
   "teammateMode": "auto"
   ```
3. **Тест на реальной задаче:** parallel-расчёт двух разделов
   (например ОВ + ВК) через два Agent-вызова в одном сообщении.
   Проверить что они реально шли параллельно (по таймингу) а не
   последовательно.
4. **Verify:** в логе сессии видны два concurrent subagent.

## Анти-паттерны

- **Не включать AGENT_TEAMS без реальной задачи под параллелизм.**
  experimental режим — может ломать другие вещи; без пользы — лишний риск.
- **Не ставить tmux только ради эксперимента.** Установка на Windows
  затратна, без реальной нужды — Karpathy §2 нарушение.

## Связанные

- [[project_designer_decomposition]] — основной триггер (stage-decomposition)
- [[backlog_promptfoo_semantic_tests]] — параллельный backlog
- К-7 отчёт `~/Desktop/K-7_audit_report.docx`, раздел 4.7

## История

- 2026-05-20 — создан backlog. tmux отсутствует, env-правки запрещены
  правилами Claude Code, реальной задачи под параллелизм нет.
