# Session report — harvest 9 плагинов + внедрение + инфра-улучшения (2026-06-01)

Сессия на developer-ПК (Даниил, MAX x5, личный ноут + VPN, БЕЗ корп-прокси).
Очень длинная, многофазная. Всё запушено в claude-base (origin синхронизирован).

## Что сделано (полный список)

### Harvest 9 CC-плагинов (анализ — SUMMARY.md + harvested/01..09)
- 1 Caveman — ⚫ пропуск (домен/русский)
- 2 Exa — 🟢 **установлен (user scope), работает, протестирован на ГОСТ 21.602**
- 2 Firecrawl — отложен до конкретного кейса (Exa web_fetch пока закрывает)
- 3 Compound Engineering — 🟡 developer-ПК (юзеру: `/plugin install compound-engineering`)
- 4 Higgsfield — отложен в сессию Word/PDF (free tier 10 cr/мес, + ComfyUI fallback)
- 5 Anthropic пачка — skill-creator/frontend-design/security-guidance УЖЕ auto-installed
- 6 Codex — ⚫ **ОТПАЛ: ChatGPT auth недоступен в РФ** (не костылить VPN)
- 7 Matt Pocock — вместо handoff/grill создан свой domain-grilling
- 8 Morph — ⚫ пропуск (код-only, не Word/PDF; free tier 200 req/мес)
- 9 Codeburn — 🟢 метрики (Health F, Adobe 0%, pdf-mcp retry 64%)

### Создано / внедрено
- **`domain-grilling`** skill — авто-grilling на строй-задачах (brainstorming не срабатывал). На тесте.
- **`skill-development`** skill + 4 правила Anthropic в CLAUDE.md USER EXTENSIONS.
- **`/sync-base`** команда — самоактуализация ПК с GitHub (safe, push не делает сам).
- **`handoff-to-new-chat`** → subscription-aware: FULL (MAX) / LITE (PRO <1500 ток).
- **`norm-lookup`** агент → Exa-first вместо WebFetch (чинит нормоконтроль).
- **`harvest`** → skills.sh равноправный с GitHub, Anthropic→pre-check, +3 урока (verify/constraint/не-списывать).
- **verify-claude-base.ps1** → consumer пропускает pytest (не ложный FAIL).
- Exa MCP user scope (доступен агентам везде).

### Уроки в memory (claude-base)
- feedback_webfetch_reality_check (WebFetch 80-90% fail, Adobe Firefly не работает)
- feedback_cloud_tools_consent (consent-prompt для cloud, не запрет)
- feedback_tool_sandbox_isolation (npm/pip через tool → sandbox, не реальный ПК)
- backlog_tools_layer_migration, backlog_cross_model_review_rf (Qwen findings), reference_licenses_k7

## Состояние
- Всё запушено. Последний коммит: `56cdda7`. origin/main синхронизирован (ahead 0).
- 12 задач TaskList — все completed.

## Что осталось ПОЛЬЗОВАТЕЛЮ руками (не горит)
1. **Restart Claude Code** на ПК с нормоконтролем — чтобы `norm-lookup` подхватил Exa
   (агенты не hot-reload). ГЛАВНОЕ для починки нормоконтроля.
2. Adobe MCP отключить (claude.ai → Settings → Connectors → Adobe → Disconnect).
3. Compound Engineering: `/plugin install compound-engineering` в десктоп/CLI Claude Code
   (в API-режиме `/plugin` недоступен). Только developer-ПК.
4. Протестировать `domain-grilling` в реальной спецификации/расчёте.

## Отложено в ОТДЕЛЬНЫЕ сессии
- 🔥 **Word/PDF косяки** (главная боль) + **Higgsfield/ComfyUI** (image/video) — вместе.
  В этой сессии искать pdf/docx/xlsx skills на skills.sh + ComfyUI кластер (runcomfy,
  173K installs — проверить local vs cloud).
- **Firecrawl** self-host — до конкретного кейса (тяжёлый JS/антиботы/краулинг).
- **Qwen** cross-model review — где запускать (сервер <организация> с GPU? см. backlog).
- **tools/ миграция** skills (инкрементально), **MCP cleanup** (adeu 0%, мусорные connectors).

## Открытые вопросы
- Сервер <организация> — есть ли GPU? (решает Qwen локальный + Firecrawl self-host).
- domain-grilling — пороги/триггеры после теста (Skill Creator Eval).

## Ключевые факты для нового чата
- developer-ПК: личный, VPN, БЕЗ корп-прокси (Set-Proxy НЕ нужен тут).
- Per-machine установки (npm/pip) через мои tool-команды идут в SANDBOX, не на реальный ПК
  — давать юзеру команды для ручного запуска (см. feedback_tool_sandbox_isolation).
- GitHub push: `git -c http.proxy="" -c https.proxy="" push` (bypass).
