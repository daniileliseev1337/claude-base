---
created: 2026-05-20
status: backlog
priority: low
trigger: «появилась потребность регрессионно тестировать вывод LLM-агента (designer, word-checker, auditor и т.п.) на эталонных промптах»
related:
  - [[karpathy-guidelines]]
  - [[chains-pattern]]
  - [[project_designer_decomposition]]
tags: [backlog, tests, promptfoo, LLM]
---

# Backlog: promptfoo для семантических тестов LLM-агентов

## Контекст

Источник идеи — аудит чужой базы Claude Code «К-7 (агенты)» от 2026-05-20
(см. отчёт `~/Desktop/K-7_audit_report.docx`, раздел 4.4). У них
promptfoo использован для regression-тестов LLM-вызовов через
Anthropic API: golden-set с эталонными prompt/response парами,
ассерты на структуру вывода.

В нашу базу как **первый этап** (Фаза 3) внедрён pytest для
детерминированных функций (см. `~/.claude/evals/`). Это покрывает
функциональное ядро скиллов (image-text-replace и подобные).

**promptfoo** же нужен для другого класса задач — тестирования
**семантики** ответов LLM-агентов. Откладывается, потому что:

- Требует Anthropic API key — оплачиваемый (отдельно от Claude Code
  subscription).
- Требует тестовых эталонов (готовых нет, нужно собирать
  репрезентативную выборку).
- Каждый LLM-call в тесте — несколько секунд, дорого для CI.
- Сейчас у нас нет LLM-агентов уровня сложности К-7 (s3-lawyer
  и т.п.), которые требуют такого тестирования.

## Когда триггер сработает

Включаем promptfoo если выполнено **хотя бы одно**:

1. Активирован `chain:project-doc-pack` с реальным
   stage-decomposition `designer` (см. [[project_designer_decomposition]])
   — появятся изолированные LLM-функции Stage 3, которые имеет
   смысл тестировать на эталонах.
2. У нас 3+ доменных LLM-агентов (помимо designer) с измеряемым
   качеством вывода (где «хорошо/плохо» можно formal-задать через
   assert на структуру).
3. После регрессии — один из агентов начал выдавать заметно худший
   результат, нужны эталоны чтобы поймать раньше.
4. Появилась потребность сравнивать модели (Opus vs Sonnet vs Haiku)
   на наших промптах — это родная задача promptfoo.

## Что делать когда триггер сработает

1. **Установка:**
   ```powershell
   npm install -g promptfoo
   # либо через pip:
   python -m pip install --user promptfoo
   ```

2. **Структура:**
   ```
   ~/.claude/evals/
   ├── promptfooconfig.yaml       ← основной конфиг (provider, defaults)
   ├── goldens/
   │   ├── designer-vent.yaml     ← эталоны для designer (вентиляция)
   │   ├── designer-electrical.yaml
   │   └── word-checker.yaml
   └── prompts/
       └── designer-v1.md          ← версии промптов для A/B
   ```

3. **Anthropic API key** — получить отдельный read-only ключ,
   положить в `~/.claude/.anthropic-api-key` (gitignored), не в
   `~/.claude.json` основного Claude Code subscription.

4. **CI integration** — пока ручной запуск. Если станет регулярным
   — добавить в SessionEnd hook (опционально).

## Анти-паттерны

- **Не создавать** golden-set «на будущее» из 50 кейсов. Стартовать
  с 5-7 ключевых и расти по факту регрессий (Karpathy §2).
- **Не дублировать** функциональные тесты pytest в promptfoo —
  только семантика LLM, не математика расчётов.
- **Не запускать** promptfoo в auto-sync hooks — дорого и медленно.

## Связанные

- `~/.claude/evals/README.md` — общий entry point для тестов
- `~/.claude/evals/test_image_text_replace.py` — текущий pytest-набор
- К-7 отчёт `~/Desktop/K-7_audit_report.docx`, раздел 4.4

## История

- 2026-05-20 — создан backlog по результату аудита К-7 и решения
  пользователя «гибрид: pytest сейчас, promptfoo в backlog».
