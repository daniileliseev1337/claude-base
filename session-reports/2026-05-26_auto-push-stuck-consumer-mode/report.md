# Auto-push «застрял»: разбор и факты — session-reports не уходят в main с consumer ПК

## Симптом

Пользователь закрыл сессию (клик «крестик» на окне Claude Code) и проверил, запушился ли его `session-reports/2026-05-26_polozhenie-dms-k7/` в claude-base. Ответ: **нет**. И не только он — застряли 5 untracked папок session-reports:

```
?? session-reports/2026-05-22_ahp-stamp-overlay/
?? session-reports/2026-05-22_blsh-tf-corrections/
?? session-reports/2026-05-25_blsh-mc-izveschenie-izm1/
?? session-reports/2026-05-25_pdf-stamp-pipeline/
?? session-reports/2026-05-26_polozhenie-dms-k7/
```

В `auto-sync.log` SessionEnd auto-push hook завершался DONE'ом — но в main ничего не уходило. Похоже на баг.

## Корень — это **НЕ баг**, это **архитектурное решение**

`~/.claude/scripts/auto-push.ps1` строки 115–132:

```powershell
$isDeveloper = Test-Path (Join-Path $claudeDir '.developer-marker')
if (-not $isDeveloper) {
    Write-SyncLog "consumer mode (no .developer-marker) — running feedback-collector"
    $feedbackScript = Join-Path $claudeDir 'scripts\feedback-collector.ps1'
    if (Test-Path $feedbackScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $feedbackScript 2>&1 | Out-Null
        Write-SyncLog "feedback-collector finished"
    } else {
        Write-SyncLog "feedback-collector.ps1 not found — skip"
    }
    Write-SyncLog "DONE (consumer)"
    Pop-Location
    exit 0
}
```

**Логика hub-and-spoke** (Phase 2 sync-redesign 2026-05-21):

| Роль | Маркер | SessionEnd auto-push |
|---|---|---|
| Developer (DANIILPC, Daniil) | Есть `~/.claude/.developer-marker` | Push в `main` как обычно |
| Consumer (сотрудники) | Маркера нет | **Push в main отключён**. Запускается `feedback-collector.ps1` вместо push'а |

То есть на consumer ПК **сами session-reports никогда не попадают в `claude-base/main` через hook'и**. Они **только локально** в файловой системе.

## Проверено на этом ПК

```
hostname: R-090226727A
user:     <разработчик>
~/.claude/.developer-marker:  отсутствует  →  consumer mode
~/.claude/.feedback-config.json:  есть, указывает на `<логин>/claude-base-feedback` (отдельный feedback-репо с PAT — секрет в отчёт не записан)
```

Лог auto-push'а текущей и предыдущих сессий — однотипный:

```
[2026-05-26 16:05:00] auto-push: DONE (consumer)
[2026-05-26 16:19:39] auto-push: consumer mode (no .developer-marker) — running feedback-collector
[2026-05-26 16:19:39] feedback-collector: feedback-pending/ empty — nothing to collect
[2026-05-26 16:19:39] auto-push: feedback-collector finished
[2026-05-26 16:19:39] auto-push: DONE (consumer)
```

Никаких ошибок, никакого «застрял». Hook сделал то, что задумано.

Те коммиты в `git log`, которые **выглядят** как session-reports от 2026-05-26 (например `d10fb39 docs(session-report): полный отчёт 2026-05-26 с audit-trail`) — пришли на этот ПК **через `auto-pull`** из `claude-base/main`, куда их запушил DANIILPC. На этом ПК с такими именами папок нет — только наши локальные.

## Почему накопилось 5 застрявших отчётов

С 22 по 26 мая на этом ПК прошло 5 сессий, в каждой Claude писал `session-reports/<date>_<тема>/report.md` по правилу из CLAUDE.md (§«Sessions — обязательный отчёт каждой сессии»). Каждый раз SessionEnd hook завершался DONE (consumer) без push'а. Папки оставались untracked.

Симптом «push не сработал» появился **только сейчас**, когда пользователь явно полез в git status. До этого выглядело как «вроде всё ок» — но на самом деле всё это время session-reports просто копились локально.

## Дополнительный фактор — отчёт не написан, push отключён

Правило CLAUDE.md обязывает **каждую** сессию писать `session-reports/<date>_<тема>/report.md`. Но политика consumer-mode параллельно **не пушит** эти отчёты. Получается противоречие: правило пишет, hook не отправляет. Без ручной починки или без `.developer-marker` отчёты **гарантированно** копятся.

Возможные решения (на принятие пользователя):

1. **Поставить `.developer-marker` на этот ПК** — если <разработчик> де-факто developer (а не просто consumer-сотрудник). Тогда hook начнёт пушить как с DANIILPC.
2. **Расширить consumer-mode** в `auto-push.ps1`: даже без developer-marker пушить узкий whitelist (`session-reports/` + `memory/` + `harvested/`), а в main коммитить от имени consumer'а. Тогда session-reports не будут застревать ни на каком ПК.
3. **Явно перенести feedback-collector** так, чтобы он сам забирал свежие session-reports и заливал их в `claude-base-feedback` (отдельный feedback-репо). Тогда consumer'ы не пишут в main, но отчёты всё равно где-то централизованно собираются.
4. **Оставить как есть**, но добавить в первой реплике сессии явный warning «на этом ПК consumer-mode, push в main отключён — N untracked session-reports накопилось, запушить вручную?». Это поможет ловить раньше.

Моё мнение — вариант **2**: hub-and-spoke сохраняется (developer = единственный, кто пишет в `agents/`, `skills/`, `CLAUDE.md`, `scripts/` и т. п.), но `session-reports/` + `memory/` от consumer'ов **должны** уходить в main, потому что эти материалы — основа аналитической работы пользователя, ради которой вся sync и придумана. Иначе теряем 80% пользы. Вариант 1 рискует тем, что consumer перестаёт быть consumer'ом — и начнёт писать в `agents/`/`skills/` race-condition'ы с DANIILPC.

## Что сделано (правильный путь — через feedback-репо)

**Архитектурное напоминание (которое я сначала упустил):** на consumer ПК `session-reports/` **не идут** в `claude-base/main`. Правильный путь — `scripts/feedback-collector.ps1` → отдельный репо `<логин>/claude-base-feedback`, ветка `feedback/<hostname>-<userprefix>`. Daniil с DANIILPC сам подхватывает оттуда и решает что внедрить в shared.

Алгоритм:

1. Копирую `report.md` из каждой папки `session-reports/<тема>/` в `~/.claude/feedback-pending/` с именем `report-<тема>.md`.
2. Запускаю `scripts/feedback-collector.ps1` — он добавляет frontmatter, перемещает в `feedback-staging/`, push'ит через GitHub API в `claude-base-feedback`, перемещает запушенные в `feedback-staging/pushed/`.
3. Локальные `session-reports/` остаются на диске untracked — это journal сотрудника, в main они не идут.

## Update — моя ошибка с push в main и revert

В первой версии этого отчёта я предложил ручной `git add session-reports/ && git push origin main`. **Это было неправильно** — нарушение hub-and-spoke. Я выполнил эту команду и запушил коммит `3cc61b9` в `claude-base/main` с 12 файлами (6 session-reports). Пользователь остановил.

Откат:

```powershell
cd $HOME\.claude
git revert 3cc61b9 --no-edit                # → коммит 361020a (delete 12 files)
git -c http.proxy="" -c https.proxy="" push origin main
# 3cc61b9..361020a  main -> main
```

Другие consumer-ПК через `auto-pull` подхватят revert безболезненно (fast-forward, без конфликтов).

Локально файлы после revert исчезли с диска (revert add-only = delete in working tree). Перед revert'ом — backup в `$env:TEMP\sr-backup-<timestamp>\`. После revert'а скопировал обратно в `session-reports/`, они снова стали untracked, как было до моей ошибки.

**Почему ошибка важна:** первая ловушка — «hook DONE без push» (см. выше) маскирует проблему накопления. Я попался во **вторую** — «push в main выглядит решением, но это нарушение архитектуры». Две ловушки сложились в один кейс: первая мотивирует на действие, вторая ловит на неправильном действии.

Правильный flow я понял только когда прочитал `scripts/feedback-collector.ps1` целиком. **Урок:** перед `git push origin main` от имени consumer-ПК — сначала проверить, есть ли feedback-механизм. Если есть — использовать его. Push в main с consumer-ПК — почти всегда ошибка.

## Артефакты

- Этот отчёт: `~/.claude/session-reports/2026-05-26_auto-push-stuck-consumer-mode/report.md`
- Скрипт-источник, к которому относится разбор: `~/.claude/scripts/auto-push.ps1` строки 115–132 (consumer-mode branch).
- Лог, по которому видна работа hook: `~/.claude/auto-sync.log` (записи с тегом `auto-push: consumer mode`, `feedback-collector`, `DONE (consumer)`).

## Открытые вопросы

- Решение по варианту 1/2/3/4 (см. выше) — на пользователе. Стоит зафиксировать как ADR в `memory/` или в `CHANGELOG.md`.
- Стоит ли в первой реплике сессии добавлять warning о застрявших untracked session-reports (по аналогии с warning о прерванном auto-sync, который уже есть в auto-pull/auto-push)? — Простое улучшение, поможет ловить такой класс проблем сразу.
- PAT в `feedback-config.json` хранится в открытом виде. По дефолту gitignored, но рискованно — если кто-то по ошибке закоммитит — токен утечёт. Стоит подумать про DPAPI / Windows Credential Manager.

## Lesson

«Hook завершается DONE» **не равно** «работа сделана». Consumer-mode hook логирует DONE даже когда умышленно ничего не делает с push'ем. Симптом наружу не виден до тех пор, пока кто-то явно не посмотрит в `git status`. Это классическая ловушка ложного успеха — как и `auditor` отвечающий «всё ок» без проверки.
