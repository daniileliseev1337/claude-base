# Session report — harvest 9 CC-плагинов + внедрение (2026-06-01)

## Что делал
Анализ присланной пользователем подборки из 9 Claude Code плагинов через
harvest-workflow (фильтр: применимость к нашей базе, не «всё в карман»),
затем внедрение одобренного на developer-ПК.

## Результаты (детали — в [SUMMARY.md](SUMMARY.md))
- 🟢 Берём 7 + создаём 1 свой (`domain-grilling`) · ⚫ пропуск 3 · 🔴 Adobe MCP отключить
- Детальные заметки по каждому — `harvested/01..09-*.md`
- Чеклист установки — [INSTALL-CHECKLIST.md](INSTALL-CHECKLIST.md)
- Инструкция актуализации всех ПК — [ACTUALIZATION-GUIDE.md](ACTUALIZATION-GUIDE.md)

## Внедрено на developer-ПК
- `domain-grilling` skill (закрывает дыру: brainstorming не на стройке) — на тесте
- Exa MCP (✓ без ключа), Codex CLI (v0.135.0)
- Codeburn прогон: Health F, Adobe 0%, pdf-mcp retry 64% (зацепка для Word/PDF)
- Подтверждено: skill-creator/frontend-design/security-guidance уже auto-installed

## Где ошибался (и исправил)
- Дважды списал инструмент через «у нас уже есть» без верификации
  (WebFetch, Adobe Firefly). Пользователь поправил данными. Урок →
  `memory/feedback_webfetch_reality_check.md`.
- Излишний скепсис к метрикам Caveman — проверил, цифры реальны.

## Что нашёл ценного (не очевидно из подборки)
- `domain-grilling` — главная находка, закрывает реальную дыру в домене.
- Codeburn `optimize` — независимо подтвердил Adobe 0% и pdf-mcp retry.
- Exa+Firecrawl — под реальный WebFetch 80-90% fail.

## Отложено (отдельные сессии)
- 🔥 Word/PDF косяки + Higgsfield/ComfyUI (image/video) — вместе
- Firecrawl self-host (инфра), MCP cleanup, Codex consent-правило финал
- domain-grilling раскат после теста
- Анализ 4 законов Anthropic (Claude MD) — пользователь пришлёт

## Уроки в memory (claude-base)
- `feedback_webfetch_reality_check.md`, `feedback_cloud_tools_consent.md`,
  `reference_licenses_k7.md`
