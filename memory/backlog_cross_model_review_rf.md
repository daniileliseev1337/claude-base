---
name: backlog-cross-model-review-rf
description: Найти cross-model reviewer на РФ-доступной модели (Codex/ChatGPT не работает — геоблок РФ). Идея из harvest #6.
metadata:
  type: project
---

# Backlog: cross-model review на РФ-доступной модели

**Контекст:** harvest 2026-06-01, #6 OpenAI codex-plugin-cc. Идея —
**cross-model review**: проверять наш код/артефакты ДРУГОЙ моделью, не
Claude-проверяет-Claude (разные слепые зоны). Codex отпал — ChatGPT
авторизация недоступна в РФ (см. ниже).

## Почему Codex не подошёл
- Codex free tier требует **ChatGPT аккаунт**.
- OpenAI блокирует регистрацию/вход из РФ (телефон-верификация РФ-номеров
  reject, геоблок). Даже с VPN — нестабильно.
- **НЕ костылить** VPN-обходами (анти-паттерн CLAUDE.md «не обходить блоки»).
- Связано: `2026-05-26_anthropic_geoblock_ru.md` (аналогичный геоблок-кейс).

## Зачем всё равно нужно
Наш `auditor` + ревьюеры = Claude проверяет Claude (один набор слепых зон).
Вторая модель ловит то, что Claude систематически не видит. Особенно для
скриптов/hooks перед раскатом на 9 ПК.

## Кандидаты (РФ-доступные модели)
| Модель | Доступ | Интеграция в Claude Code |
|---|---|---|
| DeepSeek | API доступен в РФ, дёшево/free tier | через MCP / CLI-обёртку |
| Qwen (Alibaba) | API доступен | MCP / CLI |
| GigaChat (Сбер) | РФ, API | свой MCP-сервер |
| YandexGPT | РФ, API | свой MCP-сервер |

## Qwen — research 2026-06-01 (через Exa)
**`qwen-code`** (QwenLM/qwen-code) — open-source CLI, форк Gemini CLI,
model-agnostic (любой OpenAI-compatible endpoint, включая Ollama).
Qwen3-Coder: 69.6% SWE-bench (выше Gemini 2.5 Pro, ~Sonnet).

⚠ **Qwen OAuth free tier ЗАКРЫТ 15.04.2026** (как Codex по сути). Остались:
| Путь | Free | РФ | Приватность |
|---|---|---|---|
| Локальный Ollama + Qwen | ✅ навсегда | ✅ | ✅ полная |
| OpenRouter Qwen3-Coder-480B (free) | ✅ 50/день | ⚠ регистрация/карта? | ❌ провайдер |
| DashScope Singapore | ⚠ 70M токенов/90 дней | ✅ intl | ❌ Singapore |

**Железо developer-ПК (i5-13420H, 16GB, нет дискретной GPU):** локальный
Qwen только 7B на CPU — медленно/слабее. Мощную 480B локально не потянуть
(нужен сервер с GPU).

**Открытый вопрос (отложен пользователем 2026-06-01):** где запускать —
сервер <организация> (если GPU) / этот ПК (7B медленно) / OpenRouter (проверить РФ).
Рекомендация: при возврате — если у сервера <организация> есть GPU, локальный Qwen
там идеален (приватно+мощно+бесплатно).

Источники: github.com/QwenLM/qwen-code, openrouter.ai/qwen,
alibabacloud.com/help/en/model-studio.

## Что проверить при реализации
1. Free tier / стоимость (constraint: подписки не покупаются).
2. Privacy: данные уходят на сервер модели → consent-подход
   (см. `feedback_cloud_tools_consent.md`). Для GigaChat/YandexGPT —
   данные в РФ-облаке (лучше для ПДн заказчиков, чем OpenAI/китайские).
3. Качество review кода (не все модели сильны в коде как Codex/Claude).
4. Интеграция: готовый плагин/MCP или писать обёртку.

## Приоритет
Не срочно. Триггер — когда понадобится independent review критичного кода
перед раскатом, ИЛИ найдётся готовый плагин под РФ-модель в harvest.
**GigaChat/YandexGPT предпочтительнее для приватных данных** (РФ-облако,
152-ФЗ проще).
