# 2026-06-10 — Harvest: 21 GitHub-репо из Telegram-подборки пользователя

## Контекст
Пользователь собрал ботом подборку репо (Show HN и пр.) и поручил оценить: нужно/не нужно,
заменяет/облегчает что-то в базе. Метод: корзины по описанию → 7 haiku-субагентов
(6 глубоких + 1 на беглую корзину), ~250k haiku-токенов. Факты — api.github.com + README,
лестница веб-доступа. Полные заметки: `harvested/`.

## Вердикты (21 репо)

### ВЗЯТЬ (2)
| Репо | Что | Действие |
|---|---|---|
| **bim-plugin-builder** (MIT, 2026-05) | C#-плагины Revit/Tekla БЕЗ Visual Studio: PowerShell + dotnet SDK 8; Revit 2020–2026 (net48 / net8.0-windows), сам генерит .csproj и .addin, деплоит в Addins | Пилот: тестовая кнопка под Revit 2025; при успехе — skill + fallback-секция в pyrevit-engineer для компилируемых аддинов. Риск: 1⭐, single-author — но скрипт ~100 строк, форкнуть в базу |
| **peer-review** (2026-06) | Панель AI-ревьюеров + editor-агент, синтезирующий консенсус | Код не тащить — забрать ПАТТЕРН «editor-synthesizer»: когда наши ревьюеры расходятся (PASSED vs BLOCKER), спавнить агента-резолвера вместо fail-fast. Кандидат в архитектуру ревьюеров CLAUDE.md |

### ПОПРОБОВАТЬ / харвест идей (5)
| Репо | Идея для нас |
|---|---|
| **sv-excel-agent** (218⭐, MIT) | Сам агент не нужен (дубль Claude Code + excel-MCP, OpenRouter-зависимость). ХАРВЕСТ: паттерн «формулы через живой Excel» — лечит нашу граблю кэша openpyxl (пересчёт через COM); SpreadsheetBench как eval для сметчика/снабженца |
| **scanify** (101⭐, MIT, Swift) | На Windows не встанет. ХАРВЕСТ ИДЕИ: заменить SD-полировку (3.4ГБ, медленно) в image-text-replace на детерминированный PIL/OpenCV-шум+наклон+тень (~10 строк) — кандидат в backlog скилла |
| **context-ledger** (10⭐, MIT) | Git-hook: при коммите детали → 300-токеновая запись в ledger, восстановление через git show. Идея для context_discipline; пилот возможен (Git Bash есть). Claude Desktop совместимость не проверена |
| **textsnap** (88⭐, MIT) | ~~ПОПРОБОВАТЬ~~ → **ЗАКРЫТО 2026-06-11: пилот провален.** Бенч upd_vrnlom_p1.png: кириллица в кашу («Продаваць», «Счате: фактура», вкрапления арабицы/иероглифов), ИНН/КПП исковерканы, 315 с/страницу на CPU (i5-13420H), обрезка на 2048 токенах, bbox нет. EasyOCR-pipeline (image-text-replace) остаётся безальтернативным |
| **rightmind / opra.ai / vex-tui** | Низкий приоритет: дебат-паттерн уже есть в Workflow; governance — когда понадобится formal approval; vex-tui — Go-вьюер, мониторить |

### НЕ НАДО (по изучению — 3, по описанию — 8)
- **parsley** — vision-LLM парсинг через ОБЛАЧНЫЙ API (Gemini/OpenRouter): конфиденциальные УПД наружу нельзя; наш локальный стек (pdfplumber+EasyOCR) задачу решает.
- **Matrix** — point-to-point синк сессий; наш hub-and-spoke git-синк масштабнее. **GitMo** — UI-обёртка Git, Linux-only; auto-hooks уже есть. **MetaPurge** — UI-обёртка; pikepdf+PIL умеют.
- По описанию: wsp-wordpress-mcp (нет WordPress), PhpSpreadsheet (PHP), dgdoc (Go-темплейтинг), microsoft/Lens (t2i-генерация), OCRmyPDF-AppleOCR (macOS), go-pdf (Go), makememe (юмор), OpenMythos (теория без практики).

## Добивка (3 репо, токен-экономия/безопасность)
| Репо | Вердикт | Суть |
|---|---|---|
| **guardian-runtime** (10⭐, MIT) | НЕ НАДО для подписки | Firewall перехватывает через `ANTHROPIC_BASE_URL`-прокси — работает только для СВОИХ скриптов с SDK+API-ключом; к подписочному Claude Code точки перехвата нет. Резерв: если заведём API-скрипты — вернуться за паттернами политик |
| **code-mapper** (3⭐, public domain, чистый Python 17КБ) | ПОПРОБОВАТЬ (гибрид) | Статичный PROJECT_CONTEXT.md: дерево + Mermaid-диаграммы + индекс символов, ~78% сжатие. Не конкурент graphify (тот queryable для md-базы), а дополнение: для Python-tools/ скиллов и onboarding-памятки — 0 токенов на построение |
| **structural-beacon** | NOT_FOUND | Репо 404 (удалено после HN-поста?), у автора public_repos=0 — оценка невозможна |

## Уроки
- Подборка Show HN = молодые репо (1–10⭐): брать ПАТТЕРНЫ и идеи, не зависимости; форкать мелкие скрипты в базу.
- Фан-аут 7 haiku-агентов с веб-доступом — штатно: ~250k токенов, ~1 мин/агент, лестница exa→fetch работала.

## Открытые действия (на решение хаба)
1. Пилот bim-plugin-builder (нужен dotnet SDK 8 ~200МБ; машина с Revit 2025).
2. Пилот textsnap на бенч-скане УПД (10 мин).
3. Внедрение паттерна editor-synthesizer в правило ревьюеров.
4. Backlog: scanify-идея (PIL-полировка вместо SD) в image-text-replace; live-Excel пересчёт в excel-helper.
