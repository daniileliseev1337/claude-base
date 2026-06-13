# microsoft/markitdown — апгрейд-аудит (у нас уже стоит как core MCP)

- **URL:** https://github.com/microsoft/markitdown
- **Stars:** 151 675 (проверено API)
- **Last commit:** 2026-05-26, релиз v0.1.6
- **License:** MIT
- **Описание:** конвертер документов → Markdown (PDF/DOCX/PPTX/XLSX/изображения/аудио/HTML/ZIP/YouTube). У нас в базе — один из 11 core MCP.

## Зачем смотрели
Пользователь попросил аудит на возможный апгрейд перед внедрением локальных моделей.

## Оценка — что нового и что брать
1. **Плагин `markitdown-ocr`** (главная находка): добавляет OCR встроенных картинок в PDF/DOCX/PPTX/XLSX через любой OpenAI-совместимый llm_client → **стыкуется с локальным Ollama**: `OpenAI(base_url="http://localhost:11434/v1")` + `qwen3-vl:8b`/`glm-ocr`. Это локальный LLM-OCR прямо в нашем конвертере — апгрейд пайплайна сканов (УПД, документы ИД) без облака и токенов. `pip install markitdown-ocr`.
2. Azure Document Intelligence / Content Understanding — платное облако Azure, наши данные туда не возим — пропускаем.
3. Extras `[audio-transcription]`, `[youtube-transcription]` — ниша, по запросу.
4. Проверить версию нашего uvx-кэша markitdown vs v0.1.6 при следующем /sync-base.

- Решение: внедрять markitdown-ocr + Ollama vision после pull vision-модели; тест на реальном скане УПД против EasyOCR-пайплайна (image-text-replace)
