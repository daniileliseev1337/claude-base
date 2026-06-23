# pikepdf
- URL: https://github.com/pikepdf/pikepdf
- Stars: ~2400
- Last release: v10.7 (ноябрь 2025)
- License: MPL-2.0 (зелёный свет для нашего installer)
- Описание: Низкоуровневая Python-библиотека для редактирования PDF на уровне content stream, основанная на QPDF (C++). Где PyMuPDF про rendering и удобный API, pikepdf — про **физическую** манипуляцию содержимым PDF.

## Зачем смотрели

Замена ГОСТ-штампов на 57 листах PDF (АХП <объект-Б>). PyMuPDF
`page.apply_redactions(graphics=2)` не удалял содержимое внутри Form
XObjects и nested content stream операторы — старый штамп оставался
видимым поверх нового. Нужен инструмент который умеет **физически
вырезать** содержимое из content stream, а не только рисовать поверх.
См. anti-pattern A3.5 в [[anti-patterns]] + session-report
[[2026-05-22_ahp-stamp-overlay]].

## Оценка

- Подходит для нашей проблемы? **Да** — закрывает 100% дыры PyMuPDF.
- Сильные стороны:
  - Работа с **content stream** на уровне отдельных операторов
    (q/Q, cm, Tj/TJ, m/l/c, W*, n, ...).
  - `parse_content_stream` / `unparse_content_stream` — разбор и
    пересборка stream'а как Python-объекта.
  - Inject clip-path оператора (even-odd clipping rule, `W*` + `n`)
    для физического выреза прямоугольной области в обход всех
    inner-XObjects.
  - Удаление XObjects из `/Resources` напрямую.
  - `pdf.save(..., garbage=4)` — полная сборка мусора, удаляет
    осиротевшие объекты.
  - Основан на QPDF — индустриальный стандарт парсинга PDF.
- Слабые стороны / риски:
  - Низкоуровневый — нужно понимать PDF 1.7 §8.4 (graphics state),
    §8.10 (Form XObjects), §9 (text), не «открыл и подменил».
  - Сам **не рендерит** — для preview готового PDF нужен PyMuPDF /
    pdfcpu / Acrobat.
  - Сам **не делает overlay** — комбо с PyMuPDF `show_pdf_page` или
    pdfcpu `stamp add` для финального наложения нового штампа.
- Решение: **adopted** как часть PDF-stack рядом с PyMuPDF.

## Когда использовать pikepdf vs PyMuPDF vs pdfcpu

| Задача | Инструмент | Почему |
|---|---|---|
| Прочитать текст / координаты | PyMuPDF | удобный API |
| Render → image | PyMuPDF | get_pixmap(dpi=180-300) |
| Overlay нового штампа поверх | PyMuPDF show_pdf_page **или** pdfcpu stamp add | |
| **Удалить старый штамп physically** | **pikepdf clip-path inject** | PyMuPDF не справляется |
| Удалить XObjects | pikepdf | прямой доступ к /Resources |
| Batch overlay на тысячи листов | pdfcpu | 1.3 сек / лист |
| Финальная нормализация шрифтов для Acrobat | PyMuPDF save garbage=4, clean=True | фикс Type1 без /FirstChar |

## Минимальный пример — clip-path inject (вырез прямоугольника)

Вырезает прямоугольник `clip_rect` из content stream страницы:
содержимое внутри прямоугольника становится **физически невидимым**
(не белый прямоугольник поверх, а реальный вырез через graphics state).

```python
import pikepdf
from pikepdf import Pdf, Object, OperandList, ContentStreamInstruction as CSI

def inject_clip_cutout(page, clip_rect):
    """
    clip_rect: (x0, y0, x1, y1) в user-space координатах страницы.

    Использует even-odd clipping rule: рисуем path
    (полная страница + clip_rect inner) → W* + n →
    всё последующее содержимое clipped, прямоугольник «вырезан».
    """
    x0, y0, x1, y1 = clip_rect
    page_w = float(page.MediaBox[2])
    page_h = float(page.MediaBox[3])

    # Path: внешний прямоугольник (вся страница) + inner (clip_rect)
    # m, l, l, l, h — move/line/line/line/close (rectangle)
    new_ops = [
        CSI(OperandList([0, 0]), 'm'),
        CSI(OperandList([page_w, 0]), 'l'),
        CSI(OperandList([page_w, page_h]), 'l'),
        CSI(OperandList([0, page_h]), 'l'),
        CSI(OperandList(), 'h'),
        # Inner — clip_rect
        CSI(OperandList([x0, y0]), 'm'),
        CSI(OperandList([x1, y0]), 'l'),
        CSI(OperandList([x1, y1]), 'l'),
        CSI(OperandList([x0, y1]), 'l'),
        CSI(OperandList(), 'h'),
        # Even-odd clip + no-op fill
        CSI(OperandList(), 'W*'),
        CSI(OperandList(), 'n'),
    ]

    # Префиксируем существующий content stream
    existing = list(pikepdf.parse_content_stream(page))
    page.Contents = pikepdf.unparse_content_stream(new_ops + existing)

# Использование:
with Pdf.open('input.pdf', allow_overwriting_input=True) as pdf:
    for page in pdf.pages:
        # Координаты штампа в нижнем-правом углу A4 portrait
        inject_clip_cutout(page, (450, 0, 595, 60))
    pdf.save('cutout.pdf', garbage=4)
```

После этого можно наложить новый штамп через PyMuPDF
`show_pdf_page` или pdfcpu `stamp add` — старого содержимого в
этой области уже **физически нет**.

## Ловушки

- **Graphics state stack (q/Q)** — если удаляешь блок операторов
  посередине content stream'а, удаляй **целый** `q ... Q` блок.
  Удаление одиночных операторов посередине ломает transform
  matrix для соседних элементов.
- **GC после удаления XObject** — `pdf.save(..., garbage=4)` или
  `mutool clean` нужны, чтобы реально удалить осиротевший объект
  из тела PDF.
- **Rotated pages** — clip_rect задаётся в координатах **MediaBox**
  (как и `search_for` PyMuPDF). На страницах с `/Rotate=90/180/270`
  нужно rotation-aware преобразование bbox.
- **Шрифты Acrobat** — после pikepdf+pdfcpu Acrobat может выдать
  ошибку Type1 шрифта. Финальный шаг —
  `doc.save(out, garbage=4, clean=True, deflate=True, deflate_fonts=True)`
  через PyMuPDF.

## Связанные заметки

- [[PyMuPDF]] — комплементарный инструмент.
- [[pdfcpu]] (TODO заметка) — batch-overlay.
- [[anti-patterns]] A3.5 — PyMuPDF redactions ловушка.
- session-report [[2026-05-22_ahp-stamp-overlay]] — first contact.
- session-report [[2026-05-25_pdf-stamp-pipeline]] — рабочий
  3-stage pipeline (pikepdf + pdfcpu + PyMuPDF clean).
- skill [[pdf-helper]] — куда добавить ссылку.

## Решение

**Adopted** (MPL-2.0, активный, рабочее решение для нашего кейса).
Pip install из PyPI: `pip install pikepdf`. Установлен на R-090226727A
в рамках сессии 2026-05-22. Раскатка через `mcp-manifest.json` —
TODO (после следующего успешного применения на ещё одном объекте).
