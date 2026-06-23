# skills.sh — анализ + совместимость с claude-base (2026-05-20)

## A. Что это технически

**skills.sh** = «The Open Agent Skills Ecosystem», публичный реестр + CLI для
дистрибуции AI-skills между ~55 агентами (Claude Code, Cursor, Copilot,
Windsurf, Gemini, Cline, VS Code, Codex и др.).

- **Издатель:** Vercel Labs. Репо `github.com/vercel-labs/skills`,
  TypeScript, MIT, 19.5k stars, активен (v1.5.7 от 2026-05-14), 401k
  суммарных установок по leaderboard.
- **Transport:** `npx skills add <owner/repo>` — клонирует **прямо**
  с GitHub/GitLab/любого git URL/локального пути. **Центрального
  registry-API нет** — skills.sh это просто витрина-leaderboard поверх
  GitHub. Поиск, статистика установок, теги — на сайте; сама
  установка идёт мимо реестра, напрямую из репо.
- **Install location для Claude Code:** `~/.claude/skills/<name>/` (global)
  или `.claude/skills/<name>/` (project). **Совпадает с нашим путём
  один-в-один.**
- **Private repos:** официально не поддерживаются, см. issue #381
  ([Feature: private skills](https://github.com/vercel-labs/skills/issues/381)).
- **Telemetry:** включена по умолчанию, `DISABLE_TELEMETRY=1` отключает.

## B. Формат skill manifest

**Они используют тот же формат, что и мы.** Vercel-labs/skills следует
официальной [Anthropic Skills spec](https://code.claude.com/docs/en/skills) —
никакого собственного manifest-формата они не вводили, это надстройка
поверх стандарта.

| Поле | skills.sh / Anthropic spec | Наш `stroy-formatting` | Совпадение |
|------|---------------------------|------------------------|-----------|
| `name` | required, lowercase + hyphens, ≤64 | `stroy-formatting` | ✓ |
| `description` | recommended, ≤1536 chars, содержит триггеры | многострочное с триггерами | ✓ |
| `allowed-tools` | optional, space/YAML list | `Read, Write, Edit, Bash, AskUserQuestion, mcp__word__*` | ✓ |
| `when_to_use` | optional, дополнение к description | у нас встроено в description и H2-секции | ≈ (можно вынести) |
| `disable-model-invocation`, `user-invocable`, `argument-hint`, `model`, `effort`, `context: fork`, `agent`, `paths`, `shell`, `hooks` | optional | не используем | — |
| Body | markdown под frontmatter | markdown под frontmatter | ✓ |
| Папка | `<name>/SKILL.md` + опц. `scripts/`, `reference.md`, `examples.md` | `<name>/SKILL.md` + у нас `formatting-templates/` рядом, не внутри | ⚠ |

**Разница ровно одна и она важная:** наши **dependencies** (шаблоны
`*.docx`, скрипты) лежат **снаружи** папки skill — в
`~/.claude/formatting-templates/`. По skills.sh-конвенции они должны
быть **внутри** `<skill>/` (например `<skill>/templates/*.docx`),
иначе `npx skills add` не утащит их вместе со SKILL.md.

## C. Migration cost для `stroy-formatting`

Минимальные правки чтобы skill стал публикабельным:

1. **Переместить шаблоны внутрь skill:**
   `~/.claude/formatting-templates/*.docx` →
   `~/.claude/skills/stroy-formatting/templates/*.docx`
   (~4 файла, ~200 KB).
2. **Обновить пути в SKILL.md:** строка 44 и `src = Path.home() / ".claude" / "formatting-templates"`
   → `src = Path(os.environ["CLAUDE_SKILL_DIR"]) / "templates"`
   (использовать встроенный `${CLAUDE_SKILL_DIR}` substitution).
3. **README.md на корне skill** для витрины skills.sh (1 страница: что
   делает, как вызвать, screenshot).
4. **LICENSE** в репо публикации (MIT/Apache-2.0).
5. **python-docx как dependency** — никаких изменений: skills.sh не
   управляет Python-зависимостями, пользователь сам ставит. Достаточно
   `requirements.txt` рядом со SKILL.md (как у earthtojake/text-to-cad).

Реальная оценка: 30-60 минут на skill. **Самая большая работа — не
техническая, а локализация:** SKILL.md на русском и про ГОСТ — это
сужает аудиторию до ~0 для глобального registry. Чтобы стало
осмысленно — English + универсализация ссылок на ГОСТ как «strict
academic style».

## D. Что публиковать можно / нельзя

| Skill | Публиковать? | Причина |
|-------|--------------|---------|
| `karpathy-guidelines` | ✅ да | Универсальные принципы, EN-перевод тривиален, ценно для всех |
| `chains-pattern` | ✅ да | Методология named chains, агностично к домену |
| `handoff-to-new-chat` | ✅ да | Универсальная техника mid-session handoff |
| `harvest` | ✅ да | Поиск инструментов на GitHub — generic dev workflow |
| `image-text-replace` | ✅ да | OCR + LaMa + SD — независимо от стройки |
| `pdf-helper`, `excel-helper`, `word-helper` | ⚠ возможно | Полезны, но многие части уже покрыты Anthropic-skills `pdf`/`xlsx`/`docx`. Conflict-risk. |
| `stroy-formatting` | ⚠ только в EN-варианте «academic-formatting» | ГОСТ-узко; нужна абстракция |
| `cad-reader` | ⚠ возможно | <организация> nomenclature внутри; нужна очистка |
| `format` | ❌ нет | Тонкая обёртка над `stroy-formatting`, ничего не добавит |
| `spec-writer` | ❌ нет | Хардкод <организация> объектов («<объект-A>», «<объект-Б>») |
| `upd-parser` | ❌ нет | RU-specific УПД-формат + adapter из приватного s2-invoice |
| `yandex-disk-uploader` | ❌ нет | <организация> Яндекс.Диск + конкретные subfolder-routes (`02_Договор/`) |

**Итог:** из 12 skills осмысленно публиковать 4-5 (универсальные
поведенческие), 3-4 переписывать (убирать <организация>), 3 оставить приватно.

## E. Альтернативные registries

| Registry | Transport | Формат | Зрелость | Privacy |
|----------|-----------|--------|----------|---------|
| **skills.sh** (Vercel) | `npx skills add` из git | SKILL.md (Anthropic spec) | 19.5k★, leaderboard работает | только public repos |
| **Anthropic plugins / marketplaces** | `/plugin` команда внутри Claude Code, manifest.json + skills/ | SKILL.md (тот же spec) | официально от Anthropic, наш `setup-extras` это уже использует | поддерживает private |
| **claude-base (наше)** | git clone + auto-pull/push hooks | SKILL.md (тот же spec) | работает между 2-3 ПК | private, full control |
| **GitHub topics + manual install** | `git clone` + `cp -r` | произвольный | без CLI | универсально |

Anthropic plugin-marketplace через manifest.json и `setup-extras.ps1`
уже встроен в `claude-base` и поддерживает приватность — это
**функционально перекрывает skills.sh** для наших нужд, плюс private.

## Recommendation

**Отложить публикацию на skills.sh, но подготовить почву.** Главная
причина: skills.sh не поддерживает private repos, а большая часть
наших skills <организация>-специфична. Доля кандидатов на public-релиз ~30%
(4 из 12), и для них требуется не просто migration, а локализация на
EN + обобщение. Это **отдельный полноценный проект**, не побочная
задача.

**Что делать прямо сейчас (low cost, high value):**
1. **Унифицировать структуру наших skills под Anthropic spec** —
   переместить `~/.claude/formatting-templates/` внутрь
   `stroy-formatting/templates/`. Это нужно **в любом случае**: для
   будущей публикации, для распространения через `setup-extras` (где
   skill теперь самодостаточная папка), для consistency.
2. **Использовать `${CLAUDE_SKILL_DIR}` substitution** вместо
   хардкода `~/.claude/...` — повышает портативность skills.
3. **Подключить find-skills (top skill skills.sh, 1.6M installs)
   через harvest** — `npx skills add vercel-labs/skills` ставит
   *find-skills*, который умеет искать в реестре. Дёшево попробовать
   как **потребитель** реестра, до того как становиться поставщиком.

**Когда вернуться к публикации:** когда (а) у нас будет 2-3 универсальных
skill, локализованных на EN, и (б) появится конкретный use-case
«поделиться с командой за пределами <организация>». До этого — приватный
`claude-base` + Anthropic plugin-механизм через manifest закрывают все
наши реальные потребности.

**Не блокер для текущей работы.** Архитектурно мы уже лежим в
правильном русле (тот же SKILL.md формат, тот же install path) — это
значит «миграция позже» бесплатна, а «не мигрировать» тоже валидно.

Sources:
- [vercel-labs/skills GitHub](https://github.com/vercel-labs/skills)
- [Anthropic Skills official spec](https://code.claude.com/docs/en/skills)
- [Vercel KB: Agent Skills creating/installing/sharing](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context)
- [Issue #381 — private skills support](https://github.com/vercel-labs/skills/issues/381)
- [earthtojake/text-to-cad (cadskills.xyz)](https://github.com/earthtojake/text-to-cad)
