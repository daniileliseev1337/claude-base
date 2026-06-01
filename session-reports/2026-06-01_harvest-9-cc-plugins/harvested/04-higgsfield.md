# Higgsfield — higgsfield.ai/mcp

## Источник
- URL: https://higgsfield.ai/mcp
- Cloud сервис, не GitHub repo
- Прислал пользователь как «4-я позиция» подборки 9

## Метаданные
- Тип: Cloud SaaS + MCP интерфейс. **НЕ GitHub repo** (единственный в подборке
  9 кто ведёт на коммерческий сайт higgsfield.ai, не github.com).
- Pricing: **Credit-based** по их сайту, НО точные тарифы и наличие free tier
  **не подтверждены** — WebFetch на higgsfield.ai/pricing провалился
  (JS-рендер, тот самый кейс из feedback_webfetch_reality_check).
  Цитата с MCP-страницы: «Each generation costs credits based on the model
  and resolution. Your existing Higgsfield plan credits work seamlessly.»
- API key: не требуется (auth через higgsfield.ai аккаунт)
- License: proprietary (closed-source)
- Models under hood: 30+ (Soul, Kling, Seedance, **Veo** — Google's top video model)

## ⚠ Constraint К-7: подписки не покупаются
Пользователь (2026-06-01): «подписок никаких нет и приобретаться не будут».
→ Higgsfield пройдёт **только если есть free tier** с достаточными credits
для нашего объёма (image ~раз в неделю). Проверить при установке.
Если free tier нет / недостаточен → Higgsfield отпадает, искать
open-source/self-host альтернативу для image/video generation.

## Что делает
- Image generation (up to 4K, любые соотношения)
- Video generation (cinematic style, **до 15 секунд**)
- 7 tools:
  - Video analyzer
  - Marketing video generator
  - Soul character training (consistent characters)
  - Cinematic image-to-video
  - Viral clip generator
  - Virality prediction
  - (+ ещё одно)

## Установка
- MCP конфиг для Claude Code не предоставлен явно
- Документация рекомендует CLI: «If you are using Claude Code or Codex, it's better to use the CLI»
- Подписка на higgsfield.ai обязательна

## Конкурент в нашем стеке: Adobe MCP

Полный Adobe Creative Cloud MCP уже подключён (видно в deferred list текущей сессии).
Покрывает 80% наших нужд image/video:

| Категория | Adobe MCP (есть) | Higgsfield |
|---|---|---|
| Image generation | `create_firefly_board`, `image_generative_expand`, Firefly | Soul + 30 моделей |
| Image editing | 15+ `image_*` инструментов | Минимум |
| Video | `video_create_quick_cut`, `video_resize`, `animate_design` | Veo, Kling, Seedance |
| Assets | `asset_search` (Adobe Stock + Firefly board) | Soul Characters |
| Design | `document_render_*`, `font_recommend`, `fill_text` | — |

**Перевес:** Adobe сильнее в editing/design, Higgsfield сильнее в cinematic generation.

## Применимость к нашей базе

### Use-cases image/video в стройфирме
1. Концепт-визуализация инженерных систем — Adobe справляется.
2. Marketing для КП заказчику — раз в квартал, Adobe справляется.
3. Видео-обходы объектов — снимаются камерой, не AI generation.
4. Иллюстрации тех. документации — Adobe + стоки.
5. SMM К-7 — если есть отдельная функция (вопрос пользователю).

### Где Higgsfield дал бы прирост
- High-end cinematic marketing video (15 сек) для соцсетей К-7.
- Если К-7 делает рекламные ролики проектов — Veo-качество.
- Consistent characters (Soul) — если есть mascot/брендинг.

### Где не дал бы прироста
- Технические чертежи (AutoCAD MCP).
- Проектные расчёты (своими skills).
- Документация (`word`, `excel`, `pdf` MCP).
- Image editing (Adobe лучше).

## Минусы для нас
1. **Cost overlap** — двойная подписка с Adobe Firefly.
2. **Domain mismatch** — viral/cinematic vs наш технический контекст.
3. **15-сек cap** — для технических демо короткие.
4. **Credit-based × 9 человек** — серьёзный budget без явного use-case.
5. **Data privacy не раскрыта** — prompts/outputs уходят на их серверы.

## Решение (revision 2, 2026-06-01)

**Прошлая ревизия была неверна.** Я предположил «Adobe MCP покрывает 80%»
без верификации. Пользователь подтвердил: **Adobe Firefly эмпирически не
работает** на их задачах, image/video generation у К-7 **фактически не
покрыто**. Это та же ошибка что в кейсе WebFetch (см.
`~/.claude/memory/feedback_webfetch_reality_check.md`).

🟢 **Ставим Higgsfield. Это закрытие дыры, не nice-to-have.**

### Обоснование
- Adobe Firefly fail подтверждён эмпирически.
- Альтернатив с реально работающим image/video generation у нас нет.
- Higgsfield с Veo + 30 моделями — топ-tier на 2026.
- Cost оправдан тем что покрывает критическую дыру.

### Связанный вопрос: судьба Adobe MCP в эталоне 9

Adobe MCP ≠ только Firefly. В нём также:
- Image **editing** (`image_apply_*`, `image_adjust_*` — 15+ инструментов)
- Video editing (`video_create_quick_cut`, `video_resize`, `animate_design`)
- Document render (`document_render_layout`, `font_recommend`, `fill_text`)
- Assets (`asset_search` — Adobe Stock)

**Открытый вопрос пользователю:**
- Editing инструменты Adobe MCP — работают? Есть кейсы использования?
- Если editing тоже не работает → выкинуть Adobe MCP из эталона 9 целиком.
- Если работает только editing → оставить Adobe для editing,
  Higgsfield для generation. Гибрид.

### Открытые вопросы по deployment Higgsfield
1. **CLI vs MCP** — Higgsfield рекомендует CLI для Claude Code. Ставим
   как CLI или MCP? CLI проще, MCP интегрируется глубже.
2. **На кого ставить** — все 9 ПК или только профильным (маркетинг,
   презентации, проектировщики которым нужны 3D-визуализации)?
3. **Credit-based pricing** — кто оплачивает? Корпоративная подписка
   К-7 или личная у каждого?
4. **Auth** — через higgsfield.ai аккаунт. Один корпоративный для команды
   или индивидуальные?

## Идеи в копилку
- ✅ **Veo через Higgsfield** — топ video model 2026.
- ✅ **Soul Character training** — если К-7 имеет mascot/брендинг,
  consistent characters пригодится для marketing материалов.
- ✅ **Virality prediction** — если развиваем SMM К-7, эта функция оценит
  потенциал поста до публикации.

## Рекомендация пользователю
🟢 Ставим. На финальном этапе после #9 решаем deployment (CLI/MCP,
раскат, оплата) и судьбу Adobe MCP в эталоне 9.
