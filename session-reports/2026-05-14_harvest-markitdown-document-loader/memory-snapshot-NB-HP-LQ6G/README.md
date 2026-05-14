# Memory snapshot — NB-HP-LQ6G, 2026-05-14

## Что это

**Разовое исключение** из правила «auto-memory — per-machine, не переносится между ПК» (CLAUDE.md → секция «Auto-memory»). Скопировано в session-report по явному запросу пользователя, представившегося Даниилом, для анализа на главном ПК.

## Источник

`~/.claude/projects/C--Users-ifesenko/memory/` на машине `NB-HP-LQ6G` (Windows 11, login `ifesenko`).

Это **локальная** auto-memory Claude Code этой сессии. Сами оригинальные файлы в `projects/.../memory/` **остаются на месте** — никуда не переносились, инвариант «memory per-machine» не нарушен. Это только копия для удалённого анализа.

## Содержимое (4 файла)

| Файл | Тип | Назначение |
|---|---|---|
| `MEMORY.md` | индекс | 3 записи, ссылки на остальные файлы |
| `nb-hp-lq6g-proxy-not-needed.md` | project | Прокси `scuf-meta.ru:10894` не нужен для git; env-vars мешают |
| `fessenkoim-arch-github.md` | project | GitHub-аккаунт `fessenkoim-arch` push'ит в claude-base, collaborator с 2026-05-14 |
| `git-push-diagnostic-order.md` | feedback | Урок: auth-слой проверять раньше сетевого слоя |

## Проверка на секреты

В файлах **нет**:
- Паролей (пароль прокси, переданный в чате, был сразу заменён плейсхолдером `[СЕКРЕТ — не записан]`)
- GitHub PAT (никогда не записывались)
- ПДн, банковских данных

В файлах **есть** (разрешено для private claude-base по правилам):
- Имена хостов: `NB-HP-LQ6G`, `scuf-meta.ru:10894`
- Имена аккаунтов: `ifesenko`, `fessenkoim-arch`, `daniileliseev1337`
- Имена репо и пути

## Полезно для Даниила (что хорошо бы решить на уровне `claude-base`)

1. **Обновить `auto-push.ps1`**: очищать `Env:HTTP_PROXY/HTTPS_PROXY` перед `git push`. На этой машине proxy-env установлен системно, но git его не должен использовать.
2. **Обновить `auto-push.ps1`**: писать failure-строку в `auto-sync.log` при ненулевом exit code. Сейчас лог обрывается на `pushing to origin/main...` без result-строки.
3. **Доработать `claude-lite-instaler`**: на этой машине нет `Set-Proxy.ps1`, `Start-Claude.bat`, `Start-Claude.ahk` (упомянуты в CLAUDE.md `Прокси`-секции). Либо инсталлятор их не положил, либо они должны быть optional.
4. **Решить policy по аккаунтам**: пушим в `claude-base` от **личных** аккаунтов сотрудников (`fessenkoim-arch`) или с одного **сервисного**? Текущий выбор — личный аккаунт через collaborator-приглашение (по факту работает). Альтернатива — single service account + raspread token через safe channel.
