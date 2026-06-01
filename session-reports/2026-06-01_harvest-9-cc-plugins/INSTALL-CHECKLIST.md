# Чеклист внедрения — 2026-06-01

## ✅ Уже сделано автоматически (Claude, на developer-ПК)
- [x] **Codeburn** прогон — метрики собраны (Health F, Adobe 0%, pdf-mcp retry)
- [x] **domain-grilling** skill создан → `~/.claude/skills/domain-grilling/` (на тесте)
- [x] **Exa MCP** добавлен (local scope, ✓ Connected без ключа)
- [x] **Codex CLI** установлен глобально (codex-cli 0.135.0)

## ✅ Уже было (auto-installed через claude-plugins-official)
- [x] **skill-creator** (#5.1) — есть, начать использовать Eval/Benchmark
- [x] **frontend-design** (#5.3) — есть, lazy, на всех ПК с official marketplace
- [x] **security-guidance** (#5.4) — есть (думали ставить — уже стоит)
- [x] Бонус: code-review, hookify, pr-review-toolkit, plugin-dev, agent-sdk-dev,
      mcp-server-dev — для developer-режима

## 🔲 Действия пользователя (интерактив — Claude не может)

### 1. Отключить Adobe MCP (0% использования, подтверждено Codeburn)
- claude.ai → Settings → Connectors → **Adobe** → Disconnect
- Бонус: разгрузит context (57 неиспользуемых tools)

### 2. Активировать Codex (#6) — CLI уже установлен
```
codex login            # выбрать ChatGPT, бесплатный аккаунт
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/codex:setup
```
- Consent-prompt (privacy) — реализуем hook'ом отдельно (на след. этапе)

### 3. Compound Engineering (#3) — только developer-ПК
```
/plugin install compound-engineering
```
- Для meta-dev (разработка claude-base), НЕ раскат на 8 ПК

## 🔲 Осталось у Claude (следующие шаги)
- [ ] Codex consent-hook (privacy-prompt при `/codex:`)
- [ ] domain-grilling тест через Skill Creator Eval → раскат на 9
- [ ] Exa: решить user scope / раскат на команду (сейчас local)
- [ ] Firecrawl self-host (Фаза 1)

## 🔲 Отложено на отдельную сессию
- 🔥 Word/PDF косяки (диагностика) + Higgsfield/ComfyUI (image/video)
- MCP cleanup (adeu 0%, connectors Vercel/Gmail/Preview/PDF_Tools)
