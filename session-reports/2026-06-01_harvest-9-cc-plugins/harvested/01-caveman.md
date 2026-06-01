# Caveman — JuliusBrussee/caveman

## Источник
- URL: https://github.com/JuliusBrussee/caveman
- Прислал пользователь в подборке 9 плагинов (1-я позиция)

## Метаданные (GitHub API, на 2026-06-01)
- ⭐ Stars: **67,051**
- 🍴 Forks: 3,782
- 📜 License: **MIT** ✅
- 📅 Created: 2026-04-04 (~2 мес назад)
- 📅 Last push: 2026-05-20 (12 дней назад — активный)
- 🐛 Open issues: 259
- ❌ Archived: no
- Описание: «Claude Code skill that cuts 65% of tokens by talking like caveman»

## Что делает (механизм)
- **Claude Code skill** (не plugin в строгом смысле, не обвязка из `.claude-plugin/plugin.json`).
- Ставит системный промпт «drop filler, keep substance, use fragments».
- 4 режима через slash-команды:
  - `/caveman lite` — drop filler only
  - `/caveman full` — default caveman
  - `/caveman ultra` — telegraphic
  - `/caveman wenyan` — classical Chinese (ещё короче)
- Slash extras: `/caveman-commit`, `/caveman-review`, `/caveman-stats`, `/caveman-compress <file>`
- Поддерживает 30+ агентов (CC, Codex, Gemini, Cursor, Windsurf и т.д.)

## Установка
```bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```
Node ≥18. Безопасно re-run.

## Анализ применимости к нашей базе

### Плюсы
- 65% token reduction на benchmark (range 22-87%) — экономия реальная.
- MIT — лицензионно чисто, можем брать.
- Виральный, активный, не загнётся завтра.
- Идея slash-команд для compression вписывается в slash-архитектуру Claude Code.

### Минусы / конфликты с нашим стеком
1. **Стиль наших задач плохо подходит под caveman.**
   Мы работаем с нормоконтролем, разделами РД/ПД, ответами на экспертизу,
   деловой перепиской, спецификациями. Здесь **детализация критична**.
   Сжатый ответ «Бага в АОСР раздел ОВ» — нерабочий для сдачи документации.

2. **Конфликт с дисциплиной русского языка.**
   CLAUDE.md: общение на русском, код на латинице. Caveman заточен под
   английский (есть wenyan — китайский, но не русский).

3. **Уже есть наш аналог: дисциплина Karpathy #2 «простота прежде всего» +
   skill `structured-artifacts` (вынос контекста на диск) +
   skill `handoff-to-new-chat` (compression при перегрузе) +
   built-in `/compact`.**
   Это решает ту же задачу (экономия токенов) **без потери детализации**.

4. **Раскат на 8 ПК команды нерационален.**
   Сотрудники получат сжатые ответы по умолчанию → разрушит UX
   для домена («дай полный пункт ГОСТ» → «ГОСТ 21.602 п 4.2»).

### Где мог бы пригодиться
- Лично у меня на developer-режиме на rutine задачах (статусы, диагностика,
  commit messages). Но это micro-управление, ROI низкий.
- Идея `/caveman-stats` (отчёт по экономии токенов) — интересна. У нас есть
  `~/.claude/memory/token_economy.md` но без метрик. Можно подсмотреть.

## Решение
🟡 **Адаптировать идею, не ставить плагин.**

### Что **не делаем**
- ❌ Не устанавливаем `curl | bash` ни локально, ни в раскат на команду.
- ❌ Не клонируем код (плюс не нужно по harvest-workflow — MIT + чужой стиль).

### Что **берём как идею**
- ✅ Slash-команда для compression — уже есть `/compact` built-in.
- ✅ Принцип «компрессия по запросу, не по умолчанию» — добавить как одну
  строку в CLAUDE.md? Скорее нет, это уже в Karpathy #2 + handoff skill.
- ✅ `/caveman-stats` — идея метрик token economy. **Потенциальный TODO:**
  написать наш `/token-stats` который пересчитывает session-report'ы и
  показывает где утечки. Но это отдельная задача, не из этой harvest-волны.

## Критерий success
Если через 2 недели обнаружим что пользователь явно просит «короче» 3+ раза
в одной сессии — пересмотреть и поставить локально (НЕ в раскат).

## Рекомендация пользователю
Пропускаем как плагин. Идея compression-режима у нас уже реализована
дисциплиной Karpathy + handoff-to-new-chat + /compact. Caveman заточен под
английский короткий код-help, наши задачи — русская детализированная
документация. Несовместимость на уровне домена.
