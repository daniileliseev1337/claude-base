# 2026-05-15 — Setup инструментария под docx/xlsx/pdf

**Контекст:** Пользователь сообщил «мы будем много работать с эксель ворд и пдф»,
попросил аудит достаточности скиллов и MCP, выбрать чего не хватает, и подключить.

**Итог:** 10/10 MCP подключены, 2 скилла дотянуты, портативный бинарь для PDF-diff
поставлен, написан собственный pdf-edit MCP (8 операций на FastMCP + pikepdf/pypdf/reportlab).

---

## Что делал (хронология)

1. **STOP-процедура старта.** Прочитал CLAUDE.md, провёл MCP-аудит: 6/8 серверов
   подключено, не хватало `markitdown`, `document-loader`. Подтвердил `auto-pull:
   без изменений`.

2. **Аудит покрытия по docx/xlsx/pdf.** Сводил таблицу: что закрывают уже подключённые
   `word`/`excel`/`pdf-mcp` MCP, что закрывают скиллы `word-helper`/`excel-helper`/
   `pdf-helper`, что НЕ закрывают (главный пробел — редактирование PDF + diff всех
   трёх форматов + OCR).

3. **AskUserQuestion (1):** какие форматы реально будут. Ответ: .docx/.xlsx/.pdf +
   старый Word (.doc/.rtf/.odt) + возможно сканы PDF.

4. **AskUserQuestion (2):** будут ли сравнения версий. Ответ: «да, разные файлы
   разных расширений».

5. **AskUserQuestion (3, 4):** подключать ли markitdown сейчас + искать ли diff-инструменты
   через harvest. Ответ: и то, и другое — да.

6. **Прогрев markitdown.** `uvx markitdown-mcp --help` подтянул 69 пакетов (onnxruntime,
   numpy, magika, speechrecognition). После прогрева в `claude mcp list` оба
   недостающих сервера (markitdown + document-loader) появились как ✓ Connected.
   **Сюрприз:** document-loader подтянулся сам, без отдельного прогрева — видимо
   uvx-кэш переиспользовал часть зависимостей.

7. **Прерывание пользователя на AskUserQuestion.** Пользователь отменил очередной
   AskUserQuestion и сказал «повтори вопрос». Перешёл на текстовый формат для
   уточнений (списки вариантов в markdown). Замечание зафиксировал.

8. **Harvest, два параллельных general-purpose агента:**
   - Агент 1 — PDF-редакторы. Результат: жёсткий фильтр (≥50★ + <12 мес + лицензия)
     не пропускает почти никого. Лидер `rsp2k/mcp-pdf` (всего 7★, MIT, свежий).
     Запасной путь — свой минимальный MCP на pikepdf.
   - Агент 2 — diff-инструменты. Результат: `adeu` (75★, MIT, активный — топ для
     docx с native Word Track Changes); `diff-pdf` (4200★, GPL, C++ CLI — для
     визуального page-diff PDF); xlsx-diff готовое не нашлось.

9. **Решения пользователя по 4 вопросам:**
   - PDF-редактирование → написать свой mini-MCP на pikepdf (а не подключать
     rsp2k/mcp-pdf — низкое доверие к 7★ проекту).
   - adeu → подключить как 9-й MCP.
   - diff-pdf → portable бинарь (после моего блокирующего замечания: choco
     требует админа, а его нет; пользователь согласился на portable).
   - xlsx-diff → дотянуть свой excel-helper.

10. **Блокеры окружения.** Проверка: `IsInRole(Administrator) = False`, Chocolatey
    не установлен, Python не в PATH (только Microsoft Store stub), `uv 0.11.13` есть.
    Установил Python 3.13.13 через `uv python install 3.13` — без админа,
    в `.local/bin/python3.13.exe`.

11. **Подключение adeu.** Прочитал заметку harvest-агента, через WebFetch проверил
    README — entry point `adeu-server`. Прогрел через
    `uvx --from adeu adeu-server --help` (висит на stdio = норма для MCP).
    Зарегистрировал: `claude mcp add adeu -s user -- uvx --from adeu adeu-server`.
    Статус ✓ Connected, 9/9.

12. **diff-pdf portable.** Через WebFetch GitHub API нашёл последний релиз
    `v0.5.3`. Скачал `diff-pdf-win-0.5.3.zip` (20.4 MB) через `Invoke-WebRequest`,
    распаковал в `~/.claude/bin/diff-pdf/`. Бинарь `diff-pdf.exe` запускается
    (exit 0), `--help` молчит — это wxWidgets-GUI приложение, справка идёт в окно;
    для CLI-вызова синтаксис `diff-pdf.exe [opts] file1.pdf file2.pdf` известен из README.

13. **Дотяжка excel-helper.** Добавил две секции к существующему SKILL.md:
    - `Cell-by-cell diff с подсветкой в новом xlsx` — функция `cell_diff()` с
      жёлтой/зелёной/красной заливкой через openpyxl.
    - `Formula-level diff` — функция `formula_diff()` сравнивает формулы как
      текст, ловит случай «формула была захардкожена в значение».

14. **Написание pdf-edit MCP.** PEP 723 single-file скрипт
    `~/.claude/mcp-servers/pdf-edit/pdf_edit_mcp.py`, ~190 строк, FastMCP +
    pikepdf + pypdf + reportlab. 8 операций (выбор «c» в AskUserQuestion):
    `merge_pdfs`, `split_pdf`, `delete_pages`, `rotate_pages`, `extract_range`,
    `replace_page`, `watermark_text`, `watermark_image`. Pages везде 1-based в API.

15. **Прогрев и регистрация pdf-edit MCP.** Через `uv run --script ...` с 60-сек
    таймаутом — uv установил все зависимости и сервер подвис на stdio (норма).
    `claude mcp add pdf-edit -s user -- uv run --script <path>`. Статус ✓ Connected,
    **10/10**.

16. **Дотяжка pdf-helper.** Добавил в таблицу иерархии и MCP-роутинга строки
    про `pdf-edit` (теперь не «нет MCP», а есть) и `diff-pdf.exe` как portable
    бинарь для визуального diff.

17. **Обновление CLAUDE.md.** В USER EXTENSIONS секции (CORE перезаписывается
    installer'ом) добавил блок «Эталон MCP-серверов — override CORE»:
    эталон теперь 10, а не 8. STOP-процедура в следующих сессиях должна писать
    `MCP: X/10`.

---

## Источники

**MCP-серверы (реально вызванные):**
- `fetch` — WebFetch на github.com/dealfluence/adeu (узнать entry point adeu-server)
  и на GitHub API releases vslavik/diff-pdf (узнать URL Windows ZIP).

**Скиллы (по триггерам — auto):**
- `karpathy-guidelines` — несколько раз применил принцип «не молча, без выдумок»
  при выборе portable-альтернативы Chocolatey и при предложении свой mini-MCP
  вместо ненадёжного rsp2k/mcp-pdf.
- `excel-helper` (правил), `pdf-helper` (правил, дотягивал).
- `harvest` — концепт применён в виде двух параллельных general-purpose агентов
  с детальными инструкциями по фильтрам и формату заметок.

**Sub-agents (Task tool):**
- `general-purpose` × 2 параллельно — harvest PDF-editors + harvest document-diff.

**CLI инструменты:**
- `uvx` — прогрев markitdown, adeu.
- `uv python install` — Python 3.13.
- `uv run --script` — запуск/прогрев pdf-edit MCP.
- `claude mcp add` × 2 — регистрация adeu + pdf-edit.
- `Invoke-WebRequest` — скачивание diff-pdf ZIP.
- `Expand-Archive` — распаковка.

---

## Артефакты

| Путь | Что это |
|------|---------|
| `C:\Users\Apoliakov\.claude\mcp-servers\pdf-edit\pdf_edit_mcp.py` | Свой MCP-сервер для правок PDF, 190 строк, PEP 723 |
| `C:\Users\Apoliakov\.claude\bin\diff-pdf\diff-pdf.exe` | Portable бинарь визуального page-diff (v0.5.3, GPL) |
| `C:\Users\Apoliakov\.claude\skills\excel-helper\SKILL.md` | +`cell_diff()` + `formula_diff()` (две новые секции) |
| `C:\Users\Apoliakov\.claude\skills\pdf-helper\SKILL.md` | +pdf-edit MCP роутинг + diff-pdf инструкция |
| `C:\Users\Apoliakov\.claude\CLAUDE.md` | USER EXTENSIONS: override эталона MCP 8→10 |
| `session-reports/2026-05-15_setup-doc-tooling/harvested/` | 11 файлов: 5 кандидатов на редактирование PDF + 5 на diff + 2 _SUMMARY |

---

## Итерации и сломалось

- **AskUserQuestion отклонён.** Сначала использовал AskUserQuestion с 3 вопросами;
  пользователь нажал «отмена», попросил повторить. Перешёл на markdown-списки в
  тексте — это работало нормально.
- **Чистый markdown-Ask vs structured AskUserQuestion.** Не уверен, в чём была
  причина отклонения. Возможно структурный UI с шахматной структурой неудобен.
  Возможно — language всех полей (но они были на русском). После напоминания
  пользователя «задавай мне вопросы на русском» уделил внимание полям
  `header`/`label`/`description` — все три оставались на русском, проблем не было.
- **Exit 255 от `uv python install`.** PowerShell 5.1 интерпретирует stderr-вывод
  uv (progress bars) как `NativeCommandError` и ставит exit 255, хотя реально
  Python поставился. Узнал из CLAUDE.md инструкций про PowerShell — это известный
  артефакт. Не стал делать `2>&1` — следовал инструкции «не редиректить stderr
  native exe в PS 5.1».
- **harvest-агент не до конца отфильтровал.** Агент 1 выдал 5 кандидатов, но
  только 1 (`rsp2k/mcp-pdf`) реально проходил CORE-фильтр. Остальные были
  явно отмечены как «не брать». Это правильное поведение (показать что искал и
  что не подошло), но было ощущение что фильтр слишком жёсткий для незрелого
  рынка MCP. Решение пользователя писать свой MCP — правильное.
- **`adeu init` риск.** Изначально harvest-агент рекомендовал `uvx adeu init` —
  но это автоконфиг под Claude **Desktop** (другой клиент). Не запустил вслепую;
  через WebFetch уточнил entry point (`adeu-server`) и зарегистрировал
  через `claude mcp add` напрямую. Это спасло от риска перезаписи чужого конфига.
- **diff-pdf.exe и --help.** Бинарь работает, exit 0, но help в stdout пуст.
  Это wxWidgets-приложение — справка в GUI окно. Не тратил время на доказательство,
  только подтвердил что запускается.
- **Chocolatey блокер.** Изначально пользователь ответил «через Chocolatey».
  Я остановился перед действием и проверил окружение: choco НЕ установлен,
  без админ-прав установить нельзя. Сообщил пользователю как блокер,
  предложил три альтернативы (portable / Python-аналог / пропустить).
  Пользователь выбрал portable. Без этой проверки — пошёл бы устанавливать choco
  с правами и упёрся в UAC. Karpathy «думай прежде кодить» сработал.

---

## Что выдумывал / приукрашивал

- **Ничего критичного.** Все URL получены через WebFetch (не угадывал).
  Все entry points (`adeu-server`, `markitdown-mcp` и т.д.) — из README или
  из `--help` через прогрев. Цифры stars/last-commit для harvest-кандидатов —
  от harvest-агентов; не перепроверял каждую, но они получены через `gh api` /
  WebSearch, не выдуманы.
- **Дата релиза adeu 2026-05-15 = «сегодня»** — совпадение, harvest-агент
  утверждает что релиз v1.6.9 в день сессии. Не перепроверил отдельным
  запросом.

---

## Цитаты пользователя (важные)

- «1- a, b, d(возможно)» — про форматы файлов: docx/xlsx/pdf + старый Word +
  возможно сканы. Сканы остались на будущее, OCR-стек не ставили.
- «2- да, будем сравнивать разные файлы разных разрешений» — про diff-инструменты,
  всех трёх форматов.
- «Найди все нужные скиллы на git-hub» — триггер на параллельный harvest.
- «Задавай мне вопросы на русском, пожалуйста» — feedback, корректировка стиля.
  Учтено. Все последующие AskUserQuestion и markdown-вопросы — на русском.
- «1-a; 2-a,b; 3-c» — финальные решения: portable diff-pdf, дотянуть excel-helper
  cell+formula diff, pdf-edit с расширенным набором (8 операций).

---

## Открытые вопросы / на следующие сессии

1. **Smoke-test pdf-edit на реальном PDF.** Сейчас сервер ✓ Connected, но
   функции не вызваны. При первой реальной задаче на правку PDF — прогнать,
   проверить, поправить если что.
2. **OCR-стек.** Пользователь сказал «возможно» по сканам PDF. Если придёт
   реальный скан без текстового слоя — поставить `tesseract` + `ocrmypdf`
   (без админа через `uv pip install ocrmypdf` + tesseract в `~/.claude/bin/`
   как portable). Сейчас не ставили.
3. **AcroForm заполнение в pdf-edit MCP.** Не включил в 8 операций. Если
   реально понадобится — добавить 9-ю операцию `fill_form_fields`
   через `pypdf.update_page_form_field_values`.
4. **Аннотации (перекраска облачков)** — в скилле есть, в MCP нет. Аналогично:
   по факту реальной задачи.
5. **`adeu` стабильность.** Пакет молод (v1.6.9 за один день — активный
   мейнтейнер, но и риск сломанных релизов). При первом docx-diff надо
   быть готовым к фолбэку (mammoth → текстовый diff через `difflib`).
6. **Auto-push прогноз.** Managed paths изменились: skills/, CLAUDE.md,
   mcp-servers/, bin/diff-pdf/ (последние два — в whitelist? нужно проверить
   `~/.claude/scripts/auto-push.ps1` или его конфиг).

---

## Auto-push на SessionEnd: прогноз

Ожидается push:
- `skills/excel-helper/SKILL.md` (изменён)
- `skills/pdf-helper/SKILL.md` (изменён)
- `CLAUDE.md` (изменён в USER EXTENSIONS)
- `session-reports/2026-05-15_setup-doc-tooling/` (новые файлы)

**Под вопросом** (нужно проверить whitelist managed paths):
- `mcp-servers/pdf-edit/` — новый каталог, возможно не в whitelist
- `bin/diff-pdf/` — большой портативный бинарь (~20 MB), скорее всего НЕ в whitelist
  (и хорошо — не надо коммитить чужой GPL-бинарь в репо).

В следующей сессии увижу реальный результат в `~/.claude/auto-sync.log`.
