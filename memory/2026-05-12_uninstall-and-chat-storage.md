# Кейс: где Claude Code хранит чаты, и почему «UI пустой» ≠ «чаты удалены»

**Дата:** 2026-05-12
**Контекст:** Тот же день что фиксы прокси-CONNECT и PS 5.1 `2>&1` (см.
`2026-05-09_hooks-debugging.md` ловушки 6 и 7). После выпуска
`Uninstall.ps1` пользователь запустил его на рабочем ПК для теста
переустановки, и испугался что Uninstall удалил всю историю чатов.

> Кейс полезен при работе с `~/.claude/` (бэкап, восстановление,
> uninstall, миграция между ПК) и при любых жалобах в духе «Claude
> Code забыл мои чаты».

## Главное в одном абзаце

**Чаты Claude Code хранятся в `~/.claude/projects/<encoded-cwd>/<uuid>.jsonl`**
— один `.jsonl` файл на каждую сессию, размером до десятка МБ, с
полным транскриптом. Они **scoped по cwd**: Claude Code UI и VS Code
extension показывают только те чаты, что относятся к **текущей**
открытой папке. То что в UI видно 2 сессии при том что на диске их 34
— это не потеря, это feature: остальные 32 живут в других encoded-cwd
папках и появятся, если открыть VS Code в соответствующей папке.

## Структура хранения

```
~/.claude/
└── projects/
    ├── C--Users-Deliseev/                                ← cwd = C:\Users\Deliseev\
    │   ├── bb179323-59a8-...jsonl                        ← одна сессия = один файл
    │   └── f8cc9bf1-37e5-...jsonl
    ├── C--Users-Deliseev-projects/                       ← cwd = C:\Users\Deliseev\projects\
    │   ├── 529a2d29-fce8-...jsonl
    │   └── ...
    └── C--Users-Deliseev-repos-claude-stroy-base/        ← cwd = C:\Users\Deliseev\repos\claude-stroy-base\
        ├── 0e7da5...jsonl
        ├── 119329...jsonl
        └── ... (24+ файлов накопилось за месяцы работы)
```

Encoding: backslash и колон cwd-пути заменяются на `-` или `--`
(точная схема — реализация Claude Code, нам не критично).

Каждая директория `<encoded-cwd>/` может также содержать поддиректорию
`<uuid>/` со вспомогательными файлами (видимо, summary). Главный
транскрипт — это сам `<uuid>.jsonl` файл на верхнем уровне директории
cwd.

## Что вызвало панику

Сценарий, в котором пользователь оказался:

1. Запустил `Uninstall.ps1` → 26 managed-файлов удалено, `.git/` удалена.
2. Запустил `Install.ps1` → `Apply-ClaudeMd` CASE 4 migration → `~/.claude/`
   восстановлена.
3. Открыл Claude Code Extension в VS Code → в sidebar только 2 чата.
4. Решение пользователя: «Uninstall удалил все мои чаты!»

Что на самом деле произошло:

- `projects/` был в `$PreservedItems` Uninstall.ps1 → НЕ удалялся.
- В backup (`~/.claude.uninstall-backup-<ts>/`) — 34 `.jsonl` файла.
- В текущей `~/.claude/projects/` — те же 34 `.jsonl` файла. Diff = 0.
- VS Code был открыт в `C:\Users\Deliseev\` → Claude Extension показал
  только те 2 сессии что относились к этому cwd. Остальные 32 живые,
  но в других encoded-cwd-папках.

Проверочные команды:

```powershell
$cur = "$env:USERPROFILE\.claude\projects"
$bak = "$env:USERPROFILE\.claude.uninstall-backup-<ts>\projects"
$cc  = (Get-ChildItem $cur -Recurse -File -Force | Where-Object { $_.Extension -eq '.jsonl' }).Count
$bc  = (Get-ChildItem $bak -Recurse -File -Force | Where-Object { $_.Extension -eq '.jsonl' }).Count
"Current: $cc, Backup: $bc, Diff: $($bc - $cc)"
```

Если diff = 0 — ничего не удалено, проблема в видимости. Если diff > 0
— часть пропала, восстанавливаем точечно:

```powershell
Copy-Item -Path "$bak\*" -Destination $cur -Recurse -Force
```

(Безопасно даже при diff = 0: перезаписывает идентичные файлы.)

## Дополнительная находка: token expiration через миграцию

После `Apply-ClaudeMd` CASE 4 (migration с backup → preserve → clone →
restore) `.credentials.json` физически на месте, но **auth token
внутри может оказаться невалидным** — либо истёк за время отладки,
либо что-то с прокси/IP. Симптом: `API Error: 403 forbidden ·
Please run /login`. Лекарство:

```
claude /login        # в Claude Code, browser flow
```

`credentials.json` после этого обновится с новым токеном.

## Уроки

1. **UI invisibility ≠ deletion.** Прежде чем паниковать «всё пропало»
   — проверь файлы на диске (`Get-ChildItem`, `Measure-Object Count`).
   Claude Code очень аккуратно с persistent state — он редко удаляет
   что-то сам.

2. **Claude Code чаты scoped по cwd.** Это видно по структуре
   `projects/<encoded-cwd>/`. Если ожидаешь увидеть чат в UI — открой
   ту папку в VS Code, из которой он был. Универсального глобального
   списка «все чаты» в UI нет.

3. **Backup перед Uninstall — гарантия отката.** Текущий Uninstall.ps1
   делает full `Copy-Item -Recurse` всей `~/.claude/` в
   `~/.claude.uninstall-backup-<ts>/` ДО любого удаления. Сценарий
   восстановления:
   ```powershell
   Remove-Item $env:USERPROFILE\.claude -Recurse -Force
   Move-Item "$env:USERPROFILE\.claude.uninstall-backup-<ts>" "$env:USERPROFILE\.claude"
   ```

4. **После Apply-ClaudeMd CASE 4 migration — может потребоваться
   `claude /login`.** Это нормальное поведение, не баг migration.
   Запомнить чтобы не лезть искать причину 403 в migration-логике.

5. **UX скрипта важен для нервов пользователя.** Уже после инцидента
   `Uninstall.ps1` обновлён (коммит `7fdb12a` в claude-lite-instaler):
   в Plan output теперь явно пишется
   `projects -- contains N chat session(s), ~M MB -- NOT deleted`, и
   в Next steps добавлен блок Notes про cwd-scope и `/login`. Это не
   меняет логику preservation (она и так работала), но сильно
   уменьшает риск повторной паники.

## Метрика кейса

- **Чатов на ПК пользователя при инциденте:** 34 (за месяцы работы).
- **Удалено Uninstall'ом:** 0.
- **Время от «всё пропало» до подтверждения «всё на месте»:** ~5 минут
  диалога с двумя `Get-ChildItem | Measure-Object Count`.
- **Реальный фикс ситуации:** `claude /login` после `Install.ps1`.
- **Стрессовых седых волос:** немного. Но в следующий раз — меньше.
