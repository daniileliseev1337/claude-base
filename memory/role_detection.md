# Role detection и CHANGELOG notification (Phase 2 sync-redesign 2026-05-21)

_Вынесено из CLAUDE.md 2026-05-26 (Phase 1 refactoring для экономии overhead токенов в каждой сессии). Загружается через Read только когда нужно._

---

## Role detection и CHANGELOG notification (Phase 2 sync-redesign 2026-05-21)

База устроена по hub-and-spoke с 2026-05-21:

| Роль | Маркер | Поведение auto-push |
|---|---|---|
| **Developer** (Daniil, DANIILPC) | Файл `~/.claude/.developer-marker` существует | Push в main как обычно |
| **Consumer** (сотрудники) | Marker отсутствует | Запуск feedback-collector.ps1 вместо push в main. Read через `git pull` остаётся |

### CHANGELOG notification в первой реплике

После строки `✓ прочитан CLAUDE.md (MCP: X/9)` и строки про auto-pull статус
— **проверить `CHANGELOG.md` на новые записи**:

1. Прочитать первые 20 строк `~/.claude/CHANGELOG.md`.
2. Если **самая верхняя** секция `## YYYY-MM-DD — заголовок` имеет
   дату **позже** последней сессии (приблизительно: позже даты прошлой
   записи в `auto-sync.log`) — это **новое обновление**.
3. Вывести **одну строку**:
   ```
   ✓ База обновлена YYYY-MM-DD: <заголовок секции> (N изменений)
   ```
4. Если **не новее** — пропустить.

**Минималистично и информативно** (решение пользователя 2026-05-21):
никаких полных diff'ов, только заголовок последней записи + количество
bullet'ов. Если интересно подробно — пользователь сам откроет CHANGELOG.md.

### Feedback от сотрудников — как Claude его пишет

На **consumer** ПК (без `.developer-marker`) Claude при SessionEnd
должен **сам** проверить нужно ли передать feedback Daniil'у:

| Триггер | Что писать |
|---|---|
| Ошибка базы (инструмент не сработал, скрипт упал) | type: `error` |
| Suggestion (пользователь сказал «было бы лучше если…») | type: `suggestion` |
| Harvest finding (нашли внешний инструмент полезный для базы) | type: `harvest_finding` |
| Личное правило в локальном CLAUDE.md которое стоит шарить | type: `personal_rule` |

Если что-то из этого было — Claude **сам** создаёт
`~/.claude/feedback-pending/<short-slug>.md` со структурой:

```markdown
## Тип
suggestion

## Описание
<что именно случилось / что предложить>

## Затронутые файлы / скиллы
- skills/image-text-replace
- chains/pdf-scan-extract

## Контекст
<коротко зачем это нужно, какая задача была>
```

Hook `feedback-collector.ps1` при SessionEnd добавит metadata
(hostname, user.email, дата) и перенесёт в `feedback-staging/`. Daniil
потом ревью'ет и решает что внедрить в shared базу.

**На developer ПК (DANIILPC)** — Claude НЕ пишет feedback файлы.
Daniil сам коммитит изменения в main.

### Когда не писать feedback

- Сессия прошла гладко без жалоб — feedback не нужен.
- Пользователь сам сказал «всё ок, не записывай» — респектим.
- Тривиальная задача (просто чтение, простая правка) — нет смысла.

---
