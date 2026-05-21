# Направление 1. AI-генераторы слайдов (альтернативы Gamma)

Цель: text-to-slides AI, который понимает большой русский промпт, экспортирует в .pptx, доступен из РФ.

## Сравнительная таблица

| # | Сервис | URL | Free tier | Русский язык | Большой промпт | Экспорт PPTX | Доступ из РФ | Регистрация |
|---|---|---|---|---|---|---|---|---|
| 1 | **Gamma** | gamma.app | да (с маленьким логотипом «Made in Gamma» в углу); создание, редактирование, экспорт PDF/PPTX бесплатно без лимита | да, интерфейс на русском, контент обрабатывается корректно | да (импорт текста и файлов целиком) | да, бесплатный экспорт .pptx (с водяным знаком на free) | сайт открывается без VPN; **оплата RU-картами не проходит** (нужна Wise/Revolut/KZ-карта) | Google/email |
| 2 | **Kimi Slides** (Moonshot AI, КНР) | kimi.com/kimiplus + ppt.ai/ru/kimi-ppt | open-beta, **полностью бесплатно**, без водяных знаков, без лимита слайдов | да, 15+ языков включая RU | да (можно прикреплять до 50 файлов / 100 МБ) | да, редактируемый .pptx | сайт работает из РФ; **регистрация через Google-аккаунт** | Google |
| 3 | **SlidesAI.io** | slidesai.io | freemium ($0), платные от $10/мес | да (интерфейс переведён + 100+ языков контента) | ограничен размером текста на free | да, .pptx через Google Slides/PowerPoint (работает как plugin) | сайт открывается; оплата через Google Workspace Marketplace проблемна с RU-картами | Google (обязателен) |
| 4 | **Plaan** (RU) | plaan.ru | free: 3 презентации/мес до 12 слайдов, **без водяного знака** | нативный русский | да | да, .pptx + PDF | российский сервис, без проблем | email / RU-почта |
| 5 (резерв) | **Сократик** (RU) | sokratic.ru | **бесплатной версии нет** | нативный русский | да | да | российский сервис | email |

## Что отсек

- **Decktopus** — free tier мутный, по части источников нет прямого .pptx экспорта на free, для $14.99/мес проигрывает Plus AI.
- **Plus AI** — нет постоянного free plan (только 7-дневный trial), требует Google Slides, оплата с RU-карт проблематична.
- **Presentations.ai** — free tier **не поддерживает .pptx экспорт вообще** (только просмотр); $198/год сразу.
- **Tome / Beautiful.ai / Pitch / Decktopus** — все имеют те же проблемы с оплатой из РФ + слабее по русскому языку чем Gamma/Kimi.

## РЕКОМЕНДУЮ

**Топ-1: Kimi Slides** — единственный из всех протестированных, кто даёт (а) полностью бесплатно, (б) без водяного знака, (в) нативную поддержку русского, (г) редактируемый .pptx, (д) работает из РФ без VPN и без проблем с оплатой (платить нечего). Минус — нужен Google-аккаунт для входа.

**Топ-2 (страховка): Gamma** — пользователь уже готовит промпт под Gamma, поэтому если Kimi не зайдёт по качеству — Gamma на free плане даёт всё то же самое, кроме отсутствия маленького логотипа в углу. Доступна из РФ, .pptx экспорт работает.

**Топ-3 (если хочется российского вендора): Plaan** — 3 презентации в месяц до 12 слайдов хватит на одну лекцию + 2 запасных варианта. Без водяного знака на free, оплата российскими картами.

## Источники

- [Gamma AI обзор на vc.ru (доступ из РФ)](https://vc.ru/aihub/2842556-gamma-ai-neiroset-dlya-sozdaniya-prezentatsiy)
- [Kimi AI Slides обзор на vc.ru](https://vc.ru/ai/2606502-kimi-ai-slides-bystroe-sozdanie-prezentatsiy)
- [iPhones.ru про Kimi для школьников и студентов](https://www.iphones.ru/iNotes/podarok-dlya-shkolnikov-i-studentov-v-kitae-zapustili-besplatnyy-ii-generator-prezentaciy-kotoryy-rabotaet-na-russkom-yazyke)
- [SlidesAI Supported Languages](https://www.slidesai.io/supported-languages)
- [Сократик обзор Soware](https://soware.ru/products/sokratic)
- [Топ-13 нейросетей для презентаций на Habr 2026](https://habr.com/ru/companies/bothub/articles/1014260/)
- [Habr тест Kimi/Gamma/NotebookLM 2026](https://habr.com/ru/articles/1022224/)
- [Presentations.ai vs Plus AI разбор](https://www.presentations.ai/compare/plus-ai)
