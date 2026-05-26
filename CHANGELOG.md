# CHANGELOG claude-base

Daniil ведёт версии. При каждом значимом обновлении методики — добавить
запись в начало (newest first). Сотрудники видят diff в первой реплике
Claude при новой сессии (через правило в CLAUDE.md).

Формат: дата + список изменений (semver не используется — сразу человеко-читаемые
описания: что добавлено / починено / убрано).

---

## 2026-05-26 — Безопасность + надёжность инфры

### Починено

- **Hub-and-spoke дыра** (`scripts/feedback-collector.ps1`):
  consumer-ПК теперь auto-harvest'ит untracked `session-reports/*/report.md`
  и шлёт их через GitHub API в `claude-base-feedback`. Раньше отчёты
  сотрудников копились локально и терялись (см. `session-reports/2026-05-26_auto-push-fix-consumer-mode/`).

### Добавлено

- **`scripts/Set-FeedbackToken.ps1`** — шифрование GitHub PAT в `.feedback-config.json`
  через Windows DPAPI CurrentUser scope. PAT больше не лежит в plaintext.
- **`skills/structured-artifacts/`** — методология выноса контекста крупных
  задач (3+ фазы, multi-agent) в md-файлы ROADMAP/STATE/PLAN/REVIEW/DECISIONS.
  Адаптация Концепта 2 из gsd-redux.
- **`harvested/pdf/pikepdf.md`** — заметка про pikepdf (низкоуровневое
  редактирование PDF content stream, физический вырез старого штампа
  через clip-path inject).
- **anti-patterns.md A3.5** — PyMuPDF apply_redactions/show_pdf_page
  не удаляет Form XObjects (закрывает класс ловушек «двойной слой»).
- **anti-patterns.md A4.3a** — PAT в plaintext конфигах → DPAPI.
- **karpathy-guidelines: harvest-first правило** — 2 итерации без
  рабочего результата → `/harvest` ПРЕЖДЕ обходных подходов.

### Сотруднику сделать (на каждом consumer-ПК)

После следующего `auto-pull` (запустится при следующей сессии Claude
Code) — один раз запустить шифрование PAT:

```powershell
& "$env:USERPROFILE\.claude\scripts\Set-FeedbackToken.ps1"
```

Скрипт спросит PAT (текущий, тот же что в `~/.claude/.feedback-config.json`
поле `token`). Зашифрует через DPAPI, обнулит plain token. После этого
плэйнтекст PAT нигде не хранится. Старый plain token продолжит работать
до миграции (WARN в auto-sync.log), так что fail-safe есть.

При переустановке Windows / переносе профиля — запустить скрипт заново
(DPAPI ключ привязан к user+machine).

---

## 2026-05-22 — Updater 2.0 (one-command setup)

### Добавлено

- **`scripts/Update-ClaudeBase.ps1`** — single-command setup для любого ПК.
  Делает за один запуск:
    1. Detect role (developer vs consumer)
    2. git pull origin main (с retry + bypass-proxy)
    3. merge-shared-settings
    4. verify-claude-base (22-23 проверки)
    5. (consumer only) prompt для PAT интерактивно + создание .feedback-config.json
    6. (consumer only) smoke-test push в claude-base-feedback
    7. Финальный summary PASS/FAIL по каждому шагу
- **`scripts/Update-ClaudeBase.bat`** — double-click wrapper. Сотрудник
  открывает проводник `~/.claude/scripts/`, делает двойной клик на
  Update-ClaudeBase.bat — всё автоматически.

### Починено

- verify-claude-base.ps1 устарел после Phase 1 — проверял `settings.json`
  в whitelist (мы его вынесли в gitignored). Заменено на проверку
  `settings.shared.json` + добавлена inverse check «settings.json **не**
  в whitelist».

### Как использовать (для сотрудника)

1. Открыть проводник, перейти в `C:\Users\<user>\.claude\scripts\`
2. Двойной клик на **Update-ClaudeBase.bat**
3. Если первая установка — скрипт интерактивно спросит PAT (получить
   от Daniil'а по secure channel).
4. Финал: либо `✅ Готово` либо `❌ Есть FAIL` с конкретной диагностикой.

---

## 2026-05-21 — Phase 2-follow-up: remote feedback

### Добавлено

- **`scripts/feedback-collector.ps1`** расширен GitHub API push:
  - Авто-создание branch `feedback/<hostname>-<userprefix>` от main
  - PUT `/repos/.../contents/feedback/<filename>` с PAT auth
  - После push → файл переезжает в `feedback-staging/pushed/`
  - Idempotent через GitHub SHA matching
- **`scripts/pull-feedback.ps1`** — для Daniil'а. Clone/fetch claude-base-feedback,
  list всех `feedback/*` веток, copy файлов в `~/.claude/feedback-inbox/all/`.
  Mark NEW vs already-seen.
- **Документ** `session-reports/2026-05-21_sync-redesign/phase2-followup-feedback-setup.md`:
  step-by-step что Daniil делает в GitHub UI (создать private repo,
  add collaborators, выдать PAT, распределить, убрать collaborators из main).

### Что осталось руками для Daniil'а

1. Создать private repo `claude-base-feedback` через GitHub UI
2. Добавить collaborators с write
3. Выдать PAT каждому сотруднику
4. На каждом consumer ПК создать `.feedback-config.json` с repo+token
5. Убрать collaborators из main `claude-base`

См. полный план в `session-reports/2026-05-21_sync-redesign/phase2-followup-feedback-setup.md`.

---

## 2026-05-21 — Phase 1+2 sync-redesign

**Архитектурный сдвиг от peer-to-peer git к hub-and-spoke.**

### Что изменилось

- **settings.json вынесен из git** (gitignored). Claude Code UI на каждом
  ПК пишет туда личные настройки — больше никаких merge conflict'ов
  между ПК.
- **settings.shared.json** — новый файл в git. Содержит **намеренные
  правила команды**: language=russian, effortLevel=xhigh, autoMode.allow,
  enabledPlugins, hooks.
- **scripts/merge-shared-settings.ps1** — раз вливает shared → local
  при auto-pull. Не перезаписывает UI-driven theme/viewMode.
- **Role detection** через `~/.claude/.developer-marker` (gitignored).
  DANIILPC = developer (push в main). Остальные = consumer
  (feedback-collect вместо push).
- **scripts/feedback-collector.ps1** — на consumer ПК собирает feedback
  файлы локально в `feedback-staging/`. Если есть `.feedback-config.json`
  с GitHub репо — push через API (TODO Phase 2-follow-up).
- **CHANGELOG.md** — этот файл. Сотрудники видят diff в первой реплике
  Claude.

### Что добавлено сегодня (Daniil session 2026-05-21)

- skills/handoff-to-new-chat (proactive handoff при перегрузе контекста)
- scripts/verify-claude-base.ps1 (smoke-test 22 пункта)
- scripts/auto-pull.ps1, auto-push.ps1 — retry logic + WARN + DONE + role detection
- scripts/setup-extras.ps1 — Step 0 (auto-apply git config bypass-proxy для GitHub)
- skills/image-text-replace v3.1 — calibration-guard + unify_font_size_for_batch + refine_bg_with_diffusion preference (LESSONS-LEARNED §6, §7)
- evals/ — 21 pytest regression-тест для image-text-replace
- chains/ — 3 named chain (docx-from-template, pdf-scan-extract, project-doc-pack)
- skills/chains-pattern — методология named chains
- anti-patterns.md — Категория 6 (дисциплина контекста)
- CLAUDE.md — разделы: дисциплина контекста, GitHub bypass-proxy, chains, role detection

---

## 2026-05-20 — Импорт из К-7 audit

- Audit чужой базы К-7 (агенты) — отчёт `~/Desktop/K-7_audit_report.docx`
- GH-600 study guide на русском — `~/Desktop/GH-600_study_guide_ru.docx`
- chains/ создан как first-class сущность оркестратора
- karpathy-guidelines §4 расширен — verify-criteria для делегаций
- image-text-replace v3.0 — production-ready после 16 итераций (КП К7 АХП case)
- formatting-templates починены (portrait A4, ГОСТ-поля)

---

## Как пополнять CHANGELOG

Daniil после каждого значимого коммита в main:

1. Открыть `~/.claude/CHANGELOG.md`
2. В **начало** добавить новую секцию формата:

   ```markdown
   ## YYYY-MM-DD — Краткий заголовок

   - что добавлено
   - что починено
   - что убрано (явно сказать deprecation)
   ```

3. Commit + push с CHANGELOG.md (он в auto-push whitelist).

Сотрудники при следующей сессии Claude увидят в первой реплике:
> ✓ База обновлена YYYY-MM-DD: <заголовок> (3 изменения)

См. правило «CHANGELOG notification в первой реплике» в CLAUDE.md.
