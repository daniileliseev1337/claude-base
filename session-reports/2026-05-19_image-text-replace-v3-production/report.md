# Session report — 2026-05-19 — image-text-replace v3.0 production + scan-aware PDF routing

**Host:** DANIILPC (ноутбук, Даниил)
**Дни:** 2026-05-19 (~10 часов)
**Предыдущий:** `2026-05-15_handoff-manifest-extras-installer-stage8/report.md`

## Контекст

После handoff infra-сессии — реальная production задача: добавить «20%»
к строке «Итоговая сумма (вкл. НДС)» в КП К7 АХП от 07.05.26
(финансовый scan-PDF, 4 страницы). Нужен production инструмент чтобы
команда могла делать такое regularly.

## Хронология (вехи)

1. Harvest: PaddleOCR + IOPaint LaMa + Pillow stack. Adobe Firefly MCP
   отклонён (нет remove-text-from-photo). Inspired by Appt-OCR.
2. PaddleOCR 3.x → EasyOCR (baidu CDN недоступен на корп-сети).
3. v0.1-v0.4: базовая реализация, bug fixes (Unicode paths, render_text
   sampling).
4. **4 heavy options:** PSF estimation (v0.5), Borrow glyphs (v0.6),
   Diffusion design doc, Neural CNN design doc. Bonus: pixel anchor
   (v0.7), texture residual (v0.8), histogram match (v0.9).
5. **v0.5-v2.2: 13 итераций впустую** — tuning Arial Regular когда
   реальный шрифт скана был Times Bold.
6. **A14 Font calibration sheet → revelation:** scan = Times Bold.
   v2.3 = Times Bold + smart_cap + cell-ref sampling.
7. **v3.0 final:** + SD img2img strength=0.10 финальная полировка.
   User: «именно то чего мы хотели, отличный результат с первого раза».
8. Production integration: refactor pipeline.py (full stack as
   first-class API), calibration.py CLI tool, SKILL.md переписан,
   LESSONS-LEARNED.md написан, mcp-manifest.json + diffusers/etc.
9. DELISEEV-PC выявил несостыковку: CLAUDE.md обещал pdf-edit, но
   скрипт только на <логин>-PC. User: «pdf-edit нам не нужен» →
   cleanup из всех актуальных файлов.
10. setup-extras Step 4: auto-download LaMa + EasyOCR + SD. Token
    architecture: `.hf-token` per-PC (gitignored). 3 уровня
    notification про контакт Даниила (Deliseev@<домен-организации>).
11. pdf-helper SKILL.md: scan-detection как обязательный first step
    + routing на image-text-replace OCR. image-text-replace SKILL.md:
    OCR primary, text replace secondary.
12. **Профанити toggle** per-PC opt-in: `.profanity-marker` (gitignored),
    Claude спрашивает один раз через AskUserQuestion при отсутствии.

## Источники

**MCP:** pdf-mcp (render для visual comparison), fetch (GitHub API
для inspect <логин> commits).

**Skills:** karpathy-guidelines (активно — push back на blind iteration,
push back на token в public repo, recognition что font calibration
важнее render tuning).

**Python:** easyocr 1.7.2, iopaint 1.6.0 + LaMa 174 MB, diffusers +
transformers + accelerate + safetensors + torch 2.12, pypdfium2,
pdfplumber, Pillow, opencv-python, numpy.

**SD model:** `runwayml/stable-diffusion-inpainting` (5.4 GB) через
`huggingface_hub.snapshot_download` с HF token. SD-2-inpainting 404.

**Harvest:** Appt-OCR (architecture), IOPaint, runwayml/SD-inpaint.

## Артефакты (commits в claude-base сегодня)

| Commit | Что |
|--------|-----|
| `9dd8d9d` | v0.4 fix position+weight |
| `4d59d2e` | v0.5 PSF estimation (Option 3) |
| `ba8c9cc` | v0.6 Borrow glyphs (Option 4) |
| `a86ff6f` | v0.7 pixel anchor (A4) |
| `ac6f9f8` | v0.8 texture residual (B2) |
| `d5feff3` | ROADMAP-heavy-options.md |
| `ab652d0` | v0.9 histogram match |
| `c0f592c` | v1.0 darker color + softer hist |
| `927a080` | v1.2 vertical nudge |
| `6558ad1` | v2.3 Times Bold (BREAKTHROUGH) |
| `a07e131` | v3.0 + LESSONS-LEARNED |
| `dda4617` | Production integration: full stack + calibration.py |
| `2a4b277` | Reconcile CLAUDE.md MCP standard (adeu→manifest) |
| `636ec93` | Remove pdf-edit references |
| `1efb863` | Auto-download LaMa+EasyOCR+SD |
| `bbc35c7` | Scan-detection в pdf-helper |
| `9c6f668` | Contact-info для HF token |
| `f9b6137` | Email fix + profanity toggle |

**Final result:** `Desktop\КП К7 АХП от 07.05.26 (+20%) v30-SD.pdf`
— production-ready, принят user'ом.

## Установлено в системе (DANIILPC)

- Python 3.12.10 (был)
- pip --user: easyocr, iopaint, diffusers, transformers, accelerate,
  safetensors, torch 2.12
- Models:
  - LaMa 196 MB → `C:\iopaint-cache\torch\hub\checkpoints\big-lama.pt`
  - EasyOCR Russian ~100 MB → `~/.EasyOCR/model/`
  - SD-1.5-inpaint ~5.4 GB → `C:\sd-cache\models--runwayml--stable-diffusion-inpainting\`
- `.hf-token` → `~/.claude/.hf-token` (gitignored)
- `.profanity-marker` = `enabled` → `~/.claude/.profanity-marker` (gitignored)

## Главный мета-урок — Font calibration first

8 итераций потеряны на tuning Arial когда scan font был Times Bold.
Font calibration sheet (render same string в 12 шрифтах рядом со
сканом) был бы **обязательным первым шагом** — нашёл бы правильный
шрифт за 30 sec. Записан в LESSONS-LEARNED.md.

## Итерации, ошибки

- **Blind iteration анти-паттерн:** реактивные фиксы по одному
  параметру без понимания что user видит. Решение: ASK first (font /
  size / weight / color / position / sharpness — что конкретно не так).
- **Histogram match overshoot:** strength 0.85 hollow, 0.4 ok, 0.25
  preserves dark cores.
- **Cyrillic+PowerShell traps:** cv2.imread не читает Unicode, TORCH_HOME
  на Cyrillic ломается, HF_HOME=C:\sd-cache обязательно.
- **<логин> pdf-edit drift:** CLAUDE.md → manifest → реальный код
  inconsistency недели две. Cleanup сделан.

## Что выдумывал

- В v0.X использовал PaddleOCR API без проверки 3.x changes
  (`use_angle_cls`, `show_log`) → поймал, switched to EasyOCR.
- В v1.4-v1.8 align по midline math корректно по pixel, но user всё
  равно видел misalignment. Корень был в font, не в math.

## Цитаты user'а (важные)

- «Прийдётся брать SD inpaint так как 1.0 текст уже больше похож» —
  переломный момент к Phase B.
- «Это именно то чего мы и хотели, отличный результат и с первого
  раза» — приёмка v3.0.
- «Нет нам не нужен этот PDF edit» — cleanup.
- «Нельзя ли как-то чтобы у пользователей появлялось сообщение что
  нужно написать мне (Даниил)» — гениальное решение HF distribution.
- «Я очень хочу ради поднятия настроения коллектива умеренно
  добавить русский мат» — opt-in feature.

## Открытые задачи на следующую сессию

1. **HF token rotation** — текущий в чат-логах, создать новый read-only.
2. **DELISEEV-PC SD setup** — у него нет .hf-token, нужно скопировать +
   запустить setup-extras для скачивания SD.
3. **Test profanity toggle** на чистом старте сессии (без
   .profanity-marker) — AskUserQuestion должен сработать автоматически.
4. **Test scan-detection routing** на реальном scan-PDF (не КП К7) для
   проверки generic применимости.
5. **Phase 2 CNN style transfer** — backlog до накопления dataset.

## Обезличивание

Public репо, обезличивание смягчено. **Есть:** hostnames, email
команды, GitHub аккаунты, имя файла КП К7. **Нет:** паролей, PAT,
ПДн, банковских реквизитов. HF token — в чат-логах (Issue для
rotation), но в коде/коммитах НЕТ.

## Метрика сессии

- 18 коммитов в claude-base
- 0 коммитов в claude-lite-instaler
- 2 ПК активно затронуты (DANIILPC + DELISEEV-PC параллельно)
- 16 итераций v0.1 → v3.0
- 34 task через TaskCreate
- 3 архитектурных push back
- 1 production result принят user'ом
- 2 новых файла в скилле: calibration.py, LESSONS-LEARNED.md
- 3 новых helper в pipeline.py: smart_cap_height_detect,
  find_neighbor_cell_reference, refine_text_region_with_diffusion
- Главное открытие: font calibration first

## Auto-sync

**Начало сессии:** auto-pull pulled `bbbee62..cb12d9b` от Daniil
рабочего ПК.

**В течение:** ~18 manual commits + один rebase. push'ил часто чтобы
не накапливать.

**Конец сессии (прогноз auto-push):**
- Working tree clean (всё уже push'нуто кроме этого session-report)
- SessionEnd auto-push увидит session-report → push'нёт
- В следующей сессии этот отчёт будет в auto-pull другим ПК
