---
created: 2026-05-20
status: active
owner: Даниил
tags: [мета, anti-patterns, чек-лист, индекс]
related:
  - [[karpathy-guidelines]]
  - [[chains-pattern]]
  - [[image-text-replace]]
related_external:
  - GH-600 study guide (Microsoft) — домен 1 "identify and mitigate common anti-patterns"
---

# Anti-patterns — каталог типичных ошибок и как их избежать

Собранный из всех источников нашей базы (`LESSONS-LEARNED.md` скиллов,
`memory/`, `karpathy-guidelines/SKILL.md`) реестр **anti-patterns** —
вещей которые мы уже один раз сделали неправильно или которые
формально запрещены принципами. Импорт из аудита К-7 + GH-600 study
guide (требование «identify and mitigate common anti-patterns in
agents» в домене 1).

**Использование:** перед началом сложной задачи быстро пробежаться по
релевантной категории. Перед делегацией через `Agent` — обязательно
проверить категорию «Делегация». Если кажется что anti-pattern сейчас
повторится — стоп, переосмыслить.

## Категория 1. Делегация и планирование

### A1.1 Делегация без verify-критерия

❌ **Плохо:**
```python
Agent(subagent_type="word-checker", prompt="Проверь документ X.docx")
```

✅ **Хорошо:**
```python
Agent(subagent_type="word-checker",
      prompt="Read-only ревью X.docx. Проверь: 1) плейсхолдеры,
              2) согласованность ToC ↔ body, 3) шрифт TNR.
              Возврат: PASSED/NOT PASSED + список найденных дефектов
              (CRITICAL / WARN / INFO).")
```

**Источник:** `karpathy-guidelines/SKILL.md` §4 + GH-600 домен 4
(«define success criteria and evaluation signals»).

### A1.2 Blind iteration по одному параметру

Когда пользователь говорит «текст съехал» / «цвет не тот» / «слишком
жирный» — **не** делать реактивный фикс по одному параметру.
Это анти-паттерн «градиентный спуск без понимания».

**Правильно:** **ASK first** — спросить пользователя конкретную
характеристику (font / size / weight / color / position / sharpness)
перед изменением. Каждый фикс без diagnose часто ломает что-то
другое.

**Источник:** `image-text-replace/LESSONS-LEARNED.md` §1 (КП К-7 АХП
case, 16 итераций).

### A1.3 «Сделай всё подряд» вместо приоритезации

Когда пользователь даёт неопределённый запрос «улучши X» или
«внедряй необходимое» — **не** делать все 4-5 опций подряд.
Karpathy §2 (минимум). Karpathy §5 (помощник, не подхалим).

**Правильно:** иметь мнение, выбрать 1-2 самых полезных и обосновать
**почему не остальные**. Если пользователь не согласен — сделает
явный override.

### A1.4 Не игнорировать пользовательский «измени подход»

5 итераций alignment-нюансов в LS АХП case (v1→v5) были тупиком.
Пользователь сказал «попробуй именно изменить подход» — и v6 surgical
сразу решил проблему. **Anti-pattern**: продолжать оптимизировать
существующий подход когда нужна замена.

**Признак что пора менять подход:** 3+ итерации без качественного
прогресса.

**Источник:** `image-text-replace/LESSONS-LEARNED.md` §6 (surgical
mode для длина_новая ≠ длина_старая).

## Категория 2. Скиллы и обязательные first-steps

### A2.1 Пропуск `CRITICAL FIRST STEP` в скилле

Когда SKILL.md скилла говорит «CRITICAL FIRST STEP — сделай X» —
**Claude всё равно может пропустить X**. Это случилось дважды:
- К-7 АХП case 2026-05-19: 8 итераций на Arial при scan = Times Bold
- ЛС АХП case 2026-05-20: 3 итерации Bold-vs-Regular при пропуске
  calibration

**Mitigation (в v3.1 скилла image-text-replace):**
hard `AskUserQuestion` guard перед первым render. Без явного ответа
pipeline не запускается. **Стиль `stroy-formatting`** со стилями
оформления.

**Урок для всех скиллов:** если first-step реально критичен —
делать его **через AskUserQuestion guard**, а не «пометкой» в
SKILL.md.

**Источник:** `image-text-replace/SKILL.md` v3.1 + LESSONS-LEARNED §6.

### A2.2 Default-параметры применять без диагностики

В image-text-replace скилл предлагал Times Bold default «потому что
у К-7 было Times Bold». Это **per-document** характеристика — не
переносится автоматически на новый документ.

**Правильно:** для каждого нового документа — calibration first.

### A2.3 Не читать pipeline.py до конца

В LS АХП case `refine_bg_with_diffusion` (preserve text для буквенных
ячеек) была в коде, но Claude её **не прочитал** и использовал
`refine_text_region_with_diffusion` который вызвал баг Н→П.

**Правильно:** при работе со скиллом — `grep` или Read shape файла
**до** запуска pipeline, чтобы знать **все** доступные функции.

**Источник:** `image-text-replace/LESSONS-LEARNED.md` (LS АХП §3).

## Категория 3. Документы и форматы

### A3.1 Read tool на бинарном документе

`Read` на `.docx`/`.xlsx`/`.pdf` показывает мусор. CLAUDE.md правило
MCP-routing — **обязательно** использовать соответствующий MCP.

**Правильно:** см. таблицу MCP-routing в CLAUDE.md.

### A3.2 ГОСТ-шаблон в landscape

Шаблоны `~/.claude/formatting-templates/gost-report-*.docx` исходно
были в **landscape** (29.7×21 см). ГОСТ 7.32 требует **portrait** A4.
Багу не нашли пока не сгенерировали K-7_audit_report.docx и пользователь
не заметил.

**Mitigation (2026-05-20):** 3 ГОСТ-шаблона починены на portrait.
`gost-report-with-border` оставлен в landscape — VML-рамка завязана
на landscape-координаты, требует регенерации (backlog).

**Урок:** перед использованием **любого** template проверить
orientation/dimensions/поля через `python-docx` (не доверять имени
файла).

### A3.3 US Letter вместо A4

`plain-clean.docx` исходно был **21.6 × 27.9 см** (Letter US),
не A4 (21 × 29.7). Тоже починен 2026-05-20.

**Урок:** A4 default для русских документов, явно проверять.

### A3.4 Markdown-плейсхолдеры остаются в готовом DOCX

`{{name}}`, `[[placeholder]]`, `<впишите>` — должны быть удалены
до сдачи. Обычно ловится `word-checker` агентом.

**Правильно:** всегда прогонять `word-checker` перед сдачей DOCX.

## Категория 4. Безопасность

### A4.1 Self-modification settings.json без согласия

Auto-mode classifier **правильно** блокирует попытки Claude самому
изменить `~/.claude/settings.json` чтобы добавить allow-rule
(в LS АХП case classifier остановил 4 раза).

**Правильно:** **не пытаться** обойти classifier. Если нужен
allow-rule — попросить пользователя добавить вручную, дать готовый
JSON snippet.

**Источник:** session-report 2026-05-20 LS АХП §2.

### A4.2 Изменение env-переменных без явного согласия

Стандартное правило Claude Code: «**Do not update the env unless
explicitly instructed to do so**». Касается ключей в `env: {…}`
блоке settings.json.

**Правильно:** просить пользователя добавлять env-переменные вручную
или явное «разреши править env: XYZ».

### A4.3 TLS отключение / plain passwords в .mcp.json

В К-7 базе:
- `NODE_TLS_REJECT_UNAUTHORIZED: "0"` — антипаттерн
- `WEBDAV_PASSWORD` plain text в `.mcp.json` — антипаттерн

**Правильно:** TLS не отключать. Секреты — только через env-переменные.

**Источник:** аудит К-7 + наш CLAUDE.md (раздел Безопасность).

### A4.4 Read на .credentials.json / .env / history.jsonl

`.gitignore` явно блокирует эти файлы в репо. Если Claude попытается
их прочитать — это потенциальная утечка через session-share.

**Правильно:** не читать секретные файлы. Если нужны секреты — env-переменные.

## Категория 5. Memory и контекст

### A5.1 Дублирование CLAUDE.md в memory

В memory **не** дублировать правила из CLAUDE.md. CLAUDE.md
безусловный source of truth.

**Правильно:** memory — для **накопленных** уроков и **корректировок**
подхода. CLAUDE.md — для **правил**.

### A5.2 Эфемерное в memory

«Сейчас работаю над X» — это **не** memory. Memory — **долгоживущая**
информация полезная в будущих сессиях.

### A5.3 Stale context — не очищать после смены задачи

Когда сессия переходит на **новую тему** — старый context остаётся в
chat и может загрязнять решения. GH-600 домен 3: «Prevent stale
context».

**Правильно:** при явной смене темы пользователем — `mcp__ccd_session__mark_chapter`
для разделения. Или явно зафиксировать «новая тема: …» в TaskCreate.

### A5.4 Memory без типа

CLAUDE.md memory правила: типы `user / feedback / project / reference`.
Memory без явного типа — анти-паттерн.

**Источник:** auto-memory правила в CLAUDE.md.

## Категория 6. Multi-agent и chains

### A6.1 Глубина делегации > 2 уровней

`main → доменный агент → ревьюер` — это максимум. Дальше теряется
контекст. CLAUDE.md правило: depth limit 2.

### A6.2 Параллельные tools зависящие друг от друга

Если два tool call **зависят** (output одного → input другого) —
**не** запускать параллельно. Только независимые tools параллелятся.

**Источник:** CLAUDE.md (раздел tools) + Karpathy §3.

### A6.3 Chain без verify на каждом шаге

Named chain в `~/.claude/chains/` **обязан** иметь verify-критерий на
каждом из 4 stage (collect → extract → analyze → act). Без verify
chain превращается в blind sequence.

**Источник:** `chains-pattern/SKILL.md` + GH-600 домен 1 «validate
agent plans».

### A6.4 Многоагентные конфликты — overlapping code changes

GH-600 домен 5: «detect and resolve overlapping code changes,
duplicated effort, contradictory outputs». У нас сейчас защита
**только** через git rebase autostash (auto-pull/push hooks).
Это работает для **разных файлов**, но при перекрытии — конфликт
требует ручного merge.

**Mitigation:** если работает 2 ПК одновременно — стараться править
**разные** файлы. Координация через auto-sync.log.

## Категория 7. PDF Pipeline (image-text-replace)

### A7.1 Per-cell font_size при batch замене

При batch text replacement в табличном документе — **не** рассчитывать
font_size per-cell. OCR bbox имеет ±2-3px noise → font_size колеблется
±1-2pt → визуально цифры разного размера.

**Mitigation:** `unify_font_size_for_batch()` в pipeline.py v3.1+ —
median cap_height по weight-категории, один font_size на batch.

**Источник:** `image-text-replace/LESSONS-LEARNED.md` §6 (КП ЛС АХП v7).

### A7.2 Re-render всего лейбла при разной длине

Если новый текст ≠ длина старого — никакой alignment не сделает обе
границы match. Один край всегда «уезжает».

**Правильно:** **surgical** — оставить оригинальные пиксели префикса,
рендерить только дельту.

**Источник:** LS АХП case v6.1 surgical label.

### A7.3 SD strength > 0.20 на буквенные ячейки

SD-1.5 при strength > 0.15-0.20 на тексте с **буквами** (особенно
Cyrillic с похожими формами Н/П) галлюцинирует символы.

**Правильно:** для буквенных ячеек — strength ≤ 0.10 ИЛИ использовать
`refine_bg_with_diffusion` (preserve text strokes).
Для числовых — strength 0.30 допустим (цифры устойчивее).

**Источник:** `image-text-replace/LESSONS-LEARNED.md` §3 (LS АХП Н→П баг).

### A7.4 cv2.imread на путях с кириллицей

`cv2.imread` НЕ читает Unicode-paths на Windows. → SEGFAULT или
silent fail.

**Правильно:** загружать через `PIL.Image.open()` + конвертация в
numpy array.

**Источник:** `pipeline.py:_load_image_as_array` docstring.

### A7.5 Pillow 9.5 + Cyrillic + Times Bold = SEGFAULT

Pillow 9.5.0 + freetype/HarfBuzz Raqm layout engine + кириллица в
Times Bold → ACCESS_VIOLATION без python traceback.

**Mitigation:** Pillow 12.2+ (нет бага). Альтернатива в locked env —
`ImageFont.truetype(..., layout_engine=ImageFont.LAYOUT_BASIC)`.

**Источник:** session-report LS АХП §1 (Pillow + Cyrillic SEGFAULT).

## Категория 8. PowerShell / Windows ловушки

### A8.1 PowerShell UTF-8 в CLI-аргументах

PowerShell на Windows ломает кириллицу в argv. → не передавать
русский текст через `python script.py --find "русский"`.

**Правильно:** передавать через Python-скрипт (литеральные строки)
или через стандартный input.

**Источник:** session-report LS АХП §уроки.

### A8.2 PowerShell heredoc с символами `+` `%` `$`

PowerShell парсер ломается на специальных символах в heredoc'ах.

**Правильно:** для длинных строк (commit messages, multi-line) —
передавать через файл (`git commit -F file.txt`) или python.

**Источник:** session-report LS АХП §commit.

### A8.3 PS 5.1 + UTF-8 без BOM + кириллица

Windows PowerShell 5.1 читает скрипты без BOM как Windows-1251.
Кириллица → кракозябры → парсер падает на спецсимволах.

**Mitigation:** `setup-extras.ps1` пересохранён с UTF-8 BOM
(2026-05-20). Для **новых** PS-скриптов с кириллицей — UTF-8 with BOM.

**Источник:** session с setup-extras fix.

### A8.4 PYTHONIOENCODING не utf-8 при кириллице в stdout

Когда python script print'ит русский в Windows console (cp1251) —
UnicodeEncodeError.

**Правильно:** запускать python через `PYTHONIOENCODING=utf-8 python …`.

## Категория 9. Документация и отчётность

### A9.1 Молчание ≠ всё хорошо

Reviewer-агент который возвращает «всё ок» без явного списка
проверенных пунктов — НЕ пройден.

**Правильно:** failure-mode строгий. Reviewer должен возвращать
явный список (CRITICAL / WARN / INFO).

**Источник:** CLAUDE.md (раздел Агенты-проверяльщики).

### A9.2 Session-report не пишется

Каждая сессия **обязана** писать `session-report` в
`~/.claude/session-reports/<YYYY-MM-DD>_<тема>/report.md`. CLAUDE.md
правило.

**Правильно:** триггер — закрытие сессии. Содержание — что делал,
итерации, цитаты пользователя, открытые вопросы.

### A9.3 Артефакты на Desktop без обезличивания

Public-репо `claude-base` теперь private — обезличивание смягчено, но
**пароли, API-keys, ПДн** **никогда** не пушим. Если такое промелькнуло
— `[СЕКРЕТ — не записан]`.

**Источник:** CLAUDE.md (раздел Sessions).

## Категория 10. Harvest и инструменты

### A10.1 Писать с нуля до проверки готового

Перед написанием инструмента — проверить:
1. Своя база (`~/.claude/skills/`, `~/.claude/agents/`)
2. Если нет — `harvest`-методология (GitHub, MCP registry, Anthropic skills)
3. Только потом — писать с нуля

**Источник:** `skills/harvest/SKILL.md`.

### A10.2 Бинари в репо

`cloudflared.exe` 63 MB в К-7 базе — анти-паттерн. Должно быть
`winget install` или ссылка в README.

**Правильно:** репо — для **методики**, не для **бинарей**. Бинари
ставятся через manifest или package manager.

**Источник:** аудит К-7.

### A10.3 Дубль скилла (fork анти-паттерн)

В К-7 был `pdf-advanced` рядом с `pdf` (copy Anthropic). Это анти-паттерн.

**Правильно:** если нужны расширения готового скилла — `extend`,
а не `copy`. Или использовать `harvest` workflow с осознанным
выбором лицензии.

---

## Cross-refs

- [[karpathy-guidelines]] — 5 принципов (большинство anti-patterns
  здесь — нарушение какого-то из них)
- [[chains-pattern]] — anti-patterns multi-agent (A6.*)
- [[image-text-replace]] LESSONS-LEARNED — A7.* подробно
- [[CLAUDE]] — MCP-routing (A3.1), безопасность (A4.*), agents (A9.1)
- [[memory/2026-05-09_hooks-debugging]] — A8.* PowerShell ловушки
  (16 ловушек hooks-debugging)
- GH-600 study guide (`Desktop/GH-600_study_guide_ru.docx`) — домен 1
  «identify and mitigate common anti-patterns in agents»

## История

- 2026-05-20 — первая версия. Собрано из 6+ источников
  (LESSONS-LEARNED скилла image-text-replace, karpathy-guidelines,
  hooks-debugging memory, session-report-policy memory, аудит К-7,
  GH-600 study guide).
- Обновлять при появлении нового anti-pattern в session-report или
  feedback-memory.
