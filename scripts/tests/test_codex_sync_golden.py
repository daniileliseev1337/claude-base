# -*- coding: utf-8 -*-
"""Golden-master: рендер фикстурного мини-канона побайтно совпадает со снапшотами.
Обновление снапшотов (после ОСОЗНАННОЙ правки генератора/фикстуры):
    UPDATE_GOLDEN=1 python -m pytest scripts/tests/test_codex_sync_golden.py"""
import os
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

GOLDEN_DIR = pathlib.Path(__file__).parent / "golden"

def _fname(key: str) -> str:
    return key.replace("/", "__").replace("#", "--")

def test_golden_master(make_canon):
    from codex_sync import render_all
    home = make_canon()
    rendered = render_all(home)
    # hooks.json содержит абсолютные пути от tmp home — нормализуем до <HOME>.
    # json.dumps удваивает "\" в путях Windows, поэтому наивный .replace(str(home), ...)
    # не матчится внутри hooks.json — нормализуем обе формы (сырую и JSON-экранированную),
    # иначе снапшот хранит номер временной pytest-папки и второй прогон падает нестабильно.
    home_plain = str(home)
    home_json_escaped = home_plain.replace("\\", "\\\\")
    rendered = {k: v.replace(home_json_escaped, "<HOME>").replace(home_plain, "<HOME>")
                for k, v in rendered.items()}
    if os.environ.get("UPDATE_GOLDEN") == "1":
        GOLDEN_DIR.mkdir(exist_ok=True)
        for old in GOLDEN_DIR.iterdir():
            old.unlink()
        for key, content in rendered.items():
            (GOLDEN_DIR / _fname(key)).write_text(content, encoding="utf-8", newline="\n")
    assert GOLDEN_DIR.exists(), "снапшотов нет — первый прогон: UPDATE_GOLDEN=1 pytest ..."
    golden = {f.name: f.read_text(encoding="utf-8") for f in GOLDEN_DIR.iterdir()}
    assert set(golden) == {_fname(k) for k in rendered}, "состав артефактов разошёлся со снапшотами"
    for key, content in rendered.items():
        assert content == golden[_fname(key)], f"golden mismatch: {key} — если правка генератора осознанная, UPDATE_GOLDEN=1"
