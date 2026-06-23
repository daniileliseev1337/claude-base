# Phase 2-follow-up — Remote feedback setup (2026-05-21)

## Что сделано в коде

- `scripts/feedback-collector.ps1` расширен:
  - GitHub API integration (Invoke-RestMethod + PAT auth)
  - Автоматическое создание branch `feedback/<hostname>-<userprefix>` если ещё нет
  - Push через `PUT /repos/.../contents/feedback/<filename>` API
  - После успешного push — перемещение файла в `feedback-staging/pushed/`
  - Idempotent — если файл уже в репо с тем же SHA, GitHub откажет, файл остаётся в staging

- `scripts/pull-feedback.ps1` для Daniil'а:
  - Clone/fetch claude-base-feedback репо в `~/.claude/feedback-inbox/.repo/`
  - Список всех `feedback/*` веток
  - Checkout каждой ветки → copy `feedback/*.md` в `~/.claude/feedback-inbox/all/<branch>/`
  - Mark NEW vs already-seen файлы

## Что нужно сделать в GitHub UI (действия Daniil'а)

### 1. Создать private repo `claude-base-feedback`

https://github.com/new

- Name: `claude-base-feedback`
- Visibility: **Private** ⚠ важно — feedback может содержать чувствительные подробности
- Initialize: ✅ Add README

### 2. Создать main branch с пустой структурой

После создания репо — в Web UI:

```
.
├── README.md           (по умолчанию от GitHub init)
└── feedback/
    └── .gitkeep        (создать через Add file → Create new file
                         с именем `feedback/.gitkeep` и пустым content)
```

Это нужно чтобы feedback/ path существовал — иначе PUT API не сможет создавать файлы.

### 3. Add collaborators с write

Settings → Manage access → Add people:

- `apolyakov6500-boop` — Write
- `<логин>` — Write
- `netesov002-stack` — Write (когда примет invitation в основной репо)

### 4. Создать Fine-grained PAT для каждого сотрудника

Это **per-PC** token. Можно сделать **общий** для всей команды если они доверяют друг другу.

https://github.com/settings/tokens?type=beta → **Generate new token**:

- Token name: `claude-base-feedback-write` (или per-сотрудник если разные)
- Expiration: 1 year (или дольше)
- Repository access: Only select repositories → `claude-base-feedback`
- Repository permissions:
  - **Contents**: Read and write ⚠ нужно для PUT API
  - **Metadata**: Read (auto)
- Account permissions: ничего

После Generate — **скопировать** token (показывается **один раз**!).

### 5. Распределить token сотрудникам через secure channel

**НЕ через GitHub issues или public chat**. Варианты:
- Личное сообщение в Telegram/Signal/WhatsApp
- USB flash + удалить после копирования
- Очный передачей если возможно

### 6. На каждом consumer ПК создать `.feedback-config.json`

```powershell
# На DELISEEV-PC / R-090226727A / 100226745A
notepad $HOME\.claude\.feedback-config.json
```

Содержимое:

```json
{
  "github_repo": "daniileliseev1337/claude-base-feedback",
  "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Сохранить. Этот файл **gitignored** автоматически (через `.developer-marker`-pattern в .gitignore catch-all).

### 7. Убрать collaborators из main `claude-base`

Settings → Manage access → Remove:

- `apolyakov6500-boop` (read останется потому что repo public)
- `<логин>` (тоже)

`netesov002-stack` (pending) — можно cancel invitation чтобы не запутаться.

## Как проверить что работает

### На consumer ПК

1. Закрыть текущий Claude Code чат → SessionEnd hook запустит auto-push.ps1
2. auto-push видит что **нет** `.developer-marker` → запускает feedback-collector.ps1
3. feedback-collector видит файлы в `feedback-pending/` (если Claude писал) → перемещает в staging
4. feedback-collector видит `.feedback-config.json` → push через API в `claude-base-feedback`
5. Проверить: `Get-Content ~/.claude/auto-sync.log -Tail 5` — должно быть `feedback-collector: pushed: ...` и `remote push complete: N/N files`

### На GitHub UI

После пары сессий на consumer ПК — в `claude-base-feedback` появятся branches:
- `feedback/DELISEEV-PC-Deliseev`
- `feedback/R-090226727A-...`
- `feedback/100226745A-...`

В каждой branch — папка `feedback/` с файлами.

### На DANIILPC

```powershell
powershell -File ~/.claude/scripts/pull-feedback.ps1
```

Должно показать список новых feedback файлов сгруппированных по веткам.

## Анти-паттерны

- **НЕ коммитить** `.feedback-config.json` (содержит PAT — это **секрет**).
  Файл автоматически gitignored через whitelist catch-all.
- **НЕ давать PAT** с правами больше чем нужно (только `claude-base-feedback`,
  только Contents:write).
- **НЕ использовать** общий PAT для всей команды если у тебя нет
  доверия к каждому. Лучше per-сотрудник.
- **НЕ публиковать** PAT в Telegram-чате с историей — лучше Signal с
  disappearing messages или USB.

## Что НЕ автоматизировано (намеренно)

- Создание GitHub репо — это **разовое** действие, не нужен скрипт.
- Выдача PAT — должна оставаться **под контролем человека** (security).
- Internal review of feedback — Daniil решает что внедрять, не автомат.
- Удаление feedback файлов после внедрения — Daniil руками решает что
  оставить как историю vs удалить.

## Status

- ✅ Код в `feedback-collector.ps1` и `pull-feedback.ps1` готов
- ⏳ Действия на GitHub UI — за Daniil'ом
- ⏳ Тест end-to-end после setup'а — после действий выше
