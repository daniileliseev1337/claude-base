# ui-ux-pro-max-skill (UI UX Pro Max / UUPM)

- **URL:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Stars:** 96 446 (API, 2026-06-26) — велоцитет звёзд очень высокий (репо создано 2025-11-30); проверять самому, но риск низкий (см. ниже)
- **Last commit:** 2026-06-25 (вчера — активный)
- **License:** MIT ✅
- **Lang:** Python 3.x (+ npm CLI `uipro-cli`)
- **Homepage:** https://uupm.cc
- **Описание:** AI-скилл «дизайн-интеллект»: по типу продукта генерирует целостную дизайн-систему (паттерн+стиль+палитра+шрифты+эффекты+анти-паттерны+чек-лист).

## Зачем смотрели
Цель владельца — сменить дизайн-подход klimat-pro: отойти от облачного Claude Design, звать его только для детальной работы. Нужен локальный слой «дизайн-направление».

## Что это технически
- **Локально и оффлайн.** Движок = Python-скрипт `search.py` (BM25-ранжирование) поверх CSV-баз. **API-ключа НЕТ, сети НЕТ, утечки данных НЕТ.**
- Контент: 67 UI-стилей, 161 палитра (1:1 с 161 категорией продукта), 57 пар шрифтов, 99 UX-гайдлайнов, 161 industry reasoning rule, 25 типов графиков, 17 стеков (вкл. React/Next/shadcn/Tailwind).
- **Не рисует и не генерит код сам** — выдаёт ДИЗАЙН-РЕШЕНИЯ + best-practices, код пишет Claude. Дополняет кодинг, не заменяет.
- Persist-паттерн: `design-system/MASTER.md` + `pages/*.md` overrides — консистентность между сессиями (ложится на наш FACTS.md / structured-artifacts).
- Активируется как skill автоматически на UI/UX-запросы; есть и слэш `/ui-ux-pro-max`.

## Установка (Claude Code)
- Marketplace: `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` → `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill`
- ИЛИ CLI: `npm i -g uipro-cli` → `uipro init --ai claude --global` (в `~/.claude/skills/`). Нужен Python 3.x (есть 3.12).

## Оценка
- **Подходит? ДА.** Это и есть «смена подхода»: локальный front-load дизайн-решений → меньше зависимости от Claude Design для направления.
- Сильное: MIT, оффлайн, 0 утечки, очень активный, прямо по нашей премиум-dark задаче (стили Liquid Glass / Dark OLED / Glassmorphism + золото-палитры).
- Слабое/риск: community (не Anthropic); 96k звёзд подозрительно быстрые → **перед global-install прочитать `scripts/search.py`** (supply-chain гигиена, хоть он и read-only по CSV). Выдаёт решения, не пиксели — качество зависит от реализации Claude.
- **Решение: брать (per-project тест → потом в базу как global-skill, лицензия MIT проходит).**
