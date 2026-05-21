# Sync architecture redesign for claude-base

**Date:** 2026-05-21
**Author:** subagent (commissioned by Daniil)
**Status:** design proposal, awaits Daniil's decision before any implementation
**Scope:** замена текущей peer-to-peer git-sync архитектуры на модель «один publisher, остальные read-only consumers + структурированный feedback channel»

---

## Раздел 1. Свод текущих проблем

Текущая модель — все 4 ПК (DANIILPC, R-090226727A, 100226745A, DELISEEV-PC) push'ат напрямую в `main` ветку private-репозитория `claude-base`. Симметричная peer-to-peer-репликация через git hooks (`auto-pull.ps1` на SessionStart, `auto-push.ps1` на SessionEnd). Это даёт следующие фундаментальные проблемы:

1. **`settings.json` в git — антипаттерн.** Claude Code UI постоянно дописывает в файл (`theme`, `viewMode`, MRU-настройки). Каждое UI-изменение на ПК = potential merge conflict при следующем `git pull --rebase --autostash` на другом ПК. Сегодня заблокировал pull на DELISEEV-PC, потребовался manual stash+rebase. **Корень проблемы:** файл semantically `local`, но whitelist'нут как `shared` (decision 2026-05-20 после которого начались проблемы).
2. **Race conditions.** 4 ПК асинхронно push'ат в один main. `auto-push.ps1` делает `git push` без pre-`pull --rebase` (заведомо — в hook context pull-rebase hang'ается). Если на origin кто-то опередил → push отклоняется, локальный коммит остаётся ahead, следующая сессия делает rebase. **Сегодня было 5+ таких циклов.** Eventually consistent, но шумно и непрозрачно.
3. **Auto-push timeouts.** Hook убивается через 60 сек (`timeout: 60` в settings.json). На медленной/нестабильной сети `git push` не успевает за 60 сек (особенно когда нужны 3 retry × 5 сек pause). Лог обрывается на `auto-push: start` без `DONE`. Silent failure. **Сегодня — interrupted hook на DANIILPC в 13:40, заметили только в 16:38 при следующем старте сессии.**
4. **Тихая рассинхронизация.** ПК думает что push'ил (hook завершился), а реально нет (timeout убил процесс между `git commit` и `git push`, либо push failed но pre-flight `git rev-list --count origin/main..HEAD` не запустился). **DELISEEV-PC сегодня отставал на 6 коммитов — Claude не заметил, продолжал работать как обычно, читал устаревший CLAUDE.md.**
5. **Конфликты на shared файлах.** При параллельной правке `CLAUDE.md` или `anti-patterns.md` rebase падает, hook делает `git rebase --abort`, оставляет working tree dirty. Следующая сессия не может pull'ить пока пользователь не сделает manual resolve. **Блокирует работу.**

**Дополнительные фундаментальные limitations:**

6. **Нет audit trail кто что менял.** В git history все коммиты «`auto-sync: session YYYY-MM-DD HH:MM from <hostname>`» — нет attribution, что именно изменено и **зачем**. Для Daniil как owner — невозможно review'ить «что прилетело от сотрудников» в потоке шумных auto-commits.
7. **Сотрудники могут случайно push'ить чувствительное.** Whitelist `.gitignore` помогает, но не защищает 100% — например, если в `session-reports/` сотрудник оставил клиентский шифр или ФИО, оно попадает в private-репо (приемлемо по решению 2026-05-14, но всё равно нежелательно).
8. **Нет уведомления об обновлениях.** Сотрудник не знает что прилетело — `auto-pull` молча сделал rebase. `CLAUDE.md` поменялся? Новый skill добавлен? Без явного «✓ База обновлена ... — добавлено: X, Y» сотрудник работает по устаревшей ментальной модели.

---

## Раздел 2. Архитектурные варианты

### Вариант 1. GitHub + roles (главный + read-only consumers) + feedback через Issues/PR

**A. Реализация.**
- `claude-base` остаётся на GitHub, **остаётся private**.
- **Только DANIILPC имеет push-доступ** к `main`. Остальные ПК клонируют через HTTPS без credentials с write-scope (или с PAT scope `repo:read` only — GitHub поддерживает fine-grained PATs).
- На ПК сотрудников `auto-push.ps1` **полностью удаляется** (или превращается в no-op). Остаётся только `auto-pull.ps1`.
- **Feedback channel:** отдельный репо `claude-base-feedback` (тоже private), сотрудники имеют push-доступ к **своей ветке** (`feedback/<hostname>`). Структура:
  ```
  claude-base-feedback/
    R-090226727A/
      CLAUDE.local.md          ← их персональные правила
      session-reports/         ← их сырые отчёты
      issues/2026-05-21_<topic>.md   ← структурированные тикеты
      harvested/               ← их находки
  ```
- Сотрудник на SessionEnd push'ит **только в свою ветку** своего feedback-репо. Daniil периодически открывает feedback-репо, ревью'ит, переносит ценное в `claude-base` своими руками.
- **Уведомление об обновлениях:** в `claude-base` добавляем `CHANGELOG.md` который Daniil обновляет при каждом push'е. `auto-pull.ps1` после успешного pull читает diff в `CHANGELOG.md` за последний день и логирует в `auto-sync.log` строкой `notify: <строка из CHANGELOG>`. Claude в первой реплике сессии читает эту строку и показывает пользователю.
- **`settings.json` убирается из whitelist** (gitignore'ится). Вся UI-конфигурация — personal. Shared конфиг (hooks, autoMode allow rules) выносится в `settings.shared.json` — отдельный файл, который сотрудник вручную не редактирует. `auto-pull.ps1` после pull merge'ит `settings.shared.json` → `settings.json` (только нужные ключи: `hooks`, `autoMode`, `agentPushNotifEnabled`).

**B. Решает проблемы?**

| Проблема | Решение? |
|---|---|
| `settings.json` conflict | ✅ Полностью — gitignored, sync только нужные ключи через `settings.shared.json` |
| Race conditions | ✅ Один writer = нет race |
| Push timeouts | ✅ На consumers нет push, на DANIILPC push — но он один, не критично если повторим вручную |
| Тихая рассинхронизация | ⚠ Частично — `auto-pull` всё ещё может молча упасть, но нет конфликтующих push'ей |
| Конфликты на shared файлах | ✅ Только Daniil редактирует shared — нет параллельных правок |
| Audit trail | ✅ Все коммиты в `claude-base` от Daniil, осмысленные сообщения; feedback по веткам сотрудников |
| Уведомление об обновлениях | ✅ Через `CHANGELOG.md` + строка в `auto-sync.log` |

**C. Stack.** GitHub (уже используется), 2 private-репо, fine-grained PAT с `repo:read` для сотрудников. Никаких новых tools.

**D. Effort to implement.** **3-5 часов** для Phase 1 (см. roadmap). Большая часть — отвязать `auto-push.ps1` на ПК сотрудников и настроить read-only PAT'ы.

**E. Ops cost.** Минимальный. Daniil ревью'ит feedback-репо раз в неделю. PAT'ы сотрудников нужно ротировать раз в 6-12 месяцев (GitHub fine-grained PAT может expire). Нет серверов админить.

**F. Failure modes.**
- GitHub недоступен → `auto-pull` falls back на existing local state, Claude работает в read-only к claude-base. Уже есть в логике сейчас.
- Сотрудник попытается push в `main` → 403 от GitHub, hook логирует `denied to <user>` и diagnostic. Не критично — hook не блокирует session.
- PAT сотрудника expired → pull падает, log говорит «expired», Daniil выдаёт новый PAT, сотрудник один раз делает `git credential-manager` update.

---

### Вариант 2. Self-hosted Git server (Gitea/Forgejo) + строгие permissions + отдельный feedback

**A. Реализация.**
- Поднять Gitea или Forgejo на VPS или домашнем сервере Daniil (Forgejo — fork Gitea на 2026 год активнее, чистая AGPL, ~50 MB binary).
- Все 4 ПК переключаются с github.com на gitea.daniil.ru (или DDNS).
- Роли: Daniil — owner, сотрудники — `read` на основном `claude-base` репо, `write` на своих `feedback-<hostname>` репо (отдельные репо или ветки — как в варианте 1).
- Hooks остаются по сути такие же, только URL origin меняется.
- Уведомление об обновлениях — через webhook Gitea → e-mail/Telegram Daniil'у когда сотрудник push'нул feedback. Или через ту же `CHANGELOG.md` схему.

**B. Решает проблемы?**

| Проблема | Решение? |
|---|---|
| `settings.json` conflict | ✅ Так же как в Var 1 (через role + gitignore) |
| Race conditions | ✅ Один writer |
| Push timeouts | ⚠ Зависит от latency до self-hosted сервера. Если сервер в той же сети — быстрее GitHub. Если на VPS за рубежом — может быть хуже. |
| Тихая рассинхронизация | ⚠ Так же как Var 1 |
| Конфликты на shared файлах | ✅ Один writer |
| Audit trail | ✅ Полный контроль над логами Gitea |
| Уведомление об обновлениях | ✅ Через webhooks или CHANGELOG |
| **Корп-прокси compatibility** | ❌ **Минус** — нужно whitelist'ить новый домен у IT отдела. github.com уже разрешён, новый домен — bureaucracy. |

**C. Stack.** Forgejo (рекомендую — активный fork, AGPL, обратно совместим с Gitea). VPS (€5-10/мес) или домашний сервер. Caddy/Nginx с TLS. Backup сценарий (cron на S3/B2).

**D. Effort to implement.** **2-3 дня.** Поднять сервер, настроить TLS, миграция репо, настройка PAT'ов, тест с одного ПК, потом остальные.

**E. Ops cost.** **Высокий относительно Var 1.** Сервер админить (security updates, certbot renewal, backup verification, disk space). Если упал — все 4 ПК работают в read-only к локальному cache. Стоимость хостинга. Сложность Disaster Recovery (потеряли VPS = потеряли историю если backup сломался).

**F. Failure modes.**
- VPS недоступен → consumers продолжают работать с локальной копией, но не получают обновлений. Если долго — расходятся.
- Forgejo баг в новой версии → откат, нужен компетентный sysadmin.
- IT отдел заблокировал новый домен корп-прокси → катастрофа, нужны переговоры или возврат на GitHub.

---

### Вариант 3. NO git для consumers — WebDAV/Я.Диск/Syncthing publish + manual feedback

**A. Реализация.**
- DANIILPC периодически делает `claude-base-release.zip` (или dir-tree) и публикует на Я.Диск папку с public-read link'ом (или общая папка с командой).
- На ПК сотрудников `auto-pull.ps1` заменяется на:
  ```
  download claude-base-release.zip → unzip → diff → apply
  ```
- Версионирование через `version.txt` в zip'е (`v1.3.0`). Сотрудник видит мажорные изменения в Telegram-канале/общем чате.
- **Feedback** — manual: сотрудник копирует свой CLAUDE.local.md, harvest-find или session-report в общую папку «feedback» на Я.Диске. Daniil руками забирает раз в неделю.
- **Альтернатива WebDAV:** Syncthing — peer-to-peer mesh, без сервера. Но требует все 4 ПК online одновременно для распространения = ненадёжно.

**B. Решает проблемы?**

| Проблема | Решение? |
|---|---|
| `settings.json` conflict | ✅ Полностью — нет git у consumers |
| Race conditions | ✅ Нет git — нет race |
| Push timeouts | ✅ Нет push у consumers |
| Тихая рассинхронизация | ⚠ Может быть хуже — нет ref'ов, только hash zip'а; легко пропустить релиз |
| Конфликты на shared файлах | ✅ Нет |
| Audit trail | ❌ Теряется — нет git history у consumers |
| Уведомление об обновлениях | ✅ Через version.txt + Telegram |
| Корп-прокси compatibility | ⚠ Зависит от Я.Диска (через корп-прокси может быть заблокирован Я.Диск API), Syncthing вообще требует p2p TCP |
| Offline работа | ✅ Лучше всех — снапшоты вместо live-git |

**C. Stack.** Яндекс.Диск API + REST endpoint, либо rclone, либо Syncthing. PowerShell-скрипт `apply-release.ps1` на consumer'ах.

**D. Effort to implement.** **1-2 дня.** Релиз-pipeline у Daniil (auto-zip whitelist'нутых path'ов на git-tag), скрипт apply на consumer'ах, миграция.

**E. Ops cost.** Низкий. Релизы — manual у Daniil. Я.Диск админить не надо.

**F. Failure modes.**
- Я.Диск отозвал API key → нужен новый.
- Сотрудник пропустил релиз (Telegram не открыл) → работает с устаревшей базой. Без принудительного pull это легко.
- Feedback manual — потеря feedback'ов высока.

---

## Раздел 3. Сравнительная таблица

| Параметр | Var 1 (GitHub+roles) | Var 2 (Gitea/Forgejo) | Var 3 (WebDAV/Я.Диск) |
|---|---|---|---|
| Решает race conditions | ✅ полностью | ✅ полностью | ✅ полностью |
| Решает `settings.json` conflict | ✅ через gitignore + shared-extract | ✅ так же | ✅ нет git у consumers |
| Решает push timeouts | ✅ нет push у consumers | ⚠ зависит от latency | ✅ нет push |
| Решает тихую рассинхронизацию | ⚠ улучшает, не полностью | ⚠ так же | ⚠ хуже |
| Effort to implement | **3-5 часов** | **2-3 дня** | **1-2 дня** |
| Ops cost | **Низкий** | **Высокий** (сервер) | Низкий |
| Совместим с корп-прокси | ✅ (github bypass уже настроен) | ❌ нужно whitelist новый домен | ⚠ Я.Диск иногда блочат |
| Offline работа | ✅ git local clone | ✅ git local clone | ✅ snapshot-based |
| Уведомление об обновлениях | ✅ через CHANGELOG.md | ✅ через CHANGELOG/webhook | ✅ через version.txt |
| Структурированный feedback | ✅ отдельный репо/branch per сотрудник | ✅ так же | ❌ manual copy на Я.Диск |
| Audit trail (git history) | ✅ полный | ✅ полный | ❌ теряется |

---

## Раздел 4. Рекомендация

**Var 1 (GitHub + roles + feedback-репо).** По следующим причинам:

1. **Эволюция, не революция.** GitHub уже работает, bypass-proxy уже настроен на всех 4 ПК, PAT'ы выданы, hooks написаны. Замена «все push'ат в main» → «один push'ит, остальные read-only» — это **изменение permission'ов и удаление `auto-push.ps1` на 3 ПК**, не миграция инфраструктуры.

2. **Karpathy §2 (простота).** Var 2 = поднять и админить сервер для команды из 4 ПК — overkill. Var 3 = выбросить git у consumers и потерять `audit trail` ради удобства публикации — теряется больше чем приобретается.

3. **Закрывает 4 из 5 сегодняшних проблем сразу** (race, settings, конфликты, push timeouts) и улучшает 5-ю (тихая рассинхронизация — через CHANGELOG-уведомление в первой реплике).

4. **Push back.** ТЗ упоминает Var 4 (custom FastAPI/CF Worker backend) — **отговариваю**. Для команды из 4 ПК городить REST API для feedback — это инженерная игрушка, не решение проблемы. GitHub Issues/PR в feedback-репо дают тот же API бесплатно + UI. Var 4 имел бы смысл при 20+ consumers с разнородной средой.

**Главный риск Var 1:** Daniil становится bottleneck'ом — все обновления через его руки. **Mitigation:** ввести регулярный (раз в неделю) ритуал ревью feedback-репо. Если bottleneck станет проблемой — это сигнал что команда выросла за 5+ человек, тогда уже Var 2.

---

## Раздел 5. Phase roadmap для Var 1

### Phase 1 — закрывает 60-80% боли за ~3 часа

**Tasks:**
1. **Убрать `settings.json` из whitelist** в `.gitignore` (вернуть на gitignore'нутое). Создать `settings.shared.json` с теми ключами что реально нужны shared (`hooks`, `autoMode.allow`, `agentPushNotifEnabled`). Добавить в `auto-pull.ps1` merge-шаг: после pull читать `settings.shared.json` и патчить shared-ключи в `settings.json`.
2. **Создать репо `claude-base-feedback`** (private) на GitHub. Создать ветки `feedback/R-090226727A`, `feedback/100226745A`, `feedback/DELISEEV-PC`.
3. **На ПК сотрудников:** заменить `auto-push.ps1` на версию которая push'ит только в свою ветку `feedback-репо`, не в `claude-base`. Whitelist для feedback — другой (CLAUDE.local.md, session-reports/, harvested/).
4. **На GitHub:** убрать write-access у сотрудников к `claude-base`. Выдать им fine-grained PAT с `repo:read` для `claude-base` и `repo:write` только для своей ветки `claude-base-feedback`.
5. **Добавить `CHANGELOG.md`** в `claude-base`. Daniil обновляет руками при каждом значимом push.

**Verify Phase 1:** на DELISEEV-PC попытаться `git push origin main` — должно вернуть 403. На DANIILPC закоммитить и push'нуть CHANGELOG entry, на DELISEEV-PC начать новую сессию — в auto-sync.log должна появиться строка `notify: ...`, Claude в первой реплике должен её показать.

### Phase 2 — следующая итерация, ~1 рабочий день

**Tasks:**
1. **Structured feedback templates.** Markdown-шаблоны для типов feedback в `claude-base-feedback/_templates/`:
   - `bug.md` — что сломалось, шаги воспроизведения, лог.
   - `tool-finding.md` — harvest-находка с фильтром и оценкой.
   - `rule-suggestion.md` — предложение в CLAUDE.md.
   - `session-friction.md` — где база тормозит работу.
2. **Slash-команда `/feedback <type>`** в `~/.claude/commands/feedback.md` — создаёт файл из шаблона в правильном месте feedback-репо.
3. **GitHub Actions в feedback-репо** — авто-label PR/branch update'ов по типу файла (`type:bug`, `type:harvest`, и т.д.). Daniil фильтрует.
4. **Drift detection в `auto-pull.ps1`.** Каждые N дней (или при каждой сессии) проверять `git rev-list --count HEAD..origin/main` **и логировать предупреждение если HEAD сильно отстал**. Если > 5 коммитов поведет — в первой реплике Claude явно предупреждает «база отстала на N коммитов, рекомендую закрыть сессию и проверить вручную».

**Verify Phase 2:** сотрудник выполняет `/feedback bug`, видит созданный шаблон, заполняет, commit+push в свою ветку → видно в feedback-репо с правильным label.

### Phase 3 — финальное состояние, 1-2 рабочих дня

**Tasks:**
1. **Релизный workflow.** В `claude-base` ввести git-tag'и `v1.3.0`, `v1.4.0`. Daniil тег'ает релизы. CHANGELOG.md по разделам версий.
2. **Migration cleanup.** Удалить `auto-push.ps1` на consumer'ах окончательно (или превратить в notify-only stub). Удалить write-PAT'ы.
3. **Documentation.** Обновить CLAUDE.md секцию «Auto-sync инфраструктура» под новую модель. Обновить README.md в `claude-base`. Добавить раздел в anti-patterns.md «никогда не push'ить в claude-base/main с consumer-ПК».
4. **Backup discipline.** Bare-clone `claude-base` и `claude-base-feedback` раз в неделю на отдельный диск/Я.Диск Daniil.

**Verify Phase 3:** новый ПК подключается к команде по 10-минутному guide'у (clone read-only, настройка feedback-репо, hooks). Полная процедура отдокументирована.

---

## Раздел 6. Открытые вопросы для Daniil

1. **Feedback-репо: один или несколько?** Один репо с ветками per-сотрудник проще для ревью; несколько per-сотрудник дают изоляцию (если сотрудник случайно push'нёт что-то секретное — изолированный blast radius). Какой trade-off важнее?
2. **CHANGELOG.md — manual или auto-generated?** Auto (из commit messages, через `git log --since`) дешевле, но шумнее. Manual чище, но требует дисциплины при каждом push. Какой подход выберешь?
3. **`settings.shared.json` — какие именно ключи?** Точно: `hooks`, `agentPushNotifEnabled`. Спорно: `autoMode.allow` (там длинный текст про image-text-replace pipeline — он точно общий или per-PC?), `language`, `effortLevel`, `enabledPlugins`. Нужен явный список.
4. **Удаление `auto-push.ps1` на consumer'ах — full или soft?** Full = удалить файл. Soft = оставить, но добавить в начало `if ($env:COMPUTERNAME -ne 'DANIILPC') { exit 0 }`. Soft быстрее откатить если что-то пошло не так.
5. **PAT-rotation policy.** GitHub fine-grained PAT можно настроить max 1 year expiry. Делать short-lived (30 дней) с auto-renewal через GitHub App — overkill для 4 ПК. Согласен с 1 year + manual reminder в календарь?
6. **Сколько времени готов потратить сейчас?** Phase 1 (3 часа) — да/нет? Если да — стартуем сегодня или планируем на конкретный день?
7. **`claude-base` остаётся private или переводим в public после стабилизации?** Решение 2026-05-14 — private «потому что обезличивание смягчено». Если станет public — feedback-репо точно остаётся private, но `claude-base` сам может стать demo-витриной методики. Какое долгосрочное намерение?

---

**Конец design doc.** Готов к обсуждению и доработке по фидбеку.
