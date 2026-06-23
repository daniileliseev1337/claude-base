# Session report — оптимизация graphify (триггеринг + scope + устаревание)

**Дата:** 2026-06-22
**Роль:** хаб (разработка claude-base)
**Тема:** починка инструмента graphify по двум жалобам пользователя: «не всегда вызывается где нужно» и «засоряется, берёт лишнее».

## Контекст / задача

Изучали устройство базы (Workflow-картирование 10 подсистем), затем сфокусировались на graphify — самом рычажном инструменте (экономит токены через граф-навигатор вместо слепого перебора файлов). Появился новый материал `graph-pilot` (лид-магнит к ролику, репо safishamsi/graphify) — рассмотрели как кандидат на замену/дополнение.

## Диагноз (4 корня, подтверждены фактами)

Аудит реального графа базы (1166 узлов) + независимая карта картировщика:
- **A — засорение scope.** ~55-75% узлов = session-reports (466), harvested (113), evals (61) — это история/сырьё, НЕ устройство базы. God-nodes садились на мусор, ядро (agents 19 узлов на 16 агентов, blocks 5) тонуло.
- **B — слабый триггеринг.** `description` общий, нет проактивных правил, завязка на `/graphify`.
- **C — устаревание.** Граф на 12 дней / 50 структурных файлов позади HEAD, сигнала нет. «Устаревший граф уверенно врёт».
- **D — query-лексика.** bare `query` без vocab-expansion даёт 0 hits при русском вопросе ↔ англ./нормализованные labels. Fast-path в SKILL побуждал пропускать expansion; vocab-скрипт писал без `encoding=utf-8` (падал на кириллице).

`graph-pilot` нельзя поставить вместо нашего движка: без Gemini-ключа он не строит граф по докам (а база = сплошь .md). Его ценность — триггеры + 3 гарда. Выбран **гибрид-апгрейд** нашего движка.

## Что сделано

1. **A — `.graphifyignore`** в `~/.claude` (detect() его уже читает — движок не трогали). Исключает session-reports/harvested/evals/служебные/mcp-servers/plugins/бинарники.
2. **B+E — SKILL.md graphify**: переписан `description` (живые русские триггеры намерение→, проактивность, query-first при наличии графа); добавлена секция «🛡 Гарды» (размер <100, платный `--mode deep`, не ставить ломающий PreToolUse-хук, имя пакета `graphifyy`).
3. **D — `references/query.md` + SKILL.md**: vocab-expansion закреплён как обязательный даже на fast-path; добавлен `encoding='utf-8'` в vocab-скрипт; UTF-8 заметка для Windows.
4. **C — `scripts/graph-staleness-check.ps1`** (новый SessionStart-хук, зарегистрирован в settings.shared.json после auto-pull): сравнивает `built_at_commit` графа с git HEAD по структурным путям, предупреждает одной строкой (хабу — «пересобрать», consumer — «не доверять»).
5. **F — пересборка графа** со scope: subъагенты sonnet ×8 (doc-экстракция), AST для кода. Результат: **1166 → 708 узлов, NOISE=0, built=HEAD, query возвращает ядро** (Reviewer chain → CLAUDE.md, Auditor, Karpathy и т.д.).

## Метрики до/после

| | До | После |
|---|---|---|
| Узлов | 1166 | 708 |
| Мусор (session-reports/harvested/evals) | ~640 | 0 |
| agents | 19 | 32 |
| communities | 179 | 92 |
| built_at_commit | отставал 12 дней | = HEAD |

## Где сломался / грабли

- **Workflow завис** на фазе 1: один субагент-картировщик (`agents/`) добавил в StructuredOutput поле, которого нет в схеме (`additionalProperties:false`) → валидация отбила → агент закрыл turn текстом вместо повтора → `parallel()` барьер ждал вечно, фаза critic не стартовала. Данные не потеряны — все карты лежали в jsonl как StructuredOutput-вызовы, извлёк вручную. **Урок:** не ставить `additionalProperties:false` на Workflow-схемах, или явно запрещать агентам лишние поля.
- **Windows + python**: кириллица в .py исходнике ломает py3.13 на этом окружении («encoding problem: utf-8») — комментарии только латиницей; `extract()` форкает процессы → нужен `if __name__=='__main__'` guard; путь из `.graphify_python` читать `Get-Content -Encoding UTF8`; вывод python в файл UTF-8, не в cp1251-консоль; кавычки в `python -c` съедаются PowerShell → запускать .py файлом.
- `to_json` защищает от потери данных при сокращении графа (>N узлов меньше) — нужен `force=True` для легитимного scope-сокращения.

## Осталось

- Коммит правок + graphify-out/ (за пользователем).
- Опционально: ручной labeling 92 communities (пропущен — query/explain работают без него); внести firecrawl в mcp-manifest (рассинхрон эталона, из карты MCP).

---

# Продолжение сессии (та же сессия, расширилась за пределы graphify)

## 2. Updater fix — feedback-config валидация (коммит в 7c8a978)
`Update-ClaudeBase.ps1` Step 5 валидировал `.feedback-config.json` по plaintext `token`, который с 2026-05-27 обнуляется (канон — `token_encrypted` DPAPI). Consumer после миграции получал ложный FAIL + exit 1. Фикс: `github_repo -and (token_encrypted -or token)` + WARN на legacy; интерактивная ветка теперь шифрует через DPAPI (как Set-FeedbackToken.ps1). Сверено с feedback-collector.ps1 / pull-feedback.ps1.

## 3. Методичка для сотрудников по Claude Code
- **Источник:** `docs/methodichka.md` (коммит fb2d45c) — версионируется, раздаётся командой через /sync-base. Универсальная (база как есть, ОВ/ВК/ЭО/СС).
- **<организация>-версия (фирменная, для рассылки)** на Рабочем столе: `Методичка-К7-Claude.pdf` + `Методичка-К7-Claude.docx`. Собрана на шапке <организация> из шаблона `~/Desktop/Инструкции_по_оборудованию_AV_комплекс_1.docx` (python-docx, копия шаблона → чистка тела → контент; docx2pdf через Word COM). Правки по ходу: убран блок «Утверждаю»/ген.директор; **убраны ОВ/ВК** (профиль <организация> = ЭО/СС: электрика, слаботочка/АВ/освещение — допущение, подтвердить у пользователя); добавлен раздел 13 «Наглядная карта базы (граф знаний)».
- **Граф базы** скопирован рядом: `~/Desktop/Граф-базы-К7.html` (интерактивный, 684 КБ).
- Backlog: добавить раздел 13 (про граф) и в базовый `docs/methodichka.md` (сейчас только в <организация>-версии); решить, версионировать ли <организация> DOCX/PDF.

## 4. Playwright «about:blank» — закреплена версия (коммит fdf5c8c)
Симптом (несколько сотрудников): Chrome открывается пустой, навигация не идёт; раньше работало. Корень: `npx -y @playwright/mcp@latest` авто-обновлялся, на смене версии докачка браузера через корп-прокси зависала. Воспроизведено обратное: на 0.0.76 navigate работает. Фикс: пин `@playwright/mcp@0.0.76` (регистрация + mcp-manifest.json), `/sync-base` шаг «version-drift» перерегистрирует у консьюмеров. Память: [[playwright-mcp-pin-version]].

## 5. Web-access правило — ветка окружения под корп-прокси (коммит 38e9d4d)
`memory/feedback_web_direct_access.md` предполагал, что playwright всегда доходит до сайта (верно под VPN/прямой выход, ложно под корп-прокси в терминале VS Code → about:blank). Добавлен **ШАГ −1 «Окружение»**: диагностика `env|grep proxy`; под прокси читать через exa/firecrawl (свой канал) + файлы curl --noproxy; playwright только off-proxy/VPN или с `--proxy-server` (per-machine). `@playwright/mcp` умеет `--proxy-server`/`--proxy-bypass`.
- Открытый вариант: прописать playwright `--proxy-server=<корп-прокси>` per-machine в CLAUDE.user.md, если нужно чтобы браузер реально работал на work-ПК (нужен адрес прокси).

## Память, добавленная за сессию (projects/.../memory/)
[[workflow-schema-strict-hang]], [[graphify-base-scope-rebuild]], [[next-base-session-review-feedback]], [[playwright-mcp-pin-version]].

## Очередь на следующие сессии
1. Разбор feedback-отчётов сотрудников (pull-feedback → feedback-inbox, ~10 веток) на дыры/изъяны → миграция в shared.
2. Граф БЛОКА ПТО (план в blocks/pto/, рецепт пересборки отлажен).
3. Мелочи: раздел 13 в базовый methodichka.md; firecrawl в mcp-manifest; (опц.) playwright --proxy-server per-machine.
