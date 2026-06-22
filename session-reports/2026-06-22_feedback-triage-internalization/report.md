# Session report — разбор накопленного feedback и внедрение уроков в базу

**Дата:** 2026-06-22. **Тип:** развитие claude-base (хаб). **Обезличено.**

## Задача

Пользователь: проанализировать накопившиеся feedback-репорты команды, затем
проработать находки. Отдельно — починить `domain-grilling` (у пользователя «ни
разу не вызывался, хотя правили»). PDF-штамп-кластер исключён («остатки прошлого»).

## Что сделано

### 1. Анализ feedback (Workflow, 30 агентов, ~1.3M субагент-токенов)
`pull-feedback` → 29 содержательных репортов с 9 машин (+ ~17 smoke-test мусора,
1 репорт продублирован 6× из-за инфра-бага auto-push). Fan-out haiku-извлечение →
sonnet-синтез со сверкой с базой (что уже внедрено vs новое). Кластеры: MCP-изоляция
ревьюеров, openpyxl+merge, Excel batch, инфра git-sync, deterministic-vs-LLM,
УПД-реестры, Revit, harvest-дисциплина, ТЭП.

### 2. domain-grilling — починен (хук + выбор пользователя)
**Корень не в тексте скилла:** он был пассивной подсказкой, а роутинг-гейт CLAUDE.md
(OVERRIDE) уводил сразу в доменного агента; плюс `settings.json` — **генерируемый**
файл (merge-shared-settings затирал любую правку `hooks`). Правки текста скилла не
лечили механизм.
- Новый `scripts/grilling-detector.ps1` (UserPromptSubmit, ASCII-логика, fail-open),
  sidecar `triggers.txt`/`reminder.txt` (UTF-8 — обход кодировочной граблины PS 5.1).
- По требованию пользователя поведение: **не толкать в грилинг, а спрашивать** —
  хук напоминает оркестратору предложить выбор через AskUserQuestion.
- Хук прописан в `settings.shared.json` (→ merge → personal; переживает merge,
  попадает всем). CLAUDE.md: абзац «Грилинг-выбор (до роутинга)».
- Протестирован: позитив/негатив, кириллица читается верно.

### 3. Backlog внедрён
- **P1.1 (MCP-ревьюеры):** факт-проверка показала — `word/excel/pdf-reviewer`
  декларируют MCP корректно (сбои = холодный кэш uvx), а у **`auditor` не было
  office-MCP вовсе**. Добавил read-only word/excel/pdf MCP + Bash/python fallback +
  правило «непрочитанный бинарник = NOT PASSED». CLAUDE.md: общее правило anti-холодный-кэш.
- **excel-helper:** ловушки 15 (save() теряет drawings), 16 (delete_rows + вертик. merge
  с алгоритмом snapshot→unmerge→delete→bisect→remerge + set-сверка ключей),
  17 (SUM-диапазоны рвутся при вставке за концом блока).
- **auto-pull.ps1:** wedge-детект unmerged-маркеров до pull + громкое предупреждение
  (Bug-1). Синтаксис + regex проверены.
- **deterministic-vs-LLM:** правило в `reference_workflow_tool.md` + CLAUDE.md
  (offset-арифметика, find_tables, двухпроходный матчинг; кейс 421/491).
- **named chain `upd-to-spec-reconcile`** (5 инвариантов) + регистрация в README/named_chains;
  `scripts/verify_document_entry.py` (контрольная сумма документа) + правило в upd-parser
  (Σ позиций == Всего к оплате; НДС 22% с 2026 как cross-check).
- **Revit:** `reference_pyrevit_k7.md` — GetLeaders + визуальный контроль аннотаций
  (static-method урок там уже был). `feedback_manual_procedure_verbatim.md` (Eaton:
  дословный перенос процедур). `сметчик.md` — ценовой аудит больших спеков (прогноз
  замечаний экспертизы).
- **Skill-кандидаты:** создан `pd-tep-extractor` (ТЭП из ОПЗ с cite); vendor-logo →
  ловушка в excel-helper (не плодить скилл); success-criteria отклонён (дублирует
  domain-grilling + karpathy §4).

## Где сломался / находки
- **settings.json дважды откатывал мой UserPromptSubmit** — не стал долбить вслепую,
  нашёл причину: `merge-shared-settings.ps1` берёт весь объект `hooks` из
  `settings.shared.json` (он в `$SharedKeys`). Чинить надо shared, не personal.
- **На хабе периодический auto-sync** (коммит+push каждые ~2-3 мин) — правки уходят
  в `origin/main` автоматически; ручной коммит не нужен.

## Открыто (решение пользователя)
- **Bug-2 (consumer-push):** session-reports с consumer-ПК не уходят в main
  (hub-and-spoke by design). Варианты: раздать `.developer-marker` / расширить
  whitelist / warning. Архитектурный выбор — не внедрял молча.
- **feedback-inbox/all не чистил:** smoke-test и дубли k7-pyrevit — мусор источника;
  локальное удаление вернётся при pull-feedback, чистить надо в feedback-репо.

## Артефакты (всё в managed-путях, ушли auto-sync в main)
agents/auditor.md, agents/сметчик.md, CLAUDE.md, settings.shared.json,
scripts/{grilling-detector.ps1, auto-pull.ps1}, chains/upd-to-spec-reconcile.md,
skills/{domain-grilling/*, excel-helper, upd-parser/*, pd-tep-extractor},
memory/{reference_workflow_tool, named_chains, reference_pyrevit_k7, feedback_manual_procedure_verbatim}.

## Вторая половина сессии — идеи пользователя по развитию базы

1. **Правило выбора модели субагентов (CLAUDE.md «Токен-дисциплина»).** По боли пользователя
   (дешёвая модель на содержательной задаче галлюцинирует → каскад исправлений дороже экономии):
   модель субагента/Workflow/ревьюера теперь ВЫБИРАЕТ ПОЛЬЗОВАТЕЛЬ — вопрос через AskUserQuestion
   перед каждым спавном, рекомендация по умолчанию «планка вверх» (sonnet для содержательного и
   всех ревьюеров, haiku только для тупой экстракции). Группировка однотипных + fallback на sonnet
   в автономном режиме. Обновлена заметка feedback_subagent_model_economy.

2. **Мультибэкенд Claude+GLM+codex (личное, dev дома).** Изучены 4 источника (z.ai docs, 2 youtube,
   github). Факт: `ANTHROPIC_BASE_URL` глобальный — голым env «sonnet=GLM, opus=Opus» не сделать
   (issue #25146); нужен локальный роутер-прокси (claude-code-multirouter — per-agent тег в
   agents/*.md). Подготовлен HANDOFF на Desktop (НЕ в shared).

3. **OSINT-arsenal (личное + легальный сабсет в базу).** Workflow-каталог 250+ инструментов по 15
   кластерам (Desktop, не shared). В shared базу внедрён ЛЕГАЛЬНЫЙ сабсет: agents/auditor.md
   (due-diligence контрагента: ЕГРЮЛ/OpenSanctions/crt.sh/SecurityTrails/Hudson Rock + верификация
   подлинности документов ExifTool/FotoForensics/TinEye/AI-or-Not), memory/feedback_web_direct_access
   (dorking/Intelligence X/crt.sh/ExifTool), skills/id-tom-priemka (подлинность скана). Закрывает
   feedback_cert_sourcing_fabrication. Полный arsenal (вкл. offensive) — bootstrap-скрипты на Desktop
   для самостоятельного запуска (WSL на этом ноуте нет; установка системная, не из песочницы).

Личные артефакты (Desktop, вне shared): claude-multibackend-osint-handoff, osint-arsenal-catalog,
osint-bootstrap-{windows.ps1, kali.sh, README.md}.
