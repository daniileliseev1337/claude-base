# image-text-replace — установка и примеры

Скилл для замены текста на растровых изображениях через OCR + AI-инпейнтинг.
Полная методология — в [SKILL.md](SKILL.md).

## Установка зависимостей

Все ставятся лениво при первом запуске `pipeline.py`. Но если хочешь
заранее (например, для оффлайн-машины):

```powershell
# PaddleOCR + PaddlePaddle — уже стоят (setup-extras manifest)
# Доустановить:
python -m pip install --user iopaint Pillow opencv-python numpy
```

Первый запуск **`mode=lama`** скачает модель LaMa (~174 MB) из HuggingFace
в `~/.cache/iopaint/`. На корп-прокси нужны env-vars:

```powershell
$env:HTTPS_PROXY = "http://your-proxy:port"
$env:HTTP_PROXY  = "http://your-proxy:port"
```

или прогрев через наш `~/.claude/bin/Set-Proxy.ps1`.

## Quick smoke test

```powershell
# 1. Возьми любой скан с печатным русским текстом
Copy-Item "scan.png" "$HOME\.claude\_sandbox\test-scan.png"

# 2. Dry-run: посмотреть что OCR нашёл
python "$HOME\.claude\skills\image-text-replace\pipeline.py" `
    --input "$HOME\.claude\_sandbox\test-scan.png" `
    --find "АОСР" `
    --replace "АОСР-1" `
    --dry-run

# 3. Если bbox совпадают — без --dry-run
python "$HOME\.claude\skills\image-text-replace\pipeline.py" `
    --input "$HOME\.claude\_sandbox\test-scan.png" `
    --find "АОСР" `
    --replace "АОСР-1"

# 4. Результат: ~/.claude/_sandbox/test-scan.replaced.png
```

## Типовые сценарии

### 1. Заменить шифр в скане документа

```powershell
python pipeline.py `
    --input "C:\Documents\AOSR_skan.png" `
    --find "Ф.2024.123456789" `
    --replace "Ф.2026.987654321" `
    --font "C:\Windows\Fonts\arial.ttf"
```

### 2. Batch-замена в нескольких файлах одинаковыми правилами

```powershell
$files = Get-ChildItem "C:\Sканы\*.png"
foreach ($f in $files) {
    python pipeline.py `
        --input $f.FullName `
        --find "ВКР-12" `
        --replace "ВКР-13" `
        --mode fast  # на белых сканах + однотипных правках fast быстрее
}
```

### 3. Несколько замен в одном файле

```powershell
python pipeline.py `
    --input "scan.png" `
    --find "Подрядчик: ООО Рога" --replace "Подрядчик: ООО Копыта" `
    --find "Дата: 18.05.2025"   --replace "Дата: 18.05.2026"
```

### 4. Замена по regex

```powershell
python pipeline.py `
    --input "scan.png" `
    --find "\d{2}\.\d{2}\.\d{4}" --replace "18.05.2026" `
    --regex
```

### 5. Скан внутри PDF (страница со штампом-картинкой)

```powershell
# 1. Извлечь страницу как PNG через pdf-edit MCP или pikepdf
# 2. Применить наш скилл
# 3. Вставить обратно (см. skill pdf-helper)
```

## Тонкая настройка

### Цвет нового текста не совпадает с оригиналом

По умолчанию pipeline берёт **медианный цвет тёмных пикселей внутри bbox**.
Если результат бледнее — задать явно:

```powershell
--color "#000000"   # чёрный
--color "#1a1a1a"   # тёмно-серый
```

### Размер шрифта не совпадает

Default: `int(bbox_height × 0.85)` — обычно правильно для PaddleOCR
который рисует bbox чуть больше реальной высоты букв. Если новый текст
вылазит за оригинал:

```powershell
--font-size 18
```

### Шов после инпейнта виден

Увеличить `dilate` (захватить больше пикселей вокруг текста — анти-алиасинг):

```powershell
--dilate 8
```

### OCR не находит текст

PaddleOCR ru по умолчанию. Если на картинке смесь русского + цифр —
обычно сработает. Если только английский / только цифры:

```powershell
--ocr-lang en
--ocr-lang ch  # китайский если такое попадётся
```

Можно вообще обойти OCR — если знаешь точные координаты bbox, добавить
прямой режим. Это пока не реализовано в pipeline.py (`--bbox x,y,w,h`),
TODO для следующей итерации.

## Когда LaMa не подходит — fast mode

`--mode fast` использует `cv2.inpaint` с алгоритмом TELEA. Качество ниже,
но:
- В 50-100 раз быстрее (LaMa: 1-3 сек, TELEA: <50 мс)
- Не требует загрузки 174 MB модели
- Не зависит от torch

Применяй на:
- Белых сканах с печатным текстом без декоративных элементов
- Batch'ах в 100+ файлов где LaMa суммарно займёт час
- ПК без интернета для скачивания модели

На цветных документах, штампах, печатях, watermark'ах — **только LaMa**.

## Известные ограничения (на 2026-05-18, версия 0.1)

1. **Нет detection rotated text** — PaddleOCR умеет, но pipeline пока
   рендерит новый текст только горизонтально. Если оригинал под углом,
   получится криво.
2. **Нет multi-line wrapping** — если новый текст длиннее оригинала,
   просто вылезет за bbox. Pillow в DrawText не делает auto-wrap.
3. **font-matching = поиск похожего вручную**. Auto-detect шрифта
   оригинала не реализован (Adobe `font_recommend` платный, своих
   моделей не нашли). Workaround: использовать **один и тот же шрифт
   для всех документов** в пайплайне (твой типичный документ ведь
   набирается в Times/Arial?).
4. **HuggingFace зависимость** — первое скачивание модели LaMa
   ходит на huggingface.co. На полностью оффлайн-машине положить
   модель руками в `~/.cache/iopaint/big_lama/`.

## Альтернативы которые НЕ взяли

- **Adobe Firefly MCP** — `image_fill_area` + `fill_text` есть в API,
  но Adobe явно пишет «text removal from photo — not available»
  (см. session-report 2026-05-15).
- **Stable Diffusion inpaint** — для документов overkill, шанс
  галлюцинаций выше чем у специализированной LaMa.
- **OpenCV-only** — без OCR пользователь должен задавать bbox руками,
  это не scaleable.
- **Google Document AI** — облако, paid, требует выгрузки изображений
  во внешний сервис (для документов клиентов — не делаем).

## Тесты

Будут добавлены после первого реального скана. Сейчас скилл
**не тестирован на конкретном файле** — это design + ленивая установка
зависимостей. Karpathy 4 (верификация) выполнится на первой реальной
задаче.

## Связанные

- [SKILL.md](SKILL.md) — методология подключения
- [[../skills|каталог скиллов]]
- [[../pdf-helper/SKILL|pdf-helper]] — частая связка (PDF → картинка → этот скилл → вставка)
- [[../../session-reports/2026-05-15_handoff-manifest-extras-installer-stage8/harvested/image-text-replace-stack|harvest заметки]]
