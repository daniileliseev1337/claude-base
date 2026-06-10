# Эталон MCP-серверов — override CORE-секции

_Вынесено из CLAUDE.md 2026-05-26 (Phase 1 refactoring для экономии overhead токенов в каждой сессии). Загружается через Read только когда нужно._

---

## Эталон MCP-серверов — override CORE-секции

**Актуальный эталон с 2026-06-10 — 11 core-серверов** (источник истины —
`mcp-manifest.json`, `tier: core`; CLAUDE.md STOP шаг 2 синхронизирован):

| # | Имя | Назначение |
|---|-----|------------|
| 1 | `markitdown` | Конвертация .doc/.rtf/.odt/.pptx → md |
| 2 | `document-loader` | Универсальный офисный fallback + рендер слайдов |
| 3 | `word` | Полное редактирование .docx |
| 4 | `excel` | Полное редактирование .xlsx |
| 5 | `pdf-mcp` | Чтение PDF (text/tables/render/search/toc) |
| 6 | `sequential-thinking` | Meta-cognition для multi-step |
| 7 | `fetch` | Произвольный URL (2-я ступень лестницы веб-доступа) |
| 8 | `time` | Часовые пояса, расчёт дат |
| 9 | `adeu` | docx-diff с нативными Word Track Changes (через manifest) |
| 10 | `playwright` | Реальный браузер: SPA и **пробивание антибота** (401/403), где fetch/firecrawl падают; 3-я ступень лестницы. Приём: [[feedback_web_doc_fetch_browser_antibot]] |
| 11 | `exa` | Semantic web search + fetch — **1-я ступень лестницы веб-доступа** (HTTP-MCP, ставится `claude mcp add`, см. manifest `register_command`) |

**Опциональные (по типу ПК):**

| Имя | Когда нужен |
|-----|-------------|
| `autocad-mcp` | ПК с установленным AutoCAD (через manifest, github-zip-uv) |
| `firecrawl` | Scraping/поиск с headless (нужен ключ); на антиботе может ловить 401 → эскалация на `playwright` |

**Правило для STOP-процедуры:**
- В шаге 2 сверять с **11 core** именами + опциональным `autocad-mcp` если ПК с AutoCAD.
- В шаге 6 строка подтверждения: `✓ прочитан CLAUDE.md (MCP: X/11)` (или `/12` с autocad).
- Если core MCP отсутствует — прогрев `uvx <name> --help` + restart session; exa ставится
  командой из manifest `register_command` (не uvx).

**Дополнительный портативный бинарь (не MCP, для subprocess):**
- `diff-pdf v0.5.3` (GPL-2.0): `~/.claude/bin/diff-pdf/diff-pdf.exe` —
  визуальный page-diff двух PDF. Использовать через subprocess, **код не
  копировать**. _Опционально (ставится через setup-extras); на DANIILPC сейчас
  ОТСУТСТВУЕТ — проверять наличие перед вызовом._
