# Session report: setup-extras Stage 8 — BOM-fix, HF token, SD download, диагностика git+proxy

**Дата:** 2026-05-20
**Host:** DANIILPC
**Project cwd:** `C:\Users\Даниил ПК`
**Источник:** Claude Code CLI (PowerShell 7.6.1 родительская, скрипты через pwsh)

---

## Запрос пользователя (кратко)

Установить недостающие инструменты на этом ПК и привести его в соответствие с базой `claude-base`. Стартовая точка — Stage 8/8 installer (`setup-extras.ps1`) упал на парсер-ошибках при первом запуске.

> «Наша задача работать в одной сфере, тоесть нужно чтобы все инструменты и специфика рабьоты соответсвовала базе»

> «Не нужно ничего менять в репозитории, к репо есть доступ только у главного ноутбука где идёт обучение и разработка»

> «в Session report прочто будет твой отчёт по которому мы отработаем замечания»

---

## Что делал (хронология)

1. **Диагностика парсер-ошибок setup-extras.ps1.** Падал в Windows PowerShell 5.1 на строках с русским текстом + спецсимволами (`|`, `(`, `)`, `'`). Причина — файл UTF-8 без BOM, PS 5.1 без BOM читает как CP1251 → русские байты ломают строковые литералы. PS 7+ читает корректно независимо от BOM.
2. **Хирургический фикс.** Добавил UTF-8 BOM (3 байта `EF BB BF`) в `scripts/setup-extras.ps1`. Бэкап исходника в `.bak-noBOM`. Подтвердил парсинг через `[Parser]::ParseFile` в PS 7 — синтаксис валиден.
3. **Аудит остальных `scripts/*.ps1`** на наличие BOM/русского. `auto-pull.ps1` и `auto-push.ps1` без BOM, но в них 0 русских символов — BOM некритичен, не трогал.
4. **Сверка с remote.** `gh` отсутствует в bash. Через `Invoke-WebRequest` GitHub Contents API: подтвердил что remote `scripts/setup-extras.ps1` тоже без BOM (23416 байт LF vs локально 23890 байт CRLF — разница чисто line-endings, content идентичен). Мой BOM-фикс — uncommitted в worktree.
5. **HF-токен.** Пользователь прислал в чат → положил в `~/.claude/.hf-token` (ASCII, 37 байт, no BOM, no newline). Перед записью проверил `git check-ignore` — файл gitignored. Значение токена в чате не повторял.
6. **Запуск setup-extras в фоне.** `pwsh -File setup-extras.ps1 -Yes` (флаг `-Yes` пропускает интерактивный prompt), лог в `~/.claude/setup-extras.log`, background ID `b2uln977m`.
7. **Установка diff-pdf v0.5.3.** В `~/.claude/bin/` его не было (упомянут в CLAUDE.md). По процедуре из `session-reports/2026-05-15_setup-doc-tooling/report.md` скачал `diff-pdf-win-0.5.3.zip` (20.4 MB) с GitHub releases, распаковал в `~/.claude/bin/diff-pdf/`. Smoke test: `diff-pdf.exe --help` exit 0.
8. **PaddleOCR warmup.** Запустил в фоне `python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='ru')"`. Скачивание моделей прошло через **HuggingFace Hub** (не baidu CDN как утверждает manifest), но инициализация predictor'а упала на `RuntimeError: [json.exception.parse_error.101] parse error at line 1, column 1: attempting to parse an empty input`. 6.6 MB модель `PP-LCNet_x1_0_doc_ori` всё-таки скачана в `~/.paddlex/official_models/`.
9. **SD-1.5 inpaint download.** Завершился через ~34 мин: 16/16 файлов, 5.2 GB в `C:\sd-cache\models--runwayml--stable-diffusion-inpainting\snapshots\8a4288a76071f7280aedbdb3253bdb9e9d5d84bb`. Marker `~/.claude/.local-state/setup-extras.applied` записан, manifest hash `D20F35EF`.
10. **Попытка git push BOM-фикса в claude-base.** Сначала упал на `Proxy CONNECT aborted` 3 раза подряд — даже с `-c http.version=HTTP/1.1` и `-c http.sslBackend=schannel`. Прочитал `auto-push.ps1` — там трюк: **удалить env-proxy и `git -c http.proxy="" push`**. Применил, fetch прошёл. Auto-mode classifier заблокировал push на main. После явной санкции пользователя через `AskUserQuestion` — push прошёл (`335f765`).
11. **Reverse — пользователь сказал «не нужно ничего менять в репозитории».** Push уже улетел секундой ранее. Откатывать не стал — это (а) тоже изменение репо, (б) force-push на main destructive.
12. **Memory-уроки записаны.** `feedback_paddleocr_cdn_outdated.md` (manifest-комментарий про baidu устарел) и `feedback_git_no_proxy.md` (правило git → без прокси, с **Why** и **How to apply**).

---

## Источники

### MCP-серверы (по именам)

В этой сессии MCP-серверы **не вызывались** — задача была про инфраструктуру, не про артефакты. На старте Claude видел все 10 серверов подключёнными (включая `adeu`, `autocad-mcp`).

### Скиллы (по триггерам)

Скиллы автоматически по триггерам не подгружались (задача про инфраструктуру). Принципы `karpathy-guidelines` применял из CORE-секции CLAUDE.md, без отдельной загрузки SKILL.md.

### Slash-команды

Не использовались.

### Нормативы / каталоги

Не применимо.

### Harvest

Не запускался.

---

## Артефакты для пользователя

Итоговых **рабочих** артефактов нет — сессия инфраструктурная. Что осталось на диске:

- `~/.claude/scripts/setup-extras.ps1` — теперь с UTF-8 BOM (committed `335f765`).
- `~/.claude/scripts/setup-extras.ps1.bak-noBOM` — бэкап без BOM (untracked, оставил локально).
- `~/.claude/.hf-token` — HuggingFace токен пользователя (gitignored, per-PC).
- `~/.claude/bin/diff-pdf/diff-pdf.exe` — 2.51 MB binary + 57 DLL (~50 MB total, per-PC).
- `C:\sd-cache\models--runwayml--stable-diffusion-inpainting\...` — 5.2 GB SD-1.5 inpaint модель.
- `~/.paddlex/official_models/PP-LCNet_x1_0_doc_ori/` — 6.6 MB PaddleOCR модель (частично, predictor не работает).
- `~/.claude/projects/<id>/memory/feedback_paddleocr_cdn_outdated.md` — новая memory.
- `~/.claude/projects/<id>/memory/feedback_git_no_proxy.md` — новая memory.

---

## Итерации, ошибки, что переделывал

### 1. Кодировка → диагностика → правка → push: процессуальная ошибка

**Промах процесса:** я полез делать `git push` в `main` claude-base через `AskUserQuestion`-санкцию, **не зная** что есть верхнее правило «push'ает только главный ноут разработки». Пользователь озвучил это правило **после** того как push уже улетел (`335f765`). Coincidence, не игнорирование, но процессуально я должен был **сначала спросить про политику push'ей с не-главного ПК**, а не лезть с дробным AskUserQuestion-санкции.

**Что узнал:** правило «push только с главного ноута, остальные ПК — read-only consumers» обновляет архитектуру в CLAUDE.md (там сейчас написано что `auto-push` hook работает на всех ПК через managed paths). Я в этой сессии больше не пушу руками. Hook оставлен включённым по выбору пользователя — session-reports/memory продолжают синхронизироваться.

### 2. Bash exit code != Python exit code (PaddleOCR warmup)

Когда запускал PaddleOCR warmup, обернул `python` в bash-скрипт с `echo "=== finished with exit code $RC ==="`. **Tool вернул exit code последнего echo**, который всегда 0, не Python'а. Так я **сообщил пользователю** что warmup прошёл, хотя Python внутри упал с exit 1.

**Lesson:** в обёртках для `run_in_background` явно делать `exit $RC` в конце, либо использовать `set -e`. Иначе reporting ошибочный.

### 3. Прокси: long detour до правильного решения

Потратил 4 попытки git fetch (HTTPS_PROXY env, `-c http.proxy=`, `-c http.version=HTTP/1.1`, `-c http.sslBackend=schannel`) — все упёрлись в `Proxy CONNECT aborted`. И только потом прочитал `auto-push.ps1` где трюк (env unset + `-c http.proxy=""`) явно прописан, плюс есть diagnose-строка про эту самую ошибку. **Lesson:** если в репо есть скрипт делающий то же что я пытаюсь — читать его **до** экспериментов, не после.

### 4. settings.json — корректно НЕ закоммитил

В worktree был `M settings.json` (добавлен `"effortLevel": "max"`). Я **не** включил его в commit — это per-machine preference. Правильное решение, без правок.

### 5. CDN-страх в manifest устарел

`mcp-manifest.json` комментарий: «paddleocr 3.x качает с baidu CDN недоступного с корп-сети». На DANIILPC PaddleOCR 3.5.0 явно качал через HuggingFace Hub (паттерн `Fetching 6 files: 100%`). Manifest-комментарий устарел. **Не правил manifest** по новому правилу «не менять репо». Зафиксировал в memory + в этом отчёте — на главном ноуте можно поправить.

---

## Что выдумывал / подставлял placeholder

Ничего не подставлял без верификации. Каждый шаг подтверждал данными (BOM-байты, размер файла, exit code, лог setup-extras).

Единственное где **отступил от Karpathy-принципа «спрашивать при неопределённости»** — это git push. Не задал верхний вопрос «можно ли в принципе пушить с этого ПК» **до** AskUserQuestion про scope коммита. Считал что `auto-push` hook в CLAUDE.md = санкция на push с этого ПК. Оказалось — нет.

---

## Цитаты пользователя

> «Так поставь установку SD? файл править не нужно»

> «установи сразу все недостающте тнструментыв» (опечатки, понял как «установи сразу все недостающие инструменты»)

> «Да установи сейчасм не будес ждать задачи» (про PaddleOCR warmup сразу, не ждать первой реальной задачи)

> «Наша задача работать в одной сфере, тоесть нужно чтобы все инструменты и специфика рабьоты соответсвовала базе»

> «Мы писали правило о том что для Git нельзя использовать прокси» — напомнил мне про правило git без прокси, которое я к моменту напоминания уже эмпирически нашёл в `auto-push.ps1`, но в CLAUDE.md как явного правила не было записано. Теперь в memory.

> «Не нужно ничего менять в репозитории, к репо есть доступ только у главного ноутбука где идёт обучение и разработка»

> «в Session report прочто будет твой отчёт по которому мы отработаем замечания»

---

## Открытые вопросы / замечания для главного ноута

Эти пункты **не делаю** с DANIILPC (новое правило). Замечания для разбора на главном ноуте:

1. **Update CLAUDE.md** под новую архитектуру «push только с главного ноута». Сейчас секция «Auto-sync инфраструктура» описывает auto-push hook как полноценный механизм синхронизации с любого ПК — это даёт неверный сигнал что ручной push с не-главного ПК тоже OK. Стоит дописать явное правило.

2. **Update `mcp-manifest.json`** — поправить устаревший CDN-комментарий в записи `easyocr.purpose`. Сейчас: «paddleocr 3.x качает модели с baidu CDN который недоступен с корп-сети». Реально (2026-05-20): PaddleOCR 3.5 качает через HuggingFace Hub, корп-сеть проходит.

3. **PaddleOCR 3.5 predictor RuntimeError** — `parse_error.101: parse error at line 1, column 1: attempting to parse an empty input`. Похоже на неполный config download или version-specific bug. Не блокер (primary OCR — EasyOCR), но если задача потребует PaddleOCR (table OCR / structure recognition где он сильнее), надо разобраться. Repro: `python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ru')"` на DANIILPC.

4. **diff-pdf v0.5.3 не интегрирован в `setup-extras.ps1`**. CLAUDE.md упоминает его как «дополнительный портативный бинарь», но в manifest его нет — устанавливается per-machine вручную. Можно добавить секцию `portable_binaries` в manifest + расширить `setup-extras.ps1` чтобы качал/распаковывал. На <ПК-разработчика> он уже стоит (по `session-reports/2026-05-15_setup-doc-tooling/report.md`), теперь и на DANIILPC. Дальше — для других ПК всё ещё ручная процедура.

5. **`auto-pull.ps1` от 2026-05-20 03:08:37 в auto-sync.log** показал `fatal: Cannot rebase onto multiple branches` + `auto-pull: FAILED (exit=128), aborting rebase`. Возможно в local git config несколько upstream'ов прописано (или ветка отслеживает что-то странное). Не моя проблема в этой сессии, но flag для разбора.

6. **`scripts/` не в whitelist auto-push**. Если на главном ноуте чините setup-extras.ps1 — auto-push hook **не запушит** его автоматически. Это by design (защита от ложных коммитов), но при правке скриптов нужен ручной push с главного ноута.

7. **SD model download — лицензия RunwayML.** Скачана `runwayml/stable-diffusion-inpainting` через HF Hub с токеном пользователя. Лицензия CreativeML Open RAIL-M — позволяет использование, но с ограничениями. Если будет распространение результатов (например, в скилл для других ПК) — посмотреть условия.

---

## Установлено в системе (DANIILPC)

**В этой сессии добавилось:**

- `~/.claude/bin/diff-pdf/diff-pdf.exe` v0.5.3 (GPL-2.0) + 57 DLL зависимостей, ~30 MB. Per-PC, не в git.
- `~/.claude/.hf-token` — токен HuggingFace, 37 байт ASCII. Per-PC, gitignored. Содержимое `[СЕКРЕТ — не записан]`.
- `C:\sd-cache\models--runwayml--stable-diffusion-inpainting\` — SD-1.5 inpaint model, 5.2 GB. Per-PC.
- `~/.paddlex/official_models/PP-LCNet_x1_0_doc_ori\` — частично PaddleOCR doc-orientation model, 6.6 MB. Per-PC.
- `~/.claude/scripts/setup-extras.ps1` — добавлен UTF-8 BOM (3 байта). Закоммичено в `claude-base` как `335f765`.

**Подтверждено уже стоявшее ранее** (через `setup-extras` skip-логику):
- **Python 3.12.10** — `$LOCALAPPDATA\Programs\Python\Python312`.
- **pip --user (Python 3.12), все 15 пакетов из manifest:** matplotlib, networkx, ezdxf, pypdfium2, pdfplumber, paddleocr 3.5.0, paddlepaddle, Pillow, opencv-python, iopaint, easyocr, diffusers, transformers, accelerate, safetensors.
- **MCP-сервера (user-scope), все 10 из manifest:** `markitdown`, `document-loader`, `word`, `excel`, `pdf-mcp`, `sequential-thinking`, `fetch`, `time`, `autocad-mcp`, `adeu`.
- **Модели:** LaMa (`C:\iopaint-cache\torch\hub\checkpoints\big-lama.pt`, 196 MB), EasyOCR RU+EN (`~/.EasyOCR/`).

---

## Обезличивание

Репо `claude-base` private, обезличивание смягчено.

**В этом отчёте есть** (по новому правилу — допустимо):
- Hostnames: `DANIILPC`, `<ПК-разработчика>`, `100226745A` (последнее — из auto-sync log, не моё)
- GitHub-аккаунт: `<логин>`
- Email: `<email-разработчика> (<домен-организации>` (из строки в setup-extras.ps1, не моё добавление)
- Proxy host: `scuf-meta.ru:10894` (упомянут в `feedback_git_no_proxy.md`, важен для urocheв)
- Proxy username: упомянут в memory (не в этом report'е, чтобы не дублировать)

**В этом отчёте нет** (отфильтровано):
- HF-токен пользователя — `[СЕКРЕТ — не записан]`
- Пароль corp-прокси — `[СЕКРЕТ — не записан]` (промелькнул в env-vars при диагностике, не записывал)
- GitHub PAT — не использовался, его нигде на этом ПК нет

---

## Метрика сессии

- **Коммитов в claude-base:** 1 (`335f765` — BOM-фикс). Это процессуально неправильный коммит с не-главного ноута; решение оставлено пользователю.
- **ПК затронуто:** 1 (DANIILPC). Эффект BOM-фикса — глобальный (исправляет любой Windows-ПК с PS 5.1 в будущем при `git pull`).
- **Background задач запущено:** 2 (`b2uln977m` setup-extras, `bdcrgma7s` PaddleOCR warmup).
- **Новых memory-файлов:** 2 (CDN устарел + git без прокси).
- **Архитектурных push-back-ов от пользователя:** 1 (не пушить с не-главного ПК).
- **Моих процессуальных ошибок:** 2 (push в main без знания правила; bash-обёртка скрыла Python exit code).

---

## Auto-sync

**В начале сессии (auto-pull):**

Лог `auto-sync.log` показывает:
- `[2026-05-20 03:08:37] auto-pull: start` → `Already up to date.` → `auto-pull: ok`
- НО там же: `fatal: Cannot rebase onto multiple branches.` → `auto-pull: FAILED (exit=128)`

То есть auto-pull одновременно показывает успех и failure — какая-то странность с локальным git конфигом или авто-stash логикой. Flag для разбора (см. пункт 5 в «Открытые вопросы»).

**В конце сессии (auto-push прогноз):**

Managed paths whitelist: `agents/`, `skills/`, `memory/`, `session-reports/`, `harvested/`, `CLAUDE.md`.

В этой сессии менялось:
- `session-reports/2026-05-20_setup-extras-bom-and-models/report.md` — **новый файл, попадает в whitelist** → auto-push запушит этот session-report при SessionEnd.

НЕ в whitelist (auto-push НЕ запушит):
- `~/.claude/projects/<id>/memory/feedback_*.md` (это **auto-memory** per-project, **не** общая `memory/`). Останется локально на DANIILPC.
- `settings.json` (per-PC `effortLevel: max`).
- `scripts/setup-extras.ps1.bak-noBOM` (untracked).

**Прогноз:** auto-push на SessionEnd добавит ровно 1 коммит — этот session-report. В следующей сессии при auto-pull увижу его в логе.
