# OpenAI codex-plugin-cc — openai/codex-plugin-cc

## Источник
- URL: https://github.com/openai/codex-plugin-cc
- Официальный OpenAI org
- Прислал пользователь как «6-я позиция» подборки 9

## Метаданные (GitHub API, 2026-06-01)
- ⭐ Stars: **20,047**
- 🍴 Forks: 1,214
- 📜 License: **Apache-2.0** ✅
- 📅 Created: 2026-03-30
- 📅 Last push: 2026-04-18 (~1.5 мес назад — менее активный, но не заброшен)
- 🐛 Open issues: 218
- Описание: «Use Codex from Claude Code to review code or delegate tasks.»

## Что делает
Использовать OpenAI Codex как альтернативную модель внутри Claude Code.

### Интерфейс
- Slash: `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`,
  `/codex:status`, `/codex:result`, `/codex:cancel`, `/codex:setup`
- Subagent: `codex:codex-rescue`

### Установка
```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```
Prerequisite: Codex CLI (`npm install -g @openai/codex`, плагин может
предложить авто-установку).

## ⚠ Constraint check: подписки не покупаются
**ПРОЙДЕН.** Цитата README: «ChatGPT subscription (incl. **Free**) or
OpenAI API key.» Free ChatGPT tier работает (с usage-лимитами:
«Usage will contribute to your Codex usage limits»).
→ Не нужно платить, free ChatGPT аккаунт достаточен.

## Применимость к нашей базе

### Главная ценность: cross-model review
Наш `auditor` + узкие ревьюеры (`word-checker`, `excel-validator`,
`pdf-reviewer`) = **Claude проверяет Claude** (один набор слепых зон).
Codex = **другая модель, другие слепые зоны**.
`/codex:adversarial-review` независимой моделью объективно сильнее
self-review. **Новый capability которого у нас нет.**

### Use-cases
1. `/codex:adversarial-review` скриптов/hooks перед раскатом на 9 ПК —
   independent проверка другой моделью.
2. `/codex:review` нашего claude-base кода (agents, skills, chains).
3. `/codex:rescue` — когда Claude застрял на задаче, делегировать Codex.

### Минусы / нюансы
1. **Free tier usage-лимиты** — для редкого review хватит, для интенсива нет.
2. **Privacy:** код уходит в OpenAI. Для приватных проектов со шифрами —
   только обезличенный код (claude-base и так обезличен; domain-документы
   с шифрами НЕ давать Codex).
3. Требует ChatGPT аккаунт (даже free — регистрация).
4. Менее активный репо (но Apache-2.0, официальный, не заброшен).

## Вердикт (updated — пользователь решил раскат на всех)
🟢 **Раскат на все 9 ПК.** Пользователь (2026-06-01): «этот инструмент
необходимо иметь всем, дополнительная проверка это очень good».
Принцип верный — independent cross-model review ценен для всех артефактов,
не только кода (арифметика, логика, структура).

### ⚠ Privacy: consent-prompt вместо жёсткого запрета (решение пользователя 2026-06-01)

Пользователь выбрал **гибкий consent-подход** вместо жёсткого правила
обезличивания: при активации Codex агент спрашивает разрешение на отправку.

**Фактические поправки, зафиксированные при обсуждении:**
1. Codex — **НЕ локальный** чат. Данные уходят на серверы OpenAI (cloud).
   На free ChatGPT tier **могут использоваться для обучения** (default-политика).
2. ФИО/реквизиты заказчиков — **ПДн третьих лиц** (152-ФЗ), не личные данные
   сотрудника. Отправка = вопрос compliance компании, не личный выбор.
   Пользователь принял этот риск осознанно (его прерогатива как руководителя).

**Одобренная формулировка consent-prompt (2026-06-01):**
> ⚠ Данные уйдут на серверы OpenAI (не локально). На free tier могут
> использоваться для обучения. Если в тексте есть ФИО/реквизиты заказчиков —
> это ПДн третьих лиц. Отправить в Codex? [Да / Нет / Обезличить сначала]

**Реализация:** предпочтительно **hook** на `/codex:*` команды (перехватывает
каждый вызов, человек не забудет) → показывает consent-prompt. Инструкция в
CLAUDE.md как минимальный fallback. Hook — на этапе внедрения после разбора 9.
Опция «Обезличить сначала» = быстрая замена шифр/ФИО → плейсхолдеры перед review.

### Инструкция для раската (добавить в Update-ClaudeBase / онбординг)
1. Установить Codex CLI: `npm install -g @openai/codex`.
2. Завести **бесплатный ChatGPT аккаунт**, выполнить `codex login`.
3. `/plugin marketplace add openai/codex-plugin-cc` →
   `/plugin install codex@openai-codex` → `/codex:setup`.
4. **Прочитать privacy-правило** (таблица выше) — что можно/нельзя давать Codex.

## Идея в копилку
- ✅ **Cross-model review в нашу архитектуру** — добавить опциональный
  `/codex:adversarial-review` шаг в pipeline перед раскатом критичного кода
  (hooks/scripts на 9 ПК). Дополняет, не заменяет наш `auditor`.

## Открытые вопросы
1. Есть ли у пользователя ChatGPT аккаунт (хотя бы free)? Если нет —
   завести free (бесплатно) для активации.
2. Подтвердить privacy-правило: Codex review только обезличенного кода,
   никаких domain-документов со шифрами.
3. Стоит ли формализовать cross-model adversarial-review как обязательный
   шаг для кода идущего в раскат? (отдельная задача)
