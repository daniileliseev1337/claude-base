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

### A1.5 Игнорирование прямого запрета пользователя в следующих итерациях

Если пользователь явно запретил приём («не закрашивай белым», «не трогай шапку»,
«без table-стилей») — запрет действует на **ВСЕ последующие итерации**, не только
на текущую. Повтор запрещённого приёма через 2-3 итерации (когда «забыл») —
анти-паттерн, пользователь читает это как неуважение к его указанию.

**Правильно:** зафиксировать запрет как жёсткое ограничение задачи (в TodoWrite /
память сессии), сверяться с ним перед каждой новой попыткой.

**Источник:** `2026-05-22_ahp-stamp-overlay` (R-090226727A) — повтор белых заливок
после прямого запрета → сессия закрыта «не справился».

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

### A3.5 PyMuPDF apply_redactions/show_pdf_page для замены штампа

PyMuPDF `page.apply_redactions(graphics=2)` **не удаляет** содержимое
внутри Form XObjects и nested content stream операторы (cm+Tj/TJ
многослойных штампов). `page.show_pdf_page()` копирует целевую
страницу **целиком**, clip работает только как окно отображения,
не как физический вырез.

**Симптом:** двойной слой — старый штамп виден поверх нового.
Обнаруживается **только** при визуальной проверке готового PDF
на ВСЕХ страницах (не «3-4 удобных»).

❌ **Плохо:**
```python
page.add_redact_annot(rect, fill=(1,1,1))
page.apply_redactions(graphics=2)   # белый прямоугольник, но содержимое осталось
page.show_pdf_page(rect, stamp_doc, 0, clip=stamp_rect)
```

✅ **Правильно:** для **физического выреза** старого содержимого —
[[pikepdf]] с инъекцией clip-path оператора в content stream
(even-odd clipping rule). См.
[[harvested/pdf/pikepdf|harvested/pdf/pikepdf.md]] минимальный пример.

**Дополнительные ловушки PyMuPDF:**

- `search_for` возвращает координаты в **MediaBox**, не visual.
  На страницах с `/Rotate=270` все расчёты bbox смещены.
  Нужно rotation-aware преобразование.
- Удаление XObject из `/Resources` оставляет объект в PDF до GC.
  Для очистки — `pdf.save(..., garbage=4)` или `mutool clean`.
- После pdfcpu stamp add — Acrobat может выдать ошибку «Type1
  шрифт без `/FirstChar`, `/Widths`». Лечится финальным
  `doc.save(out, garbage=4, clean=True, deflate=True, deflate_fonts=True)`
  через PyMuPDF.

**Источник:** session-report `2026-05-22_ahp-stamp-overlay` от
R-090226727A — 11 итераций (v6-v11) на 57 листов АХП Балашиха,
закрылась только pikepdf clip-path v11.

### A3.6 Content-stream surgery для НАНЕСЁННОЙ разметки на AutoCAD-PDF

Расширение A3.5 для класса «перерисовать наложение (CCTV/СС/ЭО) на чертеже,
пришедшем только в PDF». Те же методы (content-stream поиск, redaction) проваливаются
по **трём** дополнительным причинам:

- **«Толстая» линия = пучок тонких `0 w` штрихов.** В AutoCAD-PDF (печать
  `pdfplotNN.hdi`) визуально толстый луч — это не один `w`-штрих, а множество тонких
  с мастер-масштабом `matrix(.12,0,0,-.12,0,1684)` + Y-flip. Поиск «6 w» в потоке
  даёт **0 совпадений** — толщина не вычисляется линейно.
- **Цвет нанесённого = родному.** Красная разметка совпадает по цвету с родным
  красным плана (граница участка, кресты сноса) → по цвету нанесённое от подложки
  НЕ отделить.
- **`apply_redactions(REMOVE_IF_COVERED)`** на плотном чертеже сносит базу под
  диагональными bbox и саму разметку не убирает.

✅ **Правильно:** маска нанесённого из `get_drawings()` по **цвет+толщина в
page-space** → затем либо удаление SVG-узлов (lxml) + новый слой
([[reference_autocad_pdf_svg_markup]], без AutoCAD), либо построение заново в AutoCAD
([[reference_autocad_pdf_overlay_mcp]], если нужен DWG).

**Источник:** feedback `2026-06-03_autocad-pdf-svg-markup-edit` /
`2026-06-03_autocad-mcp-pdf-overlay-edit` от R-090226727A.

### A3.7 autocad-mcp: backend, печать PDF, EXPORTPDF

Ловушки живого AutoCAD через autocad-mcp (file_ipc):

- **Backend выбирается при СТАРТЕ сервера.** AutoCAD запущен позже Claude Code →
  `system status` = `backend=ezdxf` (нет PDFIMPORT, `can_plot_pdf:false`, нет
  `execute_lisp`). **Всегда проверять и при ezdxf делать `system init`** → `file_ipc`.
- **MCP `drawing plot_pdf` молча НЕ создаёт файл** (возвращает ok+путь, файла нет).
  Печатать через `(vla-PlotToFile (vla-get-Plot doc) path "DWG To PDF.pc3")`.
- **`EXPORTPDF` открывает МОДАЛЬНЫЙ диалог даже при `FILEDIA=0` → IPC виснет
  (Timeout).** Восстановление — PowerShell `WScript.Shell.AppActivate($acadPid)` +
  `SendKeys("{ESC}")`. Не использовать EXPORTPDF в автоматизации.
- **PDFIMPORT разрушает толстое наложение** (тесселляция в SOLID/HATCH, цвет в
  ByLayer) → наложение не редактировать в импорте, строить заново (`entmake`).

**Источник:** feedback `2026-06-03_autocad-mcp-pdf-overlay-edit` от R-090226727A.
Детали — [[reference_autocad_pdf_overlay_mcp]], [[2026-05-21_acad-com-cookbook]].

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

### A4.3a PAT / API-токены в plaintext конфигах

GitHub PAT / API-токены / ключи хранить в файлах в открытом виде —
даже если файл в `.gitignore` — антипаттерн.

❌ **Плохо:** `~/.claude/.feedback-config.json` с полем
`"token": "github_pat_11CA..."` в открытом виде. Утечка возможна:
случайный коммит мимо whitelist, screen recorder, утилиты дампа конфигов,
человек смотрит файл через VS Code, копирование на чужой ПК.

✅ **Правильно:** шифрование через Windows DPAPI CurrentUser scope.

```powershell
# Шифрование (one-time setup или при ротации PAT):
& "$env:USERPROFILE\.claude\scripts\Set-FeedbackToken.ps1"

# Расшифровка (используется внутри feedback-collector.ps1):
$secStr = ConvertTo-SecureString -String $cfg.token_encrypted
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secStr)
$token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
```

**Защищает от:** случайной утечки конфига (расшифровать может только
тот же Windows user на той же машине).

**НЕ защищает от:** malware работающего под этим же user (приемлемо для
feedback-PAT — repo scope, не критическая privilege).

**Источник:** 2026-05-26 — рефакторинг `.feedback-config.json`, помог
Deliseev своим feedback-отчётом ([[2026-05-26_auto-push-stuck-consumer-mode]]
параграф «PAT в plaintext»).

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

### A4.5 git / gh операции к GitHub через корп-прокси

Корп-прокси блокирует CONNECT к github.com. `git push`/`pull`/`fetch`
и `gh` команды падают с `Proxy CONNECT aborted`. Это наблюдалось на
всех ПК команды.

**Правильно:**

1. **Persistent fix** (одна команда на ПК, навсегда):
   ```powershell
   git config --global http.https://github.com/.proxy ""
   git config --global https.https://github.com/.proxy ""
   ```
   `setup-extras.ps1` Step 0 применяет автоматически на новых ПК.

2. **Если persistent не настроен** — `-c` флаги в каждой команде:
   ```powershell
   git -c http.proxy="" -c https.proxy="" push origin main
   ```

3. **Для `gh` CLI**: `$env:HTTPS_PROXY=""` перед командой.

**Что bypass-ится:** github.com, api.github.com, *.githubusercontent.com.

**Что нормально через прокси:** pypi, npm, huggingface.co (модели).

См. CLAUDE.md раздел «GitHub — обязательный bypass proxy».

### A4.6 Yandex.Disk API через корп-прокси

Те же грабли что с GitHub (A4.5) — корп-прокси может блокировать
`disk.yandex.ru`, `cloud-api.yandex.net`, `wiki.yandex.ru` через
CONNECT-метод и/или TLS handshake.

**Контекст:** knowledge library (2026-05-26 commit `fdad0bb`+) хранит
PDF норм на Я.Диске. Сам `norm-lookup` агент работает с **локальной
файловой системой** (Я.Диск-клиент уже синхронизировал файлы) —
**проксирование не требуется**. НО при будущих расширениях (Я.Диск
REST API для метаданных, Я.Wiki API для индекса) — обращения наружу
**должны идти bypass прокси**.

❌ **Плохо** (через корп-прокси упадёт):
```powershell
Invoke-RestMethod -Uri "https://cloud-api.yandex.net/v1/disk/resources?path=Claude_Library"
```

✅ **Правильно** (bypass):
```powershell
$savedProxy = $env:HTTPS_PROXY
$env:HTTPS_PROXY = ""
try {
    $resp = Invoke-RestMethod -Uri "https://cloud-api.yandex.net/v1/disk/resources?path=Claude_Library" -Headers @{Authorization="OAuth $token"}
} finally {
    $env:HTTPS_PROXY = $savedProxy
}
```

Или persistent через git config-стиль глобально для домена (если
HttpClient.DefaultProxy подхватывает — зависит от .NET runtime; для
PowerShell 5.1 безопаснее env-var bypass).

**Whitelist прямого подключения** (если расширим библиотеку до API):
- `disk.yandex.ru`, `*.yandex.ru` — web интерфейс Я.Диска
- `cloud-api.yandex.net` — REST API для resources/uploads/shares
- `wiki.yandex.ru`, `*.wiki.yandex` — Я.Wiki API

**Сам Я.Диск-клиент** (программа в трее Windows) — отдельная история,
он использует системный прокси через WPAD/PAC или явные настройки.
Это **не наша забота** — клиент работает с прокси штатно, потому что
интегрирован в Windows networking stack. Наша забота — `Invoke-RestMethod`
вызовы из PowerShell hooks/скриптов.

См. CLAUDE.md раздел «GitHub — обязательный bypass proxy» — та же
методология применима к Я.Диск-домену.

**Источник:** session-report 2026-05-20 (kp-ls-ahp-modify-+15)
+ закреплено как правило 2026-05-20 после повторения симптома на
DANIILPC, DELISEEV-PC, 100226745A.

## Категория 6. Дисциплина контекстного окна

Длинные сессии (70+ tool calls) перегружают context window. Claude
начинает «забывать», повторять рассуждения, терять точность. См. также
skill `handoff-to-new-chat` для proactive handoff.

### A6.1 Read больших файлов целиком вместо offset/limit

Read `pipeline.py` (1500 строк, 59 KB) целиком когда нужны 30 строк
функции — съедает 50× context без пользы.

**Правильно:**
1. `Grep` для нужной функции → найти `:line_number`
2. `Read offset=<line> limit=50` — только нужный фрагмент

### A6.2 Tool outputs без фильтра tail/grep

`pip install paddlex[ocr]` без `| tail` → 30000 строк stdout с
progress-bar'ами в контексте. То же с `pytest -v`, `paddleocr stack
trace`, `npm install`.

**Правильно:**
```bash
pip install X 2>&1 | tail -5
pip install X 2>&1 | grep -E "Successfully|ERROR|conflict"
pytest 2>&1 | tail -5
```

### A6.3 Длинные исследования в основном контексте вместо Agent

5+ Read'ов больших файлов + 3+ Bash + анализ — всё в main контекст.
Раздувает на 30-50%.

**Правильно:** `Agent(subagent_type="Explore" or "general-purpose",
prompt="...")` — subagent делает research, возвращает только summary.
См. рекомендацию из CLAUDE.md / karpathy-guidelines §4 о верификации
делегаций.

### A6.4 Foreground для долгих команд

`pip install` / `pytest --slow` / `python heavy_script.py` в foreground
блокирует и наполняет контекст stdout'ом в реальном времени.

**Правильно:** `run_in_background=true` для процессов > 30 сек.
Notification придёт при завершении.

### A6.5 Дублирование рассуждений между ответами

Каждый ответ Claude начинается с пересказа плана из 5 турнов назад.
Каждый пересказ — еще ~500 токенов.

**Правильно:** ссылаться кратко («по плану выше, шаг 3...»). Не
повторять fully.

### A6.6 Игнорирование proactive-триггеров handoff

Признаки перегруза (5+ Read'ов > 200 строк, 3+ Agent calls, 30+ turns)
видны, но Claude продолжает «один step и закроем». Context кончается
на самом интересном.

**Правильно:** при 2+ признаках одновременно — вызвать
`AskUserQuestion` с предложением handoff. Лучше передать в новый чат
**до** деградации, чем после.

См. skill `handoff-to-new-chat` для алгоритма.

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

### A5.5 Запись memory-правила по одному письму/итерации

Не фиксировать «правило» в memory по **одной** правке/письму/замечанию — это может
оказаться разовой спецификой, а не закономерностью. Дождаться финального ответа
пользователя / повторения паттерна (Правило skill-development: инструкция повторилась
**2-й раз** → кандидат в актив).

**Правильно:** разовое — в session-report; в memory — только подтверждённую
закономерность (с «почему» и «как применять»).

**Источник:** `blsh-tf-corrections` (R-090226727A) — сам автор сформулировал
«не записывать memory-правило по одному письму, ждать финального ответа».

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

### A8.5 PS 5.1 `Join-Path` принимает только 2 параметра

Windows PowerShell 5.1: `Join-Path $base 'a' 'b' 'c'` → `A positional
parameter cannot be found that accepts argument 'c'`. На PS 7+
работает (3+ параметров допустимо). Скрипты которые тестировались только
на PS 7 ломаются на consumer-ПК с 5.1.

**Правильно:** для совместимости с обеими editions — nested calls:
`Join-Path (Join-Path $base 'a') 'b'`. Или для длинных путей —
`[System.IO.Path]::Combine($base, 'a', 'b', 'c')` (всегда multi-arg).

**Источник:** `scripts/pull-feedback.ps1` fix 2026-05-27 (после года
работы скрипт впервые запустился на этом ПК и сразу нашёл ловушку).

### A8.6 `2>&1 | Out-Null` на native exe валит script на PS 5.1

`& git clone ... 2>&1 | Out-Null` в Windows PowerShell 5.1 заворачивает
stderr-строки в `ErrorRecord` (NativeCommandError) — `$?` становится
`$false` и `$ErrorActionPreference='Stop'` бросает terminating error
даже если git exit code = 0 (Cloning into ... это нормальный output git
в stderr). На PS 7+ обрабатывается мягче.

**Правильно:** `$ErrorActionPreference='Continue'` для скрипта + явный
`2>$null` для подавления stderr. ИЛИ обернуть в `try { ... } catch {}`.
Никогда не глотать stderr нативного exe через `2>&1 | Out-Null` если
`$ErrorActionPreference='Stop'`.

**Источник:** там же — `scripts/pull-feedback.ps1`.

### A8.7 PowerShell `>` / пайп пишет UTF-16 BOM

`python script.py > out.txt` (или `... | Out-File`) в PowerShell сохраняет вывод в
**UTF-16 LE с BOM**, а не UTF-8 → кириллица потом не читается другими инструментами
(выглядит как мусор / «нечитаемо»).

**Правильно:** не редиректить кириллический вывод через PS `>`. Python должен **сам**
писать файл в utf-8: `open(path,'w',encoding='utf-8').write(...)` или
`sys.stdout = open(path,'w',encoding='utf-8')`. (Перекликается с A8.3/A8.4.)

**Источник:** `2026-06-03_vso-reformat` (R-090226727A) — переформат docx-актов.

### A8.8 Yandex.Disk online-only файл (ReparsePoint) читается пустым/устаревшим

Файл на Я.Диске в режиме «доступно онлайн» (атрибут `ReparsePoint`, не скачан локально)
скрипт может прочитать как **пустой или устаревшей версии**. `LastWriteTime` НЕ помогает —
синхронизация ставит всем файлам одну дату.

**Симптом:** «скрипт видит пусто / у пользователя файл заполнен». Первая гипотеза при
таком расхождении — файл online-only. **Лечение:** открыть файл (скачать на устройство)
перед обработкой, либо проверить атрибут ReparsePoint.

**Источник:** `2026-06-03_vso-reformat` (R-090226727A).

### A8.9 autocad-mcp: кириллица через `(chr N)` и `drawing open`

- **Кириллицу в LISP писать ПРЯМО в коде** (Unicode), НЕ реконструировать `(chr N)` по cp1251
  («В»=1042, не 194; `(chr 194)`=`Â` → InsertBlock ищет внешний .dwg → «Ошибка файлера»).
  Чтение русских имён — приходит cp1251, читать дамп-файл PowerShell в `GetEncoding(1251)`.
- **MCP `drawing open` ВРЁТ** («opened», но активный док не меняется) → COM `vla-Open` +
  отдельный `vla-put-ActiveDocument`; рабочий путь ASCII (`C:\temp`). Проверять `(getvar "DWGNAME")`.

**Источник:** `2026-06-04_autocad-pdf-to-dwg`. Детали — [[reference_autocad_mcp_cyrillic]].

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

### A9.4 Верификация на «удобной выборке», не на всех артефактах

Проверить результат на 3 удобных страницах/файлах из 57 и заявить «готово» —
анти-паттерн. Дефект прячется именно в непроверенных (плавающий якорь, съехавший
штамп, лишняя пустая страница). Дополняет `verification-before-completion`.

**Правильно:** верификация на **ВСЕХ** артефактах задачи (рендер всех страниц,
re-grep по всему документу, счётчики по всем листам). Для тома — скриптовый проход
по всем, не точечный взгляд.

**Источник:** `2026-05-22_ahp-stamp-overlay` (двойной слой штампа найден только при
проверке всех 57 листов) + A3.5/A3.6.

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

### A10.4 Часы ручных попыток до harvest готового инструмента

Биться над задачей собственными ad-hoc скриптами часами, и только потом запустить
harvest — анти-паттерн. На типовых задачах (batch, конвертация, известный формат)
готовый инструмент часто находится быстрее.

**Правильно:** **harvest СНАЧАЛА** на задачах, которые пахнут «типовыми» — до того,
как писать свой велосипед. См. A10.1.

**Источник:** `2026-05-22_ahp-stamp-overlay`. ⚠ **Важная оговорка:** задача массовой
замены штампа в PDF в итоге **НЕ была решена** ни ручным путём, ни найденным harvest'ом
(pdfcpu/pikepdf — прототип «работал» лишь на 1 тестовом листе, на реальном томе результата
нет). Отсюда два урока: (1) harvest-first как принцип верен; (2) **«работает на 1 листе»
≠ решено** — валидировать на реальном объёме (см. A9.4), и не принимать самооценку
отчёта-исполнителя («working-prototype-ready») за подтверждённый результат.

### A10.5 Самооценка отчёта ≠ подтверждённый результат

Feedback-отчёт исполнителя может пометить задачу `working-prototype-ready` / «готово»,
тогда как у заказчика работы **результата не было** (кейс штампов: отчёт бодрый,
по факту — провал на томе). **Не переносить наработку в базу как actionable-методологию
только по самооценке отчёта** — сверять с реальным исходом у пользователя.

**Правильно:** провальные/недоведённые задачи фиксировать как анти-паттерн или
«пробовали, не сработало», а не как рабочий скилл/pipeline. Подтверждённый результат —
тот, что принят пользователем («заказчик доволен»), а не «прошло на тестовом листе».

**Источник:** откат скилла `pdf-stamp-pipeline` 2026-06-04 по прямой коррекции
пользователя: «задача провальная, никакого результата». Контраст — реально успешный
PDF-кейс перерисовки схемы камер ([[reference_autocad_pdf_svg_markup]], «заказчик доволен»).

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
