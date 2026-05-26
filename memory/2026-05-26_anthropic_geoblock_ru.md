# 2026-05-26 — Anthropic геоблок на RU IP блокирует Claude Desktop UI

## TL;DR

**Anthropic геоблокирует RU IP на уровне application backend API.** Это
не корп-прокси, не TLS MITM, не NO_PROXY. На запросах от Claude Desktop
к `api.anthropic.com/bootstrap`, GrowthBook, updater — Anthropic
**видит RU IP** и возвращает HTML страницу
`https://www.anthropic.com/app-unavailable-in-region` вместо JSON.

Claude Desktop **defensive-блокирует** этот редирект → bootstrap не
проходит → `accountId=null` → **белый экран без ошибки**.

**Единственный путь** для коллег: VPN (не-RU IP) или зарубежный
VPS-прокси.

---

## Хронология открытия (что я делал неправильно)

### Шаг 1 — Первая гипотеза (verdict: верно)

Когда увидел `Could not attach to MCP server` + scuf-meta.ru:10894
прокси — выдвинул гипотезу «Anthropic геоблокирует RU IP».

### Шаг 2 — Зря отозвал (ошибка)

Когда installer прошёл через прокси и скачал MSIX — **отозвал**
гипотезу. Логика была: «если прокси пропускает Anthropic для installer,
значит и для Claude Desktop тоже». **Это ошибка**: разные endpoints
имеют разную geo-политику:
- `downloads.claude.ai` — CDN статика, **без geo-фильтра**.
- `api.anthropic.com/bootstrap` — application API, **с geo-фильтром**.

### Шаг 3 — Логи дали финальное доказательство

После tail 300 main.log на DELISEEV-PC увидел:
```
[warn] Blocked redirect to disallowed URL
{ href: 'https://www.anthropic.com/app-unavailable-in-region' }
```

Это **прямое** доказательство geo-фильтра Anthropic.

---

## Цитаты из лога DELISEEV-PC (2026-05-26 15:23:20)

```
[warn] Blocked redirect to disallowed URL
{ href: 'https://www.anthropic.com/app-unavailable-in-region' }

[error] [growthbook] failed to parse response body:
  SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON

[error] [updater] Auto-update error:
  System.Net.WebException: 403 Forbidden (api.anthropic.com)

[warn] [account] Bootstrap API fetch failed {
  error: SyntaxError: Unexpected token '<', "<!DOCTYPE "...
}
[warn] [LocalSessionManager] Cannot initialize sessions:
  accountId=null, orgId=null
```

GrowthBook (A/B config) **получает HTML** вместо JSON → значит
`api.anthropic.com` отдал HTML page вместо JSON ответа. Это та же
`app-unavailable-in-region` страница.

---

## Что НЕ работает как индикатор геоблока

❌ **Open `https://claude.com` в браузере** — открывается нормально
   (CDN-уровень, geo-фильтр не применяется).

❌ **`curl https://claude.com` через прокси** — получает полный HTML
   (та же причина).

❌ **`Claude Setup.exe` (installer)** — качает MSIX с
   `downloads.claude.ai`, проходит **без геоблока**.

❌ **MCP servers коннектятся** — некоторые могут работать (если они
   обращаются к anthropic API напрямую через тот же SDK).

✅ **Запуск самого Claude Desktop** → log shows
   `app-unavailable-in-region` blocked redirect — **это** реальный
   индикатор геоблока.

---

## Реальные решения для коллег

### Вариант A — VPN на каждом ПК (как у DANIILPC)

- Поставить VPN-клиент.
- Постоянно держать активным во время работы с Claude Desktop.
- Минусы: трафик через VPN, нагрузка на сеть, требует админ-прав на
  установку клиента.

### Вариант B — Зарубежный VPS-прокси для фирмы

- Арендовать VPS в EU/US (~$5/мес).
- Поднять squid / 3proxy.
- Раздать коллегам через `~/.claude-proxy.json` указать **зарубежный**
  прокси (вместо `scuf-meta.ru:10894`).
- Минусы: расход на VPS + настройка.

### Вариант C — VS Code Extension (требует проверки)

**Гипотеза:** VS Code Extension использует Anthropic API напрямую
после auth login, не делает bootstrap UI flow. Возможно работает
через корп-прокси без VPN если:
- Auth token уже получен (один раз через VPN).
- Дальнейшие API запросы идут с уже валидным token.

**Проверять** на DELISEEV-PC отдельно.

### Вариант D — API ключ напрямую (без UI)

- Anthropic Console → создать API key.
- Использовать через скрипты, не через Claude Desktop.
- Минусы: нет Claude Code Desktop UI, только программный доступ.

---

## Что отозвать из нашей раскатки

1. **`Install-ClaudeDesktop.ps1`** (commit fd1dcba в claude-lite-instaler)
   — **обязательно** добавить warning в начало:
   ```
   WARNING: Claude Code Desktop требует VPN/non-RU IP для работы UI.
   Без VPN — белый экран (геоблок Anthropic).
   Если на ПК нет VPN — пропустить Stage 9 и использовать VS Code
   Extension.
   ```

2. **Start-Claude.ps1 Mode 3 (Desktop)** (commit 08c0977 в
   claude-lite-instaler) — добавить аналогичный warning перед запуском
   Desktop.

3. **CLAUDE.md / installer README** — упомянуть требование VPN для
   Desktop UI.

---

## Уроки на будущее (Karpathy §1, §5)

1. **§1 — не отзывать гипотезу преждевременно.** Я отозвал geo-блок
   гипотезу когда installer прошёл, не подождав финальной диагностики.
   Правильно было: «installer работает но Claude Desktop падает → надо
   проверить разные endpoints».

2. **§1 — assumption testing.** «Если прокси пропускает X, значит
   и Y тоже» — **неверная** предпосылка. Разные endpoints могут иметь
   разную политику.

3. **§5 — не подхалимствовать собственным гипотезам.** Я **дважды**
   менял свою позицию по геоблоку — сначала был прав, потом отозвал,
   потом снова прав. Каждый раз — на основе **частичных** данных.
   Правильно: сразу запросить **полную** диагностику (включая main.log
   tail 300), потом делать выводы.

4. **Урок раскатки:** ВСЕГДА проверять **полный E2E flow** (запуск +
   авторизация + UI render) на **рабочем ПК коллеги**, не только на
   developer ПК. У developer-а часто VPN — он не видит геоблок.

---

## Связанные документы

- `~/.claude/CLAUDE.md` секция «Прокси (если за корп-прокси)» — на
  добавление warning про VPN/non-RU для Claude Desktop.
- `~/Desktop/claude-lite-instaler/Install-ClaudeDesktop.ps1` — добавить
  warning в начало.
- `~/Desktop/claude-lite-instaler/Start-Claude.ps1` Mode 3 — добавить
  warning перед запуском Desktop.

## Источник

Сессия 2026-05-26 «Team rollout + рефакторинг базы». DELISEEV-PC лог:
`%APPDATA%\Claude\logs\main.log` (2026-05-26 15:23:20).
