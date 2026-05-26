---
created: 2026-05-18
updated: 2026-05-26
status: active
owner: Даниил
tags: [мета, индекс, harvested]
---

# Harvested — внешние инструменты

Заметки про GitHub-репо, PyPI-пакеты и MCP-серверы, которые искали в рамках harvest-workflow (см. [[2026-05-13_harvest-workflow]]). Не код этих инструментов — только описания, оценка, решение «брать / не брать».

## Категории

### Диаграммы и визуализация ([[diagrams|diagrams/]])

11 инструментов для генерации диаграмм. Краткий обзор: [[mermaid-cli]], [[graphviz-graphviz]], [[plantuml]], [[mingrammer-diagrams]], [[terrastruct-d2]], [[cdelker-schemdraw]] (электросхемы), [[pyvis]], [[blockdiag-nwdiag]], [[jgraph-drawio]], [[netbox-topology]], [[structurizr]].

### DWG / AutoCAD ([[dwg|dwg/]])

CAD-инструменты. Главный индекс — [[_INDEX]] в папке. Заметки: [[puran-water-autocad-mcp]] (взяли в работу — см. handoff DELISEEV→DANIILPC), [[ezdxf]], [[libredwg]] / [[libredwg-web]], [[AutoCADCodePack]], [[AutoLispExt]], [[acad-api-skill]], [[cad2x-converter]], [[daobataotie-CAD-MCP]], [[datadrivenconstruction-cad2data]], [[dxf-json]].

### PDF ([[pdf|pdf/]])

PDF-инструменты для извлечения / OCR / редактирования. [[pdfplumber]] (наш fallback к pdf-mcp), [[pypdfium2]], [[PyMuPDF]], [[pymupdf4llm]], [[OCRmyPDF]], [[PaddleOCR]], [[EasyOCR]], [[surya]], [[marker]], [[camelot-dev]] (таблицы), [[docling]], [[unstructured]], [[jztan-pdf-mcp]], [[rsp2k-mcp-pdf]].

### Прочее (корень)

- [[2026-05-08_alirezarezvani-claude-skills]] — большая коллекция Claude-skills, harvest заметка про неё.
- [[gsd-redux]] — spec-driven workflow для Claude Code (GSD framework). Verdict: ВЗЯТЬ 2-3 концепта. Концепт 1 (60%/70% thresholds) и Концепт 3 (agent prompt structure) уже адоптированы — см. [[CLAUDE]] / [[_TEMPLATE]]. Концепт 2 (structured artifacts) адоптирован 2026-05-26 как скилл [[structured-artifacts]] (не chain — это методология, не pipeline).
- [[codegraph]] — Pre-indexed semantic knowledge graph для AI агентов (35% дешевле, 70% меньше tool calls). Verdict: точечно для code-проектов (BIM-плагин, AutoLISP), **не** для нашей методической базы и не для документ-driven работы.
- [[README]] — описание самой папки.

## Правило harvest

Найти 2-5 внешних инструментов под задачу. GitHub (приоритет) → MCP registry → Anthropic skills. Фильтр по активности/звёздам/лицензии. Заметка в `session-reports/<...>/harvested/` (per-session) и/или сюда (общая база).

## Связанные

- [[CLAUDE]] — секция «Harvest-workflow»
- [[2026-05-13_harvest-workflow]] — методика
- [[Карта vault]] — общая карта
- [[session-reports/session-reports|session-reports]] — per-session harvest заметки
