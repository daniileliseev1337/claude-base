# Направление 3. Готовые шаблоны / decks про AI для офисных лекций

Цель: взять готовый материал «введение в LLM / AI for business / AI training» и адаптировать. Желательно русский, иначе английский — потом перевести.

## Сравнительная таблица

| # | Источник | URL | Stars | License | Формат | Содержит слайды? | Актуальность | Адаптируемость | Русский |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **microsoft/generative-ai-for-beginners** | github.com/microsoft/generative-ai-for-beginners | **111k** | MIT | 21 урок: Jupyter Notebooks + Markdown + папка `presentations/` | **да, есть папка presentations со слайдами** + видеоинтродукции к большинству уроков | свежий, актуальный (Azure OpenAI / OpenAI, GPT-4, агенты) | очень высокая (MIT, можно резать и переписывать) | **да, авто-переводы через GitHub Actions на 50+ языков включая RU** |
| 2 | **microsoft/AI-For-Beginners** | github.com/microsoft/ai-for-beginners | **47.7k** | MIT | 12 недель / 24 урока: Jupyter + Markdown | нет .pptx, но богатый контент для пересказа | актуальный, активный (PyTorch+TensorFlow) | высокая | да, 50+ языков |
| 3 | **mlabonne/llm-course** | github.com/mlabonne/llm-course | очень популярный (десятки тысяч stars) | Apache 2.0 | Roadmap (картинки) + Colab notebooks + ссылки | роадмапы как картинки годятся как слайды | очень свежий | средняя (контент для разработчиков, для офисной аудитории нужно сильно резать) | нет, английский |
| 4 | **Ryan-PG/AI-Gathering-LLM-Presentation** | github.com/Ryan-PG/AI-Gathering-LLM-Presentation | малый | смотреть в репо | **готовые слайды** (PDF/PPTX) с презентации в Keyhan Qom (ноябрь 2024) | да | конец 2024, кое-что устарело (GPT-4 era) | средняя — готовые слайды берёшь и переделываешь под Claude 2026 | нет, английский (некоторые места — фарси) |
| 5 | **vakovalskii/presentation_claude_prompt** | github.com/vakovalskii/presentation_claude_prompt | малый | смотреть в репо | Примеры промптов + AI-generated слайды специально под Claude | да | свежий | высокая (как образец промптов) | смешанный |

## Что отсек

- **Anthropic Cookbook** — это про API/код, не презентационные материалы про «что такое Claude для бухгалтерии».
- **Hugging Face spaces** — это интерактивные демки, не лекционные слайды.
- **Google AI training** — корпоративный материал, на GitHub не выкладывается, не open-source.
- **start-llms** (louisfb01) — это reading list, не слайды.

## Ключевой инсайт

**Лучший готовый материал для адаптации — это `microsoft/generative-ai-for-beginners`:**
- Папка `presentations/` уже содержит слайды по большинству уроков.
- Авто-перевод на русский настроен через GitHub Actions — то есть README и описания уроков уже есть на русском.
- 111k stars + MIT — можно взять, перекроить, выкинуть код-секции (для аудитории <организация> они не нужны) и оставить высокоуровневые слайды «Что такое LLM», «Промпт-инжиниринг», «Бизнес-применения», «Этика и риски».
- Уроки 1, 2, 3, 4 (Intro / LLMs / Prompt Engineering / Building) — почти готовая структура для 2,5-часовой лекции.

## РЕКОМЕНДУЮ

**Топ-1: microsoft/generative-ai-for-beginners** — клонировать репо, взять папку `presentations/`, выдрать слайды из уроков 1-4 + 9 (Building Image Apps) + 13 (Securing AI Apps) + 18 (Trust/Responsible AI). Перевести на русский (у них уже есть авто-переводы README, по слайдам — через тот же ChatGPT/Claude). Получится примерно 25-30 слайдов готовой основы. Перекрашиваешь под <организация> — готово.

**Топ-2 (как доп. идеи для слайдов): Ryan-PG/AI-Gathering-LLM-Presentation** — структура «как объяснить LLM незнакомым с темой людям» уже отработана в реальной презентации. Можно подсмотреть как разбили темы, какие visual metaphors использовали. Сами слайды устарели (2024, до Claude 3.5/4) — переделываешь под актуальный stack.

**Топ-3 (для промпт-инжиниринговой части лекции): vakovalskii/presentation_claude_prompt** — там специфические примеры промптов под Claude. Полезно как иллюстративный материал для секции «Как правильно писать промпты в Claude».

## Источники

- [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners)
- [microsoft/AI-For-Beginners](https://github.com/microsoft/ai-for-beginners)
- [mlabonne/llm-course](https://github.com/mlabonne/llm-course)
- [Ryan-PG/AI-Gathering-LLM-Presentation](https://github.com/Ryan-PG/AI-Gathering-LLM-Presentation)
- [vakovalskii/presentation_claude_prompt](https://github.com/vakovalskii/presentation_claude_prompt)
- [llm-course.github.io (CSC 6203 LLM course materials)](https://llm-course.github.io/)
