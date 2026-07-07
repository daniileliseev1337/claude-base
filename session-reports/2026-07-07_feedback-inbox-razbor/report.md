# Сессия 2026-07-07: разбор feedback-inbox команды (28 отчётов)

Хаб DANIIL-LAPTOP, продолжение реворка базы (handoff 2026-07-07).

## Что сделано

1. STOP-процедура: MCP 11/11, agents 16/16, install-флаг есть (напомнено /sync-base).
2. Сверка auto-pull: 5 коммитов прошлой сессии на месте по содержанию, хэши сменились
   (rebase поверх auto-sync с consumer-ПК) — норма. **Auto-push прошлой сессии НЕ ушёл:
   main ahead origin/main на 5** — уйдёт при закрытии этой сессии.
3. pull-feedback сознательно НЕ гонялся: inbox курирован прошлой сессией (45→28),
   повторный pull мог вернуть вычищенное.
4. Фан-аут: 4 субагента claude-sonnet-5 прочитали все 28 файлов (батчи по машинам:
   8+7+5+8), вернули структурные выжимки (тип/суть/грабли/кандидат/приоритет).
5. Кросс-чек кандидатов с живой базой (grep/git log по skills, chains, memory,
   scripts, anti-patterns) — главный результат ниже.
6. **Вскрыт и починен инцидент auto-push** (вопрос владельца «почему опять не
   работает»): с 02.07 гейт эфемерных сессий скипал ВСЕ настоящие SessionEnd.
   Корень (подтверждён зондом hook-probe.jsonl): stdin хука читался без UTF-8
   InputEncoding → PS 5.1 декодировал OEM → кириллица в transcript_path
   («Даниил») превращалась в мусор → Test-Path не находил транскрипт → ветка
   «нет файла = эфемерная» глушила пуш. SIM-тесты 02.07 не поймали: пути ASCII.
   Фикс: UTF-8 stdin по эталону log-tool-usage.ps1 (Блок 2) в auto-push И
   auto-pull (зонд) + fail-open на отсутствующем транскрипте (по
   задекларированному в скрипте намерению). Диф CLAUDE.md:134 применён по «ок»
   владельца (SessionStart += project-memory/session_start, новая строка Stop).

## Главный вывод

**Механизм feedback→main работает.** 15+ уроков из этих отчётов УЖЕ мигрированы в базу,
часто с прямой ссылкой на исходный feedback (пример: wedge-детект в auto-pull.ps1:88
цитирует «feedback infra 2026-06-08»; excel-helper п.15 — «Источник: feedback
vendor-logo-inserter»). Живых кандидатов ~12, решения за владельцем (таблица в чате).

## Уже мигрировано (проверено фактом в базе)

chains/upd-to-spec-reconcile (22.06) · wedge-детект auto-pull (строки 88–98) ·
skills/pd-tep-extractor (23.06) · excel-helper п.9 (token-лимит MCP read), п.10
(apply_formula + RU-запятая), п.15 (drawings+ZIP-разведка), п.16 (delete_rows на merged),
SUM-диапазоны, donor-pattern · memory/feedback_manual_procedure_verbatim (перенос процедур
дословно) · фикс инструментов ревьюеров/designer (MAJOR-блок аудита 23.06 — word-checker
получил word-MCP, auditor Bash+MCP, designer Bash) · doc-extract (CID/PScript → рендер) ·
anti-patterns A1.5 (игнорирование запрета) и A3.5 (apply_redactions) · chains/
design-stamp-corrections со Stage 6 donor-fix (26.05) · reference_pyrevit
(RenameWorkset static) · reference_av_multimedia · consumer session-reports → закрыто
самой архитектурой feedback-collector→inbox.

## Живые кандидаты (ждут решения владельца, детали в чате сессии)

1. verify_document_entry.py — контрольная сумма первички → upd-parser/tools (CRITICAL).
2. pdf-stamp-pipeline: pikepdf collapse→Form XObject + pdfcpu overlay + PyMuPDF
   font-нормализация (230×) → секция в pdf-edit + pdfcpu в манифест + 4 hard-rules
   memory. ⚠ Конфликт формулировок с pdf-edit («surgery — тупик» писан про перекраску
   аннотаций) — разграничить кейсы при интеграции.
3. Анти-паттерн «частичная верификация батча + преждевременная подмена файла».
4. VOR↔СО: линейный offset страница↔лист + двухпроходный матчинг марок → co-verify.
5. graphify: паттерн «детерминированный экстрактор → graph.json» (Слой 2).
6. Ловушки word-MCP пачкой → word-helper (add_heading color, Letter-дефолт,
   insert_paragraph_before, дубликат insert_header, грep кириллица/латиница).
7. Мелочи excel-helper (read-back после позиционного маппинга, gen_py→Dispatch).
8. success-criteria как скилл — рекомендация НЕ брать (overlap karpathy §4 + grilling).
9. vendor-logo-inserter как скилл — рекомендация НЕ брать целиком (ядро уже в
   excel-helper; добрать протокол-скрипт + приоритет источников лого).
10. Микро: границы auditor на PDF>20МБ; СПДС-правило малого штампа; harvest после
    root cause; сплошной скан после LLM-экстракции списков.

## Отклонено

harvest-summary штампов 22.05 (опровергнут вторым заходом), мануал Eaton как артефакт,
КОК-карта, ценовой срез МГЭ, шаблон ФТ AV-музея (покрыт reference_av_multimedia).

## Повторяющиеся грабли (темы)

1. Ревьюеры-субагенты vs бинарники — 8 упоминаний в 28 файлах; закрыто фиксом 23.06,
   остался нюанс больших PDF.
2. openpyxl/excel-MCP: merged/формулы/drawings — все ипостаси уже в excel-helper.
3. Детерминированные контрольные суммы переизобретены трижды (НДС×1,22, Σ документа,
   сверка графа копейка-в-копейку) → кандидат №1.
4. Массовые батчи: верификация выборкой вместо полного множества → кандидат №3.
5. Две независимые линии PDF-штампов у одной машины → без консолидации (№2) третья
   сессия изобретёт заново.

## Уроки процесса

- Отчёты БЕЗ явной заявки на интеграцию содержали кандидатов не хуже явных skill-заявок
  (verify_document_entry, extractor→graphify) — курировать inbox чтением целиком.
- Выжимки консьюмерских memory-имён (feedback-*) не совпадают с хабовыми — сверять
  покрытие грепом по СОДЕРЖАНИЮ, не по именам файлов.

## Ждёт владельца (не начато)

- Решения по кандидатам 1–10 (чат).
- path-detector project-memory v1.1 — бэклог, не трогать.

## Закрыто решениями владельца в этой сессии

- Diff CLAUDE.md:134 «Хуки» + project-memory — «ок» получено, ПРИМЕНЁН.
- 4 ИНН-кейса + ФИО-стоп-словарь — «оставить как есть» (без изменений).
