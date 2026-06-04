# Эталон MCP-серверов — override CORE-секции

_Вынесено из CLAUDE.md 2026-05-26 (Phase 1 refactoring для экономии overhead токенов в каждой сессии). Загружается через Read только когда нужно._

---

## Эталон MCP-серверов — override CORE-секции

CORE-секция CLAUDE.md (STOP-процедура, шаг 2) ссылается на эталон из **8**
серверов. Это устаревшее значение. **Актуальный эталон с 2026-05-15 — 10
серверов:**

| # | Имя | Назначение |
|---|-----|------------|
| 1 | `markitdown` | Конвертация .doc/.rtf/.odt/.pptx в†’ md |
| 2 | `document-loader` | Универсальный офисный fallback + рендер слайдов |
| 3 | `word` | Полное редактирование .docx |
| 4 | `excel` | Полное редактирование .xlsx |
| 5 | `pdf-mcp` | Чтение PDF (text/tables/render/search/toc) |
| 6 | `sequential-thinking` | Meta-cognition для multi-step |
| 7 | `fetch` | Произвольный URL |
| 8 | `time` | Часовые пояса, расчёт дат |
| 9 | `adeu` | docx-diff с нативными Word Track Changes (через manifest) |

**Опциональные (по типу ПК):**

| Имя | Когда нужен |
|-----|-------------|
| `autocad-mcp` | ПК с установленным AutoCAD (через manifest, github-zip-uv) |

**Правило для STOP-процедуры:**
- В шаге 2 сверять с **9 стандартными** именами + опциональным `autocad-mcp` если ПК с AutoCAD.
- В шаге 5 строка подтверждения: `✓ прочитан CLAUDE.md (MCP: X/9)` (или `/10` с autocad).
- Если standard MCP отсутствует — прогрев `uvx <name> --help` + restart session.

**Дополнительный портативный бинарь (не MCP, для subprocess):**
- `diff-pdf v0.5.3` (GPL-2.0): `~/.claude/bin/diff-pdf/diff-pdf.exe` —
  визуальный page-diff двух PDF. Использовать через subprocess, **код не
  копировать**.
