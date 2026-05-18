"""Замер vision-LLM (через Ollama) на УПД.
Принимает модель и картинку аргументами. Сохраняет результат в JSON.

Запуск:
    python bench_vlm.py <model_name> <png_path> <out_json>
Пример:
    python bench_vlm.py qwen2.5vl:3b samples/upd_vrnlom_p1.png result_qwen_vrnlom.json
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

import requests

PROMPT = """На изображении — российский Универсальный Передаточный Документ (УПД).
Извлеки данные строго в JSON-формате (без markdown, без комментариев, только JSON):

{
  "type": "УПД",
  "status": <1 или 2>,
  "number": "<номер счёта-фактуры>",
  "date": "<дата ДД.ММ.ГГГГ>",
  "seller": {"name": "...", "inn": "...", "kpp": "...", "address": "..."},
  "buyer":  {"name": "...", "inn": "...", "kpp": "...", "address": "..."},
  "items": [
    {"name": "...", "quantity": <число>, "unit": "...", "unit_price": <число>, "total_without_vat": <число>, "vat_rate": "...", "vat_amount": <число или null>, "total_with_vat": <число или null>}
  ],
  "total_to_pay": <число>,
  "director": "<ФИО руководителя>",
  "accountant": "<ФИО бухгалтера>"
}

Цифры — без пробелов и без знаков рубля. Если поля нет — null. Отвечай ТОЛЬКО JSON-объектом."""


def main():
    if len(sys.argv) != 4:
        print("Usage: python bench_vlm.py <model> <png_path> <out_json>")
        sys.exit(2)
    model = sys.argv[1]
    img_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])

    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    print(f"Model:  {model}", flush=True)
    print(f"Image:  {img_path.name}, {img_path.stat().st_size / 1024:.1f} KB", flush=True)
    print(f"Output: {out_path}", flush=True)

    payload = {
        "model": model,
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 2048, "num_ctx": 4096},
    }

    print("Calling Ollama...", flush=True)
    t0 = time.time()
    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json=payload,
            timeout=900,
            proxies={"http": None, "https": None},
        )
        elapsed = time.time() - t0
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP ERROR after {elapsed:.1f}s: {e}")
        print(f"Response body: {r.text[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR after {time.time()-t0:.1f}s: {e}")
        sys.exit(1)

    data = r.json()
    raw = data.get("response", "")
    print(f"OK in {elapsed:.1f}s | tokens out: {data.get('eval_count')} | ollama duration: {data.get('total_duration', 0) / 1e9:.1f}s", flush=True)

    parsed, parse_err = None, None
    try:
        text = raw.strip()
        if "```" in text:
            # вырезаю markdown-блок если есть
            parts = text.split("```")
            for p in parts:
                p = p.strip()
                if p.startswith("json"):
                    p = p[4:].strip()
                if p.startswith("{"):
                    text = p
                    break
        parsed = json.loads(text)
    except Exception as e:
        parse_err = str(e)

    result = {
        "model": model,
        "image": str(img_path),
        "elapsed_sec": round(elapsed, 2),
        "ollama_total_duration_sec": round(data.get("total_duration", 0) / 1e9, 2),
        "eval_count_tokens": data.get("eval_count"),
        "prompt_eval_count_tokens": data.get("prompt_eval_count"),
        "raw_response": raw,
        "parsed_json": parsed,
        "parse_error": parse_err,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}", flush=True)
    print("\n--- RAW (first 2000 chars) ---", flush=True)
    print(raw[:2000], flush=True)


if __name__ == "__main__":
    main()
