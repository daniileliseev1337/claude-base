# Anthropic Official — пачка из 4 плагинов

## Источник
- Skill Creator: https://claude.com/plugins/skill-creator
- Legal: https://claude.com/plugins/legal
- Frontend Design: https://claude.com/plugins/frontend-design
- Security Guidance: https://claude.com/plugins/security-guidance
- Все официальные от Anthropic, бесплатные (проходят constraint «подписки не покупаются»)
- Прислал пользователь как «5-я позиция» подборки 9

---

## 5.1 Skill Creator — 🟢 УЖЕ УСТАНОВЛЕН, начать использовать

### Что делает
- 4 режима: **Create / Eval / Improve / Benchmark**
- 4 агента: Executor (runs skills), Grader (evaluates), Comparator (A/B blind),
  Analyzer (suggests improvements)
- Utility scripts: skill init, config validation, benchmark aggregation
  с variance analysis
- Install: `/skill-creator`. Free (included with Claude Code).

### Статус у нас
**Факт:** `anthropic-skills:skill-creator` уже в skills-list — установлен.
**Но не используется.** Мы skills пишем через `superpowers:writing-skills`,
но **не тестируем системно** (Eval/Benchmark).

### Применимость
🟢 **Дыра которую закрывает:** у нас 12+ skills, мы не меряем надёжность
срабатывания их триггеров. Backlog «5 агентов не выровнены по template» —
Benchmark с variance analysis ровно для этого.
- Комплементарен `superpowers:writing-skills` (написание) — этот про
  testing/lifecycle.
- **Action:** начать применять Eval/Benchmark к существующим skills +
  при создании новых.

---

## 5.2 Legal — ⚫ Не ставим (юрисдикция)

### Что делает
- `/review-contract` (clause-by-clause + risk flags), `/triage-nda`,
  `/vendor-check`, `/brief`, `/respond`
- Configurable to org playbook
- «Claude Cowork» marketplace, 0 installs
- Дисклеймер: «All outputs reviewed by licensed attorneys»

### Применимость к нашей базе (стройфирма РФ)
🔴 **Блокер: юрисдикция.** Логика contract review заточена под common law /
западные контракты. У нас РФ-право: ГК РФ, 44-ФЗ/223-ФЗ (госзакупки),
договоры подряда по СНиП. Generic Legal их не знает.
- Всё равно нужен юрист (по их же дисклеймеру).
- `/vendor-check` частично перекрыт нашим `снабженец`.

### Вердикт
⚫ Не ставим. **Идея в копилку:** configurable contract-review playbook —
если будет потребность, адаптировать в свой агент под ГК РФ
(`contract-reviewer-rf`). Триггер: реальная повторяющаяся задача ревью
договоров.

### Вопрос пользователю
- Есть ли в К-7 юр-функция? Работаете с РФ-договорами или международными?
  Если международные (англоязычные контракты с инопартнёрами) — Legal
  может пригодиться, пересмотреть.

---

## 5.3 Frontend Design — 🟢 на developer-ПК

### Что делает
- Генерация production-grade UI (landing, dashboards, panels)
- Избегает «generic AI aesthetic» (system fonts, purple gradients)
- 829,316 installs (очень популярный). Free.
- Design framework, автоактивация на frontend-запросы (не отдельные команды).

### Применимость
- Не daily-задача стройфирмы.
- **На developer-ПК полезно:** внутренние дашборды (`/token-stats` который
  предлагали в #1), сайт К-7, web-артефакты для команды.
- Частично перекрыт `anthropic-skills:web-artifacts-builder` + `theme-factory`
  + `brand-guidelines`. Frontend Design добавляет distinctive aesthetics.

### Вердикт (updated — пользователь одобрил раскат на всех при условии лёгкости)
🟢 **Раскат на все 9 ПК.** Условия пользователя выполнены:

**Проверка веса (факты, не assumption):**
- `.claude.json:52-59` — `frontend-design` уже в `plugins`, marketplace
  `claude-plugins-official`, флаг `officialMarketplaceAutoInstalled: true`.
  **Уже auto-installed на developer-ПК.**
- Структура `plugins/frontend-design/skills/frontend-design/SKILL.md` →
  **skill-based** (не hook, не MCP). **Lazy-loaded**: baseline overhead =
  только описание-триггер, полный SKILL.md при активации.
- Триггер: «build web component / page / app». Для 8 ПК (applied domain)
  такие запросы редки → плагин «спит», нулевой overhead.

**Deployment:** через `claude-plugins-official` marketplace (auto-install).
На финале проверить что marketplace включён на всех 9 ПК.

Источники:
- https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md
- https://github.com/anthropics/claude-plugins-official

---

## 5.4 Security Guidance — 🟢 на developer-ПК (защита раската)

### Что делает
- **Pre-tool hook** на Write/Edit/MultiEdit — сканит уязвимости ДО применения.
- 8 категорий: command injection (GitHub Actions), `child_process.exec`,
  `eval()`/`new Function()`, XSS (`dangerouslySetInnerHTML`, `innerHTML`),
  Python pickle, `os.system`.
- Покрытие: JS/Node, **Python**, GitHub Actions, React.
- 175,630+ installs. Free. Автоматически, no commands.

### Применимость — прямое попадание
- Мы developer-hub: hooks/scripts раскатываются на 9 ПК. Уязвимость в нашем
  коде = бьёт по всем.
- Наши skills на **Python** (openpyxl, easyocr, pikepdf, pandas) —
  `os.system`/`eval`/pickle покрыты.
- **Минус:** PowerShell НЕ в покрытии (а у нас много hooks на PS). Python-часть
  закрывает частично.
- Комплементарен built-in `/security-review` (on-demand vs автоматический).

### Вердикт
🟢 на developer-ПК — страховка перед раскатом скриптов на 9 ПК.
❌ НЕ раскат на 8 ПК — сотрудники код не пишут.
⚠ Помнить про gap: PowerShell hooks не покрываются — их ревьюить вручную
или искать PS-security-linter (PSScriptAnalyzer).

---

## Сводка #5
| Плагин | Вердикт | Где |
|---|---|---|
| Skill Creator | 🟢 уже стоит, начать Eval/Benchmark | developer-ПК |
| Legal | ⚫ юрисдикция РФ | — (идея playbook) |
| Frontend Design | 🟢 ставим | developer-ПК |
| Security Guidance | 🟢 ставим | developer-ПК |

**3 из 4 берём (developer-ПК only), Legal — пропуск из-за РФ-права.**
Все free → constraint про подписки пройден.

## Открытые вопросы
1. Legal — есть юр-функция в К-7? РФ или международные контракты?
2. Frontend Design + Security Guidance — подтвердить developer-ПК only
   (не раскат)?
3. PowerShell security gap — нужен ли PSScriptAnalyzer как дополнение
   к Security Guidance? (отдельная задача)
