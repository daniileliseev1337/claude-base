# facts-layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить в claude-base лёгкий механизм «единый источник правды по проекту» — `FACTS.md` (ключ→значение→источник), который доменные агенты читают первым.

**Architecture:** Новый skill `facts-layer` (методология + шаблон) + одна строка-триггер в CLAUDE.md + одна строка-напоминание в `agents/_TEMPLATE.md`. FACTS.md живёт в папке проекта (или `_meta/` при structured-artifacts), НЕ в `~/.claude/`. Композируется с structured-artifacts и domain-grilling.

**Tech Stack:** Markdown (методология-артефакты, не код). Проверки — PowerShell (`Test-Path`, Select-String) + ручной smoke-эвал.

**Spec:** `docs/superpowers/specs/2026-06-02-facts-layer-design.md`

**Ограничение:** CLAUDE.md только что де-водизирован — добавлять РОВНО одну строку, не секцию.

---

### Task 1: Шаблон FACTS.template.md

**Files:**
- Create: `skills/facts-layer/references/FACTS.template.md`

- [ ] **Step 1: Создать файл шаблона**

Содержимое файла целиком:

```markdown
---
project: <название объекта>
last_updated: <YYYY-MM-DD>
---

# FACTS — единый источник правды по проекту

> Только ДАННЫЕ (факты). НЕ инструкции (это CLAUDE.md), НЕ решения-почему
> (это _meta/DECISIONS.md), НЕ межпроектные уроки (это auto-memory).
> Правишь факт — правишь ТОЛЬКО здесь. Каждый агент читает этот файл первым.
> Каждый факт обязан иметь Источник (трассировка, перепроверяемость).

## Объект
| Факт | Значение | Источник |
|---|---|---|
| Шифр | <напр. <шифр-чертежа>-06-01> | <ТЗ п.X / решение пользователя ДД.ММ.ГГГГ> |
| Объект | <название> | <ТЗ> |
| Адрес | <адрес> | <ТЗ> |

## Заказчик
| Факт | Значение | Источник |
|---|---|---|
| Заказчик | <ООО ...> | <договор / ТЗ> |

## Технические
| Факт | Значение | Источник |
|---|---|---|
| Нагрузка ОВ | <напр. 48 кВт> | <расчёт designer ДД.ММ.ГГГГ> |
| Отметка 0.000 | <напр. +145.20> | <ГП / АР> |

## Цены
| Факт | Значение | Источник |
|---|---|---|
| Цена <позиция> | <320 ₽/шт> | <КП поставщика №N> |

## Даты
| Факт | Значение | Источник |
|---|---|---|
| Срок сдачи РД | <ДД.ММ.ГГГГ> | <график / договор> |

<!-- Категории — по факту проекта, не наперёд. Лишние удалить, недостающие добавить. -->
<!-- Источник «вычислено: <агент> по <входам>» — для производных фактов. -->
```

- [ ] **Step 2: Проверить файл**

Run:
```powershell
$f = "$HOME\.claude\skills\facts-layer\references\FACTS.template.md"
Test-Path $f
(Select-String -Path $f -Pattern '^\| Факт \| Значение \| Источник \|' -AllMatches).Count
Select-String -Path $f -Pattern 'last_updated|## Объект|## Технические|## Цены' | Measure-Object | % Count
```
Expected: `True`; счёт заголовков таблиц `≥3`; счёт ключевых секций `≥4`.

- [ ] **Step 3: Commit**

```powershell
git -C "$HOME\.claude" add skills/facts-layer/references/FACTS.template.md
git -C "$HOME\.claude" commit -m "facts-layer: шаблон FACTS.template.md"
```

---

### Task 2: Skill facts-layer/SKILL.md

**Files:**
- Create: `skills/facts-layer/SKILL.md`

- [ ] **Step 1: Создать SKILL.md**

Содержимое целиком:

```markdown
---
name: facts-layer
description: |
  Единый источник правды по проекту — FACTS.md (ключ→значение→источник).
  Только ДАННЫЕ проекта (шифр, цены, нагрузки, отметки, даты, заказчик), не
  инструкции и не решения. Каждый доменный агент читает FACTS.md первым; факт
  правится в одном месте. Закрывает рассинхрон фактов между агентами/артефактами.

  Триггеры:
  - «новый проект», «начинаем объект», «соберём факты», «единый источник правды»
  - «facts.md», «файл фактов», «куда положить цифры/цену/нагрузку»
  - перед спецификацией / ВОР / КП / сметой — собрать факты проекта
  - факт встречается в нескольких артефактах и расходится
---

# facts-layer — единый источник правды по проекту

## Зачем
Факты проекта (шифр, цена, нагрузки, отметки, даты) размазаны по спецификации/
КП/смете/промптам → поменял в одном, забыл в трёх → противоречия. FACTS.md
держит их в одном месте, каждый агент читает первым, правка — только там.

## Границы (НЕ помойка)
| FACTS.md | CLAUDE.md | _meta/DECISIONS.md | auto-memory |
|---|---|---|---|
| данные проекта | инструкции «как работать» | решения «почему» | межпроектные уроки |
Свалишь одно в другое — получишь помойку. FACTS.md = ТОЛЬКО факты.

## Где живёт
`<project-cwd>/FACTS.md`. Если активны structured-artifacts — `<project-cwd>/_meta/FACTS.md`
(6-й артефакт). НЕ в `~/.claude/` (это данные проекта, не методбаза).

## Формат
Шаблон — `references/FACTS.template.md`. Frontmatter (`project`, `last_updated`) +
таблицы по категориям, строка = `Факт | Значение | Источник`. Источник обязателен
(ТЗ п.X / ГОСТ / КП №N / «решение пользователя ДД.ММ.ГГГГ» / «вычислено: <агент> по <входам>»).

## Как наполнять (старт проекта)
1. Подключить `domain-grilling` — допросить пользователя по фактам объекта.
2. Скопировать шаблон, заполнить значениями + источниками.
3. Чего нет — спросить (karpathy #1), НЕ выдумывать.

## Read-first (главное правило)
- Любая доменная задача/агент — читает FACTS.md ПЕРВЫМ (целиком, он мал).
- Оркестратор при спавне агента дублирует в промпте: «сначала прочитай FACTS.md <путь>».
- Производный факт (вычислил агент) — append со `Источник = вычислено: <агент> по <входам>`.

## Change-handling
- Факт поменялся → правка в ОДНОМ месте (значение + источник + `last_updated`).
- Все агенты подтянут новое при следующем чтении.
- Конфликт FACTS vs готовый артефакт → FACTS приоритетен (он SoT), артефакт правится.

## Отложено (не в этом скилле)
- Колонка `Consumers` (impact-map: что перегнать при смене факта) — пока решение у человека.
- Программный reader (facts.yaml) — если факты станут строго структурными.

## Композиция
- `structured-artifacts` — FACTS.md встаёт 6-м файлом в `_meta/` на крупных задачах.
- `domain-grilling` — первичное наполнение.
- `chains-pattern` — chain может начинаться с «заполни FACTS.md».
```

- [ ] **Step 2: Проверить SKILL.md**

Run:
```powershell
$f = "$HOME\.claude\skills\facts-layer\SKILL.md"
Test-Path $f
Select-String -Path $f -Pattern 'name: facts-layer|Триггеры|Границы|Read-first|Change-handling' | Measure-Object | % Count
```
Expected: `True`; счёт `≥5`.

- [ ] **Step 3: Commit**

```powershell
git -C "$HOME\.claude" add skills/facts-layer/SKILL.md
git -C "$HOME\.claude" commit -m "facts-layer: SKILL.md (методология + границы + read-first)"
```

---

### Task 3: CLAUDE.md — ОДНА строка-триггер

**Files:**
- Modify: `CLAUDE.md` (секция «Универсальные правила работы», после правила 8)

- [ ] **Step 1: Прочитать текущее правило 8 как якорь**

Run:
```powershell
Select-String -Path "$HOME\.claude\CLAUDE.md" -Pattern '8\. \*\*Оформление деловых'
```
Expected: одна строка (правило 8).

- [ ] **Step 2: Добавить правило 9 (ровно одна строка) через Edit-tool**

Вставить ПОСЛЕ строки правила 8, ОДНУ строку:

```
9. **Факты проекта — в `FACTS.md`.** Есть `FACTS.md` в папке проекта → читать первым; факты (шифр/цены/нагрузки/даты) править только там. Детали — skill `facts-layer`.
```

(НЕ создавать новую секцию. Одна нумерованная строка в существующем списке.)

- [ ] **Step 3: Проверить — добавлена 1 строка, файл чист и мал**

Run:
```powershell
$h = "$HOME\.claude"
Select-String -Path "$h\CLAUDE.md" -Pattern 'Факты проекта — в' | Measure-Object | % Count
# Кодировка не сломана:
$u=New-Object System.Text.UTF8Encoding($false,$true);$c=[System.Text.Encoding]::GetEncoding(1251,[System.Text.EncoderFallback]::ExceptionFallback,[System.Text.DecoderFallback]::ExceptionFallback)
$t=[IO.File]::ReadAllText("$h\CLAUDE.md",[Text.Encoding]::UTF8);$m=0;foreach($l in ($t -split "`n")){if($l.Trim().Length-eq0){continue};try{$b=$c.GetBytes($l);$f=$u.GetString($b);if($f-ne$l){$m++}}catch{}}
"mojibake: $m (ожид 0)"
"строк в CLAUDE.md: $((Get-Content "$h\CLAUDE.md").Count) (ожид ~113)"
```
Expected: счёт `1`; mojibake `0`; строк `~113` (было 111 + ~2).

- [ ] **Step 4: Commit**

```powershell
git -C "$HOME\.claude" add CLAUDE.md
git -C "$HOME\.claude" commit -m "CLAUDE.md: правило 9 — факты проекта в FACTS.md (1 строка)"
```

---

### Task 4: agents/_TEMPLATE.md — строка-напоминание

**Files:**
- Modify: `agents/_TEMPLATE.md`

- [ ] **Step 1: Найти раздел инструкций/процедуры в шаблоне**

Run:
```powershell
$f = "$HOME\.claude\agents\_TEMPLATE.md"
Test-Path $f
Select-String -Path $f -Pattern '^#|Процедура|Инструкции|Workflow|Шаги' | Select-Object -First 8 LineNumber, Line
```
Expected: список заголовков шаблона (для выбора места вставки).

- [ ] **Step 2: Добавить ОДНУ строку-напоминание через Edit-tool**

В начало рабочей процедуры агента (или в раздел «перед работой») добавить:

```
- **Сначала FACTS.md.** Если в папке проекта есть `FACTS.md` — прочитать его первым; факты брать оттуда, не выдумывать (skill `facts-layer`).
```

- [ ] **Step 3: Проверить**

Run:
```powershell
Select-String -Path "$HOME\.claude\agents\_TEMPLATE.md" -Pattern 'Сначала FACTS.md' | Measure-Object | % Count
```
Expected: `1`.

- [ ] **Step 4: Commit**

```powershell
git -C "$HOME\.claude" add agents/_TEMPLATE.md
git -C "$HOME\.claude" commit -m "agents/_TEMPLATE: напоминание читать FACTS.md первым"
```

---

### Task 5: Smoke-эвал (критерий успеха из spec)

**Files:**
- Create (временно): `$HOME\.claude\_sandbox\facts-eval\FACTS.md`

- [ ] **Step 1: Создать тестовый FACTS.md с фактом, нужным 3 «агентам»**

```powershell
$d = "$HOME\.claude\_sandbox\facts-eval"; New-Item -ItemType Directory -Force $d | Out-Null
@'
---
project: ЭВАЛ
last_updated: 2026-06-02
---
## Цены
| Факт | Значение | Источник |
|---|---|---|
| Цена ВУ-1 | 320 ₽/шт | КП №45 |
'@ | Set-Content "$d\FACTS.md" -Encoding utf8
```

- [ ] **Step 2: Сменить факт в ОДНОМ месте, проверить что новое значение единственное**

```powershell
$p = "$HOME\.claude\_sandbox\facts-eval\FACTS.md"
(Get-Content $p -Raw) -replace '320 ₽/шт','450 ₽/шт' | Set-Content $p -Encoding utf8
# Проверка: старого значения нет, новое есть (= источник правды один)
"старое 320: $((Select-String -Path $p -Pattern '320').Count) (ожид 0)"
"новое 450: $((Select-String -Path $p -Pattern '450').Count) (ожид 1)"
```
Expected: старое `0`, новое `1`. (Подтверждает: факт в одном месте, смена не оставляет рассинхрона.)

- [ ] **Step 3: Очистить sandbox**

```powershell
Remove-Item "$HOME\.claude\_sandbox\facts-eval" -Recurse -Force
```

- [ ] **Step 4: Финальный push**

```powershell
git -C "$HOME\.claude" -c http.proxy="" -c https.proxy="" pull --rebase --autostash origin main
git -C "$HOME\.claude" -c http.proxy="" -c https.proxy="" push origin main
```

---

## Self-review

- **Spec coverage:** Шаблон (T1) ✓, skill+границы+read-first+change (T2) ✓, CLAUDE.md 1 строка (T3) ✓, _TEMPLATE напоминание (T4) ✓, критерий успеха/эвал (T5) ✓. Отложенное (#7, reader) — явно НЕ реализуется, помечено. Покрытие полное.
- **Placeholders:** в артефактах `<...>` — это намеренные плейсхолдеры ШАБЛОНА (FACTS.template), не дыры плана. Контент каждого артефакта дан целиком.
- **Type/имена-консистентность:** `FACTS.md`, `facts-layer`, `references/FACTS.template.md` — едины во всех задачах. CLAUDE.md = правило 9 (после 8). Источник-колонка везе одинакова.